"""Network-free checks for new-release-only staging, publication, and mismatch rejection."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import zipfile

import release as r

SOURCE, TREE = "ab" * 20, "cd" * 20
ENV = {"GITHUB_REPOSITORY": r.REPO, "GITHUB_REF": f"refs/heads/{r.BRANCH}",
       "GITHUB_EVENT_NAME": "push", "GITHUB_SHA": "ef" * 20,
       "GITHUB_WORKFLOW_REF": f"{r.REPO}/{r.WORKFLOW}@refs/heads/{r.BRANCH}"}


def ref(name, source):
    return {"ref": f"refs/{name}", "object": {"type": "commit", "sha": source}}


class FakeAPI:
    def __init__(self, c, windows):
        self.c = c
        self.writes = []
        self.tag = None
        self.release = None
        self.bound_release_id = None
        self.payloads = {f"actions/artifacts/{c['artifact_id']}/zip": windows}
        self.next_asset = 100
        self.repo = {"full_name": r.REPO, "id": r.REPO_ID}
        self.run = {"id": c["source_run_id"], "head_sha": SOURCE, "head_branch": "prefect/workflow",
                    "event": "push", "path": r.SOURCE_WORKFLOW, "head_commit": {"tree_id": TREE},
                    "repository": self.repo, "head_repository": self.repo,
                    "status": "completed", "conclusion": "success"}
        self.artifact = {"id": c["artifact_id"], "name": f"BambuStudio-Prefect-Windows-x64-{SOURCE}",
            "expired": False, "size_in_bytes": c["artifact_size"], "digest": f"sha256:{c['artifact_sha256']}",
            "workflow_run": {"id": c["source_run_id"], "head_sha": SOURCE, "head_branch": "prefect/workflow",
                             "repository_id": r.REPO_ID, "head_repository_id": r.REPO_ID}}
        self.branch = ref(f"heads/{r.BRANCH}", ENV["GITHUB_SHA"])

    def get(self, path, missing=False):
        if path == f"git/ref/heads/{r.BRANCH}":
            result = self.branch
        elif path == f"git/ref/tags/{r.TAG}":
            result = self.tag
        elif path.startswith("releases?per_page=100&page="):
            result = [{"id": r.OLD_RELEASE_ID, "tag_name": "v02.08.02.61-prefect.1"}]
            if self.release:
                result.append(self.release)
        elif path == f"git/commits/{SOURCE}":
            result = {"sha": SOURCE, "tree": {"sha": TREE}}
        elif path == f"actions/runs/{self.c['source_run_id']}":
            result = self.run
        elif path == f"actions/runs/{self.c['source_run_id']}/artifacts?per_page=100":
            result = {"total_count": 1, "artifacts": [self.artifact]}
        elif self.release and path == f"releases/{self.release['id']}":
            result = self.release
        else:
            raise AssertionError(f"Unexpected API GET {path}")
        return copy.deepcopy(result)

    def download(self, path, destination):
        Path(destination).write_bytes(self.payloads[path])

    def create_tag(self):
        self.writes.append(("create_tag", r.TAG, SOURCE))
        self.tag = ref(f"tags/{r.TAG}", SOURCE)
        return copy.deepcopy(self.tag)

    def create_draft(self, body):
        self.writes.append(("create_draft", r.TAG))
        self.release = {"id": 42, "tag_name": r.TAG, "target_commitish": SOURCE, "name": r.TITLE,
                        "body": body, "draft": True, "prerelease": True, "assets": [],
                        "html_url": "https://github.com/draft", "published_at": None,
                        "url": f"https://api.github.com/repos/{r.REPO}/releases/42",
                        "upload_url": f"https://uploads.github.com/repos/{r.REPO}/releases/42/assets{{?name,label}}"}
        return copy.deepcopy(self.release)

    def bind_release(self, release, body):
        r.verify_release(release, self.c, body)
        self.bound_release_id = release["id"]

    def upload(self, release, file):
        self.writes.append(("upload", file.name))
        self.next_asset += 1
        payload = file.read_bytes()
        self.payloads[f"releases/assets/{self.next_asset}"] = payload
        asset = {"id": self.next_asset, "name": file.name, "state": "uploaded", "size": len(payload),
                 "digest": "sha256:" + hashlib.sha256(payload).hexdigest(),
                 "browser_download_url": f"https://github.com/{r.REPO}/releases/download/{r.TAG}/{file.name}"}
        self.release["assets"].append(asset)
        return copy.deepcopy(asset)

    def publish(self, release_id):
        if release_id != 42 or self.bound_release_id != 42 or not self.c["publish"]:
            raise AssertionError("Unexpected publication")
        self.writes.append(("publish", release_id))
        self.release.update(draft=False, html_url=r.PUBLIC_URL, published_at="2026-10-23T12:00:00Z")
        return copy.deepcopy(self.release)


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "delivery"
        self.work = Path(self.temp.name) / "work"
        self.root.mkdir()
        self.work.mkdir()
        self.body = "Workflow 2 fixture notes; GUI and hardware limits remain documented.\n"
        (self.root / "release-notes.md").write_text(self.body, encoding="utf-8")
        self.c = {"source_commit": SOURCE, "source_tree": TREE, "source_run_id": 123,
                  "artifact_id": 456, "patch_file": "BambuStudio-Prefect-Workflow2-patches.zip",
                  "patch_count": 1, "publish": False,
                  "notes_sha256": hashlib.sha256(self.body.encode()).hexdigest()}
        self.write_windows()
        patch = b"From fixture\nSubject: final source change\n"
        self.replay = {"success": True, "base_commit": r.BASE, "head_commit": SOURCE, "expected_tree": TREE,
                       "replayed_final_tree": TREE, "mail_replayed_final_tree": TREE,
                       "normal_index_unchanged": True, "commits": [{"commit": SOURCE}],
                       "format_patch": [{"file": "0001-fixture.patch", "commit": SOURCE,
                           "replayed_tree": TREE, "match": True, "apply_exit_code": 0, "write_tree_exit_code": 0,
                           "bytes": len(patch), "sha256": hashlib.sha256(patch).hexdigest()}]}
        self.patch_payload = patch
        self.write_patch()
        self.api = FakeAPI(self.c, self.windows)

    def write_windows(self, marker=SOURCE):
        file = self.work / "artifact.zip"
        with zipfile.ZipFile(file, "w") as archive:
            archive.writestr("PREFECT-COMMIT.txt", marker + "\n")
            archive.writestr("bambu-studio.exe", b"fixture exe")
            archive.writestr("BambuStudio.dll", b"fixture dll")
        self.windows = file.read_bytes()
        self.c.update(artifact_size=len(self.windows), artifact_sha256=hashlib.sha256(self.windows).hexdigest())

    def write_patch(self):
        file = self.root / self.c["patch_file"]
        with zipfile.ZipFile(file, "w") as archive:
            archive.writestr("series/0001-fixture.patch", self.patch_payload)
            archive.writestr("series/replay-manifest.json", json.dumps(self.replay))
        self.c.update(patch_size=file.stat().st_size, patch_sha256=r.sha256(file))

    def prepare(self):
        r.verify_build(self.api, self.c, wait_seconds=0)
        self.body, self.files, self.expected = r.prepare_files(self.api, self.c, self.root, self.work)

    def deliver(self):
        self.prepare()
        return r.deliver(self.api, ENV, self.c, self.body, self.files, self.expected, self.work)

    def stage(self):
        report = self.deliver()
        self.assertEqual(report["state"], "draft")
        self.api.writes.clear()
        return report

    def reject_without_writes(self):
        with self.assertRaises(r.VerificationError):
            self.deliver()
        self.assertEqual(self.api.writes, [])

    def test_placeholder_config_refuses_before_api_construction(self):
        placeholder = json.loads(Path(__file__).with_name("release.json").read_text(encoding="utf-8"))
        # The shipped template must remain unfilled until root pins the real build.
        if placeholder["source_commit"] is None:
            with self.assertRaises(r.VerificationError):
                r.validate_config(placeholder)
        for key in ("source_commit", "artifact_sha256", "patch_count"):
            c = dict(self.c, **{key: None})
            with self.assertRaises(r.VerificationError):
                r.validate_config(c)

    def test_stage_creates_only_new_tag_draft_and_three_assets(self):
        report = self.deliver()
        self.assertEqual(report["state"], "draft")
        self.assertEqual([x[0] for x in self.api.writes], ["create_tag", "create_draft", "upload", "upload", "upload"])
        self.assertEqual(self.api.tag["object"]["sha"], SOURCE)
        self.assertEqual(len(report["assets"]), 3)

    def test_staged_retry_is_idempotent(self):
        self.stage()
        self.assertEqual(self.deliver()["state"], "draft")
        self.assertEqual(self.api.writes, [])

    def test_publish_only_after_explicit_config_switch_and_published_retry(self):
        self.stage()
        self.c["publish"] = True
        report = self.deliver()
        self.assertEqual(report["state"], "published")
        self.assertEqual(self.api.writes, [("publish", 42)])
        self.api.writes.clear()
        self.assertTrue(self.deliver()["already_published"])
        self.assertEqual(self.api.writes, [])

    def test_publish_false_never_unpublishes_existing_release(self):
        self.stage()
        self.c["publish"] = True
        self.deliver()
        self.c["publish"] = False
        self.api.writes.clear()
        self.assertEqual(self.deliver()["state"], "published")
        self.assertEqual(self.api.writes, [])

    def test_existing_tag_wrong_commit_or_annotated_ref_rejects(self):
        for field, value in (("sha", "ac" * 20), ("type", "tag")):
            with self.subTest(field=field):
                self.api.tag = ref(f"tags/{r.TAG}", SOURCE)
                self.api.tag["object"][field] = value
                self.reject_without_writes()

    def test_existing_release_mismatch_never_edited(self):
        self.stage()
        original = copy.deepcopy(self.api.release)
        for key, value in (("body", "other notes"), ("target_commitish", "ac" * 20),
                           ("name", "different name"), ("prerelease", False), ("id", r.OLD_RELEASE_ID)):
            with self.subTest(field=key):
                self.api.release = copy.deepcopy(original)
                self.api.release[key] = value
                self.reject_without_writes()

    def test_extra_asset_or_mismatching_digest_size_state_rejects(self):
        self.stage()
        original = copy.deepcopy(self.api.release)
        for key, value in (("digest", "sha256:" + "0" * 64), ("size", 1), ("state", "starter")):
            with self.subTest(field=key):
                self.api.release = copy.deepcopy(original)
                self.api.release["assets"][0][key] = value
                self.reject_without_writes()
        self.api.release = copy.deepcopy(original)
        self.api.release["assets"].append({"id": 987, "name": "unrelated.zip"})
        self.reject_without_writes()

    def test_existing_binary_mismatch_rejected_before_any_missing_asset_upload(self):
        self.stage()
        self.api.release["assets"] = self.api.release["assets"][:1]
        first = self.api.release["assets"][0]
        self.api.payloads[f"releases/assets/{first['id']}"] = b"corrupt-existing-payload"
        self.reject_without_writes()

    def test_published_notes_mismatch_never_clobbered(self):
        self.stage()
        self.c["publish"] = True
        self.deliver()
        self.api.writes.clear()
        self.api.release["body"] = "Somebody changed published notes"
        self.reject_without_writes()

    def test_failed_or_wrong_build_repository_head_tree_artifact_rejected(self):
        for target, field, value in ((self.api.run, "conclusion", "failure"),
            (self.api.run, "head_sha", "ac" * 20), (self.api.run, "head_branch", "main"),
            (self.api.artifact, "expired", True), (self.api.artifact, "digest", "sha256:" + "0" * 64)):
            with self.subTest(field=field):
                old = target[field]
                target[field] = value
                self.reject_without_writes()
                target[field] = old

    def test_waits_only_for_pinned_running_build(self):
        self.api.run.update(status="in_progress", conclusion=None)
        def finish(_seconds):
            self.api.run.update(status="completed", conclusion="success")
        r.verify_build(self.api, self.c, sleep=finish, monotonic=lambda: 0, wait_seconds=1)
        self.assertEqual(self.api.writes, [])

    def test_wrong_environment_rejects_before_writes(self):
        self.prepare()
        for field, value in (("GITHUB_REPOSITORY", "wrong/repo"), ("GITHUB_REF", "refs/heads/main"),
                             ("GITHUB_EVENT_NAME", "pull_request"), ("GITHUB_WORKFLOW_REF", "wrong")):
            with self.subTest(field=field), self.assertRaises(r.VerificationError):
                r.deliver(self.api, dict(ENV, **{field: value}), self.c, self.body, self.files, self.expected, self.work)
        self.assertEqual(self.api.writes, [])

    def test_stale_delivery_branch_rejects(self):
        self.api.branch["object"]["sha"] = "ac" * 20
        self.reject_without_writes()

    def test_wrong_patch_count_hash_or_replay_head_rejects(self):
        self.c["patch_count"] = 2
        self.reject_without_writes()
        self.c["patch_count"] = 1
        self.c["patch_sha256"] = "ab" * 32
        self.reject_without_writes()
        self.replay["head_commit"] = "ac" * 20
        self.write_patch()
        self.reject_without_writes()

    def test_wrong_commit_marker_rejects_even_with_matching_archive_sha(self):
        self.write_windows(marker="ac" * 20)
        self.api.payloads[f"actions/artifacts/{self.c['artifact_id']}/zip"] = self.windows
        self.api.artifact.update(size_in_bytes=self.c["artifact_size"], digest=f"sha256:{self.c['artifact_sha256']}")
        self.reject_without_writes()

    def test_wrong_notes_hash_or_local_patch_mutation_rejects(self):
        (self.root / "release-notes.md").write_text(self.body + "changed", encoding="utf-8")
        self.reject_without_writes()
        (self.root / "release-notes.md").write_text(self.body, encoding="utf-8")
        with (self.root / self.c["patch_file"]).open("ab") as stream:
            stream.write(b"changed")
        self.reject_without_writes()

    def test_zip_traversal_duplicate_or_case_collision_rejects(self):
        for names in (("../bad",), ("a", "A")):
            with self.subTest(names=names):
                file = self.work / "unsafe.zip"
                with zipfile.ZipFile(file, "w") as archive:
                    for name in names:
                        archive.writestr(name, b"bad")
                with self.assertRaises(r.VerificationError):
                    r.safe_zip(file)

    def test_api_publisher_refuses_old_unbound_or_disabled_release(self):
        api = r.GithubAPI("fixture-token", self.c)
        with mock.patch.object(api, "_json") as network:
            for release_id in (r.OLD_RELEASE_ID, 42):
                with self.assertRaises(r.VerificationError):
                    api.publish(release_id)
            self.c["publish"] = True
            with self.assertRaises(r.VerificationError):
                api.publish(42)
            network.assert_not_called()

    def test_api_upload_refuses_wrong_host_old_id_and_unexpected_filename(self):
        self.prepare()
        api = r.GithubAPI("fixture-token", self.c)
        release = self.api.create_draft(self.body)
        api.bind_release(release, self.body)
        with mock.patch.object(api.opener, "open") as network:
            bad = dict(release, upload_url="https://example.invalid/upload")
            with self.assertRaises(r.VerificationError):
                api.upload(bad, self.files[0])
            bad = dict(release, id=r.OLD_RELEASE_ID)
            with self.assertRaises(r.VerificationError):
                api.upload(bad, self.files[0])
            file = self.work / "unreviewed.zip"
            file.write_bytes(b"fixture")
            with self.assertRaises(r.VerificationError):
                api.upload(release, file)
            network.assert_not_called()

    def test_bad_zip_crc_rejects_before_release_writes(self):
        payload = bytearray(self.windows)
        start = payload.index(b"fixture exe")
        payload[start] ^= 0xFF
        self.api.payloads[f"actions/artifacts/{self.c['artifact_id']}/zip"] = bytes(payload)
        self.c.update(artifact_size=len(payload), artifact_sha256=hashlib.sha256(payload).hexdigest())
        self.api.artifact.update(size_in_bytes=len(payload), digest=f"sha256:{self.c['artifact_sha256']}")
        self.reject_without_writes()

    def test_download_accept_matches_artifact_and_release_endpoints(self):
        api = r.GithubAPI("fixture-token", self.c)
        with mock.patch.object(r.subprocess, "run", return_value=mock.Mock(returncode=0)) as process:
            api.download("actions/artifacts/456/zip", self.work / "artifact-download.zip")
            self.assertIn("Accept: application/vnd.github+json", process.call_args.args[0])
            api.download("releases/assets/101", self.work / "release-download.zip")
            self.assertIn("Accept: application/octet-stream", process.call_args.args[0])

    def test_download_error_reports_only_http_status_without_signed_urls(self):
        api = r.GithubAPI("fixture-token", self.c)
        response = mock.Mock(returncode=1, stderr=b"gh: Unsupported Accept (HTTP 415) https://example.invalid/?signed=secret")
        with mock.patch.object(r.subprocess, "run", return_value=response), self.assertRaises(r.VerificationError) as caught:
            api.download("actions/artifacts/456/zip", self.work / "artifact-download.zip")
        self.assertEqual(str(caught.exception), "GitHub binary download failed (HTTP 415)")


if __name__ == "__main__":
    unittest.main()
