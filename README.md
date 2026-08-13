# Rezeptbuch & Brauportal

Fullstack-Webanwendung für Koch- und Weinrezepte mit Portionsrechner, Volltextsuche und
rollenbasierter Benutzerverwaltung. Entstanden als Abschlussprojekt (Modul 3, Mini-Agile-
Simulation mit einwöchigen Sprints).

**Live:** [rezepte-kuechenchaos.duckdns.org](https://rezepte-kuechenchaos.duckdns.org) (https://dasarchiv.uk).

## Team

David Ludwig-Erbs (NAS-Deployment) · Stefan Kallinich (AWS-Deployment)

## Features

- Speisen- und Weinrezepte mit Zutaten, Beschreibung und Zubereitung anlegen, bearbeiten, löschen
- Portionsrechner: Zutatenmengen live auf eine Zielportionszahl skalieren
- Volltextsuche über Rezepte und Weine gleichzeitig
- Rollenkonzept: `gast` (nur lesen), `benutzer` (eigene Rezepte verwalten), `admin` (alles,
  inkl. Benutzerverwaltung)
- Ownership-Schutz: `benutzer` kann nur eigene Einträge löschen, nicht die anderer
- CSRF-Schutz, gehärtete Sessions, Passwort-Mindestanforderungen
- Optionale Zwei-Faktor-Authentifizierung (TOTP) über QR-Code-Setup

## Tech-Stack

| Bereich | Technologie |
|---|---|
| Frontend | React 18, Vite, Fetch API |
| Backend | Flask 3, Gunicorn (WSGI, mehrere Worker) |
| Datenbanken | PostgreSQL 15 (Benutzer), MongoDB 6 (Rezepte & Weine) |
| Sicherheit | Werkzeug (Passwort-Hashing), Flask-Limiter (Rate-Limiting), pyotp + segno (TOTP-2FA) |
| Infrastruktur | Docker, Docker Compose, Caddy 2 (Reverse-Proxy, automatisches HTTPS) |

> Anmerkung zur Modulvorgabe: Das Projekt nutzt **Flask statt FastAPI** — bewusste Entscheidung
> im Team, gleiches REST-Architekturprinzip, aber im Rahmen des Moduls vertrauter. React Router


## Architektur

```
Browser (React/Vite SPA)
   │  Fetch API, JSON über HTTPS
   ▼
Caddy (Reverse-Proxy, TLS-Terminierung, Let's Encrypt)
   │
   ├──► Frontend-Container (nginx, statischer React-Build)
   │
   └──► Backend-Container (Flask + Gunicorn)
            │
            ├──► PostgreSQL   (Benutzer / Auth)
            └──► MongoDB      (Rezepte & Weine)
```

Alle fünf Services (frontend, backend, postgres, mongodb, proxy) laufen über Docker Compose in
einem gemeinsamen Netzwerk; `pg_data`, `mongo_data` und `caddy_data` sind benannte Volumes für
persistente Daten über Container-Neustarts hinweg.

## API-Übersicht

Basis-Pfad: `/api`. `GET` ist für alle Rollen offen (auch `gast`), veränderende Requests
(`POST`/`PUT`/`DELETE`) sind angemeldeten Nutzern vorbehalten und benötigen zusätzlich einen
gültigen `X-CSRF-Token`-Header (siehe `/api/csrf-token`).

| Endpoint | Methode | Zweck |
|---|---|---|
| `/health` | GET | Health-Check für Monitoring/Load Balancer |
| `/me` | GET | Aktuelle Session (Login-Status, Rolle, CSRF-Token) |
| `/csrf-token` | GET | CSRF-Token für die aktuelle Session ausstellen |
| `/anmeldung` | POST | Login (Schritt 1: Passwort) |
| `/anmeldung/totp` | POST | Login (Schritt 2: TOTP-Code, nur falls 2FA aktiv) |
| `/abmeldung` | POST | Logout |
| `/registrierung` | POST | Neues Benutzerkonto anlegen |
| `/2fa/status` | GET | Ist 2FA für den eingeloggten Nutzer aktiv? |
| `/2fa/setup` | POST | Neues TOTP-Secret + QR-Code erzeugen |
| `/2fa/aktivieren` | POST | 2FA mit Bestätigungscode scharf schalten |
| `/2fa/deaktivieren` | POST | 2FA deaktivieren (Passwort-Bestätigung) |
| `/benutzer` | GET, POST | Benutzerliste / neuen Benutzer anlegen (admin) |
| `/benutzer/loeschen/<id>` | DELETE | Benutzer löschen (admin) |
| `/benutzer/rolle_aendern/<id>` | POST | Rolle ändern (admin) |
| `/benutzer/2fa_zuruecksetzen/<id>` | POST | 2FA eines Benutzers zurücksetzen (admin) |
| `/essen` | GET, POST | Rezeptliste / neues Rezept |
| `/essen/<id>` | GET, PUT | Einzelnes Rezept ansehen / bearbeiten |
| `/essen/loeschen/<id>` | DELETE | Rezept löschen (Owner oder admin) |
| `/essen/skalieren` | POST | Zutatenmengen auf Zielportionen umrechnen |
| `/wein` | GET, POST | Weinliste / neuen Wein anlegen |
| `/wein/<id>` | GET, PUT | Einzelnen Wein ansehen / bearbeiten |
| `/wein/loeschen/<id>` | DELETE | Wein löschen (Owner oder admin) |
| `/suche` | GET | Volltextsuche über Rezepte und Weine (`?q=`) |

## Projektstruktur

```
projektmitmarv/
├── main.py              Flask-App, REST-Routen, CSRF-Schutz
├── benutzer.py           Benutzerverwaltung, Auth, TOTP-2FA (PostgreSQL)
├── essen.py               Speiserezepte (MongoDB)
├── wine.py                Weinrezepte (MongoDB)
├── requirements.txt        Python-Abhängigkeiten
├── Dockerfile               Backend-Image (Gunicorn)
├── docker-compose.yml        5-Service-Orchestrierung
├── Caddyfile                  Reverse-Proxy-Konfiguration
├── .env.example                 Vorlage für Umgebungsvariablen/Secrets
└── frontend/
    ├── src/
    │   ├── components/           Essen, Wein, Auth, Admin, Sicherheit, Suche, ...
    │   └── utils/api.js            CSRF-fähiger fetch()-Wrapper
    ├── Dockerfile                 Frontend-Image (nginx)
    └── nginx.conf
```

## Lokale Entwicklung

Voraussetzung: Docker + Docker Compose.

```bash
cp .env.example .env      # Secrets/Zufallswerte eintragen
docker compose up -d --build
```

Frontend danach unter `http://localhost` (über den Caddy-Proxy), Backend-API unter `/api/*`.
Für reine Frontend-Entwicklung ohne Docker: `cd frontend && npm install && npm run dev`
(erwartet ein separat laufendes Backend auf Port 5005).

## Sicherheit

- Passwörter werden mit `werkzeug.security` (PBKDF2) gehasht, nie im Klartext gespeichert
- Server-Session per signiertem, `HttpOnly`/`Secure`-Cookie statt Token im LocalStorage
- CSRF-Schutz per Double-Submit-Token auf allen veränderten Requests, inklusive Login selbst
- Session wird bei Login/Logout komplett neu aufgebaut (Schutz gegen Session Fixation)
- Passwort-Mindestanforderungen (8+ Zeichen, Groß-/Kleinbuchstabe, Ziffer) bei Registrierung
  und Admin-Benutzeranlage
- Optionale TOTP-Zwei-Faktor-Authentifizierung; kein Backup-Codes-Flow (keine eigene
  E-Mail-Domain), stattdessen Admin-Reset bei Geräteverlust
- Rate-Limiting auf den Login (10 Versuche/Minute/IP) gegen Brute-Force
- Ownership-Checks: `benutzer` kann nur eigene Rezepte/Weine löschen, `admin` alles

## Entwicklungsverlauf

**Abschlusprojekt Modul 2 (29.04.–20.05.):** Ursprüngliches Team (Marvin, Marina, Stefan, David) baute die
erste Version als serverseitig gerendertes Flask-Projekt (Jinja-Templates, SQLite) auf —
Benutzerverwaltung, Rechtevergabe, Speise- und Weinrezepte samt Portionsrechner, Kommentar-
/Bewertungssystem und Suchfunktion. Mehrere Debugging-Sessions rund um Session-Handling,
Datei-Uploads und Merge-Konflikte zwischen den Branches.

**03.–07.08. (David und Stefan):** Kompletter Umbau auf REST-API (Flask) + entkoppeltes React/Vite-SPA-
Frontend. Altlasten (alte Jinja-Templates, SQLite-Dateien, Heroku-Reste) entfernt, Backend auf
PostgreSQL (Benutzer) und MongoDB (Rezepte/Weine) umgestellt. Sicherheits-Grundlagen: Secret Key
und CORS-Origins aus Umgebungsvariablen statt hartkodiert, Debug-Modus standardmäßig aus,
Session-Cookie-Flags gesetzt. PostgreSQL-Connection-Pooling, atomare ID-Vergabe in MongoDB
(Race-Condition-Fix), Rate-Limiting auf den Login, Ownership-Prüfung beim Löschen. Caddy als
Reverse-Proxy mit automatischem HTTPS über Let's Encrypt eingerichtet, Vorbereitung des
AWS-Deployments (eu-central-1, Budget-Limit 15 €/Monat).

**11.08. (David und Stefan):** Impressum-Seite ergänzt (nicht-kommerzieller Hinweis statt vollem
Impressum, da Schulprojekt ohne Gewinnerzielungsabsicht). Login-Härtung: CSRF-Schutz
(Double-Submit-Token), Session-Regenerierung bei Login/Logout, serverseitige
Passwort-Mindestanforderungen. Optionale TOTP-Zwei-Faktor-Authentifizierung inkl.
QR-Code-Setup und Admin-Reset-Möglichkeit. Alle Änderungen lokal end-to-end getestet und auf
AWS deployed.

## Deployment

- **AWS:** EC2 t3.micro, eu-central-1, Docker Compose, Caddy-Proxy mit DuckDNS-Domain
  (`rezepte-kuechenchaos.duckdns.org`). Instanz wird zwischen Sessions gestoppt statt
  terminiert, um Kosten zu sparen (Budget-Limit 15 €/Monat).
- **NAS:** paralleles Deployment durch David (Details siehe Präsentation).

## Bekannte Einschränkungen & Ausblick

- **React Router fehlt** — Navigation läuft aktuell über internen `activeTab`-State statt
  echter URLs/Browser-Historie.
- Rate-Limiter-Speicher ist In-Memory (pro Gunicorn-Worker getrennt) — für mehrere
  Hosts/Instanzen bräuchte es einen geteilten Speicher (z. B. Redis).
- Kein automatisierter Datenbank-Export/Backup (aktuell manuell per `mongodump`/`mongorestore`).
- Keine CI/CD-Pipeline — Deployment läuft manuell per SSH + `docker compose up -d --build`.
- Keine Backup-Codes für 2FA (siehe [Sicherheit](#sicherheit)) — sinnvoll nachrüstbar, sobald
  eine eigene E-Mail-Domain existiert.
