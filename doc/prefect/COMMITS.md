# Feature-Commitserie auf GitHub

Basis: `v02.08.02.61` / `926a7192574bcb9b3a732e1ec59a46d79cb45466`.

Die folgende Reihenfolge trennt die gemeinsame Einstellungsgrundlage und jedes Feature.
Beim Nachziehen zuerst die Grundlage und danach die benötigten Feature-Commits übertragen.
Gemeinsame Übersetzungen, Build-/Prüfskripte und diese Übersicht folgen in eigenen Commits.

| ID | Commit | Änderung |
| --- | --- | --- |
| foundation | `7a24a42d0db96d22db5dbb7a08699a1a2a8e1443` | Prefect: add workflow preferences and migrate isolated profile defaults |
| F01 | `7bde42eed27083591b1c26ffedf3441636ff1620` | F01: synchronize project filaments automatically after printer changes |
| F02 | `24ec77e37aa7386a28685b9dc2c4e25eedbceed4` | F02: let users choose process fields shown in simple mode |
| F03 | `21a50b6a27492730d65596854120e12d3fca1401` | F03: keep the printer section collapsed across sidebar refreshes |
| F04 | `5ff0e5923769afbebb27992cd3ab0bad5668aeac` | F04: slice the current plate automatically with guarded background jobs |
| F05 | `259a5f96c6124102d6865d8b08b82ebbf62abf76` | F05: assign clicked filament to selected objects and parts |
| F06 | `8e00cd6931e28b38966ffbf502d82b1f5f4546c6` | F06: add filament menu action for the global support interface |
| F07 | `b5cbd93c935b27ae703cfdb67168d7cab51d3e04` | F07: import multiple models separately without merge questions |
| F08 | `9edd36287f0c15ded96232ea4338141d127044a2` | F08: suppress only the exact TPU cold-pull advisory |
| F09 | `159fc3816810124188975ffa8069ffa64000daf9` | F09: hide daily tips and remove their slicing notification space |

Die vollständige Git-Historie enthält zusätzlich die nachfolgenden gemeinsamen Pflege-Commits.
Die maschinenlesbare Feature-Zuordnung steht in [changes.json](changes.json).
Details zum Rebase und Patch-Export stehen in [UPSTREAM-UPDATES.md](UPSTREAM-UPDATES.md).

Die unveränderten ursprünglichen lokalen Commit-IDs und ihre GitHub-Zuordnung stehen in [remote-commits.json](remote-commits.json). Die Originalserie ist lokal unter `prefect/local-series-20261021` gesichert; die Tree-SHAs jeder Stufe stimmen überein.

Ergänzende Commits nach der ersten Feature-Serie:

| Commit | Bedeutung beim Nachtragen |
| --- | --- |
| `2b4187439a730f620ffff52c0d828a8f19ad1018` | CI-Compiler automatisch erkennen; nur exakt passende offizielle Abhängigkeiten wiederverwenden; GitHub-Commitzuordnung dokumentieren |
| `8862ffb3d4f9968c932132e28edc135399603361` | F01/F05/F06 zusätzlich vor Änderungen in reinen G-Code-Ansichten schützen |
| `aefb764d3a36e05004ec82e20ddf37714ce718a7` | F05 auf tatsächlich zuweisbare Modellzeilen begrenzen, Erfolg zurückmelden und nutzlosen Undo-Eintrag vermeiden; Fork-Startseite und Abhängigkeits-Layoutprüfung |
| `a10f94e49bb2863135955f37230cf8e099982b3c` | Native Windows-Prüfung der vier Policies und rekonstruierbare Patchserie dokumentieren |
| `ab6b1e83b32e6bffd5d7cc8da6ef8858617baf2a` | Absolute Bibliothekspfade des offiziellen Dependency-Pakets relokieren und vor dem Compilelauf prüfen; kompatible Zwischenstände mit geprüften Eingangsdaten wiederverwenden; beide Mechanismen unter Windows testen |
| `4b5c3546c7fba94439d9bb0fe69553723b895897` | F01 beim Wiedereinschalten mit dem frischen Druckerstand nachholen, auch wenn dieser während der ausgeschalteten Option bereits empfangen wurde; vorhandene Timer-Policy beibehalten |

Die vollständigen 20 Stufen dieser Serie wurden sowohl als Rohdiffs als auch
als exportierte Format-Patches erneut angewendet. Alle Zwischen- und Endtrees
stimmen überein: [Nachweis](validation/patch-replay.md).
