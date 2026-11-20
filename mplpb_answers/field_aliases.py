"""Bounded question-label normalization from eligible body declarations.

Language rules locate a source field; only the existing exact-field checker
can establish source support. No value, title or model suggests a field.
"""
import copy
import re

VERSION = 'source-field-alias-v1'
MAX_SOURCES = 64
MAX_BODY_BYTES = 2 * 1024 * 1024
MAX_DECLARATIONS = 256


def candidates(field):
    """Directional lexical rules and role-preserving noun reordering only."""
    from .relation_graph import _FIELD_QUALIFIER
    if not field or _FIELD_QUALIFIER.search(field):
        return {}
    groups = {
        'phone number': ('telephone number',),
        'telephone number': ('phone number',),
        'phone no': ('phone number', 'telephone number'),
        'telephone no': ('phone number', 'telephone number'),
        'postcode': ('postal code',),
        'postal code': ('postcode',),
        # Never reverse status into a geographic "state" declaration.
        'current state': ('current status', 'present status'),
        'present state': ('current status', 'present status'),
        'current status': ('present status',),
        'present status': ('current status',),
    }
    result = {name: 'bounded_document_field_lexicon' for name in groups.get(field, ())}
    m = re.fullmatch(r'(date|time|location) of ([a-z][a-z0-9]*(?: [a-z0-9]+){0,3})', field)
    if m:
        result[m[2]+' '+m[1]] = 'role_preserving_of_reordering'
    m = re.fullmatch(r'([a-z][a-z0-9]*(?: [a-z0-9]+){0,3}) (date|time|location)', field)
    if m:
        result[m[2]+' of '+m[1]] = 'role_preserving_of_reordering'
    return result


def _state(gate):
    from .evidence_contract import pin
    return pin({'snapshot': gate.corpus_snapshot, 'policy': gate.policy,
                'sources': [(s['id'], s['hash']) for s in gate.sources], 'excluded': gate.excluded})


def resolve(root, question, profile, request, as_of=None):
    from .passages import PassageIndex
    from .relation_graph import declared_fields, field_contexts
    from .body_text import body_text
    from .evidence_contract import ReaderError
    from mplpb_combined.ledger import serving_view
    alternatives = candidates(request['field'])
    if not alternatives or not request['record_id'] or request['exact_value']:
        return request
    result = copy.deepcopy(request)
    dependencies = []
    matches = {}; context_labels = set()

    def blocked(status, code):
        result['alias_resolution'] = {'status': status, 'code': code, 'dependencies': dependencies,
                                      'as_of': as_of, 'requested_field': request['field']}
        return result

    def probe(field, literal_probe=False):
        with serving_view(as_of, field):
            index = PassageIndex(root, question, profile, exact={**request, 'field': field})
            dependencies.append({'field': field, 'state': _state(index.gate)})
            records = [r for r in index.records if r.path in index.exact_paths]
            declarations = [f for r in records for f in declared_fields(r)]
            rows = [f for f in declarations if f['field'] == field]
            contexts = [f for r in records for f in field_contexts(r, field)]
            if literal_probe and (rows or contexts):
                return rows, contexts
            if (len(index.records) > MAX_SOURCES or
                    sum(len(body_text(r.body_html).encode('utf-8')) for r in index.records) > MAX_BODY_BYTES):
                raise ReaderError('alias_resolution_budget', 'Alias source inspection budget exhausted')
            if len(declarations) > MAX_DECLARATIONS:
                raise ReaderError('alias_resolution_budget', 'Alias declaration budget exhausted')
            return rows, contexts

    try:
        literal, contexts = probe(request['field'], literal_probe=True)
        if contexts and not literal:
            # Never route around a quoted/reported literal appearance.
            return request
        if literal:
            matches[request['field']] = literal
        if contexts:
            context_labels.add(request['field'])
        for field in alternatives:
            rows, contexts = probe(field)
            if rows:
                matches[field] = rows
            if contexts:
                context_labels.add(field)
    except ReaderError as exc:
        return blocked('blocked', exc.code)
    if not matches:
        return request
    if len(set(matches) | context_labels) != 1:
        result = blocked('ambiguous', 'field_alias_ambiguous')
        result['alias_resolution']['candidate_fields'] = sorted(set(matches) | context_labels)
        return result
    selected = next(iter(matches))
    result['field'] = selected
    result['alias_resolution'] = {'status': 'literal' if selected == request['field'] else 'resolved', 'dependencies': dependencies,
                                  'as_of': as_of, 'requested_field': request['field']}
    if selected == request['field']:
        return result
    metadata = result.setdefault('question_normalization', {})
    metadata.update(version=VERSION, requested_field=request['field'], field=selected,
                    record_id=request['record_id'], normalization_is_evidence=False,
                    basis=alternatives[selected], unresolved_obligations=[],
                    canonical_question=f'What is the {selected} for record {request["record_id"]}?',
                    source_field_anchors=[{k: f[k] for k in ('source_id', 'path', 'hash', 'body_start', 'body_end')}
                                          for f in matches[selected]])
    return result


def unchanged(root, question, profile, resolution):
    """Every inspected field view is a dependency, not a cached permission."""
    from mplpb_combined import provenance_gate as G
    from mplpb_combined.ledger import serving_view
    for dependency in resolution['dependencies']:
        with serving_view(resolution['as_of'], dependency['field']):
            if _state(G.gather(root, question, profile)) != dependency['state']:
                return False
    return True
