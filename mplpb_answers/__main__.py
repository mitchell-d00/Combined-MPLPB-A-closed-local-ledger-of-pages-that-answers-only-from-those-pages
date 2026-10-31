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
                          min_confidence=args.assisted_threshold, max_passages=args.max_passages, max_chars=args.max_context_chars)
    data = result.legacy()
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif args.answer_mode == 'strict':
        label = {'return':'SUPPORTED ANSWER', 'ambiguous':'AMBIGUOUS', 'not_in_corpus':'NO SUPPORTED ANSWER'}[data['kind']]
        print(label+'\n'+(R.render(result.strict, why=args.why) if data['kind'] == result.strict.kind else data['reason']))
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
    return parser


def main(argv=None):
    parser=build_parser();args=parser.parse_args(argv)
    if not hasattr(args,'fn'):parser.print_help();return 1
    return args.fn(args)

if __name__=='__main__':
    raise SystemExit(main())
