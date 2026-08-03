import os
import time
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://admin:adminpass@localhost:5432/benutzerdb')

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

def get_connection():
    """Gibt eine Verbindung zur PostgreSQL-Datenbank mit Retry-Logik zurück."""
    retries = 10
    while retries > 0:
        try:
            return psycopg2.connect(DATABASE_URL)
        except Exception as e:
            retries -= 1
            print(f"PostgreSQL noch nicht bereit. Warte 2s... ({retries} Versuche übrig). Fehler: {e}")
            time.sleep(2)
    raise Exception("Konnte keine Verbindung zur PostgreSQL-Datenbank aufbauen.")

def init_db():
    """Erstellt die Tabelle und initialisiert die Benutzer in PostgreSQL."""
    conn = None
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS benutzer (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        email VARCHAR(100) NOT NULL UNIQUE,
                        password VARCHAR(255) NOT NULL,
                        role VARCHAR(50) DEFAULT 'benutzer'
                    )
                ''')
                
                cursor.execute('SELECT COUNT(*) FROM benutzer')
                if cursor.fetchone()[0] == 0:
                    admin_hash = generate_password_hash('admin123')
                    benutzer_hash = generate_password_hash('benutzer123')
                    
                    cursor.executemany('''
                        INSERT INTO benutzer (name, email, password, role)
                        VALUES (%s, %s, %s, %s)
                    ''', [
                        ('Admin', 'admin@rezepte.de', admin_hash, 'admin'),
                        ('Benutzer', 'benutzer@rezepte.de', benutzer_hash, 'benutzer')
                    ])
    finally:
        if conn:
            conn.close()

def benutzer_anmelden(email, passwort):
    """Überprüft die Anmeldedaten."""
    conn = None
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT id, name, email, password, role FROM benutzer WHERE email = %s', (email,))
                user = cursor.fetchone()
                
        if user and check_password_hash(user[3], passwort):
            return {
                'id': user[0],
                'name': user[1],
                'email': user[2],
                'role': normalize_role(user[4]) 
            }
        return None
    finally:
        if conn:
            conn.close()

def benutzer_anlegen(name, email, passwort, role="benutzer"):
    """Fügt einen neuen Benutzer hinzu."""
    if not role:
        role = "benutzer"
    role = normalize_role(role)
    hashed_password = generate_password_hash(passwort)
        
    conn = None
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO benutzer (name, email, password, role)
                    VALUES (%s, %s, %s, %s)
                """, (name, email, hashed_password, role))
        return True, f"Benutzer {name} als '{role}' erfolgreich angelegt!"
    except psycopg2.IntegrityError:
        return False, f"Fehler: Diese E-Mail '{email}' existiert bereits."
    finally:
        if conn:
            conn.close()

def loesche_benutzer(user_id):
    """Löscht einen Benutzer."""
    conn = None
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute('DELETE FROM benutzer WHERE id = %s', (user_id,))
                success = cursor.rowcount > 0
        return success
    finally:
        if conn:
            conn.close()

def get_all_users():
    """Gibt alle Benutzer zurück."""
    conn = None
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT id, name, email, role FROM benutzer ORDER BY id')
                rows = cursor.fetchall()
        
        return [
            {
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'role': normalize_role(row[3])
            }
            for row in rows
        ]
    finally:
        if conn:
            conn.close()

def rolle_aendern(user_id, neue_role):
    """Ändert die Rolle eines Benutzers."""
    neue_rolle = normalize_role(neue_role)
    conn = None
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute('UPDATE benutzer SET role = %s WHERE id = %s', (neue_rolle, user_id))
                success = cursor.rowcount > 0
        return success
    finally:
        if conn:
            conn.close()

def mache_zu_admin(email):
    """Vergibt Administratorrechte."""
    conn = None
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute('UPDATE benutzer SET role = \'admin\' WHERE email = %s', (email,))
                success = cursor.rowcount > 0
        return success
    finally:
        if conn:
            conn.close()
