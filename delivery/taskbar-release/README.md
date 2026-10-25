# Isolated Taskbar .4 release delivery

This package derives from the reviewed Branding .3 staging/publication pipeline.
Only `.github/workflows/prefect-taskbar-release.yml` and `delivery/taskbar-release/**`
belong on the `delivery/windows` branch. The separate path filter does not trigger
the older release workflows. No source checkout/index/branch is edited here.

The source commit/tree/build run are fixed in code and config. The patch ZIP is the
31-commit / 62-exact-tree package, and the icon matches the frozen source. Actual
artifact ID/size/SHA are bound to the parent's fresh GitHub artifact evidence.
The parent's actual download/local-runtime acceptance remains separate. All
placeholders fail before token access, network, or writes. `publish` is false.

The target is only `v02.08.02.61-prefect.4`. Releases .1/.2/.3 (418968348,
422086779, 423441312) are protected. There are no tag updates, ref force writes,
asset replacements/deletions, existing-note edits, or unpublish operations.
Matching retries are idempotent; mismatches fail without repair or overwrite.

Original safeguards remain: exact repository/branch/workflow event and fresh branch
head; source commit/tree; successful own CI/run/artifact provenance; complete ZIP
CRC and hashes; replayed patch manifest and payloads; exact runtime and embedded PE
icon/version strings; exactly three expected assets; fresh remote payload download
and hashing before publication. Staging creates a verified draft. Publication of
that same draft requires an explicit later change to `publish: true`.

The notes explain the opt-in QA entry, foreground F8/menu intent, deferred CallAfter
preflight/request, InputSync error, and version metadata epoch. They claim no OS-pin
success. Local installation, shortcut operations, app starts, pin requests and
profile access are outside this pipeline.

Run both network-free suites from this local directory:
`python -B -m unittest discover -s delivery/taskbar-release -p "test_*.py" -v`
and the same command with `-O`. PE checks parse bytes; they never execute the EXE.
The new source-binding and all three protected release IDs are covered explicitly.
