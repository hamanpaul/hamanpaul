#!/usr/bin/env python3
"""Read-only gates for this profile's public-source architecture projection."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]

def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))

def safe_path(path: str) -> str:
    p = PurePosixPath(path)
    require(not p.is_absolute() and '..' not in p.parts and str(p) == path, 'unsafe path: ' + path)
    return path

def git_bytes(root: Path, revision: str, path: str) -> bytes:
    require(bool(re.fullmatch('[0-9a-f]{40}', revision)), 'unpinned revision')
    return subprocess.check_output(['git', '-C', str(root), 'show', revision + ':' + safe_path(path)])

def check(root: Path, facts=None, ir=None) -> dict:
    facts = load(root/'docs/facts.json') if facts is None else facts
    ir = load(root/'docs/index.json') if ir is None else ir
    require(set(facts) == {'schema_version','document_type','repository','scope','components','boundaries','relations','unknowns','conflicts'}, 'facts schema keys changed')
    require(facts['schema_version'] == 1 and facts['document_type'] == 'architecture-facts', 'unsupported facts schema')
    require(facts['repository']['url'] == 'https://github.com/hamanpaul/hamanpaul', 'wrong repository')
    revision = facts['repository']['revision']
    require(bool(re.fullmatch('[0-9a-f]{40}', revision)), 'unpinned revision')
    subprocess.run(['git','-C',str(root),'merge-base','--is-ancestor',revision,'HEAD'],check=True)
    lock=load(root/'docs/source-lock.json')
    require(digest((root/'docs/facts.json').read_bytes())==load(root/'docs/toolchain.json')['facts_sha256'],'facts differ from reviewed candidate')
    manifest=load(root/'docs/source-manifest.json')
    require((root/'docs/source-manifest.json').read_bytes() == git_bytes(root,revision,'docs/source-manifest.json'), 'manifest differs from source pin')
    sources={}
    for s in manifest['sources']:
        path=safe_path(s['snapshot'])
        require(path.startswith('docs/evidence/') and path.endswith('/README.md'), 'source is not a README snapshot')
        require(s['visibility']=='public' and s['repository'].startswith('hamanpaul/'), 'non-public source')
        require(bool(re.fullmatch('[0-9a-f]{40}',s['revision'])), 'source revision is not pinned')
        require(s['url']=='https://github.com/'+s['repository']+'/blob/'+s['revision']+'/README.md', 'source URL mismatch')
        data=git_bytes(root,revision,path)
        require((root/path).read_bytes()==data,'source snapshot drift: '+path)
        blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        require(blob==s['blob_sha']==lock['sources'][s['repository'].split('/',1)[1]],'source blob mismatch: '+path)
        require(digest(data)==s['sha256'],'source digest mismatch: '+path)
        require(path not in sources,'duplicate snapshot')
        sources[path]=data
    require(len(sources)==len(lock['sources']),'source inventory mismatch')
    for group in ('components','boundaries','relations','unknowns','conflicts'):
        ids=[x['id'] for x in facts[group]]
        require(ids==sorted(set(ids)),group+' IDs must be unique and sorted')
        require(all(re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',x) for x in ids),'invalid stable ID')
    # This profile intentionally contains no invented trust/deployment boundaries.
    require(facts['boundaries']==[] and facts['conflicts']==[], 'new boundary/conflict schema requires explicit verifier extension')
    for item in facts['components']+facts['relations']:
        require(item['basis']=='declared','this public-README profile supports declared facts only')
        anchors=item['evidence']
        require(bool(anchors),'missing source evidence')
        require(anchors==sorted(anchors,key=lambda a:(a['path'],a['line'],a['end_line'])),'unsorted evidence')
        for a in anchors:
            require(set(a)=={'path','line','end_line','excerpt_sha256','claim'},'anchor schema changed')
            require(a['path'] in sources,'unknown or self-generated evidence')
            lines=sources[a['path']].splitlines(keepends=True)
            require(1<=a['line']<=a['end_line']<=len(lines),'invalid evidence range')
            require(digest(b''.join(lines[a['line']-1:a['end_line']]))==a['excerpt_sha256'],'evidence hash mismatch')
            require(bool(a['claim'].strip()),'empty claim')
    require(ir['schema_version']==1 and ir['diagram_type']=='architecture','wrong native IR type')
    require(ir['meta']['quality_profile']=='showcase','showcase required')
    require(ir['meta']['repository']==dict(facts['repository'],provider='github'),'IR source pin drift')
    require(ir.get('boundaries',[])==[],'unexpected native boundary')
    expected=[]
    for c in facts['components']:
        n={k:c[k] for k in ('id','label','type','sublabel','tag') if k in c}
        n['sources']=[{k:a[k] for k in ('path','line','end_line')} for a in c['evidence'][:3]]
        expected.append(n)
    actual=[{k:c[k] for k in ('id','label','type','sublabel','tag','sources') if k in c} for c in ir['components']]
    require(expected==actual,'facts/native component projection drift')
    ids={c['id'] for c in facts['components']}
    require(all(e['from'] in ids and e['to'] in ids for e in facts['relations']),'dangling relation endpoint')
    keys=('id','from','to','label','variant')
    require([{k:e[k] for k in keys if k in e} for e in facts['relations']]==[{k:e[k] for k in keys if k in e} for e in ir['connections']],'facts/native relation projection drift')
    readme=(root/'README.md').read_text(encoding='utf-8')
    for target in re.findall(r'\]\((docs/[^)#]+)',readme):
        require((root/safe_path(target)).is_file(),'broken README link: '+target)
    return {'ok':True,'source_revision':revision,'public_sources':len(sources),'components':len(ids),'relations':len(facts['relations'])}

def native_check(root: Path, engine: Path, generate: bool=False) -> dict:
    toolchain=load(root/'docs/toolchain.json')
    cli=engine/'bin/archify.mjs'
    tree=hashlib.sha256()
    for entry in sorted(engine.rglob('*')):
        if entry.is_file():tree.update(entry.relative_to(engine).as_posix().encode()+b'\0'+hashlib.sha256(entry.read_bytes()).digest())
    require(tree.hexdigest()==toolchain['archify_tree_sha256'],'wrong Archify source tree')
    require(digest(cli.read_bytes())==toolchain['archify_cli_sha256'],'wrong Archify CLI pin')
    with tempfile.TemporaryDirectory(prefix='profile-native-') as tmp:
        out=Path(tmp)/'index.html'
        cp=subprocess.run(['node',str(cli),'deliver','architecture',str(root/'docs/index.json'),str(out),'--quality','showcase','--repo-root',str(root),'--json'],capture_output=True,text=True,check=True)
        receipt=json.loads(cp.stdout)
        require(receipt['ok'] and receipt['validation']=={'checksPassed':9,'checkCount':9,'compositionProfile':'showcase','compositionStatus':'pass','errors':0,'warnings':0},'native showcase failed')
        require(receipt['artifact']['sha256']==toolchain['artifact_sha256'],'native artifact differs from reviewed candidate')
        require(receipt['specification']['sha256']==toolchain['specification_sha256'],'native IR differs from reviewed candidate')
        if generate:
            require(not (root/'docs/index.html').exists(),'generation refuses to overwrite; remove deliberately after review')
            (root/'docs/index.html').write_bytes(out.read_bytes())
        require((root/'docs/index.html').read_bytes()==out.read_bytes(),'HTML is not exact native rendering')
        # Store no temp paths/timestamps in the persistent receipt.
        return {k:receipt[k] for k in ('ok','type','specification','artifact','validation','evidence')}

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archify-root',type=Path)
    parser.add_argument('--generate',action='store_true',help='explicit first generation; never used by read-only CI')
    parser.add_argument('--receipt',type=Path)
    a=parser.parse_args()
    if a.generate:
        require(a.archify_root is not None,'--generate requires --archify-root')
    native=native_check(ROOT,a.archify_root.resolve(),a.generate) if a.archify_root else None
    report=check(ROOT)
    if native is not None:report['native']=native
    if a.receipt:
        a.receipt.parent.mkdir(parents=True,exist_ok=True)
        a.receipt.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':
    main()
