# Vollständiger Windows-Build 4b5c – CI-Nachweis

Frische GitHub-API-Prüfung: **21.10.2026, 16:45:10 UTC**.
[Maschinenlesbare Metadaten und ausgewählte Logbelege](cloud-build-4b5c.json).

| Gegenstand | Belegtes Ergebnis |
| --- | --- |
| Quellcommit | `4b5c3546c7fba94439d9bb0fe69553723b895897` |
| Quelltree | `418524ef74e1e2d49ec1cf9d3fa6e422df072afc` |
| [Run 39623913865](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/39623913865) | abgeschlossen, **success**, Versuch 1 |
| Policy-/Manifestjob | **119304237107**, success |
| [Windows-Job 119304581333](https://github.com/ChrisPrefect/BambuStudio-Prefect/actions/runs/39623913865/job/119304581333) | vollständiges Kompilieren, Linken, Installieren und Artefaktupload erfolgreich |
| Dependency-Metadaten | **675** Dateien geprüft; **37** Referenzen in **12** Dateien relokiert |
| Linkinput-Preflight | **127** generierte Projekte, **82** vorhandene Dependency-Libraries, Release/x64 |
| Inputmanifest | **40909** Dateien erfasst, **0** instabile Dateien übersprungen |
| Artefakt | **12360594342**, **264.362.107 Bytes** |
| Artefakt-SHA-256 | `c2e28e59dba400e6414b208983f50567020dbc37e1a01ff3ae8d446309f874bc` |

Der Run begann um **15:15:00 UTC**; die API meldet den abgeschlossenen Stand
mit Aktualisierungszeit **16:42:08 UTC**. Beide Jobs und die beiden Windows-
Regressionsskripte für Inputtimestamps sowie Relokation/Linkprüfung sind erfolgreich.
Der Quellstand enthält den F01-Nachholfall beim erneuten Aktivieren des
automatischen Filamentabgleichs.

## Was tatsächlich aus dem Cache übernommen wurde

**Kein Dependency- oder Anwendungscache wurde restauriert.** Das Log meldet
für beide Schlüssel einen Miss und anschließend das fehlende Inputmanifest.
Der bisherige erfolgreiche Run **39520066087** lief auf Imageversion
`20261018.275.1`; dieser Run verwendet `20261007.264.1`, jeweils
`windows-2025-vs2026`. Die Imageversion gehört ausdrücklich zum Toolchain-
Fingerprint. Bereits dieser Unterschied trennt die Cachefamilien; daraus
wird keine weitergehende Behauptung über einzeln geänderte Compilerdateien abgeleitet.

Der Dependency-Quell-/Restorehelper-Hash blieb
`3595b199d56ad7087d9a71befdadd9034cdb4b30f4971d7f1a7b08958733e529`.
Dependencies wurden erneut aus dem geprüften offiziellen Archiv bereitgestellt.
Die Anwendung wurde vollständig neu gebaut. **Beide neuen Cache-Saves sind
ausdrücklich im Log bestätigt.** Dieser konkrete Run ist daher kein Nachweis
für einen durch Cache-Wiederverwendung beschleunigten Anwendungsbuild.

## Kurze authentische Logauszüge

Die folgenden Zeilen stammen aus dem abgeschlossenen Windows-Job. Nur der
absolute CI-Buildpfad in der Manifestzeile wurde durch `$BUILD_DIR` ersetzt.
Es werden keine Rohlogs oder persönlichen Profil-/Kontodaten abgelegt.

```text
2026-10-21T15:15:44.6034992Z Version: 20261007.264.1
2026-10-21T15:16:58.0242983Z Cache not found for input keys: prefect-deps-v2-324be78aaec996b432a5d59559d185e65e23927634ded451d55d12b01a80d516-3595b199d56ad7087d9a71befdadd9034cdb4b30f4971d7f1a7b08958733e529
2026-10-21T15:17:59.4644154Z Dependency metadata verified: 675 files; 37 references relocated in 12 files.
2026-10-21T15:18:11.6868432Z Cache saved with key: prefect-deps-v2-324be78aaec996b432a5d59559d185e65e23927634ded451d55d12b01a80d516-3595b199d56ad7087d9a71befdadd9034cdb4b30f4971d7f1a7b08958733e529
2026-10-21T15:18:13.7598364Z Cache not found for input keys: prefect-app-v1-58c9e50c2df2807fce770eaa588463cd6ad44960a16a97faeb11c53817db6937-4b5c3546c7fba94439d9bb0fe69553723b895897-39623913865-1, prefect-app-v1-58c9e50c2df2807fce770eaa588463cd6ad44960a16a97faeb11c53817db6937-4b5c3546c7fba94439d9bb0fe69553723b895897-, prefect-app-v1-58c9e50c2df2807fce770eaa588463cd6ad44960a16a97faeb11c53817db6937-
2026-10-21T15:18:14.5067408Z No build input manifest; inputs retain checkout timestamps.
2026-10-21T15:19:26.5297620Z Dependency link preflight passed: 127 projects, 0 response files, 82 dependency libraries (Release|x64).
2026-10-21T16:37:33.1213818Z Captured 40909 hashed Git/dependency inputs; unstable files skipped 0. Manifest: $BUILD_DIR/.prefect-build-inputs.json
2026-10-21T16:42:00.2390190Z Cache saved with key: prefect-app-v1-58c9e50c2df2807fce770eaa588463cd6ad44960a16a97faeb11c53817db6937-4b5c3546c7fba94439d9bb0fe69553723b895897-39623913865-1
```

Früherer erfolgreicher Run, unveränderte Imagezeilen:

```text
2026-10-21T00:14:39.0947043Z Image: windows-2025-vs2026
2026-10-21T00:14:39.0947777Z Version: 20261018.275.1
```

## Grenze dieses Nachweises

Dieser CI-Nachweis belegt den vollständigen Build. Die inzwischen geprüfte
lokale Standaloneinstallation und der tatsächliche Programmstart stehen im
[separaten Laufzeitbericht](local-windows-runtime.md). Die interaktive Abnahme
aller Bedien- und Hardwarefälle ist nicht vollständig belegt; die konkreten
Grenzen sind dort und in [VALIDATION.md](../VALIDATION.md) aufgeführt.

