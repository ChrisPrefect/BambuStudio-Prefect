# Workflow 2: Prüfstand der Erweiterung

Stand: 23. Oktober 2026, Europe/Zurich.

Quellcommit `9d4fad7292484403f0b026972835035b0a967d20`, Tree
`b6feae21b1908e493d880297e901b243073585f5`.
[Vollständiger Windows-CI-Lauf](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/39975702857).

Die Erweiterung umfasst F10/F11, den Materialklick für Misch-/Verlaufszeilen,
den schaltbaren Supportinterface-Eintrag und die gemeinsame Seite mit elf
Schaltern. Die Detailabläufe und Nachtraganker stehen in den Featuredokumenten
und [workflow-settings.md](../workflow-settings.md).

## Tatsächlich ausgeführte lokale Prüfungen

Auf Windows x64 wurden die sechs C++17-Policyprogramme mit Zig 0.14.1,
`-Wall -Wextra -Werror -pedantic` und aktiven Assertions ausgeführt. Der
`ReleaseFast`-Aufruf verwendet ausdrücklich `-UNDEBUG` aus `build.zig`:

```text
zig build -j1 -Doptimize=ReleaseFast --cache-dir <local-cache> --global-cache-dir <local-global-cache> --summary all
Build Summary: 13/13 steps succeeded
arrange: success
background: success
filament_sync: success
preferences: success
simple_fields: success
workflow: success
```

`arrange_test.cpp` prüft die effektive Rotation, Layoutschutz und die Priorität
dauerhafter Invalidierungsgründe gegenüber vorübergehend beschäftigter UI.
`preferences_test.cpp` prüft dieselben Defaults-/Migrationsfunktionen, die
`AppConfig` verwendet: neue Profile, Revision 1, ausgeschaltete Optionen,
fehlende neue Schlüssel, absichtlich leere Feldliste und höhere Revisionen.
Die bisherigen vier Policyprogramme sind ebenfalls erfolgreich.

Die Syntaxanalyse der 17 geänderten/neuen C++-Dateien zeigt **keinen zusätzlichen
Tree-sitter-Fehler** gegenüber der Basis dieses Updates: 57 bestehende
Makro-/Parsermeldungen, 57 im geänderten Stand. Das ist eine ergänzende
Syntaxkontrolle und kein vollständiger C++-Compilebeleg.

Die Manifestprüfung bestätigt alle **elf** Feature-IDs, vorhandene Dokumente,
Tests und passende Quellanker. Das reproduzierbare deutsche Katalog-Overlay
liest seinen erzeugten MO-Katalog wieder ein und bestätigt **30** Fork-Texte.
Der normale `git diff --check` ist bestanden.

Die vollständige [Patchserie](patch-replay-workflow2.md) rekonstruiert 24
Commits mit 48 exakt passenden Zwischenständen; der Repository-Index blieb
unverändert. Die ZIP enthält 809.077 Bytes und hat SHA-256
`1a59f8918bbcfdc5c79c42a5fcbea5735984e01f09222945ce8f6045a21173a5`.

## Vollständiger Windows-Build und eigenes Paket

Der [Windows-CI-Lauf 39975702857](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/39975702857)
hat den oben genannten Quellstand vollständig kompiliert und gelinkt,
installiert, paketiert und als Windows-x64-Artefakt hochgeladen. Der getrennte
Policyjob ist ebenfalls erfolgreich; das
[authentische CI-Policyprotokoll](workflow2-ci-policy-tests.log) enthält die
Compiler-/Test- und Manifestausgabe. Damit liegt ein vollständiger neuer
GUI-Build für die Workflow-2-Änderungen vor. Die frische Actions-Abfrage vom
23.10.2026 bestätigt den gesamten Lauf als **completed / success**, zuletzt
aktualisiert um **16:41:10 UTC**. Auch die abschließende Inputerfassung,
Cache-Sicherung und Cleanup-Schritte des Windows-Jobs `120489881313` sind
erfolgreich. [Kompakter Installations-/QA-Index](workflow2-results.json).

| Paketbeleg | Wert |
| --- | --- |
| Actions-Artefakt | `12517035086` |
| ZIP-Größe | 264.370.161 Bytes |
| ZIP-SHA-256 | `a595b79dd886562f1413259a9313154ab87912f9dbebf5cabbe781384605ae86` |
| Eigene Dateien / Verzeichnisse | 6.755 / 274 |
| Unkomprimierte Bytes | 600.422.844 |
| Geprüfte direkte PE-Imports | 482 |

Das Paket wurde unter `%USERPROFILE%\BambuStudio-Prefect-Windows-v2`
vollständig mit eigenen Dateien installiert. ZIP-CRC, alle Datei-SHA-256,
exakte Verzeichnisstruktur und der vollständige Quellmarker wurden geprüft.
Jede Datei hat Linkcount 1; Hardlinks, Symlinks und Ressourcen-Junctions
werden nicht verwendet. Der private vollständige Installationsbeleg hat
SHA-256 `4758e2873e8bbf7b0501519d679b4749c23beaa3a2d1a2d3090233f3d54d5f98`.
Die vorherige Anwendung und das normale Fork-Profil wurden dadurch nicht
überschrieben.

## Veröffentlichte Vorabversion

[Workflow 2 / v02.08.02.61-prefect.2](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/tag/v02.08.02.61-prefect.2)
ist am **23.10.2026 um 16:48:01 UTC** als Vorabversion veröffentlicht.
Die frischen GitHub-REST-Abfragen bestätigen Release `422086779` mit
`draft=false`, `prerelease=true` und einen direkten Commit-Tag auf `9d4fad7292484403f0b026972835035b0a967d20`.
Der Publikationslauf `39989717566` ist vollständig erfolgreich.
[Maschinenlesbarer Veröffentlichungsnachweis](published-release-workflow2.json).

| Download | Asset-ID | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| Windows-x64-ZIP | `669745438` | 264.370.161 | `a595b79dd886562f1413259a9313154ab87912f9dbebf5cabbe781384605ae86` |
| 24-Commit-Patchserie | `669746100` | 809.077 | `1a59f8918bbcfdc5c79c42a5fcbea5735984e01f09222945ce8f6045a21173a5` |
| `SHA256SUMS.txt` | `669746155` | 228 | `51f13ae2ee582a3f1967ea2bbe11f52c8867ecafd0d2b70f25dc6cbb5c0bef08` |

## Tatsächliche GUI-Laufzeitprüfung

Die Laufzeitprüfung startet die gebaute GUI-Anwendung mit zwei synthetischen
STL-Quadern, 20 × 30 × 8 mm und 25 × 12 × 10 mm. Sie verwendet ein separates
lokales QA-Profil und pro Fall ein eigenes Prozess-Tempverzeichnis auf C:.
Die bestehenden normalen Profile und deren zuletzt verwendete Verzeichnisse
werden nicht gestartet oder verändert; es erfolgen keine SMB-Zugriffe.

Die Prüfung verbindet Quellmarker und Installer-Hashes mit den tatsächlichen
EXE-/DLL-Hashes, dem gestarteten PID samt exakten Fixtureargumenten, der
MD5-geprüften gespeicherten Konfiguration, dem automatischen GUI-Backup und
den Logs desselben PID. Ein Backup enthält eine Haupt-3MF und zwei separat
gespeicherte Modellcontainer; diese werden lesend zu einer selbständigen
Momentaufnahme zusammengesetzt. Alle gelesenen Dateien werden abschließend
anhand von Stat und SHA-256 auf Stabilität geprüft.

Alle drei Fälle wurden mit getrennten tatsächlichen GUI-Neustarts erfolgreich
geprüft. Die gespeicherte Konfiguration steht jeweils auf Revision `2`; die
fünf zuvor gespeicherten Rotationswerte im Abschnitt `arrange` bleiben alle
ausgeschaltet. Die eingeschaltete F10-Option wirkt somit als Override und
überschreibt die ursprünglichen Anordnungswerte nicht.

| Tatsächlicher GUI-Fall | F10 / F11 / Hintergrundslicing | ArrangeJob | Effektive Rotation | Ergebnis im GUI-Backup |
| --- | --- | ---: | --- | --- |
| [defaults-on](runtime-workflow2/defaults-on.json) | true / true / true | 1 | true | Zwei einzelne Objekte und zwei Instanzen, XY-AABBs getrennt; zweiter Quader um 90° gedreht |
| [both-off](runtime-workflow2/both-off.json) | false / false / false | 0 | kein Job | Zwei einzelne Objekte und zwei Instanzen bleiben am Importort; XY-AABBs überlappen um 240 mm² |
| [rotation-off-arrange-on](runtime-workflow2/rotation-off-arrange-on.json) | false / true / false | 1 | false | Zwei einzelne Objekte und zwei Instanzen, XY-AABBs getrennt, ohne Anordnungsrotation |

`defaults-on` startete mit Revision `1` und fehlenden F10-/F11-Schlüsseln.
Der neue Build ergänzte beide mit `true` und speicherte Revision `2`.
Die anderen beiden Starts bewahren die ausdrücklich gespeicherten
Abschaltentscheidungen. Die öffentlichen JSON-Belege enthalten die elf
normalisierten Schalterwerte und Hashbindungen, keine Rohkonfigurationen,
Gerätezugangsdaten oder privaten absoluten Pfade.
Die obersten Aktivitätszähler wie `app_launches`, `network_calls` und
`profile_writes` beziehen sich ausschließlich auf den lesenden Prüfhelfer.
Die separat gestartete GUI-Anwendung wird durch `process_binding` und
`source_and_binary_binding` nachgewiesen; `activity_scope` stellt diese
Abgrenzung in jedem öffentlichen Fallbeleg ausdrücklich klar.

Im eingeschalteten Fall ist zusätzlich echtes automatisches Hintergrundslicing
belegt. Nach dem protokollierten Rücklauf des Arrange-Algorithmus (Zeile 8961)
folgen Slice-Start (8980), Ende von `Print::process` (9115), erzeugter G-Code
(9532) und `SlicingProcessCompletedEvent` mit Status `0`/Finished (9534).
Die Logzeilen enthalten insgesamt zwei abgeschlossene Slice-Durchläufe und
keinen `background_validation_invalid`-Marker. Die beiden Fälle mit
`background_processing=false` enthalten keinen automatischen Slice-Start.
Die Zeilennummern beziehen sich auf das anhand von SHA-256 gebundene
Laufzeitlog, nicht auf unverlässliche Quellcodezeilen.

Die XY-Prüfung verwendet die vollständigen Instanz-/Komponententransformationen
und Welt-AABBs. AABB-Überlappung ist ein konservativer Geometrienachweis,
kein allgemeiner Dreiecksüberschneidungs- oder Druckbarkeitsbeweis. Die
Mehrdatei-Backups sind durch stabile Stat-/Hash-Nachprüfungen abgesichert;
eine atomare Sperre der laufenden GUI wurde nicht behauptet.

## Desktop-Einstieg und Grenzen der Bedienabnahme

Die bestehende Desktop-Verknüpfung **BambuStudio Prefect patched** wurde auf
die neue EXE in `BambuStudio-Prefect-Windows-v2` umgestellt und anschließend
erneut ausgelesen. Ihr Argument für das normale Fork-Profil bleibt identisch;
die vorherige Verknüpfung wurde gesichert. SHA-256 der neuen Verknüpfung:
`fac0a1be60e5d1c13b95cf341d1c36d0ecaab9fa29ec7aeba1f1781da542fd5b`.
Das bestehende normale Fork-Profil wurde nicht gestartet oder verändert.
Es behält seine vorhandenen Workflow-Entscheidungen; der nächste reguläre
Start führt die oben geprüfte Revision-2-Migration aus.

Die Accessibility-Struktur des neuen Builds zeigt den **Workflow**-Tab und
**Felder...**. Der Klick in den verschachtelten Einstellungsdialog scheiterte
am konkreten Computer-Use-Fehler des zwischengespeicherten Modalzustands.
Die vorangegangene Werkzeugkalibration mit Workflow 1 hatte bei der
Screenshot-Erfassung einen Window-Capture-Timeout gemeldet, auch mit einem
eindeutig benannten QA-Prozess. Diese Screenshotdiagnose gehört zur
Kalibration; beim neuen Quellstand wurde der oben genannte Accessibility-/
Modalpfad geprüft. Daraus wird weder ein Fehler des Forks noch eine
vollständig geprüfte Mausbedienung abgeleitet.

Die drei GUI-Fälle belegen den gemeinsamen Modellimport-/Anordnungs- und
Slicingpfad mit synthetischen Dateien. Nicht vollständig durch diese Fälle
abgedeckt sind Clipboard-Einfügen, sämtliche Mehrplatten-/Abbruchzustände,
die Pointerbedienung des Materialklicks und Supportinterface-Menüs, das
interaktive An-/Ausschalten jedes einzelnen Workflow-Schalters sowie reale
Filament-/Druckerverbindungen und Hardwaredrucke. Kein Druck wurde ausgelöst;
Nutzerprozesse und normale Installation blieben unangetastet.
