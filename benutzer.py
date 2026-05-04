import sqlite3
#1. Datenbank Verbindung herstellen und erstellen falls nicht vorhanden
conn = sqlite3.connect('rezept_datenbank.db')
cursor = conn.cursor()
#2. Tabellen erstellen
cursor.execute('''
               CREATE TABLE IF NOT EXISTS rezepte(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL UNIQUE
               )
               ''')

cursor.execute('''
               CREATE TABLE IF NOT EXISTS zutaten (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rezept_id INTEGER,
                    zutaten_name TEXT NOT NULL,
                    menge REAL NOT NULL,
                    FOREIGEN KEY (rezept_id) REFERENCES rezepte(id)
                    )
               ''')
conn.commit()