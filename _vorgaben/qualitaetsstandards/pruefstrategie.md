# Prüfstrategie

Verbindliche Ergänzung zu `AGENTS.md`; früher „P0“. Zweck: dieselbe Eigenschaft nicht mehrfach
ohne Anlass prüfen. Quellenpflicht, unabhängiger Review, aktuelle Moodle-Daten,
Löschverbot und die Deployment-Gates aus `AGENTS.md` gelten unverändert.

## 1. Vor jedem Arbeitspaket

Ersteller/Orchestrator nennt kurz: Änderung, betroffene Dateien/Abhängigkeiten,
benötigte Prüfeigenschaften, vorhandene Nachweise und Modus (`routine` oder
`tool-acceptance`). Kein neues ausführliches Planungsdokument dafür erzeugen.
Bei unklarem Einfluss breiter prüfen und den Grund einmal notieren.

| Änderung | Erforderliche Prüfung | Keine automatische Wiederholung |
|---|---|---|
| Unverändertes Paket | Vorhandenen Nachweis dem Paketstand (Paket-ID, ggf. das eine Binding) und Geltungsbereich zuordnen | Identische Testserie durch jeden Agenten |
| Aktivitätstitel | Gespeicherter Titel, Ziel-ID und erwartete Sichtbarkeit; gesammelt möglich | Vollständiger HTML-Download, Rechen-/Quiztests |
| Links/Platzhalter | Erlaubter Diff, gelesene Zielzuordnung, verbleibende Platzhalter, betroffene Klickwege | Fachreview unveränderter Aussagen |
| Layout/CSS | Betroffene Ansichten, Lesbarkeit, Bedienbarkeit; Inhaltsgleichheit bei reinem Layoutauftrag | Unveränderte Fach-/Quizrechnungen |
| Fachinhalt/Rechenwerte | Fachliche Prüfung und alle abhängigen Aufgaben, Lösungen, Quizfragen/Simulationen | Unabhängige, unveränderte Kursteile |
| Quizbewertung/Antworten | Betroffene Lösungen, Punkte, Toleranzen, Feedback und ggf. Moodle-Vorschau | Unveränderte Gestaltung anderer Seiten |
| Import unveränderter freigegebener Quelle | Zielzuordnung und gespeicherte Bytes/Hash/Sichtbarkeit | Zweiter vollständiger Inhaltsvergleich bei verifizierender Antwort |
| Sichtbarkeit/Rechte/Quizschutz | Aktueller Zielzustand, gespeicherte Schutzparameter, betroffene Lernendenzugriffe | Inhalts-/Rechentests ohne Inhaltsänderung |
| Werkzeug/Plugin/Theme/relevante Umgebung | Betroffene Integrations-/Regressionsprüfungen; ggf. neue Werkzeugabnahme | Unabhängige unveränderte Komponenten |

## 2. Moodle: Nachweis bei Variante MCP

Steht in `docs/mcp-anhang.md` und gilt nur nach ausdrücklichem Variantenwechsel.

## 2a. Moodle: Nachweis bei Variante MBZ

`moodle-mbz` verwendet kein MCP und schreibt nie in die Schul-Moodle. Der Bau liefert
je Lauf drei Nachweise: statische Prüfung der `.mbz` (`check_mbz.py`: XML ohne CR,
Deklaration, Prüfsummen), Probe-Wiederherstellung im Baucontainer und Planvergleich
(`pruef.php`: Typ, Name, Sichtbarkeit, Textlängen, Fragenanzahl, Dateitypen, Bewertung).
Sie gelten für genau diese `.mbz` (SHA-256), den Plan-Hash und den Image-/Plugin-Stand.
Bei unverändertem Plan und gleichem Stand nicht erneut bauen; ein geänderter Abschnitt
verlangt nur den Neubau und die Prüfung dieses Abschnitts. Die Probe im Container belegt
weder Rechte noch das Verhalten in der Schul-Moodle noch Browserfunktion von HTML-Dateien;
das bleibt Abnahme der Lehrkraft nach dem Wiederherstellen. Nicht unterstützte Elemente
und fehlende Fragetyp-Plugins (Stand: `platform/mbz-capabilities.json`) werden in der
Übergabe benannt, nicht umgangen.

## 3. Werkzeugabnahme und Routinebetrieb

- `tool-acceptance`: bei neuem/geändertem Werkzeug oder relevanter Umgebung.
  Betroffene Positiv-/Negativfälle, Fehlerauswertung, unabhängige Rücklesewege und
  Berechtigungen prüfen. Nachweis an Version und relevante Umgebung binden.
- `routine`: nach gültiger Abnahme. Eingaben, verifizierende Antworten und noch
  offene Eigenschaften prüfen. Nicht bei jedem Kurs Fehlerinjektion und sämtliche
  Transporttests der unveränderten Plattform wiederholen.
- Speicherung, fachliche Qualität, Browserfunktion und Zugriffsrechte sind
  getrennte Eigenschaften. Hashgleichheit ersetzt keinen Lernenden-/Funktionstest.

## 4. Lokale Tests und optionale Nachweiswiederverwendung

Kursbezogene Validatoren dürfen direkt ausgeführt und mit ihrem PASS/FAIL-Ergebnis
dokumentiert werden. `scripts/check_runner.py` ist optional und wird nur verwendet,
wenn ein deterministischer Test über mehrere Kurse hinweg wiederverwendet werden
soll oder wenn Builder, Importwerkzeug, Plugin oder eine andere technische
Komponente entwickelt bzw. abgenommen wird. Normale Unterrichtsdokumente,
redaktionelle Änderungen und einmalige Kursprüfungen benötigen keinen Runner-Plan.

Wenn der Runner eingesetzt wird, enthält der Prüfplan die tatsächlich relevanten
Eingaben, Validatoren, Argumente, Arbeitsverzeichnis und nicht geheime
Umgebungskennungen. Berichte, Cache und Logs sind Ausgaben und keine Eingaben.
Der Runner führt keine Moodle-Aufrufe aus.

Der Runner darf für seine interne Cacheentscheidung technische Fingerabdrücke
erfassen. Diese werden nicht in Rahmen-, Übergabe-, Design- oder Reviewdokumente
kopiert. Nur ein erfolgreicher Lauf bei unveränderten relevanten Eingaben kann
wiederverwendet werden.
Fehler, fehlende Dateien, Timeout oder während des Tests geänderte Eingaben
ergeben keinen gültigen Nachweis. Ein veralteter Erfolg darf einen neueren
Fehlschlag nicht überdecken. `--force-reason "..."` erzwingt begründet eine
erneute Ausführung. Bei Unklarheiten über Abhängigkeiten nicht wiederverwenden.

Ausgaben liegen intern unter `<Planname>.pruefung-intern/` neben dem Plan:
`evidence.json` (technische Nachweise), `events.jsonl` (Messdaten), `logs/`
(Testausgaben, können Lösungen enthalten). Niemals nach Moodle ausliefern.
Diese Dateien sind KEIN zentraler Projektstatus und KEINE Reviewer-Freigabe.
Pro Prüfplan nur ein Runner gleichzeitig; weitere Aufrufe werden abgewiesen.
Nach einem harten Prozessabbruch kann eine `.lock` zurückbleiben. Erst prüfen,
ob der darin genannte Prozess noch läuft; die Sperre nicht automatisch entfernen.

Optionales Beispiel für einen wiederverwendbaren technischen Test:

```powershell
python scripts/check_runner.py run --spec courses/VT/rigging-mathematik-90min/checks.p0.json
python scripts/check_runner.py summary --spec courses/VT/rigging-mathematik-90min/checks.p0.json
```

Ein Runner-Nachweis bestätigt nur seine benannte Prüfeigenschaft, nie den
vollständigen Kurs oder offene Moodle-Gates.

## 5. Keine verpflichtende Prozessmessung

Prozessmessung ist kein Bestandteil eines normalen Kursauftrags. Vorhandene
Testdauer und Fehler dürfen für eine ausdrücklich beauftragte Prozessanalyse
ausgewertet werden. Keine Events, Telemetriedateien, Hashes oder zusaetzlichen
Agentenaufrufe allein zur Messung erzeugen. Inhalte, Lösungen, Tokens und
personenbezogene Daten gehören nie in Messmetadaten.
