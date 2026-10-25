# Patch-Rekonstruktion für den Taskleisten-Nachtrag

Die aktuelle Serie enthält **31 Commits** bis `3cb50caedececb98a21d2792f41c044ee596f759`,
Tree `ca2cd51f1d335f7c5172bad8152b1b727cc0f2fe`. Nach Roots unabhängiger Rekonstruktion
stimmen alle **62 Zwischenstände** aus Rohdiff- und Format-Patch-Replay mit den
Originaltrees überein. Die Archivbytes wurden während der Dokumentvorbereitung
zusätzlich lokal gelesen und gehasht.

- Basis: `v02.08.02.61`, Commit `926a7192574bcb9b3a732e1ec59a46d79cb45466`.
- Archiv: `Prefect-BambuStudio-patches-20261025-taskbar-v5.zip`.
- Größe: **1.114.689 Byte**.
- SHA256: `437aa4098bd914d9894260ef264f0c70f35b13242690aab51ea1fd94d865d142`.

[Maschinenlesbarer Überblick](patch-replay-taskbar-v5.json). Der separate
[Replay des veröffentlichten Brandingpakets .3](patch-replay-branding.md)
bleibt mit seinen damaligen 28 Commits und 56 Prüfungen unverändert. Ein
identischer Replay auf der bekannten Basis ersetzt keinen Test gegen einen
anderen zukünftigen Upstreamstand.
