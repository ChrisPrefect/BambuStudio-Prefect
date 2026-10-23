# 04 – Automatisch im Hintergrund slicen

## Gewünschtes Verhalten

Nach einer Modell-, Platten- oder Einstellungänderung slict Bambu Studio die ausgewählte Platte automatisch. Das bestehende Zeitfenster von 500 ms fasst schnelle aufeinanderfolgende Änderungen zusammen. Der Benutzer bleibt in seiner aktuellen Ansicht und kann in „Vorbereiten“ weiterarbeiten. Es wird weder automatisch gedruckt noch eine Datei an einen Drucker übertragen.

Die Anwendungseinstellung `background_processing` steuert die Funktion. Der Fork setzt sie standardmäßig auf `true`; zum Abschalten den entsprechenden Schalter in den Einstellungen ausschalten. Ein bereits gestarteter Lauf darf fertig werden. Manueller Slice-/Exportbetrieb bleibt verfügbar.

## Basis und Ursache

Basis: Upstream-Tag `v02.08.02.61`, Commit `926a7192574bcb9b3a732e1ec59a46d79cb45466`.

Upstream besitzt bereits `background_process_timer`, `Print::apply()`, die Validierung und den `BackgroundSlicingProcess`-Worker. `Plater::priv::background_processing_enabled()` war jedoch mit `SUPPORT_BACKGROUND_PROCESSING` ausgeblendet und verglich außerdem mit dem alten Textwert `"1"`. Die aktuelle Anwendungskonfiguration speichert boolesche Werte als `true`/`false`. Es ist daher nicht ausreichend, nur eine Zeile in der Config zu ändern.

## Umsetzung und stabile Codeanker

Die GUI-Anbindung liegt in `src/slic3r/GUI/Plater.cpp`; die tatsächlich verwendeten Zustandsentscheidungen stehen zusätzlich im abhängigkeitsfreien Header `src/slic3r/GUI/PrefectBackgroundPolicy.hpp`:

1. `Plater::priv::background_processing_enabled()` liest `app_config->get_bool("background_processing")` ohne Compile-Schalter. Reine G-Code-Projekte und G-Code-3MF-Dateien werden ausgeschlossen.
2. `Plater::priv::schedule_background_process()` bleibt der bestehende Debounce-Einstieg. Keine zusätzliche Worker-Implementierung und kein zweiter Slicer-Thread werden eingeführt.
3. `Plater::priv::update_restart_background_process()` wartet bei Dragging, aktiven Gizmos, Arrange-/UI-Jobs, explizitem Slicen, Export/Upload und noch nicht konsumierten Worker-Abschlussereignissen. Der Timer wird erneut für 500 ms gesetzt; das Modell wurde in diesen Fällen noch nicht konsumiert.
4. Wenn eine andere Platte ausgewählt wurde, während der Worker seine bisherige Platte bearbeitet, wird das Umschalten bis zum Abschluss zurückgestellt. Einstellungen der neuen Platte werden nicht auf den noch laufenden Print der alten Platte angewandt.
5. Auch ein bereits validiertes, aber noch nicht geslictes Modell startet nach Aktivierung der Einstellung. Deshalb genügt nicht allein ein neues `Print::apply()`-Invalidierungsereignis. Eine ungültige/fehlerhafte Platte startet nicht in einer Endlosschleife neu.
6. Vor einem automatischen Neustart werden dieselben statischen Extruder-/Geschwindigkeitstabellen wie beim manuellen Slicen vorbereitet. Aufgabenbeschränkungen werden mit `PrintBase::TaskParams()` zurückgesetzt. Alte „Alle Platten slicen“-Flags werden auf die aktuelle Platte zurückgesetzt.
7. `on_back_slice_begin()` und `MainFrame::update_slice_print_status()` halten Vorschau und Druckfreigabe aktuell. `m_is_slicing` bleibt im automatischen Lauf unverändert, damit die Oberfläche nicht in den manuellen, gesperrten Slice-Modus geht.
8. `Plater::priv::on_process_completed()` aktualisiert nach Abschluss die Slice-/Druckbuttons, sofern die Funktion aktiv ist.
9. `Plater::priv::restart_background_process()` lässt nicht erzwungene automatische Starts nur zu, wenn `prefect_background_start_prepared` innerhalb des geprüften Timer-Einstiegs gesetzt ist. Direkte Aufrufer aus Szenen-/Konfigurationsupdates werden ansonsten zum Timer umgeleitet. Ein lokaler RAII-Guard setzt die Markierung auch bei einer Ausnahme zurück. Explizite `FORCE_RESTART`-/`FORCE_EXPORT`-Aufträge bleiben auf ihrem bestehenden Pfad.
10. Seit F11 zählt auch ein noch wartender automatischer Anordnungsauftrag (`!prefect_arrange_inserted_ids.empty()`) als UI-Job-Sperre. So startet nach dem Import kein neuer automatischer Slice vor der Anordnung. Der vorhandene Hintergrundtimer ist an `background_process_timer.GetId()` gebunden; der separate Anordnungstimer darf nicht denselben generischen Timerhandler auslösen. Die vollständige Ereigniskette und Invalidierung stehen in [F11](11-auto-arrange.md).

`src/libslic3r/AppConfig.cpp` und `src/slic3r/GUI/Preferences.cpp` registrieren Standardwert und Schalter; beim Umschalten ruft der Schalter `plater()->schedule_background_process()` auf.

Die automatische Filamentsynchronisierung wartet zusätzlich auf `plater()->background_process().running()`. `is_background_process_slicing()` allein ist dafür ungeeignet: Es kennzeichnet den manuellen, UI-sperrenden Slice-Betrieb und bleibt für den editierbaren automatischen Betrieb absichtlich `false`.

## Automatisierte Zustandsprüfungen

`tests/prefect/background_test.cpp` prüft die im Timer tatsächlich verwendete Policy ohne wxWidgets, Drucker oder Netzwerkplugin. Abgedeckt sind jede Zurückstellungsursache, der Wechsel derselben/anderen Platte, die Priorität „deaktiviert/G-Code“ vor „beschäftigt“ (kein fortlaufender Wiederholungs-Timer nach Abschalten), explizite Force-Aufträge sowie die wichtige Unterscheidung zwischen `std::optional<bool>{false}` und einer nicht getroffenen Skriptentscheidung. Der gemeinsame Fork-Workflow kompiliert und startet alle `tests/prefect/*_test.cpp`.

Beispiel für einen C++17-Compiler:

```sh
g++ -std=c++17 -Wall -Wextra -Werror -pedantic tests/prefect/background_test.cpp -o background_test
./background_test
```

Diese Prüfungen belegen die Zustandsentscheidung; sie ersetzen keinen vollständigen GUI-Build und keinen Lauf mit dem tatsächlichen Slicer-Worker.

## Nachbearbeitungsskripte

Der automatische Einstieg darf die bereits bestehende Entscheidung über externe `post_process`-Befehle nicht umgehen. Ohne eine getroffene Wahl (`m_post_process_script_skip_choice` bzw. `post_process_script_choice`) bleibt diese Platte beim automatischen Start stehen. Ein manueller Klick auf „Slice“ öffnet die vorhandene Auswahl. Danach gilt die Wahl auch für automatische Läufe. „Nicht ausführen“ wird über `set_skip_post_process_once(true)` an den vorhandenen Worker übergeben; Skripte werden nicht stillschweigend erlaubt.

## Abnahme am gebauten Programm

Diese Schritte benötigen einen vollständigen GUI-Build; eine reine Diff-Prüfung ersetzt sie nicht.

| Fall | Vorgehen | Erwartung |
|---|---|---|
| Standardstart | STL laden und ca. 500 ms warten | Slicing startet ohne Klick; Ansicht bleibt erhalten |
| Debounce | Layerhöhe mehrfach schnell ändern | Es wird der letzte gültige Zustand verarbeitet |
| Bearbeiten während des Laufs | Großes Modell slicen lassen, dann verschieben oder skalieren | Vorhandener Apply-/Cancel-Pfad verwirft veraltete Daten und verarbeitet den neuen Zustand |
| Dragging/Gizmo | Objekt ziehen bzw. Schnitt-/Paint-Gizmo bedienen | Kein automatischer Neustart mitten in der Aktion; danach wird die Änderung verarbeitet |
| Arrange | Während einer Anordnung Einstellungen ändern | Worker wartet auf das Ende des UI-Jobs |
| Platte wechseln | Zwei Platten anlegen, während eines Laufs wechseln | Alter Lauf erhält keinen fremden Plattenkontext; ausgewählte Platte wird anschließend verarbeitet |
| Explizites Slice All | „Alle Platten slicen“ starten | Hintergrundtimer greift nicht in die Kette ein; danach funktioniert Auto-Slicing wieder für die aktuelle Platte |
| Fehler | Unzulässige Layerhöhe/außerhalb der Platte erzeugen | Bestehende Validierungsanzeige; keine automatische Fehlerschleife |
| Abbrechen | Fortschrittsanzeige eines automatischen Laufs abbrechen | Auch ein wartender Wiederholungs-Timer wird gestoppt; erst eine spätere Modell-/Configänderung startet erneut |
| Ein-/Ausschalten | Bei ungeslictem, bereits validiertem Modell aktivieren; danach deaktivieren | Aktivieren startet; spätere Änderungen starten im deaktivierten Zustand nicht automatisch |
| Skripte | Projekt mit einem harmlosen Test-Nachbearbeitungsskript laden | Ohne Wahl keine Ausführung; manuelle Wahl „Nicht ausführen“ bleibt für automatische Läufe wirksam |
| G-Code | G-Code bzw. G-Code-3MF öffnen | Kein automatischer Modellslice |
| Export | G-Code exportieren während der Timer vorgemerkt ist | Export wird nicht durch einen automatischen Neustart unterbrochen |
| Ergebnis | Nach erfolgreichem Lauf Vorschau und Druckdialog öffnen | Ergebnis gehört zum aktuellen Modell; Druckfreigabe folgt der vorhandenen Validierung |

## Nachtragen bei einem Upstream-Update

1. Nach `background_processing_enabled`, `schedule_background_process`, `update_restart_background_process`, `on_process_completed` und `on_action_slice_plate` suchen.
2. Prüfen, ob Upstream den alten Compile-Schalter oder Configvergleich bereits repariert hat. Dann nur fehlende Teile übernehmen.
3. Die 500-ms-Timerstruktur und die Worker-Zustände mit Upstream vergleichen. Insbesondere prüfen, ob `running()` weiterhin auch `STATE_FINISHED`/`STATE_CANCELED` einschließt und der Abschluss erst im UI-Handler konsumiert wird. Bei Übernahme von F11 die konkrete Timer-ID-Bindung und die Sperre für wartende Anordnungs-IDs gemeinsam erhalten; andernfalls können Timerereignisse falsch zugeordnet werden oder Slicing und Anordnung gleichzeitig starten.
4. Die Vorbedingungen aus dem manuellen Slice-Einstieg erneut abgleichen: neue Extruder-Vorbereitung, Skriptentscheidung, UI-Jobs und neue Projektmodi auch im automatischen Einstieg berücksichtigen.
5. Bei geändertem Mehrplattenmodell die Zuordnung `background_process.get_current_plate()` gegenüber `partplate_list.get_curr_plate()` erneut prüfen.
6. Standardwert, einmalige Migration vorhandener Konfigurationen und Einstellungs-Schalter separat nachtragen. Config ist Anwendungszustand, kein Modell-/Filamentpreset.
7. Vollständigen GUI-Build und die obige Tabelle durchführen. Insbesondere Editieren während eines langen Laufs und Wechseln der Platte sind keine durch einen Quelltext-Smoke-Test belegten Eigenschaften.
