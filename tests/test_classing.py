"""Classing assistant: dump -> review file -> reviewed, validated ledger."""
import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import Ledger
from mplpb_work import classing

DEMO = Path(__file__).parent / 'fixtures' / 'classing_demo'


def reviewed(review):
    """The decisions a person made in the README walkthrough."""
    r = copy.deepcopy(review)
    d = {x['draft_id']: x for x in r['drafts']}
    x = {y['decision_id']: y for y in r['decisions']}
    by_path = {v['source']['path']: k for k, v in d.items()}
    # Explicit fictional reviewer choices; auto-accept does not approve serving decisions.
    for draft in d.values(): draft['decision'] = 'accept'
    d[by_path['diary.md']]['decision'] = 'reject'
    for p in ('ship-9a.txt', 'ship-9b.txt'):
        d[by_path[p]]['decision'] = 'accept'
    for y in x.values():
        if y['kind'] == 'duplicate_id':
            y['choice'] = 'second_supersedes_first'
        elif y['kind'] == 'partial_correction':
            y.update(choice='field_correction', corrects_field='cargo')
        elif y['kind'] == 'declared_status':
            y['choice'] = 'withdraw_after_write'
        else:
            y['choice'] = 'ignore'
    d[by_path['ship-8.txt']]['reviewer_fields'].append(
        {'label': 'Cargo', 'value': 'thirty-eight barrels', 'quote': 'the cargo count changes only to thirty-eight barrels'})
    d[by_path['ship-7.txt']]['ratify'] = True
    return r


class Workspace(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.dump = self.root / 'dump'
        shutil.copytree(DEMO, self.dump)
        self.review = classing.propose(self.dump, auto_accept_clean=True)

    def tearDown(self):
        self.tmp.cleanup()

    def drafts(self, review=None):
        return {d['source']['path']: d for d in (review or self.review)['drafts']}


class Propose(Workspace):
    def test_every_header_line_is_a_literal_field(self):
        ship7 = self.drafts()['ship-7.txt']
        fields = {f['label']: f['value'] for f in ship7['fields']}
        self.assertEqual(fields['Cargo'], 'forty barrels of flour')  # not a sorter-known header
        text = (self.dump / 'ship-7.txt').read_text()
        for f in ship7['fields']:
            self.assertEqual(text[f['char_span'][0]:f['char_span'][1]], f['value'])

    def test_prose_with_colon_is_not_a_field(self):
        self.assertEqual(self.drafts()['diary.md']['fields'], [])

    def test_numbered_designation_becomes_id_and_keeps_date(self):
        letter = self.drafts()['letter-41.txt']
        self.assertEqual(letter['page']['doc_id'], 'LETTER-NO-41')
        self.assertIn('Date', [f['label'] for f in letter['fields']])
        self.assertEqual(letter['body'], 'Twelve bales shipped to Troy.')

    def test_auto_accept_only_clean_drafts(self):
        d = self.drafts()
        self.assertEqual(d['ship-7.txt']['decision'], 'accept')
        self.assertEqual(d['diary.md']['decision'], 'pending')  # no declared id
        self.assertEqual(d['ship-9a.txt']['decision'], 'pending')  # duplicate id
        self.assertIn('duplicate_declared_id', d['ship-9b.txt']['blockers'])

    def test_decisions_are_proposed_not_applied(self):
        kinds = {x['kind'] for x in self.review['decisions']}
        self.assertTrue({'duplicate_id', 'partial_correction', 'correction', 'declared_status', 'reference_review'} <= kinds)
        self.assertTrue(all(x['choice'] is None for x in self.review['decisions']))
        partial = next(x for x in self.review['decisions'] if x['kind'] == 'partial_correction')
        self.assertEqual(partial['recommended'], 'field_correction')

    def test_reported_speech_is_a_review_not_a_correction(self):
        ref = [x for x in self.review['decisions'] if x['kind'] == 'reference_review']
        self.assertEqual(ref[0]['reason'], 'qualified_or_quoted_reference')

    def test_drafts_are_machine_origin(self):
        self.assertTrue(all(d['page']['origin'] == 'machine' for d in self.review['drafts']))


class Build(Workspace):
    def build(self, review, **kw):
        return classing.build(review, self.dump, self.root / 'ledger', **kw)

    def test_unanswered_blocking_decision_refuses(self):
        r = reviewed(self.review)
        next(x for x in r['decisions'] if x['kind'] == 'duplicate_id')['choice'] = None
        with self.assertRaisesRegex(classing.ClassingError, 'blocking duplicate_id'):
            self.build(r, ratify_by='Tester')
        self.assertFalse((self.root / 'ledger').exists())

    def test_changed_dump_refuses(self):
        r = reviewed(self.review)
        (self.dump / 'ship-7.txt').write_text((self.dump / 'ship-7.txt').read_text().replace('forty', 'fifty'))
        with self.assertRaisesRegex(classing.ClassingError, 'dump changed'):
            self.build(r, ratify_by='Tester')

    def test_reviewer_field_must_be_literal(self):
        r = reviewed(self.review)
        self.drafts(r)['ship-8.txt']['reviewer_fields'][0]['value'] = 'thirty-nine barrels'
        with self.assertRaisesRegex(classing.ClassingError, 'not a literal quote'):
            self.build(r, ratify_by='Tester')

    def test_ratify_needs_a_named_person(self):
        with self.assertRaisesRegex(classing.ClassingError, 'ratify-by'):
            self.build(reviewed(self.review))

    def test_existing_ledger_needs_append(self):
        (self.root / 'ledger').mkdir()
        with self.assertRaisesRegex(classing.ClassingError, 'append'):
            self.build(reviewed(self.review), ratify_by='Tester')

    def test_field_correction_needs_a_field(self):
        r = reviewed(self.review)
        next(x for x in r['decisions'] if x['kind'] == 'partial_correction')['corrects_field'] = None
        with self.assertRaisesRegex(classing.ClassingError, 'corrects_field'):
            self.build(r, ratify_by='Tester')

    def test_successful_build_is_valid_and_strict_readable(self):
        receipt = self.build(reviewed(self.review), ratify_by='Tester')
        ledger = self.root / 'ledger'
        self.assertEqual(receipt['validation']['errors'], [])
        self.assertEqual(Ledger(ledger, serving=False).findings(), [])
        depth = {p['doc_id']: p['depth'] for p in receipt['pages_written']}
        self.assertEqual(depth['SHIP-7'], 0)  # ratified at write, id kept
        self.assertEqual(depth['SHIP-8'], 1)
        self.assertEqual(receipt['withdrawn'], ['RATES-1849'])
        ask = lambda q: answer_query(ledger, q).contract
        self.assertEqual(ask('What is the from for record SHIP-7?')['text'], 'From: Boston flour office')
        self.assertEqual(ask('What is the cargo for record SHIP-8?')['text'], 'Cargo: thirty-eight barrels')
        self.assertEqual(ask('What is the date for record LETTER-NO-41?')['text'], 'Date: 1 June 1851')
        self.assertNotEqual(ask('What is the subject for record RATES-1849?')['kind'], 'supported_answer')

    def test_external_profile_needs_ratification_and_declared_authorship(self):
        from mplpb_combined.reader import PROFILES
        r = reviewed(self.review)
        self.drafts(r)['ship-7.txt']['page']['source_authorship'] = 'declared-human'  # reviewer's declaration
        self.drafts(r)['letter-41.txt']['page']['source_authorship'] = 'declared-human'  # declared, not ratified
        self.build(r, ratify_by='Tester')
        ask = lambda q: answer_query(self.root / 'ledger', q, PROFILES['external']).contract['kind']
        self.assertEqual(ask('What is the from for record SHIP-7?'), 'supported_answer')
        self.assertNotEqual(ask('What is the date for record LETTER-NO-41?'), 'supported_answer')  # depth 1
        self.assertNotEqual(ask('What is the cargo for record SHIP-8?'), 'supported_answer')  # authorship unknown

    def test_append_rehearses_then_writes(self):
        first = copy.deepcopy(reviewed(self.review))
        for d in first['drafts']:
            if d['source']['path'] != 'ship-7.txt':
                d['decision'] = 'reject'
        for x in first['decisions']:
            x['choice'] = 'ignore' if 'ignore' in x['options'] else x['choice']
            if x['kind'] == 'duplicate_id':
                x['choice'] = 'keep_both'
        self.build(first, ratify_by='Tester')
        second = classing.propose(self.dump, ledger=self.root / 'ledger', auto_accept_clean=True)
        ship7 = self.drafts(second)['ship-7.txt']
        self.assertIn('id_taken_in_target_ledger', ship7['blockers'])
        ship7['decision'] = 'reject'
        for d in second['drafts']:
            if d['source']['path'] == 'letter-41.txt':
                d['decision'] = 'accept'
            elif d['decision'] != 'accept' or d['source']['path'] != 'letter-41.txt':
                d['decision'] = 'reject'
        for x in second['decisions']:
            x['choice'] = 'ignore' if 'ignore' in x['options'] else 'keep_both'
        receipt = classing.build(second, self.dump, self.root / 'ledger', append=True)
        self.assertEqual([p['doc_id'] for p in receipt['pages_written']], ['LETTER-NO-41'])
        self.assertEqual(receipt['validation']['errors'], [])


if __name__ == '__main__':
    unittest.main()
