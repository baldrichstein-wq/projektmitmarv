import os
import time
import psycopg2
from psycopg2 import pool
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

# GEAENDERT 07.08.2026 (Stefan): Vorher hat jede einzelne Funktion (init_db, benutzer_anmelden,
# ...) ueber get_connection() eine KOMPLETT NEUE psycopg2-Verbindung aufgebaut und am Ende
# wieder geschlossen. Das kostet bei jedem Request unnoetig Zeit (TCP-Handshake + Postgres-
# Authentifizierung) und kann bei kurzzeitig hoher Last viele parallele Verbindungen erzeugen.
# Jetzt wird stattdessen ein Verbindungs-Pool einmalig pro Prozess aufgebaut; get_connection()
# leiht sich eine Verbindung aus dem Pool, release_connection() gibt sie zurueck statt sie zu
# schliessen. Der Pool wird lazy (beim ersten Zugriff) aufgebaut, damit der Retry-Mechanismus
# (Postgres-Container ist beim Start des Backends evtl. noch nicht bereit) weiterhin funktioniert.
_connection_pool = None

def _get_pool():
    """Baut den Verbindungs-Pool beim ersten Aufruf auf (mit Retry, falls Postgres noch startet)."""
    global _connection_pool
    if _connection_pool is not None:
        return _connection_pool

    retries = 10
    while retries > 0:
        try:
            # minconn=1: mindestens eine offene Verbindung bereithalten
            # maxconn=10: reicht fuer einen Gunicorn-Worker mit synchronen Requests bei weitem aus
            _connection_pool = psycopg2.pool.SimpleConnectionPool(1, 10, DATABASE_URL)
            return _connection_pool
        except Exception as e:
            retries -= 1
            print(f"PostgreSQL noch nicht bereit. Warte 2s... ({retries} Versuche übrig). Fehler: {e}")
            time.sleep(2)
    raise Exception("Konnte keine Verbindung zur PostgreSQL-Datenbank aufbauen.")

def get_connection():
    """Leiht eine Verbindung aus dem Pool aus."""
    return _get_pool().getconn()

def release_connection(conn):
    """Gibt eine ausgeliehene Verbindung an den Pool zurueck, statt sie zu schliessen."""
    if conn:
        _get_pool().putconn(conn)

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
        release_connection(conn)

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
        release_connection(conn)

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
        release_connection(conn)

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
        release_connection(conn)

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
        release_connection(conn)

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
        release_connection(conn)

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
        release_connection(conn)
