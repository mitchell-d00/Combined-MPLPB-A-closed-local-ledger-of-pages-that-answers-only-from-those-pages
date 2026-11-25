"""Join immutable executions/scores; do not confuse preservation with coverage."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.audit_bubble_wrap_delivery import audit
from tools.bubble_wrap_trial import read,save,sha,HOME


def review():
    integrity=audit(ROOT)
    for name in ('scorer-amendment-v2.json','scorer-amendment-v3.json','delivery-audit-freeze.json'):
        for path,expected in read(HOME/name)['files'].items():
            assert sha(ROOT/path)==expected,'Changed versioned scorer/observer seal'
    summaries=[]
    for link in sorted((HOME/'run-ledger').glob('*.json')):
        entry=read(link);path=ROOT/entry['record'];data=read(path)
        if entry['kind']=='native-gate':
            assert data['planned']==data['completed']==len(data['rows'])
            assert data['passed']+data['failed']+data['not_run']==data['completed']
            assert sha(path.parent/'output.log')==data['raw_log_sha256']
        if not isinstance(data,dict) or data.get('scorer_version')!=3:continue
        assert data['counts']['scored']==len(data['rows'])
        assert len({r['id'] for r in data['rows']})==len(data['rows'])
        assert data['counts'].get('failed',0)==sum(bool(r['errors']) for r in data['rows'])
        summaries.append({'record':entry['record'],'source_commit':data['source_commit'],
             'counts':data['counts'],'acceptance_passed':data['acceptance_passed'],
             'remaining_non_target_incomplete_positives':sum(r.get('known_non_target_incomplete_positive',False) for r in data['rows'])})
    return {'integrity':integrity,'versioned_scores':summaries,
            'scope':'Frozen source-role targets and preservation; not all old questions answered or independently adjudicated',
            'independent_historical_accuracy':'NOT_RUN','independent_semantic_adjudication':'NOT_RUN',
            'independent_preparation':'NOT_RUN','independent_blinding':'NOT_RUN',
            'outside_custodian_scoring':'NOT_RUN','native_oocc':'NOT_RUN'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);a=p.parse_args()
    result=review()
    if a.output:save(a.output,result)
    print(json.dumps(result,indent=2))
