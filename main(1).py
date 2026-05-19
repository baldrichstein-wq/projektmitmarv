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
    # Vereinheitlichung: Wenn keine Rolle in der Session, dann 'gast'
    role = session.get('user_role', 'gast')
    name = session.get('user_name', 'Gast')
    return render_template('index.html', name=name, role=role)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0' ,port=port, debug=True)

@app.route('/ueber-uns')
def ueber_uns():
    role = session.get('user_role', 'gast')
    return render_template('ueber-uns.html', role=role)

@app.route('/benutzer', methods=['GET', 'POST'])
def verwalte_benutzer():
    role = session.get('user_role', 'gast')
    if role != 'admin':
        flash('Zugriff verweigert: Nur Administratoren dürfen Benutzer verwalten.', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        success, message = benutzer.benutzer_anlegen(name, email, password)
        flash(message, 'success' if success else 'danger')
        return redirect(url_for('verwalte_benutzer'))

    users = benutzer.get_all_users()
    return render_template('benutzer.html', users=users, role=role)
# Hier wird die Lösch-Funktion aus deinem benutzer-Modul aufgerufen
@app.route('/benutzer/loeschen/<int:user_id>', methods=['POST'])
def loesche_benutzer(user_id):
    role = session.get('user_role', 'gast')
    if role != 'admin':
        flash('Zugriff verweigert: Nur Administratoren dürfen Benutzer löschen.', 'danger')
        return redirect(url_for('home'))

    success, message = benutzer.benutzer_loeschen(user_id)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('verwalte_benutzer'))

@app.route('/anmeldung', methods=['GET', 'POST'])
def anmeldung():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        user = benutzer.benutzer_anmelden(email, password)
        if user:
            session['user_email'] = email
            session['user_name'] = user.get('name', email)
            session['user_role'] = user.get('rolle', 'gast')
            flash(f"Willkommen {session['user_name']}!", 'success')
            return redirect(url_for('home'))
        else:
            flash('Ungültige Anmeldedaten.', 'danger')

    return render_template('anmeldung.html', role=session.get('user_role', 'gast'))

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

        success, message = benutzer.benutzer_anlegen(name, email, password)
        
        if success:
            flash('Registrierung erfolgreich! Du kannst dich jetzt anmelden.', 'success')
            return redirect(url_for('anmeldung'))
        else:
            flash(message, 'danger')

    return render_template('registrierung.html', role=session.get('user_role', 'gast'))

@app.route('/wein_edit/<int:wine_id>', methods=['GET', 'POST'])
def update_wine(wine_id):
    get_wine_by_id = wine.get_wine_by_id(wine_id)
    if not get_wine_by_id:
        flash('Wein nicht gefunden.', 'danger')
        return redirect(url_for('wein_verwalten'))
    
    role = session.get('user_role', 'gast')
    if role != 'benutzer' and role != 'admin':
        flash('Nur Administratoren und Benutzer können Weine bearbeiten.', 'danger')
        return redirect(url_for('wein_verwalten'))

    if request.method == 'POST':
        name = request.form.get('name')
        liter = request.form.get('liter', '5')
        ingredients = request.form.get('ingredients', '').split(',')
        description = request.form.get('description')
        instructions = request.form.get('brewing_instructions')
        time = request.form.get('brewing_time')
        alcohol = request.form.get('alcohol_content')

        if not name:
            flash('Fehler: Der Name des Weins darf nicht leer sein!', 'danger')
            return redirect(url_for('update_wine', wine_id=wine_id))

        wine.update_wine(wine_id, name, liter, [i.strip() for i in ingredients], description, instructions, time, alcohol)
        flash(f'Wein "{name}" wurde aktualisiert!', 'success')
        return redirect(url_for('wein_verwalten'))

    wine_data = wine.get_wine_by_id(wine_id)
    return render_template('wein_edit.html', wine=wine_data, role=role)

@app.route('/wein', methods=['GET', 'POST'])
def wein_verwalten():
    role = session.get('user_role', 'gast')
    if role != 'benutzer' and role != 'admin':
        flash('Bitte melde dich an, um Weine zu sehen.', 'danger')
        return redirect(url_for('anmeldung'))

    if request.method == 'POST':
        name = request.form.get('name')
        liter = request.form.get('liter', '5')
        ingredients = request.form.get('ingredients').split(',')
        description = request.form.get('description')
        instructions = request.form.get('brewing_instructions')
        time = request.form.get('brewing_time')
        alcohol = request.form.get('alcohol_content')

        wine.add_wine(name, liter, [i.strip() for i in ingredients], description, instructions, time, alcohol)
        flash(f'Wein "{name}" hinzugefügt!', 'success')
        return redirect(url_for('wein_verwalten'))

    weine = wine.get_all_wines()
    return render_template('wein.html', wines=weine, role=role)
@app.route('/wein/loeschen/<int:wine_id>', methods=['POST'])
def loesche_wein(wine_id):
    role = session.get('user_role', 'gast')
    if role != 'admin':
        flash('Nur Administratoren können Weine löschen.', 'danger')
        return redirect(url_for('wein_verwalten'))
    
    # Hier wird die Lösch-Funktion aus deinem wine-Modul aufgerufen
    if wine.delete_wine(wine_id):
        flash('Wein wurde erfolgreich gelöscht.', 'success')
    else:
        flash('Fehler beim Löschen des Weins.', 'danger')
        
    return redirect(url_for('wein_verwalten'))

@app.route('/benutzer/rolle_aendern/<int:user_id>', methods=['POST'])
def rolle_update(user_id):
    if session.get('user_role') != 'admin':
        flash('Nicht autorisiert.', 'danger')
        return redirect(url_for('home'))
    
    neue_rolle = request.form.get('rolle')
    if benutzer.rolle_aendern(user_id, neue_rolle):
        flash(f'Rolle für Benutzer ID {user_id} wurde auf {neue_rolle} aktualisiert.', 'success')
    else:
        flash('Fehler beim Aktualisieren der Rolle.', 'danger')
    
    return redirect(url_for('verwalte_benutzer'))

@app.route('/essen', methods=['GET', 'POST'])
def verwalte_essen():
    role = session.get('user_role', 'gast')
    if role == 'gast':
        flash('Bitte melden Sie sich an.', 'danger')
        return redirect(url_for('anmeldung'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        personen = request.form.get('personenanzahl', '4')
        zutaten = request.form.get('ingredients', '').split(',')
        desc = request.form.get('description', '').strip()
        anw = request.form.get('kochanweisung', '').strip()
        zeit = request.form.get('kochzeit', '0')
        
        essen.add_essen(name, int(personen), [z.strip() for z in zutaten], desc, anw, int(zeit))
        flash('Essen gespeichert.', 'success')
        return redirect(url_for('verwalte_essen'))

    speisen_liste = essen.get_all_essen()
    return render_template('essen.html', essen=speisen_liste, role=role)

@app.route('/essen/bearbeiten/<int:essen_id>', methods=['GET', 'POST'])
def bearbeite_essen(essen_id):
    role = session.get('user_role', 'gast')
    if role == 'gast':
        flash('Bitte melde dich an.', 'danger')
        return redirect(url_for('anmeldung'))

    aktuelles_essen = essen.get_essen(essen_id)
    if not aktuelles_essen:
        flash('Rezept nicht gefunden.', 'danger')
        return redirect(url_for('verwalte_essen'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        personen = int(request.form.get('personenanzahl') or 1)
        zutaten = request.form.get('ingredients', '').split(',')
        desc = request.form.get('description', '').strip()
        anw = request.form.get('kochanweisung', '').strip()
        zeit = int(request.form.get('Kochzeit') or 0)

        essen.update_essen(essen_id, name, personen, [z.strip() for z in zutaten], desc, anw, zeit)
        flash(f'Rezept "{name}" wurde aktualisiert.', 'success')
        return redirect(url_for('verwalte_essen'))

    return render_template('essen_edit.html', essen=aktuelles_essen, role=role)

def get_essen(essen_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, personenanzahl, ingredients, description, kochanweisung, kochzeit FROM essen WHERE id = ?', (essen_id,))
        row = cursor.fetchone()
    if row:
        return {
            'id': row[0],
            'name': row[1],
            'personenanzahl': row[2],
            'ingredients': json.loads(row[3]),
            'description': row[4],
            'kochanweisung': row[5],
            'kochzeit': row[6],
        }
    return None

def update_essen(essen_id, name, personenanzahl, ingredients, description, kochanweisung, kochzeit):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE essen
            SET name = ?, personenanzahl = ?, ingredients = ?, description = ?, kochanweisung = ?, kochzeit = ?
            WHERE id = ?
        ''', (name, personenanzahl, json.dumps(ingredients), description, kochanweisung, kochzeit, essen_id))
        conn.commit()
        return cursor.rowcount > 0
    
@app.route('/essen/loeschen/<int:essen_id>', methods=['POST'])
def loesche_essen(essen_id):
    role = session.get('user_role', 'gast')
    if role != 'admin':
        flash('Nur Administratoren können Rezepte löschen.', 'danger')
        return redirect(url_for('verwalte_essen'))
    
    # Hier wird die Lösch-Funktion aus deinem wine-Modul aufgerufen
    if essen.delete_essen(essen_id):
        flash('Rezept wurde erfolgreich gelöscht.', 'success')
    else:
        flash('Fehler beim Löschen des Rezepts.', 'danger')
        
    return redirect(url_for('verwalte_essen'))

@app.route('/suche')
def suche():
    role = session.get('user_role', 'gast')
    query = request.args.get('q', '').strip().lower()
    
    gefundene_weine = []
    gefundene_speisen = []

    if query:
        # Weine durchsuchen (Name, Beschreibung und jede einzelne Zutat)
        alle_weine = wine.get_all_wines()
        for w in alle_weine:
            zutaten_string = " ".join(w['ingredients']).lower()
            if (query in w['name'].lower() or 
                (w['description'] and query in w['description'].lower()) or 
                query in zutaten_string):
                gefundene_weine.append(w)

        # Speisen durchsuchen (Name, Beschreibung und jede einzelne Zutat)
        alle_speisen = essen.get_all_essen()
        for e in alle_speisen:
            zutaten_string = " ".join(e['ingredients']).lower()
            if (query in e['name'].lower() or 
                (e['description'] and query in e['description'].lower()) or 
                query in zutaten_string):
                gefundene_speisen.append(e)

    return render_template('suche.html', 
                           query=query, 
                           weine=gefundene_weine, 
                           speisen=gefundene_speisen, 
                           role=role)

if __name__ == '__main__':
    app.run(debug=True)