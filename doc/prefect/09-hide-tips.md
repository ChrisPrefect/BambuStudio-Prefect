# F09 – Tipps ohne Restfläche ausblenden

## Verhalten und Konfiguration

`prefect_hide_tips=true` blendet sowohl das eigenständige Daily-Tips-Fenster als auch das Tipps-Panel in der Slice-Benachrichtigung aus. Die reservierte Höhe, der Trenner und das Child-Fenster für die Tipps entfallen. Der Slice-Fortschritt und die Abbrechen-Schaltfläche bleiben vorhanden.

Der Schalter steht unter Einstellungen → Workflow. Bei `false` wird die Upstream-Darstellung wieder verwendet; der bestehende `show_hints`-Wert steuert dann weiterhin das Auf-/Zuklappen. Der Fork verlässt sich bewusst nicht auf `show_daily_tips`: Dieser alte Schlüssel verhindert in der Basisversion nicht sämtliche neueren Tipps-Darstellungen.

## Dateien und Suchanker

- `src/slic3r/GUI/DailyTips.cpp`: `DailyTipsPanel::render`, `DailyTipsWindow::open` und `DailyTipsWindow::render`. Guards liegen vor ImGui-Zustandsänderungen; ein schon offenes Fenster wird beim Abschalten geschlossen.
- `src/slic3r/GUI/SlicingProgressNotification.cpp`: `const bool show_tips`. Höhe und Padding werden nur bei sichtbaren Tipps eingerechnet. Trenner sowie `BeginChild`/`EndChild` werden zusammen übersprungen.
- `src/libslic3r/AppConfig.cpp`: Standardwert.
- `src/slic3r/GUI/Preferences.cpp`: Workflow-Schalter und Reset.

Basis: `v02.08.02.61`, Commit `926a7192574bcb9b3a732e1ec59a46d79cb45466`.

## Nachziehen bei Updates

1. Alle Aufrufer von `DailyTipsPanel`, `DailyTipsWindow` und neue Tips-Komponenten suchen.
2. Die vorhandenen Render-/Open-Guards an die neuen Eintrittspunkte übernehmen.
3. In der Slice-Benachrichtigung sowohl Inhalt als auch zugehörigen Platzbedarf entfernen. Nur `render()` zu überspringen hinterließe eine leere Fläche.
4. ImGui-Paare und Style-Stacks prüfen. Bedingte Bereiche müssen `BeginChild`/`EndChild` gemeinsam umfassen.
5. Das Layout während laufendem Slice, Abschluss, Abbruch, Vorschau und bei anderer DPI prüfen.

## Abnahme im Programm

Mit aktivem Schalter ein größeres Modell slicen: nur kompakte Fortschrittsanzeige, keine Tipps und keine leere Restfläche. Abbrechen muss funktionieren. Tipps über den vorhandenen Menüpunkt öffnen: kein Fenster. Schalter deaktivieren und erneut slicen beziehungsweise Tipps öffnen: Upstream-Tipps erscheinen. Bei offenem Tipps-Fenster den Schalter wieder aktivieren: Fenster verschwindet. Neustart und 100/150/200 Prozent DPI prüfen.

Für diese ImGui-Layoutänderung ist die GUI-Abnahme maßgeblich; ein Textvergleich würde sie nicht verifizieren.
