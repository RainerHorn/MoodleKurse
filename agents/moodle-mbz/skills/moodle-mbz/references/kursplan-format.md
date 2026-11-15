# Format der kursplan.json (Version 2)

Die Datei liegt im Quellordner; alle Pfade darin sind relativ zu diesem Ordner und verwenden `/`.
Zeichensatz UTF-8, Zeilenenden egal (werden beim Bau auf LF vereinheitlicht).
Ein lauffähiges Beispiel steht in `beispiel/`.

```json
{
  "version": 2,
  "kurs": {"name": "...", "kurzname": "KURZ-1", "zusammenfassung": "<p>...</p>", "format": "topics"},
  "abschnitte": [
    {
      "id": "a1",
      "name": "1 Einführung",
      "zusammenfassung": "<p>...</p>",
      "zusammenfassung_datei": "seiten/abschnitt1.html",
      "aktivitaeten": [ { ... } ]
    }
  ],
  "bewertung": { ... }
}
```

| Feld | Pflicht | Bedeutung |
|---|---|---|
| `kurs.name`, `kurs.kurzname` | ja | Voller Name, Kurzname des Baukurses (Kurzname wird in Dateinamen verwendet) |
| `kurs.zusammenfassung`, `kurs.format` | nein | HTML-Text, Kursformat (Standard `topics`) |
| `kurs.fragensammlung` | nein | Liste von Moodle-XML-Dateien, die nur in die Fragensammlung des Kurses importiert werden (ohne Test-Aktivität) |
| `abschnitte[].id` | ja | Nur `A-Z a-z 0-9 _ -`, eindeutig; wird zum Wählen eines Abschnitts verwendet |
| `abschnitte[].name` | ja | Abschnittsname in Moodle |
| `abschnitte[].zusammenfassung` oder `zusammenfassung_datei` | nein | HTML direkt oder aus Datei |

Die Reihenfolge der Abschnitte ist die Abschnittsnummer im gebauten Kurs (erster Abschnitt = Nummer 1; Nummer 0 ist der Allgemeine Bereich).

## Aktivitäten

Gemeinsame Felder: `id` (Pflicht, im ganzen Plan eindeutig; in einer Kursproduktion die ID aus der Aktivitätenliste in `RAHMEN.md`), `art` (Pflicht), `name` (Pflicht), `sichtbar` (true/false),
`beschreibung` (Datei mit HTML-Beschreibung), `beschreibung_anzeigen` (true: Beschreibung auf der Kursseite zeigen),
`einrueckung` (0 bis 16, Einrückung auf der Kursseite), `abschluss` und `voraussetzung` (siehe unten).

### Abschluss und Zugriffsbeschränkung

| Feld | Werte | Wirkung |
|---|---|---|
| `abschluss` | `keiner` (Standard), `ansicht` (Aktivität ansehen), `abgabe` (nur `assign`: Abgabe), `manuell` | Abschlussverfolgung der Aktivität; sobald irgendeine Aktivität einen Abschluss hat, wird sie für den Kurs eingeschaltet |
| `voraussetzung` | Liste von Aktivitäts-ids | Aktivität ist erst nach **Abschluss** aller genannten Aktivitäten zugänglich (und bis dahin sichtbar, aber gesperrt). Die genannten Aktivitäten brauchen einen `abschluss` |

Typisch: Abgabe mit `abschluss: abgabe`, Lösung mit `voraussetzung: [<abgabe-id>]`.

| `art` | Quelle | `einstellungen` |
|---|---|---|
| `label` | `quelle`: HTML-Datei (Text und Medien auf der Kursseite) | – |
| `page` | `quelle`: HTML-Datei (Seiteninhalt) | – |
| `url` | – | `url` (Pflicht) |
| `file` | `quelle`: beliebige Datei (wird als Kursdatei hochgeladen) | – |
| `assign` | `beschreibung` = Aufgabentext | `max_dateien` (3), `max_groesse_mb` (10), `erlaubte_dateitypen` (Liste wie `[".java", ".pdf"]`), `online_text` (false), `punkte` (100) |
| `quiz` | `quelle`: Moodle-XML-Datei (Format von `moodle-fragen-generator`) | `zeitlimit_min` (0 = unbegrenzt), `versuche` (0 = unbegrenzt), `antworten_mischen`, `verhalten` (Standard `deferredfeedback`; z. B. `interactive` = mehrere Versuche mit sofortiger Rückmeldung), `bewertung_punkte` (Höchstnote, Standard 100; 0 = ohne Note, z. B. Selbsttest) |

Links zu anderen Aktivitäten: In Seiten- und Aufgabentexten `{{LINK:<aktivitäts-id>}}` schreiben. Der Bau ersetzt das durch einen Link mit dem Namen der Aktivität.
Links auf Aktivitäten **in einem anderen Abschnitt** funktionieren nur im Kurs-MBZ. Dasselbe gilt für `voraussetzung` über Abschnittsgrenzen.

### Workshop (`art: workshop`)

Peer-Review-Workshop mit der Strategie „Punkte pro Kriterium“ (`accumulative`). Er beginnt in der **Vorbereitungsphase**; die Phasen schaltet die Lehrkraft in Moodle.

| Feld | Bedeutung |
|---|---|
| `beschreibung` | HTML-Datei, Einleitung |
| `anleitung_autoren`, `anleitung_gutachter` | HTML-Dateien: Anleitung für Abgebende und für Beurteilende; Bilder darin als `@@PLUGINFILE@@/<dateiname>` |
| `dateien_autoren`, `dateien_gutachter` | Listen von Dateien, die zu den jeweiligen Anleitungen gehören (z. B. die Bilder) |
| `abschlusstext` | optional, HTML-Datei, Abschlusstext |
| `einstellungen.punkte_abgabe` / `punkte_beurteilung` | Höchstpunkte für die Abgabe (80) und für die Beurteilung (20) |
| `einstellungen.abgabe_datei` / `abgabe_text` | Abgabearten (Datei: true, Text: false) |
| `einstellungen.max_dateien`, `max_groesse_mb`, `erlaubte_dateitypen`, `spaete_abgaben`, `selbstbeurteilung` | wie in Moodle (max_groesse_mb 0 = Seitenlimit) |
| `einstellungen.kriterien` | Pflicht, Liste von `{beschreibung_datei` oder `beschreibung, punkte (10), gewicht (1)}` |

Dem Workshop `abschluss: manuell` geben, wenn danach eine Lösung per `voraussetzung` freigeschaltet werden soll.

Andere Aktivitätsarten und Workshop-Strategien baut das Werkzeug nicht (Stand: `platform/mbz-capabilities.json`). Wer sie braucht, ergänzt sie nach dem Wiederherstellen in Moodle oder erweitert `bau.php`.

Bilder in HTML: Inline (data-URI) oder als eigene Moodle-Datei; `@@PLUGINFILE@@`-Verweise werden vom Bau nicht aufgebaut.

## Bewertung (optional, nur sinnvoll für Kurs-MBZ)

```json
"bewertung": {
  "kategorien": [{"name": "Abgaben", "gewicht_prozent": 50, "aktivitaeten": ["a1-abgabe"]}],
  "gewichte": {"a1-test": 50},
  "notenskala": {"stufen": [[92, "1"], [81, "2"], [67, "3"], [50, "4"], [30, "5"], [0, "6"]]}
}
```

- Kurs wird auf **gewichteten Mittelwert** (Höchstwert 100) gestellt, fehlende Bewertungen zählen 0.
- `kategorien`: Bewertungskategorie mit Mittelwert ihrer Aktivitäten und eigenem Gewicht.
- `gewichte`: Gewicht einzelner Aktivitäten direkt im Kurs.
- `notenskala`: Untergrenze in Prozent und Bezeichnung; wird als Bewertungsbuchstaben des Kurses gesetzt.

## Version 1

Pläne ohne `abschnitte` (ein Abschnitt unter `abschnitt`, Aktivitäten unter `aktivitaeten`, Bewertung mit `abgaben` und `tests`) werden automatisch umgewandelt (Abschnitts-id `abschnitt`, Kurzname `MBZ-BAU`). Das Beispiel „Java mit der Blockwelt“ ist ein solcher Plan.
