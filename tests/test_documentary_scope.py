"""Ordinary-prose scope controls; these do not measure historical accuracy."""
from pathlib import Path
import tempfile
import unittest
from mplpb_combined.ledger import write
from mplpb_combined.reader import PROFILES
from mplpb_work.prose_evidence import discover
from mplpb_work.source_mapping import reconstruct


class DocumentaryScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def add(self, text, **kwargs):
        return write(self.root, doc_id='SOURCE-'+str(len(list(self.root.glob('*.html')))+1),
                     title='Archive correspondence', scope='archive', body=text, **kwargs)

    def report(self, question='Mira Ruth archive report'):
        result = discover(self.root, question)
        rich = result['information_map']['proposed_reconstruction']
        for item in rich['propositions'] + rich['connections']:
            self.assertFalse(item['answer_supported'])
            self.assertFalse(item['content_truth_verified'])
            self.assertTrue(reconstruct(self.root, question, item)['quote_fidelity'])
        return rich

    def test_shared_negation_and_condition_survive_coordination(self):
        for prefix, expected in [('Mira did not write and ', 'negated_or_scope_limited'),
                                 ('If Mira wrote and ', 'conditional_or_uncertain')]:
            with self.subTest(prefix=prefix):
                self.add(prefix+'sent the archive report.')
                frames=self.report()['propositions']
                target=next(f for f in frames if f['value']['action']=='send' and f['evidence'][0]['quote'].startswith(prefix))
                self.assertEqual(target['value']['modality'], expected)

    def test_new_subject_ends_shared_negation(self):
        self.add('Mira did not write and Ruth sent the archive report.')
        sent=next(f for f in self.report()['propositions'] if f['value']['action']=='send')
        self.assertEqual(sent['value']['actor'], 'Ruth')
        self.assertEqual(sent['value']['modality'], 'source_reports_action')

    def test_witness_report_preserves_embedded_scope(self):
        self.add('Ruth reported that Mira sent the archive report.')
        rich=self.report();sent=next(f for f in rich['propositions'] if f['value']['action']=='send')
        self.assertEqual(sent['value']['assertion_layer'], 'reported_not_independently_verified')
        self.assertEqual(sent['value']['modality'], 'reported_action_not_verified')
        self.assertTrue(any(c['kind']=='embedded_action_candidate' for c in rich['connections']))

    def test_order_does_not_establish_execution(self):
        self.add('Ruth ordered Mira to send the archive report.')
        rich=self.report();sent=next(f for f in rich['propositions'] if f['value']['action']=='send')
        self.assertEqual(sent['value']['modality'], 'future_request_or_intention')
        self.assertFalse(next(c for c in rich['connections'] if c['kind']=='embedded_action_candidate')['action_completed'])

    def test_prepositional_to_is_not_an_infinitive_complement(self):
        self.add('Mira ordered the archive note to Ruth and sent the register.')
        rich=self.report();sent=next(f for f in rich['propositions'] if f['value']['action']=='send')
        self.assertFalse(sent['value']['governing_predicates'])
        self.assertFalse(any(c['kind']=='embedded_action_candidate' for c in rich['connections']))

    def test_requested_action_later_canceled_stays_two_appearances(self):
        self.add('Ruth requested Mira to send the archive report.')
        self.add('Mira canceled sending the archive report.')
        rich=self.report()
        self.assertTrue(any(f['value']['action']=='cancel' for f in rich['propositions']))
        self.assertTrue(all(f['event_identity'] is None for f in rich['propositions']))
        self.assertTrue(all(c.get('identity_verified') is not True for c in rich['connections']))

    def test_passive_agent_is_exact_role_not_resolved_identity(self):
        self.add('The archive report was sent by Mira to Ruth.')
        sent=self.report()['propositions'][0];agent=sent['value']['passive_agent_candidate']
        self.assertEqual(agent['text'], 'Mira');self.assertIsNone(sent['value']['actor'])
        e=sent['evidence'][0]
        self.assertEqual(e['quote'][agent['start']-e['body_start']:agent['end']-e['body_start']], 'Mira')
        self.assertIsNone(sent['event_identity'])

    def test_passive_deadline_is_not_agent(self):
        self.add('The archive report was sent by June 1944.')
        self.assertIsNone(self.report()['propositions'][0]['value']['passive_agent_candidate'])

    def test_passive_honorific_and_initials_keep_complete_agent_span(self):
        self.add('The archive report was sent by Dr. Mira J. Vale to Ruth.')
        sent=self.report()['propositions'][0];agent=sent['value']['passive_agent_candidate']
        self.assertEqual(agent['text'], 'Dr. Mira J. Vale')
        e=sent['evidence'][0]
        self.assertEqual(e['quote'][agent['start']-e['body_start']:agent['end']-e['body_start']], agent['text'])

    def test_copula_in_prior_clause_does_not_erase_active_actor(self):
        self.add('Ruth was certain Mira sent the archive report.')
        sent=self.report()['propositions'][0]
        self.assertEqual(sent['value']['actor'], 'Mira')
        self.assertEqual(sent['value']['voice'], 'active_or_unresolved')

    def test_identical_subjects_do_not_merge_events(self):
        self.add('Subject: Archive report. Mira sent the archive report in June 1944.')
        self.add('Subject: Archive report. Ruth sent the archive report in July 1945.')
        rich=self.report();self.assertFalse(rich['connections'])
        self.assertTrue(all(f['event_identity'] is None for f in rich['propositions']))

    def test_same_event_in_two_records_is_not_automatic_identity(self):
        self.add('Mira sent the archive report to Ruth.')
        self.add('Ruth received the archive report from Mira.')
        rich=self.report();self.assertFalse(rich['connections'])
        self.assertEqual(len(rich['propositions']), 2)

    def test_same_message_id_with_changed_body_does_not_merge(self):
        self.add('Message-ID: archive-1. Mira sent the archive report.')
        self.add('Message-ID: archive-1. Mira did not send the archive report.')
        rich=self.report();self.assertTrue(all(f['event_identity'] is None for f in rich['propositions']))
        self.assertTrue(any(c['kind']=='possible_statement_conflict' for c in rich['connections']))

    def test_missing_intermediate_does_not_create_path(self):
        self.add('Ruth responded to the missing archive letter from Mira.')
        self.add('Mira sent an archive report to Orin.')
        self.assertFalse(self.report()['connections'])

    def test_partial_revision_does_not_rewrite_prior_claims(self):
        self.add('Mira wrote the archive report and sent the register.')
        self.add('Mira revised the archive report. The register remained unchanged.')
        before={p.name:p.read_bytes() for p in self.root.glob('*.html')}
        self.report()
        self.assertEqual(before,{p.name:p.read_bytes() for p in self.root.glob('*.html')})

    def test_conflicting_temporal_roles_do_not_become_event_order(self):
        self.add('Mira wrote the archive report in June 1944.')
        self.add('Mira published the archive report in July 1945.')
        rich=self.report();self.assertFalse(rich['connections'])
        self.assertTrue(all(d['normalized_time'] is None for f in rich['propositions'] for d in f['value']['date_candidates']))

    def test_publication_date_is_not_send_date(self):
        self.add('Published June 5, 1944. Mira sent the archive report.')
        rich=self.report();sent=next(f for f in rich['propositions'] if f['value']['action']=='send')
        self.assertFalse(sent['value']['date_candidates'])

    def test_ambiguous_pronoun_is_unresolved(self):
        self.add('Ruth and Mira wrote the archive report. She sent the register.')
        sent=next(f for f in self.report()['propositions'] if f['value']['action']=='send')
        self.assertEqual(sent['value']['actor'], 'She')
        self.assertIn('pronoun_actor_unresolved', sent['unresolved_actor_or_scope'])

    def test_corruption_after_indexing_invalidates_mapping(self):
        record=self.add('Mira sent the archive report.')
        item=self.report()['propositions'][0]
        path=self.root/record.path;path.write_text(path.read_text().replace('Mira sent','Mira hid'))
        self.assertFalse(reconstruct(self.root,'Mira Ruth archive report',item)['quote_fidelity'])

    def test_restricted_reference_cannot_supply_evidence(self):
        self.add('Mira sent the archive report.', external='no')
        self.add('Ruth wrote a reference to the private archive report.')
        result=discover(self.root,'Mira Ruth archive report',PROFILES['external'])
        self.assertTrue(all('Mira sent' not in c['quote'] for c in result['candidates']))
        self.assertFalse(result['answer_supported'])

    def test_insufficient_budget_is_explicit(self):
        from mplpb_answers.passages import PassageIndex
        from mplpb_work.prose_relations import extract
        from mplpb_work.source_mapping import _state
        self.add('Mira wrote and sent the archive report.')
        index=PassageIndex(self.root,'Mira archive report',PROFILES['internal'])
        rich=extract(index,index.retrieve(['Mira archive report'],12,12000)['passages'],
                     _state(self.root,'Mira archive report',PROFILES['internal']),max_propositions=1)
        self.assertTrue(rich['budget_truncated']);self.assertFalse(rich['answer_supported'])

    def test_confident_causal_wording_remains_source_assertion(self):
        self.add('Mira claimed that the archive report caused Ruth to send the register.')
        rich=self.report();cause=next(f for f in rich['propositions'] if f['value']['action']=='cause')
        self.assertEqual(cause['value']['assertion_layer'],'reported_not_independently_verified')
        self.assertTrue(all(c.get('causality')=='NOT ESTABLISHED' for c in rich['connections']))


if __name__=='__main__':unittest.main()
