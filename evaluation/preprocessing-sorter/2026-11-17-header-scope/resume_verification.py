"""Replay saved verification state in a fresh process; no AI continuity claim.

Run from any directory with --output NEW_DIRECTORY outside this checkout.
The repository/checkpoint is trusted development coordination, not ledger truth.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(argv)
    here=Path(__file__).resolve().parent;root=here.parents[2];out=args.output.resolve()
    if out==root or root in out.parents:raise ValueError('Use an output directory outside the checkout')
    out.mkdir(parents=True,exist_ok=False)
    state=json.loads((here/'checkpoint.json').read_text())
    if state['schema']!='mplpb-sorter-header-scope-checkpoint-v1':raise ValueError('Unknown checkpoint')
    for relative,expected in state['implementation_and_fixture_sha256'].items():
        path=(root/relative).resolve();path.relative_to(root)
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('Checkpoint byte mismatch: '+relative)
    if hashlib.sha256((here/'supplied-probe.zip').read_bytes()).hexdigest()!=state['supplied_probe_sha256']:
        raise ValueError('Supplied probe archive changed')
    for relative,expected in state.get('supplied_files_sha256',{}).items():
        path=(here/relative).resolve();path.relative_to(here)
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('Supplied probe input changed: '+relative)
    # No prior transcript, saved model session, tool credentials or source writes.
    # The existing tests are the verification rules, not a new semantic checker.
    env={k:os.environ[k] for k in ('PATH','SYSTEMROOT','WINDIR','TMPDIR','TEMP','TMP','LANG','LC_ALL','PYTHONIOENCODING') if k in os.environ}
    command=[sys.executable,'-m','unittest','tests.test_sorter','-q']
    started=time.perf_counter()
    timed_out=False
    with (out/'sorter.log').open('w') as log:
        try:
            process=subprocess.run(command,cwd=root,env=env,stdin=subprocess.DEVNULL,
                                   stdout=log,stderr=subprocess.STDOUT,timeout=120)
            exit_code=process.returncode
        except subprocess.TimeoutExpired:
            timed_out=True;exit_code=124
    report={'schema':'sorter-fresh-process-verification-v1','checkpoint_sha256':hashlib.sha256((here/'checkpoint.json').read_bytes()).hexdigest(),
            'source_and_fixture_pins_verified':True,'command':command,'exit_code':exit_code,'timed_out':timed_out,
            'wall_seconds':time.perf_counter()-started,'log':'sorter.log','private_conversation_state_used':False,
            'fresh_AI_instance_resume':'NOT RUN','minimum_model_context_tokens':None,
            'notice':'Deterministic fresh-process replay only; no historical truth or arbitrary AI resumption guarantee.'}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2));return exit_code


if __name__=='__main__':raise SystemExit(main())
