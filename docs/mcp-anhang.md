# MCP-Anhang: Direktweg per Moodle-MCP

Gilt nur, wenn der Auftrag ausdrücklich zur Variante MCP wechselt (Direktimport,
bestehender Zielkurs, Moodle-MCP). Im Standardweg MBZ braucht keine Rolle diesen
Anhang; die übrigen Regeln nennen MCP nur noch als Verweis hierher. Nur
`moodle-mcp` verwendet Moodle-MCP-Werkzeuge; Löschen bleibt verboten (`AGENTS.md`).

## Unterschied zu MBZ

- **MCP** (`moodle-mcp`): Direktes Anlegen und Befüllen in einer bestehenden
  Moodle. Braucht Kurs-ID und Zielkurs, Benutzerfreigabe für das Schreiben und
  Readback je Objekt. Mehr Aktivitäts- und Quizfunktionen je nach Plugin, dafür
  ein Aufruf je Aktivität.
- **MBZ** (`moodle-mbz`): Eine `.mbz` aus dem lokalen Baucontainer, die die
  Lehrkraft selbst wiederherstellt. Grenzen: `platform/mbz-capabilities.json`.

Ein Variantenwechsel ist eine neue Entscheidung des Benutzers. Machbarkeit und
Zielnachweise werden für die neue Variante neu erhoben; Fach-, Didaktik-, Quiz-
und Design-Ergebnisse bleiben gültig, soweit Variantengrenzen sie nicht
betreffen. Beide Varianten für denselben Kurs nur auf ausdrücklichen Wunsch.

## Ablauf und Gate

Die Schritte 1 bis 8 aus `docs/mbz-workflow.md` gelten unverändert. Danach:

1. Der Orchestrator legt einen konkreten Deployment-Plan vor (Zielinstanz,
   Zielkurs, Objekte, Sichtbarkeit).
2. Geschrieben wird erst nach Reviewer-`APPROVED` **und** ausdrücklicher
   Benutzerfreigabe für genau diesen Plan (`user_authorization` in `STATUS.json`:
   `GRANTED` mit Instanz, Kurs und Paket-ID).
3. `moodle-mcp` schreibt nur im freigegebenen Zielkurs und weist den Ist-Zustand
   nach (Abschnitt Readback).

Proben mit Schreibwirkung brauchen einen gesondert freigegebenen Plan; frühe
Machbarkeit hebt dieses Gate nicht auf.

## Machbarkeit

`moodle-mcp` prüft rein lesend nach `_templates/prozess/machbarkeit.json`, einmal
pro Zielumgebung und Funktionsumfang (Ablage `moodle/machbarkeit.json` im
Kursordner). Für gleiche Umgebung, Plugin-/Adapterversion und Toolfreigabe
vorhandene Nachweise nutzen. Eine MCP-Vorprüfung ist kein MBZ-Nachweis und
umgekehrt. Sollwerte der Werkzeugfreigabe: `agents/moodle-mcp/config.template.yaml`,
Abgleich mit `scripts/config_audit.py`.

## Material für MCP aufbereiten

- **quiz:** Die Importfassung ohne Kategorien entsteht mit
  `scripts/xml_transport.py` (`docs/gemeinsame-werkzeuge.md`).
- **visual-designer:** Seiten werden über den Seitenimport übernommen;
  Linkplatzhalter `__MOODLE_URL_key__`, aufgelöst mit `scripts/build_links.py`
  aus den Readback-Zuordnungen.

## Readback: Nachweis statt mehrfaches Rücklesen

Nur `moodle-mcp` verwendet Moodle-MCP. Kurs, Abschnitt und Module vor Änderungen
aktuell lesen. Innerhalb eines zusammenhängenden Arbeitspakets diese Daten nutzen;
bei Unterbrechung, fremden Änderungen oder unklarem Stand aktualisieren.

Eine Schreibantwort zählt nur dann als Nachweis, wenn die eingesetzte
Werkzeugversion nachweislich den gespeicherten Ist-Zustand zurückliefert. Ein
Erfolgstext oder das Echo der Eingabewerte genügt nicht. Version/Code-Fingerabdruck
und Abnahmebeleg im Arbeitspaket referenzieren. Alte Berichte oder der vorliegende
lokale Quelltext allein beweisen nicht die heute laufende Serverversion.

Für einen abgenommenen Seitenimport prüfen: richtige Zielzuordnung, `verified=1`,
SHA-256 und Bytezahl gleich Quelle, erwartete Sichtbarkeit. Dann kein erneutes
`get_page_content` zur Bestätigung derselben Speicherung. Nicht belegte Metadaten
einmal gemeinsam mit `get_module_info` lesen. `get_modules` zusätzlich nur für
eine offene Bestandsfrage, z. B. unerwartete/neue Module. Fehlende Fähigkeiten
nicht annehmen; vorhandenen gezielten Leseweg verwenden.

Bei Fehler, Hashabweichung oder Timeout stoppen und tatsächlichen Zustand
ermitteln. Keine blinden Wiederholungen von Schreibaufrufen. Sichtbarschaltung
und Schutzänderungen weiterhin gezielt nachprüfen; abweichende oder unklare
Ergebnisse nicht bis zum Paketende ignorieren. Bündelung spart Abfragen, ist
keine Transaktion und keine Garantie gegen konkurrierende Änderungen.
