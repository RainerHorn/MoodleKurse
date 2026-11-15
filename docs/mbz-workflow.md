# MBZ-Arbeitsablauf für Unterrichtsaufträge

Dieser Ablauf verwendet **Moodle-MBZ als Standard**. Die Variante wird nicht bei
jedem Kurs erneut abgefragt. Nur ein Auftrag mit Direktimport, Moodle-MCP,
bestehendem Zielkurs oder ausdrücklichem Variantenwechsel löst eine Rückfrage aus.
Die Lehrkraft stellt die fertige `.mbz` selbst in der Schul-Moodle wieder her.

Dies ist die **einzige Fassung der Schrittfolge**. Rollen-SOULs, Qualitätsstandards
und Vorlagen verweisen auf diese Schritte und wiederholen sie nicht. Nach einem
ausdrücklichen Wechsel zu MCP gelten die Schritte 1 bis 8 unverändert; an die
Stelle der Schritte 9 bis 12 treten Deployment-Plan, Benutzerfreigabe, Schreiben
und Readback durch `moodle-mcp` nach `docs/mcp-anhang.md`.

## 1. Auftrag und Lesestand

1. `AGENTS.md`, `_vorgaben/qualitaetsstandards/{projektsteuerung,pruefstrategie}.md`, lokale Rahmenlehrplan-/SCHUCO-Quellen und vorhandene `STATUS.json` lesen.
2. Auftrag nach `_templates/prozess/auftrag.md` festhalten: Bildungsgang, Lernfeld, Zeit **einschließlich Test**, Lernprodukt, Abnahmekriterien und die MBZ-Variante. **Ebene** ausdrücklich klären: vollständiger Kurs oder Abschnitt; bei Abschnitt Weg A (neuer Kurs) oder Weg B (in bestehenden Kurs), bei B Zielabschnittsnummer. Fehlende Zahlen/IDs nie raten. Kursordner nach dem Aufbau in `projektsteuerung.md` anlegen.
3. `brief.moodle_variant` in `STATUS.json` auf `MBZ` setzen. Den Bedarf des
   Kurses gegen `platform/mbz-capabilities.json` (zentrale MBZ-Machbarkeit)
   halten. `moodle-mbz` nur dann rein lesend vorprüfen lassen, wenn der Kurs
   etwas braucht, das dort fehlt (Aktivitätsart, Fragetyp, besondere
   Schutzfunktion, noch nicht abgenommener Zielweg), oder wenn sich Image,
   Plugins oder Bauwerkzeug geändert haben. Sonst kein Machbarkeitslauf.

## 2. Materialien und einfache Standbindung

4. Erste Welle, gebündelt und parallel: Fachagent (Grundlagen, Quellen, Werte)
   und `didaktik` (Ablaufskizze); eine nach Schritt 3 nötige Vorprüfung läuft
   mit. Widersprüche beheben und einen gemeinsamen Rahmen (`RAHMEN.md`) mit
   Testzeit einfrieren. Zweite Welle, wieder gebündelt: `quiz` und
   `visual-designer` auf diesem Rahmen, mit getrennten Ausgabepfaden. Regeln
   für die Wellen: `projektsteuerung.md`. Plattformlücken als eigenen Auftrag
   führen. Keine Hashes in den Fachdokumenten pflegen.
5. `quiz` benennt die **genaue MBZ-XML-Quelle** (mit oder ohne Kategorieblock) und prüft sie gegen den tatsächlichen lokalen `quiz.quelle`-Importpfad. Historische Transportdateien einer anderen Variante nicht stillschweigend verwenden. Lösungen/Antworten, XML mit Antwortdaten und Prüflogs bleiben intern.
6. `visual-designer` mappt alle Lernendenressourcen auf Seite/Datei/Test und Zugriffsstatus. Vollständige HTML-Dokumente mit eigenem CSS/JS sind als Dateien zu planen; Moodle-Editor-Fragmente als Seiten benötigen eine spätere Darstellungsprüfung. Optionale Vertiefung, Testmaterial und geschützte Lösungen getrennt halten.
7. Braucht der Review eine exakte Standbindung, referenziert er im Regelfall
   einen Git-Commit. Ein Quellmanifest nur, wenn ein vorhandenes Werkzeug es aus
   den Auslieferungsquellen erzeugt; ein gemeinsames Manifest-Werkzeug gibt es
   bisher nicht, und von Hand wird keines geschrieben. Keine Teilmanifeste je
   Rolle und keine Hashlisten in Rahmen-,
   Design-, Quiz-, Status- oder Übergabedokumenten. Eine Inhaltsänderung führt nur
   zur gezielten Nachprüfung ihrer Auswirkungen, nicht automatisch zum Vollreview.

## 3. Review und lokaler Bau

8. Unabhängiger Reviewer prüft das fertige Artefaktpaket einmal gegen Fach,
   SCHUCO, Assessment, Design und erkennbare MBZ-Grenzen. Findings gebündelt an
   Eigentümer; nach Korrektur nur geänderte Inhalte und Auswirkungen nachprüfen
   (genau eine Korrekturwelle, genau ein Delta-Review). Bleibt es bei `REJECTED`,
   folgt keine weitere Welle, sondern ein Benutzergate mit offenen `BLOCKER`,
   vermuteter Ursache und Optionen.
9. **Nach aktuellem Artefakt-APPROVED** beauftragt der Orchestrator `moodle-mbz` in derselben Kette mit dem vollständigen `moodle-mbz/kursplan.json` und dem finalen Bau. Eine gesonderte Benutzerfreigabe braucht dieser Schritt nicht: Die `.mbz` entsteht lokal, kein Agent handelt in der Schul-Moodle, und über den Einsatz entscheidet die Lehrkraft mit dem Wiederherstellen. Ein Benutzergate entsteht nur, wenn der Plan vom Auftrag abweicht (Ebene, Zielweg, Zielabschnitt), ein Element nicht unterstützt wird oder der Plan Sichtbarkeit oder Schutz gegenüber dem geprüften Paket ändert (dann zusätzlich Reviewer nach `projektsteuerung.md`). Lokale **Testbauten** auf ausdrücklich abgegrenzten Plan sind schon vorher zulässig.
10. Anforderungen an den Kursplan: eindeutige Quellzuordnung, Reihenfolge, Aktivitätsart, Sichtbarkeit, Quiz-Fragenquelle, Bewertung, Zeitlimit, Versuche und Dateiformate. Geschützte Dateien (`_intern`, siehe `projektsteuerung.md`) nicht als Lernendenressourcen eintragen; `moodle-mbz` stoppt, wenn der Plan es doch tut. Wenn der Builder Quiz-Review-Optionen nicht sicher setzt: Quiz im Plan und in der Sicherung `sichtbar:false`; nach Wiederherstellung muss die Lehrkraft die Antwort-/Feedbackoptionen setzen und die Lernendensicht prüfen, **bevor** sie es sichtbar schaltet. Keine automatische Plattformerweiterung ohne eigenen Auftrag und Abnahme. Der Orchestrator prüft Plan und Baunachweise gegen das APPROVED-Paket, **bevor** er die `.mbz` übergibt; bei Abweichung keine Übergabe, sondern ein Finding an `moodle-mbz`.
11. `moodle-mbz` baut ausschließlich im lokalen Container. Das Bauprotokoll nennt
    Planstand, Image-/Plugin-Stand und SHA-256 der fertigen `.mbz`. Es führt drei
    technische Nachweise: `check_mbz.py`, Probe-Wiederherstellung und
    `pruef.php`-Planvergleich. Bei Abweichung stoppen; unveränderten Plan nicht
    erneut bauen.
12. Lehrkraft stellt die Sicherung selbst wieder her und nimmt **in ihrer Schul-Moodle** Berechtigungen, Seiten-Sanitization, Desktop/Mobil/Druck, Downloads, Quizschutz und Lernendenansicht ab. Lokale Probe und Hash beweisen diese Eigenschaften nicht. `STATUS.json` führt Artefakt-Review und technische Bereitschaft getrennt.

Der Orchestrator aktualisiert `STATUS.json` nur an fünf Meilensteinen: Auftrag
(nach Schritt 3), Rahmen (in Schritt 4), fertige Materialien (vor Schritt 8),
Review (nach Schritt 8) und MBZ-Bau (nach Schritt 11).

## Ketten

Das Gateway begrenzt aufeinanderfolgende Bot-Nachrichten (`max_hops`, derzeit 8;
Agenten ändern das nie). Ein Kurslauf wird deshalb in drei Ketten geteilt. Eine
Kette hat höchstens zwei Wellen aus Auftrag und Rückmeldung; mit dem Weg über
`hermes` bleiben so zwei Hops Reserve.

| Kette | Schritte | Inhalt | Endet mit |
|---|---|---|---|
| 1 Materialien | 1 bis 6 | Auftrag, erste Welle, Rahmen einfrieren, zweite Welle | Meldung „Materialien fertig“ |
| 2 Review | 7 bis 11 | Gesamt-Review; bei `APPROVED` Kursplan und finaler Bau, bei `REJECTED` die eine Korrekturwelle | Übergabe der `.mbz` oder Meldung „Korrekturen fertig“ |
| 3 Delta-Review | 8 bis 11 | nur nach `REJECTED` in Kette 2: Delta-Review der Korrekturen; bei `APPROVED` Kursplan und finaler Bau | Übergabe der `.mbz`; bei `REJECTED` Benutzergate |

Schritt 12 macht die Lehrkraft außerhalb der Ketten.

Am Ende jeder Kette aktualisiert der Orchestrator `STATUS.json` (`next_action` =
nächste Kette oder offene Entscheidung) und meldet genau einmal an den
Auftraggeber. Die nächste Kette startet erst mit einem neuen Turn des
Auftraggebers, zum Beispiel „weiter“. Offene Auftragsfragen und jedes andere
Benutzergate beenden die laufende Kette ebenfalls. Erreicht ein spätes Ergebnis
den Auftraggeber nicht von selbst, ist `STATUS.json` der Wiederaufnahmepunkt.

## Übergabeformat

- Nutzer erhält eine kurze Zusammenfassung, die freigegebene `.mbz` als Datei **erst nach den Gates**, deren vollständigen SHA-256 und Größe, Kurs-/Abschnittsebene und lokale Bau-/Prüfnachweise sowie offene Lehrkraft-Schritte.
- Keine Artefakt-Hashliste standardmaessig ausliefern. Nur auf ausdrueckliche
  Nachfrage den Git-Stand oder ein von einem Werkzeug erzeugtes Quellmanifest nennen; geschuetzte
  Loesungsdateien, Statusdaten und Prueflogs bleiben intern.
- Keine erfundenen Kurs-IDs, Wiederherstellungslinks oder Moodle-Erfolgsnachweise.
