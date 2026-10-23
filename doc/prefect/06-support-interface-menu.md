# F06 – Filamentmenü „Als Supportinterface festlegen“

## Verhalten

Bei aktivierter Workflow-Option „Supportinterface-Eintrag im Filamentmenü anzeigen“
enthält das `...`-Menü jeder physischen, gemischten oder Verlaufsfilamentzeile
`Set as support interface` (deutsche
Übersetzung: „Als Supportinterface festlegen“). Der Eintrag setzt das betreffende
Filament als `support_interface_filament` in den **globalen Prozesseinstellungen**.
Die Schaltfläche benötigt keine markierten Objekte und wirkt nicht nur auf die
Auswahl. Support-Erzeugung und normale Support-Basis werden nicht zusätzlich geändert.

Die Änderung ist rückgängig machbar, markiert die Prozesskonfiguration als verändert
und invalidiert die Slicing-Vorschau. Die optionale Material-Empfehlungsabfrage aus
`Tab::on_value_change` wird für diesen direkten Menüauftrag nicht aufgerufen.

Die Option `prefect_support_interface_menu` ist standardmäßig eingeschaltet.
Abschalten entfernt den Eintrag beim nächsten Öffnen des Menüs; erneutes Einschalten
stellt ihn sofort wieder her. Eine bereits eingestellte Supportinterface-Zuordnung
bleibt erhalten. Die Option steuert die zusätzliche Bedienfunktion, nicht den
Upstream-Druckparameter.

## Code und Konfiguration

Basis: `v02.08.02.61` / `926a7192574bcb9b3a732e1ec59a46d79cb45466`.

- `src/slic3r/GUI/GUI_Factories.cpp`, `MenuFactory::create_filament_action_menu`:
  Beim Initialisieren wird genau ein Handler an eine feste ID gebunden. Bei jedem
  Öffnen wird der Eintrag je nach Option eingefügt oder zerstört; dadurch entstehen
  keine neuen Handler mit veralteten `wxMenuItem`-Zeigern. Der Handler verwendet
  `kSidebarContextMenuFilamentId`, sodass die beim Öffnen des Menüs gespeicherte
  Filamentzeile verwendet wird; kein veralteter Index aus dem Initialisierungsaufruf.
- `src/slic3r/GUI/GUI_Factories.hpp`, `m_prefect_support_interface_menu_id`:
  Die stabile ID gilt für die Lebensdauer der MenuFactory.
- `src/slic3r/GUI/Plater.hpp`: `set_support_interface_filament` deklarieren.
- `src/slic3r/GUI/Plater.cpp`, `Sidebar::set_support_interface_filament`:
  Zuerst Option prüfen, Kontextmenüindex auflösen und prüfen, G-code-Vorschau ausschließen, Undo-Snapshot,
  Kopie der aktuellen Print-Konfiguration ändern, öffentliche `Tab::load_config`
  verwenden und `Plater::update` auslösen.
- Dieselbe Datei, `Sidebar::update_mixed_filament_list`: Das vor jedem Öffnen lokal
  erzeugte Misch-/Verlaufsmenü fügt den Eintrag nur bei aktiver Option hinzu. Sein
  Handler speichert den Konfigurationsslot `cfg_idx`, nicht den Editorindex der Zeile.

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
6. Die Option `prefect_support_interface_menu` in AppConfig und der Workflow-Seite
   erhalten. Das Menü wird mehrfach geöffnet: Handler nur einmal binden, den
   Menüeintrag dynamisch ändern und nicht nach jedem Ein-/Ausschalten neue
   Update-Handler mit Zeigern auf bereits zerstörte Einträge registrieren.
7. Physische und Misch-/Verlaufsmenüs gemeinsam prüfen; letztere verwenden einen
   eigenen Menüaufbau und keine `MenuFactory::create_filament_action_menu`.

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
8. Option bei laufendem Studio ausschalten: Eintrag fehlt sowohl im physischen als
   auch im Misch-/Verlaufsmenü. Aktuelle Supportinterface-Zuordnung bleibt bestehen.
   Mehrfach ein-/ausschalten und unterschiedliche Zeilen öffnen: genau ein Eintrag,
   keine veraltete ID und keine doppelte Aktion. Neustart muss den Zustand erhalten.
9. Misch-/Verlaufsfilament nach Entfernen anderer Zeilen wählen: Der globale Wert
   entspricht dem tatsächlichen Filamentslot, nicht dessen sichtbarer Zeilennummer
   innerhalb der getrennten Mischliste. Undo und lokale Overrides erneut prüfen.

Eine vollständige GUI-/Slicing-Prüfung steht nach dem GUI-Build an; aus dem Quelltext
allein wird kein Laufzeiterfolg abgeleitet.
