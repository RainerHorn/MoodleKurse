# MoodleKurse

Git-zentrierte Multi-Agent-Umgebung fuer die Erstellung handlungsorientierter Moodle-4.5-Unterrichtskurse mit Hermes Agent.

## Agenten
- orchestrator
- didaktik
- fiae
- fisi
- fidp
- vt
- quiz
- visual-designer
- reviewer
- moodle-mcp (Variante MCP: direkt per Moodle-MCP in eine bestehende Moodle)
- moodle-mbz (Variante MBZ: `.mbz`-Kurs-/Abschnittssicherung ueber lokales Docker-Moodle)

Kursaufträge gehen direkt an `orchestrator` oder über `hermes` (Regeln:
`agents/_shared/hermes/SOUL.md`); Spezialisten beauftragt nur der Orchestrator.
Ein Kurslauf besteht aus drei Ketten, zwischen denen ein „weiter“ nötig ist
([Ablauf](docs/mbz-workflow.md)).

MBZ ist der Standardweg. Der Orchestrator fragt nur bei erkennbarem Variantenwechsel nach,
etwa bei Direktimport, bestehendem Zielkurs oder ausdrücklicher MCP-Anforderung.
Der Skill von `moodle-mbz` liegt unter `agents/moodle-mbz/skills/moodle-mbz`
(Voraussetzungen: Docker Desktop, Python 3, PowerShell 7 (`pwsh`); Einstieg `scripts/mbz.ps1`).
Der Quiz-Agent verwendet den projektspezifischen Skill unter
`agents/quiz/skills/moodle-fragen-generator`. Dessen `examples/`-Ordner enthält
Referenzbeispiele; neue Quizdateien gehören in den jeweiligen Kursordner.

## Lokale Pfade
- Repository: `C:\Users\Horn\Projekte\Moodle-Kurse`
- Kurse: `courses/` ist ein eigenes, privates Git-Repository und hier per `.gitignore` ausgeschlossen
- Moodle MCP (nur `moodle-mcp`): `C:\MoodleMCP` (Sollkonfiguration: `agents/moodle-mcp/config.template.yaml`)
- MBZ-Bau (nur `moodle-mbz`): kein MCP; Sollkonfiguration `agents/moodle-mbz/config.template.yaml` (nur `terminal`)

## Wichtige Sicherheitsregel
Nur das Hermes-Profil `moodle-mcp` erhaelt den Moodle-MCP. `moodle-mbz` bekommt keinen MCP
und schreibt nie in eine Schul-Moodle.
Das Tool `moodle_delete_module` wird nicht freigegeben.

## Setup
```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup-hermes.ps1
```

Das Setup zeigt nur den Abgleichplan. Rollen und Skills werden ausschließlich
aus `agents/` gelesen; `agents/_shared/skills/` geht an jede Rolle. Anleitung für gezielte Übernahme und bestehende Profile:
[Hermes-Abgleich](docs/hermes-setup.md).

Nach Prüfung der Einträge mit `decision: replace`:
```powershell
.\setup-hermes.ps1 -ApplyPlan _workspace/profile-plan.json
```

Gemeinsame Werkzeuge: [Komponentenkatalog](platform/components.json) und
[Verwendung](docs/gemeinsame-werkzeuge.md). MBZ-Grenzen: [zentrale Machbarkeit](platform/mbz-capabilities.json).
Ablauf: [MBZ-Arbeitsablauf](docs/mbz-workflow.md). Regeln:
[Projektsteuerung](_vorgaben/qualitaetsstandards/projektsteuerung.md) und
[Prüfstrategie](_vorgaben/qualitaetsstandards/pruefstrategie.md). Variante MCP: [MCP-Anhang](docs/mcp-anhang.md).

## Obsidian-Wissensschicht

Der Vault `C:\Users\Horn\Projekte\Obsidian\vault` enthält Kursübersichten,
Entscheidungen und dauerhaftes Wissen. Kursartefakte und `STATUS.json` bleiben
verbindlich im Kursordner unter `courses/`.

Vorschau und Synchronisation:

```powershell
python -B scripts/sync_obsidian.py --source-root . --vault C:/Users/Horn/Projekte/Obsidian/vault --dry-run
python -B scripts/sync_obsidian.py --source-root . --vault C:/Users/Horn/Projekte/Obsidian/vault
```

Manuelle Inhalte innerhalb der Marker `BEGIN MANUAL` und `END MANUAL` bleiben erhalten.
Geschützte Lösungen, interne Quizdaten, MBZ-Dateien und technische Rohlogs werden nicht kopiert.

## Git
Das Setup fuehrt absichtlich weder Commit noch Push aus.
