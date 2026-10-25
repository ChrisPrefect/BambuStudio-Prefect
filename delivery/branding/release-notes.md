# Prefect Bambu Studio – Branding

Der eigene Bambu-Studio-Fork heißt jetzt **Prefect Bambu Studio**. Die Fenstertitel tragen den Prefect-Namen; das Windows-Programm und seine Fenster verwenden das violette Icon. Die elf einzeln schaltbaren Workflow-Anpassungen der vorherigen Veröffentlichung sind weiterhin enthalten.

- Anzeigename und Windows-Dateibeschreibung: **Prefect Bambu Studio**.
- Prefect-Präfix im Fenstertitel, auch bei geöffneten Projekten.
- Violettes Icon in der EXE und den mitgelieferten Laufzeitressourcen.

Das ZIP vollständig in einen eigenen neuen lokalen Ordner entpacken. `Start-Prefect.ps1` verwendet weiterhin das getrennte Profil `%APPDATA%\BambuStudio-Prefect`; vorhandene Drucker- und Materialprofile müssen für die Namensänderung nicht migriert werden. Der interne Dateiname `bambu-studio.exe` bleibt erhalten, damit bestehende Startbefehle funktionieren. Verknüpfung und Taskleistenanheftung werden auf dem jeweiligen Windows-Rechner eingerichtet.

[Bedienung und Anpassungsliste](https://github.com/ChrisPrefect/BambuStudio-Prefect/blob/prefect/workflow/doc/prefect/README.md) · [Upstream-Updates und Patch-Anker](https://github.com/ChrisPrefect/BambuStudio-Prefect/blob/prefect/workflow/doc/prefect/UPSTREAM-UPDATES.md) · [Prüfnachweise](https://github.com/ChrisPrefect/BambuStudio-Prefect/blob/prefect/workflow/doc/prefect/VALIDATION.md)

## Prüfung

- Quellcommit: `aef480ca62cfc9ce86a065e2769efe199d7450d1`.
- Quelltree: `aecda9a6db6ebdd470c65228f65c1fae69e8ec22`.
- [Windows-Build und automatisierte Regressionstests](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/40198926718).
- Violettes ICO: 14411 Bytes, SHA-256 `db77286997a999fb0f8e06d7522f3c4f843ed61ea0d8718284d942211e1bf5a8`.
- Patch-ZIP: **28 aufeinanderfolgende Commits**, jeweils als Format-Patch und Rohdiff erneut angewendet; alle 56 Zwischen- und Endtrees stimmen überein. SHA-256 `391cbc28d22d4312a1bcd036e9a8faee12868d4f98653033cbca58ee7dcc300e`.

Vor Veröffentlichung werden Quellcommit, Quelltree, erfolgreicher Windows-Build, Artefakt-ID, ZIP-CRC und tatsächliche Download-Hashes geprüft. Zusätzlich müssen die **eingebetteten EXE-Versionstrings** und **jedes Bild der eingebetteten Iconressource** mit dem eingefrorenen Prefect-Namen und ICO übereinstimmen. Ein bloß umbenanntes altes Paket wird abgelehnt.

Der Build stellt den Web-Bundle des Filament-Managers bei fehlenden Ausgaben auch nach einem Cache-Restore wieder her und prüft nach dem Installieren alle Webdateien vor dem Upload. Damit wird das fehlende Frontend des verworfenen ersten Branding-Testpakets behoben.

`SHA256SUMS.txt` enthält die Hashes von Windows- und Patch-ZIP. Das Actions-Prüfartefakt **Prefect-Branding-release-verification** dokumentiert die tatsächlichen Source-, Build-, Asset- und Branding-Pins. Die Patchserie enthält den nachgewiesenen Replay auf der angegebenen Upstream-Basis.

Die Veröffentlichung bleibt eine Vorabversion. Konkrete lokale Bedienprüfungen und verbleibende GUI-/Druckergrenzen sind in der Dokumentation getrennt ausgewiesen. Die Namens- und Iconänderung bestätigt keine zusätzliche Drucker- oder Firmware-Kompatibilität. Es wurde durch diese Veröffentlichung kein physischer Druck gestartet.
