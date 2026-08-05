from flask import Flask, jsonify, request, session
from flask_cors import CORS
from datetime import timedelta
import os
import re
import benutzer
import wine
import essen

app = Flask(__name__)

# GEAENDERT 06.08.2026 (Stefan): Secret Key war vorher hartkodiert ('supersecretkey123') im Code
# und damit fuer jeden mit Repo-Zugriff bekannt -> Session-Cookies waeren faelschbar gewesen
# (z.B. sich selbst zum Admin machen). Kommt jetzt aus der Umgebungsvariable SECRET_KEY (.env).
# Nur im expliziten Debug-Modus gibt es einen unsicheren Fallback fuer lokale Entwicklung ohne .env.
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if os.environ.get('FLASK_DEBUG', 'false').lower() == 'true':
        SECRET_KEY = 'dev-only-insecure-key'
    else:
        raise RuntimeError(
            'SECRET_KEY Umgebungsvariable ist nicht gesetzt. '
            'In Produktion (AWS/NAS) muss ein zufaelliger, geheimer Wert gesetzt werden, '
            'z.B. per: python -c "import secrets; print(secrets.token_hex(32))"'
        )
app.secret_key = SECRET_KEY
app.permanent_session_lifetime = timedelta(days=7)

# NEU 06.08.2026 (Stefan): Cookie-Sicherheit war vorher gar nicht konfiguriert.
# SESSION_COOKIE_SECURE: 'true' sobald HTTPS aktiv ist, damit das Session-Cookie nur ueber
# verschluesselte Verbindungen gesendet wird (in .env aktuell 'false', da AWS/NAS-Domain/TLS
# noch nicht final ist -- vor dem echten Deployment auf 'true' umstellen!).
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')

# GEAENDERT 06.08.2026 (Stefan): CORS-Origins waren vorher hartkodiert auf localhost-Dev-Ports.
# Damit haette in Produktion (AWS/NAS) das echte Frontend die API gar nicht ansprechen koennen
# (Browser blockiert Cross-Origin-Requests ohne passenden CORS-Header). Kommt jetzt aus
# CORS_ORIGINS (.env, kommagetrennte Liste); Fallback nur fuer lokale Entwicklung ohne .env.
_cors_env = os.environ.get('CORS_ORIGINS')
if _cors_env:
    CORS_ORIGINS = [o.strip() for o in _cors_env.split(',') if o.strip()]
else:
    CORS_ORIGINS = [
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5174", "http://127.0.0.1:5174",
        "http://localhost:5175", "http://127.0.0.1:5175"
    ]

CORS(app, supports_credentials=True, origins=CORS_ORIGINS)

# --- UTILITY FUNKTIONEN ---

def skaliere_zutaten(zutaten_liste, original_menge, ziel_menge):
    if not original_menge or original_menge == 0:
        return zutaten_liste
        
    try:
        faktor = float(ziel_menge) / float(original_menge)
    except (ValueError, ZeroDivisionError):
        return zutaten_liste

    skalierte_liste = []
    for zutat in zutaten_liste:
        match = re.match(r"(\d+([.,]\d+)?)\s*(.*)", zutat)
        if match:
            menge = float(match.group(1).replace(',', '.'))
            einheit_und_name = match.group(3)
            neue_menge = round(menge * faktor, 2)
            neue_menge_str = str(neue_menge).replace('.', ',').rstrip('0').rstrip(',')
            skalierte_liste.append(f"{neue_menge_str} {einheit_und_name}")
        else:
            skalierte_liste.append(zutat)
    return skalierte_liste

# --- DATENBANK INITIALISIERUNG ---
benutzer.init_db()
wine.init_db()
essen.init_db()

# --- REST API ROUTEN ---

# NEU 06.08.2026 (Stefan): Health-Check-Endpoint fuer Deployment-Monitoring
# (z.B. AWS Load Balancer Health Check, NAS/Docker Container-Healthcheck).
@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/me')
def get_current_user():
    return jsonify({
        'logged_in': 'user_email' in session,
        'email': session.get('user_email'),
        'name': session.get('user_name', 'Gast'),
        'role': session.get('user_role', 'gast')
    })

@app.route('/api/anmeldung', methods=['POST'])
def anmeldung():
    data = request.json or {}
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    user = benutzer.benutzer_anmelden(email, password)
    if user:
        session.permanent = True
        session['user_email'] = email
        session['user_name'] = user.get('name', email)
        session['user_role'] = user.get('role', 'benutzer')
        return jsonify({
            'success': True,
            'message': f"Willkommen {session['user_name']}!",
            'user': {
                'email': email,
                'name': session['user_name'],
                'role': session['user_role']
            }
        })
    else:
        return jsonify({'success': False, 'message': 'Ungültige Anmeldedaten.'}), 401

@app.route('/api/abmeldung', methods=['POST'])
def abmeldung():
    session.clear()
    return jsonify({'success': True, 'message': 'Erfolgreich abgemeldet.'})

@app.route('/api/registrierung', methods=['POST'])
def registrierung():
    data = request.json or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not name or not email or not password:
        return jsonify({'success': False, 'message': 'Bitte alle Felder ausfüllen.'}), 400

    success, message = benutzer.benutzer_anlegen(name, email, password)
    return jsonify({'success': success, 'message': message}), 200 if success else 400

@app.route('/api/benutzer', methods=['GET', 'POST'])
def verwalte_benutzer():
    role = session.get('user_role', 'gast')
    if role != 'admin':
        return jsonify({'success': False, 'message': 'Zugriff verweigert.'}), 403

    if request.method == 'POST':
        data = request.json or {}
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        success, message = benutzer.benutzer_anlegen(name, email, password)
        return jsonify({'success': success, 'message': message}), 200 if success else 400

    users = benutzer.get_all_users()
    return jsonify({'success': True, 'users': users})

@app.route('/api/benutzer/loeschen/<int:user_id>', methods=['DELETE'])
def loesche_benutzer(user_id):
    role = session.get('user_role', 'gast')
    if role != 'admin':
        return jsonify({'success': False, 'message': 'Zugriff verweigert.'}), 403

    if benutzer.loesche_benutzer(user_id):
        return jsonify({'success': True, 'message': 'Benutzer wurde erfolgreich gelöscht.'})
    else:
        return jsonify({'success': False, 'message': 'Fehler beim Löschen des Benutzers.'}), 400

@app.route('/api/benutzer/rolle_aendern/<int:user_id>', methods=['POST'])
def rolle_update(user_id):
    if session.get('user_role') != 'admin':
        return jsonify({'success': False, 'message': 'Nicht autorisiert.'}), 403
    
    data = request.json or {}
    neue_rolle = data.get('rolle')
    if benutzer.rolle_aendern(user_id, neue_rolle):
        return jsonify({'success': True, 'message': f'Rolle wurde auf {neue_rolle} aktualisiert.'})
    else:
        return jsonify({'success': False, 'message': 'Fehler beim Aktualisieren der Rolle.'}), 400

@app.route('/api/wein', methods=['GET', 'POST'])
def wein_verwalten():
    role = session.get('user_role', 'gast')
    if role == 'gast':
        return jsonify({'success': False, 'message': 'Bitte melde dich an.'}), 401

    if request.method == 'POST':
        data = request.json or {}
        name = data.get('name')
        liter = data.get('liter', '5')
        ingredients = data.get('ingredients', [])
        if isinstance(ingredients, str):
            ingredients = [i.strip() for i in ingredients.split(',') if i.strip()]
        description = data.get('description')
        instructions = data.get('brewing_instructions')
        time = data.get('brewing_time')
        alcohol = data.get('alcohol_content')

        if not name:
            return jsonify({'success': False, 'message': 'Der Name des Weins darf nicht leer sein.'}), 400

        wine.add_wine(name, liter, ingredients, description, instructions, time, alcohol)
        return jsonify({'success': True, 'message': f'Wein "{name}" hinzugefügt!'})

    weine = wine.get_all_wines()
    return jsonify({'success': True, 'wines': weine})

@app.route('/api/wein/<int:wine_id>', methods=['GET', 'PUT'])
def update_wine(wine_id):
    wine_data = wine.get_wine_by_id(wine_id)
    if not wine_data:
        return jsonify({'success': False, 'message': 'Wein nicht gefunden.'}), 404
    
    role = session.get('user_role', 'gast')
    if role == 'gast':
        return jsonify({'success': False, 'message': 'Bitte melde dich an.'}), 401

    if request.method == 'PUT':
        data = request.json or {}
        name = data.get('name')
        liter = data.get('liter', '5')
        ingredients = data.get('ingredients', [])
        if isinstance(ingredients, str):
            ingredients = [i.strip() for i in ingredients.split(',') if i.strip()]
        description = data.get('description')
        instructions = data.get('brewing_instructions')
        time = data.get('brewing_time')
        alcohol = data.get('alcohol_content')

        if not name:
            return jsonify({'success': False, 'message': 'Der Name des Weins darf nicht leer sein.'}), 400

        wine.update_wine(wine_id, name, liter, ingredients, description, instructions, time, alcohol)
        return jsonify({'success': True, 'message': f'Wein "{name}" wurde aktualisiert!'})

    return jsonify({'success': True, 'wine': wine_data})

@app.route('/api/wein/loeschen/<int:wine_id>', methods=['DELETE'])
def loesche_wein(wine_id):
    role = session.get('user_role', 'gast')
    if role != 'admin' and role != 'benutzer':
        return jsonify({'success': False, 'message': 'Nicht autorisiert.'}), 403
    
    if wine.delete_wine(wine_id):
        return jsonify({'success': True, 'message': 'Wein wurde erfolgreich gelöscht.'})
    else:
        return jsonify({'success': False, 'message': 'Fehler beim Löschen des Weins.'}), 400

@app.route('/api/essen', methods=['GET', 'POST'])
def essen_verwalten():
    role = session.get('user_role', 'gast')
    if role == 'gast':
        return jsonify({'success': False, 'message': 'Bitte melden Sie sich an.'}), 401

    if request.method == 'POST':
        data = request.json or {}
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'success': False, 'message': 'Der Name des Essens darf nicht leer sein.'}), 400

        try:
            personen = int(data.get('personenanzahl', '4'))
            zeit = int(data.get('kochzeit', '0'))
        except ValueError:
            return jsonify({'success': False, 'message': 'Personenanzahl und Kochzeit müssen Zahlen sein!'}), 400
        
        zutaten = data.get('zutaten', [])
        if isinstance(zutaten, str):
            zutaten = [z.strip() for z in zutaten.split(',') if z.strip()]
        desc = data.get('description', '').strip()
        anw = data.get('kochanweisung', '').strip()
        
        essen.add_essen(name, personen, zutaten, desc, anw, zeit)
        return jsonify({'success': True, 'message': 'Essen gespeichert.'})

    speisen_liste = essen.get_all_essen()
    return jsonify({'success': True, 'essen': speisen_liste})

@app.route('/api/essen/<int:essen_id>', methods=['GET', 'PUT'])
def bearbeite_essen(essen_id):
    role = session.get('user_role', 'gast')
    if role == 'gast':
        return jsonify({'success': False, 'message': 'Bitte melde dich an.'}), 401

    aktuelles_essen = essen.get_essen(essen_id)
    if not aktuelles_essen:
        return jsonify({'success': False, 'message': 'Rezept nicht gefunden.'}), 404

    if request.method == 'PUT':
        data = request.json or {}
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'success': False, 'message': 'Der Name des Essens darf nicht leer sein.'}), 400
            
        try:
            personen = int(data.get('personenanzahl', '1'))
            zeit = int(data.get('kochzeit', '0'))
        except ValueError:
            return jsonify({'success': False, 'message': 'Personenanzahl und Kochzeit müssen Zahlen sein!'}), 400
            
        zutaten = data.get('zutaten', [])
        if isinstance(zutaten, str):
            zutaten = [z.strip() for z in zutaten.split(',') if z.strip()]
        desc = data.get('description', '').strip()
        anw = data.get('kochanweisung', '').strip()

        essen.update_essen(essen_id, name, personen, zutaten, desc, anw, zeit)
        return jsonify({'success': True, 'message': f'Rezept "{name}" wurde aktualisiert.'})

    return jsonify({'success': True, 'essen': aktuelles_essen})
    
@app.route('/api/essen/loeschen/<int:essen_id>', methods=['DELETE'])
def loesche_essen(essen_id):
    role = session.get('user_role', 'gast')
    if role != 'admin' and role != 'benutzer':
        return jsonify({'success': False, 'message': 'Nicht autorisiert.'}), 403
    
    if essen.delete_essen(essen_id):
        return jsonify({'success': True, 'message': 'Rezept wurde erfolgreich gelöscht.'})
    else:
        return jsonify({'success': False, 'message': 'Fehler beim Löschen des Rezepts.'}), 400

@app.route('/api/essen/skalieren', methods=['POST'])
def skalieren():
    data = request.json or {}
    zutaten = data.get('zutaten', [])
    original_menge = data.get('original_menge', 1)
    ziel_menge = data.get('ziel_menge', 1)
    skalierte = skaliere_zutaten(zutaten, original_menge, ziel_menge)
    return jsonify({'success': True, 'zutaten': skalierte})

@app.route('/api/suche')
def suche():
    role = session.get('user_role', 'gast')
    query = request.args.get('q', '').strip().lower()
    
    gefundene_weine = []
    gefundene_speisen = []

    if query:
        alle_weine = wine.get_all_wines()
        for w in alle_weine:
            zutaten_string = " ".join(w['ingredients']).lower()
            if (query in w['name'].lower() or 
                (w['description'] and query in w['description'].lower()) or 
                query in zutaten_string):
                gefundene_weine.append(w)

        alle_speisen = essen.get_all_essen()
        for e in alle_speisen:
            zutaten_string = " ".join(e['zutaten']).lower()
            if (query in e['name'].lower() or 
                (e['description'] and query in e['description'].lower()) or 
                query in zutaten_string):
                gefundene_speisen.append(e)

    return jsonify({
        'success': True,
        'query': query,
        'weine': gefundene_weine,
        'speisen': gefundene_speisen,
        'role': role
    })

# GEAENDERT 06.08.2026 (Stefan): debug=True war vorher fest eingebaut. Der Flask-Debugger
# erlaubt bei einem unbehandelten Fehler Remote Code Execution, sobald der Server im Netz
# erreichbar ist -- hochkritisch fuer AWS/NAS. Kommt jetzt aus FLASK_DEBUG (Default: aus).
# Hinweis: Dieser Block laeuft nur bei "python main.py" (lokale Entwicklung); im Dockerfile
# startet Gunicorn main:app direkt und dieser Block wird nicht ausgefuehrt.
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)