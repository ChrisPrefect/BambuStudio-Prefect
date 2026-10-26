# Eigene Felder in der einfachen Ansicht

## Zweck und Bedienung

Die einfache Prozessansicht ist nicht mehr auf die von Bambu vorgegebenen
`comSimple`-Felder beschränkt. Neben dem Schalter für die erweiterte Ansicht
steht **Felder...**. Der Dialog zeigt die tatsächlich vom Prozess-Tab angelegten
Felder, mit Kategorie, Gruppe, übersetzter Bezeichnung und stabilem internem
Konfigurationsschlüssel. Suche nach Bezeichnung, Gruppe, Kategorie und Schlüssel
ist möglich. Ein Häkchen bestimmt die Sichtbarkeit in der einfachen Ansicht.
Optionen, die Upstream gemeinsam in einer Eingabezeile darstellt, bilden einen
gemeinsamen Listeneintrag, mit `+` zwischen den Feldnamen. Ein Häkchen wählt
alle Schlüssel dieser Zeile gemeinsam; die bestehende gemeinsame Beschriftung
und das Layout bleiben erhalten. Die gewöhnlichen Prozessfelder dieses
Upstream-Stands besitzen jeweils eine eigene Zeile.

Ein weiterer Zugang befindet sich unter **Einstellungen → Workflow**:
Der Schalter für eigene Felder und **Felder für die einfache Ansicht wählen...**
verwenden dieselbe gespeicherte Auswahl und denselben Dialog. Beim erstmaligen
Aktivieren ohne gespeicherte Liste initialisiert `TabPrint::initialize_simple_fields()`
die Liste aus den aktuellen einfachen Standardfeldern. Eine ausdrücklich
gespeicherte leere Liste wird dabei nicht ersetzt.

Ein geändertes Feld aktiviert die eigene Auswahl automatisch. Mit dem oberen
Kontrollkästchen lässt sich die eigene Auswahl deaktivieren, ohne sie zu verlieren.
**Upstream-Standard wiederherstellen** übernimmt die `comSimple`-Vorgaben des
gegenwärtigen Upstream-Stands und deaktiviert die eigene Auswahl. Erst **OK**
speichert; **Abbrechen** verändert weder Anzeige noch Konfiguration.
Das Übernehmen der Feldauswahl lässt eine bestehende Objektauswahl bestehen.

Die Auswahl gilt für globale Druckeinstellungen sowie für die jeweiligen
verfügbaren Objekt-, Teil-, Höhenbereichs- und Platteneinstellungen. Ein Feld,
das für einen bestimmten Kontext vom Upstream entfernt wird, wird durch die
Auswahl nicht erfunden. Gewählte, im aktuellen Kontext angelegte Felder bleiben
auch dann auffindbar, wenn eine dynamische Voraussetzung fehlt: Die Zeile bleibt
sichtbar und die Eingabe ist ausgegraut. Drucker-/Nozzle-/Supportgrenzen und
Readonly-Regeln bleiben erhalten; Parameterwerte werden dafür nicht verändert.
Die erweiterte und die Entwickleransicht verwenden weiterhin die Upstream-
Moduszuordnung. Das normale Brücken-Supportfeld wird dort bei Tree-Support
ebenfalls sichtbar, aber nicht als wirksame editierbare Option dargestellt.
Filament- und Drucker-Tabs werden nicht verändert.

Die separate Funktion [F15: eine einfache Liste](15-single-simple-list.md)
entfernt Kategorienumschalter und Gruppenüberschriften. Sie funktioniert auch
ohne F02 mit den normalen einfachen Upstream-Feldern. F02 bestimmt die Feldmenge,
F15 deren Gliederung; beide Entscheidungen bleiben unabhängig gespeichert.

Die Suche in Druckeinstellungen berücksichtigt dieselbe Auswahl: Ein zusätzlich
eingeblendetes erweitertes Feld ist in der einfachen Ansicht suchbar. Das ist
eine eigenständige Integrationsstelle; nur die Zeilen auszublenden genügt nicht.

## Persistenz und Migration

Zwei Schlüssel im Abschnitt `app` der `BambuStudio.conf`:

| Schlüssel | Typ | Standard | Bedeutung |
| --- | --- | --- | --- |
| `prefect_simple_fields_enabled` | Boolean | `false` | Eigene Liste in einfacher Prozessansicht anwenden |
| `prefect_simple_fields` | String | zunächst nicht angelegt | Kommagetrennte stabile Optionsschlüssel; gespeichert leer ist eine eigene Entscheidung |

Beispiel:

```json
"prefect_simple_fields_enabled": true,
"prefect_simple_fields": "layer_height,seam_position,sparse_infill_density,support_interface_filament,wall_loops"
```

Die Reihenfolge wird beim Speichern stabil lexikographisch sortiert. Duplikate
werden entfernt. `#n`-Varianten werden auf den Basisschlüssel normalisiert; eine
Feldauswahl bezieht sich damit auf die gesamte Option. Umgebende Leerzeichen
sind beim Lesen zulässig. Ein leeres Feld bei aktivierter eigener Auswahl
bedeutet ausdrücklich, dass keine Prozessfelder angezeigt werden. Der
**Felder...**-Knopf bleibt unabhängig davon erreichbar.

Unbekannte oder beim aktuellen Drucker nicht angelegte Schlüssel werden beim
normalen Bearbeiten beibehalten. Beim Wechsel zu einem anderen Drucker oder
nach einem Upstream-Update geht die Auswahl so nicht verloren. Neue
Upstream-Felder erscheinen bei aktivierter eigener Liste erst nach Auswahl;
bei deaktivierter Liste gelten automatisch die aktuellen Upstream-Vorgaben.
Ein ausdrücklich ausgeführtes Zurücksetzen ersetzt die Liste durch die
derzeitigen Standardfelder.

Es werden nur persönliche GUI-Einstellungen gespeichert. Druckprofile,
3MF-Projektfelder und Slicer-Algorithmen erhalten keine neuen Parameter.

**Konkrete Präsenzkorrektur:** `AppConfig::has()` wertet einen leeren String als
nicht vorhanden. Für diese Liste ist das ungeeignet. Der neue Helfer
`load_simple_field_selection` verwendet deshalb `get("app", key, value)` und
dessen Präsenzrückgabe. Eine gespeicherte leere Auswahl wird nach Neustart nicht
mit Standardfeldern aufgefüllt. Vorhandene nichtleere Auswahl und unbekannte
Schlüssel bleiben erhalten; es wird keine Benutzerliste in den Quellcode kopiert.
Initialisierung und bestätigter Dialog speichern über den vorhandenen
`AppConfig::save()`-Weg im verwendeten Fork-Anwendungsprofil. Ein Update benutzt
dieselbe Profilablage; die Liste gehört nicht zu einem einzelnen Druckpreset.

## Global und Objekte sind Geltungsbereiche

**Global/Objekte** wechselt die Reichweite der Druckparameter. **Einfach/Erweitert**
ändert dagegen die sichtbaren Felder. Das sind voneinander unabhängige Achsen.
`ParamsPanel::set_active_tab` wählt bei lokalem Bearbeiten entsprechend der
Auswahl Teil, Höhenbereich, Objekt oder Platte. `TabPrintModel` entfernt bereits
beim Aufbau Schlüssel außerhalb des zulässigen `m_keys`-Umfangs.

Die lokale Konfiguration erbt zunächst die Parent-/globalen Werte und wendet
vorhandene lokale Overrides an. Bearbeiten schreibt nur in die dafür
ausgewählten Modellkonfigurationen. Zurücksetzen löscht die lokalen Schlüssel,
damit wieder der übergeordnete Wert gilt; es schreibt keine Kopie eines
vermeintlichen Standardwerts in alle Objekte.

Das Feld **Brücken nicht unterstützen** heißt in dieser Basis `bridge_no_support`,
nicht `dont_support_bridges`. Es ist ein `PrintObjectConfig`-Parameter und deshalb
global oder für ein Objekt zulässig. Ein Teil-Editor mit `PrintRegionConfig`
und ein Höhenbereich mit dessen begrenztem Schlüsselsatz bieten es strukturell
nicht an. Die gespeicherte F02-Auswahl darf dieses Scope-Limit nicht umgehen.

Zusätzlich blendet Upstream diese vorhandene Zeile bei aktivem Tree-Support
über `toggle_line` aus. Normale Stützen werten `bridge_no_support` aus;
Baumstützen verwenden `max_bridge_length`. Der Fork lässt die Brückenzeile im
zulässigen Scope auch in der Expertenansicht auffindbar, bei Tree-Support aber
deaktiviert und mit erläuterndem Tooltip. Ein ausgewähltes Häkchen wird nicht
als für Tree-Support wirksam ausgegeben. Support aus kann das Feld weiterhin
über `have_support_material` deaktivieren.

## Implementierungsstellen und stabile Suchanker

| Datei | Suchanker | Aufgabe |
| --- | --- | --- |
| `src/slic3r/GUI/PrefectSimpleView.hpp` | `class SimpleFieldSelection` | Unabhängige Parser-, Normalisierungs-, Serialisierungs- und Sichtbarkeitspolicy |
| `src/slic3r/GUI/PrefectSimpleView.hpp` | `load_simple_field_selection`, `simple_row_state` | Gespeichert-leer unterscheiden; Zeilensichtbarkeit von Anwendbarkeit trennen |
| `src/slic3r/GUI/ParamsPanel.hpp` | `m_simple_fields_btn` | Lebensdauer des neuen Knopfs |
| `src/slic3r/GUI/ParamsPanel.cpp` | `Felder...`, `configure_simple_fields`, `delete_subwindows` | Sichtbarer Zugang neben dem Modusschalter, Layout und Freigabe |
| `src/slic3r/GUI/Tab.hpp` | `configure_simple_fields` | Öffentliche Dialogfunktion des Prozess-Tabs |
| `src/slic3r/GUI/Tab.cpp` | `TabPrint::initialize_simple_fields`, `TabPrint::configure_simple_fields`, `simple_field_source_pages` | Fehlende Liste initialisieren; Auswahl aus ursprünglichen Seiten erzeugen, auch bei aktivem flachen Layout; Suche, Reset, Speichern |
| `src/slic3r/GUI/Tab.cpp` | `TabPrint::toggle_options`, `m_prefect_gate_disabled_fields`, `Page::update_visibility` | Gewählte bedingte Zeile erreichbar halten und deaktivieren; ursprüngliche Gates vor jedem Update neu auswerten |
| `src/slic3r/GUI/ConfigManipulation.cpp` | `toggle_print_fff_options`, `bridge_no_support` | Unveränderte Support-/Funktionsabhängigkeiten |
| `src/libslic3r/Support/SupportMaterial.cpp`, `src/libslic3r/Support/TreeSupport.cpp` | `bridge_no_support`, `max_bridge_length` | Unveränderte unterschiedliche Engine-Auswertung normaler und Baumstützen |
| `src/slic3r/GUI/OptionsGroup.hpp` | `is_option_visible`, `m_config_type` | Gemeinsamer virtueller Sichtbarkeitseinstieg; neutraler Initialwert für Gruppen ohne Tab-Kontext |
| `src/slic3r/GUI/OptionsGroup.cpp` | `ConfigOptionsGroup::is_visible`, `ConfigOptionsGroup::is_option_visible` | Gleiche Sichtbarkeit für noch nicht aufgebaute Seiten und aktive Eingabezeilen |
| `src/slic3r/GUI/OG_CustomCtrl.cpp` | `CtrlLine::update_visibility` | Vorhandene Modusabfrage an die Gruppenpolicy delegieren; `toggle_visible` beibehalten |
| `src/slic3r/GUI/Search.cpp` | `OptionsSearcher::append_options`, `simple_fields.visible` | Sichtbarkeit im Suchindex |
| `src/libslic3r/PrefectWorkflowPreferences.hpp` | `set_workflow_defaults`, `prefect_simple_fields_enabled` | Gemeinsame Standardwerte; eine fehlende eigene Feldauswahl ist zunächst deaktiviert |
| `src/libslic3r/AppConfig.cpp` | `Prefect::set_workflow_defaults`, `Prefect::migrate_workflow_preferences` | Gemeinsame Defaults und Migration beim Laden der Anwendungskonfiguration aufrufen |
| `src/slic3r/GUI/Preferences.cpp` | `PreferencesDialog::create_prefect_tab`, `initialize_simple_fields` | Zweiter Dialogzugang und eigener Schalter unter Einstellungen → Workflow; Checkbox nach dem Felddialog aktualisieren |
| `tests/prefect/simple_fields_test.cpp` | `Simple field policy` | Separat ausführbarer C++-Regressionstest |

Die Prozessfelder werden in diesem Upstream-Stand überwiegend als einzelne
Optionszeilen aufgebaut (`TabPrint::build`, `append_single_option_line`). Der
Dialog kann auch gemeinsam aufgebaute Zeilen vollständig auswählen. Bei einer
manuell editierten Liste, die nur den zweiten Schlüssel einer gemeinsamen Zeile
enthält, zeigt die Policy die ganze Zeile an. Seitenprüfung, Custom-Renderer
und nicht benutzerdefinierter Grid-Renderer verwenden dafür denselben
`is_line_visible`-Einstieg. Die Anzeige einzelner Unterfelder einer
zusammengesetzten Eingabe wird nicht neu eingeführt.

## Nachziehen auf einen neuen Upstream-Stand

1. Den gesamten Feature-Commit übernehmen; `PrefectWorkflowPreferences.hpp`
   mit den gemeinsamen Konfigurationsstandardwerten und die Aufrufe aus
   `AppConfig.cpp` ebenfalls übernehmen.
2. Mit `rg -n 'CtrlLine::update_visibility|ConfigOptionsGroup::is_visible|OptionsSearcher::append_options|TabPrint::build' src/slic3r/GUI`
   prüfen, ob Modusfilter, Seitenbaum und Suche noch dieselben Zuständigkeiten
   besitzen. Bei neuen Mehrfachzeilen überprüfen, dass der Dialog alle
   Optionsschlüssel der Zeile gemeinsam setzt und `is_line_visible` für die
   gesamte Zeile ausgewertet wird. Falls die GUI umgebaut wurde, die gemeinsame Policy an die drei
   heutigen Stellen anschließen: Seitenexistenz, Zeilendarstellung, Suche.
3. In `Page::new_optgroup` prüfen, dass `set_config_category_and_type` weiterhin
   die Prozess-/Modell-/Plattenzuordnung setzt. Neu eingeführte Prozesskontexte
   in `ConfigOptionsGroup::is_option_visible` und `is_visible` ergänzen.
4. In `ParamsPanel` den Knopf neben den aktuellen Modusschalter setzen und bei
   dessen expliziter Kindfensterfreigabe berücksichtigen. Keine Abhängigkeit von
   der gerade gewählten Seite einführen: Die komplette Auswahl muss auch bei
   vollständig leerer einfacher Ansicht erreichbar sein. Zusätzlich Zugang und
   Schalter in `PreferencesDialog::create_prefect_tab` erhalten. Eine fehlende
   Liste nur über `TabPrint::initialize_simple_fields` initialisieren; eine
   absichtlich gespeicherte leere Liste erhalten. Nach dem Felddialog die
   Workflow-Checkbox mit dem tatsächlich gespeicherten Wert abgleichen.
5. Umbenannte Optionsschlüssel im Upstream auf eine nötige Migration der
   gespeicherten Liste prüfen. Übersetzte Texte oder Seitenpositionen dürfen
   niemals als persistente Identität benutzt werden.
6. Regressionstest kompilieren und ausführen, GUI bauen und die nachstehenden
   Abnahmen durchführen. Ein erfolgreicher Policytest ersetzt keinen GUI-Build.
7. Zusätzliche dynamische `toggle_line`-Gates getrennt von Modus und Scope
   prüfen. Gewählte, tatsächlich registrierte Zeilen dürfen sichtbar, aber
   nicht entgegen ihrer Anwendbarkeit editierbar werden. Vor der erneuten
   Gate-Berechnung nur die eigene Präsentations-Deaktivierung zurücknehmen;
   `Field::toggle` muss Readonly weiter respektieren. Eine Seite mit genau
   einer bedingt nicht anwendbaren gewählten Zeile vor Aktivierung erreichbar
   halten. Keine ausgeschlossenen Teil-/Höhenbereichsschlüssel hinzufügen.

## Tests und Abnahmeszenarien

Der unabhängige Test benötigt nur einen C++17-Compiler und die Standardbibliothek:

```text
c++ -std=c++17 tests/prefect/simple_fields_test.cpp -o simple_fields_test
./simple_fields_test
```

Unter MSVC entsprechend `cl /std:c++17 /EHsc tests\prefect\simple_fields_test.cpp`.
Er prüft Normalisierung, Duplikate, Rundlauf der Serialisierung, unbekannte
Schlüssel, leere Auswahl und die Abgrenzung zur erweiterten Ansicht sowie zu
anderen Tabtypen.

Nach einem vollständigen Build sind zusätzlich diese GUI-Prüfungen erforderlich:

1. Frisches Profil: Ohne aktivierte eigene Auswahl exakt dieselben einfachen
   Felder wie Upstream. Erweiterte Ansicht ebenfalls vergleichen.
2. **Felder...** öffnen, nach `seam_position` suchen, aktivieren, ein bisher
   einfaches Feld abwählen. Filter löschen: Beide Änderungen bleiben erhalten.
   **OK**: Die erweiterte Option ist sichtbar, das abgewählte Feld verborgen.
3. In der einfachen Suche nach dem neu hinzugefügten erweiterten Feld suchen;
   der Sprung muss auf die jetzt sichtbare Eingabe führen.
4. Nur ein Feld einer sonst vollständig erweiterten Seite wählen: Die Seite
   muss im Seitenbaum erscheinen. Das letzte Feld einer Seite abwählen: Die
   leere Seite muss verschwinden.
5. Alle Felder abwählen: Keine Prozessfelder sichtbar; **Felder...** weiterhin
   erreichbar. Wieder ein Feld aktivieren: Seite und Feld kehren zurück.
6. In die erweiterte Ansicht wechseln: Alle dort vorgesehenen Felder bleiben
   erreichbar. Zurückwechseln: Eigene Liste wird wieder angewendet.
7. Objekt-/Teil-/Höhenbereichs-/Platteneinstellungen öffnen. Nur in diesem
   Kontext vorhandene gewählte Felder erscheinen. Drucker-/Filament-Tabs
   bleiben gegenüber Upstream unverändert.
8. Drucker- und Presetwechsel, Neustart und ein unbekannter Testschlüssel in
   der Liste: Entscheidungen bleiben erhalten; unbekannter Schlüssel geht beim
   nächsten Speichern nicht verloren.
9. Dialog verändern und **Abbrechen**: Keine Config- oder Anzeigeänderung.
   **Upstream-Standard wiederherstellen**, dann **OK**: aktuelle Standardansicht.
10. Windows-Skalierung 100/150/200 Prozent, lang übersetzte Bezeichnungen sowie
    Hell-/Dunkelmodus: Knopf, Suchfeld und Kontrollkästchen bedienen; Dialog
    vergrößern und verkleinern; keine abgeschnittenen Bestätigungsbuttons.

Der Teststatus des konkreten Fork-Builds steht im zentralen Prüfprotokoll.

Zusätzliche Regressionen für den `.6`-Quellnachtrag: gespeicherte leere und
nichtleere Listen nach erneutem Laden; F02/F15 in allen vier Kombinationen;
Suchsprung ohne sichtbare Kategorien; Global ↔ Objekt/Teil/Höhenbereich/Platte;
Tree ↔ normale Stützen und Support aus/an; nur eine gewählte bedingt gesperrte
Zeile; Nozzlewechsel und Rückkehr zur gruppierten Ansicht. Die Policytests
prüfen Speicherung und Entscheidungsgrenzen, keinen neuen nativen GUI-Build.
Der vollständige `.6`-Build und die Veröffentlichung sind inzwischen belegt.
Im normalen V7-Profil blieb die genaue gespeicherte Auswahl samt Aktivierung
erhalten; die echte DLL ist gebunden. Die eigene synthetische QA zeigte eine
flache Controlstruktur, aber nicht alle individuell beschrifteten Felder und
Enablezustände. Eine vollständige normale Hauptoberflächen-/Checkboxabnahme
wird daraus nicht abgeleitet. [Aktueller Bericht und Grenzen](validation/workflow4.md),
[Normalprofilbeleg](validation/workflow4-runtime-normal.json).
