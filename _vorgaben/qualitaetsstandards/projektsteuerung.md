# Projektsteuerung

Ergänzt `AGENTS.md`; früher „P1“, enthält seit dem 15.11.2026 auch „P2“
(Produktionsablauf). Gilt für alle neuen Unterrichtsaufträge; vorhandene
Kursfassungen und Freigaben werden dadurch nicht rückwirkend geändert. Prüfregeln
stehen in `pruefstrategie.md`, die Schrittfolge in `docs/mbz-workflow.md`.
Die Vorlagen sind kurze Arbeitsverträge, keine zusätzlichen Pflichtberichte:
ausgefüllte Aufträge/Übergaben können direkt in der Agentennachricht stehen.

## Verbindlicher Stand

`courses/<Auftrag>/STATUS.json` ist die einzige aktuelle Statusquelle; Eigentümer
ist der Orchestrator. Inhaltlich nur an den Meilensteinen Auftrag, Rahmen, fertige
Materialien, Review und MBZ-Bau aktualisieren. Zusätzlich wird am Ende jeder
Kette und an jedem Benutzergate `next_action` gesetzt, auch wenn kein
Meilenstein erreicht ist (z. B. nach der Korrekturwelle).
Andere Agenten liefern Änderungen, schreiben die Statusdatei nicht gleichzeitig.
`PROZESS.md` ist nur Einstieg/Verweis. Frühere Reviews und Importprotokolle bleiben
unveränderte Historie. Ein alter Satz „Review ausstehend“ in einer Quelle ist
keine erneute Freigabeanforderung, wenn ein passender späterer Nachweis existiert.

Schema/Vorlage: `_templates/prozess/STATUS.json`. Relative Dateipfade beziehen
sich auf den Kursordner, `brief.sources` auf die Repository-Wurzel. Keine Lösungen
oder Secrets in Statusdaten. STATUS, Reviews und interne Manifeste nie ausliefern.

- `brief`: Zielgruppe, Lernfeld, Zeit, Lernprodukt, Quellen und Abnahmekriterien.
- `package`: ID und kurze Liste der Auslieferungsdateien mit Eigentümer. Keine
  SHA-256 je Datei pflegen. `binding` nennt einmal den Stand des Pakets: den
  Commit des Kurs-Repositorys `courses/` (`{"type": "git", "value": "<Hash>"}`),
  den der Orchestrator am Meilenstein „fertige Materialien“ und nach jeder
  Korrekturwelle anlegt (nur der eigene Kursordner, kein Push). Eine
  Manifest-Prüfsumme ist für neue Kurse nicht vorgesehen. Status, Berichte, Backups, Logs und temporäre
  Dateien nicht aufnehmen. Eigentümer ist immer eine bestehende Rolle; schreibt
  ausnahmsweise eine Ersatzrolle, steht dort deren Name mit Verweis auf die
  ausdrückliche Eigentumsübertragung (Abschnitt „Parallele Wellen und Ausfälle“),
  kein erfundener Rollenname.
- `reviews`: Gegenstand (`artifacts` oder `deployment-plan`), Status, Prüfer,
  Beleg und Paket-ID. Falls das Paket ein `binding` besitzt, übernimmt der Review
  genau dieses eine Binding. Keine vollständigen Hashlisten im Status oder Review.
  `APPROVED`/`REJECTED` sind Reviewerurteile.
  `PENDING`, `HISTORICAL_APPROVED` und `UNRECONCILED` sind Verwaltungsstände.
- `technical`: Status `UNKNOWN`, `OPEN` oder `READY`, Zielumgebung, Machbarkeits-
  nachweis und offene technische Gates. READY nur für konkret geprüften Umfang;
  keine Übertragung von Testsystem auf Produktion.
- `user_authorization`: Status, genauer Umfang, Zielinstanz/Kurs, Paket-ID und
  gegebenenfalls dasselbe einzelne Paket-Binding
  und nachvollziehbare Benutzerentscheidung. `NOT_GRANTED`, `GRANTED` oder
  `HISTORICAL_TEST_ONLY`; historische Genehmigung wird nicht erweitert.
- `findings`: ID, Schwere, blockierte Phase, Eigentümer, Datei, Problem,
  Erfüllungskriterium, Zustand und Nachweis der Erledigung.
- `next_action`: eine konkrete nächste Aktion mit zuständiger Rolle. Am Ende
  einer Kette (`docs/mbz-workflow.md`) steht hier die nächste Kette oder die
  offene Benutzerentscheidung; das ist der Wiederaufnahmepunkt.

Bei relevanter Inhaltsänderung Paket-ID oder optionales Binding aktualisieren;
nur abhängige Freigaben als veraltet kennzeichnen. Historie behalten. Bei
Migration vorhandene Freigaben als `HISTORICAL_APPROVED` dokumentieren und
fehlende Versionszuordnung gezielt abgleichen; nicht den gesamten Kurs neu prüfen.

Statusdateien im Schema 1 (mit Einzelhashes) bleiben gültig und werden nicht
nachträglich umgeschrieben; ihre Hashbindungen sind Nachweise. Der Orchestrator
stellt eine solche Datei erst bei der nächsten Paketänderung auf Schema 2 um.

`python scripts/project_status.py <Kurs>/STATUS.json` prüft nur lokale Struktur,
Dateipfade und optionale Paketbindungen. Exit 0 bedeutet konsistente Statusdaten,
NICHT eine inhaltliche, technische oder Benutzerfreigabe. Keine Moodle-Aufrufe.

## Auftrag, Machbarkeit und Eigentümer

Vorlage `_templates/prozess/auftrag.md`: wenige verpflichtende Eckdaten und
Fertigstellungskriterien. Informationen aus Quellen/Stand ableiten; fehlende
entscheidende Angaben gebündelt fragen. Routineentscheidungen im vereinbarten
Rahmen trifft der Orchestrator. Fachliche Unsicherheit nicht durch Annahmen lösen.

Die Moodle-Variante ist standardmäßig `MBZ` (`AGENTS.md`). Der Orchestrator trägt
sie ohne Rückfrage in `brief.moodle_variant` ein und klärt mit den übrigen
offenen Auftragsfragen nur die Ebene: Kurs oder Abschnitt, bei Abschnitt Weg A/B
und gegebenenfalls die Zielabschnittsnummer. Eine Variantenfrage entsteht nur
bei erkennbarem Wechsel (Direktimport, bestehender Zielkurs, Moodle-MCP).

Machbarkeit bei MBZ: Maßgeblich ist `platform/mbz-capabilities.json`. Braucht der
Kurs nur, was dort steht, gibt es keinen Machbarkeitslauf und keine kursbezogene
`machbarkeit.json`. `moodle-mbz` prüft nur dann rein lesend vor, wenn der Kurs
eine dort fehlende Aktivitätsart, einen fehlenden Fragetyp, eine besondere
Schutzfunktion oder einen noch nicht abgenommenen Zielweg braucht oder sich
Image, Plugins oder Bauwerkzeug geändert haben. Das Ergebnis aktualisiert die
zentrale Datei; nur kursspezifische Abweichungen stehen zusätzlich in
`moodle-mbz/machbarkeit.json` (Vorlage `_templates/prozess/machbarkeit.json`).

Geänderte Voraussetzungen gezielt neu prüfen. Zielsystemunabhängige Vorarbeit
darf weitergehen. Der operative Weg steht in `docs/mbz-workflow.md`. Alles zur
Variante MCP (Machbarkeit, Gate, Readback) steht in `docs/mcp-anhang.md`; eine
MCP-Vorprüfung ist kein MBZ-Nachweis und umgekehrt.

## Kursordner, geschützte Dateien und Begriffe

Aufbau für neue Aufträge (bestehende Kursordner werden nicht umbenannt):

| Pfad im Kursordner | Eigentümer | Inhalt |
|---|---|---|
| `AUFTRAG.md`, `RAHMEN.md`, `STATUS.json` | orchestrator | Auftrag, eingefrorener Rahmen, Status |
| `01-fach/` | Fachagent | Fachgrundlagen, Informationstexte für Lernende, Werte, Lösungen |
| `02-didaktik/` | didaktik | Vollständige Lernsituation mit Arbeitsaufträgen, Ablauf, Zeitbudget, Aktivitätenliste |
| `04-quiz/` | quiz | Blueprint, Fragen-XML, Testmaterial |
| `06-design/` | visual-designer | Moodle-HTML für Lernende |
| `moodle-mbz/` | moodle-mbz | `kursplan.json`, Bauprotokoll, `mbz/*.mbz` (bei MCP: `moodle/`) |
| `review/` | reviewer | Reviewberichte |

Jede Rolle schreibt nur in ihren Pfad. Weitere Dateien im Kursordner sind
zulässig, wenn der Auftrag sie verlangt; sie ändern den Aufbau nicht.

Geschützte Dateien tragen `_intern` im Dateinamen (Groß-/Kleinschreibung egal): Lösungen, Fragen-XML mit
Antwortdaten, Blueprints, Prüflogs und Übergaben mit Lösungsbezug. Eine
`_intern`-Datei darf im Kursplan nur als Fragenquelle eines Tests oder der
Fragensammlung stehen, nie als Text, Seite, Datei oder Beschreibung für Lernende.
Sie wird weder ausgeliefert noch nach Obsidian synchronisiert. Eine Lösung, die
Lernende später sehen sollen, ist eine eigene Datei ohne `_intern`; ihr Schutz
(Sichtbarkeit, Voraussetzung) steht im Kursplan. Diese Regel ist
bisher eine Konvention ohne technische Sperre im Bauwerkzeug.

Drei Zustände werden nicht vermischt:

- **eingefroren**: Der Orchestrator hat den Rahmen (`RAHMEN.md`) festgelegt;
  quiz und visual-designer arbeiten darauf. Das ist kein Reviewurteil.
- **APPROVED**: Urteil des Reviewers für ein benanntes Paket.
- **Benutzerfreigabe**: Entscheidung des Benutzers für einen konkreten Umfang.

„Freigegeben“ ohne Zusatz in älteren Texten meint bei Eingaben für quiz und
visual-designer den eingefrorenen Rahmen, bei Bau und Auslieferung das
Reviewer-APPROVED; nur bei Variante MCP zusätzlich die Benutzerfreigabe für den
konkreten Plan (`AGENTS.md`, Deployment-Gate).

| Eigentümer | Verbindliche Angaben |
|---|---|
| Fachagent | Quellen-/Lernfeldbezug, Fachwerte, Aufgabenmodell, fachliche Lösungen |
| didaktik | Handlungssituation, Lernziele, sechs Phasen, Zeitbudget, Differenzierung |
| quiz | Aufgabenbewertung, Testumfang, Punkte und Feedback auf freigegebener Basis |
| visual-designer | Darstellung und zugängliche Bedienung ohne Inhaltsänderung |
| moodle-mcp | Instanz-/Werkzeugmöglichkeiten, IDs, Import und technischer Ist-Nachweis (Variante MCP) |
| moodle-mbz | Containerstand, unterstützte Aktivitäten/Fragetypen, Kursplan, `.mbz` und Bau-/Probenachweise (Variante MBZ) |
| reviewer | Unabhängiges Urteil, Findings und gezielte Nachprüfung |
| orchestrator | Auftragsrahmen, Übergaben, Status, Entscheidungen und Freigabeumfang |

Abgeleitete Fassungen referenzieren ihre Quelle; keine konkurrierenden Rechenwerte
oder Zeitpläne. Übergabe nach `_templates/prozess/uebergabe.md`: Dateien, Änderung,
Nachweise, offene Punkte. Keine vollständige Vorgeschichte erneut erzählen.

## Parallele Wellen und Ausfälle

Die Reihenfolge der Schritte steht in `docs/mbz-workflow.md` und wird hier nicht
wiederholt. Für die parallelen Wellen darin gelten diese Regeln:

- Der Orchestrator legt Eingabeversion, Rollen und getrennte Ausgabepfade fest
  (Aufbau siehe oben). Eine gemeinsame Quelle hat genau einen
  schreibenden Eigentümer.
- Erste Welle: Der Fachagent liefert Fachgrundlagen, Informationstexte für
  Lernende, Werte und Lösungen; `didaktik` liefert die vollständige
  Lernsituation mit ausformulierten Arbeitsaufträgen je Phase und einer
  Aktivitätenliste (Titel, Art, Phase). Fachwerte übernimmt `didaktik` nicht aus
  eigenem Wissen, sondern verweist auf die Fachquelle.
- Der Rahmen (`RAHMEN.md`) fasst Lernziele, fachliche Werte, Zeit inklusive
  Assessment, Lernprodukt, Komponenten und offene Gates zusammen und wird in den
  Folgeaufträgen genannt. Er enthält die verbindliche Aktivitätenliste mit je
  einer ID (nur `A-Z a-z 0-9 _ -`, im Kurs eindeutig), die der Orchestrator
  vergibt. Diese IDs gelten für `{{LINK:id}}` im Design und unverändert für den
  Kursplan; fehlt eine Aktivität, meldet die Rolle das an den Orchestrator und
  erfindet keine ID. Widersprüche vor dem Einfrieren klären; offene
  Technikfragen dürfen nur unabhängige Arbeiten passieren.
- Zweite Welle: `quiz` und `visual-designer` arbeiten unabhängig auf dem Rahmen.
  Der `visual-designer` setzt die Texte aus `01-fach/` und `02-didaktik/`
  unverändert um und bindet den Test nur als Aktivität über dessen ID ein, nicht
  dessen Inhalte. Einen eigenen Integrationsschritt gibt es nicht; fachliche
  Lösungen werden referenziert, nicht in der Gestaltung neu erfunden.

Der Auftrag nennt `depends_on`, Schreibpfade, Eingabestand, Fertigkriterium und
Wiederaufnahmepunkt; kompakte Vorlage `_templates/prozess/parallelplan.json`.
Die Vorlage ist Planung, kein automatischer Scheduler und keine neue Statusquelle.
Taskzustände/offene Blocker verbleiben in STATUS bzw. den Übergaben.

Bei fehlender Bot-Bestätigung zunächst Erreichbarkeit anhand vorhandener
Gateway-/Zustelldaten prüfen. Keinen identischen Auftrag mehrfach starten.
Bei Ausfall letzte gesicherte Übergabe und tatsächliche Dateien abgleichen;
Eigentum ausdrücklich übertragen, bevor ein Ersatzagent schreibt; in STATUS
steht dann die tatsächlich schreibende Rolle mit Verweis auf die Übertragung,
kein erfundener Rollenname. Unabhängige
Zweige können fortfahren. Statusabfragen nur bei fehlender Rückmeldung zum
vereinbarten Übergabepunkt, nicht nach jedem kleinen Arbeitsschritt.

## Kurs und Plattform

Kursarbeit umfasst Inhalte und die Verwendung bereits geeigneter Werkzeuge.
Neue Import-/Readback-Funktionen, Chatbot, Rechte- oder Schutzmechanismen erhalten
einen eigenen Auftrag unter `platform/changes/<ID>/` nach der dortigen Vorlage.
Ein Kurs benennt die Abhängigkeit und kann unabhängige Inhalte weiterentwickeln.
Ein verlangtes Merkmal wird weder stillschweigend gestrichen noch um zusätzliche
Funktionen erweitert. Integration und Prüfbedarf werden vor der Umsetzung geklärt.

`platform/components.json` ist der Katalog gemeinsamer Komponenten. Bei Auswahl
im Kursauftrag Komponente, Version, Umgebung und passenden Abnahmenachweis
referenzieren (Vorlage `_templates/prozess/komponenten.json`). Ein technischer
Hash ist nur bei einer nicht anderweitig versionierten Komponente nötig. Kein pauschales
„latest“. Ein lokaler Quellstand ist kein Nachweis über einen laufenden Server.
Nur `moodle-mcp` prüft den tatsächlich eingesetzten Moodle-Stand mit MCP; `moodle-mbz` prüft
den Baucontainer (Image-/Plugin-Stand) und kennt die Schul-Moodle nicht.
Fehlende Abnahme blockiert die abhängige Verwendung, nicht jede Vorarbeit.

Werkzeugänderungen erhalten gezielte Regressionstests im Plattformauftrag;
Kurse übernehmen gültige Nachweise nach `pruefstrategie.md`. Eine Versionsänderung verlangt eine
Einflussanalyse. Den gesamten Kurs nur bei entsprechendem Einfluss erneut prüfen.
Neue Schutz-/Rechtefunktionen brauchen ihre eigene technische Abnahme.

## Reviews und Veröffentlichung

Ein Gesamt-Review je fertigem Paket; alle erkennbaren Findings des Durchgangs
bündeln. Korrekturauftrag mit Finding-ID/Eigentümer/Erfüllungskriterium. Nachprüfung
auf Änderungen und Auswirkungen begrenzen (`pruefstrategie.md`). Neue echte Fehler melden,
kosmetische Wünsche als Vorschläge führen. Wiederholtes Scheitern führt zur
Ursachenklärung, nicht zum identischen neuen Auftrag. Ist das Urteil nach der
einen Korrekturwelle und dem Delta-Review weiter `REJECTED`, endet die Kette mit
einem Benutzergate: Der Orchestrator meldet offene `BLOCKER`, vermutete Ursache
und Optionen an den Auftraggeber und trägt die offene Entscheidung in
`next_action` ein. Der Reviewstatus bleibt `REJECTED`.

Schwere eines Findings, genau eine von drei Stufen: `BLOCKER` (verhindert
APPROVED für den genannten Gegenstand), `HINWEIS` (kein Hindernis für APPROVED,
soll behoben oder begründet offen gelassen werden), `KOSMETISCH` (Vorschlag ohne
Abnahmerelevanz). Der Reviewer ändert keine fremden Artefakte, auch keine
Kleinigkeiten; jede Korrektur läuft über ein Finding an den Eigentümer.

Bei MBZ prüft der Orchestrator den Kursplan vor der Übergabe der `.mbz` gegen
das APPROVED-Paket (Quelle, Sichtbarkeit, Schutz, keine `_intern`-Datei als
Lernendenressource); der
technische Abgleich Plan gegen Bau kommt aus dem Planvergleich des Baus. Ein
Reviewer-Urteil zum Plan (`deployment-plan`) ist bei MBZ nur nötig, wenn der
Plan Sichtbarkeit oder Schutz gegenüber dem geprüften Paket ändert.

Ein Blocker nennt seine Phase: z. B. fachlicher Fehler blockiert Artefaktfreigabe,
ungeklärtes Browserrendering technische Bereitschaft. Ein APPROVED mit einem
Blocker für DENSELBEN Gegenstand ist widersprüchlich. Andere Ebenen bleiben offen.

Auslieferung bei MBZ: Nach Artefakt-APPROVED baut `moodle-mbz` die finale `.mbz`
ohne weitere Benutzerfreigabe; der Orchestrator prüft Kursplan und Baunachweise
vor der Übergabe (`AGENTS.md`, Deployment-Gate). `user_authorization` bleibt dabei
`NOT_GRANTED`: Das Feld betrifft nur das Schreiben in eine Moodle-Instanz. Über
den Einsatz entscheidet die Lehrkraft mit dem Wiederherstellen.

Auslieferung bei MCP: Schreiben benötigt Artefakt-APPROVED, geprüfte technische
Voraussetzungen und Benutzerfreigabe für den konkreten Plan/Umfang. Eine
bestehende passende Freigabe nicht erneut einholen. Geänderte Instanz,
Zielgruppe, Inhalte oder Sichtbarkeit auf ihren genehmigten Umfang prüfen; keine
Erweiterung daraus ableiten. Test-only-Ausnahmen mit Bedingungen separat führen.
Reviewer darf einen Plan prüfen, genehmigt aber weder Benutzerentscheidungen
noch Produktion.
