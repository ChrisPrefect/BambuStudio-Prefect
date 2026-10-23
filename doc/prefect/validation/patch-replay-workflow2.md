# Nachweis der Feature-Patchserie

Basis: `926a7192574bcb9b3a732e1ec59a46d79cb45466`
Fork-Head: `9d4fad7292484403f0b026972835035b0a967d20`
Vergleichs-Tree: `b6feae21b1908e493d880297e901b243073585f5`

Alle **24 Commits** wurden zweimal in einen externen privaten `GIT_INDEX_FILE` eingespielt:
zuerst als bytegenaue rohe Git-Diffs (`--binary --full-index`), danach als die
tatsächlich ausgelieferten nummerierten Format-Patch-Dateien.
Jede Stufe wurde mit `git apply --cached` angewendet. Nach jeder Stufe stimmt
`git write-tree --missing-ok` exakt mit dem ursprünglichen Commit-Tree überein.

Endergebnis beider Durchläufe: `b6feae21b1908e493d880297e901b243073585f5` — **identisch**.
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
