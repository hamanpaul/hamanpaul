#!/usr/bin/env python3
"""Source-pinned, data-only documentation build. facts.json owns semantics.

The renderer is the unmodified Archify engine at ENGINE_REVISION. This tool never
executes source excerpt contents, performs runtime dispatch, or merges a PR.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

ENGINE_REVISION = 'd673e8300df60a5c8166abe78787fdc78f6b8000'
ROOT = Path(__file__).resolve().parents[1]
SEMANTIC_COMPONENT = ('id', 'type', 'label', 'sublabel', 'tag')
SEMANTIC_EDGE = ('id', 'from', 'to', 'label', 'variant')
TYPES = {'frontend','backend','database','cloud','security','messagebus','external'}
BASES = {'observed','declared','inferred'}
ID = re.compile(r'^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$')
SHA = re.compile(r'^[0-9a-f]{40}$')
ALLOWED_REPOS = {'hamanpaul','paulshaclaw','paulsha-cortex','paulsha-hippo','paulsha-conventions','testpilot-core','serialwrap','paulsha-patchmud','log-generator','ask-bridge','new-project-template','.github'}


def run(*args: str, cwd: Path = ROOT) -> bytes:
    return subprocess.check_output(list(args), cwd=cwd, stderr=subprocess.PIPE)


def load(path: Path) -> dict:
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f'duplicate JSON key: {key}')
            out[key] = value
        return out
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)


def save(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def relative(path: str) -> str:
    p = PurePosixPath(path)
    if p.is_absolute() or '..' in p.parts or '\\' in path:
        raise ValueError(f'unsafe path: {path}')
    return path


def manifest() -> dict:
    return load(ROOT/'docs/source-manifest.json')


def snapshot(sources_root: Path, *, fetch: bool) -> None:
    """Fetch only pinned public git data and copy exact original line bytes."""
    sources_root.mkdir(parents=True, exist_ok=True)
    prepared = set()
    for item in manifest()['sources']:
        url, revision = item['repository'], item['revision']
        name = url.removeprefix('https://github.com/hamanpaul/')
        if name not in ALLOWED_REPOS or not SHA.fullmatch(revision):
            raise ValueError('unapproved source repository or non-pinned revision')
        source = sources_root/name
        if name == 'hamanpaul':
            source = ROOT
        elif (name, revision) not in prepared and fetch:
            source.mkdir(parents=True, exist_ok=True)
            if not (source/'.git').exists():
                run('git','init','-q',str(source))
            run('git','-C',str(source),'fetch','--quiet','--depth=1',url,revision)
        prepared.add((name, revision))
        blob = run('git','-C',str(source),'show',f"{revision}:{relative(item['path'])}")
        lines = blob.splitlines(keepends=True)
        lo, hi = item['line'], item['end_line']
        if not (isinstance(lo,int) and isinstance(hi,int) and 1 <= lo <= hi <= len(lines)):
            raise ValueError('invalid source line range')
        excerpt = b''.join(lines[lo-1:hi])
        if hashlib.sha256(excerpt).hexdigest() != item['sha256']:
            raise ValueError(f"upstream excerpt hash mismatch: {item['id']}")
        path = relative(item['snapshot'])
        if not path.startswith('docs/evidence/'):
            raise ValueError('snapshot must remain under docs/evidence/')
        target = ROOT/path
        if fetch:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(excerpt)
        elif target.read_bytes() != excerpt:
            raise ValueError(f'upstream provenance mismatch: {path}')


def verify(facts: dict | None = None, ir: dict | None = None) -> dict:
    facts = load(ROOT/'docs/facts.json') if facts is None else facts
    ir = load(ROOT/'docs/architecture.json') if ir is None else ir
    required = {'schema_version','document_type','repository','scope','components','boundaries','relations','unknowns','conflicts'}
    if set(facts) != required or facts['schema_version'] != 1 or facts['document_type'] != 'architecture-facts':
        raise ValueError('unsupported facts contract')
    revision = facts['repository']['revision']
    if facts['repository']['url'] != 'https://github.com/hamanpaul/hamanpaul' or not SHA.fullmatch(revision):
        raise ValueError('repository must be source-pinned')
    run('git','cat-file','-e',revision+'^{commit}')
    if set(facts['scope']) != {'name','includes','excludes'}:
        raise ValueError('invalid bounded scope')
    sources = {s['snapshot']:s for s in manifest()['sources']}
    components, relations = facts['components'], facts['relations']
    if not components or len(sources) != len(manifest()['sources']):
        raise ValueError('empty components or duplicate snapshots')
    for group in ('components','relations','boundaries','unknowns','conflicts'):
        items = facts[group]
        ids = [x['id'] for x in items]
        if ids != sorted(set(ids)) or any(not ID.fullmatch(i) for i in ids):
            raise ValueError(f'unstable or duplicate IDs: {group}')
    for group, fields, optional in (
        (components, {'id','label','type','responsibility','basis','evidence'}, {'sublabel','tag','reasoning'}),
        (relations, {'id','from','to','label','basis','evidence'}, {'variant','reasoning'}),
    ):
        for item in group:
            if not fields <= set(item) or set(item)-fields-optional:
                raise ValueError('unexpected fact keys')
            if item['basis'] not in BASES or not item['evidence']:
                raise ValueError('unsupported basis or missing evidence')
            if item['basis'] == 'inferred':
                if not item.get('reasoning') or len({a['path'] for a in item['evidence']}) < 2:
                    raise ValueError('inference requires reasoning and two independent paths')
            elif 'reasoning' in item:
                raise ValueError('reasoning only belongs to inferred facts')
            anchors = item['evidence']
            if anchors != sorted(anchors, key=lambda a:(a['path'],a['line'],a['end_line'])):
                raise ValueError('unsorted evidence')
            for a in anchors:
                if set(a) != {'path','line','end_line','excerpt_sha256','claim'} or not a['claim']:
                    raise ValueError('invalid evidence anchor')
                path = relative(a['path'])
                if path not in sources:
                    raise ValueError('generated architecture cannot certify itself')
                data = run('git','show',f'{revision}:{path}')
                if data != (ROOT/path).read_bytes() or hashlib.sha256(data).hexdigest() != sources[path]['sha256']:
                    raise ValueError('source snapshot drift')
                lines = data.splitlines(keepends=True)
                lo, hi = a['line'], a['end_line']
                if not (isinstance(lo,int) and isinstance(hi,int) and 1 <= lo <= hi <= len(lines)):
                    raise ValueError('invalid evidence line range')
                if hashlib.sha256(b''.join(lines[lo-1:hi])).hexdigest() != a['excerpt_sha256']:
                    raise ValueError('evidence hash mismatch')
    node_ids = {c['id'] for c in components}
    if any(c['type'] not in TYPES or not c['responsibility'] for c in components):
        raise ValueError('invalid component type or responsibility')
    for e in relations:
        if e['from'] not in node_ids or e['to'] not in node_ids or not e['label']:
            raise ValueError('unknown endpoint or missing action label')
        if e.get('variant','default') not in {'default','emphasis','security','dashed'}:
            raise ValueError('unsupported relation variant')
    if facts['boundaries'] or facts['conflicts']:
        raise ValueError('this portfolio profile does not project trust boundaries or resolved conflicts; extend validation before adding them')
    for item in facts['unknowns']:
        if set(item) != {'id','question','impact'} or not item['question'] or not item['impact']:
            raise ValueError('invalid unknown')
    if ir['schema_version'] != 1 or ir['diagram_type'] != 'architecture' or ir['meta']['quality_profile'] != 'showcase':
        raise ValueError('native showcase IR required')
    if any(ir['meta']['repository'].get(k) != v for k,v in facts['repository'].items()):
        raise ValueError('IR source pin mismatch')
    expected=[]
    for c in components:
        p={k:c[k] for k in SEMANTIC_COMPONENT if k in c}
        p['sources']=[{k:a[k] for k in ('path','line','end_line')} for a in c['evidence'][:3]]
        expected.append(p)
    actual=[{k:c[k] for k in (*SEMANTIC_COMPONENT,'sources') if k in c} for c in ir['components']]
    if actual != expected:
        raise ValueError('IR component semantics differ from facts')
    if [{k:e[k] for k in SEMANTIC_EDGE if k in e} for e in ir['connections']] != [{k:e[k] for k in SEMANTIC_EDGE if k in e} for e in relations]:
        raise ValueError('IR relation semantics differ from facts')
    if ir.get('boundaries',[]) != []:
        raise ValueError('invented deployment or trust boundary')
    readme = (ROOT/'README.md').read_text(encoding='utf-8')
    for target in ('docs/index.html','docs/facts.json','docs/architecture.json','docs/source-manifest.json'):
        if f']({target})' not in readme:
            raise ValueError(f'missing README entry: {target}')
    return {'ok':True,'source_revision':revision,'components':len(components),'relations':len(relations),'source_excerpts':len(sources)}


def pin(revision: str) -> None:
    if not SHA.fullmatch(revision):
        raise ValueError('full source commit required')
    for name in ('facts.json','architecture.json'):
        path=ROOT/'docs'/name; data=load(path)
        owner=data if name=='facts.json' else data['meta']
        owner['repository']['revision']=revision
        save(path,data)


def render(engine: Path, *, compare: bool) -> None:
    verify()
    if run('git','-C',str(engine),'rev-parse','HEAD').decode().strip() != ENGINE_REVISION:
        raise ValueError('Archify engine pin mismatch')
    output=ROOT/'docs/index.html'
    with tempfile.TemporaryDirectory() as tmp:
        target=Path(tmp)/'index.html' if compare else output
        command=['node',str(engine/'bin/archify.mjs'),'deliver','architecture',str(ROOT/'docs/architecture.json'),str(target),'--repo-root',str(ROOT),'--quality','showcase','--json']
        receipt=json.loads(run(*command))
        if not receipt.get('ok'):
            raise ValueError('native delivery failed')
        if compare and output.read_bytes() != target.read_bytes():
            raise ValueError('HTML differs from exact native re-render')
        print(json.dumps(receipt, ensure_ascii=False))


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=('snapshot','provenance','pin','verify','render','check-html'))
    p.add_argument('--sources-root',type=Path,default=ROOT/'.architecture-sources')
    p.add_argument('--revision')
    p.add_argument('--archify-root',type=Path)
    a=p.parse_args()
    try:
        if a.command in ('snapshot','provenance'):
            snapshot(a.sources_root,fetch=a.command=='snapshot')
            print(json.dumps({'ok':True,'command':a.command}))
        elif a.command=='pin': pin(a.revision or '')
        elif a.command=='verify': print(json.dumps(verify(),ensure_ascii=False))
        elif a.command in ('render','check-html'):
            if not a.archify_root: raise ValueError('--archify-root is required')
            render(a.archify_root.resolve(),compare=a.command=='check-html')
        return 0
    except (ValueError,KeyError,OSError,subprocess.CalledProcessError) as e:
        print(f'{type(e).__name__}: {e}',file=sys.stderr)
        if isinstance(e,subprocess.CalledProcessError):
            print(e.stderr.decode('utf-8','replace'),file=sys.stderr)
        return 1

if __name__=='__main__':
    raise SystemExit(main())
