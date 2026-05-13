import sqlite3
from flask import session
# Werkzeug nutzt standardmäßig sichere Algorithmen wie Scrypt oder PBKDF2
from werkzeug.security import generate_password_hash, check_password_hash

DB_FILE = 'benutzer.db'

# --- Rechteverwaltung ---
RECHTE_PRO_ROLLE = {
    'admin': ['lesen', 'schreiben', 'aendern', 'loeschen', 'benutzer_verwalten'],
    'benutzer': ['lesen', 'schreiben', 'aendern'],
    'gast': ['lesen'],
}

def normalize_rolle(rolle):
    """Vereinheitlicht alte und neue Rollennamen."""
    if not rolle:
        return 'gast'
    rolle_clean = str(rolle).strip().lower()
    if rolle_clean in ['user', 'benutzer']:
        return 'benutzer'
    if rolle_clean in RECHTE_PRO_ROLLE:
        return rolle_clean
    return 'gast'

def rechte_fuer_rolle(rolle):
    """Gibt alle Rechte einer Rolle zurück."""
    rolle = normalize_rolle(rolle)
    return RECHTE_PRO_ROLLE.get(rolle, RECHTE_PRO_ROLLE['gast']) 

def hat_recht(user, recht):
    """Prüft, ob ein Benutzer ein bestimmtes Recht hat."""
    rolle = 'gast'
    if user:
        rolle = user.get('rolle', 'gast')
    return recht in rechte_fuer_rolle(rolle)

def ist_admin(user):
    """Prüft, ob der Benutzer Administrator ist."""
    return user is not None and normalize_rolle(user.get('rolle')) == 'admin'

def init_db():
    """Erstellt die Datenbank und Beispiel-Logins mit Password-Hashing."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS benutzer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            rolle TEXT DEFAULT 'benutzer'
        )
    ''')
    
    cursor.execute("PRAGMA table_info(benutzer)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'rolle' not in columns:
        cursor.execute("ALTER TABLE benutzer ADD COLUMN rolle TEXT DEFAULT 'benutzer'")

    cursor.execute('SELECT COUNT(*) FROM benutzer')
    if cursor.fetchone()[0] == 0:
        # Passwörter werden vor dem Einfügen unumkehrbar gehasht
        admin_hash = generate_password_hash('admin123')
        benutzer_hash = generate_password_hash('benutzer123')
        
        cursor.executemany('''
            INSERT INTO benutzer (name, email, password, rolle)
            VALUES (?, ?, ?, ?)
        ''', [
            ('Admin', 'admin@rezepte.de', admin_hash, 'admin'),
            ('Benutzer', 'benutzer@rezepte.de', benutzer_hash, 'benutzer')
        ])
    
    conn.commit()
    conn.close()

def benutzer_anmelden(email, passwort):
    """Überprüft die Anmeldedaten mithilfe von Hash-Vergleich."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Nur anhand der E-Mail suchen, da der Passwort-String in der DB ein Hash ist
    cursor.execute('SELECT id, name, email, password, rolle FROM benutzer WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    # check_password_hash vergleicht das Klartext-Passwort mit dem gespeicherten Hash
    if user and check_password_hash(user[3], passwort):
        return {
            'id': user[0],
            'name': user[1],
            'email': user[2],
            'rolle': normalize_rolle(user[4]) 
        }
    return None

def benutzer_anlegen(name, email, passwort, rolle="benutzer"):
    """Fügt einen neuen Benutzer mit gehashtem Passwort hinzu."""
    # Falls rolle None oder leer ist, Standardwert nutzen
    if not rolle:
        rolle = "benutzer"
    
    rolle = normalize_rolle(rolle)
    hashed_password = generate_password_hash(passwort)
        
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO benutzer (name, email, password, rolle)
            VALUES (?, ?, ?, ?)
        """, (name, email, hashed_password, rolle))
        conn.commit()
        return True, f"Benutzer {name} als '{rolle}' erfolgreich angelegt!"
    except sqlite3.IntegrityError:
        return False, f"Fehler: Diese E-Mail '{email}' existiert bereits."
    finally:
        conn.close()

def get_all_users():
    """Gibt eine Liste aller Benutzer zurück."""
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
            'rolle': normalize_rolle(row[3])
        }
        for row in rows
    ]
def rolle_aendern(user_id, neue_rolle):
    """Ändert die Rolle eines Benutzers basierend auf der ID."""
    neue_rolle = normalize_rolle(neue_rolle)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE benutzer SET rolle = ? WHERE id = ?', (neue_rolle, user_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success

def mache_zu_admin(email):
    """Vergibt Administratorrechte."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE benutzer SET rolle = "admin" WHERE email = ?', (email,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success