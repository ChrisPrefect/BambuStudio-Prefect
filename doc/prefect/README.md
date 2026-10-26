# Prefect Bambu Studio – Workflow-Fork

Dieser Fork bündelt dreizehn konkret gewünschte Anpassungen am Arbeitsablauf.
Der Änderungsstand wird auf dem Branch `prefect/workflow` im eigenen
[GitHub-Fork](https://github.com/ChrisPrefect/BambuStudio-Prefect) gepflegt.
Die gemeinsame Grundlage ist Bambu Studio **v02.08.02.61**, Commit
`926a7192574bcb9b3a732e1ec59a46d79cb45466`. Das Git-Remote `upstream` zeigt auf
`https://github.com/bambulab/BambuStudio.git`.

**Aktueller Auslieferungsstand .4 vom 25.10.2026:**
`3cb50caedececb98a21d2792f41c044ee596f759`, Tree
`ca2cd51f1d335f7c5172bad8152b1b727cc0f2fe`, enthält alle elf Funktionen,
Namen, violettes Icon, DeviceWeb-Paketprüfung und den Taskleisten-Nachtrag.
Der vollständige [Windows-Build 40222805625](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/40222805625)
ist erfolgreich. Alle 6.756 eigenen Installationsdateien, 13 DeviceWeb-Dateien
und elf eingebetteten Icon-Größen sind geprüft. Ein neuer eigener GUI-Lauf
bestätigt die verzögerte COM-Vorprüfung und lesbare Live-QA-Logs; `GetDefault`
liefert danach ein echtes, respektiertes `0x80070005`/`E_ACCESSDENIED`.
**Der tatsächliche Windows-Taskleistenpin ist jetzt nachgewiesen.** Startmenü
und echter Taskleistenlink zeigen auf v5, verwenden dasselbe normale Fork-Profil,
EXE-Icon 0 und `ChrisPrefect.BambuStudio`. Die öffentliche Shell bietet bei beiden
„Von &Taskleiste lösen“ an; alle drei ursprünglichen Pins sind SHA-identisch.
Der Desktoplink ist aktuell nicht vorhanden. Der [aktuelle Pinbeleg](validation/taskbar-v5-pin-current-public-summary.json)
dokumentiert den Zustand; die Herkunft der Pinaktion wurde nicht ermittelt.
Die [veröffentlichte Vorabversion .4](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/tag/v02.08.02.61-prefect.4)
enthält Windows-ZIP, die 31-Commit-Patchserie mit 62 identischen Zwischenständen
und Prüfsummen; alle drei öffentlichen Downloads sind vollständig anonym geprüft.
[Aktueller Auslieferungs-/Laufzeitbericht](validation/taskbar-v5.md),
[Ergebnisindex](validation/taskbar-v5-results.json).

**Historischer Auslieferungsstand .3 vom 25.10.2026:**
`aef480ca62cfc9ce86a065e2769efe199d7450d1`, Tree
`aecda9a6db6ebdd470c65228f65c1fae69e8ec22`, enthält alle elf Funktionen,
den Namen **Prefect Bambu Studio**, das violette Icon und die Paketprüfung
für die DeviceWeb-Ressourcen. Der vollständige Windows-Build ist erfolgreich;
alle 6.756 installierten Dateien und 13 DeviceWeb-Dateien sind geprüft.
Drei echte GUI-Starts bestätigen neue, benannte und geänderte Projekttitel.
28 Patches rekonstruieren alle 56 Zwischenstände beider Replaydarstellungen
exakt. Die [veröffentlichte Vorabversion .3](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/tag/v02.08.02.61-prefect.3)
enthält Windows-ZIP, Patchserie und Prüfsummen; alle drei öffentlichen
Downloads sind unabhängig nachgeprüft.
[Damals geprüfter Paket-, Laufzeit- und Veröffentlichungsnachweis](validation/branding.md).
Desktop- und Startmenülinks waren zu diesem Prüfzeitpunkt aktualisiert;
ein tatsächlicher Taskleistenpin war damals noch nicht nachgewiesen.

**Historischer Prüfstand Workflow 2:** `9d4fad7292484403f0b026972835035b0a967d20`
enthält alle elf Schalter, F10/F11 und die ergänzten Materialklickpfade.
Die sechs nativen Policytests und der vollständige Replay von 24 Patches mit
48 identischen Zwischenständen sind bestanden. Der neue vollständige
Windows-GUI-Build ist kompiliert, gelinkt und paketiert; alle 6.755 Dateien
der eigenen lokalen Installation sind mit dem Artefakt verglichen.
Drei echte GUI-Neustarts bestätigen Anordnung mit Rotation, ausgeschaltete
Anordnung und Anordnung ohne Rotation; automatisches Hintergrundslicing
ist im eingeschalteten Fall bis zum erfolgreichen Abschluss belegt.
[Paketnachweis, Laufzeitbelege und Grenzen](validation/workflow2.md).
Die [veröffentlichte Vorabversion Workflow 2](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/tag/v02.08.02.61-prefect.2)
enthält das vollständige Windows-Paket, die geprüfte Serie aus 24 Patches und
`SHA256SUMS.txt`. [Frischer Veröffentlichungsnachweis](validation/published-release-workflow2.json).

**Früherer Auslieferungsstand Workflow 1:** Der vollständige Windows-Build `4b5c3546` ist einschließlich
Linken, Paketierung und CI-Tests erfolgreich. Das finale Paket wurde außerdem
als vollständige eigene Windows-Installation mit allen 6.755 Dateien geprüft
und tatsächlich gestartet; eine Desktop-Verknüpfung verwendet das isolierte
Fork-Profil. Ressourcenlinks zur normalen Installation werden nicht benötigt.
Der Stand enthält auch das Nachholen des aktuellen Materialstands beim erneuten
Aktivieren von F01. Die interaktive Abnahme aller Bedien- und Druckerfälle ist
nicht vollständig belegt. [Lokaler Laufzeitnachweis und genaue Grenzen](validation/local-windows-runtime.md),
[damaliger CI-Nachweis](validation/cloud-build-4b5c.md).
Der GitHub-Fork ist angelegt; dessen Remote heißt `origin`.
Das [veröffentlichte Vorabpaket Workflow 1](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/tag/v02.08.02.61-prefect.1)
enthält das vollständige Windows-ZIP, die geprüfte Serie aus 20 Patches und
`SHA256SUMS.txt`. [Veröffentlichungsnachweis](validation/published-release.json).
Der jeweils aktuelle Nachweis, einschließlich tatsächlich ausgeführter Tests,
steht in [VALIDATION.md](VALIDATION.md).

## Zusätzlicher Identitätsnachtrag

Der Nachtrag vom 25.10.2026 gibt dem Fork den sichtbaren Namen
**Prefect Bambu Studio**, setzt ihn vor den Projektnamen im Fenstertitel
und trennt seine Windows-Taskleistengruppe über `ChrisPrefect.BambuStudio`.
Details, betroffene Quellstellen, technische Abgrenzung und die Anleitung
zum Nachtragen bei Upstream-Updates stehen in [12-branding.md](12-branding.md).
Er wurde mit Paket `.3` eingeführt und ist in `.4` erhalten; die violetten Vektor- und Rasterassets
sind in [purple-app-icon-assets.md](purple-app-icon-assets.md) beschrieben.
Die drei damaligen Fenstertitel sind an der veröffentlichten `.3`-Quelle geprüft.
Der aktuelle Taskleisten-Nachtrag ist in [taskbar-integration.md](taskbar-integration.md) dokumentiert.
Der aktuelle Windows-Pinzustand und die Metadaten des tatsächlichen
Taskleistenlinks sind getrennt von der früheren nativen API-Ablehnung
[nachgewiesen](validation/taskbar-v5-pin-current-public-summary.json).

## Anpassungsliste

| ID | Anpassung und Bedienung | Schalter / Standard | Detaildokumentation |
| --- | --- | --- | --- |
| F01 | Änderungen der Filamente am ausgewählten Drucker automatisch ins Projekt übernehmen, ohne Sync-Assistenten oder Abschluss-OK | `prefect_auto_sync_filaments=true` | [Automatischer Filamentabgleich](01-filament-auto-sync.md) |
| F02 | Über **Felder...** neben dem Modusschalter selbst festlegen, welche Druckeinstellungen in der einfachen Ansicht erscheinen | `prefect_simple_fields_enabled=false`; eigene Liste erst nach Auswahl aktiv | [Eigene einfache Ansicht](simple-fields.md) |
| F03 | Die obere Drucker-Box dauerhaft eingeklappt halten; Kopfzeile bleibt sichtbar | `prefect_printer_collapsed=true` | [Drucker-Box](03-printer-collapsed.md) |
| F04 | Nach Änderungen die aktuelle Platte mit dem vorhandenen Worker automatisch im Hintergrund slicen | `background_processing=true` | [Hintergrundslicing](04-background-slicing.md) |
| F05 | Markierten Objekten/Teilen durch Klick auf Farbfeld oder Filamentnamen das betreffende Filament zuweisen | `prefect_click_filament_assigns_selection=true` | [Filamentklick](05-click-filament-assignment.md) |
| F06 | Im Filament-`...`-Menü **Als Supportinterface festlegen** anbieten; setzt das globale Supportinterface-Material | `prefect_support_interface_menu=true`; verwendet vorhandenen `support_interface_filament`-Key | [Supportinterface-Menü](06-support-interface-menu.md) |
| F07 | Gemeinsam importierte Modelldateien ohne Zusammenfassungsfrage als einzelne Objekte laden | `prefect_import_separate_objects=true` | [Getrennte Importe](07-separate-imports.md) |
| F08 | Ausschließlich die wiederkehrende TPU-Cold-Pull-Empfehlung ausblenden | `prefect_suppress_tpu_cold_pull=true` | [TPU-Erinnerung](08-tpu-cold-pull.md) |
| F09 | Tippsfenster, Slicing-Tipps und typisierte Tipps/Vorschläge ausblenden, einschließlich Kurvenplanungs-Hinweis und reserviertem Platz | `prefect_hide_tips=true` | [Tipps abschalten](09-hide-tips.md) |
| F10 | Automatische Rotation bei manuellem und automatischem Anordnen immer einschalten | `prefect_arrange_rotation=true` | [Anordnungsrotation](10-arrange-rotation.md) |
| F11 | Nach dem Einfügen mehrerer unabhängiger Objekte automatisch anordnen | `prefect_arrange_after_import=true` | [Automatische Anordnung](11-auto-arrange.md) |
| F12 | Beim ersten Toolbar-Klick sofort anordnen; Optionspopup für den nächsten Lauf offen halten | `prefect_arrange_on_click=true` | [Sofort anordnen](arrange-on-click.md) |
| F13 | Helio-Additive-Werbung und Aktivierungsaufforderungen ausblenden | `prefect_hide_helio_ads=true` | [Helio-Werbung](hide-helio-advertising.md) |

Alle dreizehn Funktionen sind unter **Einstellungen → Workflow** einzeln schaltbar.
Die [vollständige Einstellungsseite](workflow-settings.md) enthält auch den
Zugang zur eigenen Feldauswahl und einen Schalter für den Supportinterface-
Menüeintrag. Dieser verwendet `prefect_support_interface_menu=true`; der
bestehende Druckparameter `support_interface_filament` bleibt erhalten.

Die Änderungen ersetzen gezielt die genannten wiederkehrenden Rückfragen. Es
wird kein allgemeiner Mechanismus eingeführt, der beliebige unbekannte Dialoge
automatisch mit „Ja“ beantwortet. Bestehende Druckergrenzen, Validierungen und
die Entscheidung über externe Nachbearbeitungsskripte behalten ihre Bedeutung.

## Verhalten, das beim Benutzen wichtig ist

- **Drucker als Materialquelle:** F01 übernimmt Typ, Farbe und passende Profile
  aus dem ausgewählten Gerät. Ungespeicherte Änderungen am gerade editierten
  Filamentprofil können dabei verworfen werden. Die vorhandenen numerischen
  Objektzuweisungen bleiben maßgeblich. Die konkrete Übernahme und Sonderfälle
  sind im F01-Dokument beschrieben.
- **Aktuelle Platte:** F04 startet nach etwa 500 ms ohne weitere Änderungen.
  F01 bündelt Druckermeldungen über etwa 750 ms und wartet bei einem laufenden
  Slicing-/UI-Job. Diese Zeitfenster sind keine harte Laufzeitgarantie.
- **Farben und Profile weiterhin bearbeiten:** Mit Shift-Klick auf das Farbfeld
  wird der Farbwähler geöffnet. Dropdown-Pfeil beziehungsweise Shift-Klick auf
  den Namen lassen die Profilauswahl erreichbar. Ohne Objektauswahl bleibt die
  bisherige Bedienung bestehen.
- **Supportinterface:** F06 ändert nur die globale Interface-Zuweisung.
  Support-Erzeugung, Support-Basismaterial und bestehende lokale Overrides
  werden nicht zusätzlich verändert.
- **Projektstruktur:** F07 beantwortet die beiden heuristischen
  Zusammenfassungsfragen mit „Nein“. Gespeicherte 3MF-Strukturen und bewusst
  hinzugefügte Teile werden nicht pauschal zerlegt.
- **Weitere Tippsmeldungen:** F09 erfasst auch den Kurvenplanungs-/Bogenanpassungshinweis und automatische Filamentswitcher-Erstnutzungstipps. Druck-/Kalibrierwarnungen bleiben erhalten. Die unabhängige Helio-Werbeoption F13 gilt auch dann, wenn allgemeine Tipps zugelassen sind.

## Eigenes Profil statt Änderungen an der normalen Installation

Auf dem geprüften Windows-System liegt das aktuelle Paket vollständig unter
`%USERPROFILE%\BambuStudio-Prefect-Windows-v5`. ZIP-Hash, sämtliche Datei-Hashes,
exakte Paketstruktur und fehlende Ressourcen-/Dateilinks sind im
[aktuellen Prüfbericht](validation/taskbar-v5.md) festgehalten.
Die Laufzeitprüfung verwendet ein separates Profil mit ausschließlich
synthetischen Prüfmodellen. Das bestehende normale Fork-Profil wird dabei
nicht gestartet oder verändert.
Desktop und Startmenü enthalten **Prefect Bambu Studio** mit geprüftem Ziel,
Arbeitsverzeichnis, Icon und `ChrisPrefect.BambuStudio`. Der bisherige
Desktoplink **BambuStudio Prefect patched** wurde bytegenau gesichert und
erst nach Prüfung beider neuen Links umbenannt. Die bisherige
`--datadir "%APPDATA%\BambuStudio-Prefect"`-Angabe bleibt identisch.
Der nächste reguläre Start ergänzt dort die neuen Standards über die
Revision-2-Migration und erhält die schon gespeicherten Entscheidungen.

[Start-Prefect.ps1](../../scripts/prefect/Start-Prefect.ps1) ist der Einstieg für
eine gebaute Fork-Version. Er startet die angegebene `bambu-studio.exe` mit
`--datadir` und einem eigenen Profilverzeichnis. Standardmäßig ist das:

```text
%APPDATA%\BambuStudio-Prefect
```

Die normalen Bambu-Studio-Daten unter `%APPDATA%\BambuStudio` bleiben erhalten.
Das Skript verweigert dieses normale Verzeichnis ausdrücklich als Fork-Profil.
Es ersetzt keine installierte EXE und kompiliert selbst kein Programm.

Beispiel nach einem erfolgreichen Build, aus dem Repository-Stamm:

```powershell
.\scripts\prefect\Start-Prefect.ps1 -ExecutablePath 'C:\Pfad\zum\Fork\bambu-studio.exe'
```

Für einen erstmaligen lokalen Import der vorhandenen Konfiguration und Profile:

```powershell
.\scripts\prefect\Start-Prefect.ps1 -ExecutablePath 'C:\Pfad\zum\Fork\bambu-studio.exe' -ImportStockProfile
```

`-ImportStockProfile` funktioniert nur, solange das neue Profilverzeichnis noch
nicht existiert. Kopiert werden `BambuStudio.conf` sowie die Ordner `user` und
`system`, soweit vorhanden. Bereits vorhandene Fork-Profile werden nicht
überschrieben. Ein anderes Ziel lässt sich mit `-ProfileDirectory` angeben.
Diese persönlichen Laufzeitdaten gehören nicht in Git, Patches oder CI-Artefakte.
Das optionale Bambu-Netzwerkplugin und eine Geräteverbindung bleiben für die
Kommunikation mit dem Drucker erforderlich.

## Standardwerte und einmalige Migration

`AppConfig::set_defaults()` ergänzt über `PrefectWorkflowPreferences.hpp` fehlende
Fork-Schalter. Die neun `prefect_*`-Booleans aus F01/F03/F05/F06/F07/F08/F09/F10/F11
sind standardmäßig `true`.
Hintergrundslicing ist ebenfalls standardmäßig aktiv. Die eigene einfache
Feldauswahl bleibt zunächst deaktiviert. Beim erstmaligen Aktivieren ohne
`prefect_simple_fields` initialisiert `TabPrint` die Liste mit den aktuellen einfachen Standardfeldern.
Eine ausdrücklich gespeicherte leere Liste bleibt dagegen leer.

`AppConfig::load()` prüft zusätzlich den **eingelesenen JSON-Inhalt** auf
`app.prefect_workflow_revision`. Ein fehlender Schlüssel oder Revision `1`
wird auf Revision `2` gehoben. Vorhandene Entscheidungen einschließlich
`background_processing=false` bleiben erhalten. Höhere Revisionen werden
nicht herabgesetzt. Neue Schlüssel erhalten nur dann den Standard, wenn sie
fehlen. Die Migration prüft weiterhin das gelesene JSON statt ausschließlich
der im Konstruktor bereits gesetzten Standardwerte. Die sechs nativen
Policytests enthalten auch die Fälle für erhaltene Abschaltentscheidungen.

Die vorhandene Funktion **Einstellungen zurücksetzen** entfernt auch die neuen
Funktionsschalter und die eigene Feldauswahl und setzt die Fork-Standardwerte
erneut. Die Migrationsrevision bleibt erhalten. Ein bloßes Ausschalten einzelner
Funktionen erfordert dagegen keinen Profilreset.

## Änderungen prüfen und weiterpflegen

Die maschinenlesbare Bestandsliste steht in [changes.json](changes.json).
Die abgeschlossene Feature-Commitserie ist in [COMMITS.md](COMMITS.md) zugeordnet.
`scripts/prefect/check_manifest.py` prüft die elf IDs, die Detaildokumente und
die eingetragenen Quellcodeanker. Der Workflow
[prefect-workflow.yml](../../.github/workflows/prefect-workflow.yml) kompiliert
die unabhängigen C++-Policytests und beschreibt anschließend einen vollständigen
Windows-Build samt portablem Paket. Ob dieser Build tatsächlich ausgeführt
wurde und erfolgreich war, muss anhand seines Laufs geprüft werden.

Die sechs unabhängigen Tests unter `tests/prefect/*_test.cpp` prüfen:

- F01: Stoppen, Warten und Synchronisieren bei Geräte-/Jobzuständen;
- F02: Feldlisten, Normalisierung, gemeinsame Zeilen und Modusgrenzen;
- F04: Timer-/Workerentscheidungen, Plattenwechsel und Skriptwahl;
- F08: exakte Unterdrückung der Cold-Pull-Warnung mit unverändertem Verhalten
  bei anderen Meldungen und Schweregraden;
- F10/F11: wirksame Anordnungsrotation, Layoutschutz und Warten beziehungsweise
  Verwerfen eines aufgeschobenen Anordnungsauftrags;
- gemeinsame Einstellungen: Standardwerte und Migration mit erhaltenen
  Abschaltentscheidungen, fehlenden Schlüsseln und bewusst leerer Feldliste.

Sie prüfen keinen vollständigen wxWidgets-Build, kein tatsächliches Slicing und
keine Druckerverbindung. Die dafür erforderlichen Abnahmeszenarien stehen je
Feature im Detaildokument. Die Umsetzung enthält keine automatische
Druckauslösung.

Für ein Update sind die getrennten Feature-Commits und ein Format-Patch-Export
vorgesehen. Der vollständige Ablauf einschließlich Konfliktlösung,
Konfigurationsmigration, Übersetzung und Abnahme steht in
[UPSTREAM-UPDATES.md](UPSTREAM-UPDATES.md). Entscheidend sind Funktionen und
Optionsschlüssel, nicht unverlässliche Zeilennummern.
