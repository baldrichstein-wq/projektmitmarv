import sqlite3
import json

DB_FILE = 'essen.db'

PREDEFINED_Essen = {
    'name': 'Kaiserliches Kräuter-Kaninchen mit Rosmarin',
    'Zutaten': [
        '1/2 Kaninchen',
        '4 Zweige frischer Rosmarin',
        '2 Zweige Thymian',
        '1 Zehe Knoplauch (zerdrückt)',
        'Salz & Pfeffer (wie von der Dame verlangt! )',
        'etwas Butter oder Olivenöl',
        'Bräter'
    ],
    'description': 'Ein köstliches Gericht, das die Aromen von frischen Kräutern und zartem Kaninchen vereint. Perfekt für ein festliches Mahl oder einen besonderen Anlass.',
    'kochanweisung': 'Das Fleisch mit Salz, Pfeffer und dem zerdrückten Knoblauch kräftig einmassieren. Die Kräuter fein hacken und unter die Gewürzmischung rühren. Das Kaninchen damit bestreichen und mindestens 2 Stunden ziehen lassen. Bei mittlerer Hitze im Ofen goldbraun braten, bis es nach Sieg riecht!',
    'Kochzeit': 2,
}


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
                Kochzeit INTEGER,
            )
        ''')

        cursor.execute('SELECT COUNT(*) FROM essen')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO essen (name, Zutaten, description, kochanweisung, Kochzeit)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                PREDEFINED_Essen['name'],
                json.dumps(PREDEFINED_Essen['Zutaten']),
                PREDEFINED_Essen['description'],
                PREDEFINED_Essen['kochanweisung'],
                PREDEFINED_Essen['Kochzeit'],
            ))
            conn.commit()


def add_essen(name, Zutaten, description, kochanweisung, Kochzeit):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO essen (name, Zutaten, description, kochanweisung, Kochzeit)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            name,
            json.dumps(Zutaten),
            description,
            kochanweisung,
            Kochzeit,
        ))
        conn.commit()
        return cursor.lastrowid


def get_all_essen():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, Zutaten, description, kochanweisung, Kochzeit FROM essen ORDER BY id')
    rows = cursor.fetchall()
    conn.close()
    essen= []
    for row in rows:
        essen.append({
            'id': row[0],
            'name': row[1],
            'ingredients': json.loads(row[2]),
            'description': row[3],
            'kochanweisung': row[4],
            'Kochzeit': row[5]
        })
    return essen


def delete_essen(essen_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM essen WHERE id = ?', (essen_id,))
        conn.commit()
        return cursor.rowcount > 0


def get_essen(essen_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, Zutaten, description, kochanweisung, Kochzeit FROM essen WHERE id = ?', (essen_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'name': row[1],
            'ingredients': json.loads(row[2]),
            'description': row[3],
            'kochanweisung': row[4],
            'Kochzeit': row[5],
        }
    return None
