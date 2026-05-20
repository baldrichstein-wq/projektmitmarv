import sqlite3
from flask import session
# Werkzeug nutzt standardmäßig sichere Algorithmen wie Scrypt oder PBKDF2
from werkzeug.security import generate_password_hash, check_password_hash

DB_FILE = 'benutzer.db'

# --- Rechteverwaltung ---
RECHTE_PRO_ROLE = {
    'admin': ['lesen', 'schreiben', 'aendern', 'loeschen', 'benutzer_verwalten'],
    'benutzer': ['lesen', 'schreiben', 'aendern'],
    'gast': ['lesen'],
}

def normalize_role(role):
    """Vereinheitlicht alte und neue Rollennamen."""
    if not role:
        return 'gast'
    role_clean = str(role).strip().lower()
    if role_clean in ['user', 'benutzer']:
        return 'benutzer'
    if role_clean in RECHTE_PRO_ROLE:
        return role_clean
    return 'gast'

def rechte_fuer_role(role):
    """Gibt alle Rechte einer Rolle zurück."""
    role = normalize_role(role)
    return RECHTE_PRO_ROLE.get(role, RECHTE_PRO_ROLE['gast']) 

def hat_recht(user, recht):
    """Prüft, ob ein Benutzer ein bestimmtes Recht hat."""
    role = 'benutzer'
    if user:
        role = user.get('role', 'benutzer')
    return recht in rechte_fuer_role(role)

def ist_admin(user):
    """Prüft, ob der Benutzer Administrator ist."""
    return user is not None and normalize_role(user.get('role')) == 'admin'

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
            role TEXT DEFAULT 'benutzer'
        )
    ''')
    
    cursor.execute("PRAGMA table_info(benutzer)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'role' not in columns:
        cursor.execute("ALTER TABLE benutzer ADD COLUMN role TEXT DEFAULT 'benutzer'")

    cursor.execute('SELECT COUNT(*) FROM benutzer')
    if cursor.fetchone()[0] == 0:
        # Passwörter werden vor dem Einfügen unumkehrbar gehasht
        admin_hash = generate_password_hash('admin123')
        benutzer_hash = generate_password_hash('benutzer123')
        
        cursor.executemany('''
            INSERT INTO benutzer (name, email, password, role)
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
    cursor.execute('SELECT id, name, email, password, role FROM benutzer WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    # check_password_hash vergleicht das Klartext-Passwort mit dem gespeicherten Hash
    if user and check_password_hash(user[3], passwort):
        return {
            'id': user[0],
            'name': user[1],
            'email': user[2],
            'role': normalize_role(user[4]) 
        }
    return None

def benutzer_anlegen(name, email, passwort, role="benutzer"):
    """Fügt einen neuen Benutzer mit gehashtem Passwort hinzu."""
    # Falls role None oder leer ist, Standardwert nutzen
    if not role:
        role = "benutzer"
    
    role = normalize_role(role)
    hashed_password = generate_password_hash(passwort)
        
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO benutzer (name, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (name, email, hashed_password, role))
        conn.commit()
        return True, f"Benutzer {name} als '{role}' erfolgreich angelegt!"
    except sqlite3.IntegrityError:
        return False, f"Fehler: Diese E-Mail '{email}' existiert bereits."
    finally:
        conn.close()
def loesche_benutzer(user_id):
    """Löscht einen Benutzer basierend auf der ID."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM benutzer WHERE id = ?', (user_id,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success

def get_all_users():
    """Gibt eine Liste aller Benutzer zurück."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, role FROM benutzer ORDER BY id')
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'role': normalize_role(row[3])
        }
        for row in rows
    ]
def rolle_aendern(user_id, neue_role):
    """Ändert die Rolle eines Benutzers basierend auf der ID."""
    neue_rolle = normalize_role(neue_rolle)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE benutzer SET role = ? WHERE id = ?', (neue_role, user_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success


def mache_zu_admin(email):
    """Vergibt Administratorrechte."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE benutzer SET role = "admin" WHERE email = ?', (email,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success
