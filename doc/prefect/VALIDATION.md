# Prüfprotokoll des Prefect-Forks

Stand: **27. Oktober 2026**, Zeitzone Europe/Zurich.

## Aktueller Prüfstand Workflow 4 / Prefect Bambu Studio .6

Quelle `727a703155237a94e4fcc31ebc4effef515d13f0`, Tree
`16cbb874d6bef7ebbc3453e407451eb9af252b0e`. Der vollständige
[Build 40414286154](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/40414286154)
ist erfolgreich, einschließlich neun C++-Policyprogrammen und beiden Python-
Prüfsuiten. Das echte Artefakt `12695023513` mit 264.440.555 Byte/SHA256
`add72a5bfc23845c5aee6909d95686d99ec538d26d2f455d16110f4f5b52af73`
ist nach Download, CRC und Quelle geprüft. Alle 6.756 Dateien der eigenen
V7-Installation wurden erneut gehasht; 13 DeviceWeb-Dateien, elf violette
Icon-Größen und 14 DLL-Marker stimmen. 37 Patches rekonstruieren 74 Zwischenbäume
exakt. [Gesamtbericht](validation/workflow4.md), [Index](validation/workflow4-results.json).

Ein nativer synthetischer CLI-Roundtrip erhält zwei Objekte, drei Instanzen und
zwei Platten; er ist kein Test des Löschen-Knopfs. Eigener QA- und normaler
Profilstart sind jeweils an EXE/DLL gebunden. Im normalen Profil blieben genaue
Feldauswahl und Aktivierung erhalten, MD5 ist gültig, neue Standards und
Rotationsmarker sind gespeichert. Nutzerkeys und Configfingerprints bleiben
privat. [Normaler Start](validation/workflow4-runtime-normal.json),
[eigene QA](validation/workflow4-runtime-qa.json),
[CLI](validation/workflow4-native-fixture.json).

Die eigene QA-Accessibility zeigt flache Controls und initial eingeklappte
Druckerbox, identifiziert aber nicht alle selbst gezeichneten Feldlabels und
Enablezustände. Normale AX enthält keine vollständige Hauptoberfläche.
Direkte Arrange-/Quick-delete-/Undo-Klicks, alle 16 Checkboxwechsel und physische
Sync-/Druckerfälle sind nicht vollständig angenommen. Aktuelle Capture-/Modal-
Cachefehler bleiben Werkzeugbefunde. Die eigene synthetische QA wurde über den
exakt gebundenen Helfer beendet, ohne behaupteten graceful exit oder Stoppen
einer Benutzerapp. [Root-UI-Grenzen](validation/workflow4-ui-observations.json).

Vorhandene Startmenü-/Taskleistenlinks führen zu V7 mit normalem Profil und
AUMID/Icon0. Erfolgreiche öffentliche Unpin-Abfragen bestätigen beide Links;
drei Stockpins bleiben bytegleich, Desktop abwesend. Der fehlgeschlagene erste
Pfad-Split-Versuch ist kein gültiger Beleg. [OS-Pin](validation/workflow4-os-pin.json).

Die [`.6`](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/tag/v02.08.02.61-prefect.6)
ist seit **27.10.2026, 00:22:49 Europe/Zurich** veröffentlicht. Publisher
`40419300381` ist erfolgreich; alle drei anonymen Downloads bestehen SHA256,
beide ZIP-Archive die CRC-Prüfung. Fünf ältere Releases und sechs direkte Tags bleiben unverändert.
[Finaler Veröffentlichungsbeleg](validation/published-release-workflow4.json).
Der finale Dokumentationscommit verändert die gebaute Quelle727 und die 37er-
Patchserie nicht. Frühere `.5`-Laufzeit-/Paketdaten bleiben historisch.

## Historischer, zuletzt veröffentlichter Prüfstand Workflow 3 / Prefect Bambu Studio .5

Quelle `939e0b3ce6dce937502666f334950eec2e0f542a`, Tree
`e397ecc3b38d7a22b6ac4891d0897dfc273d7000`. Der vollständige
[Windows-Lauf 40248952898](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/40248952898)
ist **completed / success**, einschließlich acht nativer C++17-Policytests.
Artefakt `12619554874`, **264.429.447 Byte**, SHA256
`cb9bdf2c59b3cf913bbbbe5a17e5687568000c0b2341462afb9bdb69296246fa`.
Alle **6.756** Dateien der separaten eigenen V6-Installation sind erneut
gehasht und mit dem ZIP verglichen; 13 DeviceWeb-Dateien und elf violette
Icon-Größen stimmen bytegenau überein. 35 Commits seit der Basis rekonstruieren
alle **70 Zwischenbäume** als Rohdiff und Format-Patch.
[Bericht](validation/workflow3.md), [Ergebnisindex](validation/workflow3-results.json).

Ein eigener isolierter V6-GUI-Start und die tatsächlich geladene neue DLL
sind nachgewiesen. Fehlende F12-/F13-Schlüssel erhalten `true`, F09 ist aktiv.
`prefect_arrange_after_import=false` ist ausschließlich eine Einstellung
dieses QA-Profils; der Funktionsstandard bleibt `true`. Der Einstellungsdialog
wurde geöffnet. Zwei aktuelle offizielle Captureversuche liefen jedoch in
einen Timeout; die Workflow-Tabaktivierung scheiterte am Elementcache und
Tastaturnavigation belegt keinen Seitenwechsel. **Keine visuelle Abnahme der
13 Checkboxen, des ersten Anordnungsklicks oder des physischen Druckertipps**
wird daraus abgeleitet. Die eigene Prüfinstanz ist beendet; die bestehende
ungespeicherte Benutzersitzung bleibt unverändert offen. Ein normaler
Profilneustart mit V6 ist noch nicht geprüft.
[Bereinigter Laufzeitbeleg](validation/runtime-workflow3/startup.json).

Startmenü und bereits vorhandener Taskleistenlink sind auf die geprüfte
V6-Installation aktualisiert, mit unveränderten normalen Profilargumenten,
`ChrisPrefect.BambuStudio` und EXE-Icon 0. Der lesende öffentliche Shelltest
vom **26.10.2026, 00:44:34 UTC** bietet bei beiden „Von &Taskleiste lösen“ an;
die drei ursprünglichen Pins bleiben bytegleich, der Desktoplink abwesend.
Dies ist keine neue Pinaktion und kein Neustart über den Pin.
[Metadaten](validation/workflow3-shortcuts.json), [OS-Zustand](validation/workflow3-os-pin.json).

Die [Vorabversion .5](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/tag/v02.08.02.61-prefect.5)
ist seit **26.10.2026, 01:01:23 UTC** veröffentlicht. Alle drei echten anonymen
HTTP-200-Downloads sind vollständig nach SHA256 geprüft; Windows- und Patch-ZIP
bestehen CRC, Quellmarker beziehungsweise 35/70-Manifest stimmen überein.
Die vier älteren Releases mit zwölf Assets und alle fünf direkten Tags sind
erneut geprüft. [Finaler Veröffentlichungsbeleg](validation/published-release-workflow3.json),
[öffentliche Downloads](validation/workflow3-public-downloads.json).
Der [Ergebnisindex](validation/workflow3-results.json) trennt diese Belege
von Build, Installation, Laufzeit und OS-Pin.
Der frühere Lauf `40247351853` auf `3401f393` scheiterte mit C2248:
Ein privater verschachtelter Benachrichtigungstyp wurde in freien Signaturen
benannt. Der aktuelle native MSVC-Build enthält und bestätigt die gezielte
Korrektur auf generische Lambdas; Header/PCH bleiben unverändert.

## Historischer Prüfstand Prefect Bambu Studio .4

Quelle `3cb50caedececb98a21d2792f41c044ee596f759`, Tree
`ca2cd51f1d335f7c5172bad8152b1b727cc0f2fe`. Der vollständige
[Windows-Lauf 40222805625](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/40222805625)
ist **completed / success**. Artefakt `12610262804`, 264.422.804 Byte, SHA256
`def117ac577b143386f226fce6be1189b5a533acc8aa62bb7e97e9bcd4f19ab9`.
Alle 6.756 eigenen Dateien, 13 DeviceWeb-Ressourcen, elf violetten Icon-Größen
sind geprüft. Die früheren Desktop-/Startmenülink-Prüfungen bleiben zeitlich
gebunden; aktuell sind Startmenü und tatsächlicher Taskleistenlink geprüft.
Die 31 Patches rekonstruieren 62 Zwischenstände exakt.

Der tatsächliche eigene GUI-Lauf belegt `CallAfter`-Vorprüfung und live lesbare
verschlüsselte QA-Logs. Der frühere `0x8001010D` tritt an dieser Stelle im neuen
Lauf nicht mehr auf. `GetDefault` liefert nun ein echtes **`0x80070005` /
`E_ACCESSDENIED`**; die Anwendung respektiert dies und führt keinen Pinrequest aus.
Die damaligen offiziellen Capture-/Modalcachepfade lieferten weitere konkrete
Werkzeugfehler. **Der tatsächliche OS-Pin ist jetzt nachgewiesen**: Die lesende
Prüfung vom **25.10.2026, 22:23 UTC** findet den echten Prefect-Taskleistenlink
mit korrekter v5-Installation, normalem Fork-Profil, EXE-Icon 0 und AUMID.
Die öffentliche Shell meldet bei Startmenü- und Taskleistenlink
„Von &Taskleiste lösen“; die drei ursprünglichen Pins bleiben SHA-identisch.
[Damals beobachteter Zustand und Metadaten](validation/taskbar-v5-pin-current-public-summary.json).
Der Desktoplink war nicht vorhanden. Herkunft und Zeitpunkt der
Pinaktion wurden nicht ermittelt; die Prüfung löste keine Pinaktion aus.
Der [frühere Stand ohne Prefect-Pin um 19:24:20 UTC](validation/taskbar-v5-pin-remaining.json)
und der native API-Fehler bleiben historische Befunde. Keine Token-, Registry-,
Sicherheits- oder Datenschutzumgehung wurde dafür vorgenommen.

Die [Vorabversion .4](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/tag/v02.08.02.61-prefect.4)
ist seit **25.10.2026, 19:18:03 UTC** veröffentlicht. Quelle und alle drei anonymen
HTTP-200-Downloads sind vollständig anhand der SHA256 geprüft; .1/.2/.3 blieben
unverändert. [Historischer Bericht](validation/taskbar-v5.md),
[Ergebnisindex](validation/taskbar-v5-results.json),
[Veröffentlichung](validation/published-release-taskbar-v5.json).
Die neue Prüfung wiederholt keine vollständige Workflow-, Drucker- oder Titelmatrix.

## Historischer Prüfstand Prefect Bambu Studio .3

Geprüfter Quellcommit: `aef480ca62cfc9ce86a065e2769efe199d7450d1`, Tree
`aecda9a6db6ebdd470c65228f65c1fae69e8ec22`. Der vollständige
[Windows-Build 40198926718](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/40198926718)
ist **completed / success**. Artefakt `12600886554`, alle 6.756 installierten
Dateien, die 13 DeviceWeb-Ressourcen und elf eingebetteten violetten
Icon-Größen sind geprüft. Drei tatsächliche GUI-Starts bestätigen den
Prefect-Präfix, einen benannten Projekttitel und den Änderungsstern.
Desktop- und Startmenülinks waren geprüft; **ein tatsächlicher OS-Taskleistenpin
war zu diesem historischen Prüfzeitpunkt noch nicht nachgewiesen**. Die neue Titelprüfung wiederholt keine vollständige
Workflow-/Hardwarematrix.

Die Serie aus 28 Patches rekonstruiert alle 56 Zwischenstände beider
Darstellungen exakt. Die [Vorabversion .3](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/tag/v02.08.02.61-prefect.3)
ist seit **25.10.2026, 14:13:20 UTC** veröffentlicht; der direkte Quelltag,
erfolgreiche Veröffentlichungslauf und alle drei anonym frisch geladenen
öffentlichen Assets stimmen mit den erwarteten Größen und SHA-256 überein.
[Aktueller Bericht](validation/branding.md),
[maschinenlesbarer Index](validation/branding-results.json),
[Veröffentlichung und öffentliche Downloads](validation/published-release-branding.json).

Die folgenden Workflow-2- und Workflow-1-Belege behalten ihre ursprünglichen
Quellstände. Sie werden durch die Branding-Prüfung nicht als erneut am
aktuellen Binärstand ausgeführte Tests ausgegeben.

## Historischer Prüfstand Workflow 2 vom 23. Oktober 2026

Die Erweiterung ist an Quellcommit `9d4fad7292484403f0b026972835035b0a967d20`
und Tree `b6feae21b1908e493d880297e901b243073585f5` gebunden.
Sechs native C++17-Policyprogramme, Manifest und Katalog sind geprüft; die
24 Patches rekonstruieren alle 48 Zwischenstände exakt. Der neue Windows-
GUI-Build ist einschließlich Compile, Link, Installation, Paketierung und
Artefakt-Upload erfolgreich. Das Artefakt `12517035086` wurde vollständig
lokal installiert und anhand seiner 6.755 Datei-Hashes geprüft. Paket-SHA-256:
`a595b79dd886562f1413259a9313154ab87912f9dbebf5cabbe781384605ae86`.
Die tatsächlichen GUI-Fälle mit synthetischen Modellen und deren Grenzen
stehen getrennt im [Workflow-2-Bericht](validation/workflow2.md).
Der gesamte Actions-Lauf ist **completed / success**, einschließlich der
abschließenden Cache-Schritte. Drei echte GUI-Neustarts bestätigen
Anordnung mit Rotation, vollständig ausgeschaltete Anordnung und Anordnung
ohne Rotation. Im eingeschalteten Fall ist außerdem automatisches Slicing
nach der Anordnung bis Finished-Status `0` belegt.
[Kompakter Installations-/QA-Index](validation/workflow2-results.json).
Die [Vorabversion Workflow 2](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/tag/v02.08.02.61-prefect.2)
ist am 23.10.2026 um **16:48:01 UTC** veröffentlicht. Frische REST-Abfragen
bestätigen `draft=false`, den direkten Quelltag und alle drei Asset-IDs,
Größen und SHA-256-Werte sowie den erfolgreichen Publikationslauf:
[Veröffentlichungsnachweis](validation/published-release-workflow2.json).

Die folgenden Abschnitte dokumentieren den historischen Workflow-1-Stand.
Sie sind keine pauschale Aussage über die Abnahme neuer Workflow-2-Funktionen.

## Historische Abnahme Workflow 1 vom 21. Oktober 2026

Das [Vorabpaket Workflow 1](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/tag/v02.08.02.61-prefect.1)
ist veröffentlicht. Der [frische Veröffentlichungsnachweis](validation/published-release.json)
bestätigt den tatsächlichen Tag, die drei Assets und den erfolgreichen
Finalisierungslauf; die unten genannten Grenzen der Bedien-/Hardwaretests gelten weiter.

Die vier unabhängigen C++-Policytests wurden erfolgreich kompiliert und
ausgeführt. Alle Assertions waren aktiv. Der dokumentierte Quellvergleich ergibt
keine neu hinzugekommenen Tree-sitter-Syntaxfehlerknoten. Manifestprüfung und
`git diff --check` waren erfolgreich. Der vollständige Windows-Build des
Quellstands `4b5c3546c7fba94439d9bb0fe69553723b895897` ist einschließlich
Linken, Installationsverzeichnis und Artefakt erfolgreich. Die lokale
vollständige Standaloneinstallation und der tatsächliche Programmstart sind
ebenfalls geprüft. Die interaktive Abnahme sämtlicher Bedien- und Hardwarefälle
ist nicht vollständig belegt; [lokaler Laufzeitbericht](validation/local-windows-runtime.md)
und [maschinenlesbare Zusammenfassung](validation/local-windows-runtime.json)
trennen die beobachteten Ergebnisse von diesen Grenzen.

## Geprüfter Quellstand und Belege

- Upstream-Tag: `v02.08.02.61`.
- Upstream-Commit: `926a7192574bcb9b3a732e1ec59a46d79cb45466`.
- Branch: `prefect/workflow`.
- Getestet wurde der geänderte Arbeitsbaum über dieser Basis. Die anschließende
  Feature-Commitserie endet bei `871e85b815541cd2cc698fc9f68c32bc34e5f8c9`;
  die geprüften Quellinhalte blieben dabei unverändert. Zuordnung: [COMMITS.md](COMMITS.md).
- [Maschinenlesbare Ergebnisse und SHA-256-Fingerprints](validation/results.json)
  enthalten die geprüften Test-/Policyquellen mit normalisierten LF-Zeilenenden
  und die Hashes der tatsächlich ausgeführten Test-EXEs.
- [Compiler-/Ausführungsprotokoll](validation/policy-tests.log): reale Ausgabe
  des Test-Runners; lokale absolute Taskpfade wurden durch `$CHECKOUT`, `$ZIG`
  und `$GLOBAL_CACHE` ersetzt; Leerraum am Zeilenende wurde normalisiert. Exitcode: **0**, **9/9 Build-Schritte erfolgreich**.
- [Differentieller Syntaxbericht](validation/syntax-audit.json): Dateien,
  geänderte Funktionen und Fehlerknoten gegenüber dem Basisstand.

Die Fingerprints identifizieren die Prüfquellen auch dann, wenn anschließend
Dokumentations- oder Commitnachrichten ergänzt werden. Nach inhaltlichen
Quelländerungen die betroffenen Prüfungen erneut ausführen und dieses Protokoll
aktualisieren.

## Ausgeführte C++-Regressionstests

Compiler: **Zig 0.14.1** mit gebündeltem Clang und C++-Standardbibliothek,
natives Windows-x86_64-Ziel. Build seriell mit `-j1`, Optimierung `ReleaseFast`.
Für die Testübersetzungseinheiten wurden diese Flags verwendet:

```text
-std=c++17 -UNDEBUG -Wall -Wextra -Werror -pedantic
```

| Testquelle | Geprüfte Policy | Assert-Aufrufstellen im Quelltext | Ergebnis |
| --- | --- | ---: | --- |
| `tests/prefect/background_test.cpp` | Hintergrundslicing: Zustandsgrenzen, Verzögerung, Plattenwechsel, vorbereiteter Start und optionale Skriptentscheidung | 14 | kompiliert, ausgeführt, Exit 0 |
| `tests/prefect/filament_sync_test.cpp` | Filamentabgleich: Synchronisieren, Warten und Stoppen bei Job-/Geräte-/Profilzuständen | 9 | kompiliert, ausgeführt, Exit 0 |
| `tests/prefect/simple_fields_test.cpp` | Eigene Felder: Parser, Serialisierung, Modusgrenzen, unbekannte Schlüssel, leere Auswahl und zweite Option einer gemeinsamen Zeile | 20 | kompiliert, ausgeführt, Exit 0 |
| `tests/prefect/workflow_test.cpp` | Exakte TPU-Cold-Pull-Unterdrückung; andere Meldungen und Schweregrade bleiben unberührt | 8 | kompiliert, ausgeführt, Exit 0 |

Die Zahl benennt statische `assert(...)`-Aufrufstellen, nicht eine behauptete
Anzahl interaktiver Abnahmeszenarien. Schleifen werten einzelne Aufrufstellen
mehrfach aus. Die drei Tests mit Statusausgabe meldeten ihre erfolgreichen
Regressionen; der Filamenttest besitzt keine eigene Textausgabe und wurde über
den erfolgreichen Prozessabschluss geprüft.

### Schutz gegen wirkungslose Release-Tests

Der erste ReleaseFast-Versuch definierte `NDEBUG`. Dadurch entfielen Assertions,
und nur in Assertions verwendete Variablen lösten bei `-Werror` Fehler aus.
Dieser Versuch war kein bestandener Testlauf. Der Runner wurde korrigiert:

1. `tests/prefect/build.zig` übergibt `-UNDEBUG` ausdrücklich an den C++-Compiler.
2. Jede der vier Testquellen besitzt zusätzlich einen `#ifdef NDEBUG`-/
   `#error`-Schutz. Ein künftiger Runner mit abgeschalteten Assertions kann
   diese Dateien nicht erfolgreich kompilieren.
3. Der erfolgreiche Lauf benutzte diese korrigierten Quellen. Die vorhandenen
   Linux-CI-Befehle setzen kein `NDEBUG`; die Schutzprüfung gilt dort ebenfalls.

Außerdem wurden die Cachepfade absolut angegeben. Zuvor fand der gestartete
Runner EXEs aus einem relativen Cachepfad wegen unterschiedlicher
Arbeitsverzeichnisse nicht. Der erfolgreiche Lauf verwendete eindeutige
absolute lokale und globale Cacheverzeichnisse und führte alle vier EXEs aus.

### Reproduzierbarer Einstieg

Im Repository-Stamm, mit einem installierten Zig 0.14.1 und zuvor aufgelösten
absoluten Pfaden:

```powershell
$checkout = (Get-Location).Path
$zigExecutable = 'C:\Pfad\zu\zig.exe'
$localCache = Join-Path $checkout 'out\prefect-zig-cache'
$globalCache = 'C:\Pfad\zum\separaten\zig-cache'
& $zigExecutable build --build-file (Join-Path $checkout 'tests\prefect\build.zig') -j1 -Doptimize=ReleaseFast --cache-dir $localCache --global-cache-dir $globalCache --verbose --summary all
if ($LASTEXITCODE -ne 0) { throw 'Policytests fehlgeschlagen.' }
```

Die beim protokollierten Lauf entstandenen Kopien liegen lokal unter
`out/prefect-tests/{background,filament_sync,simple_fields,workflow}.exe`.
Diese EXEs sind eigenständige Prüftools, keine Bambu-Studio-Anwendung und kein
Beleg für deren GUI- oder Druckerfunktionen.

## Differentieller Syntaxaudit

Der Audit verwendete **tree-sitter 0.25.2** mit **tree-sitter-cpp 0.23.4**,
verglich den aktuellen Arbeitsbaum mit Git-HEAD auf dem Ausgangscommit und
normalisierte vorhandene Makro-/Präprozessorfehler für den Vergleich.

| Kennzahl | Ergebnis |
| --- | ---: |
| Untersuchte geänderte/neue C++-Dateien | 27 |
| Fehlerknoten bereits in der Basis | 60 |
| Fehlerknoten im aktuellen Stand | 60 |
| Neu hinzugekommene Fehlerknoten | **0** |

Die bestehenden Fehlerknoten wurden nicht als Compilerfehler ausgegeben: Ein
Parser ohne vollständige Präprozessor-/Projektkonfiguration kann gültige
Makrokonstruktionen nicht immer vollständig interpretieren. Umgekehrt bedeutet
„keine zusätzlichen Fehlerknoten“ weder korrekte C++-Typauflösung noch
erfolgreiches Linken. Der Audit ersetzt deshalb keinen Compilerlauf der GUI.

## Weitere ausgeführte Prüfungen

- `python scripts/prefect/check_manifest.py`: erfolgreich; alle neun Feature-IDs
  besitzen Detaildokumentation und passende Quellcodeanker.
- `git diff --check`: erfolgreich; lediglich Hinweise auf spätere automatische
  LF-/CRLF-Konvertierung in zwei Arbeitsdateien, keine Whitespacefehler.
- Quellcode-Review prüfte unter anderem AppConfig-Vollständigkeit der Includes,
  ausgeglichene ImGui-Begin/End-/Style-Pfade beim Verbergen der Tipps,
  Zuordnung von ausgewähltem Filament zum aktuellen Menüindex und die
  Sichtbarkeit gemeinsamer Optionszeilen. Daraus wird kein Laufzeitnachweis
  abgeleitet.

## Zusätzlicher nativer Windows-Lauf und Patch-Rekonstruktion

Der Quellstand `aefb764d3a36e05004ec82e20ddf37714ce718a7` enthält außerdem
die geprüften G-Code-Ansichts- und Auswahlfilterkorrekturen. Alle vier
Policytests wurden mit **Microsoft MSVC 19.50.35739 / Linker 14.50.35739**
erneut kompiliert, gelinkt und ausgeführt: jeweils Compiler- und Test-Exitcode
**0**. Optionen: `/MD /EHsc /std:c++17 /utf-8 /W4 /WX`; Assertions bleiben
aktiv. [Originalprotokoll mit Quell-/EXE-/Compiler-Hashes](validation/msvc-policy-tests.log).
Dieser zusätzliche Lauf ersetzt ebenfalls keinen vollständigen GUI-Build.

Alle **20 Commits** bis einschließlich `4b5c3546c7fba94439d9bb0fe69553723b895897`
wurden zweimal auf der unveränderten
Upstream-Basis rekonstruiert: einmal mit rohen Git-Diffs, einmal mit den
tatsächlich exportierten Format-Patches. **Alle 40 Treevergleiche bestanden**;
der Endtree ist `418524ef74e1e2d49ec1cf9d3fa6e422df072afc`. Der normale
Repository-Index blieb unverändert. [Prüfbericht](validation/patch-replay.md),
[maschinenlesbare Einzelbelege](validation/patch-replay.json) und
[reproduzierbares Werkzeug](tools/export_and_replay_patches.py).
Maschinenspezifische Pfadpräfixe sind in den veröffentlichten Belegen durch
`$CHECKOUT` beziehungsweise `$PATCH_DIR` ersetzt; Inhalts-Hashes und Exitcodes
bleiben erhalten. Dieser Nachweis betrifft die festgelegte Basis, keine
behauptete konfliktfreie Anwendung auf eine unbekannte zukünftige Version.

## Vollständiger Windows-Build

### Aktueller Stand 4b5c einschließlich F01-Nachholfall

[GitHub-Actions-Lauf 39623913865](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/39623913865)
ist für den Quellcommit `4b5c3546c7fba94439d9bb0fe69553723b895897`, Tree
`418524ef74e1e2d49ec1cf9d3fa6e422df072afc`, vollständig **success**.
Die frische API-Prüfung vom **21.10.2026, 16:45:10 UTC** bestätigt beide Jobs:
Policy-/Manifestjob **119304237107** sowie Windows-Job **119304581333**.
Alle Anwendungsquellen wurden kompiliert und gelinkt, das Paket installiert
und als Artefakt hochgeladen. Auch die beiden Windows-Regressionsskripte sind
erfolgreich. Dieser Stand enthält den F01-Nachholfall beim erneuten Einschalten.

- Dependency-Normalisierung: **675** Metadaten-Dateien geprüft,
  **37** Referenzen in **12** Dateien relokiert.
- Tatsächlicher Linkinput-Preflight: **127** Projekte, **82** vorhandene
  Dependency-Libraries, Release/x64.
- Inputmanifest: **40909** Dateien erfasst, **0** instabile Dateien übersprungen.
- Artefakt **12360594342**, **264.362.107 Bytes**, SHA-256
  `c2e28e59dba400e6414b208983f50567020dbc37e1a01ff3ae8d446309f874bc`.

Beide Caches meldeten einen **Miss**; es wurde kein Inputmanifest restauriert.
Die Runner-Imageversion wechselte gegenüber dem früheren Erfolg von
`20261018.275.1` auf `20261007.264.1`. Die Imageversion ist Bestandteil des
Toolchain-Fingerprints, daher passte die vorherige Cachefamilie nicht.
Die Anwendung wurde vollständig neu gebaut; beide neuen Cache-Saves sind
anschließend ausdrücklich bestätigt. Dieser Run belegt keine inkrementelle
Wiederverwendung alter Anwendungsobjekte.

[Frische API-Metadaten](validation/cloud-build-4b5c.json) und
[kurzer authentischer Log-/Cachenachweis](validation/cloud-build-4b5c.md)
halten die Details ohne Rohlogs oder persönliche Profildaten fest.
Die **interaktive GUI-Abnahme ist nicht vollständig belegt**; aus dem CI-Erfolg
wird kein vollständiger Bedien- oder Druckertest abgeleitet. Der tatsächliche lokale
Programmstart ist inzwischen durch den separaten Laufzeitnachweis unten belegt.

### Früherer vollständiger Stand ab6b

[GitHub-Actions-Lauf 39520066087](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/39520066087)
hat beide Jobs erfolgreich abgeschlossen. Der Windows-Job umfasst alle
Anwendungsquellen, das abschließende Linken und CMake-Installieren. Die vier
Policytests und die Manifestprüfung sind im separaten Linux-Job bestanden.
Die beiden Windows-Regressionsskripte für Cache-Eingaben sowie Dependency-
Relokation/Linkprüfung sind ebenfalls erfolgreich.

Der tatsächliche Dependency-Baum wurde vor der Kompilierung normalisiert:
37 Referenzen in zwölf Metadaten-Dateien; die anschließende Prüfung erfasste
127 generierte Projekte und 82 vorhandene Dependency-Bibliotheken.
Der Compile-/Installationsschritt lief am 21.10.2026 von 00:18:33 bis
01:34:42 UTC erfolgreich. Dependency- und Anwendungscache wurden danach
erfolgreich gesichert.

Artefakt **12314660106**, **264.361.825 Bytes**, SHA-256
`70fd163a738b4042cadde0511d3c3c31a4a17fef527e90ec79f95939c92810ea`.
[API-Metadaten und Zuordnung zum Quellcommit](validation/cloud-build-ab6b.json).
Dieser Buildnachweis ist von der lokalen Bedien- und Geräteabnahme zu unterscheiden.

## Lokale Standaloneinstallation und tatsächlicher Start

Das finale Artefakt wurde vollständig lokal gespeichert, anhand seiner
264.362.107 Bytes und seines oben genannten SHA-256 authentifiziert und unter
`%USERPROFILE%\BambuStudio-Prefect-Windows` installiert. Alle **6.755 eigenen
Dateikopien**, **274 Ordner** und **600.390.512 unkomprimierten Bytes** wurden
am tatsächlichen Ziel mit der vollständigen ZIP-Struktur und sämtlichen
Datei-SHA-256 verglichen. Jede Datei hat NTFS-Linkcount 1; es wurden keine
Hardlinks, Symlinks oder Ressourcen-Junctions angelegt. ZIP-CRC, sichere Pfade,
vollständiger Quellmarker und **482 direkte PE-Imports** sind geprüft.

Die eigene EXE startete mit dem isolierten Profil
`%APPDATA%\BambuStudio-Prefect`: einmal mit zwei STL-Prüfmodellen als Argumenten
und nachfolgend ohne Modellargumente. Die Desktop-Verknüpfung **BambuStudio
Prefect** verweist auf diese EXE und das isolierte Profil. Die deutsche
Accessibility-Struktur zeigte **Felder...**, die eingeklappte Drucker-Box und
fünf Filamentslots. Die Profilmigration steht auf Revision `1`;
Hintergrundslicing sowie F01/F03/F05/F07/F08/F09 sind aktiv. Die eigene einfache
Feldauswahl bleibt mit `prefect_simple_fields_enabled=false` beim Standard.

Ein anfänglicher upstreamseitiger **Tipps**-Modal für einen Filamentswitcher
war nach Neustart nicht mehr vorhanden. Der dazugehörige bestehende Schlüssel
`show_fila_switch_tips=false` ist bestätigt. Er betrifft den Ready-Hinweis,
nicht den separaten Warnpfad eines unkalibrierten Switchers und nicht F09.

Der ausführliche [lokale Laufzeitbericht](validation/local-windows-runtime.md)
und die [normierte JSON-Zusammenfassung](validation/local-windows-runtime.json)
benennen die privaten Protokollfingerprints. Personenbezogene Profile,
Gerätedaten, rohe Accessibility-Bäume und Anwendungslogs werden nicht veröffentlicht.

## Laufzeit- und Gerätenachweise

| Bereich | Tatsächlich belegt | Grenze des Nachweises |
| --- | --- | --- |
| Vollständige Bambu-Studio-GUI | Compile/Link und lokaler Start für `4b5c3546` erfolgreich | vollständige interaktive Funktionsabnahme nicht abgeschlossen |
| Standalone-Fork-Anwendung | vollständige eigene Installation, exakte Paket-/Dateihashes, Desktop-Einstieg und isoliertes Profil | keine Behauptung eines realen Drucktests |
| GitHub-CI | Run 39623913865 vollständig erfolgreich | Build-/Policybeleg, kein Hardwaretest |
| F01 Geräteabgleich | aktiviertes Profil und fünf sichtbare Filamentslots | physische Spulenänderung, wiederholter Sync und Offline-/Reconnect-Fälle nicht vollständig ausgeführt |
| F02/F03 | **Felder...** und eingeklappte Drucker-Box sichtbar | Pickerbedienung und gespeicherte eigene Feldauswahl nicht vollständig geprüft |
| F05/F06/F07/F08/F09 | Quell-/Build-/Policybelege; Start mit zwei STL-Argumenten; Fork-Schalter aktiv | Pointer-/Menüaktionen, Importobjektzahl, TPU-Druck und vollständiges Slicing-Tippslayout nicht vollständig abgenommen |
| F04 echter Slicer-Worker | Zustands-Policytests bestanden, Profil aktiviert | tatsächlicher automatischer Fortschritt, Editieren, Plattenwechsel, Slice-All/Export und Skriptwahl nicht vollständig interaktiv ausgeführt |
| Sprache und Profilmigration | deutsche Oberfläche, Revision `1`, isolierter Start und Neustart beobachtet | weitere Profil-/Sprachkombinationen nicht als Laufzeitserie geprüft |

Die native Sky-Aufnahme scheiterte auch beim Datei-Explorer mit **FrameArrived
timeout**. Accessibility-Text war teilweise lesbar, während Pointergeometrie
und Elementcache unzuverlässig waren. Die lesende Windows-Sitzungsprüfung
bestätigte eine aktive, entsperrte Konsole mit sichtbarer Desktopfläche
1600 × 900; das belegt weder eine funktionierende Capture-Schnittstelle noch
einen Featuredeadlock. Diese Werkzeuggrenze wird nicht als bestandene
Bedienprüfung ausgegeben. Die vollständigen Abnahmeszenarien bleiben in den
neun Detaildokumenten und [UPSTREAM-UPDATES.md](UPSTREAM-UPDATES.md) beschrieben.
