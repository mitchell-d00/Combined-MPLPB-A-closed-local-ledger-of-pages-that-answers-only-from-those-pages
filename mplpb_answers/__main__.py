"""Default user CLI: supported answers, explicit legacy candidate inspection."""
import json
import sys
from mplpb_combined import reader as R
from mplpb_combined.__main__ import build_parser as legacy_parser, _profile
from .support import supported_answer
from . import __version__


def cmd_ask(args):
    from .pipeline import answer_query
    reader = None
    if args.reader_model:
        from .local_reader import OllamaLocalReader
        try:
            reader = OllamaLocalReader(args.reader_model, endpoint=args.reader_endpoint,
                                       reviewer_model=args.reviewer_model,
                                       model_digest=args.reader_digest, reviewer_digest=args.reviewer_digest)
        except ValueError as exc:
            print(json.dumps({'error': str(exc), 'answer_supported': False}), file=sys.stderr)
            return 2
    if args.answer_mode == 'strict' and reader is not None:
        raise ValueError('Use --answer-mode assisted to enable the explicitly configured local reader')
    result = answer_query(args.root, args.question, _profile(args), mode=args.answer_mode, reader=reader,
                          min_confidence=args.assisted_threshold, max_passages=args.max_passages, max_chars=args.max_context_chars,
                          record_id=args.record_id,field=args.field,as_of=args.as_of)
    data = result.legacy()
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif args.answer_mode == 'strict':
        label = {'return':'SUPPORTED ANSWER', 'ambiguous':'AMBIGUOUS', 'not_in_corpus':'NO SUPPORTED ANSWER'}[data['kind']]
        print(label+'\n'+(R.render(result.strict, why=args.why) if data['kind'] == result.strict.kind else result.contract['text'] or data['reason']))
        if result.contract['diagnostic']['code'] == 'partial_procedure_evidence':
            print(result.contract['text'])
        if result.strict.kind != 'return':
            print('Diagnostic: '+result.contract['diagnostic']['code']+' — '+result.contract['diagnostic']['message'])
    else:
        c = result.contract
        print(c['kind'].upper().replace('_',' '))
        print(c['diagnostic']['message'])
        if c['text']:
            print(c['text'])
        for claim in c['claims']:
            for citation in claim.get('citations', []):
                print('[{source_id} {hash}] {quote}'.format(**citation))
        if c['missing']:
            print('Unanswered: '+'; '.join(c['missing']))
        if c['clarification']:
            print(c['clarification'])
    if not args.json:
        print(result.contract['source_assurance']['notice'])
    if args.answer_mode == 'strict':
        return {'return': 0, 'ambiguous': 2, 'not_in_corpus': 3}[data['kind']]
    return {'supported_answer': 0, 'model_assisted_answer': 0, 'partial_answer': 4, 'conflict': 2, 'clarify': 5, 'abstain': 3}[result.contract['kind']]


def cmd_candidates(args):
    result = R.answer(args.root, args.question, _profile(args))
    data = result.to_dict()
    data.update(mode='candidate_retrieval', answer_supported=False,
                notice='Legacy lexical candidates only. Scope does not establish body support.')
    print(json.dumps(data, indent=2, ensure_ascii=False) if args.json else
          'CANDIDATE RETRIEVAL — NOT A SUPPORTED ANSWER\n' + R.render(result, why=args.why))
    return {'return':0,'ambiguous':2,'not_in_corpus':3}[result.kind]


def cmd_tags(args):
    from mplpb_combined.ledger import Ledger
    from mplpb_combined.provenance_gate import gather
    from mplpb_combined.record import text_of
    from .procedures import automatic_tags
    records=[r for r in Ledger(args.root).servable() if r.path==args.path]
    if len(records)!=1: raise ValueError('Choose one current source page path')
    rec=records[0]
    if rec.path not in {s['path'] for s in gather(args.root,rec.title,R.PROFILES[args.profile]).sources}:
        raise ValueError('Source page is withheld by the provenance gate')
    print(json.dumps(automatic_tags(text_of(rec.body_html),{'id':rec.id,'path':rec.path,'hash':rec.hash}),indent=2))
    return 0


def cmd_work(args):
    from mplpb_work.__main__ import main as work_main
    return work_main(args.work_args)


def cmd_investigate(args):
    from mplpb_work.investigation import investigate
    try:
        result=investigate(args.root,args.question,profile=R.PROFILES[args.profile],
            start_source_ids=args.source,max_hops=args.max_hops,max_sources=args.max_sources,
            max_chars=args.max_source_chars,work_directory=args.work_directory)
    except (ValueError,OSError) as exc:
        print(json.dumps({'error':str(exc),'answer_supported':False}),file=sys.stderr)
        return 3
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return 0 if result['status']=='evidence_report' else 3


def cmd_reconstruct(args):
    from mplpb_work.prose_evidence import reconstruct_report
    reader=None
    if args.reader_model:
        from .local_reader import OllamaLocalReader
        reader=OllamaLocalReader(args.reader_model,endpoint=args.reader_endpoint)
    result=reconstruct_report(args.root,args.question,R.PROFILES[args.profile],
                              max_passages=args.max_passages,max_chars=args.max_context_chars,reader=reader)
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return 0 if result['status']=='research_report' else 3


def cmd_correct_claim(args):
    from .corrections import correct_claim
    try:
        result=correct_claim(args.root,args.source_id,args.old_quote,args.new_quote,
                             effective_at=args.effective_at,profile=R.PROFILES[args.profile],
                             corrects_field=args.corrects_field,valid_from=args.valid_from,valid_until=args.valid_until)
    except (ValueError,OSError) as exc:
        print(json.dumps({'error':str(exc),'answer_supported':False}),file=sys.stderr)
        return 3
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return 0


def build_parser():
    parser = legacy_parser()
    parser.prog = 'mplpb-combined'
    for action in parser._actions:
        if action.dest == 'version': action.version = __version__ + ' (supported CLI; legacy core 1.0.0)'
    sub = next(a for a in parser._actions if hasattr(a, 'choices') and isinstance(a.choices, dict))
    ask = sub.choices['ask']
    ask.set_defaults(fn=cmd_ask)
    ask.add_argument('--answer-mode', choices=['strict', 'assisted'], default='strict')
    ask.add_argument('--reader-model', help='Explicit installed local Ollama model; no automatic downloads')
    ask.add_argument('--reviewer-model', help='Optional separate local review model')
    ask.add_argument('--reader-endpoint', default='http://127.0.0.1:11434')
    ask.add_argument('--reader-digest'); ask.add_argument('--reviewer-digest')
    ask.add_argument('--assisted-threshold', type=float, default=0.8)
    ask.add_argument('--max-passages', type=int, default=12)
    ask.add_argument('--max-context-chars', type=int, default=8000)
    ask.add_argument('--record-id', help='Exact record ID or ID@sha256 pin; routing never supplies field support')
    ask.add_argument('--field', help='Explicit source body field label')
    ask.add_argument('--as-of', help='ISO date or timezone-qualified timestamp for a declared correction window')
    candidate = sub.add_parser('candidates', help='inspect legacy lexical candidates; not supported answers',
                               parents=[legacy_parser()._subparsers._group_actions[0].choices['ask']], add_help=False)
    candidate.set_defaults(fn=cmd_candidates)
    tags=sub.add_parser('tag-procedure',help='draft numbered-step tags without promoting them to evidence')
    tags.add_argument('root');tags.add_argument('path')
    tags.add_argument('--profile',choices=R.PROFILES,default='internal')
    tags.set_defaults(fn=cmd_tags)
    import argparse
    work = sub.add_parser('work', help='durable specialist tasks, claims, permissions and handoffs')
    work.add_argument('work_args', nargs=argparse.REMAINDER)
    work.set_defaults(fn=cmd_work)
    investigation=sub.add_parser('investigate',help='crawl declared relations with capability-gated documentary experts; not a factual answer')
    investigation.add_argument('root');investigation.add_argument('question')
    investigation.add_argument('--profile',choices=R.PROFILES,default='internal')
    investigation.add_argument('--source',action='append',help='exact eligible source record ID to start from; repeat for multiple seeds')
    investigation.add_argument('--max-hops',type=int,default=2)
    investigation.add_argument('--max-sources',type=int,default=12)
    investigation.add_argument('--max-source-chars',type=int,default=200000)
    investigation.add_argument('--work-directory',help='new private directory to retain specialist work and host recovery credential')
    investigation.set_defaults(fn=cmd_investigate)
    reconstruction=sub.add_parser('reconstruct',help='inspect checked documentary evidence, candidate graph, layers and unresolved obligations')
    reconstruction.add_argument('root');reconstruction.add_argument('question')
    reconstruction.add_argument('--profile',choices=R.PROFILES,default='internal')
    reconstruction.add_argument('--max-passages',type=int,default=12)
    reconstruction.add_argument('--max-context-chars',type=int,default=12000)
    reconstruction.add_argument('--reader-model',help='optional explicitly installed local candidate reader; never historical truth authority')
    reconstruction.add_argument('--reader-endpoint',default='http://127.0.0.1:11434')
    reconstruction.set_defaults(fn=cmd_reconstruct)
    correction=sub.add_parser('correct-claim',help='explicitly revise one unique source span while preserving the predecessor and unaffected text')
    correction.add_argument('root');correction.add_argument('source_id')
    correction.add_argument('--old-quote',required=True);correction.add_argument('--new-quote',required=True)
    correction.add_argument('--effective-at',default='')
    correction.add_argument('--corrects-field')
    correction.add_argument('--valid-from');correction.add_argument('--valid-until')
    correction.add_argument('--profile',choices=R.PROFILES,default='internal')
    correction.set_defaults(fn=cmd_correct_claim)
    return parser


def main(argv=None):
    parser=build_parser();args=parser.parse_args(argv)
    if not hasattr(args,'fn'):parser.print_help();return 1
    return args.fn(args)

if __name__=='__main__':
    raise SystemExit(main())
