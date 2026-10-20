# F08 – TPU-Cold-Pull-Hinweis gezielt ausblenden

## Verhalten und Konfiguration

`prefect_suppress_tpu_cold_pull=true` entfernt genau den Hinweis „Please cold pull before printing TPU to avoid clogging. You may use cold pull maintenance on the printer.“ aus den Materialprüfergebnissen. Der Schalter steht unter Einstellungen → Workflow. Bei `false` verhält sich die Prüfung wie Upstream.

Die Filterung erfolgt anhand des englischen Nachrichtenschlüssels und `action == "warning"`, vor der Übersetzung. Die Sprache hat keinen Einfluss. Alle anderen TPU-/AMS-/Düsenmeldungen durchlaufen die unveränderte Prüfung. Wird dieselbe Meldung künftig als Verbot eingestuft oder ändert sich ihr Text, zeigt die neue Upstream-Version sie wieder; die Wartung muss dann bewusst entscheiden, ob sie weiterhin gefiltert werden soll.

## Dateien und Suchanker

- `src/libslic3r/PrefectWorkflow.hpp`: `suppress_tpu_cold_pull` ist die kleine, unabhängig testbare Entscheidung.
- `src/slic3r/GUI/DeviceCore/DevFilaBlackList.cpp`: `PrefectWorkflow::suppress_tpu_cold_pull` filtert den passenden Eintrag, bevor er in `result.action_items` gelangt.
- `resources/printers/filaments_blacklist.json`: unveränderte Upstream-Quelldaten, anhand derer der Text abgeglichen wurde.
- `src/libslic3r/AppConfig.cpp`: Standardwert `true`.
- `src/slic3r/GUI/Preferences.cpp`: Workflow-Schalter und Rücksetzen auf Fork-Standardwerte.
- `tests/prefect/workflow_test.cpp`: prüft Abschalten, Schweregrad und andere Meldungen.

Basis: `v02.08.02.61`, Commit `926a7192574bcb9b3a732e1ec59a46d79cb45466`.

## Nachziehen bei Updates

1. Nach dem alten englischen Text in der aktuellen Materialdatenbank und im Code suchen. Nicht nach dem übersetzten Dialogtitel suchen.
2. Falls Upstream stabile Warnungs-IDs eingeführt hat, auf diese umstellen und die Tests auf die neue ID aktualisieren.
3. Den Filter weiterhin vor der Übersetzung, aber nur für den präzisen Warnungstyp einsetzen. Keine komplette Blacklist abschalten.
4. Standardwert, Schalter, Manifest und deutschen Katalog übernehmen.
5. Eigenständigen Regressionstest und vollständigen Windows-Build ausführen.

## Abnahme im Programm

TPU/TPU-AMS auf einem betroffenen Drucker wählen und die Druckvorbereitung öffnen. Mit aktivem Schalter darf die Cold-Pull-Zeile nicht erscheinen. Schalter ausschalten, denselben Ablauf wiederholen: Die Zeile muss wieder erscheinen. Einen anderen Materialhinweis sowie eine unzulässige AMS-/Düsenkombination testen. Diese müssen unabhängig vom Schalter angezeigt werden. Auf Deutsch und Englisch wiederholen; nach einem Neustart muss der Schalter erhalten bleiben.

Die eigenständigen Tests ersetzen diesen Druckerdialog-Test nicht.
