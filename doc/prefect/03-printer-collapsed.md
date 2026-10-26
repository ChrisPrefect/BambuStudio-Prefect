# F03 – Druckerbox standardmäßig eingeklappt

## Verhalten und Prüfstand

`prefect_printer_collapsed=true` legt den **Anfangszustand** der Druckerbox fest.
Beim Aufbau der Sidebar ist der Inhalt eingeklappt, der Titel bleibt sichtbar.
Ein Klick auf den Titel öffnet oder schließt die Box auch bei eingeschalteter
Workflowoption. Der Benutzer muss die Vorgabe dafür nicht abschalten.

Eine spätere Aktualisierung der Oberfläche oder des Druckerprofils behält die
manuelle Entscheidung in derselben Sidebar bei. Der Workflow-Schalter speichert
den Startstandard, nicht den zuletzt angeklickten Zustand. Eine neu aufgebaute
Sidebar beziehungsweise ein neuer Programmstart beginnt erneut mit diesem
Standard. Bei `false` beginnt sie mit dem normalen offenen Inhalt.

Wird der Workflow-Schalter tatsächlich geändert, gilt die neue Vorgabe einmal:
`false → true` klappt die Box ein, `true → false` öffnet sie. Anschließende
Titelklicks bleiben wirksam, bis die Vorgabe wieder geändert oder die Sidebar
neu erzeugt wird.

Druckerauswahl, Filamentsynchronisierung und Netzwerkfunktionen behalten ihre
bisherigen Pfade. Die Änderung betrifft den sichtbaren Container; sie ändert
keine Druckparameter oder Presetwerte.

Der hier beschriebene Stand ist in **`.6`** veröffentlicht: Quelle
`727a703155237a94e4fcc31ebc4effef515d13f0`, Tree
`16cbb874d6bef7ebbc3453e407451eb9af252b0e`.
Der [native Buildlauf 40414286154](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/40414286154)
ist vollständig erfolgreich, einschließlich Windows-Kompilierung, Paketierung
und abschließender Cache-Schritte. Der
[Release 424868721 / `.6`](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/tag/v02.08.02.61-prefect.6)
wurde am **26.10.2026 um 23:22:49 UTC** veröffentlicht
(**27.10.2026, 00:22:49 Europe/Zurich**). Alle drei öffentlichen Dateien wurden
anonym vollständig geladen und nach SHA256 geprüft; beide ZIPs bestehen CRC.
Die 37 Feature-Commits sind durch 74 identische Patch-Zwischenbäume belegt.
[Auslieferungsbericht und Prüfgrenzen](validation/workflow4.md),
[Veröffentlichungsnachweis](validation/published-release-workflow4.json).

Quellgebundene Starts im isolierten Prüfprofil und im normalen Forkprofil sind
separate Laufzeitnachweise. Sie ersetzen keine sichtbare Bedienprüfung dieser
Funktion. Die nachstehenden Klick-, Häkchen-, Refresh- und Neustartfälle bleiben
als manuelle Abnahme offen, soweit sie nicht einzeln ausdrücklich belegt sind.

Die veröffentlichte **`.5`** ist historisch: Dort war die eingeklappte Box bei
aktivierter Option dauerhaft gesperrt. Ihr Prüfbericht belegt das neue
Aufklapp-/Refreshverhalten nicht.

## Quellanker

Basis: Upstream `v02.08.02.61`, Commit
`926a7192574bcb9b3a732e1ec59a46d79cb45466`.

- `src/slic3r/GUI/Plater.cpp`, `Sidebar::Sidebar`: Direkt nach dem Erzeugen von
  `m_panel_printer_content` wird der Workflowwert in
  `m_prefect_printer_collapse_applied` übernommen. Bei `true` setzt
  `SetMaxSize({-1, 0})` den Zustand vor dem ersten Layout.
- Derselbe Konstruktor, `m_panel_printer_title->Bind(wxEVT_LEFT_DOWN, ...)`:
  Der Handler wechselt anhand von `GetMaxHeight()` zwischen Höhe null und
  unbegrenzter Höhe. Er darf nicht wegen `prefect_printer_collapsed` vorzeitig
  zurückkehren.
- `Sidebar::update_ui_from_settings`: Nur wenn der aktuelle Workflowwert vom
  zuletzt angewandten Wert abweicht, wird die Höhenbegrenzung geändert.
  Danach wird der Vergleichswert aktualisiert und die Sidebar neu gelayoutet.
  Ein unveränderter Wert darf den inzwischen manuell geöffneten Inhalt nicht
  wieder schließen.
- `src/slic3r/GUI/Plater.hpp`: `m_prefect_printer_collapse_applied` bezeichnet
  den zuletzt angewandten **Workflowwert**, nicht den momentanen Aufklappzustand.
- `src/libslic3r/PrefectWorkflowPreferences.hpp`, `set_workflow_defaults`:
  Fehlende Werte erhalten `true`; eine gespeicherte Abschaltentscheidung bleibt.
- `src/slic3r/GUI/Preferences.cpp`, `create_prefect_tab`, Checkboxcallback und
  Resetliste: Der eigenständige Schalter löst den vorhandenen UI-Refresh aus.

## Nachtragen bei einem Upstream-Update

1. Nach `m_panel_printer_title`, `m_panel_printer_content`, `SetMaxSize` und
   `Sidebar::update_ui_from_settings` suchen. Bei einem neuen Collapse-Widget
   dessen öffentliche API für Anfangszustand und Benutzerklick verwenden.
2. Die Situationen erster Aufbau, echter Defaultwechsel und gewöhnlicher
   Refresh trennen. Nur die ersten beiden setzen den Zustand.
3. Keine Sperre im Titelhandler und kein bedingungsloses Einklappen bei jedem
   Profil-/UI-Refresh übernehmen. Beide würden die manuelle Wahl wieder aufheben.
4. Den Vergleichswert nach dem Anwenden aktualisieren. Ein Benutzerklick darf
   weder den Workflowwert noch diesen Vergleichswert umschreiben.
5. Default, Settingscallback und Reset zusammen übernehmen. Der Container darf
   Drucker-/Filamentdaten weiterhin aktualisieren, auch wenn sein Inhalt zu ist.

## Konkrete Prüfungen

Die Defaults-/Migrationstests in `tests/prefect/preferences_test.cpp` prüfen
fehlende Schlüssel und erhaltene Abschaltentscheidungen. Sie prüfen keine
wxWidgets-Höhenbegrenzung oder sichtbare Titelbedienung. Die entsprechenden
Policytests liefen im erfolgreichen Quell-CI mit aktiven Assertions. Der native
Windows-Build ist erfolgreich; die folgende sichtbare Bedienabnahme ist damit
noch nicht nachgewiesen.

Die folgende noch offene Abnahme ist am ausgelieferten `.6`-Build in einem
eigenen Prüfprofil durchzuführen:

| Fall | Vorgehen und erwartetes Ergebnis |
| --- | --- |
| Startdefault ein | Mit `true` starten: Inhalt bereits beim ersten Layout zu; Titel sichtbar. |
| Manuell öffnen | Titel anklicken: Inhalt öffnet sich, Workflowoption bleibt `true`. |
| Refresh nach Öffnen | Druckerprofil wechseln, Materialzahl oder DPI/Farbmodus aktualisieren: derselbe Container bleibt offen. |
| Manuell schließen | Titel erneut anklicken und UI aktualisieren: Inhalt bleibt zu. |
| Default ändern | Auf `false` schalten: einmal öffnen; danach manuell schließen und aktualisieren: bleibt zu. Zurück auf `true`: einmal schließen; danach wieder manuell öffnbar. |
| Neuer Start | Nach manuellem Öffnen bei `true` normal beenden und neu starten: wieder anfangs zu. Bei `false` anfangs offen. |
| Funktionsgrenze | Bei eingeklappter Box Drucker-/Filamentinformationen aktualisieren: Datenpfade funktionieren weiter; keine Druckauslösung nötig. |
