import os #für das Hochladen späterer Dateien
import json #Damit kann man die detaillierten Listen der Fix- und variablen Kosten in die Textdatei exportieren und später wieder in ein funktionsfähiges Python-Dictionary umwandeln.

# Definiert die Standard-Fixkosten-Kategorien, die bei der Registrierung abgefragt werden.
FIXKOSTEN = ["Wohnkosten (Miete/Hypothekarzins)", "Krankenkasse/Versicherungen", "Öffentlicher Verkehr/Auto", "Abos (Internet/Handy)"]
# Datei-Endung für die Speicherung
DATEI_ENDUNG = ".txt"

def format_waehrung(betrag):
    """Formatiert einen Betrag in das Schweizer Währungsformat (X'XXX.XX CHF)."""
    # Verwendet die Tausendertrennzeichen-Logik des Originals, um CHF-Konventionen zu folgen.
    return f"{betrag:,.2f} CHF".replace(",", "X").replace(".", ",").replace("X", ".")

def eingabe_pruefung(anweisung, datentyp=float, positiv_erforderlich=True, min_wert=None, max_wert=None):
    """Prüft, ob die Eingabe dem korrekten Datentyp entspricht und im gewünschten Bereich liegt."""
    while True:
        try:
            eingabe = input(anweisung).strip().replace(',', '.') # Ersetzt Komma durch Punkt für Python-Float-Parsing
            
            if not eingabe:
                raise ValueError("Eingabe darf nicht leer sein.")
            
            wert = datentyp(eingabe)

            if positiv_erforderlich and wert < 0:
                print("Fehler: Der Wert muss positiv sein.")
                continue

            if min_wert is not None and wert < min_wert:
                print(f"Fehler: Der Wert muss mindestens {min_wert} sein.")
                continue

            if max_wert is not None and wert > max_wert:
                print(f"Fehler: Der Wert darf maximal {max_wert} sein.")
                continue

            return wert

        except ValueError:
            typ_name = "Zahl" if datentyp in (float, int) else "Text"
            print(f"Ungültige Eingabe. Bitte geben Sie eine gültige {typ_name} ein.")
        except Exception as e:
            print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")

def brutto_zu_netto(brutto_einkommen_monatlich, alter):
    """Schätzt das Nettoeinkommen in der Schweiz (vereinfacht: AHV, BVG, Steuern)."""
    
    # 1. AHV/IV/EO/ALV: Konstante 6.2%
    abzug_sozial = brutto_einkommen_monatlich * 0.062
    
    # 2. BVG (Pensionskasse) - Altersabhängig
    if alter < 25: bvg_prozent = 0.0
    elif alter <= 34: bvg_prozent = 0.04
    elif alter <= 44: bvg_prozent = 0.07
    else: bvg_prozent = 0.10
        
    abzug_bvg = brutto_einkommen_monatlich * bvg_prozent

    # 3. Steuern - Einkommensabhängig (Pauschal)
    brutto_einkommen_jahr = brutto_einkommen_monatlich * 12
    if brutto_einkommen_jahr <= 60000: steuer_prozent = 0.05 
    elif brutto_einkommen_jahr <= 100000: steuer_prozent = 0.10 
    else: steuer_prozent = 0.15 

    abzug_steuern = brutto_einkommen_monatlich * steuer_prozent

    gesamtabzug = abzug_sozial + abzug_bvg + abzug_steuern
    netto_einkommen = brutto_einkommen_monatlich - gesamtabzug
    
    gesamtabzug_prozent = 0.062 + bvg_prozent + steuer_prozent
    
    return netto_einkommen, gesamtabzug_prozent

def finanzen_berechnen(benutzerdaten):
    """Berechnet die monatliche Sparquote oder den Vermögensverzehr und aktualisiert das Dictionary."""
    netto_einkommen = benutzerdaten.get("Einkommen Netto", 0.0)
    gesamte_kosten = benutzerdaten.get("Monatliche Gesamtkosten", 0.0)

    ergebnis = netto_einkommen - gesamte_kosten
    benutzerdaten["Monatliches Ergebnis"] = ergebnis

    if ergebnis > 0:
        benutzerdaten["Ergebnis Art"] = "Monatliche Sparquote"
    elif ergebnis < 0:
        benutzerdaten["Ergebnis Art"] = "Monatlicher Vermögensverzehr"
    else:   
        benutzerdaten["Ergebnis Art"] = "Ausgeglichen" 
    
    return benutzerdaten

# --- REGISTRIERUNG / HAUPT-ERFASSUNG ---

def registrierung_persoenliche_daten(benutzerdaten):
    """Erfasst Vorname, Nachname und Alter."""
    print("\n--- Schritt 1: Persönliche Daten erfassen ---")
    benutzerdaten["Vorname"] = input("Vorname: ").strip()
    benutzerdaten["Name"] = input("Name: ").strip() # Korrigiert von 'Nachname' zu 'Name' (konsistent mit Speichern)
    benutzerdaten["Alter"] = eingabe_pruefung("Alter (18-100): ", datentyp=int, min_wert=18, max_wert=100)
    print("Persönliche Daten erfolgreich erfasst.")
    return benutzerdaten
        

def registrierung_finanzielle_daten(benutzerdaten, vorgegebene_fixkosten): 
    """Erfasst finanzielle Daten, berechnet Netto-Einkommen und Kosten."""
    print("\n--- Schritt 2: Finanzielle Angaben erfassen ---")

    # 1. Vermögen und Reserve
    # BUG FIX: Hier wurde der Prompt-String zugewiesen, nicht das Ergebnis der Eingabeprüfung.
    benutzerdaten["Aktuelles Gesamtvermögen"] = eingabe_pruefung("Aktuelles Gesamtvermögen in CHF: ")
    benutzerdaten["Finanzielle Reserve"] = eingabe_pruefung("Finanzielle Reserve (Betrag für Notfälle) in CHF: ")

    # 2. Einkommen
    while True:
        einkommen_wert = eingabe_pruefung("Monatliches Einkommen in CHF: ")
        typ = input("Handelt es sich hierbei um ein 'brutto'- oder 'netto'-Einkommen? ").strip().lower()

        if typ == 'brutto':
            alter = benutzerdaten.get("Alter", 30)
            netto_einkommen, abzug_prozent = brutto_zu_netto(einkommen_wert, alter)

            benutzerdaten["Einkommen Brutto"] = einkommen_wert
            benutzerdaten["Einkommen Netto"] = netto_einkommen
            print(f"Totaler Abzug: {abzug_prozent*100:.2f}%")
            print(f"Monatliches Nettoeinkommen: {format_waehrung(netto_einkommen)}")
            break
        elif typ == 'netto':
            benutzerdaten["Einkommen Netto"] = einkommen_wert
            benutzerdaten["Einkommen Brutto"] = "nicht anwendbar" 
            print(f'--> Monatliches Nettoeinkommen: {format_waehrung(einkommen_wert)}')
            break
        else:
            print("Ungültige Eingabe. Bitte geben Sie 'brutto' oder 'netto' ein.")

    # 3. Fixkosten erfassen
    print("\n--- Schritt 3: Fixkosten erfassen ---")
    benutzerdaten["Fixkosten"] = {}
    
    for posten in vorgegebene_fixkosten:
        wert = eingabe_pruefung(f'Monatliche Fixkosten für {posten} in CHF: ')
        benutzerdaten["Fixkosten"][posten] = wert
            
    # 4. Variable Kosten (individuelle Posten)
    print("\n--- Schritt 4: Variable Kosten erfassen ---")
    benutzerdaten["Variable Kosten"] = {}
    while True:
        posten_name = input("Weiteren variablen Kostenpunkt benennen (z.B. 'Lebensmittel') oder 'ende' zum Abschliessen: ").strip()
        if posten_name.lower() == 'ende':
            break

        wert = eingabe_pruefung(f"Monatliche Kosten für {posten_name} in CHF: ")
        benutzerdaten["Variable Kosten"][posten_name] = wert

    # Gesamtkosten berechnen
    fixkosten_gesamt = sum(benutzerdaten["Fixkosten"].values())
    variable_kosten_gesamt = sum(benutzerdaten["Variable Kosten"].values())
    benutzerdaten["Monatliche Gesamtkosten"] = fixkosten_gesamt + variable_kosten_gesamt

    # Berechnung des Ergebnisses und die Ausgabe
    benutzerdaten = finanzen_berechnen(benutzerdaten)
    ausgabe_basis_ergebnis(benutzerdaten)

    return benutzerdaten

# --- SPEICHERUNG / LADEN ---

def daten_laden(benutzerdaten):
    """Lädt die Daten aus einer Textdatei und stellt sie wieder her."""
    print("\n--- Daten aus Textdatei laden ---")
    dateiname = input("Name der zu ladenden Datei (z.B. 'Meier_Hans.txt'): ").strip()
    
    if not os.path.exists(dateiname):
        print(f"Fehler: Datei '{dateiname}' wurde nicht gefunden.")
        return None

    try:
        with open(dateiname, 'r') as file:
            geladene_daten = {}
            for line in file:
                line = line.strip()
                if not line or line.startswith("---"):
                    continue
                
                if ":" in line:
                    key, value_str = line.split(":", 1)
                    key = key.strip()
                    value_str = value_str.strip()
                    
                    # Logik: Prüfen, ob es sich um ein JSON-Dictionary (Kostenliste) handelt
                    if value_str.startswith("{") and value_str.endswith("}"):
                        value = json.loads(value_str)
                    # Logik: Prüfen, ob es sich um eine Zahl (int/float) handelt, die RAW gespeichert wurde
                    elif key in ["Aktuelles Gesamtvermögen", "Finanzielle Reserve", "Einkommen Netto", "Einkommen Brutto", "Monatliche Gesamtkosten", "Monatliches Ergebnis", "Alter"]:
                        try:
                            # Wir versuchen, den Wert direkt als Float zu parsen, da daten_speichern ihn RAW speichert.
                            value = float(value_str)
                            if key == "Alter": value = int(value)
                        except ValueError:
                            value = value_str # Fallback für "nicht anwendbar" oder Fehler
                    # Logik: Standardmäßig als String behandeln
                    else:
                        value = value_str
                        
                    geladene_daten[key] = value

            benutzerdaten.update(geladene_daten)
            
            # Wichtig: Nach dem Laden muss das Ergebnis neu berechnet werden, um 'Ergebnis Art' zu setzen.
            if "Einkommen Netto" in benutzerdaten and "Monatliche Gesamtkosten" in benutzerdaten:
                benutzerdaten = finanzen_berechnen(benutzerdaten)

            print(f"Daten für {benutzerdaten.get('Vorname', '')} {benutzerdaten.get('Name', '')} erfolgreich geladen.")
            return benutzerdaten

    except Exception as e:
        print(f"Fehler beim Lesen der Datei: {e}")
        return None


# Vorstellung durch Jana

def daten_speichern(benutzerdaten):
    """Speichert alle RAW-Daten (Zahlen als Zahlen, Listen als JSON-Strings) in einer Textdatei."""
    if "Name" not in benutzerdaten or "Vorname" not in benutzerdaten:
        print("Fehler: Name und Vorname fehlen. Speichern nicht möglich.")
        return
        
    dateiname = f'{benutzerdaten["Name"]}_{benutzerdaten["Vorname"]}{DATEI_ENDUNG}'
    
    daten_zum_speichern = benutzerdaten.copy()

    # Kosten-Dictionaries als JSON-String speichern
    if "Fixkosten" in daten_zum_speichern:
        daten_zum_speichern["Fixkosten"] = json.dumps(daten_zum_speichern["Fixkosten"])
    if "Variable Kosten" in daten_zum_speichern:
        # Key korrigiert und vereinheitlicht (Original hatte Inkonsistenzen)
        daten_zum_speichern["Variable Kosten"] = json.dumps(daten_zum_speichern["Variable Kosten"])
    
    try:
        with open(dateiname, 'w') as file:
            file.write("--- Persönliche Daten ---\n")
            
            # Persönliche Daten (explizit zuerst)
            for key in ["Vorname", "Name", "Alter"]:
                if key in daten_zum_speichern:
                    file.write(f"{key}: {daten_zum_speichern.pop(key)}\n")

            file.write("\n--- Finanzielle Daten und Ergebnis ---\n")
            # Alle übrigen Daten (Zahlen werden RAW gespeichert, um das Laden zu vereinfachen)
            for key, value in daten_zum_speichern.items():
                file.write(f"{key}: {value}\n")

        print(f"\nDaten erfolgreich gespeichert in: *{dateiname}*")
    
    except Exception as e:
        print(f"\nFehler beim Speichern der Datei: {e}")

# --- ANPASSEN / SONDERSZENARIEN ---

def zukunftsszenarien_berechnen(benutzerdaten):
    """Berechnet die Szenarien C.1, C.2 und C.3."""
    
    # BUG FIX: Dictionary-Zugriff war fehlerhaft (benutzerdaten(...) statt benutzerdaten.get(...))
    ergebnis = benutzerdaten.get("Monatliches Ergebnis", 0.0)
    aktuelles_vermoegen = benutzerdaten.get("Aktuelles Gesamtvermögen", 0.0)
    reserve = benutzerdaten.get("Finanzielle Reserve", 0.0)
    
    print("\n--- ZUKUNFTSSZENARIEN BERECHNEN ---")
    
    if ergebnis > 0:
        # C.1/C.2: Sparquote vorhanden
        print(f"Ihr Überschuss (Sparquote): {format_waehrung(ergebnis)}")
        
        wahl = input("Haben Sie ein spezifisches Sparziel (z.B. Auto)? (ja/nein): ").lower().strip()
        
        if wahl == 'ja':
            # C.1: Spezifisches Sparziel
            ziel_name = input("Name des Sparziels (z.B. 'Neues Auto'): ").strip()
            ziel_kosten = eingabe_pruefung(f"Geschätzte Kosten für '{ziel_name}' in CHF: ")
            
            effektives_startkapital = aktuelles_vermoegen - reserve
            zu_sparender_betrag = ziel_kosten - effektives_startkapital
            
            print("-" * 50)
            if zu_sparender_betrag <= 0:
                print(f"Gute Nachrichten: Sie können sich '{ziel_name}' (Kosten: {format_waehrung(ziel_kosten)}) sofort leisten,")
                print(f"da Ihr freies Vermögen ({format_waehrung(effektives_startkapital)}) ausreicht.")
                print(f"Restliches freies Vermögen danach: {format_waehrung(abs(zu_sparender_betrag))}")
            else:
                monate_benoetigt = zu_sparender_betrag / ergebnis
                jahre = int(monate_benoetigt // 12)
                monate = round(monate_benoetigt % 12) 
                
                print(f"Sparziel: '{ziel_name}' (Kosten: {format_waehrung(ziel_kosten)})")
                print(f"Sie müssen noch {format_waehrung(zu_sparender_betrag)} ansparen.")
                print(f"Benötigte Zeit, um das Sparziel zu erreichen: ca. {jahre} Jahre und {monate} Monate.")
            print("-" * 50)
            
        else:
            # C.2: Allgemeiner Vermögensaufbau
            jahre_eingabe = eingabe_pruefung("Für wie viele Jahre soll der Vermögensaufbau berechnet werden?: ", datentyp=int, min_wert=1)
            
            gespart_in_jahren = ergebnis * jahre_eingabe * 12
            gesamtvermoegen_prognose = aktuelles_vermoegen + gespart_in_jahren
            
            print("-" * 50)
            print(f"Prognose (Vermögensaufbau in {jahre_eingabe} Jahren):")
            print(f"Angesparter Betrag durch Sparquote: {format_waehrung(gespart_in_jahren)}")
            print(f"Geschätztes Gesamtvermögen nach {jahre_eingabe} Jahren: {format_waehrung(gesamtvermoegen_prognose)}")
            print("-" * 50)
            
    elif ergebnis < 0:
        # C.3: Vermögensverzehr besteht
        verzehr_monatlich = abs(ergebnis)
        vermoegen_fuer_verzehr = aktuelles_vermoegen
        
        if vermoegen_fuer_verzehr <= 0:
            reichweite_monate = 0
        else:
            reichweite_monate = vermoegen_fuer_verzehr / verzehr_monatlich

        jahre = int(reichweite_monate // 12)
        monate = round(reichweite_monate % 12)

        print(f"Ihr monatlicher Vermögensverzehr beträgt: {format_waehrung(verzehr_monatlich)}")
        print("-" * 50)
        print("Was passiert, wenn das Einkommen plötzlich wegfällt?")
        print(f"Ihr bestehendes Vermögen ({format_waehrung(vermoegen_fuer_verzehr)}) reicht, um Ihre Ausgabesituation")
        print(f"noch für ca. {jahre} Jahre und {monate} Monate abzudecken.")
        print("-" * 50)
    
    else:
        print("Ihr Budget ist ausgeglichen. Keine Spar-/Verzehrs-Szenarien berechenbar.")

def daten_anpassen(benutzerdaten, vorgegebene_fixkosten):
    """Ermöglicht die Anpassung der finanziellen Daten."""
    
    if not benutzerdaten:
        print("Keine Daten geladen. Bitte registrieren Sie sich zuerst oder laden Sie eine Datei.")
        return benutzerdaten

    while True:
        print("\n--- DATEN ANPASSEN ---")
        print("1. Aktuelles Gesamtvermögen anpassen")
        print("2. Finanzielle Reserve anpassen")
        print("3. Monatliches Einkommen anpassen (Brutto/Netto neu eingeben)")
        print("4. Fixkosten anpassen/ergänzen/löschen")
        print("5. Variable Kosten anpassen/ergänzen/löschen")
        print("6. Zurück zum Hauptmenü")
        
        wahl = input("Ihre Wahl (1-6): ").strip()

        if wahl == '1':
            benutzerdaten["Aktuelles Gesamtvermögen"] = eingabe_pruefung("Neues Gesamtvermögen in CHF: ")
        elif wahl == '2':
            benutzerdaten["Finanzielle Reserve"] = eingabe_pruefung("Neue finanzielle Reserve in CHF: ")
        elif wahl == '3':
            # BUG FIX: Der Aufruf musste das zweite Argument (vorgegebene_fixkosten) enthalten.
            registrierung_finanzielle_daten(benutzerdaten, vorgegebene_fixkosten)
        elif wahl == '4':
            bearbeite_kosten(benutzerdaten, "Fixkosten")
        elif wahl == '5':
            bearbeite_kosten(benutzerdaten, "Variable Kosten")
        elif wahl == '6':
            # Nach jeder Änderung wird das Ergebnis neu berechnet
            benutzerdaten = finanzen_berechnen(benutzerdaten)
            ausgabe_basis_ergebnis(benutzerdaten)
            return benutzerdaten
        else:
            print("Ungültige Wahl.")
            continue
            
        # Nach jeder Änderung die Gesamtkosten und das Ergebnis neu berechnen
        fixkosten_gesamt = sum(benutzerdaten.get("Fixkosten", {}).values())
        variable_kosten_gesamt = sum(benutzerdaten.get("Variable Kosten", {}).values())
        
        benutzerdaten["Monatliche Gesamtkosten"] = fixkosten_gesamt + variable_kosten_gesamt
        benutzerdaten = finanzen_berechnen(benutzerdaten)
        ausgabe_basis_ergebnis(benutzerdaten) # Zeigt das aktuelle Ergebnis nach der Änderung

def bearbeite_kosten(benutzerdaten, kosten_art):
    """Hilfsfunktion zum Bearbeiten von Fix- oder variablen Kosten."""
    kosten_dict = benutzerdaten.get(kosten_art, {})
    
    if kosten_dict == {}:
        benutzerdaten[kosten_art] = {}
        kosten_dict = benutzerdaten[kosten_art]

    while True:
        print(f"\n--- {kosten_art} bearbeiten ---")
        if not kosten_dict:
            print("Aktuell sind keine Kostenpunkte erfasst.")
        else:
            print("Aktuelle Kostenpunkte:")
            for idx, (posten, wert) in enumerate(kosten_dict.items()):
                print(f"{idx+1}. {posten}: {format_waehrung(wert)}")
        
        print("\nOptionen:")
        print("A. Neuen Posten hinzufügen")
        print("B. Bestehenden Posten ändern")
        print("C. Bestehenden Posten löschen")
        print("D. Zurück zur Datenanpassung")
        
        wahl = input("Ihre Wahl (A/B/C/D): ").upper().strip()
        
        if wahl == 'A':
            posten_name = input("Name des neuen Postens: ").strip()
            if posten_name:
                wert = eingabe_pruefung(f"Monatliche Kosten für {posten_name} in CHF: ")
                kosten_dict[posten_name] = wert
                print(f"Posten '{posten_name}' hinzugefügt.")
        
        elif wahl == 'B':
            if not kosten_dict:
                print("Keine Posten zum Ändern.")
                continue
            posten_zu_aendern = input("Name des Postens, den Sie ändern möchten: ").strip()
            if posten_zu_aendern in kosten_dict:
                neuer_wert = eingabe_pruefung(f"Neuer Wert für {posten_zu_aendern} in CHF: ")
                kosten_dict[posten_zu_aendern] = neuer_wert
                print(f"Posten '{posten_zu_aendern}' aktualisiert.")
            else:
                print("Posten nicht gefunden.")
                
        elif wahl == 'C':
            if not kosten_dict:
                print("Keine Posten zum Löschen.")
                continue
            posten_zu_loeschen = input("Name des Postens, den Sie löschen möchten: ").strip()
            if posten_zu_loeschen in kosten_dict:
                del kosten_dict[posten_zu_loeschen]
                print(f"Posten '{posten_zu_loeschen}' gelöscht.")
            else:
                print("Posten nicht gefunden.")
                
        elif wahl == 'D':
            benutzerdaten[kosten_art] = kosten_dict 
            return
            
        else:
            print("Ungültige Wahl.")

# Vorstellung durch Rouven 

# --- AUSGABE-FUNKTIONEN ---

def ausgabe_basis_ergebnis(benutzerdaten):
    """Zeigt das aktuelle monatliche Budgetergebnis an."""
    ergebnis = benutzerdaten.get("Monatliches Ergebnis", 0.0)
    netto = benutzerdaten.get("Einkommen Netto", 0.0)
    kosten = benutzerdaten.get("Monatliche Gesamtkosten", 0.0)
    ergebnis_art = benutzerdaten.get("Ergebnis Art")

    print("\n"+"="*60)
    print("AKTUELLES BUDGET-ERGEBNIS")
    print("="*60)
    print(f"Monatliches Nettoeinkommen: {format_waehrung(netto)}")
    print(f"Monatliche Gesamtkosten: {format_waehrung(kosten)}")
    print("-" * 60)

    if ergebnis > 0:
        print(f"{ergebnis_art}: {format_waehrung(ergebnis)}")
    elif ergebnis < 0:
        print(f"{ergebnis_art}: {format_waehrung(abs(ergebnis))}")
    else:
        print(ergebnis_art)
    print("="*60)

def haupt_menue(benutzerdaten, vorgegebene_fixkosten):
    """Menü für registrierte/geladene Benutzer."""
    
    while True:
        print(f"\nWillkommen zurück, {benutzerdaten.get('Vorname', 'User')}! (Hauptmenü)")
        print("1. Aktuelles Budget-Ergebnis anzeigen")
        print("2. Finanzielle Daten anpassen")
        print("3. Zukunftsszenarien berechnen (Sparen/Verzehr)")
        print("4. Änderungen speichern (Textdatei exportieren)")
        print("5. Account löschen und abmelden")
        print("6. Abmelden (Zurück zum Start)")
        
        wahl = input("Ihre Wahl (1-6): ").strip()
        
        if wahl == '1':
            ausgabe_basis_ergebnis(benutzerdaten)
        elif wahl == '2':
            # BUG FIX: Muss die fixen Kosten für den Unter-Flow mitgeben
            benutzerdaten = daten_anpassen(benutzerdaten, vorgegebene_fixkosten)
        elif wahl == '3':
            zukunftsszenarien_berechnen(benutzerdaten)
        elif wahl == '4':
            daten_speichern(benutzerdaten)
        elif wahl == '5':
            if daten_loeschen(benutzerdaten):
                return None
        elif wahl == '6':
            print("Abgemeldet. Zurück zum Startbildschirm.")
            start_programm()    
        else:
            print("Ungültige Wahl.")

def daten_loeschen(benutzerdaten):
    """Löscht die gespeicherte Textdatei und den aktuellen Account."""
    if "Name" not in benutzerdaten or "Vorname" not in benutzerdaten:
        print("Kein Account geladen, es gibt nichts zu löschen.")
        return False
        
    dateiname = f'{benutzerdaten["Name"]}_{benutzerdaten["Vorname"]}{DATEI_ENDUNG}'
    
    bestaetigung = input(f"Sind Sie sicher, dass Sie Ihren Account und die Datei '{dateiname}' löschen möchten? (ja/nein): ").lower().strip()
    
    if bestaetigung == 'ja':
        try:
            if os.path.exists(dateiname):
                os.remove(dateiname)
                print(f"Account und Datei '{dateiname}' erfolgreich gelöscht.")
                return True
            else:
                print(f"Warnung: Die Datei '{dateiname}' existiert nicht (mehr) auf dem System.")
                return True
        except Exception as e:
            print(f"Fehler beim Löschen der Datei: {e}")
            return False
    else:
        print("Löschvorgang abgebrochen.")
        return False


# --- PROGRAMM START (HAUPT-LOOP) ---

def start_programm():
    """Startet das Programm und die Hauptschleife."""
    
    benutzerdaten = None
    vorgegebene_fixkosten = FIXKOSTEN # Nutzt die vordefinierte Konstante
    
    print("\n" + "="*60)
    print("WILKOMMEN ZUM BUDGET-PLANER")
    print("="*60)

    while True:
        
        if benutzerdaten:
            # Wenn Daten geladen sind, direkt ins Hauptmenü
            benutzerdaten = haupt_menue(benutzerdaten, vorgegebene_fixkosten)
            continue
        
        # Startbildschirm (wenn keine Daten geladen)
        print("\nHauptmenü:")
        print("1. Neu registrieren und Daten erfassen")
        print("2. Bestehende Textdatei hochladen/einloggen")
        print("3. Programm beenden")

        wahl = input("Ihre Wahl (1/2/3): ").strip()

        if wahl == '1':
            # Szenario Registrierung
            benutzerdaten = {}
            benutzerdaten = registrierung_persoenliche_daten(benutzerdaten)
            benutzerdaten = registrierung_finanzielle_daten(benutzerdaten, vorgegebene_fixkosten)
            daten_speichern(benutzerdaten)
            
        elif wahl == '2':
            # Szenario Login (Dateiupload)
            benutzerdaten = {}
            geladene_daten = daten_laden(benutzerdaten)
            if geladene_daten:
                benutzerdaten = geladene_daten
                # finanzen_berechnen wird bereits in daten_laden aufgerufen, aber wir rufen es zur Sicherheit erneut auf.
                benutzerdaten = finanzen_berechnen(benutzerdaten)
                ausgabe_basis_ergebnis(benutzerdaten)
            else:
                benutzerdaten = None
                
        elif wahl == '3':
            print("Programm wird beendet. Auf Wiedersehen!")
            break
        else:
            print("Ungültige Wahl. Bitte geben Sie 1, 2 oder 3 ein.")

if __name__ == "__main__":
    start_programm()

# Vorstellung durch Alessio