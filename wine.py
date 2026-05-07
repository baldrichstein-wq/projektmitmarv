import sqlite3
import json

DB_FILE = 'wines.db'

PREDEFINED_WINE = {
    'name': 'Holunder Johannisbeer Wein',
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
                INSERT INTO wines (name, ingredients, description, brewing_instructions, brewing_time, alcohol_content)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                PREDEFINED_WINE['name'],
                json.dumps(PREDEFINED_WINE['ingredients']),
                PREDEFINED_WINE['description'],
                PREDEFINED_WINE['brewing_instructions'],
                PREDEFINED_WINE['brewing_time'],
                PREDEFINED_WINE['alcohol_content'],
            ))
            conn.commit()


def add_wine(name, ingredients, description, brewing_instructions, brewing_time, alcohol_content):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO wines (name, ingredients, description, brewing_instructions, brewing_time, alcohol_content)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            name,
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
    cursor.execute('SELECT id, name, ingredients, description, brewing_instructions, brewing_time, alcohol_content FROM wines ORDER BY id')
    rows = cursor.fetchall()
    conn.close()
    wines = []
    for row in rows:
        wines.append({
            'id': row[0],
            'name': row[1],
            'ingredients': json.loads(row[2]),
            'description': row[3],
            'brewing_instructions': row[4],
            'brewing_time': row[5],
            'alcohol_content': row[6],
        })
    return wines


def delete_wine(wine_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM wines WHERE id = ?', (wine_id,))
        conn.commit()
        return cursor.rowcount > 0


def get_wine(wine_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, ingredients, description, brewing_instructions, brewing_time, alcohol_content FROM wines WHERE id = ?', (wine_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'name': row[1],
            'ingredients': json.loads(row[2]),
            'description': row[3],
            'brewing_instructions': row[4],
            'brewing_time': row[5],
            'alcohol_content': row[6],
        }
    return None
