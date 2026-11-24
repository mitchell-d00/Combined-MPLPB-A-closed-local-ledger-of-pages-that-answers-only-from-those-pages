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
    try:
        if args.answer_mode == 'strict' and reader is not None:
            raise ValueError('Use --answer-mode assisted to enable the explicitly configured local reader')
        result = answer_query(args.root, args.question, _profile(args), mode=args.answer_mode, reader=reader,
                              min_confidence=args.assisted_threshold, max_passages=args.max_passages, max_chars=args.max_context_chars,
                              record_id=args.record_id,field=args.field,as_of=args.as_of,
                              experience_graph=args.experience_graph)
    except ValueError as exc:
        print(json.dumps({'error': str(exc), 'answer_supported': False}) if args.json
              else f'Invalid request: {exc}', file=sys.stderr)
        return 2
    data = result.legacy()
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif 'collection_filter' in result.contract:
        print(result.contract['kind'].upper().replace('_', ' '))
        print(result.contract['text'] or result.contract['diagnostic']['message'])
    elif (result.contract.get('documentary_support', {}).get('scope') == 'bounded_record_statements'
          or result.contract['diagnostic'].get('stage') == 'bounded_records'):
        contract = result.contract
        print(contract['kind'].upper().replace('_', ' '))
        print(contract['text'] or contract['diagnostic']['message'])
        for claim in contract['claims']:
            for cite in claim['citations']:
                print('[{source_id} {hash}] {quote}'.format(**cite))
    elif result.contract.get('question_parts'):
        contract = result.contract
        print(contract['kind'].upper().replace('_', ' '))
        for part in contract['question_parts']:
            label = f"{part['record_id']}: {part['field']}" if 'record_id' in part else part['field']
            print(label + ' [' + part['status'] + ']')
            if part['status'] != 'verified':
                print(part['diagnostic']['message'])
                for step in part['diagnostic']['next_steps']:
                    print(step)
        for claim in contract['claims']:
            for cite in claim['citations']:
                print('[{source_id} {hash}] {quote}'.format(**cite))
    elif args.answer_mode == 'strict':
        label = {'return':'SUPPORTED ANSWER', 'ambiguous':'AMBIGUOUS', 'not_in_corpus':'NO SUPPORTED ANSWER'}[data['kind']]
        print(label+'\n'+(R.render(result.strict, why=args.why) if data['kind'] == result.strict.kind else result.contract['text'] or data['reason']))
        if result.contract['diagnostic']['code'] == 'partial_procedure_evidence':
            print(result.contract['text'])
        if result.contract['kind'] == 'conflict' and result.contract['claims']:
            for claim in result.contract['claims']:
                for citation in claim['citations']:
                    print('[{source_id} {hash}] {quote}'.format(**citation))
        if result.strict.kind != 'return':
            print('Diagnostic: '+result.contract['diagnostic']['code']+' — '+result.contract['diagnostic']['message'])
        if result.contract['diagnostic'].get('evidence_gap'):
            for step in result.contract['diagnostic']['next_steps']:
                print('Next: ' + step)
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
        if (result.sync or {}).get('status') == 'mismatch':
            print(json.dumps(result.sync, ensure_ascii=False, sort_keys=True))
        _print_graph_helper(result.sync)
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


def cmd_advanced(args):
    from .advanced import advanced_query
    from .local_reader import OllamaLocalReader

    try:
        if bool(args.reader_model) != bool(args.reader_digest):
            raise ValueError('Provide the local model and its digest together')
        reader = OllamaLocalReader(args.reader_model, model_digest=args.reader_digest) if args.reader_model else None
        result = advanced_query(args.root, args.question, R.PROFILES[args.profile],
                                follow_up=args.follow_up, reader=reader,
                                experience_graph=args.experience_graph)
    except (OSError, ValueError) as exc:
        print(f'Advanced MPLPB stopped: {exc}', file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result['status'].replace('_', ' ').upper())
        strict = result['strict']
        experience = result.get('experience')
        if experience:
            print(experience['presentation']['text'])
            if experience['pass_id'] is not None:
                print(f"Experience pass: {experience['pass_id']}")
        elif strict:
            print(strict['text'] or strict['diagnostic']['message'])
            for claim in strict['claims']:
                for cite in claim['citations']:
                    print('[{source_id} {hash}] {quote}'.format(**cite))
        inspection = result['inspection']
        if inspection:
            detail = inspection['detail']
            print(f"Inspection ({inspection['path']}): {detail.get('kind') or detail['status']}")
            if inspection.get('label'):
                print(inspection['label'])
            if inspection['path'] == 'assisted':
                print(detail['text'] or detail['diagnostic']['message'])
                for claim in detail['claims']:
                    for cite in claim['citations']:
                        print('[{source_id} {hash}] {quote}'.format(**cite))
            else:
                ids = detail['source_ids'] if inspection['path'] == 'lookup' else [s['id'] for s in detail['sources']]
                if ids:
                    print('Records to inspect: ' + ', '.join(ids))
        if result['next_step']:
            print(result['next_step'])
        if (result.get('flag_sync') or {}).get('status') == 'mismatch':
            print(result['strict']['diagnostic']['code'])
            print(json.dumps(result['flag_sync'], ensure_ascii=False, sort_keys=True))
        _print_graph_helper(result.get('flag_sync'))
    return {'supported_answer': 0, 'conflict': 2, 'partial_answer': 4, 'clarify': 5}.get(result['status'], 3)


def _print_graph_helper(sync):
    helper = (sync or {}).get('helper')
    if helper:
        print(helper['label'])
        print(helper['text'])
        for cite in helper['citations']:
            print('[{source_id} {hash}] {quote}'.format(**cite))


def cmd_experience_pass(args):
    import sqlite3
    from .experience_graph import history, read_pass

    try:
        result = (history(args.graph, args.pass_id, args.history) if args.history is not None
                  else read_pass(args.graph, args.pass_id, include_version=True))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, sqlite3.Error) as exc:
        print(f'Experience graph stopped: {exc}', file=sys.stderr)
        return 2
    return 0


def cmd_advanced_train(args):
    from mplpb_work.training import orchestrate

    try:
        result = orchestrate(args.fixtures.read_bytes(), args.key.read_bytes(), args.baseline.read_bytes(),
                             candidate_rule=args.candidate.read_bytes() if args.candidate else None,
                             objective=args.objective)
        with args.output.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
    except (OSError, ValueError) as exc:
        print(f'Advanced MPLPB training stopped: {exc}', file=sys.stderr)
        return 2
    print(result['status'])
    return int(result['status'] in {'candidate_blocked', 'review_needed'})


def cmd_narrate(args):
    from .local_narrator import narrate
    try:
        result = narrate(args.question, args.corpus, args.profile, no_model=args.no_model)
    except (ValueError, OSError) as exc:
        print(json.dumps({'error': str(exc), 'answer_supported': False}), file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(('VALIDATED FORMATTING' if result.narration['status'] == 'validated_formatting'
               else 'LEDGER ONLY') + ' — ' + result.kind)
        print(result.text)
        if result.narration['reason']:
            print('Narrator: ' + result.narration['reason'])
        for claim in result.ledger_result.get('claims', []):
            for cite in claim.get('citations', []):
                print('[{source_id} {hash} {path}:{body_start}-{body_end}] {quote}'.format(**cite))
        print(result.ledger_result['source_assurance']['notice'])
    return {'supported_answer': 0, 'conflict': 2, 'clarify': 5,
            'partial_answer': 4}.get(result.kind, 3)


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
            max_chars=args.max_source_chars,work_directory=args.work_directory,
            adaptive_search=args.adaptive_search)
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
    inspection = next(((operation, ids) for operation, ids in (
        ('wording', args.compare_wording), ('writing_dates', args.earliest_writing_date),
        ('request_dispatch_receipt', args.trace_sources)) if ids), None)
    result=reconstruct_report(args.root,args.question,R.PROFILES[args.profile],
                              max_passages=args.max_passages,max_chars=args.max_context_chars,reader=reader,
                              inspection=inspection)
    from mplpb_work.prose_evidence import render_reconstruction
    print(render_reconstruction(result) if args.format=='text' else json.dumps(result,indent=2,ensure_ascii=False))
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


def cmd_article(args):
    from pathlib import Path
    from .evidence_contract import loads, ReaderError
    from mplpb_work.article import assemble, render
    try:
        with Path(args.plan).open('rb') as stream:
            raw = stream.read(65537)
        if len(raw) > 65536:
            raise ValueError('Article plan exceeds 64 KiB')
        plan = loads(raw.decode('utf-8'))
        result = assemble(args.root, plan, R.PROFILES[args.profile],
                          max_passages=args.max_passages, max_chars=args.max_context_chars)
    except (ValueError, OSError, ReaderError) as exc:
        print(json.dumps({'error': str(exc), 'answer_supported': False}), file=sys.stderr)
        return 2
    print(render(result) if args.format == 'text' else json.dumps(result, indent=2, ensure_ascii=False))
    # Exit 0 means a dossier was assembled, never that history was resolved.
    return 0 if result['status'] == 'article_snapshot' else 3


def build_parser():
    parser = legacy_parser()
    parser.prog = 'mplpb-combined'
    for action in parser._actions:
        if action.dest == 'version': action.version = __version__ + ' (supported CLI; legacy core 1.0.0)'
    sub = next(a for a in parser._actions if hasattr(a, 'choices') and isinstance(a.choices, dict))
    ask = sub.choices['ask']
    ask.set_defaults(fn=cmd_ask)
    from pathlib import Path
    ask.add_argument('--answer-mode', choices=['strict', 'assisted'], default='strict')
    ask.add_argument('--experience-graph', type=Path, help='Require a current matching experience graph path')
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
    advanced = sub.add_parser('advanced', help='choose a source inspection after strict Ask')
    advanced.add_argument('root')
    advanced.add_argument('question')
    advanced.add_argument('--profile', choices=R.PROFILES, default=R.DEFAULT_PROFILE)
    from .advanced import PATHS
    advanced.add_argument('--follow-up', choices=PATHS, default='auto')
    advanced.add_argument('--experience-graph', type=Path, help='Read and record local inspection passes in SQLite')
    advanced.add_argument('--reader-model')
    advanced.add_argument('--reader-digest')
    advanced.add_argument('--json', action='store_true')
    experience = sub.add_parser('experience-pass', help='inspect one recorded experience graph pass')
    experience.add_argument('graph', type=Path)
    experience.add_argument('pass_id', type=int)
    experience.add_argument('--history', nargs='?', const=25, type=int, metavar='LIMIT',
                            help='list recent versions of this pass scope')
    experience.set_defaults(fn=cmd_experience_pass)
    advanced.set_defaults(fn=cmd_advanced)
    training = sub.add_parser('advanced-train', help='freeze, diagnose, and test one bounded rule')
    for parameter in ('fixtures', 'key', 'baseline', 'output'):
        training.add_argument(parameter, type=Path)
    selection = training.add_mutually_exclusive_group()
    selection.add_argument('--candidate', type=Path)
    selection.add_argument('--objective', choices=('elapsed_days', 'inclusive_days'))
    training.set_defaults(fn=cmd_advanced_train)
    narrator = sub.add_parser('narrate', help='optionally format a strict answer with a constrained local model')
    narrator.add_argument('question')
    narrator.add_argument('--corpus', required=True)
    narrator.add_argument('--profile', choices=R.PROFILES, default=R.DEFAULT_PROFILE)
    narrator.add_argument('--no-model', action='store_true', help='use the pure ledger result without model calls')
    narrator.add_argument('--json', action='store_true')
    narrator.set_defaults(fn=cmd_narrate)
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
    investigation.add_argument('--adaptive-search',action='store_true',
                               help='prioritize declared supersession and uncovered question terms within each hop')
    investigation.add_argument('--work-directory',help='new private directory to retain specialist work and host recovery credential')
    investigation.set_defaults(fn=cmd_investigate)
    reconstruction=sub.add_parser('reconstruct',help='inspect checked documentary evidence, candidate graph, layers and unresolved obligations')
    reconstruction.add_argument('root');reconstruction.add_argument('question')
    reconstruction.add_argument('--profile',choices=R.PROFILES,default='internal')
    reconstruction.add_argument('--format',choices=('json','text'),default='json',help='readable source evidence or compatible full JSON')
    reconstruction.add_argument('--max-passages',type=int,default=12)
    reconstruction.add_argument('--max-context-chars',type=int,default=12000)
    reconstruction.add_argument('--reader-model',help='optional explicitly installed local candidate reader; never historical truth authority')
    reconstruction.add_argument('--reader-endpoint',default='http://127.0.0.1:11434')
    selected = reconstruction.add_mutually_exclusive_group()
    selected.add_argument('--compare-wording', nargs=2, metavar=('SOURCE_A', 'SOURCE_B'))
    selected.add_argument('--earliest-writing-date', nargs=2, metavar=('SOURCE_A', 'SOURCE_B'))
    selected.add_argument('--trace-sources', nargs=3, metavar=('REQUEST', 'DISPATCH', 'RECEIPT'))
    reconstruction.set_defaults(fn=cmd_reconstruct)
    article = sub.add_parser('article', help='assemble checked/candidate research sections; no article-level proof')
    article.add_argument('root')
    article.add_argument('--plan', required=True, help='UTF-8 JSON with a title and 1–8 original questions')
    article.add_argument('--profile', choices=R.PROFILES, default='internal')
    article.add_argument('--format', choices=('json', 'text'), default='json')
    article.add_argument('--max-passages', type=int, default=12)
    article.add_argument('--max-context-chars', type=int, default=12000)
    article.set_defaults(fn=cmd_article)
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
