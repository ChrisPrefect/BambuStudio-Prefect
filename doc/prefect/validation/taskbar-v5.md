# Prefect Bambu Studio .4: Auslieferung und Taskleistenprüfung

Die [Vorabversion .4](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/tag/v02.08.02.61-prefect.4) ist veröffentlicht und lokal installiert. Build, Paketbytes, alle Installationsdateien, violette EXE-Ressourcen, normale Verknüpfungen und ein eigener tatsächlicher GUI-Lauf sind geprüft. **Der tatsächliche Windows-Taskleistenpin ist inzwischen nachgewiesen.** Die öffentliche Shell bietet beim Startmenü- und tatsächlichen Taskleistenlink „Von &Taskleiste lösen“ an; Metadaten und unveränderte Originalpins sind geprüft. Der frühere native `E_ACCESSDENIED`-Befund bleibt getrennt erhalten; in jenem GUI-Lauf wurde kein Pinrequest ausgeführt.

| Bindung | Wert |
| --- | --- |
| Quellcommit | `3cb50caedececb98a21d2792f41c044ee596f759` |
| Quelltree | `ca2cd51f1d335f7c5172bad8152b1b727cc0f2fe` |
| Vollständig erfolgreicher Windows-Lauf | [40222805625](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/40222805625), `completed/success` |
| Windows-Artefakt | `12610262804`, 264.422.804 Byte |
| Windows-ZIP SHA256 | `def117ac577b143386f226fce6be1189b5a533acc8aa62bb7e97e9bcd4f19ab9` |
| Öffentlicher Release | `423604332`, veröffentlicht 25.10.2026 um 19:18:03 UTC, Prerelease, kein Draft |
| Veröffentlichungslauf | [40225345075](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/40225345075), `completed/success` |
| Patchserie | 31 Commits, 62 identische Zwischenstände |

[Maschinenlesbarer Ergebnisindex](taskbar-v5-results.json), [CI-Beleg](taskbar-v5-ci.json), [Veröffentlichung und öffentliche Downloads](published-release-taskbar-v5.json), [Patch-Rekonstruktion](patch-replay-taskbar-v5.md).

## Installation, Ressourcen und normale Einstiegspunkte

Alle **6.756 eigenen Dateien** in **274 Verzeichnissen** mit **600.216.856 entpackten Bytes** wurden vollständig mit den Artefaktbytes und SHA256 verglichen. Es entstanden keine Hardlinks, Symlinks oder Junctions. Die Prüfung erfasste 482 direkte PE-Imports und die feste Quellenmarkierung. [Bereinigter Installationsbeleg](taskbar-v5-installation.json).

Die tatsächliche EXE trägt den Anzeigenamen **Prefect Bambu Studio** und elf violette Icon-Größen, deren Bytes exakt den Quellassets entsprechen. Alle 13 DeviceWeb-Ressourcen entsprechen ebenfalls dem Installer. Die sechs neuen Taskbar-Diagnosemarker sind in der tatsächlichen DLL nachgewiesen. [PE-/Ressourcenprüfung](taskbar-v5-resources.json). Die unveränderte Vektorquelle und Ableitung sind in [purple-app-icon-assets.md](../purple-app-icon-assets.md) beschrieben; ein Screenshot des Windows-Symbolcaches wird damit nicht behauptet.

Die frühere Prüfung von 19 Uhr bestätigte Desktop- und Startmenülinks mit **Prefect Bambu Studio**, eigener Windows-v5-Installation und `ChrisPrefect.BambuStudio`. Arbeitsverzeichnis, EXE-Icon 0 und dieselben normalen Fork-`--datadir`-Argumente waren geprüft; die vorherigen Links sind gesichert. Die Prüfung las keine normalen Profildaten. [Historischer Verknüpfungsbeleg](taskbar-v5-shortcuts.json). Aktuell sind Startmenü- und tatsächlicher Taskleistenlink vorhanden und geprüft; der Desktoplink ist nicht vorhanden. Ein Wiederherstellen wurde nicht vorgenommen.

## Nachgetragene COM-Ereignisgrenze

Die optionale native `TaskbarManager`-Integration erscheint ausschließlich mit `PREFECT_QA_TASKBAR_PIN=1`. Die lesende Initialisierung prüft eigene Prozesskennung, dokumentierte LAF-Voraussetzung, Desktopmarker und Taskleistenstatus. Sie verändert keine Berechtigung und erzeugt keinen Token.

Der vorherige reale v4-Lauf erreichte `GetDefault`, scheiterte im direkten Aktivierungs-Handler jedoch mit `-2147417843`, also `0x8001010D`/`RPC_E_CANTCALLOUT_ININPUTSYNCCALL`. Das ist ein COM-Aufruf während einer eingabesynchronen Windows-Verarbeitung, keine Zugriffsablehnung. Deshalb laufen Initialisierung und Aktivierungsprüfung jetzt mit `frame.CallAfter` nach Rückkehr aus diesem Eingabestack auf dem UI-Thread. Schwache Frame-/State-Referenzen und die bestehenden COM-Lebensdauerprüfungen bleiben erhalten. [Microsofts Fehlercodebeschreibung](https://learn.microsoft.com/en-us/windows/win32/com/com-error-codes-3).

Der erste F8 kann nur eine noch ausstehende Vorprüfung nachholen. F8 während einer laufenden Prüfung merkt keinen Pin für später vor. Erst ein neuer F8-/Menüvorgang bei Ready erzeugt genau einen nachgelagerten Intent. Weitere Eingaben bleiben über dessen gesamte reentrante COM-Fortsetzung gesperrt. Der Callback prüft Vordergrund, `IsPinningAllowed` und Vordergrund erneut; erst danach ist höchstens ein Request pro Anwendungszustand möglich. Initialisierung, Aktivierung und Timer erzeugen keinen Pinrequest. [Quellanker und Updateablauf](../taskbar-integration.md).

Nur im eingeschalteten QA-Pfad setzt der vorhandene verschlüsselnde LogSink `auto_flush(true)` unter seinem Backendlock. Dieser Lock endet vor dem Logaufruf; ein zusätzlicher Klartextlog entsteht nicht. Die fixen Diagnosefelder bleiben `stage`, `hresult` und `value`. Die neuen Stages sind eng gebunden: `ui_installed` und `user_action_deferred` jeweils `0/-1`, `preflight_deferred` HRESULT 0 und genau Grund 1, 2 oder 4.

## Tatsächlicher eigener GUI-Lauf und Grenze

Die getrennte v5-Prüfumgebung verwendet 2.517 manifestgeprüfte eigene Presetdateien, einen gültigen Config-MD5-Footer, keine alten MRUs und keine kopierten Anmelde-/Netzwerkplugin-Dateien. Alte v4-Profile und Belege bleiben erhalten. Der QA-Parser weist 14 gezielt ungültige Payloads ab und prüft die exakte CLI sowie den vorzeichenbehafteten HRESULT. Vorbereitung und ihre Null-Appstart-Zähler gelten nur für den Helfer, nicht für die separat gestartete GUI.

Der tatsächliche eigene GUI-Start und die Diagnose sind an Quelle, EXE-/DLL-Bytes, exakte CLI, Prozess-Erstellungsidentität und Launchbeleg gebunden. Noch bei laufender App waren `ui_installed`, `preflight_deferred` mit Grund 1, `qa_enabled`, LAF-Anforderung 0 und der Desktopmarker im verschlüsselten Log lesbar. Danach scheiterte `GetDefault` tatsächlich mit **`-2147024891` = `0x80070005`/`E_ACCESSDENIED`**. Es gab **keinen Pinrequest**. [Unveränderter bereinigter Laufzeitbeleg](runtime-taskbar-v5/preflight.json).

Dieser Lauf zeigt den vorherigen Eingabe-Sync-Fehler an dieser Stelle nicht mehr und bestätigt lesbare Live-Diagnose. Er bestätigt zugleich die echte Zugriffsablehnung der nativen Vorprüfung. Diese wird respektiert. Der vorhandene Desktopmarker allein garantiert die API-Verwendbarkeit auf dem geprüften Windows 10 mit Build 19045 nicht; Microsofts Desktopbeispiel benennt für seinen ursprünglichen Veröffentlichungsstand SDK und Betriebssystem ab Insider-Build 23516. Daraus wird keine zusätzliche konkrete Ursache abgeleitet und keine Erhöhung von Rechten empfohlen. [Microsofts Beispielvoraussetzungen](https://github.com/microsoft/Windows-classic-samples/blob/main/Samples/TaskbarManager/README.md).

Der aktuelle offizielle Windows-Client lieferte bei den geprüften Capture-/Modalpfaden weiterhin `FrameArrived`-/Capture-Timeouts beziehungsweise nicht im Cache verfügbare verschachtelte Modalelemente. Diese konkreten Fehlschläge sind keine allgemeine Unmöglichkeitsaussage. Es wurden keine Sicherheits-/Datenschutzeinstellungen, Token, private Protokolle oder Taskband-Registrydaten verändert.

Die damalige Dateiprüfung vom **25.10.2026, 19:24:20 UTC** fand genau die drei ursprünglichen TaskBar-Links und keinen Prefect-Link. Sie bleibt als [historisches Inventar](taskbar-v5-pin-remaining.json) unverändert erhalten.

## Aktuell nachgewiesener Windows-Pinzustand

Die neue lesende Prüfung vom **25.10.2026, 22:23 UTC** bestätigt vier tatsächliche TaskBar-Links. `Prefect Bambu Studio.lnk` hat SHA256 `ab0c6ad6f7dc0f947dcd77df67b75891cad620d3f14705d145194518d6a62f8b` und zeigt auf die oben gebundene v5-EXE. Installerbeleg, Quellenmarker und EXE-/DLL-Hashes wurden erneut geprüft. Ziel, Arbeitsverzeichnis, normale Fork-`--datadir`-Argumente, EXE-Icon 0 und `ChrisPrefect.BambuStudio` sind über den normalen COM-PropertyStore zurückgelesen. Alle drei bisherigen TaskBar-Dateien bleiben SHA-identisch. [Vollständiger bereinigter Metadatenbeleg](taskbar-v5-pin-verified-final.json).

Die öffentliche Windows-Shell bietet sowohl am normalen Startmenülink als auch am tatsächlichen Taskleistenlink exakt **„Von &Taskleiste lösen“** an. Damit ist der aktuelle angeheftete OS-Zustand zusätzlich zur vorhandenen Linkdatei nachgewiesen. Die Prüfung rief kein Verb auf, startete keine App und änderte weder Pin noch Profil. [Bereinigter Shellzustand](taskbar-v5-shell-pin-state.json), [kombinierter öffentlicher Ergebnisbeleg](taskbar-v5-pin-current-public-summary.json). Der Shellbeleg enthält ausschließlich die Taskleistenverben und bindet den vollständigen ursprünglichen Prüfbericht per SHA256.

Der Desktoplink ist aktuell nicht vorhanden. Herkunft und Zeitpunkt der Pinaktion sowie des Desktoplink-Wegfalls wurden nicht ermittelt. Es wird weder ein beobachteter eigener Pin-Klick noch eine erfolgreiche `TaskbarManager`-Anfrage behauptet. Der frühere native `E_ACCESSDENIED`-Befund bleibt gültig. Die Startargumente sind anhand der tatsächlichen angehefteten Verknüpfung geprüft; ein neuer Appstart über den Pin und eine Pixelprüfung des sichtbaren Symbolcaches sind damit nicht behauptet.

## Veröffentlichung und historische Abgrenzung

Alle drei öffentlichen HTTPS-Downloads wurden anonym mit HTTP 200 vollständig geladen und nach Bytezahl/SHA256 geprüft. Das Windows-ZIP enthält die 6.756 geprüften Dateien; das Patcharchiv hat **1.114.689 Byte**, SHA256 `437aa4098bd914d9894260ef264f0c70f35b13242690aab51ea1fd94d865d142`. Der Quelltag zeigt direkt auf 3cb50. Die früheren Releases .1, .2 und .3 blieben unverändert. [Frischer Veröffentlichungsnachweis](published-release-taskbar-v5.json).

Die [Brandingbelege der Ausgabe .3](branding.md) einschließlich ihrer drei Titelprüfungen und die [Workflow-2-Laufzeitfälle](workflow2.md) behalten ihre damaligen Quell-/Binärbindungen. Dieser v5-Lauf wiederholt keine vollständige Geräte-, Drucker-, Titel- oder Workflowmatrix. Öffentliche Belege enthalten keine Rohlogs, Konfigurationen, Benutzerpfade, PIDs oder HWNDs.
