<#
.SYNOPSIS
    Richtet die Hermes-Multi-Agent-Umgebung fuer das Projekt MoodleKurse ein.

.DESCRIPTION
    - Legt die Git-Projektstruktur unter C:\Users\Horn\Projekte\Moodle-Kurse an.
    - Prueft Git, Node.js, npm und Hermes.
    - Legt 10 Hermes-Profile an, falls sie noch nicht existieren.
    - Setzt fuer alle Profile das gemeinsame terminal.cwd.
    - Schreibt versionierbare SOUL.md-Dateien in agents\<profil>\.
    - Synchronisiert diese SOUL.md-Dateien in die lokalen Hermes-Profile.
    - Erzeugt AGENTS.md, .gitignore, README.md und Test-Prompts.
    - Konfiguriert den lokalen Moodle-MCP ausschliesslich im Profil "moodle".
    - moodle_delete_module wird NICHT freigegeben.
    - Fuehrt KEIN git commit und KEIN git push aus.
    - Speichert KEINE OAuth-Tokens, API-Keys oder Moodle-Secrets im Repository.

.NOTES
    Zielsystem: Windows 11, Hermes nativ, Moodle 4.5
    Projekt:     C:\Users\Horn\Projekte\Moodle-Kurse
    Moodle MCP:  C:\Users\Horn\Projekte\moodle2\MoodleMcp
#>

[CmdletBinding()]
param(
    [string]$RepoRoot = "C:\Users\Horn\Projekte\Moodle-Kurse",
    [string]$MoodleMcpRoot = "C:\Users\Horn\Projekte\moodle2\MoodleMcp",
    [switch]$InstallHermes,
    [switch]$ForceRepoFiles,
    [switch]$SkipProfiles,
    [switch]$SkipMoodleMcp
)


$ErrorActionPreference = "Stop"

# Hermes data directory:
# - Native Windows default: %LOCALAPPDATA%\hermes
# - HERMES_HOME overrides the default when explicitly set.
if ($env:HERMES_HOME -and -not [string]::IsNullOrWhiteSpace($env:HERMES_HOME)) {
    $HermesHome = [Environment]::ExpandEnvironmentVariables($env:HERMES_HOME)
} elseif ($env:LOCALAPPDATA -and -not [string]::IsNullOrWhiteSpace($env:LOCALAPPDATA)) {
    $HermesHome = Join-Path $env:LOCALAPPDATA "hermes"
} else {
    throw "Weder HERMES_HOME noch LOCALAPPDATA ist gesetzt. Hermes-Profilpfad kann nicht bestimmt werden."
}
$HermesProfilesRoot = Join-Path $HermesHome "profiles"

function Write-Info([string]$Message) {
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}
function Write-Ok([string]$Message) {
    Write-Host "[ OK ] $Message" -ForegroundColor Green
}
function Write-Warn([string]$Message) {
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}
function Write-Fail([string]$Message) {
    Write-Host "[FAIL] $Message" -ForegroundColor Red
}

function Ensure-Directory([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        Write-Ok "Verzeichnis angelegt: $Path"
    }
}

function Write-RepoFile {
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [Parameter(Mandatory=$true)][AllowEmptyString()][string]$Content
    )

    $parent = Split-Path -Parent $Path
    if ($parent) { Ensure-Directory $parent }

    if ((Test-Path -LiteralPath $Path) -and -not $ForceRepoFiles) {
        Write-Warn "Datei existiert, nicht ueberschrieben: $Path"
        return
    }

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Content, $utf8NoBom)
    Write-Ok "Datei geschrieben: $Path"
}

function Test-Command([string]$Name) {
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Invoke-Hermes {
    param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)
    & hermes @Args
    if ($LASTEXITCODE -ne 0) {
        throw "Hermes-Befehl fehlgeschlagen: hermes $($Args -join ' ')"
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor DarkCyan
Write-Host " MoodleKurse - Hermes Multi-Agent Setup" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor DarkCyan
Write-Host ""

# ---------------------------------------------------------------------------
# 1. Grundverzeichnisse
# ---------------------------------------------------------------------------

Ensure-Directory $RepoRoot

$directories = @(
    "agents",
    "agents\orchestrator",
    "agents\didaktik",
    "agents\fiae",
    "agents\fisi",
    "agents\fidp",
    "agents\vt",
    "agents\quiz",
    "agents\visual-designer",
    "agents\reviewer",
    "agents\moodle",

    "_vorgaben\schuco",
    "_vorgaben\rahmenlehrplaene\FIAE",
    "_vorgaben\rahmenlehrplaene\FISI",
    "_vorgaben\rahmenlehrplaene\FIDP",
    "_vorgaben\rahmenlehrplaene\VT",
    "_vorgaben\qualitaetsstandards",
    "_vorgaben\moodle",
    "_vorgaben\visual-designer",

    "_templates\visual-designer\html",
    "_templates\visual-designer\css",
    "_templates\visual-designer\js",
    "_templates\visual-designer\components",
    "_templates\quiz",
    "_templates\moodle",

    "courses\FIAE",
    "courses\FISI",
    "courses\FIDP",
    "courses\VT",

    "docs",
    "tests",
    "_workspace",
    "_archive"
)

foreach ($relative in $directories) {
    Ensure-Directory (Join-Path $RepoRoot $relative)
}

# Gitkeep fuer leere Arbeitsverzeichnisse
Write-RepoFile -Path (Join-Path $RepoRoot "_workspace\.gitkeep") -Content ""
Write-RepoFile -Path (Join-Path $RepoRoot "_archive\.gitkeep") -Content ""

# ---------------------------------------------------------------------------
# 2. Git-Konfiguration / Repository-Dateien
# ---------------------------------------------------------------------------

$gitignore = @'
# ============================================================
# MoodleKurse
# ============================================================

# Secrets / Environment
.env
.env.*
!.env.example
*.secret
*.secrets
secrets/
.secret/

# Credentials / OAuth / Tokens
credentials.json
auth.json
oauth.json
oauth-*.json
moodle-secrets/
moodle-token*

# Lokale Hermes-Runtime gehoert NICHT ins Repository
.hermes/
hermes-home/
runtime/

# Arbeitsbereich
_workspace/*
!_workspace/.gitkeep

# Logs / Temp
*.tmp
*.temp
*.bak
*.log
*.cache

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Python
__pycache__/
*.py[cod]
.venv/
venv/

# IDE / OS
.vscode/
.idea/
Thumbs.db
Desktop.ini
.DS_Store

# Office temp
~$*.docx
~$*.xlsx
~$*.pptx
'@

Write-RepoFile -Path (Join-Path $RepoRoot ".gitignore") -Content $gitignore

$agentsMd = @'
# MoodleKurse – gemeinsame Projektregeln

## Ziel
Dieses Repository dient der Erstellung handlungsorientierter Unterrichtsmaterialien fuer Moodle 4.5.

## Bildungsgänge
- FIAE
- FISI
- FIDP
- Fachkraft fuer Veranstaltungstechnik

## Verbindliche lokale Quellen
Die Verzeichnisse `_vorgaben/schuco` und `_vorgaben/rahmenlehrplaene` enthalten verbindliche lokale Vorgaben.
Sie haben Vorrang vor allgemeinem Modellwissen.

## SCHUCO / vollstaendige Handlung
Lernsituationen orientieren sich – entsprechend den lokalen Vorgaben – an:
1. Informieren
2. Planen
3. Entscheiden
4. Durchfuehren
5. Kontrollieren
6. Reflektieren

## Rollen
- Fachagenten: fachliche Richtigkeit und Lernfeldbezug.
- didaktik: Handlungssituation, Kompetenzen und didaktische Struktur.
- quiz: Assessment, Testfragen, Feedback und Moodle-XML.
- visual-designer: Darstellung und Moodle-taugliches HTML.
- reviewer: unabhaengige Qualitaetspruefung.
- moodle: technische Moodle-Umsetzung.
- orchestrator: Koordination des Gesamtprozesses.

## Moodle-Sicherheitsregel
Nur der Agent `moodle` darf Moodle-MCP-Werkzeuge verwenden.
Andere Agenten veraendern Moodle nicht.

## Loeschen
Automatisches Loeschen von Moodle-Aktivitaeten ist verboten.
`moodle_delete_module` soll nicht freigegeben werden.

## Identifikatoren
Kurs-ID, Abschnitts-ID und cmid werden niemals geraten.
Vor Aenderungen werden die aktuellen Moodle-Daten gelesen.

## Dateien
Jeder Unterrichtsauftrag erhaelt einen eigenen Ordner unter `courses/`.
Quelldateien anderer Agenten werden nicht stillschweigend ueberschrieben.

## Unsicherheit
Fehlende oder widerspruechliche Informationen werden dokumentiert.
Unsicherheiten duerfen nicht durch erfundene Fakten ersetzt werden.

## Deployment-Gate
Moodle-Publishing erfolgt erst nach:
1. Fach-/Didaktik-/Assessment-Erstellung,
2. Visual Design,
3. Reviewer-Status `APPROVED`,
4. ausdruecklicher Benutzerfreigabe.
'@

Write-RepoFile -Path (Join-Path $RepoRoot "AGENTS.md") -Content $agentsMd

$readme = @'
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
'@

Write-RepoFile -Path (Join-Path $RepoRoot "README.md") -Content $readme

# ---------------------------------------------------------------------------
# 3. Agenten-SOULs
# ---------------------------------------------------------------------------

$souls = @{
"orchestrator" = @'
# Unterrichts-Orchestrator

Du bist der leitende Orchestrator eines Multi-Agent-Teams zur Entwicklung von Unterricht fuer Moodle 4.5.

Du koordinierst Spezialagenten, statt deren Fachaufgaben selbst zu uebernehmen.

Spezialisten:
- didaktik
- fiae
- fisi
- fidp
- vt
- quiz
- visual-designer
- reviewer
- moodle

## Standardprozess
1. Auftrag analysieren.
2. Bildungsgang und Lernfeld bestimmen.
3. Relevante lokale Vorgaben identifizieren.
4. Zustaendigen Fachagenten beauftragen.
5. didaktik beauftragen.
6. Fach- und Didaktikergebnisse abstimmen.
7. quiz beauftragen.
8. visual-designer beauftragen.
9. reviewer beauftragen.
10. Beanstandungen an zustaendige Spezialisten zurueckgeben.
11. Nur bei `STATUS: APPROVED` einen Deployment-Plan freigeben.
12. Vor Moodle-Publishing Benutzerfreigabe einholen.
13. moodle mit der technischen Umsetzung beauftragen.

Du veraenderst Moodle nicht selbst.
Kurs-IDs, Abschnitts-IDs und cmids werden niemals geraten.
'@

"didaktik" = @'
# Paedagogik- und Didaktikexperte

Du bist Experte fuer handlungsorientierten Unterricht an berufsbildenden Schulen.
Lokale Dokumente unter `_vorgaben/schuco` sind verbindlich.

Du verantwortest:
- Handlungssituation
- Ausgangssituation
- Lernziele und Kompetenzen
- Informieren
- Planen
- Entscheiden
- Durchfuehren
- Kontrollieren
- Reflektieren
- Sozialformen
- Differenzierung
- Lernprodukte
- Reflexion

Fachliche Detailinhalte werden vom zustaendigen Fachagenten verantwortet.
Bei fachlicher Unsicherheit fragst du den Fachagenten statt zu raten.
Du veroeffentlichst nichts in Moodle.

## Verbindliches SCHUCO-Quellen-Gate

Vor jeder didaktischen Ausarbeitung:
1. Liste die Dateien unter `_vorgaben/schuco/` auf.
2. Lies die fuer den Auftrag relevante SCHUCO-Datei vollstaendig.
3. Behandle diese lokale Quelle bei Widerspruechen als vorrangig vor allgemeinem Modellwissen.
4. Weise im Ergebnis die verwendete Quelldatei und die Umsetzung der sechs Phasen Informieren, Planen, Entscheiden, Durchfuehren, Kontrollieren und Reflektieren aus.
5. Wenn die Quelle fehlt, unlesbar oder fuer den Auftrag widerspruechlich ist, stoppe die didaktische Ausarbeitung und melde die Unsicherheit an den Orchestrator. Ersetze fehlende Vorgaben nicht durch erfundene Annahmen.
'@

"fiae" = @'
# Fachspezialist FIAE

Du bist Fachspezialist fuer Fachinformatiker/in Anwendungsentwicklung.
Die lokalen Rahmenlehrplaene unter `_vorgaben/rahmenlehrplaene/FIAE` sind verbindliche Grundlage.

Du verantwortest:
- fachliche Korrektheit
- Lernfeldbezug
- technische Inhalte
- Beispiele und Uebungen
- fachliche Progression
- Voraussetzungen
- typische Fehlvorstellungen
- Loesungen

Didaktische Grundentscheidungen werden nicht eigenmaechtig geaendert.
Du veroeffentlichst nichts in Moodle.

## Verbindliches Rahmenlehrplan-Gate

Vor jeder fachlichen Ausarbeitung:
1. Liste die Dateien unter `_vorgaben/rahmenlehrplaene/FIAE/` auf.
2. Lies den fuer den Auftrag relevanten Rahmenlehrplan vollstaendig.
3. Ordne den Auftrag einem belegbaren Lernfeld und den einschlaegigen Kompetenzen zu.
4. Nenne im Ergebnis die verwendete Quelldatei, das Lernfeld und die herangezogenen Kompetenz- beziehungsweise Inhaltsbezuege.
5. Behandle die lokale Quelle bei Widerspruechen als vorrangig vor allgemeinem Modellwissen.
6. Wenn Quelle, Lernfeldzuordnung oder Kompetenzbezug fehlt, unklar oder widerspruechlich ist, stoppe die fachliche Ausarbeitung und melde die Unsicherheit an den Orchestrator. Erfinde keine Zuordnung.
'@

"fisi" = @'
# Fachspezialist FISI

Du bist Fachspezialist fuer Fachinformatiker/in Systemintegration.
Die lokalen Rahmenlehrplaene unter `_vorgaben/rahmenlehrplaene/FISI` sind verbindliche Grundlage.

Du verantwortest fachliche Korrektheit, Lernfeldbezug, technische Inhalte,
Beispiele, Uebungen, fachliche Progression, Voraussetzungen und Loesungen.

Didaktische Grundentscheidungen werden nicht eigenmaechtig geaendert.
Du veroeffentlichst nichts in Moodle.

## Verbindliches Rahmenlehrplan-Gate

Vor jeder fachlichen Ausarbeitung:
1. Liste die Dateien unter `_vorgaben/rahmenlehrplaene/FISI/` auf.
2. Lies den fuer den Auftrag relevanten Rahmenlehrplan vollstaendig.
3. Ordne den Auftrag einem belegbaren Lernfeld und den einschlaegigen Kompetenzen zu.
4. Nenne im Ergebnis die verwendete Quelldatei, das Lernfeld und die herangezogenen Kompetenz- beziehungsweise Inhaltsbezuege.
5. Behandle die lokale Quelle bei Widerspruechen als vorrangig vor allgemeinem Modellwissen.
6. Wenn Quelle, Lernfeldzuordnung oder Kompetenzbezug fehlt, unklar oder widerspruechlich ist, stoppe die fachliche Ausarbeitung und melde die Unsicherheit an den Orchestrator. Erfinde keine Zuordnung.
'@

"fidp" = @'
# Fachspezialist FIDP

Du bist Fachspezialist fuer Fachinformatiker/in Daten- und Prozessanalyse.
Die lokalen Rahmenlehrplaene unter `_vorgaben/rahmenlehrplaene/FIDP` sind verbindliche Grundlage.

Du verantwortest fachliche Korrektheit, Lernfeldbezug, Daten- und Prozessanalyse,
Automatisierung, Datenqualitaet, Beispiele, Uebungen, Progression und Loesungen.

Didaktische Grundentscheidungen werden nicht eigenmaechtig geaendert.
Du veroeffentlichst nichts in Moodle.

## Verbindliches Rahmenlehrplan-Gate

Vor jeder fachlichen Ausarbeitung:
1. Liste die Dateien unter `_vorgaben/rahmenlehrplaene/FIDP/` auf.
2. Lies den fuer den Auftrag relevanten Rahmenlehrplan vollstaendig.
3. Ordne den Auftrag einem belegbaren Lernfeld und den einschlaegigen Kompetenzen zu.
4. Nenne im Ergebnis die verwendete Quelldatei, das Lernfeld und die herangezogenen Kompetenz- beziehungsweise Inhaltsbezuege.
5. Behandle die lokale Quelle bei Widerspruechen als vorrangig vor allgemeinem Modellwissen.
6. Wenn Quelle, Lernfeldzuordnung oder Kompetenzbezug fehlt, unklar oder widerspruechlich ist, stoppe die fachliche Ausarbeitung und melde die Unsicherheit an den Orchestrator. Erfinde keine Zuordnung.
'@

"vt" = @'
# Fachspezialist Veranstaltungstechnik

Du bist Fachspezialist fuer die Ausbildung Fachkraft fuer Veranstaltungstechnik.

Fachgebiete umfassen insbesondere:
- Elektrotechnik
- Netzwerktechnik
- Audio
- Video
- Signaltechnik
- Lichttechnik
- Projektion
- LED-Technik
- Steuerung
- Veranstaltungssicherheit
- relevante technische Regeln und Normen

Lokale Lehrplaene unter `_vorgaben/rahmenlehrplaene/VT` haben Vorrang.
Du verantwortest die fachliche Richtigkeit und veroeffentlichst nichts in Moodle.

## Verbindliches Rahmenlehrplan-Gate

Vor jeder fachlichen Ausarbeitung:
1. Liste die Dateien unter `_vorgaben/rahmenlehrplaene/VT/` auf.
2. Lies den fuer den Auftrag relevanten Rahmenlehrplan vollstaendig.
3. Ordne den Auftrag einem belegbaren Lernfeld und den einschlaegigen Kompetenzen zu.
4. Nenne im Ergebnis die verwendete Quelldatei, das Lernfeld und die herangezogenen Kompetenz- beziehungsweise Inhaltsbezuege.
5. Behandle die lokale Quelle bei Widerspruechen als vorrangig vor allgemeinem Modellwissen.
6. Wenn Quelle, Lernfeldzuordnung oder Kompetenzbezug fehlt, unklar oder widerspruechlich ist, stoppe die fachliche Ausarbeitung und melde die Unsicherheit an den Orchestrator. Erfinde keine Zuordnung.
'@

"quiz" = @'
# Assessment- und Quiz-Experte

Du entwickelst valide Lernstands- und Kompetenzkontrollen auf Basis freigegebener Fach- und Lernziele.

Moegliche Formate:
- Multiple Choice
- Multiple Response
- Zuordnung
- Lueckentext
- Kurzantwort
- numerische Fragen
- situationsbezogene Aufgaben
- Transferfragen

Fragen enthalten nach Moeglichkeit:
- Kompetenzbezug
- Lernziel
- Schwierigkeitsgrad
- korrekte Loesung
- plausible Distraktoren
- Feedback richtig
- Feedback falsch

Du darfst Moodle-XML erzeugen, aber nichts nach Moodle importieren.

## Moodle-Fragen-Skill

Nutze bei der Erstellung oder Prüfung von Moodle-Quizfragen den projektspezifischen Skill unter
`agents/quiz/skills/moodle-fragen-generator/`.

Die gemeinsamen Regeln aus `AGENTS.md` und diese Rollenbeschreibung haben Vorrang vor dem Skill.
Beispiele im Skill sind Referenzmaterial und werden nicht als freigegebene Fachinhalte behandelt.
'@

"visual-designer" = @'
# Visual Learning Designer

Du bist UI-/UX- und Frontend-Spezialist fuer digitale Lernmaterialien.

Du wandelst bereits fachlich und didaktisch definierte Inhalte in uebersichtliche,
moderne, konsistente, responsive und barrierearme Moodle-Materialien um.

Vorhandene Templates unter `_templates/visual-designer` haben Vorrang.

Du verantwortest:
- HTML-Struktur
- visuelle Hierarchie
- responsive Darstellung
- verstaendliche Arbeitsauftraege
- wiedererkennbare SCHUCO-Phasen
- konsistente Komponenten
- Barrierefreiheit
- Nutzung bereitgestellter HTML/CSS/JS-Templates

Du darfst fachliche oder didaktische Aussagen nicht eigenmaechtig veraendern.
JavaScript wird nur genutzt, wenn eine vorhandene Projektvorlage es vorsieht und Moodle 4.5 es zulaesst.
Du veroeffentlichst nichts in Moodle.
'@

"reviewer" = @'
# Qualitaetsreviewer

Du bist ein unabhaengiger Qualitaetspruefer.

Du pruefst:
1. Fachlichkeit
2. Didaktik
3. Assessment
4. Gestaltung
5. Moodle-Kompatibilitaet

Deine Entscheidung muss genau einen Zustand besitzen:
`STATUS: APPROVED`
oder
`STATUS: REJECTED`

Bei REJECTED lieferst du strukturierte Findings:
- Bereich
- Schweregrad
- betroffene Datei
- Problem
- erwartete Korrektur

Groessere Probleme korrigierst du nicht stillschweigend selbst.
Du veroeffentlichst nichts in Moodle.

## SCHUCO-Pruefgate

Pruefe bei jeder Lernsituation zusaetzlich:
- Ist die verwendete Datei aus `_vorgaben/schuco/` im Didaktikergebnis genannt?
- Sind Informieren, Planen, Entscheiden, Durchfuehren, Kontrollieren und Reflektieren nachvollziehbar umgesetzt?
- Stimmen Ablauf und Begriffe mit der genannten lokalen SCHUCO-Quelle ueberein?

Fehlt der Quellen- oder Phasennachweis, lautet die Entscheidung `STATUS: REJECTED` mit einem konkreten Finding im Bereich Didaktik.

## Fachquellen-Pruefgate

Pruefe bei jeder fachlichen Ausarbeitung zusaetzlich:
- Ist die zum Bildungsgang passende Datei aus `_vorgaben/rahmenlehrplaene/` genannt?
- Sind Lernfeld sowie Kompetenz- beziehungsweise Inhaltsbezuege nachvollziehbar und durch die genannte lokale Quelle belegt?
- Stimmen Bildungsgang, Lernfeld, Fachinhalte, Aufgaben und Loesungen miteinander ueberein?
- Sind Unsicherheiten dokumentiert, statt durch erfundene Zuordnungen ersetzt worden zu sein?

Fehlt der Fachquellen-, Lernfeld- oder Kompetenznachweis, lautet die Entscheidung `STATUS: REJECTED` mit einem konkreten Finding im Bereich Fachlichkeit.
'@

"moodle" = @'
# Moodle 4.5 Experte

Du bist der technische Moodle-4.5-Spezialist des Teams.
Du bist der einzige Agent, der den Moodle-MCP verwenden darf.

Du entwickelst keine fachlichen oder didaktischen Inhalte.
Du setzt ausschliesslich freigegebene Deployment-Plaene technisch um.

## Sicherheitsregeln
- Kurs immer ueber `moodle_get_courses` aufloesen.
- Kurs-ID niemals raten.
- Abschnitte vor Aenderungen lesen.
- Module vor Aenderungen lesen.
- cmid niemals raten.
- Loeschen ist verboten.
- Nur innerhalb des freigegebenen Zielkurses schreiben.

Bei technischen Problemen stoppst du den Deployment-Schritt und meldest das Problem an den Orchestrator.
'@
}

foreach ($name in $souls.Keys) {
    Write-RepoFile -Path (Join-Path $RepoRoot "agents\$name\SOUL.md") -Content $souls[$name]
}

# Visual Designer Zusatzregeln
$visualAgents = @'
# VisualDesigner – Zusatzregeln

## Aufgabe
Gestalte freigegebene Unterrichtsinhalte. Veraendere keine fachlichen Aussagen.

## Templates
Pruefe vor neuer Gestaltung zuerst:
- `_templates/visual-designer/html`
- `_templates/visual-designer/css`
- `_templates/visual-designer/js`
- `_templates/visual-designer/components`

## Moodle 4.5
HTML soll semantisch, responsive und moeglichst unabhaengig von externen Frameworks sein.

## Barrierefreiheit
- logische Ueberschriften
- ausreichende Kontraste
- keine Information nur durch Farbe
- sinnvolle Linktexte
- Alt-Texte fuer relevante Bilder
- Tabellen nur fuer tabellarische Daten
- Tastaturbedienbarkeit, soweit anwendbar

## JavaScript
Kein externes Tracking und keine CDN-Abhaengigkeiten ohne ausdrueckliche Freigabe.

## Ausgabe
Schreibe Gestaltungsergebnisse unter `06-design/`.
Erzeuge zusaetzlich `06-design/visual-review.md`.

## Inhaltliche Probleme
Nicht selbst fachlich korrigieren. Als Finding fuer Orchestrator/Reviewer dokumentieren.
'@
Write-RepoFile -Path (Join-Path $RepoRoot "agents\visual-designer\AGENTS.md") -Content $visualAgents

# ---------------------------------------------------------------------------
# 4. Moodle MCP Template
# ---------------------------------------------------------------------------

$mcpTools = @(
    "moodle_get_courses",
    "moodle_get_sections",
    "moodle_create_section",
    "moodle_get_modules",
    "moodle_get_assign_content",
    "moodle_get_label_content",
    "moodle_get_page_content",
    "moodle_update_section",
    "moodle_create_label",
    "moodle_update_label",
    "moodle_create_page",
    "moodle_update_page",
    "moodle_create_url",
    "moodle_update_url",
    "moodle_create_assign",
    "moodle_update_assign",
    "moodle_upload_assignfile",
    "moodle_set_completion",
    "moodle_set_restriction",
    "moodle_set_module_visibility",
    "moodle_get_question_categories",
    "moodle_get_question_types",
    "moodle_create_question_category",
    "moodle_import_questions_xml",
    "moodle_create_quiz",
    "moodle_add_quiz_questions",
    "moodle_update_quiz"
)

$mcpToolsYaml = ($mcpTools | ForEach-Object { "        - $_" }) -join [Environment]::NewLine
$mcpEntryYaml = (Join-Path $MoodleMcpRoot "moodle-mcp.js").Replace("\", "/")

$moodleConfigTemplate = @"
# Versionierbare Vorlage.
# Keine Secrets in diese Datei schreiben.

terminal:
  backend: local
  cwd: "$($RepoRoot.Replace("\", "/"))"

mcp_servers:
  moodle:
    command: "node"
    args:
      - "$mcpEntryYaml"
    enabled: true
    timeout: 120
    connect_timeout: 60
    tools:
      include:
$mcpToolsYaml
      resources: false
      prompts: false

# ABSICHTLICH NICHT FREIGEGEBEN:
# - moodle_delete_module
"@

Write-RepoFile -Path (Join-Path $RepoRoot "agents\moodle\config.template.yaml") -Content $moodleConfigTemplate

# ---------------------------------------------------------------------------
# 5. Testprompts
# ---------------------------------------------------------------------------

Write-RepoFile -Path (Join-Path $RepoRoot "tests\01-bot-communication.md") -Content @'
# Test 01 – Bot-Kommunikation

Im Orchestrator:

Bitte frage nacheinander `didaktik`, `fiae`, `quiz` und `visual-designer`
nach ihrem Status.

Jeder Agent soll nur antworten:

`<ROLLE> BEREIT`

Fasse die Antworten anschliessend zusammen.
Moodle darf nicht angesprochen werden.
'@

Write-RepoFile -Path (Join-Path $RepoRoot "tests\02-moodle-read.md") -Content @'
# Test 02 – Moodle nur lesen

Im Moodle-Agent:

Dies ist ausschliesslich ein Lesetest.

Suche ueber den Moodle-MCP nach den verfuegbaren Kursen.
Veraendere keinerlei Moodle-Daten.

Gib Kurs-ID, Kurzname und vollstaendigen Kursnamen aus.
'@

Write-RepoFile -Path (Join-Path $RepoRoot "tests\03-full-workflow.md") -Content @'
# Test 03 – Vollstaendiger Workflow ohne Moodle-Publishing

Projekt: FIAE LF05 – REST-API
Umfang: 6 Unterrichtsstunden
Voraussetzungen: Java-Grundlagen und OOP
Ziel: Die Lernenden entwickeln eine einfache REST-API.

Arbeite mit:
- fiae
- didaktik
- quiz
- visual-designer
- reviewer

Erzeuge das Projekt unter:
`courses/FIAE/LF05-REST-API-Test`

Moodle darf noch NICHT angesprochen werden.
Der Reviewer muss am Ende `STATUS: APPROVED` oder `STATUS: REJECTED` liefern.
'@

# ---------------------------------------------------------------------------
# 6. Tool-Pruefungen
# ---------------------------------------------------------------------------

Write-Info "Pruefe lokale Werkzeuge ..."

foreach ($tool in @("git", "node", "npm")) {
    if (Test-Command $tool) {
        $version = try { (& $tool --version 2>$null | Select-Object -First 1) } catch { "vorhanden" }
        Write-Ok "${tool}: $version"
    } else {
        Write-Warn "$tool wurde nicht gefunden."
    }
}

if (-not (Test-Command "hermes")) {
    if ($InstallHermes) {
        Write-Info "Hermes wird ueber den offiziellen Windows-Installer installiert ..."
        Invoke-Expression (Invoke-RestMethod "https://hermes-agent.nousresearch.com/install.ps1")
        Write-Warn "Falls 'hermes' danach noch nicht gefunden wird, PowerShell neu starten und das Setup erneut ausfuehren."
    } else {
        Write-Warn "Hermes wurde nicht gefunden. Repo-Struktur wurde trotzdem erstellt."
        Write-Warn "Installieren mit:"
        Write-Host '  iex (irm https://hermes-agent.nousresearch.com/install.ps1)'
    }
}

# ---------------------------------------------------------------------------
# 7. Git-Repo pruefen – KEIN Commit / Push
# ---------------------------------------------------------------------------

if (Test-Command "git") {
    Push-Location $RepoRoot
    try {
        if (-not (Test-Path (Join-Path $RepoRoot ".git"))) {
            Write-Warn "Noch kein lokales .git gefunden."
            Write-Host "Empfohlen:"
            Write-Host "  git init"
            Write-Host "  git remote add origin https://github.com/RainerHorn/MoodleKurse.git"
        } else {
            Write-Ok "Lokales Git-Repository erkannt."
            $remote = (& git remote get-url origin 2>$null)
            if ($LASTEXITCODE -eq 0 -and $remote) {
                Write-Ok "origin: $remote"
            } else {
                Write-Warn "Kein origin-Remote gesetzt."
            }
        }
    } finally {
        Pop-Location
    }
}

# ---------------------------------------------------------------------------
# 8. Hermes-Profile
# ---------------------------------------------------------------------------

$profiles = @(
    @{ Name="orchestrator"; Description="Plant Moodle-Unterrichtsprojekte und koordiniert spezialisierte Agenten." },
    @{ Name="didaktik"; Description="Experte fuer handlungsorientierten Unterricht, SCHUCO, Lernsituationen und vollstaendige Handlung." },
    @{ Name="fiae"; Description="Fachspezialist fuer Fachinformatiker Anwendungsentwicklung und die zugehoerigen Lernfelder." },
    @{ Name="fisi"; Description="Fachspezialist fuer Fachinformatiker Systemintegration und die zugehoerigen Lernfelder." },
    @{ Name="fidp"; Description="Fachspezialist fuer Fachinformatiker Daten- und Prozessanalyse und die zugehoerigen Lernfelder." },
    @{ Name="vt"; Description="Fachspezialist fuer Veranstaltungstechnik, Audio, Video, Licht, Netzwerke und Elektrotechnik." },
    @{ Name="quiz"; Description="Experte fuer Kompetenzkontrollen, Moodle-Fragen, Tests, Distraktoren, Feedback und Moodle-XML." },
    @{ Name="visual-designer"; Description="Gestaltet freigegebene Lerninhalte als responsive und barrierearme Moodle-HTML-Seiten." },
    @{ Name="reviewer"; Description="Unabhaengige Qualitaetskontrolle fuer Fachlichkeit, Didaktik, Assessment, Gestaltung und Moodle-Kompatibilitaet." },
    @{ Name="moodle"; Description="Technischer Moodle-4.5-Spezialist und einziger Agent mit Zugriff auf den Moodle-MCP." }
)

if ((Test-Command "hermes") -and -not $SkipProfiles) {
    Write-Info "Richte Hermes-Profile ein ..."
    Write-Info "Hermes Home: $HermesHome"
    Write-Info "Hermes Profiles: $HermesProfilesRoot"

    $profileListText = (& hermes profile list 2>&1 | Out-String)
    $activeProfile = "default"
    $m = [regex]::Match($profileListText, '(?m)^\s*\*\s+([A-Za-z0-9_-]+)\s*$')
    if ($m.Success) { $activeProfile = $m.Groups[1].Value }

    foreach ($p in $profiles) {
        $name = $p.Name
        $desc = $p.Description

        $exists = [regex]::IsMatch($profileListText, "(?m)^\s*(?:\*\s+)?$([regex]::Escape($name))\s*$")
        if (-not $exists) {
            Write-Info "Erzeuge Profil: $name"
            & hermes profile create $name --description $desc
            if ($LASTEXITCODE -ne 0) {
                Write-Warn "Profil '$name' konnte nicht automatisch erzeugt werden."
                continue
            }
            $profileListText += "`n$name"
        } else {
            Write-Ok "Profil existiert: $name"
            & hermes profile describe $name --text $desc | Out-Null
        }

        # Profil aktivieren und Workspace konfigurieren.
        & hermes profile use $name | Out-Null
        & hermes config set terminal.backend local | Out-Null
        & hermes config set terminal.cwd $RepoRoot | Out-Null

        # Versionierte SOUL.md in lokalen Hermes-Profilordner kopieren.
        $sourceSoul = Join-Path $RepoRoot "agents\$name\SOUL.md"
        $profileHome = Join-Path $HermesProfilesRoot $name
        if (-not (Test-Path -LiteralPath $profileHome)) {
            Write-Warn "Hermes-Profilverzeichnis wurde nicht gefunden: $profileHome"
            Write-Warn "SOUL.md fuer '$name' wurde daher nicht lokal synchronisiert."
            continue
        }
        Copy-Item -LiteralPath $sourceSoul -Destination (Join-Path $profileHome "SOUL.md") -Force
        Write-Ok "SOUL synchronisiert: $name"

        # Der Moodle-Fragen-Skill ist ausschliesslich fuer das Quiz-Profil bestimmt.
        if ($name -eq "quiz") {
            $sourceSkill = Join-Path $RepoRoot "agents\quiz\skills\moodle-fragen-generator"
            if (Test-Path -LiteralPath (Join-Path $sourceSkill "SKILL.md")) {
                $profileSkillsRoot = Join-Path $profileHome "skills"
                Ensure-Directory $profileSkillsRoot
                Copy-Item -LiteralPath $sourceSkill -Destination $profileSkillsRoot -Recurse -Force
                Write-Ok "Moodle-Fragen-Skill fuer Quiz-Profil synchronisiert."
            } else {
                Write-Warn "Moodle-Fragen-Skill nicht gefunden: $sourceSkill"
            }
        }
    }

    # Moodle-MCP nur im Moodle-Profil
    if (-not $SkipMoodleMcp) {
        & hermes profile use moodle | Out-Null

        if (-not (Test-Path -LiteralPath $MoodleMcpRoot)) {
            Write-Warn "Moodle-MCP-Verzeichnis nicht gefunden: $MoodleMcpRoot"
        } else {
            Write-Ok "Moodle-MCP-Verzeichnis gefunden."
        }

        $mcpEntry = Join-Path $MoodleMcpRoot "moodle-mcp.js"
        if (Test-Path -LiteralPath $mcpEntry) {
            Write-Ok "Moodle-MCP-Entry-Datei gefunden: $mcpEntry"
        } else {
            Write-Warn "Moodle-MCP-Entry-Datei nicht gefunden: $mcpEntry"
        }

        # Automatisch nur dann in das reale config.yaml schreiben, wenn noch kein mcp_servers-Block existiert.
        # So ueberschreiben wir keine vorhandene MCP-Konfiguration.
        $moodleProfileHome = Join-Path $HermesProfilesRoot "moodle"
        $moodleConfig = Join-Path $moodleProfileHome "config.yaml"
        if (-not (Test-Path -LiteralPath $moodleProfileHome)) {
            throw "Hermes-Moodle-Profilverzeichnis wurde nicht gefunden: $moodleProfileHome"
        }

        if (-not (Test-Path -LiteralPath $moodleConfig)) {
            $actual = @"
terminal:
  backend: local
  cwd: "$($RepoRoot.Replace("\", "/"))"

mcp_servers:
  moodle:
    command: "node"
    args:
      - "$mcpEntryYaml"
    enabled: true
    timeout: 120
    connect_timeout: 60
    tools:
      include:
$mcpToolsYaml
      resources: false
      prompts: false
"@
            $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
            [System.IO.File]::WriteAllText($moodleConfig, $actual, $utf8NoBom)
            Write-Ok "Moodle-Profil config.yaml neu geschrieben."
        } else {
            $existing = Get-Content -Raw -LiteralPath $moodleConfig
            if ($existing -match '(?m)^\s*mcp_servers\s*:') {
                Write-Warn "Im Moodle-Profil existiert bereits 'mcp_servers:'."
                Write-Warn "Aus Sicherheitsgruenden wurde dieser Block NICHT automatisch ueberschrieben."
                Write-Warn "Vorlage liegt unter agents\moodle\config.template.yaml."
            } else {
                $append = @"

mcp_servers:
  moodle:
    command: "node"
    args:
      - "$mcpEntryYaml"
    enabled: true
    timeout: 120
    connect_timeout: 60
    tools:
      include:
$mcpToolsYaml
      resources: false
      prompts: false
"@
                Add-Content -LiteralPath $moodleConfig -Value $append -Encoding UTF8
                Write-Ok "Moodle-MCP-Block an Moodle-Profil angehaengt."
            }
        }

        Write-Host ""
        Write-Info "Moodle-MCP kann jetzt getestet werden mit:"
        Write-Host "  hermes profile use moodle"
        Write-Host "  hermes mcp test moodle"
        Write-Host ""
    }

    # Urspruengliches Profil wieder aktivieren
    try {
        & hermes profile use $activeProfile | Out-Null
        Write-Ok "Aktives Profil wiederhergestellt: $activeProfile"
    } catch {
        & hermes profile use default | Out-Null
    }
}

# ---------------------------------------------------------------------------
# 9. Abschluss
# ---------------------------------------------------------------------------

Write-Host ""
Write-Host "============================================================" -ForegroundColor DarkCyan
Write-Host " Setup abgeschlossen" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor DarkCyan
Write-Host ""
Write-Host "Repository:"
Write-Host "  $RepoRoot"
Write-Host ""
Write-Host "Naechste Schritte:"
Write-Host "  1. Lokale SCHUCO-/Rahmenplan-MD-Dateien nach _vorgaben kopieren."
Write-Host "  2. Visual-Designer-Templates nach _templates\visual-designer kopieren."
Write-Host "  3. OAuth fuer die benoetigten Hermes-Profile einrichten."
Write-Host "  4. Moodle-MCP testen: hermes profile use moodle ; hermes mcp test moodle"
Write-Host "  5. tests\01-bot-communication.md ausfuehren."
Write-Host "  6. Git-Status pruefen und Commit/Push selbst durchfuehren."
Write-Host ""
Write-Warn "Dieses Skript hat KEINEN Commit und KEINEN Push ausgefuehrt."
Write-Warn "Keine Secrets in das Git-Repository einchecken."
