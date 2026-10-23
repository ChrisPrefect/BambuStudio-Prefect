# Bambu Studio Prefect – Workflow 2

Eigener Workflow-Fork auf Basis von Bambu Studio **v02.08.02.61**. Die Anpassungen lassen sich einzeln auf der gemeinsamen Seite **Einstellungen → Workflow** ein- und ausschalten.

- Filamente automatisch vom ausgewählten Drucker übernehmen, einschließlich Nachholen beim Wiedereinschalten.
- Die Druckeinstellungen der einfachen Ansicht über **Felder…** selbst auswählen.
- Obere Drucker-Box dauerhaft eingeklappt halten.
- Aktuelle Platte nach Änderungen automatisch im Hintergrund slicen.
- Markierten Objekten und Teilen durch Klick auf ein Filament das Material zuweisen, einschließlich Misch-/Verlaufsfilamenten, mit Undo. Shift erhält die Bearbeitung.
- Optionaler Filamentmenü-Eintrag **Als Supportinterface festlegen**, auch für Misch-/Verlaufsfilamente.
- Mehrere Modelldateien ohne Zusammenfassungsfrage als einzelne Objekte importieren.
- Die genaue TPU-Cold-Pull-Erinnerung ausblenden.
- Tippsfenster und Tippsbereich einschließlich Leerfläche ausblenden.
- Beim Anordnen die automatische Rotation immer einschalten.
- Nach dem Einfügen mehrerer Objekte automatisch anordnen.

[Bedienung und Anpassungsliste](https://github.com/ChrisPrefect/BambuStudio-Prefect/blob/prefect/workflow/doc/prefect/README.md) · [Dateien, Suchanker und Anleitung für Upstream-Updates](https://github.com/ChrisPrefect/BambuStudio-Prefect/blob/prefect/workflow/doc/prefect/UPSTREAM-UPDATES.md) · [Prüfnachweise und bekannte Prüfgrenzen](https://github.com/ChrisPrefect/BambuStudio-Prefect/blob/prefect/workflow/doc/prefect/VALIDATION.md)

## Windows-Paket

Das ZIP vollständig in einen eigenen neuen lokalen Ordner entpacken. `Start-Prefect.ps1` startet die enthaltene Anwendung mit dem separaten Profil `%APPDATA%\BambuStudio-Prefect`. Das vollständige Paket benötigt keine vorhandene Bambu-Studio-Installation. Vorhandene Anwenderprofile werden nicht durch den Download ersetzt.

## Herkunft und Prüfung

- Quellcommit: `9d4fad7292484403f0b026972835035b0a967d20`.
- Quelltree: `b6feae21b1908e493d880297e901b243073585f5`.
- [Windows-CI: vollständiges Kompilieren, Linken, Paketieren und Regressionstests](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/39975702857).
- Patch-ZIP: **24 aufeinanderfolgende Commits**, nach erneutem Anwenden beider Patchdarstellungen mit identischen Zwischen- und Endtrees. SHA-256: `1a59f8918bbcfdc5c79c42a5fcbea5735984e01f09222945ce8f6045a21173a5`.

Das Actions-Prüfartefakt **Prefect-Workflow2-release-verification** mit `workflow2-release-verification.json` benennt Quellcommit, Quelltree, den erfolgreich abgeschlossenen Windows-Build, Artefakt-ID und SHA-256 der Downloads. `PREFECT-COMMIT.txt` im Windows-Paket bindet es an diesen Quellcommit. `SHA256SUMS.txt` enthält die Prüfsummen von Windows- und Patch-ZIP. Das Patch-ZIP enthält die dokumentierte, erneut angewendete Commitserie und deren Replay-Nachweis.

Diese Veröffentlichung ist eine **Vorabversion**. Der vollständige Windows-Build und die automatisierten Regressionstests sind geprüft. Die Dokumentation unterscheidet tatsächlich durchgeführte lokale Bedienprüfungen von noch offenen GUI-Szenarien. Nicht jede Kombination aus Drucker, Firmware, Material und Mehrfachauswahl ist praktisch geprüft. Es wurde kein physischer Druck gestartet; die Druckerkommunikation und der TPU-Hinweis sind nicht als Hardware-Abnahme bestätigt.
