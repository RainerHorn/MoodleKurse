# Zusatz-Plugins für das lokale Moodle

Persönliche, nicht eingecheckte Zusatz-Plugins. Ein gemeinsamer Ordner lässt sich über die Umgebungsvariable `MBZ_PLUGIN_DIR` angeben (z. B. dort, wo die Plugin-Zips des Fragen-Skills liegen).

Hier abgelegte `<typ>_<name>.zip` werden von `scripts/mbz.ps1` beim nächsten Lauf im Container installiert (z. B. `qtype_ddmatch.zip`).
Die Zips stammen aus dem Moodle-Plugin-Verzeichnis (Anmeldung nötig), müssen zu Moodle 4.5 passen und werden **nicht** ins Git eingecheckt.
Die Fragetypen, die Ihre Quizdateien verwenden und die nicht im Moodle-Kern liegen (z. B. `ddmatch`, `coderunner`), müssen hier installiert sein, sonst bricht der Fragenimport ab.
