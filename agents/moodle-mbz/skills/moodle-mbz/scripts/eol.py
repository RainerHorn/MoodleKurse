#!/usr/bin/env python3
"""Zeilenenden und Kodierung der Kursquellen vereinheitlichen (nur Standardbibliothek).

Regel: Alle Textdateien sind UTF-8 ohne BOM mit LF. CRLF und einzelnes CR werden zu LF.
Binärdateien (png, pdf, zip ...) werden nie angefasst.

Aufruf:
  python eol.py normalisieren <ordner>   Dateien im Ordner umschreiben (idempotent)
  python eol.py pruefen <ordner>         nur melden, Exit-Code 1 bei Abweichungen
"""
import sys
from pathlib import Path

TEXT = {".html", ".htm", ".xml", ".json", ".css", ".js", ".svg", ".md", ".txt", ".csv",
        ".java", ".py", ".php", ".yml", ".yaml", ".ps1", ".sh"}


def pruefe(pfad: Path):
    """Gibt (Befund, Text) zurück; Befund ist eine Liste von Kurzmeldungen."""
    roh = pfad.read_bytes()
    befund = []
    if roh.startswith(b"\xef\xbb\xbf"):
        befund.append("BOM")
        roh = roh[3:]
    try:
        text = roh.decode("utf-8")
    except UnicodeDecodeError as e:
        raise SystemExit(f"FEHLER {pfad}: kein gültiges UTF-8 ({e}). Datei nach UTF-8 umwandeln.")
    if "\r\n" in text:
        befund.append("CRLF")
    if "\r" in text.replace("\r\n", ""):
        befund.append("einzelnes CR")
    return befund, text


def main(argv):
    if len(argv) != 3 or argv[1] not in ("normalisieren", "pruefen"):
        print(__doc__)
        return 2
    modus, ordner = argv[1], Path(argv[2])
    if not ordner.is_dir():
        print(f"Ordner fehlt: {ordner}")
        return 2
    geaendert = 0
    gesamt = 0
    for p in sorted(ordner.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in TEXT:
            continue
        gesamt += 1
        befund, text = pruefe(p)
        if not befund:
            continue
        geaendert += 1
        print(f"{'repariert' if modus == 'normalisieren' else 'ABWEICHUNG'}: {p.relative_to(ordner)} ({', '.join(befund)})")
        if modus == "normalisieren":
            neu = text.replace("\r\n", "\n").replace("\r", "\n")
            p.write_bytes(neu.encode("utf-8"))
    print(f"{gesamt} Textdateien geprüft, {geaendert} {'repariert' if modus == 'normalisieren' else 'mit Abweichung'}")
    return 1 if (modus == "pruefen" and geaendert) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
