# Bewusstes Anheften der eigenen Prefect-Anwendung

## Zweck und Einstieg

Die Windows-Anwendung kann ihre eigene dokumentierte `TaskbarManager`-Integration
bereitstellen. Sie ist mit `PREFECT_QA_TASKBAR_PIN=1` für eine gezielte lokale
Abnahme einschaltbar. Im normalen Start bleibt dieser zusätzliche Menüeintrag
ausgeblendet. Bei aktiviertem Einstieg zeigt die eigene Topbar den Status und
die Aktion **An Taskleiste anheften** mit **F8**. Ein Pinrequest benötigt einen
späteren tatsächlichen Menüklick oder F8 im Vordergrund. Der Windows-Dialog
bleibt Bestandteil des Ablaufs.

Der erste F8 kann zunächst nur die lesende Vorprüfung starten, wenn das Fenster
beim Start noch nicht im Vordergrund war. Sobald der Status bereit ist, löst
ein weiterer bewusster F8 die Anfrage aus. Ein Timer startet keine Anfrage.

## Quellanker zum Nachtragen

Die Implementierung liegt vollständig in
[`GUI_App.cpp`](../../src/slic3r/GUI/GUI_App.cpp):

- Windows-Includes: das rohe SDK-ABI-Header `windows.ui.shell.h`, `roapi.h` und
  WRL. Das ähnlich benannte `winrt/Windows.UI.Shell.h` ist eine andere
  C++/WinRT-Projektion und darf nicht als Ersatz für die verwendeten
  `ABI::Windows::…`-Typen eingesetzt werden.
- `PrefectTaskbarPin`: Vorprüfung, explizite Anfrage, beobachtender Timer und
  Lebensdauerverwaltung der COM-Objekte.
- `install_prefect_taskbar_pin_ui`: Env-Guard, eigener Topbarmenüpunkt sowie
  zusätzliche F8-, Aktivierungs- und Destroy-Handler. Bestehende Accelerator-
  Einträge und die Behandlung anderer Tasten bleiben erhalten.
- Aufruf nach `mainframe->Show(true)` beim ersten Aufbau und beim Neuerzeugen
  der Oberfläche. Die Menü-ID verhindert eine doppelte Installation am selben
  Frame. Diese Windows-Oberfläche nutzt `topbar()->GetTopMenu()`; eine native
  `GetMenuBar()` ist an dieser Stelle nicht vorhanden.

Die Prozess-AUMID wird von der bestehenden Branding-Initialisierung gesetzt.
Diese Integration liest sie lediglich und verlangt
`ChrisPrefect.BambuStudio`. Startmenüverknüpfung und tatsächliche Anwendung
müssen dieselbe Kennung und den richtigen ausführbaren Pfad verwenden.

## Windows-API und Statusübergänge

Nach einer Vordergrundaktivierung wird die eigene Prozesskennung geprüft.
Der dokumentierte LAF-Test liest ausschließlich den benannten DWORD-Wert des
Taskbar-Pin-Features. Ein fehlender Wert ergibt gemäß Microsoft keine positive
Tokenanforderung. Ein tatsächlich erforderlicher Token oder ein Zugriffsfehler
wird gemeldet; die Anwendung erzeugt keinen Token und ändert keine Berechtigung.

Die ComBase-Exporte werden aus dem System32-Modul dynamisch geladen. Der
Ro-Uninitialize-Zeiger hat den korrekten Typ `void (WINAPI*)()`. Erfolgreiche
`RoInitialize`-Ergebnisse einschließlich `S_FALSE` werden nach Freigabe der
COM-Objekte ausgeglichen. Die dokumentierte Desktop-Marker-IID wird abgefragt,
danach folgen `GetDefault`, die Verfügbarkeitsprüfung und die lesende
`IsCurrentAppPinnedAsync`-Abfrage.

Ein tatsächlicher Benutzerhandler stellt einen einmaligen Intent in die
UI-Ereignisschleife. Dessen `CallAfter`-Fortsetzung prüft den Vordergrund und
`IsPinningAllowed` erneut und ruft erst dann `RequestPinCurrentAppAsync` auf.
Der Pending-Guard bleibt über die gesamte reentrante COM-Fortsetzung gesetzt;
nach Beginn einer Anfrage ist ein zweiter Versuch in derselben Instanz gesperrt.
Der wx-Timer liest lediglich den asynchronen Zustand und das Ergebnis. Eine
Windows-Ablehnung oder ein Fehler wird unverändert als solcher protokolliert.

Auch die lesenden Initialisierungs-/Aktivierungsprüfungen laufen über
`CallAfter`. Der erste reale Lauf zeigte beim direkten Aufruf aus dem
Aktivierungsereignis `0x8001010D` (`RPC_E_CANTCALLOUT_ININPUTSYNCCALL`).
COM kann während eines eingabesynchronen Aufrufs keinen solchen ausgehenden
Aufruf beginnen. Die Fortsetzung kehrt deshalb zuerst aus diesem Windows-
Eingabestack zurück. Sie bleibt auf dem UI-Thread und hält die übrigen
Vordergrund-/Berechtigungsprüfungen bei. Aktivierung, Initialisierung und Timer
erzeugen weiterhin keinen Pinintent. Der beobachtete Fehler ist keine
Berechtigungsablehnung. [Microsofts Fehlercodebeschreibung](https://learn.microsoft.com/en-us/windows/win32/com/com-error-codes-3),
[COM-Aufrufsynchronisation](https://learn.microsoft.com/en-us/windows/win32/com/call-synchronization).

Sichtbare Menüzustände und Aufräumlogik sind an den echten Frame gebunden.
Schwache Frame-/State-Referenzen, lokale starke Callback-/COM-Referenzen und
die verzögerte Apartmentfreigabe schützen den Fall, dass ein synchroner
COM-Aufruf die Windows-Nachrichtenschleife erneut betritt oder das Fenster
währenddessen geschlossen wird. Beim Schließen endet die Timerbeobachtung.

## Diagnose und tatsächlicher Nachweis

Die vorhandene Anwendungsprotokollierung erhält Einträge mit dem Präfix
`PrefectTaskbarPin` und den Feldern `stage`, `hresult` und `value`. Für die
Abnahme wird ein getrenntes lokales Prüfprofil verwendet. Nur im eingeschalteten
QA-Pfad wird am bestehenden Sink `auto_flush(true)` unter dessen Backendlock
gesetzt; der Lock endet vor einem Logaufruf. Damit sind auch kleine Statusfolgen
sofort im vorhandenen verschlüsselten Profil-Log lesbar. Der erste Lauf hatte
sie erst beim regulären Schließen auf die Platte geschrieben. Es entsteht kein
zusätzlicher Klartextlog. `ui_installed`, `preflight_deferred` und
`user_action_deferred` machen Installation und Fortsetzungen unterscheidbar.
Diese Einträge
belegen einen API-Zustand; sie ersetzen die Kontrolle des tatsächlichen
Windows-Pins nicht.

Nach einem positiven Ergebnis ist die neue TaskBar-Verknüpfung separat auf
Anzeigenamen, Ziel-EXE, Arbeitsverzeichnis, Icon, AUMID und Profilargumente
zurückzulesen. Die bisherigen Pins sind dabei zu erhalten. Insbesondere darf
ein während der Prüfung verwendetes Profil nicht versehentlich zum normalen
Startprofil der angehefteten Verknüpfung werden. Eine vorbereitete oder nur
in den TaskBar-Ordner kopierte Datei ist kein erfolgreicher OS-Pin.

Die aktuelle `.6`-Quelle `727a703155237a94e4fcc31ebc4effef515d13f0`
behält den Nachtrag. Der vorhandene Pin und der Startmenülink wurden auf die
vollständig geprüfte V7-Installation aktualisiert. Erfolgreiche öffentliche
Unpin-Abfragen sind an die exakten neuen Linkhashes gebunden; drei ursprüngliche
Pins bleiben bytegleich, Desktop abwesend. Normale Profilargumente, AUMID und
EXE-Icon0 sind erhalten. Dies ist keine neue Pinaktion, kein Test eines Starts
über den Pin und keine Pixelprüfung des Iconcaches.
[Aktueller OS-/Metadatenbeleg](validation/workflow4-os-pin.json),
[aktueller Bericht](validation/workflow4.md).

Die historische `.5`-Quelle `939e0b3ce6dce937502666f334950eec2e0f542a`
behält den Nachtrag. Nach vollständiger V6-Installation wurden nur die beiden
vorhandenen Startmenü-/Taskleistenlinks nach privater Sicherung aktualisiert.
Der öffentliche Shelltest vom 26.10.2026 um 00:44:34 UTC bietet an beiden
„Von &Taskleiste lösen“ an. Ziel, normale Profilargumente, AUMID und EXE-Icon 0
sind gebunden; alle drei ursprünglichen Pins sind bytegleich und der
Desktoplink bleibt abwesend. Es gab keinen neuen Pinrequest und keinen
Neustart über den Pin. [Aktueller OS-/Metadatenbeleg](validation/workflow3-os-pin.json),
[aktueller Paket- und Laufzeitstand](validation/workflow3.md).

Der historische Nachtrag ist mit Quelle `3cb50caedececb98a21d2792f41c044ee596f759`
nativ kompiliert und in [Vorabversion .4](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/tag/v02.08.02.61-prefect.4)
veröffentlicht. Ein tatsächlicher eigener GUI-Lauf bestätigt die verzögerte
Vorprüfung und live lesbare verschlüsselte Logs. Nach Desktopmarker und
LAF-Anforderung 0 liefert `GetDefault` nun tatsächlich `0x80070005`/
`E_ACCESSDENIED`; diese Ablehnung wird respektiert, ohne Pinrequest.
Der vorhandene Marker allein garantiert die Desktop-API-Verwendbarkeit auf
Windows 10/Build 19045 nicht; Microsofts [Desktopbeispiel](https://github.com/microsoft/Windows-classic-samples/blob/main/Samples/TaskbarManager/README.md)
benannte ursprünglich SDK und Windows ab Insider-Build 23516. Daraus wird
keine zusätzliche konkrete Ursache und keine Empfehlung für erhöhte Rechte abgeleitet.

**Der tatsächliche OS-Pinzustand ist inzwischen separat geprüft.** Am
25.10.2026 um 22:23 UTC zeigt die öffentliche Windows-Shell bei normalem
Startmenülink und tatsächlichem Prefect-Taskleistenlink jeweils
„Von &Taskleiste lösen“. Der lesende Linkvergleich bestätigt v5, normales
Fork-Profil, Arbeitsverzeichnis, EXE-Icon 0 und `ChrisPrefect.BambuStudio`;
die drei ursprünglichen Pins waren unverändert. Der Desktoplink war
nicht vorhanden. [Damals geprüfter Pin-/Shellnachweis](validation/taskbar-v5-pin-current-public-summary.json).
Die Herkunft der Pinaktion wurde nicht ermittelt und wird keiner API-Anfrage
oder Agentaktion zugeschrieben. Der frühere `E_ACCESSDENIED`-Befund bleibt
erhalten. Das [Inventar von 19:24 UTC](validation/taskbar-v5-pin-remaining.json)
belegt den damaligen Stand ohne Prefect-Pin. Die damaligen Capture-/Modalcache-
Fehler des offiziellen Clients werden nicht als allgemeine Unmöglichkeit ausgegeben.
[Auslieferungsbericht und Grenzen](validation/taskbar-v5.md),
[gebundener nativer Laufzeitbeleg](validation/runtime-taskbar-v5/preflight.json).

## Primärquellen

- [Microsoft: Pin your app to the taskbar](https://learn.microsoft.com/en-us/windows/apps/develop/windows-integration/pin-to-taskbar)
- [Microsofts Beispiel für eine unpackaged Desktopanwendung](https://github.com/microsoft/Windows-classic-samples/blob/main/Samples/TaskbarManager/CppUnpackagedDesktopTaskbarPin/MainWindow.xaml.cpp)

Beim Übertragen auf einen neuen Upstreamstand zuerst die Topbar- und
Frame-Lebensdaueranker prüfen, anschließend gegen den tatsächlichen SDK-ABI
kompilieren und die Windows-Voraussetzungen im echten eigenen Prozess
beurteilen. Eine frühere Diagnose aus einem unidentifizierten Hilfsprozess
entscheidet nicht über die Berechtigung der eigenen Anwendung.
