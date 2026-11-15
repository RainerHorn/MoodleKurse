# Verbesserungen des Moodle-Agentenprozesses

Stand: 2026-11-03. Status: P0/P1 und P2 IMP-13 bis IMP-16 umgesetzt; IMP-17 vorbereitet, empirischer Modellvergleich offen.

Diese Datei dokumentiert Analyse, Verbesserungen und Umsetzungsstand. Der Benutzer hat P0, P1 und anschließend die nächste Priorität P2 beauftragt. Diese Datei erteilt keine Moodle-Freigabe und ersetzt keine bestehenden Agentenregeln. Damals wurde vor Änderungen an bestehenden Markdown-Dateien einmalig `<Dateiname>.bak` angelegt. Diese Regel ist überholt: Laut `AGENTS.md` ist Git die Sicherung, im Repository entstehen keine neuen `.bak`-Dateien.

## Umsetzungsnachweis P0

- Gemeinsame [Prüfstrategie](_vorgaben/qualitaetsstandards/pruefstrategie.md) mit Änderungsmatrix, Nachweiswiederverwendung, gebündelten Metadaten und Trennung von Werkzeugabnahme/Routinebetrieb erstellt; in `AGENTS.md` und den Rollen `orchestrator`, `moodle`, `reviewer` verankert.
- Pauschale Rückleseregel im Rigging-Deployment-Plan für künftige Ausführungen präzisiert. Historische Protokolle, offene Gates und Veröffentlichungsumfang unverändert.
- [Prüf-Runner](scripts/check_runner.py), [Planvorlage](_templates/pruefung/checks.example.json) und [konkreter Rigging-Rechenkernplan](courses/VT/rigging-mathematik-90min/checks.p0.json) ergänzt. Prüfnachweise enthalten Eingabe-/Validator-/Executable-/Runner-Hashes, Argumente, Umgebung und Geltungsbereich. Fehlgeschlagene, unterbrochene oder während des Laufs veränderte Prüfungen werden nicht als gültiger Erfolg übernommen.
- Messung: Testdauer, PASS/FAIL/REUSED und Anlass automatisch; MCP-Aufrufe, Paketdauer, menschliche Wartezeit und Korrekturen können aus vorhandenen Protokollen einmal je Arbeitspaket gemeldet werden. Keine automatische Hermes-/MCP-Instrumentierung und keine erfundenen historischen Messwerte.
- Abnahme: sechs gezielte Runner-Tests bestanden (Wiederverwendung, Eingabe-/Validator-/Umgebungsänderung, Fehler nach früherem Erfolg, fehlende/geänderte Eingaben, Timeout, deaktivierter Cache, Messdaten und Sperrdatei). Sandbox-Zugriff auf temporäre Testdateien war zunächst blockiert; derselbe Testlauf lief mit erteilter Ausführungsfreigabe erfolgreich.
- Praxisnachweis: vorhandener Rigging-Rechenkern-Test einmal PASS, zweiter Aufruf REUSED ohne erneute Testausführung. Keine vollständige Kursprüfung oder Moodle-Abnahme daraus abgeleitet.
- Die drei geänderten SOUL-Dateien in die vorhandenen Hermes-Profile synchronisiert und dort ebenfalls einmalig gesichert. Für die Anwendung neue Agentensitzungen verwenden; ein Neuladen bereits laufender Unterhaltungen wurde nicht nachgewiesen. Keine Modelle oder MCP-Konfigurationen geändert.
- Sicherungen sind lokal und durch die bestehende `*.bak`-Regel von Git ausgeschlossen. Neue Prüf-/Messdaten liegen intern unter `<Planname>.pruefung-intern/` und sind ebenfalls ausgeschlossen; sie dürfen nicht ausgeliefert werden.
- P0 ist als Regeln und lokale Werkzeuge umgesetzt. Die Laufzeitwirkung im nächsten echten Kurslauf muss noch gemessen werden. Weitere Kursvalidatoren erst mit vollständiger Abhängigkeitsliste an den Runner anbinden; deren allgemeine Wiederverwendung bleibt IMP-14. Die umfassende Setup-Konsolidierung bleibt IMP-15.

## Umsetzungsnachweis P1

- [Projektsteuerung](_vorgaben/qualitaetsstandards/projektsteuerung.md), kompakte Auftrags-/Übergabe-/Review-Vorlagen und Machbarkeitsvorlage unter `_templates/prozess/` erstellt und in AGENTS/Rollen verankert. Frühe Moodle-Vorprüfung ist ausdrücklich nur lesend.
- Beide vorhandenen Kurse besitzen eine `STATUS.json` mit lokalem Artefaktsnapshot, Eigentümern, Nachweisen, offenen Punkten und nächster Aktion. `PROZESS.md` verweist darauf; alter Blueprint-Status ist durch den zentralen Verweis ersetzt. Migration basiert auf Berichten, nicht auf neuen Moodle-Aufrufen. Historische Freigaben werden nicht nachträglich an neue Hashes gebunden.
- [Lokale Statusprüfung](scripts/project_status.py) und vier gezielte Tests ergänzt. Beide Kursstatusdateien konsistent; vier Tests bestanden. Exit 0 ist keine Veröffentlichungsfreigabe.
- Quiz-Skill mit dem Skill-Creator-Verfahren von 597 auf 310 Wörter gekürzt (rund 48 %). Kernregeln bleiben im Einstieg, Beispiele/Spezialfälle in gezielt gelesenen Referenzen. Marker-/Vorschaupflicht, falsche Rangfolge, ungültiger XML-Tag und widersprüchliche Titel-/Codeformatregeln bereinigt. Ordering-Versionsangabe anhand offizieller Moodle-Releasenotes korrigiert.
- Beim Profilabgleich drei zusätzliche aktive Quiz-Regeln entdeckt (Transportableitung, konservative Rundung, Drucklayout). Vor dem Schreiben angehalten, Regeln in die passenden Referenzen übernommen, anschließend synchronisiert. Keine fremden Ergänzungen stillschweigend verworfen.
- Vier Rollen und sechs Skill-/Referenzdateien in die Hermes-Profile übernommen; vorhandene Sicherungen erhalten. Für neue Regeln neue Agentensitzungen verwenden; Reload laufender Unterhaltungen nicht nachgewiesen.
- Standard-Skillvalidator ausgeführt, aber durch fehlendes `PyYAML` blockiert. Statt Installation gezielte Ersatzprüfung der einfachen Frontmatter-Felder und direkten Referenzlinks durchgeführt. Ein vorhandener Quizfall mit sechs Fragen bestand die Struktur-/Tag-/Gewichtsprüfung; kein erneuter Fachreview und kein Moodle-Import.
- Einzelheiten und Anforderungszuordnung: [P1-Umsetzungsbericht](docs/p1-umsetzung.md). P2, Modelle und Moodle selbst unverändert.

## Umsetzungsnachweis P2

- [Produktionsablauf](_vorgaben/qualitaetsstandards/produktionsablauf.md): Plattformaufträge separat, Komponenten mit Version/Hash/Nachweis binden; parallele Vorarbeiten und anschließende Quiz-/Gestaltungsarbeit mit klaren Eigentümern und Integrationsbarriere.
- [Komponentenkatalog](platform/components.json), gemeinsame XML-Transport-/Link-Build-Werkzeuge und kompakte Vorlagen ergänzt. Vorhandene Kursbuilder bleiben reproduzierbar; neue Werkzeuge nutzen kursbezogene Eingaben und überschreiben keine Berichte.
- Setup von eingebetteten Alttexten befreit; [Profilabgleich](docs/hermes-setup.md) mit Vorschau, ausdrücklicher Dateiauswahl, Hashprüfung und einmaligen Sicherungen. Genau eine geänderte Orchestrator-Datei synchronisiert; 61 weitere Dateien bereits identisch. Neue Agentensitzungen verwenden.
- Acht gezielte Tests bestanden; bestehende XML-Importfassung und acht Linkseiten byteidentisch im Speicher reproduziert. Keine Kursartefakte oder Moodle-Daten geändert. Konfigurationsvorlage für vorhandenen MCP-Pfad und Werkzeugumfang korrigiert, aktive persönliche Konfigurationen unangetastet.
- IMP-17: Messschema vorbereitet; belastbare Rollen-/Modellmessungen fehlen. Deshalb kein Modellwechsel und keine behauptete Laufzeitersparnis. Empirischer Vergleich bleibt offen.
- Details, Grenzen und Validierung: [P2-Umsetzungsbericht](docs/p2-umsetzung.md).

## Ziel und Priorisierung

Hauptproblem laut Benutzer: zu viele Tests und wiederholtes Zurücklesen nach Schreibvorgängen. Deshalb haben weniger redundante Prüfungen Vorrang vor Modellwechseln und allgemeinen Textkürzungen.

- **P0:** unmittelbare Entlastung bei Tests und Readbacks.
- **P1:** vermeidbare Abstimmungs- und Korrekturschleifen verhindern.
- **P2:** Wiederverwendung, Parallelisierung und weitere Optimierung.

Die Nummern sind stabile Aufgaben-IDs und geben innerhalb der Prioritäten die empfohlene Reihenfolge an. Abhängige Aufgaben können gemeinsam umgesetzt werden. Aufwandsschätzungen sind relativ: klein, mittel, groß; keine Zeitversprechen.

## P0 – Tests und Rücklesen reduzieren

### IMP-01 – Verifizierende Schreibantworten als Nachweis anerkennen

- [x] Eine gemeinsame Prüfregel definieren: Ein Nachweis pro Prüfeigenschaft und unverändertem Stand; zusätzliche Kontrollen brauchen einen konkreten Anlass.
- **Befund:** Der lokale Code von `C:/MoodleMCP/Plugin/local_aicoursecreator/local_aicoursecreator/classes/external/import_page_file.php` berechnet `sha256`, `bytes` und `verified` aus dem gespeicherten Datenbankinhalt. Updates prüfen den Inhalt zusätzlich innerhalb der Transaktion. Im Seitenupdate-Protokoll werden anschließend trotzdem vollständige Inhalte erneut gelesen und verglichen.
- **Änderung:** Nach Abnahme der verwendeten Werkzeugversion genügt die verifizierende Importantwort für die darin tatsächlich belegten Eigenschaften. Kein zusätzlicher vollständiger Inhaltsabruf im Normalfall. Fehlende Nachweise bleiben gezielt zu prüfen. Ein bloßes `success` ohne gespeicherten Ist-Zustand genügt nicht.
- **Ausnahmen:** Abweichung, Timeout/unklarer Ausgang, geänderte Werkzeugversion, relevante Umgebungsänderung oder konkrete Fehlersuche. Nach unklarem Schreibausgang zuerst Zustand lesen; nicht blind erneut schreiben.
- **Betroffen:** `agents/moodle/SOUL.md`, `agents/orchestrator/SOUL.md`, künftige Deployment-Pläne; bestehende freigegebene Pläne nur ausdrücklich angepasst.
- **Abnahme:** Ein erfolgreicher verifizierender Import löst keinen zweiten Inhaltsvergleich aus. Zielzuordnung, Prüfsumme und erwartete Sichtbarkeit werden weiterhin ausgewertet. Darstellung und Rechte werden nicht als durch den Hash bewiesen behandelt.
- **Aufwand:** klein bis mittel. Grundlage für IMP-02 und IMP-03.

### IMP-02 – Gleichartige Metadatenprüfungen bündeln

- [x] Mehrfachabfragen pro Objekt durch eine gezielte gemeinsame Abfrage pro geeignetem Arbeitspaket ersetzen.
- **Änderung:** Das vorhandene `get_module_info` für mehrere Module verwenden. `get_modules` nur zusätzlich aufrufen, wenn dessen Bestandsinformation eine andere, noch offene Prüffrage beantwortet. Bei Titeländerungen Titel und Zielzuordnung prüfen; nicht routinemäßig den vollständigen HTML-Inhalt herunterladen.
- **Grenze:** Vorab aktuelle Moodle-Daten lesen bleibt verpflichtend. Bei konkurrierenden Änderungen oder veraltetem Stand erneut lesen. Kritische Zugriffskontrollen und Sichtbarschaltungen erhalten einen ausdrücklich definierten Prüfablauf; sie werden nicht pauschal gebündelt.
- **Beleg:** `courses/VT/rigging-mathematik-90min/moodle/12_testsystem_seiten_update_protokoll.md` und `moodle/14_testsichtbarkeit_protokoll.md`.
- **Potenzial:** Protokoll 12 beschreibt acht Schreibaufrufe plus 18 zusätzliche Leseaufrufe danach. Acht verifizierende Importe plus eine gemeinsame Metadatenabfrage wären neun statt 26 Aufrufe, etwa 65 % weniger in diesem Teilablauf. Vorabchecks sind nicht mitgezählt; dies ist keine gemessene Laufzeitersparnis.
- **Abnahme:** Jede Abfrage beantwortet eine benannte Prüffrage; identische Metadaten werden ohne Zwischenänderung nicht wiederholt abgerufen.
- **Aufwand:** klein bis mittel; abhängig von IMP-01.

### IMP-03 – Prüfungen nach Änderungsumfang auswählen

- [x] Eine kleine Änderungs-/Prüfmatrix für Inhalte, Rechenwerte, Quizbewertung, Layout, Links, Titel und Sichtbarkeit erstellen.
- **Änderung:** Nur betroffene Artefakte und ihre fachlichen/technischen Abhängigkeiten neu prüfen. Titeländerung: Metadaten. Linkersetzung: Linkziele, Platzhalter und zulässiger Änderungsumfang. Rechenwertänderung: abhängige Aufgaben, Lösungen und Quizfragen. Layoutänderung: betroffene Darstellung, ohne automatisch alle Rechentests zu wiederholen.
- **Grenze:** Bei unklarem Einfluss oder grundlegenden Änderungen breiter prüfen. Keine starre Obergrenze, die tatsächliche Fehler ungeprüft lässt.
- **Betroffen:** Orchestrator, Reviewer, Fach-/Quiz-/Design-Prüfabläufe.
- **Abnahme:** Ein kleiner Änderungsauftrag startet keine unbegründete vollständige Prüfserie; erforderliche Folgeprüfungen sind nachvollziehbar.
- **Aufwand:** mittel; zusammen mit IMP-04 sinnvoll.

### IMP-04 – Prüfnachweise zwischen Agenten wiederverwenden

- [x] Einen kompakten gemeinsamen Prüfnachweis einführen.
- **Inhalt:** Prüfeigenschaft, Eingabedateien und Prüfsummen, Validator-Version/Prüfsumme, relevante Umgebung, Ergebnis, Zeitpunkt und Geltungsbereich.
- **Änderung:** Nachfolgende Agenten übernehmen gültige Nachweise für unveränderte Eingaben. Neu prüfen bei geänderten Eingaben, Prüfscripten, relevanter Umgebung, fehlender Evidenz oder begründetem Zweifel. Generierte Prüfberichte aus der eigenen Eingabefingerabdruck-Berechnung ausnehmen, damit ihre Neuschreibung nicht ständig neue Prüfungen auslöst.
- **Unabhängigkeit:** Der Reviewer behält seine unabhängige fachliche Beurteilung und kann Prüfungen begründet reproduzieren. Wiederverwendung technischer Nachweise ist kein automatisches fachliches APPROVED.
- **Abnahme:** Ein unverändert weitergereichtes Paket löst keine identische Testserie bei jedem Agenten aus. Geänderte Abhängigkeiten machen den zugehörigen Nachweis ungültig.
- **Aufwand:** mittel; mit IMP-07 abstimmen.

### IMP-05 – Werkzeugabnahme von laufender Kursproduktion trennen

- [x] Zwei Prüfmodi festlegen: Werkzeugentwicklung/-abnahme und Routinebetrieb.
- **Änderung:** Negative Tests, Fehlerinjektion, vollständige Transportvergleiche und Rechteprüfungen bei Einführung oder relevanter Änderung eines Werkzeugs durchführen. Im Routinebetrieb gezielt Eingaben, verifizierende Antworten und Arbeitspaket-Ergebnisse prüfen.
- **Grenze:** Browserdarstellung, Lernendenzugriff, Lösungsschutz und Quizfeedback bleiben eigenständige Prüfeigenschaften. Ein Datenbank-Hash ersetzt keinen Funktionstest.
- **Betroffen:** Moodle-Agent, Reviewer, Plattformtests und Deployment-Vorlagen.
- **Abnahme:** Ein neuer Kurs startet nicht erneut die vollständige Abnahme eines unveränderten Importwerkzeugs. Der verwendete Werkzeug-/Umgebungsstand ist belegt.
- **Aufwand:** mittel.

### IMP-06 – Aufwand messen, ohne zusätzliche Agentenschleifen

- [x] Laufzeit je Phase, Wartezeit auf Menschen, Schreib-/Leseaufrufe, Testläufe und Korrekturursachen aus vorhandenen Abläufen kompakt erfassen.
- **Änderung:** Protokollierung möglichst im Werkzeug/Runner; keine zusätzliche Unterhaltung nur zur Messung. Prüfläufe nach Anlass unterscheiden: Änderung, Erstabnahme, Fehleranalyse oder Wiederholung ohne Änderung.
- **Abnahme:** Vorher-/Nachher-Vergleich an vergleichbaren Kursläufen; Fehler und Nacharbeit ebenfalls erfassen. Keine pauschalen Beschleunigungsversprechen.
- **Aufwand:** klein bis mittel; möglichst begleitend zu IMP-01 beginnen.

## P1 – Status, Übergaben und Anweisungen klären

### IMP-07 – Einen verbindlichen aktuellen Projektstatus führen

- [x] Pro Kurs eine zentrale strukturierte Statusdatei mit Artefaktversionen, Prüfverweisen, offenen Blockern und nächster Aktion vorsehen.
- **Befund:** `PROZESS.md` beschreibt beim Rigging-Kurs einen älteren Importstand als `moodle/14_testsichtbarkeit_protokoll.md`. Der Quiz-Blueprint nennt eine ausstehende Prüfung; ein späterer Preflight behandelt dies erneut als Freigabefrage, obwohl vorherige Reviews das Assessment einschließen. Die Versionszuordnung fehlt als eindeutige Entscheidungsgrundlage.
- **Änderung:** Orchestrator verantwortet den aktuellen Status. Historische Berichte bleiben Historie; Statusanzeigen werden daraus bzw. aus der zentralen Datei abgeleitet und nicht unabhängig gepflegt.
- **Abnahme:** Jeder Agent erkennt den aktuellen Stand und die gültigen Nachweise ohne Rekonstruktion der gesamten Berichtshistorie.
- **Aufwand:** mittel; Grundlage für IMP-08.

### IMP-08 – Freigaben und Blocker eindeutig abgrenzen

- [x] Inhalts-/Artefaktfreigabe, technische Einsatzbereitschaft und Benutzerfreigabe getrennt dokumentieren.
- **Änderung:** `APPROVED`/`REJECTED` erhalten einen eindeutigen Prüfgegenstand mit Paketversion/Prüfsummen. Findings nennen die konkret blockierte Phase, Schweregrad, Eigentümer und Erfüllungskriterium. Verbesserungsideen ohne Abnahmerelevanz werden separat geführt.
- **Benutzerfreigabe:** Zielinstanz, Kurs, Paket und erlaubter Ablauf festhalten. Innerhalb einer bestehenden Freigabe keine erneuten Routinefragen; Erweiterungen des Umfangs gesondert entscheiden.
- **Beleg:** `review/02_re_review.md` korrigiert die widersprüchliche Kombination von APPROVED und Publikationsblockern aus Review 01.
- **Abnahme:** Eine fachliche Freigabe wird weder als Veröffentlichungserlaubnis missverstanden noch wegen ungeklärter Technik wiederholt eingeholt.
- **Aufwand:** mittel.

### IMP-09 – Technische Machbarkeit früh prüfen

- [x] `moodle` vor der vollständigen Materialproduktion mit einer lesenden Machbarkeitsprüfung beauftragen (Prozessregel; keine ungefragte Live-Prüfung bestehender Kurse).
- **Inhalt:** Zielsystem, verfügbare Import-/Lesewerkzeuge, Fragetypen, Dateiformate, Darstellungsweg, manuelle Schritte und benötigte Browserabnahmen.
- **Änderung:** Ein versioniertes Fähigkeitsprofil wiederverwenden und bei relevanten Änderungen aktualisieren. Kurs-ID und aktueller Zielbestand werden weiterhin auftragsbezogen gelesen. Fehlende Infrastruktur vor der Gestaltung eines davon abhängigen Pakets klären.
- **Abnahme:** Fehlender Dateiimport oder nicht setzbare Quizoptionen werden vor der vollständigen Ausarbeitung erkannt.
- **Aufwand:** mittel; ausschließlich `moodle` verwendet Moodle-MCP.

### IMP-10 – Verbindliche Aufträge, Übergaben und Zuständigkeiten

- [x] Eine kurze Auftragsvorlage und ein einheitliches Übergabeformat erstellen.
- **Auftrag:** Bildungsgang, belegtes Lernfeld, Umfang einschließlich Test, Voraussetzungen, Lernprodukt, Materialien, Zusatzfunktionen und Abnahmekriterien.
- **Agentenauftrag:** konkrete Eingaben, Ausgabepfade, Zuständigkeit, Abhängigkeiten und Fertigstellungskriterien.
- **Übergabe:** Ergebnisdateien, Prüfnachweise, offene Blocker und notwendige Entscheidungen; keine Wiederholung der gesamten Vorgeschichte.
- **Eigentümer:** Fachagent für fachliche Werte/Lösungen, Didaktik für Ablauf/Zeitbudget, Quiz für Bewertung, Design für Darstellung. Gemeinsame Inhalte referenzieren oder ableiten statt konkurrierende Fassungen zu pflegen. Orchestrator entscheidet Routinefragen innerhalb des vereinbarten Rahmens und bündelt Benutzerfragen.
- **Abnahme:** Jeder Spezialist kann ohne erneute Grundsatzklärung beginnen; Quelldateien anderer Agenten werden nicht stillschweigend überschrieben.
- **Aufwand:** mittel.

### IMP-11 – Reviews bündeln und Korrekturen gezielt nachprüfen

- [x] Einen Gesamt-Review des fertigen Pakets mit vollständiger Befundliste und anschließenden gezielten Nachprüfungen vereinbaren.
- **Änderung:** Befund-ID, zuständiger Agent, betroffene Dateien und Erfolgskriterium je Korrekturauftrag. Nachprüfungen auf Änderungen und Auswirkungen begrenzen. Neue tatsächliche Fehler dürfen weiterhin gemeldet werden; neue kosmetische Wünsche werden nicht nachträglich zu Pflichtblockern.
- **Schleifenregel:** Nach wiederholtem Scheitern zuerst Ursache und Auftrag präzisieren, nicht denselben Auftrag unverändert erneut senden.
- **Abnahme:** Eine Linkkorrektur führt nicht zur erneuten vollständigen Fachbegutachtung. Unabhängiger Reviewer und verbindliche Quellenprüfungen bleiben erhalten.
- **Aufwand:** klein bis mittel; nutzt IMP-03, IMP-04 und IMP-08.

### IMP-12 – SKILL.md kürzen und widersprüchliche Referenzen bereinigen

- [x] Den Quiz-Skill und seine Referenzen nach Benutzerauftrag P1 konsolidieren.
- **Antwort auf die Benutzerfrage:** Ja. Im untersuchten Repository gibt es eine `SKILL.md`: `agents/quiz/skills/moodle-fragen-generator/SKILL.md`, vor Umsetzung 597, jetzt 310 Wörter. Die übrigen Agentenanweisungen heißen überwiegend `SOUL.md`. Diese sind bereits relativ kurz; der größere Nutzen liegt in eindeutigen Regeln und bedarfsgerechtem Nachladen, nicht allein in weniger Zeilen.
- **Kürzungskandidaten:** Die beiden XML-Beispiele in die Strukturreferenz/Vorlagen auslagern; Kategorie-, Tag- und Validierungsregeln zwischen Ablauf und Detailabschnitt entdoppeln; Spezialfälle zu CodeRunner/SVG nur bei passendem Auftrag laden; Ressourcenhinweise zu einer kompakten Auswahlhilfe zusammenfassen.
- **Im Hauptskill behalten:** Zweck/Anwendung, Rangfolge der Regeln, Rollen-/Moodle-Grenze, nötige Eingaben, kurzer Ablauf, Kernanforderungen, gezielte Referenzverweise, Ausgabe- und Prüfnachweis. Kritische Grenzen nur dann durch Verweise ersetzen, wenn die gemeinsamen Regeln im tatsächlichen Hermes-Aufruf zuverlässig geladen werden.
- **Vor dem Kürzen korrigieren:** `references/moodle-xml-structure.md` erklärt Frage-Marker zu Pflicht und verweist in seiner Rangfolge auf `.github/instructions/questions.instructions.md`; der Hauptskill erklärt Marker ausdrücklich für optional und ordnet sich `AGENTS.md`/Rolle unter. Gültige Regelquelle und fachliche Aussagen klären; widersprüchliche Altanweisungen nicht lediglich in Referenzen verstecken.
- **Vorgehen:** Jede bestehende Anforderung auf „beibehalten“, „zusammenführen“ oder „gezielt referenzieren“ abbilden. Eine verbindliche Anforderung darf bei der Kürzung nicht versehentlich verloren gehen. Gemeinsame Regeln zentral, Rollenspezifika in SOUL.md, ausführbare Fachabläufe im Skill halten.
- **Abnahme:** Kürzerer Hauptskill, eindeutige Referenzhierarchie und vollständige Anforderungsabdeckung. Ein repräsentativer Quizauftrag reicht zur gezielten Verhaltensprüfung; keine neue umfassende Testkampagne allein wegen Textkürzungen. Gesamten tatsächlich geladenen Kontext berücksichtigen: Auslagern spart nichts, wenn danach alle Referenzen immer vollständig gelesen werden.
- **Erwartung:** Weniger Kontext und Interpretationskonflikte; keine belegte Laufzeitquote. Vorrangig bleiben IMP-01 bis IMP-05.
- **Aufwand:** mittel; mit IMP-10 und IMP-15 abstimmen.

## P2 – Wiederverwendung und weiterer Ausbau

### IMP-13 – Plattformarbeit und Kursproduktion organisatorisch trennen

- [x] Wiederverwendbare Import-, Readback-, Chatbot- und Schutzfunktionen als eigene Plattformaufgaben behandeln.
- **Änderung:** Kurse verwenden einen bekannten abgenommenen Funktionsstand. Neue Funktionen erhalten eigene Anforderungen und Abnahme; ihre Integration in den Kurs erfolgt ausdrücklich. Optionale Erweiterungen nicht stillschweigend zum Pflichtumfang machen oder eigenmächtig weglassen.
- **Beleg:** Der Rigging-Auftrag enthält neben Unterrichtsmaterialien auch Seitenimport-, DOCX-, Chatlock- und Readback-Entwicklung.
- **Abnahme:** Ein Kursauftrag wird nicht unbeabsichtigt zum offenen Plattformentwicklungsprojekt.
- **Aufwand:** mittel bis groß; eng mit IMP-05 und IMP-09 verbunden.

### IMP-14 – Build, Validatoren, Templates und Importableitungen wiederverwenden

- [x] Gemeinsame XML-Transport-/Link-Build-Stufen mit kursbezogenen Eingaben, Versionen und gezielten Tests bereitgestellt; Gesamtbuilder bleibt bewusst kursbezogen. Nutzung im nächsten Kurs noch zu beobachten.
- **Änderung:** Autorendatei und technische Importfassung explizit unterscheiden. Beispielsweise Kategorieblock im Quiz-Original erhalten und bei Bedarf eine getestete Transportableitung für den konkreten Importweg erzeugen. Nicht jedes Mal einen neuen Konverter samt vollständigem Review entwickeln.
- **Templates:** Einen auf dem Zielsystem geprüften Darstellungsweg und optionale Komponenten definieren. Nicht benötigte Spiele-/Chatbot-Funktionen nicht automatisch in jedes Material einbauen. Bestehende ausdrückliche Template-Vorgaben dabei berücksichtigen.
- **Validatoren:** Nach Möglichkeit reine Prüfmodi ohne Überschreiben fremder Berichte; Ergebnisse zentral erfassen. Wiederholbare technische Vergleiche durch Scripts statt durch erneute Modellinterpretation erledigen.
- **Abnahme:** Nächster Kurs nutzt vorhandene Komponenten mit kursbezogenen Eingaben; Änderungen an gemeinsamen Komponenten lösen gezielte Regressionstests aus.
- **Aufwand:** groß; nutzt IMP-03 bis IMP-05 und IMP-09.

### IMP-15 – Setup und aktive Agentenkonfiguration synchron halten

- [x] Verbindliche Pflegequellen und Profilabgleich eingerichtet. Lokalen Komponentenstand dokumentiert; tatsächlich installierter Serverstand bleibt separat durch moodle nachzuweisen.
- **Befund:** `setup-hermes.ps1` enthält eingebettete Rollen und kopiert SOUL-Dateien/Quiz-Skill in Profile. Die versionierte Moodle-Konfigurationsvorlage enthält spätere Import-/Readback-Werkzeuge noch nicht. Deployment-Protokolle nennen `C:/MoodleMCP` statt des im Setup genannten Pfades.
- **Änderung:** Rollen möglichst aus den versionierten Dateien synchronisieren statt parallele Textfassungen pflegen. Abweichungen aktiver Profile lesend feststellen; gezielte Synchronisierung mit Vorschau statt pauschalem Setup-Überschreiben. Secrets bleiben außerhalb des Repositorys.
- **Grenze:** Eine heutige Abweichung aller aktiven Profile wurde nicht nachgewiesen. Die Profilübersicht belegt Modelle und Gateway-Status, nicht die geladenen Anweisungsversionen.
- **Abnahme:** Nach einer Rollen-/Skill-Änderung ist nachweisbar, welcher Stand in welchem Profil aktiv ist; keine alten Regeln durch Setup erneut eingeführt.
- **Aufwand:** mittel.

### IMP-16 – Unabhängige Arbeit nach gemeinsamem Rahmen parallelisieren

- [x] Fachgrundlagen, didaktischen Grobentwurf und technische Vorprüfung parallel planen; gemeinsamen Rahmen und anschließende Integrationsbarriere verbindlich festgelegt. Laufzeitwirkung im nächsten Kurs messen.
- **Änderung:** Nach abgestimmten Lernzielen und Inhalten Quiz-Erstellung und Gestaltung stabiler Seiten parallel ausführen. Endintegration wartet auf erforderliche Ergebnisse. Zuständigkeiten und Dateieigentum explizit festlegen.
- **Grenze:** Keine vollständigen konkurrierenden Inhaltsfassungen vor der Abstimmung erzeugen. Bot-Erreichbarkeit und Wiederaufnahme nach Ausfällen klären; im FIAE-Prozess ist ein nicht erreichbarer Bot dokumentiert.
- **Abnahme:** Weniger serielle Wartezeit ohne zusätzliche Abstimmungsschleifen oder Dateikonflikte.
- **Aufwand:** mittel; erst nach IMP-07 und IMP-10.

### IMP-17 – Modelle erst nach Prozessbereinigung anhand von Messwerten optimieren

- [ ] Nach Reduktion redundanter Aufrufe verbleibende Laufzeiten und Qualität je Rolle vergleichen.
- **Stand P2:** Messvorlage und Vergleichskriterien vorhanden. Bisher nur lokale Test-/Cachezeiten, keine belastbaren Modellvergleichsdaten. Dieser Punkt bleibt bis zu echten Rollenläufen offen; Modelle unverändert.
- **Ausgelesener Stand (`hermes profile list`):** orchestrator `gpt-6-sol`; didaktik/fiae `gpt-5.6-sol`; fidp/quiz `gpt-6.1-sol`; fisi/moodle/vt `claude-sonnet-5-5[1m]`; reviewer/visual-designer `claude-opus-5-5`. Dies sind konfigurierte Kennungen, keine Bewertung ihrer Leistung.
- **Änderung:** Gezielte Rollenvergleiche nur bei nachgewiesenem Restengpass. Deterministische Prüfungen in Tools/Scripts belassen. Keine unbelegte Modellmigration als erste Maßnahme.
- **Abnahme:** Eine Modelländerung ist durch vergleichbare Laufzeit-/Qualitätsdaten begründet und wird ausdrücklich beauftragt.
- **Aufwand:** abhängig vom verbleibenden Engpass; nach IMP-06.

## Unverändert zu bewahrende Regeln

- Verbindliche lokale SCHUCO- und Rahmenlehrplanquellen sowie vollständige Handlung.
- Fachliche Richtigkeit, Lösungsschutz und unabhängiger Reviewer.
- Moodle-MCP ausschließlich durch `moodle`; keine geratenen IDs, aktuelle Daten vor Änderungen.
- Kein automatisches Löschen von Moodle-Aktivitäten.
- Publishing nur nach den geltenden Qualitätsgates und ausdrücklicher Benutzerfreigabe.
- Keine fremden Quelldateien stillschweigend überschreiben; Unsicherheiten dokumentieren.

Prüfungen sollen zielgerichteter werden. Korrekte Speicherung, fachliche Qualität, Browserfunktion und Zugriffsrechte sind unterschiedliche Nachweise; keiner ersetzt pauschal die anderen.

## Nächster Schritt

P0/P1/P2 im nächsten beauftragten Kurslauf anwenden und tatsächliche Laufzeit-/Qualitätsdaten erfassen. Daraus bei einem verbleibenden Modellengpass IMP-17 bearbeiten. Eine neue Kursproduktion, Moodle-Ausführung oder Veröffentlichung ist mit der Prozessoptimierung nicht beauftragt.
