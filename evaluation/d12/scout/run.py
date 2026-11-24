"""Scout post-freeze replay. Native runs read the source packet and questions only."""
import argparse
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from mplpb_answers.advanced import advanced_query
from mplpb_answers.documentary import plan
from mplpb_answers.passages import PassageIndex
from mplpb_answers.pipeline import answer_query
from mplpb_combined.reader import terms
from mplpb_work.investigation import investigate
from test_tools.four_score_twenty import PROFILE, import_packet
from tools.unprepared_sources import inside, load, save, sha

CHARACTERS = 8000


def verify_files(root, manifest):
    for line in (root / manifest).read_text().splitlines():
        expected, name = line.split(maxsplit=1)
        if sha(inside(root, name).read_bytes()) != expected:
            raise ValueError(f'Frozen input changed: {name}')


def search(index, question, limit):
    query = terms(question)
    overlap = [(len(query & terms(p['text'])), p) for p in index.passages]
    ordered = sorted(overlap, key=lambda pair: (-pair[0], pair[1]['source_id'], pair[1]['body_start']))
    baseline, size = [], 0
    for count, passage in ordered:
        if count and size + len(passage['text']) <= CHARACTERS:
            baseline.append(passage)
            size += len(passage['text'])
        if len(baseline) == limit:
            break
    return {'overlap': baseline, 'native': index.retrieve([question], limit, CHARACTERS)['passages']}


def scout(bundle):
    verify_files(bundle, 'protocol.sha256')
    verify_files(bundle, 'inputs.sha256')
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    if revision != (bundle / 'engine.txt').read_text().strip():
        raise ValueError('Use the frozen engine checkout')
    if subprocess.check_output(['git', 'status', '--porcelain']):
        raise ValueError('The frozen engine checkout must be clean, including untracked files')
    packets = load(bundle / 'inputs/sources.json')
    cases = load(bundle / 'inputs/questions.json')
    rows = []
    with TemporaryDirectory(prefix='mplpb-scout-') as tmp:
        for packet in packets:
            root = Path(tmp) / packet['id']
            ledger, graph = root / 'ledger', root / 'scout.sqlite'
            import_packet(bundle, packet['sources'], ledger)
            for case in cases:
                if case['packet'] != packet['id']:
                    continue
                question = case['question']
                native = answer_query(ledger, question, PROFILE).contract
                index = PassageIndex(ledger, question, PROFILE)
                evidence = {f'{method}_{limit}': passages
                            for limit in (3, 12) for method, passages in search(index, question, limit).items()}
                passes = [advanced_query(ledger, question, PROFILE, experience_graph=graph) for _ in range(2)]
                expert = investigate(ledger, question, profile=PROFILE, max_hops=1, max_sources=4)
                rows.append({'id': case['id'], 'question': question, 'plan': plan(question), 'strict': native,
                             'discovery': evidence, 'advanced_passes': passes, 'expert': expert})
    return {'schema': 'scout-audit-v1', 'engine': revision,
            'inputs_sha256': sha((bundle / 'inputs.sha256').read_bytes()), 'cases': rows}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    options = parser.parse_args()
    save(options.output, scout(options.bundle))
