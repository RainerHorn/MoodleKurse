# Fachdetails und erprobte Sonderfälle

Diese Datei ist eine vertiefende Referenz. Die übergeordnete `../SKILL.md`, `agents/quiz/SOUL.md` und das Projekt-`AGENTS.md` haben Vorrang. Aussagen wie „Pflicht“ gelten nur, soweit sie diesen Quellen und der bestätigten Moodle-/Plugin-Konfiguration nicht widersprechen.

Nur den Abschnitt zum passenden Spezialfall lesen. Ablauf und Kernregeln stehen in
`../SKILL.md`, XML-Struktur in `moodle-xml-structure.md`, Vorlagen und Fehlersuche in
`../templates/README.md`, die optionale Vorschau in `html-preview.md`. Auftrag, aktueller
Status und vorhandene Prüfnachweise haben Vorrang vor den Beispielen hier.

## Moodle-XML Pflichtregeln

### Fragentitel-Tag (kritisch, häufige Fehlerquelle)
- Der Tag für den Fragentitel heißt wörtlich `name` (vier Buchstaben), nicht `n`:
  `<name><text>Mein Fragetitel</text></name>`. Mit einem falschen Tag zeigt Moodle keinen Titel an.
- Tagnamen wörtlich schreiben; Zeichenreferenzen innerhalb eines Tagnamens sind unzulässig.
- Der Titeltext darf UTF-8 einschließlich Umlauten enthalten; XML-Sonderzeichen im Text escapen.
- Nach jeder XML-Erzeugung mit dem Skript im Abschnitt „Validierung“ prüfen.

### CDATA (kritisch)
- **Jedes** `<text>`-Element, das HTML enthält, **muss** in CDATA stehen:
  - `<questiontext><text>`: praktisch immer (enthält meist HTML/SVG)
  - `<answer><text>` / `<feedback><text>` / `<generalfeedback><text>`: sobald HTML-Tags wie `<p>`, `<code>`, `<strong>` etc. enthalten sind
- Vermeide Importfehler („String erwartet“), indem du konsequent so schreibst:
  - `<text><![CDATA[ ... HTML ... ]]></text>`
- Nicht nötig bei reinem Text, Zahlenwerten und Base64-Dateien.
- Benannte HTML-Entities (`&auml;`, `&nbsp;`, `&ndash;`) sind außerhalb von CDATA ein
  XML-Fehler („undefined entity“). Stattdessen UTF-8 direkt, CDATA oder numerische Entities (`&#228;`).
- CDATA lässt sich nicht verschachteln. Kommt `]]>` im Text vor, den Block teilen:
  `<![CDATA[Code: ]]]]><![CDATA[>]]>`.
- `--` ist in XML-Kommentaren unzulässig („not well-formed“); Zierlinien mit `==` schreiben.

### Deutsche Umlaute und Sonderzeichen (Pflicht)
- **Immer korrekte deutsche Umlaute verwenden:** ä, ö, ü, Ä, Ö, Ü, ß — niemals Ersatzschreibungen wie ae, oe, ue, ss.
- Innerhalb von CDATA-Blöcken sind alle Unicode-Zeichen sicher. Das XML-Encoding `UTF-8` in der Deklaration stellt die korrekte Verarbeitung sicher.
- Gilt für Fragetexte, Antwortoptionen, Feedbacks und Titel gleichermaßen.

### Fragetyp-spezifische Regeln
#### `ddmatch` (Zuordnung)
- Verwende `<subquestion>` + `<answer>` Paare.
- Wenn HTML in subquestion/answer: jeweils CDATA.

#### `ddwtos` (Drag-and-drop into text)
- Lücken: `[[1]]`, `[[2]]`, ...
- Für jede Lücke `[[n]]` müssen passende `<dragbox>`-Einträge mit `<group>n</group>` existieren.
- **Jede Gruppe braucht mindestens einen Distractor** (falsches Angebot).
- **`<dragbox>`-Struktur (Pflicht):**
  ```xml
  <dragbox>
    <text>Wort</text>
    <group>1</group>
  </dragbox>
  ```
- **Richtige Antwort = absolute Position im XML:** Bei `ddwtos` ist Lücke `[[1]]` = die **1. `<dragbox>` im gesamten XML**, Lücke `[[2]]` = die **2. `<dragbox>`**, usw. – unabhängig von der Gruppe. Die Gruppe bestimmt nur Farbe und welche Dragboxen in eine Lücke passen, **nicht** die Zuordnung zur Lücke. Distractoren kommen **nach** allen richtigen Antworten. Korrekte Reihenfolge:
  ```xml
  <!-- Richtige Antworten zuerst (Position = Lückennummer) -->
  <dragbox><text>extends</text><group>1</group></dragbox>       <!-- → [[1]] -->
  <dragbox><text>@Override</text><group>2</group></dragbox>     <!-- → [[2]] -->
  <dragbox><text>berechneFlaeche</text><group>3</group></dragbox> <!-- → [[3]] -->
  <!-- Distractoren danach -->
  <dragbox><text>implements</text><group>1</group></dragbox>
  <dragbox><text>@Overload</text><group>2</group></dragbox>
  <dragbox><text>getFlaeche</text><group>3</group></dragbox>
  ```
- **`infinite`-Flag (Pflicht korrekt!):** Moodle wertet `infinite` nach dem Prinzip `array_key_exists('infinite', ...)` aus – d.h. die **bloße Existenz** des Tags setzt das Flag auf true, egal welcher Wert drin steht.
  - Wort darf **mehrfach** verwendet werden → `<infinite/>` (leeres Tag)
  - Wort darf **nur einmal** verwendet werden → Tag **komplett weglassen** (kein `<infinite>0</infinite>`!)
  - `<infinite>0</infinite>` setzt infinite trotzdem auf true → **verboten**
  - `<infinite>1</infinite>` funktioniert **nicht zuverlässig** → immer `<infinite/>` verwenden
- **Lücken werden nur im Plaintext erkannt.** `[[n]]`-Syntax funktioniert in `format="html"` innerhalb von `<pre>`-Blöcken – aber niemals innerhalb von HTML-Attributen oder verschachtelten Tags.
- **`questiontext format="html"`** ist korrekt und ausreichend; `[[n]]` wird auch in HTML-CDATA erkannt.

#### `gapselect` (Lückentext mit Dropdown)
- Gleiche Nummerierung wie `ddwtos`: `[[n]]` verweist auf die **n-te `<selectoption>` im
  gesamten XML**. Zuerst die richtigen Optionen in der Reihenfolge der Lücken, danach die
  Distractors; `<group>` bestimmt nur, welche Optionen im Dropdown einer Lücke erscheinen.

#### `multichoice`
- Für Mehrfachauswahl: `<single>false</single>`.
- Punkte: richtige Antworten sollen zusammen **≈ 100%** ergeben (z. B. 2×50 oder 3×33.33333).
- Falsche Antworten können negative fractions haben (z. B. `-25`, `-50`).
- Antworttexte dürfen **nicht** mit `+`, `-`, `~` beginnen (Moodle-Sonderzeichen).
- **Antworttextlänge neutralisieren:** Die richtige Antwort darf **nicht erkennbar die längste** sein. Alle Distraktoren müssen eine ähnliche Länge und Detailtiefe haben wie die korrekte Antwort – sonst ist die Lösung durch reines Abzählen der Zeichen erratbar.
- **Mischung beachten (kritisch):** Moodle mischt die Antwortoptionen bei `<shuffleanswers>true</shuffleanswers>` zufällig. Daher dürfen Antworten **keine positionsabhängigen Formulierungen** enthalten (z. B. nicht „Alle oben genannten", „Antwort A und C sind richtig", „Die erste Aussage …"). Jede Antwortoption muss **eigenständig verständlich** sein, unabhängig davon, an welcher Stelle sie im Quiz angezeigt wird.

#### `cloze`
- Eingebettete Syntax im Fragetext, z. B.:
  - `{1:MULTICHOICE:Option1~Option2~=Richtig~Option3}`
- `=` markiert die richtige Option, `~` trennt Optionen.
- Kein zusätzliches `<defaultgrade>` nötig.
- **Kurzantworten nur eingebettet:** `SHORTANSWER` (Groß-/Kleinschreibung egal) und
  `SHORTANSWER_C` (Groß-/Kleinschreibung zählt) sind innerhalb von `cloze` erlaubt. Der
  eigenständige Fragetyp `shortanswer` wird nicht verwendet.
- Bei Kurzantworten jede zulässige Schreibweise als eigene richtige Antwort angeben
  (`{1:SHORTANSWER:=Berlin~=Berlin (Stadt)}`) und nur einsetzen, wenn die Antwort
  eindeutig und kurz ist; sonst `MULTICHOICE` oder `gapselect`.

#### Sourcecode in Aufgabentexten

Zum Format passende Darstellung verwenden: bei HTML mehrzeiligen Code als
`<pre><code>…</code></pre>` innerhalb von CDATA, bei Markdown einen Fenced-Code-Block
mit Sprachkürzel und `format="markdown"`. HTML-Inhalt korrekt escapen; Backticks
nicht unverarbeitet in HTML anzeigen. Inline-Bezeichner bei HTML als `<code>`.
Die gewählte Vorlage und Zielinstallation bestimmen das Rendering.

#### `coderunner` – Beispiele für Fragetypen
Die tatsächlich verfügbaren Typen/Prototypen der Zielinstallation sind maßgeblich.
Die folgende Liste ist keine Verfügbarkeitszusage und keine abschließende Whitelist:

| Typ | Verwendung |
|---|---|
| `java_class` | **Standard für Java-Aufgaben.** Schüler schreibt eine einzelne Klasse. |
| `java_method` | Schüler schreibt nur eine Methode (kein Klassenrumpf). |
| `java_program` | Schüler schreibt ein vollständiges Programm inkl. `main`. |
| `python3` | Python-3-Aufgaben. |
| `python3_w_input` | Python-3 mit `input()`-Aufrufen. |
| `python2` | Python-2-Aufgaben (Ausnahme, nur wenn explizit gefordert). |
| `c_function` | C – einzelne Funktion. |
| `c_program` | C – vollständiges Programm. |
| `cpp_function` | C++ – einzelne Funktion. |
| `cpp_program` | C++ – vollständiges Programm. |
| `php` | PHP-Aufgaben. |
| `sql` | SQL-Aufgaben. |
| `nodejs` | JavaScript/Node.js-Aufgaben. |
| `multilanguage` | Sprach-agnostische Aufgaben. |
| `pascal_function` | Pascal – einzelne Funktion. |
| `pascal_program` | Pascal – vollständiges Programm. |
| `octave_function` | Octave/MATLAB-Aufgaben. |
| `directed_graph` | Gerichtete Graphen. |
| `undirected_graph` | Ungerichtete Graphen. |

**Für alle Java-Vererbungsaufgaben gilt:** `<coderunnertype>java_class</coderunnertype>` – Schüler schreibt die Kindklasse, Elternklassen/Interfaces werden über das Python3-Template bereitgestellt.

#### `coderunner` – Java mit Hintergrundklassen (`java_class`)
- Wenn eine Elternklasse oder ein Interface vorgegeben werden soll (z. B. für Vererbung), darf dies **nicht** nur in `<globalextra>` stehen, da dies vom Java-Kompiler in der Sandbox nicht automatisch als ausführbare Datei erstellt wird.
- Stattdessen **muss ein eigenes `<template>` in `<language>python3</language>`** verwendet werden, das die Hintergrundklasse, den Studenten-Code und den Testfall explizit auf die Platte schreibt und zusammen kompiliert.
- **Kritisch für Java in Jobe-Sandbox:** Beim Aufruf von `javac` muss der JVM-Speicher limitiert werden, da die 64-Bit-Sandbox sonst oft beim Allokieren von 1 GB Class Space abstürzt (Fehler: `Could not allocate compressed class space`).
- Beispiel für das notwendige `os.system`-Kommando im Python-Template:
  `ret = os.system('javac -J-Xmx128m -J-XX:CompressedClassSpaceSize=64m -encoding UTF-8 AccountBase.java BankAccount.java Test.java 2>&1')`
  `if ret == 0: os.system('java -Xmx128m -XX:CompressedClassSpaceSize=64m -cp . Test')`
- Das Python-Template (`<template>`) in XML muss linksbündig (ohne führende Leerzeichen) beginnen, anderenfalls produziert der CodeRunner einen `IndentationError` in Python.
- **`<template>` muss immer in CDATA eingebettet sein:** `<template><![CDATA[\n ... \n]]></template>`. Ohne CDATA brechen `&`-Zeichen (z. B. in `-J-Xmx128m`) das XML.
- **Importerspezifische Felder:** Titeltext darf UTF-8 enthalten. Musterlösung und CodeRunner-Felder anhand eines Exports der bestätigten Zielinstallation bzw. passender Vorlage übernehmen. Frühere Fehler mit `<answer>` sind kein allgemeines Verbot für jede Plugin-/Importer-Version; den bestätigten Importvertrag beachten.
- **Separate XML-Dateien pro Aufgabe:** Nur wenn der konkrete Importweg dies nachweislich verlangt; andernfalls nach Auftrag bündeln. Jede Autoren-Datei erhält den Kategorieblock gemäß Hauptskill.
- **`<expected>` immer in CDATA:** Das `<expected><text>`-Element muss immer in CDATA eingebettet sein: `<expected><text><![CDATA[...]]></text></expected>`. Ohne CDATA führen Sonderzeichen (z. B. `–` U+2013, `|`, Umlaute) zu `mysqli`-Fehlern beim Import.
- **Kein `textwrap.dedent()` mit Triple-Quotes im Template:** Triple-Quote-Strings im Python-Template dürfen nicht zusammen mit `printf`-Formatstrings (`%s`, `%f`, `%n`) verwendet werden – Moodle's Template-Engine kann `%`-Sequenzen fehlinterpretieren. Stattdessen **immer einfache String-Konkatenation** verwenden:
  ```python
  # RICHTIG: String-Konkatenation
  src = (
      "public class Beispiel {\n"
      "    private String name;\n"
      "}\n"
  )
  # EINZIGE Ausnahme: student_src darf Triple-Quotes nutzen
  student_src = """{{ STUDENT_ANSWER }}"""
  ```

## SVG-Regeln (Inline im Fragetext)
- SVG immer inline im CDATA-Fragetext, mit:
  - `xmlns="http://www.w3.org/2000/svg"`
  - fixer `width`/`height` **und** `viewBox="0 0 <width> <height>"`
  - Style: `font-family:Arial,sans-serif;font-size:13px;display:block;margin:10px auto;`
- Das `viewBox`-Attribut ist zwingend erforderlich, damit die SVG bei kleinen Viewports proportional skaliert statt abgeschnitten zu werden.

### Marker/Pfeile
- Definiere Marker in `<defs>` und verwende sie per `marker-end="url(#id)"`.
- Für gestrichelte Beziehungen: `stroke-dasharray="6,3"`.
- Bewährte Marker (in `<defs>` am Anfang des SVG):
  ```xml
  <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L0,6 L9,3 z" fill="#333"/>
  </marker>
  <!-- Vererbung: hohles Dreieck; Linie startet bei der Kindklasse, marker-end zeigt zur Elternklasse -->
  <marker id="inherit" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L0,12 L12,6 z" fill="#fff" stroke="#333" stroke-width="2"/>
  </marker>
  ```
- Rotiert ein Pfeil falsch, `refX`/`refY` prüfen; für vertikale Pfeile hat sich
  `refX="7" refY="3"` mit `points="0 0,8 3,0 6"` bewährt.

### Netzwerktopologien – Cisco-Symbole (Pflicht)
- Bei **jeder** Netzwerktopologie-Darstellung (VLANs, Routing, Switching, IP-Netze, etc.) **müssen** die Symbole aus `assets/symbols/cisco/` verwendet werden.
- Verfügbare Symbole:
  | Datei | Symbol | viewBox | Empfohlene Rendergröße |
  |---|---|---|---|
  | `assets/symbols/cisco/router.svg` | Cisco Router (3D-Zylinder, blau) | `0 0 60 41` | `width="84" height="57"` |
  | `assets/symbols/cisco/switch.svg` | Cisco L2-Switch (3D-Gehäuse, blau) | `0 0 77 39` | `width="66" height="34"` |
  | `assets/symbols/cisco/pc.svg` | Cisco PC/Workstation (3D-Arbeitsplatz, blau) | `0 0 59 53` | `width="78" height="70"` |

- Weitere Symbole im selben Ordner (Rendergröße proportional zur viewBox wählen):
  `laptop.svg` (`0 0 68 47`), `layer-3-switch.svg` (`0 0 49 49`), `printer.svg` (`0 0 69 27`),
  `server.svg` (`0 0 33 48`), `wireless-router.svg` (`0 0 60 59.287`).

- **Einbettung: ausschließlich via Base64-`<image>`-Tag** (Pflicht, keine andere Methode):
  1. SVG-Datei binär lesen und als Base64 kodieren (Python: `base64.b64encode(data).decode()`)
  2. Data-URI bauen: `data:image/svg+xml;base64,<BASE64>`
  3. Im Topologie-SVG als `<image href="<DATA-URI>" x="..." y="..." width="..." height="..."/>` einsetzen

  **Python-Snippet (immer so verwenden):**
  ```python
  import base64

  symbols = {}
  for name in ['pc', 'switch', 'router']:
      with open(f'${HERMES_SKILL_DIR}/assets/symbols/cisco/{name}.svg', 'rb') as f:
          data = f.read()
      symbols[name] = 'data:image/svg+xml;base64,' + base64.b64encode(data).decode()

  PC = symbols['pc']
  SW = symbols['switch']
  RT = symbols['router']
  ```

  **Verwendung im SVG-String:**
  ```python
  svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="580" height="200" ...>
    <!-- PC bei (x=18, y=53), 78×70 px -->
    <image href="{PC}" x="18" y="53" width="78" height="70"/>
    <text x="57" y="134" text-anchor="middle" font-size="12" font-weight="bold">PC-A</text>
    <text x="57" y="147" text-anchor="middle" font-size="10" fill="#495057">192.168.1.10</text>

    <!-- Switch bei (x=158, y=71), 66×34 px -->
    <image href="{SW}" x="158" y="71" width="66" height="34"/>
    <text x="191" y="115" text-anchor="middle" font-size="12" font-weight="bold">SW-A</text>

    <!-- Router bei (x=252, y=61), 84×57 px -->
    <image href="{RT}" x="252" y="61" width="84" height="57"/>
    <text x="291" y="126" text-anchor="middle" font-size="12" font-weight="bold">Router R1</text>

    <!-- Verbindungslinien als <line>-Elemente -->
    <line x1="96" y1="88" x2="158" y2="88" stroke="#495057" stroke-width="2"/>
  </svg>'''
  ```

- **Ankerpunkte** (Mitte des Symbols, für Verbindungslinien-Berechnung):
  | Symbol | Horizontale Mitte | Vertikale Mitte (Anschluss) |
  |---|---|---|
  | PC (78×70) | x + 39 | y + 35 |
  | Switch (66×34) | x + 33 | y + 17 |
  | Router (84×57) | x + 42 | y + 28 |

- **Keine selbst gezeichneten** Primitive (Kreise, Rechtecke, etc.) für Geräte, für die ein Symbol vorliegt – ausschließlich die Cisco-Symbole via Base64-`<image>`.
- Trunk-Links und einfache Verbindungslinien werden als SVG-`<line>`-Elemente gezeichnet (kein Symbol notwendig).
- Labels (Gerätename, IP-Adresse) werden als `<text>`-Elemente **unterhalb** des Symbols platziert, vertikal versetzt: Name bei `symbol_y + symbol_height + 12`, IP bei `symbol_y + symbol_height + 24`.

### UML/Diagramm-Konsistenz
- Klassendiagramme:
  - Wenn Aggregation/Komposition gezeichnet ist, muss das passende Attribut in der „Ganzes"-Klasse modelliert sein (z. B. `tiere: Tier[]` für Komposition, `pfleger: Pfleger[]` für Aggregation).
  - **Auch die „Teil"-Klasse** trägt bei einer Assoziation (`→`) das passende Referenzattribut, wenn die Beziehung aus der Klasse heraus navigierbar sein soll (z. B. `pfleger: Pfleger` in `Tier`).
  - **Alle Attribute einheitlich formatieren:** Assoziationsattribute (Typ = Klassenname) dürfen **nicht kursiv oder grau** dargestellt werden — in UML gibt es keine Konvention, die Objektreferenzattribute optisch von primitiven Attributen unterscheidet.
  - **Bevorzugtes Layout:** Klassen, die über Aggregation/Komposition verbunden sind, horizontal nebeneinander anordnen. Die Raute (◆/◇) sitzt dabei **horizontal** zwischen Linie und Klassenbox — nicht als schräge Diagonale. Die Assoziation (`→`) zwischen Klassen auf gleicher Ebene wird als U-förmige Linie unterhalb der Boxen geführt.
  - Vererbung: Kindklasse dupliziert keine Attribute der Elternklasse.
  - Multiplizitäten stehen nahe an den Klassen, nicht in der Linienmitte.
- Use-Case:
  - Akteure **außerhalb** der Systemgrenze, Use-Cases **innerhalb**.
- Aktivität:
  - genau **ein** Startknoten, mindestens **ein** Endknoten.
  - Entscheidung hat ≥2 ausgehende Kanten mit Bedingungen `[Ja]`/`[Nein]` (oder sinngemäß).

## Qualitätsanforderungen

- Keine „unsichtbaren“ Beziehungen: wenn eine Beziehung im Diagramm existiert, muss sie in Text/Antworten nachvollziehbar sein.
- Keine unnötigen Features: Erzeuge genau die angeforderten Fragen und Fragetypen.

### Numerische Grenzwerte und konservative Rundung

Bei konservativ gerundeten Positionsfenstern auch die unmittelbar benachbarten,
nach außen gerundeten Werte prüfen. Eine pauschale numerische Toleranz darf kein
vergrößertes Fenster als voll richtig akzeptieren. Bei ausdrücklich geforderten
Hundertstel-Endwerten gegebenenfalls Toleranz 0 verwenden und begründen.
Nur bei Änderungen an Werten, Toleranzen oder Bewertungslogik neu prüfen (`pruefstrategie.md`).

### Druckbare Testbögen

Wenn druckbare HTML-Testbögen geliefert werden, echten PDF-Druckexport und
Seitenrendering zur Sichtprüfung verwenden: Leer-/Überlaufseiten, Pagination und
Antwortflächen kontrollieren. CSS-Seitenabschnitte allein sind kein Nachweis.
Ein bestehender Nachweis bleibt bei unverändertem Inhalt, Layout und Druckweg
verwendbar; keine zusätzlichen Druckprodukte allein zum Testen erzeugen.

Vorgehen für eine neue oder geänderte Druckfassung:
1. Erzeuge XML und Papier-HTML aus derselben internen Aufgabenquelle; vergleiche
   Fallangaben, Auftrag, Kriterien, Punkte und alle Auswahloptionen. Dropdowns
   dürfen auf Papier Ankreuzfelder werden, ihre Optionen und Teilpunkte nicht.
2. Drucke die lokale HTML-Datei etwa mit einem vorhandenen Chromium-Browser:
   `BROWSER --headless --disable-gpu --no-pdf-header-footer --user-data-dir=SCRATCHPROFIL --print-to-pdf=ABSOLUTES_ZIEL file:///ABSOLUTE_QUELLE`.
   Verwende einen separaten Profilpfad und prüfe den tatsächlichen PDF-Ausgang.
3. Extrahiere den Text mit `pdftotext -enc UTF-8 -layout TEST.pdf -` und vergleiche
   je echter PDF-Seite mit dem sichtbaren HTML. Berücksichtige vom Browser erzeugte
   Listenbuchstaben und schließe nicht gedruckte SVG-`title`/`desc`-Metadaten aus.
   Prüfe vollständige Textpassagen/Optionen; gleiche Zeichenhäufigkeiten allein
   beweisen weder Wortlaut noch Reihenfolge. Normalisiere keine fachlich relevanten
   Zahlen, Einheiten oder Zeichen weg.
4. Rendere die Seiten und prüfe Grafikbeschriftung, Ankreuzfelder und Schreibraum
   visuell. Bei Überläufen erst Abstände oder Optionsanordnung korrigieren, nicht
   unbemerkt Inhalte kürzen. Nach Korrekturen neue PDF erzeugen und die betroffenen
   Seiten erneut ansehen.
5. Halte PDF-Parität, visuelle Druckprüfung, geplante Bearbeitungszeit und späteren
   Moodle-Import/Schutz als getrennte Nachweise fest. Ein lokaler Parserlauf ersetzt
   keinen Moodle-Cloze-Import, eine Textprüfung keine Layoutprüfung.

### Bepunktung (`<defaultgrade>`) nach Blueprint

Lege Punktgewichte aus Lernziel und beobachtbarer Leistung im Blueprint fest;
Moodle schreibt nicht vor, jede Einzelwahl mit genau einem Punkt oder jede
Mehrfachwahl nach Anzahl richtiger Optionen zu gewichten.
- **`multichoice`:** `<defaultgrade>` ist das vereinbarte Fragegewicht. Bei
  Einzelwahl genau eine Antwort mit `fraction="100"`; falsche Antworten nach
  vereinbartem Schema, üblicherweise 0. Bei Mehrfachwahl ergeben die positiven
  Gewichte ungefähr 100 Prozent; Teilpunkt-/Abzugsregeln ausdrücklich festlegen.
- **Zuordnungen/Lücken:** Gleichgewichtete Teilaufgaben können je einen Punkt
  erhalten, müssen es aber nicht. Fragegewicht und Papier-Teilpunkte abstimmen.
- **`cloze`:** Eingebettete Teilgewichte maschinell summieren. Ein zusätzliches
  Defaultgrade-Feld ist nicht nötig; falls vorhanden, muss es mit dem beabsichtigten
  Gesamtgewicht übereinstimmen. Die importierten Teil-/Slotgewichte später prüfen.
- **Freitext:** Beobachtbare Teilkriterien mit eindeutigen Punktwerten festlegen;
  Rubriksumme mit XML- und Papiergewicht vergleichen. Automatische und manuelle
  Punkte getrennt ausweisen; vor Handkorrektur Gesamtwertung als vorläufig führen.
- **`coderunner`:** Gewichtung aus dem beauftragten Bewertungsschema übernehmen,
  nicht automatisch aus der Zahl technischer Testfälle ableiten.
- **Parität:** XML-Fragegewichte, späterer Slotplan, Blueprint, Schlüssel und
  sichtbare Papier-/Vorschaupunkte müssen dieselbe Gesamtsumme ergeben.
- **Wiederholungsabzug:** `<penalty>` (z. B. `0.3333333`) nur setzen, wenn das
  Bewertungsschema mehrere Versuche mit Abzug vorsieht.

### Lösungsneutralität in SVG-Grafiken (kritisch)
**Die Grafik darf niemals die Lösung vorwegnehmen oder visuell verraten.** Konkret:
- **Keine farbliche Hervorhebung** von Elementen, die die gesuchte Antwort darstellen (z. B. eine gesuchte Zwischentabelle nicht orange/gelb einfärben, wenn „Zwischentabelle" die korrekte Antwort ist).
- **Keine Legenden**, die direkt auf die richtige Antwort hinweisen (z. B. „Pfeile = Fremdschlüsselbezüge" in einer Farbe, die mit der zu identifizierenden Sonderrolle assoziiert ist).
- **Alle gleichwertigen Elemente** (z. B. mehrere Tabellen, Klassen, Knoten) erhalten **einheitliche Farben und Rahmen** – es sei denn, die Aufgabe lautet ausdrücklich, den Unterschied der Farbe zu erklären.
- **Vor der Fertigstellung prüfen:** Könnte ein Schüler die richtige Antwort allein aus dem Diagramm ableiten, ohne die Frage zu lösen? Wenn ja → Grafik anpassen.
- **Multiplizitätslabels weglassen, wenn sie Teil der Lösung sind:** Wenn eine Lücke `[[n]]` die korrekte Antwort `"1"`, `"0..*"` o. ä. enthält, dürfen diese Werte **nicht** im Diagramm als Label sichtbar sein — sonst ist die Lösung direkt ablesbar.

### Überschneidungsfreiheit in SVG-Grafiken (kritisch)
**Kein grafisches Element darf ein anderes überlagern oder unleserlich machen.**
- **Koordinaten rechnerisch prüfen:** Rechtecke, Ellipsen, Texte und Verbindungslinien dürfen sich nicht überlappen.
- **Mindestabstände einhalten:** Zwischen Boxen ≥ 10 px; Beschriftungen vollständig innerhalb der Box oder mit ≥ 5 px Abstand zur nächsten Box; Linien kreuzen keine Boxen, wenn eine Umgehung möglich ist.
- **Beschriftungen nicht durch Linien kreuzen lassen:** Verbindungslinien dürfen keine Texte schneiden; bei Bedarf Texte rechts/links/oberhalb der Grafik platzieren.
- **SVG `width`/`height` groß genug wählen**, sodass alle Elemente inkl. Markerspitzen innerhalb des sichtbaren Bereichs liegen (`refX`/`refY` des Markers einkalkulieren).
- **Textlänge schätzen:** Bei `font-size:13px` ≈ 7–8 px pro Zeichen; Boxbreite ≥ Textlänge × 8 px + 16 px Innenabstand.
- **Callout-Nummern (①②…)** dürfen keine anderen Elemente überdecken – Platz vor dem Element reservieren.

## Validierung (vor dem finalen Ergebnis)

Wohlgeformtheit und Fragentitel-Tag nach jeder XML-Erzeugung prüfen (Pfad der eigenen Datei einsetzen):

```python
import xml.etree.ElementTree as ET
tree = ET.parse('DATEI.xml')  # bricht bei nicht wohlgeformter XML ab
for q in tree.getroot().findall('question'):
    if q.get('type') == 'category':
        continue
    n = q.find('name')  # sucht den Tag mit den vier Buchstaben n-a-m-e
    if n is not None and n.find('text') is not None:
        print(f"OK: titel='{n.find('text').text}'")
    else:
        print("FEHLER: Frage hat keinen korrekten Fragentitel-Tag!")
```

Zusätzlich nach `<text>`-Elementen mit HTML ohne CDATA suchen. Meldet Moodle
„n Fragen erkannt, 0 importiert“, enthält mindestens eine Frage einen Fehler:
Fragen einzeln prüfen. Weitere Fehlerbilder: `../templates/README.md`.
