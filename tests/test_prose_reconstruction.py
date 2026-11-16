"""Bounded interpretation controls. Historical performance is scored separately."""
import json
from pathlib import Path
import tempfile
import unittest
from mplpb_combined.ledger import write,withdraw
from mplpb_combined.reader import PROFILES
from mplpb_work.prose_evidence import discover
from mplpb_work.source_mapping import reconstruct
from mplpb_answers.prose_retrieval import retrieve
from mplpb_answers.passages import PassageIndex

ROOT=Path(__file__).resolve().parents[1]


class ProseReconstructionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)

    def report(self,q):return discover(self.root,q)['information_map']['proposed_reconstruction']

    def test_original_correspondence_request_is_not_delivery(self):
        # Exact preserved historical text, not new Event-ID/Related/answer fields.
        case=json.loads((ROOT/'evaluation/unprepared-originals/2026-11-16/reference-draft.json').read_text())['cases'][1]
        quote=case['citations'][0]['quote']
        write(self.root,doc_id='LETTER-1',title='Imported excerpt',scope='correspondence',body=quote)
        report=self.report('Who arranged for Wallace to receive the book?')
        actions=report['propositions'];sends=[x for x in actions if x['value']['action']=='send']
        self.assertTrue(sends);s=sends[0]
        self.assertEqual(s['value']['actor'],'Murray')
        self.assertEqual(s['value']['modality'],'future_request_or_intention')
        self.assertIn('WALLACE',s['value']['object_bindings'][0]['resolved_candidate'])
        self.assertIn('possible',s['qualification_cues']);self.assertFalse(s['answer_supported'])
        self.assertTrue(any(x['kind']=='reported_request_candidate' for x in report['connections']))
        for item in actions+report['connections']:
            r=reconstruct(self.root,'Who arranged for Wallace to receive the book?',item)
            self.assertTrue(r['quote_fidelity']);self.assertFalse(r['semantic_relationship_verified'])

    def test_conditional_failure_and_discretion_not_actual_events(self):
        write(self.root,doc_id='SOURCE-1',title='Fictional control',scope='archive',body='Mira wrote a note. If the operation should fail, Mira would retract the report. The Secretary may in his discretion, grant leases for ten years.')
        frames=self.report('Mira operation report Secretary leases')['propositions']
        retract=next(x for x in frames if x['value']['action']=='retract')
        grant=next(x for x in frames if x['value']['action']=='grant')
        self.assertEqual(retract['value']['modality'],'conditional_or_uncertain')
        self.assertEqual(grant['value']['modality'],'permission_or_possibility')
        self.assertFalse(retract['answer_supported']);self.assertFalse(grant['content_truth_verified'])

    def test_opposing_literal_statements_are_candidates_with_both_quotes(self):
        write(self.root,doc_id='LETTER-1',title='Fictional',scope='archive',body='Mira retracted all earlier archive claims.')
        write(self.root,doc_id='LETTER-2',title='Fictional',scope='archive',body='Mira did not retract all earlier archive claims.')
        r=self.report('Mira archive claims retracted')
        conflicts=[x for x in r['connections'] if x['kind']=='possible_statement_conflict']
        self.assertTrue(conflicts);self.assertEqual(len(conflicts[0]['evidence']),2)
        self.assertTrue(any('not retract all' in e['quote'] for e in conflicts[0]['evidence']))
        self.assertFalse(conflicts[0]['answer_supported'])

    def test_shared_vocabulary_does_not_create_event_or_causal_edge(self):
        write(self.root,doc_id='LETTER-1',title='Fictional',scope='archive',body='Mira sent an archive note.')
        write(self.root,doc_id='LETTER-2',title='Fictional',scope='archive',body='Orin received a garden register.')
        r=self.report('Mira Orin archive garden')
        self.assertTrue(r['propositions']);self.assertFalse(r['connections'])
        self.assertTrue(all(x['event_identity'] is None for x in r['propositions']))

    def test_heading_routing_does_not_make_heading_answer_evidence(self):
        write(self.root,doc_id='SOURCE-1',title='Imported',scope='archive',body_html='<h2>Observatory archive ledger</h2><p>The sample conclusion is tentative, not confirmed.</p>')
        report=discover(self.root,'Observatory archive sample conclusion')
        self.assertTrue(report['candidates'])
        self.assertTrue(all('Observatory' not in c['quote'] for c in report['candidates']))
        self.assertFalse(report['retrieval_discovery']['routing_metadata_is_answer_evidence'])

    def test_restrictions_and_withdrawal_still_govern_facets(self):
        r=write(self.root,doc_id='SOURCE-1',title='Fictional',scope='archive',external='no',body='Mira retracted the archive conclusion.')
        self.assertFalse(discover(self.root,'Mira archive conclusion',PROFILES['external'])['candidates'])
        withdraw(self.root,r.id)
        self.assertFalse(discover(self.root,'Mira archive conclusion')['candidates'])

    def test_nominal_actions_and_navigation_are_not_historical_events(self):
        write(self.root,doc_id='SOURCE-1',title='Fictional',scope='archive',body_html='<nav><p>Apply for a Grant</p></nav><p>The Order of the Day described a well-received article and a written declaration about the Union cause.</p><footer><p>Mira wrote a website notice.</p></footer>')
        report=self.report('archive Order article declaration')
        self.assertFalse(report['propositions'])
        self.assertFalse(report['connections'])

    def test_passive_repeal_and_scope_remain_literal_candidates(self):
        write(self.root,doc_id='SOURCE-1',title='Quoted public constitutional text',scope='archive',body_html='<p>The eighteenth article of amendment to the Constitution of the United States is hereby repealed.</p><p>The transportation or importation into any State, Territory, or possession of the United States for delivery or use therein of intoxicating liquors, in violation of the laws thereof, is hereby prohibited.</p>')
        report=self.report('constitutional provision repealed transportation laws')
        repeal=next(x for x in report['propositions'] if x['value']['action']=='repeal')
        self.assertIsNone(repeal['value']['actor'])
        self.assertIn('eighteenth article',repeal['value']['affected_subject_text'])
        self.assertTrue(any('in violation' in x['value']['literal_qualifiers'] for x in report['qualifications']))
        self.assertFalse(repeal['answer_supported']);self.assertFalse(repeal['content_truth_verified'])

    def test_same_paragraph_actor_continuity_is_only_a_proposal(self):
        write(self.root,doc_id='SOURCE-1',title='Fictional',scope='archive',body_html='<p>Mira surveyed the archive. She wrote an archive note.</p><p>She sent an archive report.</p>')
        report=self.report('Mira archive note report')
        links=[x for x in report['connections'] if x['kind']=='possible_pronoun_antecedent']
        self.assertEqual(len(links),1);self.assertEqual(links[0]['value']['actor_candidate'],'Mira')
        self.assertFalse(links[0]['identity_verified']);self.assertFalse(links[0]['answer_supported'])


if __name__=='__main__':unittest.main()
