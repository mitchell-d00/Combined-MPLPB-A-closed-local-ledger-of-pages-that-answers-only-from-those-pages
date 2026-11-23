"""Replay discovery combinations with fixed passage budgets on the historical 22."""
import argparse
from collections import Counter, defaultdict
from copy import copy
from itertools import zip_longest
import gzip
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from mplpb_answers.passages import PassageIndex
from mplpb_answers.pipeline import answer_query
from mplpb_answers.synonym_graph import build, open_index
from test_tools.historical_graph_study import DATA, PROFILE, visible
from tools.article_study import file_pins
from tools.sorter_first_study import FAMILIES, ROOT
from tools.unprepared_challenge import code_pins, frozen, read, save, sha
from tools.unprepared_sources import import_corpus

BUDGET = (12, 8000)
WIDE = (24, 16000)
EXTENDED = (16, 11000)


def retrieve(index, question, ids=None, budget=BUDGET):
    if ids is not None:
        if not ids:
            return []
        index = copy(index)
        index.passages = [p for p in index.passages if p['source_id'] in ids]
        index.sources = [s for s in index.sources if s['id'] in ids]
    return index.retrieve([question], *budget)['passages']


def fuse(lanes, budget):
    seen, output, size = set(), [], 0
    for group in zip_longest(*lanes):
        for passage in group:
            if passage is None or passage['id'] in seen:
                continue
            if len(output) >= budget[0]:
                return output
            if size + len(passage['text']) <= budget[1]:
                output.append(passage)
                size += len(passage['text'])
                seen.add(passage['id'])
    return output


def status(answer):
    return [answer['kind'], answer['diagnostic']['code'], answer['answer_supported']]


def next_stage(answer, ordinary, combined, graph, expert):
    if answer['kind'] == 'conflict':
        return 'inspect_competing_witnesses'
    if answer['answer_supported']:
        return 'show_strict_citations'
    known = {p['id'] for p in ordinary}
    if any(p['id'] not in known for p in combined):
        return 'inspect_additional_eligible_spans'
    if graph or expert:
        return 'search_with_confirmed_record_or_field'
    return 'request_record_identifier_or_rephrase'


def view(p):
    return {key: p[key] for key in ('source_id', 'path', 'hash', 'body_start', 'text')}


def group_paths(result):
    follow_ups = {
        'show_strict_citations': None,
        'inspect_competing_witnesses': 'mplpb-combined reconstruct LEDGER QUESTION --format text',
        'inspect_additional_eligible_spans': 'Research probe: inspect graph candidates alongside ordinary passages',
        'search_with_confirmed_record_or_field':
            'mplpb-combined ask LEDGER QUESTION --answer-mode strict --record-id CONFIRMED_ID --field CONFIRMED_FIELD',
        'request_record_identifier_or_rephrase': 'Ask the operator to identify the source or clarify the question.',
    }
    groups = defaultdict(list)
    for row in result['rows']:
        action = row['suggested_next_step']
        groups[action].append({
            'id': row['id'], 'strict_status': row['strict'][0],
            'first_command': 'mplpb-combined advanced LEDGER QUESTION --follow-up none',
            'follow_up': follow_ups[action],
            'ordinary_anchor_matches': row['matched']['ordinary_12'],
            'graph_anchor_matches': row['matched']['graph_12'],
            'source_record_candidates': row['graph_sources'],
            'investigation_visits': row['expert_sources'],
            'inspection_is_proof': False,
        })
    return {'revision': result['revision'],
            'routing_inputs': 'Strict status and discovery probes. Draft anchors were opened after routing.',
            'groups': groups}


def run(output, article_replay, mode_report):
    expert = read(mode_report)
    baseline = read(article_replay / 'report.json')
    if baseline['cases'] != 22 or baseline['runtime_sha256'] != code_pins(ROOT):
        raise ValueError('Run the historical article baseline with this runtime before comparing discovery')
    with gzip.open(article_replay / 'packets.json.gz', 'rt', encoding='utf-8') as source:
        strict = {ident: answer for packet in json.load(source)
                  for ident, answer in zip(packet['ids'], packet['standalone'])}
    expert_rows = {row['id']: row for row in expert['cases']}
    rows = []
    with TemporaryDirectory() as folder:
        scratch = Path(folder)
        catalog = DATA / 'catalog.json'
        database = scratch / 'graph.db'
        build(database, read(catalog))
        with open_index(database) as graph:
            for family, (base, seal) in FAMILIES.items():
                corpus = ROOT / base
                frozen(corpus, seal)
                for kind, path in [('seal', corpus / seal), ('questions', corpus / 'questions.json')]:
                    key = kind + '_sha256'
                    pin = sha(path.read_bytes())
                    if pin != expert['originals'][family][key] or pin != baseline['originals'][family][key]:
                        raise ValueError('Historical input or prior replay pin differs')
                ledger = scratch / family
                import_corpus(corpus, ledger)
                original = file_pins(ledger)
                artifacts = []
                for case in read(corpus / 'questions.json')['cases']:
                    ident, question = case['id'], case['question']
                    prior = strict[ident]
                    expert_case = expert_rows[ident]
                    if prior['question'] != question or prior['kind'] != expert_case['strict']['kind']:
                        raise ValueError(f'Baseline or mode replay differs for {ident}')
                    index = PassageIndex(ledger, question, PROFILE)
                    graph_ids = graph.lookup(family, question)['records']
                    expert_ids = expert_case['investigation']['sources']
                    normal = retrieve(index, question)
                    narrow_graph = retrieve(index, question, graph_ids) if graph_ids else normal
                    narrow_expert = retrieve(index, question, expert_ids) if expert_ids else normal
                    paired = fuse([normal, narrow_graph], BUDGET)
                    all_arms = fuse([normal, narrow_graph, narrow_expert], BUDGET)
                    ordinary_extended = retrieve(index, question, budget=EXTENDED)
                    graph_append = fuse([normal + narrow_graph], EXTENDED)
                    expert_append = fuse([normal + narrow_expert], EXTENDED)
                    wide_ordinary = retrieve(index, question, budget=WIDE)
                    wide_combo = fuse([wide_ordinary, narrow_graph, narrow_expert], WIDE)
                    arms = {
                        'ordinary_12': normal, 'graph_12': narrow_graph, 'expert_12': narrow_expert,
                        'ordinary_graph_12': paired, 'all_three_12': all_arms, 'ordinary_24': wide_ordinary,
                        'all_three_24': wide_combo, 'ordinary_16': ordinary_extended,
                        'ordinary_then_graph_16': graph_append, 'ordinary_then_expert_16': expert_append,
                    }
                    hinted = answer_query(ledger, question, PROFILE, max_passages=12, max_chars=8000,
                                          source_hints=[view(p) for p in all_arms]).contract
                    route = next_stage(prior, normal, all_arms, graph_ids, expert_ids)
                    ordinary_keys = {p['id'] for p in normal}
                    new = [view(p) for p in all_arms if p['id'] not in ordinary_keys][:3]
                    artifacts.append((ident, arms, {
                        'id': ident, 'family': family,
                        'strict': status(prior), 'strict_with_combined_hints': status(hinted),
                        'same_native_claims': prior['claims'] == hinted['claims'],
                        'graph_sources': graph_ids, 'expert_sources': expert_ids,
                        'suggested_next_step': route, 'suggestion_spans': new,
                    }))
                if original != file_pins(ledger):
                    raise ValueError('Replay changed the imported ledger')
                # Open reference drafts only after every route and Ask result for this family is fixed.
                drafts = {row['id']: row['citations'] for row in read(corpus / 'reference-draft.json')['cases']}
                for ident, arms, row in artifacts:
                    anchors = drafts[ident]
                    row['draft_anchors'] = len(anchors)
                    row['matched'] = {name: visible(anchors, {'passages': passages})
                                      for name, passages in arms.items()}
                    rows.append(row)
                frozen(corpus, seal)
    if len(rows) != 22:
        raise ValueError('Expected the unchanged historical 22')
    scored = [r for r in rows if r['draft_anchors']]
    arms = rows[0]['matched']
    ref = {name: 'ordinary_' + name.rsplit('_', 1)[1] for name in arms}
    summary = {}
    for arm in arms:
        summary[arm]={'all_anchors_in':sum(r['matched'][arm]==r['draft_anchors'] for r in scored),
            'anchors_visible':sum(r['matched'][arm] for r in scored),
            'improved_cases':sum(r['matched'][arm]>r['matched'][ref[arm]] for r in scored),
            'regressed_cases':sum(r['matched'][arm]<r['matched'][ref[arm]] for r in scored)}
    result={'revision':(subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
                        if (ROOT / '.git').exists() else None),
            'catalog_sha256':sha((DATA/'catalog.json').read_bytes()),
            'expert_packet_sha256':sha(mode_report.read_bytes()),
            'cases_with_draft_anchors':len(scored),'total_draft_anchors':sum(r['draft_anchors'] for r in scored),
            'summary':summary,'suggested_next_steps':dict(Counter(r['suggested_next_step'] for r in rows)),
            'strict_status_changes':sum(r['strict']!=r['strict_with_combined_hints'] for r in rows),
            'strict_claim_changes':sum(not r['same_native_claims'] for r in rows),
            'answer_supported_delta':sum(r['strict_with_combined_hints'][-1]-r['strict'][-1] for r in rows),
            'rows':rows}
    save(output, result)
    print(json.dumps({k: v for k, v in result.items() if k != 'rows'}, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--article-replay', type=Path, required=True)
    parser.add_argument('--mode-report', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--paths-output', type=Path)
    args = parser.parse_args()
    result = run(args.output, args.article_replay, args.mode_report)
    if args.paths_output:
        save(args.paths_output, group_paths(result))


if __name__ == '__main__':
    main()
