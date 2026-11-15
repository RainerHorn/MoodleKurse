# P1 – Umsetzung und gezielte Abnahme

Stand: 2026-11-03. IMP-07 bis IMP-12 umgesetzt. Keine Moodle-Aufrufe, Imports oder
neuen Veröffentlichungsfreigaben. Einmalige `.md.bak`-Sicherungen bleiben erhalten.

## Ergebnis

| Aufgabe | Umsetzung |
|---|---|
| IMP-07 | STATUS.json je vorhandenem Kurs, Artefakt-Hashes, Eigentümer, Nachweise, offene Punkte, nächste Aktion; PROZESS.md als Verweis |
| IMP-08 | Getrennte Review-/Technik-/Benutzerzustände, Paket-/Hashbindung und phasenbezogene Blocker |
| IMP-09 | Frühe rein lesende Machbarkeit in Orchestrator und Moodle-Rolle, wiederverwendbare Vorlage mit Versions-/Umgebungsbezug |
| IMP-10 | Kompakte Auftrags-/Übergabevorlagen und klare Eigentümer; Routineentscheidungen beim Orchestrator |
| IMP-11 | Gesamt-Review, gebündelte Findings, gezielte Nachprüfung; keine neuen Wunschkriterien als Pflichtblocker |
| IMP-12 | Quiz-Einstieg von 597 auf 310 Wörter; Detailbeispiele und Spezialregeln bedarfsgerecht, Konflikte bereinigt |

Zentrale Regeln: `AGENTS.md`, `_vorgaben/qualitaetsstandards/projektsteuerung.md`.
Die Vorlagen sind in Agentennachrichten nutzbar; keine zusätzlichen vollständigen
Berichte pro Arbeitsschritt erforderlich. P0 gilt weiter.

## Erhaltung der Skill-Anforderungen

| Bisherige Anforderung | Neuer Ort / Behandlung |
|---|---|
| Quellen-/Rollenrangfolge, freigegebene Inhalte, kein MCP/Import | Hauptskill Grenzen und Abschluss |
| Parameter aus Auftrag ableiten, echte Lücken klären | Hauptskill Schritt 1 |
| Plugins nur bei bestätigter Verfügbarkeit | Hauptskill Grenzen |
| Vorlagen, Kursordner, Beispiele nicht überschreiben | Hauptskill Schritte 2–3 |
| UTF-8, Deklaration, quiz, name, questiontext, Tags, CDATA | Hauptskill Kernregeln; XML-Beispiel in Strukturreferenz |
| Eigene Kategorie, gemeinsamer Pfad bei Teil-Dateien, keine erfundenen Zuordnungen | Hauptskill Kernregeln |
| Positive MC-Gewichte, neutrale Distraktoren, keine Positionsabhängigkeit | Hauptskill Kernregeln |
| Konsistenz Diagramm/Frage/Lösung/Punkte/Feedback | Hauptskill Kernregeln |
| Wohlgeformtheit, Typen, Bewertung, Feedback, Platzhalter, Konsistenz | Hauptskill Schritt 4; P0-Nachweise |
| Vorschau nur bei Bedarf; kein Ersatz für Moodle | Hauptskill Schritt 5; optionale Details |
| Kommentare optional; CodeRunner-Einzelexport nur bei bestätigtem Bedarf | Hauptskill Kernregeln |
| Cisco-Assets und bedarfsgerechte Spezialreferenzen | Hauptskill Routing; Pfade in Fachdetails berichtigt |
| Abschlussinformationen und unabhängiger Review | Hauptskill Schritte/Übergabe |
| Zusätzliche Regel im aktiven Profil: Transportableitung nur auf Auftrag, Original schützen, Bytes/Bäume/Hashes prüfen | Strukturreferenz vollständig erhalten |
| Zusätzliche Profilregel: konservative Grenzwerte/Toleranzen | Fachdetails „Numerische Grenzwerte und konservative Rundung“ |
| Zusätzliche Profilregel: PDF-Druckexport und Seitenrendering | Fachdetails „Druckbare Testbögen“; vorhandene gültige Nachweise bleiben nutzbar |

Die historischen Quelldokumente sind Herkunftsnotizen statt konkurrierender
Anweisungen. Originale liegen in ihren einmaligen Sicherungen. Keine neue
pauschale Test-/Vorschaupflicht eingeführt.

Technische Formatkorrekturen orientieren sich an der
[Moodle-4.5-XML-Dokumentation](https://docs.moodle.org/405/en/Moodle_XML_format).
Die Ordering-Vorlagen nennen jetzt Core-Einführung mit Moodle 4.4 gemäß den
[offiziellen Releasenotes](https://moodledev.io/general/releases/4.4).

## Abnahme und Grenzen

- Vier Tests in `tests/test_project_status.py` bestanden: Änderungserkennung,
  Freigabebindung/Blocker, historische Testgenehmigung und Pfadgrenzen.
- Beide echten Kursstatusdateien mit `scripts/project_status.py` konsistent.
  Sie dokumentieren den lokalen Stand und historische Berichte; heute laufende
  Moodle-Version, Sichtbarkeit und Rechte wurden nicht behauptet oder geprüft.
- `quick_validate.py` aus skill-creator versucht: fehlendes PyYAML. Gezielte
  Ersatzprüfung der einfachen YAML-Strings, Namens-/Beschreibungsgrenzen und
  direkten Referenzlinks bestanden (`_workspace/validate_p1.ps1`). Kein allgemeiner
  YAML-Parser oder vollständiger Skillvalidator-Erfolg behauptet.
- Vorhandenes sechs Fragen umfassendes Quiz strukturell gegen die Kernregeln
  geprüft: Kategorie, Titel, Texte, Tags und positive MC-Gewichte bestanden.
  Keine neue fachliche oder Live-Importfreigabe daraus abgeleitet.
- Vier SOUL-Dateien und sechs Skill-/Referenzdateien nach Abgleich und Sicherung
  in Hermes synchronisiert. Ein erster Abgleich stoppte vor allen Schreibvorgängen
  wegen zusätzlicher Profilregeln; diese wurden vor der Übernahme erhalten.

Neue Hermes-Agentensitzungen verwenden. Ob laufende Unterhaltungen geänderte
Dateien nachladen, wurde nicht geprüft. Setup-Konsolidierung und allgemeine
Komponentenmigration gehören weiterhin zum noch offenen P2.
