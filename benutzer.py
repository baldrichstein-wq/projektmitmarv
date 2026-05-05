import sqlite3

def init_db():
    """Erstellt die Datenbank und die Tabelle, falls sie nicht existieren."'
    
#1. Datenbank Verbindung herstellen und erstellen falls nicht vorhanden
conn = sqlite3.connect('benutzer.db')
cursor = conn.cursor()
#2. Tabellen erstellen
cursor.execute('''
    CREATE TABLE IF NOT EXISTS benutzer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
''')
conn.commit()
conn.close()

def benutzer_anlegen(name, email, passwort):
    """Fügt einen neuen Benutzer hinzu."""
    try:
        conn = sqlite3.connect('benutzer.db')
        cursor = conn.cursor()
        
        # Den Benutzer in die Tabelle einfuegen
        cursor.execute('''
            INSERT INTO benutzer (name, email, password) 
            VALUES (?, ?, ?)
        ''', (name, email, passwort))
        
        conn.commit()
        print(f"Benutzer {name} erfolgreich angelegt!")
    except sqlite3.IntegrityError:
        print("Fehler: Diese E-Mail '{email}' existiert bereits.")
    finally:
        conn.close()

# --- Programmstart ---
if __name__ == "__main__":
    init_db() 

# wichtig: Die Funktion muss definiert sein, bevor sie gerufen wird.

# Testlauf:
# benutzer_anlegen("Max Mustermann", "max@kochen.de", "superSicher123")
