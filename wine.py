import sqlite3
import json

DB_FILE = 'wines.db'

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

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                liter TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                description TEXT,
                brewing_instructions TEXT,
                brewing_time INTEGER,
                alcohol_content REAL
            )
        ''')

        cursor.execute('SELECT COUNT(*) FROM wines')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO wines (name, liter, ingredients, description, brewing_instructions, brewing_time, alcohol_content)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                PREDEFINED_WINE['name'],
                PREDEFINED_WINE['liter'],
                json.dumps(PREDEFINED_WINE['ingredients']),
                PREDEFINED_WINE['description'],
                PREDEFINED_WINE['brewing_instructions'],
                PREDEFINED_WINE['brewing_time'],
                PREDEFINED_WINE['alcohol_content'],
            ))
            conn.commit()

def add_wine(name, liter, ingredients, description, brewing_instructions, brewing_time, alcohol_content):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO wines (name, liter, ingredients, description, brewing_instructions, brewing_time, alcohol_content)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            name,
            liter,
            json.dumps(ingredients),
            description,
            brewing_instructions,
            brewing_time,
            alcohol_content,
        ))
        conn.commit()
        return cursor.lastrowid

def get_all_wines():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Wichtig: liter muss im SELECT enthalten sein
    cursor.execute('SELECT id, name, liter, ingredients, description, brewing_instructions, brewing_time, alcohol_content FROM wines ORDER BY id')
    rows = cursor.fetchall()
    conn.close()
    wines = []
    for row in rows:
        wines.append({
            'id': row[0],
            'name': row[1],
            'liter': row[2],
            'ingredients': json.loads(row[3]),
            'description': row[4],
            'brewing_instructions': row[5],
            'brewing_time': row[6],
            'alcohol_content': row[7],
        })
    return wines

def get_wine_by_id(wine_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, liter, ingredients, description, brewing_instructions, brewing_time, alcohol_content FROM wines WHERE id = ?', (wine_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'name': row[1],
            'liter': row[2],
            'ingredients': json.loads(row[3]),
            'description': row[4],
            'brewing_instructions': row[5],
            'brewing_time': row[6],
            'alcohol_content': row[7],
        }
    return None

def delete_wine(wine_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM wines WHERE id = ?', (wine_id,))
        conn.commit()
        return cursor.rowcount > 0

def update_wine(wine_id, name, liter, ingredients, description, brewing_instructions, brewing_time, alcohol_content):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE wines
            SET name = ?, liter = ?, ingredients = ?, description = ?, brewing_instructions = ?, brewing_time = ?, alcohol_content = ?
            WHERE id = ?
        ''', (
            name,
            liter,
            json.dumps(ingredients),
            description,
            brewing_instructions,
            brewing_time,
            alcohol_content,
            wine_id
        ))
        conn.commit()
        return cursor.rowcount > 0