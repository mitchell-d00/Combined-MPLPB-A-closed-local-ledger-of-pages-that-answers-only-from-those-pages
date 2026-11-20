"""Independently worded controls for source-grounded identity and co-reference."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import write
from mplpb_combined.reader import PROFILES


class ReferenceIdentityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def page(self, ident, body, **options):
        return write(self.root, doc_id=ident, title='Museum catalogue',
                     scope='source events pronouns', body_html=f'<pre>{body}</pre>', **options)

    def event(self, ident, key, registry='Maritime Inventory', extra='', **options):
        return self.page(ident, f'Event Registry: {registry}\nOccurrence ID: COPY-{ident}\nEvent ID: {key}{extra}', **options)

    def ask_event(self, **options):
        return answer_query(self.root, 'Do sources RECORD-A and RECORD-B refer to the same event?', **options).contract

    def ask_pronoun(self, pronoun='I'):
        return answer_query(self.root, f'Who does "{pronoun}" refer to in source RECORD-A?').contract

    def test_two_named_sources_can_support_registry_scoped_agreement(self):
        self.event('RECORD-A', 'D-42')
        self.event('RECORD-B', 'D-42')
        result = self.ask_event()
        self.assertTrue(result['answer_supported'], result['diagnostic'])
        claim = result['claims'][0]
        self.assertTrue(claim['proposition']['same_event'])
        self.assertEqual({c['source_id'] for c in claim['citations']}, {'RECORD-A', 'RECORD-B'})
        self.assertFalse(result['verification']['truth_verified'])

    def test_distinct_requires_explicit_reference_under_one_registry(self):
        self.event('RECORD-A', 'D-42', extra='\nDifferent Event From: COPY-RECORD-B')
        self.event('RECORD-B', 'D-44')
        result = self.ask_event()
        self.assertTrue(result['answer_supported'], result['diagnostic'])
        self.assertFalse(result['claims'][0]['proposition']['same_event'])
        self.event('RECORD-C', 'D-47', extra='\nOccurrence ID: COPY-RECORD-B')
        self.assertFalse(self.ask_event()['answer_supported'])

    def test_distinct_keys_and_equal_text_under_different_registries_withhold(self):
        self.event('RECORD-A', 'D-42')
        self.event('RECORD-B', 'D-44')
        self.assertFalse(self.ask_event()['answer_supported'])

    def test_declared_shared_key_conflicting_with_distinct_reference_withholds(self):
        self.event('RECORD-A', 'D-42', extra='\nDifferent Event From: COPY-RECORD-B')
        self.event('RECORD-B', 'D-42')
        self.assertEqual(self.ask_event()['kind'], 'conflict')

    def test_explicit_binding_and_speech_attribution_preserve_scope(self):
        self.page('RECORD-A', '“I checked the freight tags,” said Amélie Wells.')
        result = self.ask_pronoun()
        self.assertTrue(result['answer_supported'], result['diagnostic'])
        self.assertEqual(result['claims'][0]['proposition']['referent'], 'Amélie Wells')
        self.assertFalse(self.ask_pronoun('she')['answer_supported'])

    def test_imported_speech_uses_verified_capture_text(self):
        from tools.exploration_store import ExplorationStore
        store = ExplorationStore(self.root/'collections')
        corpus = store.create('D4 imported notes')['corpus']
        speech = '“I checked the freight tags,” said Amélie Wells.'
        source = store.add(corpus, 'Freight record', 'https://example.org/freight', speech)
        result = answer_query(store.root(corpus), f'Who does "I" refer to in source {source["id"]}?').contract
        self.assertTrue(result['answer_supported'], result['diagnostic'])
        self.assertEqual(result['claims'][0]['proposition']['referent'], 'Amélie Wells')
        self.assertEqual(result['claims'][0]['citations'][0]['quote'], speech)

    def test_unverified_capture_suffix_cannot_supply_a_proof_boundary(self):
        self.page('RECORD-A', '“I checked the freight tags,” said Amélie Wells.\nSource capture: {}',
                  origin='machine')
        self.assertFalse(self.ask_pronoun()['answer_supported'])

    def test_qualified_named_speaker_is_unresolved(self):
        self.page('RECORD-A', 'Perhaps Amélie Wells said, “I checked the freight tags.”')
        self.assertFalse(self.ask_pronoun()['answer_supported'])

    def test_quoted_markup_cannot_supply_binding(self):
        write(self.root, doc_id='RECORD-A', title='Quoted example', scope='source pronouns',
              body_html='<blockquote><pre>Pronoun "he" refers to Tobin Singh.</pre></blockquote>')
        self.assertFalse(self.ask_pronoun('he')['answer_supported'])

    def test_complete_proof_requires_full_budget_and_delivery(self):
        self.event('RECORD-A', 'D-42')
        self.event('RECORD-B', 'D-42', external='no')
        self.assertFalse(self.ask_event(max_passages=3)['answer_supported'])
        self.assertFalse(self.ask_event(profile=PROFILES['external'])['answer_supported'])

    def test_source_change_discards_verified_binding(self):
        from mplpb_answers import reference_identity
        record = self.page('RECORD-A', 'Pronoun "she" refers to Inez Nordin.')
        original = reference_identity.verify

        def changed(*args, **kwargs):
            selected = original(*args, **kwargs)
            path = self.root / record.path
            path.write_text(path.read_text().replace('Inez Nordin', 'Inez Morris'))
            return selected

        with patch.object(reference_identity, 'verify', side_effect=changed):
            answer = self.ask_pronoun('she')
        self.assertEqual(answer['diagnostic']['code'], 'source_changed')
        self.assertEqual(answer['claims'], [])
