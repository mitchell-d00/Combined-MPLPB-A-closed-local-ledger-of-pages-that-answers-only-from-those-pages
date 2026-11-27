"""Post-run source/polarity assessment of existing D% outputs.

This does not execute questions, rewrite them or amend the original scorer/key.
Prospective yes/no formatting is scored separately from literal source support.
Same-operator software assessment, never independent semantic adjudication.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from tools import dpercent as D


def subset(actual, expected):
    return all(k in actual and type(actual[k]) is type(v) and actual[k] == v
               for k,v in expected.items())


def literal_text(claim):
    text=claim['text']
    return text[5:] if text.startswith('Yes. ') else text[4:] if text.startswith('No. ') else text


def assess(public, custody, run, output, baseline=None):
    public,custody,run,output=map(Path,(public,custody,run,output))
    if output.exists():raise FileExistsError(output)
    D.verify(public,custody)
    keys=D.read(custody/'key.json')['cases'];execution=D.read(run/'run.json')
    assert execution['packet_seal_sha256']==D.sha((public/'seal.json').read_bytes())
    entries={r['case_id']:r for r in execution['cases']}
    rows=[];old_by_sources={};case_inputs={}
    for key in keys:
        case=D.read(public/'packets'/key['id']/'case.json')
        material={'sources':case['sources'],'profile':case['profile'],
                  'bytes':{s['path']:D.sha((public/'packets'/key['id']/s['path']).read_bytes()) for s in case['sources']}}
        signature=D.sha(json.dumps(material,sort_keys=True).encode())
        case_inputs[key['id']]=(case,signature)
        if baseline and (Path(baseline)/key['id']/'result.json').exists():
            before=D.read(Path(baseline)/key['id']/'result.json')['answer']
            if key['expected']=='answer' and before['answer_supported']:
                old_by_sources.setdefault(signature,[]).append(key)
    for key in keys:
        ident=key['id'];entry=entries.get(ident);case,signature=case_inputs[ident]
        row={'id':ident,'family':key['family'],'expected':key['expected'],'question':case['question'],
             'source_signature':signature,'input_signature':D.sha((signature+case['question']).encode())}
        if not entry or entry['execution']!='completed':
            row.update(execution='not_run' if not entry else 'failed',source_correct=False)
            rows.append(row);continue
        path=run/ident/'result.json';assert D.sha(path.read_bytes())==entry['sha256']
        raw=D.read(path);answer=raw['answer'];errors=[]
        if raw['question']!=case['question'] or answer['question']!=case['question']:errors.append('original_question_changed')
        sources={s['source_id']:s for s in raw['source_receipts']}
        manifest={s['path']:s for s in case['sources']}
        if answer.get('verification',{}).get('truth_verified') is not False:errors.append('truth_scope')
        for claim in answer['claims']:
            if not claim.get('citations'):errors.append('missing_citation')
            for cite in claim.get('citations',[]):
                src=sources.get(cite.get('source_id'));lo=cite.get('body_start');hi=cite.get('body_end')
                if not src or type(lo)!=int or type(hi)!=int or not 0<=lo<hi<=len(src['canonical_body']) or src['canonical_body'][lo:hi]!=cite['quote'] or src['hash']!=cite['hash']:
                    errors.append('citation_correspondence');continue
                if manifest[src['source_file']].get('retired'):errors.append('ineligible_witness')
                if D.sha((public/'packets'/ident/src['source_file']).read_bytes())!=src['raw_sha256']:errors.append('source_mutation')
            p=claim.get('proposition',{})
            if p.get('modality')=='instruction' and (p.get('completion_asserted_by_source') is not False or p.get('execution_independently_verified') is not False):errors.append('instruction_promoted_to_execution')
        if key['expected']=='refuse':
            if answer['answer_supported']:errors.append('unsupported_completion')
            if answer['claims'] and answer['kind']!='conflict':errors.append('unexpected_partial_claims_require_review')
        elif not answer['answer_supported']:errors.append('positive_miss')
        else:
            claims=answer['claims'];targets=key['required_propositions']
            if targets:
                if not all(any(subset(c.get('proposition',{}),t) for c in claims) for t in targets):errors.append('incomplete_claim')
                if not all(any(subset(c.get('proposition',{}),t) for t in targets) for c in claims):errors.append('additional_unkeyed_claim')
            else:
                if {literal_text(c) for c in claims}!=set(key['required_field_quotes']):errors.append('literal_source_claim')
                expected_parts=[part for witness in key['required_field_quotes'] for part in witness.split('\n') if part]
                quotes=[c['quote'] for claim in claims for c in claim['citations']]
                if not all(part in quotes for part in expected_parts):errors.append('incomplete_witnesses')
        yes_no=key['family'] in {'yes_no','classification_confirmation','confirmation'}
        polarity_ok=None
        if yes_no:
            if key['expected']=='refuse':polarity_ok=not answer['answer_supported'] and not answer['text'].startswith(('Yes.','No.'))
            else:
                negative=any(' is not ' in quote for quote in key['required_field_quotes'])
                polarity='negative' if negative else 'positive';prefix='No. ' if negative else 'Yes. '
                polarity_ok=(answer['answer_supported'] and answer['text'].startswith(prefix)
                             and all(c.get('proposition',{}).get('relation')=='literal_classification'
                                     and c['proposition'].get('polarity')==polarity
                                     and c['text'].startswith(prefix) for c in answer['claims']))
        row.update(execution='completed',kind=answer['kind'],supported=answer['answer_supported'],
                   source_correct=not errors,source_errors=errors,polarity_contract=polarity_ok,
                   raw_sha256=entry['sha256'],budget_stop='budget' in answer['diagnostic']['code'])
        if baseline:
            old=D.read(Path(baseline)/ident/'result.json')['answer'];was=old['answer_supported']
            row['lost_support_flag']=was and not answer['answer_supported']
            row['new_source_supported_answer']=not was and answer['answer_supported'] and not errors
            same_proposition=any(k['required_propositions']==key['required_propositions'] and k['required_field_quotes']==key['required_field_quotes'] for k in old_by_sources.get(signature,[]))
            row['new_original_wording_on_previously_admitted_sources']=row['new_source_supported_answer'] and same_proposition
        rows.append(row)
    completed=[r for r in rows if r['execution']=='completed'];gains=[r for r in completed if r.get('new_original_wording_on_previously_admitted_sources')]
    summary={'planned':len(keys),'completed':len(completed),'execution_failures':sum(r['execution']!='completed' for r in rows),
             'source_decisions_correct':sum(r['source_correct'] for r in completed),
             'positive_targets':sum(k['expected']=='answer' for k in keys),'correct_source_supported_answers':sum(r['source_correct'] and r['expected']=='answer' for r in completed),
             'unsupported_completions':sum('unsupported_completion' in r['source_errors'] for r in completed),
             'source_errors':dict(Counter(e for r in completed for e in r['source_errors'])),
             'polarity_contract_pass':sum(r['polarity_contract'] is True for r in completed),'polarity_contract_fail':sum(r['polarity_contract'] is False for r in completed),
             'budget_stops':sum(r['budget_stop'] for r in completed),
             'unique_questions':len({r['question'] for r in rows}),'unique_inputs':len({r['input_signature'] for r in rows}),
             'new_source_supported_executions':sum(r.get('new_source_supported_answer',False) for r in completed),
             'lost_support_flags_requiring_review':sum(r.get('lost_support_flag',False) for r in completed),
             'new_wording_executions_on_matched_previously_admitted_sources':len(gains),
             'new_wording_unique_questions':len({r['question'] for r in gains}),
             'new_wording_unique_inputs':len({r['input_signature'] for r in gains})}
    result={'schema':'bunyip-r02-source-and-format-assessment-v1','summary':summary,'rows':rows,
            'scorer_sha256':D.sha(Path(__file__).read_bytes()),'key_sha256':D.sha((custody/'key.json').read_bytes()),
            'original_scores_unchanged':True,'custody':'Same-operator deterministic source/key comparison; independent semantic adjudication NOT_RUN.',
            'gain_scope':'Only unchanged original questions count. Previously admitted identical sources/propositions are post-run mechanism attribution, not new canonical executions. Metadata/polarity formatting is separate from source-support gain.'}
    D.save(output,result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('packets','custodian','run','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--baseline',type=Path)
    a=p.parse_args();print(json.dumps(assess(a.packets,a.custodian,a.run,a.output,a.baseline)['summary'],indent=2))
