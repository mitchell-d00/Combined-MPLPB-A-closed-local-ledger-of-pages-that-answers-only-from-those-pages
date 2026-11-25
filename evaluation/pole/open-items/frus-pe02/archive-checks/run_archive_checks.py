import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess
import time

parser = argparse.ArgumentParser()
parser.add_argument('group', choices=['software', 'native', 'browser'])
parser.add_argument('--root', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
output = args.output.resolve()
output.mkdir(parents=True, exist_ok=True)
commands = {
 'software': [
  ['python','tools/build_handoff.py','--check'],
  ['python','-m','tools.audit_documentation'],
  ['python','tools/check_repository_infrastructure.py'],
  ['python','tools/replay_report_pins.py','--runtime','.', '--fixtures','evaluation/report-pins/2026-11-25/fixtures.json','--output',str(output/'frozen-replay.json')],
  ['python','-m','unittest','tests.test_ledger_ui','-q'],
  ['node','tests/javascript-api.cjs'],
  ['python','tools/check_ui_script.py'],
  ['node','tools/check_browser_transport.cjs'],
  ['node','--check','tools/mplpb_agent_bridge.mjs'],
  ['node','tests/documentary-render.cjs'],
  ['node','tests/browser-ai-helper.cjs'],
  ['node','tests/browser-model-loader.cjs'],
  ['node','tests/browser-webgpu-limits.cjs'],
  ['node','crawler/test_worker.mjs'],
  ['node','crawler/test_historical.mjs'],
 ],
 'native': [
  ['python','-m','unittest','tests.test_integrity_hunt','tests.test_record','tests.test_ledger','tests.test_literal_evidence','tests.test_answer_reliability','tests.test_answer_support','-q'],
  ['python','-m','tools.evaluate_public_evidence','--output',str(output/'public-controls.json'),'--require-capabilities'],
  ['python','-m','unittest','discover','-s','tests','-q'],
 ],
 'browser': [
  ['python','tools/build_browser_runtime.py','--core-archive','/workspace/pyodide-core.tar.bz2','--output','dist/index.html'],
  ['node','tools/check_browser_wasm.mjs','/workspace/pyodide-runtime/pyodide','dist/index.html'],
  ['python','/workspace/run_verified_browser.py','--root','.', '--output',str(output/'verified-browser.json'),'--preview-dir','dist'],
 ],
}
results=[]
for number,command in enumerate(commands[args.group]):
    start=time.monotonic()
    stem=args.group+'-'+str(number+1)
    row={'argv':command,'cwd':str(args.root.resolve()),'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    env=dict(os.environ, PLAYWRIGHT_BROWSERS_PATH='/workspace/pw-browsers')
    try:
        with (output/(stem+'.stdout.log')).open('w') as stdout, (output/(stem+'.stderr.log')).open('w') as stderr:
            process=subprocess.run(command,cwd=args.root,env=env,stdout=stdout,stderr=stderr,timeout=1800)
        row['exit_code']=process.returncode
    except subprocess.TimeoutExpired:
        row.update(exit_code=None,error='Timed out after 1800 seconds')
    row.update(seconds=round(time.monotonic()-start,3),stdout=stem+'.stdout.log',stderr=stem+'.stderr.log')
    results.append(row)
    (output/(args.group+'.json')).write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(row),flush=True)
raise SystemExit(0 if all(row['exit_code']==0 for row in results) else 1)
