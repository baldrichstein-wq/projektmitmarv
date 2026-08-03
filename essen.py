import os
import pymongo
from pymongo import MongoClient

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://root:mongopass@localhost:27017/')

PREDEFINED_Essen = {
    'name': 'Kaiserliches Kräuter-Kaninchen mit Rosmarin',
    'personenanzahl': 4,
    'zutaten': [
        '0,5 kg Kaninchen',
        '4 Zweige frischer Rosmarin',
        '2 Zweige Thymian',
        '1 Zehe Knoplauch (zerdrückt)',
        'Salz & Pfeffer (wie von der Dame verlangt! )',
        'etwas Butter oder Olivenöl',
        'Bräter'
    ],
    'description': 'Ein köstliches Gericht, das die Aromen von frischen Kräutern und zartem Kaninchen vereint. Perfekt für ein festliches Mahl oder einen besonderen Anlass.',
    'kochanweisung': 'Das Fleisch mit Salz, Pfeffer und dem zerdrückten Knoblauch kräftig einmassieren. Die Kräuter fein hacken und unter die Gewürzmischung rühren. Das Kaninchen damit bestreichen und mindestens 2 Stunden ziehen lassen. Bei mittlerer Hitze im Ofen goldbraun braten, bis es nach Sieg riecht!',
    'kochzeit': 120,
}

def format_kochzeit(minuten_gesamt):
    """Wandelt Minuten in ein 'X Std. Y Min.' Format um."""
    if not minuten_gesamt or minuten_gesamt <= 0:
        return "0 Min."
    
    stunden = minuten_gesamt // 60
    minuten = minuten_gesamt % 60
    
    parts = []
    if stunden > 0:
        parts.append(f"{stunden} Std.")
    if minuten > 0:
        parts.append(f"{minuten} Min.")
    
    return " ".join(parts)

# Reuse MongoClient connection pool globally
_mongo_client = None

def get_collection():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(MONGO_URI)
    db = _mongo_client['rezeptdb']
    return db['essen']

def get_next_id(collection):
    highest = collection.find_one(sort=[("id", -1)])
    if highest and 'id' in highest:
        return highest["id"] + 1
    return 1

def init_db():
    col = get_collection()
    if col.count_documents({}) == 0:
        doc = PREDEFINED_Essen.copy()
        doc['id'] = 1
        col.insert_one(doc)

def add_essen(name, personenanzahl, zutaten, description, kochanweisung, kochzeit):
    col = get_collection()
    new_id = get_next_id(col)
    doc = {
        'id': new_id,
        'name': name,
        'personenanzahl': personenanzahl,
        'zutaten': zutaten,
        'description': description,
        'kochanweisung': kochanweisung,
        'kochzeit': kochzeit
    }
    result = col.insert_one(doc)
    return result.acknowledged

def get_all_essen():
    col = get_collection()
    cursor = col.find({}, {'_id': 0}).sort('id', 1)
    essen_liste = []
    for doc in cursor:
        minuten_roh = doc.get('kochzeit', 0)
        essen_liste.append({
            'id': doc.get('id'),
            'name': doc.get('name'),
            'personenanzahl': doc.get('personenanzahl'),
            'zutaten': doc.get('zutaten', []),
            'description': doc.get('description'),
            'kochanweisung': doc.get('kochanweisung'),
            'kochzeit_min': minuten_roh,
            'kochzeit': format_kochzeit(minuten_roh)
        })
    return essen_liste

def get_essen(essen_id):
    col = get_collection()
    doc = col.find_one({'id': int(essen_id)}, {'_id': 0})
    if doc:
        minuten_roh = doc.get('kochzeit', 0)
        return {
            'id': doc.get('id'),
            'name': doc.get('name'),
            'personenanzahl': doc.get('personenanzahl'),
            'zutaten': doc.get('zutaten', []),
            'description': doc.get('description'),
            'kochanweisung': doc.get('kochanweisung'),
            'kochzeit_min': minuten_roh,
            'kochzeit': format_kochzeit(minuten_roh)
        }
    return None

def delete_essen(essen_id):
    col = get_collection()
    result = col.delete_one({'id': int(essen_id)})
    return result.deleted_count > 0

def update_essen(essen_id, name, personenanzahl, zutaten, description, kochanweisung, kochzeit):
    col = get_collection()
    result = col.update_one(
        {'id': int(essen_id)},
        {'$set': {
            'name': name,
            'personenanzahl': personenanzahl,
            'zutaten': zutaten,
            'description': description,
            'kochanweisung': kochanweisung,
            'kochzeit': kochzeit
        }}
    )
    return result.modified_count > 0 or result.matched_count > 0