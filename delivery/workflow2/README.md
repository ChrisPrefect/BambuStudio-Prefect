# Workflow 2 release pipeline

Reviewed release pipeline for Workflow 2. `delivery/workflow2/release.json` pins
the actual frozen source, build run, Windows artifact, patch ZIP and reviewed notes.
Every required pin must be filled before execution; missing or placeholder values
are rejected before token access or network. `publish: false` prepares a verified
draft; changing it to `true` explicitly enables publication of that same draft.

## Files to deliver to the existing `delivery/windows` branch

- `.github/workflows/prefect-workflow2-release.yml`
- `delivery/workflow2/release.py`
- `delivery/workflow2/test_release.py`
- `delivery/workflow2/release.json`
- `delivery/workflow2/release-notes.md`
- The final patch ZIP named by `patch_file`, copied into `delivery/workflow2`.

The new workflow triggers only for those new paths. It does not change or trigger
the old `delivery/windows/**` publisher or `delivery/finalization/**` finalizer.
The only permissions are `contents: write` and `actions: read`, for the existing
repository and delivery branch, with persisted checkout credentials disabled.

## Root integration

1. Freeze source on `prefect/workflow`. Fill exact `source_commit`, `source_tree`
   and the ID of its own `.github/workflows/prefect-workflow.yml` push run.
2. After that run creates the unique Windows artifact, pin its numeric ID,
   `size_in_bytes` and digest (without `sha256:`) as `artifact_id`, `artifact_size`
   and `artifact_sha256`. The script still waits if the pinned run is running;
   it requires its successful completion before any tag/release writes.
3. Export/replay the complete final patch series. Copy its ZIP beside the script.
   Fill exact basename, byte size, SHA-256 and number of `.patch` files.
4. Review `release-notes.md`, including its honest GUI/hardware test limits.
   Pin SHA-256 of its UTF-8 text with LF newlines as `notes_sha256`.
5. Keep `publish: false` for staging. Run the tests below, then root may push only
   the new paths to `delivery/windows`. The workflow creates the new lightweight
   tag `v02.08.02.61-prefect.2` at the frozen commit, a new draft, and its three
   verified assets. The proof artifact records its release ID and draft URL.
6. After root has inspected the local GUI and draft assets, change only
   `publish` to `true` and push the config. It rechecks every pin, downloads and
   hashes all three remote assets again, then publishes the same draft as a
   prerelease. Its public canonical URL ends with `/releases/tag/` plus the tag.

Do not edit notes or inputs after staging. If they differ, execution stops without
repairing or replacing the release; a changed frozen source requires a deliberately
reviewed new release procedure. No `DELETE`, tag PATCH, asset replacement, draft
note update or unpublish operation exists. The old Workflow 1 release ID is also
explicitly forbidden. Published identical reruns perform no writes; published
mismatches fail. Draft retries upload only missing assets, after checking all
existing metadata and downloaded payload hashes before any mutation.

The Windows artifact is pinned by metadata, actual archive SHA/size, every ZIP
CRC, a unique source marker and unique exe/DLL. The patch archive is pinned by
SHA/size/count, upstream base, replay success, final source/tree and every
format-patch payload hash. All guards use explicit exceptions, including under
`python -O`; tests run in both ordinary and optimized Python locally.

## Network-free tests

From the pipeline root:

```text
python -m unittest discover -s delivery/workflow2 -p "test_*.py" -v
python -O -m unittest discover -s delivery/workflow2 -p "test_*.py" -v
```

Tests cover stage-only creation, explicit publication, no-write retries, protected
old release IDs, source/run/artifact provenance, mismatching existing tags/releases/
assets, corrupt existing payloads before missing-asset uploads, config placeholders,
the marker, patch replay pins, stale delivery commits and ZIP path collisions.

`workflow2-release-verification.json` is emitted only after fresh release/tag and
complete asset checks. It contains public provenance, never credentials or local
printer/profile data. The Actions artifact retains it for 90 days.
