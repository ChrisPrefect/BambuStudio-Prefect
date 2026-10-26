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

## Workflow 2

`9d4fad7292484403f0b026972835035b0a967d20` ergänzt F10/F11, die gemeinsame
Einstellungsseite mit elf Schaltern, erweiterte Materialklickpfade und das
schaltbare Supportinterface-Menü. Die gemeinsamen Defaults und Migration auf
Revision 2 stehen in `PrefectWorkflowPreferences.hpp`; die Details werden in
den jeweiligen Featuredokumenten und [workflow-settings.md](workflow-settings.md)
mit Datei-/Funktionsankern erklärt.

Die vollständige Serie bis zu diesem Stand enthält **24 Commits**. Ihre
48 Zwischenstände (Rohdiff und Format-Patch pro Commit) stimmen exakt mit den
Originaltrees überein. Der normale Index blieb unverändert:
[damaliger Replaynachweis](validation/patch-replay-workflow2.md).
Der gebaute Quellstand bleibt unabhängig von späteren reinen Dokumentationscommits
an diesen vollständigen Commit und Tree `b6feae21b1908e493d880297e901b243073585f5`
gebunden.

## Branding und vollständiges DeviceWeb-Paket

Der historische Auslieferungsstand `.3` endet bei
`aef480ca62cfc9ce86a065e2769efe199d7450d1`, Tree
`aecda9a6db6ebdd470c65228f65c1fae69e8ec22`. Die vier zusätzlichen Stufen
über Workflow 2 sind:

| Commit | Bedeutung beim Nachtragen |
| --- | --- |
| `1b158e9ec8d7b9cd9ec5274e348520ed6c0c075f` | Elf Workflow-Schalter, F10/F11 und den geprüften Workflow-2-Patchreplay dokumentieren |
| `7bc9b7949f94a59b9cf2058d9f12d63bf468ad8c` | Tatsächliche Workflow-2-Laufzeitprüfungen und damalige Veröffentlichung dokumentieren |
| `ac0d8686993821d3feb521c9f27ffe1c22eaeba9` | Sichtbaren Namen, zentrale Titelbildung, Windows-Appkennung und violette App-Icons umsetzen; reproduzierbare Asset-Ableitung dokumentieren |
| `aef480ca62cfc9ce86a065e2769efe199d7450d1` | Fehlende generierte DeviceWeb-Ausgaben bei wiederverwendetem Anwendungscache gezielt neu bauen und vor Paketupload prüfen |

Die vollständige Serie enthält **28 Commits**, deren **56 Zwischenstände**
aus Rohdiff- und Format-Patch-Replay exakt mit den Originaltrees übereinstimmen.
[Damals geprüfter Replaynachweis](validation/patch-replay-branding.md),
[damaliger Build-/Installations-/Veröffentlichungsstand](validation/branding.md).
Spätere reine Dokumentationscommits verändern diese Bindung des tatsächlich
gebauten Binärpakets nicht.

## Workflow 3 / Vorabversion .5

Die aktuelle vollständige Serie endet bei
`939e0b3ce6dce937502666f334950eec2e0f542a`, Tree
`e397ecc3b38d7a22b6ac4891d0897dfc273d7000`. Sie enthält **35 Commits**
seit der unveränderten Upstreambasis. Alle **70 Zwischenbäume** beider
Replaydarstellungen stimmen mit den ursprünglichen Git-Objekten überein:
[aktueller Replaynachweis](validation/patch-replay-workflow3.md),
[abschließender Gegenvergleich](validation/patch-replay-workflow3-final.json).

Der historische `.4`-Stand `3cb50caedececb98a21d2792f41c044ee596f759`
behält seine [31/62-Serie](validation/patch-replay-taskbar-v5.md).
Darauf folgen diese vier Commits:

| Commit | Bedeutung beim Nachtragen |
| --- | --- |
| `da45e437c3022e798c942740706ef28db7c5da27` | Veröffentlichung `.4` und konkrete Grenzen der nativen Taskleisten-Vorprüfung dokumentieren |
| `2cf24283fbc22f744fcf56624a28796331c12fb6` | Den danach lesend nachgewiesenen OS-Pin samt unveränderten ursprünglichen Pins dokumentieren |
| `3401f3938e2e3ab70438ea27931496f0f4d4c3b4` | F09 um typisierte und bereits offene Tipps erweitern, F12 sofortiges Anordnen mit offenem Popup und F13 unabhängigen Helio-Werbefilter ergänzen; 13 Workflow-Schalter und acht Policytests |
| `939e0b3ce6dce937502666f334950eec2e0f542a` | Den privaten `NotificationData`-Typ in freien Filtern über generische Lambdas deduzieren; vollständigen GUI-Header/PCH unverändert lassen |

Der native Windows-Build und die veröffentlichte `.5` binden die Binärdateien
an diesen letzten Sourcecommit. Spätere reine Dokuanpassungen werden nicht
als neue Binärquelle oder erneut ausgeführte GUI-Matrix ausgegeben.
[Aktuelle Auslieferung und Prüfgrenzen](validation/workflow3.md).
