# Modellvergleich nach Messwerten (Backlog IMP-17)

Gilt nur für eine ausdrücklich beauftragte Prozess- oder Modellanalyse. Im
normalen Kursauftrag wird nichts gemessen (`pruefstrategie.md`, Abschnitt 5).
Dieser Text stand bis zum 15.11.2026 in `produktionsablauf.md`.

Erst verbleibenden Engpass bestimmen: Modellarbeit, Tools/Tests, menschliche
Wartezeit und Korrekturen getrennt erfassen. Vorhandene Events des Prüf-Runners liefern
Tooldaten; für tatsächliche Rollenläufe `_templates/prozess/modellmessung.json`
einmal aus vorhandenen Zeitstempeln/Protokollen ergänzen. Fehlende Werte bleiben
null, keine neue Agentenschleife nur für Telemetrie.

Ein Rollenvergleich hält Eingaben, Quellen, Werkzeuge, Qualitätskriterien und
Aufgabenkomplexität vergleichbar. Modellkennung, Prompt-/Regelstand, Wiederholungen
und Qualitätsbefund festhalten; keine Modelllatenz aus gesamter Paketdauer ableiten.
Vor einem Vergleich Stichprobe und Entscheidungskriterium passend zum Engpass
festlegen. Korrekturzeit und Blocker zählen mit. Ein einzelner schneller Lauf
begründet keine Migration. Modelle erst bei belastbarem Vorteil und ausdrücklich
beauftragtem Wechsel ändern. IMP-17 bleibt bis zu echten Vergleichsdaten offen.
