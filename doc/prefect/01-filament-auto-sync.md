# F01 – Filamente bei Druckeränderungen automatisch übernehmen

## Gewünschtes Verhalten und Bedienung

`prefect_auto_sync_filaments=true` übernimmt die Materialliste des aktuell ausgewählten
Druckers automatisch. Der Drucker ist für Typ, Profil und Farbe maßgeblich. Nach einer
Änderung wird 750 ms gewartet, damit zusammengehörige Netzwerkpakete nur eine
Synchronisierung auslösen. Eine Änderung von Farbe, Material-ID, Materialtyp,
Mehrfachfarben, Belegungsstatus, AMS-/Slot-Zuordnung oder Drucker-ID zählt als Änderung.
Stetige Temperatur- und Fortschrittsmeldungen ohne Materialänderung lösen nichts aus.

Die automatische Synchronisierung verwendet den vorhandenen direkten Übernahmemodus.
Sie öffnet weder den Farbzuordnungsassistenten noch die Abschlussbestätigung. Die
manuelle Synchronisierung über die vorhandenen Schaltflächen bleibt verfügbar und
behält ihre bisherigen Dialoge. Abschalten ist über die Prefect-Einstellungen möglich.

## Implementierung und stabile Suchanker

Basis: BambuStudio `v02.08.02.61`, Commit
`926a7192574bcb9b3a732e1ec59a46d79cb45466`.

| Datei | Suchanker | Zweck |
| --- | --- | --- |
| `src/slic3r/GUI/Plater.hpp` | `m_prefect_filament_sync_timer`, `m_prefect_observed_filaments` | Timer und unveränderte letzte Druckermeldung; kein globaler Zustand |
| `src/slic3r/GUI/Plater.cpp` | `Sidebar::Sidebar`, `filament_sync_action` | Timer besitzt Sidebar als wx-Owner; GUI-Thread; Stop/Retry/Sync |
| dieselbe Datei | `Sidebar::load_ams_list` | Erkennt Geräte- und Inhaltsänderungen; startet Timer neu |
| dieselbe Datei | `Sidebar::sync_ams_list` | Zusätzlicher optionaler Parameter `automatic=false`; vorhandene Pipeline weiterverwenden |
| dieselbe Datei | `Sidebar::~Sidebar` | Timer vor Zerstörung stoppen |
| `src/slic3r/GUI/PrefectFilamentSyncPolicy.hpp` | `filament_sync_action` | Abhängigkeitenfreie Ablaufentscheidung für Regressionstest |
| `tests/prefect/filament_sync_test.cpp` | `main` | Übergänge bei Jobs, Verbindungsverlust, Profil- und Gerätewechsel |

`GUI_App.cpp` ruft `load_ams_list` bereits nach LAN- und Cloud-Materialmeldungen auf.
`DeviceCore/DevManager.cpp` ruft dieselbe Methode bei Gerätewechsel und Verlust auf.
Diese Stellen sind absichtlich unverändert; keine zweite Netzwerkabfrage und kein
Polling der gesamten Filamentliste.

Wichtig: `PresetBundle::filament_ams_list` ist keine saubere Vergleichsquelle. Die
vorhandene Sync-Pipeline ergänzt darin temporär `filament_changed`. Deshalb speichert
die Sidebar eine eigene Kopie der von `build_filament_ams_list` gelieferten Daten.
Sonst würde jedes spätere MQTT-Paket eine neue Synchronisierung auslösen.

Der Timer wartet in 1000-ms-Schritten, solange Slicing, ein UI-Job, ein modaler Dialog,
eine unterbrochene Verbindung oder ein unpassendes Druckerprofil vorliegt. So geht
eine einmal erkannte Änderung nicht verloren, wenn gerade ein Job läuft. Ein anderer
ausgewählter Drucker, ein G-code-/G-code-3MF-Projekt, Shutdown oder eine deaktivierte
Option stoppen den Vorgang. Die Druckerprüfung erhält explizit `popup_warning=false`.

Der automatische Pfad benutzt eine frische `SyncResult` mit `direct_sync=true` und
verwendet deshalb keine veraltete Auswahl des manuell geöffneten Sync-Dialogs.
Vor der Änderung wird ein Undo-Snapshot erstellt. Danach laufen die vorhandenen
Aktualisierungen für Materialanzahl, Mehrfarbfilamente, Spülmengen, Comboboxen,
Projektkonfiguration und Vorschaubilder weiter. Ein `Plater::update()` invalidiert
anschließend das Slicing-Ergebnis. Eine ScopeGuard setzt die Reentranzsperre zurück.

## Bewusste Regeln und Nebenwirkungen

- Materialprofile und Farben im Projekt werden wie bei manueller direkter Übernahme
  ersetzt. Unsgespeicherte Änderungen des gerade editierten Filamentprofils werden
  beim Laden des ersten synchronisierten Profils verworfen; der automatische Modus
  fragt hierfür nicht erneut. Gespeicherte Benutzerprofile werden nicht gelöscht.
- Bestehende Objektzuweisungen folgen den bisherigen numerischen Filamentindizes.
  Der Modus führt keine zusätzliche Farbnäherungszuordnung durch.
- Bei einem installierten und bereiten Filamentwechsler werden externe Spulen wie im
  vorhandenen Sync-Dialog ausgeschlossen. Mixed-Filament-Erhalt und optionale
  Farbzusammenführung bleiben Aufgaben von `PresetBundle::sync_ams_list`.
- Sind alle Slots leer oder ist kein kompatibles Profil verfügbar, wird die
  Projektliste nicht auf null Materialien reduziert. Das entspricht der vorhandenen
  Sync-Pipeline. Unbekannte Materialien nutzen deren generische/bisherige
  Ersatzprofile; im automatischen Modus erfolgt die Meldung im Log statt als OK-Dialog.
- Eine Verbindung zum Drucker und dessen Netzwerk-Plugin bleiben erforderlich.
  Keine Druckaufträge, Heizbefehle oder Materialladebefehle werden ausgelöst.

## Nachziehen bei einem Upstream-Update

1. Neue `load_ams_list`-Aufrufer prüfen: Die Methode muss weiter nur auf dem GUI-Thread
   aufgerufen werden und vollständige zusammengeführte Gerätestände erhalten.
2. `build_filament_ams_list` vergleichen. Neue semantisch relevante Materialfelder
   gehören in die beobachtete Kopie; häufig wechselnde Telemetrie gehört nicht hinein.
3. Alle Änderungen an `sync_ams_list` und `PresetBundle::sync_ams_list` lesen. Den
   `automatic`-Parameter mit Defaultwert erhalten, damit bisherige Aufrufer manuell bleiben.
4. Jede neu eingeführte modale Meldung in der Sync-Pipeline auf den automatischen Pfad
   prüfen. Diagnosen ins Log oder in eine passive Statusanzeige leiten.
5. Die explizite Initialisierung von `SyncResult` und `skip_ext` mit dem neuen
   Dialogschema vergleichen. Kein Ergebnis eines früheren Dialogs übernehmen.
6. Folgende Prüfungen nach einem vollständigen GUI-Build ausführen.

## Prüfszenarien

1. Drucker verbinden; ohne Sync-Klick muss die erste Liste erscheinen. Farbe eines
   Slots am Drucker ändern: nach etwa 750 ms neue Farbe in Studio, kein Dialog.
2. Material-ID, Typ, Spulenbelegung und Mehrfachfarben ändern; passende Profile prüfen.
3. Identische Gerätemeldung mehrfach senden: kein neuer Undo-Eintrag und kein neuer Sync.
4. Während des Slicens ein Material ändern: erst Job fertigstellen, danach genau den
   aktuellsten Stand übernehmen. Auch mit Hintergrundslicing testen.
5. Modalen Dialog öffnen, Material ändern und schließen: Sync danach ohne neuen
   Gerätewechsel. Dasselbe mit Offline/Online und unpassendem/passendem Druckerprofil.
6. Während des Wartens zu anderem Drucker wechseln: kein alter Druckerstand im neuen
   Projekt. Verbindung vollständig trennen: Timer stoppen.
7. Externe Spule, AMS, zwei Extruder, Filamentwechsler und Mixed-Filamente prüfen.
8. Unbekanntes Material: kein OK-Dialog; Ersatzprofil und Logeintrag kontrollieren.
9. G-code/geslicte 3MF öffnen: keine automatische Änderung oder Neues-Projekt-Meldung.
10. Option deaktivieren und Gerät ändern: nur vorhandene manuelle Übernahme möglich.
11. Manuellen Sync öffnen: Abbrechen, Farbzuordnung und Abschlussdialog weiter nutzbar.

Der reine Policy-Test lässt sich ohne GUI-Abhängigkeiten mit einem C++-Compiler bauen:
`c++ -std=c++17 tests/prefect/filament_sync_test.cpp -o prefect_filament_sync_policy`
und anschließend ausführen. Er ersetzt die Geräte- und GUI-Prüfungen nicht.
