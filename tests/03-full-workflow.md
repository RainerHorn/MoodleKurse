# Test 03 – Workflow bis zum Reviewurteil, ohne Bau

Direkt im Orchestrator-Chat eingeben. Ablauf und Ketten: `docs/mbz-workflow.md`.

Projekt: FIAE LF05 – REST-API
Umfang: 6 Unterrichtsstunden einschliesslich Test
Voraussetzungen: Java-Grundlagen und OOP
Ziel: Die Lernenden entwickeln eine einfache REST-API.
Variante: MBZ, ganzer Kurs.

Erzeuge das Projekt unter:
`courses/FIAE/lf05-rest-api-test`

Dies ist ein Prozesstest: Der Auftrag endet mit dem Reviewurteil. Es wird kein
Kursplan erstellt und keine `.mbz` gebaut, auch nicht nach `APPROVED`.

## Kette 1

Erwartet: erste Welle (`fiae`, `didaktik`) gebündelt, `RAHMEN.md` eingefroren,
zweite Welle (`quiz`, `visual-designer`) gebündelt, Ordner `01-fach`,
`02-didaktik`, `04-quiz`, `06-design`, `STATUS.json` am Meilenstein
„Materialien“, genau eine Meldung „Materialien fertig“. Der Lernfeldbezug ist
von `fiae` aus dem lokalen Rahmenlehrplan belegt, nicht aus dem Projekttitel
übernommen.

## Kette 2

Danach eingeben: `weiter`

Erwartet: ein Gesamt-Review durch `reviewer` mit `STATUS: APPROVED` oder
`STATUS: REJECTED` und Findings in den Stufen `BLOCKER`, `HINWEIS`,
`KOSMETISCH`. Bei `REJECTED` genau eine Korrekturwelle und die Meldung
„Korrekturen fertig“; das Delta-Review folgt erst nach einem weiteren `weiter`.
