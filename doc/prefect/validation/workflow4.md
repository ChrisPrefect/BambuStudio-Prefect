# Workflow 4 / veröffentlichte Prefect Bambu Studio .6

Dokumentationsstand: **27. Oktober 2026**, Europe/Zurich. Quellfreeze und
Patcharchiv stammen vom 26. Oktober; der Archivname `20261026` bleibt erhalten.

Quelle `727a703155237a94e4fcc31ebc4effef515d13f0`, Tree
`16cbb874d6bef7ebbc3453e407451eb9af252b0e`.
Der [Buildlauf 40414286154](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/40414286154)
ist seit **26.10.2026, 23:05:48 UTC** vollständig **completed / success**.
Policyjob `121892544860` und Windowsjob `121892750589` einschließlich der
abschließenden Cache-Schritte sind erfolgreich. Das tatsächliche Windows-
Artefakt wurde vollständig geladen und nach SHA256, ZIP-CRC und Quellmarker
geprüft. Die separate V7-Installation und die aktualisierten vorhandenen Links
sind ebenfalls belegt. Eigener QA-Start und normaler Profilstart mit tatsächlich
geladener V7-DLL sind getrennt geprüft. Die `.6` ist veröffentlicht; einzelne
sichtbare Bedienfälle bleiben ausdrücklich offen.
[CI-Beobachtung](workflow4-ci.json), [Paketdownloadbeleg](workflow4-artifact.json),
[Ergebnisindex mit offenen Bindungen](workflow4-results.json).

## Dokumentiertes Quellverhalten

- F02 erhält stabile gespeicherte Feldschlüssel einschließlich einer bewusst
  leeren Liste. Dynamisch nicht anwendbare gewählte, im aktuellen Scope
  registrierte Felder bleiben sichtbar und deaktiviert. Scopefilter und
  Drucker-/Nozzle-/Supportgrenzen bleiben erhalten.
- F03 startet mit eingeklappter Druckerbox und lässt den Header bedienbar.
  Normale UI-/Presetrefreshes erhalten die anschließende Benutzerentscheidung.
- F10 verwendet editierbare Rotationsstandards je Modus. Die frühere effektive
  Force-Wahl wird einmal migriert; spätere eigene Abschaltentscheidungen bleiben
  erhalten. Stringsetter verhindern den `const char*`-zu-`bool`-Overloadfehler.
- F12 hält das Optionspopup bei jedem direkten Anordnen-Iconklick offen und
  nutzt den bestehenden Event-/Jobpfad. Hintergrundslicing ist kein stilles
  Veto; normale Jobvorbereitung hält es an. Interner Toolwechsel und
  programmatisches Schließen erzeugen keinen neuen Auftrag.
- F14 löscht nur die Instanzen der aktuellen Platte über den vorhandenen
  Snapshot-/Undo-/Löschweg. Kopien desselben Objekts auf anderen Platten werden
  bei der Auswahl nicht pauschal mitgenommen.
- F15 zeigt die einfache Prozessansicht ohne Gruppenüberschriften und
  Kategorienumschalter. Es funktioniert unabhängig von F02 mit normalen
  einfachen Upstream-Feldern oder mit der eigenen gespeicherten Auswahl.
- F16 verwendet nur für die fertige manuelle Sync-Erfolgseinblendung einen
  eigenen 1000-ms-OneShot-Timer. Die Frist beginnt bei Show beziehungsweise
  sichtbarer Erneuerung, nicht beim Synchronisationsklick. Hover pausiert sie
  nicht; automatisches Hide hebt das Hauptfenster nicht an.

Diese Beschreibung ist keine vollständige sichtbare GUI-Abnahme.
Die detaillierten Updateanker und konkreten Abnahmeszenarien stehen in den
Featurebeschreibungen der eingefrorenen Quelle.

## Vollständige Patch-Rekonstruktion

37 Commits seit `926a7192574bcb9b3a732e1ec59a46d79cb45466` wurden zweimal
nachgespielt: als Rohdiff und als die tatsächlich ausgelieferten Format-Patches.
Alle **74 Zwischenbäume** stimmen mit den tatsächlichen Git-Quellobjekten überein.
Der normale Index blieb bytegleich und der Quellarbeitsbaum sauber.
Das frühere `.5`-Patcharchiv wurde unverändert nachgeprüft.

| Archiv | Wert |
| --- | --- |
| Name | `Prefect-BambuStudio-patches-20261026-workflow4.zip` |
| Bytes | 1.777.625 |
| SHA256 | `914b68c8e572d4050e6837610ddad19862e28b1a1a40a41a8f3fd625583707bb` |
| Mitglieder | 77: 37 Patches, 37 Rohdiffs, Manifest, Bericht und Exportwerkzeug |

ZIP-CRC, alle Patch-/Diffhashes, sichere Mitgliedspfade und Privacyprüfung sind
bestanden. Persönliche Projekte, Wiederherstellungsdaten, Rohprofile und
maschinenbezogene Arbeitsverzeichnisse gehören nicht in das öffentliche Archiv.
[Replaybericht](patch-replay-workflow4.md),
[vollständiges Manifest](patch-replay-workflow4.json),
[abschließender Tree-Gegenvergleich](patch-replay-workflow4-final.json).

## Tatsächliches Paket, Installation und vorhandener OS-Pin

Das tatsächliche Artefakt `12695023513` enthält 6.756 Dateien, ist
**264.440.555 Byte** groß und hat SHA256
`add72a5bfc23845c5aee6909d95686d99ec538d26d2f455d16110f4f5b52af73`.
Der geladene ZIP-Inhalt besteht CRC, und der Quellmarker entspricht `727a7031`.
Die eigene V7-Installation enthält alle **6.756 Dateien** und **274 Ordner**.
Sämtliche Datei-SHA256 stimmen mit dem ZIP überein. Es wurden keine Hardlinks,
Symlinks oder Junctions verwendet. Der Installer startete keine Anwendung und
griff nicht auf das normale Profil zu. [Installationsbeleg](workflow4-installation.json).
Der gesonderte Nachinstallationscheck hat alle 6.756 Dateien erneut gehasht und
den tatsächlichen Baum exakt mit dem Installer verglichen. Alle 13 DeviceWeb-
Dateien, elf eingebetteten violetten Icon-Größen und 14 erwarteten DLL-Byte-Marker
sind bestätigt. Diese Byteprüfungen belegen noch keine sichtbare Bedienung.
[Installierte PE-/Webressourcen](workflow4-resources.json).

Die beiden vorhandenen Startmenü-/Taskleistenlinks wurden nach privater
Sicherung auf V7 aktualisiert. Normale Profilargumente,
`ChrisPrefect.BambuStudio` und EXE-Icon 0 sind erhalten. Die drei ursprünglichen
Pins bleiben bytegleich; der Desktoplink bleibt abwesend. Die Aktualisierung
erzeugte keinen neuen Pin und startete keine App.
[Metadaten und Bindung](workflow4-shortcuts.json).

Die maßgebliche erfolgreiche öffentliche Shellprüfung bietet bei Startmenü
und tatsächlichem Pin jeweils **„Von &Taskleiste lösen“** an. Sie ist über
die exakten Link-SHA256 an V7 gebunden. Der quarantänisierte erste fehlgeschlagene
Pfad-Split-Versuch wird ausdrücklich nicht als Nachweis verwendet. Unbeteiligte
Shellverben und private Pfade werden nicht veröffentlicht.
[Aktueller OS-Zustand](workflow4-os-pin.json).

## Tatsächliche native und GUI-Laufzeitbelege

Der installierte V7-CLI-Prozess hat ein synthetisches Mehrplattenprojekt mit
**zwei Objekten, drei Instanzen und zwei Platten** eingelesen und erneut als
3MF exportiert. Exit-/Resultcode sind 0, CRC sowie Instanzzahlen und Transformationen
sind erhalten. Eine Kopie mit Instanz 0 auf einer anderen Platte bleibt erhalten.
Das ist ein Parser-/Roundtriptest, kein Aufruf des neuen Löschen-Knopfs.
[Nativer Fixturebeleg](workflow4-native-fixture.json).

Die eigene isolierte GUI-Prüfung bindet tatsächliche Prozessidentität, sieben
Argumente und geladene DLL an das neue Paket. Fehlende F14-/F15-/F16-Schalter
wurden mit `true` gespeichert. Die erste Rotationsmigration setzt Revision 1
und überträgt die zuvor wirksame Wahl in alle drei Modi. F01, Hintergrundslicing
und F11 waren ausschließlich im QA-Profil ausgeschaltet; das sind keine neuen
Produktionsstandards. Die synthetische eigene Feldliste blieb erhalten.
[Finaler eigener Laufzeitbeleg](workflow4-runtime-qa.json).

Roots offizielle Accessibility-Beobachtung zeigt in dieser eigenen Prüfung eine
flache Controlstruktur ohne Kategorienumschalter und Gruppenüberschriften sowie
die anfangs eingeklappte Druckerbox. Die individuellen, selbst gezeichneten
Feldbeschriftungen und sämtliche Enablezustände waren damit nicht vollständig
identifiziert. Der Einstellungsdialog ließ sich öffnen und per Escape schließen;
Workflow-Tab- und Modalaktionen wurden vom aktuellen Elementcache abgewiesen.
Frische WGC-Aufnahmen liefen in einen Timeout. Das sind konkrete Werkzeugbefunde,
keine als bestanden ausgegebenen Pixelprüfungen und keine allgemeine
Unmöglichkeitsbehauptung. [Root-UI-Beobachtung](workflow4-ui-observations.json).

Der A-Tastaturbefehl wurde gesendet, aber weder ein direkter Anordnen-Iconklick
noch das Platzierungsergebnis sind abgenommen. Ebenso offen sind echte
Quick-delete-/Undo-Bedienung, alle 16 Checkboxwechsel, Header-/Rotationscheckbox-
Bedienung, physischer Sync-Timer und Werbesichtbarkeit. Ein eigener Save-As-
Versuch wurde ohne gespeicherte Datei abgebrochen. Die exakt gebundene synthetische
QA-Instanz wurde anschließend durch den autorisierten Helfer beendet; ein
graceful exit ist nicht nachgewiesen, keine Benutzeranwendung wurde beendet.

**Der normale V7-Profilstart ist separat belegt:** tatsächliche EXE, stabile
Prozessidentität, genau die normalen Datadirargumente und geladene neue DLL
stimmen. MD5 der normalen Config und ihrer vorherigen Sicherung sind gültig;
die genaue vorhandene Feldauswahl und ihre Aktivierungsentscheidung blieben
erhalten. Neue Standards und Rotationsmarker sind gespeichert. Feldschlüssel,
Configinhalt und Configfingerprint werden nicht veröffentlicht. Die normale
Accessibility zeigte jedoch keine vollständige Hauptoberfläche; die flache
Normalansicht wird nicht aus der eigenen QA abgeleitet.
[Finaler Normalprofilbeleg](workflow4-runtime-normal.json).

Start über den angehefteten Link und ein Pixeltest des Windows-Iconcaches sind
nicht als durchgeführt belegt. Der verifizierte OS-Pinstatus bleibt ein eigener
Metadaten-/Shellnachweis.

## Veröffentlichung und öffentliche Downloads

Die [Vorabversion `.6`](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/tag/v02.08.02.61-prefect.6)
ist seit **26.10.2026, 23:22:49 UTC**, also **27.10.2026, 00:22:49 Europe/Zurich**,
veröffentlicht, Release `424868721`. Publisher `40419300381` ist erfolgreich;
der direkte Tag zeigt auf die gebaute Quelle `727a7031`.
Alle drei anonymen öffentlichen HTTP-200-Downloads wurden vollständig gehasht.
Windows- und Patch-ZIP bestehen CRC, Quellmarker und 37/74-Manifest stimmen.
Die fünf älteren Releases und alle sechs direkten Tags sind unverändert.
[Finaler Veröffentlichungsbeleg](published-release-workflow4.json),
[öffentliche Downloadprüfung](workflow4-public-downloads.json).

- [Windows-ZIP](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/download/v02.08.02.61-prefect.6/Prefect-Bambu-Studio-2.8.2.61-Windows-x64.zip)
- [37er-Patchserie](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/download/v02.08.02.61-prefect.6/Prefect-BambuStudio-patches-20261026-workflow4.zip)
- [SHA256SUMS.txt](https://github.com/ChrisPrefect/BambuStudio-Prefect/releases/download/v02.08.02.61-prefect.6/SHA256SUMS.txt)

Die veröffentlichte `.5` und ihre früheren Installations-, Pin- und
Laufzeitbelege bleiben historische Nachweise der Quelle `939e0b3c`. Aussagen
über eine damals erhaltene ungespeicherte Sitzung gelten nur für den damaligen
Prüfzeitpunkt; sie sind keine Behauptung einer heute noch laufenden Sitzung.
Keine frühere GUI-Prüfung wird als am neuen Binärstand wiederholt ausgegeben.

Die öffentlichen Belege verwenden kanonische UTF-8-/LF-Hashes. Der abschließende
Dokumentationscommit ist getrennt von der gebauten Quelle und der 37er-Patchserie;
er ändert deren Binär- und Replaybindung nicht.
