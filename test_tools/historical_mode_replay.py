"""Compare Ask, candidate lookup, and expert investigation on the frozen historical questions."""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from mplpb_answers.local_reader import OllamaLocalReader
from mplpb_answers.pipeline import answer_query
from mplpb_answers.support import candidate_answer
from mplpb_combined.reader import PROFILES, RETURN
from mplpb_work.investigation import investigate
from tools.article_study import file_pins
from tools.sorter_first_study import FAMILIES, ROOT
from tools.unprepared_challenge import frozen, read, save, sha
from tools.unprepared_sources import import_corpus


def ask_result(answer):
    return {'kind': answer['kind'], 'diagnostic': answer['diagnostic']['code'],
            'answer_supported': answer['answer_supported'],
            'citations': sum(len(claim['citations']) for claim in answer['claims'])}


def run(output, reader=None, *, include_advanced=False):
    rows, inputs = [], {}
    profile = PROFILES['internal']
    reader_identity = reader.describe() if reader else 'unconfigured'
    for family, (folder, seal) in FAMILIES.items():
        corpus = ROOT / folder
        frozen(corpus, seal)
        inputs[family] = {'seal_sha256': sha((corpus / seal).read_bytes()),
                          'questions_sha256': sha((corpus / 'questions.json').read_bytes())}
        with TemporaryDirectory(prefix='mplpb-mode-replay-') as tmp:
            ledger = Path(tmp) / 'ledger'
            import_corpus(corpus, ledger)
            initial = file_pins(ledger)
            for case in read(corpus / 'questions.json')['cases']:
                question = case['question']
                strict = answer_query(ledger, question, profile).contract
                assisted = answer_query(ledger, question, profile, mode='assisted', reader=reader).contract
                candidate, _ = candidate_answer(ledger, question, profile)
                report = investigate(ledger, question, profile=profile)
                if report['answer_supported']:
                    raise ValueError(f'Investigation promoted an answer for {case["id"]}')
                rows.append({
                    'id': case['id'], 'family': family,
                    'strict': ask_result(strict), 'assisted': ask_result(assisted),
                    'same_claims': strict['claims'] == assisted['claims'],
                    'candidate_lookup': {'kind': 'candidate_only' if candidate.kind == RETURN else candidate.kind,
                                         'source': candidate.record.id if candidate.kind == RETURN else None},
                    'investigation': {'kind': report['status'], 'answer_supported': report['answer_supported'],
                                      'sources': [source['id'] for source in report['sources']],
                                      'verified_observations': len(report['verification']['verified']),
                                      'declared_links': dict(Counter(link['status'] for link in report['relations'])),
                                      'receipts': [receipt['status'] for receipt in report['receipts']]},
                })
                if include_advanced:
                    from mplpb_answers.advanced import advanced_query
                    result = advanced_query(ledger, question, profile)
                    if result['strict'] != strict or result['answer_supported'] != strict['answer_supported']:
                        raise ValueError(f'Advanced MPLPB changed strict proof for {case["id"]}')
                    rows[-1]['advanced'] = {'kind': result['status'],
                                            'inspection': (result['inspection'] or {}).get('path')}
            if initial != file_pins(ledger):
                raise ValueError(f'Replay changed the imported ledger for {family}')
        frozen(corpus, seal)
    if len(rows) != 22:
        raise ValueError('Expected the unchanged historical 22')
    modes = ('strict', 'assisted', 'candidate_lookup', 'investigation')
    if include_advanced:
        modes += ('advanced',)
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() if (ROOT / '.git').exists() else None
    result = {'revision': revision, 'originals': inputs,
              'assisted_reader': reader_identity,
              'case_count': len(rows), 'outcomes': {mode: dict(Counter(case[mode]['kind'] for case in rows))
                                                   for mode in modes},
              'assisted_diagnostics': dict(Counter(case['assisted']['diagnostic'] for case in rows)),
              'cases': rows}
    save(output, result)
    print(json.dumps({k: result[k] for k in ('outcomes', 'assisted_diagnostics')}, indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--reader-model', help='Installed loopback Ollama model')
    parser.add_argument('--reader-digest', help='Expected digest of the installed model')
    parser.add_argument('--include-advanced', action='store_true')
    args = parser.parse_args()
    if bool(args.reader_model) != bool(args.reader_digest):
        parser.error('--reader-model and --reader-digest must be provided together')
    if args.output.exists():
        parser.error('Choose a new output file')
    reader = OllamaLocalReader(args.reader_model, model_digest=args.reader_digest) if args.reader_model else None
    return run(args.output, reader, include_advanced=args.include_advanced)


if __name__ == '__main__':
    raise SystemExit(main())
