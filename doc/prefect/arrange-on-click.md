# F12 – Jeder direkte Anordnungsklick startet den Job

## Verhalten und Prüfstand

Mit `prefect_arrange_on_click=true` startet jeder direkte linke Klick auf das
Anordnen-Symbol den vorhandenen manuellen Anordnungsauftrag, sofern Objekte
vorhanden sind, kein UI-Job läuft und die Anwendung nicht gerade beendet wird.
Das Optionspopup bleibt dabei offen. Auch ein erneuter direkter Klick auf das
bereits gedrückte Symbol ist ein Startwunsch und kein Schließklick.

Laufendes Hintergrundslicing darf diesen manuellen Wunsch nicht blockieren.
Der Auftrag gelangt über das vorhandene Canvas-Event in den normalen
Anordnungs-Worker; dessen Vorbereitung stoppt den Hintergrundprozess. Ein
anderer bereits laufender **UI-Job** bleibt dagegen eine Sperre. Es wird kein
paralleler Job und kein automatischer Wiederholungsauftrag für einen Busy-Klick
eingeführt.

Während eines UI-Jobs bleiben das Popup sichtbar und seine veränderlichen
Optionen einschließlich der vorhandenen Anordnen-Taste gesperrt. Danach lassen
sich Abstand, Rotation und weitere Einstellungen ändern. Die vorhandene Taste
im Popup behält ihren eigenen Startpfad. F10 liefert einen editierbaren
Rotationsstandard; F11 steuert die Mehrfachimport-Anordnung separat.

Werkzeugwechsel, ein Klick außerhalb zum Schließen oder programmgesteuertes
Zurücksetzen der Toolbar sind keine zusätzlichen Anordnungswünsche. Bei
`prefect_arrange_on_click=false` gilt wieder das klassische Toggleverhalten:
Symbol öffnet/schließt die Optionen, die vorhandene Popuptaste startet den Job.
Bestehende Tastaturbefehle und Auswahl-/Plattenlogik werden nicht ersetzt.

Diese überarbeitete Semantik ist für **`.6`** vorbereitet. Neuer vollständiger
Build, sichtbare GUI-Abnahme und Veröffentlichung sind noch ausstehend. Die
historische veröffentlichte **`.5`** startete nur beim Öffnungsübergang; ihr
damaliger Startup-/Buildbeleg prüft nicht die neuen Wiederholungsklicks oder
den manuellen Start bei laufendem Hintergrundslicing.

## Quellanker und Aufrufkette

- `src/slic3r/GUI/GLCanvas3D.cpp`, `_init_main_toolbar`, Eintrag `"arrange"`:
  Eingabe- und Enablecallback halten eine `weak_ptr` genau auf die Toolbar,
  der das Symbol gehört. Nicht nachträglich über einen möglicherweise anderen
  Canvas-/Toolbarzugriff den gedrückten Zustand ermitteln.
- Der linke Actioncallback prüft `prefect_arrange_on_click`, den tatsächlichen
  Arrange-Pressedzustand und `manual_arrange_available(...)`. Er postet
  `SimpleEvent(EVT_GLCANVAS_ARRANGE)`; er startet den Job nicht unmittelbar im
  Eingabehandler. Die Funktion `arrange_on_toolbar_open` behält ihren Namen,
  bekommt beim direkten Wiederholungsklick aber weiterhin `popup_open=true`.
- `src/slic3r/GUI/GLToolbar.cpp`, `GLToolbar::do_action`: Die bestehende
  Toggle-Zustandsmaschine dispatcht beim Werkzeugwechsel auch das bisherige
  Element. `requested_item_id`, `check_hover`, Aktion `Left` und Elementname
  unterscheiden deshalb den **direkt angeklickten** Arrangeeintrag vom
  bisherigen, nur zu schließenden Werkzeug.
- `Prefect::preserve_arrange_popup_on_click(...)` lässt nur für diesen direkten
  Arrangeklick bei eingeschaltetem F12 den bereits gedrückten Zustand bestehen.
  Andere Werkzeuge und programmatische Close-Aufrufe behalten ihr Toggleverhalten.
- `src/slic3r/GUI/PrefectArrangePolicy.hpp` enthält außerdem
  `manual_arrange_available`, `arrange_toolbar_enabled` und
  `arrange_on_toolbar_open`. Verfügbarkeit verlangt Objekte, freien UI-Worker
  und eine nicht schließende Anwendung. Hintergrundslicing ist bewusst kein
  weiteres Ausschlusskriterium. Ein bereits offenes Popup bleibt auch bei
  belegtem Worker erhalten.
- `GLCanvas3D::_render_arrange_menu` verwendet dieselbe Verfügbarkeitsentscheidung
  für die allgemeine Sperre der Popupsteuerungen. Die vorhandene Popuptaste ruft
  weiterhin `set_prepare_state(Job::PREPARE_STATE_DEFAULT)` und `Plater::arrange()`.
- `src/slic3r/GUI/Plater.cpp`: Der vorhandene Handler von
  `EVT_GLCANVAS_ARRANGE` setzt denselben Prepare-Zustand und ruft `arrange()`.
  Die vorhandene UI-Jobgruppe stoppt in `before_start()` den Backgroundprozess.
  Undo, Abbruch, Worker und die bestehende Modell-/Plattenlogik bleiben dort
  maßgeblich.
- `src/libslic3r/PrefectWorkflowPreferences.hpp` ergänzt einen fehlenden
  F12-Schlüssel mit `true` und erhält gespeichertes `false`.
  `src/slic3r/GUI/Preferences.cpp` enthält Workflow-Schalter und Resetliste.

## Nachtragen bei einem Upstream-Update

Basis: `v02.08.02.61` / `926a7192574bcb9b3a732e1ec59a46d79cb45466`.

1. Arrangeeintrag, seine Toolbarinstanz, `GLToolbar::do_action` und den
   `EVT_GLCANVAS_ARRANGE`-Handler gemeinsam verfolgen. Eine alleinige Einfügung
   von `arrange()` im Klickhandler reicht nicht.
2. Direkte Eingabe vom automatisch mitdispatchten Schließen des bisherigen
   Werkzeugs trennen. Nur den gedrückten Zustand des unmittelbar angeklickten
   Arrangeeintrags erhalten; niemals sämtliche Togglebuttons offen halten.
3. Den vorhandenen Event-/Jobpfad nutzen. Hintergrundslicing darf den Start
   nicht vorab verhindern, wenn der Job es selbst geordnet stoppt. Einen
   vorhandenen UI-Worker oder die Schließphase weiterhin respektieren.
4. Toolbarzustand und Popuprenderer zusammen prüfen: Busy darf das Popup nicht
   automatisch schließen, seine Parameter dürfen während des Jobs aber auch
   nicht veränderbar werden.
5. Popup-Anordnen, Tastaturbefehle, Abbruch, Undo und F11-Aufträge erhalten.
   Keinen zweiten Scheduler oder eine Busy-Retryschleife für F12 hinzufügen.

## Konkrete Prüfungen

`tests/prefect/arrange_test.cpp` prüft die Policykombinationen für direkten
Arrange-Klick, andere Werkzeuge, programmgesteuertes Schließen, abgeschaltetes
F12, UI-Busy und erhaltenen Popupzustand. Die Verfügbarkeitsfunktion hat bewusst
keinen Backgroundslicing-Veto. Diese kleinen Tests mit aktiven Assertions
belegen weder echte Eventzustellung noch sichtbare Toolbarbedienung. Für den
neuen Stand wird hier kein erfolgreicher Build-/GUI-Lauf behauptet.

Mit mindestens zwei synthetischen, zunächst überlappenden Objekten im separaten
Prüfprofil am neuen vollständigen Build prüfen. F11 für diesen Versuch
ausschalten, damit der Import das Ausgangslayout nicht bereits anordnet:

| Fall | Vorgehen und erwartetes Ergebnis |
| --- | --- |
| Erster Klick | F12 ein, UI-Worker frei: einmal direkt auf Arrange-Klicken. Ein Job beginnt; Popup bleibt offen. |
| Erneuter Symbolklick | Nach Ende direkt dasselbe weiterhin gedrückte Symbol anklicken: genau ein neuer Job, Popup bleibt offen. |
| Hintergrundslicing | Während eines laufenden Background-Slice direkt klicken: der normale manuelle Job stoppt den Hintergrundprozess und ordnet an. |
| UI-Job läuft | Während einer anderen UI-Arbeit klicken: kein zusätzlicher oder aufgeschobener F12-Job. Ein bereits offenes Popup bleibt sichtbar, seine Steuerungen gesperrt. |
| Werkzeugwechsel | Mit offenem Arrangepopup auf ein anderes Werkzeug wechseln: das Arrangeelement schließt ohne neuen Arrangeauftrag; anderes Werkzeug verhält sich wie zuvor. |
| Außerhalb/programmatisch schließen | Popup über vorhandenen Closepfad schließen: kein Anordnungsjob; erneuter direkter Arrangeklick startet wieder normal. |
| Popuptaste | Nach dem Job Abstand ändern und die vorhandene Anordnen-Taste benutzen: ein weiterer Lauf mit den neuen Optionen. |
| F12 aus | Workflowoption ausschalten: Symbol öffnet/schließt nur, Popuptaste startet weiterhin. Entscheidung speichern und normal neu starten. |
| Grenzen | Leeres Modell, Schließphase, Abbruch/Undo sowie F10/F11 jeweils separat prüfen; keine parallelen Worker oder veränderte Platten-/Auswahlsemantik. |
