# Bambu Studio – Prefect-Workflow-Fork

Dieser Fork bündelt die neun konkret gewünschten Anpassungen am Arbeitsablauf.
Der Änderungsstand wird auf dem Branch `prefect/workflow` im eigenen
[GitHub-Fork](https://github.com/ChrisPrefect/BambuStudio-Prefect) gepflegt.
Die gemeinsame Grundlage ist Bambu Studio **v02.08.02.61**, Commit
`926a7192574bcb9b3a732e1ec59a46d79cb45466`. Das Git-Remote `upstream` zeigt auf
`https://github.com/bambulab/BambuStudio.git`.

**Auslieferungsstand:** Der vollständige Windows-Build `4b5c3546` ist einschließlich
Linken, Paketierung und CI-Tests erfolgreich. Das finale Paket wurde außerdem
als vollständige eigene Windows-Installation mit allen 6.755 Dateien geprüft
und tatsächlich gestartet; eine Desktop-Verknüpfung verwendet das isolierte
Fork-Profil. Ressourcenlinks zur normalen Installation werden nicht benötigt.
Der Stand enthält auch das Nachholen des aktuellen Materialstands beim erneuten
Aktivieren von F01. Die interaktive Abnahme aller Bedien- und Druckerfälle ist
nicht vollständig belegt. [Lokaler Laufzeitnachweis und genaue Grenzen](validation/local-windows-runtime.md),
[aktueller CI-Nachweis](validation/cloud-build-4b5c.md).
Der GitHub-Fork ist angelegt; dessen Remote heißt `origin`.
Der jeweils aktuelle Nachweis, einschließlich tatsächlich ausgeführter Tests,
steht in [VALIDATION.md](VALIDATION.md).

## Anpassungsliste

| ID | Anpassung und Bedienung | Schalter / Standard | Detaildokumentation |
| --- | --- | --- | --- |
| F01 | Änderungen der Filamente am ausgewählten Drucker automatisch ins Projekt übernehmen, ohne Sync-Assistenten oder Abschluss-OK | `prefect_auto_sync_filaments=true` | [Automatischer Filamentabgleich](01-filament-auto-sync.md) |
| F02 | Über **Felder...** neben dem Modusschalter selbst festlegen, welche Druckeinstellungen in der einfachen Ansicht erscheinen | `prefect_simple_fields_enabled=false`; eigene Liste erst nach Auswahl aktiv | [Eigene einfache Ansicht](simple-fields.md) |
| F03 | Die obere Drucker-Box dauerhaft eingeklappt halten; Kopfzeile bleibt sichtbar | `prefect_printer_collapsed=true` | [Drucker-Box](03-printer-collapsed.md) |
| F04 | Nach Änderungen die aktuelle Platte mit dem vorhandenen Worker automatisch im Hintergrund slicen | `background_processing=true` | [Hintergrundslicing](04-background-slicing.md) |
| F05 | Markierten Objekten/Teilen durch Klick auf Farbfeld oder Filamentnamen das betreffende Filament zuweisen | `prefect_click_filament_assigns_selection=true` | [Filamentklick](05-click-filament-assignment.md) |
| F06 | Im Filament-`...`-Menü **Als Supportinterface festlegen** anbieten; setzt das globale Supportinterface-Material | Zusätzlicher Menüeintrag; verwendet bestehenden `support_interface_filament`-Key | [Supportinterface-Menü](06-support-interface-menu.md) |
| F07 | Gemeinsam importierte Modelldateien ohne Zusammenfassungsfrage als einzelne Objekte laden | `prefect_import_separate_objects=true` | [Getrennte Importe](07-separate-imports.md) |
| F08 | Ausschließlich die wiederkehrende TPU-Cold-Pull-Empfehlung ausblenden | `prefect_suppress_tpu_cold_pull=true` | [TPU-Erinnerung](08-tpu-cold-pull.md) |
| F09 | Tippsfenster und Tippsbereich der Slicing-Meldung vollständig ausblenden, einschließlich des reservierten Platzes | `prefect_hide_tips=true` | [Tipps abschalten](09-hide-tips.md) |

Die schaltbaren Funktionen stehen im neuen Register **Workflow** der
Anwendungseinstellungen. F02 besitzt einen eigenen Dialog und einen eigenen
Reset auf die aktuellen Upstream-Standardfelder. F06 ergänzt ein vorhandenes
Menü und benötigt keinen zusätzlichen Druckparameter.

Die Änderungen ersetzen gezielt die genannten wiederkehrenden Rückfragen. Es
wird kein allgemeiner Mechanismus eingeführt, der beliebige unbekannte Dialoge
automatisch mit „Ja“ beantwortet. Bestehende Druckergrenzen, Validierungen und
die Entscheidung über externe Nachbearbeitungsskripte behalten ihre Bedeutung.

## Verhalten, das beim Benutzen wichtig ist

- **Drucker als Materialquelle:** F01 übernimmt Typ, Farbe und passende Profile
  aus dem ausgewählten Gerät. Ungespeicherte Änderungen am gerade editierten
  Filamentprofil können dabei verworfen werden. Die vorhandenen numerischen
  Objektzuweisungen bleiben maßgeblich. Die konkrete Übernahme und Sonderfälle
  sind im F01-Dokument beschrieben.
- **Aktuelle Platte:** F04 startet nach etwa 500 ms ohne weitere Änderungen.
  F01 bündelt Druckermeldungen über etwa 750 ms und wartet bei einem laufenden
  Slicing-/UI-Job. Diese Zeitfenster sind keine harte Laufzeitgarantie.
- **Farben und Profile weiterhin bearbeiten:** Mit Shift-Klick auf das Farbfeld
  wird der Farbwähler geöffnet. Dropdown-Pfeil beziehungsweise Shift-Klick auf
  den Namen lassen die Profilauswahl erreichbar. Ohne Objektauswahl bleibt die
  bisherige Bedienung bestehen.
- **Supportinterface:** F06 ändert nur die globale Interface-Zuweisung.
  Support-Erzeugung, Support-Basismaterial und bestehende lokale Overrides
  werden nicht zusätzlich verändert.
- **Projektstruktur:** F07 beantwortet die beiden heuristischen
  Zusammenfassungsfragen mit „Nein“. Gespeicherte 3MF-Strukturen und bewusst
  hinzugefügte Teile werden nicht pauschal zerlegt.
- **Weiterer bestehender Hinweis:** Der einmalige Dialog **Tipps** für einen
  bereiten Filamentswitcher verwendet den vorhandenen Anwendungsschlüssel
  `show_fila_switch_tips=false`. Im geprüften Fork-Profil ist er ausgeschaltet;
  nach Neustart erschien der Dialog nicht mehr. Der Hinweis ist unabhängig
  von F09/DailyTips. Eine Warnung zu einem nicht kalibrierten Switcher besitzt
  einen separaten Pfad und bleibt davon unberührt.

## Eigenes Profil statt Änderungen an der normalen Installation

Auf dem geprüften Windows-System ist die vollständige eigene Anwendung unter
`%USERPROFILE%\BambuStudio-Prefect-Windows` installiert. Die Desktop-Verknüpfung
**BambuStudio Prefect** startet deren `bambu-studio.exe` mit
`--datadir "%APPDATA%\BambuStudio-Prefect"`. ZIP-Hash, sämtliche Datei-Hashes,
exakte Paketstruktur und fehlende Ressourcen-/Dateilinks sind im
[lokalen Installationsnachweis](validation/local-windows-runtime.md) festgehalten.

[Start-Prefect.ps1](../../scripts/prefect/Start-Prefect.ps1) ist der Einstieg für
eine gebaute Fork-Version. Er startet die angegebene `bambu-studio.exe` mit
`--datadir` und einem eigenen Profilverzeichnis. Standardmäßig ist das:

```text
%APPDATA%\BambuStudio-Prefect
```

Die normalen Bambu-Studio-Daten unter `%APPDATA%\BambuStudio` bleiben erhalten.
Das Skript verweigert dieses normale Verzeichnis ausdrücklich als Fork-Profil.
Es ersetzt keine installierte EXE und kompiliert selbst kein Programm.

Beispiel nach einem erfolgreichen Build, aus dem Repository-Stamm:

```powershell
.\scripts\prefect\Start-Prefect.ps1 -ExecutablePath 'C:\Pfad\zum\Fork\bambu-studio.exe'
```

Für einen erstmaligen lokalen Import der vorhandenen Konfiguration und Profile:

```powershell
.\scripts\prefect\Start-Prefect.ps1 -ExecutablePath 'C:\Pfad\zum\Fork\bambu-studio.exe' -ImportStockProfile
```

`-ImportStockProfile` funktioniert nur, solange das neue Profilverzeichnis noch
nicht existiert. Kopiert werden `BambuStudio.conf` sowie die Ordner `user` und
`system`, soweit vorhanden. Bereits vorhandene Fork-Profile werden nicht
überschrieben. Ein anderes Ziel lässt sich mit `-ProfileDirectory` angeben.
Diese persönlichen Laufzeitdaten gehören nicht in Git, Patches oder CI-Artefakte.
Das optionale Bambu-Netzwerkplugin und eine Geräteverbindung bleiben für die
Kommunikation mit dem Drucker erforderlich.

## Standardwerte und einmalige Migration

`AppConfig::set_defaults()` ergänzt fehlende Fork-Schalter. Die sechs
`prefect_*`-Booleans aus F01/F03/F05/F07/F08/F09 sind standardmäßig `true`.
Hintergrundslicing ist ebenfalls standardmäßig aktiv. Die eigene einfache
Feldauswahl bleibt zunächst deaktiviert; ein fehlender `prefect_simple_fields`-
Wert entspricht einer leeren Liste.

`AppConfig::load()` prüft zusätzlich den **eingelesenen JSON-Inhalt** auf
`app.prefect_workflow_revision`. Fehlt der Schlüssel, wird beim ersten Laden
`background_processing=true` und `prefect_workflow_revision="1"` gesetzt und
die Konfiguration als geändert markiert. Dadurch wird auch ein kopiertes
Stock-Profil mit explizitem `background_processing=false` einmalig aktiviert.
Danach bleibt eine vom Benutzer getroffene Entscheidung zum Abschalten erhalten.
Die Revision wird nicht anhand bereits im Konstruktor gesetzter Standardwerte
erkannt, da diese sonst die Migration verdecken würden.

Die vorhandene Funktion **Einstellungen zurücksetzen** entfernt auch die neuen
Funktionsschalter und die eigene Feldauswahl und setzt die Fork-Standardwerte
erneut. Die Migrationsrevision bleibt erhalten. Ein bloßes Ausschalten einzelner
Funktionen erfordert dagegen keinen Profilreset.

## Änderungen prüfen und weiterpflegen

Die maschinenlesbare Bestandsliste steht in [changes.json](changes.json).
Die abgeschlossene Feature-Commitserie ist in [COMMITS.md](COMMITS.md) zugeordnet.
`scripts/prefect/check_manifest.py` prüft die neun IDs, die Detaildokumente und
die eingetragenen Quellcodeanker. Der Workflow
[prefect-workflow.yml](../../.github/workflows/prefect-workflow.yml) kompiliert
die unabhängigen C++-Policytests und beschreibt anschließend einen vollständigen
Windows-Build samt portablem Paket. Ob dieser Build tatsächlich ausgeführt
wurde und erfolgreich war, muss anhand seines Laufs geprüft werden.

Die vier unabhängigen Tests unter `tests/prefect/*_test.cpp` prüfen:

- F01: Stoppen, Warten und Synchronisieren bei Geräte-/Jobzuständen;
- F02: Feldlisten, Normalisierung, gemeinsame Zeilen und Modusgrenzen;
- F04: Timer-/Workerentscheidungen, Plattenwechsel und Skriptwahl;
- F08: exakte Unterdrückung der Cold-Pull-Warnung mit unverändertem Verhalten
  bei anderen Meldungen und Schweregraden.

Sie prüfen keinen vollständigen wxWidgets-Build, kein tatsächliches Slicing und
keine Druckerverbindung. Die dafür erforderlichen Abnahmeszenarien stehen je
Feature im Detaildokument. Die Umsetzung enthält keine automatische
Druckauslösung.

Für ein Update sind die getrennten Feature-Commits und ein Format-Patch-Export
vorgesehen. Der vollständige Ablauf einschließlich Konfliktlösung,
Konfigurationsmigration, Übersetzung und Abnahme steht in
[UPSTREAM-UPDATES.md](UPSTREAM-UPDATES.md). Entscheidend sind Funktionen und
Optionsschlüssel, nicht unverlässliche Zeilennummern.
