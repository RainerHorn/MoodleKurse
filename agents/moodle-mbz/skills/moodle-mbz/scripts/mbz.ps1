<#
.SYNOPSIS
  Erzeugt aus einer kursplan.json eine Moodle-4.5-Sicherung (.mbz) auf Kurs- oder Abschnittsebene,
  prüft sie statisch und stellt sie zur Probe in einem lokalen Moodle (Docker) wieder her.

.PARAMETER Plan
  Pfad zur kursplan.json. Der Ordner der Datei ist der Quellordner (HTML, Fragen-XML, Dateien).

.PARAMETER Modus
  kurs (Standard) oder abschnitt.

.PARAMETER Abschnitt
  Bei -Modus abschnitt: Abschnitts-id aus dem Plan oder "alle" (eine .mbz je Abschnitt).

.PARAMETER Ziel
  Nur Abschnittsmodus, nur für die Probe: neu (als eigener Kurs wiederherstellen),
  bestehend (in einen vorhandenen Kurs einfügen), beide (Standard).

.PARAMETER ZielNummer
  Nur bei einem einzelnen Abschnitt: Nummer des Abschnitts im Zielkurs. Beim Einfügen in einen bestehenden
  Kurs landen die Aktivitäten im gleichnummerierten Abschnitt (Standard: Position im Plan).

.PARAMETER Ausgabe
  Zielordner für die .mbz (Standard: <Quellordner>\mbz).

.PARAMETER OhneProbe
  Nur bauen und statisch prüfen, keine Wiederherstellung.

.EXAMPLE
  .\mbz.ps1 -Plan C:\Kurse\java\kursplan.json
  .\mbz.ps1 -Plan C:\Kurse\java\kursplan.json -Modus abschnitt -Abschnitt k01 -Ziel bestehend
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Plan,
    [ValidateSet('kurs', 'abschnitt')][string]$Modus = 'kurs',
    [string]$Abschnitt = '',
    [ValidateSet('neu', 'bestehend', 'beide')][string]$Ziel = 'beide',
    [int]$ZielNummer = 0,
    [string]$Ausgabe = '',
    [string]$KursKurz = '',
    [switch]$OhneProbe
)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$utf8 = New-Object System.Text.UTF8Encoding($false)

$skill = Split-Path $PSScriptRoot
$dockerDir = Join-Path $skill 'docker'
$work = Join-Path $dockerDir 'work'
$plan = (Resolve-Path $Plan).Path
$quelle = Split-Path $plan
if (-not $Ausgabe) { $Ausgabe = Join-Path $quelle 'mbz' }
if ($Modus -eq 'abschnitt' -and -not $Abschnitt) { throw 'Bei -Modus abschnitt ist -Abschnitt <id|alle> nötig.' }
if ($Modus -eq 'kurs') { $Abschnitt = ''; $ZielNummer = 0 }
if ($ZielNummer -gt 0 -and $Abschnitt -eq 'alle') { throw '-ZielNummer geht nur mit einer einzelnen Abschnitts-id.' }
$adminPass = if ($env:MBZ_ADMIN_PASS) { $env:MBZ_ADMIN_PASS } else { 'Mbz-Admin#2026x' }

function Schritt($t) { Write-Host "`n== $t" -ForegroundColor Cyan }
function Docker-Php($skriptArgs, $umgebung = @{}) {
    $a = @('exec'); foreach ($k in $umgebung.Keys) { $a += @('-e', "$k=$($umgebung[$k])") }
    $a += @('mbz-moodle', 'php') + $skriptArgs
    $aus = & docker @a 2>&1
    if ($LASTEXITCODE -ne 0) { Write-Host ($aus -join "`n"); throw "php $($skriptArgs[0]) fehlgeschlagen (Exit $LASTEXITCODE)" }
    return $aus
}

# 1. Quellen in den Arbeitsordner kopieren und Zeilenenden vereinheitlichen (Originale bleiben unverändert)
Schritt '1/6 Quellen kopieren, Zeilenenden auf LF/UTF-8 vereinheitlichen'
New-Item -ItemType Directory -Force $work | Out-Null
foreach ($d in 'export', 'out', 'scripts') { Remove-Item (Join-Path $work $d) -Recurse -Force -ErrorAction SilentlyContinue }
New-Item -ItemType Directory -Force (Join-Path $work 'out'), (Join-Path $work 'scripts') | Out-Null
robocopy $quelle (Join-Path $work 'export') /E /XD mbz .git node_modules /XF *.mbz /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy fehlgeschlagen ($LASTEXITCODE)" }
$global:LASTEXITCODE = 0
Copy-Item (Join-Path $PSScriptRoot '*.php') (Join-Path $work 'scripts')
python (Join-Path $PSScriptRoot 'eol.py') normalisieren (Join-Path $work 'export')
if ($LASTEXITCODE -ne 0) { throw 'eol.py fehlgeschlagen' }
python (Join-Path $PSScriptRoot 'eol.py') pruefen (Join-Path $work 'export') | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Nach der Normalisierung sind noch Abweichungen vorhanden' }
foreach ($f in Get-ChildItem (Join-Path $work 'scripts') -Filter *.php) {  # PHP-Skripte ebenfalls LF
    [System.IO.File]::WriteAllText($f.FullName, ([System.IO.File]::ReadAllText($f.FullName)).Replace("`r`n", "`n"), $utf8)
}

# 2. Moodle starten
Schritt '2/6 Moodle-Container starten'
docker info *> $null
if ($LASTEXITCODE -ne 0) { throw 'Docker läuft nicht. Docker Desktop starten.' }
docker compose -f (Join-Path $dockerDir 'docker-compose.yml') up -d
if ($LASTEXITCODE -ne 0) { throw 'docker compose up fehlgeschlagen' }
for ($i = 0; $i -lt 60; $i++) {
    $r = docker exec mbz-db mariadb -umoodleuser -pmoodlepass -e 'select 1' moodle 2>&1
    if ($r -match '1') { break }
    Start-Sleep 3
}
$tab = docker exec mbz-db mariadb -umoodleuser -pmoodlepass moodle -N -e "select count(*) from information_schema.tables where table_schema='moodle' and table_name='mdl_config'"
if ($tab -notmatch '1') {
    Write-Host 'Erste Installation von Moodle (dauert einige Minuten)...'
    Docker-Php @('/var/www/html/admin/cli/install_database.php', '--lang=en', '--adminuser=admin', "--adminpass=$adminPass", '--adminemail=admin@example.com', '--fullname=MBZ', '--shortname=MBZ', '--agree-license') | Out-Null
}

# Zusatz-Plugins (z. B. qtype_ddmatch, qtype_coderunner) installieren, falls noch nicht vorhanden.
# Quellen: Ordner aus $env:MBZ_PLUGIN_DIR (z. B. gemeinsamer Plugin-Ordner), skills\moodle-fragen-generator\plugins (falls vorhanden) und docker\plugins (nur lokal).
# Dateiname: <typ>_<name>[_<Versionsnummer>].zip (Marktplatz-Name genügt); der Ordner im Zip darf <name> oder <typ>_<name> heißen.
# Vor der Installation wird "requires" aus version.php mit dem Test-Moodle verglichen; Unpassendes wird übersprungen.
$pluginDirs = @((Join-Path (Split-Path $skill) 'moodle-fragen-generator\plugins'), (Join-Path $dockerDir 'plugins'))
if ($env:MBZ_PLUGIN_DIR) { $pluginDirs = @($env:MBZ_PLUGIN_DIR) + $pluginDirs }
$verzeichnisse = @{ qtype = 'question/type'; qbehaviour = 'question/behaviour'; qformat = 'question/format'; mod = 'mod'; local = 'local'; block = 'blocks'; filter = 'filter'; tool = 'admin/tool' }
$neuPlugin = $false
$moodleVersion = [int](([regex]::Match((docker exec mbz-moodle grep -E '^\$version' /var/www/html/version.php), '(\d{10})')).Groups[1].Value)
Add-Type -AssemblyName System.IO.Compression.FileSystem
foreach ($pluginDir in $pluginDirs) {
    if (-not (Test-Path $pluginDir)) { continue }
    foreach ($z in Get-ChildItem $pluginDir -Filter *.zip) {
        if ($z.BaseName -notmatch '^([a-z]+)_(\w+?)(?:_\d{10})?$' -or -not $verzeichnisse.ContainsKey($Matches[1])) { Write-Warning "Plugin-Zip $($z.Name): Name muss <typ>_<name>[_<version>].zip sein (typ: $($verzeichnisse.Keys -join ', '))"; continue }
        $typ = $Matches[1]; $pname = $Matches[2]; $pfadZiel = "/var/www/html/$($verzeichnisse[$typ])"
        docker exec mbz-moodle test -d "$pfadZiel/$pname"
        if ($LASTEXITCODE -eq 0) { continue }
        $arch = [System.IO.Compression.ZipFile]::OpenRead($z.FullName)
        try {
            $vp = $arch.Entries | Where-Object { $_.FullName -match '^[^/]+/version\.php$' } | Select-Object -First 1
            if (-not $vp) { Write-Warning "Plugin-Zip $($z.Name): keine version.php im obersten Ordner, übersprungen"; continue }
            $sr = New-Object System.IO.StreamReader($vp.Open()); $vtext = $sr.ReadToEnd(); $sr.Close()
        } finally { $arch.Dispose() }
        $req = [regex]::Match($vtext, '\$plugin->requires\s*=\s*(\d+)').Groups[1].Value
        if ($req -and [int64]$req -gt $moodleVersion) {
            Write-Warning "Plugin $($z.Name) verlangt Moodle-Version $req, das Test-Moodle hat $moodleVersion (4.5.4): übersprungen. Zip für Moodle 4.5 beschaffen."
            continue
        }
        Write-Host "Installiere Plugin $($z.BaseName) ..."
        docker cp $z.FullName "mbz-moodle:/tmp/plugin.zip" | Out-Null
        docker exec mbz-moodle sh -c "rm -rf /tmp/plug && mkdir /tmp/plug && unzip -q -o /tmp/plugin.zip -d /tmp/plug && d=`$(ls /tmp/plug | head -1) && rm -rf $pfadZiel/$pname && mv /tmp/plug/`$d $pfadZiel/$pname && chown -R www-data:www-data $pfadZiel/$pname && rm -rf /tmp/plug /tmp/plugin.zip"
        docker exec mbz-moodle test -d "$pfadZiel/$pname"
        if ($LASTEXITCODE -ne 0) { throw "Plugin $($z.Name) liegt nach dem Entpacken nicht unter $pfadZiel/$pname" }
        $neuPlugin = $true
    }
}
$global:LASTEXITCODE = 0
if ($neuPlugin) { Write-Host 'Plugins aktualisieren (upgrade.php) ...'; Docker-Php @('/var/www/html/admin/cli/upgrade.php', '--non-interactive') | Out-Null }
# 3. Kurs bauen und sichern
Schritt "3/6 Kurs bauen und sichern (Modus $Modus$(if ($Abschnitt) { ", Abschnitt $Abschnitt" }))"
$umg = @{ MBZ_PLAN = '/work/export/' + (Split-Path $plan -Leaf); MBZ_MODUS = $Modus; MBZ_ABSCHNITT = $Abschnitt; MBZ_ZIELNUMMER = $ZielNummer }
if ($KursKurz) { $umg.KURSKURZ = $KursKurz }
$aus = Docker-Php @('/work/scripts/bau.php') $umg
$aus | Select-String 'Kurs |Fragen|MBZ:|KURSID|Bewertung|WARNUNG' | ForEach-Object { Write-Host $_.Line }
$mbzs = @(Get-ChildItem (Join-Path $work 'out') -Filter *.mbz)
if ($mbzs.Count -eq 0) { throw 'Es wurde keine .mbz erzeugt' }
New-Item -ItemType Directory -Force $Ausgabe | Out-Null
foreach ($m in $mbzs) { Copy-Item $m.FullName $Ausgabe -Force }

# 4. Statische Prüfung
Schritt '4/6 Statische Prüfung der .mbz (CR, Deklaration, Prüfsummen)'
$bad = 0
foreach ($m in $mbzs) {
    python (Join-Path $PSScriptRoot 'check_mbz.py') (Join-Path $Ausgabe $m.Name)
    if ($LASTEXITCODE -ne 0) { $bad++ }
}
if ($bad) { throw "Statische Prüfung fehlgeschlagen ($bad Datei(en))" }

# 5./6. Probe-Wiederherstellung und Vergleich mit dem Plan
if ($OhneProbe) { Write-Host "`nFertig (ohne Probe): $Ausgabe"; return }
$probleme = 0
foreach ($m in $mbzs) {
    $id = ''
    if ($m.Name -match '_abschnitt_(.+)\.mbz$') { $id = $Matches[1] }
    $ziele = if ($Modus -eq 'kurs') { @('neu') } elseif ($Ziel -eq 'beide') { @('neu', 'bestehend') } else { @($Ziel) }
    foreach ($z in $ziele) {
        Schritt "5/6 Probe: $($m.Name) wiederherstellen ($z)"
        $r = Docker-Php @('/work/scripts/restore.php', "/work/out/$($m.Name)", $z) @{ MBZ_ZIELNUMMER = $ZielNummer }
        $kid = [regex]::Match(($r -join "`n"), 'RESTORED=(\d+)').Groups[1].Value
        if (-not $kid) { throw "Wiederherstellung ($z) fehlgeschlagen: $($r -join ' ')" }
        Schritt "6/6 Vergleich mit dem Plan (Kurs $kid)"
        $pa = @('/work/scripts/pruef.php', $kid, $(if ($id) { $id } else { 'alle' }))
        if ($z -eq 'bestehend' -and $ZielNummer -gt 0) { $pa += $ZielNummer }
        elseif ($z -eq 'bestehend') {
            $ids = @((Get-Content $plan -Raw | ConvertFrom-Json).abschnitte | Where-Object { $_ } | ForEach-Object { $_.id })
            $pa += $(if ($ids.Count -eq 0) { 1 } else { [array]::IndexOf($ids, $id) + 1 })
        }
        $p = Docker-Php $pa @{ MBZ_PLAN = $umg.MBZ_PLAN }
        $p | ForEach-Object { Write-Host $_ }
        if (($p | Select-String '^FEHLER ' -CaseSensitive).Count -gt 0) { $probleme++ }
    }
}
if ($probleme) { throw "Probe: $probleme Prüfung(en) mit Fehlern" }
Write-Host "`nFertig. MBZ in: $Ausgabe" -ForegroundColor Green
Get-ChildItem $Ausgabe -Filter *.mbz | ForEach-Object { Write-Host ("  {0} ({1} KB)" -f $_.Name, [math]::Round($_.Length / 1KB)) }

