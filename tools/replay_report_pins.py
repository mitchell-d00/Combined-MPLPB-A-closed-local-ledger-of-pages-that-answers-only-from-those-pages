"""Replay sealed PR-body fixtures through the real CLI with mocked HTTP only."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--runtime', type=Path, required=True)
    parser.add_argument('--fixtures', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = args.fixtures.read_bytes()
    frozen = json.loads(raw)
    runtime = args.runtime.resolve()
    bridge = runtime / 'tools/mplpb_agent_bridge.mjs'
    runs = []
    for fixture in frozen['fixtures']:
        for role in ('al', 'betty'):
            # No network implementation remains available to the CLI. Every
            # request must be one of these three exact public mock endpoints.
            data = dict(body=fixture['body'], head=frozen['head'], role=role)
            preload = """
import assert from 'node:assert/strict';
const data = DATA;
const repo = 'https://github.com/synthetic-owner/synthetic-repo';
const api = 'https://api.github.com/repos/synthetic-owner/synthetic-repo/pulls';
let calls = 0;
globalThis.fetch = async reference => {
 const url = String(reference);
 calls++;
 if (calls === 1) {
  assert.equal(url, 'https://raw.githubusercontent.com/synthetic-owner/synthetic-repo/HEAD/.well-known/mplpb.json');
  return {ok:true,json:async()=>({repository:repo,team_building:{roles:{[data.role]:{name:data.role}}}})};
 }
 if (calls === 2) {
  assert.equal(url, api+'?state=all&sort=created&direction=desc&per_page=1');
  return {ok:true,json:async()=>[{number:101}]};
 }
 assert.equal(calls, 3);
 assert.equal(url, api+'/101');
 return {ok:true,json:async()=>({html_url:repo+'/pull/101',state:'open',draft:false,merged:false,
  head:{sha:data.head,repo:{full_name:'synthetic-fork/synthetic-repo'}},body:data.body})};
};
process.on('exit',()=>assert.equal(calls,3));
""".replace('DATA', json.dumps(data))
            preloader = 'data:text/javascript;base64,' + base64.b64encode(preload.encode()).decode()
            command = ['node', '--import', preloader, str(bridge),
                       'https://github.com/synthetic-owner/synthetic-repo', '--'+role]
            result = dict(case=fixture['id'], role=role, timeout_seconds=30,
                          expected=fixture['expected'], passed=False, false_current=False)
            try:
                completed = subprocess.run(command, cwd=runtime, capture_output=True, text=True, timeout=30)
                result.update(exit_code=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)
                if completed.returncode == 0:
                    live = json.loads(completed.stdout)['live_pull_request']
                    actual = dict(report_head=live['report_head'], match=live['report_matches_current_head'])
                    actual['status'] = 'match' if actual['match'] else 'missing' if actual['report_head'] is None else 'stale'
                    result.update(actual=actual, passed=actual == fixture['expected'],
                                  false_current=actual['match'] and not fixture['expected']['match'])
            except (subprocess.TimeoutExpired, ValueError, KeyError) as error:
                result['error'] = str(error)
            runs.append(result)
    report = dict(schema='mplpb-report-pin-replay-v1', mocked_http_only=True,
                  fixture_sha256=hashlib.sha256(raw).hexdigest(),
                  bridge_sha256=hashlib.sha256(bridge.read_bytes()).hexdigest(),
                  summary=dict(executions=len(runs), passed=sum(r['passed'] for r in runs),
                               failed=sum(not r['passed'] for r in runs),
                               false_current=sum(r['false_current'] for r in runs)), runs=runs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report['summary']))
    return 0 if report['summary']['failed'] == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
