# Hermes: Repository und Profile abgleichen

Die vier Fach-SOULs (`fiae`, `fisi`, `fidp`, `vt`) entstehen aus
`agents/_shared/fach/` (Vorlage und `rollen.json`); dort ändern, dann
`python scripts/build_fach_souls.py --write`. Ohne `--write` vergleicht das
Skript nur.

Pflegequellen sind `agents/<Rolle>/SOUL.md`, die zugehörigen `skills/`, die für alle
Rollen gemeinsamen Skills unter `agents/_shared/skills/` (der Abgleich verteilt sie
in jedes Profil; im Repository gibt es davon keine Rollenkopien) sowie
`agents/moodle-mcp/config.template.yaml` für die nicht geheimen Moodle-MCP-Sollwerte
(`agents/moodle-mbz/config.template.yaml` enthält bewusst keinen MCP).
Der Komponentenstand steht in `platform/components.json`; Serverabnahme bleibt
ein eigener Nachweis. Modellwahl, Zugangsdaten und weitere persönliche Einstellungen
liegen ausschließlich in lokalen Profilen. Rollen lesen AGENTS und die zentralen
Prozessregeln aus dem gemeinsamen Repository.

Das Standardprofil `hermes` liegt nicht unter `profiles/`, sondern direkt in
`%LOCALAPPDATA%/hermes`; der Abgleich erfasst es nicht. Seine Regeln für die
Kursproduktion stehen in `agents/_shared/hermes/SOUL.md`. Diesen Text von Hand
in `%LOCALAPPDATA%/hermes/SOUL.md` übernehmen (als Abschnitt, falls dort schon
anderes steht) und den Skill `agents/_shared/skills/moodle-agent-control-plane`
nach `%LOCALAPPDATA%/hermes/skills/` kopieren. Danach eine neue Sitzung starten.
Wer Kurse nur direkt im Orchestrator-Chat beauftragt, braucht diesen Schritt nicht.

`setup-hermes.ps1` erzeugt keine Projekttexte mehr. Standard ist ein lesender
Abgleich aller vorhandenen Repository-Rollen und Skills mit den Profilen:

```powershell
.\setup-hermes.ps1 | Set-Content -Encoding utf8 _workspace/profile-plan.json
```

Profilwurzel: `HERMES_HOME/profiles`, sonst `%LOCALAPPDATA%/hermes/profiles`.
Abweichende Installation mit `-ProfilesRoot <Pfad>` angeben. Plan nennt Dateien,
Quell-/Zielhash und SAME/DIFF/MISSING. Jeder Unterschied startet mit `keep`.
Nur geprüfte Einträge auf `decision: replace` setzen; fremde Ergänzungen vorher
in der Pflegequelle zusammenführen. Dann denselben Plan anwenden:

```powershell
.\setup-hermes.ps1 -ApplyPlan _workspace/profile-plan.json
```

Alle Planpfade und Hashes werden vor dem ersten Schreiben geprüft. Geänderte
Quellen/Ziele verlangen eine neue Vorschau. Es gibt keine Löschungen. Vorhandene
Dateien erhalten einmalig `.bak`; bestehende Sicherungen bleiben erhalten und
werden nicht als Skillressourcen kopiert. Die Übernahme ist pro Datei, keine
Transaktion über alle Profile; nach Unterbrechung neu abgleichen. Neue Sitzungen
starten, damit Anweisungen neu geladen werden. Dateigleichheit beweist keinen
Reload bereits laufender Unterhaltungen.

Neue Hermes-Installation/Profile separat mit der lokal verfügbaren Hermes-CLI
einrichten (`hermes --help`, `hermes profile --help`); anschließend diesen Abgleich
verwenden. Fehlende Profile werden nicht als bloße Verzeichnisse angelegt.
Die alten Optionen `-InstallHermes`, `-ForceRepoFiles`, `-MoodleMcpRoot` und
`-SkipMoodleMcp` brechen mit Erklärung ab. `-SkipProfiles` bleibt ein No-op.
Kein Remote-Installationsskript und keine automatische Änderung der aktiven Auswahl.

Es gibt zwei Moodle-Rollen und damit zwei Profile: `moodle-mcp` (ehemals `moodle`) und
`moodle-mbz`. Das bisherige Profil `moodle` wird nicht automatisch umbenannt. Neue Profile
`moodle-mcp` und `moodle-mbz` mit der Hermes-CLI anlegen (bzw. das alte Profil dorthin
übernehmen), `terminal.cwd` setzen und beim Profil `moodle-mcp` die MCP-Konfiguration
samt Zugangsdaten aus dem alten Profil übernehmen; erst danach das alte Profil entfernen.
Bis dahin meldet `config_audit.py` ein weiteres Profil mit Moodle-MCP als Abweichung.

### Pflichtschritte beim Umbenennen eines Profils

Am Beispiel `moodle` → `moodle-mcp` (erprobt am 15.11.2026). Bot-zu-Bot-Nachrichten
landen immer im kanonischen „Bot Chat“ des Zielprofils. Dieser Chat stammt noch
aus dem alten Profil und muss deshalb zweimal angepasst werden.

1. **Identität migrieren:** `hermes profile migrate-identity <alt> <neu>`
   (hier `hermes profile migrate-identity moodle moodle-mcp`; idempotent).
   Ohne diesen Schritt behalten bestehende Sessions die alte Route `agent:<alt>:…`.
   Symptom: `profiles/<neu>/logs/gateway.log` zeigt
   `receipt refused: ValueError: route mismatch`, der Absender meldet
   `Could not check <neu>'s Bot Chat registry (storage_unavailable)`.

2. **Alten Bot Chat archivieren:** `migrate-identity` schreibt die Route um, aber
   nicht die eingefrorenen Zugangsdaten des Chats. Sie bleiben an das alte
   Profilverzeichnis gebunden. Symptom: Die Nachricht kommt an, bricht aber mit
   `api_calls=0` ab, und es erscheint
   `launch_credentials_unavailable (home: the frozen config credentials belong to another home)`
   oder `(profile: …)`. Ein Modellwechsel hilft nicht. `/new` hilft in der App auch
   nicht, denn dort wird ein Bot Chat nur verdichtet. Die App zeigt kanonische Bot
   Chats nicht in der Seitenleiste, und `hermes sessions archive` lässt sie
   absichtlich aus. Deshalb über den Gateway archivieren. Das ist derselbe Aufruf,
   den die App verwendet:

   ```powershell
   $venv = (Get-ChildItem "$env:LOCALAPPDATA\hermes\installs\*\environments\*\venv\Scripts\python.exe" | Select-Object -First 1).FullName
   $env:HERMES_HOME = "$env:LOCALAPPDATA\hermes\profiles\<neu>"
   @'
   import sys, asyncio, sqlite3, os, uuid
   sys.path.insert(0, os.path.expandvars(r"%LOCALAPPDATA%\hermes\hermes-agent"))
   db = sqlite3.connect(os.path.join(os.environ["HERMES_HOME"], "state.db"))
   sid, rev = db.execute("select id, runtime_revision from sessions where title='Bot Chat'").fetchone()
   db.close()
   from hermes_cli.gateway_client import connect_gateway
   async def main():
       async with connect_gateway() as cl:
           print(await cl.rpc("session.mutate", session_id=sid, request_id="archive-" + uuid.uuid4().hex,
                              expected_revision=rev, operation="archive", payload={"archived": True}))
   asyncio.run(main())
   '@ | & $venv -
   Remove-Item Env:HERMES_HOME
   ```

   Gibt es mehrere Hermes-Umgebungen, für `$venv` die Umgebung nehmen, die
   `hermes doctor` unter „Runtime venv“ als aktiv nennt.
   Erwartet wird eine Antwort mit `"archived": true`. Danach gibt es keine Session
   mehr mit dem Titel „Bot Chat“. Die nächste Bot-Nachricht legt automatisch einen
   neuen Bot Chat an, der an das neue Profil gebunden ist. Der alte Verlauf bleibt
   als archivierte Unterhaltung erhalten und wird nicht gelöscht. Falls die App den
   alten Chat noch anzeigt, die App neu starten.

3. **Nacharbeiten:** Mit `python scripts/config_audit.py` prüfen. Agenten-Handles
   in Profil-Skills (`@<alt>`) unter `%LOCALAPPDATA%\hermes\profiles\*\skills`
   auf den neuen Namen umstellen.

4. **Testen:** Ein Fehlversuch an einen Bot verbraucht trotzdem einen Hop von
   `gateway.bot_loop_guard.max_hops`. Den Test deshalb mit einer eigenen
   Benutzernachricht im Orchestrator-Chat neu starten, nicht über `hermes`, oder
   10 Minuten Ruhe abwarten. `max_hops` nicht erhöhen. Erfolgreich ist der Test,
   wenn im Log des Zielprofils eine neue `chat=local-…`-ID mit `api_calls` ≥ 1
   steht.

Neu angelegte Profile (wie `moodle-mbz`) brauchen diese Schritte nicht.

Moodle-MCP-Konfiguration mit `python scripts/config_audit.py` lesend abgleichen
(Standardprofil `moodle-mcp`, anderes mit `--profile <Name>`).
Das Werkzeug versteht bewusst nur die einfache Blockstruktur der hiesigen
Konfiguration, gibt keine env-/Tokenwerte aus und meldet unklare Syntax als Fehler.
Es ersetzt keinen allgemeinen YAML-Parser. Es schreibt keine Konfigurationen.
MCP nur für `moodle-mcp`, nicht für `moodle-mbz`; Löschwerkzeug bleibt ausgeschlossen. Bei Drift gezielt
die Sollwerte übernehmen, niemals die gesamte Profildatei durch die Vorlage ersetzen.
`terminal.cwd` bei neuen Profilen explizit auf dieses Repository setzen.
