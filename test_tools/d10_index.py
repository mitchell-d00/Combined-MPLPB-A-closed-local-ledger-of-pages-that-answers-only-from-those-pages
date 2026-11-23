"""Build a D10 suite registry and a deterministic ten-topic preparation plan."""
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return sha256(encoded(value)).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(raw), sha256(raw).hexdigest()


def write(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write('\n')


def index(topics_path, study_path):
    topics, topic_pin = read(topics_path)
    study, study_pin = read(study_path)
    if topics.get('topic_metadata_only') is not True:
        raise ValueError('D100 catalog must declare its topics to be metadata only')
    topic_index = defaultdict(list)
    for row in topics['entries']:
        topic_index[row['section']].append({'title': row['topic'], 'topic_url': row['url']})

    suites = {}
    for row in study['catalog']['classes']:
        family = row['family']
        if family in suites:
            raise ValueError(f'Duplicate D% class: {family}')
        status = row['status']
        suite = {'family': family, 'dpercent_status': status}
        if status == 'executable':
            suite['dpercent_measurement'] = row['measurement']
            suite['development_receipt_cases'] = study['family_counts'][family]
            suite['live_surface_status'] = ('ready_for_frozen_capture' if family == 'exact_anchor'
                                            else 'requires_source_and_pair_adapter')
            suite['pair_plan'] = (
                ['source_supported_obligation', 'one_changed_required_obligation']
                if row['measurement'] == 'source_answer_or_refusal'
                else ['required_anchored_observation', 'one_forbidden_graph_promotion_control']
            )
        elif status == 'not_measured_by_this_worker':
            suite['reason'] = row['reason']
            suite['live_surface_status'] = 'needs_dedicated_adapter_or_review'
        else:
            raise ValueError(f'Unknown D% class status: {status}')
        suites[family] = suite
    if set(study['family_counts']) != {family for family, row in suites.items()
                                       if row['dpercent_status'] == 'executable'}:
        raise ValueError('D% measured family coverage differs from catalog')
    return {
        'schema': 'mplpb-d10-suite-index-v1',
        'sources': {'d100_topic_catalog_sha256': topic_pin, 'dpercent_study_sha256': study_pin,
                    'd100_revision_url': topics['catalog_revision_url']},
        'topic_sections': dict(topic_index),
        'suites': suites,
        'counts': {'topics': sum(map(len, topic_index.values())), 'sections': len(topic_index),
                   **Counter(row['dpercent_status'] for row in suites.values())},
        'authority': 'development_plan',
    }


def plan(registry, family, seed):
    suite = registry['suites'][family]
    if suite['dpercent_status'] != 'executable':
        raise ValueError(f'{family} requires a dedicated adapter or independent review')
    sections = registry['topic_sections']
    ordered_sections = sorted(sections, key=lambda name: digest([seed, family, 'section', name]))
    if len(ordered_sections) < 10:
        raise ValueError('A D10 plan requires ten distinct topic sections')
    draws = []
    for number, section in enumerate(ordered_sections[:10], 1):
        row = min(sections[section], key=lambda topic: digest([seed, family, section, topic]))
        draws.append({'id': f'D10-{number:02d}', 'section': section, **row,
                      'status': 'source_needed', 'pair_plan': suite['pair_plan']})
    return {'schema': 'mplpb-d10-draw-plan-v1', 'seed': seed, 'suite': family,
            'index_sha256': digest(registry), 'draws': draws, 'capture_status': 'not_run',
            'answer_supported': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--topics', required=True, type=Path)
    parser.add_argument('--study', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    targets = parser.add_argument_group('optional draw plan')
    targets.add_argument('--suite')
    targets.add_argument('--seed')
    targets.add_argument('--plan-output', type=Path)
    args = parser.parse_args()
    if sum(value is not None for value in (args.suite, args.seed, args.plan_output)) not in (0, 3):
        parser.error('Provide --suite, --seed, and --plan-output together')
    try:
        registry = index(args.topics, args.study)
        draw = plan(registry, args.suite, args.seed) if args.suite else None
        write(args.output, registry)
        if draw:
            write(args.plan_output, draw)
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
