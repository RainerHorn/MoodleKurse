# Test 01 – Bot-Kommunikation

Direkt im Orchestrator-Chat eingeben (der Benutzer ist Auftraggeber, `hermes` ist
nicht beteiligt):

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
