# Test 01 – Bot-Kommunikation

In der Hermes-App in einem neuen Chat des Profils `orchestrator` eingeben (der
Benutzer ist Auftraggeber, `hermes` ist nicht beteiligt). Nicht per
`hermes -p orchestrator chat`: In CLI-Sitzungen fehlt `message_agent`, der
Orchestrator kann dort keinen Agenten erreichen.

Dies ist ein Erreichbarkeitstest, kein Kursauftrag.
Frage `didaktik`, `fiae`, `quiz` und `visual-designer` in **einer** gebündelten
Nachricht nach ihrem Status.

Jeder Agent soll nur antworten:

`<ROLLE> BEREIT`

Fasse die Antworten anschliessend zusammen.
Moodle darf nicht angesprochen werden.

Erwartet: ein `message_agent`-Aufruf mit vier Zielen, vier Antworten, keine
weitere Delegation. `max_hops` wird nicht verändert. Ein Fehlversuch verbraucht
trotzdem einen Hop; danach mit einer neuen Benutzernachricht neu starten.
