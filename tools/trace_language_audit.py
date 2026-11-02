import json
from pathlib import Path
from mplpb_combined.ledger import Ledger
from mplpb_answers.body_text import body_text
from mplpb_answers import relation_graph,frames,literal_evidence,practical_evidence,policy_evidence,operational_evidence
from mplpb_combined.provenance_gate import gather
from mplpb_combined.reader import PROFILES,DEFAULT_PROFILE
base=json.load(open('evaluation/language-audit/baseline-full.json'))
source={r.id:r for r in Ledger('examples/studio').servable()}
groups={
'procedure': 'od01 od07 op08 rt01 rt02 rt03 rt04 rt05 rt06 h06 h14 h20 h21 h22 c01 c02 c05 c06 c07 c08',
'situation_to_relation': 'od02 od03 od05 od06 od09 od10 om01 om03 om07 h01 h02 h04 h05 h07 h08 c03',
'conditions': 'od04 om02 om04 om05 om08 h15',
'comparison': 'h03',
'reference': 'op04',
'missing_value': 'om06',
'unknown_relation': 'h11',
'multiple_owners': 'h10',
}
lookup={i:k for k,ids in groups.items() for i in ids.split()}
repairs={
'procedure':('interpretation','Ordered procedure with explicit action, prerequisites, thresholds and stop conditions; cite every step and refuse incomplete plans.','deliberately unsupported free-form procedure'),
'situation_to_relation':('interpretation','Separate symptom recognition from causal proof and recommendations. Require an explicit symptom-to-relation alias and source assertion; clarify diagnosis.','deliberately unsupported situation inference'),
'conditions':('interpretation','Preserve condition, exception, modality and time; request missing applicability instead of unconditional advice.','legitimate restraint or unsupported conditional interpretation'),
'comparison':('interpretation','Return source-declared suitability separately; do not invent a universal ranking.','benchmark expects a page, not an established comparison'),
'reference':('evidence','Resolve it only to a unique explicit same-document antecedent with cited antecedent span; reject ambiguous referents.','deliberately unsupported anaphora'),
'missing_value':('evidence','No water quantity is given; explain the gap rather than invent a recipe amount.','incomplete benchmark expectation / legitimate abstention'),
'unknown_relation':('interpretation','Recognize location/disposition with the subject and prohibition intact; unknown wording must remain unsupported.','deliberately unsupported relationship form'),
'multiple_owners':('conflict assessment','Retain separate owners and citations, explain compatible repetition and ancestry without selecting one.','contractual ambiguity, not evidence contradiction'),
}
rows=[]
for name,v in base['datasets'].items():
 if not name.startswith('probes'):continue
 for r in v['rows']:
  if r['expected']!='return':continue
  a=r['supported'];rec=source[r['expected_doc']];q=r['question']
  parsed=next((f for mod in (literal_evidence,practical_evidence,policy_evidence,operational_evidence,relation_graph,frames) if (f:=mod.parse(q)) is not None),None)
  gate=gather('examples/studio',q,PROFILES[DEFAULT_PROFILE])
  c=lookup.get(r['id'])
  if a['kind']=='return':
   c='supported';stage='none';repair='No question-specific repair. Keep exact quote and qualifiers.';disposition='supported complete source claim'
   if r['id']=='op05':disposition='supported conditional quotation; antecedent it remains unresolved (partial applicability)'
  else:
   stage,repair,disposition=repairs[c]
   if parsed is not None and stage=='interpretation':stage='evidence extraction' # recognizer matched but did not establish body proof
  extra=[]
  if r['id'] in ('h01','h07'):
   extra.append('incomplete_benchmark_expectation')
   disposition='expected page does not establish this diagnosis; ambiguity is not proven body conflict'
   repair+=' Flag the expected dipping page: it does not assert the requested diagnosis.'
  if r['id']=='h15':
   extra.append('provenance_exclusion')
   disposition='legitimate refusal: expected page excluded by not-for injury'
   repair='Retain the restriction and explain eligibility; do not bypass not-for to meet a document label.'
  rows.append(dict(id=r['id'],dataset=name,question=q,source_id=rec.id,source_path=rec.path,source_hash=rec.hash,source_passage=body_text(rec.body_html),observed=a,classes=[c]+extra+(['multiple_owners'] if a['kind']=='ambiguous' and c!='multiple_owners' else []),first_failure_stage=stage,disposition=disposition,expected_defensible_behavior=repair,proposed_general_repair=repair,trace=dict(interpretation=parsed.to_dict() if parsed else None,collection='examples/studio',eligible_ids=[s['id'] for s in gate.sources],excluded=gate.excluded,expected_source_retrieved=rec.id in [s['id'] for s in gate.sources],candidate_checks=a['support'].get('candidate_checks',[]),rendered=a['text'],follow_up='Existing source inspection / clarify; no source edits authorized')))
Path('evaluation/language-audit/cases.json').write_text(json.dumps(rows,indent=2)+'\n')
lines=['# Per-case baseline semantic review','', 'Model-authored review of inspected development data. Original labels and source bytes unchanged. Full stage diagnostics are in cases.json. Each cited passage below is the body of the historically expected page; page identity is not an entailment oracle.','']
for r in rows:
 lines += [f"## {r['dataset']} / {r['id']}", '',r['question'],'', '> '+r['source_passage'],'',f"Observed: **{r['observed']['kind']}**. Returned: {r['observed']['text'] or '(no answer)'}. Disposition: {r['disposition']}.",'',f"Classes: {', '.join(r['classes'])}. First limiting stage: {r['first_failure_stage']}. Expected defensible behavior / general repair: {r['expected_defensible_behavior']}",'']
Path('evaluation/language-audit/CASES.md').write_text('\n'.join(lines))
print(len(rows),'answerable cases traced')
