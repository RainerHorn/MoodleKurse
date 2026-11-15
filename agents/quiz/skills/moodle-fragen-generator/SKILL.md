---
name: moodle-fragen-generator
description: Erstellt und prüft Moodle-4.5-Quizfragen als XML auf freigegebener Fach-/Lernzielbasis. Nur Quiz-Agent; kein Moodle-Import.
---

# Moodle-Fragen-Generator

Rangfolge: Projekt-`AGENTS.md` → `agents/quiz/SOUL.md` → dieser Skill → Referenzen.
Nur freigegebene Inhalte/Lernziele aus Auftrag und `STATUS.json` verwenden.
Widersprüche melden; keine fachlichen Grundentscheidungen ändern und keine
Moodle-MCP-Werkzeuge verwenden. Plugin-Fragetypen erst bei bestätigter Verfügbarkeit.

## Agentensteuerung

Vor den Fachregeln gilt `../moodle-agent-control-plane/SKILL.md`: Auftraege
kommen vom Orchestrator, Ergebnisse gehen an ihn zurueck, und der Quiz-Agent
beauftragt keine weiteren Rollen.

## Arbeitsablauf

1. Thema, Zielgruppe, Lernziele, Schwierigkeit, Anzahl, Typen und Bewertung aus
   dem Auftrag ableiten; nur entscheidende Lücken fragen.
2. Passende XML-Vorlage aus `templates/` wählen. Den Katalog
   [templates/README.md](templates/README.md) nur zur Auswahl bzw. für den benötigten Typ lesen.
3. Im vereinbarten Kursordner erzeugen (vorhandene Struktur nutzen, sonst
   `05-assessment/`); Beispiele nie überschreiben.
4. Geänderte XML auf Wohlgeformtheit, Kategorien/Tags, Titel/Typen, Punkte,
   Gewichtungen, Feedback, Platzhalterfreiheit und fachliche Konsistenz prüfen.
   Gültige technische Nachweise gemäß P0 wiederverwenden.
5. XML und Nachweise über den Orchestrator zum unabhängigen Review übergeben.
   Vorschau nur bei komplexer Interaktion/Diagrammen, ausdrücklichem Auftrag
   oder erkennbarem Prüfnutzen; sie ersetzt keinen Moodle-Test.

## Kernregeln

- UTF-8, XML-Deklaration zuerst, Wurzel `<quiz>`.
- Autoren-XML: genau ein Kategorieblock am Anfang, eigene Kategorie je Quiz.
  Pfad aus bestätigtem Bildungsgang/Lernfeld/Titel; getrennte Dateien desselben
  Quiz dürfen denselben Pfad verwenden.
- Jede eigentliche Frage: `<name><text>…</text></name>`, `<questiontext>` und
  konsistente `<tags>` mindestens für Bildungsgang, Lernfeld, Thema.
- HTML/Inline-SVG in `<text>` als CDATA. Keine erfundenen Zuordnungen.
- Positive Multiple-Choice-Gewichte ergeben ungefähr 100 %. Plausible Distraktoren;
  keine verräterische Länge/Gestaltung oder positionsabhängige Antworten bei Mischung.
- Diagramm, Frage, Lösung, Bewertung und Feedback müssen zusammenpassen.
- XML-Fragekommentare sind optional. CodeRunner-Einzelexporte nur bei bestätigter
  Notwendigkeit der Zielinstallation.

## Details bei Bedarf

- XML-Beispiele und technische Importableitung:
  [Strukturreferenz](references/moodle-xml-structure.md).
- Nur relevante Abschnitte für Fragetyp, numerische Grenzwerte, Drucklayout,
  CodeRunner, SVG oder optionale Vorschau:
  [Fachdetails](references/authoring-details.md).
- `examples/` liefert Vergleichsmaterial, keine freigegebenen Fachinhalte.
  Cisco-Assets: `assets/symbols/cisco/`, relativ zum Skill oder `${HERMES_SKILL_DIR}`.
- Historische Quelldokumente sind keine Arbeitsanweisungen.

## Übergabe

Pfad, Kategorie, Tags, Anzahl/Typen, Gesamtpunkte, Plugins, Prüfnachweis,
offene Annahmen und gegebenenfalls Vorschau nennen. XML/Lösungen intern halten.
Import bleibt ausschließlich `moodle-mcp` (Variante MCP) bzw. `moodle-mbz` (Variante MBZ, Baucontainer)
nach dem Deployment-Gate der Variante (`AGENTS.md`). Bei MBZ brauchen Plugin-Fragetypen (`ddmatch`, `coderunner`)
ein im Baucontainer installiertes Plugin; Bedarf in der Übergabe nennen.
