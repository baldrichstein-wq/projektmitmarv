import os
import pymongo
from pymongo import MongoClient

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

def get_next_id(collection):
    highest = collection.find_one(sort=[("id", -1)])
    if highest and 'id' in highest:
        return highest["id"] + 1
    return 1

def init_db():
    col = get_collection()
    if col.count_documents({}) == 0:
        doc = PREDEFINED_WINE.copy()
        doc['id'] = 1
        col.insert_one(doc)

def add_wine(name, liter, ingredients, description, brewing_instructions, brewing_time, alcohol_content):
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
        'alcohol_content': alcohol_content
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