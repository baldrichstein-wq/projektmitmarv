from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import benutzer
import wine
import essen

app = Flask(__name__, template_folder='templates')
# Der Secret Key ist zwingend notwendig, damit Sessions sicher verschlüsselt werden können!
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'supersecretkey123')


# Initialisiere Datenbanken beim Start
benutzer.init_db()
wine.init_db()
essen.init_db()

@app.route('/')
def home():
    # Wir lesen den Namen nun aus der Flask-Session aus.
    # Ist niemand angemeldet, wird standardmäßig 'Besucher' verwendet.
    user_name = session.get('user_name', 'Besucher')
    return render_template('index.html', name=user_name)

@app.route('/ueber-uns')
def ueber_uns():
    return render_template('ueber-uns.html')

@app.route('/benutzer', methods=['GET', 'POST'])
def verwalte_benutzer():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not name or not email or not password:
            flash('Bitte füllen Sie alle Felder aus.', 'danger')
            return redirect(url_for('verwalte_benutzer'))

        success, message = benutzer.benutzer_anlegen(name, email, password)
        flash(message, 'success' if success else 'danger')
        return redirect(url_for('verwalte_benutzer'))

    users = benutzer.get_all_users()
    return render_template('benutzer.html', users=users)

@app.route('/anmeldung', methods=['GET', 'POST'])
def anmeldung():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Bitte füllen Sie alle Felder aus.', 'danger')
            return redirect(url_for('anmeldung'))

        # user sollte im besten Fall ein Dictionary aus der DB zurückgeben
        user = benutzer.benutzer_anmelden(email, password)
        if user:
            # Speichere die E-Mail (und ggf. den Namen) sicher in der nutzerspezifischen Flask-Session
            session['user_email'] = email
            # Falls dein Modul den Namen zurückgibt, setze ihn hier. Behelfsmäßig nehmen wir hier die E-Mail:
            session['user_name'] = email 
            
            flash('Erfolgreich angemeldet.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Ungültige Anmeldedaten.', 'danger')

    return render_template('anmeldung.html')

@app.route('/abmeldung')
def abmeldung():
    # Lösche den Nutzer aus der Flask-Session des aktuellen Browsers
    session.pop('user_email', None)
    session.pop('user_name', None)
    
    # Falls das benutzer-Modul noch interne Logiken hat:
    try:
        benutzer.benutzer_abmelden()
    except AttributeError:
        pass # Ignorieren, falls die Funktion nicht existiert

    flash('Erfolgreich abgemeldet.', 'success')
    return redirect(url_for('home'))

@app.route('/wein', methods=['GET', 'POST'])
def verwalte_wein():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        ingredients = request.form.get('ingredients', '').strip()
        description = request.form.get('description', '').strip()
        brewing_instructions = request.form.get('brewing_instructions', '').strip()
        brewing_time = request.form.get('brewing_time', '').strip()
        alcohol_content = request.form.get('alcohol_content', '').strip()

        if not name or not ingredients or not description:
            flash('Bitte füllen Sie mindestens Name, Zutaten und Beschreibung aus.', 'danger')
            return redirect(url_for('verwalte_wein'))

        try:
            brewing_time_int = int(brewing_time) if brewing_time else 0
            alcohol_float = float(alcohol_content) if alcohol_content else 0.0
        except ValueError:
            flash('Gärzeit muss eine Zahl und Alkoholgehalt eine Dezimalzahl sein.', 'danger')
            return redirect(url_for('verwalte_wein'))

        wine.add_wine(
            name=name,
            ingredients=[item.strip() for item in ingredients.split(',') if item.strip()],
            description=description,
            brewing_instructions=brewing_instructions,
            brewing_time=brewing_time_int,
            alcohol_content=alcohol_float,
        )
        flash(f"Wein '{name}' wurde gespeichert.", 'success')
        return redirect(url_for('verwalte_wein'))

    wines = wine.get_all_wines()
    return render_template('wein.html', wines=wines)

@app.route('/wein/loeschen/<int:wine_id>', methods=['POST'])
def loesche_wein(wine_id):
    deleted = wine.delete_wine(wine_id)
    if deleted:
        flash('Wein erfolgreich gelöscht.', 'success')
    else:
        flash('Wein nicht gefunden.', 'danger')
    return redirect(url_for('verwalte_wein'))

@app.route('/essen', methods=['GET', 'POST'])
def verwalte_essen():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        ingredients = request.form.get('ingredients', '').strip()
        description = request.form.get('description', '').strip()
        zubereitung = request.form.get('zubereitung', '').strip()
        kochzeit = request.form.get('Kochzeit', '').strip()

        # NEU: Validierung eingefügt, damit keine leeren Einträge in die DB kommen
        if not name or not ingredients or not description:
            flash('Bitte füllen Sie mindestens Name, Zutaten und Beschreibung aus.', 'danger')
            return redirect(url_for('verwalte_essen'))

        try:
            kochzeit_int = int(kochzeit) if kochzeit else 0
            essen.add_essen(
                name=name,
                zutaten=[i.strip() for i in ingredients.split(',') if i.strip()],
                description=description,
                kochanweisung=zubereitung, 
                kochzeit=kochzeit_int      
            )
            flash(f"Essen '{name}' gespeichert.", 'success')
        except ValueError:
            flash('Fehler bei den Eingabedaten. Kochzeit muss eine Zahl sein.', 'danger')
        
        return redirect(url_for('verwalte_essen'))

    speisen_liste = essen.get_all_essen()
    return render_template('essen.html', essen=speisen_liste)

@app.route('/essen/loeschen/<int:essen_id>', methods=['POST'])
def loesche_essen(essen_id):
    deleted = essen.delete_essen(essen_id)
    if deleted:
        flash('Essen erfolgreich gelöscht.', 'success')
    else:
        flash('Essen nicht gefunden.', 'danger')
    return redirect(url_for('verwalte_essen'))

@app.route('/suche')
def suche():
    query = request.args.get('q', '').strip().lower()
    ergebnisse_wein = []
    ergebnisse_essen = []

    if query:
        # Suche in Weinen
        alle_weine = wine.get_all_wines()
        ergebnisse_wein = [w for w in alle_weine if query in w['name'].lower() or query in w['description'].lower()]
        
        # Suche in Essen
        alle_speisen = essen.get_all_essen()
        ergebnisse_essen = [e for e in alle_speisen if query in e['name'].lower() or query in e['description'].lower()]

    # KORREKTUR: Typo in Template-Name korrigiert ('suche.html' statt 'such.html')
    return render_template('suche.html', query=query, weine=ergebnisse_wein, speisen=ergebnisse_essen)

if __name__ == '__main__':
    app.run(debug=True)