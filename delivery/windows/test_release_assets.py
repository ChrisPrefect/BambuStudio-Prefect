"""Local, network-free draft upload regression tests."""
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from release_assets import bind_draft, upload_assets_to_draft

REPO = 'ChrisPrefect/BambuStudio-Prefect'
SOURCE = '4b5c3546c7fba94439d9bb0fe69553723b895897'
PREVIOUS = 'ab6b1e83b32e6bffd5d7cc8da6ef8858617baf2a'
TAG = 'v02.08.02.61-prefect.1'
RELEASE = 418968348

class FakeAPI:
    def __init__(self):
        self.release = {'id': RELEASE, 'draft': True, 'tag_name': 'untagged-fixture',
            'target_commitish': SOURCE, 'url': f'https://api.github.com/repos/{REPO}/releases/{RELEASE}',
            'upload_url': f'https://uploads.github.com/repos/{REPO}/releases/{RELEASE}/assets' + '{?name,label}', 'assets': []}
        self.sha = SOURCE
        self.parents = [PREVIOUS]
        self.calls = []
    def __call__(self, path, method='GET', payload=None):
        self.calls.append((path, method, payload))
        if path.startswith('git/ref/tags/'):
            return {'object': {'type': 'commit', 'sha': self.sha}}
        if path == f'git/commits/{SOURCE}':
            return {'parents': [{'sha': sha} for sha in self.parents]}
        if path.startswith('git/refs/tags/') and method == 'PATCH':
            assert payload['force'] is False
            self.sha = payload['sha']
            return {'object': {'type': 'commit', 'sha': self.sha}}
        if path == f'releases/{RELEASE}':
            if method == 'PATCH':
                self.release.update(payload)
            return self.release
        if path == f'releases/{RELEASE}/assets?per_page=100':
            return self.release['assets']
        if path.startswith('releases/assets/') and method == 'DELETE':
            asset_id = int(path.rsplit('/', 1)[1])
            self.release['assets'] = [item for item in self.release['assets'] if item['id'] != asset_id]
            return None
        raise AssertionError('Unexpected API request ' + path)

class FakeUpload:
    def __init__(self, api):
        self.api = api
        self.calls = 0
    def open(self, request, timeout):
        from urllib.parse import parse_qs, urlsplit
        self.calls += 1
        assert hasattr(request.data, 'read'), 'Expected streamed file, not full bytes'
        data = request.data.read()
        name = parse_qs(urlsplit(request.full_url).query)['name'][0]
        assert int(request.get_header('Content-length')) == len(data)
        item = {'id': self.calls, 'name': name, 'state': 'uploaded', 'size': len(data),
                'digest': 'sha256:' + hashlib.sha256(data).hexdigest()}
        self.api.release['assets'].append(item)
        return io.BytesIO(json.dumps(item).encode())

class DraftUploadTests(unittest.TestCase):
    def test_only_pinned_direct_child_can_fast_forward_draft_tag(self):
        api = FakeAPI()
        api.sha = PREVIOUS
        result = bind_draft(api, REPO, RELEASE, TAG, SOURCE, PREVIOUS)
        self.assertTrue(result['draft'])
        self.assertEqual(api.sha, SOURCE)
        self.assertIn(('git/refs/tags/' + TAG, 'PATCH', {'sha': SOURCE, 'force': False}), api.calls)
        for parents in ([], ['0' * 40], [PREVIOUS, '0' * 40]):
            api = FakeAPI()
            api.sha = PREVIOUS
            api.parents = parents
            with self.assertRaises(AssertionError): bind_draft(api, REPO, RELEASE, TAG, SOURCE, PREVIOUS)
            self.assertFalse(any(method != 'GET' for _, method, _ in api.calls))

    def test_rebinds_untagged_draft_explicitly(self):
        api = FakeAPI()
        release = bind_draft(api, REPO, RELEASE, TAG, SOURCE)
        self.assertEqual(release['tag_name'], TAG)
        self.assertTrue(release['draft'])
        self.assertIn((f'releases/{RELEASE}', 'PATCH', {'tag_name': TAG, 'target_commitish': SOURCE, 'draft': True}), api.calls)
    def test_published_release_and_wrong_tag_are_rejected_before_mutation(self):
        for state in ('published', 'wrong_tag'):
            api = FakeAPI()
            if state == 'published': api.release['draft'] = False
            else: api.sha = '0' * 40
            with self.assertRaises(AssertionError): bind_draft(api, REPO, RELEASE, TAG, SOURCE)
            self.assertFalse(any(method != 'GET' for _, method, _ in api.calls))
    def test_streamed_upload_digest_check_and_idempotent_retry(self):
        api = FakeAPI()
        bind_draft(api, REPO, RELEASE, TAG, SOURCE)
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / 'fixture.zip'
            file.write_bytes(b'draft-upload-regression' * 100)
            expected = {file.name: hashlib.sha256(file.read_bytes()).hexdigest()}
            upload = FakeUpload(api)
            for _ in range(2):
                result = upload_assets_to_draft(api, REPO, RELEASE, TAG, SOURCE, [file], expected, 'fixture-token', upload)
                self.assertTrue(result['draft'])
            self.assertEqual(upload.calls, 1)
    def test_malicious_upload_host_and_local_mutation_are_rejected(self):
        api = FakeAPI()
        bind_draft(api, REPO, RELEASE, TAG, SOURCE)
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / 'fixture.zip'
            file.write_bytes(b'original')
            expected = {file.name: hashlib.sha256(file.read_bytes()).hexdigest()}
            api.release['upload_url'] = 'https://example.invalid/upload'
            with self.assertRaises(AssertionError):
                upload_assets_to_draft(api, REPO, RELEASE, TAG, SOURCE, [file], expected, 'fixture-token', FakeUpload(api))
            api.release['upload_url'] = f'https://uploads.github.com/repos/{REPO}/releases/{RELEASE}/assets'
            file.write_bytes(b'changed')
            with self.assertRaises(AssertionError):
                upload_assets_to_draft(api, REPO, RELEASE, TAG, SOURCE, [file], expected, 'fixture-token', FakeUpload(api))

if __name__ == '__main__': unittest.main()
