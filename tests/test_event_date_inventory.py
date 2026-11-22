"""Finite event/date source assertions, not historical identity or truth."""
import html
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from mplpb_combined import ledger as L
from mplpb_answers.pipeline import answer_query


class EventDateInventoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.question = ('Distinguish the bombardment, surrender, evacuation and telegram dates in the '
                         'North Harbour record, without treating the webpage review date as an event date.')
        self.body = ('Citation: Telegram from Captain Voss announcing withdrawal from North Harbour; June 22, 1882; Archive collection.\n'
                     'On June 17, the coastal batteries opened fire on the harbour.\n'
                     'At 3:15 p.m., June 18, Captain Voss surrendered North Harbour, evacuating the garrison on the following day.\n'
                     'This page was last reviewed on February 4, 2020.')

    def add(self, text=None, **kw):
        return L.write(self.root, doc_id='PAGE-'+str(len(list(self.root.glob('*.html')))+1), title='Archive',
                       scope='archive', body_html='<pre>'+html.escape(text or self.body)+'</pre>', **kw)

    def ask(self, **kw):return answer_query(self.root, self.question, **kw).contract

    def test_natural_date_inventory_preserves_the_original_question(self):
        self.add()
        question = ('What separate dates does the North Harbour record list for opening fire, '
                    'giving up the harbour, leaving it, and the telegram date listed in the catalog?')
        result = answer_query(self.root, question).contract
        self.assertTrue(result['answer_supported'], result['diagnostic'])
        claim = result['claims'][0]
        self.assertEqual(claim['proposition']['verified_question'], question)
        self.assertEqual([link['requested_role'] for link in claim['proposition']['date_links']],
                         ['telegram', 'bombardment', 'surrender', 'evacuation'])
        self.assertFalse(claim['proposition']['date_links'][0]['receipt_verified'])
        self.assertIsNone(claim['proposition']['date_links'][-1]['year'])

    def test_natural_date_inventory_keeps_extra_obligations(self):
        from mplpb_answers.documentary_verify import date_inventory_request
        self.add()
        head = 'What separate dates does the North Harbour record give for '
        for tail in (
            'opening fire, giving up the fort, and leaving it?',
            'opening fire, leaving it, and the telegram date listed in the catalog?',
            'opening fire, giving up the harbour, and actual receipt of the telegram?',
            'opening fire, giving up the harbour, and the telegram date listed in the catalog before revision?',
            'opening fire and bombardment?',
        ):
            with self.subTest(question=head + tail):
                self.assertIsNone(date_inventory_request(head + tail))
                self.assertFalse(answer_query(self.root, head + tail).contract['answer_supported'])

    def test_natural_date_inventory_requires_explicit_role_evidence(self):
        question = ('What separate dates does the North Harbour page give for opening fire, '
                    'giving up the harbour, leaving it, and the telegram date listed in the catalogue?')
        for body in (self.body.replace('opened fire on', 'bombarded'),
                     self.body.replace('fire on the harbour', 'fire on the warehouse'),
                     self.body.replace('surrendered North Harbour', 'surrendered West Harbour'),
                     self.body.replace('surrendered North Harbour', 'reportedly surrendered North Harbour'),
                     self.body.replace(', evacuating the garrison on the following day', '')):
            with self.subTest(body=body), tempfile.TemporaryDirectory() as tmp:
                L.write(tmp, doc_id='SCOPE', title='Archive', scope='archive',
                        body_html='<pre>'+html.escape(body)+'</pre>')
                self.assertFalse(answer_query(tmp, question).contract['answer_supported'])

    def test_each_link_is_checked_without_inheriting_review_or_catalogue_year(self):
        self.add(); r=self.ask()
        self.assertTrue(r['answer_supported'])
        p=r['claims'][0]['proposition']; links={v['requested_role']:v for v in p['date_links']}
        self.assertEqual(links['bombardment']['date_text'],'June 17')
        self.assertEqual(links['surrender']['date_text'],'June 18')
        self.assertEqual(links['surrender']['time_text'],'3:15 p.m.')
        self.assertEqual(links['evacuation']['resolved_month_day'],'June 19')
        self.assertIsNone(links['evacuation']['year'])
        self.assertEqual(links['telegram']['date_role'],'source_catalogue_document_date')
        self.assertEqual(p['review_dates'][0]['date_text'],'February 4, 2020')
        self.assertFalse(p['event_coreference_established']); self.assertFalse(p['causation_established'])
        self.assertFalse(r['verification']['truth_verified'])

    def test_same_clause_calendar_arithmetic_retains_unknown_year(self):
        self.add(self.body.replace('June 18','December 31'))
        r=self.ask(); self.assertTrue(r['answer_supported'])
        v=next(x for x in r['claims'][0]['proposition']['date_links'] if x['requested_role']=='evacuation')
        self.assertEqual(v['resolved_month_day'],'January 1'); self.assertIsNone(v['year'])

    def test_may_is_a_month_and_hedging_remains_hedging(self):
        self.add(self.body.replace('June','May'))
        self.assertTrue(self.ask()['answer_supported'])
        with tempfile.TemporaryDirectory() as tmp:
            L.write(tmp,doc_id='TEST',title='Archive',scope='archive',body_html='<pre>'+html.escape(self.body.replace('opened fire','allegedly opened fire'))+'</pre>')
            self.assertFalse(answer_query(tmp,self.question).contract['answer_supported'])

    def test_qualified_second_owner_is_not_pruned(self):
        self.add()
        self.add('On June 18, Captain Reed reportedly surrendered North Harbour.')
        self.assertFalse(self.ask()['answer_supported'])

    def test_catalogue_line_survives_nearby_navigation_without_accepting_navigation_events(self):
        markup=('<nav>Archive navigation</nav><p>'+self.body.split('\n')[0]+'</p>'+ ''.join('<p>'+x+'</p>' for x in self.body.split('\n')[1:-1])+
                '<footer>'+self.body.split('\n')[-1]+'</footer>')
        L.write(self.root,doc_id='HTML',title='Archive',scope='archive',body_html=markup)
        r=self.ask();self.assertTrue(r['answer_supported'])
        self.assertTrue(all(c['quote'] for c in r['claims'][0]['citations']))

    def test_refutation_unknown_reference_and_quoted_fields_stay_unresolved(self):
        for text in [self.body+'\nThe above account is incorrect.',
                     self.body+'\nCorrection: the date is June 20.',
                     self.body.replace('the following day','a later day'),
                     self.body.replace('Citation:', '> Citation:'),
                     'The plan was as follows.\n'+self.body,
                     self.body.replace('North Harbour','North Harbourish')]:
            with self.subTest(text=text),tempfile.TemporaryDirectory() as tmp:
                L.write(tmp,doc_id='TEST',title='Archive',scope='archive',body_html='<pre>'+html.escape(text)+'</pre>')
                self.assertFalse(answer_query(tmp,self.question).contract['answer_supported'])

    def test_source_change_during_kernel_discards_all_links(self):
        record=self.add()
        from mplpb_answers import documentary_verify as kernel
        original=kernel.date_inventory
        calls=[]
        def changed(index,source):
            r=original(index,source);calls.append(1)
            if len(calls)==2:L.withdraw(self.root,record.id)
            return r
        with patch.object(kernel,'date_inventory',side_effect=changed):
            result=self.ask()
        self.assertFalse(result['answer_supported']);self.assertEqual(result['claims'],[])

    def test_actor_clause_and_near_miss_are_not_bare_occurrences(self):
        for replacement in ['the captain suspected the coastal batteries opened fire',
                            'the coastal batteries almost opened fire',
                            'the proposal: coastal batteries opened fire']:
            text=self.body.replace('the coastal batteries opened fire',replacement)
            with self.subTest(replacement=replacement),tempfile.TemporaryDirectory() as tmp:
                L.write(tmp,doc_id='SCOPE',title='Archive',scope='archive',body_html='<pre>'+html.escape(text)+'</pre>')
                self.assertFalse(answer_query(tmp,self.question).contract['answer_supported'])

    def test_negative_and_adverbial_subjects_are_not_named_actors(self):
        for actor in ['Nobody','No One','Neither','Unfortunately']:
            text=self.body.replace('Captain Voss surrendered',actor+' surrendered')
            with self.subTest(actor=actor),tempfile.TemporaryDirectory() as tmp:
                L.write(tmp,doc_id='SCOPE',title='Archive',scope='archive',body_html='<pre>'+html.escape(text)+'</pre>')
                self.assertFalse(answer_query(tmp,self.question).contract['answer_supported'])

    def test_unknown_leap_year_does_not_guess_relative_date(self):
        self.add(self.body.replace('June 18','February 28'))
        r=self.ask()
        self.assertFalse(r['answer_supported'])
        self.assertTrue(r['claims'])

    def test_plan_negation_report_and_quotes_cannot_be_completed(self):
        for text in [self.body.replace('opened fire','did not open fire'),
                     self.body.replace('opened fire','would open fire'),
                     self.body.replace('On June 17','If approved, on June 17'),
                     self.body.replace('the coastal batteries opened fire','a witness claimed the coastal batteries opened fire'),
                     self.body.replace('opened fire','opened fire only if approved'),
                     'The following is an example.\n'+self.body]:
            with self.subTest(text=text), tempfile.TemporaryDirectory() as tmp:
                L.write(tmp,doc_id='TEST',title='Archive',scope='archive',body_html='<pre>'+html.escape(text)+'</pre>')
                self.assertFalse(answer_query(tmp,self.question).contract['answer_supported'])

    def test_missing_link_is_not_filled_by_similar_record(self):
        self.add(self.body.replace(', evacuating the garrison on the following day',''))
        self.add('On June 19, a vessel evacuated South Harbour.')
        r=self.ask(); self.assertFalse(r['answer_supported'])
        self.assertTrue(any('evacuation' in m for m in r['missing']))

    def test_two_record_owners_and_repeated_events_remain_unresolved(self):
        self.add(); self.add()
        self.assertFalse(self.ask()['answer_supported'])
        with tempfile.TemporaryDirectory() as tmp:
            L.write(tmp,doc_id='ONE',title='Archive',scope='archive',body_html='<pre>'+html.escape(self.body+'\nOn June 20, coastal batteries bombarded North Harbour.')+'</pre>')
            self.assertFalse(answer_query(tmp,self.question).contract['answer_supported'])

    def test_headers_titles_and_review_dates_cannot_fill_event_dates(self):
        self.add('The batteries opened fire on the harbour. This page was last reviewed on June 17, 1882.')
        self.assertFalse(self.ask()['answer_supported'])

    def test_extra_causal_or_execution_obligation_is_not_dropped(self):
        self.add()
        for q in [self.question+' Establish that the telegram caused the surrender.',
                  self.question+' And prove that the telegram was received.']:
            self.assertFalse(answer_query(self.root,q).contract['answer_supported'])

    def test_restrictions_and_withdrawal_remain_effective(self):
        record=self.add(not_for='confidential')
        self.assertFalse(answer_query(self.root,self.question+' confidential').contract['answer_supported'])
        L.withdraw(self.root,record.id); self.assertFalse(self.ask()['answer_supported'])

    def test_budget_and_source_mutation_never_reuse_a_certificate(self):
        self.add(); self.assertTrue(self.ask()['answer_supported'])
        from mplpb_answers import documentary_verify as kernel
        with patch.object(kernel,'DATE_LOCATOR_CHARS',30):
            self.assertFalse(self.ask()['answer_supported'])
        p=next(self.root.glob('*.html'));p.write_text(p.read_text().replace('June 18','June 21'))
        self.assertFalse(self.ask()['answer_supported'])


if __name__=='__main__':unittest.main()
