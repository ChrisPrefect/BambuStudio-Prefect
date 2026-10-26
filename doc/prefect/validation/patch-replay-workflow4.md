# Nachweis der Feature-Patchserie

Basis: `926a7192574bcb9b3a732e1ec59a46d79cb45466`
Fork-Head: `727a703155237a94e4fcc31ebc4effef515d13f0`
Vergleichs-Tree: `16cbb874d6bef7ebbc3453e407451eb9af252b0e`

Alle **37 Commits** wurden zweimal in einen externen privaten `GIT_INDEX_FILE` eingespielt:
zuerst als bytegenaue rohe Git-Diffs (`--binary --full-index`), danach als die
tatsächlich ausgelieferten nummerierten Format-Patch-Dateien.
Jede Stufe wurde mit `git apply --cached` angewendet. Nach jeder Stufe stimmt
`git write-tree --missing-ok` exakt mit dem ursprünglichen Commit-Tree überein.

Endergebnis beider Durchläufe: `16cbb874d6bef7ebbc3453e407451eb9af252b0e` — **identisch**.
Der normale Repository-Index blieb nach SHA-256-Vergleich unverändert.
Keine Arbeitsdatei wurde verändert oder ausgecheckt.

Unveränderte Baseline-Blobs dürfen im Partial Clone fehlen; deren bekannte
Objekt-IDs bleiben unverändert. `GIT_NO_LAZY_FETCH=1` verhindert Downloads.
Geänderte Inhalte werden aus den Patches vollständig neu gehasht.

`replay-manifest.json` enthält pro Commit die Tree-IDs, Patch-/Diff-SHA-256,
Exitcodes und die tatsächlich ausgeführten Git-Kommandos.
`replay-diffs/` enthält die rohen angewendeten Diffs. Die beim Prüfen erzeugten
privaten Git-Objekte werden nicht mitgeliefert. Die nummerierten `.patch` sind die Serie.

Dieser Nachweis belegt die vollständige Rekonstruktion des Quellbaums auf
der festgelegten Basis. Er belegt keine konfliktfreie Anwendung auf einem
unbekannten zukünftigen Upstream und ersetzt keinen GUI-Build.

## Wiederholen

`export_and_replay_patches.py` benötigt Python 3 und Git. Parameter:
`--repo`, `--output` (neu/leeres Verzeichnis), `--base`, `--head`,
`--expected-tree`, optional `--git`. Das Skript verändert weder normale
Repository-Indizes noch Arbeitsdateien.
