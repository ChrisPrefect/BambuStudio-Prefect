# Prefect Bambu Studio

Eigener Workflow-Fork auf Basis von **v02.08.02.61**: automatische Filamentübernahme,
eigene Felder in der einfachen Ansicht, eingeklappte Drucker-Box,
Hintergrundslicing, Filamentzuweisung per Klick, Supportinterface-Menü,
getrennte Modellimporte sowie ausgeblendete TPU-Cold-Pull-Hinweise und Tipps.
Workflow 2 ergänzt erzwungene Anordnungsrotation und automatische Anordnung
nach dem Einfügen mehrerer Objekte. Alle elf Optionen stehen gemeinsam unter
**Einstellungen → Workflow**; Materialklick unterstützt auch Misch-/Verlaufszeilen.

Der Fork trägt ein violettes Programmsymbol und zeigt **Prefect Bambu Studio**
vor dem Projektnamen im Fenstertitel, einschließlich des Änderungssterns.

[**Windows-Vorabversion .3 herunterladen**](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/tag/v02.08.02.61-prefect.3)
enthält das vollständige Windows-Paket, die 28 geprüften Patches und SHA-256-Prüfsummen.

[Alle elf Anpassungen und Bedienung](doc/prefect/README.md) ·
[Gemeinsame Einstellungsseite](doc/prefect/workflow-settings.md) ·
[Änderungen bei Upstream-Updates nachtragen](doc/prefect/UPSTREAM-UPDATES.md) ·
[Prüfprotokoll](doc/prefect/VALIDATION.md) ·
[Windows-Builds](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/workflows/prefect-workflow.yml)

Die Fork-Version startet mit einem eigenen Profil über `Start-Prefect.ps1`.
Der aktuelle Windows-Build ist kompiliert und gelinkt; alle 6.756 Dateien der
lokalen Installation, die 13 DeviceWeb-Ressourcen und die elf eingebetteten
Icon-Größen sind geprüft. Drei echte GUI-Starts bestätigen die Titel für ein
neues, ein benanntes und ein geändertes Projekt. Desktop- und Startmenülink
verwenden den neuen Namen und dieselbe AppUserModelID wie die Anwendung.
Das tatsächliche Anheften an die Windows-Taskleiste ist noch offen.
[Aktueller Auslieferungs- und Laufzeitnachweis](doc/prefect/validation/branding.md)
nennt Quellstand, öffentliche Downloads und Prüfgrenzen. Die früheren
[Workflow-2-Laufzeitprüfungen](doc/prefect/validation/workflow2.md) für Anordnung
und Hintergrundslicing behalten ihren eigenen geprüften Quellstand.

---

![image](https://user-images.githubusercontent.com/106916061/179006347-497d24c0-9bd6-45b7-8c49-d5cc8ecfe5d7.png)
# BambuStudio
Bambu Studio is a cutting-edge, feature-rich slicing software.  
It contains project-based workflows, systematically optimized slicing algorithms, and an easy-to-use graphic interface, bringing users an incredibly smooth printing experience.

Prebuilt Windows, macOS 64-bit and Linux releases are available through the [github releases page](https://github.com/bambulab/BambuStudio/releases/).

Bambu Studio is based on [PrusaSlicer](https://github.com/prusa3d/PrusaSlicer) by Prusa Research, which is from [Slic3r](https://github.com/Slic3r/Slic3r) by Alessandro Ranellucci and the RepRap community.

See the [wiki](https://github.com/bambulab/BambuStudio/wiki) and the [documentation directory](https://github.com/bambulab/BambuStudio/tree/master/doc) for more information.

# What are Bambu Studio's main features?
Key features are:
- Basic slicing features & GCode viewer
- Multiple plates management
- Remote control & monitoring
- Auto-arrange objects
- Auto-orient objects
- Hybrid/Tree/Normal support types, Customized support
- multi-material printing and rich painting tools
- multi-platform (Win/Mac/Linux) support
- Global/Object/Part level slicing parameters

Other major features are:
- Advanced cooling logic controlling fan speed and dynamic print speed
- Auto brim according to mechanical analysis
- Support arc path(G2/G3)
- Support STEP format
- Assembly & explosion view
- Flushing transition-filament into infill/object during filament change

# How to compile
Following platforms are currently supported to compile:
- Windows 64-bit, [Compile Guide](https://github.com/bambulab/BambuStudio/wiki/Windows-Compile-Guide)
- Mac 64-bit, [Compile Guide](https://github.com/bambulab/BambuStudio/wiki/Mac-Compile-Guide)
- Linux, [Compile Guide](https://github.com/bambulab/BambuStudio/wiki/Linux-Compile-Guide)
  - currently we only provide linux appimages on [github releases](https://github.com/bambulab/BambuStudio/releases) for Ubuntu/Fedora, and a [flathub version](https://flathub.org/apps/com.bambulab.BambuStudio) can be used for all the linux platforms

# Report issue
You can add an issue to the [github tracker](https://github.com/bambulab/BambuStudio/issues) if **it isn't already present.**

# License
Bambu Studio is licensed under the GNU Affero General Public License, version 3. Bambu Studio is based on PrusaSlicer by PrusaResearch.

PrusaSlicer is licensed under the GNU Affero General Public License, version 3. PrusaSlicer is owned by Prusa Research. PrusaSlicer is originally based on Slic3r by Alessandro Ranellucci.

Slic3r is licensed under the GNU Affero General Public License, version 3. Slic3r was created by Alessandro Ranellucci with the help of many other contributors.

The GNU Affero General Public License, version 3 ensures that if you use any part of this software in any way (even behind a web server), your software must be released under the same license.

The bambu networking plugin is based on non-free libraries. It is optional to the Bambu Studio and provides extended networking functionalities for users.
By default, after installing Bambu Studio without the networking plugin, you can initiate printing through the SD card after slicing is completed.

