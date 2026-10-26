# Alle Workflow-Anpassungen einzeln schalten

Unter **Einstellungen → Workflow** stehen die sechzehn Anpassungen gemeinsam auf
einer scrollbaren Seite. Jeder Schalter speichert einen eigenen Wert im
Anwendungsprofil. Es ist kein Zurücksetzen des Profils nötig, um eine Funktion
abzuschalten. Eine gespeicherte eigene Feldauswahl bleibt beim Ausschalten erhalten.

| Funktion | Konfigurationsschlüssel | Standard |
| --- | --- | --- |
| Druckerfilamente automatisch synchronisieren | `prefect_auto_sync_filaments` | an |
| Eigene Felder in der einfachen Ansicht | `prefect_simple_fields_enabled` | aus; zunächst Upstream-Standardfelder |
| Drucker-Box beim Start einklappen, danach manuell bedienbar | `prefect_printer_collapsed` | an |
| Automatisch im Hintergrund slicen | `background_processing` | an |
| Angeklicktes Filament zuweisen | `prefect_click_filament_assigns_selection` | an |
| Supportinterface-Eintrag im Filamentmenü | `prefect_support_interface_menu` | an |
| Mehrere Modelle einzeln importieren | `prefect_import_separate_objects` | an |
| TPU-Cold-Pull-Erinnerung ausblenden | `prefect_suppress_tpu_cold_pull` | an |
| Tipps ausblenden | `prefect_hide_tips` | an |
| Initialer editierbarer Rotationsstandard beim Anordnen | `prefect_arrange_rotation` | an |
| Mehrere eingefügte Objekte automatisch anordnen | `prefect_arrange_after_import` | an |
| Mit jedem direkten Anordnen-Iconklick starten und Optionen offen halten | `prefect_arrange_on_click` | an |
| Helio-Additive-Werbung ausblenden | `prefect_hide_helio_ads` | an |
| Aktuelle Platte ohne Rückfrage leeren | `prefect_quick_delete_plate` | an |
| Einfache Ansicht als eine Liste | `prefect_simple_single_list` | an, unabhängig von eigener Feldauswahl |
| Manuelle Sync-Erfolgseinblendung kurz zeigen | `prefect_short_sync_notice` | an, 1000-ms-Timerfrist |

Die Feldauswahl lässt sich auch direkt von dieser Seite öffnen. Beim erstmaligen
Aktivieren ohne gespeicherte Liste wird die aktuelle einfache Standardansicht
als Ausgangspunkt verwendet. Eine bewusst gespeicherte leere Auswahl bleibt leer.
Der bisherige Zugang **Felder...** neben dem Ansichtsmodus bleibt erhalten.

Der Schalter für das Supportinterface steuert den zusätzlichen Menüeintrag,
nicht den Druckparameter selbst. Bereits zugewiesene Supportmaterialien werden
durch das Abschalten nicht verändert. Materialklick und Supportinterface-Menü
werden auch im jeweiligen Handler geprüft; ein zuvor geöffnetes Menü darf eine
inzwischen deaktivierte Funktion nicht mehr ausführen.

Rotation ist ein Anfangswert; die Checkbox im Anordnungs-Popup bleibt bedienbar.
Gespeicherte Entscheidungen je FFF-, sequenziellem FFF- und SLA-Modus gewinnen
danach. Die frühere effektive F10-Erzwingung wird einmal über
`prefect_arrange_rotation_default_revision` übertragen; sie wird nicht bei
jedem Lauf erneut angewendet. Die automatische Anordnung bleibt unabhängig.

F12 startet mit jedem direkten linken Klick auf das Anordnen-Icon den vorhandenen
Job, sofern kein UI-Job läuft; das Popup bleibt offen. Interner Toolwechsel
und programmatisches Schließen starten keinen Auftrag. Hintergrundslicing
blockiert den manuellen Auftrag nicht still, sondern wird vom vorhandenen
Jobstart angehalten. Der bestehende Anordnen-Button im Popup bleibt erhalten.
Die Optionen sind während der Arbeit gesperrt. F13 steuert Helio-Werbung
unabhängig von F09; echte Analyseergebnisse und Fehler bleiben erhalten.

## Aktueller Auslieferungs- und Prüfstand

Die neuen/separat überarbeiteten sechzehn Funktionen sind für `.6` dokumentiert.
Der neue Sourcecommit, vollständige native Build, GUI-Abnahme und Veröffentlichung
sind noch nachzuweisen. [Änderungsinventar](changes.json),
[neue Details F14](14-quick-plate-delete.md), [F15](15-single-simple-list.md),
[F16](16-sync-success-timeout.md). F15 zeigt ohne F02 die normalen einfachen
Upstream-Felder und mit F02 dessen gespeicherte Liste; Scope-Limits bleiben.
Eine leere gespeicherte Liste wird über echte Schlüsselpräsenz erkannt.

**Historisch:** Die dreizehn früheren Schalter gehören zur veröffentlichten `.5`, Quelle
`939e0b3ce6dce937502666f334950eec2e0f542a`. Der vollständige Windows-Build,
acht Policytests, V6-Installation und 35/70-Patchreplay sind geprüft.
Ein eigener isolierter V6-GUI-Start bestätigt, dass fehlende F12-/F13-Schlüssel
mit `true` ergänzt werden; ein bereits gespeichertes `false` bleibt nach
den Migrationstests erhalten. F11 war nur im QA-Profil ausgeschaltet.
Die konkrete Checkboxdarstellung/-bedienung und der F12-Toolbar-Erstklick
sind wegen der dokumentierten Capture-/Elementcachefehler noch nicht visuell
abgenommen. Die vorhandene Benutzersitzung bleibt offen; die installierte
Version wird beim nächsten normalen Start wirksam.
[Prüfbericht und genaue Grenzen](validation/workflow3.md).

## Profilmigration und Upstream-Updates

`AppConfig::set_defaults()` ergänzt nur fehlende Werte. Revision 2 behält
gespeicherte Entscheidungen einschließlich `background_processing=false` bei.
Die neue Revision verlangt keine Kopie oder Änderung des normalen Studio-Profils.

Stabile Einstiegspunkte für Updates sind `PreferencesDialog::create_prefect_tab`,
`set_workflow_defaults` und `migrate_workflow_preferences` in
`PrefectWorkflowPreferences.hpp`, deren Aufrufe aus `AppConfig.cpp` sowie der
Reset-Dialog in `Preferences.cpp`. Die Feldliste wird über
`TabPrint::initialize_simple_fields` initialisiert und in
`TabPrint::configure_simple_fields` bearbeitet.
Die englischen `_L`-Texte stehen samt deutschen Übersetzungen in
`scripts/prefect/translations-de.json`; das Katalogskript erzeugt PO/MO reproduzierbar.

Bei Updates alle sechzehn Schalter auf Sichtbarkeit, Speicherung nach Neustart und
unabhängiges Ein-/Ausschalten prüfen. Für F02 zusätzlich fehlende, leere und mit
unbekannten Schlüsseln versehene Listen testen. Bestehende explizite `false`-Werte
dürfen durch neue Standardwerte oder die Migration nicht wieder aktiviert werden.
