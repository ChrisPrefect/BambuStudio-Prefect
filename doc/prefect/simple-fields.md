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

Ein geändertes Feld aktiviert die eigene Auswahl automatisch. Mit dem oberen
Kontrollkästchen lässt sich die eigene Auswahl deaktivieren, ohne sie zu verlieren.
**Upstream-Standard wiederherstellen** übernimmt die `comSimple`-Vorgaben des
gegenwärtigen Upstream-Stands und deaktiviert die eigene Auswahl. Erst **OK**
speichert; **Abbrechen** verändert weder Anzeige noch Konfiguration.
Das Übernehmen der Feldauswahl lässt eine bestehende Objektauswahl bestehen.

Die Auswahl gilt für globale Druckeinstellungen sowie für die jeweiligen
verfügbaren Objekt-, Teil-, Höhenbereichs- und Platteneinstellungen. Ein Feld,
das für einen bestimmten Kontext vom Upstream entfernt wird, wird durch die
Auswahl nicht erfunden. Ebenso bleiben Drucker-/Funktionsabhängigkeiten und
deaktivierte Eingabefelder erhalten. Die erweiterte und die Entwickleransicht
verwenden weiterhin die Upstream-Moduszuordnung. Filament- und Drucker-Tabs
werden nicht verändert.

Die Suche in Druckeinstellungen berücksichtigt dieselbe Auswahl: Ein zusätzlich
eingeblendetes erweitertes Feld ist in der einfachen Ansicht suchbar. Das ist
eine eigenständige Integrationsstelle; nur die Zeilen auszublenden genügt nicht.

## Persistenz und Migration

Zwei Schlüssel im Abschnitt `app` der `BambuStudio.conf`:

| Schlüssel | Typ | Standard | Bedeutung |
| --- | --- | --- | --- |
| `prefect_simple_fields_enabled` | Boolean | `false` | Eigene Liste in einfacher Prozessansicht anwenden |
| `prefect_simple_fields` | String | leer | Kommagetrennte stabile Optionsschlüssel |

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

## Implementierungsstellen und stabile Suchanker

| Datei | Suchanker | Aufgabe |
| --- | --- | --- |
| `src/slic3r/GUI/PrefectSimpleView.hpp` | `class SimpleFieldSelection` | Unabhängige Parser-, Normalisierungs-, Serialisierungs- und Sichtbarkeitspolicy |
| `src/slic3r/GUI/ParamsPanel.hpp` | `m_simple_fields_btn` | Lebensdauer des neuen Knopfs |
| `src/slic3r/GUI/ParamsPanel.cpp` | `Felder...`, `configure_simple_fields`, `delete_subwindows` | Sichtbarer Zugang neben dem Modusschalter, Layout und Freigabe |
| `src/slic3r/GUI/Tab.hpp` | `configure_simple_fields` | Öffentliche Dialogfunktion des Prozess-Tabs |
| `src/slic3r/GUI/Tab.cpp` | `TabPrint::configure_simple_fields` | Liste aus `m_pages`/Gruppen/Zeilen erzeugen, Suche, Häkchen, Reset, Speichern, Aktualisieren |
| `src/slic3r/GUI/OptionsGroup.hpp` | `is_option_visible`, `m_config_type` | Gemeinsamer virtueller Sichtbarkeitseinstieg; neutraler Initialwert für Gruppen ohne Tab-Kontext |
| `src/slic3r/GUI/OptionsGroup.cpp` | `ConfigOptionsGroup::is_visible`, `ConfigOptionsGroup::is_option_visible` | Gleiche Sichtbarkeit für noch nicht aufgebaute Seiten und aktive Eingabezeilen |
| `src/slic3r/GUI/OG_CustomCtrl.cpp` | `CtrlLine::update_visibility` | Vorhandene Modusabfrage an die Gruppenpolicy delegieren; `toggle_visible` beibehalten |
| `src/slic3r/GUI/Search.cpp` | `OptionsSearcher::append_options`, `simple_fields.visible` | Sichtbarkeit im Suchindex |
| `src/libslic3r/AppConfig.cpp` | `prefect_simple_fields_enabled` | Standardwerte, vom gemeinsamen Fork-Konfigurationscommit bereitgestellt |
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

1. Den gesamten Feature-Commit übernehmen; die Konfigurationsstandardwerte aus
   dem gemeinsamen Fork-Konfigurationscommit ebenfalls übernehmen.
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
   vollständig leerer einfacher Ansicht erreichbar sein.
5. Umbenannte Optionsschlüssel im Upstream auf eine nötige Migration der
   gespeicherten Liste prüfen. Übersetzte Texte oder Seitenpositionen dürfen
   niemals als persistente Identität benutzt werden.
6. Regressionstest kompilieren und ausführen, GUI bauen und die nachstehenden
   Abnahmen durchführen. Ein erfolgreicher Policytest ersetzt keinen GUI-Build.

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
