import sqlite3

DB_FILE = 'benutzer.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS benutzer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            rolle TEXT DEFAULT 'user'
        )
    ''')
    conn.commit()
    conn.close()

def nutzer_anmeldung(email, passwort):
    """Überprüft Anmeldedaten und gibt User-Daten zurück (ohne Session)."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, rolle FROM benutzer WHERE email = ? AND password = ?', (email, passwort))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {
            'id': user[0],
            'name': user[1],
            'email': user[2],
            'rolle': user[3]
        }
    return None

def besucher_rechten():
    return {
        'rolle': 'user',
        'rechte': ['lesen']
    } 

def benutzer_anlegen(name, email, passwort, rolle="user"):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO benutzer (name, email, password, rolle)
            VALUES (?, ?, ?, ?)
        ''', (name, email, passwort, rolle))
        conn.commit()
        return True, f"Benutzer {name} als '{rolle}' erfolgreich angelegt!"
    except sqlite3.IntegrityError:
        return False, f"Fehler: Diese E-Mail '{email}' existiert bereits."
    finally:
        conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, rolle FROM benutzer ORDER BY id')
    rows = cursor.fetchall()
    conn.close()
    return [{'id': r[0], 'name': r[1], 'email': r[2], 'rolle': r[3]} for r in rows]

def mache_zu_admin(email):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE benutzer SET rolle = "admin" WHERE email = ?', (email,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()