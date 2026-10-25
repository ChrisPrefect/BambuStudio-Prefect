# Violettes App-Symbol aus den vorhandenen SVG-Quellen

Der Fork verwendet **`#7C3AED`** statt des bisherigen `#00AE42` für seine
Windows-App-Symbole. Die vorhandenen Bambu-Zeichen und ihre Vektorpfade bleiben
erhalten. Das ist eine Änderung der App-Identität; grüne Schaltflächen,
Filamentfarben, Druckersymbole und die große About-Grafik werden nicht
pauschal umgefärbt.

## Quellen und erzeugte Dateien

Die ursprüngliche App-Kachel ist `resources/images/BambuStudio.svg`, 128 × 128.
Sie enthält genau eine grüne Hintergrundfüllung und vier weiße Zeichenpfade.
Nur die Hintergrundfüllung wird geändert; alle anderen SVG-Bytes bleiben
erhalten. Der Generator prüft die SHA-256 der auf Grün zurückgesetzten Quelle,
damit spätere Änderungen am Upstream-Symbol eine ausdrückliche Prüfung brauchen.

Das bisherige `BambuStudioTitle.ico` zeigt dagegen nur ein grünes Zeichen auf
transparentem Hintergrund. Dafür wird die unveränderte Pfadgeometrie aus
`BambuStudioBlack.svg` verwendet. Die neue `BambuStudioTitle.svg` ändert dessen
vier Zeichenfüllungen auf Violett und stellt die originale 10:12-Geometrie in
einer quadratischen transparenten Fläche dar. Sie ersetzt das freigestellte
Zeichen nicht durch die App-Kachel und verzerrt seine Proportionen nicht.

| Datei unter `resources/images` | Verwendung / Ableitung |
| --- | --- |
| `BambuStudio.svg` | Bestehende App-Kachel, eine violette Hintergrundfüllung |
| `BambuStudioTitle.svg` | Neue dokumentierte Vektorquelle des freigestellten violetten Titelzeichens |
| `BambuStudio_32px.png` | Kachel, direkt mit 32 × 32 aus dem SVG gerendert |
| `BambuStudio_128px.png` | Kachel, direkt mit 128 × 128 gerendert; auch vom Hauptfenster referenziert |
| `BambuStudio_192px.png` | Kachel, direkt mit 192 × 192 gerendert |
| `BambuStudio.png` | Kachel, ursprüngliche Größe 154 × 154 |
| `BambuStudio.ico` | Windows-EXE-/Shell-Kachel mit mehreren direkt gerenderten PNG-Frames |
| `BambuStudioTitle.ico` | Entsprechende Frames des freigestellten Titelzeichens für bestehende Dialoge |

Beide ICO-Dateien enthalten 32-Bit-PNG-Frames für **16, 20, 24, 32, 40, 48,
64, 128, 154, 192 und 256 Pixel**. Die alte einzelne 154-Pixel-Darstellung
bleibt dadurch zusätzlich zu den üblichen Windows-/DPI-Größen verfügbar.
Die Windows-Ressource `src/platform/msw/BambuStudio.rc.in` bindet weiterhin
`BambuStudio.ico` ein; es werden keine neuen CMake-Variablen benötigt.
Die bestehenden Dialogaufrufer von `BambuStudioTitle.ico` bleiben erhalten.

`BambuStudioBlack.svg` selbst bleibt unverändert. Die macOS-ICNS-Dateien und
Mac-spezifischen PNGs werden durch diesen Windows-Nachtrag nicht geändert.

## Reproduzieren und prüfen

Der Generator [render_app_icons.py](../../scripts/prefect/render_app_icons.py)
benötigt Python, **resvg_py 0.5.0 / resvg 0.48.1** und Pillow. Der Renderer ist
im Skript fest geprüft. Pillow wird ausschließlich zum Lesen und Prüfen der
PNG-/ICO-Frames verwendet, nicht zum Umfärben oder Generieren der Bilddaten.
Der vorliegende Prüflauf verwendete Pillow 12.3.0.

```text
python -m pip install resvg_py==0.5.0 Pillow
python scripts/prefect/render_app_icons.py --check
python scripts/prefect/render_app_icons.py --write --report doc/prefect/validation/purple-app-icon.json
```

`--check` erzeugt die erwarteten Bytes im Speicher und vergleicht alle acht
Assets mit den eingecheckten Dateien. `--write` aktualisiert nur diese acht
Dateien. Systemfonts werden nicht geladen; die Quellen enthalten keine Texte,
externen Bilder oder Skripte. Die normalen App-Builds übernehmen die bereits
eingecheckten Assets und benötigen den Python-Renderer nicht.

Der [maschinenlesbare Nachweis](validation/purple-app-icon.json) enthält
Originalquellen-Hashes, Werkzeugversionen, Ausgabe-Hashes und 22 Vergleiche:
Für jede ICO-Größe werden die grüne und violette Variante derselben SVG-Quelle
mit demselben Renderer erzeugt. Ihre Alpha-Kanäle stimmen exakt überein.
Die weißen vollständig deckenden Bereiche der Kachel bleiben ebenfalls exakt
erhalten. Jede gepackte ICO-Größe wird zusätzlich wieder gelesen und pixelgenau
mit dem zugehörigen SVG-Render verglichen.

Die Pfaddaten sind gegenüber den offiziellen SVG-Quellen unverändert. Eine
byteidentische Kantenglättung gegenüber den alten, anderweitig gerenderten
Upstream-PNG-/ICO-Bildern wird nicht behauptet. Die Transparenzprüfung bezieht
sich ausdrücklich auf den grünen und violetten Render derselben Vektorquelle.

## G-code-Viewer und Umfang

Unter Windows lädt `MainFrame.cpp`, `main_frame_icon(...)`, das Icon der
laufenden EXE auch im Viewer-Modus. Der frühere Wechsel auf eine separate
Viewer-EXE ist in dieser Basis auskommentiert. Dieser Pfad verwendet deshalb
automatisch die neue eingebettete violette App-Kachel.

Die optionale alte Vorlage `BambuStudio-gcodeviewer.rc.in` referenziert
`images/BambuStudio-gcodeviewer.ico`; ein solches ICO oder eine entsprechende
Viewer-SVG liegt in dieser Upstream-Basis nicht im Git-Baum. Hier wurde kein
nicht vorhandenes Viewer-Symbol neu gestaltet. `gcode.icns` gehört zum
separaten macOS-Umfang.

## Prüfung der tatsächlichen Windows-EXE

Der finale Quellstand `aef480ca62cfc9ce86a065e2769efe199d7450d1` wurde im
vollständigen Windows-Lauf `40198926718` gebaut und als
[Vorabversion .3](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/tag/v02.08.02.61-prefect.3)
veröffentlicht. Die tatsächlich installierte EXE enthält alle elf ICO-Größen;
ihre Frame-Bytes stimmen vollständig mit dem eingecheckten violetten ICO
überein. [Öffentlicher PE-/Icon-Beleg](validation/branding-pe-icon.json).
Die drei realen Fenstertitel und Verknüpfungen sind getrennt im
[Auslieferungsbericht](validation/branding.md) belegt. Das tatsächliche
Anheften an die OS-Taskleiste und deren sichtbarer Symbolcache sind weiterhin
kein durch diesen Bytevergleich bestätigter Prüfschritt.

## Bei einem Upstream-Update nachtragen

1. Die Pfade der Windows-RC-Ressource, `main_frame_icon`, der App-PNG-Aufrufer
   und der Dialogaufrufer von `BambuStudioTitle.ico` prüfen. Falls Upstream neue
   App-Identitätsdateien verwendet, diese gezielt an die Vektorquellen anbinden.
2. Die neuen offiziellen `BambuStudio.svg` und `BambuStudioBlack.svg` gegen die
   bisherigen Pfade vergleichen. Bei einer neuen Geometrie die gepinnten
   Quellen-Hashes erst nach Prüfung aktualisieren; ein Generatorfehler ist
   kein Anlass, beliebige zusätzliche grüne Grafiken zu verändern.
3. Nur die beschriebenen Füllfarben übernehmen. Die transparente Titelvariante
   und die Kachel bleiben verschiedene Symbole. Die Vektorpfade erhalten.
4. Assets mit dem gepinnten Renderer erzeugen, `--check` ausführen und den
   öffentlichen Hash-/Alpha-Nachweis erneuern. Für PNGs keine Rastervorlage
   nachzeichnen oder nachträglich skalieren; jede Größe direkt aus SVG rendern.
5. Den Windows-Build kompilieren und danach die tatsächlich eingebetteten
   EXE-Frames, Dialogsymbole und die Verknüpfung der installierten Fork-Version
   prüfen. Generator-/Assetnachweise allein belegen weder die neue EXE noch
   den Windows-Symbolcache oder eine tatsächlich angeheftete Taskleiste.
