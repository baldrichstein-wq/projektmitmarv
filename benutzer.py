import os
import re
import time
import psycopg2
from psycopg2 import pool
import pyotp
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://admin:adminpass@localhost:5432/benutzerdb')

# NEU 11.08.2026 (Stefan): Mindestanforderungen an neue Passwoerter (Registrierung + vom Admin
# angelegte Benutzer). Greift nur bei NEU angelegten Konten -- die beiden Seed-Benutzer aus
# init_db() (admin123/benutzer123) werden direkt gehasht angelegt und laufen nicht durch diese
# Pruefung, damit der lokale Erstzugang wie bisher funktioniert.
def passwort_ist_stark(passwort):
    """Prueft Mindestanforderungen an ein neues Passwort. Gibt (ok, fehlermeldung) zurueck."""
    if len(passwort) < 8:
        return False, 'Das Passwort muss mindestens 8 Zeichen lang sein.'
    if not re.search(r'[A-Z]', passwort):
        return False, 'Das Passwort muss mindestens einen Großbuchstaben enthalten.'
    if not re.search(r'[a-z]', passwort):
        return False, 'Das Passwort muss mindestens einen Kleinbuchstaben enthalten.'
    if not re.search(r'\d', passwort):
        return False, 'Das Passwort muss mindestens eine Ziffer enthalten.'
    return True, ''

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

                # NEU 11.08.2026 (Stefan): Spalten fuer TOTP-2FA. "CREATE TABLE IF NOT EXISTS"
                # oben legt sie nur bei einer brandneuen Tabelle an -- auf einer bereits
                # bestehenden Installation (AWS/NAS) braucht es zusaetzlich ein ALTER TABLE,
                # sonst fehlen die Spalten dort weiterhin.
                cursor.execute('ALTER TABLE benutzer ADD COLUMN IF NOT EXISTS totp_secret VARCHAR(64)')
                cursor.execute('ALTER TABLE benutzer ADD COLUMN IF NOT EXISTS totp_enabled BOOLEAN NOT NULL DEFAULT FALSE')

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
    stark_genug, fehler = passwort_ist_stark(passwort)
    if not stark_genug:
        return False, fehler

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
                cursor.execute('SELECT id, name, email, role, totp_enabled FROM benutzer ORDER BY id')
                rows = cursor.fetchall()

        return [
            {
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'role': normalize_role(row[3]),
                'totp_enabled': bool(row[4])
            }
            for row in rows
        ]
    finally:
        release_connection(conn)

def get_user_by_email(email):
    """Gibt Name/Rolle zu einer E-Mail zurück (ohne Passwort-Prüfung, z.B. nach 2FA-Login)."""
    conn = None
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT id, name, email, role FROM benutzer WHERE email = %s', (email,))
                row = cursor.fetchone()
        if not row:
            return None
        return {'id': row[0], 'name': row[1], 'email': row[2], 'role': normalize_role(row[3])}
    finally:
        release_connection(conn)

# --- TOTP Zwei-Faktor-Authentifizierung ---
# NEU 11.08.2026 (Stefan): Bewusst OHNE Backup-/Recovery-Codes umgesetzt -- das Projekt hat
# keine eigene E-Mail-Domain, ueber die man sonst Recovery-Codes verschicken wuerde, und ein
# separates "Codes sicher aufbewahren"-UI waere fuer dieses kleine Team-Projekt Overkill.
# Stattdessen kann ein admin 2FA fuer einen Benutzer zuruecksetzen (siehe totp_admin_reset),
# falls z.B. das Handy mit der Authenticator-App verloren geht.

def totp_secret_generieren(email, issuer='Rezept&Brau'):
    """Erzeugt ein neues TOTP-Secret, speichert es (2FA bleibt bis zur Bestaetigung inaktiv)
    und gibt (secret, otpauth_uri) zurueck."""
    secret = pyotp.random_base32()
    conn = None
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    'UPDATE benutzer SET totp_secret = %s, totp_enabled = FALSE WHERE email = %s',
                    (secret, email)
                )
        uri = pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer)
        return secret, uri
    finally:
        release_connection(conn)

def totp_aktivieren(email, code):
    """Prüft den vom Nutzer eingegebenen Code gegen das zuvor erzeugte Secret und schaltet
    2FA erst dann scharf -- so wird sichergestellt, dass die Authenticator-App den Code auch
    wirklich korrekt erzeugt, bevor der Nutzer beim naechsten Login davon abhaengt."""
    conn = None
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT totp_secret FROM benutzer WHERE email = %s', (email,))
                row = cursor.fetchone()
                if not row or not row[0]:
                    return False
                if not pyotp.TOTP(row[0]).verify(code, valid_window=1):
                    return False
                cursor.execute('UPDATE benutzer SET totp_enabled = TRUE WHERE email = %s', (email,))
        return True
    finally:
        release_connection(conn)

def totp_deaktivieren(email):
    conn = None
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    'UPDATE benutzer SET totp_secret = NULL, totp_enabled = FALSE WHERE email = %s',
                    (email,)
                )
        return True
    finally:
        release_connection(conn)

def totp_admin_reset(user_id):
    """Setzt 2FA fuer einen Benutzer zurueck (Admin-Aktion, z.B. bei Geraeteverlust)."""
    conn = None
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    'UPDATE benutzer SET totp_secret = NULL, totp_enabled = FALSE WHERE id = %s',
                    (user_id,)
                )
                success = cursor.rowcount > 0
        return success
    finally:
        release_connection(conn)

def totp_status(email):
    conn = None
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT totp_enabled FROM benutzer WHERE email = %s', (email,))
                row = cursor.fetchone()
        return bool(row and row[0])
    finally:
        release_connection(conn)

def totp_code_pruefen(email, code):
    conn = None
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT totp_secret, totp_enabled FROM benutzer WHERE email = %s', (email,))
                row = cursor.fetchone()
        if not row or not row[0] or not row[1]:
            return False
        return pyotp.TOTP(row[0]).verify(code, valid_window=1)
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
