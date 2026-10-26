# F16: Manuelle Filamentsynchronisation kurz bestätigen

## Exakter Umfang

`prefect_short_sync_notice=true` blendet ausschließlich das Erfolgsfenster
**Successfully synchronized color and type of filament from printer.** nach
einer 1000-ms-Timerfrist aus. Die Frist hängt nicht davon ab, ob die Maus über
dem Fenster steht. Der eigene Schalter befindet sich unter
**Einstellungen → Workflow**. Bei `false` bleibt das ursprüngliche Verhalten
der Einblendung erhalten.

F16 betrifft `FinishSyncAmsDialog` nach einer erfolgreichen **manuellen**
Synchronisation. Warnungen, Konfliktentscheidungen, die Synchronisation selbst
und andere Dialogklassen werden nicht beschleunigt oder automatisch bestätigt.
F01, der automatische Abgleich, erzeugt schon vorher keine solche zusätzliche
Erfolgseinblendung und wird hier nicht erneut verändert.

## Timer, Fokus und Lebensdauer

`PrefectSyncNoticeDeadline` ist ein eigener OneShot-`wxTimer`, den das
Erfolgsfenster über `wxClientData` besitzt. `StartOnce(1000)` wird bei Show und
beim Erneuern der Informationen neu gestartet. Hide, Wiederverwendung und
Destruktor stoppen die Frist. Der Timerdestruktor stoppt ebenfalls; der
virtuelle `Notify`-Callback prüft unmittelbar vor dem Ausblenden noch
Fensterzustand, Programmende, Dialogmodus und aktuellen Schalterwert.

Die Frist beginnt beim tatsächlichen Anzeigen des **fertigen Erfolgsfensters**
beziehungsweise bei dessen Erneuerung im bereits sichtbaren Zustand. Sie beginnt
nicht beim Klick auf **Synchronisieren** und begrenzt nicht die Dauer des
Netzwerk-/Filamentabgleichs. Eine erneute Erfolgseinblendung erhält eine neue
Frist; der schon abgeschlossene Abgleich wird weder abgebrochen noch wiederholt.

Die automatische Aktion verwendet `Hide()` und führt **keinen** OK-/Entscheidungs-
Handler aus. `BaseTransparentDPIFrame::Show(false)` stoppt dessen Animationstimer.
Der manuelle OK-Weg darf weiterhin `on_hide()` verwenden. Das ist absichtlich
getrennt: `on_hide()` zeigt und hebt das Hauptfenster an, was beim automatischen
Ausblenden den Fokus eines inzwischen aktiven Fensters stören könnte.

Der neue Timer ist unabhängig vom vorhandenen Hover-/Fade-Animationstimer.
Es wird kein globales Standardtimeout und kein Timer anderer Hinweisfenster
geändert. 1000 ms ist die angeforderte Frist der UI-Ereignisschleife; eine unter
Last verspätete Ereigniszustellung wird nicht als harte Echtzeitgarantie ausgegeben.

## Nachtragen und prüfen

| Datei | Anker | Bedeutung |
| --- | --- | --- |
| `src/slic3r/GUI/SyncAmsInfoDialog.cpp` | `PrefectSyncNoticeDeadline`, `FinishSyncAmsDialog` | Eigener Timer, Show/Hide, Aktualisierung, expliziter Stop im Destruktor |
| `src/slic3r/GUI/BaseTransparentDPIFrame.cpp` | `Show`, `on_hide` | Unveränderte Basisklasse; Fokuswirkung des manuellen Weges prüfen |
| `src/libslic3r/PrefectWorkflowPreferences.hpp` | `prefect_short_sync_notice` | Nur fehlenden Wert mit `true` ergänzen |
| `src/slic3r/GUI/Preferences.cpp` | `prefect_short_sync_notice` | Einzelschalter und Reset |
| `tests/prefect/preferences_test.cpp` | `prefect_short_sync_notice` | Standard und erhaltene Benutzerauswahl |

Beim Update die Besitzbeziehung Fenster → ClientData → Timer und dessen Stop
vor Fensterfreigabe erhalten. Kein von diesem Fenster unabhängiger Raw-Pointer-
Timer darf später auf ein zerstörtes Fenster zugreifen. Den Show-Handler auf
das eigene Ereignisobjekt begrenzen; neue Informationen starten eine neue Frist.
Die allgemeine Hoverpause und Warnfenster bleiben erhalten.

Die eigentliche wxTimer-/Fensterfunktion benötigt nach dem neuen nativen Build
eine echte GUI-Abnahme: manueller Sync erfolgreich, Maus darüber, frühes
manuelles Schließen, erneute Synchronisation, Schalter aus, Fensterzerstörung
und Fokus in einem anderen Fenster. Ein Konflikt-/Fehlerdialog muss unverändert
bleiben. Die Preferences-Policy allein belegt diese UI-Fälle nicht.
**Die neue `.6` ist in diesem Quellstand noch nicht gebaut oder veröffentlicht.**
