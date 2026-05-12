from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import re
import benutzer
import wine
import essen

app = Flask(__name__, template_folder='templates')
app.secret_key = 'supersecretkey123' 

# --- UTILITY FUNKTIONEN (aus rechner.py) ---

def skaliere_zutaten(zutaten_liste, original_menge, ziel_menge):
    """
    Extrahiert Zahlen aus den Zutaten-Strings und skaliert sie proportional.
    """
    if not original_menge or original_menge == 0:
        return zutaten_liste
        
    faktor = float(ziel_menge) / float(original_menge)
    skalierte_liste = []

    for zutat in zutaten_liste:
        # Sucht nach Zahlen (auch Kommazahlen) am Anfang oder innerhalb des Strings
        match = re.match(r"(\d+([.,]\d+)?)\s*(.*)", zutat)
        if match:
            menge = float(match.group(1).replace(',', '.'))
            einheit_und_name = match.group(3)
            neue_menge = round(menge * faktor, 2)
            # Formatierung zurück zu Deutsch (Punkt zu Komma)
            neue_menge_str = str(neue_menge).replace('.', ',').rstrip('0').rstrip(',')
            skalierte_liste.append(f"{neue_menge_str} {einheit_und_name}")
        else:
            # Falls keine Zahl gefunden wurde, einfach übernehmen
            skalierte_liste.append(zutat)
            
    return skalierte_liste

# --- DATENBANK INITIALISIERUNG ---

benutzer.init_db()
wine.init_db()
essen.init_db()

# --- ROUTEN ---

@app.route('/')
def home():
    role = request.args.get('role', session.get('user_role', 'besucher'))
    name = session.get('user_name', role)
    return render_template('index.html', name=name, role=role)

@app.route('/ueber-uns')
def ueber_uns():
    role = request.args.get('role', session.get('user_role', 'besucher'))
    return render_template('ueber-uns.html', role=role)

@app.route('/benutzer', methods=['GET', 'POST'])
def verwalte_benutzer():
    role = request.args.get('role', session.get('user_role', 'besucher'))
    if role != 'admin':
        flash('Zugriff verweigert: Nur Administratoren dürfen Benutzer verwalten.', 'danger')
        return redirect(url_for('home', role=role))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not name or not email or not password:
            flash('Bitte füllen Sie alle Felder aus.', 'danger')
            return redirect(url_for('verwalte_benutzer', role=role))

        success, message = benutzer.benutzer_anlegen(name, email, password)
        flash(message, 'success' if success else 'danger')
        return redirect(url_for('verwalte_benutzer', role=role))

    users = benutzer.get_all_users()
    return render_template('benutzer.html', users=users, role=role)

@app.route('/anmeldung', methods=['GET', 'POST'])
def anmeldung():
    role = request.args.get('role', session.get('user_role', 'besucher'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Bitte füllen Sie alle Felder aus.', 'danger')
            return redirect(url_for('anmeldung', role=role))

        user = benutzer.benutzer_anmelden(email, password)
        if user:
            session['user_email'] = email
            session['user_name'] = user.get('name', email)
            session['user_role'] = user.get('rolle', 'besucher')
            flash(f"Willkommen {session['user_name']}!", 'success')
            return redirect(url_for('home', role=session['user_role']))
        else:
            flash('Ungültige Anmeldedaten.', 'danger')

    return render_template('anmeldung.html', role=role)

@app.route('/abmeldung')
def abmeldung():
    session.clear()
    try:
        benutzer.benutzer_abmelden()
    except AttributeError:
        pass
    flash('Erfolgreich abgemeldet.', 'success')
    return redirect(url_for('home'))

# --- WEIN SEKTION ---

@app.route('/wein', methods=['GET', 'POST'])
def verwalte_wein():
    role = request.args.get('role', session.get('user_role', 'besucher'))

    if role == 'besucher':
        flash('Zugriff verweigert: Bitte melde dich an, um Weine zu verwalten.', 'danger')
        return redirect(url_for('home', role=role))

    if request.method == 'POST':
        name = request.form.get('name')
        ingredients = request.form.get('ingredients').split(',') # Annahme: Komma-getrennt
        description = request.form.get('description')
        instructions = request.form.get('brewing_instructions')
        time = request.form.get('brewing_time')
        alcohol = request.form.get('alcohol_content')

        wine.add_wine(name, [i.strip() for i in ingredients], description, instructions, time, alcohol)
        flash(f'Wein "{name}" erfolgreich hinzugefügt!', 'success')
        return redirect(url_for('verwalte_wein', role=role))

    weine = wine.get_all_wines()
    return render_template('wein.html', wines=weine, role=role)

@app.route('/wein/rechner/<int:wine_id>', methods=['GET', 'POST'])
def rechner_wein(wine_id):
    role = request.args.get('role', session.get('user_role', 'besucher'))
    rezept = wine.get_wine(wine_id) # Erfordert get_wine() in wine.py
    
    if not rezept:
        flash('Wein-Rezept nicht gefunden.', 'danger')
        return redirect(url_for('verwalte_wein', role=role))

    ziel_liter = request.args.get('liter', 5.0, type=float)
    basis_liter = 5.0 # Standardbasis aus rechner.py
    
    skalierte_zutaten_liste = skaliere_zutaten(rezept['ingredients'], basis_liter, ziel_liter)
    
    return render_template('wein_rechner.html', 
                           rezept=rezept, 
                           zutaten=skalierte_zutaten_liste, 
                           ziel=ziel_liter, 
                           role=role)

@app.route('/wein/loeschen/<int:wine_id>', methods=['POST'])
def loesche_wein(wine_id):
    role = request.args.get('role', session.get('user_role', 'besucher'))
    if role != 'admin':
        flash('Fehler: Nur Administratoren dürfen Einträge löschen!', 'danger')
        return redirect(url_for('verwalte_wein', role=role))

    wine.delete_wine(wine_id)
    flash('Wein gelöscht.', 'success')
    return redirect(url_for('verwalte_wein', role=role))

# --- ESSEN SEKTION ---

@app.route('/essen', methods=['GET', 'POST'])
def verwalte_essen():
    role = request.args.get('role', session.get('user_role', 'besucher'))
    if role == 'besucher':
        flash('Bitte melden Sie sich an, um Rezepte zu verwalten.', 'danger')
        return redirect(url_for('home', role=role))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        personenanzahl = request.form.get('personenanzahl', '').strip()
        ingredients = request.form.get('ingredients', '').strip()
        description = request.form.get('description', '').strip()
        zubereitung = request.form.get('zubereitung', '').strip()
        kochzeit = request.form.get('kochzeit', '').strip()

        if not name or not ingredients or not description:
            flash('Bitte füllen Sie mindestens Name, Zutaten und Beschreibung aus.', 'danger')
            return redirect(url_for('verwalte_essen', role=role))

        try:
            kochzeit_int = int(kochzeit) if kochzeit else 0
            essen.add_essen(
                name=name,
                personenanzahl=int(personenanzahl),
                zutaten=[i.strip() for i in ingredients.split(',') if i.strip()],
                description=description,
                kochanweisung=zubereitung,
                kochzeit=kochzeit_int,
            )
            flash('Essen gespeichert.', 'success')
        except ValueError:
            flash('Fehler bei den Eingabedaten. Personen und Kochzeit müssen Zahlen sein.', 'danger')

        return redirect(url_for('verwalte_essen', role=role))

    speisen_liste = essen.get_all_essen()
    return render_template('essen.html', essen=speisen_liste, role=role)

@app.route('/essen/rechner/<int:essen_id>', methods=['GET'])
def rechner_essen(essen_id):
    role = request.args.get('role', session.get('user_role', 'besucher'))
    rezept = essen.get_essen(essen_id) # Erfordert get_essen() in essen.py
    
    if not rezept:
        flash('Rezept nicht gefunden.', 'danger')
        return redirect(url_for('verwalte_essen', role=role))

    # Standardmäßig die Original-Personenanzahl nehmen, falls nichts angegeben
    basis_personen = float(rezept.get('personenanzahl', 1))
    ziel_personen = request.args.get('personen', basis_personen, type=float)
    
    skalierte_zutaten_liste = skaliere_zutaten(rezept['ingredients'], basis_personen, ziel_personen)
    
    return render_template('essen_rechner.html', 
                           rezept=rezept, 
                           zutaten=skalierte_zutaten_liste, 
                           ziel=ziel_personen, 
                           role=role)

@app.route('/essen/loeschen/<int:essen_id>', methods=['POST'])
def loesche_essen(essen_id):
    role = request.args.get('role', session.get('user_role', 'besucher'))
    if role != 'admin':
        flash('Nur Administratoren können Rezepte löschen.', 'danger')
        return redirect(url_for('verwalte_essen', role=role))

    deleted = essen.delete_essen(essen_id)
    if deleted:
        flash('Erfolgreich gelöscht.', 'success')
    else:
        flash('Essen nicht gefunden.', 'danger')
    return redirect(url_for('verwalte_essen', role=role))

# --- SUCHE ---

@app.route('/suche')
def suche():
    role = request.args.get('role', session.get('user_role', 'besucher'))
    query = request.args.get('q', '').strip().lower()
    ergebnisse_wein = []
    ergebnisse_essen = []

    if query:
        alle_weine = wine.get_all_wines()
        ergebnisse_wein = [w for w in alle_weine if query in w.get('name', '').lower() or query in w.get('description', '').lower()]

        alle_speisen = essen.get_all_essen()
        ergebnisse_essen = [e for e in alle_speisen if query in e.get('name', '').lower() or query in e.get('description', '').lower()]

    return render_template('suche.html', query=query, weine=ergebnisse_wein, speisen=ergebnisse_essen, role=role)

if __name__ == '__main__':
    app.run(debug=True)