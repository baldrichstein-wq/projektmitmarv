import sqlite3
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