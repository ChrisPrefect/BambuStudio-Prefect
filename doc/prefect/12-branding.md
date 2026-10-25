# 12 – Eindeutiger Programmname und Windows-Taskleistengruppe

## Gewünschtes Verhalten

Der sichtbare Name dieses Forks lautet **Prefect Bambu Studio**. Damit steht „Prefect“ in Fensterlisten und Taskleisten-Vorschauen vorn. Der Projektname bleibt hinter dem Programmnamen erhalten, einschließlich des Sterns für ungespeicherte Änderungen. Die sichtbare Windows-Topbar verwendet denselben Text wie der native Fenstertitel; ihre vorhandene Kürzung langer Titel bleibt aktiv.

| Zustand | Nativer Fenster-/Taskleisten-Titel |
| --- | --- |
| Leeres, unverändertes Projekt | `Prefect Bambu Studio` |
| Unbenanntes Projekt mit Änderungen | `Prefect Bambu Studio - *` |
| Projekt `Gehäuse` unverändert | `Prefect Bambu Studio - Gehäuse` |
| Projekt `Gehäuse` geändert | `Prefect Bambu Studio - * Gehäuse` |
| Separater G-code-Viewer, falls dieser Modus verwendet wird | `Prefect Bambu Studio G-code Viewer - <Dateiname>` |

Bereits der Konstruktor setzt den neuen Namen, bevor ein Projekt geladen ist. Der Titelcache speichert den vollständigen zusammengesetzten Text. Deshalb erhält auch ein zunächst leerer Projektname beim ersten Update den vollständigen Topbar-Titel. Über-/Copyright-Fenster, Splash-Anzeigen und die vom gemeinsamen Anzeigenamen abgeleiteten Dialogtitel verwenden ebenfalls den neuen Namen. Der vorhandene Einstellungsdialog und der Rückfragedialog für laufende Uploads verwenden nun ausdrücklich diesen Anzeigenamen.

Das Branding ist eine feste Identität dieser Anwendung und kein weiterer Workflow-Schalter. Die elf bestehenden Workflow-Optionen bleiben unabhängig davon erhalten.

## Geänderte Quellstellen

| Datei / Anker | Änderung |
| --- | --- |
| `src/libslic3r/libslic3r.h`, `SLIC3R_APP_FULL_NAME` | Neuer reiner Anzeigename `Prefect Bambu Studio`; zusätzlicher UI-Name `GCODEVIEWER_APP_FULL_NAME`. |
| `src/slic3r/GUI/MainFrame.cpp`, `MainFrame::MainFrame()` und `MainFrame::update_title()` | Initialer Name und zentrales Zusammenbauen des Titels mit „Prefect“ am Anfang, Projektname und Änderungsstern. Der native Titel und die Windows-Topbar werden gemeinsam aktualisiert. |
| Dieselbe Datei, `SettingsDialog::SettingsDialog()` und macOS-Dock-Tooltip | Den Anzeigenamen statt des technischen Namens verwenden. |
| `src/slic3r/GUI/GUI_App.cpp`, `GUI_App::GUI_App()` | Windows-Prozess früh mit `SetCurrentProcessExplicitAppUserModelID(L"ChrisPrefect.BambuStudio")` kennzeichnen, bevor die App-Konfiguration Dialoge erzeugen kann. Ein Fehler wird nach der vorhandenen Log-Initialisierung protokolliert und beendet die Anwendung nicht. |
| Dieselbe Datei, `GUI_App::init_app_config()` | `SetAppDisplayName(...)` getrennt vom unveränderten `SetAppName(SLIC3R_APP_KEY)` setzen. Splash- und Upload-Dialoge nutzen den UI-Namen. |
| `src/slic3r/GUI/AboutDialog.cpp` und `src/slic3r/GUI/Plater.cpp`, `GCODEVIEWER_APP_FULL_NAME` | Auch UI-Titel im G-code-Viewer erhalten den Fork-Namen. |
| `src/platform/msw/BambuStudio.rc.in` | Windows-Dateibeschreibung und `ProductName` auf `Prefect Bambu Studio` setzen. |
| `src/platform/msw/BambuStudio-gcodeviewer.rc.in` | Entsprechende sichtbare Metadaten der optionalen Viewer-Ressource setzen. |

`SLIC3R_APP_NAME`, `SLIC3R_APP_KEY`, `GCODEVIEWER_APP_NAME` und `GCODEVIEWER_APP_KEY` bleiben unverändert. Sie werden unter anderem in Netzwerkheadern, User-Agent, Konfigurations-/G-code-Kopfzeilen, Übersetzungskatalogen und Profilpfaden verwendet. Das Umbenennen dieser technischen Bezeichner wäre für eine erkennbare Anwendung nicht erforderlich und würde andere Schnittstellen berühren. Dateinamen von EXE/DLL, `InternalName`, `OriginalFilename`, Dateiformat-/URL-Registrierung, die vorhandene Instanzprüfung und sämtliche Drucker- oder Kontoeinstellungen bleiben unverändert.

Die RC-Dateien enthalten den Anzeigenamen absichtlich direkt: Der vorhandene `@SLIC3R_APP_NAME@`-Wert ist ein technischer Name. Diese kleine Änderung benötigt keine neuen CMake-Variablen oder Änderungen am Abhängigkeitscache. `GUI_App.cpp` bindet den benötigten Shell-Header schon ein und verwendet bereits Shell32-Funktionen.

## Taskleiste und Verknüpfung

Die eigene AppUserModelID lautet **`ChrisPrefect.BambuStudio`**. Sie grenzt die Windows-Taskleistengruppe gegenüber der Upstream-Anwendung ab und bleibt über Fork-Updates stabil. Die für Startmenü/Taskleiste erstellte `.lnk` muss dieselbe Eigenschaft **`System.AppUserModel.ID`** tragen. Ihr sichtbarer Name ist `Prefect Bambu Studio`; Ziel, Arbeitsverzeichnis, Argumente und Icon müssen auf die tatsächlich installierte Fork-Version zeigen. Die bestehende `--datadir`-Angabe bleibt dabei erhalten.

Microsoft verlangt die Prozesskennung früh vor dem Erzeugen von UI und denselben Wert auf der zugehörigen Verknüpfung: [SetCurrentProcessExplicitAppUserModelID](https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nf-shobjidl_core-setcurrentprocessexplicitappusermodelid), [Application User Model IDs](https://learn.microsoft.com/en-us/windows/win32/shell/appids). Die Kennung selbst heftet keine Anwendung an; das tatsächliche Anheften und die Prüfung des installierten Pakets werden im Auslieferungsnachweis getrennt dokumentiert.

## Nachtragen bei einem Upstream-Update

1. Zuerst nach `SLIC3R_APP_FULL_NAME`, `SetAppName`, `MainFrame::update_title`, `set_project_name`, `FileDescription`, `ProductName` und bestehenden AppUserModelID-Aufrufen suchen. Den technischen und den sichtbaren Namen weiterhin getrennt behandeln.
2. Den reinen Anzeigenamen sowie den zusätzlichen Viewer-Anzeigenamen übernehmen. Nur UI-Verwendungen des bisherigen Viewer-Namens umstellen; seine Konfigurationskopfzeile bleibt erhalten.
3. Die zentrale Titelbildung anpassen. Falls Upstream die Titelbildung aus `MainFrame::update_title()` verlagert, alle tatsächlichen Fenster-/Topbar-Pfade zusammenführen und den vollständigen Titel cachen. Leerer Projektname, Änderungen und Viewer-Modus sind eigene Prüffälle.
4. Den vorhandenen `SetAppName` unverändert lassen und `SetAppDisplayName` ergänzen. Die Windows-Prozesskennung muss vor der ersten UI gesetzt werden. Falls Upstream inzwischen eine eigene Kennung setzt, diese für den Fork gezielt ersetzen, damit sie später nicht überschrieben wird.
5. Die sichtbaren Windows-Ressourcen aktualisieren. Eingebettetes Icon und Startmenü-/Taskleisten-Verknüpfung gehören zur separaten Icon-/Installationsänderung; ihre AppUserModelID muss exakt mit dem Prozess übereinstimmen.
6. Den nativen Windows-Build kompilieren/linken, anschließend EXE-Dateibeschreibung, leeres Fenster, benanntes und geändertes Projekt sowie Taskleisten-Gruppe und Start über die angeheftete Verknüpfung am installierten Paket prüfen. Ein Neustart darf das Profil nicht wechseln oder eine zweite Fork-Taskleistengruppe erzeugen.

## Prüfstand dieses Quellnachtrags

Der Nachtrag vom 25.10.2026 wurde lokal im Source-Diff geprüft. `git diff --check` und die bestehende Manifestprüfung sind die lokalen Integritätsprüfungen; sie belegen keine native Windows-Kompilierung und kein erfolgreiches Anheften. Der gebündelte CI-Build und die tatsächliche lokale Installations-/Taskleistenabnahme folgen durch den Auslieferungslauf. Hier wird dafür kein vorweggenommener Erfolg behauptet.
