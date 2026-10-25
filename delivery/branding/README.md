# Prefect Bambu Studio Branding release (.3)

Reviewed release mechanism, copied from the real Workflow 2 stage/publication and
isolated under `delivery/branding/**` and `prefect-branding-release.yml`.
`release.json` binds the actual frozen source, build run, artifact, replayed patch
ZIP, source ICO and reviewed notes. Every required pin must be filled; missing or
placeholder pins fail before token access or network. `publish: false` prepares a
verified draft; changing it to `true` enables publication of that same draft.

Upload the workflow and `delivery/branding` files only to `delivery/windows` after
root supplies frozen pins. This README maps to `delivery/branding/README.md`, never
the repository's main README. The helper and test files `pe_branding.py` and
`test_pe_branding.py`, plus the final pinned ICO, must accompany `release.py`.
The new workflow path filters do not trigger the older Workflow 1/2 pipelines.

## Stage, then publish

1. Freeze source commit/tree and its own `prefect-workflow.yml` push run.
2. Pin the unique completed Windows artifact's ID, byte size and SHA-256.
3. Copy the replayed patch ZIP into `delivery/branding`; pin basename, byte size,
   SHA-256 and actual `.patch` count. It must reconstruct the frozen source/tree.
4. Copy the final source ICO into `delivery/branding/PrefectBambuStudio.ico`;
   pin its actual byte size/SHA-256. The installed archive's
   `resources/images/BambuStudio.ico` must contain identical bytes.
5. Review/pin the UTF-8 LF release notes. Keep `publish: false` while preparing
   the draft. Run the local tests, then push only the new delivery paths.
6. The new lightweight tag `v02.08.02.61-prefect.3` is created only at the frozen
   source. The draft contains exactly Windows ZIP, patch ZIP and `SHA256SUMS.txt`.
7. After actual local name/title/icon/shortcut acceptance, change only `publish`
   to `true`. Recheck the verified draft, then publish the same prerelease.

Existing releases/tags/assets for `.1` (ID 418968348) and `.2` (ID 422086779) are
protected. No ref PATCH, tag force update, asset deletion/replacement, release-note
edit or unpublish operation exists. Identical retries are idempotent; mismatching
existing objects fail without being repaired or clobbered.

## Actual Windows resources and cache behavior

`src/platform/msw/BambuStudio.rc.in` becomes the generated `BambuStudio.rc` and is
compiled into the GUI shim `bambu-studio.exe`. Its version resource ID 1 contains
`ProductName`/`FileDescription`; group icon ID 2 points to RT_ICON image payloads.
The large `BambuStudio.dll` contains the GUI implementation and has no corresponding
version resource in the existing Workflow 2 package. Runtime images are separately
installed below `resources/`; changing only a shortcut cannot update either the
EXE metadata or its embedded icon.

The release verifier parses PE resources as data using only Python's standard
library. It does not load or execute the EXE. It requires both display-name version
strings to equal `Prefect Bambu Studio`, verifies every embedded icon frame against
the pinned ICO, and checks the runtime ICO bytes. A parser integration check against
the actual existing Workflow 2 EXE found the previous `BambuStudio` strings and its
one 154×154 embedded frame; that proves parser behavior, not new branding acceptance.
New source bytes must pass these checks after the new build exists.

The existing build cache already checks generator, compiler/SDK, image version,
compiler/CMake hashes, workspace, architecture, CMake-list inputs and build flags.
Pure C++/RC/icon edits can reuse compatible objects; changing a `CMakeLists.txt`
changes the app cache family. `SOURCE_DATE_EPOCH` follows the latest app-source
commit, so a version/display constant change may invalidate generated version/PCH
inputs correctly. No cache safety guard is weakened. The next run's actual image
and cache hit/miss must be observed; old success never proves a new hit.

The source workflow also repairs the cached `device_page.stamp` when its generated
source-tree outputs are missing, invokes upstream's `device_page_build` target,
and verifies the complete installed DeviceWeb bundle before uploading. A successful
native build alone previously omitted that uncached bundle. The first ac0 branding
artifact was rejected locally for this defect; release `.3` requires the repaired
source/run and new actual artifact and replay pins. No rejected package is staged.

## Verification

```text
python -m unittest discover -s delivery/branding -p "test_*.py" -v
python -O -m unittest discover -s delivery/branding -p "test_*.py" -v
```

Tests cover provenance, source/ZIP/patch/notes/icon pins, Stage→Publish, protected
older releases, endpoint-specific download headers, status-only errors, no-write
mismatch guards, exact PE strings/icon frames and bounded malformed-resource reads.
The real Win32 layouts are described by Microsoft's
[PE specification](https://learn.microsoft.com/windows/win32/debug/pe-format) and
[version StringFileInfo specification](https://learn.microsoft.com/windows/win32/menurc/stringfileinfo).
