# F15: Einfache Prozessansicht als eine Liste

## Unabhängig von der eigenen Feldauswahl

`prefect_simple_single_list=true` entfernt in der einfachen Prozessansicht die
Kategorienumschalter und Gruppenüberschriften. Alle dort verfügbaren Felder
stehen zusammen in einer Liste. **F15 ist unabhängig von F02:** Bei abgeschalteter
eigener Feldauswahl gelten die normalen einfachen Upstream-Felder; bei aktivem
F02 gilt dessen gespeicherte Auswahl. In der erweiterten/Expertenansicht bleibt
die normale Gliederung erhalten. Filament- und Drucker-Tabs werden nicht abgeflacht.

Der eigene Schalter unter **Einstellungen → Workflow** erlaubt die Rückkehr
zur gruppierten einfachen Ansicht, ohne die Feldliste zu ändern. Eine bewusst
leere F02-Auswahl bleibt leer und lässt den Feldauswahldialog weiterhin erreichbar.
Felder, die der aktuelle Objekt-/Teil-/Höhenbereichs-/Plattenkontext strukturell
nicht unterstützt, werden nicht als unzulässige Overrides hinzugefügt.
[F02 und Reichweitenregeln](simple-fields.md).

## Gemeinsame Controls und Lebensdauer

`TabPrint::prepare_simple_view` behält die ursprünglichen `PageShp`-Objekte in
`m_prefect_grouped_pages`. Die flache Seite referenziert dieselben vorhandenen
`ConfigOptionsGroup`-Objekte mit denselben Configbindungen, Callbacks und
Undo-/Vererbungsfunktionen. Es gibt keine kopierte zweite Konfiguration und
keinen nachgebauten Satz von Parametereditoren. Der zusätzliche **Frequent**-
Block des Objekteditors wird ausgelassen, weil diese Felder bereits in ihren
ursprünglichen Gruppen vorhanden sind.

Beim Wechsel wird der bestehende Clear-/Activate-Lebenszyklus der Controls
verwendet. Nur der aktuell besitzende Prozess-Tab darf die gemeinsam genutzte
Parent-Seite leeren. Inaktive Scopes bereinigen ausschließlich eigene
Gruppendaten. Kategorienleisten und deren Sizer gehören dagegen jeweils ihrem
eigenen Tab; ihre Sichtbarkeit verändert keine andere aktive Leiste.

`Page::activate` und `Page::update_visibility` verbergen auf der flachen Seite
nur die bestehenden Gruppenköpfe und den unmittelbar zugehörigen Abstand.
Metadaten für Suche, Gruppenidentität und ursprüngliche Kategorien bleiben
erhalten. `Tab::activate_option` findet Suchtreffer in der flachen Seite über
ihren Schlüssel. Der Rückwechsel verwendet die ursprünglichen Seiten; die
vorhandene Nozzle-/Varianten-ID-Zuordnung wird ohne Änderung von Druckparametern
über `switch_excluder(-1, false)` neu gebunden.

## Updateanker

| Datei | Anker |
| --- | --- |
| `src/slic3r/GUI/PrefectSimpleView.hpp` | `use_single_simple_list` — genau Modus und F15, keine F02-Abhängigkeit |
| `src/slic3r/GUI/Tab.hpp` | `m_prefect_single_list`, `m_prefect_grouped_pages`, `simple_single_list_active` |
| `src/slic3r/GUI/Tab.cpp` | `TabPrint::prepare_simple_view`, `simple_field_source_pages`, `hide_prefect_group_header` |
| `src/slic3r/GUI/Tab.cpp` | `Tab::update_visibility`, `rebuild_page_tree`, `set_expanded`, `activate_option` |
| `src/libslic3r/PrefectWorkflowPreferences.hpp` | `prefect_simple_single_list` |
| `src/slic3r/GUI/Preferences.cpp` | `prefect_simple_single_list` — Checkbox, Refresh beider Tablisten und Reset |
| `tests/prefect/simple_fields_test.cpp` | `use_single_simple_list` |

Nach Upstream-Updates besonders die Ownership der gemeinsamen Parent-Seite,
aktive/inaktive Scopes, Suchnavigation, Varianten-IDs und eventuelle doppelte
Frequent-Felder prüfen. Originalgruppen nicht klonen oder ihre Druckparameter
umdefinieren. Falls die Headerstruktur anders aufgebaut wird, nur den neuen
Kopf und seinen Abstand ausblenden, keine Eingabezeilen oder bedingten Widgets.

## Abnahme

Die Policytests prüfen F15 an/aus unabhängig von F02, die normalen Modusgrenzen
und eine leere gespeicherte F02-Liste. Nach neuem GUI-Build sind vier
Kombinationen F02/F15 an/aus zu prüfen; außerdem Einfach ↔ Experte, Suche,
Global ↔ Objekt/Teil/Höhenbereich/Platte, Nozzlewechsel, eine ausschließlich
bedingt nicht anwendbare gewählte Zeile und Neustart. **Neuer nativer GUI-Build
und sichtbare Abnahme der `.6` sind noch nicht belegt.**
