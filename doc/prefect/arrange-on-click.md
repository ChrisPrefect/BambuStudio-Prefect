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

Der hier beschriebene Stand ist in **`.6`** veröffentlicht: Quelle
`727a703155237a94e4fcc31ebc4effef515d13f0`, Tree
`16cbb874d6bef7ebbc3453e407451eb9af252b0e`.
Der [native Buildlauf 40414286154](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/40414286154)
ist vollständig erfolgreich, einschließlich Windows-Kompilierung, Paketierung
und abschließender Cache-Schritte. Der
[Release 424868721 / `.6`](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/tag/v02.08.02.61-prefect.6)
wurde am **26.10.2026 um 23:22:49 UTC** veröffentlicht
(**27.10.2026, 00:22:49 Europe/Zurich**). Alle drei öffentlichen Dateien wurden
anonym vollständig geladen und nach SHA256 geprüft; beide ZIPs bestehen CRC.
Die 37 Feature-Commits sind durch 74 identische Patch-Zwischenbäume belegt.
[Auslieferungsbericht und Prüfgrenzen](validation/workflow4.md),
[Veröffentlichungsnachweis](validation/published-release-workflow4.json).

Quellgebundene Starts im isolierten Prüfprofil und im normalen Forkprofil sind
separate Laufzeitnachweise. Sie ersetzen keine sichtbare Bedienprüfung dieser
Funktion. Die nachstehenden Klick-, Häkchen-, Refresh- und Neustartfälle bleiben
als manuelle Abnahme offen, soweit sie nicht einzeln ausdrücklich belegt sind.

Die historische veröffentlichte **`.5`** startete nur beim Öffnungsübergang;
ihr damaliger Startup-/Buildbeleg prüft weder die neuen Wiederholungsklicks
noch den manuellen Start bei laufendem Hintergrundslicing.

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
belegen weder echte Eventzustellung noch sichtbare Toolbarbedienung. Sie liefen
im erfolgreichen Quell-CI mit aktiven Assertions; auch der native Windows-Build
ist erfolgreich. Ein tatsächlicher erster oder wiederholter direkter Iconklick
mit sichtbarem Anordnungsergebnis wird dadurch nicht als bestanden ausgegeben.

Die folgenden noch offenen Fälle mit mindestens zwei synthetischen, zunächst
überlappenden Objekten im separaten Prüfprofil am ausgelieferten `.6`-Build
prüfen. F11 für diesen Versuch
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
