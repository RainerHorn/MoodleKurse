# Moodle-Quiz-XML-Vorlagen

Nur den Katalog und den Abschnitt zum benötigten Fragetyp lesen. Rangfolge:
Projekt-`AGENTS.md` → `agents/quiz/SOUL.md` → `../SKILL.md` → diese Vorlagen.
Regeln, die für mehrere Fragetypen gelten (Fragentitel-Tag, CDATA, SVG, Bepunktung,
Lösungsneutralität), stehen einmal in `../references/authoring-details.md` und werden
hier nicht wiederholt. Alte Import-Workarounds nur bei bestätigter Notwendigkeit anwenden.

## Katalog

| Vorlage | Fragetyp | Verwendung |
|---|---|---|
| `template-multichoice-mehrfachauswahl.xml` | multichoice | Eine oder mehrere richtige Antworten |
| `template-multichoice-mit-svg.xml` | multichoice + SVG | Multiple Choice mit Workflow-Diagramm |
| `template-ddmatch-zuordnung.xml` | ddmatch | Zuordnung (links ↔ rechts) |
| `template-ddmatch-zuordnung-mit-svg.xml` | ddmatch + SVG | Zuordnung mit geometrischen Formen |
| `template-ddwtos-lueckentext.xml` | ddwtos | Lückentext mit Drag-and-drop |
| `template-ddwtos-lueckentext-mit-svg.xml` | ddwtos + SVG | Lückentext mit Prozessdiagramm |
| `template-gapselect-lueckentextauswahl.xml` | gapselect | Lückentext mit Dropdown-Auswahl |
| `template-cloze-eingebettete-antworten.xml` | cloze | Eingebettete Antworten |
| `template-cloze-mit-svg.xml` | cloze + SVG | Cloze mit Flussdiagramm |
| `template-numerical-numerisch.xml` | numerical | Zahl mit Toleranz |
| `template-ordering-anordnung.xml` | ordering | Elemente in die richtige Reihenfolge bringen |
| `template-ddimageortext-drag-auf-bild.xml` | ddimageortext | Drag-and-drop auf ein Bild |
| `template-ddimageortext-drag-auf-svg.xml` | ddimageortext + SVG | Drag-and-drop auf eine SVG-Grafik |
| `template-coderunner-java.xml` | coderunner | Java-Aufgabe |
| `template-coderunner-java-background-class.xml` | coderunner | Java mit vorgegebener Hintergrundklasse |
| `template-coderunner-python-background-class.xml` | coderunner | Python mit vorgegebener Hintergrundklasse |
| `template-stackaufgabe_algorithmik.xml` | stack | STACK-Aufgabe |

`ddmatch`, `coderunner` und `stack` sind Plugin-Fragetypen. Was der MBZ-Baucontainer kennt,
steht in `platform/mbz-capabilities.json`; ein dort fehlender Typ wird als Plugin-Bedarf
gemeldet, nicht ersetzt. `ordering` gehört seit Moodle 4.4 zum Kern
([Releasenotes](https://moodledev.io/general/releases/4.4)).

## Verwendung

Vorlage in den Ausgabepfad des Auftrags kopieren (Standard `04-quiz/` im Kursordner), alle
Platzhalter in eckigen Klammern ersetzen (`[TITEL DER AUFGABE]`, `[Begriff 1]` …) und die
XML-Struktur samt CDATA-Blöcken unverändert lassen. Mehrere `<question>`-Blöcke dürfen in
einer Datei stehen. Importiert wird nicht durch den Quiz-Agenten.

## Hinweise je Fragetyp

### ddmatch (Zuordnung)

Distractor ohne Zuordnung: Unterfrage mit leerem Text, die Antwort erscheint als Falschoption.

```xml
<subquestion format="html">
  <text><![CDATA[<p></p>]]></text>  <!-- leer -->
  <answer format="html">
    <text><![CDATA[<p>MIDI-Controller</p>]]></text>
  </answer>
</subquestion>
```

### ddwtos (Lückentext mit Drag-and-drop)

`[[n]]` verweist auf die n-te `<dragbox>` im gesamten XML, nicht auf die Gruppe. Zuerst die
richtigen Begriffe in der Reihenfolge der Lücken, danach die Distractors; `<group>` legt nur
fest, in welche Lücke ein Begriff passt. Vollständige Regeln (auch `<infinite/>`):
`../references/authoring-details.md`, Abschnitt `ddwtos`.

```xml
<p>Ein Prozess besteht aus mehreren [[1]]. Das Ergebnis wird über die [[2]] ausgegeben.</p>

<dragbox><text>Arbeitsschritten</text><group>1</group></dragbox>  <!-- [[1]] -->
<dragbox><text>Schnittstelle</text><group>2</group></dragbox>     <!-- [[2]] -->
<dragbox><text>Komponenten</text><group>1</group></dragbox>       <!-- Distractor für Lücke 1 -->
<dragbox><text>Eingabeeinheit</text><group>2</group></dragbox>    <!-- Distractor für Lücke 2 -->
```

### gapselect (Lückentext mit Dropdown)

Wie `ddwtos`, nur mit Dropdown in der Lücke: `[[n]]` verweist auf die n-te `<selectoption>`
im gesamten XML. Richtige Optionen zuerst, Distractors danach; `<group>` bestimmt, welche
Optionen im Dropdown einer Lücke erscheinen. `<shuffleanswers>` mischt die Anzeige.

```xml
<p>Ein Quadrat hat [[1]] Ecken und [[2]] Symmetrieachsen.</p>

<selectoption><text>4</text><group>1</group></selectoption>  <!-- [[1]] -->
<selectoption><text>4</text><group>2</group></selectoption>  <!-- [[2]] -->
<selectoption><text>3</text><group>1</group></selectoption>  <!-- Distractor für Lücke 1 -->
<selectoption><text>2</text><group>2</group></selectoption>  <!-- Distractor für Lücke 2 -->
```

### multichoice

`<single>true</single>` für Einzelauswahl (eine Antwort mit `fraction="100"`),
`<single>false</single>` für Mehrfachauswahl. Gewichte, Abzüge und Formulierungsregeln:
`../references/authoring-details.md`, Abschnitte `multichoice` und „Bepunktung“.

```xml
<single>false</single>
<answer fraction="50" format="html"><text><![CDATA[<p>Kreise haben keine Ecken</p>]]></text></answer>
<answer fraction="50" format="html"><text><![CDATA[<p>Quadrate haben vier gleich lange Seiten</p>]]></text></answer>
<answer fraction="-25" format="html"><text><![CDATA[<p>Dreiecke haben vier Ecken</p>]]></text></answer>
```

### numerical

```xml
<answer fraction="100" format="moodle_auto_format">
  <text>42</text>
  <tolerance>0.5</tolerance>  <!-- akzeptiert 41.5 bis 42.5; 0 = nur exakt -->
</answer>
```

Grenzwerte und konservative Rundung: `../references/authoring-details.md`.

### cloze (eingebettete Antworten)

Syntax `{PUNKTE:FRAGETYP:ANTWORTEN}`; `=` markiert die richtige Antwort, `~` trennt Antworten,
`%PROZENT%` verteilt Punkte bei MULTIRESPONSE, `:TOLERANZ` gilt bei NUMERICAL.

| Typ | Beispiel |
|---|---|
| MULTICHOICE | `{1:MULTICHOICE:=Richtig~Falsch1~Falsch2}` |
| MULTIRESPONSE | `{2:MULTIRESPONSE:~%33.33%Rot~%33.33%Gelb~%33.33%Blau~%-100%Grün}` |
| NUMERICAL | `{1:NUMERICAL:=42:0.1}` |
| SHORTANSWER | `{1:SHORTANSWER:=Berlin~=Berlin (Stadt)}` |
| SHORTANSWER_C | `{1:SHORTANSWER_C:=Linux}` |

Kurzantworten sind nur so erlaubt, eingebettet in `cloze`; der eigenständige Fragetyp
`shortanswer` wird nicht verwendet. Regeln dazu: `../references/authoring-details.md`,
Abschnitt `cloze`.

### ordering (Anordnung)

Die Reihenfolge der `<answer>`-Elemente im XML ist die richtige Reihenfolge; Moodle mischt
bei der Anzeige. `fraction` ist die Position (1, 2, 3 …), `<md5key>` bleibt leer.
Einstellungen sind Zahlen, kein Text (`<layouttype>0</layouttype>`, nicht `VERTICAL`).

```xml
<question type="ordering">
  <shuffleanswers>1</shuffleanswers>
  <layouttype>0</layouttype>   <!-- 0 = vertikal, 1 = horizontal -->
  <selecttype>0</selecttype>   <!-- 0 = alle anzeigen -->
  <selectcount>0</selectcount> <!-- 0 = alle Elemente -->
  <gradingtype>0</gradingtype>
  <showgrading>1</showgrading>
  <answer fraction="1" format="html">
    <text><![CDATA[<p>Schritt 1: Planung</p>]]></text>
    <feedback format="html"><text></text></feedback>
    <md5key></md5key>
  </answer>
  <answer fraction="2" format="html">
    <text><![CDATA[<p>Schritt 2: Durchführung</p>]]></text>
    <feedback format="html"><text></text></feedback>
    <md5key></md5key>
  </answer>
</question>
```

`gradingtype`: `0` alles oder nichts, `1` Punkte je richtig platziertem Element,
`2` längste zusammenhängende Teilfolge, `3` längste korrekte Teilsequenz.

### ddimageortext (Drag-and-drop auf ein Bild)

1. **Bild:** PNG, JPG oder SVG, 600 bis 800 px breit; für Diagramme SVG.
2. **Base64:** Das Bild steht als Datei im XML; der Name einer SVG muss `background.svg`
   lauten, `path="/"` muss gesetzt sein.

   ```powershell
   $bytes = [System.IO.File]::ReadAllBytes("C:\pfad\zum\bild.png")
   [Convert]::ToBase64String($bytes) | Out-File -Encoding ASCII base64.txt
   ```

   ```xml
   <file name="background.svg" path="/" encoding="base64">BASE64-STRING-HIER</file>
   ```

3. **Koordinaten:** `xleft`/`ytop` sind die linke obere Ecke der Drop-Zone in Pixeln.
   Bei einem Nummernkreis `<circle cx="200" cy="63" r="11"/>` gilt `xleft = cx − r = 189`,
   `ytop = cy − r = 52`; bei einem Rechteck `xleft = x`, `ytop = y`.
4. **Struktur:**

   ```xml
   <drag>
     <no>1</no>
     <text><![CDATA[Begriff 1]]></text>
     <draggroup>1</draggroup>
     <infinite/>  <!-- optional: mehrfach verwendbar -->
   </drag>
   <drop>
     <text></text>
     <no>1</no>
     <choice>1</choice>  <!-- verweist auf drag no="1" -->
     <xleft>189</xleft>
     <ytop>52</ytop>
   </drop>
   ```

5. **Abstände:** Moodle zeigt jedes Label als schwebende Box an der Drop-Position.
   Mindestens 80 px vertikal und 150 px horizontal zwischen Drop-Zonen, höchstens eine Zone
   je 80 × 40 px. Nummernkreise an Ränder von Rechtecken, in leere Außenbereiche oder
   entlang von Pfeilen setzen, nicht über Text, Formen oder Pfeilspitzen.
6. **Distractors:** `<drag>` ohne zugehörige `<drop>`-Zone. Im Fragetext ankündigen
   („Es gibt 2 zusätzliche Begriffe, die nicht passen.“); entfällt der Distractor, auch den
   Satz streichen.
7. **Zeichenfläche:** bis 4 Zonen 420 × 200 px, 5 bis 6 Zonen 600 × 400 px, ab 7 Zonen oder
   bei breiten Labels 780 × 520 px.

Prüfliste: jedes `<drag>` hat eine eindeutige `<no>`; jedes `<drop>` verweist über `<choice>`
auf ein vorhandenes `<drag>`; Koordinaten liegen innerhalb des Bildes; Abstände eingehalten;
Distractors angekündigt.

### coderunner

Die drei Vorlagen enthalten den vollständigen Aufbau. Regeln für Hintergrundklassen,
Python-Template, CDATA in `<template>` und `<expected>` sowie die Liste der Typen:
`../references/authoring-details.md`, Abschnitte `coderunner`.

| Fehler in der Sandbox | Ursache | Lösung |
|---|---|---|
| `IndentationError` | Python-Template eingerückt | `<template>` ohne führende Leerzeichen am Zeilenanfang beginnen |
| `cannot find symbol` (Hintergrundklasse) | Klasse steht nur in `<globalextra>` | Eigenes `<template>` in `python3`, das alle Klassen schreibt und gemeinsam mit `javac` kompiliert |
| `Could not allocate compressed class space` | 64-Bit-Java fordert 1 GB Class Space an | `javac -J-Xmx128m -J-XX:CompressedClassSpaceSize=64m`, `java -Xmx128m -XX:CompressedClassSpaceSize=64m` |

## Fehlersuche

| Fehler | Ursache | Lösung |
|---|---|---|
| Import schlägt fehl | XML nicht wohlgeformt | Lokal parsen (Skript in `authoring-details.md`, „Validierung“); Tags, CDATA und UTF-8 prüfen |
| n Fragen erkannt, 0 importiert | Eine fehlerhafte Frage bricht den gesamten Import ab | Fragen einzeln prüfen |
| Umlaute falsch dargestellt | Datei nicht als UTF-8 gespeichert | UTF-8 ohne BOM schreiben |
| `ParseError: undefined entity` | Benannte Entity außerhalb CDATA | UTF-8 direkt, CDATA oder numerische Entity |
| „String erwartet (CDATA?)“ | HTML in `<text>` ohne CDATA | `<text><![CDATA[<p>…</p>]]></text>` |
| `ParseError: not well-formed` | `--` in einem XML-Kommentar | Zierlinien mit `==` schreiben |
| multichoice: Gewichte ergeben nicht 100 % | Positive `fraction`-Werte falsch verteilt | Zwei richtige: 50 + 50; drei richtige: 33.33 + 33.33 + 33.34 |
| multichoice: Option wird nicht angezeigt | Antworttext beginnt mit `+`, `-` oder `~` | Umformulieren, z. B. „positiv (+)“ |
| ddwtos/gapselect: falsche Lösung gilt als richtig | Richtige Antwort steht nicht an Position n | Richtige Einträge zuerst in Lückenreihenfolge, Distractors danach |
| `<infinite/>` wirkt nicht | Falsche Stelle oder Wert im Tag | Leeres Tag `<infinite/>`: bei ddimageortext in `<drag>`, bei ddwtos in `<dragbox>` |
| ddimageortext: Bild erscheint nicht | Dateiname oder Base64 fehlerhaft | Name `background.svg`, `path="/"`, Base64 neu erzeugen |
| ddimageortext: Koordinaten falsch | `xleft`/`ytop` falsch berechnet | Kreis (r = 11): `cx − 11`, `cy − 11`; Rechteck: `x`, `y` |
| ddimageortext: Labels überlappen oder verdecken das Diagramm | Zonen zu nah oder über Inhalt | Abstände einhalten, Kreise in Leerräume setzen |
| ordering: „String erwartet“ | Einstellung als Text statt Zahl | `<layouttype>0</layouttype>` |
| ordering: Importfehler | Fragetyp oder Importweg ungeklärt | Tatsächlichen Fehler prüfen; keinen Versionsfehler vermuten |
| SVG-Pfeil rotiert falsch, Vererbungspfeil zeigt falsch | Marker oder Linienrichtung | `authoring-details.md`, „Marker/Pfeile“ |
| Base64-Bild zu groß | Bild unkomprimiert | PNG komprimieren, JPEG-Qualität senken oder SVG verwenden |

## Quellen

- [Moodle-4.5-XML-Format](https://docs.moodle.org/405/en/Moodle_XML_format)
- [Moodle: Fragetypen](https://docs.moodle.org/en/Question_types)
- [SVG-Tutorial (MDN)](https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial)
