import sqlite3

def init_db():
    """Erstellt die Datenbank mit der Spalte 'rolle'."""
    conn = sqlite3.connect('benutzer.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS benutzer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            rolle TEXT DEFAULT 'user' -- Hier wurde die Spalte hinzugefügt!
        )
    ''')
    conn.commit()
    conn.close()

def benutzer_anlegen(name, email, passwort, rolle="user"): 
    """Fügt einen neuen Benutzer hinzu. (Standardrolle: user)."""
    try:
        conn = sqlite3.connect('benutzer.db')
        cursor = conn.cursor()
        # Wichtig: 4 Spalten brauchen auch 4 Platzhalter (?)
        cursor.execute('''
            INSERT INTO benutzer (name, email, password, rolle) 
            VALUES (?, ?, ?, ?)
        ''', (name, email, passwort, rolle))
        conn.commit()
        print(f"Benutzer {name} als '{rolle}' erfolgreich angelegt!")
    except sqlite3.IntegrityError:
        print(f"Fehler: Diese E-Mail '{email}' existiert bereits.")
    finally:
        conn.close()

def mache_zu_admin(email):
    """Vergibt Administratorrechte an eine vorhandene E-Mail-Adresse."""
    conn = sqlite3.connect('benutzer.db')
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

    # 1. Normalen Benutzer anlegen
    benutzer_anlegen("max Mustermann", "max@kochen.de", "superSicher123")

    # 2. Diesen Benutzer zum Admin befördern
    mache_zu_admin("max@kochen.de")

    # 3. Optional: Direkt einen Admin erstellen
    benutzer_anlegen("Admin Chef", "chef@firma.de", "geheim123", rolle="admin")
