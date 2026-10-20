# F06 – Filamentmenü „Als Supportinterface festlegen“

## Verhalten

Das `...`-Menü jeder Filamentzeile enthält `Set as support interface` (deutsche
Übersetzung: „Als Supportinterface festlegen“). Der Eintrag setzt das betreffende
Filament als `support_interface_filament` in den **globalen Prozesseinstellungen**.
Die Schaltfläche benötigt keine markierten Objekte und wirkt nicht nur auf die
Auswahl. Support-Erzeugung und normale Support-Basis werden nicht zusätzlich geändert.

Die Änderung ist rückgängig machbar, markiert die Prozesskonfiguration als verändert
und invalidiert die Slicing-Vorschau. Die optionale Material-Empfehlungsabfrage aus
`Tab::on_value_change` wird für diesen direkten Menüauftrag nicht aufgerufen.

## Code und Konfiguration

Basis: `v02.08.02.61` / `926a7192574bcb9b3a732e1ec59a46d79cb45466`.

- `src/slic3r/GUI/GUI_Factories.cpp`, `MenuFactory::create_filament_action_menu`:
  Eintrag wird nur beim Initialisieren angelegt. Der Handler verwendet
  `kSidebarContextMenuFilamentId`, sodass die beim Öffnen des Menüs gespeicherte
  Filamentzeile verwendet wird; kein veralteter Index aus dem Initialisierungsaufruf.
- `src/slic3r/GUI/Plater.hpp`: `set_support_interface_filament` deklarieren.
- `src/slic3r/GUI/Plater.cpp`, `Sidebar::set_support_interface_filament`:
  Kontextmenüindex auflösen und prüfen, G-code-Vorschau ausschließen, Undo-Snapshot,
  Kopie der aktuellen Print-Konfiguration ändern, öffentliche `Tab::load_config`
  verwenden und `Plater::update` auslösen.

`support_interface_filament` bleibt der vorhandene Upstream-Key. Null bedeutet Auto,
das gewählte Sidebar-Filament wird als Index plus eins eingetragen. Es wird kein
separater Prefect-Druckparameter eingeführt. Das Menü ist bei FFF aktiv.

Bestehende Objekt-/Plattenüberschreibungen behalten nach Upstream-Regeln Vorrang vor
der globalen Einstellung. Die Funktion entfernt solche lokalen Overrides nicht.
Auf der Oberfläche neu angelegte englische `_L`-Strings benötigen einen passenden
Eintrag im deutschen Übersetzungskatalog; andernfalls zeigt wx die englische Quelle.

## Nachziehen bei einem Upstream-Update

1. `create_filament_action_menu`, `kSidebarContextMenuFilamentId` und das Speichern von
   `m_menu_filament_id` in `Sidebar::init_filament_combo` gemeinsam vergleichen.
2. Bleibt `support_interface_filament` der einsbasierte Key? Bei geänderten Filament-
   Indizes die Konvertierung anpassen und keine nullbasierte UI-ID direkt speichern.
3. `Tab::load_config` muss weiter Dirty-Zustand und Prozess-UI aktualisieren. Das
   geschützte `load_key_value` darf nicht direkt aus Sidebar aufgerufen werden.
4. Nach Änderungen an globalen/Platten-Prozessen bewusst denselben Geltungsbereich
   erhalten oder Änderung klar dokumentieren.
5. Neuen Menütext in `bbl/i18n/de/BambuStudio_de.po` nachziehen und den Laufzeitkatalog
   `resources/i18n/de/BambuStudio.mo` reproduzierbar ergänzen/bauen.

## Prüfszenarien

1. Drei Filamente anlegen; Menü von Filament 3 öffnen und Eintrag wählen. Globalen
   Supportinterface-Wert prüfen: exakt Filament 3, auch ohne Objektauswahl.
2. Danach Menü von Filament 1 wählen: keine gecachte Zuordnung zu Filament 3.
3. Undo/Redo und Dirty-Markierung kontrollieren; Slicing neu durchführen und tatsächliche
   Interface-Lagen in der Vorschau kontrollieren.
4. Support-Basis und „Support aktivieren“ müssen ihren bisherigen Wert behalten.
5. Lokale Interface-Overrides prüfen; diese werden absichtlich nicht überschrieben.
6. Filament entfernen/zusammenführen und Menü neu öffnen: aktuelle Indizes prüfen.
7. G-code-Vorschau: keine Projektänderung oder Neues-Projekt-Abfrage.

Eine vollständige GUI-/Slicing-Prüfung steht nach dem GUI-Build an; aus dem Quelltext
allein wird kein Laufzeiterfolg abgeleitet.
