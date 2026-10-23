"""Create only Workflow 2; stage a verified draft, then optionally publish it.

No tag updates, asset replacement/deletion, existing-release note edits, or writes
to Workflow 1 are implemented. Guards remain active under python -O.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
import time
from urllib.error import HTTPError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
import zipfile

REPO = "ChrisPrefect/BambuStudio-Prefect"
REPO_ID = 1427616802
BRANCH = "delivery/windows"
TAG = "v02.08.02.61-prefect.2"
TITLE = "Bambu Studio Prefect 2.8.2.61 – Workflow 2"
WORKFLOW = ".github/workflows/prefect-workflow2-release.yml"
SOURCE_WORKFLOW = ".github/workflows/prefect-workflow.yml"
BASE = "926a7192574bcb9b3a732e1ec59a46d79cb45466"
OLD_RELEASE_ID = 418968348
WINDOWS_NAME = "BambuStudio-Prefect-2.8.2.61-Workflow2-Windows-x64.zip"
PREFIX = f"repos/{REPO}/"
PUBLIC_URL = f"https://github.com/{REPO}/releases/tag/{TAG}"
KEYS = {"source_commit", "source_tree", "source_run_id", "artifact_id", "artifact_size",
        "artifact_sha256", "patch_file", "patch_size", "patch_sha256", "patch_count",
        "notes_sha256", "publish"}


class VerificationError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def validate_config(c):
    require(set(c) == KEYS, "Release config fields differ from the reviewed schema")
    for key in ("source_commit", "source_tree"):
        require(isinstance(c[key], str) and re.fullmatch(r"[0-9a-f]{40}", c[key])
                and len(set(c[key])) > 1, f"Unfilled or invalid {key}")
    for key in ("artifact_sha256", "patch_sha256", "notes_sha256"):
        require(isinstance(c[key], str) and re.fullmatch(r"[0-9a-f]{64}", c[key])
                and len(set(c[key])) > 1, f"Unfilled or invalid {key}")
    for key in ("source_run_id", "artifact_id", "artifact_size", "patch_size", "patch_count"):
        require(type(c[key]) is int and c[key] > 0, f"Unfilled or invalid {key}")
    require(type(c["publish"]) is bool, "publish must be a JSON boolean")
    require(isinstance(c["patch_file"], str)
            and re.fullmatch(r"BambuStudio-Prefect-[A-Za-z0-9.-]+\.zip", c["patch_file"])
            and c["patch_file"] != WINDOWS_NAME, "Unsafe or conflicting patch filename")


def verify_environment(env):
    require(env.get("GITHUB_REPOSITORY") == REPO, "Wrong repository")
    require(env.get("GITHUB_REF") == f"refs/heads/{BRANCH}", "Wrong delivery branch")
    require(env.get("GITHUB_EVENT_NAME") == "push", "Only a push may deliver Workflow 2")
    require(env.get("GITHUB_WORKFLOW_REF") == f"{REPO}/{WORKFLOW}@refs/heads/{BRANCH}",
            "Wrong workflow ref")
    require(re.fullmatch(r"[0-9a-f]{40}", env.get("GITHUB_SHA", "")), "Missing delivery commit")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        raise VerificationError("Unexpected authenticated API/upload redirect")


class GithubAPI:
    """The only writes exposed are creation of the new tag/draft/assets and publication."""
    def __init__(self, token, config):
        validate_config(config)
        require(bool(token), "Missing GitHub authorization")
        self.token, self.config = token, config
        self.bound_release_id = None
        self.opener = build_opener(NoRedirect())

    def _json(self, path, method="GET", payload=None, missing=False):
        require(path.startswith(PREFIX), "API path outside pinned repository")
        headers = {"Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github+json",
                   "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "Prefect-Workflow2-release"}
        data = None
        if payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        try:
            with self.opener.open(Request(f"https://api.github.com/{path}", data=data,
                                          method=method, headers=headers), timeout=120) as response:
                return json.load(response)
        except HTTPError as exc:
            if missing and method == "GET" and exc.code == 404:
                return None
            raise VerificationError(f"GitHub {method} failed with HTTP {exc.code}") from exc

    def get(self, path, missing=False):
        return self._json(PREFIX + path, missing=missing)

    def download(self, path, destination):
        require(path.startswith("actions/artifacts/") or path.startswith("releases/assets/"),
                "Unexpected binary download endpoint")
        # gh handles the GitHub-controlled artifact redirect. Tokens are never
        # passed as arguments or forwarded by our own cross-host redirect code.
        with Path(destination).open("wb") as output:
            result = subprocess.run(["gh", "api", "--hostname", "github.com", PREFIX + path,
                                     "-H", "Accept: application/octet-stream"], stdout=output,
                                    stderr=subprocess.PIPE, timeout=1800, check=False)
        require(result.returncode == 0, "GitHub binary download failed")

    def create_tag(self):
        return self._json(PREFIX + "git/refs", "POST",
                          {"ref": f"refs/tags/{TAG}", "sha": self.config["source_commit"]})

    def create_draft(self, body):
        require(hashlib.sha256(body.encode("utf-8")).hexdigest() == self.config["notes_sha256"],
                "Unreviewed release notes")
        return self._json(PREFIX + "releases", "POST", {
            "tag_name": TAG, "target_commitish": self.config["source_commit"],
            "name": TITLE, "body": body, "draft": True, "prerelease": True,
            "generate_release_notes": False})

    def bind_release(self, release, body):
        verify_release(release, self.config, body)
        self.bound_release_id = release["id"]

    def publish(self, release_id):
        require(self.config["publish"] is True, "Publication has not been enabled")
        require(release_id == self.bound_release_id and release_id != OLD_RELEASE_ID,
                "Only the verified Workflow 2 release can be published")
        return self._json(PREFIX + f"releases/{release_id}", "PATCH", {"draft": False})

    def upload(self, release, file):
        require(release["id"] == self.bound_release_id and release["id"] != OLD_RELEASE_ID
                and release.get("draft") is True and release.get("tag_name") == TAG,
                "Uploads require the bound Workflow 2 draft")
        base = release["upload_url"].split("{", 1)[0]
        url = urlsplit(base)
        require(url.scheme == "https" and url.netloc == "uploads.github.com"
                and url.path == f"/repos/{REPO}/releases/{release['id']}/assets"
                and not url.query and not url.fragment, "Unexpected upload endpoint")
        file = Path(file)
        require(file.name in {WINDOWS_NAME, self.config["patch_file"], "SHA256SUMS.txt"},
                "Unexpected asset filename")
        with file.open("rb") as stream:
            request = Request(base + "?" + urlencode({"name": file.name}), data=stream, method="POST",
                headers={"Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github+json",
                         "X-GitHub-Api-Version": "2022-11-28", "Content-Type": "application/octet-stream",
                         "Content-Length": str(file.stat().st_size), "User-Agent": "Prefect-Workflow2-release"})
            with self.opener.open(request, timeout=1800) as response:
                return json.load(response)


def verify_ref(data, name, source):
    require(data is not None and data.get("ref") == f"refs/{name}"
            and data.get("object", {}).get("type") == "commit"
            and data["object"].get("sha") == source, f"Unexpected ref: {name}")


def fresh_delivery_guard(api, env):
    verify_ref(api.get(f"git/ref/heads/{BRANCH}"), f"heads/{BRANCH}", env["GITHUB_SHA"])


def verify_build(api, c, *, sleep=time.sleep, monotonic=time.monotonic, wait_seconds=3.5 * 3600):
    commit = api.get(f"git/commits/{c['source_commit']}")
    require(commit.get("sha") == c["source_commit"] and commit.get("tree", {}).get("sha") == c["source_tree"],
            "Pinned source commit/tree mismatch")
    deadline = monotonic() + wait_seconds
    while True:
        run = api.get(f"actions/runs/{c['source_run_id']}")
        require(run.get("id") == c["source_run_id"] and run.get("head_sha") == c["source_commit"]
                and run.get("head_branch") == "prefect/workflow" and run.get("event") == "push"
                and run.get("path") == SOURCE_WORKFLOW
                and run.get("head_commit", {}).get("tree_id") == c["source_tree"], "Pinned build identity mismatch")
        for field in ("repository", "head_repository"):
            require(run.get(field, {}).get("full_name") == REPO and run[field].get("id") == REPO_ID,
                    "Pinned build repository mismatch")
        if run.get("status") == "completed":
            require(run.get("conclusion") == "success", "Pinned build did not succeed")
            break
        require(monotonic() < deadline, "Timed out waiting for pinned build")
        print("Waiting for the pinned Workflow 2 Windows build.", flush=True)
        sleep(30)
    result = api.get(f"actions/runs/{c['source_run_id']}/artifacts?per_page=100")
    artifacts = result.get("artifacts", [])
    require(result.get("total_count") == len(artifacts) and len(artifacts) < 100,
            "Incomplete source artifact list")
    matches = [a for a in artifacts if a.get("name") == f"BambuStudio-Prefect-Windows-x64-{c['source_commit']}"]
    require(len(matches) == 1, "Missing unique pinned Windows artifact")
    artifact = matches[0]
    require(artifact.get("id") == c["artifact_id"] and artifact.get("expired") is False
            and artifact.get("size_in_bytes") == c["artifact_size"]
            and artifact.get("digest") == f"sha256:{c['artifact_sha256']}", "Pinned artifact mismatch")
    provenance = artifact.get("workflow_run", {})
    require(provenance.get("id") == c["source_run_id"] and provenance.get("head_sha") == c["source_commit"]
            and provenance.get("head_branch") == "prefect/workflow"
            and provenance.get("repository_id") == REPO_ID and provenance.get("head_repository_id") == REPO_ID,
            "Artifact provenance mismatch")


def safe_zip(file):
    archive = zipfile.ZipFile(file)
    names = archive.namelist()
    require(len(names) == len(set(names)), "Duplicate ZIP entries")
    require(len(names) == len({n.casefold() for n in names}), "Case-colliding ZIP entries")
    for name in names:
        path = PurePosixPath(name)
        require(not path.is_absolute() and ".." not in path.parts and "\\" not in name
                and ":" not in name and not any(ord(c) < 32 for c in name), "Unsafe ZIP path")
    require(archive.testzip() is None, "ZIP CRC check failed")
    return archive


def prepare_files(api, c, root, work):
    body = (root / "release-notes.md").read_text(encoding="utf-8")
    require(hashlib.sha256(body.encode("utf-8")).hexdigest() == c["notes_sha256"], "Release notes hash mismatch")
    patch = root / c["patch_file"]
    require(patch.is_file() and not patch.is_symlink() and patch.stat().st_size == c["patch_size"]
            and sha256(patch) == c["patch_sha256"], "Patch ZIP pin mismatch")
    with safe_zip(patch) as archive:
        patches = [n for n in archive.namelist() if n.endswith(".patch")]
        require(len(patches) == c["patch_count"], "Patch count mismatch")
        manifests = [n for n in archive.namelist() if PurePosixPath(n).name == "replay-manifest.json"]
        require(len(manifests) == 1, "Missing unique patch replay manifest")
        replay = json.loads(archive.read(manifests[0]))
        require(replay.get("success") is True and replay.get("base_commit") == BASE
                and replay.get("head_commit") == c["source_commit"]
                and replay.get("expected_tree") == c["source_tree"]
                and replay.get("replayed_final_tree") == c["source_tree"]
                and replay.get("mail_replayed_final_tree") == c["source_tree"]
                and replay.get("normal_index_unchanged") is True, "Patch replay source/tree mismatch")
        entries = replay.get("format_patch", [])
        require(len(entries) == c["patch_count"] and len(replay.get("commits", [])) == c["patch_count"],
                "Replay patch/commit count mismatch")
        by_name = {PurePosixPath(n).name: n for n in patches}
        require(len(by_name) == len(patches), "Ambiguous patch basenames")
        require({e.get("file") for e in entries} == set(by_name), "Patch manifest filename mismatch")
        for entry in entries:
            data = archive.read(by_name[entry["file"]])
            require(entry.get("match") is True and entry.get("apply_exit_code") == 0
                    and entry.get("write_tree_exit_code") == 0 and entry.get("bytes") == len(data)
                    and entry.get("sha256") == hashlib.sha256(data).hexdigest(), "Patch payload verification failed")
        require(entries[-1].get("commit") == c["source_commit"]
                and entries[-1].get("replayed_tree") == c["source_tree"], "Patch series does not end at pinned source")
    portable = work / WINDOWS_NAME
    api.download(f"actions/artifacts/{c['artifact_id']}/zip", portable)
    require(portable.stat().st_size == c["artifact_size"] and sha256(portable) == c["artifact_sha256"],
            "Downloaded Windows artifact pin mismatch")
    with safe_zip(portable) as archive:
        names = archive.namelist()
        markers = [n for n in names if PurePosixPath(n).name == "PREFECT-COMMIT.txt"]
        require(len(markers) == 1 and archive.read(markers[0]).decode("utf-8-sig").strip() == c["source_commit"],
                "Windows commit marker mismatch")
        for executable in ("bambu-studio.exe", "bambustudio.dll"):
            require(sum(PurePosixPath(n).name.casefold() == executable for n in names) == 1,
                    f"Missing unique {executable}")
    checksums = work / "SHA256SUMS.txt"
    checksums.write_bytes(f"{c['artifact_sha256']}  {portable.name}\n{c['patch_sha256']}  {patch.name}\n".encode("ascii"))
    files = [portable, patch, checksums]
    expected = {f.name: {"name": f.name, "size": f.stat().st_size, "sha256": sha256(f)} for f in files}
    return body, files, expected


def release_for_tag(api):
    matches = []
    for page in range(1, 101):
        releases = api.get(f"releases?per_page=100&page={page}")
        require(isinstance(releases, list), "Invalid release list")
        matches.extend(r for r in releases if r.get("tag_name") == TAG)
        if len(releases) < 100:
            break
    else:
        raise VerificationError("Incomplete release enumeration")
    require(len(matches) <= 1, "Duplicate Workflow 2 releases")
    return matches[0] if matches else None


def verify_release(release, c, body):
    require(type(release.get("id")) is int and release["id"] > 0 and release["id"] != OLD_RELEASE_ID,
            "Protected/invalid release ID")
    require(release.get("tag_name") == TAG and release.get("target_commitish") == c["source_commit"]
            and release.get("name") == TITLE and release.get("body") == body
            and release.get("prerelease") is True and type(release.get("draft")) is bool,
            "Existing release identity/notes mismatch; refusing to change it")
    require(release.get("url") == f"https://api.github.com/repos/{REPO}/releases/{release['id']}",
            "Unexpected release API URL")
    if release["draft"] is False:
        require(release.get("html_url") == PUBLIC_URL and bool(release.get("published_at")),
                "Published release URL/timestamp mismatch")


def verify_assets(release, expected, *, complete=False):
    assets = release.get("assets", [])
    names = [a.get("name") for a in assets]
    require(len(names) == len(set(names)) and len(assets) == len({a.get("id") for a in assets}),
            "Duplicate release assets")
    require(set(names) <= set(expected), "Unexpected release asset; refusing any mutation")
    if complete:
        require(set(names) == set(expected), "Missing release asset")
    for asset in assets:
        e = expected[asset["name"]]
        require(type(asset.get("id")) is int and asset["id"] > 0 and asset.get("state") == "uploaded"
                and asset.get("size") == e["size"] and asset.get("digest") == f"sha256:{e['sha256']}",
                f"Existing asset mismatch: {asset.get('name')}; refusing replacement")
        if release["draft"] is False:
            require(asset.get("browser_download_url") ==
                    f"https://github.com/{REPO}/releases/download/{TAG}/{asset['name']}", "Asset download URL mismatch")


def verify_remote_payloads(api, release, expected, work):
    for asset in release["assets"]:
        downloaded = work / f"verify-{asset['id']}"
        api.download(f"releases/assets/{asset['id']}", downloaded)
        e = expected[asset["name"]]
        require(downloaded.stat().st_size == e["size"] and sha256(downloaded) == e["sha256"],
                "Downloaded release asset differs from verified input")
        downloaded.unlink()


def deliver(api, env, c, body, files, expected, work):
    verify_environment(env)
    validate_config(c)
    fresh_delivery_guard(api, env)
    tag = api.get(f"git/ref/tags/{TAG}", missing=True)
    release = release_for_tag(api)
    if tag is not None:
        verify_ref(tag, f"tags/{TAG}", c["source_commit"])
    require(release is None or tag is not None, "Existing release without pinned tag")
    if release is not None:
        verify_release(release, c, body)
        verify_assets(release, expected, complete=release["draft"] is False)
        # Reject an existing payload mismatch before creating a ref/release or
        # uploading any missing file. Matching API metadata alone is insufficient.
        verify_remote_payloads(api, release, expected, work)
    if tag is None:
        fresh_delivery_guard(api, env)
        require(api.get(f"git/ref/tags/{TAG}", missing=True) is None, "Tag changed during preparation")
        api.create_tag()
    verify_ref(api.get(f"git/ref/tags/{TAG}"), f"tags/{TAG}", c["source_commit"])
    if release is None:
        fresh_delivery_guard(api, env)
        require(release_for_tag(api) is None, "Release appeared during preparation")
        release = api.create_draft(body)
        verify_release(release, c, body)
        verify_assets(release, expected)
    api.bind_release(release, body)
    release_id = release["id"]
    for file in files:
        fresh_delivery_guard(api, env)
        verify_ref(api.get(f"git/ref/tags/{TAG}"), f"tags/{TAG}", c["source_commit"])
        release = api.get(f"releases/{release_id}")
        verify_release(release, c, body)
        verify_assets(release, expected, complete=release["draft"] is False)
        require(file.stat().st_size == expected[file.name]["size"] and sha256(file) == expected[file.name]["sha256"],
                "Local release file changed after verification")
        if not any(a["name"] == file.name for a in release["assets"]):
            require(release["draft"] is True, "Refusing to upload to a published release")
            api.upload(release, file)
    release = api.get(f"releases/{release_id}")
    verify_release(release, c, body)
    verify_assets(release, expected, complete=True)
    # Independently download and hash all assets before allowing publication.
    verify_remote_payloads(api, release, expected, work)
    was_published = release["draft"] is False
    if c["publish"] and not was_published:
        fresh_delivery_guard(api, env)
        verify_ref(api.get(f"git/ref/tags/{TAG}"), f"tags/{TAG}", c["source_commit"])
        release = api.get(f"releases/{release_id}")
        verify_release(release, c, body)
        verify_assets(release, expected, complete=True)
        require(release["draft"] is True, "Release changed before publication")
        api.publish(release_id)
    release = api.get(f"releases/{release_id}")
    verify_release(release, c, body)
    verify_assets(release, expected, complete=True)
    verify_ref(api.get(f"git/ref/tags/{TAG}"), f"tags/{TAG}", c["source_commit"])
    require(not c["publish"] or release["draft"] is False, "Publication did not complete")
    return {"verified_at": datetime.now(timezone.utc).isoformat(), "state": "draft" if release["draft"] else "published",
            "already_published": was_published, "repository": REPO, "tag": TAG, "release_id": release_id,
            "html_url": release["html_url"], "source_commit": c["source_commit"], "source_tree": c["source_tree"],
            "source_run_id": c["source_run_id"], "artifact_id": c["artifact_id"], "patch_count": c["patch_count"],
            "notes_sha256": c["notes_sha256"], "delivery_commit": env["GITHUB_SHA"],
            "assets": [dict(a, sha256=expected[a["name"]]["sha256"]) for a in release["assets"]]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=Path("workflow2-release-verification.json"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    c = json.loads((root / "release.json").read_text(encoding="utf-8"))
    validate_config(c)  # Placeholders fail before token access, network, or any write.
    verify_environment(os.environ)
    api = GithubAPI(os.environ.get("GH_TOKEN", ""), c)
    fresh_delivery_guard(api, os.environ)
    verify_build(api, c)
    with tempfile.TemporaryDirectory(prefix="prefect-workflow2-") as temp:
        work = Path(temp)
        body, files, expected = prepare_files(api, c, root, work)
        report = deliver(api, os.environ, c, body, files, expected, work)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"state": report["state"], "html_url": report["html_url"], "release_id": report["release_id"]}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (VerificationError, OSError, ValueError, zipfile.BadZipFile, subprocess.TimeoutExpired) as exc:
        print(f"Workflow 2 delivery stopped: {exc}", file=sys.stderr)
        sys.exit(1)
