import json
from pathlib import Path
import tempfile
import unittest
from mplpb_combined import ledger as L
from tools import chat_logic as C
from tools.ledger_ui import App, ROOT


class ChatLogicTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'corpus'
        self.app = App(self.root.parent, topic_base=Path(self.temp.name) / 'topics')

    def tearDown(self):
        self.temp.cleanup()

    def page(self, title, body, external='no', **kw):
        return L.write(self.root, title=title, scope=title, body=body, origin='machine',
                       owner='unknown', source_authorship='unknown', external=external, **kw)

    def test_explicit_inference_with_both_pinned_premises(self):
        a = self.page('Dragon', 'Fact: Dragon | instance_of | reptile')
        b = self.page('Reptile', 'Fact: reptile | subclass_of | animal')
        result = C.relations(self.root, 'internal', 'Dragon', 'animal')
        self.assertEqual(result[0]['status'], 'rule_inference')
        self.assertIn('TYPE-2', result[0]['rules'])
        self.assertEqual({p['hash'] for p in result[0]['premises']}, {a.hash, b.hash})
        self.assertEqual(C.relations(self.root, 'external', 'Dragon', 'animal'), [])

    def test_co_occurrence_and_related_to_are_not_transitive_types(self):
        self.page('Dragon', 'Dragon and budget are mentioned together.\n\nFact: Dragon | related_to | reptile')
        self.page('Reptile', 'Fact: reptile | subclass_of | animal')
        self.assertEqual(C.relations(self.root, 'internal', 'Dragon', 'budget'), [])
        self.assertEqual(C.relations(self.root, 'internal', 'Dragon', 'animal'), [])
        self.assertEqual(C.relations(self.root, 'internal', 'Dragon', 'reptile')[0]['status'], 'source_assertion')

    def test_altered_or_retired_premise_cannot_support_inference(self):
        a = self.page('Dragon', 'Fact: Dragon | instance_of | reptile')
        b = self.page('Reptile', 'Fact: reptile | subclass_of | animal')
        path = self.root / b.path
        path.write_text(path.read_text().replace('subclass_of', 'instance_of'))
        self.assertEqual(C.relations(self.root, 'internal', 'Dragon', 'animal'), [])

    def test_duplicate_assertions_keep_both_source_pins(self):
        a = self.page('One', 'Fact: Dragon | instance_of | reptile')
        b = self.page('Two', 'Fact: Dragon | instance_of | reptile')
        result = C.relations(self.root, 'internal', 'Dragon', 'reptile')
        self.assertEqual({p['hash'] for p in result[0]['premises']}, {a.hash, b.hash})

    def test_subclass_chain_and_cycle_are_bounded(self):
        self.page('A', 'Fact: alpha | subclass_of | beta')
        self.page('B', 'Fact: beta | subclass_of | gamma')
        self.page('C', 'Fact: gamma | subclass_of | alpha')
        result = C.relations(self.root, 'internal', 'alpha', 'gamma')
        self.assertEqual(len(result), 1)
        self.assertIn('TYPE-1', result[0]['rules'])

    def test_followup_requires_context_and_rechecks_hash(self):
        rec = self.page('Dragon', 'A synthetic page about Dragon.')
        self.app.corpora['custom'] = ('Custom', self.root)
        first = self.app.chat(dict(corpus='custom', message='what is it?'))
        self.assertEqual(first['response']['kind'], 'clarify')
        selected = self.app.chat(dict(corpus='custom', message='topic Dragon', session=first['session']))
        follow = self.app.chat(dict(corpus='custom', message='what is it?', session=first['session']))
        self.assertEqual(follow['response']['reader']['question'], 'what is Dragon?')
        self.assertEqual(follow['response']['reasoning'][0]['rule'], 'CTX-1')
        more = self.app.chat(dict(corpus='custom', message='tell me more', session=first['session']))
        self.assertEqual(more['response']['reader']['id'], rec.id)
        path = self.root / rec.path
        path.write_text(path.read_text().replace('synthetic', 'changed'))
        stale = self.app.chat(dict(corpus='custom', message='what is it?', session=first['session']))
        self.assertEqual(stale['response']['kind'], 'clarify')
        self.assertIsNone(stale['response']['context'])

    def test_self_reference_names_declared_creator_with_source(self):
        reply = self.app.chat(dict(corpus='canned', message='who made you?'))['response']
        self.assertEqual(reply['reader']['id'], 'SELF-0004')
        self.assertIn('Mitchell D. McPhetridge', reply['message'])
        self.assertIn('cannot authenticate', reply['message'])
        rec = L.Ledger(ROOT / 'examples/system').by_id['SELF-0004'][0]
        self.assertIn((ROOT / 'docs/SYSTEM_SELF.md').read_text().splitlines()[2], rec.text)

    def test_export_chain_detects_mutation_and_reset_expires_session(self):
        result = self.app.chat(dict(corpus='canned', message='who made you?'))
        sid = result['session']
        exported = self.app.export_chat({'session': sid})
        self.assertTrue(exported['chain_intact'])
        changed = json.loads(json.dumps(exported['turns']))
        changed[0]['payload']['question'] = 'forged'
        self.assertFalse(C.verify_log(changed))
        self.app.reset_chat({'session': sid})
        with self.assertRaises(ValueError):
            self.app.chat(dict(corpus='canned', message='Cat', session=sid))

    def test_profile_change_clears_context_but_retains_session(self):
        result = self.app.chat(dict(corpus='canned', message='who made you?'))
        follow = self.app.chat(dict(corpus='canned', profile='external', message='what is it?', session=result['session']))
        self.assertEqual(follow['session'], result['session'])
        self.assertIsNone(follow['response']['context'])


class ContextualRelationTests(unittest.TestCase):
    def test_natural_bounded_type_question_and_unknown_budget_show_sources(self):
        app = App()
        selected = app.chat(dict(corpus='logic', message='topic Dungeons and Dragons'))
        result = app.chat(dict(corpus='logic', message='is it a game?', session=selected['session']))
        self.assertEqual(result['response']['kind'], 'relations')
        self.assertIn('TYPE-2', result['response']['relations'][0]['rules'])
        unknown = app.chat(dict(corpus='logic', message='relate it -> budget', session=selected['session']))
        self.assertEqual(unknown['response']['kind'], 'unknown_relation')
        self.assertEqual(len(unknown['response']['sources']), 2)
