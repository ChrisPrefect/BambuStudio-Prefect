# F10 – Rotation als editierbarer Anordnungsstandard

## Verhalten und Prüfstand

`prefect_arrange_rotation=true` ist der Standard für neue beziehungsweise
ausdrücklich zurückgesetzte Anordnungseinstellungen. Das Häkchen
„Automatische Rotation für die Anordnung“ bleibt bedienbar. Wird es ausgeschaltet,
gilt diese Wahl für den jeweiligen Druckmodus auch beim nächsten Laden und nach
einem normalen Neustart. Der Workflow-Schalter erzwingt die Rotation nicht bei
jedem Rendern oder Anordnungsjob erneut.

Die gespeicherten Modi sind getrennt: FFF nach Schicht, FFF nach Objekt und SLA.
Ein vorhandener Moduswert hat nach der einmaligen Übernahme des alten
Forkverhaltens Vorrang vor dem zentralen Default. Das Umstellen des Defaults
überschreibt anschließend keine bewusste Modusentscheidung. „Zurücksetzen“ im
Anordnungsmenü ist dagegen eine ausdrückliche Rücksetzung des aktuellen Modus
und verwendet den aktuellen Default für die Rotation.

Gemeint ist die Z-Rotation beim Platzieren auf der Platte. Es wird kein
Orientierungsjob für eine neue Druckausrichtung um X/Y ausgelöst. Abstand,
Materialregeln, Kalibrierregionen, gesperrte Platten und Größenbegrenzungen bleiben
Bestandteil des vorhandenen Anordnungsalgorithmus.

Diese korrigierte Semantik gehört zum vorbereiteten Nachtrag für **`.6`**.
Neuer vollständiger Build, sichtbare GUI-Abnahme und Veröffentlichung sind noch
ausstehend. In der historischen veröffentlichten **`.5`** war der zentrale
Schalter ein dauerhafter Override mit gesperrtem Häkchen. Dessen Build-/GUI-
Belege dürfen nicht als Prüfung des neuen editierbaren Defaults ausgegeben werden.

## Einmalige Übernahme vorhandener Profile

`src/slic3r/GUI/PrefectArrangePolicy.hpp`,
`migrate_arrange_rotation_defaults(config)`, verwendet den Marker
`prefect_arrange_rotation_default_revision`:

1. Ist bereits ein nicht leerer Marker vorhanden, bleibt die Config unverändert.
   Auch eine höhere zukünftige Revision wird nicht zurückgesetzt.
2. Ohne Marker und mit eingeschaltetem altem Fork-Schalter werden die drei
   aktuellen Modusschlüssel in `arrange` einmal auf `"1"` gesetzt:
   `enable_rotation_fff`, `enable_rotation_fff_seq_print`, `enable_rotation_sla`.
   Damit wird die zuvor tatsächlich erzwungene Rotation in eine editierbare
   gespeicherte Wahl übertragen. Alte versteckte `0`-Werte gewinnen bei diesem
   einmaligen Übergang bewusst nicht gegen das bisher wirksame `true`.
3. War der alte Fork-Schalter ausgeschaltet, werden dessen Modus-/Legacywerte
   nicht überschrieben. Der Marker wird trotzdem auf `"1"` gesetzt.
4. Spätere Änderungen des Häkchens werden nicht erneut migriert. Die Änderung
   markiert AppConfig über dessen normale Setter als schmutzig; die normale
   Configspeicherung muss den Marker und die gewählten Moduswerte mit sichern.

Diese zusätzliche Markerrevision ersetzt nicht die gemeinsame
`prefect_workflow_revision`. Die Resetliste in `Preferences.cpp` enthält auch
den Rotationsmarker, damit ein ausdrücklicher Einstellungsreset wieder den
definierten Anfangszustand herstellen kann.

## Quellanker und tatsächliche Jobparameter

`src/slic3r/GUI/GLCanvas3D.cpp`, `load_arrange_settings()`:

- Zuerst die einmalige Migration aufrufen.
- Für FFF den aktuellen suffigierten Schlüssel bevorzugen. Nur wenn er fehlt,
  auf `enable_rotation` beziehungsweise `enable_rotation_seq_print` zurückfallen.
  Ein aktueller `"0"` darf nicht von einem alten `"1"` verdrängt werden.
- `initial_arrange_rotation(stored, default)` verwendet nur bei leerem Wert den
  Default. Gespeicherte `"1"`, `"yes"` und `"true"` bedeuten ein; `"0"` und
  `"false"` bleiben aus.

`GLCanvas3D::_render_arrange_menu(...)` übernimmt Änderungen des normalen
Häkchens unmittelbar in `settings_out.enable_rotation`. Es gibt keinen
F10-spezifischen Disabled-Bereich mehr. Eine allgemeine Sperre während eines
laufenden UI-Jobs bleibt bestehen. Die Y-Achsen-Ausrichtung wird nur bei
ausgeschalteter effektiver Rotation bedienbar; bloßes Anzeigen soll keine
abweichende gespeicherte Y-Vorgabe überschreiben.

Boolesche Menüwerte werden als `"1"`/`"0"` mit dem **dreiparametrigen
`AppConfig::set_str(section, key, value)`** gespeichert. Das ist auch bei den
benachbarten Material-/Y-/Kalibrieroptionen wichtig: Ein dreiparametriger
`set(..., enabled ? "1" : "0")` kann den `bool`-Overload auswählen, weil beide
`const char*` nicht null sind. Dann würde selbst das ausgeschaltete Häkchen als
`true` gespeichert. Die Migration verwendet beim dreiparametrigen `set` deshalb
ausdrücklich `std::string("1")`; der zweiparametrige Markersetter ist davon
nicht betroffen.

`src/slic3r/GUI/Jobs/ArrangeJob.cpp`, `init_arrange_params(...)`, setzt
`params.allow_rotations = settings.enable_rotation`. Es darf hier kein
`prefect_arrange_rotation || ...` mehr geben. `params.align_to_y_axis` bleibt an
ausgeschaltete Rotation gebunden. Alle vorhandenen Aufrufer dieser Parameter-
Funktion, einschließlich der Importanordnung aus F11, verwenden damit dieselbe
gespeicherte Entscheidung wie das Menü.

Default/Erhaltung fehlender Schlüssel stehen in
`src/libslic3r/PrefectWorkflowPreferences.hpp`; Workflow-Schalter und Resetliste
in `src/slic3r/GUI/Preferences.cpp`.

## Policy- und manuelle Prüfungen

`tests/prefect/arrange_test.cpp` enthält die Fälle für die einmalige Migration,
unveränderte fremde Anordnungswerte, ausgeschaltete Altvorgabe, erhaltene höhere
Markerrevision und ein späteres gespeichertes `0` nach Kopie/Neustart der
Testconfig. Sein Configstub bildet den gefährlichen dreiparametrigen
`bool`-Overload nach und zählt dessen unerwünschte Benutzung. Die Defaults werden
zusätzlich durch `tests/prefect/preferences_test.cpp` abgedeckt. Aktive
Assertions sind Voraussetzung; diese Tests ersetzen keine echte Configdatei-
oder GUI-Abnahme. Hier wird kein neuer erfolgreicher CI-/GUI-Lauf behauptet.

Die folgenden Bedienprüfungen gehören zum neuen vollständigen Build und einem
separaten synthetischen Profil:

| Fall | Vorgehen und erwartetes Ergebnis |
| --- | --- |
| Alter Force-Modus ein | Marker fehlt, alter Workflowwert `true`, versteckte Moduswerte `0`: erster Ladevorgang übernimmt einmal `1` in alle drei aktuellen Schlüssel und setzt Marker `1`. |
| Altvorgabe aus | Marker fehlt und Workflowwert `false`: aktuelle/Legacywerte bleiben erhalten; nur der Marker kommt hinzu. |
| Editierbares Häkchen | Rotation ausschalten: Häkchen bleibt aus, Menü mehrfach öffnen und anordnen verändert diese Wahl nicht. |
| Normaler Neustart | Nach dem Ausschalten normal beenden und erneut starten: derselbe Modus lädt `0`; Marker verhindert erneute Übernahme. |
| Getrennte Modi | Nach Schicht ein, nach Objekt aus wählen; zwischen beiden wechseln und neu starten: jeweilige Wahl bleibt. SLA getrennt prüfen, sofern verfügbar. |
| Aktuell vor Legacy | Aktueller FFF-Schlüssel `0`, Legacy `1`, vorhandener Marker: `0` hat Vorrang. |
| Default nach Migration ändern | Zentralen Default ändern: vorhandene Moduswahl bleibt; ausdrückliches Menü-Reset verwendet dagegen den neuen Default. |
| Schreibformat | Nach Speichern die isolierte Config prüfen: ausgeschaltet steht als `0`, nicht versehentlich als boolesches `true`. Abstand und andere nicht zurückgesetzte Werte bleiben erhalten. |
| Y-Ausrichtung und Job | Bei Rotation ein ist Y-Ausrichtung gesperrt; bei Rotation aus wird die gespeicherte zulässige Wahl wirksam. Sichtbarer Zustand und echter Jobparameter stimmen überein. |

## Nachtragen bei einem Upstream-Update

Basis: `v02.08.02.61` / `926a7192574bcb9b3a732e1ec59a46d79cb45466`.

1. Nach `load_arrange_settings`, `_render_arrange_menu`, `init_arrange_params`
   und den drei `enable_rotation_*`-Schlüsseln suchen.
2. Die einmalige Migration vor dem Lesen der Moduswerte erhalten. Vorhandene
   Marker dürfen keine erneute Änderung auslösen; andere Einstellungen bleiben
   unangetastet. Die Migration niemals in jeden Jobstart verlagern.
3. Auf demselben Moduswert anzeigen und ausführen. Alte Force-/OR-Pfade und
   gesperrte F10-Checkboxen entfernen, statt einen zweiten Override einzubauen.
4. Aktuelle Schlüssel vor Legacywerten lesen und stringbasierte Setter prüfen.
   Ein Aufruf mit `const char*` darf nicht still den `bool`-Overload treffen.
5. Menü-Reset, Defaults, Markerreset und Tests zusammen übertragen. Dann die
   manuellen Modus-, Speicher- und Neustartfälle am vollständigen Build prüfen.
