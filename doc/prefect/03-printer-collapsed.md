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

Diese Semantik gehört zum vorbereiteten Nachtrag für **`.6`**. Ein vollständiger
neuer Build, eine GUI-Abnahme und die Veröffentlichung dieses Nachtrags sind
noch ausstehend. Die veröffentlichte **`.5`** ist historisch: Dort war die
eingeklappte Box bei aktivierter Option dauerhaft gesperrt. Ihr Prüfbericht
belegt das hier beschriebene neue Verhalten nicht.

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
wxWidgets-Höhenbegrenzung oder sichtbare Titelbedienung. Für diese Änderung wird
hier kein bereits erfolgreicher neuer Build oder GUI-Lauf behauptet.

Die folgende Abnahme erfolgt am neuen vollständigen GUI-Build in einem eigenen
Prüfprofil:

| Fall | Vorgehen und erwartetes Ergebnis |
| --- | --- |
| Startdefault ein | Mit `true` starten: Inhalt bereits beim ersten Layout zu; Titel sichtbar. |
| Manuell öffnen | Titel anklicken: Inhalt öffnet sich, Workflowoption bleibt `true`. |
| Refresh nach Öffnen | Druckerprofil wechseln, Materialzahl oder DPI/Farbmodus aktualisieren: derselbe Container bleibt offen. |
| Manuell schließen | Titel erneut anklicken und UI aktualisieren: Inhalt bleibt zu. |
| Default ändern | Auf `false` schalten: einmal öffnen; danach manuell schließen und aktualisieren: bleibt zu. Zurück auf `true`: einmal schließen; danach wieder manuell öffnbar. |
| Neuer Start | Nach manuellem Öffnen bei `true` normal beenden und neu starten: wieder anfangs zu. Bei `false` anfangs offen. |
| Funktionsgrenze | Bei eingeklappter Box Drucker-/Filamentinformationen aktualisieren: Datenpfade funktionieren weiter; keine Druckauslösung nötig. |
