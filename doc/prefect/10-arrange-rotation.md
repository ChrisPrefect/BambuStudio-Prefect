# 10 – Automatische Rotation bei der Anordnung immer aktiv

## Verhalten und Einstellung

`prefect_arrange_rotation: true` aktiviert die Rotation für die Anordnung unabhängig vom zuletzt gespeicherten Häkchen im Anordnungsmenü. Dies ist der neue Fork-Standard. Die Option steht unter **Einstellungen → Workflow** und wirkt ohne Neustart.

Das Anordnungsmenü zeigt „Automatische Rotation für die Anordnung“ bei aktiver Einstellung immer angehakt und gesperrt. Der Hinweis am Kontrollkästchen verweist auf die zentrale Einstellungsseite. Dort lässt sich das Verhalten wieder ausschalten. Bei `false` gilt unmittelbar wieder das normale, je Druckmodus gespeicherte Kontrollkästchen. Der Fork überschreibt dessen gespeicherten Wert nicht beim Aktivieren seiner Vorgabe.

Die Änderung betrifft die Rotation um Z beim Platzieren der Objekte. Sie führt keine automatische Optimierung der Druckausrichtung um X/Y aus und ruft keinen Orientierungsjob auf.

## Umsetzung und Priorität

`src/slic3r/GUI/PrefectArrangePolicy.hpp`, Funktion `arrange_rotation_enabled(force_rotation, remembered_rotation)`, definiert die effektive Entscheidung als `force_rotation || remembered_rotation`. Dieselbe Funktion verwenden das sichtbare Menü und die tatsächlichen Arrangement-Parameter.

`src/slic3r/GUI/GLCanvas3D.cpp`:

- `_render_arrange_menu(...)` liest `prefect_arrange_rotation` bei jedem Rendern. Nur die lokale Anzeigekopie wird für den erzwungenen Zustand geändert; `settings_out.enable_rotation` und die ursprünglichen Configwerte bleiben erhalten.
- Bei erzwungener Rotation wird das Häkchen angehakt und deaktiviert. Eine widersprechende Y-Achsen-Ausrichtung wird ebenfalls als deaktiviert dargestellt. Das bloße Öffnen des Menüs schreibt den ursprünglichen Y-Ausrichtungswert nicht um.
- `load_arrange_settings()` bevorzugt für FFF die vom Menü geschriebenen Schlüssel `arrange.enable_rotation_fff` und `arrange.enable_rotation_fff_seq_print`. Nur wenn der jeweilige Schlüssel fehlt, liest es die älteren Schlüssel `enable_rotation` beziehungsweise `enable_rotation_seq_print`. Der SLA-Schlüssel bleibt `enable_rotation_sla`. Ein expliziter aktueller Wert `0` hat Vorrang vor einem alten Wert `1`.

`src/slic3r/GUI/Jobs/ArrangeJob.cpp`, `init_arrange_params(...)`, liest den zentralen Schalter beim tatsächlichen Jobstart. `params.allow_rotations` erhält die effektive Entscheidung. `params.align_to_y_axis` wird nur bei ausgeschalteter Rotation wirksam. Dadurch stimmen Ausführung und sichtbares Häkchen auch dann überein, wenn das Menü vorher nicht geöffnet wurde.

Alle vorhandenen Aufrufer von `init_arrange_params(...)` verwenden dieselbe Entscheidung. Dazu gehören die normale automatische Anordnung, die Anordnung nach dem Einfügen aus F11 und vorhandene Platzierungsfunktionen, die dieselben Arrangement-Parameter nutzen. Abstand, Materialmischung, Kalibrierregion, gesperrte Platten und Größenbegrenzungen bleiben Teil der bestehenden Bambu-Anordnung.

Der Menüknopf „Zurücksetzen“ bleibt eine ausdrückliche Rücksetzung der ursprünglichen Anordnungsoptionen. Solange die Fork-Vorgabe aktiv ist, bleibt die effektive Rotation trotzdem eingeschaltet.

## Prüfung

`tests/prefect/arrange_test.cpp` prüft alle vier Kombinationen aus Fork-Schalter und gespeichertem Häkchen. Der Test wird vom bestehenden Workflow über `*_test.cpp` und vom lokalen Zig-Testlauf ausgeführt. Assertions müssen aktiviert sein; ein Build mit `NDEBUG` ohne `-UNDEBUG` schlägt absichtlich fehl.

Die folgenden Bedienprüfungen gehören zur GUI-Abnahme; diese Dokumentation behauptet ihre Ausführung nicht:

| Fall | Vorgehen und erwartetes Ergebnis |
|---|---|
| Vorgabe ein | Mit bisher nicht angehakter Rotation starten. Anordnungsmenü öffnen: Häkchen gesetzt und gesperrt. Anordnen nutzt Rotation. |
| Vorgabe aus, alter Wert aus | Zentralen Schalter deaktivieren. Häkchen wird sofort normal bedienbar und ist wieder aus. |
| Vorgabe aus, alter Wert ein | Normales Häkchen einschalten, zentrale Vorgabe ein- und ausschalten. Häkchen bleibt danach ein. |
| Neustart | Bei ausgeschalteter Vorgabe pro Druckmodus ein Häkchen speichern. Neustarten: aktuelle suffigierte Schlüssel werden wieder gelesen. |
| Altes Profil | Nur alte Schlüssel ohne `_fff` verwenden. Ohne aktuellen Schlüssel wird der alte Wert übernommen. |
| Widersprüchliche Schlüssel | Alter Schlüssel `1`, aktueller Schlüssel `0`: bei ausgeschalteter Vorgabe gilt `0`. |
| Druckfolge | Zwischen „Nach Schicht“ und „Nach Objekt“ wechseln. Aktive Vorgabe erzwingt Rotation in beiden Modi; aus zeigt die jeweiligen gespeicherten Werte. |
| Zurücksetzen | Im Menü zurücksetzen. Bei aktiver Vorgabe ist effektive Rotation weiter ein; nach Ausschalten gilt der zurückgesetzte Originalwert. |
| Y-Ausrichtung | Aktive Rotation erlaubt keine gleichzeitige Y-Ausrichtung; gespeicherte Originalvorgabe wird nicht allein durch die Anzeige gelöscht. |

## Nachtragen bei einem Upstream-Update

Basis: Upstream `v02.08.02.61`, `926a7192574bcb9b3a732e1ec59a46d79cb45466`.

1. Nach `_render_arrange_menu`, `Auto rotate for arrangement`, `load_arrange_settings`, `init_arrange_params` und `allow_rotations` suchen.
2. Prüfen, ob Upstream inzwischen die gespeicherten Modusschlüssel konsistent liest/schreibt. Die Legacy-Fallback-Korrektur nur übernehmen, solange sie noch benötigt wird. Aktuelle Werte müssen auch bei `0` Vorrang haben.
3. Die effektive Entscheidung an der Stelle auswerten, die dem echten Arrangement-Algorithmus seine Parameter übergibt. Eine reine Änderung des sichtbaren Häkchens reicht nicht aus.
4. Ursprüngliche Werte erhalten. Der zentrale Schalter soll keine einmalige Configmigration sein und beim Ausschalten keine erfundenen Ersatzwerte herstellen.
5. Anzeige, gesperrten Zustand und Y-Achsen-Unverträglichkeit im Anordnungsmenü mit derselben Entscheidung verbinden.
6. Default/Schalter, deutschen Hinweistext, Manifest und Policytest zusammen übernehmen. Danach die obigen Neustart- und Druckfolgefälle auf dem vollständigen Build prüfen.
