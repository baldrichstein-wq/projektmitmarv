
# Rezeptbuch

Ein Flask-Backend-Projekt der Gruppe Marvin, Marina, Stefan und David — entstanden im Rahmen der dreiwöchigen Projektphase (Sprint 1–3).

---

## Inhaltsverzeichnis

- [Projektbeschreibung](#projektbeschreibung)
- [Schnellstart](#schnellstart)
- [Konfiguration](#konfiguration)
- [API-Übersicht](#api-übersicht)
- [JWT-Authentifizierung](#jwt-authentifizierung)
- [Team & Rollen](#team--rollen)
- [Sprint-Tagebuch](#sprint-tagebuch)

---

## Projektbeschreibung

Rezeptbuch ist eine webbasierte Plattform zum Verwalten von Essen- und Weinrezepten. Benutzer können sich registrieren, anmelden und — je nach Rolle — Rezepte anlegen, bearbeiten und löschen. Ein integrierter Rezept-Rechner skaliert Zutaten für beliebige Personenzahlen oder Liter-Mengen.

**Technologie-Stack:**

| Komponente | Technologie |
|---|---|
| Web-Framework | Flask 2.0+ (Application Factory, Blueprints) |
| Datenbank-ORM | Flask-SQLAlchemy 3.0+ |
| Datenbank | SQLite (Entwicklung) / PostgreSQL (Produktion) |
| Authentifizierung | Flask-JWT-Extended 4.0+ (API: Bearer Token, WebUI: httponly Cookies) |
| API-Dokumentation | flask-smorest + Swagger UI (`/api/docs`) |
| Validierung | marshmallow 3.0+ |
| Tests | pytest 7.0+ + pytest-flask |

---

## Schnellstart

### Voraussetzungen

- Python 3.11+
- pip

### Installation

```bash
# Repository klonen
git clone <repo-url>
cd projektmitmarv

# Abhängigkeiten installieren
pip install -r requirements.txt

# Umgebungsvariablen konfigurieren
cp .env.example .env
# .env nach Bedarf anpassen

# Anwendung starten
python run.py
```

Die Anwendung ist dann unter `http://localhost:5000` erreichbar.  
Die Swagger-UI ist unter `http://localhost:5000/api/docs` verfügbar.

### Mit PostgreSQL

In der `.env`-Datei die `DATABASE_URL` auf eine PostgreSQL-Verbindung setzen:

```
DATABASE_URL=postgresql://benutzer:passwort@localhost:5432/rezeptbuch
```

SQLite wird automatisch verwendet, wenn keine PostgreSQL-URL konfiguriert ist.

---

## Konfiguration

| Variable | Standardwert | Beschreibung |
|---|---|---|
| `FLASK_ENV` | `development` | Umgebung (`development`, `testing`, `production`) |
| `SECRET_KEY` | (zufällig) | Flask-Session-Schlüssel |
| `JWT_SECRET_KEY` | (zufällig) | JWT-Signaturschlüssel |
| `DATABASE_URL` | SQLite (`instance/rezeptbuch.db`) | Datenbank-Verbindungsstring |

---

## API-Übersicht

Alle API-Endpunkte sind unter `/api/v1/` erreichbar und erfordern einen JWT Bearer Token (außer Login).

### Authentifizierung

| Methode | Pfad | Beschreibung |
|---|---|---|
| `POST` | `/api/v1/auth/login` | Login, gibt `access_token` und `refresh_token` zurück |
| `POST` | `/api/v1/auth/refresh` | Neuen Access-Token per Refresh-Token anfordern |

### Essen

| Methode | Pfad | Rolle | Beschreibung |
|---|---|---|---|
| `GET` | `/api/v1/essen/` | alle | Alle Rezepte auflisten |
| `POST` | `/api/v1/essen/` | benutzer, admin | Neues Rezept anlegen |
| `GET` | `/api/v1/essen/<id>` | alle | Einzelnes Rezept abrufen |
| `PUT` | `/api/v1/essen/<id>` | benutzer, admin | Rezept bearbeiten |
| `DELETE` | `/api/v1/essen/<id>` | admin | Rezept löschen |

### Wein

| Methode | Pfad | Rolle | Beschreibung |
|---|---|---|---|
| `GET` | `/api/v1/wein/` | alle | Alle Weinrezepte auflisten |
| `POST` | `/api/v1/wein/` | benutzer, admin | Neues Weinrezept anlegen |
| `GET` | `/api/v1/wein/<id>` | alle | Einzelnes Weinrezept abrufen |
| `PUT` | `/api/v1/wein/<id>` | benutzer, admin | Weinrezept bearbeiten |
| `DELETE` | `/api/v1/wein/<id>` | admin | Weinrezept löschen |

### Benutzer (Admin only)

| Methode | Pfad | Beschreibung |
|---|---|---|
| `GET` | `/api/v1/benutzer/` | Alle Benutzer auflisten |
| `PUT` | `/api/v1/benutzer/<id>/rolle` | Benutzerrolle ändern |

---

## JWT-Authentifizierung

### Token per API holen

```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@rezepte.de", "password": "admin123"}'
```

**Antwort:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

### Geschützte Endpunkte aufrufen

```bash
curl http://localhost:5000/api/v1/essen/ \
  -H "Authorization: Bearer <access_token>"
```

### Token erneuern

```bash
curl -X POST http://localhost:5000/api/v1/auth/refresh \
  -H "Authorization: Bearer <refresh_token>"
```

### Standard-Zugangsdaten (Entwicklung)

| E-Mail | Passwort | Rolle |
|---|---|---|
| `admin@rezepte.de` | `admin123` | admin |
| `benutzer@rezepte.de` | `benutzer123` | benutzer |

> **Hinweis:** Diese Zugangsdaten sind nur für die lokale Entwicklung gedacht. In der Produktion müssen eigene Werte in der `.env` gesetzt werden.

---

## Team & Rollen

| Name | Aufgaben |
|---|---|
| **Marvin** | Projektleitung, Architektur, Weinrezepte, Rechner, API-Design |
| **Marina** | Benutzerverwaltung, Rechtevergabe, Templates |
| **Stefan** | Datenbank, Essensrezepte, Datenbankmodelle |
| **David** | Flask-Integration, HTML-Routen, Bugfixing |

---

## Sprint-Tagebuch

### Sprint 1 (Woche 1)

- Projektidee festgelegt: Rezeptbuch
- GitHub-Repository eingerichtet
- Flask-Grundstruktur mit `main.py` aufgebaut
- SQLite-Datenbanken für Essen, Wein und Benutzer angelegt (sqlite3)
- CRUD-Operationen für Essen- und Weinrezepte implementiert
- Benutzer anlegen und verwalten (Marina)
- Rechtevergabe nach Rolle (Marvin, Marina)
- HTML-Templates mit Jinja2 erstellt

### Sprint 2 (Woche 2)

- Flask-Integration aller Module in `main.py` (David)
- Weinrezepte überarbeitet und verbessert (Marvin)
- Wein-zu-Essen-Vorschläge eingebaut
- Rezept-Rechner für Skalierung nach Personen und Litern (Marvin)
- Suchfunktion über Rezepte und Weine
- Fehlerbehebung (Mac-Probleme, Import-Konflikte) — frustrierender Tag, Team kämpft sich durch

### Sprint 3 (Woche 3)

- Komplette Neustrukturierung auf Application Factory + Blueprints
- SQLAlchemy-ORM ersetzt rohe sqlite3-Abfragen
- REST-API mit JWT-Authentifizierung (Bearer Token)
- Swagger UI unter `/api/docs` eingebunden
- Umschaltung SQLite ↔ PostgreSQL über Umgebungsvariablen
- Automatisierte Tests mit pytest (49 Tests, 100 % grün)
- JWT-Authentifizierung für WebUI via httponly Cookies
- Projektpräsentation: **22.05.2026** (Generalprobe: 20.05.2026)


