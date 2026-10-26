# Isolated Workflow 3 (.5) delivery preparation

Only `.github/workflows/prefect-workflow3-release.yml` and `delivery/workflow3-release/**` belong on `delivery/windows`. No old delivery path is edited. The only target tag is `v02.08.02.61-prefect.5`. Releases .1/.2/.3/.4 (418968348, 422086779, 423441312, 423604332) are protected.

Source 939e0b3ce6dce937502666f334950eec2e0f542a, tree e397ecc3b38d7a22b6ac4891d0897dfc273d7000 and run 40248952898 are frozen. The corrected 35-commit / 70-tree patch archive is bound to its freshly verified bytes. Artifact 12619554874 is bound to 264429447 freshly hashed bytes, exact source marker, 6756 CRC-checked files, EXE/DLL hashes and embedded/runtime branding. Production rechecks successful full CI before staging. Incomplete production inputs fail before token access, network, temporary files or writes. Synthetic fallback source pins exist only inside unittest mock scopes. `publish` remains false; no publication is authorized by this preparation.

Preserved guards: exact repository/branch/workflow event and fresh branch head, frozen source/tree/build, artifact provenance, full ZIP/CRC/hash validation, replayed patch manifest/payload verification, exact embedded/runtime icon and EXE branding, exactly three expected assets and freshly downloaded remote payload checks. Draft creation and later one-flag publication are separate steps. No deletion, replacement, force ref update, old-release edit or unpublish route exists.

Run both network-free suites: `python -B -m unittest discover -s delivery/workflow3-release -p "test_*.py" -v`, then with `-O`. PE tests parse bytes; they never execute the app.

`build-upload-manifest.py --base-commit FULL_SHA --base-tree FULL_SHA` creates byte-exact local GitData metadata. `read_file_chunk.py LOCAL_PATH OFFSET LENGTH` returns one bounded base64 chunk from this directory only. No helper pushes or mutates GitHub. Local paths in upload manifests are private workstation metadata, not public reports.
