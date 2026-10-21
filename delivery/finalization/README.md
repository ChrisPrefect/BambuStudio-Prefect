# Pinned release finalization

This is a single-release finalizer, not a general release uploader. It can only update release **418968348** in **ChrisPrefect/BambuStudio-Prefect**. It has no implementation for creating/deleting assets, releases, tags, or refs.

The workflow runs only after a push to `delivery/windows` that changes its own workflow file or `delivery/finalization/**`. These paths do not overlap the asset preparation workflow's `delivery/windows/**` filter.

Before the only possible mutation it verifies the current delivery branch commit, repository and workflow environment; source commit/tree; successful source and asset-preparation runs; exact source artifact; existing lightweight tag; release identity; the exact three asset IDs/names/sizes/SHA-256 digests/states; and the downloaded exact 218-byte checksum file. The release-notes SHA-256 is independently pinned. A second branch/tag/release read immediately precedes the PATCH.

The PATCH addresses the fixed release ID, keeps the existing tag and source commit, supplies the reviewed notes, sets `draft=false` and retains `prerelease=true`. The response and a fresh GET must contain the expected public canonical release/download URLs, unchanged asset digests, source, body and existing tag. Only then is `final-release-verification.json` produced. It contains no credentials.

An already published exact match is accepted without a write. An already published mismatch fails without editing it. A failed precondition never attempts publication. A changed release after the final preflight also fails without editing it. A failure after GitHub accepted publication can leave the release published; a repeat accepts it only if all public fields and digests match.

## Validation

From the repository root:

```text
python3 -m unittest discover -s delivery/finalization -p 'test_*.py' -v
python3 -O -m unittest discover -s delivery/finalization -p 'test_*.py' -v
```

The tests use an in-memory API and no credentials/network. They cover draft publication; public idempotence; read-only validation; incorrect asset identity/size/digest/state; extra/duplicate assets; wrong/annotated tags; failed/wrong source runs and artifacts; wrong environment/stale delivery commit; changed notes/checksum bytes; published mismatches; post-PATCH corruption; and transport write restrictions.

The script also supports `--read-only`. Actual GitHub validation requires the workflow's environment values and a `GH_TOKEN` that can read this draft and Actions metadata. Do not manufacture the workflow environment to publish from another context.

## Updating for another release

Do not reuse this finalizer unchanged. Review every constant against new successful build evidence, replace the notes and their `BODY_SHA256`, adjust fixture IDs, and run both test commands. Publishing requires a reviewed commit touching only the finalizer paths on the delivery branch. The application source and existing source tag are not changed by this workflow.
