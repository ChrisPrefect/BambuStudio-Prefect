# Workflow 3 / Prefect Bambu Studio .5

Quelle `939e0b3ce6dce937502666f334950eec2e0f542a`, Tree
`e397ecc3b38d7a22b6ac4891d0897dfc273d7000`.
Der vollständige [Buildlauf 40248952898](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/40248952898)
ist **completed / success**; die acht nativen Policytests und der Windows-
GUI-Build einschließlich Compile, Link, Paketierung und Cacheabschluss sind
erfolgreich. [Ergebnisindex](workflow3-results.json), [CI-Beleg](workflow3-ci.json).

## Verhalten und Prüfung

- F09 erfasst den Kurvenplanungshinweis `BBLArcFittingInfo`, obwohl er im
  Upstream Warning-Level verwendet. Die automatische Abschaltung der
  Bogenanpassung bleibt erhalten. Explizite Tipp-/Tutorialtypen und
  Vereinfachungshinweise werden semantisch behandelt; aktive und wartende
  Meldungen werden beim Einschalten bereinigt. Echte Druck-/Kalibrierwarnungen
  und Fehler behalten ihre Anzeige. [Updateanker](../09-hide-tips.md).
- F12 startet den vorhandenen Anordnungsjob optional beim Öffnen des
  Toolbar-Popups. Das Popup bleibt offen; seine Optionen sind während des
  Jobs gesperrt. Schließen und beschäftigter Worker starten keinen weiteren
  Auftrag. [Updateanker](../arrange-on-click.md).
- F13 unterdrückt Helio-Werbung und automatische Tutorials unabhängig von F09.
  Ausdrücklich aktivierte Analysen, Ergebnisse und echte Fehler behalten ihre
  Funktion. Drei bereits offene Tutorialtexte werden gezielt bereinigt.
  [Updateanker](../hide-helio-advertising.md).

Die acht C++17-Policytests verwenden aktive Assertions und Warnungen als Fehler.
Die Tipp-/Heliotests prüfen getrennte Schalter, echte Warn-/Fehlerstufen und
aktive sowie verspätete Meldungen. Sie sind keine sichtbare GUI-Bedienprüfung.

`NotificationManager::NotificationData` ist privat. Die beiden freien
Filterhelfer deduzieren den Typ deshalb durch generische Lambdas, statt ihn
in ihren Signaturen zu benennen. Header/PCH bleiben unverändert; Policyaufrufe
sind vollständig als `Slic3r::Prefect::…` qualifiziert. Die kleine native
Compile-Reproduktion und der vollständige aktuelle MSVC-Build sind bestanden.
Der frühere Lauf `40247351853` auf `3401f393` scheiterte mit C2248 und bleibt
ein historischer Fehlversuch, dessen Paket nicht ausgeliefert wird.

## Vollständiges Paket und eigene Installation

| Bindung | Wert |
| --- | --- |
| Artefakt | `12619554874` |
| ZIP-Größe | 264.429.447 Byte |
| ZIP-SHA256 | `cb9bdf2c59b3cf913bbbbe5a17e5687568000c0b2341462afb9bdb69296246fa` |
| Eigene Installation | separate Windows-v6-Installation |
| Datei-/Ordnerzahl | 6.756 / 274 |
| Unkomprimierte Bytes | 600.230.595 |
| DeviceWeb-Ressourcen | 13, alle Bytes mit Installer verglichen |
| Eingebettete violette Icon-Größen | 11, alle Framebytes verglichen |

ZIP-CRC, sichere Paketpfade, exakter Quellmarker, alle Datei-SHA256 und
482 direkte PE-Imports sind geprüft. Nach der Kopie wurden sämtliche
6.756 Dateien erneut gehasht; der tatsächliche Baum entspricht exakt dem
Installer. Jede Datei hat Linkcount 1; keine Junctions, Symlinks oder
Hardlinks wurden angelegt. Die neue DLL enthält die erwarteten F12-/F13-
und Taskleistenmarker. [Installationsbeleg](workflow3-installation.json),
[PE-/Webressourcen](workflow3-resources.json).

## Eigener tatsächlicher GUI-Start und Prüfgrenzen

Der isolierte V6-GUI-Start ist an die tatsächliche EXE und geladene neue DLL
gebunden. Fehlende F12-/F13-Schlüssel erhalten `true`; F09 ist aktiv.
`prefect_arrange_after_import=false` ist nur der bewusst gewählte QA-Wert;
der Standard von F11 bleibt `true`. Der Einstellungsdialog wurde mit sichtbarer
Workflow-Tabbezeichnung geöffnet.

Zwei offizielle Aufnahmeversuche, einschließlich frischer Fensterbindung,
liefen in einen Timeout. Die Tabaktivierung wurde vom Elementcache abgelehnt;
Tastaturnavigation belegt keinen Wechsel auf die Workflow-Seite. Deshalb sind
weder Checkboxpixel/-bedienung aller 13 Funktionen noch der tatsächliche
F12-Erstklick oder ein physisch ausgelöster Kurvenplanungstipp als bestanden
markiert. Die kleine Policyprüfung und der native Build bleiben davon getrennt.
[Bereinigter Laufzeitbeleg](runtime-workflow3/startup.json).

Die eigene QA-Instanz wurde durch den exakt gebundenen Helfer beendet. Die
bestehende ungespeicherte Benutzersitzung bleibt offen und unverändert.
Ein normaler Profilneustart oder das erneute Öffnen über den Pin ist nicht
als ausgeführt belegt. Die installierte Version und die aktualisierten
Einstiegspunkte werden beim nächsten normalen Start verwendet.

## Bestehende Einstiegspunkte und tatsächlicher Windows-Pin

Startmenü und bereits vorhandener Taskleistenlink wurden nach bytegenauer
privater Sicherung auf die geprüfte V6-EXE aktualisiert. Normale Fork-
Profilargumente, `ChrisPrefect.BambuStudio` und EXE-Icon 0 sind erhalten.
Der Desktoplink bleibt abwesend; die drei ursprünglichen Pins sind
SHA-identisch. Es wurde kein neuer Pin erzeugt und kein TaskbarManager-
Request ausgeführt. [Metadatenbeleg](workflow3-shortcuts.json).

Der lesende öffentliche Shelltest vom **26.10.2026, 00:44:34 UTC** bietet bei
Startmenü und tatsächlichem Taskleistenlink jeweils **„Von &Taskleiste lösen“**
an. Zusammen mit den gebundenen Metadaten bestätigt dies den OS-Pin für V6.
Andere Shellverben und private Pfade sind aus dem öffentlichen Bericht
entfernt. Die Herkunft der ursprünglichen Pinaktion und ein Pixeltest des
Windows-Iconcaches werden nicht behauptet. [OS-Zustand](workflow3-os-pin.json).

## Vollständige Patch-Rekonstruktion

35 Commits seit `926a7192574bcb9b3a732e1ec59a46d79cb45466` wurden als
Rohdiffs und Format-Patches angewendet. Alle **70 Zwischenbäume** entsprechen
den tatsächlichen Git-Quellobjekten. Der normale Index blieb bytegleich.
ZIP-CRC, alle Patch-/Diffhashes und öffentliche Pfadbereinigung sind geprüft.

| Archiv | Wert |
| --- | --- |
| Name | `Prefect-BambuStudio-patches-20261026-workflow3.zip` |
| Bytes | 1.404.746 |
| SHA256 | `8abbd698fb04595fa27f793673993eea9d68ad3609f971a02894149035555746` |
| Mitglieder | 73 |

[Replaybericht](patch-replay-workflow3.md),
[vollständiges Manifest](patch-replay-workflow3.json),
[abschließender Tree-Gegenvergleich](patch-replay-workflow3-final.json).

## Veröffentlichung und historische Belege

Die [Vorabversion .5](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/tag/v02.08.02.61-prefect.5)
ist seit **26.10.2026, 01:01:23 UTC** veröffentlicht, Release `423757668`.
Publisher `40252092127` ist erfolgreich. Alle drei tatsächlichen anonymen
HTTP-200-Downloads sind vollständig gehasht. Windows-ZIP und Patch-ZIP
bestehen CRC; der öffentliche Quellmarker und das 35/70-Patchmanifest stimmen.
Die vier älteren Releases mit ihren zwölf Assets und alle fünf direkten
Tags sind unverändert. [Finaler Veröffentlichungsbeleg](published-release-workflow3.json),
[unabhängige öffentliche Downloads](workflow3-public-downloads.json).

- [Windows-ZIP](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/download/v02.08.02.61-prefect.5/Prefect-Bambu-Studio-2.8.2.61-Windows-x64.zip)
- [35er-Patchserie](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/download/v02.08.02.61-prefect.5/Prefect-BambuStudio-patches-20261026-workflow3.zip)
- [SHA256SUMS.txt](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/download/v02.08.02.61-prefect.5/SHA256SUMS.txt)

Der getrennte [Ergebnisindex](workflow3-results.json) führt diese Belege
gesondert von Build, Installation, Laufzeit und OS-Pin.

Der [historische .4-Bericht](taskbar-v5.md), sein damaliger API-Fehler und
der spätere Pinbeleg bleiben an Quelle `3cb50cae` gebunden. Die
[Titelprüfungen .3](branding.md) und [Workflow-2-Prüfungen](workflow2.md)
behalten ebenfalls ihre ursprünglichen Quellen. Sie werden nicht als am
V6-Binärstand erneut ausgeführte Testmatrix ausgegeben.

Öffentliche Nachweise enthalten keine persönlichen Profile, Projekte,
Gerätezugänge, Rohlogs oder Accessibility-Bäume. Die SHA-Verweise des
Ergebnisindex beziehen sich auf Git-kanonische UTF-8-Dateien mit LF.
