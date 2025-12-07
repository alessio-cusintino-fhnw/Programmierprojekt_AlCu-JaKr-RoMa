# Programmierprojekt_AlCu-JaKr-RoMa

# 1. Beschreibung und Ziele der Applikation
In unserer Applikation handelt es sich um eine Konsolenapplikation, welche dem User hilft, die persönlichen Finanzen im Überblick zu behalten.

Dieses Programm umfasst folgende Aufgabenbereiche und hilft bei folgenden Problemen:
- Erstellen, Bearbeiten und Löschen von Einnahmen und Ausgaben
- Festlegen von Sparzielen
- Import und Export von den Dateien
- Übersicht über Ausgaben und Einnahmen darstellen

Es richtet sich an Nutzende, welche ihre Finanzen einfach und übersichtlich darstellen möchten.

# 2. Aufrufen der Applikation
Für den Abruf der Applikation ist Python Version 3.10

# 3. Funktionen

## 3.1. def format_waehrung
Diese Funktion definiert den Schweizer Franken als Währung während des gesamten Programms und legt die Zahlenformate fest (1'234.00 CHF).

## 3.2. def eingabe_pruefung
In dieser Funktion werden die Eingaben jeweils validiert. Das gewünschte Ergebnis wird validiert, und Fehler werden angezeigt.

## 3.3. def brutto_zu_netto
Diese Funktion berechnet bei einer Eingabe des Bruttoeinkommens aus, wie viel das Nettoeinkommen schätzungsweise beträgt. Dabei werden übliche Lohnabzüge sowie Steuerannahmen getroffen und subtrahiert.

## 3.4. def finanzen_berechnen
Die eingegebenen Daten werden in der folgenden Funktion verglichen und validiert, z. B. ob ein Vermögensauf- oder -abbau stattfindet.

## 3.5. def registrierung_persoenliche_daten
Der User kann hier seine persönlichen Angaben wie Vorname, Name oder Alter angeben. Diese werden im weiteren Verlauf der Applikation verwendet.

## 3.6. def registrierung_finanzielle_daten
Diese Funktion fragt den User ab, wie hoch aktuelle Vermögens- und Salärverhältnisse sind und erfasst zudem auch weitere Ausgaben oder Kosten.

## 3.7. def daten_laden
Die zuvor eingegebenen und in der Textdatei gespeicherten Daten werden geladen und angezeigt.

## 3.8. def daten_speichern
Die hier vorliegende Funktion speichert sämtliche vom User eingegebene Daten in der Textdatei für die spätere Verwendung.

## 3.9. def zukunftsszenarien_berechnen
Für den User lassen sich hier zukünftige Werte berechnen wie zum Beispiel Sparziele (Ferien, Auto ...) oder einen Vermögensaufbau.

## 3.10. def daten_anpassen
Der User kann hier sämtliche Eingaben korrigieren (Reserven, Einkommen, Ausgaben).

## 3.11. def bearbeite_kosten
Hier lassen sich Kosten und Ausgaben ändern.

## 3.12. def ausgabe_basis_ergebnis
Hier wird das monatliche Ergebnis angezeigt.

## 3.13. def haupt_menue
Dieses Menü ist das zentrale Steuermenü, welches für die Navigation im Programm notwendig ist. Es führt den User durch die einzelnen Funktionen (erstellen, bearbeiten, löschen, anzeigen). 

## 3.14. def daten_loeschen
Möchte der User das Programm nicht mehr löschen oder neu anfangen, kann er das Dokument vollständig löschen.

## 3.15. def start_programm
Diese Funktion startet die Hauptschleife und somit das gesamte Programm.

# 4. Beispiele und Nutzung
User:innen können folgende Szenarien (nicht abschliessend) abdecken:
- Verwalten von Einnahmen (Lohn, weitere ...)
- Verwalten von fixen Ausgaben (Miete, Verkehrsmittel, Lebensmittel)
- Verwalten von variablen Kosten (z. B. Reisen, einmalige Käufe etc.)
- Darstellung von Sparzielen oder Projektionen

# 5. Rechte und Mitwirkung
Das Programm wurde im Rahmen des Moduls "Grundlagen Programmierung" von Jana Kräuchi, Rouven Mallach und Alessio Cusintino erstellt. Alle Rechte sowie Fehler sind daher vorzubehalten.
