import sqlite3

DB_FILE = 'benutzer.db'

def init_db():
    """Erstellt die Datenbank mit der Spalte 'rolle'."""
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
    """Überprüft die Anmeldedaten eines Benutzers."""
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
    """Gibt die Standardrechte für Besucher zurück."""
    return {
        'rolle': 'user',
        'rechte': ['lesen']
    } 

def benutzer_anlegen(name, email, passwort, rolle="user"):
    """Fügt einen neuen Benutzer hinzu. (Standardrolle: user)."""
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
    return [
        {
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'rolle': row[3]
        }
        for row in rows
    ]

def mache_zu_admin(email):
    """Vergibt Administratorrechte an eine vorhandene E-Mail-Adresse."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE benutzer SET rolle = "admin" WHERE email = ?', (email,))

    if cursor.rowcount > 0:
        print(f"Rechte aktualisiert: {email} ist jetzt Administrator.")
    else:
        print(f"Fehler: kein benutzer mit der E-Mail {email} gefunden.")

    conn.commit()
    conn.close()

# --- Programmstart ---
if __name__ == "__main__":
    init_db()

    benutzer_anlegen("max Mustermann", "max@kochen.de", "superSicher123")
    mache_zu_admin("max@kochen.de")
    benutzer_anlegen("Admin Chef", "chef@firma.de", "geheim123", rolle="admin")
