import sqlite3
from typing import List
from pydantic import BaseModel

# --- Datenmodelle (wine.py) ---
class Wine(BaseModel):
    id: int = None
    name: str
    ingredients: List[str]
    description: str
    brewing_instructions: str
    brewing_time: int
    alcohol_content: float

# --- Datenbank Initialisierung (test.py & essen.py) ---
def init_all_dbs():
    """Initialisiert alle Datenbanken: benutzer, wines und essen."""
    databases = {
        'benutzer.db': '''
            CREATE TABLE IF NOT EXISTS benutzer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )''',
        'wines.db': '''
            CREATE TABLE IF NOT EXISTS wines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                description TEXT,
                brewing_instructions TEXT,
                brewing_time INTEGER,
                alcohol_content REAL
            )''',
        'essen.db': '''
            CREATE TABLE IF NOT EXISTS essen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                description TEXT,
                cooking_instructions TEXT,
                cooking_time INTEGER
            )'''
    }

    print(f"{'='*50}")
    print(f"{'DATENBANK INITIALISIERUNG':^50}")
    print(f"{'='*50}")

    for db_name, schema in databases.items():
        try:
            with sqlite3.connect(db_name) as conn:
                conn.execute(schema)
                print(f" [+] {db_name:<15} | Status: OK")
        except sqlite3.Error as e:
            print(f" [!] {db_name:<15} | Fehler: {e}")
    
    print(f"{'='*50}\n")

# --- Datenabfrage für die Anzeige ---
def get_table_counts():
    counts = {}
    for db, table in [('benutzer.db', 'benutzer'), ('wines.db', 'wines'), ('essen.db', 'essen')]:
        try:
            with sqlite3.connect(db) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cursor.fetchone()[0]
        except:
            counts[table] = "Fehler"
    return counts

# --- Schöne Ausgabe (Dashboard) ---
def print_dashboard():
    counts = get_table_counts()
    
    print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    print("┃                SYSTEM DASHBOARD                  ┃")
    print("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")
    print(f"┃  Anzahl Benutzer:   {str(counts['benutzer']):<28} ┃")
    print(f"┃  Anzahl Weine:      {str(counts['wines']):<28} ┃")
    print(f"┃  Anzahl Rezepte:    {str(counts['essen']):<28} ┃")
    print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
    
    # Detailansicht Weine (Beispiel aus wine.py)
    print("\n--- Aktuelle Weinkarte ---")
    with sqlite3.connect('wines.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, alcohol_content FROM wines LIMIT 5")
        rows = cursor.fetchall()
        if not rows:
            print(" (Keine Weine in der Datenbank vorhanden)")
        for row in rows:
            print(f" • {row[0]:<15} | Alkohol: {row[1]}%")
    print("-" * 30)

# --- Hauptprogramm ---
if __name__ == "__main__":
    # 1. Datenbanken vorbereiten
    init_all_dbs()
    
    # 2. Beispiel-Eintrag hinzufügen (optional, nur wenn leer)
    with sqlite3.connect('wines.db') as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM wines")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO wines (name, ingredients, description, brewing_instructions, brewing_time, alcohol_content) VALUES (?,?,?,?,?,?)",
                      ("Hauswein", "Trauben, Wasser", "Ein Klassiker", "Gären", 30, 11.5))
    
    # 3. Die schöne Ausgabe aufrufen
    print_dashboard()