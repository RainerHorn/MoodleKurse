#!/usr/bin/env python3
"""Statische Prüfung einer .mbz-Datei ohne Moodle (nur Standardbibliothek).

Prüft:
  - gzip-tar lesbar, moodle_backup.xml vorhanden
  - Alle XML-Dateien: UTF-8 ohne BOM, kein CR, Deklaration exakt <?xml version="1.0" encoding="UTF-8"?>, wohlgeformt
  - HTML-/Textinhalte in files/: nur gemeldet (Nutzerdateien dürfen CR enthalten), aber nie in XML
  - files.xml: jede Datei (contenthash) liegt im Archiv, Größe und SHA1 stimmen
  - moodle_backup.xml: Abschnitte und Aktivitäten haben ihr Verzeichnis im Archiv
Aufruf: python check_mbz.py <datei.mbz> [--bericht]
Exit-Code 0 = in Ordnung, 1 = Fehler.
"""
import hashlib
import sys
import tarfile
import xml.etree.ElementTree as ET

DEKLARATION = b'<?xml version="1.0" encoding="UTF-8"?>'


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    pfad = argv[1]
    fehler, warn = [], []
    try:
        tar = tarfile.open(pfad, "r:gz")
    except (tarfile.TarError, OSError) as e:
        print(f"FEHLER {pfad}: kein lesbares gzip-tar ({e})")
        return 1
    mitglieder = {m.name: m for m in tar.getmembers() if m.isfile()}
    namen = set(mitglieder)
    verz = {n.split("/")[0] + "/" + n.split("/")[1] for n in namen if n.count("/") >= 2}

    if "moodle_backup.xml" not in namen:
        fehler.append("moodle_backup.xml fehlt")

    xml_n = 0
    for n, m in mitglieder.items():
        if not n.endswith(".xml") or n.startswith("files/"):
            continue
        xml_n += 1
        roh = tar.extractfile(m).read()
        if roh.startswith(b"\xef\xbb\xbf"):
            fehler.append(f"{n}: BOM")
            roh = roh[3:]
        if b"\r" in roh:
            anzahl = roh.count(b"\r")
            fehler.append(f"{n}: enthält CR ({anzahl}x)")
        erste = roh.split(b"\n", 1)[0].strip()
        if erste != DEKLARATION:
            fehler.append(f"{n}: Deklaration {erste[:60]!r}")
        try:
            ET.fromstring(roh)
        except ET.ParseError as e:
            fehler.append(f"{n}: nicht wohlgeformt ({e})")

    # files.xml gegen Inhalte
    dateien = 0
    if "files.xml" in namen:
        wurzel = ET.fromstring(tar.extractfile(mitglieder["files.xml"]).read())
        gesehen = set()
        for f in wurzel.findall("file"):
            name = f.findtext("filename")
            h = f.findtext("contenthash")
            if name == "." or not h or h in gesehen:
                continue
            gesehen.add(h)
            dateien += 1
            ziel = f"files/{h[:2]}/{h}"
            if ziel not in namen:
                fehler.append(f"files.xml: {name} ({h}) fehlt im Archiv")
                continue
            daten = tar.extractfile(mitglieder[ziel]).read()
            if hashlib.sha1(daten).hexdigest() != h:
                fehler.append(f"files/{h[:2]}/{h}: SHA1 passt nicht ({name})")
            size = f.findtext("filesize")
            if size and int(size) != len(daten):
                fehler.append(f"{name}: Größe {len(daten)} statt {size}")
            if name.lower().endswith((".html", ".htm", ".svg", ".txt", ".java")) and b"\r" in daten:
                warn.append(f"Nutzerdatei {name} enthält CR (nur Hinweis)")

    # moodle_backup.xml gegen Verzeichnisse
    art, abschn, akt = "?", 0, 0
    if "moodle_backup.xml" in namen:
        mb = ET.fromstring(tar.extractfile(mitglieder["moodle_backup.xml"]).read())
        art = mb.findtext(".//details/detail/type") or "?"
        for s in mb.findall("information/contents/sections/section"):
            abschn += 1
            d = s.findtext("directory")
            if not any(n.startswith(d + "/") for n in namen):
                fehler.append(f"Abschnittsverzeichnis fehlt: {d}")
        for a in mb.findall("information/contents/activities/activity"):
            akt += 1
            d = a.findtext("directory")
            if not any(n.startswith(d + "/") for n in namen):
                fehler.append(f"Aktivitätsverzeichnis fehlt: {d}")
        if mb.findtext("information/settings/setting/[name='users']/value") not in (None, "0"):
            warn.append("Einstellung users ist nicht 0 (Nutzerdaten enthalten?)")

    print(f"{pfad}\n  Typ: {art}, Abschnitte: {abschn}, Aktivitäten: {akt}, XML-Dateien: {xml_n}, Dateiinhalte: {dateien}")
    for w in warn:
        print(f"  Hinweis: {w}")
    for f in fehler:
        print(f"  FEHLER {f}")
    print("  Ergebnis: " + ("FEHLER" if fehler else "in Ordnung"))
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

