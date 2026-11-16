"""Checked source assertions/composition, distinct from candidate interpretation."""
import html
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from mplpb_answers.pipeline import answer_query
from mplpb_answers.passages import PassageIndex
from mplpb_answers import documentary,documentary_verify
from mplpb_combined.ledger import write
from mplpb_combined.reader import PROFILES


class DocumentaryAssertionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.n=0

    def add(self,body,**kwargs):
        self.n+=1
        return write(self.root,doc_id='SOURCE-'+str(self.n),title='Archive',scope='archive',
                     body_html='<pre>'+html.escape(body)+'</pre>',**kwargs)

    def answer(self,q,**kwargs):return answer_query(self.root,q,**kwargs).contract

    def letter(self,body=None):
        return self.add('RUTH STONE TO MIRA VALE. Boston, November 13th, 1859.\nMy dear Sir,\n'+(body or 'I have told Orin to send you by post (if possible) a copy of my report, and I hope that you will receive it tomorrow.'))

    def test_complete_source_assertion_has_checked_roles_not_historical_truth(self):
        self.add('Ruth Stone appointed Mira Vale.')
        r=self.answer('Who appointed Mira Vale?')
        self.assertEqual(r['kind'],'supported_answer');self.assertTrue(r['answer_supported'])
        p=r['claims'][0];self.assertTrue(p['source_support_established'])
        self.assertEqual(p['proposition']['actor_text'],'Ruth Stone');self.assertEqual(p['proposition']['object_text'],'Mira Vale')
        self.assertFalse(p['historical_truth_independently_verified']);self.assertIsNone(p['proposition']['event_identity'])
        self.assertIn('Source assertion',r['text'])

    def test_two_independent_obligations_compose_with_two_witnesses(self):
        self.add('Ruth Stone appointed Mira Vale.');self.add('Orin Hale appointed Lena Grey.')
        r=self.answer('Who appointed Mira Vale, and who appointed Lena Grey?')
        self.assertTrue(r['answer_supported']);self.assertEqual(len(r['claims']),2)
        self.assertEqual(len(r['sources']),2);self.assertFalse(r['missing'])
        self.assertTrue(all(p['proposition']['event_identity'] is None for p in r['claims']))

    def test_missing_second_obligation_does_not_get_filled_by_first(self):
        self.add('Ruth Stone appointed Mira Vale.')
        r=self.answer('Who appointed Mira Vale, and who appointed Lena Grey?')
        self.assertEqual(r['kind'],'partial_answer');self.assertFalse(r['answer_supported'])
        self.assertEqual(len(r['claims']),1);self.assertTrue(any('Lena Grey' in m for m in r['missing']))
        self.assertIn('Source assertion',answer_query(self.root,'Who appointed Mira Vale, and who appointed Lena Grey?').legacy()['text'])

    def test_causal_part_does_not_inherit_support(self):
        self.add('Ruth Stone appointed Mira Vale.')
        r=self.answer('Who appointed Mira Vale, and why did this cause the war?')
        self.assertEqual(r['kind'],'partial_answer');self.assertFalse(r['answer_supported'])
        self.assertTrue(any('cause the war' in m for m in r['missing']))

    def test_reported_instruction_has_header_bindings_and_preserved_conditions(self):
        self.letter();r=self.answer('Who arranged for Mira Vale to receive the report, and which dated letter records the arrangement?')
        self.assertEqual(r['kind'],'partial_answer');self.assertFalse(r['answer_supported'])
        p=r['claims'][0]['proposition'];self.assertEqual(p['writer_text'],'RUTH STONE')
        self.assertEqual(p['requested_recipient_text'],'MIRA VALE');self.assertEqual(p['intermediary_text'],'Orin')
        self.assertEqual(p['condition_text'],'if possible');self.assertEqual(p['heading_date_text'],'November 13th, 1859')
        self.assertEqual(p['date_role'],'letter_heading_date_role_unresolved')
        self.assertFalse(p['dispatch_verified']);self.assertFalse(p['receipt_verified'])
        self.assertEqual(len(r['claims'][0]['citations']),2);self.assertIn('if possible',r['text'])
        self.assertTrue(any('dispatch' in m and 'receipt' in m for m in r['missing']))

    def test_conditional_negated_or_quoted_opening_is_not_certified(self):
        for body in ['If approved, I have told Orin to send you a copy of my report.',
                     'I have not told Orin to send you a copy of my report.',
                     '"I have told Orin to send you a copy of my report."']:
            with self.subTest(body=body):
                with tempfile.TemporaryDirectory() as tmp:
                    root=Path(tmp);write(root,doc_id='SOURCE-1',title='Archive',scope='archive',body_html='<pre>RUTH STONE TO MIRA VALE. Boston, November 13th, 1859.\nMy dear Sir,\n'+html.escape(body)+'</pre>')
                    r=answer_query(root,'Who arranged for Mira Vale to receive the report?').contract
                    self.assertFalse(r['answer_supported']);self.assertFalse(r['claims'])

    def test_heading_cannot_bind_a_later_letter_opening(self):
        self.add('RUTH STONE TO MIRA VALE. Boston, November 13th, 1859.\nMy dear Sir,\nThe archive is closed.\nORIN HALE TO LENA GREY. Boston, November 14th, 1859.\nMy dear Sir,\nI have told Tomas to send you a copy of my report.')
        r=self.answer('Who arranged for Lena Grey to receive the report?')
        self.assertEqual(r['claims'][0]['proposition']['writer_text'],'ORIN HALE')
        self.assertEqual(r['claims'][0]['proposition']['requested_recipient_text'],'LENA GREY')

    def test_source_contrary_statement_is_not_pruned_by_retrieval(self):
        self.add('Ruth Stone appointed Mira Vale.');self.add('Ruth Stone did not appoint Mira Vale.')
        r=self.answer('Who appointed Mira Vale?')
        self.assertEqual(r['kind'],'conflict');self.assertFalse(r['answer_supported'])
        self.assertEqual({c['proposition']['negative'] for c in r['claims']},{False,True})
        self.assertTrue(any('did not appoint' in c['citations'][0]['quote'] for c in r['claims']))

    def test_distinct_temporal_scopes_require_clarification_not_event_merging(self):
        self.add('On June 1, Ruth Stone appointed Mira Vale.');self.add('On June 2, Orin Hale appointed Mira Vale.')
        r=self.answer('Who appointed Mira Vale?')
        self.assertEqual(r['kind'],'clarify');self.assertFalse(r['answer_supported'])
        self.assertTrue(all(c['proposition']['event_identity'] is None for c in r['claims']))

    def test_multiple_appearances_do_not_establish_event_identity_or_independence(self):
        self.add('Ruth Stone appointed Mira Vale.');self.add('Ruth Stone appointed Mira Vale.')
        r=self.answer('Who appointed Mira Vale?')
        self.assertEqual(len(r['claims']),2);self.assertEqual(len(r['sources']),2)
        self.assertTrue(all(c['proposition']['event_identity'] is None for c in r['claims']))
        self.assertFalse(r['verification']['independence_verified'])

    def test_unresolved_role_reference_does_not_complete_question(self):
        self.add('Ruth Stone appointed Mira Vale to that position.')
        r=self.answer('Who appointed Mira Vale to command the archive?')
        self.assertEqual(r['kind'],'partial_answer');self.assertFalse(r['answer_supported'])
        self.assertTrue(r['claims'][0]['proposition']['unresolved_reference'])
        self.assertIn('that position',r['text'])

    def test_conditional_and_reported_actions_are_not_unconditional_proofs(self):
        for body in ['If approved, Ruth Stone appointed Mira Vale.',
                     'Ruth Stone never appointed Mira Vale.',
                     'Not Ruth Stone appointed Mira Vale.',
                     'Orin claimed that Ruth Stone appointed Mira Vale.',
                     'This is a fictional example. Ruth Stone appointed Mira Vale.',
                     'Ruth Stone appointed Mira Vale and sent the report.',
                     'She appointed Mira Vale.']:
            with self.subTest(body=body):
                with tempfile.TemporaryDirectory() as tmp:
                    root=Path(tmp);write(root,doc_id='SOURCE-1',title='Archive',scope='archive',body=body)
                    r=answer_query(root,'Who appointed Mira Vale?').contract
                    self.assertFalse(r['answer_supported']);self.assertFalse(r['claims'])

    def test_unparsed_passive_denial_prevents_complete_acceptance(self):
        self.add('Ruth Stone appointed Mira Vale.');self.add('Mira Vale was not appointed by Ruth Stone.')
        r=self.answer('Who appointed Mira Vale?')
        self.assertEqual(r['kind'],'partial_answer');self.assertFalse(r['answer_supported'])
        self.assertTrue(r['documentary_support']['alternative_evidence'])

    def test_original_question_exclusions_survive_decomposition(self):
        self.add('Ruth Stone appointed Mira Vale.',not_for='garden')
        r=self.answer('Who appointed Mira Vale, and why was the garden closed?')
        self.assertFalse(r['answer_supported']);self.assertFalse(r['claims'])

    def test_restricted_source_reference_does_not_supply_a_proof(self):
        self.add('Ruth Stone appointed Mira Vale.',external='no')
        self.add('The archive references SOURCE-1 about Mira Vale.')
        r=self.answer('Who appointed Mira Vale?',profile=PROFILES['external'])
        self.assertFalse(r['answer_supported']);self.assertFalse(r['claims'])

    def test_source_change_after_kernel_wipes_assertions_and_metadata(self):
        record=self.add('Ruth Stone appointed Mira Vale.');check=documentary_verify.check
        def changed(*a,**kw):
            result=check(*a,**kw);p=self.root/record.path;p.write_text(p.read_text().replace('Ruth Stone','Orin Hale'));return result
        with patch('mplpb_answers.documentary.kernel.check',side_effect=changed):r=self.answer('Who appointed Mira Vale?')
        self.assertEqual(r['diagnostic']['code'],'source_changed');self.assertFalse(r['claims']);self.assertFalse(r['sources'])
        self.assertEqual(r['documentary_support']['source_support_claims'],0)
        self.assertNotIn('Ruth Stone appointed Mira Vale',str(r))

    def test_kernel_rejects_trimmed_condition_even_with_exact_quote(self):
        self.add('If approved, Ruth Stone appointed Mira Vale.')
        index=PassageIndex(self.root,'Who appointed Mira Vale?',PROFILES['internal']);r=index.records[0]
        from mplpb_answers.body_text import body_text
        body=body_text(r.body_html);a=body.index('Ruth Stone')
        proposal={'kind':'action_statement','source_id':r.id,'path':r.path,'hash':r.hash_actual,'start':a,'end':len(body),'quote':body[a:]}
        self.assertFalse(documentary_verify.check(index,[proposal])['proofs'])

    def test_extractor_cannot_award_source_support(self):
        self.add('Ruth Stone appointed Mira Vale.')
        index=PassageIndex(self.root,'Who appointed Mira Vale?',PROFILES['internal'])
        proposals=documentary.propose(index,index.retrieve(['Who appointed Mira Vale?'],12,8000)['passages'])
        self.assertTrue(proposals);self.assertTrue(all('source_support_established' not in p for p in proposals))
        proposals[0]['actor_text']='Invented';proposals[0]['answer_supported']=True
        proofs=documentary_verify.check(index,proposals)['proofs']
        self.assertEqual(proofs[0]['proposition']['actor_text'],'Ruth Stone')

    def test_display_budget_cannot_hide_second_obligation(self):
        self.add('Ruth Stone appointed Mira Vale.');self.add('Orin Hale appointed Lena Grey.')
        r=self.answer('Who appointed Mira Vale, and who appointed Lena Grey?',max_passages=1)
        self.assertEqual(r['kind'],'partial_answer');self.assertFalse(r['answer_supported'])
        self.assertLessEqual(sum(len(c['citations']) for c in r['claims']),1)

    def test_verification_is_read_only(self):
        self.letter();before={p.name:p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.answer('Who arranged for Mira Vale to receive the report?')
        self.assertEqual(before,{p.name:p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_quotation_markup_and_qualified_heading_do_not_lose_scope(self):
        for markup in ['<blockquote><p>Ruth Stone appointed Mira Vale.</p></blockquote>',
                       '<h2>Hypothetical example</h2><p>Ruth Stone appointed Mira Vale.</p>']:
            with self.subTest(markup=markup),tempfile.TemporaryDirectory() as t:
                write(t,doc_id='SOURCE-1',title='Archive',scope='archive',body_html=markup)
                self.assertFalse(answer_query(t,'Who appointed Mira Vale?').contract['answer_supported'])

    def test_incomplete_contrary_scan_cannot_create_complete_answer(self):
        self.add('Ruth Stone appointed Mira Vale.');self.add('Archive background. '*200)
        check=documentary_verify.check
        with patch('mplpb_answers.documentary.kernel.check',side_effect=lambda i,p:check(i,p,max_scan_chars=1000)):
            r=self.answer('Who appointed Mira Vale?')
        self.assertEqual(r['kind'],'partial_answer');self.assertFalse(r['answer_supported'])
        self.assertFalse(r['documentary_support']['contrary_evidence_scan_complete'])

    def test_unresolved_pronoun_in_possible_contrary_evidence_is_not_ignored(self):
        self.add('Ruth Stone appointed Mira Vale.');self.add('Mira Vale was discussed. She was never appointed.')
        r=self.answer('Who appointed Mira Vale?')
        self.assertEqual(r['kind'],'partial_answer');self.assertFalse(r['answer_supported'])
        self.assertTrue(r['documentary_support']['alternative_evidence'])

    def test_issued_order_does_not_prove_execution(self):
        self.add('Ruth Stone ordered Mira Vale to send the archive report. Mira Vale did not send the archive report.')
        r=self.answer('Who ordered Mira Vale to send the archive report, and who sent the archive report?')
        self.assertEqual(r['kind'],'partial_answer');self.assertFalse(r['answer_supported'])
        self.assertTrue(any(c['proposition']['action']=='order' for c in r['claims']))
        self.assertFalse(any(c['proposition']['action']=='send' and not c['proposition']['negative'] for c in r['claims']))
        self.assertIn('does not establish its execution',r['text'])

    def test_request_cancellation_is_alternative_context_not_an_applied_correction(self):
        self.letter();self.add('Orin canceled sending the report.')
        r=self.answer('Who arranged for Mira Vale to receive the report?')
        self.assertEqual(r['kind'],'partial_answer');self.assertFalse(r['answer_supported'])
        self.assertTrue(r['documentary_support']['alternative_evidence'])
        self.assertFalse(r['documentary_support']['contrary_evidence_scan_complete'])

    def test_unresolved_authored_correction_prevents_complete_answer(self):
        self.add('Ruth Stone appointed Mira Vale.');self.add('The previous statement was retracted.')
        r=self.answer('Who appointed Mira Vale?')
        self.assertEqual(r['kind'],'partial_answer');self.assertFalse(r['answer_supported'])
        self.assertTrue(r['documentary_support']['alternative_evidence'])

    def test_general_correspondence_forms_do_not_require_a_book_or_told_template(self):
        for text,verb,obj in [
            ('I asked Dr. Orin Hale to deliver you the sealed packet.','deliver','the sealed packet'),
            ('I have instructed Orin to forward my manuscript to you.','forward','my manuscript'),
            ('I requested Orin to post you a letter by courier.','post','a letter'),
            ('I ordered Orin to send you the register (if practicable).','send','the register')]:
            with self.subTest(text=text),tempfile.TemporaryDirectory() as t:
                write(t,doc_id='SOURCE-1',title='Archive',scope='archive',body_html='<pre>RUTH STONE TO MIRA VALE. Boston, October 4th, 1888.\nDear Madam,\n'+text+'</pre>')
                r=answer_query(t,'Who arranged for Mira Vale to receive the packet or manuscript or letter or register?').contract
                self.assertEqual(r['kind'],'partial_answer');self.assertFalse(r['answer_supported'])
                p=r['claims'][0]['proposition'];self.assertEqual(p['requested_action'],verb);self.assertEqual(p['object_text'],obj)
                self.assertFalse(p['dispatch_verified']);self.assertFalse(p['receipt_verified'])

    def test_plural_possessive_is_not_an_open_quote(self):
        self.add("Veterans' records are retained. Ruth Stone appointed Mira Vale.")
        self.assertTrue(self.answer('Who appointed Mira Vale?')['answer_supported'])

    def test_multi_sentence_quoted_action_is_not_an_author_assertion(self):
        self.add("Orin said 'The archive was open. Ruth Stone appointed Mira Vale.'")
        r=self.answer('Who appointed Mira Vale?')
        self.assertFalse(r['answer_supported']);self.assertFalse(r['claims'])

    def test_temporal_adverb_and_planning_context_are_not_guessed_actors_or_events(self):
        for body in ['Yesterday Ruth Stone appointed Mira Vale.',
                     'Apparently Ruth Stone appointed Mira Vale.',
                     'The plan was as follows. Ruth Stone appointed Mira Vale.']:
            with self.subTest(body=body),tempfile.TemporaryDirectory() as t:
                write(t,doc_id='SOURCE-1',title='Archive',scope='archive',body=body)
                self.assertFalse(answer_query(t,'Who appointed Mira Vale?').contract['answer_supported'])

    def test_following_correction_note_cannot_be_silently_removed(self):
        self.letter('I have told Orin to send you a copy of my report. (N.B. This was not a real instruction.)')
        r=self.answer('Who arranged for Mira Vale to receive the report?')
        self.assertFalse(r['answer_supported']);self.assertFalse(r['claims'])


if __name__=='__main__':unittest.main()
