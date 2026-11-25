"""Audit retained inventory receipts without executing the reader or transfer."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import tarfile


def load(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def meaning(answer):
    return {k: answer.get(k) for k in
            ('kind', 'answer_supported', 'text', 'claims', 'missing', 'clarification')}


def audit(root):
    folder = root / 'evaluation/current-failure-inventory'
    proposal = folder / 'proposal'
    freeze = load(proposal / 'freeze.json')
    for field, path in {
        'development_sha256': proposal / 'development.json',
        'transfer_seal_sha256': proposal / 'transfer-seal.json',
        'preservation_sha256': proposal / 'preservation.json',
        'generator_sha256': root / 'tools/freeze_reported_content_proposal.py',
        'rule_sha256': proposal / 'rule.md',
    }.items():
        assert freeze[field] == digest(path)
    scoring = load(proposal / 'scoring-seal.json')
    for field, path in {
        'freeze_sha256': proposal / 'freeze.json',
        'role_obligations_sha256': proposal / 'role-obligations.json',
        'fresh_development_key_sha256': folder / 'fresh-contrasts/expectations.json',
        'matched_control_key_sha256': folder / 'matched-contrasts/expectations.json',
    }.items():
        assert scoring[field] == digest(path)
    assert not scoring['reader_implementation_performed']
    all_rows = []
    for relative in ('', 'fresh-contrasts', 'matched-contrasts'):
        packet = folder / relative
        selection = load(packet / 'selection.json')
        receipt = load(packet / 'replay/receipt.json')
        summary = load(packet / ('analysis.json' if not relative else 'summary.json'))
        assert receipt['selection_sha256'] == digest(packet / 'selection.json')
        assert summary['selection_sha256'] == receipt['selection_sha256']
        assert len(selection['cases']) == len(receipt['cases']) == len(summary['cases'])
        for case, result, row in zip(selection['cases'], receipt['cases'], summary['cases'], strict=True):
            assert case['id'] == result['id'] == row['id']
            assert result['status'] == row['status'] == 'completed'
            inputs = packet / case['input_path']
            assert {str(p.relative_to(inputs)): digest(p) for p in inputs.rglob('*') if p.is_file()} == case['files']
            path = packet / 'replay' / case['suite'] / case['id'] / 'result.json'
            assert digest(path) == result['sha256']
            assert row['citations_valid'] and not row['unsupported_complete']
            all_rows.append(row)
    known, focus = [], []
    with tarfile.open(root / 'evaluation/dpercent-known-weaknesses/2026-11-20/execution.tar.gz') as old_known, \
            tarfile.open(root / 'evaluation/pole/open-items/focus-extend/native-readbacks.tar.gz') as old_focus:
        for case in load(folder / 'selection.json')['cases']:
            current = load(folder / 'replay' / case['suite'] / case['id'] / 'result.json')
            if case['suite'] == 'known':
                old = json.load(old_known.extractfile(f"run/{case['origin_shard']}/{case['id']}/result.json"))
                known.append({'id': case['id'], 'historical_complete': old['answer']['answer_supported'],
                              'current_complete': current['answer']['answer_supported'],
                              'meaning_equal': meaning(old['answer']) == meaning(current['answer'])})
            else:
                old = json.load(old_focus.extractfile(f"focus-after/{case['id']}/result.json"))
                focus.append({'id': case['id'], 'meaning_equal': meaning(old['answer']) == meaning(current['answer']),
                              'pack_equal': old['retrieval'] == current['retrieval']})
    # The direct-writing matched control has an authored typed key, not an independent judgment.
    matched = folder / 'matched-contrasts'
    key = next(k for k in load(matched / 'expectations.json') if k['id'] == 'FRESH-14')
    direct = load(matched / 'replay/fresh/FRESH-14/result.json')['answer']
    props = [c.get('proposition', {}) for c in direct['claims']]
    normal = lambda s: ' '.join(str(s).casefold().strip(' .').split())
    assert all(any(all(p.get(k) is v if type(v) is bool else normal(p.get(k)) == normal(v)
                       for k, v in target.items()) for p in props)
               for target in key['required_propositions'])
    reports = [r for r in all_rows if r['suite'] in ('known', 'focus') and r['family'] == 'reported_statement']
    assert len(reports) == 5
    assert all(r['source_key_full_discovery'] and r['native_documentary_goals'] == [] and
               r['diagnostic'] == 'interpretation_unsupported' for r in reports)
    result = {
        'native_baseline_commit': load(folder / 'selection.json')['baseline_commit'],
        'native_repair_in_this_update': False,
        'completed_current_cases': len(all_rows),
        'current_kinds': dict(Counter(r['kind'] for r in all_rows)),
        'positive_targets': sum(r['expected'] == 'answer' for r in all_rows),
        'non_full_support_controls': sum(r['expected'] != 'answer' for r in all_rows),
        'incorrect_full_support_on_negative_targets': sum(r['unsupported_complete'] for r in all_rows),
        'invalid_citations': sum(not r['citations_valid'] for r in all_rows),
        'reported_proof_budget_stops': sum(r['observed_failure_stage'] == 'budget' for r in all_rows),
        'partial_sorter_graphs': sum(not r['sorter_complete'] for r in all_rows),
        'known_historical_complete': sum(r['historical_complete'] for r in known),
        'known_current_complete': sum(r['current_complete'] for r in known),
        'known_lost_complete': sum(r['historical_complete'] and not r['current_complete'] for r in known),
        'known_recovered_complete': [r['id'] for r in known if not r['historical_complete'] and r['current_complete']],
        'old_meaning_views_equal': sum(r['meaning_equal'] for r in known + focus),
        'focus_discovery_packs_equal': sum(r['pack_equal'] for r in focus),
        'reported_content_first_stop': [r['id'] for r in reports],
        'independent_semantic_adjudication': 'NOT_RUN',
        'scope': 'Authored software keys and retained native contracts; not a 605-case census or independent semantic score.'
    }
    assert result['completed_current_cases'] == 111
    assert result['old_meaning_views_equal'] == 94
    assert result['focus_discovery_packs_equal'] == 32
    assert result['known_lost_complete'] == 0
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = audit(args.root)
    raw = json.dumps(result, indent=2) + '\n'
    if args.output:
        with args.output.open('x') as f:
            f.write(raw)
    print(raw)
