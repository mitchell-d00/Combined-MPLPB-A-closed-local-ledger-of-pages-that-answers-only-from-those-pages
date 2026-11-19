"""Post-run comparison of sealed development records; never a runtime answer key."""
import argparse
import json
from pathlib import Path

from tools.sorter_first_study import FAMILIES, ROOT
from tools.report_sorter_options_study import native, metrics, visible
from tools.unprepared_challenge import read, frozen, covers
from tools.source_roundtrip import original_passage
from mplpb_work.answer_router import question_parts


def report(before, after):
    before,after=Path(before),Path(after)
    results={name:[] for name in ('before','after')};cases=[];missed=[]
    for family,(relative,seal) in FAMILIES.items():
        corpus=ROOT/relative;frozen(corpus,seal)
        references={r['id']:r for r in read(corpus/'reference-draft.json')['cases']}
        imported=read(after/family/'import-receipt.json')
        if imported!=read(before/family/'import-receipt.json'):
            raise ValueError('Original import receipts differ')
        records={r['id']:r for r in imported['records']}
        for q in read(corpus/'questions.json')['cases']:
            rows={name:read(directory/family/'direct'/(q['id']+'.json'))
                  for name,directory in (('before',before),('after',after))}
            for name,row in rows.items():
                if row['question']!=q['question']:raise ValueError('Question changed')
                results[name].append(row)
            found={name:[any(covers(p,ref) for p in visible(row))
                         for ref in references[q['id']]['citations']] for name,row in rows.items()}
            entry={'family':family,'id':q['id'],'question':q['question'],
                   'required_question_parts':question_parts(q['question']),
                   'native_result_unchanged':native(rows['before'])==native(rows['after']),
                   'before':native(rows['before']),'after':native(rows['after']),
                   'draft_reference_spans_found':found,
                   'diagnostic':rows['after'].get('answer',{}).get('diagnostic'),
                   'semantic_correctness_independently_reviewed':False}
            entry['checked_original_evidence']=[original_passage(corpus,imported,e)
                for c in rows['after'].get('answer',{}).get('claims',[]) for e in c.get('citations',[])]
            cases.append(entry)
            for i,ref in enumerate(references[q['id']]['citations']):
                if found['after'][i]:continue
                record=records[ref['source_id']]
                anchor=dict(source_id=ref['source_id'],path=record['path'],hash=record['hash'],
                            body_start=ref['start'],body_end=ref['end'],quote=ref['quote'])
                missed.append({'id':q['id'],'question':q['question'],'reference':ref,
                               'original_source':original_passage(corpus,imported,anchor),
                               'meaning':'Unsurfaced draft anchor; not proof of an answerable obligation.'})
    totals={name:metrics(rows) for name,rows in results.items()}
    for name in totals:
        totals[name]['draft_spans_found']=sum(sum(c['draft_reference_spans_found'][name]) for c in cases)
        totals[name]['draft_span_total']=sum(len(c['draft_reference_spans_found'][name]) for c in cases)
    return {'schema':'fixpack-original-retest-v1','baseline_protocol':read(before/'protocol.json'),
            'updated_protocol':read(after/'protocol.json'),'totals':totals,'cases':cases,
            'all_native_results_unchanged':all(c['native_result_unchanged'] for c in cases),
            'unsurfaced_draft_anchors':missed,'independent_semantic_review':'NOT RUN',
            'historical_relationship_precision':None,'historical_relationship_recall':None,
            'false_link_rate':None,'appropriate_refusal_accuracy':None,
            'notice':'Sealed development questions, source discovery and mechanical contract comparison only. '
                     'A draft anchor is not a semantic answer key; a candidate or rewrite is not a complete original-question answer.'}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before',required=True,type=Path)
    parser.add_argument('--after',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--table',type=Path)
    args=parser.parse_args(argv);value=report(args.before,args.after)
    with args.output.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
    if args.table:
        def cell(text):return str(text).replace('|','\\|').replace('\n',' ')
        lines=['# Unchanged-question obligation and evidence table','',
               'Source-attributed checks only. Semantic correctness and historical truth remain unreviewed; full original-byte anchors are in the comparison JSON.','',
               '| ID | Required parts | Checked source statements | Where checking stops |','|---|---|---|---|']
        for c in value['cases']:
            claims='; '.join(x.get('text','') for x in c['after']['claims']) or 'No checked statement retained'
            stop=c['diagnostic']['code']+'; '+'; '.join(c['after']['missing'])
            lines.append('| '+' | '.join(map(cell,(c['id'],'; '.join(c['required_question_parts']),claims,stop)))+' |')
        with args.table.open('x',encoding='utf-8') as stream:stream.write('\n'.join(lines)+'\n')
    print(json.dumps(value['totals'],indent=2));return 0


if __name__=='__main__':raise SystemExit(main())
