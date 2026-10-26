# Isolated Workflow 4 (.6) delivery preparation

Only `.github/workflows/prefect-workflow4-release.yml` and
`delivery/workflow4-release/**` are new on `delivery/windows`. The only target
tag is `v02.08.02.61-prefect.6`. Old releases .1–.5 are protected by exact IDs:
418968348, 422086779, 423441312, 423604332, 423757668.

Source 727a703155237a94e4fcc31ebc4effef515d13f0, tree
16cbb874d6bef7ebbc3453e407451eb9af252b0e and CI run 40414286154 are bound.
The actual Windows artifact 12695023513 is bound to 264440555 verified bytes,
SHA256 add72a5bfc23845c5aee6909d95686d99ec538d26d2f455d16110f4f5b52af73.
The new 37-commit/74-tree patch archive is bound to 1777625 bytes and SHA256
914b68c8e572d4050e6837610ddad19862e28b1a1a40a41a8f3fd625583707bb.
Notes and icon bytes are pinned. publish=false. Production independently
requires the complete successful source CI before any release staging write.
Incomplete inputs fail before token access, network, temporary files or writes.
Synthetic test pins exist only inside unittest mock scopes. No .5 archive was
copied or reused as a new package. Local preparation performs no remote action.

Preserved guards include exact repository/branch/workflow/event and fresh branch
head; source/tree/build/artifact provenance; full ZIP/CRC/SHA; raw/mail patch
replay identities and payload hashes; exact PE/icon bytes; exactly three assets;
authenticated full remote-asset re-downloads before publication; and separate
draft staging versus one-flag publication. No deletion, replacement, force-ref,
old-release editing or unpublish route is implemented.

Network-free tests: python -B -m unittest discover -s delivery/workflow4-release
-p "test_*.py" -v; repeat with -O. PE tests parse bytes without running an app.
The local upload-manifest/chunk/publication-flag helpers do not push to GitHub.
Private helper manifests retain local paths; public evidence must be sanitized.
