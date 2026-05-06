from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import benutzer
import essen
import wine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup-Logik
    benutzer.init_db()
    wine.init_db()
    yield
    # Shutdown-Logik (falls nötig)

app = FastAPI(
    title="Rezpetbuch",
    description="API für die Verwaltung von Benutzern, Speisen und Weinen",
    lifespan=lifespan
)

# --- Pydantic Modelle für die Validierung ---
class BenutzerCreate(BaseModel):
    name: str
    email: str
    passwort: str

class LoginRequest(BaseModel):
    email: str
    passwort: str

class LoginResponse(BaseModel):
    status: str
    message: str
    benutzer: dict | None = None

class RegisterResponse(BaseModel):
    status: str
    message: str

# --- Wein Pydantic Modelle ---
class WineCreate(BaseModel):
    name: str
    ingredients: list[str]
    description: Optional[str] = ""
    brewing_instructions: Optional[str] = ""
    brewing_time: int = 0
    alcohol_content: float = 0.0

class WineUpdate(BaseModel):
    name: Optional[str] = None
    ingredients: Optional[list[str]] = None
    description: Optional[str] = None
    brewing_instructions: Optional[str] = None
    brewing_time: Optional[int] = None
    alcohol_content: Optional[float] = None

class WineResponse(BaseModel):
    id: int
    name: str
    ingredients: list[str]
    description: str
    brewing_instructions: str
    brewing_time: int
    alcohol_content: float

class WineListResponse(BaseModel):
    wines: List[WineResponse]

# --- Endpunkte ---

@app.get("/")
def read_root():
    return {"message": "Willkommen im Rezpetbuch"}

@app.post("/benutzer/registrieren/", status_code=201)
def registriere_benutzer(user: BenutzerCreate):
    """Registriert einen neuen Benutzer."""
    try:
        benutzer.benutzer_anlegen(user.name, user.email, user.passwort)
        return RegisterResponse(
            status="success",
            message=f"Benutzer '{user.name}' wurde erfolgreich registriert."
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/benutzer/anmelden/")
def anmeldung(login: LoginRequest):
    """Versucht, einen Benutzer anzumelden."""
    ergebnis = benutzer.benutzer_anmelden(login.email, login.passwort)
    if ergebnis:
        return LoginResponse(
            status="success",
            message=f"Willkommen zurück, {ergebnis['name']}!",
            benutzer=ergebnis
        )
    raise HTTPException(status_code=401, detail="Ungültige E-Mail oder Passwort.")

@app.get("/rezepte")
def get_essen_status():
    # Hier simulieren wir die Logik aus Option [2]
    return {
        "datenbank": "essen.db",
        "tabelle": "essen",
        "status": "aktiv"
    }

# --- Wein Endpunkte (CRUD) ---

@app.get("/weine/", response_model=WineListResponse)
def get_all_weine():
    """Gibt alle Weine zurück."""
    weine = wine.get_all_wines()
    return WineListResponse(wines=[WineResponse(**w) for w in weine])

@app.get("/weine/{wine_id}", response_model=WineResponse)
def get_ein_wein(wine_id: int):
    """Gibt einen einzelnen Wein zurück."""
    result = wine.get_wine(wine_id)
    if not result:
        raise HTTPException(status_code=404, detail="Wein nicht gefunden.")
    return WineResponse(**result)

@app.post("/weine/", status_code=201, response_model=WineResponse)
def create_wein(wine_data: WineCreate):
    """Erstellt einen neuen Wein-Eintrag."""
    wine_dict = wine_data.model_dump()
    result = wine.create_wine(wine_dict)
    return WineResponse(**result)

@app.put("/weine/{wine_id}", response_model=WineResponse)
def update_wein(wine_id: int, wine_data: WineUpdate):
    """Aktualisiert einen bestehenden Wein-Eintrag."""
    existing = wine.get_wine(wine_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Wein nicht gefunden.")
    
    update_dict = {k: v for k, v in wine_data.model_dump().items() if v is not None}
    result = wine.update_wine(wine_id, update_dict)
    if not result:
        raise HTTPException(status_code=500, detail="Aktualisierung fehlgeschlagen.")
    return WineResponse(**result)

@app.delete("/weine/{wine_id}")
def delete_wein(wine_id: int):
    """Löscht einen Wein-Eintrag."""
    if not wine.delete_wine(wine_id):
        raise HTTPException(status_code=404, detail="Wein nicht gefunden.")
    return {"status": "success", "message": f"Wein {wine_id} wurde gelöscht."}

@app.post("/system")
def initialize_system():
    # Entspricht Option [4]
    benutzer.init_db()
    wine.init_db()
    return {"status": "success", "message": "Alle Datenbanken wurden erfolgreich initialisiert."}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)