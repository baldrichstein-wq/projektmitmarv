import sqlite3
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
conn = sqlite3.connect('wines.db')
class Wine(BaseModel):
    id: int
    name: str
    ingredients: List[str]
    description: str
    brewing_instructions: str
    brewing_time: int
    alcohol_content: float
def init_db():
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
    conn.commit()
@app.post("/wines")
def create_wine(wine: Wine):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO wines (name, ingredients, description, brewing_instructions, brewing_time, alcohol_content)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        wine.name,
        ",".join(wine.ingredients),
        wine.description,
        wine.brewing_instructions,
        wine.brewing_time,
        wine.alcohol_content
    ))
    conn.commit()
    return {"message": "Wine created successfully", "wine_id": cursor.lastrowid}
@app.get("/wines")
def get_wines():
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM wines')
    rows = cursor.fetchall()
    wines = []
    for row in rows:
        wine = Wine(
            id=row[0],
            name=row[1],
            ingredients=row[2].split(','),
            description=row[3],
            brewing_instructions=row[4],
            brewing_time=row[5],
            alcohol_content=row[6]
        )
        wines.append(wine)
    return wines
@app.get("/wines/{wine_id}")
def get_wine(wine_id: int):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM wines WHERE id = ?', (wine_id,))
    row = cursor.fetchone()
    if row:
        wine = Wine(
            id=row[0],
            name=row[1],
            ingredients=row[2].split(','),
            description=row[3],
            brewing_instructions=row[4],
            brewing_time=row[5],
            alcohol_content=row[6]
        )
        return wine
    return {"message": "404: Wine not found"}
@app.delete("/wines/{wine_id}")
def delete_wine(wine_id: int):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM wines WHERE id = ?', (wine_id,))
    conn.commit()
    if cursor.rowcount:
        return {"message": "Wine deleted successfully"}
    return {"message": "404:Wine not found"}
