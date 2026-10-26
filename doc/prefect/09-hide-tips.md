# F09 – Tipps ohne Restfläche ausblenden

## Verhalten und Konfiguration

`prefect_hide_tips=true` blendet sowohl das eigenständige Daily-Tips-Fenster als auch das Tipps-Panel in der Slice-Benachrichtigung aus. Die reservierte Höhe, der Trenner und das Child-Fenster für die Tipps entfallen. Der Slice-Fortschritt und die Abbrechen-Schaltfläche bleiben vorhanden.

Zusätzlich unterdrückt F09 die typisierten Tipps und Vorschläge aus dem NotificationManager: `DidYouKnowHint`, `SimplifySuggestion`, allgemeine `CustomNotification` auf Hint-Level und den konkreten `BBLArcFittingInfo`-Hinweis. Letzterer erzeugt den Screenshottext zur erkannten erweiterten Kurvenplanung und läuft im Upstream auf Warning-Level. Der Filter erkennt ihn am Typ, nicht am übersetzten Text. Die automatische Deaktivierung der Bogenanpassung selbst bleibt erhalten.

Automatische Erstnutzungstipps für einen bereiten Filamentswitcher werden ebenfalls übersprungen. Der separate `show_fila_switch_tips`-Wert bleibt gespeichert; echte NotReady-/Kalibrierwarnungen und bewusst geöffnete Hilfe bleiben erreichbar. Bereits sichtbare gefilterte Benachrichtigungen verschwinden beim Einschalten; beim Ausschalten werden alte Meldungen nicht künstlich wiederholt.

Druckwarnungen wie `BBLMultiFilaNoWipeTower` bleiben auch dann sichtbar, wenn der Upstream sie als Hint einstuft. Fehler und schwerwiegende Warnungen werden nicht pauschal nach Level ausgeblendet. Der Schalter steht unter Einstellungen → Workflow. Bei `false` wird die Upstream-Darstellung wieder verwendet; der bestehende `show_hints`-Wert steuert dann weiterhin das Auf-/Zuklappen. Der Fork verlässt sich bewusst nicht auf `show_daily_tips`: Dieser alte Schlüssel verhindert in der Basisversion nicht sämtliche neueren Tipps-Darstellungen.

## Dateien und Suchanker

- `src/slic3r/GUI/DailyTips.cpp`: `DailyTipsPanel::render`, `DailyTipsWindow::open` und `DailyTipsWindow::render`. Guards liegen vor ImGui-Zustandsänderungen; ein schon offenes Fenster wird beim Abschalten geschlossen.
- `src/slic3r/GUI/SlicingProgressNotification.cpp`: `const bool show_tips`. Höhe und Padding werden nur bei sichtbaren Tipps eingerechnet. Trenner sowie `BeginChild`/`EndChild` werden zusammen übersprungen.
- `src/slic3r/GUI/NotificationManager.cpp`: typisierte F09-Filter am Meldungseingang und vor dem Rendern; kein Textvergleich für allgemeine Tipps. Der separate F13-Livefilter für drei alte Helio-Tutorialtexte ist im Helio-Dokument beschrieben.
- Die freien Helfer `prefect_suppress_tip` und `prefect_suppress_helio_tip` sind bewusst generische Lambdas mit `const auto&`: `NotificationManager::NotificationData` ist privat und darf außerhalb des Klassenkontexts nicht ausdrücklich als Parametertyp genannt werden. Der erste native MSVC-Lauf meldete dafür C2248; die finale Quelle `939e0b3c` deduziert den Typ ohne Änderung des gemeinsamen Headers/PCH. Policyaufrufe sind vollständig als `Slic3r::Prefect::…` qualifiziert, damit ein sichtbarer `Slic3r::GUI::Prefect`-Namespace sie nicht anders bindet.
- `src/slic3r/GUI/Plater.cpp`: Ready-Zweig von `show_filament_switcher_dialog`.
- `src/libslic3r/PrefectWorkflowPreferences.hpp`: Standardwert.
- `src/slic3r/GUI/Preferences.cpp`: Workflow-Schalter und Reset.

Basis: `v02.08.02.61`, Commit `926a7192574bcb9b3a732e1ec59a46d79cb45466`.

## Nachziehen bei Updates

1. Alle Aufrufer von `DailyTipsPanel`, `DailyTipsWindow`, `push_notification` und neue Tips-Komponenten suchen. Die Typ-/Level-Zuordnung gegen den neuen Upstream prüfen, vor allem scheinbare Hint-Level-Druckwarnungen.
2. Die vorhandenen Render-/Open-Guards an die neuen Eintrittspunkte übernehmen.
3. In der Slice-Benachrichtigung sowohl Inhalt als auch zugehörigen Platzbedarf entfernen. Nur `render()` zu überspringen hinterließe eine leere Fläche.
4. ImGui-Paare und Style-Stacks prüfen. Bedingte Bereiche müssen `BeginChild`/`EndChild` gemeinsam umfassen.
5. Das Layout während laufendem Slice, Abschluss, Abbruch, Vorschau und bei anderer DPI prüfen.
6. Die beiden freien Filter als generische Lambdas erhalten oder den Typzugriff innerhalb eines zulässigen Klassenkontexts lösen. Ein isolierter Policytest erkennt keinen unzulässigen Zugriff auf den privaten GUI-Typ; zusätzlich den vollständigen nativen GUI-Build prüfen. Den F09/F13-Filter vor Timestamp-Deduplizierung und vor verzögerten Callbacks lassen und beide Warteschlangen beim Umschalten bereinigen.

## Abnahme im Programm

Mit aktivem Schalter ein größeres Modell slicen: nur kompakte Fortschrittsanzeige, keine Tipps und keine leere Restfläche. Abbrechen muss funktionieren. Tipps über den vorhandenen Menüpunkt öffnen: kein Fenster. Schalter deaktivieren und erneut slicen beziehungsweise Tipps öffnen: Upstream-Tipps erscheinen. Bei offenem Tipps-Fenster den Schalter wieder aktivieren: Fenster verschwindet. Neustart und 100/150/200 Prozent DPI prüfen.

Für diese ImGui-Layoutänderung ist die GUI-Abnahme maßgeblich; ein Textvergleich würde sie nicht verifizieren.

Zusätzliche Regression: Den Kurvenplanungs-Hinweis mit F09 an/aus auslösen; nur seine Anzeige darf wechseln. Eine schon offene Meldung beim Einschalten schließen. Druckwarnung ohne Wischturm, Kalibrierwarnung, Slice-Fehler und Slice-Erfolg jeweils erhalten. Die Policytests prüfen diese Klassengrenzen unabhängig von Sprache und GUI.
