# Prefect-Änderungen auf neue Bambu-Studio-Versionen übertragen

## Festgelegte Ausgangsbasis

| Eigenschaft | Wert |
| --- | --- |
| Upstream | `https://github.com/bambulab/BambuStudio.git` |
| Lokaler Remote-Name | `upstream` |
| Ausgangstag | `v02.08.02.61` |
| Zugehöriger Commit | `926a7192574bcb9b3a732e1ec59a46d79cb45466` |
| Feature-Branch | `prefect/workflow` |
| Änderungsinventar | `doc/prefect/changes.json` mit F01 bis F16 |

Das Ziel ist eine nachvollziehbare Patchserie über dem neuen Upstream-Release.
Die Detaildokumente erklären für jede Funktion die Entscheidung, bestehende
Aufrufpfade, persistente Schlüssel, Nebenwirkungen und Laufzeitprüfungen.
Eine Konfliktlösung nach Funktionen und Zuständigkeiten hat Vorrang vor dem
mechanischen Übernehmen alter Zeilen.

Der neue Quellnachtrag für `.6` umfasst F01–F16. Ein neuer Commit-/Treepin,
nativer GUI-Build und Replay-/Releasebeleg werden erst nach tatsächlicher
Erzeugung eingetragen. Die folgenden abgeschlossenen Serien sind historische
Belege ihrer jeweiligen Quellen, keine Prüfung der geänderten `.6`.

Die zuletzt veröffentlichte Serie `.5` bis `939e0b3ce6dce937502666f334950eec2e0f542a`
enthält **35 Commits**. Alle **70 Zwischenstände** aus Rohdiff- und
Format-Patch-Replay stimmen exakt mit den Originaltrees überein.
[Aktueller Replaynachweis](validation/patch-replay-workflow3.md),
[maschinenlesbarer Überblick](validation/patch-replay-workflow3.json) und
[unabhängiger abschließender Tree-Gegenvergleich](validation/patch-replay-workflow3-final.json).
Die Serie enthält zusätzlich zum Workflow den
[Anzeigenamen und die Windows-Appkennung](12-branding.md),
[reproduzierbare violette App-Icons](purple-app-icon-assets.md), die
[DeviceWeb-Paketkorrektur](device-web-packaging.md) und die
[explizite native Taskleistenintegration](taskbar-integration.md).
Bei Updates deren Quellanker und getrennte Build-/Installationsprüfungen
übernehmen. Insbesondere COM-Arbeit aus Aktivierungs-/Inputsync-Handlern
per `CallAfter` auf die UI-Schleife verschieben, einen Benutzerintent über
die ganze reentrante Fortsetzung sperren und reale Berechtigungsfehler respektieren.
Die vorhandene LogSink-Auto-Flush-Änderung bleibt ausschließlich QA-gebunden.

Workflow 3 erweitert F09 um typisierte Meldungseingänge und die Bereinigung
aktiver/verzögerter Tipps. Die freien Helfer deduzieren den privaten
`NotificationManager::NotificationData`-Typ durch generische Lambdas; dessen
Nennung außerhalb der Klasse verursacht C2248. Die konkrete Korrektur und
vollständig qualifizierten Policy-Namespaceaufrufe stehen in
[09-hide-tips.md](09-hide-tips.md). Dazu kommen die getrennt schaltbaren
[F12-Toolbaraktion](arrange-on-click.md) und [F13-Werbefilter](hide-helio-advertising.md).
Die acht nativen Policytests und der native MSVC-GUI-Build sind beide nötig.

Die [historische .4-Serie](validation/patch-replay-taskbar-v5.md) bis
`3cb50caedececb98a21d2792f41c044ee596f759` behält ihre 31 Commits und
62 geprüften Zwischenstände.

Die [historische Brandingserie .3](validation/patch-replay-branding.md) bis
`aef480ca62cfc9ce86a065e2769efe199d7450d1` behält ihre damals geprüften
28 Commits und 56 Zwischenstände.

Der historische Workflow-2-Stand `9d4fad7292484403f0b026972835035b0a967d20`
enthält 24 Commits und 48 geprüfte Zwischenstände:
[damaliger Bericht](validation/patch-replay-workflow2.md),
[damalige Einzelbelege](validation/patch-replay-workflow2.json).

Die frühere Workflow-1-Serie bis `4b5c3546c7fba94439d9bb0fe69553723b895897` ist auch
praktisch geprüft: 20 Rohdiffs und dieselben 20 exportierten Format-Patches
rekonstruieren jede Commitstufe exakt. [Bericht](validation/patch-replay.md)
und [Einzelbelege](validation/patch-replay.json). Mit
[export_and_replay_patches.py](tools/export_and_replay_patches.py) lässt sich
dieser Nachweis nach einem Update wiederholen; einen neuen Ausgabeordner,
den neuen Basis-/Head-Commit und dessen erwarteten Tree übergeben.

Der Quellstand enthält persönliche GUI-Anpassungen, keine zweite Slicer-Engine.
Upstream-Implementierungen für Import, Materialzuweisung, Undo, Validierung und
Slicing sollen auch nach dem Update weiterverwendet werden.

## Vor einem Update sichern und den Ausgangszustand erfassen

Zuerst offene Arbeit committen oder gezielt sichern. Ein Rebase wird auf einem
sauberen Arbeitsbaum durchgeführt. Den aktuellen Fork-Head, die neue Upstream-
Version und den getesteten Binärstand im Prüfprotokoll festhalten. Das eigene
Laufzeitprofil sichern, während die Anwendung geschlossen ist; persönliche
Konfiguration und Geräteanmeldedaten bleiben außerhalb des Repositorys.

```powershell
git status --short
git rev-parse HEAD
git log --reverse --format='%h %s' v02.08.02.61..prefect/workflow
git remote -v
git branch backup/prefect-before-update
```

Der Sicherungsname muss bei späteren Updates eindeutig ergänzt werden. Weder
eine bestehende Backup-Referenz überschreiben noch uncommittete Änderungen mit
einem Reset verwerfen. Ein kompletter Git-Bundle-Export ergänzt das
Format-Patch-Archiv, falls ein Export mitgeliefert wird; persönliche Profile
werden nicht darin abgelegt.

## Variante A: die Feature-Commits rebasen

Den konkreten neuen Release-Tag auswählen und gezielt holen. Die Bezeichnung
`vNEUER_RELEASE` ist in den Beispielen durch einen tatsächlich vorhandenen Tag
zu ersetzen.

```powershell
git fetch --no-tags upstream tag vNEUER_RELEASE
git show --no-patch --format=fuller vNEUER_RELEASE
git switch prefect/workflow
git rebase --onto vNEUER_RELEASE 926a7192574bcb9b3a732e1ec59a46d79cb45466 prefect/workflow
```

`--onto` benennt die alte Basis ausdrücklich. Das ist auch bei einem anfänglich
flachen Checkout hilfreich, weil nicht auf eine zufällig erratene gemeinsame
Historie vertraut wird. Der neue Tag muss lokal vorhanden und die Feature-
Commitfolge vollständig sein. Bei einem späteren Update den dann dokumentierten
alten Basis-Commit verwenden, nicht dauerhaft den Ausgangscommit von 2.8.2.61.

Bei Konflikten nur die betroffenen Funktionen auf die aktuelle Upstream-Struktur
übertragen und anschließend die betroffenen Dateien gezielt stagen:

```powershell
git status --short
git diff
git add -- PFAD_DER_GEPRUEFTEN_DATEI
git rebase --continue
```

Zum Zurückkehren vor den begonnenen Rebase dient `git rebase --abort`. Ein
Feature-Commit darf nur ausgelassen werden, wenn seine vollständige Funktion
im neuen Upstream bereits nachweislich vorhanden ist. Dann im Inventar
festhalten, welche Upstream-Änderung ihn ersetzt und wie die Gleichwertigkeit
geprüft wurde.

Nach dem Rebase den neuen Verlauf mit der Sicherung vergleichen:

```powershell
git range-diff v02.08.02.61..backup/prefect-before-update vNEUER_RELEASE..prefect/workflow
git diff --check vNEUER_RELEASE..prefect/workflow
```

Auch hier bei späteren Updates den alten Basistag ersetzen. Ein sauberer Rebase
belegt nur, dass Git die Änderungen zusammenführen konnte. Die Verhaltensprüfung
bleibt erforderlich.

## Variante B: Format-Patches auf einen neuen Release anwenden

Das bereitgestellte Format-Patch-Archiv enthält die Feature-Commits mit
Commitnachrichten und Kontext. Die konkreten Archiv- und Patchnamen ergeben
sich aus dem Export und sind kein stabiler Teil der Implementierung. Auf einem
frischen Checkout der neuen Basis zunächst auch den alten Basistag holen, damit
Git für `--3way` auf alte Blobs zugreifen kann:

```powershell
git fetch --no-tags upstream tag v02.08.02.61
git fetch --no-tags upstream tag vNEUER_RELEASE
git switch -c prefect/update vNEUER_RELEASE
$patchFiles = @(Get-ChildItem -LiteralPath '.\patches' -Filter '*.patch' -File | Sort-Object Name)
if ($patchFiles.Count -eq 0) { throw 'Keine Format-Patches gefunden.' }
git am --3way -- $patchFiles.FullName
```

Bei einem Konflikt die Funktion wie beim Rebase prüfen, gezielt stagen und
`git am --continue` verwenden. `git am --abort` kehrt vor die Serie zurück.
Ein einzelner Sammel-Diff mit `git apply` ist für die Pflege weniger hilfreich,
da die Featuregrenzen und Erklärungen verloren gehen. Ein Archiv mit Patches
ersetzt außerdem nicht die neue Upstream-Quelle und deren Buildabhängigkeiten.

## Logische Änderungsgruppen und Prüfreihenfolge

Die endgültigen Commit-Hashes können sich durch einen Rebase ändern. Deshalb
verwendet diese Tabelle Feature-IDs, logische Titel und Quellcodeanker. Die
tatsächliche Commitzuordnung lässt sich jederzeit aus dem Git-Log und dem
Patchexport ermitteln.

| Gruppe / logischer Titel | IDs | Zentraler Einstieg beim Update |
| --- | --- | --- |
| Gemeinsame Fork-Standards und Workflow-Einstellungen | alle schaltbaren Features | `AppConfig::set_defaults`, `AppConfig::load`, `PreferencesDialog::create_prefect_tab`, Reset-Liste |
| Druckerfilamente automatisch übernehmen | F01 | `Sidebar::load_ams_list`, Timer, `Sidebar::sync_ams_list`, `filament_sync_action` |
| Eigene einfache Druckeinstellungen | F02 | `TabPrint::configure_simple_fields`, `ConfigOptionsGroup::is_line_visible`, `OptionsSearcher::append_options` |
| Drucker-Box beim Start einklappen und danach bedienbar lassen | F03 | `m_panel_printer_title`, `m_prefect_printer_collapse_applied`, `Sidebar::update_ui_from_settings` |
| Vorhandenen Hintergrundworker aktivieren | F04 | `background_processing_enabled`, `update_restart_background_process`, `restart_background_process`, `on_process_completed` |
| Filamentklick zur Zuweisung | F05 | `PlaterPresetComboBox`, `assign_filament_to_selection`, `ObjectList::set_extruder_for_selected_items` |
| Supportinterface im Filamentmenü | F06 | `MenuFactory::create_filament_action_menu`, `set_support_interface_filament`, Menü-Kontextindex |
| Modellimporte einzeln behalten | F07 | `Plater::priv::load_files`, `looks_like_multipart_object`, `ask_multi` |
| TPU-Cold-Pull-Empfehlung abwählen | F08 | `DevFilaBlackList::check_filaments`, `suppress_tpu_cold_pull`, unveränderter englischer Meldungstext |
| Tipps vollständig verbergen | F09 | `DailyTipsPanel::render`, `DailyTipsWindow::open/render`, `SlicingProgressNotification::render` |
| Editierbare Rotationsstandards und spätere eigene Wahl | F10 | `migrate_arrange_rotation_defaults`, `initial_arrange_rotation`, `set_str`, `params.allow_rotations = settings.enable_rotation` |
| Anordnung nach Mehrfachimport | F11 | `auto_arrange_insertion_eligible`, eingefügte Objekt-IDs und Pending-Job-Guards |
| Direkte Anordnen-Iconklicks mit offenem Popup | F12 | `requested_item_id`, `preserve_arrange_popup_on_click`, `EVT_GLCANVAS_ARRANGE`, `manual_arrange_available` |
| Helio-Werbung getrennt ausblenden | F13 | `PrefectHelioAdsPolicy.hpp`, typisierte beziehungsweise exakt begrenzte alte Tutorialhinweise |
| Aktuelle Platte instanzgenau leeren | F14 | `prefect_clear_current_plate`, `plate_instance_ids`, `Selection::remove_curr_plate`, `get_volume_idxs_from_instance` |
| Einfache Ansicht unabhängig von F02 abflachen | F15 | `use_single_simple_list`, `prepare_simple_view`, `m_prefect_grouped_pages`, `hide_prefect_group_header` |
| Manuelle Sync-Erfolgseinblendung kurz zeigen | F16 | `PrefectSyncNoticeDeadline`, `FinishSyncAmsDialog`, `StartOnce(1000)` |
| Eindeutige Identität, violette Assets und expliziter Taskleistenintent | Branding/Taskbar | `MainFrame::update_title`, AppUserModelID, `PrefectTaskbarPin::defer_foreground_check`, `user_action`, `request_from_user_action`, Weakref-/Closed-Guards und QA-only `locked_backend()->auto_flush(true)` |
| Dokumentation, Übersetzung und überprüfbarer Build | alle | `changes.json`, Tests, Übersetzungs-Overlay, eigener Workflow, Profilstarter |

Gemeinsame Voraussetzungen zuerst prüfen; die tatsächliche Commitserie kann
mehrere zusammenhängende Änderungen an derselben Datei enthalten. Insbesondere
`Plater.cpp` verbindet F01/F03/F04/F05/F06/F07. Einen scheinbar unabhängigen
Hunk daraus nicht isoliert übernehmen, wenn seine Deklaration, Policy oder
Konfigurationsregistrierung fehlt.

## Featurebezogene Konfliktprüfung

### F01: automatischer Materialabgleich

Die bestehenden LAN-/Cloud-Aufrufer von `load_ams_list` müssen weiterhin im
GUI-Thread vollständige zusammengeführte Daten liefern. Den unveränderten
Gerätestand getrennt von der durch `filament_changed` mutierten
`PresetBundle::filament_ams_list` vergleichen. Neue Materialeigenschaften in
die Änderungserkennung aufnehmen, volatile Temperatur-/Fortschrittswerte nicht.
Manuelle Sync-Aufrufe bleiben mit dem Default `automatic=false` manuell.

Im automatischen Pfad `SyncResult` frisch erzeugen, direkte Übernahme erhalten,
keine früheren Dialogauswahlen verwenden. Neue modale Meldungen der
Sync-Pipeline prüfen. Offline, Job, Abschlussereignis und unpassendes Profil
müssen die erkannte Änderung bis zum nächsten zulässigen Zeitpunkt vormerken.
Gerätewechsel, Shutdown und G-Code-Projekt müssen den alten Auftrag stoppen.

### F02: eigene einfache Ansicht

Feldidentitäten sind stabile Optionsschlüssel. Die drei Sichtbarkeitsebenen
müssen zusammenpassen: noch nicht aufgebaute Seiten, aktive Zeilen und Suche.
Gemeinsam beschriftete Mehrfachzeilen werden als Einheit ausgewählt; auch eine
manuell unvollständige Liste mit nur dem zweiten Schlüssel zeigt diese Zeile.
Sowohl Custom-Renderer als auch Grid-Renderer verwenden `is_line_visible`.
Die ursprünglichen Enable-/Disable-Abhängigkeiten bleiben erhalten. Ein gewähltes,
im aktuellen Scope tatsächlich registriertes Feld kann bei `toggle_visible=false`
sichtbar, aber deaktiviert dargestellt werden; seine Anwendbarkeit wird nicht
erfunden. Readonly und Drucker-/Nozzle-/Supportgates weiter respektieren.

Neue Prozesskontexte müssen in der Typzuordnung ergänzt werden. Umbenannte
Optionsschlüssel gegebenenfalls migrieren; unbekannte Schlüssel bei normalem
Speichern nicht löschen. Der Knopf muss bei leerer einfacher Ansicht erreichbar
bleiben und die Anwendungsauswahl beim Speichern erhalten.
Gespeichert-leer über `load_simple_field_selection` und die Präsenzrückgabe von
`AppConfig::get(section,key,out)` erkennen, nicht über `has()`, das leere Strings
als fehlend behandelt. Vorhandene nichtleere und unbekannte Schlüssel erhalten.
Die drei voneinander getrennten Grenzen prüfen: Modus, aktueller Scope und
dynamische Anwendbarkeit. `bridge_no_support` ist global/objektbezogen, kein
Teil-/Höhenbereichsparameter; normales Supportmaterial und TreeSupport verwenden
unterschiedliche Engineparameter. [Details und Abnahme](simple-fields.md).

### F03: kompakte Drucker-Box

Anfangsgröße, Benutzerklick und erneute Anwendung der Einstellungen prüfen.
Der Schalter ist ein Startdefault, keine dauerhafte Sperre des Headerklicks.
Nur eine geänderte Defaultentscheidung erneut anwenden; normale UI- und
Presetrefreshes dürfen die vom Benutzer gewählte Stellung nicht überschreiben.
Wenn Upstream ein anderes Collapse-Widget einführt, dessen öffentliche API
verwenden. Ein-/Ausklappen bleibt bei beiden Schalterstellungen möglich,
ohne Preset- oder Gerätezustand zu verändern.

### F04: Hintergrundslicing

Manuelle Slice-Vorbereitung und automatischen Timer gemeinsam vergleichen:
Extrudertabellen, Validierung, aktive Platte, Force-Aufträge, Export/Upload,
UI-Jobs, Dragging/Gizmos und Verarbeitung von Worker-Abschlussereignissen.
Eine neue Platte darf nicht in den noch arbeitenden Print einer anderen Platte
geschrieben werden. `prefect_background_start_prepared` muss nicht erzwungene
Starts weiterhin durch den geprüften Timer-Einstieg führen.

Die erste Entscheidung über externe `post_process`-Befehle darf nicht als
Nebeneffekt des Autoslicens erteilt werden. Bei `std::optional<bool>` bedeutet
ein gesetztes `false` eine getroffene Wahl, nicht „unentschieden“. Sowohl F04
als auch F01 mit einem langen tatsächlichen Slicing-Lauf prüfen.

### F05/F06: Materialaktionen

Eventrouting und DPI-Geometrie der Filamentzeile prüfen. Nur ein tatsächlich
ausgeführter Zuweisungsklick wird konsumiert; sonst `event.Skip()`. Shift und
Dropdown-Pfeil bleiben erreichbar. Vorhandene Undo-/Zuweisungsfunktionen
weiterverwenden. Die zwei mit F05 korrigierten Instanz-/Volumeindexfehler nicht
doppelt patchen, falls Upstream sie bereits behoben hat.

Für F06 den beim Öffnen gesetzten aktuellen Menüindex verwenden, keine beim
Erzeugen eingefangene alte Filament-ID. UI-Indizes bleiben an der Grenze zu
den Modellwerten um eins zu verschieben. Der Geltungsbereich bleibt die globale
Prozesskonfiguration; lokale Overrides behalten ihren Vorrang.

### F07: Importentscheidungen

Nur die zwei heuristischen Zusammenfassungsfragen unterdrücken. Neue Importpfade
auf Äquivalente prüfen, aber gespeicherte 3MF-Projekte, explizite Teileimporte,
STEP-Strukturen und verbundene/unverbundene Meshinseln nicht pauschal aufteilen.
Ein neuer Upstream-Standardmechanismus kann die Fork-Bedingungen ersetzen,
wenn beide ursprünglichen Fälle mit derselben Entscheidung abgedeckt sind.

### F08/F09: gezielte Hinweise

Für F08 Schweregrad `warning` und exakten ursprünglichen Cold-Pull-Text mit der
aktuellen Blacklist vergleichen. Ein geänderter Text erfordert eine bewusste
Anpassung samt Test; andere Warnungen oder Verbote dürfen nicht über einen
pauschalen TPU-/Blacklist-Filter verschwinden.

Bei F09 Start des eigenständigen Fensters, Rendering des Panels und
Platzberechnung der Slicing-Meldung gemeinsam übertragen. ImGui-Begin/End- und
Style-Stacks müssen ausgeglichen bleiben. Ausblenden darf den Fortschritt,
Abbrechen und Ergebnisstatus nicht beseitigen.

### F10/F11: Rotation und Anordnung nach dem Einfügen

`PrefectArrangePolicy.hpp` enthält Initialisierung, Legacy-Migration und
Warteentscheidungen. Die alte F10-Erzwingung ist entfernt: `ArrangeJob` verwendet
das tatsächliche `settings.enable_rotation`. `migrate_arrange_rotation_defaults`
überträgt nur bei fehlendem `prefect_arrange_rotation_default_revision` die
frühere effektive Force-Wahl in alle drei Modusschlüssel. Danach gewinnen
gespeicherte Entscheidungen, auch ein ausdrückliches `false`; höhere Marker
werden nicht zurückgesetzt. Bei ausgeschaltetem altem F10 keine vorhandenen
Moduswerte überschreiben. Reset darf bewusst den aktuellen Initialstandard
setzen. Die Y-Achsenoption bleibt zur tatsächlich aktivierten Rotation passend.

Wichtig bei `AppConfig`-Aufrufstellen: Ein dreiteiliges
`set("arrange", key, "0")` kann wegen der `const char*`-zu-`bool`-Konvertierung
den Boolean-Overload wählen und `true` speichern. Für die Popup-Booleans
`set_str` verwenden; bei Template-Migrationen einen echten `std::string`
übergeben. Legacy-, `1`/`0`-, `true`/`false`- und `yes`/`no`-Lesefälle prüfen.

F11 wird an erfolgreichen Mehrfachimport und normales Einfügen aus der
Zwischenablage angeschlossen. Den vorhandenen Job für die eingefügten
Objekt-IDs verwenden; vorhandene Objekte bleiben Hindernisse. Gespeicherte
Projektanordnungen, Einfügen von Teilen/Instanzen und bewusstes Klonen werden
nicht über denselben Automatismus umgeordnet. Die konkrete Integration,
Wartebedingungen und Mehrplatten-/Undo-Prüfungen stehen in
[F11](11-auto-arrange.md); die Rotationssteuerung in [F10](10-arrange-rotation.md).

Bei Updates Importabschluss, Modellidentität, Undo-Position, ID-Gültigkeit,
Projektwechsel, Busy-/Modalzustand und Jobabbruch gemeinsam prüfen. Ein verspäteter
Timer darf nach einem neuen Projekt, Undo oder einer geänderten Objektmenge keine
andere Auswahl anordnen. Beide reinen Policy-Einstiege werden in
`tests/prefect/arrange_test.cpp` geprüft; echte Geometrie-/Jobfälle separat testen.

## Konfiguration und Übersetzung nachziehen

Die gemeinsamen Defaults stehen in `PrefectWorkflowPreferences.hpp`, aufgerufen
aus `AppConfig.cpp`. Revision 2 ergänzt fehlende Schalter und behält vorhandene
Entscheidungen, insbesondere `background_processing=false`, bei. Ein fehlender
Revisionsschlüssel und Revision 1 werden auf 2 gehoben; eine höhere Revision
bleibt erhalten. Die Fälle werden mit den tatsächlich verwendeten Defaults- und
Migrationsfunktionen in `tests/prefect/preferences_test.cpp` geprüft.

`PreferencesDialog::create_prefect_tab` muss weiterhin alle sechzehn Funktionen auf
einer Seite abbilden, einschließlich eigenem Schalter plus Picker für F02 und
`prefect_support_interface_menu` für F06. Die gemeinsame
[Einstellungsdokumentation](workflow-settings.md) benennt alle Schlüssel und
Standardwerte. F02 unterscheidet eine fehlende von einer absichtlich leeren
gespeicherten Liste. Sichtbare Checkbox und tatsächlicher Wert müssen auch nach
Verlassen des Feldauswahldialogs und dessen Reset übereinstimmen.

Die Reset-Liste in `PreferencesDialog::on_reset_preferences` muss die neuen
UI-Schlüssel kennen. Die private Feldliste gehört zur Anwendung, nicht in
Filament-/Druckprofile. Ein neues Upstream-Boolean-Format mit `get_bool`
abgleichen; der frühere reine Vergleich gegen `"1"` genügt nicht.

Quellkatalog der deutschen Übersetzung ist
`bbl/i18n/de/BambuStudio_de.po`; Laufzeitkatalog ist
`resources/i18n/de/BambuStudio.mo`. Der Fork ergänzt neue Texte mit
`scripts/prefect/translations-de.json` und dem reproduzierbaren
`scripts/prefect/update_german_catalog.py`. Vorhandene Einträge des binären
Katalogs bleiben beim Overlay erhalten. Nach einem Update gegen die neuen
Upstream-Kataloge erneut erzeugen, nicht einen alten kompletten Katalog über
die neue Übersetzung kopieren. Anwendung anschließend tatsächlich auf Deutsch
starten und neue Schalter, Menütexte sowie Tooltips prüfen.

## Verbindliche Prüfung vor einer neuen Fork-Auslieferung

1. Änderungen mit `git diff --check` prüfen und das Inventar auf neue Basis,
   Dateien, Anker und Tests aktualisieren. Den Manifestprüfer mit Python starten.
2. Alle `tests/prefect/*_test.cpp` mit C++17 und aktivierten Assertions
   kompilieren und ausführen. Der eigene Workflow benutzt
   `-Wall -Wextra -Werror -pedantic`; Release-Schalter mit `NDEBUG` dürfen die
   `assert`-Tests nicht wirkungslos machen.
3. Übersetzungs-Overlay gegen die neue Upstream-Version erzeugen und dessen
   Konsistenzprüfung ausführen.
4. Vollständigen GUI-Build samt nativen Abhängigkeiten erstellen. Die Policy-
   Tests belegen keinen Build der geänderten wxWidgets-/ImGui-Dateien.
   CI-Erfolg durch Run und Artefakt verifizieren, nicht durch Existenz der YAML.
5. Mit `Start-Prefect.ps1` in einem neuen isolierten Profil starten. Danach
   zusätzlich ein kopiertes vorhandenes Profil prüfen: Revision, Standardwerte,
   individuelle Abschaltentscheidungen und Neustartverhalten kontrollieren.
6. Die Prüftabellen aller sechzehn Detaildokumente am gebauten Programm durchführen.
   F01 benötigt einen tatsächlichen Drucker; F04 ein längeres Modell mit
   gleichzeitigem Editieren, Plattenwechsel und manuellem Slice-All. Keine
   Druckauslösung ist für diese Oberflächen-/Slicing-Abnahme erforderlich.
7. Querkombinationen F01+F04, F02+F06, F05 mit Objekt-/Teil-/Montageauswahl und
   F07 mit mehrfarbigem 3MF testen. Undo/Redo und Neustart einbeziehen.
8. In `VALIDATION.md` exakt dokumentieren: neuer Basis- und Fork-Commit,
   Compiler/Buildumgebung, ausgeführte Befehle, Ergebnisse, GUI-/Gerätekontext,
   Artefakt und offen gebliebene Prüfungen. Erst danach einen entsprechend
   geprüften Binärstand als benutzbar ausweisen.

Nach erfolgreicher Abnahme den neuen Basis-Commit in README, Inventar,
Prüfprotokoll und diesem Updateablauf festhalten, die Patchserie neu exportieren
und ihre Anwendung auf einem sauberen Checkout prüfen. Die ursprünglichen
Feature-IDs bleiben unverändert, damit spätere Änderungen vergleichbar bleiben.

## Nachtrag Workflow 3

F09 muss zusätzlich typisierte Tippsbenachrichtigungen unterdrücken, einschließlich des `BBLArcFittingInfo`-Hinweises. Dessen Warning-Level allein ist kein geeigneter Filter: Die automatische Anpassung und echte Warnungen bleiben nötig. Die zusätzlichen, unabhängig schaltbaren Funktionen sind [F12: sofort anordnen](arrange-on-click.md) und [F13: Helio-Werbung](hide-helio-advertising.md). Ihre Detaildokumente enthalten die Updateanker und Gegenprüfungen bei ausgeschaltetem Schalter. Historische Paket- und Pinbelege bleiben an ihre ursprünglichen Sourcecommits gebunden.

## Nachtrag für Workflow 4 / geplante .6

- **F12:** Den echten GLToolbar-Mauspfad mit `check_hover=true` und der
  ursprünglich angeforderten Item-ID prüfen. Der beim Toolwechsel intern
  ebenfalls aufgerufene alte Arrange-Eintrag muss ausschalten und darf keinen
  Auftrag erzeugen. Ein erneuter direkter Iconklick bleibt dagegen gedrückt
  und postet einmal den bestehenden `EVT_GLCANVAS_ARRANGE`-Befehl. UI-Jobs
  blockieren weitere Arbeit; Hintergrundslicing nicht still als Veto verwenden,
  da `Jobs::before_start` es vor dem manuellen Job anhält. Den bestehenden
  Popupbutton erhalten. [Detail](arrange-on-click.md).
- **F14:** Aktuelle Plattenzuordnung pro Instanz statt nach Instanz 0 oder
  ganzem Objekt prüfen. IDs vor Mutation sammeln, vorhandenen Snapshot und
  `erase`-Pfad erhalten. Andere Platten, unplatzierte Kopien, Filamente und
  Undo/Redo prüfen. [Detail](14-quick-plate-delete.md).
- **F15:** Nur Einfachmodus und eigener Layoutschalter entscheiden über die
  flache Ansicht, niemals F02 voraussetzen. Bestehende Groups/Configs teilen,
  Originalseiten für Rückkehr behalten und nur den tatsächlichen Owner die
  gemeinsame Parent-Seite leeren lassen. Suchkategorien erhalten und den
  Suchsprung auf die flache Seite umleiten. [Detail](15-single-simple-list.md).
- **F16:** Den OneShot-Timer ausschließlich dem manuellen Erfolgsfenster
  zuordnen. Show/Update starten neu, Hide/Destruktor stoppen. Auto-Hide darf
  weder OK-Handler noch `on_hide()` mit Hauptfenster-Raise auslösen; Warnungen
  und die allgemeine Hoverpause anderer Fenster bleiben erhalten.
  [Detail](16-sync-success-timeout.md).

Diese Updateanker beschreiben Sourceverhalten. Vor einer `.6`-Auslieferung
sind neuer vollständiger nativer Build, aktuelle Paket-/Replaybindungen und
eigene Laufzeitbelege erforderlich; historische `.5`-Ergebnisse ersetzen sie nicht.
