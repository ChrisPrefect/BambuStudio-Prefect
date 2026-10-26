# F14: Aktuelle Platte mit einem Klick leeren

## Verhalten und Schalter

`prefect_quick_delete_plate=true` ergänzt ganz links in der 3D-Haupttoolbar
**Alle Objekte auf der aktuellen Platte löschen**. Ein Klick löscht ohne
Bestätigungsdialog über den vorhandenen Auswahl-/Löschweg. Der normale
Undo-Snapshot bleibt erhalten. Andere Platten, Filamente und Druckeinstellungen
werden nicht zurückgesetzt. Der Schalter unter **Einstellungen → Workflow**
blendet nur diesen zusätzlichen Einstieg aus; er ersetzt keine bestehenden
Löschbefehle.

Der Knopf ist nur für die normale 3D-Vorbereitung vorgesehen. Leere Platte,
fehlendes Modell, laufender UI-Job, Programmende, reiner G-Code-Modus und
bereits exportierte Dateiansicht sperren die Aktion. Der Handler prüft diese
Voraussetzungen erneut; ein zuvor sichtbarer Knopf darf keinen inzwischen
ungültigen Auftrag ausführen.

## Platte und Instanz sind getrennte Identitäten

Ein Modellobjekt kann mehrere Kopien auf verschiedenen Platten besitzen.
`Selection::remove_curr_plate` prüft deshalb **jede Instanz** mit
`PartPlate::contain_instance(object, instance)`. Die unabhängige Policy
`plate_instance_ids` sammelt die Paare vor der Änderung. Anschließend werden
nur die GL-Volumes der passenden Instanz ausgewählt, nicht alle Kopien des
Objekts. Die erste Instanz ist kein Stellvertreter für die ganze Objektgruppe.

Der bestehende `Selection::erase`-/ObjectList-Weg entscheidet danach über
Instanz- oder Objektlöschung. Ein Objekt wird nur vollständig entfernt, wenn
seine gesamte ausgewählte Instanzmenge betroffen ist. Der vorhandene Snapshot
**Selection-Delete Curr Plate All** ermöglicht Undo. Es wird keine zweite
manuelle Modelllöschschleife und kein Filament-Reset eingeführt.

## Dateien und Updateanker

| Datei | Anker | Aufgabe |
| --- | --- | --- |
| `src/slic3r/GUI/GLCanvas3D.cpp` | `prefect_clear_current_plate`, `can_clear_plate` | Erster Toolbarplatz, sichtbarer Schalter, erneute Handlerguards |
| `src/slic3r/GUI/Plater.cpp` | `Plater::remove_curr_plate_all` | Vorhandenen Löschpfad erreichen |
| `src/slic3r/GUI/Selection.cpp` | `Selection::remove_curr_plate`, `get_volume_idxs_from_instance` | Snapshot und Auswahl nur der passenden Instanzen |
| `src/slic3r/GUI/PrefectPlatePolicy.hpp` | `plate_instance_ids` | Reine Ermittlung der Modell-/Instanzpaare |
| `src/libslic3r/PrefectWorkflowPreferences.hpp` | `prefect_quick_delete_plate` | Fehlenden Schlüssel mit `true` ergänzen |
| `src/slic3r/GUI/Preferences.cpp` | `prefect_quick_delete_plate` | Einzelschalter, unmittelbare UI-Aktualisierung und Reset |
| `tests/prefect/plate_clear_test.cpp` | `Current-plate deletion` | Geteilte Objekte, fremde und unplatzierte Instanzen, leere Platte |

Beim Upstream-Update die Toolbarreihenfolge und beide Guardpfade übertragen.
Die Instanzzuordnung vor Mutationen erfassen, weil Löschungen Indizes verschieben.
`get_volume_idxs_from_object` wäre hier eine Regression: Es würde Kopien auf
anderen Platten einschließen. Snapshot und vorhandenen Instanz-/Objektlöschweg
erhalten; die Policy allein prüft noch keine echte Undo-Wiederherstellung.

## Tests und ausstehende GUI-Abnahme

Der C++17-Test `plate_clear_test.cpp` prüft Kopien desselben Objekts auf zwei
Platten sowie eine unplatzierte Kopie. Die ausgewählten ID-Mengen sind disjunkt;
die Eingabedaten bleiben bei ihrer Ermittlung unverändert. `preferences_test.cpp`
prüft den Standardwert und erhaltene Abschaltentscheidungen.

Nach einem vollständigen neuen GUI-Build: dieselbe Objektgruppe auf zwei Platten
verteilen, eine Platte leeren, die andere und die Filamentliste vergleichen und
Undo/Redo prüfen. Leere Platte, laufenden Job, G-Code-Ansicht sowie Ein-/Ausschalten
des Toolbarplatzes testen. **Dieser Quellnachtrag für `.6` enthält noch keinen
neuen Build-, Laufzeit- oder Veröffentlichungsnachweis.**
