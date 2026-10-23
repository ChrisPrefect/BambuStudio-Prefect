# 11 – Mehrere eingefügte Objekte automatisch anordnen

## Verhalten und Einstellung

`prefect_arrange_after_import: true` aktiviert die Anordnung nach dem erfolgreichen Einfügen mehrerer unabhängiger Objekte. Dies ist der Fork-Standard. Die Option steht auf der zentralen Seite „Prefect-Arbeitsablauf“ und wirkt ohne Neustart. Beim Ausschalten wird auch ein noch wartender Auftrag verworfen.

Erfasst werden normale Geometrieimporte über `Plater::priv::load_files(...)`, einschließlich gemeinsam importierter STL/OBJ-Dateien, und normales Einfügen aus der Studio-Zwischenablage über `Plater::paste_from_clipboard()`, wenn dabei mindestens zwei neue `ModelObject`-Wurzeln entstehen. Zwei unabhängige STEP-Dateien mit je einem Objekt sind ebenfalls zulässig. Entscheidend ist die Zahl der tatsächlich eingefügten Objektwurzeln, nicht die Zahl ausgewählter Dateinamen oder Mesh-Inseln.

Die Anordnung bewegt die neu eingefügten Objekte. Bereits vorhandene Objekte dienen als feste Hindernisse. Ihre relative Lage auf ihrer Platte und ihre explizite Druckreihenfolge werden erhalten. Bei zusätzlichen Platten kann Bambu die Darstellung seiner Platten im globalen Plattenraster verschieben; dafür bleibt die vorhandene Umrechnung zwischen Platten- und Weltkoordinaten zuständig.

Die Drehoption aus F10 wirkt auch für diese Anordnung. Wird F10 ausgeschaltet, verwendet der Anordnungsjob die normale gespeicherte Drehoption.

## Bewusst erhaltene Strukturen

Diese Automatik führt kein `split()` aus und verändert die Hierarchie vorhandener Objekte nicht. Folgende Fälle werden nicht automatisch neu gepackt:

- Ein einzelnes eingefügtes Objekt, auch wenn es mehrere Volumen/Teile oder Instanzen enthält.
- Ein vom Benutzer ausdrücklich als ein mehrteiliges Objekt zusammengefasster Import, der nur eine Objektwurzel ergibt.
- Importbatches mit 3MF oder AMF, einschließlich `.amf.xml`: Projekt-/Plattenpositionen bleiben erhalten.
- STEP-Importe, deren tatsächlich gelesener Inhalt mehrere Objektwurzeln als Baugruppe liefert. Diese erkennbare Baugruppenstruktur wird vor der weiteren Importverarbeitung markiert. Mehrere einzelne STEP-Dateien mit je einer unabhängigen Wurzel fallen nicht pauschal unter diesen Ausschluss.
- Wiederherstellung (`LoadStrategy::Restore`), stille Operationen (`Silence`), reine Configimporte und G-code-/Vorschauprojekte.
- Einfügen von Einstellungen, Volumen oder Instanzen ohne mehrere neue Objektwurzeln. Der ausdrückliche Clone-/Array-Pfad wird nicht an die Automatik angebunden.

Die normale manuelle Anordnung bleibt verfügbar. Ein ausdrücklicher Klick auf Anordnen ersetzt einen noch wartenden automatischen Auftrag, damit kein zweiter Job folgt.

## Ereigniskette und Schutzbedingungen

`src/slic3r/GUI/Plater.cpp`, `Plater::priv`:

1. Zu Beginn jedes `load_files(...)` wird ein älterer wartender Auftrag gelöscht. Erst am erfolgreichen normalen Funktionsende kann der neue Import einen Auftrag anlegen. Frühe Abbrüche/Fehler pflegen deshalb keinen veralteten Auftrag ein.
2. `queue_prefect_arrange_after_import(...)` prüft zentralen Schalter, Zahl der eingefügten Wurzeln und Layoutschutz mit `PrefectArrangePolicy.hpp`. Indizes werden geprüft, auf stabile `ObjectID` abgebildet und dedupliziert. Gespeichert werden außerdem Model-ID, alle Objekt-IDs in ihrer aktuellen Reihenfolge und die aktive Undo-Position.
3. Ein eigener einmaliger wx-Timer wartet zunächst 500 ms. Importdialoge und Snapshot-Scope können vorher auslaufen. Der bestehende Hintergrundtimer wird nun an seine konkrete Timer-ID gebunden; er darf die neuen Timerereignisse nicht als Slicing-Ereignisse behandeln.
4. `on_prefect_arrange_after_import(...)` verwirft den Auftrag bei ausgeschaltetem Schalter, Schließen, nicht editierbarem/ungeeignetem Projekt, geändertem Modell, geänderten Objektwurzeln oder geänderter Undo-Position.
5. Bei vorübergehender Auslastung wartet derselbe Auftrag weitere 250 ms: Hauptfenster deaktiviert/modal, Ansicht verborgen, beschäftigter Cursor oder Maus-Capture, unterdrückte Hintergrundverarbeitung, Post-Processing-Dialog, manuelles Slicing, Publishing, laufender Slicer, Export/Upload, anderer UI-Job/Worker, Drag/Gizmo-Edit oder noch nicht abgearbeitetes Slicing-Fertig-/Abbruchereignis.
6. Solange der Auftrag wartet, startet der automatische Hintergrund-Slicer keinen neuen Slice. Ein bereits laufender Slice darf erst auslaufen. `on_process_completed(...)` quittiert `STATE_FINISHED`/`STATE_CANCELED` mit `background_process.stop()` und stellt `IDLE` her; danach kann der wartende Anordnungsjob starten.
7. Vor dem Jobstart wird der Timerauftrag konsumiert. `m_ui_jobs.arrange(inserted_ids)` verwendet denselben exklusiven, abbrechbaren `ArrangeJob` und denselben „Arrange“-Undo-Snapshot wie die bestehende manuelle Anordnung. Es gibt keinen zweiten Packalgorithmus und kein stilles Kopieren einer fertigen Ergebnisposition.

Eine neue Importoperation, Projekt-Reset, Undo/Redo, manuelle Anordnung oder Destruktion verwirft wartende Arbeit ausdrücklich. Auch eine andere Änderung der Undo-Position vor dem Start verwirft den alten Auftrag, statt nach einer neueren Benutzeraktion verspätet Objekte zu verschieben.

Die gespeicherte Undo-Position bleibt beim regulären Ende des Import-Scope erhalten: `Plater::TakeSnapshot::~TakeSnapshot()` ruft nur `allow_snapshots()` auf und erzeugt keinen neuen Snapshot. Das wurde im vorhandenen Quellcode geprüft.

## Übergabe an den vorhandenen Arrangement-Job

`Plater::priv::Jobs` behält einen Zeiger auf seinen vorhandenen `ArrangeJob`. `arrange(...)` übergibt optional die neue ID-Liste. Eine normale manuelle Anordnung übergibt eine leere Liste und verwendet weiter den bisherigen vollständigen Anordnungspfad.

`src/slic3r/GUI/Jobs/ArrangeJob.hpp/.cpp`:

- `set_inserted_object_ids(...)` speichert die konkrete Objektmenge. `prepare()` verwendet bei einer nicht leeren Liste den bestehenden `prepare_selected()`-Pfad, ohne die sichtbare Auswahl des Benutzers zu ändern.
- Für diesen Pfad bestimmt die ID-Liste alle Instanzen der neuen Wurzeln. Die sichtbare Auswahl wird nicht nachträglich als Auswahlquelle benutzt. Eine leere resultierende Auswahl fällt nicht auf „alles anordnen“ zurück.
- Bereits vorhandene Objekte werden in `m_unselected` übergeben, auch vorhandene nicht druckbare Objekte. Sie werden nicht versehentlich in die zu verschiebenden `m_unprintable` aufgenommen. Ihre ursprüngliche `arrange_order` wird beim Durchreichen der vorhandenen Setter erhalten.
- Wie bei `prepare_all()` werden Platten mit einer abweichenden lokalen Druckfolge für die Dauer des Jobs gesperrt. Ursprünglich gesperrte Platten bleiben gesperrt. Eigene temporäre Sperren werden bei Erfolg, Abbruch und behandelter Worker-Ausnahme wieder aufgehoben.
- Der unveränderte Rechenkern heißt `arrangement::arrange(m_selected, m_unselected, bedpts, params)`. Er berücksichtigt feste Objekte, Abstände, Ausschlusszonen, Materialregeln und weitere vorhandene Parameter. Die vorhandene `PartPlateList`-Vor-/Nachverarbeitung übernimmt gesperrte Platten, Plattenraster und neue Platten.

Wichtiger Befund für spätere Updates: In dieser Upstream-Basis ruft `ExclusiveJobGroup::start()` den vorhandenen virtuellen `before_start()`-Hook nicht auf. Deshalb verlässt sich die Automatik nicht auf dessen Kommentar zum Stoppen des Slicers, sondern wartet ausdrücklich auf einen inaktiven Slicer samt abgearbeitetem Abschlussereignis. Der Patch verändert keine Thread-Abbruch- oder Orphan-Thread-Strategie.

## Prüfungen und Grenzen

`tests/prefect/arrange_test.cpp` prüft die Live-Policy für Zahl/Layoutschutz, aktiven/ausgeschalteten Schalter, Retry bei Beschäftigung und sämtliche dauerhaften Invalidierungsgründe, einschließlich ihrer Priorität gegenüber `busy`. Die Datei ist im lokalen Zig-Runner aufgenommen; die CI findet sie über `*_test.cpp`.

Diese kleinen Tests beweisen keine Geometrie-Kollisionsfreiheit und keine wx-Ereignisreihenfolge. Die folgenden Fälle sind GUI-/Geometrie-Abnahmefälle, keine Behauptung bereits ausgeführter Bedienprüfungen:

| Fall | Erwartung |
|---|---|
| Zwei STL zusammen importieren | Zwei Wurzeln; nach Importende eine automatische Anordnung mit normaler Fortschritts-/Abbruchfunktion. |
| Nur ein Objekt/mehrteiliges Objekt | Keine zusätzliche automatische Anordnung. |
| Zwei normale Objekte kopieren/einfügen | Nur die beiden neuen Wurzeln werden automatisch angeordnet. |
| Teile/Settings/Instanzen einfügen, Clone | Kein neuer automatischer Job; bestehender Befehl behält sein Verhalten. |
| Bestehendes Objekt auf Platte | Neues Paar wird kollisionsfrei unter Berücksichtigung des festen Objekts gepackt; dessen Lage auf der Platte und Druckreihenfolge bleiben erhalten. |
| Mehrere Platten, eine gesperrt | Gesperrte Inhalte unverändert; keine neuen Objekte auf gesperrter Platte; korrekte Plattenraster-Umrechnung. |
| Abweichende lokale Druckfolge | Betroffene Platte während des Jobs geschützt; temporäre Sperre nach Erfolg/Abbruch/Geometriefehler wieder weg. |
| Nicht druckbares Altobjekt | Bleibt am ursprünglichen Ort; wird nicht automatisch auf die virtuelle Platte versetzt. |
| Platz reicht nicht | Normaler Bambu-Algorithmus erstellt weitere zulässige Platten beziehungsweise meldet nicht packbare Objekte. |
| 3MF/AMF-Projekt öffnen | Gespeicherte Objekt-/Plattenpositionen bleiben erhalten. |
| Eine STEP-Baugruppe öffnen | Erkannte Baugruppenplatzierung bleibt erhalten. |
| Zwei einzelne STEP-Dateien | Bei je einer unabhängigen Objektwurzel ist automatische Anordnung zulässig. |
| Modal/Drag/Slice/Export aktiv | Kein paralleler Anordnungsjob; derselbe wartende Auftrag wird später nochmals geprüft. |
| Einstellung während Wartezeit aus | Kein verspäteter Jobstart. |
| Neuer Import/Projekt/Undo vor Start | Kein Job mit alten Indizes/IDs. |
| Undo nach erfolgreicher Anordnung | Erstes Undo nimmt die Anordnung zurück; danach kann der Import-/Paste-Snapshot zurückgenommen werden. Redo reproduziert die Reihenfolge. |
| Manueller Arrange-Klick vor Timer | Genau der manuelle Job läuft, kein nachfolgender doppelter Timerjob. |

## Nachtragen bei einem Upstream-Update

Basis: Upstream `v02.08.02.61`, `926a7192574bcb9b3a732e1ec59a46d79cb45466`.

1. Nach `load_files`, `step_subassembly_split`, `paste_from_clipboard`, `background_process_timer`, `update_restart_background_process` und `undo_redo_to` suchen. Erfolgsenden, Layoutschutz und Timerbindung erneut gegen aktuelle Importpfade prüfen.
2. Den Auftrag an tatsächliche neue `ModelObject`-Wurzeln binden. Keine lang lebenden Objektindizes oder rohen ModelObject-Zeiger im Timer speichern; stabile IDs und Invalidierung bleiben erforderlich.
3. Neue Projekt-/Assembly-/Restore-Formate auf Layoutschutz prüfen. STEP nicht allein anhand seiner Dateiendung pauschal ausschließen.
4. Den aktuellen exklusiven Arrangement-Job wiederverwenden. Wenn Upstream eine sichere ID-/Objektmengenauswahl anbietet, diese dem kleinen optionalen Setter vorziehen.
5. Prüfen, wie feste Objekte, nicht druckbare Objekte, Druckreihenfolge, gesperrte Platten und abweichende lokale Druckfolgen behandelt werden. Den Rückfall „nichts ausgewählt bedeutet alles“ für explizite ID-Listen ausschließen.
6. Job-/Slicer-Lebenszyklus und tatsächliche Aufrufkette von `before_start` erneut lesen. Alle bestehenden Export-/Upload-/Modal-Schutzbedingungen erhalten; Abschlussereignisse müssen konsumiert sein.
7. Configdefault/zentralen Schalter, Policyheader, Test, Zig-Liste und Manifest zusammen nachtragen. Die obige Tabelle mit dem vollständigen Windows-Build prüfen und ausgeführte Fälle samt konkreter Build-ID im Prüfprotokoll festhalten.
