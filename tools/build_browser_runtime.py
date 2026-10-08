#!/usr/bin/env python3
"""Build standalone HTML from explicit repo paths and a pinned Pyodide core."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import tarfile
import tempfile
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
VERSION = '314.0.7'
CORE_SHA256 = '2abdcc2e35208af406e07724cffa85bc582ced97e9028383ecf5462541393f95'
CORE_URL = f'https://github.com/pyodide/pyodide/releases/download/{VERSION}/pyodide-core-{VERSION}.tar.bz2'
CORE_FILES = ('pyodide.js','pyodide.asm.mjs','pyodide.asm.wasm','python_stdlib.zip','pyodide-lock.json')

def encode(raw): return base64.b64encode(raw).decode('ascii')

def build(core_archive, output):
    raw = Path(core_archive).read_bytes()
    if hashlib.sha256(raw).hexdigest() != CORE_SHA256:
        raise ValueError('Pyodide core archive differs from the published release digest')
    with tarfile.open(core_archive) as archive:
        runtime = {name: encode(archive.extractfile('pyodide/'+name).read()) for name in CORE_FILES}
    folders = ('mplpb_combined', 'tools', 'examples/studio', 'examples/patch-canned',
               'examples/clarification-dogs', 'examples/provenance-gate/separate',
               'examples/system', 'examples/chat-logic', 'evaluation/wiki', 'docs/patch-canned/supplied', 'browser')
    paths = set()
    for folder in folders:
        paths.update(p for p in (ROOT / folder).rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.tmp') and p.name != '.lock')
    paths.add(ROOT / 'LICENSE')
    files = {p.relative_to(ROOT).as_posix(): encode(p.read_bytes()) for p in sorted(paths)}
    manifest = {name: hashlib.sha256(base64.b64decode(value)).hexdigest() for name,value in files.items()}
    bundle = {'schema': 1, 'runtime_version': VERSION, 'runtime_release_sha256': CORE_SHA256,
              'runtime': runtime, 'runtime_manifest': {k: hashlib.sha256(base64.b64decode(v)).hexdigest() for k,v in runtime.items()}, 'files': files, 'manifest': manifest, 'worker': (ROOT/'browser/worker.js').read_text()}
    html = (ROOT/'index.html').read_text()
    html = re.sub(r'<section id="connection".*?</section>',
                  '<section id="connection" class="panel" hidden><h2>Open your browser ledger.</h2>'
                  '<p>The embedded Python engine checks your sealed pages inside this browser. '
                  'No local server is needed. Allow browser storage to resume your session.</p>'
                  '<div id="connection-error" class="small"></div></section>', html, count=1, flags=re.S)
    html = html.replace('async function api(url,options){const response=await fetch(url,options),data=await response.json();if(!response.ok)throw Error(data.error||\'Request failed\');return data;}',
                        'async function api(url,options){return browserApi(url,options);}')
    ending = "if(location.protocol==='file:')$('connection').hidden=false;else boot();"
    if ending not in html: raise ValueError('UI bootstrap changed; update the browser builder')
    html = html.replace(ending, 'startBrowserRuntime();')
    html = html.replace('<script>\n', '<script>\n' + (ROOT/'browser/client.js').read_text() + '\n', 1)
    encoded = json.dumps(bundle, ensure_ascii=True, separators=(',', ':')).replace('<', '\\u003c')
    html = html.replace('<script>\n', '<script id="mplpb-runtime-bundle" type="application/json">'+encoded+'</script>\n<script>\n', 1)
    html = html.replace('Python must be running locally.', 'Python runs inside this browser through WebAssembly.')
    html = html.replace('Browser storage holds a session ID, not source text.', 'Browser IndexedDB holds this runtime’s sessions and imported captures. Browser clearing can erase them; export important transcripts.')
    html = html.replace('Opening index.html alone displays launcher instructions.', 'This standalone HTML embeds the engine, pages and Python runtime.')
    html = html.replace('The app reads its configured ledger and save slot; it does not crawl local folders.', 'The app uses its bundled ledger and browser save slot; it does not crawl local folders.')
    html = html.replace('Chat turns and declared notes use a local save slot and resume after refresh or app relaunch.', 'Chat turns, declared notes and imported captures use this browser’s IndexedDB save slot and resume after refresh.')
    html = html.replace('Browser storage holds a session ID, not source text.', 'Browser storage holds sessions and imported captures for this mode.')
    html = html.replace('Questions and source text are not saved there.', 'This browser stores sessions and imported captures; export before clearing browser data.')
    html = html.replace('Questions and source text are not saved to browser storage.', 'Standalone mode stores session turns and captures in browser IndexedDB.')
    html = html.replace('No source bodies or questions are saved to browser storage.', 'Session turns and imported sources are saved in browser IndexedDB. This journal is separate and lasts for this tab.')
    html = html.replace('Browser storage holds a session ID, not source text.', 'Browser storage holds sessions and imported captures.')
    html = html.replace('python3 launch.py --root /path/to/corpus', 'Bundled corpora are ready. Use search TOPIC and import Exact title to add public Wikipedia pages.')
    html = html.replace('The journal lasts for this tab only.', 'The journal lasts for this tab only. Session storage belongs to this browser and origin; it is not shared with the desktop server.')
    html = html.replace('Local reader unavailable:', 'Browser runtime unavailable:')
    html = html.replace('mplpb-session-id', 'mplpb-browser-session-id').replace('mplpb-ui-preferences', 'mplpb-browser-ui-preferences')
    html = html.replace('mplpb-collection-sessions', 'mplpb-browser-collection-sessions').replace('mplpb-crawler-url','mplpb-browser-crawler-url').replace('mplpb-guide-choice','mplpb-browser-guide-choice')
    # Browser mode has its own exact self-reference transport notice, shown on every screen.
    html = html.replace('<footer class="footer">', '<footer class="footer">Standalone WebAssembly mode · no Python server · saved in this browser.<br>')
    output = Path(output); output.parent.mkdir(parents=True, exist_ok=True); output.write_text(html, encoding='utf-8')
    return {'output': str(output), 'bytes': output.stat().st_size, 'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
            'bundled_files': len(files), 'pyodide': VERSION, 'core_release_sha256': CORE_SHA256}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--core-archive', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT/'dist/MPLPB_Browser.html')
    args = parser.parse_args()
    if args.core_archive:
        result = build(args.core_archive, args.output)
    else:
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp)/'core.tar.bz2'
            with urlopen(CORE_URL, timeout=45) as response: raw = response.read(8_000_001)
            archive.write_bytes(raw)
            result = build(archive, args.output)
    print(json.dumps(result, indent=2))

if __name__ == '__main__': main()
