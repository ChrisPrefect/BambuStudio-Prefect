# Prefect Bambu Studio – Taskleistenintegration

Diese Vorabversion enthält die elf einzeln schaltbaren Workflow-Anpassungen, den Prefect-Namen und das violette Windows-Icon sowie einen bewusst aktivierbaren Prüfeinstieg für die eigene Taskleistenintegration.

## Bewusster Prüfeinstieg

Nur mit `PREFECT_QA_TASKBAR_PIN=1` erscheint der zusätzliche Topbar-Eintrag **An Taskleiste anheften** mit **F8**. Der normale Start blendet diesen Prüfeinstieg aus. Der erste F8 kann zunächst nur die lesende Vorprüfung starten; sobald der Status bereit ist, kann ein weiterer bewusster F8 oder Menüklick im Vordergrund den Windows-Bestätigungsablauf anfordern. Initialisierung, Aktivierung und Timer lösen keine Pin-Anfrage aus.

Lesende Vorprüfung und ausdrückliche Benutzeraktion werden mit `CallAfter` aus dem Windows-Eingabestack in die eigene UI-Ereignisschleife fortgesetzt. Damit wird der im früheren Prüflauf beobachtete Fehler `RPC_E_CANTCALLOUT_ININPUTSYNCCALL` (`0x8001010D`) gezielt adressiert. Vordergrund-, App-Identitäts- und Verfügbarkeitsprüfungen bleiben erhalten. Die Anwendung umgeht keine Windows-Bestätigung oder Berechtigung.

Die Diagnose unterscheidet `ui_installed`, `preflight_deferred` und `user_action_deferred` im vorhandenen verschlüsselten Anwendungslog. API-Status und Diagnosemarker sind kein Nachweis einer tatsächlichen Taskleistenanheftung. **Diese Veröffentlichungsnotizen behaupten keinen erfolgreichen OS-Pin.** Die tatsächliche Windows-Abnahme bleibt separat dokumentiert.

## Reproduzierbare Versionsmetadaten

`VERSION_METADATA_EPOCH` stammt aus dem letzten Commit der Versions-/Brandingdateien und steuert `SOURCE_DATE_EPOCH`. Die bestehende Anzeige „Build Time“ bezeichnet damit das reproduzierbare Metadatendatum, nicht die Kompilierungszeit oder den letzten beliebigen GUI-Commit. Geänderte Quelldateien werden weiterhin anhand ihrer Bytes und Git-Blobs neu gebaut; die echte Quellidentität bleibt der unten angegebene Sourcecommit und `PREFECT-COMMIT.txt`.

## Paket und Nachweise

Das Windows-ZIP vollständig in einen neuen lokalen Ordner entpacken. `Start-Prefect.ps1` verwendet das getrennte normale Profil `%APPDATA%\BambuStudio-Prefect`. Eine lokale QA-Profilprüfung und die normalen Profilargumente von Verknüpfungen sind getrennt zu behandeln. Die vorherigen Releases `.1`, `.2` und `.3` bleiben erhalten.

- Quellcommit: `3cb50caedececb98a21d2792f41c044ee596f759`.
- Quelltree: `ca2cd51f1d335f7c5172bad8152b1b727cc0f2fe`.
- [Eigener Windows-Build und Regressionstests](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/40222805625).
- Violettes ICO: 14411 Bytes, SHA-256 `db77286997a999fb0f8e06d7522f3c4f843ed61ea0d8718284d942211e1bf5a8`.
- Patch-ZIP: 31 aufeinanderfolgende Format-Patches und 31 rohe Diffs; alle 62 Zwischenbäume und beide Endbäume stimmen exakt mit den ursprünglichen Git-Trees überein. 1114689 Bytes, SHA-256 `437aa4098bd914d9894260ef264f0c70f35b13242690aab51ea1fd94d865d142`.

Die Auslieferung prüft Source/Tree, erfolgreichen eigenen Build, Artefaktprovenienz, ZIP-CRC und echte Download-Hashes sowie EXE-Versionstrings, jedes eingebettete Iconbild und die Laufzeit-ICO-Datei. Der Source-Workflow stellt fehlende DeviceWeb-Ausgaben nach Cache-Restore wieder her und prüft das installierte Filament-Manager-Bundle vor dem Artefaktupload. `SHA256SUMS.txt` enthält die Hashes von Windows- und Patch-ZIP.

[Anpassungen und Bedienung](https://github.com/ChrisPrefect/BambuStudio-Prefect/blob/3cb50caedececb98a21d2792f41c044ee596f759/doc/prefect/README.md) · [Taskleistenanker und Prüfgrenzen](https://github.com/ChrisPrefect/BambuStudio-Prefect/blob/3cb50caedececb98a21d2792f41c044ee596f759/doc/prefect/taskbar-integration.md) · [Nachtragen bei Upstream-Updates](https://github.com/ChrisPrefect/BambuStudio-Prefect/blob/3cb50caedececb98a21d2792f41c044ee596f759/doc/prefect/UPSTREAM-UPDATES.md)

Dies bleibt eine Vorabversion. Die Quelländerung und ihre Paketprüfung ersetzen weder die lokale Windows-Pin-Abnahme noch physische Druckertests. Durch diese Veröffentlichung wurde kein Druck gestartet.
