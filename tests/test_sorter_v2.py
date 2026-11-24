"""Rules v2 sorter: one test per rule plus the v1 safety behaviors it must keep.

Every case builds its own small corpus. Assertions name the review edge kind,
the reason and the target, because those are what downstream review tools use.
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from mplpb_work import sorter as v1
from mplpb_work import sorter_v2 as v2

FIXTURES = Path(__file__).parent / 'fixtures' / 'sorter'

ORIGINAL = 'Message-ID: SHIP-7\nSubject: Barrel shipment\nDate sent: May 12, 1850\n\nForty barrels of flour left Boston for the Albany depot.\n'


def corpus(files):
    tmp = tempfile.TemporaryDirectory()
    for name, text in files.items():
        Path(tmp.name, name).write_text(text, encoding='utf-8')
    return tmp


def run(files, mode='compare'):
    with corpus(files) as root:
        return v2.sort_directory(root, mode)


def reviews(graph, kind=None):
    paths = {n['id']: n['span']['path'] for n in graph['nodes']}
    out = []
    for e in graph['edges']:
        if not e.get('comparison_only') or e['kind'] == 'repeated_phrase_review':
            continue
        if kind and e['kind'] != kind:
            continue
        out.append(dict(e, from_path=paths.get(e['from']), to_path=paths.get(e['to'])))
    return out


def nodes(graph, kind):
    return [n for n in graph['nodes'] if n['kind'] == kind]


def links(graph):
    return {(e['kind'], e['from_path'], e['to_path']) for e in reviews(graph)
            if e['kind'] in {'possible_correction', 'possible_partial_correction', 'explicit_reference_candidate'}}


class TerminalPunctuation(unittest.TestCase):  # R1
    def test_sentence_final_targets_link(self):
        for tail in ('.', ':', ';', ')', '!', ' today.'):
            with self.subTest(tail=tail):
                g = run({'a.txt': ORIGINAL, 'z.txt': f'Message-ID: SHIP-30\nSubject: x\n\nCorrection to SHIP-7{tail}\n'})
                self.assertIn(('possible_correction', 'z.txt', 'a.txt'), links(g))

    def test_internal_punctuation_is_kept(self):
        g = run({'a.txt': 'Message-ID: REC-1850.7\n\nBody.\n', 'b.txt': 'Message-ID: REC-9\n\nSee REC-1850.7.\n'})
        self.assertIn('REC-1850.7', {n['value'] for n in nodes(g, 'identifier')})
        self.assertIn(('explicit_reference_candidate', 'b.txt', 'a.txt'), links(g))


class NumberedDesignations(unittest.TestCase):  # R2
    def test_header_designation_declares_and_body_reference_links(self):
        g = run({'41.txt': 'Letter No. 41\nDate: 1 June 1851\n\nTwelve bales shipped.\n',
                 '42.txt': 'Letter No. 42\nDate: 3 June 1851\n\nRef. Letter No. 41 is hereby corrected: ten bales, not twelve.\n'})
        declared = {n['value'] for n in nodes(g, 'header_identifier') if n['primary_identity_eligible']}
        self.assertEqual(declared, {'LETTER-NO-41', 'LETTER-NO-42'})
        self.assertIn(('possible_correction', '42.txt', '41.txt'), links(g))

    def test_designation_in_body_is_not_a_declaration(self):
        g = run({'a.txt': 'Subject: notes\n\nLetter No. 5\n\nunrelated\n'})
        self.assertFalse([n for n in nodes(g, 'header_identifier') if n['value'] == 'LETTER-NO-5'])

    def test_number_without_document_type_is_not_an_identifier(self):
        g = run({'a.txt': 'Subject: x\n\nThis is No. 1 priority.\n'})
        self.assertFalse([n for n in nodes(g, 'identifier') if 'NO-' in n['value']])


class RecognizedTargets(unittest.TestCase):  # R3
    def test_plain_word_is_not_a_target(self):
        g = run({'a.txt': 'Subject: x\n\nSee you at the depot.\n'})
        self.assertFalse(nodes(g, 'reference_mention'))

    def test_v1_invented_target_word(self):
        with corpus({'t.txt': 'Letter No. 42\n\nRef. Letter No. 41 is hereby corrected.\n'}) as root:
            old = v1.sort_directory(root, 'compare')
        self.assertIn('Letter', {n.get('value') for n in nodes(old, 'reference_mention')})
        g = run({'t.txt': 'Letter No. 42\n\nRef. Letter No. 41 is hereby corrected.\n'})
        self.assertNotIn('Letter', {n.get('value') for n in nodes(g, 'reference_mention')})

    def test_correction_with_unrecognized_target_is_reviewed_not_dropped(self):
        g = run({'a.txt': 'Message-ID: N-1\n\nCorrection to the ledger total.\n'})
        reasons = {e['reason'] for e in reviews(g, 'unresolved_reference_review')}
        self.assertIn('unrecognized_target_form', reasons)


class PassiveDirection(unittest.TestCase):  # R4
    def test_self_agent_links(self):
        for text in ('SHIP-7 is superseded by this notice.', 'SHIP-7 is hereby amended.', 'SHIP-7 has been corrected by the present letter.'):
            with self.subTest(text=text):
                g = run({'a.txt': ORIGINAL, 'r.txt': f'Message-ID: SHIP-22\n\n{text}\n'})
                self.assertIn(('possible_correction', 'r.txt', 'a.txt'), links(g))

    def test_third_party_and_unstated_agents_do_not_link(self):
        cases = {'SHIP-7 was superseded by SHIP-9.': 'third_party_relation_reported',
                 'SHIP-7 was corrected.': 'passive_agent_unstated'}
        for text, reason in cases.items():
            with self.subTest(text=text):
                g = run({'a.txt': ORIGINAL, 'r.txt': f'Message-ID: SHIP-23\n\n{text}\n'})
                self.assertFalse(links(g) & {('possible_correction', 'r.txt', 'a.txt')})
                self.assertIn(reason, {e['reason'] for e in reviews(g, 'unresolved_reference_review')})


class ClauseScope(unittest.TestCase):  # R5
    def test_later_clause_modal_does_not_block(self):
        g = run({'a.txt': ORIGINAL, 'c.txt': 'Message-ID: SHIP-8\n\nCorrection to SHIP-7: the barrels will be recounted.\n'})
        self.assertIn(('possible_correction', 'c.txt', 'a.txt'), links(g))
        statement = [n for n in nodes(g, 'statement') if n['span']['path'] == 'c.txt'][-1]
        self.assertEqual(statement['scope'], 'conditional_or_uncertain')  # v1 statement scope kept

    def test_same_clause_modal_still_blocks(self):
        g = run({'a.txt': ORIGINAL, 'f.txt': 'Message-ID: SHIP-11\n\nIf the clerk agrees, a correction to SHIP-7 would move the depot.\n'})
        self.assertFalse(links(g))

    def test_quote_elsewhere_in_statement_does_not_block(self):
        g = run({'a.txt': ORIGINAL, 'c.txt': 'Message-ID: SHIP-8\n\nCorrection to SHIP-7. The depot is now called "Troy Yard".\n'})
        self.assertIn(('possible_correction', 'c.txt', 'a.txt'), links(g))

    def test_quoted_correction_still_blocks(self):
        g = run({'a.txt': ORIGINAL, 'e.txt': 'Message-ID: SHIP-10\n\nHe wrote "this corrects SHIP-7" in pencil.\n'})
        self.assertFalse(links(g))

    def test_month_may_is_not_a_modal(self):
        g = run({'a.txt': ORIGINAL, 'c.txt': 'Message-ID: SHIP-8\n\nCorrection to SHIP-7 made on 14 May 1850.\n'})
        self.assertIn(('possible_correction', 'c.txt', 'a.txt'), links(g))


class Negation(unittest.TestCase):  # R6
    def test_governing_negation_blocks(self):
        for text in ('This does not correct SHIP-7.', 'This is not a correction to SHIP-7.', 'This never amends SHIP-7.'):
            with self.subTest(text=text):
                g = run({'a.txt': ORIGINAL, 'd.txt': f'Message-ID: SHIP-9\n\n{text}\n'})
                self.assertFalse(links(g))

    def test_negation_about_something_else_does_not_block(self):
        g = run({'a.txt': ORIGINAL, 'c.txt': 'Message-ID: SHIP-8\n\nCorrection to SHIP-7: thirty-eight barrels, not forty.\n'})
        self.assertIn(('possible_correction', 'c.txt', 'a.txt'), links(g))

    def test_double_negation_is_unresolved_not_affirmed(self):
        g = run({'a.txt': ORIGINAL, 's.txt': 'Message-ID: SHIP-23\n\nIt is not untrue that this note corrects SHIP-7.\n'})
        self.assertFalse(links(g))
        mention = [n for n in nodes(g, 'reference_mention') if n['span']['path'] == 's.txt'][0]
        self.assertEqual(mention['local_scope'], 'negation_scope_unresolved')


class ReportedSpeech(unittest.TestCase):  # R7
    def test_unquoted_reported_correction_does_not_link(self):
        # The ID is not sentence-final, so v1's R1 bug does not mask the scope bug.
        text = 'Message-ID: SHIP-10\n\nThe porter said this note corrects SHIP-7 in full.\n'
        g = run({'a.txt': ORIGINAL, 'e.txt': text})
        self.assertFalse(links(g))
        self.assertIn('qualified_or_quoted_reference', {e['reason'] for e in reviews(g, 'unresolved_reference_review')})
        with corpus({'a.txt': ORIGINAL, 'e.txt': text}) as root:
            old = v1.sort_directory(root, 'compare')
        self.assertTrue([e for e in old['edges'] if e['kind'] == 'possible_correction'], 'v1 linked reported speech')


class DescriptiveReferences(unittest.TestCase):  # R8
    def test_candidates_listed_none_selected(self):
        g = run({'a.txt': ORIGINAL,
                 'b.txt': 'Message-ID: WOOL-1\n\nTwenty bales of wool left Salem.\n',
                 'p.txt': 'Message-ID: SHIP-20\n\nThe earlier Boston flour note had the count wrong; it should read thirty-eight barrels.\n'})
        review = reviews(g, 'descriptive_reference_review')
        self.assertEqual(len(review), 1)
        self.assertEqual([c['path'] for c in review[0]['candidates']], ['a.txt'])
        self.assertFalse(review[0]['target_established'])
        self.assertFalse(links(g))

    def test_disconnected_statements_get_no_candidates(self):
        # Negative control from the PR #52 workspace report: common words alone
        # must not propose a relationship.
        g = run({'a.txt': 'Message-ID: A-1\n\nThe weather in Boston was cold and the river froze early.\n',
                 'b.txt': 'Message-ID: B-1\n\nThe Boston bank opened late because the clerk was ill.\n',
                 'p.txt': 'Message-ID: P-1\n\nThe earlier note about Boston was wrong; the clerk should read the order again.\n'})
        review = reviews(g, 'descriptive_reference_review')
        self.assertEqual(len(review), 1)
        self.assertEqual(review[0]['candidates'], [])


class KeptV1Safety(unittest.TestCase):
    def test_same_id_changed_body_flagged_not_merged(self):
        g = run({'a.txt': ORIGINAL, 'b.txt': ORIGINAL.replace('Forty', 'Thirty-eight')})
        cluster = reviews(g, 'candidate_identity_cluster')[0]
        self.assertTrue(cluster['changed_bodies'])
        self.assertFalse(cluster['historical_identity_established'])

    def test_ambiguous_target_is_not_resolved(self):
        g = run({'a.txt': ORIGINAL, 'b.txt': ORIGINAL.replace('Forty', 'Ten'),
                 'c.txt': 'Message-ID: SHIP-8\n\nCorrection to SHIP-7.\n'})
        self.assertIn('ambiguous_identifier', {e['reason'] for e in reviews(g, 'unresolved_reference_review')})
        self.assertFalse(links(g))

    def test_missing_target(self):
        g = run({'g.txt': 'Message-ID: SHIP-12\n\nSee SHIP-99 for the claim.\n'})
        self.assertIn('missing_or_outside_budget', {e['reason'] for e in reviews(g, 'unresolved_reference_review')})

    def test_code_fence_and_forwarded_text_stay_qualified(self):
        g = run({'a.txt': ORIGINAL, 'i.md': '# Notes\n\n```\nCorrection to SHIP-7 sets the count to five.\n```\n'})
        self.assertFalse(links(g))

    def test_every_assessment_is_unsupported(self):
        g = run({'a.txt': ORIGINAL, 'c.txt': 'Message-ID: SHIP-8\n\nCorrection to SHIP-7.\n'})
        for item in g['nodes'] + g['edges'] + g['sources']:
            self.assertIs(item['assessment']['answer_supported'], False)

    def test_original_fixture_reviews_match_v1(self):
        keep = lambda g: sorted((e['kind'], e.get('reason'), e.get('target_key'), e['from'] if e['kind'] != 'possible_partial_correction' else '')
                                for e in g['edges'] if e.get('comparison_only') and e['kind'] != 'repeated_phrase_review')
        old = v1.sort_directory(FIXTURES, 'compare')
        new = v2.sort_directory(FIXTURES, 'compare')
        self.assertEqual(keep(old), keep(new))


class ReplayAndCompatibility(unittest.TestCase):
    def test_deterministic_and_verifiable(self):
        with corpus({'a.txt': ORIGINAL, 'c.txt': 'Message-ID: SHIP-8\n\nCorrection to SHIP-7.\n'}) as root:
            first = v2.sort_directory(root, 'compare')
            self.assertEqual(first, v2.sort_directory(root, 'compare'))
            self.assertEqual(v2.verify_graph(first, root)['status'], 'source_fidelity_replayed')
            Path(root, 'c.txt').write_text('Message-ID: SHIP-8\n\nCorrection to SHIP-6.\n', encoding='utf-8')
            with self.assertRaises(v2.SortError):
                v2.verify_graph(first, root)

    def test_v1_graph_is_rejected_by_v2_verify_and_vice_versa(self):
        old = v1.sort_directory(FIXTURES, 'compare')
        new = v2.sort_directory(FIXTURES, 'compare')
        with self.assertRaises(v2.SortError):
            v2.verify_graph(old, FIXTURES)
        with self.assertRaises(v1.SortError):
            v1.verify_graph(new, FIXTURES)

    def test_v1_graph_accepted_as_prior_snapshot(self):
        old = v1.sort_directory(FIXTURES, 'compare')
        new = v2.sort_directory(FIXTURES, 'compare', prior_text=json.dumps(old))
        self.assertEqual(new['prior_assessment']['raw_sha256'][:7], 'sha256:')

    def test_raw_mode_edges_are_prefix_of_compare(self):
        raw = v2.sort_directory(FIXTURES, 'not-compared')
        cmp = v2.sort_directory(FIXTURES, 'compare')
        self.assertEqual(raw['nodes'], cmp['nodes'])
        self.assertEqual(cmp['edges'][:len(raw['edges'])], raw['edges'])

    def test_v1_engine_bytes_are_unchanged(self):
        # Pin of mplpb_work/sorter.py at bbf6690 (PR #52 merge). Changing it
        # invalidates every stored v1 graph and frozen sorter study.
        digest = hashlib.sha256((Path(v1.__file__)).read_bytes()).hexdigest()
        self.assertTrue(digest.startswith('0e8eb56604ba34f3'), digest)


class AdditionalScopeAndBudgetTests(unittest.TestCase):
    def test_trailing_reporting_clause_is_not_an_authored_correction(self):
        graph=run({'a.txt':ORIGINAL,'b.txt':'Message-ID: SHIP-8\n\nThis note corrects SHIP-7, the clerk said.'})
        self.assertFalse(reviews(graph,'possible_correction'))
        self.assertTrue(any(e.get('local_scope')=='reported_speech_scope' for e in reviews(graph,'unresolved_reference_review')))

    def test_phrase_witness_cap_keeps_distinct_record_occurrences(self):
        phrase = 'Patient workers folded clean linen.'
        source = 'Message-ID: MILL-23\n\n' + '\n\n'.join([phrase] * 8)
        files = {'a.txt': source, 'z.txt': 'Message-ID: MILL-24\n\n' + phrase}
        with corpus(files) as root:
            raw = v2.sort_directory(root)
            compared = v2.sort_directory(root, 'compare')
        nodes = [node for node in compared['nodes']
                 if node['kind'] == 'phrase_key' and node['value'] == 'patient workers folded clean']
        self.assertEqual(len(nodes), 8)
        self.assertEqual(len({node['occurrence'] for node in nodes}), 2)
        self.assertEqual(raw['nodes'], compared['nodes'])
        node_ids = {node['id'] for node in nodes}
        self.assertTrue(any(edge['kind'] == 'repeated_phrase_review' and edge['comparison_only']
                            and set(edge['evidence_nodes']) <= node_ids for edge in compared['edges']))

    def test_descriptive_pair_search_obeys_comparison_budget(self):
        with corpus({'a.txt':ORIGINAL,'b.txt':'Message-ID: SHIP-8\n\nThe earlier Boston flour note was wrong.'}) as root:
            raw=v2.sort_directory(root,'not-compared',limits={'comparisons':1})
            graph=v2.sort_directory(root,'compare',limits={'comparisons':1})
        self.assertEqual(raw['nodes'],graph['nodes'])
        self.assertIn('comparison_budget',graph['limits_or_exclusions'])
        self.assertFalse(graph['complete'])


if __name__ == '__main__':
    unittest.main()
