"""D% expansion: known-error stress cases using the unchanged isolated D% worker.

Developer-authored semantic templates, not independent/unseen validation.
No generator or key is mounted into the runtime. No acceptance-language filters.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import secrets
from tools import dpercent as D

VERSION = 'dpercent-expanded-v1'
FIELD_FAMILIES = {
    'field_literal': 'answer', 'field_synonym': 'answer', 'field_compound': 'answer',
    'field_same_subject': 'answer', 'field_changed_body': 'answer',
    'field_negation': 'refuse', 'field_past_scope': 'refuse',
    'field_quoted_only': 'refuse', 'field_reported_only': 'refuse',
    'field_conflict': 'refuse', 'field_missing_bridge': 'refuse',
    'field_wrong_id': 'refuse', 'field_restricted': 'refuse',
    'field_corrupted': 'refuse', 'field_withdrawn': 'refuse',
    'field_stacked': 'refuse', 'field_missing_label': 'refuse',
}
FORMS = (
    'What is the {field} for record {id}?',
    'Show me the {field} for record {id}.',
    'For record {id}, what {field} is recorded?',
    'Tell me the {field} stated in record {id}.',
    'Please give me {id}’s {field}.',
    'Find {id} and show its {field}.',
    'Which {field} is explicitly listed for record {id}?',
    'Looking only at {id}, report the {field} recorded there.',
    'In record {id}, what does the {field} field say?',
    'Record {id}: report the {field}.',
)
VOCABULARY = (('Current Status', 'current state', 'Pending', 'Complete'),
              ('Custody Location', 'location of custody', 'East vault', 'West vault'),
              ('Dispatch Date', 'date of dispatch', '1848-03-02', '1848-03-05'))


def field_case(number, family, dice):
    ident = 'ARCH-' + str(10000+number)
    field, alias, value, rival = dice.choose('field_vocabulary', VOCABULARY)
    form = dice.choose('field_question_structure', tuple(range(len(FORMS))))
    newline = dice.choose('field_line_ending', ('\n', '\r\n'))
    fence = dice.choose('field_quote_fence', ('```', '~~~', '>'))
    heading = dice.choose('field_heading', ('', '# Register\n\n', 'Subject: Archive notice\n'))
    unicode_note = dice.choose('field_unicode', ('Entry copied by Edda Marén.', 'Résumé — 東京.', 'Clerk wrote this entry.'))
    body = f'Record-ID: {ident}\n{field}: {value}\nOther Label: untouched\nSubject: Archive notice\n\nClerk wrote this entry. {unicode_note}'
    # Real field declarations remain first; editorial headings instead exercise
    # malformed/quoted families, never silently remove difficult generated cases.
    q = FORMS[form].format(field=field.lower(), id=ident)
    texts = [body]; flags = {}; expected = FIELD_FAMILIES[family]
    target = [f'{field}: {value}']
    if family == 'field_synonym': q = FORMS[form].format(field=alias, id=ident)
    elif family == 'field_compound':
        q = f'For record {ident}, report its {field.lower()} and other label.'
        target.append('Other Label: untouched')
    elif family == 'field_same_subject': texts.append(body.replace(ident, ident+'-OTHER').replace(value,rival))
    elif family == 'field_changed_body': texts.append(body.replace(unicode_note, 'Different documentary body: amendment to an unrelated claim.'))
    elif family == 'field_negation': q = f'Which {field.lower()} is not stated in record {ident}?'
    elif family == 'field_past_scope': q = q.rstrip('?.')+' before the revision?'
    elif family == 'field_quoted_only':
        quoted = ('\n'.join('> '+line for line in body.splitlines()) if fence=='>' else fence+'text\n'+body+'\n'+fence)
        texts = [heading+'Documentation example, not an independent record.\n'+quoted]
    elif family == 'field_reported_only': texts = [heading+'The porter said that the following unverified card existed:\n'+body]
    elif family == 'field_conflict': texts.append(body.replace(value,rival))
    elif family == 'field_missing_bridge': q = f'Prove that record {ident} establishes that this status caused completed delivery.'
    elif family == 'field_wrong_id': q = q.replace(ident,ident+'-ABSENT')
    elif family == 'field_restricted': flags['external']='no'
    elif family == 'field_corrupted': flags['corrupt']=True
    elif family == 'field_withdrawn': flags['retired']=True
    elif family == 'field_stacked': texts = [body.replace('\n',' ')]
    elif family == 'field_missing_label': q = FORMS[form].format(field='unrecorded authorization',id=ident)
    documents=[]
    for i,text in enumerate(texts,1):
        source={'path':f'sources/record-{i:02d}.md','source_class':'original',**flags}
        documents.append((source,(text.replace('\n',newline)+'\n').encode('utf-8')))
    case={'id':f'DP{number:05d}','question':q,'profile':'external' if family=='field_restricted' else dice.choose('field_profile',('internal','lab')),
          'sources':[s for s,_ in documents],'budget':{'passages':12,'characters':8000}}
    key={'id':case['id'],'family':family,'expected':expected,'required_propositions':[],
         'reference_sources':['SOURCE-0001'] if expected=='answer' else [],'source_facts':[],
         'structural_expectations':{},'automatic_answer_matcher':'literal_field_set_v1',
         'required_field_quotes':target,'features':{'question_form':form,'field':field,'line_ending':'CRLF' if newline=='\r\n' else 'LF',
         'fence':fence,'heading':heading,'source_count':len(documents)}}
    return case,documents,key


def prepare(out, custodian, count=1000, seed=None):
    out,custodian=Path(out).resolve(),Path(custodian).resolve()
    if type(count) is not int or not 1<=count<=D.LIMITS['cases']:raise ValueError('Cases must be 1–4096')
    if out==custodian or out in custodian.parents or custodian in out.parents or custodian==D.ROOT or D.ROOT in custodian.parents:raise ValueError('Keep custody disjoint and outside repository')
    seed=secrets.randbits(128) if seed is None else seed
    if type(seed) is not int or not 0<=seed<2**128:raise ValueError('Invalid seed')
    out.mkdir(parents=True,exist_ok=False);custodian.mkdir(parents=True,exist_ok=False,mode=0o700)
    dice=D.Dice(seed);families=list(D.FAMILIES)+list(FIELD_FAMILIES)
    schedule=dice.shuffle('expanded_family_schedule',[families[i%len(families)] for i in range(count)])
    keys=[];total=0;file_count=0
    for i,family in enumerate(schedule,1):
        case,documents,key=(field_case(i,family,dice) if family in FIELD_FAMILIES else D.case_material(i,family,dice))
        folder=out/'packets'/case['id'];folder.mkdir(parents=True)
        for source,raw in documents:
            total+=len(raw);file_count+=1
            if total>D.LIMITS['packet_bytes'] or file_count>D.LIMITS['files']:raise ValueError('Packet budget exceeded; partial preparation retained')
            path=folder/source['path'];path.parent.mkdir(exist_ok=True);path.write_bytes(raw)
        D.save(folder/'case.json',case);keys.append(key)
    D.save(custodian/'key.json',{'schema':VERSION+'-key','cases':keys});(custodian/'key.json').chmod(0o600)
    D.save(custodian/'dice.json',{'seed':str(seed),'rolls':dice.rolls,'sampling':'Stratified families, unbiased d100 draws; no runtime acceptance filters.'})
    D.save(out/'protocol.json',{'schema':VERSION,'cases':count,'families':families,'limits':D.LIMITS,
        'structural_combinations_lower_bound':8*len(FORMS)*len(VOCABULARY)*2*3,
        'independent_validation':'NOT RUN','source_kind':'Known-error developer-authored synthetic stress test',
        'no_language_acceptance_filter':True,'engine_fixes_during_batch':False})
    seal={'schema':VERSION+'-seal','public_files':D.files(out),'key_sha256':D.sha((custodian/'key.json').read_bytes()),
          'dice_sha256':D.sha((custodian/'dice.json').read_bytes()),'generator_sha256':D.sha(Path(__file__).read_bytes()),
          'generator_dependencies':{'tools/dpercent.py':D.sha(Path(D.__file__).read_bytes())},
          'worker_sha256':D.sha((D.ROOT/'tools/dpercent_worker.py').read_bytes()),'seed_commitment':D.sha(str(seed).encode()),'source_bytes':total,'source_files':file_count}
    D.save(out/'seal.json',seal);D.save(custodian/'public-seal-copy.json',seal)
    return seal


def score(packets,custodian,run,output):
    output=Path(output)
    if output.exists():raise FileExistsError(output)
    base=D.score(packets,custodian,run,output.with_suffix('.base.json'))
    keys={k['id']:k for k in D.read(Path(custodian)/'key.json')['cases']}
    for row in base['cases']:
        key=keys[row['id']]
        if key['automatic_answer_matcher']!='literal_field_set_v1' or row['execution']!='completed':continue
        answer=D.read(Path(run)/row['id']/'result.json')['answer']
        texts={c['text'] for c in answer.get('claims',[])}
        # The base scorer checks every present anchor. A field claim must also
        # have an anchor: an empty citation list must not pass by vacuous truth.
        match=(texts==set(key['required_field_quotes']) and row['quotation_fidelity']
               and all(c.get('citations') for c in answer.get('claims',[])))
        if row['answer_supported'] and key['expected']=='answer':
            row['outcome']='detected_answer' if match else 'incorrect_supported_answer'
        row['literal_field_set_match']=match;row['features']=key['features']
    rows=base['cases'];complete=all(r['execution']=='completed' for r in rows)
    pos=[r for r in rows if r['expected']=='answer'];neg=[r for r in rows if r['expected']=='refuse']
    tp=sum(r['outcome']=='detected_answer' for r in pos);fp=sum(r['outcome']=='false_alarm' for r in neg)
    metrics=base['metrics'];metrics.update(correct_complete_answers=tp,false_alarms=fp,E=tp/len(pos) if pos and complete else None,
        F=fp/len(neg) if neg and complete else None,E_lower_bound=tp/len(pos) if pos else None,
        complete_decision_match=complete and tp==len(pos) and fp==0,
        outcomes=dict(Counter(r['outcome'] for r in rows)),
        unscored_supported=sum(r['outcome']=='supported_semantics_unscored' for r in rows))
    metrics['by_family']={family:{'cases':sum(r['family']==family for r in rows),'outcomes':dict(Counter(r['outcome'] for r in rows if r['family']==family))} for family in sorted({r['family'] for r in rows})}
    metrics['by_feature'] = {}
    for feature in ('question_form', 'field', 'line_ending', 'fence', 'source_count'):
        values={str(r['features'][feature]) for r in rows if 'features' in r}
        metrics['by_feature'][feature]={value:{'cases':sum(str(r.get('features',{}).get(feature))==value for r in rows if 'features' in r), 'outcomes':dict(Counter(r['outcome'] for r in rows if 'features' in r and str(r['features'][feature])==value))} for value in sorted(values)}
    metrics['caution']='Typed source propositions or exact field sets with independently rechecked quotation anchors; unknown semantic shapes remain unscored. Known-error authored development templates, not independent review.'
    base.update(schema=VERSION+'-score',expanded_scorer_sha256=D.sha(Path(__file__).read_bytes()),metrics=metrics)
    D.save(output,base);return base


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    prep=sub.add_parser('prepare')
    prep.add_argument('--out',type=Path,required=True);prep.add_argument('--custodian',type=Path,required=True)
    prep.add_argument('--cases',type=int,default=1000);prep.add_argument('--seed',type=int)
    scoring=sub.add_parser('score')
    for arg in ('packets','custodian','run','output'):scoring.add_argument('--'+arg,type=Path,required=True)
    a=p.parse_args()
    if a.command=='prepare':print(json.dumps(prepare(a.out,a.custodian,a.cases,a.seed)))
    else:print(json.dumps(score(a.packets,a.custodian,a.run,a.output)['metrics']))


if __name__=='__main__':main()
