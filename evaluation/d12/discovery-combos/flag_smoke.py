"""Reproduce selected CLI routes using the recorded discovery candidates."""
import argparse
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from mplpb_answers.__main__ import main
from tools.sorter_first_study import FAMILIES, ROOT
from tools.unprepared_challenge import frozen, read, save
from tools.unprepared_sources import import_corpus


def run(replay, output):
    cases = {row['id']: row for row in read(replay)['rows']}
    path, seal = FAMILIES['original']
    corpus = ROOT / path
    frozen(corpus, seal)
    questions = {row['id']: row['question'] for row in read(corpus / 'questions.json')['cases']}
    rows = []
    with TemporaryDirectory() as tmp:
        ledger = Path(tmp) / 'ledger'
        import_corpus(corpus, ledger)
        for ident in ('H01', 'H09', 'H13'):
            question_args = [str(ledger), questions[ident]]
            investigation = ['investigate', *question_args, '--adaptive-search', '--max-hops', '1', '--max-sources', '4']
            seeds = list(cases[ident]['graph_sources'])[:4]
            for source in seeds:
                investigation.extend(['--source', source])
            for lane, command in [('graph_seeded_adaptive', investigation),
                                  ('reconstruction', ['reconstruct', *question_args])]:
                with redirect_stdout(io.StringIO()) as stream:
                    code = main(command)
                result = json.loads(stream.getvalue())
                rows.append({'id': ident, 'lane': lane, 'exit_code': code, 'status': result['status'],
                             'answer_supported': result['answer_supported'],
                             'native_kind': result.get('native_answer', {}).get('kind'),
                             'verified_observations': len(result.get('observations', [])),
                             'traversed_links': sum(link['status'] == 'traversed'
                                                    for link in result.get('relations', []))})
    save(output, {'cases': rows})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    run(args.replay, args.output)
