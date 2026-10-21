"""ID-bound draft uploads; never discover or publish a release by tag."""
from __future__ import annotations
import hashlib
from pathlib import Path
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler

if not __debug__:
    raise RuntimeError('Release verification requires active assertions; do not use python -O.')

EXPECTED_REPOSITORY = 'ChrisPrefect/BambuStudio-Prefect'

class NoUploadRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        raise RuntimeError('Unexpected release asset upload redirect')

def validate_draft(release, repo, release_id, tag, source):
    assert repo.lower() == EXPECTED_REPOSITORY.lower(), 'Wrong release repository'
    assert release['id'] == release_id and release['draft'] is True, 'Expected the pinned draft release'
    assert release['tag_name'] == tag, 'Release tag binding mismatch'
    assert release['target_commitish'] == source, 'Release source binding mismatch'
    assert release['url'] == f'https://api.github.com/repos/{repo}/releases/{release_id}', 'Unexpected release URL'
    return release

def verify_tag(api, tag, source):
    ref = api('git/ref/tags/' + quote(tag, safe=''))
    assert ref['object']['type'] == 'commit' and ref['object']['sha'] == source, 'Git tag must point at built source'

def bind_draft(api, repo, release_id, tag, source, previous_source=None):
    assert isinstance(release_id, int) and not isinstance(release_id, bool) and release_id > 0
    assert repo.lower() == EXPECTED_REPOSITORY.lower(), 'Wrong release repository'
    release = api(f'releases/{release_id}')
    assert release['id'] == release_id and release['draft'] is True, 'Refusing to change a published release'
    ref = api('git/ref/tags/' + quote(tag, safe=''))
    assert ref['object']['type'] == 'commit', 'Expected lightweight release tag'
    if ref['object']['sha'] != source:
        assert previous_source and ref['object']['sha'] == previous_source, 'Unexpected previous tag target'
        commit = api(f'git/commits/{source}')
        assert [parent['sha'] for parent in commit['parents']] == [previous_source], 'Release tag update must be a direct fast-forward'
        api('git/refs/tags/' + quote(tag, safe=''), 'PATCH', {'sha': source, 'force': False})
    verify_tag(api, tag, source)
    # Unpublishing can give a draft an untagged-* name. Rebind explicitly before uploading.
    api(f'releases/{release_id}', 'PATCH', {'tag_name': tag, 'target_commitish': source, 'draft': True})
    release = api(f'releases/{release_id}')
    verify_tag(api, tag, source)
    return validate_draft(release, repo, release_id, tag, source)

def sha256(file):
    with Path(file).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def check_asset(asset, file, expected_sha):
    assert asset['name'] == file.name and asset['state'] == 'uploaded', 'Asset upload incomplete'
    assert asset['size'] == file.stat().st_size, 'Asset size mismatch'
    assert asset.get('digest') == 'sha256:' + expected_sha, 'Asset digest mismatch'
    return asset

def upload_assets_to_draft(api, repo, release_id, tag, source, files, expected, token, opener=None):
    assert token, 'Missing upload authorization'
    assert len({Path(file).name for file in files}) == len(files), 'Duplicate asset names'
    opener = opener or build_opener(NoUploadRedirect())
    for path in files:
        file = Path(path)
        expected_sha = expected[file.name]
        assert sha256(file) == expected_sha, 'Local asset changed after verification'
        release = validate_draft(api(f'releases/{release_id}'), repo, release_id, tag, source)
        verify_tag(api, tag, source)
        base = release['upload_url'].split('{', 1)[0]
        parts = urlsplit(base)
        assert parts.scheme == 'https' and parts.netloc == 'uploads.github.com', 'Unexpected upload host'
        assert parts.path == f'/repos/{repo}/releases/{release_id}/assets' and not parts.query and not parts.fragment, 'Unexpected upload endpoint'
        assets = api(f'releases/{release_id}/assets?per_page=100')
        matching = [item for item in assets if item['name'] == file.name]
        assert len(matching) <= 1, 'Duplicate remote asset names'
        if matching:
            item = matching[0]
            if item.get('state') == 'uploaded' and item.get('digest') == 'sha256:' + expected_sha and item.get('size') == file.stat().st_size:
                check_asset(item, file, expected_sha)
                continue
            # Replace only this known asset on this verified draft; unrelated assets remain intact.
            api(f"releases/assets/{item['id']}", 'DELETE')
        url = base + '?' + urlencode({'name': file.name})
        # urllib streams the file object in bounded blocks. No full ZIP is loaded in memory.
        with file.open('rb') as stream:
            request = Request(url, data=stream, method='POST', headers={
                'Authorization': 'Bearer ' + token,
                'Accept': 'application/vnd.github+json',
                'X-GitHub-Api-Version': '2022-11-28',
                'Content-Type': 'text/plain' if file.suffix == '.txt' else 'application/zip',
                'Content-Length': str(file.stat().st_size),
            })
            with opener.open(request, timeout=900) as response:
                import json
                uploaded = json.load(response)
        check_asset(uploaded, file, expected_sha)
    release = validate_draft(api(f'releases/{release_id}'), repo, release_id, tag, source)
    verify_tag(api, tag, source)
    for path in files:
        file = Path(path)
        matching = [item for item in release['assets'] if item['name'] == file.name]
        assert len(matching) == 1, 'Missing uploaded asset'
        check_asset(matching[0], file, expected[file.name])
    return release
