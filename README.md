
# projektmitmarv

Schulprojekt1 Rezeptbuch


Team

David (NAS-Deployment), Stefan (AWS-Deployment)


07.05. Fehlerbehebung und Fehlersuche und wieder auf tauchen von Fehlern David Marvin Marina Stefan  (wir sind Frustriert Mac ist Scheiße)
20.05.2026 02:06 Uhr Bugfixing David mit Suporter Felix (4 Stunden Fehlersuche)

06.08.2026 Stefan - Aufraeumen der Altlasten und Absicherung fuer Deployment auf AWS und NAS:

Entfernte Altlasten (altes, server-gerendertes Flask-Projekt, ersetzt durch REST-API main.py + frontend/-SPA):
- main (1).py, main inet.py, test  (alte main.py-Versionen mit render_template)
- rechner.py  (Skalierungs-Logik ist bereits identisch in main.py enthalten)
- templates/ und static/  (HTML/CSS/JS der alten Server-gerenderten Oberflaeche, main.py nutzt kein render_template mehr)
- benutzer.db, essen.db, essen.db-shm, essen.db-wal, wines.db  (alte SQLite-Datenbanken; Projekt nutzt jetzt ausschliesslich PostgreSQL fuer Benutzer und MongoDB fuer Essen/Wein)
- Procfile, runtime.txt  (Heroku-spezifische Dateien, nicht mehr relevant da Deployment ueber Docker auf AWS/NAS erfolgt)
- .DS_Store aus Git-Tracking entfernt (macOS-Systemdatei, gehoert nicht ins Repo)

Sicherheits-/Deployment-Fixes:
- main.py: Secret Key kommt jetzt aus der Umgebungsvariable SECRET_KEY (App startet nicht mehr mit hartkodiertem "supersecretkey123"; in Produktion Pflicht, sonst Fehler beim Start)
- main.py: Flask-Debug-Modus kommt aus FLASK_DEBUG (Default: aus) statt fest debug=True (Debug-Modus in Produktion ist ein Remote-Code-Execution-Risiko)
- main.py: CORS-Origins kommen aus CORS_ORIGINS (kommagetrennt) statt hartkodierter localhost-Ports, damit die echte Frontend-Domain auf AWS/NAS funktioniert
- main.py: Session-Cookie-Flags gesetzt (SESSION_COOKIE_HTTPONLY, SESSION_COOKIE_SECURE per Env, SESSION_COOKIE_SAMESITE)
- main.py: neuer Endpoint /api/health fuer Health-Checks (z.B. AWS Load Balancer, NAS Container-Monitoring)
- Dockerfile: Start jetzt ueber Gunicorn statt Flask-Dev-Server, Container laeuft als non-root User, COPY *.db entfernt (keine SQLite-Dateien mehr noetig)
- docker-compose.yml: Volume-Mount "backend_data:/app" entfernt (ueberlagerte bisher den kopierten Anwendungscode im Container mit einem leeren Volume); Ports von Postgres und MongoDB werden nicht mehr auf den Host gemappt (nur noch intern im Docker-Netzwerk erreichbar); alle Zugangsdaten (Postgres, MongoDB, Secret Key, CORS) kommen jetzt aus Umgebungsvariablen/.env statt hartkodiert im Compose-File zu stehen; veraltetes "version:"-Attribut entfernt
- .env.example neu angelegt als Vorlage fuer die echten, geheimen Werte (.env selbst wird nicht committed, siehe .gitignore)
- requirements.txt: Versionen fest gepinnt (vorher teils mit >=) fuer reproduzierbare Builds
- .gitignore: *.db und .env/.env.* ergaenzt, damit Datenbank-Dumps und Secrets nicht mehr versehentlich eingecheckt werden

Offene Punkte fuer spaeter (nicht in diesem Schritt umgesetzt): Connection-Pooling fuer PostgreSQL, atomische ID-Vergabe in MongoDB (wine.py/essen.py), Rate-Limiting fuer den Login, Ownership-Pruefung beim Loeschen von Rezepten.

Lokaler Testlauf (docker compose) am selben Tag:
- Stack lokal per "docker compose up --build" gestartet, um die Aenderungen im Browser zu pruefen
- Zwei alte, lokale Docker-Volumes (pg_data, mongo_data) enthielten noch Passwoerter aus fruehreren Testlaeufen mit den alten, hartkodierten Zugangsdaten -> Authentifizierung schlug fehl. Volumes geloescht (nur lokale Testdaten, keine echten Nutzerdaten) und Stack neu gestartet, danach liefen alle vier Container (backend, frontend, postgres, mongodb) fehlerfrei
- Health-Check (/api/health), Login (/api/anmeldung) und Frontend (Port 8082) erfolgreich getestet
- 20 Beispiel-Essensrezepte und 10 Beispiel-Weinrezepte ueber die bestehende REST-API (/api/essen, /api/wein) angelegt, damit die Anwendung mit realistischen Daten ausprobiert werden kann
- Hinweis: Rezepte liegen in den Docker-Volumes pg_data/mongo_data und bleiben bei "docker compose stop/down" (ohne -v) sowie beim Schliessen von Docker Desktop erhalten; nur "docker compose down -v" bzw. ein manuelles Loeschen der Volumes entfernt sie

Ausfuehrliches Schritt-fuer-Schritt-Protokoll dieser gesamten Session: docs/protokoll-2026-08-06-deployment-sicherheit.md

07.08.2026 Stefan - Offene Punkte aus der Analyse vom 06.08. behoben (bis auf die tote
RECHTE_PRO_ROLE-Tabelle in benutzer.py und fehlende Eingabevalidierung bei liter/brewing_time/
alcohol_content in main.py -- bewusst zurueckgestellt) sowie AWS-Vorbereitung:

- Caddyfile (neu) + docker-compose.yml: neuer proxy-Service (Caddy) uebernimmt Port 80/443 und
  automatisches HTTPS via Let's Encrypt (Domain ueber Env-Variable DOMAIN, Fallback "localhost"
  mit selbstsigniertem Zertifikat fuer lokale Tests). backend und frontend haben keine direkten
  Host-Port-Mappings mehr, sind nur noch ueber den Proxy erreichbar.
- benutzer.py: PostgreSQL-Verbindungs-Pool (psycopg2.pool.SimpleConnectionPool) statt einer neuen
  Verbindung pro Request/Funktionsaufruf.
- wine.py, essen.py: atomare ID-Vergabe ueber eine MongoDB-"counters"-Collection
  (find_one_and_update mit $inc) statt "hoechste ID + 1" (war eine Race Condition bei
  gleichzeitigen Schreibzugriffen).
- main.py: Rate-Limiting auf /api/anmeldung (10 Versuche/Minute pro IP, ueber flask-limiter)
  gegen Brute-Force-Logins.
- wine.py, essen.py, main.py: Ownership-Pruefung beim Loeschen -- neues Feld created_by
  (E-Mail des Erstellers) wird beim Anlegen von Wein/Essen gespeichert; beim Loeschen darf
  admin weiterhin alles loeschen, benutzer aber nur noch eigene Eintraege (Eintraege ohne
  erfassten Ersteller, z.B. Altdaten, sind dann nur noch fuer admin loeschbar).
- Dockerfile, docker-compose.yml: Gunicorn-Worker-Anzahl ueber WEB_CONCURRENCY (.env)
  konfigurierbar statt fest auf 4 -- Default jetzt 2, passend fuer kleine AWS-Instanzen
  (z.B. t3.micro mit 1 GiB RAM).
- requirements.txt: flask-limiter ergaenzt. .env.example: DOMAIN und WEB_CONCURRENCY ergaenzt.
- Neue, bewusst nicht versionierte Datei docs/aws-setup-eu-central-1.md (in .gitignore) mit
  sehr detaillierter Schritt-fuer-Schritt-Anleitung fuer die AWS-Sandbox (eu-central-1,
  15 EUR/Monat-Limit, gelegentlicher statt Dauerbetrieb).

Bewusst nicht umgesetzt: Bereinigung der Git-Historie von den alten .db-Dateien (waere ein
destruktiver Schritt mit Force-Push, auf Wunsch zurueckgestellt).



-main.py Einbindung der wine.py, benutzer.py und essen.py mit Flask um die für die HTML zu gewährleisten David Woche 1 und 2

-Benutzer anlegen und verwalten       Marina Woche 1

-Rechtevergabe                        Marvin Marina woche 1

-Essensrezept einfügen,ändern,löschen  Stefan David woche 1

-Weinrezepte einfügen,ändern,löschen   Marvin verbessern woche 1

-Weine für Essen vorschlagen           Marivn woche 2

-Rezepte berechnen für x Personen und X Liter  Berechnung woche 2

-Datenbanken für Rezepte mit sqlite3 Stefan Marvin Woche 1

-Datenbank für Benutzer David Marina Woche 1

- Html als GUI Marvin Woche 2

- Kommentar Sektion für Rezepte und bewertungsdurchschnitt anzeige sowie bewertungen  Woche 2

- Suchfunktion für den zweck der suche bestimmter rezepte Woche 2

- funktion für das erstellen von rezepten anderer nutzer global sichtbar Woche 1 und 2

Nutzung von Flask statt Fastapi

IDEEN

Suchfunktion:

-nach zutaten

-nach essen

-nach kochart (in der heimischen küche, outdoor)

-nach zeit
-nach vor-haupt-nachspeiße


- Menü Zusammenstellung gimimg



-Glosar Woche 3

