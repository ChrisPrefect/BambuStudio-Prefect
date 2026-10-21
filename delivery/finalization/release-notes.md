# Bambu Studio Prefect – Workflow 1

Eigener Workflow-Fork auf Basis von Bambu Studio **v02.08.02.61**. Die neun Anpassungen sind unter **Einstellungen → Workflow** beziehungsweise direkt im jeweiligen Bedienfeld erreichbar.

- Filamente automatisch vom ausgewählten Drucker übernehmen, einschließlich Nachholen beim Wiedereinschalten.
- **Felder…**: die Druckeinstellungen der einfachen Ansicht selbst auswählen.
- Obere Drucker-Box dauerhaft eingeklappt halten.
- Aktuelle Platte nach Änderungen automatisch im Hintergrund slicen.
- Markierten Objekten und Teilen durch Klick auf ein Filament das Material zuweisen, mit Undo.
- Filamentmenü: **Als Supportinterface festlegen**.
- Mehrere Modelldateien ohne Zusammenfassungsfrage als einzelne Objekte importieren.
- Die genaue TPU-Cold-Pull-Erinnerung ausblenden.
- Tippsfenster und Tippsbereich einschließlich Leerfläche ausblenden.

[Vollständige Anpassungsliste und Bedienung](https://github.com/ChrisPrefect/BambuStudio-Prefect/blob/prefect/workflow/doc/prefect/README.md) · [Dateien, Suchanker und Anleitung für Upstream-Updates](https://github.com/ChrisPrefect/BambuStudio-Prefect/blob/prefect/workflow/doc/prefect/UPSTREAM-UPDATES.md) · [Prüfnachweise](https://github.com/ChrisPrefect/BambuStudio-Prefect/blob/prefect/workflow/doc/prefect/VALIDATION.md)

## Windows-Paket

Das ZIP vollständig in einen **neuen eigenen Ordner** entpacken. `Start-Prefect.ps1` startet die enthaltene Anwendung mit dem separaten Profil `%APPDATA%\BambuStudio-Prefect`. Das vollständige Download-Paket benötigt keine vorhandene Bambu-Studio-Installation. Nicht über eine vorhandene lokale Installation mit Ressourcenverknüpfungen entpacken.

## Herkunft und Prüfung

- Quellcommit: `4b5c3546c7fba94439d9bb0fe69553723b895897`.
- Quelltree: `418524ef74e1e2d49ec1cf9d3fa6e422df072afc`.
- [Windows-CI: vollständiges Kompilieren, Linken, Paketieren und Regressionstests](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/39623913865).
- Windows-ZIP: SHA-256 `c2e28e59dba400e6414b208983f50567020dbc37e1a01ff3ae8d446309f874bc`.
- Patch-ZIP: **20 aufeinanderfolgende Commits**; alle Zwischen- und Endtrees wurden beim erneuten Anwenden geprüft. SHA-256 `7c5207922f3eec258eb8dfc1595644fc55501f10a69e10334ca770c52ff48025`.
- `SHA256SUMS.txt` enthält die Prüfsummen der beiden Downloads.

Das vollständige Paket wurde lokal als eigenständige Installation geprüft und gestartet. Die native Screenshot-/Zeigersteuerung lieferte Zeitüberschreitungen auch im Windows-Explorer; deshalb ist die vollständige manuelle Bedienabnahme der neun Funktionen noch offen. Drucker-/AMS-Abnahme und ein physischer Druck wurden nicht durchgeführt. Konkrete Prüfschritte und Grenzen stehen im verlinkten Prüfprotokoll.
