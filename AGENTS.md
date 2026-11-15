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
- moodle-mcp: technische Moodle-Umsetzung per Moodle-MCP (direkt in eine bestehende Moodle).
- moodle-mbz: technische Moodle-Umsetzung als Kurssicherung `.mbz` (lokales Moodle im Container, ohne MCP).
- orchestrator: Koordination des Gesamtprozesses; verwendet standardmaessig MBZ und fragt nur bei einem erkennbaren Variantenwechsel nach.

## Moodle-Variante (MCP oder MBZ)
**Standard ist MBZ.** Der Orchestrator traegt `MBZ` in `STATUS.json`
(`brief.moodle_variant`) und im Auftrag ein, ohne die bereits festgelegte Variante
bei jedem Kurs erneut abzufragen. Nur wenn der Auftrag Direktimport, einen
bestehenden Zielkurs, Moodle-MCP oder einen ausdruecklichen Variantenwechsel nennt,
wird die Variante gebuendelt geklaert. Ohne ausdruecklichen Wechsel weder
`moodle-mcp` beauftragen noch Moodle-MCP-Werkzeuge aufrufen. MCP bleibt als
dokumentierte Alternative erhalten; alles dazu steht in `docs/mcp-anhang.md`.
- `MCP`: Rolle `moodle-mcp`, Direktschreiben per MCP, Readback je Objekt.
- `MBZ`: Rolle `moodle-mbz`, `.mbz`-Sicherung (Kurs oder Abschnitt), von der Lehrkraft
  in der Schul-Moodle wiederhergestellt.
Fach-, Didaktik-, Quiz- und Designarbeit sind variantenunabhaengig, beachten aber die
Grenzen der gewaehlten Variante. Fuer MBZ stehen sie ausschliesslich in
`platform/mbz-capabilities.json` (zentrale MBZ-Machbarkeit); andere Dokumente
wiederholen diese Liste nicht.
Der operative Ablauf steht einmal, in `docs/mbz-workflow.md`, samt seinen
Sicherheitsgates. Rollen und andere Dokumente verweisen auf dessen Schritte.

## Moodle-Sicherheitsregel
Nur der Agent `moodle-mcp` darf Moodle-MCP-Werkzeuge verwenden.
Andere Agenten, auch `moodle-mbz`, veraendern keine Moodle-Instanz. `moodle-mbz` arbeitet
nur mit lokalen Dateien und dem lokalen Baucontainer; Wiederherstellen in der Schul-Moodle
macht die Lehrkraft.

## Loeschen
Automatisches Loeschen von Moodle-Aktivitaeten ist verboten.
`moodle_delete_module` soll nicht freigegeben werden.
Das Entfernen des eigenen Baukurses im lokalen Container durch `moodle-mbz` ist Teil des
Werkzeugs und nicht gemeint.

## Identifikatoren
Kurs-ID, Abschnitts-ID und cmid werden niemals geraten.
Vor Aenderungen werden die aktuellen Moodle-Daten gelesen (Variante MCP). Bei MBZ erfragt
der Orchestrator Zielabschnittsnummer und Zielweg ueber den Auftraggeber beim Benutzer; sie
werden nicht geraten.

## Dateien
Jeder Unterrichtsauftrag erhaelt einen eigenen Ordner unter `courses/`.
Ordneraufbau, Eigentuemer und die Kennzeichnung geschuetzter Dateien (`_intern`)
stehen in `_vorgaben/qualitaetsstandards/projektsteuerung.md`.
Quelldateien anderer Agenten werden nicht stillschweigend ueberschrieben.

Fuer versionierte Dateien ist Git die Sicherung. Keine `.bak`-Dateien neben
Projektdateien erzeugen. Vor groesseren automatischen Aenderungen vorhandene
Fremdaenderungen mit `git status` pruefen und bei Bedarf einen Commit oder Branch
verwenden. Nur unversionierte Dateien ausserhalb des Repositorys benoetigen eine
gesonderte Sicherung.

## Obsidian-Wissensschicht

Der Vault `C:\Users\Horn\Projekte\Obsidian\vault` ist die Navigations- und
Wissensschicht. Kursartefakte, `STATUS.json`, Pruefbelege und Auslieferungsdateien
bleiben ausschliesslich in diesem Repository verbindlich. Der Orchestrator kann
nach einem Statusmeilenstein `scripts/sync_obsidian.py` ausfuehren. Die
Synchronisation laeuft nur von `Moodle-Kurse` nach Obsidian und kopiert keine
geschuetzten Loesungen, internen Quizdaten, MBZ-Dateien oder technischen Rohlogs.
Automatisch erzeugte Notizbereiche nicht manuell bearbeiten; eigene Inhalte nur
zwischen `BEGIN MANUAL` und `END MANUAL` pflegen.

## Effiziente Pruefung

Bei Pruef-, Review- oder Deployment-Auftraegen gilt zusaetzlich
`_vorgaben/qualitaetsstandards/pruefstrategie.md`. Pro Pruefeigenschaft und
unveraendertem Stand genuegt ein gueltiger Nachweis. Pruefungen nach
Aenderungsumfang auswaehlen, vorhandene technische Nachweise wiederverwenden
und gleichartige Metadatenabfragen buendeln. Im Routinebetrieb keine manuellen
Hashlisten je Rolle oder Dokument pflegen. Falls eine unveraenderliche Bindung
noetig ist, genau einen Git-Stand oder ein von einem Werkzeug erzeugtes Quellmanifest referenzieren. Die
finale `.mbz` erhaelt einen SHA-256. Wiederholungen brauchen einen konkreten
Anlass. Fachliche Unabhaengigkeit und die Deployment-Gates bleiben verbindlich;
ein technischer PASS ist kein Reviewer-APPROVED.

## Projektsteuerung

Fuer Unterrichtsauftraege gilt `_vorgaben/qualitaetsstandards/projektsteuerung.md`.
Der Orchestrator pflegt pro Kurs `STATUS.json` als einzige aktuelle Statusquelle.
Alle Agenten lesen vor ihrer Arbeit ihren Auftrag, dessen Eingaben und den dort
verlinkten Stand. Historische Berichte sind Nachweise, keine aktuellen Freigaben.
Rollen: Fachwerte/Loesungen beim Fachagenten, Ablauf/Zeitbudget bei didaktik,
Bewertung bei quiz, Darstellung beim visual-designer, Technik bei moodle-mcp bzw. moodle-mbz.
Uebergaben nennen Dateien, Aenderungen, Pruefnachweise und offene Entscheidungen.

## Verbindlicher Agenten-Kommunikationsweg

Fuer die Moodle-Kursproduktion gilt eine flache, eindeutige Steuerungskette
(Benutzerentscheidung vom 15.11.2026: zwei gleichwertige Eingaenge).

**Auftraggeber** eines Kursauftrags ist entweder der Benutzer direkt im
Orchestrator-Chat oder `hermes` im Namen des Benutzers.

1. Der Benutzer erarbeitet Anforderungen, Korrekturen und Freigaben direkt mit
   `orchestrator` oder mit `hermes`.
2. `hermes` uebergibt den konsolidierten Auftrag ausschliesslich an `orchestrator`
   und beauftragt nie selbst eine Spezialistenrolle. Die Regeln fuer `hermes`
   stehen in `agents/_shared/hermes/SOUL.md`.
3. Nur `orchestrator` beauftragt Fach-, Didaktik-, Quiz-, Design-, Review- und Moodle-Rollen.
4. Spezialisten beauftragen keine anderen Rollen. Abhaengigkeiten, Ergebnisse und Blocker gehen an `orchestrator` zurueck.
5. `orchestrator` konsolidiert den Stand und meldet nur Meilensteine, echte Blocker
   und Benutzergates an den Auftraggeber, auf dem Weg, auf dem der Auftrag kam.
6. Rueckfragen an den Benutzer und Benutzerfreigaben laufen nur ueber
   `orchestrator` und den Auftraggeber. Spezialisten fragen den Benutzer nicht
   selbst; sie melden fehlende Angaben an `orchestrator`.

Ein direkter Produktionsauftrag von `hermes`, einem anderen Spezialisten oder dem
Benutzer an eine Fachrolle wird nicht ausgefuehrt; die Rolle verweist auf den
Orchestratorweg. Dies gilt nicht fuer klar abgegrenzte Einzelauftraege ausserhalb
einer orchestrierten Moodle-Kursproduktion.

Ein Kurslauf passt nicht in ein Hop-Budget. Er besteht deshalb aus drei festen
Ketten (`docs/mbz-workflow.md`, Abschnitt Ketten). Jede Kette endet mit
aktualisierter `STATUS.json` und einer Meldung an den Auftraggeber; erst ein
neuer Turn des Auftraggebers ("weiter") startet die naechste.

Eine substanzielle Fertigmeldung ist kein FYI: Bei aktivem Auftrag darf weder
`orchestrator` noch eine Spezialistenrolle mit `[SILENT]` enden. Die Rolle meldet
Ergebnis, Nachweise, Blocker und offenen Wiederaufnahmepunkt an ihren Auftraggeber.
Hop-Limits werden nicht erhoeht oder durch Umgehungsketten kompensiert. Der
Workflow bleibt bei hoechstens einer Spezialistenebene plus Rueckmeldung. Eine
abweichende Topologie braucht eine ausdrueckliche neue Benutzerentscheidung.

## Wiederverwendung und Parallelitaet

Fuer Plattformabhaengigkeiten und parallele Auftraege gilt ebenfalls
`_vorgaben/qualitaetsstandards/projektsteuerung.md`. Gemeinsame Werkzeuge stehen
in `platform/components.json`; nur benoetigte Komponenten und Referenzen laden.
Rollen/Skills im Repository sind die Pflegequelle. Profilabgleich nach
`docs/hermes-setup.md`, niemals eingebettete Alttexte aus Setup-Skripten verwenden.

Der Orchestrator beauftragt voneinander unabhaengige Fach-, Didaktik-, Quiz- und
Designrollen direkt und moeglichst in einer gebuendelten Welle. Reviewer melden
Findings an den Orchestrator und delegieren Korrekturen nicht selbst. Der
Orchestrator ordnet Findings den Eigentuemerrollen zu, sendet eine direkte
Korrekturwelle und danach hoechstens eine gezielte Delta-Pruefwelle. Lautet
auch deren Urteil `REJECTED`, delegiert der Orchestrator nicht weiter: Er meldet
die offenen `BLOCKER`, die vermutete Ursache und die Optionen als Benutzergate an
den Auftraggeber. Serielle
Bot-Ketten sind nur zulaessig, wenn eine Ausgabe fachlich zwingend Eingabe der
naechsten Rolle ist.

## Unsicherheit
Fehlende oder widerspruechliche Informationen werden dokumentiert.
Unsicherheiten duerfen nicht durch erfundene Fakten ersetzt werden.

## Deployment-Gate
Jede Auslieferung (finale `.mbz` bzw. MCP-Schreiben) setzt voraus:
1. Fach-/Didaktik-/Assessment-Erstellung,
2. Visual Design,
3. Reviewer-Status `APPROVED`.

- **MBZ** (Benutzerentscheidung vom 15.11.2026): Danach baut `moodle-mbz` die
  finale `.mbz` ohne weitere Benutzerfreigabe. Der Orchestrator prueft Kursplan
  und Baunachweise, bevor er sie uebergibt. Kein Agent schreibt in die
  Schul-Moodle; die Lehrkraft entscheidet mit dem Wiederherstellen ueber den
  Einsatz und nimmt dort ab. Ein Benutzergate entsteht nur, wenn der Plan vom
  Auftrag abweicht (Ebene, Zielweg, Zielabschnitt), ein Element nicht
  unterstuetzt wird oder Sichtbarkeit oder Schutz gegenueber dem geprueften
  Paket geaendert werden.
- **MCP**: zusaetzlich 4. ausdrueckliche Benutzerfreigabe fuer den konkreten
  Plan vor jedem Schreiben (`docs/mcp-anhang.md`).

Lokale Testbaeue von `moodle-mbz` im Container veraendern keine Schul-Moodle und sind vorab erlaubt.
