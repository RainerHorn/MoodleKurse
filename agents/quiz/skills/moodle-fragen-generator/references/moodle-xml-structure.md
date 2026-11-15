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

Die Autorenfassung behält ihren Kategorieblock. Verlangt der bestätigte
MCP-Importweg eine feste Kategorie ohne Kategorieblock in der Datei, eine
auf ausdrücklichen Auftrag eine gesonderte geschützte Transportfassung ableiten.
Original erhalten; ausschließlich den Kategorieblock entfernen. Gesamtbytevergleich,
Fragebaumvergleich und SHA-256/Größe belegen gemeinsam diese begrenzte Änderung.
Diese lokale Prüfung behauptet ohne Testimport keine Live-Importfähigkeit.
Für eine solche Ableitung keine vollständige fachliche Neufreigabe verlangen.
Import und aktueller Kategorie-/Fragen-Readback bleiben Aufgabe von `moodle-mcp` (Variante MCP); bei MBZ übernimmt `moodle-mbz` Import und Prüfung im Baucontainer.

## Gezielt prüfen

- XML parsen; Kategorie, Titel, Text und Tags strukturell prüfen.
- Bewertung/Antworten/Feedback gegen den freigegebenen Blueprint prüfen.
- In Typvorlagen benötigte Felder ergänzen; Platzhalter nicht ausliefern.
- CLOZE-Syntax und Toleranzen typspezifisch prüfen; lokale Syntaxprüfung ersetzt
  keine Moodle-Vorschau bei bislang ungeprüfter Interaktion.
- Für `ddwtos`, CodeRunner und SVG nur den passenden Abschnitt in
  `authoring-details.md` lesen.
- Keine wiederholte Markerzählung, zusätzliche Pflichtvorschau oder vollständige
  Testserie für eine unveränderte Datei. P0-Nachweise verwenden.
