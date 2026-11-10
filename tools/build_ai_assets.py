"""Reconstruct pinned optional browser-AI runtime assets without fetching models."""
import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
BEGIN='<!-- BEGIN OPTIONAL AI HELPER -->'
END='<!-- END OPTIONAL AI HELPER -->'
JS_BEGIN='// BEGIN OPTIONAL AI HELPER SCRIPT'
JS_END='// END OPTIONAL AI HELPER SCRIPT'


def runtime(root=ROOT):
    base=Path(root)/'assets/ai'
    manifest=json.loads((base/'manifest.json').read_text())['runtime']
    chunks=[]
    for part in manifest['parts']:
        path=Path(part['path'])
        if path.is_absolute() or '..' in path.parts:raise ValueError('Unsafe AI runtime part path')
        raw=(base/path).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=part['sha256']:raise ValueError('Optional AI runtime part differs from pin')
        chunks.append(base64.b64decode(raw,validate=False))
    packed=b''.join(chunks)
    if hashlib.sha256(packed).hexdigest()!=manifest['gzip_sha256']:raise ValueError('Optional AI runtime archive differs from pin')
    raw=gzip.decompress(packed)
    if len(raw)!=manifest['uncompressed_bytes'] or hashlib.sha256(raw).hexdigest()!=manifest['uncompressed_sha256']:
        raise ValueError('Optional AI runtime bytes differ from pin')
    patch_pin=manifest.get('local_patch')
    if patch_pin:
        path=Path(patch_pin['path'])
        if path.is_absolute() or '..' in path.parts:raise ValueError('Unsafe AI runtime patch path')
        patch_bytes=(base/path).read_bytes()
        if hashlib.sha256(patch_bytes).hexdigest()!=patch_pin['sha256']:raise ValueError('AI runtime patch differs from pin')
        patch=json.loads(patch_bytes)
        if patch.get('schema')!='mplpb-runtime-literal-patch-v1' or patch.get('id')!=patch_pin['id'] or patch.get('upstream_sha256')!=manifest['uncompressed_sha256']:
            raise ValueError('AI runtime patch does not identify this upstream')
        source=raw.decode('utf-8')
        for change in patch['changes']:
            if change['expected_occurrences']!=1 or source.count(change['old'])!=1:raise ValueError('AI runtime patch context differs')
            source=source.replace(change['old'],change['new'])
        raw=source.encode('utf-8')
        if len(raw)!=patch_pin['output_bytes'] or hashlib.sha256(raw).hexdigest()!=patch_pin['output_sha256']:raise ValueError('Patched AI runtime differs from output pin')
    return raw


def build(output,root=ROOT):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    raw=runtime(root)
    model=json.loads((Path(root)/'assets/ai/model.json').read_text())
    manifest=json.loads((Path(root)/'assets/ai/manifest.json').read_text())['runtime']
    if model['runtime']['sha256']!=hashlib.sha256(raw).hexdigest() or model['runtime'].get('local_patch')!=manifest.get('local_patch',{}).get('id'):
        raise ValueError('Model configuration runtime pin differs from built runtime')
    catalog=json.loads((Path(root)/'assets/ai/models.json').read_text())
    ids=set()
    if catalog.get('schema')!='mplpb-model-catalog-v1' or not catalog.get('models'):raise ValueError('Invalid MIT model catalog')
    for entry in catalog['models']:
        if entry.get('license_spdx')!='MIT':raise ValueError('Only MIT-licensed models may be delivered')
        mid=entry['model_id'];record=entry['record']
        if mid in ids or record['model_id']!=mid:raise ValueError('Duplicate or inconsistent model identity')
        ids.add(mid)
        if entry['runtime']!=model['runtime']:raise ValueError('Catalog runtime pin differs from built runtime')
        notice=Path(entry['license_file'])
        if notice.is_absolute() or len(notice.parts)!=1:raise ValueError('Unsafe model license path')
        license_bytes=(Path(root)/'assets/ai'/notice).read_bytes()
        if hashlib.sha256(license_bytes).hexdigest()!=entry['license_sha256'] or b'MIT License' not in license_bytes:raise ValueError('MIT license notice differs from pin')
        if record.get('integrity',{}).get('onFailure')!='error' or not all(record['integrity'].get(key,'').startswith('sha256-') for key in ('config','model_lib')):raise ValueError('Model config and library must be integrity pinned')
        if entry['minimum_tensor_buffer_bytes']<=0 or entry['weights']['tensor_download_bytes']<=0:raise ValueError('Invalid model resource sizes')
    if catalog.get('default_model_id') not in ids:raise ValueError('Default model is missing from catalog')
    (output/'webllm.mjs').write_bytes(raw)
    for name in ('model.json','models.json','manifest.json','LICENSE-WEBLLM.txt','LICENSE-PHI4.txt','LICENSE-LOGLEVEL.txt',*(entry['license_file'] for entry in catalog['models'])):
        shutil.copyfile(Path(root)/'assets/ai'/name,output/name)
    if (Path(root)/'assets/ai/patches').exists():
        shutil.copytree(Path(root)/'assets/ai/patches',output/'patches',dirs_exist_ok=True)
    return {'runtime_bytes':(output/'webllm.mjs').stat().st_size,'models_downloaded':False,'paid_service_configured':False}


def markup(root=ROOT):
    return BEGIN+'''\n<details id="ai-helper" class="panel" style="max-width:1100px;margin:16px auto;padding:16px">
<summary><strong>Builder and chat helper · optional free browser AI</strong></summary>
<p>Everyone can use this page. No paid AI service or account is required. The optional pretrained model runs on a compatible visitor device; it does not run on GitHub’s servers.</p>
<label>AI model · MIT licenses only <select id="ai-helper-model" aria-describedby="ai-helper-model-info" disabled></select></label>
<p id="ai-helper-model-info" class="small" role="status">Loading model choices. No model weights are downloaded until you press Load.</p>
<button id="ai-helper-load" type="button" disabled>Load selected model</button>
<label><input id="ai-helper-use-model" type="checkbox" disabled> Use loaded AI for proposals</label>
<p id="ai-helper-model-status" role="status" aria-live="polite">No AI model loaded. Downloading and initialization are separate stages.</p>
<details><summary>Model loading details</summary><pre id="ai-helper-load-report" style="white-space:pre-wrap;overflow-wrap:anywhere"></pre></details>
<button id="ai-helper-export-load" type="button">Export model load report</button>
<p class="small">This local report includes browser/GPU capabilities, load progress and available runtime errors. It is not uploaded automatically and does not include your source questions. A 100% download does not establish that the model can initialize.</p>
<p class="small">Phi-1.5 is the smallest default; successful iPad loading is not guaranteed. Working memory estimates are not measured free memory. To change models after a load attempt, choose one and reload. MPLPB remains available. No fine-tuning or automatic training on your conversations takes place.</p>
<div style="display:flex;gap:8px;flex-wrap:wrap">
<label>Collection <select id="ai-helper-corpus" aria-label="Helper collection"></select></label>
<label>Task <select id="ai-helper-mode"><option value="ask">Ask sources</option><option value="chat">Chat with MPLPB</option><option value="build">Build a collection/source</option><option value="general">General chat · model text is unverified</option></select></label>
</div>
<label>Your request <textarea id="ai-helper-message" rows="3" maxlength="4000" style="width:100%;box-sizing:border-box" placeholder="Ask a question, discuss your sources, or describe what you want to build."></textarea></label>
<details><summary>Provide source text for a reviewed import</summary>
<label>Title <input id="ai-helper-title" maxlength="200"></label>
<label>Source URL <input id="ai-helper-url" type="url" placeholder="https://…"></label>
<label>Exact supplied text <textarea id="ai-helper-source" rows="5" maxlength="10000" style="width:100%;box-sizing:border-box"></textarea></label>
<p class="small">Choose Build to propose an import. Supplied text is saved exactly after review. An AI-generated draft is labeled unverified; saving it does not ratify its truth or authorship.</p>
</details>
<button id="ai-helper-send" type="button">Send to helper</button>
<p id="ai-helper-status" role="status" aria-live="polite">No model loaded. The existing MPLPB engine and manual reviewed builder are available.</p>
<pre id="ai-helper-output" style="white-space:pre-wrap;overflow-wrap:anywhere"></pre>
<pre id="ai-helper-review" style="white-space:pre-wrap;overflow-wrap:anywhere"></pre>
<button id="ai-helper-approve" type="button" hidden>Save this reviewed draft</button>
<button id="ai-helper-cancel" type="button" hidden>Cancel draft</button>
<details><summary>Inspect the original engine result and evidence</summary><pre id="ai-helper-evidence" style="white-space:pre-wrap;overflow-wrap:anywhere"></pre></details>
<details><summary>Inspect inputs, model proposals and actual execution paths</summary><pre id="ai-helper-trace" style="white-space:pre-wrap;overflow-wrap:anywhere"></pre></details>
<button id="ai-helper-export" type="button">Export this tab’s interaction trace</button>
<p class="small">The trace separates proposals, approvals and engine results. It is not a model’s private reasoning. General model context is limited and held in this tab; export before closing. Your browser’s pages are not automatically shared with other visitors.</p>
</details>
'''+END


def embed(root=ROOT,check=False):
    path=Path(root)/'index.html';html=path.read_text();original=html;block=markup(root)
    if BEGIN in html:
        start=html.index(BEGIN);end=html.index(END,start)+len(END)
        if html[end:end+1]=='\n':end+=1
        html=html[:start]+html[end:]
    if JS_BEGIN in html:
        start=html.index(JS_BEGIN);end=html.index(JS_END,start)+len(JS_END)
        if html[end:end+1]=='\n':end+=1
        html=html[:start]+html[end:]
    scripts='\n'.join((Path(root)/'browser'/name).read_text() for name in ('ai-helper.js','ai-model-loader.js','ai-helper-ui.js'))
    script=JS_BEGIN+'\ndocument.addEventListener(\'DOMContentLoaded\',function(){\n'+scripts+'\n});\n'+JS_END+'\n'
    # Keep the desktop single-inline-script/CSP contract. The helper markup is
    # parsed after that script, so initialize it only once DOM parsing completes.
    html=html.replace('</script>',script+'</script>',1)
    updated=html.replace('</body>',block+'\n</body>',1)
    if check:
        if updated!=original:raise ValueError('Optional helper HTML is stale; run python tools/build_ai_assets.py --embed-helper')
    else:path.write_text(updated)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path);p.add_argument('--embed-helper',action='store_true');p.add_argument('--check',action='store_true')
    args=p.parse_args()
    if args.embed_helper or args.check:embed(check=args.check)
    if args.output:print(json.dumps(build(args.output),indent=2))
    elif not (args.embed_helper or args.check):p.error('Choose --output, --embed-helper or --check')


if __name__=='__main__':main()
