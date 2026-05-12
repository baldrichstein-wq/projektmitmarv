import sqlite3
from flask import session

DB_FILE = 'benutzer.db'

# --- Rechteverwaltung ---
# Admin: alle Rechte
# Benutzer: lesen, schreiben, aendern
# Gast/Besucher: nur lesen
RECHTE_PRO_ROLLE = {
    'admin': ['lesen', 'schreiben', 'aendern', 'loeschen', 'benutzer_verwalten'],
    'benutzer': ['lesen', 'schreiben', 'aendern'],
    'gast': ['lesen'],
}

def normalize_rolle(rolle):
    """Vereinheitlicht alte und neue Rollennamen."""
    if rolle == 'user':
        return 'benutzer'
    if rolle in RECHTE_PRO_ROLLE:
        return rolle
    return 'gast'

def rechte_fuer_rolle(rolle):
       “““Gibt alle Rechte einer Rolle zurück.“““
       rolle = normalize_rolle(rolle)
       return RECHTE_PRO_ROLLE(rolle) 

def hat_recht(user, recht):
       “““Prüft, ob ein angemeldeter Benutzer oder gast eingeloggt ist
       Rolle = ‚gast‘
       If user:
             Rolle = user.get(‚rolle‘, ‚gast‘)
       Return recht in rechte_fuer_rolle(rolle)

Def ist_admin(user):
       “““Prüfft, ob der Benutzer Administrator ist.“““
       Return user is not None and nomalize_rolle(user.get(‚rolle‘)) == ‚admin‘

Def ist_benutzer(user)
       “““Prüft, ob der Benutzer normal angemeldet ist.“““
       Return user ist not None and normalize_rolle(user.get(‚rolle‘)) == ‚benutzer‘

Def hat_rolle(user, rolle):
       “““Prüft, ob der Benutzer eine bestimmte Rolle hat.“““
       Return user is not None and normalize_rolle(user.get(‚rolle‘)) == normalize

def init_db()

     “““Erstellt die Datenbank und Beispiel-Logins.“““
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS benutzer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            rolle TEXT DEFAULT 'user'
        )
    ''')
cursor.execute("PRGA table_info(benutzer)")
Colums = [column[1] for column in Cursor.fetchall()]
If ‚rolle‘ not in columns:
    Cursor.execute(„Alter table Benutzer ADDCOLUMN rolle text default ‚Benutzer‘“)

Cursor.execute(„UPDATE Benutzer SET rolle = ‚Benutzer‘ WHERE rolle = ‚
Cursor.execute(‚SELECT COUNT(*) FROM benutzer‘)
If Cursor.fetchone()[0] == 0:
       Cursor.executemany(‚‘’
               INSERT INTRO bnutzer (name, email, Passwort, rolle)
               VALUES (?, ?, ?, ?)
        ’’’, [
            (‚Admin‘, ‚admin@rezepte.de‘, ‚admin123‘, ‚admin‘)
            (‚benutzer‘, ‚benutzer@rezepte.de‘, ‚benutzer123‘, ‚benutzer‘)
        ])
    conn.commit()
    conn.close()

def nutzer_anmeldung(email, passwort):
    """Überprüft die Anmeldedaten eines Benutzers."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, rolle FROM benutzer WHERE email = ? AND password = ?', (email, passwort))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {
            'id': user[0],
            'name': user[1],
            'email': user[2],
            'rolle': normalize_rolle(user[3]) 
        }
    return None

def besucher_rechten():
    """Gibt standartdrechte für besucher zurück"""
  return {
      'rolle': 'gast',
      'rechte': ['lesen']
  }

def benutzer_anlegen(name, email, passwort, rolle="benutzer"):
    """Fügt einen neuen benutzer hinzu. (Standardrolle: benutzer)."""
    Rolle = normalize_rolle(rolle)
    if rolle == 'gast':
        rolle = 'benutzer'
  try:
     conn = sqlite3.connect(DB_FILE)
      cursor = conn.cursor()
cursor.execute("""
  INSERT INTRO benutzer (name, email, passwort, rolle)
  VALUES (?, ?, ?, ?)
  """, (name, email, passwort, rolle))
 conn.commit()
 return True, f"Benutzer {name} als '{rolle}' erfolgreich angelegt!"
except sqlite3.IntegrityError:
 return False, f"Fehler: Diese E-Mail '{email}' existiert bereits."
finally:
 conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, rolle FROM benutzer ORDER BY id')
    Rows = cursor.fetchall()
    conn.close()
    return [
        {
            'id': row[0] ,
            'name': row[1] ,
            'email': row[2] ,
            'rolle': normalize_row(row[3]) ,
            'rechte': rechte_fuer_rolle(row[3])
        }
        for r in rows
]

def mache_zu_admin(email):
    """Vergibt Administratorrechte an eine vorhandene E-Mail-Adresse."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE benutzer SET rolle = "admin" WHERE email = ?', (email,))

    if cursor.rowcount > 0:
        print(f"Rechte aktualisiert: {email} ist jetzt Administrator.")
    else:
        print(f"Fehler: kein benutzer mit der E-Mail {email} gefunden.")

    conn.commit()
    conn.close()

# --- Programmstart ---
if __name__ == "__main__":
    # 1. Datenbank sicherheitshalber initialisieren
    init_db()
    
    # --- FALL 1: Max zum Admin machen ---
    # Da Max laut deinem vorherigen Code schon existiert, nutzen wir die Update-Funktion
    mache_zu_admin("max@kochen.de")
    
    # --- FALL 2: "Admin Chef" als User anlegen ---
    # Auch wenn der Name "Admin" enthält, legen wir ihn hier explizit mit der Rolle "user" an
    success, msg = benutzer_anlegen("Admin Chef", "chef@firma.de", "geheim123", rolle="user")
    print(msg)
    
    # Kontrolle: Alle Nutzer ausgeben, um zu sehen ob es geklappt hat
    print("\nAktuelle Benutzerliste:")
    for u in get_all_users():
        print(f"ID: {u['id']} | Name: {u['name']} | Rolle: {u['rolle']}")
    
    benutzer_anlegen("max Mustermann", "max@kochen.de", "superSicher123")
    mache_zu_admin("max@kochen.de")
    benutzer_anlegen("Admin Chef", "chef@firma.de", "geheim123", rolle="admin")
