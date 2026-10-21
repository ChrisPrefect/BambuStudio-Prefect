# Lokaler Windows-Lauf des finalen Standalonepakets

Stand: **21. Oktober 2026**, Europe/Zurich. Geprüfter Anwendungsquellstand:
`4b5c3546c7fba94439d9bb0fe69553723b895897`, Basis `v02.08.02.61`.
Das vollständige Paket ist lokal installiert und tatsächlich gestartet worden.
Die interaktive Abnahme aller neun Funktionen ist damit nicht vollständig belegt.
Die [maschinenlesbare Zusammenfassung](local-windows-runtime.json) hält diese
Grenze ausdrücklich fest.

## Vollständige eigene Installation

Das finale Windows-Artefakt **12360594342** aus dem erfolgreichen
[CI-Lauf 39623913865](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/39623913865)
wurde vollständig lokal gespeichert und geprüft:

| Prüfung | Tatsächliches Ergebnis |
| --- | --- |
| ZIP-Größe | 264.362.107 Bytes |
| ZIP-SHA-256 | `c2e28e59dba400e6414b208983f50567020dbc37e1a01ff3ae8d446309f874bc` |
| Quellmarker | exakter vollständiger Commit `4b5c3546c7fba94439d9bb0fe69553723b895897` |
| Paketinhalt | 6.755 Dateien, 274 Ordner, 600.390.512 unkomprimierte Bytes |
| ZIP-Prüfung | sichere Windows-Pfade, keine ZIP-Links, jede Datei vollständig mit CRC und SHA-256 geprüft |
| Installationsprüfung | vollständige Datei-/Ordnermenge und sämtliche Datei-SHA-256 am tatsächlichen Ziel erneut geprüft |
| Dateieigentum | 6.755 eigene Kopien; NTFS-Linkcount jeder Datei ist 1 |
| Verbindungen zu anderen Ressourcenverzeichnissen | keine Junctions, Symlinks oder zusätzlich angelegten Hardlinks |
| Native Abhängigkeiten | 482 direkte PE-Imports geprüft und als Paket- oder Windows-Abhängigkeit aufgelöst |

Der ZIP-Hash wurde vor und nach der Installation bestätigt. Die Installation
erfolgte nach Prüfung des Platzbudgets mit zusätzlicher Reserve von 1 GiB.
Das Ziel enthält alle Ressourcen selbst; seine Funktionsfähigkeit setzt keine
Ressourcenverknüpfung zur normalen Studio-Installation voraus.

Normierte lokale Ablage:

```text
%USERPROFILE%\BambuStudio-Prefect-Windows\bambu-studio.exe
%USERPROFILE%\BambuStudio-validation\BambuStudio-Prefect-4b5c-Windows-x64.zip
```

Das private vollständige Installationsprotokoll
`%USERPROFILE%\BambuStudio-validation\standalone-final-install.json`
umfasst 3.665.222 Bytes und hat SHA-256
`def1a1188dc2fc253e57e3891643522477ab890650f21fee4b0ee121881ced0c`.
Es wird wegen der enthaltenen lokalen Dateimetadaten nicht als Rohdatei
veröffentlicht. Diese Zusammenfassung enthält die relevanten Ergebnisse.

## Desktop-Einstieg und isoliertes Profil

Die Desktop-Verknüpfung **BambuStudio Prefect** verweist auf die eigene EXE
und verwendet als Argument:

```text
--datadir "%APPDATA%\BambuStudio-Prefect"
```

Der private Verknüpfungsnachweis hat SHA-256
`92a463bdb0a68bf76963c591259da1b34d60e7ccd8bf7cbbcacb806426c8d8aa`.
Das normale Anwendungsprofil wurde durch diese Auslieferung nicht verändert.

Die ausschließlich auf Anwendungsschlüssel begrenzte Leseprüfung des
Fork-Profils bestätigt `prefect_workflow_revision="1"` und aktiviertes
`background_processing`. F01/F03/F05/F07/F08/F09 stehen jeweils auf `true`.
`prefect_simple_fields_enabled=false`; eine eigene Feldliste ist noch nicht
gespeichert. Damit bleiben die bisherigen Standardfelder der einfachen Ansicht
die Ausgangsauswahl. Die Sprache ist `de_CH`.

## Beobachteter Programmstart

Die tatsächlich laufende EXE wurde dem oben genannten eigenen Paketpfad
zugeordnet. Ein Start verwendete zwei STL-Prüfmodelle als Kommandozeilenargumente;
anschließend erfolgte ein Neustart ohne Modellargumente. Die resultierende
Objektzahl des ersten Imports wurde nicht vollständig verifiziert.
Die Prozessmessung zeigte zu Beginn ungefähr 714 MB privaten Speicher
(etwa 681 MiB); das ist eine Beobachtung dieses Starts, keine Speicherzusage.

Die lesbare Accessibility-Struktur zeigte eine deutsche Oberfläche, den
Zugang **Felder...**, die eingeklappte obere Drucker-Box und fünf Filamentslots.
Diese Beobachtung bestätigt den UI-Zugang zu F02 und den sichtbaren Zustand von
F03. Sie belegt keinen vollständig bedienten F02-Auswahldialog und keine reale
Änderung einer Druckerspule.

### Eigenständiger Filamentswitcher-Hinweis

Beim ersten Start war der Hauptbereich wegen eines modalen Dialogs **Tipps**
deaktiviert. Der Dialog enthielt HTML und **OK**. Er wurde dem bestehenden
Filamentswitcher-Hinweis `Sidebar::priv::show_fila_switch_msg()` zugeordnet.
Nach dem Neustart war dieser Dialog nicht mehr vorhanden und der Hauptbereich
aktiviert. Das ist unabhängig von den DailyTips aus F09.

Der vorhandene Anwendungsschlüssel `show_fila_switch_tips=false` unterdrückt
den einmaligen Hinweis für einen **bereiten** Filamentswitcher. Der
Upstream-Pfad setzt diesen Wert bereits vor dem Öffnen des Hinweises auf
`false`; im verwendeten Fork-Profil ist dieser Wert bestätigt.
Ein erkannter, noch **nicht kalibrierter** Switcher verwendet dagegen einen
separaten Warnpfad mit einem Zustandsflag im Arbeitsspeicher. Diese Warnung
wird durch `show_fila_switch_tips` und F09 nicht pauschal ausgeschaltet.

Stabile Quellanker für spätere Updates:

- `Sidebar::priv::show_filament_switcher_dialog()` und
  `Sidebar::priv::show_fila_switch_msg()` in `src/slic3r/GUI/Plater.cpp`;
- Aufruf im Druckerstatusabgleich und `show_fila_switch_tips` in
  `AppConfig::set_defaults()`;
- HTML-Inhalt und `CenterOnParent()` in `src/slic3r/GUI/MsgDialog.cpp`.

Es wurde keine zusätzliche Sourceänderung zur Unterdrückung dieses Dialogs
als Teil des Laufzeitnachweises vorgenommen.

## Reichweite der interaktiven Abnahme

| Funktion | Belegt | Grenze dieses lokalen Laufs |
| --- | --- | --- |
| F01 | aktiviertes Profil; fünf Filamentslots sichtbar | tatsächliche Spulenänderung, erneute Übernahme sowie Offline-/Reconnect-Fälle nicht vollständig ausgeführt |
| F02 | **Felder...** sichtbar, Standardauswahl aktiv | Pickerbedienung und Persistenz einer eigenen Auswahl nicht vollständig ausgeführt |
| F03 | obere Drucker-Box sichtbar eingeklappt | weitere Zustandswechsel nicht als vollständige Abnahmeserie dokumentiert |
| F04 | Schalter aktiv; separate Policytests bestanden | echter automatischer Workerfortschritt, Editieren, Plattenwechsel und Export nicht vollständig interaktiv geprüft |
| F05/F06 | Source-/Buildnachweise vorhanden | Filamentklick, Kontextmenüaktion, Parameteränderung und Undo/Redo nicht vollständig bedient |
| F07 | echter Appstart mit zwei STL-Argumenten | resultierende Objektzahl und sämtliche Importdialogpfade nicht verifiziert |
| F08 | exakte Unterdrückungs-Policy separat geprüft | kein realer TPU-Druck oder Cold-Pull-Ablauf ausgeführt |
| F09 | Schalter aktiv | vollständiges Layout der Slicing-Meldung nicht interaktiv abgenommen |

Die vier nativen Policytests, die Patch-Rekonstruktion und der vollständige
CI-Compile-/Linklauf sind eigenständige bestandene Prüfungen. Ihre Belege
stehen in [VALIDATION.md](../VALIDATION.md) und im
[finalen CI-Bericht](cloud-build-4b5c.md). Sie werden nicht als Ersatz für
diese nicht vollständig ausgeführten Bedien- oder Hardwarefälle gewertet.

## Grenzen der verwendeten UI-Werkzeuge

Die native Sky-Aufnahme scheiterte mit **FrameArrived timeout** sowohl bei der
Fork-Anwendung als auch beim Datei-Explorer. Accessibility-Text war mit
ausgeschalteter Aufnahme teilweise lesbar; Pointergeometrie, Elementcache und
einige Eingabeaktionen waren unzuverlässig. Daher wird aus diesen Versuchen
kein vollständiger Bediennachweis abgeleitet.

Eine rein lesende Win32-/WTS-Prüfung um **20:50:20 UTC** bestätigte eine aktive,
entsperrte Konsolensitzung, sichtbare `WinSta0`, InputDesktop `Default` und
eine Monitorfläche von **1600 × 900** unter Windows 10 x64, Build 19045.
Damit war keine Bildschirmsperre oder fehlende Desktopfläche nachgewiesen.
Dieser Status beweist seinerseits nicht, dass die Capture-Schnittstelle Frames
liefert. Ein Deadlock der neuen Fork-Funktionen wurde nicht belegt.

Die Veröffentlichung enthält weder rohe Accessibility-Bäume noch persönliche
Projektpfade, Gerätenamen/-kennungen, Anwendungslogs oder Anmeldedaten.
Alle lokalen Benutzerpfade sind durch `%USERPROFILE%` beziehungsweise
`%APPDATA%` normiert.
