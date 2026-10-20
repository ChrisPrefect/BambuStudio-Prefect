"""Byte-exact patch export plus full tree replay using an external private index.
No worktree/index modifications, no lazy blob downloads, no compile dependencies.
"""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    cli=argparse.ArgumentParser()
    for name in ('repo','output','base','head','expected-tree'):
        cli.add_argument('--'+name,required=True)
    cli.add_argument('--git',default='git')
    args=cli.parse_args()
    repo=Path(args.repo).resolve(); out=Path(args.output).resolve()
    if out.exists() and any(p.is_file() for p in out.rglob('*')):
        raise RuntimeError('Output must be new or contain only empty directories')
    out.mkdir(parents=True,exist_ok=True)
    diffs=out/'replay-diffs'; diffs.mkdir(exist_ok=True)
    objects=out/'replay-objects'; objects.mkdir(exist_ok=True)
    base_env=os.environ.copy()
    base_env['GIT_NO_LAZY_FETCH']='1'
    base_env['GIT_OBJECT_DIRECTORY']=str(objects)
    base_env['GIT_ALTERNATE_OBJECT_DIRECTORIES']=str(repo/'.git/objects')
    commands=[]
    def git(*argv,env=None,target=None):
        result=subprocess.run([args.git,'-C',str(repo),*argv],env=env or base_env,
            stdout=target if target is not None else subprocess.PIPE,stderr=subprocess.PIPE)
        commands.append({'argv':['git',*argv],'exit_code':result.returncode,
            'stderr':result.stderr.decode('utf-8',errors='replace').strip()})
        if result.returncode:
            raise RuntimeError(str(argv)+'\n'+result.stderr.decode('utf-8',errors='replace'))
        return result.stdout or b''
    def text(*argv,env=None):
        return git(*argv,env=env).decode('utf-8').strip()
    base=text('rev-parse',args.base); head=text('rev-parse',args.head)
    expected=text('rev-parse',head+'^{tree}')
    if expected!=args.expected_tree:
        raise RuntimeError('Frozen head tree differs: '+expected)
    real_index=Path(text('rev-parse','--git-path','index'))
    if not real_index.is_absolute(): real_index=repo/real_index
    before=sha(real_index)
    report={'date':'2026-10-21','timezone':'Europe/Zurich','base_commit':base,
        'head_commit':head,'expected_tree':expected,'commits':[],'format_patch':[],
        'commands':commands,'no_lazy_fetch':True,'success':False}
    with tempfile.TemporaryDirectory(prefix='private-index-',dir=out) as temp:
        env=base_env.copy(); env['GIT_INDEX_FILE']=str(Path(temp)/'replay.index')
        env['GIT_OPTIONAL_LOCKS']='0'
        git('read-tree',base,env=env)
        if text('write-tree','--missing-ok',env=env)!=text('rev-parse',base+'^{tree}'):
            raise RuntimeError('Initial private index does not match base')
        previous=base
        sequence=text('rev-list','--reverse','--first-parent',base+'..'+head).splitlines()
        for number,commit in enumerate(sequence,1):
            parents=text('show','-s','--format=%P',commit).split()
            if parents!=[previous]: raise RuntimeError('Nonlinear series at '+commit)
            subject=text('show','-s','--format=%s',commit)
            diff=diffs/f'{number:04d}-{commit[:12]}.diff'
            with diff.open('wb') as stream:
                git('diff','--binary','--full-index','--no-renames','--no-ext-diff',
                    '--no-textconv',previous,commit,'--',target=stream)
            git('apply','--cached','--whitespace=nowarn',str(diff),env=env)
            tree=text('write-tree','--missing-ok',env=env)
            wanted=text('rev-parse',commit+'^{tree}')
            if tree!=wanted: raise RuntimeError('Raw diff replay tree mismatch at '+commit)
            report['commits'].append({'position':number,'commit':commit,'parent':previous,
                'subject':subject,'expected_tree':wanted,'replayed_tree':tree,'match':True,
                'diff':diff.relative_to(out).as_posix(),'diff_bytes':diff.stat().st_size,
                'diff_sha256':sha(diff),'apply_exit_code':0,'write_tree_exit_code':0})
            print(f'PASS raw {number:02d} {commit[:12]} {tree}',flush=True)
            previous=commit
        report['replayed_final_tree']=text('write-tree','--missing-ok',env=env)
        if report['replayed_final_tree']!=expected: raise RuntimeError('Final raw replay mismatch')
        patch_paths=[Path(line) for line in git('format-patch','--binary','--full-index',
            '--no-renames','--no-signature','--output-directory',str(out),base+'..'+head).decode('utf-8').splitlines() if line]
        if len(patch_paths)!=len(sequence): raise RuntimeError('Mail patch count mismatch')
        # Verify the actual distributable .patch files too, from the same base.
        git('read-tree',base,env=env)
        for patch,entry in zip(patch_paths,report['commits']):
            git('apply','--cached','--whitespace=nowarn',str(patch),env=env)
            tree=text('write-tree','--missing-ok',env=env)
            if tree!=entry['expected_tree']: raise RuntimeError('Mail patch replay mismatch '+patch.name)
            report['format_patch'].append({'file':patch.name,'commit':entry['commit'],
                'bytes':patch.stat().st_size,'sha256':sha(patch),'replayed_tree':tree,
                'match':True,'apply_exit_code':0,'write_tree_exit_code':0})
            print(f'PASS mail {entry["position"]:02d} {entry["commit"][:12]} {tree}',flush=True)
        report['mail_replayed_final_tree']=text('write-tree','--missing-ok',env=env)
    report['normal_index_sha256_before']=before
    report['normal_index_sha256_after']=sha(real_index)
    report['normal_index_unchanged']=before==report['normal_index_sha256_after']
    if not report['normal_index_unchanged']: raise RuntimeError('Normal index changed concurrently')
    report['success']=True
    (out/'replay-manifest.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    document='\n'.join([
        '# Nachweis der Feature-Patchserie','',f'Basis: `{base}`',f'Fork-Head: `{head}`',
        f'Vergleichs-Tree: `{expected}`','',
        f'Alle **{len(sequence)} Commits** wurden zweimal in einen externen privaten `GIT_INDEX_FILE` eingespielt:',
        'zuerst als bytegenaue rohe Git-Diffs (`--binary --full-index`), danach als die',
        'tatsächlich ausgelieferten nummerierten Format-Patch-Dateien.',
        'Jede Stufe wurde mit `git apply --cached` angewendet. Nach jeder Stufe stimmt',
        '`git write-tree --missing-ok` exakt mit dem ursprünglichen Commit-Tree überein.','',
        f'Endergebnis beider Durchläufe: `{expected}` — **identisch**.',
        'Der normale Repository-Index blieb nach SHA-256-Vergleich unverändert.',
        'Keine Arbeitsdatei wurde verändert oder ausgecheckt.','',
        'Unveränderte Baseline-Blobs dürfen im Partial Clone fehlen; deren bekannte',
        'Objekt-IDs bleiben unverändert. `GIT_NO_LAZY_FETCH=1` verhindert Downloads.',
        'Geänderte Inhalte werden aus den Patches vollständig neu gehasht.','',
        '`replay-manifest.json` enthält pro Commit die Tree-IDs, Patch-/Diff-SHA-256,',
        'Exitcodes und die tatsächlich ausgeführten Git-Kommandos.',
        '`replay-diffs/` enthält die rohen angewendeten Diffs; `replay-objects/` die',
        'beim Prüfen erzeugten Git-Objekte. Die nummerierten `.patch` sind die Serie.','',
        'Dieser Nachweis belegt die vollständige Rekonstruktion des Quellbaums auf',
        'der festgelegten Basis. Er belegt keine konfliktfreie Anwendung auf einem',
        'unbekannten zukünftigen Upstream und ersetzt keinen GUI-Build.','',
        '## Wiederholen','',
        '`export_and_replay_patches.py` benötigt Python 3 und Git. Parameter:',
        '`--repo`, `--output` (neu/leeres Verzeichnis), `--base`, `--head`,',
        '`--expected-tree`, optional `--git`. Das Skript verändert weder normale',
        'Repository-Indizes noch Arbeitsdateien.',''])
    (out/'REPLAY-REPORT.md').write_text(document,encoding='utf-8')
    (out/'export_and_replay_patches.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({'success':True,'commits':len(sequence),'tree':expected,
        'raw_and_mail_replay':'both passed','normal_index_unchanged':True,'output':str(out)},ensure_ascii=False),flush=True)
    return 0
if __name__=='__main__': sys.exit(main())
