# Windows-Build und Auslieferung

Der Anwendungsworkflow liegt in
`.github/workflows/prefect-workflow.yml` auf `prefect/workflow`.
Er führt zuerst alle sechs C++17-Policytests und die Manifestprüfung aus.
Danach baut er unter Windows die vollständige GUI und das portable
Installationsverzeichnis. Der tatsächliche Ergebnisnachweis steht in
[VALIDATION.md](VALIDATION.md); die Existenz des Workflows allein ist kein
Buildnachweis.

Der aktuelle vollständige Windows-Build
[40222805625](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/40222805625)
für `3cb50caedececb98a21d2792f41c044ee596f759` ist erfolgreich. Die
[veröffentlichte Vorabversion .4](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/tag/v02.08.02.61-prefect.4)
enthält das geprüfte Windows-Paket mit 6.756 Dateien, die Serie aus 31
Patches und `SHA256SUMS.txt`. Alle 62 Replay-Zwischenstände und die drei
öffentlichen Downloads sind geprüft. [Aktueller Auslieferungsbericht](validation/taskbar-v5.md)
und [Veröffentlichungsbeleg](validation/published-release-taskbar-v5.json).
Der eigene GUI-Lauf bestätigt die verzögerte COM-Vorprüfung und Live-QA-Logs;
die native API lehnt `GetDefault` mit `E_ACCESSDENIED` ab. Das tatsächliche
OS-Anheften bleibt offen. Desktop und Startmenü sind auf v5 umgestellt.

Der [historische Auslieferungsbericht .3](validation/branding.md) behält
seinen damaligen Build 40198926718, seine 28/56-Patchbelege und drei Titelprüfungen.
Diese werden nicht als neue Tests am v5-Binärstand ausgegeben.

## Compiler und Abhängigkeiten

Der Workflow übernimmt die vom MSVC-Setup tatsächlich ausgewählte
Visual-Studio-Hauptversion. Für VS 17 wird der Generator `Visual Studio 17 2022`,
für VS 18 `Visual Studio 18 2026` verwendet. Ein unerwarteter Hauptversionswechsel
bricht mit einer konkreten Meldung ab, statt einen anderen Compiler stillschweigend
zu erraten. Der Dependency-Cache trennt die Hauptversionen und wird zusätzlich
über die Inhalte von `deps/**` und `cmake/**` gebunden.

Für die Ausgangsbasis kann
`scripts/prefect/Restore-UpstreamDependencies.ps1` das offizielle Artefakt
`bambulab/BambuStudio`, ID `9220135690`, wiederverwenden. Es stammt vom
Upstream-Commit `9a530f77c23d8c3430d1dbef02e103cd8bd6480e`. Seine
Dependency- und CMake-Quellen stimmen exakt mit der gewählten Releasebasis
überein:

| Prüfung | Erwarteter Wert |
| --- | --- |
| `deps`-Tree | `ff281d41e59773ecd48419d60b101529790735fa` |
| `cmake`-Tree | `476b31db07057c30ba134d4e1f488524888a81c8` |
| Äußere ZIP, SHA-256 | `55a5fc5b55a3424ed358e31639000fc726d4e4964b524bab128989eaa87754b5` |
| Innere ZIP, SHA-256 | `50dabbd4e85d30307c9d4b818697e8db0461d2752701076bec2aae87acadcc34` |

Die historische innere Datei heißt
`BambuStudio_dep_win64_20260814_vs2022.zip`, enthält aber Boost-Bibliotheken
mit `vc145` im Namen. Deshalb ist die Wiederverwendung ausdrücklich an VS 18
gebunden. Bei geänderten Trees, anderem Compiler oder nicht mehr verfügbarem
Artefakt nimmt der Workflow den vorhandenen Upstream-Dependency-Bauweg.
Ein Prüfsummenfehler ist ein harter Fehler. Die neue Gesamtversion muss nach
einem Abhängigkeitsupdate einschließlich vollständigem Linken geprüft werden.

Der aktuelle vollständige Build verwendet die überprüften offiziellen
Abhängigkeiten; ein zusätzlicher erfolgreicher Neubau sämtlicher unveränderter
Dependency-Quellen wird damit nicht behauptet.

## Relokation und frühe Linkprüfung

Das Originalpaket enthält zwölf Textmetadaten-Dateien mit dem absoluten
ursprünglichen Installationspräfix
`D:/a/BambuStudio/BambuStudio/deps/build/BambuStudio_dep/usr/local`.
Insbesondere `lib/cmake/occt/OpenCASCADEVisualizationTargets.cmake` verweist
damit auf `freetype.lib`. Ohne Relokation kann der gesamte C++-Compilelauf
erfolgreich sein und erst das abschließende Linken mit `LNK1181` scheitern.

`Restore-UpstreamDependencies.ps1` prüft zunächst die unveränderten ZIP-Hashes
und normalisiert anschließend ausschließlich Textmetadaten im extrahierten
Stagingverzeichnis. Die Suche umfasst den gesamten Präfixbaum, einschließlich
der OpenCV-Metadaten außerhalb von `lib/cmake`. Bibliotheken, DLLs und Header
werden nicht umgeschrieben. BOM und Zeilenenden der Metadaten bleiben erhalten.
`prefect-relocation.json` hält das aktuelle und frühere Präfixe fest, damit auch
ein bereits verschobener Cache erneut normalisiert werden kann.

Nach jeder CMake-Konfiguration läuft `Test-DependencyLinkInputs.ps1`, bevor der
lange Compilerlauf beginnt. Er untersucht generierte Visual-Studio-Projekte
und vorhandene Response-Dateien auf zurückgebliebene Ursprungspräfixe und
kontrolliert absolute Librarypfade im Dependency-Staging für `Release|x64`.
Noch nicht gebaute eigene Projektbibliotheken im Buildverzeichnis sind davon
ausgenommen. Die CI-Hilfsskripte benötigen PowerShell 7.2 oder neuer.

## Wiederverwendbare Zwischenstände

Der Dependency-Cache wird direkt nach dessen erfolgreicher Vorbereitung
gespeichert. Der separate Anwendungscache wird auch nach einem Compiler- oder
Linkfehler gesichert. Beide Cache-Speichervorgänge sind zusätzliche Optimierungen;
eine Cache-Störung ersetzt keine erfolgreiche Configure-, Link- oder Paketprüfung.

Die Anwendungscache-Familie bindet Compiler, SDK, CMake, absolutes Workspace,
Architektur, Dependency-/CMake-Inhalte, Buildflags und die Input-Manifestlogik.
Ein eindeutiger Schlüssel pro Commit, Run und Versuch erlaubt, einen weiter
fortgeschrittenen Zwischenstand neu zu speichern. Beim Wiederherstellen werden
zuerst Zwischenstände desselben Commits, danach derselben kompatiblen Familie
gesucht.

Ein neuer Checkout allein macht sonst sämtliche Objektdateien veraltet:
`Build-CacheInputs.ps1` erfasst Git-Blobidentität, tatsächlichen SHA-256 und
Zeitstempel der Eingabedateien. Nur bei weiterhin identischen Bytes werden
frühere Zeitstempel wiederhergestellt. Echte Änderungen behalten ihren neuen
Zeitstempel. Das Werkzeug verändert keine Dateiinhalte oder Git-Indexeinträge.
Das zugehörige Windows-Testskript weist mit echtem MSBuild nach, dass identische
Eingaben übersprungen und geänderte Eingaben erneut gebaut werden.

`version_metadata_epoch.py` bestimmt `VERSION_METADATA_EPOCH` aus dem letzten
Commit, der eine der tatsächlichen Versions-/Brandingdateien berührt:
`version.inc`, `src/libslic3r/libslic3r.h`,
`src/libslic3r/libslic3r_version.h.in` oder `src/libslic3r/CMakeLists.txt`.
Der letzte Pfad enthält die Erzeugung des Versionsheaders und des Zeitwerts.
Die CI setzt `SOURCE_DATE_EPOCH` auf genau diesen Wert. Bei einem flachen
Checkout wird nur so weit vertieft, bis der Metadatencommit vor der
Shallow-Grenze nachgewiesen ist; ein nicht belegbarer oder lokal veränderter
Metadatenstand bricht ab. Es gibt keinen festgeschriebenen Commit oder Ersatzwert.

**`SLIC3R_BUILD_TIME` bezeichnet in diesem reproduzierbaren Build das Datum
der Versions-/Brandingmetadaten, nicht die Uhrzeit der Kompilierung oder der
letzten beliebigen Quelländerung.** Dies gilt auch für die vorhandene Anzeige
„Build Time“ im Über-Dialog und für die entsprechenden Logfelder. Ein reiner
GUI-Funktionsnachtrag, Workflow- oder Dokumentationsfix ändert dadurch nicht
allein wegen seines Datums den gemeinsam eingebundenen Versionsheader und
sämtliche PCH-Abhängigkeiten. Eine Änderung der genannten Metadaten ändert
den Wert weiterhin. Public-Builds verwenden `BBL_RELEASE_TO_PUBLIC=1` und
lassen `SLIC3R_COMPILE_VERSION` wie bisher leer; interne Builds erhalten
weiterhin ihre normale zusätzliche Git-SHA-Abhängigkeit.

Die echte Quellidentität bleibt unverändert der aktuelle `GITHUB_SHA`, der
Artefaktname und `PREFECT-COMMIT.txt`. Geänderte C++-Bytes/Git-Blobs werden
weiterhin vom unveränderten Input-Manifest erkannt und neu gebaut; die
Epochregel setzt selbst keine Datei-Zeitstempel zurück und schwächt weder
die Toolchain-/CMake-/Flag-Familie noch den tatsächlichen Compile/Link ab.
Tests verwenden getrennte synthetische Git-Historien, prüfen GUI- gegen
Metadatenänderungen, flache Historie und die reale CMake-Headererzeugung.
Der bestehende native MSBuild-Cachetest prüft zusätzlich, dass geänderte
Eingaben trotz wiederverwendeter Umgebung tatsächlich erneut gebaut werden.

## Paketinhalt und Profil

Das Windows-Artefakt enthält das CMake-Installationsverzeichnis,
`Start-Prefect.ps1` und `PREFECT-COMMIT.txt`. Letztere Datei benennt den
tatsächlich gebauten Quellcommit. Das neue Laufzeitprofil wird über `--datadir`
getrennt geführt; [Bedienung und Profilimport](README.md).
Persönliche Profile und Druckerzugänge gehören nicht ins veröffentlichte ZIP.

Der DeviceWeb-Bau benötigt zusätzlich die generierten Dateien außerhalb des
Anwendungscaches. Ein wiederhergestellter aktueller Stamp allein garantiert
deren Existenz nicht. Der Workflow repariert bei fehlenden Ausgaben gezielt
den Stamp, baut das vorhandene `device_page_build`-Target und vergleicht
generierte, Ressourcen- und installierte Bäume vor dem Upload. Der finale
Build enthält alle 13 Dateien. [Ursache, Prüfungen und Update-Anker](device-web-packaging.md),
[Paketnachweis](validation/branding-deviceweb.json).

## Separater Release-Transport

Der Branch
[`delivery/windows`](https://github.com/ChrisPrefect/BambuStudio-Prefect/tree/delivery/windows)
enthält `.github/workflows/prefect-publish.yml` und `delivery/windows/`.
Er überträgt fertige Pakete in einen Release-Entwurf und verändert keine
Anwendungsquellen. Sein Push löst den Anwendungsworkflow nicht erneut aus.

`release.json` bindet den Transport an einen bestimmten Build-Run,
Quellcommit, Quelltree, Release-Tag und die geprüfte Patch-ZIP. Das Python-
Skript wartet auf den erfolgreichen Run, prüft dessen Repository und Head,
GitHub-Artefakt-Digest, ZIP-CRC und `PREFECT-COMMIT.txt`. Erst danach lädt es
das unveränderte Windows-ZIP, die Patchserie und `SHA256SUMS.txt` hoch.
Die Digests der hochgeladenen Assets werden erneut mit der API verglichen.
Ein bereits veröffentlichter Release wird nicht ersetzt. Der Transport allein
veröffentlicht keinen Entwurf.

**Workflow 1 wurde am 21.10.2026 als Vorabversion veröffentlicht.** Vollständiger
Windows-Build, Paketinstallation und tatsächlicher Start sind belegt; die
vollständige interaktive Bedien- und Hardwareabnahme bleibt ausdrücklich offen.
Diese Grenze steht auch im veröffentlichten Releasetext. Der
[Veröffentlichungsnachweis](validation/published-release.json) hält Quellstand,
Tag, Asset-IDs, Größen und SHA-256 sowie den erfolgreichen Finalisierungslauf fest.

Die getrennte `.github/workflows/prefect-finalize.yml` auf `delivery/windows`
prüft vor dem Veröffentlichen exakt den bestehenden Release, seine drei Assets,
die heruntergeladenen Prüfsummenbytes, den echten Tag und die erfolgreichen
Build-/Transportläufe. `delivery/finalization/` enthält dafür den strikt an
diesen Release gebundenen Code, Releasetext und 13 Regressionstests. Die
Veröffentlichung ändert keine Tags, Assets oder Anwendungsquellen. Ein bereits
identisch veröffentlichter Stand wird ohne erneuten Schreibzugriff akzeptiert.

Bei einem Update:

1. Die Feature-Serie nach [UPSTREAM-UPDATES.md](UPSTREAM-UPDATES.md) übertragen
   und prüfen. Neue Patchserie samt Replaynachweis exportieren.
2. Den Anwendungsworkflow erfolgreich für den konkreten neuen Quellcommit
   abschließen lassen und den Binärstand starten/testen.
3. Auf `delivery/windows` die neue Patch-ZIP ablegen und `release.json`
   vollständig aktualisieren, einschließlich `patch_count` für die tatsächlich
   exportierte Serie. Für eine neue Version einen neuen Tag verwenden.
4. Den Transportworkflow ausführen. Seine Prüfung und die Release-Asset-
   Prüfsummen kontrollieren; `prepared-release.json` wird als eigener
   CI-Nachweis abgelegt. Zusätzlich den tatsächlichen Git-Tag mit der Git-Refs-
   API lesen und mit `PREFECT-COMMIT.txt` vergleichen: `target_commitish` eines
   Release-Eintrags allein beweist nicht das Ziel eines bereits vorhandenen Tags.
5. Releasebeschreibung und Prüfprotokoll auf den tatsächlich geprüften
   Endstand bringen und den Entwurf veröffentlichen.
