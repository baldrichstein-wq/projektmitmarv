import sqlite3
import json
DB_FILE = 'essen.db'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS essen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                Zutaten TEXT NOT NULL,
                description TEXT,
                kochanweisung TEXT,
                Kochzeit INTEGER
            )
        ''') # Komma nach INTEGER entfernt

        cursor.execute('SELECT COUNT(*) FROM essen')
        if cursor.fetchone()[0] == 0:
            # Beispiel-Essen einfügen... (Logik wie vorher)
            pass

def add_essen(name, zutaten, description, kochanweisung, kochzeit):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO essen (name, Zutaten, description, kochanweisung, Kochzeit)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, json.dumps(zutaten), description, kochanweisung, kochzeit))
        conn.commit()
        return cursor.lastrowid

def get_all_essen():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, Zutaten, description, kochanweisung, Kochzeit FROM essen ORDER BY id')
    rows = cursor.fetchall()
    conn.close()
    return [{
        'id': r[0], 'name': r[1], 'ingredients': json.loads(r[2]),
        'description': r[3], 'kochanweisung': r[4], 'Kochzeit': r[5]
    } for r in rows]

def delete_essen(essen_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM essen WHERE id = ?', (essen_id,))
        conn.commit()
        return cursor.rowcount > 0