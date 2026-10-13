"""Default user CLI: supported answers, explicit legacy candidate inspection."""
import json
from mplpb_combined import reader as R
from mplpb_combined.__main__ import build_parser as legacy_parser, _profile
from .support import supported_answer
from . import __version__


def cmd_ask(args):
    result = supported_answer(args.root, args.question, _profile(args))
    if args.json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        label = {'return':'SUPPORTED ANSWER', 'ambiguous':'AMBIGUOUS', 'not_in_corpus':'NO SUPPORTED ANSWER'}[result.kind]
        print(label + '\n' + R.render(result, why=args.why))
    return {'return':0,'ambiguous':2,'not_in_corpus':3}[result.kind]


def cmd_candidates(args):
    result = R.answer(args.root, args.question, _profile(args))
    data = result.to_dict()
    data.update(mode='candidate_retrieval', answer_supported=False,
                notice='Legacy lexical candidates only. Scope does not establish body support.')
    print(json.dumps(data, indent=2, ensure_ascii=False) if args.json else
          'CANDIDATE RETRIEVAL — NOT A SUPPORTED ANSWER\n' + R.render(result, why=args.why))
    return {'return':0,'ambiguous':2,'not_in_corpus':3}[result.kind]


def build_parser():
    parser = legacy_parser()
    parser.prog = 'mplpb-combined'
    for action in parser._actions:
        if action.dest == 'version': action.version = __version__ + ' (supported CLI; legacy core 1.0.0)'
    sub = next(a for a in parser._actions if hasattr(a, 'choices') and isinstance(a.choices, dict))
    sub.choices['ask'].set_defaults(fn=cmd_ask)
    candidate = sub.add_parser('candidates', help='inspect legacy lexical candidates; not supported answers',
                               parents=[legacy_parser()._subparsers._group_actions[0].choices['ask']], add_help=False)
    candidate.set_defaults(fn=cmd_candidates)
    return parser


def main(argv=None):
    parser=build_parser();args=parser.parse_args(argv)
    if not hasattr(args,'fn'):parser.print_help();return 1
    return args.fn(args)

if __name__=='__main__':
    raise SystemExit(main())
