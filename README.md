
# projektmitmarv

Schulprojekt1 Rezeptbuch


Team

Marvin, Marina, Stefan, David


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

