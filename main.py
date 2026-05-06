import sqlite3
from fastapi import FastAPI

app = FastAPI()

def init_db():
    # Verbindung zur zentralen oder jeweiligen Datenbank
    conn_user = sqlite3.connect('benutzer.db')
    conn_wine = sqlite3.connect('wines.db')
    conn_essen = sqlite3.connect('essen.db')
    
    # Tabelle für Benutzer erstellen
    conn_user.execute('''
        CREATE TABLE IF NOT EXISTS benutzer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    
    # Tabelle für Weine erstellen
    conn_wine.execute('''
        CREATE TABLE IF NOT EXISTS wines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            description TEXT,
            brewing_instructions TEXT,
            brewing_time INTEGER,
            alcohol_content REAL
        )
    ''')
    
    # Tabelle für Essen erstellen
    conn_essen.execute('''
        CREATE TABLE IF NOT EXISTS essen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            description TEXT
        )
    ''')

    conn_user.commit()
    conn_wine.commit()
    conn_user.close()
    conn_wine.close()
    conn_essen.close()

@app.on_event("startup")
def startup_event():
    init_db()