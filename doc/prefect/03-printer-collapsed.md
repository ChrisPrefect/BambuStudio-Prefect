# F03 – Drucker-Box dauerhaft eingeklappt

## Verhalten

`prefect_printer_collapsed=true` hält den Inhalt unter dem Titel „Drucker“ dauerhaft
auf Höhe null. Der Titel bleibt sichtbar. Ein Klick auf den Titel öffnet die Box in
diesem Modus nicht. Deaktiviert man die Option, wird die Box wieder eingeblendet und
der bisherige Klick zum Ein-/Ausklappen funktioniert normal.

Die Druckerauswahl und die Synchronisierung laufen weiterhin; ausgeblendet wird nur
der Inhalt der oberen Box. Filamentliste und Prozesseinstellungen sind unabhängig.

## Codestellen

Basis: `v02.08.02.61` / `926a7192574bcb9b3a732e1ec59a46d79cb45466`.
Alle UI-Änderungen sind in `src/slic3r/GUI/Plater.cpp`.

- `Sidebar::Sidebar`, direkt nach Anlage von `m_panel_printer_content`:
  `SetMaxSize({-1, 0})` setzt den Anfangszustand vor der ersten Layoutberechnung.
- Derselbe Konstruktor, `m_panel_printer_title->Bind(wxEVT_LEFT_DOWN, ...)`:
  ignoriert das Aufklappen, solange die Option aktiv ist.
- `Sidebar::update_ui_from_settings`: wendet die Einstellung erneut an und berechnet
  `m_scrolled_sizer->Layout()`. So funktionieren auch Änderungen im Einstellungsdialog
  und UI-Neuaufbauten bei Materialzahl-/Druckeränderungen.

Die vorhandene Höhenbegrenzung wird weiterverwendet; keine versteckten Kopien der
Druckersteuerung und keine Änderung am Modell-/Presetzustand.

## Update-Anleitung

Nach `m_panel_printer_title`, `m_panel_printer_content` und `SetMaxSize` suchen.
Wenn Upstream auf einen Collapse-Widget umstellt, die drei Eingriffspunkte auf dessen
öffentliche API übertragen: Anfangszustand, Benutzerklick, Preferences-Refresh.
Die Option muss unabhängig von den übrigen Einstellungen schaltbar bleiben.

## Prüfung

1. Mit aktivierter Option starten: keine kurz aufgeklappte Box beim ersten Layout.
2. Titel anklicken: weiterhin eingeklappt.
3. Drucker wechseln, Materialanzahl ändern, Darkmode/DPI ändern: weiterhin eingeklappt.
4. Option deaktivieren: Box erscheint und Titel klappt sie wieder normal ein/aus.
5. Wieder aktivieren, Studio schließen und starten: Zustand bleibt eingeklappt.

Die lokale Quellcodeprüfung bestätigt die drei Eingriffspunkte. Eine Laufzeitprüfung
erfordert einen vollständigen GUI-Build.
