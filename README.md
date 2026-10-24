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
- moodle

Der Quiz-Agent verwendet den projektspezifischen Skill unter
`agents/quiz/skills/moodle-fragen-generator`. Dessen `examples/`-Ordner enthält
Referenzbeispiele; neue Quizdateien gehören in den jeweiligen Kursordner.

## Lokale Pfade
- Repository: `C:\Users\Horn\Projekte\Moodle-Kurse`
- Moodle MCP: `C:\Users\Horn\Projekte\moodle2\MoodleMcp`

## Wichtige Sicherheitsregel
Nur das Hermes-Profil `moodle` erhaelt den Moodle-MCP.
Das Tool `moodle_delete_module` wird nicht freigegeben.

## Setup
```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup-hermes.ps1
```

Optional kann Hermes durch das Skript installiert werden:
```powershell
.\setup-hermes.ps1 -InstallHermes
```

## Git
Das Setup fuehrt absichtlich weder Commit noch Push aus.
