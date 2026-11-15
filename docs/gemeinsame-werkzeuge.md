# Gemeinsame Werkzeuge, Version 1

Katalog: `platform/components.json`. Python-Standardbibliothek, lokale Dateien,
keine Moodle-Aufrufe. Im Kursauftrag Komponente und Version nennen; der Git-Stand
bindet die Bytes, ein eigener Dateihash ist nur für nicht versionierte Komponenten
nötig. Nach Änderung neue Nachweise nur für betroffene Eigenschaften nach `pruefstrategie.md`.
Die Grenzen des MBZ-Baus stehen in `platform/mbz-capabilities.json`.

## XML-Transport (nur Variante MCP, siehe `docs/mcp-anhang.md`)

```powershell
python scripts/xml_transport.py ORIGINAL.xml IMPORT.xml --derive
python scripts/xml_transport.py ORIGINAL.xml IMPORT.xml
```

Nur bei angeforderter Importfassung ohne Kategorien. `--derive` erzeugt eine
neue Datei exklusiv; vorhandene Dateien werden nie überschrieben. Optional
`--source-sha256 <Hash>` bindet eine freigegebene Quelle. Standardaufruf prüft
rein lesend. Das Werkzeug entfernt direkte `question type="category"`-Elemente
einschließlich einer ansonsten leeren eigenen Zeile. Alle übrigen Bytes bleiben
erhalten, auch CDATA. UTF-8, Wurzel `quiz`, keine DTD/Entities. Kein Nachweis für
Fragequalität, Punkte, fachliche Richtigkeit oder erfolgreiche Moodle-Importe.

## Link-Build (nur Variante MCP)

```powershell
python scripts/build_links.py QUELLE.html ZIEL.html --mapping readback.json --origin https://moodle.example --build
python scripts/build_links.py QUELLE.html ZIEL.html --mapping readback.json --origin https://moodle.example
```

Mapping hat `targets`: je Platzhalterschlüssel ein Objekt mit `viewurl`, `cmid`,
`modname` und `source` (tatsächlicher Readbackbeleg). Eingabe ist explizit, IDs
werden nicht erzeugt. Unterstützt doppelt zitierte `href="__MOODLE_URL_key__"`,
root-wwwroot und `/mod/<typ>/view.php?id=<cmid>` derselben Instanz. Andere Formen
bewusst ablehnen. Platzhalter nur in HTML-Linkattributen verwenden, nicht in
Skripten/Kommentaren. Der lokale Vergleich ersetzt keine Prüfung der Herkunft,
Aktualität, Erreichbarkeit oder Rechte durch `moodle-mcp`.
`build_links.py` gehört zur Variante MCP (Readback-Zuordnung). Bei Variante MBZ ersetzt
`moodle-mbz` `{{LINK:id}}` im Kursplan selbst; dort wird dieses Werkzeug nicht gebraucht.

`--build` legt eine neue Ausgabe an; Standard vergleicht nur. Keine Berichte werden
überschrieben. Für den Cache des Prüf-Runners Quelle, Mapping, dieses Script und alle sonstigen
Abhängigkeiten als Eingaben/Validatoren vollständig deklarieren. Konsolenergebnis
im vorhandenen Runner erfassen; keinen zusätzlichen Modellcheck derselben Bytes.

## Gestaltung und bestehende Kurse

Zuerst `_templates/visual-designer/html`, `css` und `js` prüfen.
Semantisches Moodle-HTML ist der Grundweg, ausgewählte Vorlage und Zielabnahme
werden im Komponentensnapshot benannt. CSS/JS/Master-Templates sind Kandidaten,
keine pauschal für jedes Zielsystem abgenommenen Komponenten. Spiele, Simulator,
Chatbot und Druck/DOCX nur nach Auftrag auswählen; bei ausdrücklicher Vorgabe
eines vollständigen Master-Templates diese respektieren oder Konflikt klären.
Optionale Funktionen samt nötigen Abhängigkeiten gezielt integrieren.

Der Rigging-Gesamtbuilder bleibt kursbezogen: Fachwerte, Simulator, DOCX und
Schutzfunktionen lassen sich nicht durch bloßes Verschieben verallgemeinern.
Gemeinsam sind jetzt Transport-/Linkstufe, Prüf-Runner und Statusprüfung.
Bestehende Kursbuilder bleiben für historische Reproduktion erhalten. Neue Kurse
nutzen gemeinsame Stufen statt neuer Kopien. Weitere Extraktionen nur bei einem
konkreten zweiten Anwendungsfall. Unveränderte Kursartefakte nicht neu generieren.
