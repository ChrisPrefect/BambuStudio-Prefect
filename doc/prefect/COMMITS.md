# Lokale Feature-Commitserie

Basis: `v02.08.02.61` / `926a7192574bcb9b3a732e1ec59a46d79cb45466`.

Die folgende Reihenfolge trennt die gemeinsame Einstellungsgrundlage und jedes Feature.
Beim Nachziehen zuerst die Grundlage und danach die benötigten Feature-Commits übertragen.
Gemeinsame Übersetzungen, Build-/Prüfskripte und diese Übersicht folgen in eigenen Commits.

| ID | Commit | Änderung |
| --- | --- | --- |
| foundation | `cdcc804f0ae838c583155957bb40fcd3a2ea4626` | Prefect: add workflow preferences and migrate isolated profile defaults |
| F01 | `271e6449d056d1d48647f127755bc9751d5c6793` | F01: synchronize project filaments automatically after printer changes |
| F02 | `84dc2b1416eda3f41e879cc19425ef0d4d64d966` | F02: let users choose process fields shown in simple mode |
| F03 | `62c6a22d89a56356f7b0f4e6f72bb7666e0b697a` | F03: keep the printer section collapsed across sidebar refreshes |
| F04 | `dcd6b229cfe1a3da13c1cacc700fa7cd5e441796` | F04: slice the current plate automatically with guarded background jobs |
| F05 | `ff833abb53a99156b03ff15ee720f3fd668b62cc` | F05: assign clicked filament to selected objects and parts |
| F06 | `904901adb509d2b0e7ae97d8bb4574dff0ff42b5` | F06: add filament menu action for the global support interface |
| F07 | `4ef4c7d252a90aaa2965626f973fd165fc55067b` | F07: import multiple models separately without merge questions |
| F08 | `e67394ffb07601ac644dba08016e2a06ad2774c6` | F08: suppress only the exact TPU cold-pull advisory |
| F09 | `871e85b815541cd2cc698fc9f68c32bc34e5f8c9` | F09: hide daily tips and remove their slicing notification space |

Die vollständige Git-Historie enthält zusätzlich die nachfolgenden gemeinsamen Pflege-Commits.
Die maschinenlesbare Feature-Zuordnung steht in [changes.json](changes.json).
Details zum Rebase und Patch-Export stehen in [UPSTREAM-UPDATES.md](UPSTREAM-UPDATES.md).
