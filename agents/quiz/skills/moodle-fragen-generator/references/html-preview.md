# HTML-Vorschau – optionale Gestaltungsvorlage

Rangfolge: Projekt-`AGENTS.md` → `agents/quiz/SOUL.md` → `../SKILL.md` → diese Referenz.
Ob eine Vorschau entsteht, entscheidet `../SKILL.md` (Schritt 6). „Verbindlich“ heißt
unten: verbindlich, wenn eine Vorschau gebaut wird.

Nur bei tatsächlich benötigter Vorschau lesen. Die folgenden
Gestaltungsangaben sind eine Vorlage, keine zusätzlichen Abnahmekriterien.
Bestehende Projekt-Templates und konkrete Benutzerwünsche haben Vorrang.

## Technische Rahmenbedingungen
- Einzelne `.html`-Datei, kein externes CSS/JS
- Lokale Systemschriften oder vorhandene Projektfonts; keine neuen externen Font-Abhängigkeiten.
- Hintergrund der Seite: `#e9eaec`

## CSS-Variablen (verbindlich)
```css
--moodle-orange: #f98012;
--moodle-orange-dark: #d4600a;
--moodle-blue: #0f6cbf;
--moodle-blue-light: #e8f4fd;
--moodle-green: #1d7a1d;
--moodle-green-light: #d4edda;
--moodle-red: #ca3120;
--moodle-red-light: #fde8e6;
--moodle-gray: #6a737b;
--moodle-gray-light: #f3f3f3;
--moodle-border: #dee2e6;
--moodle-text: #1d2125;
--moodle-white: #ffffff;
--radius: 4px;
--shadow: 0 1px 3px rgba(0,0,0,.12), 0 1px 2px rgba(0,0,0,.08);
```

## Fragetyp-Badge-Farben (verbindlich)
| Typ | Klasse | Hintergrund | Textfarbe | Rahmen |
|-----|--------|-------------|-----------|--------|
| multichoice | `.type-mc` | `#e8f4fd` | `#0f6cbf` | `#0f6cbf` |
| ddwtos | `.type-dnd` | `#f0fdf4` | `#166534` | `#166534` |
| ddmatch | `.type-match` | `#fefce8` | `#854d0e` | `#ca8a04` |
| cloze | `.type-cloze` | `#fdf4ff` | `#6b21a8` | `#9333ea` |

## Seitenstruktur (verbindlich)
1. **`<header class="site-header">`** – orangefarbene Kopfleiste (Höhe 52px, `background: var(--moodle-orange)`)
   - Links: Logo „moodle Vorschau" (weiß, bold)
   - Rechts: Breadcrumb-Text mit Kurs/Thema (klein, halbtransparent weiß)

2. **`<div class="quiz-header">`** – weißer Metabereich unter Header
   - Emoji-Icon-Box (48×48px, orange), Quiz-Titel (h1), Untertitel (Klasse · Niveau · Anzahl)
   - Rechts: Badges für Zeitangabe und Gesamtpunkte
   - **Zeitangabe:** Den freigegebenen Testslot aus Auftrag/Didaktik anzeigen.
     Aufgabenrichtzeiten einschließlich Orientierung und Endkontrolle dagegen
     prüfen; keine pauschale Zwei-Minuten-pro-Frage-Berechnung verwenden.

3. **`<div class="main-wrap">`** – 2-Spalten-Grid (`1fr 220px`), max-width 900px, zentriert
   - **Linke Spalte**: `.questions` – alle Fragekarten gestapelt
   - **Rechte Spalte**: `.sidebar` – sticky, weiße Karte

4. **Sidebar** (sticky, `top: 20px`):
   - Überschrift „Fragennavigation" (uppercase, grau)
   - `.q-nav`-Grid (5 Felder pro Zeile, 34×34px Quadrate)
     - Standard: `background: var(--moodle-gray-light)`, `border: 1px solid var(--moodle-border)`
     - Aktiv/beantwortet: `background: var(--moodle-orange)`, weiß, orange Rahmen
     - Hover: `background: var(--moodle-blue-light)`, blau
   - Kursinfos (Kurs, Klasse, Fragen, Punkte) in kleiner Schrift
   - Fortschrittsbalken mit Label „Fortschritt: X/N"

5. **Fragekarten** `.question-card`:
   - `background: white`, `border: 1px solid var(--moodle-border)`, `border-radius: 4px`, `box-shadow: var(--shadow)`
   - **Card-Header** (`.question-header`): grauer Hintergrund (`var(--moodle-gray-light)`), Trennlinie unten
     - Orangefarbene Nummerierung (`.q-num`), Titel, Fragetyp-Badge, Punktzahl rechts
   - **Card-Body** (`.question-body`): `padding: 20px 22px`
   - **Card-Footer** (`.question-footer`): grauer Hintergrund, klein, Status links / Typ rechts

6. **Lehrkraft-Werkzeuge (Pflicht, Sidebar-Karte):** Die HTML-Vorschau richtet sich an Lehrkräfte. In der Sidebar muss eine Karte „Lehrkraft-Werkzeuge" mit folgenden Buttons vorhanden sein:
   - **„Lösung anzeigen / Lösung verbergen"** – Toggle-Schalter. Bei Aktivierung werden alle korrekten Antworten visuell hervorgehoben (grüner Rahmen/Hintergrund), bei Deaktivierung wird der Ausgangszustand wiederhergestellt.
   - **„Neu beginnen"** – Setzt das gesamte Quiz in den Ausgangszustand zurück: alle Auswahlen, Feedback-Boxen, DnD-Zuordnungen, Fortschrittsanzeige und Navigations-Markierungen werden gelöscht. Ermöglicht der Lehrkraft, die Vorschau erneut durchzuspielen.
   - **Keine Submit-/Abschließen-Leiste** – die Vorschau ist kein echtes Quiz.

## Interaktivität (verbindlich, via inline JavaScript)

### Multiple Choice (`multichoice`)
- **Indikator-Typ:** Bei `<single>true</single>` (Einfachauswahl) → **Kreis** (Radio-Button-Optik, `border-radius:50%`). Bei `<single>false</single>` (Mehrfachauswahl) → **Quadrat** (Checkbox-Optik, `border-radius:3px`). Der Indikator muss den tatsächlichen Fragetyp widerspiegeln.
- Antwortoptionen als `.answer-option` mit linkem Indikator (`.answer-indicator`)
- **Einfachauswahl (`single=true`):** Klick → sofortige visuelle Auswertung (kein separater Check-Button):
  - Richtig: `.correct` → `background: var(--moodle-green-light)`, grüner Rahmen, ✓ im Indikator
  - Falsch: `.incorrect` → `background: var(--moodle-red-light)`, roter Rahmen, ✗ im Indikator
  - Alle anderen Optionen werden deaktiviert (`onclick = null`)
- **Mehrfachauswahl (`single=false`) — KRITISCH:**
  - Klick auf eine Option **togglet** nur den Auswahlstatus (`.selected`-Klasse + Häkchen im Indikator). Es findet **keine sofortige Auswertung** statt!
  - Unter den Optionen erscheint ein Button **„Antwort prüfen"**, der erst nach Klick die Auswertung durchführt.
  - Bei Auswertung: alle ausgewählten richtigen Optionen → `.correct`, alle ausgewählten falschen → `.incorrect`, nicht ausgewählte richtige → grüner Rahmen als Hinweis.
  - **Niemals** bei Klick auf eine einzelne Option automatisch alle anderen korrekten Antworten aufdecken!
- Feedback-Box (`.feedback-box`) erscheint animiert darunter (`.show`)
- Status-Feld im Footer wechselt zu „Beantwortet" (grün)

### Drag & Drop in Text (`ddwtos`) – Click-basiert
- Begriffe aus Pool (`.drag-chip`) per Klick auswählen (blauer Outline-Rahmen)
- Lücken (`.drop-slot`) per Klick befüllen
- Button „Antwort prüfen" → Lücken färben sich grün (`.correct-slot`) oder rot (`.wrong-slot`)
- Verwendete Chips erhalten `.used` (ausgegraut, nicht klickbar)
- Bereits belegte Lücken können durch erneute Auswahl überschrieben werden (alter Chip wird freigegeben)

### Zuordnung (`ddmatch`)
- `<select>`-Dropdowns in Tabelle (`.match-table`)
- Bei jeder Änderung sofortige Prüfung: `.correct-select` (grün) oder `.wrong-select` (rot)
- Wenn alle Felder ausgefüllt: Gesamt-Feedback-Box erscheint

### Lückentext/Cloze (`cloze`)
- `<select>`-Elemente inline im `<pre>`-Block (`.cloze-select`)
- Bei jeder Änderung sofortige Prüfung: `.correct-cloze` oder `.wrong-cloze`
- Wenn alle Felder ausgefüllt: Gesamt-Feedback-Box erscheint

### Gemeinsame Feedback-Box
```
.feedback-box.correct  → background: var(--moodle-green-light), border-left: 4px solid var(--moodle-green)
.feedback-box.incorrect → background: var(--moodle-red-light),  border-left: 4px solid var(--moodle-red)
.feedback-box.info      → background: var(--moodle-blue-light),  border-left: 4px solid var(--moodle-blue)
```
Einblendung via `animation: fadeIn .2s ease` (translateY -4px → 0).

### Fortschritt & Navigation
- `markAnswered(n)`: setzt Nav-Quadrat auf orange, inkrementiert Zähler, aktualisiert Fortschrittsbalken

## Code-/Pre-Darstellung
```css
pre {
  font-family: 'Source Code Pro', monospace;
  font-size: 13px;
  background: #1e1e2e;   /* dunkles Terminal-Dunkelblau */
  color: #cdd6f4;
  border-radius: 4px;
  padding: 16px 18px;
  overflow-x: auto;
  line-height: 1.7;
}
code {
  font-family: 'Source Code Pro', monospace;
  font-size: 13px;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 3px;
  padding: 1px 5px;
}
```

## Responsive
- Unterhalb 700px: einspaltig (Sidebar unter Fragen, `position: static`)
- Quiz-Badge-Leiste im Header wird ausgeblendet

## Darstellung von Antworten und Grafiken

- Richtige und falsche Antworten nicht in fester Reihenfolge zeigen (etwa erst alle
  richtigen), sondern gemischt wie in Moodle.
- SVGs skalierbar halten: `svg { max-width: 100%; height: auto; }`.
- Korrekte deutsche Umlaute auch in der Vorschau.

