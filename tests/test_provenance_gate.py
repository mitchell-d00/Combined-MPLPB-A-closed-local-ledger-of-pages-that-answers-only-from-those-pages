import json
import shutil
import subprocess
import sys
from pathlib import Path

from mplpb_combined import ledger as L, reader as R
from mplpb_combined.provenance_gate import gather, render
from mplpb_combined.record import upsert_meta, parse_page, render_page
from tests.support import LedgerTest


class TestProvenanceGate(LedgerTest):
    def setUp(self):
        super().setUp()
        self.game = self.page('Dungeons & Dragons', '1974 dungeons dragons publication',
                              body='TSR published Dungeons & Dragons in 1974.',
                              owner='Game author', directory='games')
        self.budget = self.page('General budget', 'budget planning',
                                body='A general budget lists income and expense categories.',
                                owner='Budget author', directory='budgets')
        self.question = '1974 dungeons and dragons budget'

    def ids(self, result):
        return [s['id'] for s in result.sources]

    def reseal(self, rec, field, value):
        path = self.root / rec.path
        changed = parse_page(upsert_meta(path.read_text(), field, value), rec.path)
        path.write_text(render_page(changed.fields, changed.title, changed.body_html))

    def test_game_and_budget_are_separate_sources(self):
        result = gather(self.root, self.question)
        self.assertEqual(set(self.ids(result)), {self.game.id, self.budget.id})
        self.assertEqual(result.lexical_coverage, 'complete')
        game, budget = ({s['id']: s for s in result.sources}[r.id]
                        for r in (self.game, self.budget))
        self.assertNotIn('budget', game['matched_terms'])
        self.assertEqual(budget['matched_terms'], ['budget'])
        self.assertEqual(budget['owner'], 'Budget author')
        self.assertEqual(game['text'], self.game.text)
        self.assertEqual(budget['text'], self.budget.text)

    def test_budget_on_two_pages_returns_both_without_ambiguity(self):
        both = self.page('Publishing example', 'dungeons dragons budget',
                         body='A fictional Dungeons & Dragons budget exercise, not historical data.')
        result = gather(self.root, self.question)
        self.assertEqual(result.kind, 'source_bundle')
        self.assertEqual(set(result.term_sources['budget']), {self.budget.id, both.id})
        self.assertEqual(len(result.sources), 3)

    def test_complete_word_coverage_never_asserts_a_relationship(self):
        data = gather(self.root, self.question).to_dict()
        self.assertEqual(data['relationship_status'], 'not_established_by_retrieval')
        self.assertFalse(data['answer_synthesized'])
        self.assertFalse(data['authorship_authenticated'])
        self.assertIn('not that a page answers', data['notice'])

    def test_missing_budget_is_visible_even_with_a_subject_source(self):
        L.withdraw(self.root, self.budget.id, when='2026-01-02T00:00Z')
        result = gather(self.root, self.question)
        self.assertEqual(self.ids(result), [self.game.id])
        self.assertEqual(result.unmatched_terms, ['budget'])
        self.assertEqual(result.lexical_coverage, 'partial')

    def test_scope_does_not_hide_a_prose_budget_source(self):
        another = self.page('Account notes', 'account notes', body='The budget has three categories.')
        result = gather(self.root, self.question)
        row = next(s for s in result.sources if s['id'] == another.id)
        self.assertEqual(row['scope_terms'], [])
        self.assertEqual(row['prose_only_terms'], ['budget'])
        self.assertIn(another.id, result.term_sources['budget'])

    def test_scope_only_suppresses_prose_sources(self):
        another = self.page('Account notes', 'account notes', body='A budget note.')
        profile = R.Profile('scope', 1, False)
        self.assertNotIn(another.id, self.ids(gather(self.root, 'budget', profile)))

    def test_each_source_carries_full_provenance(self):
        row = gather(self.root, self.question).sources[0]
        for key in ('id', 'path', 'hash', 'status', 'origin', 'origin_depth', 'owner',
                    'updated', 'derived_from', 'supersedes', 'ancestry', 'verification', 'location'):
            self.assertIn(key, row)
        self.assertEqual(row['location'], 'local')
        self.assertTrue(row['hash'].startswith('sha256:'))
        self.assertTrue(row['verification']['hash_intact'])

    def test_less_specific_sources_are_not_dropped(self):
        partial = self.page('Dungeons notes', 'dungeons', body='Notes.')
        self.assertIn(partial.id, self.ids(gather(self.root, self.question)))

    def test_altered_page_is_excluded(self):
        self.edit(self.budget, 'income', 'invented money')
        result = gather(self.root, self.question)
        self.assertNotIn(self.budget.id, self.ids(result))
        self.assertTrue(any('altered' in e['reason'] for e in result.excluded))
        self.assertNotIn('invented money', json.dumps(result.to_dict()))

    def test_duplicate_identity_excludes_both_copies(self):
        shutil.copyfile(self.root / self.budget.path, self.root / 'copy.html')
        result = gather(self.root, 'budget')
        self.assertEqual(result.kind, 'not_in_corpus')
        self.assertEqual(len([e for e in result.excluded if e['id'] == self.budget.id]), 2)

    def test_missing_explicit_origin_is_not_assumed_human(self):
        self.reseal(self.budget, 'origin', '')
        result = gather(self.root, 'budget')
        self.assertEqual(result.kind, 'not_in_corpus')
        self.assertTrue(any('origin' in e['reason'] for e in result.excluded))

    def test_invalid_declared_depth_is_excluded(self):
        self.reseal(self.budget, 'origin-depth', 'bananas')
        self.assertEqual(gather(self.root, 'budget').kind, 'not_in_corpus')

    def test_valid_derived_source_keeps_pinned_ancestry(self):
        derived = L.derive(self.root, [self.budget.id], title='Budget excerpt',
                           scope='budget excerpt', body='A general budget lists income.',
                           owner='Excerpt author', when='2026-01-01T00:00Z')
        result = gather(self.root, 'budget')
        row = next(s for s in result.sources if s['id'] == derived.id)
        self.assertEqual((row['origin'], row['origin_depth']), ('machine', 1))
        self.assertEqual(row['ancestry'][0]['id'], self.budget.id)
        self.assertEqual(row['ancestry'][0]['hash'], self.budget.hash)

    def test_damaged_parent_blocks_derived_evidence(self):
        derived = L.derive(self.root, [self.budget.id], title='Budget excerpt',
                           scope='budget excerpt', body='A budget excerpt.', when='2026-01-01T00:00Z')
        self.edit(self.budget, 'income', 'altered income')
        result = gather(self.root, 'budget')
        self.assertNotIn(derived.id, self.ids(result))
        self.assertNotIn(self.budget.id, self.ids(result))

    def test_superseded_dependency_requires_recheck(self):
        derived = L.derive(self.root, [self.budget.id], title='Budget excerpt',
                           scope='budget excerpt', body='A budget excerpt.', when='2026-01-01T00:00Z')
        revised = L.revise(self.root, self.budget.id, body='New budget categories.', when='2026-01-02T00:00Z')
        result = gather(self.root, 'budget')
        self.assertNotIn(derived.id, self.ids(result))
        self.assertIn(revised.id, self.ids(result))
        self.assertTrue(any('requires recheck' in e['reason'] for e in result.excluded))

    def test_shared_ancestry_is_not_independent_corroboration(self):
        derived = L.derive(self.root, [self.budget.id], title='Budget excerpt',
                           scope='budget excerpt', body='A budget excerpt.', when='2026-01-01T00:00Z')
        result = gather(self.root, 'budget')
        shared = next(x for x in result.shared_lineage if x['root_id'] == self.budget.id)
        self.assertEqual(set(shared['source_ids']), {derived.id, self.budget.id})
        self.assertIn('not independent', shared['notice'])

    def test_policy_hash_exposes_changed_settings_even_with_same_name(self):
        a = gather(self.root, 'budget', R.Profile('same', 1, True))
        b = gather(self.root, 'budget', R.Profile('same', 0, False))
        self.assertNotEqual(a.policy['settings_hash'], b.policy['settings_hash'])

    def test_snapshot_changes_when_a_page_is_withdrawn(self):
        a = gather(self.root, 'budget')
        L.withdraw(self.root, self.budget.id, when='2026-01-02T00:00Z')
        b = gather(self.root, 'budget')
        self.assertNotEqual(a.corpus_snapshot, b.corpus_snapshot)

    def test_unpinned_lineage_is_excluded(self):
        derived = L.derive(self.root, [self.budget.id], title='Budget excerpt',
                           scope='budget excerpt', body='A budget excerpt.', when='2026-01-01T00:00Z')
        self.reseal(derived, 'derived-from', self.budget.id)
        self.assertNotIn(derived.id, self.ids(gather(self.root, 'budget')))

    def test_external_profile_withholds_machine_sources(self):
        machine = self.page('Budget draft', 'budget draft', origin='machine')
        result = gather(self.root, 'budget', R.PROFILES['external'])
        self.assertNotIn(machine.id, self.ids(result))
        self.assertIn(self.budget.id, self.ids(result))
        self.assertTrue(any('depth' in e['reason'] for e in result.excluded))

    def test_not_for_still_blocks_a_page(self):
        restricted = self.page('Budget draft', 'budget draft', not_for='auction')
        result = gather(self.root, 'budget auction')
        self.assertNotIn(restricted.id, self.ids(result))
        self.assertTrue(any('not-for' in e['reason'] for e in result.excluded))

    def test_ignore_not_for_is_an_explicit_profile_option(self):
        restricted = self.page('Budget draft', 'budget draft', not_for='auction')
        result = gather(self.root, 'budget auction', R.Profile('compare', 1, True, False))
        self.assertIn(restricted.id, self.ids(result))

    def test_empty_absent_and_stopword_queries_refuse(self):
        for query in ('', 'what is it', 'lunar forecast'):
            self.assertEqual(gather(self.root, query).kind, 'not_in_corpus')

    def test_negative_query_preserves_original_and_flags_the_premise(self):
        query = 'why was Dungeons and Dragons not published in 1974'
        result = gather(self.root, query)
        self.assertEqual(result.question, query)
        self.assertTrue(result.query_flags)
        self.assertFalse(result.to_dict()['answer_synthesized'])

    def test_pointer_is_not_presented_as_source_evidence(self):
        pointer = self.page('Budget link', 'budget', kind='pointer', points_to='elsewhere')
        self.assertNotIn(pointer.id, self.ids(gather(self.root, 'budget')))

    def test_external_html_symlink_is_rejected_before_crawling(self):
        outside = Path(self.tmp) / 'outside.html'
        outside.write_text('not part of the corpus')
        (self.root / 'escape.html').symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'escapes'):
            gather(self.root, 'budget')

    def test_legacy_single_owner_reader_is_unchanged(self):
        self.assertEqual(R.answer(self.root, self.question).record.id, self.game.id)
        self.assertEqual(len(gather(self.root, self.question).sources), 2)

    def test_cli_json_returns_a_source_bundle(self):
        proc = subprocess.run([sys.executable, '-m', 'mplpb_combined', 'gate', str(self.root),
                               self.question, '--json'], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)['kind'], 'source_bundle')

    def test_render_attaches_source_identity_to_each_text(self):
        text = render(gather(self.root, self.question))
        for rec in (self.game, self.budget):
            self.assertIn(rec.text, text)
            self.assertIn(rec.id, text)
            self.assertIn(rec.hash, text)
        self.assertIn('not that a page answers', text)
