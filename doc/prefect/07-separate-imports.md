# 07 – Gemeinsam importierte Dateien als einzelne Objekte laden

## Gewünschtes Verhalten und Einstellung

Beim gleichzeitigen Laden mehrerer STL-/OBJ-Dateien erscheint die Frage „Load these files as a single object with multiple parts?“ nicht mehr. Die Dateien bleiben einzelne Objekte. Ebenso wird bei einer normalen Modelldatei mit mehreren vom Importer erkannten Objekten nicht mehr aufgrund unterschiedlicher Z-Höhen angeboten, daraus ein mehrteiliges Objekt zu bilden.

`prefect_import_separate_objects: true` aktiviert dieses Verhalten; dies ist der Fork-Standard. `false` stellt die bisherigen Rückfragen wieder her. Die Option befindet sich in den Anwendungseinstellungen. Ein laufender Import liest den Wert an den jeweiligen Entscheidungsstellen; normalerweise wird sie vor dem Import eingestellt.

## Geltungsbereich

Die Änderung entscheidet die beiden heuristischen Zusammenfassungsfragen wie „Nein“. Sie zerlegt weder ein explizit als ein Objekt modelliertes Mehrvolumenobjekt noch die Teile eines gespeicherten 3MF-Projekts. Der gezielte Befehl zum Laden/Hinzufügen von Teilen, bestehende Modifier, Baugruppen und der STEP-Importpfad behalten ihre vorhandene Struktur. Eine einzelne STL bleibt eine einzelne STL; eine Mesh-Datei wird nicht anhand unverbundener Inseln automatisch zerlegt.

Das ist entscheidend für spätere Updates: Die gewünschte Standardentscheidung beim gleichzeitigen Import darf nicht durch pauschales `split()` nach jedem Import umgesetzt werden, da dies gespeicherte Projekte und Mehrmaterialobjekte verändern würde.

## Basis und Codeanker

Basis: Upstream-Tag `v02.08.02.61`, Commit `926a7192574bcb9b3a732e1ec59a46d79cb45466`.

In `src/slic3r/GUI/Plater.cpp`, Funktion `Plater::priv::load_files(...)`, sind genau zwei Bedingungen erweitert:

1. Der Block `!is_project_file && model.looks_like_multipart_object()` öffnet den Dialog nur noch, wenn `!app_config->get_bool("prefect_import_separate_objects")` gilt. Ohne Dialog wird `model.convert_multipart_object(filaments_cnt)` nicht ausgeführt.
2. Im Abschlussblock `new_model != nullptr && new_model->objects.size() > 1` wird der bisherige `if (ask_multi)` um dieselbe Bedingung ergänzt. `load_model_objects(new_model->objects)` bleibt unverändert und übernimmt die einzelnen Objekte.

Es werden keine Importstrategien, Datenstrukturen, Koordinaten oder Einheitenkonvertierungen verändert. Standardwert/Schalter liegen in `AppConfig.cpp`/`Preferences.cpp`.

## Abnahme am gebauten Programm

| Fall | Vorgehen | Erwartung |
|---|---|---|
| Mehrere STL | Zwei benannte STL-Dateien gemeinsam über Öffnen auswählen | Kein Zusammenfassungsdialog; zwei getrennte Einträge in der Objektliste |
| Drag-and-drop | Dieselben Dateien gemeinsam auf die Platte ziehen | Gleiches Ergebnis |
| Mehrere OBJ/STL gemischt | Gemischte Dateien gemeinsam laden | Jede vom Importer erkannte Objektwurzel bleibt erhalten |
| Unterschiedliche Höhe | Eine normale Modelldatei mit mehreren erkannten Objekten auf verschiedenen Z-Höhen laden | Keine heuristische Zusammenfassung |
| 3MF-Projekt | Projekt mit mehrteiligem, mehrfarbigem Objekt laden | Objekt-/Teilezuordnung und Einstellungen bleiben erhalten |
| Explizit Teil hinzufügen | An einem Objekt „Teil hinzufügen“ verwenden | Teil wird dem gewählten Objekt hinzugefügt |
| STEP | Eine STEP-Baugruppe laden | STEP-Struktur folgt weiterhin dem bestehenden Importpfad |
| Rücknahme | Einstellung deaktivieren und mehrere Dateien erneut laden | Upstream-Dialog erscheint wieder; Ja/Nein funktioniert wie zuvor |
| Rückgängig | Mehrere Objekte laden, dann Undo | Bestehendes Import-Undo bleibt funktionsfähig |

## Nachtragen bei einem Upstream-Update

1. In `Plater::priv::load_files` nach `looks_like_multipart_object`, `ask_multi`, `convert_multipart_object` sowie den beiden englischen Dialogtexten suchen.
2. Prüfen, ob Upstream neue Importpfade oder einen eigenen gespeicherten Standard eingeführt hat. Wenn ja, diesen bevorzugt an die Fork-Einstellung anbinden.
3. Die Bedingung jeweils nur um den Anwendungsschalter ergänzen. Den eigentlichen `load_model_objects`-Pfad nicht ändern.
4. Projekt- und explizite Teileimporte separat prüfen. Die Option betrifft heuristisches Zusammenfassen, kein allgemeines Aufteilen.
5. Configstandard/GUI-Schalter nachtragen und die obige Tabelle auf einem vollständigen GUI-Build ausführen.
