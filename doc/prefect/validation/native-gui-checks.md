# Native GUI-Einzelprüfungen mit MSVC

Erfasst: 2026-10-20T23:29:07.535490+00:00. C++-Ausgangsstand: `aefb764d3a36e05004ec82e20ddf37714ce718a7`. Die Quell-SHA256 unten binden jeden Befund an die tatsächlich geprüften Bytes. Keine C++-Datei wurde für diese Prüfungen geändert.

Werkzeuge: nativer Windows-x64-MSVC v145, `cl.exe 19.50.35739`, `link.exe 14.50.35739`, CMake 3.31.12, Ninja 1.13.2; Windows SDK 10.0.26100.9169. Vollständige GUI-CMake-Konfiguration und Ninja-Generierung erfolgreich; dabei wurden echte Compiler-ABI-Proben kompiliert und gelinkt.

Die Abhängigkeiten stammen aus dem offiziellen Bambu-Artefakt `9220135690` (`BambuStudio_dep_win64_20260814`), dessen `deps`- und `cmake`-Git-Bäume mit der Releasebasis `926a7192574bcb9b3a732e1ec59a46d79cb45466` übereinstimmen. Inneres ZIP: SHA256 `50DABBD4E85D30307C9D4B818697E8DB0461D2752701076BEC2AAE87ACADCC34`.

## Erfolgreiche Prüfungen

| Quelldatei | Prüfung | Exit |
|---|---|---|
| `src/libslic3r/AppConfig.cpp` | Optimiertes Objekt (/MD /O2 /Ob2 /Zi) | 0 |
| `src/slic3r/GUI/Preferences.cpp` | Optimiertes Objekt (/MD /O2 /Ob2 /Zi) | 0 |
| `src/slic3r/GUI/OptionsGroup.cpp` | Syntax /Zs | 0 |
| `src/slic3r/GUI/Field.cpp` | Syntax /Zs | 0 |
| `src/slic3r/GUI/Widgets/ComboBox.cpp` | Syntax /Zs | 0 |
| `src/slic3r/GUI/GUI_ObjectList.cpp` | Syntax /Zs | 0 |
| `src/slic3r/GUI/Tab.cpp` | Syntax /Zs + offizieller /FI-PCH-Header | 0 |

Die Objektprüfungen erzeugten tatsächlichen Maschinencode; `/Zs` prüft C++-Syntax und Typen ohne Objektcode, Optimierer-/PDB-Ausgabe oder Linken. Diese Einzelprüfungen belegen keinen vollständigen GUI-Link und keinen GUI-Start; der vollständige CI-Build und der Laufzeittest sind getrennte Nachweise.

## Kommandos und Normierung

Ausgangspunkt war für jede Datei ihr tatsächlicher Eintrag aus `compile_commands.json`, C++17 und die dort erzeugten GUI-/Boost-/wx-Definitionen. Die Include-Reihenfolge blieb erhalten; ausschließlich der Pfad des identischen Abhängigkeits-Headerbaums wurde vom Netzlaufwerk auf dessen lokale Extraktion umgesetzt. Kein zusätzliches `CL=/I` blieb aktiv. SDK-/CRT-Header und Bibliotheken waren dieselben beim Konfigurieren und Prüfen.

- Objektprüfungen: ursprüngliches CMake-Kommando mit `/MD /O2 /Ob2 /Zi -std:c++17 -c`. Objekte, PDB und temporäre Dateien lagen auf dem Buildlaufwerk.
- Syntaxprüfungen: `/Fo...`, `/Fd...`, `/Zi`, `/FS`, `/MP` entfernt; `-c` durch `/Zs` ersetzt. Für die knappe lokale Speichersituation wurde `/Zm520` entfernt; keine Definitions-/Quelldatenänderung.
- `Tab.cpp`: zusätzlich `/FI<SOURCE>/src/slic3r/pchheader.hpp`, um genau die offizielle Windows-/CommCtrl-Include-Reihenfolge zu erhalten. Es wurde kein vorgefertigtes PCH-Binärabbild verwendet.

## Nachgewiesene Include-Reihenfolge bei Tab

Der zunächst ohne offiziellen PCH-Header ausgeführte Tab-Test meldete `TreeView_GetToolTips`/`TreeView_SetToolTips` als unbekannt. Die Ursache liegt im Headerkontext: OCCT `Standard_Macro.hxx` definiert unter Windows `NOUSER`; die SDK-Datei `CommCtrl.h` überspringt dann ihren Inhalt. Der offizielle GUI-PCH-Header bindet Windows/CommCtrl vor OCCT ein. Zwei native Minimalproben bestätigten dies, beide mit Exit 0:

```text
OCCT vor Windows/CommCtrl: NOUSER definiert, TreeView_GetToolTips MISSING
Windows/CommCtrl vor OCCT: NOUSER später definiert, TreeView_GetToolTips DEFINED
```

Der anschließende Tab-Test mit offiziellem `/FI` bestand. Ein Quellpatch an Tab war nicht erforderlich.

## Grenzen der lokalen Umgebung

Der lokale Plater-Test ohne PCH erreichte C1060 (Compiler-Heap erschöpft). Beim gezielten Versuch ohne `/Zm520` scheiterte zusätzlich der frühere PowerShell/.NET-Async-Logger; dieser Versuch liefert keinen gültigen Plater-Befund. Der spätere Python-Logger bestand die kleineren GUI-Prüfungen. Plater wurde lokal nicht als vollständig geprüft gewertet. Der vollständige optimierte PCH-Build ist die separate CI-Prüfung.

## Fingerabdrücke

- Compiler SHA256: `CB461B804D4792DB79046C59E17C42A0214CD5112560486114EBE52FCEC107AD`.
- Linker SHA256: `7BA9173DC57AAA229F122A5D8D27A99E1357C83723A461F7B06765367DBF88EE`.

- `src/libslic3r/AppConfig.cpp`: Quelle `8EF1FBC863AC8548378430289479F1C9E2A6337F559939C84449BFBAEF6B295A`; vollständiges Prüfprotokoll `AppConfig.cpp.object.log`, SHA256 `088765D58F1960D9CE765CD0B594829CA841E6992360904C20FDB651E57EEEC1`.
- `src/slic3r/GUI/Preferences.cpp`: Quelle `F9E2FA7CDE22A5B3981127AC7BE5321A5F25CD5359CFBEB73516AC2B67ED9C28`; vollständiges Prüfprotokoll `Preferences.cpp.object.log`, SHA256 `B6B25A92CAF91614BA59A0E7F61FA2E761A23B79F5AFAE4DC4408D3BBD6D8CEE`.
- `src/slic3r/GUI/OptionsGroup.cpp`: Quelle `AF80744C4BE7A104AFBCB482573F023ACD00F5EA7F1995FA47AD24CEADC214E6`; vollständiges Prüfprotokoll `OptionsGroup.cpp.syntax-default-heap-python.log`, SHA256 `A65C25B98F979B6B26E145880287D25FA9727F0AA835E8174BC109E18A9CBA13`.
- `src/slic3r/GUI/Field.cpp`: Quelle `513C62EFAFC2D017515E1762FEB12768DC857DCC74556020135653697D7E1FA2`; vollständiges Prüfprotokoll `Field.cpp.syntax-default-heap-python.log`, SHA256 `5323C8B0B3756C48B9E861EAD1CD15C4C997E88654A5F623C7F861C78A57DABB`.
- `src/slic3r/GUI/Widgets/ComboBox.cpp`: Quelle `B62BC9F149C97E2EB89C60C6426BB47DBA5EAAA42E821BD69D3F86F2D512E89B`; vollständiges Prüfprotokoll `ComboBox.cpp.syntax-default-heap-python.log`, SHA256 `6AB17C9283F736E214F2C808F172A1F52CE92DA254C804A7F03F284360C0F984`.
- `src/slic3r/GUI/GUI_ObjectList.cpp`: Quelle `045A248278CBF3B9CE9F8E969489AF82AB8FE9F0A7564F76C42751FD3969C3ED`; vollständiges Prüfprotokoll `GUI_ObjectList.cpp.syntax-default-heap-python.log`, SHA256 `1C70C401A8747D0630A9183B8050C73553F96AA1B4AEF8E98E2E0D451A05BF51`.
- `src/slic3r/GUI/Tab.cpp`: Quelle `349585E2313B7DE3FDED728854148BA20446DCE982D359C9C286D7D19B84994F`; vollständiges Prüfprotokoll `Tab.cpp.syntax-default-heap-force-pch-header-python.log`, SHA256 `D3625D63FA697B5D9D2554B02F1CA74EA7F663886EF4111180FD3FBBFE8E9EFE`.

Optimierte Objektartefakte:

- `AppConfig.cpp.obj`: 13280836 Bytes, SHA256 `C0FFFBE4249F8EE24F14EC6C1FA7D66DC144D642882EFA8E3E76C91B1ACE9618`.
- `Preferences.cpp.obj`: 15045245 Bytes, SHA256 `6E517491F052302F933467A0216E88A57C3CD733DD6FEF33371914AD8B1D84E2`.

Die vollständigen Rohprotokolle und Objekte wurden auf dem privaten Buildlaufwerk erhalten. Die vier nativen Policy-Tests sind zusätzlich in [msvc-policy-tests.log](msvc-policy-tests.log) dokumentiert.
