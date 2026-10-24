---
name: moodle-fragen-generator
description: Erstellt und validiert Moodle-4.5-Quizfragen als Moodle-XML, einschließlich Kategorien, Tags, optionaler SVG-Diagramme und CodeRunner-Aufgaben. Nur für den Quiz-Agenten und nur auf Grundlage freigegebener Fachinhalte und Lernziele verwenden; kein Moodle-Import.
---

# Moodle-Fragen-Generator

Erzeuge valide, fachlich abgestimmte Moodle-XML-Fragen für einen Unterrichtsauftrag. Die gemeinsamen Regeln aus `AGENTS.md` und die Rolle aus `agents/quiz/SOUL.md` haben Vorrang vor diesem Skill.

## Grenzen

- Verwende ausschließlich freigegebene Fachinhalte, Kompetenzen und Lernziele des aktuellen Unterrichtsauftrags.
- Ändere keine fachlichen oder didaktischen Grundentscheidungen. Dokumentiere Widersprüche für Orchestrator oder Reviewer.
- Erzeuge und validiere Dateien, importiere sie aber nicht nach Moodle und verwende keine Moodle-MCP-Werkzeuge.
- Verwende Plugin-Fragetypen wie `coderunner` oder `stack` nur, wenn ihre Verfügbarkeit für das Zielsystem bestätigt wurde.
- Behandle Dateien unter `examples/` als erprobte Beispiele, nicht als verbindliche Vorgaben oder aktuelle Fachquellen.

## Arbeitsablauf

1. Ermittle Thema, Zielgruppe, Lernziele, Schwierigkeit, Anzahl, Fragetypen und gewünschte Bewertung aus dem freigegebenen Projektstand. Frage nur nach Angaben, die sich daraus nicht ableiten lassen.
2. Wähle passende Vorlagen unter `templates/`. Lies `templates/README.md` und bei Bedarf die thematisch passenden Abschnitte aus `references/authoring-details.md`.
3. Lege für jedes Quiz eine eigene Fragenkategorie fest und erzeuge Moodle-XML mit XML-Deklaration, `<quiz>` als Wurzel, einem Kategorieblock am Dateianfang sowie mindestens `<name>`, `<questiontext>` und `<tags>` pro eigentlicher Frage.
4. Speichere Ergebnisse im Ordner des Unterrichtsauftrags, standardmäßig unter `05-assessment/`. Lege keine neuen Ergebnisse unter `examples/` ab.
5. Validiere XML-Wohlgeformtheit, den Kategorieblock, Tags jeder eigentlichen Frage, Fragentitel, Fragetypen, Punktwerte, Antwortgewichtungen, Feedback, Platzhalterfreiheit und fachliche Konsistenz.
6. Erzeuge eine HTML-Vorschau nur bei komplexen Interaktionen, Diagrammen, ausdrücklichem Auftrag oder wenn sie die Qualitätsprüfung wesentlich unterstützt. Sie ist kein Ersatz für Moodle-Tests.
7. Übergib XML und Prüfergebnis an den Reviewer. Ein späterer Import bleibt dem Moodle-Agenten nach Deployment-Gate und Benutzerfreigabe vorbehalten.

## Verbindliche XML-Regeln

- UTF-8 verwenden; die XML-Deklaration muss die erste Zeile sein.
- Jede Quizdatei beginnt innerhalb von `<quiz>` mit genau einem Kategorieblock. Alle folgenden Fragen der Datei gehören zu dieser Kategorie:

  ```xml
  <question type="category">
    <category>
      <text>$course$/top/Bildungsgang/Lernfeld/Quiztitel</text>
    </category>
  </question>
  ```

- Verwende eine eigene Kategorie pro fachlich zusammengehörigem Quiz, nicht pro einzelner Frage. Mehrere technisch getrennte XML-Dateien desselben Quiz dürfen denselben Kategoriepfad verwenden.
- Bilde den Kategoriepfad aus bestätigtem Bildungsgang, Lernfeld und eindeutigem Quiztitel. Erfinde keine fehlenden Angaben; dokumentiere sie als offene Annahme.
- HTML-Fragmente und Inline-SVG innerhalb von `<text>` in CDATA einschließen.
- Den Fragentitel als `<name><text>…</text></name>` schreiben.
- Jede eigentliche Frage – ausgenommen der Kategorieblock – erhält `<tags>`. Verwende mindestens bestätigte Werte für Bildungsgang, Lernfeld und Thema; ergänze bei Bedarf Kompetenz, Fragetyp oder Schwierigkeitsgrad. Beispiel:

  ```xml
  <tags>
    <tag><text>FISI</text></tag>
    <tag><text>LF03</text></tag>
    <tag><text>OSI-Modell</text></tag>
    <tag><text>mittel</text></tag>
  </tags>
  ```

- Tags müssen fachlich zutreffen, innerhalb eines Quiz konsistent geschrieben und frei von erfundenen Lernfeld- oder Kompetenzangaben sein.
- Bei Multiple Choice müssen positive `fraction`-Werte zusammen ungefähr 100 Prozent ergeben. Positionsabhängige Antworten sind bei gemischten Optionen unzulässig.
- Distraktoren müssen plausibel sein und dürfen die Lösung nicht durch Länge, Detailgrad, Reihenfolge oder Gestaltung verraten.
- Diagramm, Frage, Lösung, Bewertung und Feedback müssen dieselbe fachliche Aussage abbilden.
- Kommentare wie `<!-- question: q1 -->` sind optional und keine Moodle-Anforderung.
- CodeRunner-Aufgaben einzeln exportieren, wenn dies für die konkrete Moodle-/Plugin-Installation als notwendig bestätigt ist.

## Ressourcen

- Für allgemeine XML-Struktur und Importdetails: `references/moodle-xml-structure.md`.
- Für spezielle Fragetypen, CodeRunner, SVG und Vorschaugestaltung: nur die benötigten Abschnitte aus `references/authoring-details.md` lesen. Bei Konflikten gilt diese `SKILL.md`.
- Für konkrete Strukturen: passende Datei unter `templates/` verwenden.
- Für Vergleich und Fehlersuche: gezielt ähnliche Dateien unter `examples/` ansehen.
- Cisco-Symbole liegen unter `assets/symbols/cisco/`; Pfade immer relativ zum Skill-Verzeichnis beziehungsweise über `${HERMES_SKILL_DIR}` auflösen.

## Abschlussbericht

Nenne Ausgabepfad, Kategoriepfad, verwendete Tags, Anzahl und Typen der Fragen, Gesamtpunkte, verwendete Plugins, XML-Prüfergebnis, offene Annahmen und ob eine Vorschau erzeugt wurde.
