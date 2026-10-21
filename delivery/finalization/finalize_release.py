"""Publish only the already verified, pinned Prefect draft. No tag/asset writes."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone

REPOSITORY = "ChrisPrefect/BambuStudio-Prefect"
REPOSITORY_ID = 1427616802
BRANCH = "delivery/windows"
SOURCE = "4b5c3546c7fba94439d9bb0fe69553723b895897"
TREE = "418524ef74e1e2d49ec1cf9d3fa6e422df072afc"
SOURCE_RUN = 39623913865
PUBLISHER_RUN = 39625168492
PUBLISHER_SOURCE = "bef61af9d7ac6d4a7ef74a1613f3c8d97e447e0f"
RELEASE_ID = 418968348
TAG = "v02.08.02.61-prefect.1"
TITLE = "Bambu Studio Prefect 2.8.2.61 – Workflow 1"
PREFIX = f"repos/{REPOSITORY}/"
RELEASE_PATH = f"{PREFIX}releases/{RELEASE_ID}"
ASSETS = (
    {"id": 663154498, "name": "BambuStudio-Prefect-2.8.2.61-Windows-x64.zip",
     "size": 264362107, "sha256": "c2e28e59dba400e6414b208983f50567020dbc37e1a01ff3ae8d446309f874bc"},
    {"id": 663155136, "name": "BambuStudio-Prefect-patches-20261021.zip",
     "size": 470661, "sha256": "7c5207922f3eec258eb8dfc1595644fc55501f10a69e10334ca770c52ff48025"},
    {"id": 663155220, "name": "SHA256SUMS.txt", "size": 218,
     "sha256": "6c4112a32483767a770e4b0e783761b5ebfb33566fe23b6e0240c17a2d6c6eb3"},
)
CHECKSUMS = "".join(f"{a['sha256']}  {a['name']}\n" for a in ASSETS[:2]).encode("ascii")
# Pinned separately from the build: these notes disclose the outstanding GUI/hardware limits.
BODY_SHA256 = "57af5a1d00b3c5f14b48271fb7fed83b8d2fed393d62209f9546ac09145cf257"
CANONICAL_RELEASE = f"https://github.com/{REPOSITORY}/releases/tag/{TAG}"


class VerificationError(RuntimeError):
    pass


def require(condition, message):
    # Deliberately not `assert`: all guards must remain active with python -O.
    if not condition:
        raise VerificationError(message)


class GithubAPI:
    """gh handles authentication; this adapter exposes only reads and one fixed PATCH."""

    def _run(self, path, *, payload=None, binary=False):
        require(path.startswith(PREFIX), "API path is outside the pinned repository")
        command = ["gh", "api", "--hostname", "github.com", "--method",
                   "PATCH" if payload is not None else "GET", path,
                   "-H", "X-GitHub-Api-Version: 2022-11-28",
                   "-H", "Accept: application/octet-stream" if binary else "Accept: application/vnd.github+json"]
        data = None
        if payload is not None:
            require(path == RELEASE_PATH and not binary, "Only the pinned release may be updated")
            require(set(payload) == {"tag_name", "target_commitish", "name", "body", "draft", "prerelease"},
                    "Unexpected release update fields")
            require(payload["tag_name"] == TAG and payload["target_commitish"] == SOURCE
                    and payload["name"] == TITLE and payload["draft"] is False
                    and payload["prerelease"] is True, "Release update target does not match pins")
            require(hashlib.sha256(payload["body"].encode("utf-8")).hexdigest() == BODY_SHA256,
                    "Release update body does not match its pin")
            command += ["--input", "-"]
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        result = subprocess.run(command, input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                check=False, timeout=120)
        # Do not echo command inputs, environment, or raw server errors into public artifacts.
        require(result.returncode == 0, f"GitHub API {('PATCH' if payload is not None else 'GET')} failed")
        if binary:
            return result.stdout
        try:
            return json.loads(result.stdout)
        except (ValueError, UnicodeDecodeError) as exc:
            raise VerificationError("GitHub returned invalid JSON") from exc

    def get(self, path):
        return self._run(path)

    def get_bytes(self, path):
        return self._run(path, binary=True)

    def patch_release(self, payload):
        return self._run(RELEASE_PATH, payload=payload)


def verify_environment(env):
    require(env.get("GITHUB_REPOSITORY") == REPOSITORY, "Wrong repository")
    require(env.get("GITHUB_REF") == f"refs/heads/{BRANCH}", "Wrong branch")
    require(env.get("GITHUB_EVENT_NAME") == "push", "Only a branch push can finalize")
    require(env.get("GITHUB_WORKFLOW_REF") ==
            f"{REPOSITORY}/.github/workflows/prefect-finalize.yml@refs/heads/{BRANCH}",
            "Wrong workflow ref")
    require(re.fullmatch(r"[0-9a-f]{40}", env.get("GITHUB_SHA", "")) is not None,
            "Missing workflow commit")


def verify_ref(api, ref, expected_sha):
    data = api.get(f"{PREFIX}git/ref/{ref}")
    require(data.get("ref") == f"refs/{ref}", f"Wrong {ref} ref")
    require(data.get("object", {}).get("type") == "commit"
            and data["object"].get("sha") == expected_sha, f"Wrong {ref} commit")


def verify_run(api, run_id, source, branch, workflow):
    run = api.get(f"{PREFIX}actions/runs/{run_id}")
    require(run.get("id") == run_id and run.get("status") == "completed"
            and run.get("conclusion") == "success", f"Run {run_id} has not succeeded")
    require(run.get("head_sha") == source and run.get("head_branch") == branch
            and run.get("path") == workflow and run.get("event") == "push", f"Run {run_id} source mismatch")
    for field in ("repository", "head_repository"):
        require(run.get(field, {}).get("full_name") == REPOSITORY
                and run[field].get("id") == REPOSITORY_ID, f"Run {run_id} repository mismatch")
    if run_id == SOURCE_RUN:
        require(run.get("head_commit", {}).get("tree_id") == TREE, "Source run tree mismatch")


def verify_provenance(api, env):
    verify_ref(api, f"heads/{BRANCH}", env["GITHUB_SHA"])
    commit = api.get(f"{PREFIX}git/commits/{SOURCE}")
    require(commit.get("sha") == SOURCE and commit.get("tree", {}).get("sha") == TREE,
            "Source commit/tree mismatch")
    verify_run(api, SOURCE_RUN, SOURCE, "prefect/workflow", ".github/workflows/prefect-workflow.yml")
    verify_run(api, PUBLISHER_RUN, PUBLISHER_SOURCE, BRANCH, ".github/workflows/prefect-publish.yml")
    data = api.get(f"{PREFIX}actions/runs/{SOURCE_RUN}/artifacts?per_page=100")
    require(data.get("total_count") == 1 and len(data.get("artifacts", [])) == 1,
            "Unexpected source artifact set")
    artifact = data["artifacts"][0]
    require(artifact.get("id") == 12360594342
            and artifact.get("name") == f"BambuStudio-Prefect-Windows-x64-{SOURCE}"
            and artifact.get("size_in_bytes") == ASSETS[0]["size"]
            and artifact.get("digest") == f"sha256:{ASSETS[0]['sha256']}"
            and artifact.get("expired") is False, "Source artifact mismatch")
    run = artifact.get("workflow_run", {})
    require(run.get("id") == SOURCE_RUN and run.get("head_sha") == SOURCE
            and run.get("repository_id") == REPOSITORY_ID
            and run.get("head_repository_id") == REPOSITORY_ID
            and run.get("head_branch") == "prefect/workflow", "Source artifact provenance mismatch")
    verify_ref(api, f"tags/{TAG}", SOURCE)


def verify_assets(release, *, public=False):
    assets = release.get("assets", [])
    require(len(assets) == len(ASSETS), "Release must contain exactly the three verified assets")
    require(len({a.get("id") for a in assets}) == len(ASSETS), "Duplicate release asset IDs")
    by_id = {a["id"]: a for a in assets}
    for expected in ASSETS:
        actual = by_id.get(expected["id"], {})
        require(actual.get("name") == expected["name"] and actual.get("size") == expected["size"]
                and actual.get("state") == "uploaded"
                and actual.get("digest") == f"sha256:{expected['sha256']}",
                f"Release asset mismatch: {expected['name']}")
        if public:
            require(actual.get("browser_download_url") ==
                    f"https://github.com/{REPOSITORY}/releases/download/{TAG}/{expected['name']}",
                    f"Release asset URL mismatch: {expected['name']}")


def verify_release(release, body, *, public=False):
    require(release.get("id") == RELEASE_ID and release.get("tag_name") == TAG
            and release.get("target_commitish") == SOURCE and release.get("name") == TITLE
            and release.get("prerelease") is True, "Release identity/source mismatch")
    require(type(release.get("draft")) is bool, "Invalid release draft flag")
    verify_assets(release, public=public)
    if public:
        require(release["draft"] is False and release.get("body") == body,
                "Published release body or draft flag mismatch")
        require(release.get("html_url") == CANONICAL_RELEASE and bool(release.get("published_at")),
                "Published release URL/timestamp mismatch")


def finalize(api, env, body, *, read_only=False):
    verify_environment(env)
    require(hashlib.sha256(body.encode("utf-8")).hexdigest() == BODY_SHA256,
            "Release notes differ from the reviewed pinned body")
    verify_provenance(api, env)
    release = api.get(RELEASE_PATH)
    verify_release(release, body)
    actual_checksums = api.get_bytes(f"{PREFIX}releases/assets/{ASSETS[2]['id']}")
    require(actual_checksums == CHECKSUMS and len(actual_checksums) == ASSETS[2]["size"]
            and hashlib.sha256(actual_checksums).hexdigest() == ASSETS[2]["sha256"],
            "Downloaded SHA256SUMS content mismatch")
    already_published = release["draft"] is False
    if already_published:
        # Never silently edit a release that somebody has already published differently.
        verify_release(release, body, public=True)
    elif not read_only:
        # Fresh guards immediately before the only possible mutation.
        verify_ref(api, f"heads/{BRANCH}", env["GITHUB_SHA"])
        verify_ref(api, f"tags/{TAG}", SOURCE)
        release = api.get(RELEASE_PATH)
        verify_release(release, body)
        require(release["draft"] is True, "Release changed during finalization; refusing to edit it")
        response = api.patch_release({"tag_name": TAG, "target_commitish": SOURCE, "name": TITLE,
                                      "body": body, "draft": False, "prerelease": True})
        verify_release(response, body, public=True)
    if not read_only or already_published:
        # The final report is emitted only after a fresh public GET and tag check.
        release = api.get(RELEASE_PATH)
        verify_release(release, body, public=True)
        verify_ref(api, f"tags/{TAG}", SOURCE)
    report = {
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "state": "verified-draft-read-only" if read_only and not already_published else "published",
        "already_published": already_published, "repository": REPOSITORY, "release_id": RELEASE_ID,
        "source_commit": SOURCE, "source_tree": TREE, "tag": TAG, "source_run": SOURCE_RUN,
        "publisher_run": PUBLISHER_RUN, "finalizer_commit": env["GITHUB_SHA"],
        "release_notes_sha256": BODY_SHA256,
        "html_url": release.get("html_url"),
        "assets": [dict(a, download_url=f"https://github.com/{REPOSITORY}/releases/download/{TAG}/{a['name']}")
                   for a in ASSETS],
    }
    # Read-only reports retain the actual draft URL; proposed download URLs are marked as such.
    if report["state"] == "verified-draft-read-only":
        report["download_urls_pending_publication"] = True
    return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only", action="store_true", help="Validate every precondition without publishing")
    parser.add_argument("--report", type=Path, default=Path("final-release-verification.json"))
    args = parser.parse_args()
    body = Path(__file__).with_name("release-notes.md").read_text(encoding="utf-8")
    report = finalize(GithubAPI(), os.environ, body, read_only=args.read_only)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"state": report["state"], "html_url": report["html_url"],
                      "source_commit": SOURCE, "report": str(args.report)}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (VerificationError, subprocess.TimeoutExpired) as exc:
        print(f"Finalization stopped: {exc}", file=sys.stderr)
        sys.exit(1)
