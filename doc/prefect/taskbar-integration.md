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

Der aktive Benutzerhandler prüft den Vordergrund und `IsPinningAllowed`
erneut. Nur dieser Handler ruft `RequestPinCurrentAppAsync` auf. Nach Beginn
einer Anfrage ist ein zweiter Versuch in derselben Instanz gesperrt.
Der wx-Timer liest lediglich den asynchronen Zustand und das Ergebnis. Eine
Windows-Ablehnung oder ein Fehler wird unverändert als solcher protokolliert.

Sichtbare Menüzustände und Aufräumlogik sind an den echten Frame gebunden.
Schwache Frame-/State-Referenzen, lokale starke Callback-/COM-Referenzen und
die verzögerte Apartmentfreigabe schützen den Fall, dass ein synchroner
COM-Aufruf die Windows-Nachrichtenschleife erneut betritt oder das Fenster
währenddessen geschlossen wird. Beim Schließen endet die Timerbeobachtung.

## Diagnose und tatsächlicher Nachweis

Die vorhandene Anwendungsprotokollierung erhält Einträge mit dem Präfix
`PrefectTaskbarPin` und den Feldern `stage`, `hresult` und `value`. Für die
Abnahme wird ein getrenntes lokales Prüfprofil verwendet. Diese Einträge
belegen einen API-Zustand; sie ersetzen die Kontrolle des tatsächlichen
Windows-Pins nicht.

Nach einem positiven Ergebnis ist die neue TaskBar-Verknüpfung separat auf
Anzeigenamen, Ziel-EXE, Arbeitsverzeichnis, Icon, AUMID und Profilargumente
zurückzulesen. Die bisherigen Pins sind dabei zu erhalten. Insbesondere darf
ein während der Prüfung verwendetes Profil nicht versehentlich zum normalen
Startprofil der angehefteten Verknüpfung werden. Eine vorbereitete oder nur
in den TaskBar-Ordner kopierte Datei ist kein erfolgreicher OS-Pin.

Dieser Quellnachtrag wartet beim Erstellen dieses Dokuments noch auf die
native Kompilierung und tatsächliche Laufzeitabnahme. Der aktuelle
[Auslieferungsbericht](validation/branding.md) benennt den jeweils belegten
Stand. Ein SDK- oder API-Check allein wird dort nicht als Pin-Erfolg gewertet.

## Primärquellen

- [Microsoft: Pin your app to the taskbar](https://learn.microsoft.com/en-us/windows/apps/develop/windows-integration/pin-to-taskbar)
- [Microsofts Beispiel für eine unpackaged Desktopanwendung](https://github.com/microsoft/Windows-classic-samples/blob/main/Samples/TaskbarManager/CppUnpackagedDesktopTaskbarPin/MainWindow.xaml.cpp)

Beim Übertragen auf einen neuen Upstreamstand zuerst die Topbar- und
Frame-Lebensdaueranker prüfen, anschließend gegen den tatsächlichen SDK-ABI
kompilieren und die Windows-Voraussetzungen im echten eigenen Prozess
beurteilen. Eine frühere Diagnose aus einem unidentifizierten Hilfsprozess
entscheidet nicht über die Berechtigung der eigenen Anwendung.
