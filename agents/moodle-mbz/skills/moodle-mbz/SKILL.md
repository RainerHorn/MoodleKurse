---
name: moodle-mbz
description: Erzeugt aus einem Kursplan (kursplan.json mit HTML-Seiten, Fragen-XML, Dateien) eine Moodle-4.5-Sicherung (.mbz) auf Kurs- oder Abschnittsebene, schnell und ohne Moodle-MCP. Ein lokales Moodle im Docker-Container (mbzbau) baut den Kurs mit der eigenen API und sichert ihn; danach folgen statische Prüfung (Zeilenenden, Prüfsummen) und Probe-Wiederherstellung. Auslösen bei: „MBZ erstellen“, „Kurs/Abschnitt als Sicherung“, „zum Hochladen/Wiederherstellen in Moodle“, „schneller als MCP“, „Abschnitt in bestehenden Kurs einfügen“. Nicht für das Überarbeiten einer vorhandenen .mbz (dafür RefurbishMoodle).
---

# moodle-mbz

Aktueller Kursweg des Benutzers: **ausschliesslich MBZ**, kein Moodle-MCP und keine direkten Änderungen an der Schul-Moodle. Ein **lokales Moodle 4.5** (Docker, Projekt `mbzbau`) baut den Kurs und erzeugt die `.mbz` mit Moodles eigener Sicherungsfunktion. Formale Gültigkeit erst nach statischer Prüfung, Probe-Wiederherstellung und Planvergleich behaupten; Kompatibilität, Rechte und Lernendensicht in der Schul-Moodle sind damit nicht belegt. Die Lehrkraft stellt die `.mbz` dort selbst über *Wiederherstellen* ein. MBZ ist der Standard und wird nicht je Kurs neu abgefragt; der Ablauf steht in `docs/mbz-workflow.md`. Der aktuelle Stand von Image, Aktivitätsarten und Fragetyp-Plugins steht in `platform/mbz-capabilities.json`; diese Datei ist bei Abweichungen von den Angaben unten maßgeblich.

Arbeitssprache Deutsch. Ergebnisse als Dateien, Kurzbericht im Chat.

## Agentensteuerung

Vor den technischen Schritten gilt `../moodle-agent-control-plane/SKILL.md`:
Bau- und Pruefauftraege kommen vom Orchestrator, Ergebnisse gehen an ihn
zurueck, und die MBZ-Rolle beauftragt keine weiteren Rollen. Wo dieser Skill
unten "nachfragen" oder "dem Nutzer berichten" sagt, heisst das in einer
orchestrierten Kursproduktion: an den Orchestrator melden. Direkt mit dem
Nutzer spricht der Skill nur bei einem Einzelauftrag ausserhalb davon.

## Eingaben

- Ein Ordner mit `kursplan.json` und allen Quellen (HTML-Seiten von `material`/`aufgaben`, Fragen-XML von `moodle-fragen-generator`, Dateien). Format: `references/kursplan-format.md`, Beispiel: `beispiel/`.
- Docker Desktop läuft. Python 3 im Pfad. Erster Lauf installiert Moodle einmalig (einige Minuten).

## Vor dem Start immer klären (nachfragen, nicht raten)

1. **Ebene:** ganzer **Kurs** oder einzelner **Abschnitt** (eine Abschnitts-id oder `alle` = eine .mbz je Abschnitt)?
2. Bei Abschnitt: **Zielweg**. Beide Wege werden unterstützt, der Nutzer wählt den aktuellen:
   - **A – neu:** Die Abschnitts-MBZ wird als eigener, neuer Kurs wiederhergestellt (Sammelkurs oder Testkurs; Abschnitte später von Hand verschieben).
   - **B – bestehend:** Die Abschnitts-MBZ wird in einen **bestehenden Kurs eingefügt** (*Wiederherstellen → In bestehenden Kurs einfügen*, nichts löschen).
   - Beim Weg B die **Abschnittsnummer im Zielkurs** erfragen (`-ZielNummer`). Beobachtung im Test mit `restore_controller` (Moodle 4.5.4), **in der Schul-Moodle 4.5 bestätigt** (2026-11-12, Kapitel 1.3 per Wiederherstellen in Abschnitt 2 eingefügt, alles angekommen): Die Aktivitäten landen im **gleichnummerierten Abschnitt** des Zielkurses; Hat der Zielabschnitt bereits einen Namen, bleibt dieser erhalten; ist er **unbenannt und leer** (Moodle zeigt dann „Abschnitt N“), übernimmt er Namen und Zusammenfassung (Banner) aus der MBZ (beides im Test beobachtet). „Abschnitt N“ ist die Standardanzeige für **Abschnittsnummer N**; die Nummer lässt sich in der Moodle-URL prüfen (`course/view.php?id=…&section=N`). Ohne `-ZielNummer` gilt die Position des Abschnitts im Plan.
3. Mit `-ZielNummer` wird nur der eine Abschnitt gebaut, ohne Bewertungsstruktur; ein `{{LINK:id}}` auf einen anderen Abschnitt bricht dann mit Fehlermeldung ab. Ohne `-ZielNummer` (Abschnittsmodus) bekommt ein Link in einen anderen Abschnitt eine WARNUNG, weil er in der Abschnitts-MBZ ins Leere zeigt. Dem Nutzer das vorher sagen.

## Ablauf

```powershell
# ganzer Kurs
scripts\mbz.ps1 -Plan <ordner>\kursplan.json

# ein Abschnitt, Weg A und B probeweise prüfen (Standard -Ziel beide)
scripts\mbz.ps1 -Plan <ordner>\kursplan.json -Modus abschnitt -Abschnitt a1

# ein Abschnitt für den Einsatz in bestehendem Kurs, Zielabschnitt Nr. 3
scripts\mbz.ps1 -Plan <ordner>\kursplan.json -Modus abschnitt -Abschnitt a1 -Ziel bestehend -ZielNummer 3

# alle Abschnitte als einzelne .mbz
scripts\mbz.ps1 -Plan <ordner>\kursplan.json -Modus abschnitt -Abschnitt alle
```

Das Skript führt sechs Schritte aus und bricht beim ersten Fehler ab:
1. Quellen in den Arbeitsordner **kopieren** (Originale bleiben unberührt) und **Zeilenenden vereinheitlichen** (`scripts/eol.py`).
2. Container `mbz-moodle` und `mbz-db` starten (`docker/docker-compose.yml`, nur localhost).
3. `scripts/bau.php`: Kurs mit Moodles API bauen, Fragen importieren, Bewertung setzen, sichern (Kurs oder Abschnitt).
4. **Statische Prüfung** `scripts/check_mbz.py`: kein CR in XML, Deklaration exakt, BOM, wohlgeformt, Prüfsummen der Dateien.
5. **Probe-Wiederherstellung** `scripts/restore.php` (neu und/oder bestehend).
6. **Vergleich mit dem Plan** `scripts/pruef.php` (Typ, Name, Sichtbarkeit, Textlängen, Fragenanzahl, Dateitypen, Bewertung).

Ergebnis: `<Quellordner>\mbz\*.mbz` (oder `-Ausgabe`). Einen lokalen **Testbau** klar von der finalen `.mbz`-Übergabe trennen; letztere erst nach aktuellem Artefakt-APPROVED (in einer Kursproduktion ohne weitere Benutzerfreigabe, siehe Deployment-Gate in `AGENTS.md`). Dem Nutzer Pfad, vollständigen SHA-256, Größe und die Prüfergebnisse berichten, bei Abschnitten auch, welcher Zielweg geprüft wurde. Das Bauprotokoll nennt den Planstand und den SHA-256 der `.mbz`; keine Hashlisten je Quelldatei pflegen. Fragen-Kategorie, verknüpfte Quizslots, Punkte, Zeitlimit, Versuche und Sichtbarkeit im lokalen Prüfnachweis abgleichen. Sind Quiz-Review-Einstellungen nicht wirksam und überprüfbar gesetzt, das Quiz in der Sicherung `sichtbar: false` belassen und die Lehrkraft-Prüfung nach Wiederherstellung als offenes Gate ausweisen.

## Zeilenenden (CR/LF), verbindliche Regeln

Frühere Probleme kamen von CRLF in XML-Dateien einer `.mbz` und von Windows-Editoren. Deshalb:

- **Alles UTF-8 ohne BOM, LF.** `eol.py normalisieren` wandelt CRLF und einzelnes CR in LF und entfernt BOM, nur im Arbeitskopie-Ordner. `pruefen` meldet Abweichungen. Binärdateien werden nie angefasst.
- `bau.php` normalisiert beim Einlesen ein zweites Mal; die MBZ-XML schreibt Moodle selbst (kein ElementTree, keine eigene XML-Serialisierung).
- `check_mbz.py` lässt die MBZ durchfallen, wenn irgendeine XML-Datei ein CR enthält. Dateien der Lernenden (HTML, TXT in `files/`) erzeugen nur einen Hinweis.
- Dateien schreiben (PowerShell): nie `Set-Content`/`Out-File` ohne Kodierungsangabe; stattdessen `[System.IO.File]::WriteAllText($pfad, $text, (New-Object System.Text.UTF8Encoding($false)))`. In Python `write_text(..., encoding="utf-8", newline="\n")`.
- Das Repo erzwingt LF über `.gitattributes`. Skripte mit CRLF brechen im Linux-Container (`bash\r`).
- Müssen CR in Fragen bewusst erhalten bleiben (z. B. Coderunner-Testfälle), gehören sie als `&#13;` in die Fragen-XML; das ist nicht automatisiert und im Bericht zu erwähnen.

## Grenzen und Hinweise

- Unterstützte Arten: `label`, `page`, `url`, `file`, `assign` (Dateiabgabe, optional Onlinetext), `quiz` (aus Moodle-XML), dazu Abschlussverfolgung, Zugriffsbeschränkung nach Abschluss, Einrückung und eine reine Fragensammlung. Dazu `workshop` (Peer-Review mit Bewertungsstrategie „Punkte pro Kriterium“; startet in der Vorbereitungsphase, Phasen schaltet die Lehrkraft in Moodle; Bewertungskriterien je als Punkte, keine Skalen). **Nicht unterstützt:** Forum, Lektion, H5P und andere Workshop-Strategien. Enthält die Vorlage so etwas, dem Nutzer vor dem Bau sagen, was fehlt (und was dadurch ungeschützt würde, z. B. eine Lösung, die nach einer fehlenden Aktivität freigeschaltet werden soll: bis dahin `sichtbar: false` setzen).
- HTML-Seiten, die komplette Dokumente mit eigenem CSS/JS sind (z. B. die Lernmaterialien), gehören als `file` (HTML-Datei als Kursdatei) in den Plan, nicht als `page`: Moodle bereinigt Seitentext beim Wiederherstellen je nach Berechtigung.
- **Quiz-Prüfungsoptionen (Feedbackschutz) sind nicht plan-steuerbar:** `bau.php` setzt fest: Antworten, Feedback, Richtig/Falsch, Punkte nur „während des Versuchs“ verborgen, „direkt nach“, „später“ und „nach Schließen“ sichtbar; `timeopen/timeclose` = 0. Fordert ein Blueprint gesperrte Rückmeldungen bis zum Testende, in der Machbarkeit als UNAVAILABLE melden. Zwei Wege nennen: `bau.php` erweitern (nur auf Auftrag) oder die Lehrkraft stellt die Optionen nach dem Wiederherstellen von Hand ein; bis dahin Quiz `sichtbar: false`.
- **Machbarkeitsprüfung (read-only) ohne Bau:** `docker ps`, Image-ID (`docker inspect mbz-moodle`), Release per `docker exec mbz-moodle sh -c "grep -E '^.release' /var/www/html/version.php"`, Fragetypen/Aktivitäten per `ls` in `question/type` und `mod`, Toolhashes der `scripts/*`. Quell-HTML auf CRLF, `<html/head/body>`, script/style/img und Inline-Styles prüfen (Fragmente ohne eigenes CSS/JS dürfen `page` sein; Bereinigung in der Schul-Moodle bleibt UNKNOWN, Lehrkraft prüft). Ergebnis nach `<Kursordner>/moodle-mbz/machbarkeit.json` (Vorlage `_templates/prozess/machbarkeit.json`; Status VERIFIED/UNAVAILABLE/UNKNOWN). Die MCP-Vorprüfung `moodle/machbarkeit.json` ist kein MBZ-Nachweis. Keine mehrzeiligen Python-Heredocs im bash-Tool (Quoting bricht); JSON direkt mit `write_file` schreiben.
- Fragetypen müssen im lokalen Moodle installiert sein: Kern-Typen ja; den Stand von `ddmatch` und `coderunner` nennt `platform/mbz-capabilities.json` (bei geändertem Image per `ls question/type` neu prüfen und die Datei aktualisieren). Fehlt ein Plugin, bricht der Fragenimport mit „Question type ddmatch is not supported by XML import“ ab. Lösung: das Plugin-Zip aus dem Moodle-Plugin-Verzeichnis (Anmeldung nötig, Version für 4.5) als `qtype_ddmatch[_<Version>].zip` in `docker/plugins/` dieses Skills (lokal, nicht eingecheckt) oder in einen Ordner ablegen, den die Umgebungsvariable `MBZ_PLUGIN_DIR` nennt; `skills/moodle-fragen-generator/plugins/` wird zusätzlich gelesen, falls dieser Ordner neben dem Skill liegt. `mbz.ps1` installiert es beim nächsten Lauf. Der Installer prüft `requires` gegen das Test-Moodle und überspringt unpassende Zips mit Warnung. Getestet mit Coderunner und `ddmatch` 2.5.4 (installiert, Fragen bleiben vom Typ ddmatch); `ddmatch` 2.6.0 verlangt Moodle 5.0 und wird übersprungen. Niemals stillschweigend auf den Kernfragetyp `match` umstellen: das ändert die Fragen.
- Das Image ist Moodle **4.5.4**. Eine `.mbz` lässt sich in gleiche oder neuere Versionen einspielen, in ältere meist nicht.
- Der Container ist ein Werkzeug ohne echte Daten. Admin-Passwort aus `MBZ_ADMIN_PASS` (Standard nur für lokale Entwicklung), Port nur auf `127.0.0.1`.
- Links `{{LINK:id}}` in Aufgabentexten und Seiten werden nach dem Bau durch Moodle-Links ersetzt; Moodle ordnet Links auf Aktivitäten **innerhalb derselben MBZ** beim Wiederherstellen neu zu (im Test mit Kurs-MBZ bestätigt).
- Der Baukurs wird vor jedem Lauf gelöscht (gleicher Kurzname). Probekurse (`PROBE…`, `MBZ-ZIEL`) bleiben im lokalen Container liegen und sind unkritisch.
