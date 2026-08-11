from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta
import os
import re
import secrets
import hmac
import io
import segno
import benutzer
import wine
import essen

app = Flask(__name__)

# NEU 07.08.2026 (Stefan): Rate-Limiting gegen Brute-Force auf den Login (siehe anmeldung()
# weiter unten, dort mit @limiter.limit(...) auf 10 Versuche/Minute pro IP begrenzt).
# Hinweis: Der Standard-Speicher von Flask-Limiter ist In-Memory und damit PRO GUNICORN-WORKER-
# PROZESS getrennt -- bei z.B. 2 Workern (WEB_CONCURRENCY) sind effektiv bis zu 2x so viele
# Versuche moeglich, je nachdem welchen Worker der Request trifft. Fuer dieses Projekt (kleine,
# einzelne EC2-Instanz) ausreichend; bei mehreren Instanzen/Hosts braeuchte es einen geteilten
# Speicher (z.B. Redis) als Limiter-Backend.
limiter = Limiter(get_remote_address, app=app, default_limits=[])

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

CORS(app, supports_credentials=True, origins=CORS_ORIGINS,
     allow_headers=['Content-Type', 'X-CSRF-Token'])

# NEU 11.08.2026 (Stefan): CSRF-Schutz (Double-Submit-Token). Die Session laeuft ueber ein
# signiertes Cookie (SameSite=Lax/Strict), das reicht aber allein nicht gegen CSRF -- ein
# fremdes Formular/Script auf einer anderen Seite kann bei SameSite=Lax weiterhin GET-Navigation
# und teils simple Cross-Site-Requests ausloesen. Deshalb zusaetzlich ein Token, das NUR per
# JavaScript aus der API gelesen und explizit als Header mitgeschickt werden kann -- das kann
# eine fremde Seite nicht faelschen, da sie den Token nicht auslesen darf (CORS blockiert das
# Lesen der Response fuer fremde Origins).
CSRF_SAFE_METHODS = {'GET', 'HEAD', 'OPTIONS'}

def _get_or_create_csrf_token():
    token = session.get('csrf_token')
    if not token:
        token = secrets.token_urlsafe(32)
        session['csrf_token'] = token
    return token

@app.before_request
def _csrf_protect():
    if request.method in CSRF_SAFE_METHODS:
        return
    session_token = session.get('csrf_token')
    header_token = request.headers.get('X-CSRF-Token', '')
    if not session_token or not header_token or not hmac.compare_digest(session_token, header_token):
        return jsonify({'success': False, 'message': 'Ungültiges oder fehlendes CSRF-Token. Bitte Seite neu laden.'}), 403

@app.route('/api/csrf-token')
def csrf_token():
    return jsonify({'csrf_token': _get_or_create_csrf_token()})

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
        'role': session.get('user_role', 'gast'),
        'csrf_token': _get_or_create_csrf_token()
    })

@app.route('/api/anmeldung', methods=['POST'])
@limiter.limit("10 per minute")
def anmeldung():
    data = request.json or {}
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    user = benutzer.benutzer_anmelden(email, password)
    if user:
        # GEAENDERT 11.08.2026 (Stefan): Session vor dem Login komplett leeren statt nur zu
        # ueberschreiben -- verhindert, dass Werte aus einer evtl. vor dem Login manipulierten
        # Session (Session Fixation) in die frisch authentifizierte Session uebernommen werden.
        # Das erzeugt zugleich ein neues CSRF-Token, das alte (vor dem Login gueltige) Token
        # wird damit ungueltig.
        session.clear()

        # NEU 11.08.2026 (Stefan): Wenn 2FA aktiv ist, wird die Session NUR als "wartet auf
        # TOTP-Code" markiert -- user_email/name/role werden erst in /api/anmeldung/totp
        # gesetzt, nachdem der zweite Faktor bestaetigt wurde. So ist ein Angreifer mit
        # gestohlenem Passwort ohne den zweiten Faktor weiterhin nicht angemeldet.
        if benutzer.totp_status(email):
            session['pending_2fa_email'] = email
            return jsonify({
                'success': True,
                'totp_required': True,
                'csrf_token': _get_or_create_csrf_token()
            })

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
            },
            'csrf_token': _get_or_create_csrf_token()
        })
    else:
        return jsonify({'success': False, 'message': 'Ungültige Anmeldedaten.'}), 401

# NEU 11.08.2026 (Stefan): Zweiter Schritt des Logins, falls der Benutzer 2FA aktiviert hat --
# wird von anmeldung() oben ueber 'totp_required' im Frontend ausgeloest.
@app.route('/api/anmeldung/totp', methods=['POST'])
@limiter.limit("10 per minute")
def anmeldung_totp():
    pending_email = session.get('pending_2fa_email')
    if not pending_email:
        return jsonify({'success': False, 'message': 'Keine ausstehende Anmeldung. Bitte erneut anmelden.'}), 400

    data = request.json or {}
    code = data.get('code', '').strip()

    if not benutzer.totp_code_pruefen(pending_email, code):
        return jsonify({'success': False, 'message': 'Code ungültig oder abgelaufen.'}), 401

    user = benutzer.get_user_by_email(pending_email)
    session.clear()
    session.permanent = True
    session['user_email'] = pending_email
    session['user_name'] = user.get('name', pending_email) if user else pending_email
    session['user_role'] = user.get('role', 'benutzer') if user else 'benutzer'
    return jsonify({
        'success': True,
        'message': f"Willkommen {session['user_name']}!",
        'user': {
            'email': pending_email,
            'name': session['user_name'],
            'role': session['user_role']
        },
        'csrf_token': _get_or_create_csrf_token()
    })

@app.route('/api/abmeldung', methods=['POST'])
def abmeldung():
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Erfolgreich abgemeldet.',
        'csrf_token': _get_or_create_csrf_token()
    })

# --- Zwei-Faktor-Authentifizierung (Verwaltung durch den eingeloggten Benutzer) ---

@app.route('/api/2fa/status')
def zwei_fa_status():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Bitte anmelden.'}), 401
    return jsonify({'success': True, 'enabled': benutzer.totp_status(session['user_email'])})

@app.route('/api/2fa/setup', methods=['POST'])
def zwei_fa_setup():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Bitte anmelden.'}), 401

    secret, uri = benutzer.totp_secret_generieren(session['user_email'])
    qr = segno.make(uri)
    buf = io.BytesIO()
    qr.save(buf, kind='svg', xmldecl=False, svgns=True, scale=4)
    qr_svg = buf.getvalue().decode('utf-8')

    return jsonify({'success': True, 'secret': secret, 'otpauth_uri': uri, 'qr_svg': qr_svg})

@app.route('/api/2fa/aktivieren', methods=['POST'])
@limiter.limit("10 per minute")
def zwei_fa_aktivieren():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Bitte anmelden.'}), 401

    data = request.json or {}
    code = data.get('code', '').strip()
    if benutzer.totp_aktivieren(session['user_email'], code):
        return jsonify({'success': True, 'message': 'Zwei-Faktor-Authentifizierung wurde aktiviert.'})
    return jsonify({'success': False, 'message': 'Code ungültig. Bitte erneut versuchen.'}), 400

@app.route('/api/2fa/deaktivieren', methods=['POST'])
def zwei_fa_deaktivieren():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Bitte anmelden.'}), 401

    data = request.json or {}
    password = data.get('password', '').strip()
    if not benutzer.benutzer_anmelden(session['user_email'], password):
        return jsonify({'success': False, 'message': 'Passwort falsch.'}), 401

    benutzer.totp_deaktivieren(session['user_email'])
    return jsonify({'success': True, 'message': 'Zwei-Faktor-Authentifizierung wurde deaktiviert.'})

# NEU 11.08.2026 (Stefan): Admin-Reset falls ein Benutzer sein Geraet mit der Authenticator-App
# verliert -- ohne eigene E-Mail-Domain gibt es keinen Recovery-Codes-per-Mail-Weg, das uebernimmt
# stattdessen der admin (analog zu rolle_update() oben).
@app.route('/api/benutzer/2fa_zuruecksetzen/<int:user_id>', methods=['POST'])
def zwei_fa_admin_reset(user_id):
    if session.get('user_role') != 'admin':
        return jsonify({'success': False, 'message': 'Nicht autorisiert.'}), 403

    if benutzer.totp_admin_reset(user_id):
        return jsonify({'success': True, 'message': 'Zwei-Faktor-Authentifizierung wurde zurückgesetzt.'})
    return jsonify({'success': False, 'message': 'Fehler beim Zurücksetzen.'}), 400

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
    # GEAENDERT 10.08.2026 (Stefan): Ansehen (GET) ist jetzt auch fuer Gaeste erlaubt, nur das
    # Anlegen (POST) bleibt angemeldeten Nutzern vorbehalten.
    if request.method == 'POST' and role == 'gast':
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

        # NEU 07.08.2026 (Stefan): Ersteller mitspeichern -- wird fuer die Ownership-Pruefung
        # beim Loeschen gebraucht (siehe loesche_wein() weiter unten).
        wine.add_wine(name, liter, ingredients, description, instructions, time, alcohol,
                      created_by=session.get('user_email'))
        return jsonify({'success': True, 'message': f'Wein "{name}" hinzugefügt!'})

    weine = wine.get_all_wines()
    return jsonify({'success': True, 'wines': weine})

@app.route('/api/wein/<int:wine_id>', methods=['GET', 'PUT'])
def update_wine(wine_id):
    wine_data = wine.get_wine_by_id(wine_id)
    if not wine_data:
        return jsonify({'success': False, 'message': 'Wein nicht gefunden.'}), 404

    role = session.get('user_role', 'gast')
    # GEAENDERT 10.08.2026 (Stefan): Ansehen (GET) ist jetzt auch fuer Gaeste erlaubt, nur das
    # Bearbeiten (PUT) bleibt angemeldeten Nutzern vorbehalten.
    if request.method == 'PUT' and role == 'gast':
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

# GEAENDERT 07.08.2026 (Stefan): Vorher durfte jeder eingeloggte "benutzer" JEDEN Wein loeschen,
# nicht nur seine eigenen. Jetzt: admin darf immer loeschen, benutzer nur eigene Eintraege
# (created_by == eigene E-Mail). Weine ohne erfassten Ersteller (z.B. Altdaten von vor dieser
# Aenderung, created_by ist dann None) koennen nur noch von admin geloescht werden -- sicherer
# Default, statt sie weiterhin fuer jeden benutzer freizugeben.
@app.route('/api/wein/loeschen/<int:wine_id>', methods=['DELETE'])
def loesche_wein(wine_id):
    role = session.get('user_role', 'gast')
    if role not in ('admin', 'benutzer'):
        return jsonify({'success': False, 'message': 'Nicht autorisiert.'}), 403

    if role != 'admin':
        wine_data = wine.get_wine_by_id(wine_id)
        if not wine_data:
            return jsonify({'success': False, 'message': 'Wein nicht gefunden.'}), 404
        if wine_data.get('created_by') != session.get('user_email'):
            return jsonify({'success': False, 'message': 'Du kannst nur eigene Weine löschen.'}), 403

    if wine.delete_wine(wine_id):
        return jsonify({'success': True, 'message': 'Wein wurde erfolgreich gelöscht.'})
    else:
        return jsonify({'success': False, 'message': 'Fehler beim Löschen des Weins.'}), 400

@app.route('/api/essen', methods=['GET', 'POST'])
def essen_verwalten():
    role = session.get('user_role', 'gast')
    # GEAENDERT 10.08.2026 (Stefan): Ansehen (GET) ist jetzt auch fuer Gaeste erlaubt, nur das
    # Anlegen (POST) bleibt angemeldeten Nutzern vorbehalten.
    if request.method == 'POST' and role == 'gast':
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

        # NEU 07.08.2026 (Stefan): Ersteller mitspeichern -- fuer die Ownership-Pruefung beim
        # Loeschen (siehe loesche_essen() weiter unten), analog zu wein_verwalten() oben.
        essen.add_essen(name, personen, zutaten, desc, anw, zeit, created_by=session.get('user_email'))
        return jsonify({'success': True, 'message': 'Essen gespeichert.'})

    speisen_liste = essen.get_all_essen()
    return jsonify({'success': True, 'essen': speisen_liste})

@app.route('/api/essen/<int:essen_id>', methods=['GET', 'PUT'])
def bearbeite_essen(essen_id):
    role = session.get('user_role', 'gast')
    # GEAENDERT 10.08.2026 (Stefan): Ansehen (GET) ist jetzt auch fuer Gaeste erlaubt, nur das
    # Bearbeiten (PUT) bleibt angemeldeten Nutzern vorbehalten.
    if request.method == 'PUT' and role == 'gast':
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
    
# GEAENDERT 07.08.2026 (Stefan): analog zu loesche_wein() oben -- admin darf immer loeschen,
# benutzer nur eigene Rezepte (created_by == eigene E-Mail). Rezepte ohne erfassten Ersteller
# (Altdaten) sind damit nur noch fuer admin loeschbar.
@app.route('/api/essen/loeschen/<int:essen_id>', methods=['DELETE'])
def loesche_essen(essen_id):
    role = session.get('user_role', 'gast')
    if role not in ('admin', 'benutzer'):
        return jsonify({'success': False, 'message': 'Nicht autorisiert.'}), 403

    if role != 'admin':
        essen_data = essen.get_essen(essen_id)
        if not essen_data:
            return jsonify({'success': False, 'message': 'Rezept nicht gefunden.'}), 404
        if essen_data.get('created_by') != session.get('user_email'):
            return jsonify({'success': False, 'message': 'Du kannst nur eigene Rezepte löschen.'}), 403

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