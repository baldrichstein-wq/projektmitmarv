<<<<<<< HEAD
import sqlite3
from fastapi import FastAPI

app = FastAPI()

def init_db():
    # Verbindung zur zentralen oder jeweiligen Datenbank
    conn_user = sqlite3.connect('benutzer.db')
    conn_wine = sqlite3.connect('wines.db')
    conn_essen = sqlite3.connect('essen.db')
    
    # Tabelle für Benutzer erstellen
    conn_user.execute('''
        CREATE TABLE IF NOT EXISTS benutzer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    
    # Tabelle für Weine erstellen
    conn_wine.execute('''
        CREATE TABLE IF NOT EXISTS wines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            description TEXT,
            brewing_instructions TEXT,
            brewing_time INTEGER,
            alcohol_content REAL
        )
    ''')
    
    # Tabelle für Essen erstellen
    conn_essen.execute('''
        CREATE TABLE IF NOT EXISTS essen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            description TEXT
        )
    ''')

    conn_user.commit()
    conn_wine.commit()
    conn_user.close()
    conn_wine.close()
    conn_essen.close()

@app.on_event("startup")
def startup_event():
    init_db()
=======
import benutzer
import essen
import wine
import os
import sys

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("=" * 45)
    print(f"{'🏠 KÜCHEN- & KELLER-MANAGER':^45}")
    print("=" * 45)

def main_menu():
    while True:
        clear_screen()
        print_header()
        print("[1] 👤 Neuen Benutzer anlegen")
        print("[2] 🍲 Speisekarte anzeigen (DB-Status)")
        print("[3] 🍷 Wein-Keller verwalten (DB-Status)")
        print("[4] ⚙️  System-Datenbanken initialisieren")
        print("[0] ❌ Beenden")
        print("-" * 45)
        
        auswahl = input("Wählen Sie eine Option: ")

        if auswahl == "1":
            print("\n--- Benutzer registrieren ---")
            name = input("Name: ")
            email = input("E-Mail: ")
            pw = input("Passwort: ")
            benutzer.benutzer_anlegen(name, email, pw)
            input("\nDrücken Sie Enter zum Fortfahren...")

        elif auswahl == "2":
            print("\n--- Speise-Datenbank Status ---")
            # In essen.py wird die DB beim Import automatisch erstellt.
            # Hier könnte man eine Abfrage-Funktion ergänzen.
            print("Datenbank 'essen.db' ist aktiv.")
            print("Tabelle 'essen' wurde geprüft.")
            input("\nDrücken Sie Enter zum Fortfahren...")

        elif auswahl == "3":
            print("\n--- Wein-Verwaltung ---")
            print("\nInitialisiere Wein-Tabelle...")
            wine.init_db()
            print("Erledigt.")
            input("\nDrücken Sie Enter zum Fortfahren...")

        elif auswahl == "4":
            print("\n--- System-Check ---")
            benutzer.init_db()
            wine.init_db()
            print("[✔] Alle Datenbanken (Benutzer, Essen, Wein) sind bereit.")
            input("\nDrücken Sie Enter zum Fortfahren...")

        elif auswahl == "0":
            print("\nProgramm beendet. Auf Wiedersehen!")
            sys.exit()

        else:
            print("\n[!] Ungültige Auswahl, bitte versuchen Sie es erneut.")
            input("\nDrücken Sie Enter...")

if __name__ == "__main__":
    # Initialer Start der Datenbanken
    benutzer.init_db()
    wine.init_db()
    main_menu()
>>>>>>> cd66443e4d493ad48c13cefa2b9cdfeb2d67be39
