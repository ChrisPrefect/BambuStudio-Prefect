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

## Vollständiger Build und Laufzeit

Der vollständige Windows-GUI-Build und die Bedienprüfung des neuen Pakets
werden getrennt vom obigen Policybeleg erfasst. Der erfolgreiche Build von
Workflow 1 ist kein Nachweis für diese neuen wxWidgets-/ImGui-/ArrangeJob-Änderungen.
Bis hier wird kein erfolgreicher neuer GUI-Build oder vollständiger interaktiver
Funktions-/Druckertest behauptet.
