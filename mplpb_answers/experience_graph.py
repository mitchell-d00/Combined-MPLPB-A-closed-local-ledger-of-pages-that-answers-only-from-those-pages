"""Local SQLite graph of strict boundaries, provenance pins and inspection passes."""
from contextlib import closing
import json
from pathlib import Path
import sqlite3

from .evidence_contract import canonical, pin
from .presentation import FOLLOW_UP_FLAGS

APPLICATION_ID = 0x4D504C58
VERSION = 1
_SCHEMA = """
CREATE TABLE passes (
    id INTEGER PRIMARY KEY,
    scope TEXT NOT NULL,
    state TEXT NOT NULL,
    route TEXT CHECK(route IN ('lookup', 'investigate', 'assisted')),
    candidates TEXT NOT NULL,
    previous INTEGER REFERENCES passes(id),
    recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    graph TEXT NOT NULL
);
CREATE INDEX scoped_passes ON passes(scope, state, id);
"""


def graph_keys(root, native, channel='advanced', selector=None):
    answer, gate = native.contract, native.gate
    scope = pin([channel, str(Path(root).resolve()), gate['profile'], answer['question'], selector])
    decision = {key: answer[key] for key in
                ('kind', 'answer_supported', 'claims', 'missing', 'diagnostic', 'code_sha256')}
    state = pin([gate['corpus_snapshot'], gate['policy'], decision])
    return scope, state


def _open(path):
    return sqlite3.connect(path, timeout=3)


def _check(db):
    if (db.execute('PRAGMA application_id').fetchone()[0] != APPLICATION_ID or
            db.execute('PRAGMA user_version').fetchone()[0] != VERSION):
        raise ValueError('File is not a compatible MPLPB experience graph')


def _empty(db):
    return (db.execute('PRAGMA application_id').fetchone()[0] == 0 and
            db.execute('PRAGMA user_version').fetchone()[0] == 0 and
            not db.execute('SELECT 1 FROM sqlite_master LIMIT 1').fetchone())


def previous(path, scope, state=None):
    path = Path(path).resolve()
    if not path.exists():
        return None
    with closing(sqlite3.connect(path.as_uri() + '?mode=ro', uri=True, timeout=3)) as db:
        if _empty(db):
            return None
        _check(db)
        restriction, params = (' AND state=?', (scope, state)) if state is not None else ('', (scope,))
        row = db.execute('SELECT id, route, candidates, state FROM passes WHERE scope=?' + restriction +
                         ' ORDER BY id DESC LIMIT 1', params).fetchone()
    if row is None:
        return None
    candidates = json.loads(row[2])
    if not isinstance(candidates, list) or any(not isinstance(item, str) for item in candidates):
        raise ValueError('Invalid experience candidate list')
    return {'id': row[0], 'flag': row[1], 'candidates': candidates, 'state': row[3]}


SEAM_FLAGS = frozenset({'current', 'retired', 'eligible', 'conflict', 'seam:handoff', 'pass:source-body',
                        'pass:inspection', 'pass:history', 'boundary:scope', 'boundary:open',
                        'boundary:warning', 'relation:checked', 'candidate:locator', *FOLLOW_UP_FLAGS})
NODE_FLAGS = {
    'pass': ('seam:handoff',), 'previous_pass': ('pass:history',),
    'seam': ('seam:handoff',), 'candidate_record': ('candidate:locator',),
    'claim': ('pass:source-body',), 'relation': ('relation:checked',),
    'source_span': ('eligible', 'pass:source-body'), 'boundary': ('boundary:warning',),
    'helper': ('candidate:locator',),
}


def graph_nodes(observation, decision, requested, selected, prior, candidates, snapshot, helper=None):
    """Build an inspectable graph from this fresh decision, using pins for witnesses."""
    nodes, edges = [{'id': 'pass', 'type': 'pass', 'requested_flag': requested,
                     'selected_flag': selected}], []
    if prior:
        nodes.append({'id': 'previous', 'type': 'previous_pass', 'pass_id': prior['id']})
        edges.append({'from': 'previous', 'to': 'pass', 'kind': 'followed_by'})
    diagnostic = observation['diagnostic']
    nodes.append({'id': 'seam', 'type': 'seam', 'code': diagnostic['code'],
                  'stage': observation['stopped_at'], 'result': observation['strict_kind']})
    edges.append({'from': 'pass', 'to': 'seam', 'kind': 'observed'})
    if helper:
        nodes.append({'id': 'helper', 'type': 'helper', 'suggestion_sha256': pin(helper)})
        edges.append({'from': 'seam', 'to': 'helper', 'kind': 'suggests_next_check'})
    for number, source_id in enumerate(candidates):
        ident = f'candidate-{number}'
        nodes.append({'id': ident, 'type': 'candidate_record', 'source_id': source_id})
        edges.append({'from': 'pass', 'to': ident, 'kind': 'located'})
    for count, warning in enumerate(decision['warnings']):
        ident = f'boundary-{count}'
        nodes.append({'id': ident, 'type': 'boundary', 'code': warning['code']})
        edges.append({'from': 'seam', 'to': ident, 'kind': 'requires_warning'})
    for number, unresolved in enumerate(decision['unresolved']):
        ident = f'unresolved-{number}'
        nodes.append({'id': ident, 'type': 'boundary', 'code': 'unresolved',
                      'obligation_sha256': pin(unresolved)})
        edges.append({'from': 'seam', 'to': ident, 'kind': 'left_open'})
    for number, claim in enumerate(decision['claims']):
        ident = f'claim-{number}'
        relation = (claim.get('proposition') or {}).get('relation')
        nodes.append({'id': ident, 'type': 'relation' if relation else 'claim',
                      'relation': relation, 'claim_sha256': pin(claim)})
        edges.append({'from': 'pass', 'to': ident, 'kind': 'presented_from_strict'})
        for count, warning in enumerate(decision['warnings']):
            if warning['code'] == 'source_scope':
                edges.append({'from': ident, 'to': f'boundary-{count}', 'kind': 'bounded_by'})
        for position, cite in enumerate(claim['citations']):
            span = f'{ident}-span-{position}'
            nodes.append({'id': span, 'type': 'source_span',
                          'source_id': cite['source_id'], 'path': cite.get('path'), 'hash': cite['hash'],
                          'body_start': cite.get('body_start'), 'body_end': cite.get('body_end')})
            edges.append({'from': ident, 'to': span, 'kind': 'cites'})
    for node in nodes:
        flags = set(NODE_FLAGS[node['type']])
        if node['type'] != 'previous_pass':
            flags.add('current')
        if node['type'] == 'seam' and observation['strict_kind'] == 'conflict':
            flags.add('conflict')
        if node.get('code') == 'source_scope':
            flags.add('boundary:scope')
        if node.get('code') == 'unresolved':
            flags.add('boundary:open')
        if node['type'] == 'pass':
            flags.add(requested)
            if selected:
                flags.update(('pass:inspection', selected))
        node['flags'] = sorted(flags)
    tagged = {node['id']: set(node['flags']) for node in nodes}
    for edge in edges:
        edge['flags'] = sorted(tagged[edge['from']] | tagged[edge['to']])
    return {'authority': 'experience_metadata', 'eligibility_snapshot': snapshot,
            'nodes': nodes, 'edges': edges}


def append(path, scope, state, route, candidates, prior, graph):
    for component in _components(graph).values():
        flags = component.get('flags')
        if (not isinstance(flags, list) or not flags or
                any(not isinstance(flag, str) or flag not in SEAM_FLAGS for flag in flags) or
                len(set(flags)) != len(flags)):
            raise ValueError('Graph path requires controlled, unique flags')
    path = Path(path)
    with closing(_open(path)) as db:
        with db:
            db.execute('BEGIN IMMEDIATE')
            if _empty(db):
                # executescript commits implicitly, so run each DDL statement
                # individually under the same write transaction as the pass.
                for statement in _SCHEMA.strip().split(';'):
                    if statement.strip():
                        db.execute(statement)
                db.execute(f'PRAGMA application_id={APPLICATION_ID}')
                db.execute(f'PRAGMA user_version={VERSION}')
            _check(db)
            cursor = db.execute('INSERT INTO passes(scope,state,route,candidates,previous,graph) '
                                'VALUES(?,?,?,?,?,?)',
                                (scope, state, route, canonical(candidates), prior['id'] if prior else None,
                                 canonical(graph)))
            return cursor.lastrowid


def read_pass(path, pass_id, *, include_version=False):
    """Inspect a stored graph without running Ask or creating a database."""
    uri = Path(path).resolve().as_uri() + '?mode=ro'
    with closing(sqlite3.connect(uri, uri=True, timeout=3)) as db:
        _check(db)
        row = db.execute('SELECT graph, scope, state, previous, recorded_at FROM passes WHERE id=?',
                         (pass_id,)).fetchone()
    if row is None:
        raise ValueError('Experience pass not found')
    graph = json.loads(row[0])
    if include_version:
        graph['version'] = {'pass_id': pass_id, 'scope': row[1], 'state': row[2],
                            'supersedes': row[3], 'recorded_at_utc': row[4]}
    return graph


def _components(graph):
    nodes = {('node', node['id']): node for node in graph['nodes']}
    edges = {('edge', edge['from'], edge['to'], edge['kind']): edge for edge in graph['edges']}
    if len(nodes) != len(graph['nodes']) or len(edges) != len(graph['edges']):
        raise ValueError('Experience graph contains duplicate identities')
    return nodes | edges


def _diff(system, stored):
    expected, actual = _components(system), _components(stored)
    differences = []
    for key in sorted(expected.keys() | actual.keys()):
        required = expected.get(key, {})
        recorded = actual.get(key, {})
        wanted, observed = set(required.get('flags', [])), set(recorded.get('flags', []))
        if wanted != observed or required != recorded:
            differences.append({
                'path': list(key), 'missing_from_graph': sorted(wanted - observed),
                'extra_in_graph': sorted(observed - wanted),
                'path_or_provenance_changed': (
                    {k: v for k, v in required.items() if k != 'flags'} !=
                    {k: v for k, v in recorded.items() if k != 'flags'}),
            })
    if stored.get('eligibility_snapshot') != system['eligibility_snapshot']:
        differences.append({'path': ['eligibility_snapshot'], 'missing_from_graph': [],
                            'extra_in_graph': [], 'path_or_provenance_changed': True})
    return differences


def recheck_path(path, matched):
    try:
        differences = _diff(matched['path'], read_pass(path, matched['pass_id']))
    except (OSError, TypeError, ValueError, KeyError, sqlite3.Error):
        return {'status': 'mismatch', 'reason': 'graph_unavailable', 'differences': []}
    if differences:
        return {'status': 'mismatch', 'reason': 'flag_or_path_differs', 'differences': differences}
    return matched


def sync_path(path, root, native, selector):
    """Match a recorded path to native system tags or append its next source version."""
    from .presentation import investigation_hint, judge, observe

    scope, state = graph_keys(root, native, 'strict', selector)
    observation = observe(native.contract, None)
    decision = judge(observation)
    # Every citation emitted by the native contract belongs to the strict
    # sync path, including attributed alternatives and incomplete evidence.
    decision['claims'] = native.contract['claims']
    helper = investigation_hint(native.contract)
    expected = graph_nodes(observation, decision, 'none', None, None, [],
                           native.gate['corpus_snapshot'], helper)
    try:
        prior = previous(path, scope)
        if prior and prior['state'] == state:
            pass_id = prior['id']
        else:
            pass_id = append(path, scope, state, None, [], prior, expected)
    except (OSError, TypeError, ValueError, KeyError, sqlite3.Error):
        return {'status': 'mismatch', 'reason': 'graph_unavailable', 'differences': []}
    result = recheck_path(path, {'status': 'matched', 'pass_id': pass_id, 'path': expected,
                                  'flag_vocabulary': sorted(SEAM_FLAGS)})
    if result['status'] == 'matched':
        result['helper'] = helper
    return result
