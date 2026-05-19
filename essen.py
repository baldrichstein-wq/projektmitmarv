import sqlite3
import json

DB_FILE = 'essen.db'

# Standardrezept für die Initialisierung
PREDEFINED_Essen = {
    'name': 'Kaiserliches Kräuter-Kaninchen mit Rosmarin',
    'personenanzahl': 4,
    'Zutaten': [
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
    'Kochzeit': 120, # In Minuten angegeben (2 Stunden)
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

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS essen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                personenanzahl INTEGER,
                Zutaten TEXT NOT NULL,
                description TEXT,
                kochanweisung TEXT,
                Kochzeit INTEGER
            )
        ''')

        cursor.execute('SELECT COUNT(*) FROM essen')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO essen (name, personenanzahl, Zutaten, description, kochanweisung, Kochzeit)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                PREDEFINED_Essen['name'],
                PREDEFINED_Essen['personenanzahl'],
                json.dumps(PREDEFINED_Essen['Zutaten']),
                PREDEFINED_Essen['description'],
                PREDEFINED_Essen['kochanweisung'],
                PREDEFINED_Essen['Kochzeit']
            ))
            conn.commit()

def add_essen(name, personenanzahl, Zutaten, description, kochanweisung, Kochzeit):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO essen (name, personenanzahl, Zutaten, description, kochanweisung, Kochzeit)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            name,
            personenanzahl,
            json.dumps(Zutaten),
            description,
            kochanweisung,
            Kochzeit
        ))
        conn.commit()
        return cursor.lastrowid

def get_all_essen():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, personenanzahl, Zutaten, description, kochanweisung, Kochzeit FROM essen ORDER BY id')
    rows = cursor.fetchall()
    conn.close()
    
    essen_liste = []
    for row in rows:
        minuten_roh = row[6]
        essen_liste.append({
            'id': row[0],
            'name': row[1],
            'personenanzahl': row[2],
            'zutaten': json.loads(row[3]),
            'description': row[4],
            'kochanweisung': row[5],
            'kochzeit_min': minuten_roh,
            'kochzeit': format_kochzeit(minuten_roh)
        })
    return essen_liste

def get_essen(essen_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, personenanzahl, Zutaten, description, kochanweisung, Kochzeit FROM essen WHERE id = ?', (essen_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        minuten_roh = row[6]
        return {
            'id': row[0],
            'name': row[1],
            'personenanzahl': row[2],
            'zutaten': json.loads(row[3]),
            'description': row[4],
            'kochanweisung': row[5],
            'kochzeit_min': minuten_roh,
            'kochzeit': format_kochzeit(minuten_roh)
        }
    return None

def delete_essen(essen_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM essen WHERE id = ?', (essen_id,))
        conn.commit()
        return cursor.rowcount > 0

def update_essen(essen_id, name, personenanzahl, zutaten, description, kochanweisung, kochzeit):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE essen
            SET name = ?, personenanzahl = ?, zutaten = ?, description = ?, kochanweisung = ?, kochzeit = ?
            WHERE id = ?
        ''', (
            name,
            personenanzahl,
            json.dumps(Zutaten),
            description,
            kochanweisung,
            Kochzeit,
            essen_id
        ))
        conn.commit()
        return cursor.rowcount > 0