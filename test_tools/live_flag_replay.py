"""Compare graph-scoped and ordinary Strict Ask on frozen historical fixtures."""
from collections import Counter
from importlib import import_module
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from mplpb_answers.advanced import advanced_query
from mplpb_answers.pipeline import answer_query
from test_tools.four_score_twenty import PROFILE, import_packet
from tools.sorter_first_study import FAMILIES, ROOT
from tools.unprepared_challenge import frozen, read
from tools.unprepared_sources import import_corpus, load


def replay(root):
    historical = Counter()
    for collection, (directory, seal) in FAMILIES.items():
        corpus = ROOT / directory
        frozen(corpus, seal)
        ledger = root / collection
        import_corpus(corpus, ledger)
        for case in read(corpus / 'questions.json')['cases']:
            question = case['question']
            plain = answer_query(ledger, question, PROFILE).contract
            synced = answer_query(ledger, question, PROFILE, experience_graph=root / 'historical.sqlite')
            if synced.sync['status'] != 'matched' or synced.contract != plain:
                raise ValueError('Historical strict decision diverged: ' + case['id'])
            historical[plain['kind']] += 1

    bundle = ROOT / 'evaluation/d12/scout'
    scout = import_module('evaluation.d12.scout.run')
    scout.verify_files(bundle, 'protocol.sha256')
    scout.verify_files(bundle, 'inputs.sha256')
    packets = load(bundle / 'inputs/sources.json')
    cases = load(bundle / 'inputs/questions.json')
    passes = 0
    for packet in packets:
        ledger = root / packet['id']
        import_packet(bundle, packet['sources'], ledger)
        for case in cases:
            if case['packet'] != packet['id']:
                continue
            question = case['question']
            plain = answer_query(ledger, question, PROFILE).contract
            for _ in range(2):
                result = advanced_query(ledger, question, PROFILE, experience_graph=root / 'scout.sqlite')
                if result['flag_sync']['status'] != 'matched' or result['strict'] != plain:
                    raise ValueError('Scout strict decision diverged: ' + case['id'])
                passes += 1
    return {'historical_strict_kinds': dict(historical), 'scout_matching_passes': passes}


if __name__ == '__main__':
    with TemporaryDirectory(prefix='mplpb-live-flags-') as temporary:
        print(json.dumps(replay(Path(temporary)), indent=2))
