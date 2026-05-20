import essen
import wine
import re

def skaliere_zutaten(zutaten_liste, original_menge, ziel_menge):
    """
    Extrahiert Zahlen aus den Zutaten-Strings und skaliert sie.
    """
    faktor = ziel_menge / original_menge
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
            # Falls keine Zahl gefunden wurde (z.B. "Salz & Pfeffer"), einfach übernehmen
            skalierte_liste.append(zutat)
            
    return skalierte_liste

def berechne_essen_rezept(essen_id, ziel_personen):
    rezept = essen.get_essen(essen_id)
    if not rezept:
        print("Essen-Rezept nicht gefunden.")
        return

    print(f"\n--- Skaliertes Rezept: {rezept['name']} ---")
    print(f"Basis: {rezept['personenanzahl']} Personen -> Ziel: {ziel_personen} Personen")
    
    neue_zutaten = skaliere_zutaten(rezept['zutaten'], rezept['personenanzahl'], ziel_personen)
    
    for zutat in neue_zutaten:
        print(f"• {zutat}")

def berechne_wein_rezept(wine_id, ziel_liter):
    rezept = wine.get_wine(wine_id)
    if not rezept:
        print("Wein-Rezept nicht gefunden.")
        return

    # Wir nehmen an, dass das Basis-Rezept (Holunder) für 5 Liter ausgelegt ist 
    # (laut deinem String "Wasser bis 5l ansatz erreicht")
    basis_liter = 5.0 
    
    print(f"\n--- Skalierter Wein: {rezept['name']} ---")
    print(f"Basis: {basis_liter}L -> Ziel: {ziel_liter}L")
    
    neue_zutaten = skaliere_zutaten(rezept['ingredients'], basis_liter, ziel_liter)
    
    for zutat in neue_zutaten:
        print(f"• {zutat}")

if __name__ == "__main__":
    # Initialisiere DBs falls noch nicht geschehen
    essen.init_db()
    wine.init_db()

    print("Willkommen beim Rezept-Rechner!")
    
    # Beispiel-Abfrage für Essen
    essen_id = 1 # Kaiserliches Kräuter-Kaninchen
    personen = float(input("Für wie viele Personen soll gekocht werden? "))
    berechne_essen_rezept(essen_id, personen)

    print("\n" + "="*30)

    # Beispiel-Abfrage für Wein
    wine_id = 1 # Holunder Johannisbeer Wein
    liter = float(input("Wie viel Liter Wein sollen angesetzt werden? "))
    berechne_wein_rezept(wine_id, liter)