# Alle Workflow-Anpassungen einzeln schalten

Unter **Einstellungen → Workflow** stehen die dreizehn Anpassungen gemeinsam auf
einer scrollbaren Seite. Jeder Schalter speichert einen eigenen Wert im
Anwendungsprofil. Es ist kein Zurücksetzen des Profils nötig, um eine Funktion
abzuschalten. Eine gespeicherte eigene Feldauswahl bleibt beim Ausschalten erhalten.

| Funktion | Konfigurationsschlüssel | Standard |
| --- | --- | --- |
| Druckerfilamente automatisch synchronisieren | `prefect_auto_sync_filaments` | an |
| Eigene Felder in der einfachen Ansicht | `prefect_simple_fields_enabled` | aus; zunächst Upstream-Standardfelder |
| Obere Drucker-Box eingeklappt halten | `prefect_printer_collapsed` | an |
| Automatisch im Hintergrund slicen | `background_processing` | an |
| Angeklicktes Filament zuweisen | `prefect_click_filament_assigns_selection` | an |
| Supportinterface-Eintrag im Filamentmenü | `prefect_support_interface_menu` | an |
| Mehrere Modelle einzeln importieren | `prefect_import_separate_objects` | an |
| TPU-Cold-Pull-Erinnerung ausblenden | `prefect_suppress_tpu_cold_pull` | an |
| Tipps ausblenden | `prefect_hide_tips` | an |
| Automatische Rotation beim Anordnen | `prefect_arrange_rotation` | an |
| Mehrere eingefügte Objekte automatisch anordnen | `prefect_arrange_after_import` | an |
| Beim ersten Klick sofort anordnen und Optionen anzeigen | `prefect_arrange_on_click` | an |
| Helio-Additive-Werbung ausblenden | `prefect_hide_helio_ads` | an |

Die Feldauswahl lässt sich auch direkt von dieser Seite öffnen. Beim erstmaligen
Aktivieren ohne gespeicherte Liste wird die aktuelle einfache Standardansicht
als Ausgangspunkt verwendet. Eine bewusst gespeicherte leere Auswahl bleibt leer.
Der bisherige Zugang **Felder...** neben dem Ansichtsmodus bleibt erhalten.

Der Schalter für das Supportinterface steuert den zusätzlichen Menüeintrag,
nicht den Druckparameter selbst. Bereits zugewiesene Supportmaterialien werden
durch das Abschalten nicht verändert. Materialklick und Supportinterface-Menü
werden auch im jeweiligen Handler geprüft; ein zuvor geöffnetes Menü darf eine
inzwischen deaktivierte Funktion nicht mehr ausführen.

Die Rotation wird bei aktivierter Option für manuelles und automatisches Anordnen
eingeschaltet. Nach dem Abschalten gelten wieder die gespeicherten normalen
Anordnungseinstellungen. Die automatische Anordnung ist davon unabhängig schaltbar.

F12 startet beim Öffnen des Anordnungs-Popups sofort den vorhandenen Job;
das Popup bleibt zur Kontrolle der Optionen offen. Ein schließender Klick
oder ein bereits beschäftigter Worker startet keinen zweiten Auftrag.
Die Optionen sind während der Arbeit gesperrt. F13 steuert Helio-Werbung
unabhängig von F09; echte Analyseergebnisse und Fehler bleiben erhalten.

## Aktueller Auslieferungs- und Prüfstand

Die dreizehn Schalter gehören zur veröffentlichten Vorabversion `.5`, Quelle
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

Bei Updates alle dreizehn Schalter auf Sichtbarkeit, Speicherung nach Neustart und
unabhängiges Ein-/Ausschalten prüfen. Für F02 zusätzlich fehlende, leere und mit
unbekannten Schlüsseln versehene Listen testen. Bestehende explizite `false`-Werte
dürfen durch neue Standardwerte oder die Migration nicht wieder aktiviert werden.
