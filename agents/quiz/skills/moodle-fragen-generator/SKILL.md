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
   dem Auftrag ableiten; nur entscheidende Lücken fragen. Die aktuelle Moodle-Variante
   aus Status und Auftrag bestimmen, bevor frühere Transport- oder Techniknotizen
   übernommen werden; ein eingefrorener Fachstand friert nicht die Zieltechnik ein.
2. Passende XML-Vorlage aus `templates/` wählen. Den Katalog
   [templates/README.md](templates/README.md) nur zur Auswahl bzw. für den benötigten Typ lesen.
3. Im vereinbarten Kursordner erzeugen (vorhandene Struktur nutzen, sonst
   `04-quiz/`); Beispiele nie überschreiben.
4. Geänderte XML auf Wohlgeformtheit, Kategorien/Tags, Titel/Typen, Punkte,
   Gewichtungen, Feedback, Platzhalterfreiheit und fachliche Konsistenz prüfen.
   Gültige technische Nachweise gemäß
   `_vorgaben/qualitaetsstandards/pruefstrategie.md` wiederverwenden.
5. Vor Abschluss alle angekündigten Übergabedateien tatsächlich erstellen und
   ihre Verweise prüfen; fertige Fragen allein schließen das Paket nicht ab.
   Prüf-Exitcodes, wiederverwendeten Geltungsbereich und offene Gates nennen.
   Kein eigenes Quiz-Manifest und keine Hashliste anlegen
   (`_vorgaben/qualitaetsstandards/projektsteuerung.md`). Verlangt der konkrete
   Auftrag ausnahmsweise eine Standbindung, sie automatisch aus den tatsächlichen
   Dateien erzeugen und gegenlesen, nie von Hand pflegen; Manifest und Übergabe
   nicht rekursiv ineinander hashen.
6. XML und Nachweise über den Orchestrator zum unabhängigen Review übergeben.
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
- Formuliere sichtbare Bewertungskriterien lösungsneutral: Nenne die geforderte
  Leistung und Punkte, nicht bereits die gesuchte Rolle, den Rücksprung oder den
  korrigierten Ausgang. Prüfe auch Kriterien, Überschriften und Hilfetexte auf
  Antwortverrat; getrennte Lösungsdateien allein reichen nicht.
- Übernimm den freigegebenen Testslot exakt und summiere Aufgabenrichtzeiten plus
  Orientierung/Endkontrolle maschinell. Begründe die Bearbeitbarkeit anhand der
  tatsächlichen Lese-/Antwortlast; behaupte ohne Zielgruppenpilot keine empirisch
  bestätigte Dauer und leite Zeit oder Punktgewichte nicht pauschal aus der
  Fragenanzahl ab.
- Liefere bei MBZ die kategorisierte Autoren-XML als exakt benannte Importquelle
  und einen maschinenlesbaren Slot-/Punkte-/Zeit-/Schutzplan. Eine historische
  kategorielose MCP-Transportfassung ist keine MBZ-Importvorgabe. Benenne für die
  Designintegration Bannergruppe, Einrückung und anfängliche Sichtbarkeit von Test
  und Test-PDF, ohne eine konkurrierende Design-Deployment-Map zu erzeugen.
- Erlaubte Sichtauszüge und Merkhilfen im Testkopf benennen und konkret aus der
  freigegebenen Quelle übernehmen. Ihre tatsächliche Sichtbarkeit für jede betroffene
  Frage und im Papierfallback prüfen; ein Link oder ein bloßer Materialverweis
  ersetzt keine im Test verfügbare Quelle.
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
Nur für Bestandskurse mit hashgebundenen Altnachweisen gilt der Rest dieses
Absatzes bis zum Verweis auf die Strukturreferenz:
Bei reinen Dokumentationsänderungen unveränderte Frage-/XML-Hashes gegen den
vorhandenen Nachweis abgleichen, statt die ganze Inhaltsprüfung zu wiederholen.
Den alten Dokumenthash ausdrücklich der gesicherten Vorfassung zuordnen; keinen
aktuellen Gesamt-Fingerprint behaupten. Parallel gepflegte Status-/Auftragsdateien
nicht in die statische Quellenbindung aufnehmen; Variante und gewählten Kursumfang
zur Laufzeit semantisch prüfen. Einen optional dokumentierten Lesestand klar von
unveränderlichen Fach-/Ergebnisartefakten trennen, damit legitime Kontextänderungen
keinen fachlich unveränderten Test blockieren.
Bei freigegebenen Quellenkorrekturen auch die Eingabeliste alter Prüfnachweise (früher „P0“) prüfen.
Alte Nachweise unverändert historisch erhalten; nur explizit autorisierte Pfade mit
vollständigen Alt-/Neuhashes neu binden, alle übrigen Hashprüfungen strikt lassen.
Unveränderte Quiz-/XML-/HTML-/PDF-Bytes weiter gegen den früheren Stand vergleichen,
aber den historischen Gesamt-PASS nicht auf neue Quellenbytes übertragen.
Bei ausdrücklich unveränderlichem Assessment auch dessen Herkunftshash erhalten;
neuen Rahmenstand über separate geschützte Alt-/Neu-Bindungsmetadaten zuordnen,
statt durch Umschreiben des Herkunftsfelds eine verbotene Inhaltsänderung auszulösen.
Den Delta-Validator mit Positiv- und Negativfällen prüfen: legitimer Kontextwechsel,
unerlaubte Quellenbytes, falsche Variante/Kursebene sowie Umlabeln alter Nachweise.
Die [Strukturreferenz](references/moodle-xml-structure.md) beschreibt die Reihenfolge
für Quellenneubindung und historische Prüfevidenz.
Freigabestatus explizit nach Gegenstand prüfen; ein Textmuster, das Negationen wie
„kein APPROVED“ übersieht, kann eine offene Freigabe irrtümlich positiv auslegen.
Import bleibt ausschließlich `moodle-mcp` (Variante MCP) bzw. `moodle-mbz` (Variante MBZ, Baucontainer)
nach dem Deployment-Gate der Variante (`AGENTS.md`). Bei MBZ brauchen Plugin-Fragetypen (`ddmatch`, `coderunner`)
ein im Baucontainer installiertes Plugin; Bedarf in der Übergabe nennen.
