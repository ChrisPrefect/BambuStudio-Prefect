# Prefect Bambu Studio – Workflow 3

Diese Vorabversion ergänzt zwei einzeln schaltbare Workflow-Optionen und vervollständigt das Ausblenden von Tipps:

- **Anordnen mit einem Klick:** Öffnen der Anordnen-Optionen startet direkt einen Lauf. Das Popup bleibt offen; nach Abschluss lassen sich Optionen ändern und die Anordnung erneut starten. Während laufender Berechnung sind die Bedienelemente gesperrt. Ausschalten stellt den bisherigen reinen Popup-Einstieg wieder her.
- **Helio-Werbung ausblenden:** Blendet Aktivierungsangebote, Werbeeinstiege und Helio-Werbetipps aus. Bereits aktivierte Analysefunktionen und vorhandene Ergebnisse bleiben verfügbar.
- **Tipps vollständig ausblenden:** Entfernt zusätzlich allgemeine Tippbenachrichtigungen einschließlich bereits offener oder wartender Tipps. Relevante Warnungen, Fehler und Fortschrittsmeldungen bleiben erhalten.

Die neuen Schalter sind standardmäßig aktiv und stehen auf der gemeinsamen Workflow-Seite. Gespeicherte ausgeschaltete Werte werden erhalten. Die bisherigen elf Optionen einschließlich erzwungener Anordnungsrotation und automatischer Anordnung nach Mehrfachimport bleiben erhalten.

Das Windows-ZIP vollständig in einen neuen lokalen Ordner entpacken. `Start-Prefect.ps1` verwendet das getrennte normale Profil `%APPDATA%\BambuStudio-Prefect`. Bestehende Releases `.1`, `.2`, `.3` und `.4` werden nicht verändert.

- Quellcommit: `939e0b3ce6dce937502666f334950eec2e0f542a`.
- Quelltree: `e397ecc3b38d7a22b6ac4891d0897dfc273d7000`.
- Windows-Artefakt: `12619554874`, 264429447 Bytes, SHA256 `cb9bdf2c59b3cf913bbbbe5a17e5687568000c0b2341462afb9bdb69296246fa`, 6756 Dateien.
- [Windows-Build und Regressionstests](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/40248952898).
- Patchserie: 35 Commits / 70 identische Zwischenstände; 1404746 Bytes, SHA256 `8abbd698fb04595fa27f793673993eea9d68ad3609f971a02894149035555746`.

Die Auslieferung prüft Source/Tree, erfolgreichen eigenen CI-Lauf, Artefaktprovenienz, vollständige ZIP-CRC/Hashes, Patchserie sowie tatsächliche EXE-Versionstrings und alle eingebetteten violetten Iconbilder. `SHA256SUMS.txt` bindet Windows- und Patch-ZIP.

[Anpassungen und Bedienung](https://github.com/ChrisPrefect/BambuStudio-Prefect/blob/939e0b3ce6dce937502666f334950eec2e0f542a/doc/prefect/README.md) · [Nachtragen bei Upstream-Updates](https://github.com/ChrisPrefect/BambuStudio-Prefect/blob/939e0b3ce6dce937502666f334950eec2e0f542a/doc/prefect/UPSTREAM-UPDATES.md)

Dies bleibt eine Vorabversion. Die Paketprüfung ersetzt keine physische Druckerabnahme. Durch diese Veröffentlichung wird kein Druck gestartet. Dieser Veröffentlichungsablauf führt weder lokale Appstarts noch Pin- oder Profiländerungen aus; lokale Laufzeitbelege werden getrennt dokumentiert.
