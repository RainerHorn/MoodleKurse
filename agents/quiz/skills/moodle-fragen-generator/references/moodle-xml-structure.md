# Moodle-XML: Struktur und Importableitung

Rangfolge: Projekt-`AGENTS.md` → `agents/quiz/SOUL.md` → `../SKILL.md` →
diese Referenz. Bei XML-Strukturfragen lesen; typspezifische XML-Dateien in
`../templates/` verwenden. Keine zusätzliche Pflicht zur HTML-Vorschau.

## Projektkonventionen und Moodle-Format

Ein Kategorieblock je Autoren-Quiz und Tags für Bildungsgang/Lernfeld/Thema sind
Projektkonventionen. Moodle selbst unterstützt auch andere Kategorieaufteilungen.
Die Zielkategorie hängt vom tatsächlichen Importweg ab; keine Kategorie-IDs raten.
UTF-8, Wurzel, Name und CDATA erläutert die
[Moodle-4.5-Formatdokumentation](https://docs.moodle.org/405/en/Moodle_XML_format).

Ein minimales Strukturbeispiel (Inhalt und Bewertung durch Auftrag ersetzen):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<quiz>
  <question type="category">
    <category><text>$course$/top/FISI/LF03/Beispielquiz</text></category>
  </question>
  <question type="multichoice">
    <name><text>Beispielfrage</text></name>
    <questiontext format="html"><text><![CDATA[<p>Fragetext</p>]]></text></questiontext>
    <defaultgrade>1</defaultgrade>
    <single>true</single>
    <shuffleanswers>true</shuffleanswers>
    <answer fraction="100" format="html">
      <text><![CDATA[<p>Richtige Antwort</p>]]></text>
      <feedback format="html"><text><![CDATA[<p>Begründung</p>]]></text></feedback>
    </answer>
    <answer fraction="0" format="html">
      <text><![CDATA[<p>Plausibler Distraktor</p>]]></text>
      <feedback format="html"><text><![CDATA[<p>Korrekturhinweis</p>]]></text></feedback>
    </answer>
    <tags>
      <tag><text>FISI</text></tag>
      <tag><text>LF03</text></tag>
      <tag><text>Beispielthema</text></tag>
    </tags>
  </question>
</quiz>
```

`<!-- question: q1 -->` ist ein optionaler Kommentar und kein Pflichtnachweis.
Fragen durch `<question>`-Elemente zählen, Kategorieelemente separat behandeln.
Der Tagname lautet wörtlich `name`, nicht `n` und nicht `na&#x6D;e`.
Titeltexte dürfen UTF-8 enthalten; XML-Sonderzeichen außerhalb CDATA escapen.

## Autorenfassung und Transportfassung

1. Aktuelle Variante aus Auftrag und Status lesen. Für MBZ die kategorisierte
   Autorenfassung als Quelle für die Kursfragensammlung vorsehen; Kategorie und Tags
   übergeben. Eine frühere MCP-Transportfassung nicht zur MBZ-Vorgabe erklären.
2. Nur wenn der bestätigte MCP-Importweg eine feste Zielkategorie ohne Kategorieblock
   verlangt, auf ausdrücklichen Auftrag eine separate geschützte Transportfassung
   ableiten. Die Autorenfassung mit Kategorie unverändert erhalten.
3. Die relevante Komponente `xml-transport` aus `platform/components.json` wählen
   und ihren Hash prüfen. Bei passendem vorhandenem Nachweis das gemeinsame Werkzeug
   `scripts/xml_transport.py` nutzen statt einen kursbezogenen Entferner neu zu bauen.
   Die Erzeugung erfolgt mit `--derive`, die Quellenbindung optional mit
   `--source-sha256`; das Werkzeug überschreibt keine vorhandene Zieldatei.
4. Ausschließliche Kategorieentnahme durch Gesamtbytevergleich, Fragebaumvergleich
   und SHA-256/Bytezahl belegen; IDs, Reihenfolge, Typen, Punkte, Antworten und Feedback
   müssen erhalten bleiben. Für unveränderten Inhalt keine vollständige fachliche
   Neufreigabe oder Plattform-Testserie verlangen.
5. Beim Variantenwechsel nur betroffene Technik-/Übergabetexte ändern und testen.
   Frühere Ableitungen und technische Generator-Alttexte als historisch kennzeichnen;
   alte Generatoren nicht unbesehen ausführen, wenn sie aktuelle Dokumentation
   überschreiben würden. Fach-/Quiz-Bytes bleiben bei reinem Technikwechsel erhalten.

Eine lokale Prüfung beweist keine Live-Import- oder MBZ-Baufähigkeit. MCP-Import und
aktueller Readback gehören zu `moodle-mcp`; MBZ-Import/Bau, Kursplan, Schutzparameter
und Probewiederherstellung zu `moodle-mbz`. Offene Bau-/Zielentscheidungen ausdrücklich
nennen, statt frühere Kurs- oder Kategorie-IDs auf eine andere Variante zu übertragen.

## Quellenneubindung ohne Quizinhaltsänderung

Gilt nur für Bestandskurse, die bereits ein Quiz-Manifest oder hashgebundene
Altnachweise besitzen. Neue Kurse legen kein eigenes Quiz-Manifest und keine
Hashliste an (`_vorgaben/qualitaetsstandards/projektsteuerung.md`); für sie
entfällt dieser Abschnitt. „P0“ bezeichnet hier die früheren Prüfpläne und
Nachweise dieser Bestandskurse (z. B. `checks.p0.json`); die Regeln dazu heißen
heute `pruefstrategie.md`.

Grundsätze:

- Bei reinen Dokumentationsänderungen unveränderte Frage-/XML-Hashes gegen den
  vorhandenen Nachweis abgleichen, statt die ganze Inhaltsprüfung zu wiederholen.
- Den alten Dokumenthash ausdrücklich der gesicherten Vorfassung zuordnen; keinen
  aktuellen Gesamt-Fingerprint behaupten.
- Parallel gepflegte Status-/Auftragsdateien nicht in die statische Quellenbindung
  aufnehmen; Variante und gewählten Kursumfang zur Laufzeit semantisch prüfen.
- Einen optional dokumentierten Lesestand klar von unveränderlichen
  Fach-/Ergebnisartefakten trennen, damit legitime Kontextänderungen keinen
  fachlich unveränderten Test blockieren.
- Alte Nachweise unverändert historisch erhalten; nur explizit autorisierte Pfade
  mit vollständigen Alt-/Neuhashes neu binden, alle übrigen Hashprüfungen strikt
  lassen. Den historischen Gesamt-PASS nicht auf neue Quellenbytes übertragen.

Reihenfolge:

1. Manifest, Übergabe, Abschlussvalidator, vorhandene Regressionstests und alte
   P0-Evidenz gemeinsam lesen. Die vollständige Eingabeliste des Altnachweises
   prüfen: Ein korrigierter Lösungsschlüssel oder Rahmen kann dort zusätzlich
   gebunden sein, auch wenn Fragen und XML unverändert bleiben.
2. Aktuelle Quellenbytes mit den im Auftrag freigegebenen vollständigen Hashes
   abgleichen. Vor Änderungen alle bisherigen Quiz-Ergebnisdateien gegen das alte
   Manifest prüfen; dadurch lässt sich die behauptete Inhaltskonstanz belegen.
3. Im Manifest ausschließlich die autorisierten Quellen auf neue Bytezahl/Hash
   setzen und je Pfad das genaue Alt-/Neuhashpaar samt fachlichem Änderungsgrund
   erfassen. Wenn das Assessment ausdrücklich bytegleich bleiben muss, auch ein
   eingebettetes altes Rahmenhashfeld nicht ändern: Es dokumentiert die Herkunft.
   Eine separate geschützte Rebind-Datei verknüpft genau diesen alten Hash mit dem
   aktuellen Rahmen, den autorisierten Quellenwechseln und den unveränderten
   Assessment-/XML-/HTML-/PDF-Hashes. Der Validator prüft Herkunft und aktuelle
   Bindung getrennt sowie die übrigen Quellen weiterhin vollständig gegen den Rahmen.
   Keine pauschale Ausnahme für geänderte Markdown-Dateien zulassen:
   Sie würde auch unerlaubte weitere Quellenänderungen verdecken.
4. Den historischen P0-Bericht und seine ursprünglichen Eingabehashes unverändert
   lassen. Im Delta-Validator getrennt prüfen: Der Altbeleg nennt den alten Hash,
   die heutige Quelle besitzt exakt den neu autorisierten Hash. Nicht betroffene
   Eingaben, Validatoren und Quiz-Ergebnisdateien weiterhin strikt vergleichen.
   Einen ursprünglichen Gesamt-PASS nur für seine damaligen Bytes ausweisen;
   aktuelle Quellenbindung ist weder neuer Fachreview noch aktueller Gesamt-PASS.
5. Manifesthash erst nach der letzten Manifeständerung berechnen und in die
   Übergabe übernehmen. Abschluss-Prüfcode separat hashen statt ihn an seinen
   eigenen veralteten Hash im Prüfmanifest zu binden. Herkunftshashes in bewusst
   unveränderten Generatoren/Fragenpools als historisch erklären; solche Generatoren
   nicht zur vermeintlichen Reparatur erneut ausführen.
6. Den Abschlussvalidator und die vorhandenen Regressionstests ausführen, jeweils
   mit Exitcode und getrenntem Log. Beispielsweise ab Repository-Wurzel:
   `python courses/<Kurs>/quiz/validate_abschluss.py` und
   `python -m unittest discover -s courses/<Kurs>/quiz -p test_validate_abschluss.py -v`.
   Die Pfade dem tatsächlichen Projektbestand entnehmen, nicht neu voraussetzen.
   Bei vorhandenen P0-Plänen den betroffenen Check gezielt mit
   `python scripts/check_runner.py run --spec <Plan> --check <Check-ID>` wählen;
   keine komplette Produktion oder unverändertes PDF-Rendering starten. Neue vom
   Validator gelesene Rebind-Dateien und Inhaltsanker in dessen Eingabeliste aufnehmen.
   Vorher prüfen, ob alte Evidenz tatsächlich lokal vorliegt: Ein Bericht mit früherem
   PASS oder ein fehlender Cache belegt keinen aktuellen REUSED-Lauf. Fehlende alte
   Evidenz offen nennen und den erforderlichen gezielten Check neu ausführen.
7. Regressionen um die konkrete Bindungsänderung ergänzen: autorisierte neue
   Quellen akzeptieren; weitere veränderte Quellenbytes, ein als aktuell
   umetikettiertes Alt-PASS und nachträglich auf neue Werte umgeschriebene
   P0-Eingabehashes ablehnen. Bei getrennten Herkunfts-/Aktuellbindungen auch das
   Überschreiben des alten Assessment-Herkunftshashs sowie veraltete aktuelle
   Rahmenbindungen ablehnen. Kontext-/Hashmutationen in Tests im Speicher mocken,
   damit keine fremden Fach- oder Statusdateien für Negativtests geändert werden.
   Den erwarteten Ablehnungsgrund oder die erreichte Prüfstufe mitprüfen: Ein neuer
   vorgelagerter Hashwächter kann sonst sämtliche alten Mutationstests früh abbrechen
   und eine nicht mehr ausgeübte Bewertungs-/Paritätsprüfung scheinbar bestätigen.
   Bei temporären Testkopien neue gelesene Metadaten und Inhaltsanker mitkopieren,
   damit fehlende Dateien nicht als erfolgreiche fachliche Fehlererkennung zählen.
8. In der Übergabe geänderte Metadaten-/Prüfdateien mit vollständigen SHA-256,
   erfolgreiche Exitcodes und unveränderte Quiz-Contenthashes melden. Ein neues
   Metadatenpaket nicht als neue Reviewer- oder Veröffentlichungsfreigabe ausgeben.

## Gezielt prüfen

- XML parsen; Kategorie, Titel, Text und Tags strukturell prüfen.
- Bewertung/Antworten/Feedback gegen den freigegebenen Blueprint prüfen.
- In Typvorlagen benötigte Felder ergänzen; Platzhalter nicht ausliefern.
- CLOZE-Syntax und Toleranzen typspezifisch prüfen; lokale Syntaxprüfung ersetzt
  keine Moodle-Vorschau bei bislang ungeprüfter Interaktion.
- Für `ddwtos`, CodeRunner und SVG nur den passenden Abschnitt in
  `authoring-details.md` lesen.
- Keine wiederholte Markerzählung, zusätzliche Pflichtvorschau oder vollständige
  Testserie für eine unveränderte Datei. Vorhandene Nachweise nach
  `pruefstrategie.md` verwenden.
