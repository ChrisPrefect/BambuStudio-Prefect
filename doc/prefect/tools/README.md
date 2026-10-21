# GUI-Prüfgeometrien reproduzieren

Python 3.8 oder neuer genügt; zusätzliche Pakete sind nicht nötig. Aus der Repositorywurzel:

```sh
python doc/prefect/tools/create_gui_fixtures.py --output-dir ../prefect-gui-fixtures
```

`--output-dir` ist Pflicht. Das Werkzeug schreibt drei STL-Dateien und ein deterministisches `gui-fixtures.json` in diesen Ordner. Die erzeugten STL-Dateien gehören außerhalb des Repositorys. Es öffnet keine Anwendung und startet keinen Druck.

| Datei | Größe | Facetten | Verwendung |
|---|---:|---:|---|
| `prefect_cube_A.stl` | 1.217 Bytes | 12 | Geschlossener 20-mm-Würfel; Mehrfachimport und Filamentzuweisung. |
| `prefect_cube_B.stl` | 1.217 Bytes | 12 | Gleiche Geometrie mit anderem Objektnamen. |
| `prefect_progress_tower_80x80x150.stl` | 33.684 Bytes | 672 | 80 × 80 × 150 mm, 25 durchgehende 10-mm-Öffnungen und 5-mm-Stege; Hintergrund-Slicing beobachten. |

Der Turm hat 26 Konturen pro regulärem horizontalen Schnitt und bei 0,2 mm Schichthöhe ungefähr 750 Schichten. Die tatsächliche Slicing-Dauer hängt vom Prozessprofil und Rechner ab. Falls der Fortschritt zu kurz sichtbar ist, kann das isolierte Prüfprofil beispielsweise 0,08 mm Schichthöhe und Gyroid-Infill verwenden.

Die STL-Bytes stimmen mit den ursprünglichen Abnahme-Fixtures überein. Dafür schreibt das Werkzeug die ASCII-Würfel ausdrücklich mit CRLF und den Turm als Little-Endian-Binär-STL. Sortierte Zellen, feste Facettenfolge und ein Manifest ohne Zeitstempel oder lokale Pfade halten die Ausgabe reproduzierbar. Die historischen Würfel enthalten nicht spezifizierte Nullnormalen; ihre Facettenorientierung wird anhand der Vertices geprüft. Der Turm enthält korrekte Einheitsnormalen.

Nach dem Generieren werden geschlossene Kantenpaare mit entgegengesetzter Laufrichtung, Zusammenhang, Orientierung, Bounding-Box, Volumen, Fläche, Facettenzahlen, Euler-Charakteristik und Mittelschnittkonturen geprüft. Danach erfolgt ein Vergleich mit den bekannten SHA256-Werten sowie ein Rücklesen der geschriebenen Bytes. Die Prüfungen bleiben mit `python -O` aktiv. Die [Referenzwerte](../validation/gui-fixtures.json) sind als kleine JSON-Datei eingecheckt.

Ein erneuter Lauf mit identischen Ausgaben ist zulässig. Abweichende vorhandene Zieldateien werden vor dem Schreiben erkannt und nicht überschrieben; dafür einen neuen Ausgabeordner wählen.
