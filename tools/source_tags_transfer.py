"""Open the reserved proposal packet once after the committed ZIP is frozen."""
import argparse
import json
from pathlib import Path
import shutil
from types import SimpleNamespace

from tools.source_tags_trial import ROOT, read, save, sha, snapshot, run, score

def execute(a):
    cap=read(a.freeze);assert sha(a.archive)==cap['archive_sha256']
    def runtime(root):return {str(p.relative_to(root)):sha(p) for name in ['mplpb_answers','mplpb_combined','mplpb_work'] for p in sorted((root/name).glob('*.py'))}
    assert runtime(a.candidate)==cap['runtime_sha256']
    for path,expected in cap['tool_sha256'].items():assert sha(ROOT/path)==sha(a.candidate/path)==expected,path
    seal=read(a.seal)
    save(a.once,{'candidate_commit':cap['commit'],'archive_sha256':cap['archive_sha256'],
                 'packet_seal_sha256':sha(a.seal),'candidate_runs_authorized':1,
                 'native_edits_after_open_forbidden':True,'same_operator':True})
    # Input/key bytes are first opened only after the create-only lock above.
    assert sha(a.custody/'manifest.json')==seal['manifest_sha256']
    assert sha(a.custody/'key.json')==seal['key_sha256']
    destination=a.destination.resolve();destination.mkdir(parents=True,exist_ok=False)
    packet=destination/'packet';packet.mkdir()
    for name in ['manifest.json','key.json','seal.json']:shutil.copyfile(a.custody/name,packet/name)
    shutil.copytree(a.custody/'inputs',packet/'inputs')
    manifest=read(packet/'manifest.json');assert len(manifest['cases'])==24
    for case in manifest['cases']:assert snapshot(packet/'inputs'/case['id'])==case['files']
    results={};baseline_output=a.run_output/'baseline'
    for phase,implementation,commit in [('baseline',a.baseline,a.baseline_commit),('candidate',a.candidate,cap['commit'])]:
        output=a.run_output/phase
        executed=run(SimpleNamespace(packet=packet,implementation=implementation,output=output,source_commit=commit))
        scored=score(SimpleNamespace(packet=packet,run=output,baseline=baseline_output if phase=='candidate' else None,
                                     output=destination/(phase+'-score.json')))
        results[phase]={'execution_returncode':executed,'score_returncode':scored}
    assert runtime(a.candidate)==cap['runtime_sha256']
    for path,expected in cap['tool_sha256'].items():assert sha(ROOT/path)==expected,path
    candidate=read(destination/'candidate-score.json')
    save(destination/'completion.json',{'candidate':cap,'candidate_runs':1,
         'native_fingerprints_unchanged_after_open':True,'results':results,
         'acceptance_passed':candidate['acceptance_passed'] and results['candidate']['execution_returncode']==0,
         'packet_consumed_for_future_development':True,'same_operator':True,
         'independent_preparation':'NOT_RUN','independent_blinding':'NOT_RUN',
         'independent_semantic_adjudication':'NOT_RUN','outside_custodian_scoring':'NOT_RUN','native_oocc':'NOT_RUN'})
    print(json.dumps(results));return int(not read(destination/'completion.json')['acceptance_passed'])

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['freeze','archive','candidate','baseline','custody','seal','destination','once','run-output']:
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--baseline-commit',required=True)
    a=p.parse_args()
    for name in ['freeze','archive','candidate','baseline','custody','seal','destination','once','run_output']:
        setattr(a,name,getattr(a,name).resolve())
    raise SystemExit(execute(a))
