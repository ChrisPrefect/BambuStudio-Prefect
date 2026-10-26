# F13 – Helio-Additive-Werbung ausblenden

`prefect_hide_helio_ads=true` blendet Helio-Werbeflächen und Aktivierungsaufforderungen aus. Der Schalter steht unter **Einstellungen → Workflow** und ist standardmäßig eingeschaltet. Bei `false` sind die Upstream-Werbeflächen wieder verfügbar. Bereits gespeicherte Helio-Ergebnisse und ausdrücklich aktivierte Analysen werden nicht aus Projekten entfernt.

Die Funktion ist eine lokale Darstellungsoption. Sie ändert keine Druckerprotokolle, Anmeldedaten oder Netzwerkberechtigungen. Druck-, Slicing- und Analysefehler bleiben sichtbar.

## Quellanker und Nachziehen bei Updates

- `MainFrame.cpp`: `update_helio_button_state` steuert den Drittanbieter-/Aktivierungseinstieg, den bereits aktivierten Analysebutton und ihre RichTooltips. Bei ausgeblendetem Angebot entfällt auch der zugehörige leere Platz/Trenner. Der Eventhandler prüft die Einstellung erneut.
- `DailyTips.cpp/.hpp`: `daily_tip_source` wählt bei gesperrter Helio-Werbung allgemeine Tipps. Beim Quellenwechsel werden Rendererinhalt und Seitenindex erneuert, damit kein zwischengespeicherter Werbetipp stehen bleibt.
- `Plater.cpp`: die automatischen Helio-Tutorialaufrufe nach Slicing beziehungsweise beim Öffnen der Analyse beachten F13.
- `HelioReleaseNote.cpp` und `ReleaseNote.cpp`: Aktivieren/Deaktivieren aktualisiert die gemeinsame Sichtbarkeitsentscheidung. Im ausdrücklich geöffneten Analysedialog werden Trial-/Plans-/Upgrades-Werbe-CTAs ausgeblendet; Kontoverwaltung, nötiger Abonnementhinweis und reale Kontingente bleiben erhalten.
- `Widgets/SwitchButton.cpp`: geänderte RichTooltip-Inhalte schließen ein bereits offenes altes Popup.
- `PrefectHelioAdsPolicy.hpp`: isolierte Quellen-/Sichtbarkeitsentscheidung; `helio_ads_test.cpp` prüft F09/F13 und aktivierte Analysen getrennt.

Im gebundenen Upstream befinden sich die acht Helio-Werbetipps in `helio_hints.ini`; die allgemeine Tippsquelle enthält keine Helio-Werbung. DeviceWeb enthält hier keine zusätzliche Helio-Werbefläche. Deshalb wird kein genereller Web-/Netzwerkfilter eingeführt.

Die konkreten Einstiegspunkte stehen auch im Änderungsmanifest. Bei einem Update alle Aufrufer und Textquellen von `Helio`, `helio_enable`, Werbe-RichTooltips, Welcome-/Enable-Dialogen, Slice-Tutorials, DailyTips und Vorschau-CTAs prüfen. Werbung hat mehrere voneinander unabhängige Eintrittspunkte; nur den Hauptbutton auszublenden reicht nicht.

Die Sichtbarkeitsbedingungen müssen die aktuelle Workflow-Einstellung beachten, einschließlich eines bereits offenen Menüs oder Tippsfensters. Beim Filtern von Tipps deren bestehende Navigation und gültige Indizes erhalten. Einen in alten Profilen aktiven Tutorialzustand bei aktivem F13 nicht weiter als automatische Aufforderung anzeigen. Gespeicherte Zustände nicht löschen, damit der Schalter rücknehmbar bleibt.

Neue Standards ausschließlich bei fehlendem Schlüssel ergänzen. Resetliste und deutsche Übersetzungen gemeinsam pflegen. Ein explizit gespeichertes `false` muss ein Upgrade überstehen.

## Abnahme

F13 an: Topbar, leeres Projekt, Slice-Fortschritt/-Abschluss, Vorschau und DailyTips auf Helio-Werbung/Activation-CTA prüfen. Ein früher aktives Tutorial darf keine Aufforderung öffnen. Vorhandenes Helio-Projektergebnis weiterhin betrachten; reale Fehler nicht verstecken. F13 aus: Upstream-Einstiege und Tipps stehen wieder zur Verfügung. F09 und F13 getrennt testen: Werbefilter soll auch bei sichtbaren allgemeinen Tipps gelten, allgemeine Tipps dürfen beim Abschalten nur von F13 nicht verschwinden.

Für bereits offene oder verzögert wartende Tutorialmeldungen enthält `NotificationManager.cpp::prefect_suppress_helio_tip` einen eng begrenzten Livefilter. Nur die drei aktuellen, exakt lokalisierten Helio-Tutorialtexte auf `CustomNotification`/Hint-Level werden erkannt. Die neuen Meldungen sind zusätzlich an ihren Ursprüngen unterdrückt. Bei Upstream-Änderungen diese drei Textanker samt dem abschließenden doppelten Zeilenumbruch des ersten Tipps nachführen; keine Textpräfixe oder allgemeinen Custom-Warnungen filtern. F09 bleibt ein typisierter, sprachunabhängiger Filter.
