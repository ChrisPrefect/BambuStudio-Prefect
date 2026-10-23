# F05 – Markierten Objekten per Filamentklick Material zuweisen

## Verhalten

Bei `prefect_click_filament_assigns_selection=true` weist ein einfacher Klick auf das
nummerierte Farbfeld oder den Namensbereich einer Filamentzeile dieses Filament den
markierten Objekten/Teilen zu. Die Zuweisung folgt der aktuellen Auswahl; mehrere
markierte Objekte werden gemeinsam geändert. Undo verwendet die vorhandenen
Zuweisungsfunktionen. Die Auswahl wird nicht gelöscht.

Dies gilt auch für die separat dargestellten Misch- und Verlaufsfilamente: Sowohl
das nummerierte Farbfeld als auch deren Inhaltsfläche weisen den tatsächlichen
Konfigurationsslot zu. Diese Zeilen verwenden keinen `PlaterPresetComboBox` und
waren deshalb in Workflow 1 noch nicht vom Filamentklick erfasst. Beim Doppelklick
auf den Namensbereich einer normalen Filamentzeile öffnet der zweite Klick keine
Profilauswahl und erzeugt keinen zweiten Zuweisungs-Snapshot.

Ohne Auswahl bleiben die bisherigen Funktionen bestehen. Shift-Klick auf das Farbfeld
öffnet den Farbwähler auch bei markierten Objekten. Der rechte Dropdown-Pfeil sowie
Shift-Klick auf den Namen öffnen weiterhin die Profilauswahl. Das `...`-Menü bleibt
unverändert erreichbar. Bei deaktivierter Option gilt das bisherige Verhalten.
Bei Misch-/Verlaufsfilamenten öffnet Shift-Klick auf Inhalt oder Farbfeld deren
Editor. Ohne zuweisbare Auswahl öffnet die Inhaltsfläche weiterhin den Editor.
Die bei Upstream inaktive Misch-Farbfläche bleibt bei deaktivierter Option inaktiv.

Eine ausschließlich markierte Plattenzeile, eine Einstellungs-/Gruppenzeile oder
ein Supportblocker/-enforcer gilt nicht als zuweisbare Objektauswahl. Der Klick
öffnet in diesem Fall wie bisher die Farbe-/Profilauswahl und erzeugt keinen
wirkungslosen Undo-Eintrag. In gemischten Auswahlen werden nur gültige
Objekt-/Instanz-/Teil-/Modifier- oder vorhandene Höhenbereichseinträge geändert;
der bestehende Sonderfall für Schnittverbinder bleibt erhalten.

## Implementierung

Basis: `v02.08.02.61` / `926a7192574bcb9b3a732e1ec59a46d79cb45466`.

| Datei | Suchanker | Aufgabe |
| --- | --- | --- |
| `src/slic3r/GUI/PresetComboBoxes.cpp` | `PlaterPresetComboBox::PlaterPresetComboBox`, `Prefect: the row body assigns` | Klick auf Namensbereich abfangen; rechte 24 DIP für Dropdown erhalten |
| dieselbe Datei | `clr_picker->Bind`, `prefect_click_filament_assigns_selection` | Nummeriertes Farbfeld weist Material zu; Shift erhält Farbwähler |
| `src/slic3r/GUI/PresetComboBoxes.hpp` und `.cpp` | `m_prefect_assignment_click_handled`, `assign_on_click` | Erfolgreichen ersten Namensklick merken; dessen `wxEVT_LEFT_DCLICK` ohne zweite Zuweisung konsumieren; sonst Ereignis weitergeben |
| `src/slic3r/GUI/Plater.hpp` | `assign_filament_to_selection` | Öffentliche Sidebar-Methode |
| `src/slic3r/GUI/Plater.cpp` | `Sidebar::assign_filament_to_selection` | Index validieren, Auswahl prüfen und vorhandenen Zuweisungsweg aufrufen |
| dieselbe Datei | `Sidebar::update_mixed_filament_list`, `on_mixed_click`, `mixed_swatch` | Misch-/Verlaufsinhalt und nummerierte Farbfelder an denselben Zuweisungsweg anbinden; Shift erhält den Editor |
| `src/slic3r/GUI/GUI_ObjectList.cpp` | `ObjectList::set_extruder_for_selected_items` | Zwei für Instanz-/Teilzuweisung relevante Upstream-Fehler korrigieren |

UI-Filamentindizes sind nullbasiert; Modell-/Extruderzuweisung ist einsbasiert.
Deshalb wird ausschließlich an der Schnittstelle `filament_id + 1` übergeben.
Misch-/Verlaufszeilen verwenden hierfür `cfg_idx` aus
`mixed_filament_config_indices()`, nicht ihren sichtbaren Zeilenindex `i`.
Letzterer bleibt ausschließlich der Index für `edit_mixed_filament`.
Der gemeinsame Sidebar-Einstieg prüft die Option zusätzlich zu den UI-Handlern,
sodass das Abschalten sofort für beide Darstellungen wirkt.
In der normalen Ansicht wird `ObjectList::set_extruder_for_selected_items` benutzt.
In der Montageansicht wird deren eigener Canvas geprüft und
`Plater::change_extruder_for_assemble_selection` aufgerufen. Die aktive Undo-Stackwahl
bestimmt, welcher Weg gilt. G-code-Vorschauen werden ohne Änderung verlassen; es wird
insbesondere nicht `is_new_project_in_gcode3mf()` aufgerufen, denn diese Methode würde
einen Warnungsdialog öffnen und ein neues Projekt anlegen.

Die Fehlerkorrekturen im vorhandenen ObjectList-Weg sind Teil dieses Features:

1. Bei `itInstance` wurde der noch nicht initialisierte lokale Wert `item` an
   `GetObject` übergeben. Richtig ist der ausgewählte Wert `sel_item`.
2. Vor Zugriff auf `volumes[vol_idx]` wurde fälschlich `obj_idx` mit der Anzahl der
   Volumes verglichen. Jetzt werden negative/zu große Objekt- und Volumeindizes
   abgefangen und `vol_idx` gegen die tatsächliche Volumeanzahl geprüft.
3. Der gemeinsame Zuweisungseinstieg filtert nicht zuweisbare Zeilentypen und
   veraltete Modellindizes vor jedem Konfigurationszugriff. Der erste gültige
   Eintrag legt den Undo-Snapshot an. Die Methode liefert nun einen Boolean
   zurück; nur nach tatsächlich zugelassener Zuweisung wird der Filamentklick
   konsumiert. Bereits bestehende Aufrufer dürfen den Rückgabewert ignorieren.

## Nachziehen bei Upstream-Updates

1. Konstruktor der `PlaterPresetComboBox` auf neue Eventhandler prüfen. Der Bind-Handler
   muss den Klick genau dann schlucken, wenn eine Zuweisung erfolgte, sonst `Skip()`.
2. Neue DPI-/Dropdowngeometrie beachten; rechts muss die native Pfeilfläche frei bleiben.
3. Den Materialzuweisungsweg weiterverwenden, nicht selbst Extruderwerte im Modell
   schreiben. Dadurch bleiben Undo, Farbgebung, Slicing und Teilüberschreibungen erhalten.
4. Prüfen, ob Upstream die zwei ObjectList-Fehler bereits korrigiert hat. Dann nur die
   übrig gebliebenen nötigen Teile übernehmen.
5. Nach Änderungen am Montage-/Undo-System den Canvas-Zweig gegen den aktuellen
   Kontextmenüweg „Filament ändern“ vergleichen.
6. Separat gezeichnete Misch-/Verlaufszeilen berücksichtigen. Nach Änderungen am
   Filamentmodell den sichtbaren Editorindex und tatsächlichen Konfigurationsslot
   weiterhin auseinanderhalten. Neue Farbflächen müssen denselben Handler benutzen.
7. `ComboBox` behandelt `wxEVT_LEFT_DOWN` und `wxEVT_LEFT_DCLICK` separat. Nach einem
   erfolgreichen ersten Namensklick den zweiten nur konsumieren; Shift, Pfeilfläche,
   deaktivierte Option oder ein erster Klick ohne Zuweisung bleiben beim nativen Weg.

## Prüfszenarien

1. Ein Objekt markieren und Filament 2 anklicken: Objektliste und Modell werden korrekt
   eingefärbt; kein Farbwähler oder Presetmenü; Undo/Redo prüfen.
2. Mehrere Objekte, einzelne Teile, Modifier und Instanzen eines Objekts auswählen;
   denselben Test wiederholen. Supportblocker/-enforcer erhalten keine Objektmaterialien.
3. Objekt mit Index größer als seine Volumeanzahl testen; Teilzuweisung bleibt gültig.
4. Montageansicht und normale Ansicht abwechselnd testen; jeweilige Auswahl ändern.
5. Ohne Auswahl auf Farbfeld klicken: Farbwähler. Mit Auswahl Shift-Farbfeld: Farbwähler.
6. Rechts auf Dropdown-Pfeil bzw. mit Shift auf Name klicken: Presetauswahl verfügbar.
7. Option deaktivieren: bestehende Farbe-/Presetbedienung wiederhergestellt.
8. Geslicte 3MF/G-code-Vorschau: Klick erzeugt kein neues Projekt.
9. Nur eine Platte, Einstellungs-/Gruppenzeile oder einen Supportblocker auswählen:
   Klick ändert keine Modellkonfiguration und erzeugt keinen Undo-Eintrag.
   Gemischte gültige/ungültige Auswahl: nur zulässige Einträge erhalten das Material.
10. Mindestens zwei physische sowie mehrere Misch-/Verlaufsfilamente anlegen;
    nummeriertes Misch-Farbfeld und Inhaltsfläche jeweils separat anklicken.
    Objekt-/Teilzuweisung und Undo müssen den angezeigten globalen Slot verwenden,
    auch nachdem vorhergehende physische oder gemischte Zeilen entfernt wurden.
11. Shift-Klick auf Misch-/Verlaufsfeld und Inhalt: Editor. Option ausschalten:
    Inhalt öffnet Editor, Misch-Farbfeld weist nichts zu. Ohne Objektauswahl darf
    ein Klick keinen Zuweisungs-Snapshot erzeugen.
12. Namensbereich eines physischen Filaments doppelt anklicken: genau die erste
    Zuweisung, kein Presetmenü und kein zusätzlicher Undo-Snapshot für den zweiten
    Druck. Shift-Doppelklick und Pfeilfläche behalten ihre normale Profilauswahl.

Diese GUI-Szenarien benötigen einen vollständigen GUI-Build; die lokale Arbeit
enthält keinen behaupteten Laufzeitnachweis dafür.
