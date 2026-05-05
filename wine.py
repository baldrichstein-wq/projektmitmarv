import sqlite3
import json
from typing import List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

DB_FILE = 'wines.db'

# Predefined recipe: Holunder Johannisbeer Wein
PREDEFINED_WINE = {
    "name": "Holunder Johannisbeer Wein",
    "ingredients": [
        "1 Pack Weinhefe Sorte Portwein",
        "500g Johannisbeeren Schwarz",
        "1000g Holunderbeeren",
        "1800g Zucker",
        "Wasser bis 5l ansatz erreicht",
        "Starsan für Desinfektion von Brauutensilien",
        "5g Hefenährsalz",
        "Gärbehälter mit Gärstopfen und ggf je nach bauweise Deckel und Gärröhrchen",
        "Dampfentsafter"
    ],
    "description": "Ein Sehr kräftiger Wein mit eigenwilligen jedoch durchaus wohlschmeckend herben und teils süßen Geschmack, hier steht der Holunder im Vordergrund und die Johannisbeere soll den Holunder komplementieren und etwas zum Körper des Weines beitragen.",
    "brewing_instructions": "Alle utensilien falls nicht bereits während betrieb im falle eines Dampfentsafters welcher sich aufgrund seiner Funktionsweise selbst steriliert mit 5-10ml starsan in Wasser aufgelöst spülen und abtropfen lassen denn dieses Mittel ist ein No Rinse Sanatiser aka muss nach korrekter anwendung nicht mehr ausgespült werden. Hier empfehle ich nach den Instruktionen auf der Verpackung zu arbeiten. Wasser in den untersten Topf des Dampfentsafters geben, Schlauch mit Klemme auf den mittleren Segement am Zapfstutzen anbringen, in das oberste Segment Entsaftungsgut geben aber nicht übermäßig viel damit der dampf auch durch die Früchte gelangen kann um diese zu garen. Den Holunder 30 Minuten und die Johannisbeeren 45 Minuten Entsaften. Saft in einen sauberen Hitzebeständigen Gefäß auffangen und kühlen. Nach kühlen auf grob 25-30 Grad in das Gärgefäß einfüllen und im selbigen Topf wasser erwärmen und Zucker drin auflösen. Ca. 2-3 tl Zucker auf Reserve halten, mit lauwarmen Wasser eine kleine Tasse oder anderes Gefäß befüllen, Zucker und Hefe einrühren und warten bis diese schäumt. anschließend Mixtur in Gärgefäß geben, mit restlichen Wasser und zuckerlösung auffüllen bis NICHT GANZ VOLL damit nichts überschäumt. verschließen schwenken und an einen warmen dunklen Ort lagern und gären lassen. Für die erste Woche täglich schwenken für mischen und danach stehen lassen. Nach ende der Gärung abfiltrieren und abfüllen und kalt stellen zum töten der Hefe. WARNUNG, FLASCHEN STEHEN POTENTIELL UNTER DRUCK, FÜR MINDESTENS 2 WOCHEN TÄGLICH KONTROLLIEREN UM PLATZEN ZU VERMEIDEN",
    "brewing_time": 8,
    "alcohol_content": 15.0
}

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
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
        
        # Insert predefined recipe if table is empty
        cursor.execute('SELECT COUNT(*) FROM wines')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO wines (name, ingredients, description, brewing_instructions, brewing_time, alcohol_content)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                PREDEFINED_WINE["name"],
                json.dumps(PREDEFINED_WINE["ingredients"]), # Safer serialization
                PREDEFINED_WINE["description"],
                PREDEFINED_WINE["brewing_instructions"],
                PREDEFINED_WINE["brewing_time"],
                PREDEFINED_WINE["alcohol_content"]
            ))
            conn.commit()

# Dependency to get DB connection per request
def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

# --- Pydantic Models ---
class WineBase(BaseModel):
    name: str
    ingredients: List[str]
    description: str
    brewing_instructions: str
    brewing_time: int
    alcohol_content: float

class WineCreate(WineBase):
    pass # No ID required for creation

class WineResponse(WineBase):
    id: int # ID returned in the response

# --- Endpoints ---
@app.post("/wines", response_model=WineResponse)
def create_wine(wine: WineCreate, conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO wines (name, ingredients, description, brewing_instructions, brewing_time, alcohol_content)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        wine.name,
        json.dumps(wine.ingredients),
        wine.description,
        wine.brewing_instructions,
        wine.brewing_time,
        wine.alcohol_content
    ))
    conn.commit()
    
    # Return the newly created object
    return {**wine.model_dump(), "id": cursor.lastrowid}

@app.get("/wines", response_model=List[WineResponse])
def get_wines(conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM wines')
    rows = cursor.fetchall()
    
    wines = []
    for row in rows:
        wines.append({
            "id": row[0],
            "name": row[1],
            "ingredients": json.loads(row[2]), # Safe deserialization
            "description": row[3],
            "brewing_instructions": row[4],
            "brewing_time": row[5],
            "alcohol_content": row[6]
        })
    return wines

@app.get("/wines/{wine_id}", response_model=WineResponse)
def get_wine(wine_id: int, conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM wines WHERE id = ?', (wine_id,))
    row = cursor.fetchone()
    
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "ingredients": json.loads(row[2]),
            "description": row[3],
            "brewing_instructions": row[4],
            "brewing_time": row[5],
            "alcohol_content": row[6]
        }
    
    # Proper 404 handling
    raise HTTPException(status_code=404, detail="Wine not found")

@app.delete("/wines/{wine_id}")
def delete_wine(wine_id: int, conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM wines WHERE id = ?', (wine_id,))
    conn.commit()
    
    if cursor.rowcount:
        return {"message": "Wine deleted successfully"}
        
    # Proper 404 handling
    raise HTTPException(status_code=404, detail="Wine not found")