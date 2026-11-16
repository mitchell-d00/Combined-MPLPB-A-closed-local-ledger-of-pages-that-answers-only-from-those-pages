"""Inspect native answers and reversible candidate maps of imported originals."""
import argparse
import json
from pathlib import Path
from mplpb_answers.pipeline import answer_query
from mplpb_work.prose_evidence import discover
from mplpb_work.source_mapping import reconstruct
from tools.source_roundtrip import original_passage
from tools.unprepared_sources import load,save


def inspect(ledger,question):
    answer=answer_query(ledger,question).contract
    candidates=discover(ledger,question)
    return {'schema':'original-reconstruction-inspection-v1','question':question,
            'native_answer':answer,'candidate_analysis':candidates,
            'answer_supported':answer['answer_supported'],
            'notice':'Native source support and candidate interpretation have separate authority. Quote fidelity does not verify historical meaning.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='command',required=True)
    a=s.add_parser('map');a.add_argument('--ledger',required=True);a.add_argument('--question',required=True);a.add_argument('--output',required=True)
    b=s.add_parser('reconstruct');b.add_argument('--ledger',required=True);b.add_argument('--report',required=True);b.add_argument('--mapping-id',required=True)
    b.add_argument('--corpus',required=True);b.add_argument('--import-receipt',required=True);b.add_argument('--output',required=True)
    args=p.parse_args()
    if args.command=='map':save(args.output,inspect(args.ledger,args.question));return
    report=load(args.report);m=report['candidate_analysis']['information_map']
    rich=m.get('proposed_reconstruction',{})
    candidates=m['mappings']+m['relationships']+rich.get('propositions',[])+rich.get('connections',[])+rich.get('qualifications',[])
    items=[x for x in candidates if x['mapping_id']==args.mapping_id]
    if len(items)!=1:raise ValueError('Choose one mapping ID')
    result=reconstruct(args.ledger,report['question'],items[0])
    if result['quote_fidelity']:
        receipt=load(args.import_receipt)
        result['original_passages']=[original_passage(args.corpus,receipt,e) for e in result['passages']]
    save(args.output,result)


if __name__=='__main__':main()
