# Prefect Bambu Studio .3: Auslieferungs- und Laufzeitnachweis

Stand: **25. Oktober 2026**. Dieser Bericht gehört zum tatsächlich gebauten
und veröffentlichten Quellstand, nicht zu einem vorbereiteten Build.

| Bindung | Geprüfter Wert |
| --- | --- |
| Upstream-Basis | `926a7192574bcb9b3a732e1ec59a46d79cb45466` (`v02.08.02.61`) |
| Quellcommit | `aef480ca62cfc9ce86a065e2769efe199d7450d1` |
| Quelltree | `aecda9a6db6ebdd470c65228f65c1fae69e8ec22` |
| Windows-Build | [40198926718](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/40198926718), **completed / success** |
| Build-Artefakt | `12600886554` |
| Windows-ZIP | `Prefect-Bambu-Studio-2.8.2.61-Windows-x64.zip`, **264.400.383 Bytes** |
| ZIP-SHA-256 | `0ec260a2f8ffdec491d92a1cd27995c3d6f1c67b651e129e76faebc894104d24` |

Der [maschinenlesbare Index](branding-results.json) verknüpft die unten
genannten öffentlichen Belege über ihre SHA-256-Werte. Persönliche Profile,
Anmeldedaten, private Projekte und absolute Rechnerpfade sind darin nicht
enthalten.

Die öffentlichen Dateiverweise im Index verwenden die UTF-8-Bytes der
Git-Blobs mit LF-Zeilenenden. Bei einem Windows-Checkout mit automatischer
CRLF-Konvertierung vor dem Vergleich auf LF normalisieren oder den Git-Blob
lesen. Private Vollbeleg-Hashes sowie Binär- und Archivhashes beziehen sich
weiterhin auf ihre unveränderten Originalbytes. Die öffentliche Kopie des
Replaymanifests ist auf LF normalisiert; das veröffentlichte Patcharchiv
bleibt bytegenau unverändert.

## Vollständiger Build und lokale Installation

Der Windows-Lauf hat die GUI kompiliert, gelinkt, installiert und das portable
Paket erfolgreich hochgeladen. Der [CI-Beleg](branding-ci.json) bindet den
Erfolg an den exakten Quellcommit. Das ZIP wurde vollständig auf CRC geprüft;
sein `PREFECT-COMMIT.txt` stimmt mit dem Quellcommit überein.

Die lokale Installation unter
`%USERPROFILE%\BambuStudio-Prefect-Windows-v3` enthält **6.756 Dateien und
274 Verzeichnisse**. Alle Datei-Hashes stimmen mit dem Paket überein.
Junctions, symbolische Links und Hardlinks: jeweils **0**. Es werden keine
Ressourcen einer anderen installierten Bambu-Studio-Version eingebunden.
[Öffentliche Installationszusammenfassung](branding-installation.json).

| Laufzeitdatei | Bytes | SHA-256 |
| --- | ---: | --- |
| `bambu-studio.exe` | 95.744 | `e113e57c2e6db449de57c438ccab52555d659bfa94b7a0f88b899c419708469c` |
| `BambuStudio.dll` | 139.230.720 | `a800ec6db80a6b816d0594201c13766bc46700d5b05933a1d5189e050b841e84` |

Die **13 DeviceWeb-Dateien** sind vollständig vorhanden; ihre lokalen
Runtime-Abhängigkeiten und die Hashes der öffentlichen Quellassets sind
geprüft. Der frühere Build für `ac0d8686993821d3feb521c9f27ffe1c22eaeba9`
hatte diese Ausgaben trotz erfolgreicher Kompilierung ausgelassen und ist
kein finaler Auslieferungsnachweis. Der aktuelle Stand behebt die Ursache
gezielt im Build-/Paketpfad. [Analyse und Update-Anker](../device-web-packaging.md),
[aktueller Paketbeleg](branding-deviceweb.json). Die Prüfung belegt die
Paketressourcen; sie ist keine interaktive Abnahme des Filament-Managers.

## Name, Icon und tatsächliche Fenstertitel

Die Windows-EXE enthält den Anzeigenamen **Prefect Bambu Studio** und
**elf eingebettete Icon-Größen**: 16, 20, 24, 32, 40, 48, 64, 128, 154,
192 und 256 Pixel. Alle eingebetteten Frame-Bytes stimmen mit dem violetten
Quell-ICO überein. [PE-/Icon-Beleg](branding-pe-icon.json).
Der [reproduzierbare Vektor-Assetnachweis](purple-app-icon.json) prüft
zusätzlich unveränderte Pfade und 22 Alpha-/Rendervergleiche der grünen und
violetten Variante derselben SVG-Quelle. Eine byteidentische Kantenglättung
gegenüber den alten Upstream-Bitmaps wird damit nicht behauptet.
[Generator und Nachtrag bei Updates](../purple-app-icon-assets.md).

Drei frische GUI-Starts der geprüften Installation verwendeten ein getrenntes
Prüfprofil und ausschließlich synthetische Modelle. Die tatsächlichen
Ergebnisse sind:

| Fall | Beobachteter nativer Fenstertitel | Öffentlicher Beleg |
| --- | --- | --- |
| Neues Projekt ohne Datei | `Prefect Bambu Studio - Unbenannt` | [clean](runtime-branding/clean.json) |
| Synthetisches `Prefect-Branding-QA.3mf` | `Prefect Bambu Studio - Prefect-Branding-QA` | [named](runtime-branding/named.json) |
| Zwei synthetische STL-Objekte, ungespeichert | `Prefect Bambu Studio - * Unbenannt` | [dirty](runtime-branding/dirty.json) |

Der neue deutsche Projektname lautet beim echten Start `Unbenannt`; es wird
kein zunächst leerer Projekttext unterstellt. Die letzte Aufnahme erfolgte
um **14:11:03 UTC**. Jede Beobachtung aus der nativen SkyAX-Fensterliste wurde
an den eigenen Prozess, seine exakte Startzeile, Prozessstartidentität und
die oben gepinnten EXE-/DLL-Bytes gebunden. Die öffentlichen Belege enthalten
keine numerischen Prozess- oder Fensterkennungen.

Die Aktivitätszähler in diesen drei JSONs beschreiben ausschließlich den
lesenden Capture-Helfer. Seine Nullwerte für Appstarts, Profiländerungen
und Prozessstopps bedeuten nicht, dass keine GUI gestartet wurde; die drei
tatsächlichen Starts sind separat an ihre Startbelege gebunden.
Ein Screenshot- oder Pixelnachweis der benutzerdefinierten Topbar ist damit
nicht verbunden. Quellstellen und Titelbildung: [12-branding.md](../12-branding.md).

## Desktop, Startmenü und offener Taskleistenpin

Die neuen Desktop- und Startmenülinks heißen **Prefect Bambu Studio**.
Ziel-EXE, Arbeitsverzeichnis, bestehende Profilargumente, Icon-Index `0`
und `System.AppUserModel.ID=ChrisPrefect.BambuStudio` wurden zurückgelesen
und geprüft. Die Anwendung setzt dieselbe Prozesskennung früh vor der UI.
Der vorherige Desktoplink wurde bytegenau gesichert und erst nach Prüfung
beider neuen Links gezielt umbenannt. Bestehende Taskleistenpins blieben
bei dieser Verknüpfungserstellung unverändert.
[Öffentlicher Verknüpfungsbeleg](branding-shortcuts.json).

**Das tatsächliche Anheften an die Windows-Taskleiste bleibt offen.**
Eine vorbereitete `.lnk`, korrekte AppUserModelID und eingebettete Icon-Bytes
sind kein Nachweis eines vorhandenen OS-Pins oder des sichtbaren
Windows-Symbolcaches. Dieser Bericht enthält keinen Pin-Erfolgsclaim.
Das normale Fork-Profil und die Stock-Installation wurden für diese
isolierten GUI-Prüfungen nicht gestartet oder verändert.

## Veröffentlichung und unabhängige öffentliche Downloads

Die [Vorabversion `v02.08.02.61-prefect.3`](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/tag/v02.08.02.61-prefect.3)
ist als Release **423441312** seit **25.10.2026, 14:13:20 UTC** öffentlich
(`draft=false`, `prerelease=true`). Der echte Git-Tag zeigt direkt auf den
oben genannten Quellcommit. Publikationslauf
[40201186272](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/40201186272)
ist **completed / success**. Die älteren Releases `.1` und `.2` blieben
unverändert.

Alle drei kanonischen öffentlichen Download-URLs wurden frisch und anonym
mit HTTP 200 heruntergeladen und unabhängig nach Größe und SHA-256 geprüft.
Beim öffentlichen Windows-ZIP sind außerdem CRC, Quellmarker und alle 13
DeviceWeb-Ressourcen erneut geprüft. [Vollständiger öffentlicher Beleg](published-release-branding.json).

| Asset-ID | Datei | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| 675202019 | Windows-x64-ZIP | 264.400.383 | `0ec260a2f8ffdec491d92a1cd27995c3d6f1c67b651e129e76faebc894104d24` |
| 675202354 | `Prefect-BambuStudio-patches-20261025-devicewebfix.zip` | 1.015.207 | `391cbc28d22d4312a1bcd036e9a8faee12868d4f98653033cbca58ee7dcc300e` |
| 675202414 | `SHA256SUMS.txt` | 232 | `12dc112abb67c78b94e0cdeed4782d0eaa3f60535a91083c60c9d90c2e4ff3a6` |

## Patchserie und Reichweite der Abnahme

Die aktuelle Serie enthält **28 Commits** über der dokumentierten Basis.
Jeder exportierte Format-Patch und jeder Rohdiff wurde mit einem getrennten
Index erneut angewendet. Alle **56 Zwischenstände** entsprechen exakt den
Originaltrees; der normale Repository-Index und der Quellarbeitsbaum blieben
unverändert. Archivinhalt, CRC, Einzelhashes und öffentliche Pfade sind geprüft.
[Replaybericht](patch-replay-branding.md),
[Commit-/Tree-Einzelbelege](patch-replay-branding.json),
[abschließende Verifikation](patch-replay-branding-verification.json).

Diese Auslieferung prüft das aktuelle Paket, Branding, die drei Titelzustände
und die öffentliche Veröffentlichung. Sie wiederholt keine vollständige
Matrix aller elf Workflow-Schalter und keine Drucker-/Hardwareabnahme.
Die früheren [Workflow-2-Laufzeitbelege](workflow2.md) für Anordnung und
Hintergrundslicing bleiben ausdrücklich an ihren damaligen Quellstand
`9d4fad7292484403f0b026972835035b0a967d20` gebunden. Es wurde kein Druck
automatisch ausgelöst.
