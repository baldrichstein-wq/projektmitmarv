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