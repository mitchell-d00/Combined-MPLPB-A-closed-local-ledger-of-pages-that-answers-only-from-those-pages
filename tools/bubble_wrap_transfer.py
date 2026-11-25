"""Open the existing sealed packet only after an exact committed ZIP freeze."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from types import SimpleNamespace
import sys

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools import bubble_wrap_trial as trial
from tools import bubble_wrap_score_v3 as scorer
from tools.bubble_wrap_adapter import runtime_files, sha, snapshot


def execute(a):
    candidate=trial.read(a.candidate_freeze)
    assert sha(a.archive)==candidate['archive_sha256']
    for name,expected in candidate['tool_sha256'].items():
        assert sha(ROOT/name)==sha(a.candidate_root/name)==expected
    pins={str(p.relative_to(a.candidate_root)):sha(p) for p in runtime_files(a.candidate_root)}
    assert pins==candidate['runtime_sha256']
    proposal=ROOT/'evaluation/current-failure-inventory/proposal'
    seal=trial.read(proposal/'transfer-seal.json')
    trial.verify_frozen()
    # Create-only lock precedes reading instance bytes or the scoring key.
    trial.save(a.once,{'candidate_commit':candidate['commit'],'archive_sha256':candidate['archive_sha256'],
        'transfer_seal_sha256':sha(proposal/'transfer-seal.json'),'candidate_runs_authorized':1,
        'source_not_to_change_after_packet_open':True,'independent_preparation':'NOT_RUN'})
    key_path=a.custody/'transfer-key.json'
    assert sha(key_path)==seal['key_sha256']
    original_key=trial.read(key_path);by_id={r['id']:r for r in original_key}
    folder=trial.HOME/'transfer';folder.mkdir(exist_ok=False)
    keys,rows={},[]
    for frozen in seal['cases']:
        ident='BW-TRANSFER-'+frozen['id'];source=a.custody/'transfer/inputs'/frozen['id']
        assert snapshot(source)==frozen['files']
        packet=folder/'inputs'/frozen['id'];shutil.copytree(source,packet)
        k=by_id[frozen['id']]
        keys[ident]={'expected':'source_answer' if k['supported_source_content_target'] else 'withhold',
            'roles':{'reporter':k['reporter'],'author':k['attributed_author'],'object':k['object'],
                'inner_action':k['inner_action'],'inner_negative':k['inner_negative'],'outer_negative':False,
                'content_asserted_by_reporter':True,'conditions':[],
                'source_writer_or_unknown':k['source_header_writer'],'actual_authorship_established':False},
            'eligible_complete_witnesses':[k['full_governing_clause']]}
        rows.append({'id':ident,'original_id':frozen['id'],'family':'BW-TRANSFER','origin_prs':[103],
            'memberships':['transfer'],'packet':str(packet.relative_to(ROOT)),'files':frozen['files'],
            'case_hash':trial.digest(frozen['files']),'genre':frozen['genre'],'structure':frozen['structure'],
            'variant':frozen['variant'],'public_raw_output':True,'allowed_target_change':True,
            'original_key_sha256':seal['key_sha256'],'protected_rule':'Source-scoped report attribution; no independent actual authorship',
            'budgets':candidate['budgets'],'custody':'Same operator, templates visible, instances/key opened after candidate ZIP freeze'})
    manifest=folder/'manifest.json';key=folder/'derived-scoring-key.json'
    trial.save(manifest,{'cases':rows,'original_seal_sha256':sha(proposal/'transfer-seal.json'),
                        'original_key_sha256':seal['key_sha256'],'candidate':candidate})
    trial.save(key,keys)
    # Bind the key projection before either transfer score; original key unchanged.
    trial.save(folder/'opened-freeze.json',{'manifest_sha256':sha(manifest),'derived_key_sha256':sha(key),
        'original_key_sha256':seal['key_sha256'],'candidate_commit':candidate['commit'],
        'native_edits_after_open':False,'independent_preparation':'NOT_RUN','independent_blinding':'NOT_RUN',
        'independent_semantic_adjudication':'NOT_RUN','outside_custodian_scoring':'NOT_RUN','native_oocc':'NOT_RUN'})
    results={}
    for phase,implementation,commit in [('baseline',a.baseline_root,trial.BASELINE),
                                        ('candidate',a.candidate_root,candidate['commit'])]:
        output=a.run_output/('transfer-'+phase)
        args=SimpleNamespace(phase='transfer',implementation=implementation,source_commit=commit,
            output=output,membership=None,case_id=None,transfer_manifest=manifest)
        code=trial.run(args)
        score_path=folder/(phase+'-score.json')
        scored=scorer.score(SimpleNamespace(run=output,output=score_path,transfer_manifest=manifest,transfer_key=key))
        results[phase]={'execution_returncode':code,'score_returncode':scored,'score_sha256':sha(score_path)}
    assert pins=={str(p.relative_to(a.candidate_root)):sha(p) for p in runtime_files(a.candidate_root)}
    trial.save(folder/'completion.json',{'candidate':candidate,'results':results,
         'candidate_runs':1,'native_fingerprints_unchanged_after_open':True,
         'packet_consumed_for_future_development':True,
         'acceptance_passed':results['candidate']['execution_returncode']==results['candidate']['score_returncode']==0})
    print(json.dumps(results))
    return int(not trial.read(folder/'completion.json')['acceptance_passed'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('candidate-freeze','archive','candidate-root','baseline-root','custody','once','run-output'):
        p.add_argument('--'+n,type=Path,required=True)
    raise SystemExit(execute(p.parse_args()))
