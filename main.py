from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import benutzer
import wine
import essen

app = Flask(__name__, template_folder='templates')
app.secret_key = 'supersecretkey123'  # Bleibt für flash() notwendig

# Initialisiere Datenbanken
benutzer.init_db()
wine.init_db()
essen.init_db()

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
    session.pop('user_email', None)
    session.pop('user_name', None)
    session.pop('user_role', None)

    try:
        benutzer.benutzer_abmelden()
    except AttributeError:
        pass

    flash('Erfolgreich abgemeldet.', 'success')
    return redirect(url_for('home'))

@app.route('/wein', methods=['GET', 'POST'])
def verwalte_wein():
    # 1. Rolle sofort prüfen
    role = request.args.get('role', 'besucher')

    # 2. Sicherheits-Check: Besucher komplett aussperren
    if role == 'besucher':
        flash('Zugriff verweigert: Bitte melde dich an, um Weine zu verwalten.', 'danger')
        return redirect(url_for('home', role=role))

    # 3. Erst nach dem Check die POST-Logik (Erstellen) erlauben
    if request.method == 'POST':
        name = request.form.get('name')
        ingredients = request.form.getlist('ingredients')
        description = request.form.get('description')
        instructions = request.form.get('brewing_instructions')
        time = request.form.get('brewing_time')
        alcohol = request.form.get('alcohol_content')

        # Wein hinzufügen (aus wine.py)
        wine.add_wine(name, ingredients, description, instructions, time, alcohol)

        flash(f'Wein "{name}" erfolgreich hinzugefügt!', 'success')
        return redirect(url_for('verwalte_wein', role=role))

    # GET-Teil: Liste anzeigen
    weine = wine.get_all_wines()
    return render_template('wein.html', wines=weine, role=role)

@app.route('/wein/loeschen/<int:wine_id>', methods=['POST'])
def loesche_wein(wine_id):
    role = request.args.get('role', 'besucher')

    # STRENGER CHECK: Nur Admin darf löschen
    if role != 'admin':
        flash('Fehler: Nur Administratoren dürfen Einträge löschen!', 'danger')
        return redirect(url_for('verwalte_wein', role=role))

    wine.delete_wine(wine_id)
    flash('Wein gelöscht.', 'success')
    return redirect(url_for('verwalte_wein', role=role))

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
                personenanzahl=personenanzahl,
                zutaten=[i.strip() for i in ingredients.split(',') if i.strip()],
                description=description,
                kochanweisung=zubereitung,
                kochzeit=kochzeit_int,
            )
            flash('Essen gespeichert.', 'success')
        except ValueError:
            flash('Fehler bei den Eingabedaten. Kochzeit muss eine Zahl sein.', 'danger')

        return redirect(url_for('verwalte_essen', role=role))

    speisen_liste = essen.get_all_essen()
    return render_template('essen.html', essen=speisen_liste, role=role)

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
