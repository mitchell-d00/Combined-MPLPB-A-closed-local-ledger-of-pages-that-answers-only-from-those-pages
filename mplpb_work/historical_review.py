"""Typed historical-review entry rules on the existing capability work ledger.

Entry is an auditable assessment, not a truth certificate. Synthetic oracles
are explicitly separate test universes and never real-world historical evidence.
"""
import json
from .errors import WorkError
from .store import digest
from .model import words, strings

REGIME='historical-review-v1'
FIELDS={'id','claim_id','claim_revision','reviewer_id','reviewer_kind','decision','rationale',
        'independence_attestation','evidence_ids','scope','uncertainties'}
FINDING_FIELDS={'reviewer_id','reviewer_kind','rationale','independence_attestation','scope','uncertainties',
                'claim_sha256','reviewer_seat','reviewer_instance','evidence_pins','historical_truth_independently_verified'}


def validate_record(payload,dependencies,actor,state):
    """Also enforce the typed regime on direct WorkStore.put, not only helper calls."""
    try:entry=json.loads(payload['finding'])
    except (TypeError,ValueError) as exc:raise WorkError('Invalid typed historical finding') from exc
    if not isinstance(entry,dict) or set(entry)!=FINDING_FIELDS:raise WorkError('Incomplete typed historical finding')
    for key in ['reviewer_id','rationale','independence_attestation','scope']:words(entry[key])
    strings(entry['uncertainties'])
    if (entry['reviewer_kind'] not in {'synthetic_fixture','human_declared'} or entry['historical_truth_independently_verified'] is not False
        or entry['reviewer_seat']!=actor['seat'] or entry['reviewer_instance']!=actor['instance']
        or not dependencies or entry['evidence_pins']!=dependencies):raise WorkError('Historical reviewer identity/evidence pins are not bound to this capability')
    target,revision=next(iter(payload['target'].items()));claim=state['records'][target]
    if (claim['revision']!=revision or entry['claim_sha256']!=digest(claim['payload'])
        or any(state['records'][key]['kind']!='evidence' for key in dependencies)):
        raise WorkError('Historical review requires a current claim and source evidence')


def enter_review(store,credential,entry):
    """Append through existing rights, visibility, revision and source gates."""
    if not isinstance(entry,dict) or set(entry)!=FIELDS:raise WorkError('Incomplete historical review entry')
    for key in ['reviewer_id','rationale','independence_attestation','scope']:words(entry[key])
    strings(entry['evidence_ids'],empty=False);strings(entry['uncertainties'])
    if entry['reviewer_kind'] not in {'synthetic_fixture','human_declared'}:raise WorkError('Declare synthetic fixture or self-declared human review')
    if entry['decision'] not in {'support','challenge','inconclusive'}:raise WorkError('Unknown historical review decision')
    view=store.snapshot(credential);records={r['id']:r for r in view['records']};claim=records.get(entry['claim_id'])
    if not claim or claim['kind']!='claim' or type(entry['claim_revision']) is not int or claim['revision']!=entry['claim_revision']:
        raise WorkError('Choose one visible current claim revision')
    evidence=[]
    for identifier in entry['evidence_ids']:
        record=records.get(identifier)
        if not record or record['kind']!='evidence' or record['effective_status']!='eligible':raise WorkError('Review requires currently eligible exact evidence')
        evidence.append(record)
    finding={k:entry[k] for k in ['reviewer_id','reviewer_kind','rationale','independence_attestation','scope','uncertainties']}
    finding.update(claim_sha256=digest(claim['payload']),reviewer_seat=view['contract']['seat'],reviewer_instance=view['contract']['instance'],
                   evidence_pins={r['id']:r['revision'] for r in evidence},
                   historical_truth_independently_verified=False)
    return store.put(credential,id=entry['id'],kind='review',payload={
        'task':claim['payload']['task'],'target':{claim['id']:claim['revision']},'target_variable':entry['scope'],
        'regime':REGIME,'finding':json.dumps(finding,sort_keys=True),'outcome':entry['decision'],'resolution':''},
        dependencies={r['id']:r['revision'] for r in evidence},visibility=claim['visibility'],expected_revision=0,expected_head=view['head'])


def inspect_reviews(store,credential,claim_id,*,synthetic_oracle=None,oracle_sha256=None):
    """Fresh scoped view; repeated reviewer labels/seats cannot be independent."""
    view=store.snapshot(credential);records={r['id']:r for r in view['records']};claim=records.get(claim_id)
    if not claim or claim['kind']!='claim':raise WorkError('Choose a visible claim')
    rows=[];stale=False
    for r in records.values():
        p=r['payload']
        if r['kind']!='review' or p['regime']!=REGIME or claim_id not in p['target']:continue
        try:entry=json.loads(p['finding'])
        except (TypeError,ValueError):stale=True;continue
        if not isinstance(entry,dict) or set(entry)!=FINDING_FIELDS:stale=True;continue
        current=(p['target'][claim_id]==claim['revision'] and entry.get('claim_sha256')==digest(claim['payload'])
                 and r['effective_status']!='needs_recheck'
                 and all(identifier in records and records[identifier]['kind']=='evidence'
                         and records[identifier]['revision']==revision and records[identifier]['effective_status']=='eligible'
                         for identifier,revision in entry.get('evidence_pins',{}).items()))
        stale|=not current
        rows.append({'review_id':r['id'],'record_revision':r['revision'],'current':current,'decision':p['outcome'],**entry})
    accepted=[r for r in rows if r['current']]
    distinct=len({(r['reviewer_id'],r['reviewer_seat']) for r in accepted})>=2 and len({r['reviewer_id'] for r in accepted})>=2 and len({r['reviewer_seat'] for r in accepted})>=2
    synthetic=bool(accepted) and all(r['reviewer_kind']=='synthetic_fixture' for r in accepted)
    status='needs_recheck' if stale else 'contested' if any(r['decision']=='challenge' for r in accepted) else 'synthetic_fixture_reviewed' if synthetic and distinct else 'declared_reviews_pending_independent_validation' if accepted else 'NOT RUN'
    matches=None
    if synthetic_oracle is not None:
        if (not isinstance(synthetic_oracle,dict) or set(synthetic_oracle)!={'universe','proposition','truth_value'}
            or not isinstance(synthetic_oracle['universe'],str) or not synthetic_oracle['universe'].startswith('synthetic-')
            or type(synthetic_oracle['truth_value']) is not bool or digest(synthetic_oracle)!=oracle_sha256
            or synthetic_oracle['proposition']!=claim['payload']['proposition']):raise WorkError('Use a pinned matching synthetic-universe oracle')
        matches=synthetic and distinct and not stale and all((r['decision']=='support')==synthetic_oracle['truth_value'] for r in accepted)
    if store.snapshot(credential)['head']!=view['head']:
        status='needs_recheck';rows=[];matches=False if matches is not None else None
    return {'schema':REGIME,'claim_id':claim_id,'claim_revision':claim['revision'],'review_status':status,'reviews':rows,
            'synthetic_fixture_truth_matches':matches,'synthetic_oracle_sha256':oracle_sha256 if synthetic_oracle is not None else None,
            'reviewer_identity_independently_verified':False,'reviewer_independence_verified':False,
            'historical_truth_independently_verified':False,'answer_supported':False,
            'notice':'Host capabilities authorize entries, not reviewer identity or historical truth. Synthetic truth applies only to its declared test universe.'}
