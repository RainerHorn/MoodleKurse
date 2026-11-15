---
name: moodle-agent-control-plane
description: Steuert Moodle-Agenten über den Orchestrator; Auftraggeber ist der Benutzer direkt oder Hermes.
version: 0.4.0
author: Horn, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Moodle, Multi-Agent, Workflow]
    related_skills: []
---

# Moodle Agent Control Plane

Dieser Skill erzwingt den Kommunikationsweg bei orchestrierten Moodle-Kursproduktionen. Fachliche und technische Rollenregeln bleiben in der jeweiligen SOUL-Datei und in `AGENTS.md`.

## When to Use

- Bei jeder Erstellung, Überarbeitung, Prüfung oder Auslieferung eines Moodle-Kurses.
- Bei Fertigmeldungen, Blockern oder Benutzergates aus einer laufenden Kursproduktion.
- Nicht für klar abgegrenzte Einzelaufträge außerhalb einer orchestrierten Moodle-Kursproduktion.

## Procedure

Auftraggeber eines Kursauftrags ist der Benutzer direkt im Orchestrator-Chat oder Hermes im Namen des Benutzers.

1. Der Benutzer klärt Spec, Korrekturen und Freigaben direkt mit dem Orchestrator oder mit Hermes.
2. Hermes übergibt genau einen konsolidierten Auftrag an den Orchestrator und beauftragt nie selbst einen Spezialisten.
3. Nur der Orchestrator beauftragt Fach-, Didaktik-, Quiz-, Design-, Review- und Moodle-Rollen.
4. Spezialisten beauftragen keine anderen Rollen. Sie melden Ergebnis, Nachweise, Abhängigkeiten und Blocker an den Orchestrator zurück.
5. Der Orchestrator verifiziert und konsolidiert die Ergebnisse und meldet nur Meilensteine, echte Blocker und Benutzergates an den Auftraggeber, auf dem Weg, auf dem der Auftrag kam.
6. Rückfragen an den Benutzer und Benutzerfreigaben laufen nur über den Orchestrator und den Auftraggeber. Ein Spezialist fragt den Benutzer nicht selbst, sondern meldet die fehlende Angabe an den Orchestrator.

## Ketten

Ein Kurslauf besteht aus drei Ketten (`docs/mbz-workflow.md`, Abschnitt Ketten). Jede Kette umfasst höchstens zwei Wellen aus Auftrag und Rückmeldung und endet mit aktualisierter `STATUS.json` und einer Meldung an den Auftraggeber. Die nächste Kette beginnt erst mit einem neuen Turn des Auftraggebers („weiter“). Jedes Benutzergate beendet die laufende Kette ebenfalls.

Bleibt das Urteil nach der einen Korrekturwelle und dem Delta-Review `REJECTED`, delegiert der Orchestrator nicht weiter und meldet ein Benutzergate.

## Transport Rules

- Ein Spezialist führt keinen direkten Produktionsauftrag von Hermes, dem Benutzer oder einem anderen Spezialisten aus, sondern verweist auf den Orchestratorweg.
- Eine substanzielle Fertigmeldung darf bei aktivem Auftrag nicht mit `[SILENT]` enden.
- Der Reviewer delegiert keine Korrekturen.
- Hop-Limits werden nicht erhöht und nicht durch Umgehungsketten kompensiert.
- Die Topologie bleibt bei einer Spezialistenebene plus Rückmeldung.
- `STATUS.json` und die kanonischen Projektdateien sind die verbindliche Zustandsquelle.

## Pitfalls

- Eine Antwort im lokalen Bot-Chat ist nicht automatisch eine Rückmeldung an den ursprünglichen Auftraggeber. Endete der ursprüngliche Auftragsturn bereits, muss der Orchestrator den später abgeschlossenen Meilenstein genau einmal aktiv per `message_agent(expects_reply=false)` an Hermes zurückmelden, wenn Hermes der Auftraggeber ist. Kam der Auftrag vom Benutzer direkt, steht der Wiederaufnahmepunkt in `STATUS.json` (`next_action`) und in der nächsten Antwort im Orchestrator-Chat. Nur die finale Antwort im noch laufenden ursprünglichen Hermes-Auftrag wird automatisch zurücktransportiert.
- Ein technischer PASS ersetzt weder Reviewer-APPROVED noch Benutzerfreigabe. Bei MBZ folgt der finale Bau auf APPROVED ohne weitere Benutzerfreigabe; bei MCP bleibt sie vor jedem Schreiben Pflicht.
- Direkte Spezialistenbeauftragung durch Hermes behebt keinen Transportfehler, sondern verletzt die Steuerungskette.

## Verification

Vor Abschluss prüfen:

- Der Auftrag kam über den vorgesehenen Vorgänger der Kette (Orchestrator: vom Benutzer direkt oder von Hermes; Spezialist: vom Orchestrator).
- Keine Spezialistenrolle hat eine andere Rolle beauftragt.
- Ergebnis und Nachweise wurden an den Orchestrator zurückgegeben.
- Offene Benutzergates wurden vom Orchestrator an den Auftraggeber gemeldet.
