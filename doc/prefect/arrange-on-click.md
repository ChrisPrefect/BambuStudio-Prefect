# F12 – Anordnen sofort starten, Optionen weiter anzeigen

`prefect_arrange_on_click=true` startet beim Öffnen des Anordnen-Popups über den Toolbarbutton sofort den vorhandenen Anordnungsjob. Das Optionspopup bleibt offen. Nach Abschluss lassen sich Abstand, Rotation und weitere vorhandene Optionen ändern und über die Anordnen-Taste erneut anwenden. Ein weiterer Toolbar-Klick zum Schließen startet keinen zweiten Job.

Der eigene Schalter steht unter **Einstellungen → Workflow**. Bei `false` öffnet der Toolbarbutton wie im Upstream nur die Optionen. Die vorhandenen Optionen F10 (Rotation erzwingen) und F11 (Mehrfachimporte automatisch anordnen) bleiben unabhängig schaltbar. Der bestehende Tastaturbefehl und die Auswahl-/Plattenlogik werden weiterverwendet.

## Quellanker und Updateanleitung

- `GLCanvas3D.cpp`: Arrange-Toolbar `left.action_callback`, Aktivierungsbedingung und Arrange-Popuprenderer. Nur der Übergang zum offenen Popup darf den zusätzlichen Lauf auslösen.
- `PrefectArrangePolicy.hpp`: getrennte Entscheidung für Öffnen, Job-Verfügbarkeit und Einstellung.
- `PrefectWorkflowPreferences.hpp`: nur fehlende Schlüssel ergänzen; explizites `false` erhalten.
- `Preferences.cpp`: Workflow-Schalter und Resetliste.

Beim Upstream-Update sowohl den Eingabehandler als auch die Toolbar-Zustandsmaschine prüfen. Eine alleinige Einfügung von `arrange()` im Handler reicht nicht: Wird die Toolbar bei einem laufenden UI-Job deaktiviert, kann sie das Popup sofort wieder schließen. Das bereits offene Arrange-Popup bleibt während des Jobs sichtbar, seine veränderlichen Optionen und die zweite Starttaste sind bis zum Jobende gesperrt. Andere Werkzeuge und ihre Busy-Prüfungen behalten ihren Zustand.

Die bestehende `Plater::arrange()`-Implementierung bleibt für Undo, Worker, Abbruch und ausstehende Importanordnung maßgeblich. Keine parallelen Anordnungsjobs einführen. Der Job darf seine Parameter nicht aus währenddessen veränderlichen Popupfeldern nachlesen.

## Abnahme

Mit mindestens zwei Objekten einmal auf Anordnen klicken: genau ein Lauf beginnt und das Popup bleibt sichtbar. Währenddessen sind seine Parameter/Starttaste gesperrt. Danach Abstand ändern und im Popup erneut anordnen: genau ein zweiter Lauf mit neuen Parametern. Popup schließen: kein zusätzlicher Lauf. F12 ausschalten und nach Neustart prüfen: erster Klick öffnet nur die Optionen. F10/F11 jeweils separat ein-/ausschalten und einen belegten UI-Worker berücksichtigen. Die Policytests decken die Zustandsentscheidungen ab; sichtbare Popupbedienung benötigt eine eigene GUI-Prüfung.
