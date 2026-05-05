import sqlite3
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Funktion zur Initialisierung der Datenbanken
def init_db():
    # Nutzung von Context-Managern für automatische Transaktionen
    # Verbindung zur Benutzer-Datenbank
    with sqlite3.connect('benutzer.db') as conn_user:
        conn_user.execute('''
            CREATE TABLE IF NOT EXISTS benutzer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        conn_user.commit()[aiter: 1]

    # Verbindung zur Wein-Datenbank
    with sqlite3.connect('wines.db') as conn_wine:
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
        conn_wine.commit()

# Modernes Lifespan-Handling statt veraltetem startup-Event
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Wird beim Start der Anwendung ausgeführt
    init_db()[aiter: 1]
    yield
    # Hier könnten Aufräumarbeiten beim Herunterfahren stehen

app = FastAPI(lifespan=lifespan)[aiter: 1]