# Anleitung: moodle-mbz

## Wofür?
Erzeugt aus einem Kursplan (`kursplan.json` plus HTML-Seiten, Fragen-XML und Dateien) eine Moodle-4.5-Sicherung (`.mbz`) für einen ganzen Kurs oder für einzelne Abschnitte. Das ist der Standardweg des Projekts (`moodle-mcp` nur nach ausdrücklichem Wechsel): Ein lokales Moodle im Docker-Container baut den Kurs und sichert ihn; Sie stellen die `.mbz` in Ihrer Moodle über *Wiederherstellen* ein.

## Wann wird der Skill ausgelöst?
Bei „MBZ erstellen“, „Kurs/Abschnitt als Sicherung zum Hochladen“, „Abschnitt in bestehenden Kurs einfügen“. Das Überarbeiten einer vorhandenen `.mbz` gehört nicht zu diesem Skill.

## Inhalt dieses Ordners
- `SKILL.md` – Ablauf, Rückfragen, Regeln für Zeilenenden
- `scripts/mbz.ps1` – Einstieg (baut, prüft, probiert)
- `scripts/bau.php`, `plan.php`, `restore.php`, `pruef.php` – laufen im Container
- `scripts/stage.py` – Quellen bytegleich unter den Plan-Ordner kopieren und gegen `quelle-manifest.json` prüfen
- `scripts/eol.py` – Zeilenenden und Kodierung vereinheitlichen
- `scripts/check_mbz.py` – statische Prüfung einer `.mbz` (auch einzeln nutzbar)
- `docker/docker-compose.yml` – Moodle 4.5.4 und MariaDB, nur localhost
- `docker/plugins/` – lokale Zusatz-Plugins als `<typ>_<name>.zip` (werden automatisch installiert, nicht eingecheckt); weitere Ordner: `MBZ_PLUGIN_DIR` (Umgebungsvariable) und, falls vorhanden, `skills/moodle-fragen-generator/plugins/`
- `references/kursplan-format.md` – Format der `kursplan.json`
- `beispiel/` – kleiner Beispielkurs mit zwei Abschnitten

## Voraussetzungen
Docker Desktop, Python 3 im Pfad, PowerShell 7 (`pwsh`, nicht Windows PowerShell 5.1; Grund in `SKILL.md`). Erster Lauf lädt die Images und installiert Moodle (einige Minuten, danach in Sekunden bis wenigen Minuten pro Kurs). Optional `MBZ_ADMIN_PASS` setzen.

## Ablauf in vier Schritten
1. Quellordner vorbereiten: `kursplan.json` und die Dateien, auf die sie verweist (siehe `references/kursplan-format.md`).
2. Starten, z. B. ganzer Kurs: `scripts\mbz.ps1 -Plan C:\Kurse\java\kursplan.json`
3. Bei Abschnitten entscheiden Sie (der Skill fragt nach):
   - **Ebene:** eine Abschnitts-id oder `alle`.
   - **Weg A, neu:** Die Abschnitts-MBZ wird als eigener Kurs wiederhergestellt.
   - **Weg B, bestehend:** Die Abschnitts-MBZ wird in einen vorhandenen Kurs eingefügt. Die Aktivitäten landen im gleichnummerierten Abschnitt des Zielkurses; die Nummer geben Sie mit `-ZielNummer` an.
4. Ergebnis in `<Quellordner>\mbz\`. In Moodle: Kurs → *Wiederherstellen* → Datei hochladen → „Als neuen Kurs“ oder „In bestehenden Kurs einfügen“.

## Zeilenenden (CR/LF)
Alles wird als UTF-8 ohne BOM mit LF verarbeitet. Das Skript normalisiert eine Arbeitskopie der Quellen, prüft nach dem Bau jede XML-Datei der `.mbz` auf CR und bricht bei einem Fund ab. Das Repo erzwingt LF über `.gitattributes`. Eigene Skripte unter Windows nicht mit `Set-Content` ohne Kodierung schreiben (siehe `SKILL.md`).

## Beispielaufrufe
> Erstelle aus kursplan.json im Ordner java/ eine MBZ für den ganzen Kurs.

> Erzeuge aus java/kursplan.json den Abschnitt k03 als MBZ, ich füge ihn als Abschnitt 4 in einen bestehenden Kurs ein.

## Bekannte Grenzen
Welche Aktivitätsarten und Fragetypen (Kern und Plugins wie `ddmatch`, `coderunner`) der Bau unterstützt, steht ausschließlich in `platform/mbz-capabilities.json`. Ein fehlendes Plugin als Zip nach `docker/plugins/` oder in den Ordner aus `MBZ_PLUGIN_DIR` legen. Eine `.mbz` aus Moodle 4.5 lässt sich in 4.5 und neuer einspielen, nicht in ältere Versionen.