#!/usr/bin/env python3
"""
Rezeptbuch-Anwendung
- Benutzerregistrierung & Anmeldung
- CRUD für Rezepte (Hinzufügen, Ändern, Löschen)
- Suchfunktion
- SQLite-Datenbank
"""

import sqlite3
import hashlib
import getpass
from datetime import datetime
from typing import Optional


# ============================================================
#  DATENBANK-INITIALISIERUNG
# ============================================================

DB_PATH = "rezeptbuch.db"


def init_db() -> sqlite3.Connection:
    """Erstellt die Datenbank und Tabellen, falls sie nicht existieren."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            category TEXT DEFAULT 'Sonstiges',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    return conn


# ============================================================
#  PASSWORT-HASHING
# ============================================================

def hash_password(password: str, salt: Optional[str] = None):
    """Hashed ein Passwort mit SHA-256 und einem Salt."""
    if salt is None:
        import os
        salt = os.urandom(32).hex()
    password_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return salt, password_hash


def verify_password(password: str, stored_salt: str, stored_hash: str) -> bool:
    """Überprüft ein Passwort gegen einen gespeicherten Hash."""
    _, computed_hash = hash_password(password, stored_salt)
    return computed_hash == stored_hash


# ============================================================
#  BENUTZER-VERWALTUNG
# ============================================================

def register_user(conn: sqlite3.Connection, username: str, password: str) -> bool:
    """Registriert einen neuen Benutzer."""
    try:
        salt, pw_hash = hash_password(password)
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, f"{salt}:{pw_hash}")
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def login_user(conn: sqlite3.Connection, username: str, password: str):
    """Loggt einen Benutzer ein und gibt die User-ID zurück."""
    cursor = conn.execute(
        "SELECT id, password_hash FROM users WHERE username = ?", (username,)
    )
    row = cursor.fetchone()

    if not row:
        return None

    user_id, stored_pw = row
    salt, pw_hash = stored_pw.split(":")

    if verify_password(password, salt, pw_hash):
        return user_id
    return None


# ============================================================
#  REZEPT-VERWALTUNG (CRUD)
# ============================================================

def add_recipe(conn: sqlite3.Connection, user_id: int, title: str,
               ingredients: str, instructions: str, category: str = "Sonstiges") -> Optional[int]:
    """Fügt ein neues Rezept hinzu und gibt die ID zurück."""
    cursor = conn.execute(
        """INSERT INTO recipes (user_id, title, ingredients, instructions, category)
           VALUES (?, ?, ?, ?, ?)""",
        (user_id, title, ingredients, instructions, category)
    )
    conn.commit()
    return cursor.lastrowid


def get_user_recipes(conn: sqlite3.Connection, user_id: int):
    """Gibt alle Rezepte des Benutzers zurück."""
    cursor = conn.execute(
        "SELECT id, title, ingredients, instructions, category, created_at, updated_at "
        "FROM recipes WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
    )
    return cursor.fetchall()


def get_recipe_by_id(conn: sqlite3.Connection, recipe_id: int, user_id: int):
    """Gibt ein einzelnes Rezept zurück."""
    cursor = conn.execute(
        "SELECT id, title, ingredients, instructions, category FROM recipes "
        "WHERE id = ? AND user_id = ?", (recipe_id, user_id)
    )
    return cursor.fetchone()


def update_recipe(conn: sqlite3.Connection, recipe_id: int, user_id: int,
                  title: str, ingredients: str, instructions: str, category: str):
    """Aktualisiert ein bestehendes Rezept."""
    conn.execute(
        """UPDATE recipes SET title = ?, ingredients = ?, instructions = ?,
           category = ?, updated_at = CURRENT_TIMESTAMP
          WHERE id = ? AND user_id = ?""",
        (title, ingredients, instructions, category, recipe_id, user_id)
    )
    conn.commit()


def delete_recipe(conn: sqlite3.Connection, recipe_id: int, user_id: int) -> bool:
    """Löscht ein Rezept. Gibt True zurück, wenn erfolgreich."""
    cursor = conn.execute(
        "DELETE FROM recipes WHERE id = ? AND user_id = ?", (recipe_id, user_id)
    )
    conn.commit()
    return cursor.rowcount > 0


# ============================================================
#  SUCHE
# ============================================================

def search_recipes(conn: sqlite3.Connection, user_id: int, query: str):
    """Sucht Rezepte nach Titel und Zutaten."""
    like_query = f"%{query}%"
    cursor = conn.execute(
        "SELECT id, title, ingredients, instructions, category, created_at, updated_at "
        "FROM recipes WHERE user_id = ? AND (title LIKE ? OR ingredients LIKE ?) "
        "ORDER BY created_at DESC",
        (user_id, like_query, like_query)
    )
    return cursor.fetchall()


# ============================================================
#  AUSGABE-HELPER
# ============================================================

def print_recipe(recipe: tuple):
    """Formatiert und gibt ein Rezept aus."""
    rid, title, ingredients, instructions, category, created, updated = recipe
    print("\n" + "=" * 60)
    print(f"  📖 [{rid}] {title}")
    print("=" * 60)
    print(f"  Kategorie:   {category}")
    print(f"  Erstellt am: {created}")
    print(f"  Geändert am: {updated}")
    print("-" * 60)
    print("  🥄 Zutaten:")
    for line in ingredients.strip().split("\n"):
        line = line.strip()
        if line:
            print(f"    • {line}")
    print("-" * 60)
    print("  👨‍🍳 Anleitung:")
    for line in instructions.strip().split("\n"):
        line = line.strip()
        if line:
            print(f"    → {line}")
    print("=" * 60 + "\n")


def print_recipe_list(recipes):
    """Gibt eine Liste von Rezepten kompakt aus."""
    if not recipes:
        print("\n  Keine Rezepte gefunden.")
        return

    print(f"\n{'ID':<5} {'Titel':<30} {'Kategorie':<15} {'Erstellt am'}")
    print("-" * 80)
    for r in recipes:
        rid, title, _, _, category, created, _ = r
        # Titel kürzen
        display_title = (title[:27] + "...") if len(title) > 30 else title
        print(f"{rid:<5} {display_title:<30} {category:<15} {created}")
    print()


# ============================================================
#  EINGABE-HELPER
# ============================================================

def get_multiline_input(prompt: str, field_name: str) -> str:
    """Liest mehrzeilige Eingabe ein. Beenden mit leerer Zeile oder 'END'."""
    print(f"\n{prompt}")
    print("  (Schreibe deine Zeilen und drücke Enter.)")
    print("  (Beende mit einer leeren Zeile oder tippe 'END' und drücke Enter.)")

    lines = []
    while True:
        try:
            line = input(f"  > {field_name}: ").rstrip()
        except EOFError:
            break
        if line == "END" or (line == "" and len(lines) > 0):
            break
        lines.append(line)

    return "\n".join(lines)


# ============================================================
#  BENUTZEROBERFLÄCHE
# ============================================================

def auth_menu(conn: sqlite3.Connection):
    """Zeigt das Anmelde-/Registrierungs-Menü."""
    while True:
        print("\n" + "=" * 50)
        print("   🍳 REZEPTBUCH")
        print("=" * 50)
        print("   1. Registrieren")
        print("   2. Anmelden")
        print("   3. Beenden")
        print("=" * 50)

        choice = input("\nWähle eine Option (1-3): ").strip()

        if choice == "3":
            print("Tschüss! 👋")
            return None

        elif choice == "1":
            username = input("Benutzername: ").strip()
            if not username:
                print("  ❌ Benutzername darf nicht leer sein.")
                continue
            password = getpass.getpass("Passwort: ")
            if len(password) < 4:
                print("  ❌ Passwort muss mindestens 4 Zeichen haben.")
                continue

            if register_user(conn, username, password):
                print(f"  ✅ Registrierung erfolgreich! Willkommen {username}!")
                return login_user(conn, username, password)
            else:
                print("  ❌ Benutzername ist bereits vergeben.")

        elif choice == "2":
            username = input("Benutzername: ").strip()
            password = getpass.getpass("Passwort: ")
            user_id = login_user(conn, username, password)
            if user_id:
                print(f"  ✅ Angemeldet als {username}!")
                return user_id
            else:
                print("  ❌ Falscher Benutzername oder Passwort.")

        else:
            print("  ⚠️  Ungültige Option. Bitte 1, 2 oder 3 wählen.")


# ============================================================
#  REZEPT-MENU (Hauptmenü)
# ============================================================

def recipe_menu(conn: sqlite3.Connection, user_id: int):
    """Das Hauptmenü für angemeldete Benutzer."""
    # Benutzername holen
    cursor = conn.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    username = cursor.fetchone()[0]

    while True:
        print("\n" + "=" * 55)
        print(f"   🍳 REZEPTBUCH — Angemeldet als: {username}")
        print("=" * 55)
        print("   1. 📋 Meine Rezepte anzeigen")
        print("   2. ➕ Neues Rezept hinzufügen")
        print("   3. ✏️  Rezept bearbeiten")
        print("   4. 🗑️  Rezept löschen")
        print("   5. 🔍 Rezepte suchen")
        print("   6. 👤 Benutzer wechseln")
        print("   7. 🚪 Abmelden")
        print("=" * 55)

        choice = input("\nWähle eine Option (1-7): ").strip()

        if choice == "1":
            _show_my_recipes(conn, user_id)

        elif choice == "2":
            _add_recipe_flow(conn, user_id)

        elif choice == "3":
            _edit_recipe_flow(conn, user_id)

        elif choice == "4":
            _delete_recipe_flow(conn, user_id)

        elif choice == "5":
            _search_recipes_flow(conn, user_id)

        elif choice == "6":
            print("\n  👤 Benutzer wechseln...")
            return

        elif choice == "7":
            print("  👋 Bis bald!")
            return

        else:
            print("  ⚠️  Ungültige Option.")


def _show_my_recipes(conn, user_id):
    recipes = get_user_recipes(conn, user_id)
    if not recipes:
        print("\n  Du hast noch keine Rezepte gespeichert. 📝")
        return

    print(f"\n  Deine Rezepte ({len(recipes)} Stück):")
    print("-" * 70)
    for r in recipes:
        rid, title, _, _, category, created, _ = r
        print(f"    [{rid}] {title:<35} 📁 {category}")
    print("-" * 70)

    detail = input("\n  Detailansicht für Rezept [ID eingeben] oder 'z' zurücks: ").strip()
    if detail.lower() == "z":
        return
    try:
        rid = int(detail)
        recipe = get_recipe_by_id(conn, rid, user_id)
        if recipe:
            print_recipe(recipe)
        else:
            print("  ❌ Rezept nicht gefunden.")
    except ValueError:
        print("  ⚠️  Bitte eine gültige ID eingeben.")


def _add_recipe_flow(conn, user_id):
    print("\n" + "-" * 50)
    print("   🆕 NEUES REZEPT ERSTELLEN")
    print("-" * 50)

    title = input("  Titel des Rezepts: ").strip()
    if not title:
        print("  ❌ Titel darf nicht leer sein.")
        return

    categories = ["Frühstück", "Mittagessen", "Abendessen", "Dessert", "Snack",
                  "Getränk", "Suppe", "Salat", "Beilage", "Sonstiges"]
    print(f"\n  Kategorien: {', '.join(categories)}")
    category = input("  Kategorie (oder 'END' für Sonstiges): ").strip()
    if not category or category == "END":
        category = "Sonstiges"

    ingredients = get_multiline_input(
        "Zutaten eingeben (eine pro Zeile):", "Zutat"
    )
    instructions = get_multiline_input(
        "Anleitung eingeben (eine Zeile pro Schritt):", "Schritt"
    )

    if not title or not ingredients or not instructions:
        print("  ❌ Titel, Zutaten und Anleitung dürfen nicht leer sein.")
        return

    recipe_id = add_recipe(conn, user_id, title, ingredients, instructions, category)
    print(f"\n  ✅ Rezept '{title}' erfolgreich gespeichert! (ID: {recipe_id})")


def _edit_recipe_flow(conn, user_id):
    recipes = get_user_recipes(conn, user_id)
    if not recipes:
        print("\n  Du hast keine Rezepte zum Bearbeiten. 📝")
        return

    print("\n" + "-" * 50)
    print("   ✏️  REZEPT BEARBEITEN")
    print("-" * 50)
    print_recipe_list(recipes)

    choice = input("  Rezept-ID zum Bearbeiten: ").strip()
    try:
        recipe_id = int(choice)
    except ValueError:
        print("  ❌ Ungültige ID.")
        return

    recipe = get_recipe_by_id(conn, recipe_id, user_id)
    if not recipe:
        print("  ❌ Rezept nicht gefunden oder kein Zugriff.")
        return

    # Aktuelle Werte anzeigen
    _, old_title, old_ingredients, old_instructions, old_category, _, _ = recipe
    print(f"\n  Aktuelle Daten:")
    print(f"    Titel:     {old_title}")
    print(f"    Kategorie: {old_category}")
    print(f"    Zutaten:\n{old_ingredients}")
    print(f"    Anleitung:\n{old_instructions}")

    new_title = input("\n  Neuer Titel [Enter für unverändert]: ").strip() or old_title
    categories = ["Frühstück", "Mittagessen", "Abendessen", "Dessert", "Snack",
                  "Getränk", "Suppe", "Salat", "Beilage", "Sonstiges"]
    print(f"  Kategorien: {', '.join(categories)}")
    new_category = input(f"  Neue Kategorie [{old_category}]: ").strip() or old_category

    print("\n  Zutaten (Enter für unverändert):")
    new_ingredients = get_multiline_input("", "Zutat")
    new_ingredients = new_ingredients.strip() or old_ingredients

    print("\n  Anleitung (Enter für unverändert):")
    new_instructions = get_multiline_input("", "Schritt")
    new_instructions = new_instructions.strip() or old_instructions

    update_recipe(conn, recipe_id, user_id, new_title, new_ingredients,
                  new_instructions, new_category)
    print(f"\n  ✅ Rezept '{new_title}' wurde aktualisiert!")


def _delete_recipe_flow(conn, user_id):
    recipes = get_user_recipes(conn, user_id)
    if not recipes:
        print("\n  Du hast keine Rezepte zum Löschen. 📝")
        return

    print("\n" + "-" * 50)
    print("   🗑️  REZEPT LÖSCHEN")
    print("-" * 50)
    print_recipe_list(recipes)

    choice = input("  Rezept-ID zum Löschen: ").strip()
    try:
        recipe_id = int(choice)
    except ValueError:
        print("  ❌ Ungültige ID.")
        return

    recipe = get_recipe_by_id(conn, recipe_id, user_id)
    if not recipe:
        print("  ❌ Rezept nicht gefunden oder kein Zugriff.")
        return

    _, title, _, _, category, _, _ = recipe
    confirm = input(f"\n  Bist du sicher? '{title}' ({category}) unwiderruflich löschen? (j/N): ").strip().lower()
    if confirm == "j":
        delete_recipe(conn, recipe_id, user_id)
        print(f"  ✅ Rezept '{title}' wurde gelöscht.")
    else:
        print("  ❌ Abgebrochen.")


def _search_recipes_flow(conn, user_id):
    recipes = get_user_recipes(conn, user_id)
    if not recipes:3
    print("\n  Du hast keine Rezepte. 🔍")
    return

    print("\n" + "-" * 50)
    print("   🔍 REZEPTE SUCHE")
    print("-" * 50)

    query = input("  Suchbegriff (Titel oder Zutat): ").strip()
    if not query:
        # Alle Rezepte anzeigen
        print_recipe_list(recipes)
        return

    results = search_recipes(conn, user_id, query)
    if not results:
        print(f"\n  Keine Ergebnisse für '{query}'.")
        return

    print(f"\n  {len(results)} Ergebnis(se) für '{query}':")
    for r in results:
        print_recipe(r)


# ============================================================
#  HAUPTPROGRAMM
# ============================================================

def main():
    """Einstiegspunkt der Anwendung."""
    conn = init_db()

    try:
        while True:
            user_id = auth_menu(conn)
            if user_id is None:
                break
            recipe_menu(conn, user_id)
    except (KeyboardInterrupt, EOFError):
        print("\n\n  ⚠️  Programm wurde beendet.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()