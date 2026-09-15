#!/usr/bin/env python3
"""Inspect the checked-in HTML via real file navigation; never mutate it."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
from verify_profile_architecture import ROOT, require

def inspect(output: Path, executable: str | None) -> dict:
    html=ROOT/'docs/index.html'
    ir=json.loads((ROOT/'docs/index.json').read_text())
    output.mkdir(parents=True,exist_ok=True)
    expected_nodes={n['id'] for n in ir['components']}
    expected_edges={e['id'] for e in ir['connections']}
    failures=[]
    requests=[]
    measurements=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=executable)
        page=browser.new_page(viewport={'width':1440,'height':900})
        page.on('pageerror',lambda error:failures.append(str(error)))
        page.on('request',lambda req:requests.append(req.url) if req.url.startswith(('http:','https:')) else None)
        page.goto(html.as_uri(),wait_until='load')
        canvas=page.locator('.diagram-container svg').first
        require(canvas.is_visible(),'missing native SVG canvas')
        nodes=canvas.locator('g[data-node-id]')
        require(set(nodes.evaluate_all('(nodes)=>nodes.map(n=>n.dataset.nodeId)'))==expected_nodes,'node coverage mismatch')
        require(all(n.is_visible() for n in nodes.all()),'a core node is hidden')
        edges=canvas.locator('path[data-edge-id]').evaluate_all('(edges)=>edges.map(e=>({id:e.dataset.edgeId,d:e.getAttribute("d"),marker:e.getAttribute("marker-end")}))')
        require({e['id'] for e in edges}==expected_edges and all(e['d'] and e['marker'] for e in edges),'directional path coverage mismatch')
        for width,height in ((1440,900),(1600,1000),(1920,1080),(2048,1320),(390,844)):
            page.set_viewport_size({'width':width,'height':height})
            page.wait_for_timeout(400)
            m=page.evaluate('({width:innerWidth,height:innerHeight,scrollWidth:document.documentElement.scrollWidth,scrollHeight:document.documentElement.scrollHeight})')
            require(m['scrollWidth']<=width and (width<1440 or m['scrollHeight']<=height),'viewport overflow: '+str(m))
            measurements.append(m)
            page.screenshot(path=str(output/f'light-{width}.png'),full_page=True)
        page.set_viewport_size({'width':1440,'height':900})
        target=sorted(expected_nodes)[0]
        canvas.locator('[data-node-id="'+target+'"]').click()
        require(page.locator('#focus-chip').is_visible() and target in page.locator('#focus-id').inner_text(),'focus control failed')
        links=page.locator('#focus-evidence-links a')
        require(links.count()>0 and ir['meta']['repository']['revision'] in links.first.get_attribute('href'),'source link is not pinned')
        page.locator('#btn-reach-downstream').click()
        require(page.locator('#btn-reach-downstream').get_attribute('aria-pressed')=='true','reach control failed')
        page.locator('#btn-focus-clear').click()
        page.locator('#btn-node-finder').click()
        page.locator('#node-finder-input').fill(target)
        require(page.locator('#node-finder-results').is_visible(),'finder failed')
        page.locator('#node-finder-close').click()
        before=page.locator('html').get_attribute('data-theme')
        page.locator('#btn-theme').click()
        page.wait_for_timeout(500)
        require(page.locator('html').get_attribute('data-theme')!=before,'theme control failed')
        for width,height in ((1440,900),(2048,1320)):
            page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(400)
            page.screenshot(path=str(output/f'dark-{width}.png'),full_page=True)
        require(not failures and not requests,'browser errors or unexpected network: '+str((failures,requests)))
        report={'ok':True,'file_navigation':True,'transport':'file','html_sha256':hashlib.sha256(html.read_bytes()).hexdigest(),'browser':browser.version,'nodes':len(expected_nodes),'directional_paths':len(expected_edges),'viewports':measurements,'page_errors':failures,'http_requests':requests,'visual_review':'pending'}
        browser.close()
    (output/'browser.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--executable',default=shutil.which('google-chrome') or shutil.which('chromium'))
    args=parser.parse_args()
    print(json.dumps(inspect(args.output,args.executable),indent=2))
