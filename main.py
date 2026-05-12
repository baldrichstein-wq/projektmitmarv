from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import re
import benutzer
import wine
import essen

app = Flask(__name__, template_folder='templates')
app.secret_key = 'supersecretkey123' 

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

# --- ROUTEN ---

@app.route('/')
def home():
    # Rolle aus Session holen, Standard ist 'besucher'
    role = session.get('user_role', 'besucher')
    name = session.get('user_name', 'Gast')
    return render_template('index.html', name=name, role=role)

@app.route('/ueber-uns')
def ueber_uns():
    role = session.get('user_role', 'besucher')
    return render_template('ueber-uns.html', role=role)

@app.route('/benutzer', methods=['GET', 'POST'])
def verwalte_benutzer():
    role = session.get('user_role', 'besucher')
    if role != 'admin':
        flash('Zugriff verweigert: Nur Administratoren dürfen Benutzer verwalten.', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        # Standardrolle für neue User über das Formular könnte 'user' sein
        success, message = benutzer.benutzer_anlegen(name, email, password)
        flash(message, 'success' if success else 'danger')
        return redirect(url_for('verwalte_benutzer'))

    users = benutzer.get_all_users()
    return render_template('benutzer.html', users=users, role=role)

@app.route('/anmeldung', methods=['GET', 'POST'])
def anmeldung():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        user = benutzer.benutzer_anmelden(email, password)
        if user:
            session['user_email'] = email
            session['user_name'] = user.get('name', email)
            session['user_role'] = user.get('rolle', 'besucher')
            flash(f"Willkommen {session['user_name']}!", 'success')
            return redirect(url_for('home'))
        else:
            flash('Ungültige Anmeldedaten.', 'danger')

    return render_template('anmeldung.html', role=session.get('user_role', 'besucher'))

@app.route('/abmeldung')
def abmeldung():
    session.clear()
    flash('Erfolgreich abgemeldet.', 'success')
    return redirect(url_for('home'))
@app.route('/registrierung', methods=['GET', 'POST'])
def registrierung():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not name or not email or not password:
            flash('Bitte alle Felder ausfüllen.', 'danger')
            return redirect(url_for('registrierung'))

        # Nutzt die vorhandene Funktion aus deinem benutzer-Modul
        success, message = benutzer.benutzer_anlegen(name, email, password)
        
        if success:
            flash('Registrierung erfolgreich! Du kannst dich jetzt anmelden.', 'success')
            return redirect(url_for('anmeldung'))
        else:
            flash(message, 'danger')

    return render_template('registrierung.html', role=session.get('user_role', 'besucher'))

@app.route('/wein', methods=['GET', 'POST'])
def verwalte_wein():
    role = session.get('user_role', 'besucher')
    if role == 'besucher':
        flash('Bitte melde dich an, um Weine zu sehen.', 'danger')
        return redirect(url_for('anmeldung'))

    if request.method == 'POST':
        name = request.form.get('name')
        ingredients = request.form.get('ingredients').split(',')
        description = request.form.get('description')
        instructions = request.form.get('brewing_instructions')
        time = request.form.get('brewing_time')
        alcohol = request.form.get('alcohol_content')

        wine.add_wine(name, [i.strip() for i in ingredients], description, instructions, time, alcohol)
        flash(f'Wein "{name}" hinzugefügt!', 'success')
        return redirect(url_for('verwalte_wein'))

    weine = wine.get_all_wines()
    return render_template('wein.html', wines=weine, role=role)

@app.route('/essen', methods=['GET', 'POST'])
def verwalte_essen():
    role = session.get('user_role', 'besucher')
    if role == 'besucher':
        flash('Bitte melden Sie sich an.', 'danger')
        return redirect(url_for('anmeldung'))

    if request.method == 'POST':
        # ... (Logik wie gehabt)
        name = request.form.get('name', '').strip()
        # ... (Verarbeitung)
        flash('Essen gespeichert.', 'success')
        return redirect(url_for('verwalte_essen'))

    speisen_liste = essen.get_all_essen()
    return render_template('essen.html', essen=speisen_liste, role=role)

@app.route('/suche')
def suche():
    role = session.get('user_role', 'besucher')
    query = request.args.get('q', '').strip().lower()
    # ... (Suchlogik wie gehabt)
    return render_template('suche.html', query=query, weine=[], speisen=[], role=role)

if __name__ == '__main__':
    app.run(debug=True)