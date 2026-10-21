# Prüfprotokoll des Prefect-Forks

Stand: **21. Oktober 2026**, Zeitzone Europe/Zurich.

Die vier unabhängigen C++-Policytests wurden erfolgreich kompiliert und
ausgeführt. Alle Assertions waren aktiv. Der aktuelle Quellvergleich ergibt
keine neu hinzugekommenen Tree-sitter-Syntaxfehlerknoten. Manifestprüfung und
`git diff --check` waren erfolgreich. Der vollständige Windows-Build des
Quellstands `ab6b1e83b32e6bffd5d7cc8da6ef8858617baf2a` ist einschließlich
Linken, Installationsverzeichnis und Artefakt erfolgreich. Die lokale
Laufzeitabnahme wird getrennt erfasst.

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

## Laufzeit- und Gerätenachweise

| Bereich | Status dieses Protokolls | Erforderlicher Nachweis |
| --- | --- | --- |
| Vollständige Bambu-Studio-GUI | Compile und Link für `ab6b1e83` erfolgreich | lokaler Start und Bedienung separat prüfen |
| Portable Fork-Anwendung | Artefakt 12314660106 gebaut und dem Quellcommit zugeordnet | erfolgreicher Start mit isoliertem Profil |
| GitHub-CI | Run 39520066087 vollständig erfolgreich | tatsächlicher Workflow-Run und Windows-Artefakt oben verlinkt |
| F01 Geräteabgleich | keine reale Druckerverbindung im Testlauf | Materialänderung am ausgewählten Gerät, Übernahme ohne Dialog und Wiederholungs-/Offlinefälle |
| F02/F03/F05/F06/F07/F08/F09 Bedienung | Quellcode/Policies geprüft | jeweilige Detail-Prüftabellen am gebauten Programm, einschließlich Undo/Redo und Neustart |
| F04 echter Slicer-Worker | Zustands-Policytests bestanden | längeres Modell, Editieren während des Laufs, Plattenwechsel, Slice-All, Export und Skriptwahl |
| Übersetzung und Profilmigration in der GUI | noch keine GUI-Abnahme | Start auf Deutsch und mit neuem/importiertem isoliertem Profil; persistente Entscheidungen nach Neustart |

Das Vorhandensein einer Buildanleitung oder eines Workflows wird nicht als
erstelltes Programm ausgewiesen. Sobald ein tatsächlicher Build oder eine
interaktive Abnahme erfolgreich abgeschlossen ist, diese Tabelle mit Datum,
Fork-Commit, Umgebung und konkretem Beleg fortschreiben. Die vollständigen
Szenarien stehen in den neun Detaildokumenten und
[UPSTREAM-UPDATES.md](UPSTREAM-UPDATES.md).
