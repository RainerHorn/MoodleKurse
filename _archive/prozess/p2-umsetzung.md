# Umsetzung P2 – 2026-11-03

Beauftragt mit „dann weiter mit der nächsten Priorität“. IMP-13 bis IMP-16 sind
als Regeln und lokale Werkzeuge umgesetzt. IMP-17 ist vorbereitet, der empirische
Rollenvergleich bleibt mangels vergleichbarer echter Kursläufe offen.

## Änderungen und Grenzen

| Aufgabe | Umsetzung |
|---|---|
| IMP-13 | Zentraler Produktionsablauf trennt Plattformaufträge von Kursen; Plattformvorlage, Komponentenregister und Kursbindung mit Version/Hash/Nachweis. |
| IMP-14 | Gemeinsamer XML-Transport und Link-Build mit reinem Prüfmodus. Vorhandener Prüf-Runner und Statusvalidator im Katalog. Komponentenwahl statt automatischer Vollausstattung. |
| IMP-15 | 1.053 Zeilen eingebettetes Setup durch kleinen Abgleich-Einstieg ersetzt; Repository-Dateien sind Pflegequelle. Vorschau, explizite Auswahl, Hashprüfung, einmalige Sicherung. MCP-Sollvorlage aktualisiert und lesender Teilumfang-Audit ergänzt. |
| IMP-16 | Zwei parallele Phasen mit Rahmenabstimmung, getrennten Schreibpfaden, Integrationsbarriere und Wiederaufnahme bei Bot-Ausfall definiert. Kompakter Abhängigkeitsplan. |
| IMP-17 | Messvorlage und Entscheidungskriterien vorbereitet. Keine Modelländerung oder behauptete Beschleunigung; Vergleich bleibt offen. |

Gemeinsame Werkzeuge dokumentiert in `docs/gemeinsame-werkzeuge.md`.
Keine Moodle-Aufrufe, keine Änderungen an Kursartefakten, keine Neuvergabe von
Reviewer- oder Benutzerfreigaben. Die großen Rigging-Builder bleiben erhalten:
Ihre Fach-/Simulator-/DOCX-/Schutzlogik ist kursbezogen. Gemeinsame Stufen sind
ohne Kopieren für weitere Kurse nutzbar; keine vorgetäuschte vollständige
Verallgemeinerung des Gesamtbuilders.

## Gezielte Abnahme

`python -m unittest discover -s tests -p test_p2_tools.py -v`: acht Tests bestanden.
Sie prüfen Kategorieentnahme mit CRLF/CDATA/Leerformen und DTD-Ablehnung,
Link-Zielbindung/fehlplatzierten Platzhalter, begrenzte Konfigurationsauswertung,
Vorschau ohne Übernahme, Sicherungserhalt, veraltete Pläne, Pfadabweichungen und
Gesamtvorprüfung vor dem ersten Schreiben. Der reale Fixturefall vergleicht die
vorhandene Quiz-Importfassung und alle acht Rigging-Seiten mit den im Speicher
erzeugten Ergebnissen: byteidentisch, ohne Ausgaben zu schreiben.

Der erste Testlauf konnte die temporären Profil-Testverzeichnisse wegen der
Sandbox nicht beschreiben. Derselbe Lauf bestand nach Ausführungsfreigabe.
Keine vollständige Kurs-/Browser-/Serverabnahme wiederholt. Vorhandene P0/P1-
Prüfer wurden nicht verändert; ihre bisherigen Nachweise bleiben zugeordnet.

## Konfiguration und Synchronisierung

Profilvorschau: 62 verwaltete Dateien, 61 identisch und nur der in P2 geänderte
Orchestrator abweichend. Zielinhalt vor Übernahme geprüft; genau diese eine Datei
über den hashgebundenen Plan synchronisiert. Bestehende `.bak` erhalten.
Neue Sitzungen laden den neuen Stand; laufender Session-Reload ist nicht belegt.
Nicht verwaltete Zusatzdateien werden nicht gelöscht. Modelle und persönliche
Profilkonfigurationen wurden nicht überschrieben.

Lesender Konfigurationsaudit: command, MCP-Skriptpfad, tools.include und
terminal.cwd stimmen zwischen Vorlage und vorhandenem Moodle-Profil überein.
In den untersuchten anderen Profilkonfigurationen keine Moodle-Serverdeklaration
oder Referenz auf `moodle-mcp.js` gefunden. Dies ist ein begrenzter Dateiabgleich,
keine Aussage über sämtliche denkbaren MCP-Aliase oder effektiv laufende Prozesse.
Secrets werden weder kopiert noch ausgegeben.

Lokaler Plugin-Quellstand erklärt Release 1.7.0 / Build 2026103102. Historische
Kurskopien können abweichen. Register kennzeichnet diesen Befund als SOURCE_ONLY:
Versionsdatei und Adapterhash beweisen weder Serverinstallation noch Abnahme.

## Noch zu messen

Vorhandene P0-Messung umfasst einen lokalen Rechenkernlauf (etwa 0,24 s) und
Nachweiswiederverwendung (etwa 0,12 s). Das sind keine Rollen-/Modelllaufzeiten.
Beim nächsten beauftragten Kurs Durchlaufzeit, menschliche Wartezeit, Tools,
Korrekturen und Qualitätsbefund aus vorhandenen Protokollen erfassen. Erst bei
verbleibendem modellbezogenem Engpass vergleichbare Rollenläufe planen.
IMP-17 bleibt hierfür sichtbar offen; neue Kursproduktion ist nicht mitbeauftragt.
