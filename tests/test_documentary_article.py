"""Article assembly controls; fictional cases do not establish historical accuracy."""
import html
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from mplpb_combined import ledger as L
from mplpb_combined.reader import PROFILES
from mplpb_work import article
from mplpb_answers.__main__ import main
from mplpb_answers.pipeline import answer_query


class DocumentaryArticleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.n = 0

    def add(self, text, **kw):
        self.n += 1
        return L.write(self.root, doc_id='RECORD-'+str(self.n), title='Archive',
                       scope='archive', body_html='<pre>'+html.escape(text)+'</pre>', **kw)

    def assemble(self, *questions, **kw):
        return article.assemble(self.root, {'title': 'Research dossier',
                                'questions': list(questions)}, **kw)

    def test_multisource_sections_do_not_create_cross_source_relationship(self):
        self.add('Nora Finch appointed Ellis Marsh.')
        self.add('Ada Reed wrote the harbour report.')
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        r = self.assemble('Who appointed Ellis Marsh?', 'Who wrote the harbour report?')
        self.assertEqual(r['status'], 'article_snapshot')
        self.assertEqual(r['coverage']['complete_sections'], 2)
        self.assertFalse(r['answer_supported'])
        self.assertFalse(r['historical_truth_independently_verified'])
        self.assertIsNone(r['provenance']['independent_witness_count'])
        self.assertEqual(r['cross_section_relationships'], [])
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        for section in r['sections']:
            self.assertTrue(section['report']['native_answer']['answer_supported'])
            self.assertTrue(section['report']['native_answer']['claims'][0]['citations'])

    def test_competing_accounts_are_displayed_without_selecting_a_winner(self):
        self.add('Nora Finch appointed Ellis Marsh.')
        self.add('Nora Finch did not appoint Ellis Marsh.')
        r = self.assemble('Who appointed Ellis Marsh?')
        a = r['sections'][0]['report']['native_answer']
        self.assertEqual(a['kind'], 'conflict')
        self.assertFalse(a['answer_supported'])
        self.assertEqual({c['proposition']['negative'] for c in a['claims']}, {True, False})
        text = article.render(r)
        self.assertIn('conflict', text)
        self.assertIn('did not appoint', text)
        self.assertIn('Independent witnesses: NOT ESTABLISHED', text)

    def test_three_appearances_keep_one_declared_root_without_truth_claim(self):
        original = self.add('Nora Finch appointed Ellis Marsh.')
        for _ in range(2):
            self.add('Nora Finch appointed Ellis Marsh.', derived_from=[original.id+'@'+original.hash])
        r = self.assemble('Who appointed Ellis Marsh?')
        groups = r['provenance']['shared_declared_roots']
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]['root_id'], original.id)
        self.assertEqual(len(groups[0]['source_ids']), 3)
        self.assertEqual(len(r['provenance']['sources']), 3)
        self.assertFalse(r['provenance']['independence_verified'])
        self.assertFalse(r['historical_truth_independently_verified'])

    def test_absent_lineage_does_not_establish_independence(self):
        for _ in range(3):
            self.add('Nora Finch appointed Ellis Marsh.')
        r = self.assemble('Who appointed Ellis Marsh?')
        self.assertEqual(r['provenance']['shared_declared_roots'], [])
        self.assertIsNone(r['provenance']['independent_witness_count'])
        self.assertFalse(r['provenance']['independence_verified'])

    def test_shared_root_across_different_questions_is_still_visible(self):
        original = self.add('Original account.')
        a = self.add('Nora Finch appointed Ellis Marsh.', derived_from=[original.id+'@'+original.hash])
        b = self.add('Ada Reed wrote the harbour report.', derived_from=[original.id+'@'+original.hash])
        r = self.assemble('Who appointed Ellis Marsh?', 'Who wrote the harbour report?')
        group = r['provenance']['shared_declared_roots'][0]
        self.assertEqual(group['source_ids'], sorted([a.id, b.id]))
        self.assertEqual(group['root_id'], original.id)
        self.assertEqual(r['cross_section_relationships'], [])

    def test_assembly_preserves_native_negation_dates_and_conditions_exactly(self):
        self.add('On June 2, Nora Finch appointed Ellis Marsh.')
        self.add('If approved, Ada Reed sent the harbour report.')
        questions = ['Who appointed Ellis Marsh?', 'Who sent the harbour report?']
        r = self.assemble(*questions)
        for q, section in zip(questions, r['sections']):
            self.assertEqual(section['report']['native_answer'],
                             answer_query(self.root, q, max_chars=12000).contract)

    def test_all_delivery_profiles_keep_restricted_material_gated(self):
        self.add('Nora Finch appointed Ellis Marsh.', external='no')
        for name in PROFILES:
            with self.subTest(profile=name):
                r = self.assemble('Who appointed Ellis Marsh?', profile=name)
                self.assertEqual(r['sections'][0]['report']['native_answer'],
                                 answer_query(self.root, 'Who appointed Ellis Marsh?', PROFILES[name], max_chars=12000).contract)
                if name == 'external':
                    self.assertFalse(r['sections'][0]['report']['native_answer']['answer_supported'])
                    self.assertEqual(r['provenance']['sources'], [])

    def test_eligible_source_budget_stops_before_section_work(self):
        self.add('Nora Finch appointed Ellis Marsh.')
        with patch.object(article, 'MAX_SOURCES_PER_SECTION', 0), patch.object(article, 'reconstruct_report') as work:
            r = self.assemble('Who appointed Ellis Marsh?')
        self.assertEqual(r['status'], 'source_budget_exceeded')
        self.assertEqual(r['sections'], [])
        work.assert_not_called()

    def test_missing_bridge_and_ambiguous_actor_remain_unanswered(self):
        self.add('Nora Finch appointed Ellis Marsh.')
        self.add('She sent the parcel.')
        r = self.assemble('Who appointed Ellis Marsh?', 'Who sent the parcel?',
                          'Did the appointment cause the delivery?')
        self.assertEqual(r['coverage']['complete_sections'], 1)
        self.assertEqual(r['coverage']['unresolved_sections'], 2)
        self.assertEqual(r['cross_section_relationships'], [])
        self.assertTrue(all(not s['report']['native_answer']['answer_supported'] for s in r['sections'][1:]))

    def test_restrictions_preserve_each_original_question(self):
        self.add('Nora Finch appointed Ellis Marsh.', not_for='confidential')
        q = 'Who appointed Ellis Marsh? confidential'
        r = self.assemble(q)
        self.assertEqual(r['sections'][0]['question'], q)
        self.assertFalse(r['sections'][0]['report']['native_answer']['answer_supported'])
        self.assertEqual(r['provenance']['sources'], [])

    def test_source_change_between_sections_discards_entire_assembly(self):
        source = self.add('Nora Finch appointed Ellis Marsh.')
        real = article.reconstruct_report
        calls = []
        def mutate(*args, **kw):
            result = real(*args, **kw)
            calls.append(1)
            if len(calls) == 2:
                L.withdraw(self.root, source.id)
            return result
        with patch.object(article, 'reconstruct_report', side_effect=mutate):
            r = self.assemble('Who appointed Ellis Marsh?', 'Who wrote the harbour report?')
        self.assertEqual(r['status'], 'source_changed')
        self.assertEqual(r['sections'], [])
        self.assertEqual(r['provenance']['sources'], [])
        self.assertNotIn('Nora Finch appointed', article.render(r))

    def test_corrupted_source_and_retired_source_never_reuse_old_support(self):
        source = self.add('Nora Finch appointed Ellis Marsh.')
        self.assertEqual(self.assemble('Who appointed Ellis Marsh?')['coverage']['complete_sections'], 1)
        p = self.root/source.path
        p.write_text(p.read_text().replace('Nora Finch appointed', 'Ada Reed appointed'))
        r = self.assemble('Who appointed Ellis Marsh?')
        self.assertEqual(r['coverage']['complete_sections'], 0)
        self.assertEqual(r['provenance']['sources'], [])

    def test_plan_validation_and_budgets(self):
        for plan in [{'title': 'x', 'questions': []},
                     {'title': 'x', 'questions': ['Who?']*9},
                     {'title': 'x', 'questions': ['Who?'], 'answer': 'yes'},
                     {'title': 'x', 'questions': ['Who?', 'Who?']},
                     {'title': 'x', 'questions': [' ']}]:
            with self.subTest(plan=plan), self.assertRaises(ValueError):
                article.assemble(self.root, plan)
        for kw in [{'max_passages': 0}, {'max_chars': 999}, {'max_chars': 64001}]:
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                self.assemble('Who wrote the harbour report?', **kw)

    def test_deterministic_replay_and_snapshot_notice(self):
        self.add('Nora Finch appointed Ellis Marsh.')
        first = self.assemble('Who appointed Ellis Marsh?')
        self.assertEqual(first, self.assemble('Who appointed Ellis Marsh?'))
        self.assertIn('Snapshot only', article.render(first))

    def test_cli_accepts_bounded_plan(self):
        self.add('Nora Finch appointed Ellis Marsh.')
        p = self.root/'plan.json'
        p.write_text(json.dumps({'title': 'Appointments', 'questions': ['Who appointed Ellis Marsh?']}))
        import io
        out = io.StringIO()
        with patch('sys.stdout', out):
            code = main(['article', str(self.root), '--plan', str(p)])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out.getvalue())['coverage']['complete_sections'], 1)


if __name__ == '__main__':
    unittest.main()
