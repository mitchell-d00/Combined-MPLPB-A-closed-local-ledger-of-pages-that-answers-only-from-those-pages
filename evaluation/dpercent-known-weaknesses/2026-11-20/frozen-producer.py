"""Versioned, stratified known-weakness study; never changes old D% producers.

Keys remain outside execution. Graph checks measure textual structure, not truth.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import secrets
from tools import dpercent as D
from tools import dpercent_expanded as E

VERSION = 'dpercent-known-weaknesses-v1'
SORTER = (
    'duplicate_appearance', 'fenced_example', 'quoted_header', 'forwarded_header',
    'same_subject', 'changed_body', 'same_body_different_ids', 'concatenated_records',
    'unique_correction', 'partial_correction', 'quoted_correction', 'reported_correction',
    'negated_correction', 'conditional_correction', 'missing_target', 'ambiguous_target',
    'passive_correction', 'numbered_reference', 'punctuated_reference',
)
ALIASES = ('alias_role_date', 'alias_role_time', 'alias_role_location',
           'alias_adjective_date', 'alias_adjective_time', 'alias_adjective_location',
           'alias_collision', 'alias_geographic_state')
PENDING = {
    'crash_atomic_publication': 'Process-kill/storage adapter required; text questions cannot establish crash durability.',
    'classing_import_authorization': 'Classing transaction adapter required; sorter graph checks do not execute imports.',
    'reader_retired_snapshot_all_profiles': 'Retired-page export/reader adapter required; native suite has separate controls.',
    'scoped_correction_as_of': 'D% worker does not apply ledger correction transactions or as-of queries.',
    'source_change_during_verification': 'Concurrent mutation adapter required; static corruption is tested separately.',
    'model_tripwire_quality': 'No live model invoked; precision/recall of semantic flags unmeasured.',
    'local_narrator_hallucination': 'Narrator transport/mocked-model adapter required; no model execution here.',
    'cold_instance_continuity': 'Fresh-instance task-store adapter required; deterministic replay is not a continuity test.',
    'independent_semantic_accuracy': 'Independent review NOT RUN; authored keys do not certify historical truth.',
    'coherent_false_original': 'Closed evidence cannot detect an internally coherent false original without other evidence.',
    'dependent_corroboration': 'Shared ancestry/copy-dependency semantic assessment requires source-linked review.',
    'unfamiliar_event_identity': 'General event identity accuracy requires independently annotated unfamiliar records.',
    'exploration_budget_counterevidence': 'Dedicated exploration/proof-budget separation adapter required.',
    'long_document_ocr_page_boundaries': 'Dedicated long-document/OCR span-coverage adapter required.',
    'restriction_in_referenced_source': 'Nested source-access adapter required; source-level profile exclusions are tested.',
}
FAMILIES = tuple(D.FAMILIES) + tuple(E.FIELD_FAMILIES) + tuple('sorter_'+x for x in SORTER) + ALIASES


def catalog():
    rows = []
    for name in FAMILIES:
        rows.append({'family': name, 'status': 'executable',
                     'measurement': 'textual_graph_obligations_and_required_refusal' if name.startswith('sorter_') else 'source_answer_or_refusal',
                     'basis': 'retained D%, expanded stress, alias counterexamples, sorter regression classes'})
    rows += [{'family': k, 'status': 'not_measured_by_this_worker', 'reason': v} for k, v in PENDING.items()]
    return {'schema': VERSION+'-catalog', 'classes': rows,
            'scope': 'Known documented classes only; not a claim to enumerate unknown failures.',
            'independent_validation': 'NOT RUN'}


def material(number, family, dice):
    if family in D.FAMILIES:
        return D.case_material(number, family, dice)
    if family in E.FIELD_FAMILIES:
        return E.field_case(number, family, dice)
    ident = 'NOTE-'+str(30000+number)
    newline = dice.choose('new_line_ending', ('\n', '\r\n'))
    note = dice.choose('unicode_context', ('Zoë copied the note — 東京.', 'Émile read the entry.', 'Clerk copied this entry.'))
    fence = dice.choose('markdown_fence', ('```', '~~~'))
    ending = dice.choose('reference_punctuation', ('.', ';', ':', '!'))
    documents = []
    graph = {}
    def add(text):
        path = 'sources/item-%02d.md' % (len(documents)+1)
        documents.append(({'path': path, 'source_class': 'original'}, text.replace('\n', newline).encode('utf-8')))
    if family.startswith('alias_'):
        fields = {
            'alias_role_date': ('Accession Date', 'date of accession', '1851-05-04', True),
            'alias_role_time': ('Approval Time', 'time of approval', '14:20', True),
            'alias_role_location': ('Deposit Location', 'location of deposit', 'East vault', True),
            'alias_adjective_date': ('Due Date', 'date of due', '1851-05-04', False),
            'alias_adjective_time': ('Local Time', 'time of local', '14:20', False),
            'alias_adjective_location': ('General Location', 'location of general', 'East vault', False),
            'alias_collision': ('Telephone Number', 'telephone no', '020-555-0171', False),
            'alias_geographic_state': ('Current State', 'current status', 'Maine', False),
        }
        field, alias, value, positive = fields[family]
        text = f'Record-ID: {ident}\n{field}: {value}\n'
        if family == 'alias_collision': text += 'Phone Number: 020-555-0199\n'
        add(text+'\n'+note+'\n')
        form = dice.choose('alias_structure', E.FORMS)
        question = form.format(field=alias, id=ident)
        target = [f'{field}: {value}']
        expected = 'answer' if positive else 'refuse'
    else:
        kind = family.removeprefix('sorter_')
        real = f'Message-ID: {ident}\nSubject: Depot notice\n\nTwelve crates arrived. {note}\n'
        second = ident+'-NEXT'
        add(real)
        graph = {'primary_occurrences': 2, 'cluster_sizes': [], 'required_edges': [], 'forbidden_edges': []}
        correction_edges = ['possible_correction', 'possible_partial_correction']
        if kind in {'duplicate_appearance', 'fenced_example', 'changed_body'}:
            add(real if kind != 'changed_body' else real.replace('Twelve crates', 'Nine crates'))
            graph['cluster_sizes'] = [2]
            if kind == 'changed_body': graph['changed_bodies'] = True
            if kind == 'fenced_example':
                add('# Documentation\nExample only; not another communication.\n'+fence+'text\n'+real+fence+'\n')
                graph['embedded_identifiers_min'] = 1
        elif kind in {'quoted_header', 'forwarded_header'}:
            if kind == 'quoted_header': add('\n'.join('> '+line for line in real.splitlines())+'\n')
            else: add('----- Forwarded message -----\n'+real)
            graph.update(primary_occurrences=1, embedded_identifiers_min=1)
        elif kind in {'same_subject', 'same_body_different_ids'}:
            add(real.replace(ident, second) if kind == 'same_body_different_ids' else real.replace(ident, second).replace('Twelve', 'Six'))
        elif kind == 'concatenated_records':
            documents.clear(); add(real+'\n'+real.replace(ident, second))
        elif kind == 'numbered_reference':
            documents.clear(); add('Letter No. 41\n\nTwelve crates arrived.\n')
            add('Letter No. 42\n\nSee Letter No. 41.\n')
            graph['required_edges'] = ['explicit_reference_candidate']
        else:
            statements = {
                'unique_correction': f'This notice corrects {ident}: nine crates.',
                'partial_correction': f'This notice corrects {ident} only in quantity; the date remains unchanged.',
                'quoted_correction': f'> This notice corrects {ident}: nine crates.',
                'reported_correction': f'The porter said this corrects {ident}: nine crates.',
                'negated_correction': f'This notice does not correct {ident}.',
                'conditional_correction': f'If approved, this notice corrects {ident}: nine crates.',
                'missing_target': 'This notice corrects LOST-900: nine crates.',
                'ambiguous_target': f'This notice corrects {ident}: nine crates.',
                'passive_correction': f'{ident} is hereby corrected by this notice: nine crates.',
                'punctuated_reference': f'See {ident}{ending}',
            }
            add(f'Message-ID: {second}\nSubject: Depot notice\n\n'+statements[kind]+'\n')
            if kind == 'ambiguous_target':
                add(real); graph.update(primary_occurrences=3, cluster_sizes=[2])
            if kind in {'unique_correction', 'passive_correction'}: graph['required_edges'] = ['possible_correction']
            elif kind == 'partial_correction': graph['required_edges'] = ['possible_partial_correction']
            elif kind == 'punctuated_reference': graph['required_edges'] = ['explicit_reference_candidate']
            else:
                graph['required_edges'] = [] if kind == 'negated_correction' else ['unresolved_reference_review']
                graph['forbidden_edges'] = correction_edges
        question = f'Does record {ident} prove the crates were delivered and independently establish the historical event?'
        expected = 'refuse'; target = []
    case = {'id': 'DP%05d' % number, 'question': question, 'profile': 'internal',
            'sources': [s for s, _ in documents], 'budget': {'passages': 12, 'characters': 8000}}
    key = {'id': case['id'], 'family': family, 'expected': expected, 'required_propositions': [],
           'reference_sources': ['SOURCE-0001'] if expected == 'answer' else [], 'source_facts': [],
           'structural_expectations': graph, 'automatic_answer_matcher': 'literal_field_set_v1',
           'required_field_quotes': target, 'features': {'line_ending': 'CRLF' if newline == '\r\n' else 'LF',
                'fence': fence, 'source_count': len(documents), 'reference_punctuation': ending}}
    return case, documents, key


def prepare(out, custodian, count=4096, seed=None, shard_size=256):
    out, custodian = Path(out).resolve(), Path(custodian).resolve()
    if type(count) is not int or not 1 <= count <= 65536: raise ValueError('Cases must be 1–65536')
    if type(shard_size) is not int or not 1 <= shard_size <= 512: raise ValueError('Shard size must be 1–512')
    if out == custodian or out in custodian.parents or custodian in out.parents or custodian == D.ROOT or D.ROOT in custodian.parents:
        raise ValueError('Keep custody disjoint and outside repository')
    seed = secrets.randbits(128) if seed is None else seed
    if type(seed) is not int or not 0 <= seed < 2**128: raise ValueError('Invalid seed')
    out.mkdir(parents=True, exist_ok=False); custodian.mkdir(parents=True, mode=0o700, exist_ok=False)
    dice = D.Dice(seed)
    schedule = dice.shuffle('balanced_known_weakness_classes', [FAMILIES[i % len(FAMILIES)] for i in range(count)])
    shards = []; total_bytes = 0
    for start in range(0, count, shard_size):
        name = 'shard-%04d' % (start//shard_size+1); public = out/name; private = custodian/name
        public.mkdir(); private.mkdir(mode=0o700); keys = []; before = len(dice.rolls)
        for i in range(start, min(count, start+shard_size)):
            case, docs, key = material(i+1, schedule[i], dice); keys.append(key)
            folder = public/'packets'/case['id']; folder.mkdir(parents=True)
            for source, raw in docs:
                total_bytes += len(raw)
                if total_bytes > 128*1024**2: raise ValueError('128MiB global packet budget exceeded; partial preparation retained')
                path = folder/source['path']; path.parent.mkdir(exist_ok=True); path.write_bytes(raw)
            D.save(folder/'case.json', case)
        D.save(private/'key.json', {'schema': VERSION+'-key', 'cases': keys}); (private/'key.json').chmod(0o600)
        D.save(private/'dice.json', {'seed': str(seed), 'rolls': dice.rolls[before:]})
        D.save(public/'protocol.json', {'schema': VERSION, 'cases': len(keys), 'limits': D.LIMITS,
                                      'independent_validation': 'NOT RUN', 'no_language_acceptance_filter': True})
        seal = {'public_files': D.files(public), 'key_sha256': D.sha((private/'key.json').read_bytes()),
                'dice_sha256': D.sha((private/'dice.json').read_bytes()), 'generator_sha256': D.sha(Path(__file__).read_bytes()),
                'generator_dependencies': {str(p): D.sha((D.ROOT/p).read_bytes()) for p in ('tools/dpercent.py', 'tools/dpercent_expanded.py')},
                'worker_sha256': D.sha((D.ROOT/'tools/dpercent_worker.py').read_bytes())}
        D.save(public/'seal.json', seal); D.save(private/'public-seal-copy.json', seal)
        shards.append({'name': name, 'cases': len(keys), 'seal_sha256': D.sha((public/'seal.json').read_bytes())})
    D.save(custodian/'schedule-dice.json', {'seed': str(seed), 'rolls': dice.rolls})
    manifest = {'schema': VERSION, 'cases': count, 'shards': shards, 'family_counts': dict(Counter(schedule)),
                'catalog': catalog(), 'source_bytes': total_bytes, 'seed_commitment': D.sha(str(seed).encode()),
                'schedule_dice_sha256': D.sha((custodian/'schedule-dice.json').read_bytes()),
                'maximum_result_bytes': len(shards)*D.LIMITS['total_result_bytes'],
                'generator_sha256': D.sha(Path(__file__).read_bytes()), 'independent_validation': 'NOT RUN'}
    D.save(out/'study.json', manifest); D.save(custodian/'study-copy.json', manifest)
    return manifest


def graph_checks(graph, expected):
    """Explicit positive discovery requirements prevent vacuous empty-graph passing."""
    nodes, edges = graph['nodes'], graph['edges']
    clusters = [e for e in edges if e['kind'] == 'candidate_identity_cluster']
    kinds = {e['kind'] for e in edges}
    checks = {'complete_graph': graph['complete'], 'mode_nodes_identical': graph['nodes_identical_between_modes'],
              'mode_labels_identical': graph['node_labels_identical_between_modes'],
              'non_authoritative': graph['all_labels_non_authoritative']}
    if not expected: return checks
    checks['primary_occurrences'] = sum(n['kind']=='source_occurrence' and n.get('identity_role')=='declared_record_candidate' for n in nodes) == expected['primary_occurrences']
    checks['cluster_sizes'] = sorted(len(e['members']) for e in clusters) == expected['cluster_sizes']
    checks['required_edges'] = set(expected['required_edges']) <= kinds
    checks['forbidden_edges'] = not (set(expected['forbidden_edges']) & kinds)
    if 'embedded_identifiers_min' in expected:
        checks['embedded_inspectable'] = sum(n['kind']=='header_identifier' and n.get('primary_identity_eligible') is False for n in nodes) >= expected['embedded_identifiers_min']
    if expected.get('changed_bodies'): checks['changed_body_warning'] = any(e.get('changed_bodies') is True for e in clusters)
    return checks


def execute_shards(packets, custodian, output, implementation=D.ROOT, max_shards=None):
    packets, custodian, output = map(Path, (packets, custodian, output))
    manifest = D.read(packets/'study.json')
    if manifest != D.read(custodian/'study-copy.json'): raise ValueError('Study manifest differs from sealed custody copy')
    if max_shards is not None and (type(max_shards) is not int or max_shards < 1): raise ValueError('max_shards must be positive')
    output.mkdir(parents=True, exist_ok=True)
    completed = 0
    for shard in manifest['shards']:
        name = shard['name']; public = packets/name; private = custodian/name
        if D.sha((public/'seal.json').read_bytes()) != shard['seal_sha256']: raise ValueError('Shard seal changed')
        D.verify(public, private)
        dest = output/name; report = output/(name+'-score.json')
        if not dest.exists():
            if max_shards is not None and completed >= max_shards: continue
            D.run(public, dest, implementation=implementation); completed += 1
        if not report.exists():
            if not (dest/'run.json').exists(): continue
            E.score(public, private, dest, report)
    return summarize(packets, custodian, output)


def summarize(packets, custodian, output):
    packets, custodian, output = map(Path, (packets, custodian, output))
    manifest = D.read(packets/'study.json'); families = {}; finished = 0; features = {}
    if manifest != D.read(custodian/'study-copy.json'): raise ValueError('Study manifest changed')
    for family, count in manifest['family_counts'].items():
        families[family] = {'planned': count, 'executed': 0, 'outcomes': {}, 'graph_failures': 0}
    for shard in manifest['shards']:
        name = shard['name']; report = output/(name+'-score.json')
        if not report.exists(): continue
        D.verify(packets/name, custodian/name)
        score = D.read(report); keys = {k['id']: k for k in D.read(custodian/name/'key.json')['cases']}
        run = D.read(output/name/'run.json'); receipts = {r['case_id']: r for r in run['cases']}
        for row in score['cases']:
            family = families[row['family']]; family['executed'] += 1; finished += 1
            outcome = row['outcome']; family['outcomes'][outcome] = family['outcomes'].get(outcome, 0)+1
            for feature, value in keys[row['id']].get('features', {}).items():
                cohort = features.setdefault(feature, {}).setdefault(str(value), {'cases': 0, 'outcomes': {}})
                cohort['cases'] += 1
                cohort['outcomes'][outcome] = cohort['outcomes'].get(outcome, 0)+1
            if row['execution'] != 'completed': continue
            path = output/name/row['id']/'result.json'
            if D.sha(path.read_bytes()) != receipts[row['id']]['sha256']: raise ValueError('Execution output changed')
            data = D.read(path); checks = graph_checks(data['sorter'], keys[row['id']]['structural_expectations'])
            if not all(checks.values()): family['graph_failures'] += 1
        # Preserve per-case graph diagnostics separately from answer scores.
        diagnostics = []
        for row in score['cases']:
            if row['execution'] == 'completed':
                data = D.read(output/name/row['id']/'result.json')
                diagnostics.append({'id': row['id'], 'family': row['family'],
                    'checks': graph_checks(data['sorter'], keys[row['id']]['structural_expectations'])})
        target = output/(name+'-graph-checks.json')
        if target.exists():
            if D.read(target) != diagnostics: raise ValueError('Graph diagnostics changed')
        else: D.save(target, diagnostics)
    result = {'schema': VERSION+'-summary', 'planned': manifest['cases'], 'executed': finished,
              'not_run': manifest['cases']-finished, 'partial': finished != manifest['cases'], 'by_family': families, 'by_feature': features,
              'independent_validation': 'NOT RUN', 'semantic_relationship_precision': None,
              'semantic_relationship_recall': None, 'human_review_seconds': None,
              'unmeasured_classes': PENDING, 'caution': 'Graph obligations check textual observations, not historical identity or truth.'}
    # Publication of the derived progress summary is atomic; source ledger is never written.
    temporary = output/'summary.pending.json'; temporary.write_text(json.dumps(result, indent=2)+'\n'); temporary.replace(output/'summary.json')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__); sub = p.add_subparsers(dest='command', required=True)
    prep = sub.add_parser('prepare')
    for name in ('out', 'custodian'): prep.add_argument('--'+name, type=Path, required=True)
    prep.add_argument('--cases', type=int, default=4096); prep.add_argument('--seed', type=int); prep.add_argument('--shard-size', type=int, default=256)
    run = sub.add_parser('run')
    for name in ('packets', 'custodian', 'output'): run.add_argument('--'+name, type=Path, required=True)
    run.add_argument('--implementation', type=Path, default=D.ROOT); run.add_argument('--max-shards', type=int)
    sub.add_parser('catalog')
    a = p.parse_args()
    if a.command == 'prepare': result = prepare(a.out, a.custodian, a.cases, a.seed, a.shard_size)
    elif a.command == 'run': result = execute_shards(a.packets, a.custodian, a.output, a.implementation, a.max_shards)
    else: result = catalog()
    print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
