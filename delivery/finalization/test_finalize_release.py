"""Network-free regression checks of publication guards and idempotence."""
import copy
import hashlib
from pathlib import Path
import unittest
from unittest import mock

import finalize_release as f

BODY = Path(__file__).with_name("release-notes.md").read_text(encoding="utf-8")
ENV = {
    "GITHUB_REPOSITORY": f.REPOSITORY, "GITHUB_REF": f"refs/heads/{f.BRANCH}",
    "GITHUB_EVENT_NAME": "push", "GITHUB_SHA": "a" * 40,
    "GITHUB_WORKFLOW_REF": f"{f.REPOSITORY}/.github/workflows/prefect-finalize.yml@refs/heads/{f.BRANCH}",
}


def ref(name, sha):
    return {"ref": f"refs/{name}", "object": {"type": "commit", "sha": sha}}


def run(run_id, sha, branch, workflow):
    return {"id": run_id, "status": "completed", "conclusion": "success", "head_sha": sha,
            "head_branch": branch, "path": workflow, "event": "push",
            "repository": {"id": f.REPOSITORY_ID, "full_name": f.REPOSITORY},
            "head_repository": {"id": f.REPOSITORY_ID, "full_name": f.REPOSITORY},
            "head_commit": {"tree_id": f.TREE}}


class FakeAPI:
    def __init__(self, *, published=False):
        self.patch_calls = []
        self.reads = []
        self.post_patch_corrupt = False
        assets = [dict(a, digest=f"sha256:{a['sha256']}", state="uploaded",
                       browser_download_url=f"https://github.com/{f.REPOSITORY}/releases/download/{f.TAG}/{a['name']}")
                  for a in f.ASSETS]
        self.release = {"id": f.RELEASE_ID, "tag_name": f.TAG, "target_commitish": f.SOURCE,
                        "name": f.TITLE, "prerelease": True, "draft": not published,
                        "assets": assets, "body": BODY if published else "old draft notes",
                        "published_at": "2026-10-21T20:00:00Z" if published else None,
                        "html_url": f.CANONICAL_RELEASE if published else "https://github.com/draft"}
        self.data = {
            f"{f.PREFIX}git/ref/heads/{f.BRANCH}": ref(f"heads/{f.BRANCH}", ENV["GITHUB_SHA"]),
            f"{f.PREFIX}git/ref/tags/{f.TAG}": ref(f"tags/{f.TAG}", f.SOURCE),
            f"{f.PREFIX}git/commits/{f.SOURCE}": {"sha": f.SOURCE, "tree": {"sha": f.TREE}},
            f"{f.PREFIX}actions/runs/{f.SOURCE_RUN}":
                run(f.SOURCE_RUN, f.SOURCE, "prefect/workflow", ".github/workflows/prefect-workflow.yml"),
            f"{f.PREFIX}actions/runs/{f.PUBLISHER_RUN}":
                run(f.PUBLISHER_RUN, f.PUBLISHER_SOURCE, f.BRANCH, ".github/workflows/prefect-publish.yml"),
            f"{f.PREFIX}actions/runs/{f.SOURCE_RUN}/artifacts?per_page=100": {
                "total_count": 1, "artifacts": [{
                    "id": 12360594342, "name": f"BambuStudio-Prefect-Windows-x64-{f.SOURCE}",
                    "size_in_bytes": f.ASSETS[0]["size"], "digest": f"sha256:{f.ASSETS[0]['sha256']}",
                    "expired": False, "workflow_run": {
                        "id": f.SOURCE_RUN, "head_sha": f.SOURCE, "repository_id": f.REPOSITORY_ID,
                        "head_repository_id": f.REPOSITORY_ID, "head_branch": "prefect/workflow"}}]},
        }
        self.checksums = f.CHECKSUMS

    def get(self, path):
        self.reads.append(path)
        return copy.deepcopy(self.release if path == f.RELEASE_PATH else self.data[path])

    def get_bytes(self, path):
        if path != f"{f.PREFIX}releases/assets/663155220":
            raise AssertionError("Unexpected binary read")
        return self.checksums

    def patch_release(self, payload):
        self.patch_calls.append(copy.deepcopy(payload))
        self.release.update(payload)
        self.release.update(html_url=f.CANONICAL_RELEASE, published_at="2026-10-21T20:00:00Z")
        if self.post_patch_corrupt:
            self.release["assets"][0]["digest"] = "sha256:" + "0" * 64
        return copy.deepcopy(self.release)


class FinalizationTests(unittest.TestCase):
    def reject(self, api, *, env=None, body=BODY):
        with self.assertRaises(f.VerificationError):
            f.finalize(api, ENV if env is None else env, body)
        self.assertEqual(api.patch_calls, [])

    def test_notes_and_checksum_pins(self):
        self.assertEqual(hashlib.sha256(BODY.encode("utf-8")).hexdigest(), f.BODY_SHA256)
        self.assertEqual(len(f.CHECKSUMS), 218)
        self.assertEqual(hashlib.sha256(f.CHECKSUMS).hexdigest(), f.ASSETS[2]["sha256"])

    def test_draft_publishes_once_and_verifies_canonical_links(self):
        api = FakeAPI()
        report = f.finalize(api, ENV, BODY)
        self.assertEqual(len(api.patch_calls), 1)
        self.assertFalse(api.patch_calls[0]["draft"])
        self.assertEqual(report["state"], "published")
        self.assertEqual(report["html_url"], f.CANONICAL_RELEASE)
        self.assertEqual(len(report["assets"]), 3)
        self.assertEqual(api.reads[-2:], [f.RELEASE_PATH, f"{f.PREFIX}git/ref/tags/{f.TAG}"])

    def test_matching_published_release_is_idempotent(self):
        api = FakeAPI(published=True)
        report = f.finalize(api, ENV, BODY)
        self.assertEqual(api.patch_calls, [])
        self.assertTrue(report["already_published"])

    def test_read_only_verifies_draft_without_publishing(self):
        api = FakeAPI()
        report = f.finalize(api, ENV, BODY, read_only=True)
        self.assertEqual(api.patch_calls, [])
        self.assertEqual(report["state"], "verified-draft-read-only")
        self.assertTrue(report["download_urls_pending_publication"])

    def test_wrong_asset_identity_size_digest_or_state_rejected(self):
        for key, value in (("id", 1), ("name", "wrong.zip"), ("size", 1),
                           ("digest", "sha256:" + "0" * 64), ("state", "starter")):
            with self.subTest(field=key):
                api = FakeAPI()
                api.release["assets"][0][key] = value
                self.reject(api)

    def test_extra_or_duplicate_asset_rejected(self):
        for replacement in ("extra", "duplicate"):
            with self.subTest(replacement=replacement):
                api = FakeAPI()
                if replacement == "extra":
                    api.release["assets"].append({"id": 99})
                else:
                    api.release["assets"][1] = copy.deepcopy(api.release["assets"][0])
                self.reject(api)

    def test_wrong_or_annotated_tag_rejected_without_repair(self):
        for field, value in (("sha", "0" * 40), ("type", "tag")):
            with self.subTest(field=field):
                api = FakeAPI()
                api.data[f"{f.PREFIX}git/ref/tags/{f.TAG}"]["object"][field] = value
                self.reject(api)

    def test_wrong_source_tree_failed_run_or_artifact_rejected(self):
        for scenario in ("tree", "run", "artifact", "publisher"):
            with self.subTest(scenario=scenario):
                api = FakeAPI()
                if scenario == "tree":
                    api.data[f"{f.PREFIX}git/commits/{f.SOURCE}"]["tree"]["sha"] = "0" * 40
                elif scenario == "run":
                    api.data[f"{f.PREFIX}actions/runs/{f.SOURCE_RUN}"]["conclusion"] = "failure"
                elif scenario == "publisher":
                    api.data[f"{f.PREFIX}actions/runs/{f.PUBLISHER_RUN}"]["head_sha"] = "0" * 40
                else:
                    api.data[f"{f.PREFIX}actions/runs/{f.SOURCE_RUN}/artifacts?per_page=100"]["artifacts"][0]["expired"] = True
                self.reject(api)

    def test_wrong_repository_branch_event_workflow_or_stale_commit_rejected(self):
        for field, value in (("GITHUB_REPOSITORY", "other/repo"), ("GITHUB_REF", "refs/heads/main"),
                             ("GITHUB_EVENT_NAME", "pull_request"), ("GITHUB_WORKFLOW_REF", "wrong"),
                             ("GITHUB_SHA", "0" * 40)):
            with self.subTest(field=field):
                self.reject(FakeAPI(), env=dict(ENV, **{field: value}))

    def test_changed_notes_or_exact_checksum_bytes_rejected(self):
        self.reject(FakeAPI(), body=BODY + "changed")
        api = FakeAPI()
        api.checksums = api.checksums.replace(b"\n", b"\r\n")
        self.reject(api)

    def test_published_mismatch_is_never_edited(self):
        for field, value in (("body", "different published notes"), ("html_url", "https://wrong"),
                             ("tag_name", "other-tag"), ("prerelease", False)):
            with self.subTest(field=field):
                api = FakeAPI(published=True)
                api.release[field] = value
                self.reject(api)

    def test_post_patch_corruption_fails_without_success_report(self):
        api = FakeAPI()
        api.post_patch_corrupt = True
        with self.assertRaises(f.VerificationError):
            f.finalize(api, ENV, BODY)
        self.assertEqual(len(api.patch_calls), 1)

    def test_api_adapter_refuses_unexpected_write_target_or_payload(self):
        api = f.GithubAPI()
        with mock.patch.object(f.subprocess, "run") as process:
            with self.assertRaises(f.VerificationError):
                api._run(f"{f.PREFIX}git/refs/tags/{f.TAG}", payload={})
            with self.assertRaises(f.VerificationError):
                api.patch_release({"draft": False})
            process.assert_not_called()


if __name__ == "__main__":
    unittest.main()
