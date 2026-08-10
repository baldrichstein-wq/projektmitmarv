import os
import pymongo
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://root:mongopass@localhost:27017/')

PREDEFINED_WINE = {
    'name': 'Holunder Johannisbeer Wein',
    'liter': '5',
    'ingredients': [
        '1 Pack Weinhefe Sorte Portwein',
        '500g Johannisbeeren Schwarz',
        '1000g Holunderbeeren',
        '1800g Zucker',
        'Wasser bis 5l ansatz erreicht',
        'Starsan für Desinfektion von Brauutensilien',
        '5g Hefenährsalz',
        'Gärbehälter mit Gärstopfen und ggf je nach bauweise Deckel und Gärröhrchen',
        'Dampfentsafter'
    ],
    'description': 'Ein sehr kräftiger Wein mit eigenwilligem Geschmack, bei dem Holunder und Johannisbeere zusammenwirken.',
    'brewing_instructions': 'Alle Utensilien sauber vorbereiten, Früchte entsaften, Zucker und Hefe einrühren und in einem sauberen Gärbehälter gären lassen.',
    'brewing_time': 8,
    'alcohol_content': 15.0
}

# Reuse MongoClient connection pool globally
_mongo_client = None

def get_collection():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(MONGO_URI)
    db = _mongo_client['rezeptdb']
    return db['wines']

# GEAENDERT 07.08.2026 (Stefan): Vorher wurde die naechste ID per
# "collection.find_one(sort=[('id', -1)])['id'] + 1" ermittelt. Das ist NICHT atomar: Legen
# zwei Requests (z.B. zwei gleichzeitige Gunicorn-Worker) gleichzeitig einen Wein an, koennen
# beide dieselbe "hoechste ID" lesen, bevor der jeweils andere fertig geschrieben hat -> zwei
# Weine mit derselben ID. find_one_and_update mit $inc ist dagegen eine einzige atomare
# Operation auf MongoDB-Seite und damit race-condition-frei. Die eigentliche Zaehlung liegt in
# einer separaten "counters"-Collection (ein Dokument pro Collection-Name).
def get_next_id(collection):
    db = collection.database
    counters = db['counters']
    counter_id = collection.name
    result = counters.find_one_and_update(
        {'_id': counter_id},
        {'$inc': {'seq': 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    seq = result['seq']
    # Absicherung fuer bestehende Datenbanken, die schon vor dieser Aenderung befuellt wurden:
    # Der Counter startet dann bei 1, obwohl schon hoehere IDs vergeben sind. Einmalig auf die
    # naechste freie ID nach dem aktuellen Maximum springen.
    if seq == 1:
        highest = collection.find_one(sort=[("id", -1)])
        if highest and highest.get('id', 0) >= seq:
            seq = highest['id'] + 1
            counters.update_one({'_id': counter_id}, {'$set': {'seq': seq}})
    return seq

# GEAENDERT 10.08.2026 (Stefan): Vorher "count_documents == 0 -> insert" -- nicht atomar, daher
# legten mehrere Gunicorn-Worker beim gleichzeitigen Start alle das gleiche Grundrezept doppelt
# an (jeder Worker sah "noch leer", bevor der andere fertig war). Ein Unique-Index auf 'id'
# macht den Insert race-frei: nur der erste Worker legt das Dokument an, alle anderen bekommen
# einen DuplicateKeyError und tun nichts.
def init_db():
    col = get_collection()
    col.create_index('id', unique=True)
    if col.count_documents({}) == 0:
        doc = PREDEFINED_WINE.copy()
        doc['id'] = 1
        doc['created_by'] = None
        try:
            col.insert_one(doc)
        except DuplicateKeyError:
            return
        # Counter auf 1 setzen, damit die naechste Vergabe (get_next_id) korrekt bei 2 startet
        # und nicht mit der hier vergebenen ID 1 kollidiert.
        col.database['counters'].update_one(
            {'_id': col.name}, {'$set': {'seq': 1}}, upsert=True
        )

# GEAENDERT 07.08.2026 (Stefan): neuer Parameter created_by (E-Mail des anlegenden Nutzers).
# Wird beim Loeschen gebraucht, um zu pruefen, ob ein "benutzer" (nicht admin) nur seine
# eigenen Weine loeschen darf -- siehe main.py, loesche_wein().
def add_wine(name, liter, ingredients, description, brewing_instructions, brewing_time, alcohol_content, created_by=None):
    col = get_collection()
    new_id = get_next_id(col)
    doc = {
        'id': new_id,
        'name': name,
        'liter': liter,
        'ingredients': ingredients,
        'description': description,
        'brewing_instructions': brewing_instructions,
        'brewing_time': brewing_time,
        'alcohol_content': alcohol_content,
        'created_by': created_by
    }
    col.insert_one(doc)
    return new_id

def get_all_wines():
    col = get_collection()
    cursor = col.find({}, {'_id': 0}).sort('id', 1)
    wines = []
    for doc in cursor:
        wines.append({
            'id': doc.get('id'),
            'name': doc.get('name'),
            'liter': doc.get('liter'),
            'ingredients': doc.get('ingredients', []),
            'description': doc.get('description'),
            'brewing_instructions': doc.get('brewing_instructions'),
            'brewing_time': doc.get('brewing_time'),
            'alcohol_content': doc.get('alcohol_content'),
            'created_by': doc.get('created_by'),
        })
    return wines

def get_wine_by_id(wine_id):
    col = get_collection()
    doc = col.find_one({'id': int(wine_id)}, {'_id': 0})
    if doc:
        return {
            'id': doc.get('id'),
            'name': doc.get('name'),
            'liter': doc.get('liter'),
            'ingredients': doc.get('ingredients', []),
            'description': doc.get('description'),
            'brewing_instructions': doc.get('brewing_instructions'),
            'brewing_time': doc.get('brewing_time'),
            'alcohol_content': doc.get('alcohol_content'),
            'created_by': doc.get('created_by'),
        }
    return None

def delete_wine(wine_id):
    col = get_collection()
    result = col.delete_one({'id': int(wine_id)})
    return result.deleted_count > 0

def update_wine(wine_id, name, liter, ingredients, description, brewing_instructions, brewing_time, alcohol_content):
    col = get_collection()
    result = col.update_one(
        {'id': int(wine_id)},
        {'$set': {
            'name': name,
            'liter': liter,
            'ingredients': ingredients,
            'description': description,
            'brewing_instructions': brewing_instructions,
            'brewing_time': brewing_time,
            'alcohol_content': alcohol_content
        }}
    )
    return result.modified_count > 0 or result.matched_count > 0
