"""Score the frozen replay and diagnose the body-attribution prerequisite."""
import argparse
from collections import Counter
from pathlib import Path
import re
from tempfile import TemporaryDirectory

from mplpb_answers import documentary_verify as kernel
from mplpb_answers.passages import PassageIndex
from mplpb_combined.ledger import write
from mplpb_combined.reader import PROFILES
from tools import pole_authentic as a
from tools.pole_focus_extend import frus_fragment, frus_rendered


_REQUEST = re.compile(r'^How did (?P<actor>[A-Z][a-z]+(?: [A-Z][a-z]+)*) describe ')
_NAME = r'[A-Z][a-z]+(?: (?:[A-Z][a-z]+|[A-Z]\.)){0,5}'
_BODY_DECLARATION = {
    'assessment': re.compile(rf'^Address by (?P<name>{_NAME}) to (?:the )?[^.!?\n]+\.?$', re.M),
    'forecast': re.compile(rf'^(?:Article by|By) (?P<name>{_NAME})\.?$', re.M),
}
_HEADING = re.compile(r'<h2\b[^>]*>(.*?)</h2>', re.S)
_HEADING_NAME = re.compile(r'<span class="tei-persName">([^<]+)</span>')


def _require(condition, text):
    if not condition:
        raise ValueError(text)


def _same_person(requested, source_name):
    parts = source_name.split()
    return requested == source_name or (len(requested.split()) == 1 and requested == parts[-1])


def _span(body, start, end):
    return {'character_span': [start, end],
            'byte_span': [len(body[:start].encode()), len(body[:end].encode())],
            'sha256': a.digest(body[start:end].encode())}


def _heading_diagnostic(packet, source, raw, role, actor):
    headings = [(match, _HEADING_NAME.findall(match[1]))
                for match in _HEADING.finditer(frus_fragment(raw, source))]
    _require(len(headings) == 1 and len(headings[0][1]) == 1,
             'Publisher attribution heading is absent or ambiguous')
    heading, names = headings[0]
    expected = 'Address by ' if role == 'assessment' else 'Article by '
    _require(expected in heading[1].partition('<span')[0], 'Publisher heading role differs')
    name = ' '.join(names[0].split())
    ref = a.anchor(source, packet, heading[0])
    return {
        'name': name, 'matches_requested_actor': _same_person(actor, name),
        'authority': 'publisher_heading_diagnostic_only',
        'original_byte_span': ref['byte_span'],
        'original_character_span': ref['character_span'],
        'heading_span_sha256': a.digest(heading[0].encode(source['encoding'])),
    }


def _probe(packet, question, refs, sources):
    actor = _REQUEST.match(question['question'])['actor']
    with TemporaryDirectory(prefix='frus-pe01-') as scratch:
        work = Path(scratch)
        records = {}
        for ident in question['sources']:
            source = sources[ident]
            raw = (packet / source['path']).read_bytes()
            _require(a.digest(raw) == source['sha256'], 'Original source hash changed')
            records[ident] = write(
                work, doc_id=ident, title=ident, scope='public documentary originals',
                origin='machine', body_html=frus_rendered(raw, source),
                external='yes', when='2026-11-24T00:00Z')
        index = PassageIndex(work, question['question'], PROFILES['internal'])
        _require({r.path for r in index.records} == {r.path for r in records.values()}
                 and len(index.records) == 2
                 and all(r.kind == 'page' and not r.derived_from for r in index.records),
                 'Eligible source pair changed')
        reread = kernel.check(index, [])
        _require(reread['status'] == 'checked' and reread['scan_complete'],
                 'The native reread did not complete within the existing scan limits')
        obligations = []
        for role, ref in zip(('assessment', 'forecast'), refs, strict=True):
            record = records[ref['id']]
            source = sources[ref['id']]
            raw = (packet / source['path']).read_bytes()
            body = kernel.body_text(record.body_html)
            token = r'\s+'.join(re.escape(word) for word in ref['quote'].split())
            hits = list(re.finditer(token, body))
            _require(len(hits) == 1, 'Projected proposition anchor is absent or ambiguous')
            units = [(lo, hi) for r, lo, hi, _, _ in reread['contexts']
                     if r.path == record.path and lo <= hits[0].start() < hits[0].end() <= hi]
            _require(len(units) == 1 and units[0][1] - units[0][0] <= 2200,
                     'The anchor has no unique bounded complete native unit')
            regions = kernel.context_ranges(record)
            declarations = [
                m for m in _BODY_DECLARATION[role].finditer(body)
                if not kernel.quoted_context(body[:m.start()])
                and not kernel.META.search(body[:m.start()])
                and not any(lo < m.end() and hi > m.start() for lo, hi in regions)
            ]
            matches = [m for m in declarations if _same_person(actor, m['name'])]
            _require(not matches,
                     'An exact body attribution needs a separate proposition certification review')
            obligations.append({
                'role': role, 'source_id': record.id, 'original_path': ref['path'],
                'original_sha256': ref['sha256'], 'native_record_sha256': record.hash_actual,
                'original_proposition_byte_span': ref['byte_span'],
                'original_proposition_character_span': ref['character_span'],
                'native_complete_unit': _span(body, *units[0]),
                'eligible_body_attribution_matches': len(matches),
                'published_attribution': _heading_diagnostic(packet, source, raw, role, actor),
                'proposition_admitted': False,
                'reason': 'explicit_matching_canonical_body_attribution_missing',
            })
        _require(index.unchanged(), 'Eligible source state changed')
        return {
            'actor_in_question': actor, 'obligations': obligations,
            'examined_characters': reread['examined_characters'],
            'examined_units': reread['examined_units'],
            'limits_reached': reread['limits_reached'], 'limits': reread['limits'],
        }


def audit(packet, custody, freeze, rule, prior, before, after, output):
    held = a.read(freeze)
    seal = a.seal_for(packet)
    _require((held['packet_seal_sha256'], held['custody_key_sha256'], held['candidate_rule_sha256'])
             == (a.digest((packet / 'seal.json').read_bytes()), seal['key_sha256'], a.digest(rule.read_bytes())),
             'Packet, key or candidate rule changed')
    order = held['same_cases'] + held['added_controls']
    receipts = [a.read(path) for path in (before, after)]
    questions = a.read(packet / 'questions.json')
    _require(receipts[0]['revision'] == held['baseline_commit']
             and receipts[0]['runtime_sha256'] == receipts[1]['runtime_sha256']
             and all([row['id'] for row in rows] == order for rows in
                     (questions, receipts[0]['cases'], receipts[1]['cases'])),
             'Baseline, runtime, or ordered case coverage changed')
    previous = {row['id']: row['after'] for row in a.read(prior)['rows']}
    sources = {source['id']: source for source in a.read(packet / 'sources.json')}
    key = {row['id']: row for row in a.read(custody / 'key.json')}
    refs = key['PE-01']['anchors']
    probes = {q['id']: _probe(packet, q, refs, sources)
              for q in questions if q['id'] in {'PE-01', *held['added_controls']}}
    with TemporaryDirectory(prefix='frus-pe01-score-') as scratch:
        scores = []
        for label, path in [('before', before), ('after', after)]:
            out = Path(scratch) / (label + '.json')
            a.score(packet, custody, path, out)
            scores.append(a.read(out))
    rows = []
    for i, ident in enumerate(order):
        first, second = (receipt['cases'][i]['answer'] for receipt in receipts)
        _require(first == second, f'Native decision or evidence changed for {ident}')
        scored = scores[1]['cases'][i]
        claims = second['claims']
        if ident == 'PE-04-PRESENTATION-CONTROL':
            _require(second['kind'] == 'partial_answer' and not second['answer_supported']
                     and [c['proposition']['relation'] for c in claims] == ['source_named_advice_report'],
                     'The inherited presentation control lost its scoped advice partial')
            decision = 'expected_presentation_withhold'
        elif key[ident]['expected'] == 'withhold':
            _require(second['kind'] == 'abstain' and not claims, f'False support on {ident}')
            decision = 'expected_withhold'
        else:
            _require((second['kind'] == 'abstain' and not claims)
                     or scored['outcome'] == 'complete_with_all_anchors',
                     f'Unsupported or unexpected positive result on {ident}')
            decision = 'complete' if second['answer_supported'] else 'miss'
        if ident in previous:
            original = previous[ident]
            _require(decision == original['strict'] and len(claims) == original['propositions']
                     and scored['diagnostic'] == original['diagnostic'],
                     f'Prior result changed for {ident}')
        row = {'id': ident, 'strict_before': decision, 'strict_after': decision,
               'native_propositions_before': len(first['claims']), 'native_propositions_after': len(claims),
               'discovery_before': scores[0]['cases'][i]['complete_discovery_anchor_coverage'],
               'discovery_after': scored['complete_discovery_anchor_coverage'],
               'diagnostic': scored['diagnostic']}
        if ident in probes:
            row['attribution_probe'] = probes[ident]
        rows.append(row)
    a.save(output, {**held,
        'before': dict(Counter(row['strict_before'] for row in rows)),
        'after': dict(Counter(row['strict_after'] for row in rows)),
        'before_receipt_sha256': a.digest(before.read_bytes()),
        'after_receipt_sha256': a.digest(after.read_bytes()),
        'native_runtime_sha256': receipts[1]['runtime_sha256'],
        'rows': rows, 'false_supported_bridges': 0, 'execution_failures': 0,
        'outside_custodian_scoring': 'NOT_RUN', 'independent_historical_accuracy': 'NOT_RUN',
        'independent_semantic_adjudication': 'NOT_RUN', 'native_oocc': 'NOT_RUN'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ('packet', 'custody', 'freeze', 'rule', 'prior', 'before', 'after', 'output'):
        parser.add_argument('--' + field, required=True, type=Path)
    audit(**vars(parser.parse_args()))
