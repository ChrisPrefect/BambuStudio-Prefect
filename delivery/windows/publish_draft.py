"""Attach verified build assets to a draft; publication follows GUI acceptance."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import time
import zipfile

root = Path(__file__).resolve().parent
config = json.loads((root / 'release.json').read_text(encoding='utf-8'))
repo = os.environ['GITHUB_REPOSITORY']
source = config['source_commit']
run_id = config['source_run_id']
tag = config['tag']

def api(path, method='GET', payload=None):
    command = ['gh', 'api', '--method', method, f'repos/{repo}/{path}']
    if payload is not None:
        command += ['--input', '-']
    result = subprocess.run(command, input=None if payload is None else json.dumps(payload).encode(),
                            stdout=subprocess.PIPE, check=True)
    return json.loads(result.stdout)

def digest(file):
    with file.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

commit = api(f'git/commits/{source}')
assert commit['tree']['sha'] == config['source_tree'], 'Unexpected source tree'
deadline = time.monotonic() + 3.5 * 60 * 60
while True:
    run = api(f'actions/runs/{run_id}')
    assert run['head_sha'] == source, 'Workflow belongs to a different commit'
    assert run['head_repository']['full_name'].lower() == repo.lower(), 'Wrong source repository'
    if run['status'] == 'completed':
        assert run['conclusion'] == 'success', f"Source build failed: {run['conclusion']}"
        break
    assert time.monotonic() < deadline, 'Timed out waiting for source build'
    print('Waiting for the pinned Windows build to complete successfully.', flush=True)
    time.sleep(30)

artifacts = api(f'actions/runs/{run_id}/artifacts')['artifacts']
matching = [item for item in artifacts if item['name'] == f'BambuStudio-Prefect-Windows-x64-{source}']
assert len(matching) == 1 and not matching[0]['expired'], 'Missing unique Windows artifact'
artifact = matching[0]
portable = Path('BambuStudio-Prefect-2.8.2.61-Windows-x64.zip')
with portable.open('wb') as output:
    subprocess.run(['gh', 'api', f"repos/{repo}/actions/artifacts/{artifact['id']}/zip"], stdout=output, check=True)
portable_sha = digest(portable)
assert artifact.get('digest') == f'sha256:{portable_sha}', 'Windows artifact digest mismatch'
assert portable.stat().st_size == artifact['size_in_bytes'], 'Windows artifact size mismatch'
with zipfile.ZipFile(portable) as archive:
    assert archive.testzip() is None, 'Invalid portable ZIP'
    names = archive.namelist()
    markers = [name for name in names if name.endswith('PREFECT-COMMIT.txt')]
    assert len(markers) == 1 and archive.read(markers[0]).decode('utf-8-sig').strip() == source
    assert len([name for name in names if name.lower().endswith('/bambu-studio.exe') or name.lower() == 'bambu-studio.exe']) == 1
    assert len([name for name in names if name.lower().endswith('/bambustudio.dll') or name.lower() == 'bambustudio.dll']) == 1

patch = root / config['patch_file']
assert digest(patch) == config['patch_sha256'], 'Patch archive digest mismatch'
with zipfile.ZipFile(patch) as archive:
    assert archive.testzip() is None
    assert len([name for name in archive.namelist() if name.endswith('.patch')]) == 17
checksums = Path('SHA256SUMS.txt')
checksums.write_text(f'{portable_sha}  {portable.name}\n{digest(patch)}  {patch.name}\n', encoding='ascii')

releases = api('releases?per_page=100')
existing = [release for release in releases if release['tag_name'] == tag]
assert len(existing) <= 1
if existing:
    release = existing[0]
    assert release['draft'], 'Refusing to replace a published release'
    release = api(f"releases/{release['id']}", 'PATCH', {'target_commitish': source})
else:
    release = api('releases', 'POST', {'tag_name': tag, 'target_commitish': source,
                                      'name': config['title'], 'draft': True, 'prerelease': True})
subprocess.run(['gh', 'release', 'upload', tag, str(portable), str(patch), str(checksums),
                '--repo', repo, '--clobber'], check=True)
release = api(f"releases/{release['id']}")
expected = {portable.name: portable_sha, patch.name: digest(patch), checksums.name: digest(checksums)}
for name, sha in expected.items():
    assets = [asset for asset in release['assets'] if asset['name'] == name]
    assert len(assets) == 1 and assets[0]['state'] == 'uploaded'
    assert assets[0].get('digest') == f'sha256:{sha}', f'Uploaded asset digest mismatch: {name}'
proof = {'source_commit': source, 'source_tree': config['source_tree'], 'source_run_id': run_id,
         'artifact_id': artifact['id'], 'release_id': release['id'], 'release_url': release['html_url'],
         'draft': release['draft'], 'assets': expected, 'success': True}
Path('prepared-release.json').write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
print(json.dumps(proof, indent=2))
