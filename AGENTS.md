# MoodleKurse – gemeinsame Projektregeln

## Ziel
Dieses Repository dient der Erstellung handlungsorientierter Unterrichtsmaterialien fuer Moodle 4.5.

## Bildungsgänge
- FIAE
- FISI
- FIDP
- Fachkraft fuer Veranstaltungstechnik

## Verbindliche lokale Quellen
Die Verzeichnisse `_vorgaben/schuco` und `_vorgaben/rahmenlehrplaene` enthalten verbindliche lokale Vorgaben.
Sie haben Vorrang vor allgemeinem Modellwissen.

## SCHUCO / vollstaendige Handlung
Lernsituationen orientieren sich – entsprechend den lokalen Vorgaben – an:
1. Informieren
2. Planen
3. Entscheiden
4. Durchfuehren
5. Kontrollieren
6. Reflektieren

## Rollen
- Fachagenten: fachliche Richtigkeit und Lernfeldbezug.
- didaktik: Handlungssituation, Kompetenzen und didaktische Struktur.
- quiz: Assessment, Testfragen, Feedback und Moodle-XML.
- visual-designer: Darstellung und Moodle-taugliches HTML.
- reviewer: unabhaengige Qualitaetspruefung.
- moodle: technische Moodle-Umsetzung.
- orchestrator: Koordination des Gesamtprozesses.

## Moodle-Sicherheitsregel
Nur der Agent `moodle` darf Moodle-MCP-Werkzeuge verwenden.
Andere Agenten veraendern Moodle nicht.

## Loeschen
Automatisches Loeschen von Moodle-Aktivitaeten ist verboten.
`moodle_delete_module` soll nicht freigegeben werden.

## Identifikatoren
Kurs-ID, Abschnitts-ID und cmid werden niemals geraten.
Vor Aenderungen werden die aktuellen Moodle-Daten gelesen.

## Dateien
Jeder Unterrichtsauftrag erhaelt einen eigenen Ordner unter `courses/`.
Quelldateien anderer Agenten werden nicht stillschweigend ueberschrieben.

## Unsicherheit
Fehlende oder widerspruechliche Informationen werden dokumentiert.
Unsicherheiten duerfen nicht durch erfundene Fakten ersetzt werden.

## Deployment-Gate
Moodle-Publishing erfolgt erst nach:
1. Fach-/Didaktik-/Assessment-Erstellung,
2. Visual Design,
3. Reviewer-Status `APPROVED`,
4. ausdruecklicher Benutzerfreigabe.
