"""Finite reconstruction contracts; fictional controls are not human accuracy."""
import html
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from mplpb_combined.ledger import write
from mplpb_combined.reader import PROFILES
from mplpb_answers.pipeline import answer_query
from mplpb_answers.passages import PassageIndex
from mplpb_answers.body_text import body_text, _cached_projection
from mplpb_answers import documentary, documentary_verify as kernel, source_units


class ReconstructionEngineTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.n=0

    def add(self,text,markup=False,**kw):
        self.n+=1
        return write(self.root,doc_id='RECORD-'+str(self.n),title='No answer in title',scope='historical archive',
                     body_html=text if markup else '<pre>'+html.escape(text)+'</pre>',**kw)

    def ask(self,q,**kw):return answer_query(self.root,q,**kw).contract

    def test_explicit_cause_and_resource_are_checked_separately(self):
        self.add('The expedition was delayed because of heavy rain.')
        self.add('The rescue ship provided food for the safe return to shore.')
        r=self.ask('Why was the expedition delayed, and what resource supported return to shore?')
        self.assertEqual(r['kind'],'partial_answer');self.assertFalse(r['answer_supported'])
        self.assertEqual({c['proposition']['relation'] for c in r['claims']},{'source_causal_assertion','source_resource_assertion'})
        self.assertTrue(all(c['source_support_established'] and not c['historical_truth_independently_verified'] for c in r['claims']))
        self.assertTrue(r['missing'])

    def test_conditional_reported_and_planned_causes_cannot_be_certified(self):
        for text in ['If approved, the expedition was delayed because of rain.',
                     'Orin said that the expedition was delayed because of rain.',
                     'The expedition would be delayed because of rain.',
                     'The expedition was perhaps delayed because of rain.',
                     'The expedition was delayed. Heavy rain fell later.']:
            self.assertIsNone(kernel.relationship_assertion(text))

    def test_negated_cause_retains_negation(self):
        value=kernel.relationship_assertion('The expedition was not delayed because of rain.')
        self.assertTrue(value['negative']);self.assertEqual(value['cause_text'],'rain')

    def test_cause_is_not_inferred_from_temporal_sequence(self):
        self.add('The arrival occurred before the departure.')
        r=self.ask('Why was the expedition delayed?')
        self.assertFalse(r['answer_supported']);self.assertFalse(r['claims'])
        value=kernel.relationship_assertion('The arrival occurred before the departure.')
        self.assertFalse(value['causality_established']);self.assertIsNone(value['normalized_event_time'])

    def test_temporal_roles_are_separate(self):
        for text,role in [('The report was published after the expedition.','publication'),
                          ('The report was revised before the departure.','revision'),
                          ('The letter was received after the departure.','receipt')]:
            p=kernel.relationship_assertion(text);self.assertEqual(p['date_role'],role)
            self.assertEqual(p['reference_date_role'],'unresolved')

    def test_passive_by_phrase_has_explicit_actor_without_identity(self):
        p=kernel.relationship_assertion('The district was surveyed by Ruth Stone.')
        self.assertEqual(p['actor_text'],'Ruth Stone');self.assertIsNone(p['event_identity'])
        self.assertIsNone(kernel.relationship_assertion('The district was surveyed by her.'))

    def test_unit_boundaries_keep_wrapped_cause_and_ocr_headings(self):
        text='1-1\nSUMMARY\nThe expedition was delayed because of heavy\nrain.\nThe rescue ship provided food for safe return.'
        r=self.add(text);body=body_text(r.body_html);units=list(source_units.statement_units(body))
        self.assertTrue(any(q=='The expedition was delayed because of heavy\nrain.' for a,b,q in units))
        for a,b,q in units:self.assertEqual(body[a:b],q)

    def test_source_layers_and_source_bytes_are_preserved(self):
        r=self.add('<nav>Ruth Stone appointed Mira Vale.</nav><h2>Editorial introduction</h2><p>The account is disputed.</p><h2>Transcript</h2><p>The expedition was delayed because of rain.</p><blockquote><p>The report was published after the voyage.</p></blockquote>',markup=True)
        raw=(self.root/r.path).read_bytes();report=source_units.inspect_source(r)
        layers={u['documentary_layer'] for u in report['units']}
        self.assertIn('site_chrome',layers);self.assertIn('documentary_transcript',layers);self.assertIn('quotation',layers)
        self.assertEqual((self.root/r.path).read_bytes(),raw);self.assertFalse(report['authoritative'])

    def test_chrome_quote_and_plan_scope_do_not_certify_cause(self):
        for markup in ['<nav>{}</nav>','<blockquote>{}</blockquote>','<h2>Plan</h2><p>{}</p>']:
            with tempfile.TemporaryDirectory() as tmp:
                write(tmp,doc_id='REC',title='Archive',scope='archive',body_html=markup.format('The expedition was delayed because of rain.'))
                r=answer_query(tmp,'Why was the expedition delayed?').contract
                self.assertFalse(r['claims']);self.assertFalse(r['answer_supported'])
        self.add('The plan was as follows. The expedition was delayed because of rain.')
        self.assertFalse(self.ask('Why was the expedition delayed?')['claims'])

    def test_units_report_budget_exhaustion(self):
        r=self.add('The expedition was delayed because of rain. '*80)
        report=source_units.inspect_source(r,max_chars=1000,max_units=2)
        self.assertFalse(report['complete_source_examined']);self.assertTrue(report['limits_reached'])

    def test_immutable_cache_never_serves_changed_content_or_policy(self):
        _cached_projection.cache_clear();self.assertEqual(body_text('<p>Old wording.</p>'),'Old wording.')
        body_text('<p>Old wording.</p>');self.assertGreater(_cached_projection.cache_info().hits,0)
        self.assertEqual(body_text('<p>New wording.</p>'),'New wording.')
        self.add('The expedition was delayed because of rain.',external='no')
        self.assertFalse(self.ask('Why was the expedition delayed?',profile=PROFILES['external'])['claims'])

    def test_fabricated_relationship_fields_do_not_change_kernel_meaning(self):
        self.add('The expedition was delayed because of rain.')
        index=PassageIndex(self.root,'Why was the expedition delayed?');p=index.passages[0]
        proposals=documentary.propose(index,[p]);self.assertTrue(proposals)
        proposals[0].update(cause_text='a conspiracy',confidence=1,source_support_established=True)
        proofs=kernel.check(index,proposals)['proofs']
        self.assertEqual(proofs[0]['proposition']['cause_text'],'rain')

    def test_trimmed_qualifier_or_false_quote_is_rejected(self):
        rec=self.add('If approved, the expedition was delayed because of rain.')
        body=body_text(rec.body_html);a=body.index('the expedition')
        p={'kind':'relationship_statement','path':rec.path,'source_id':rec.id,'hash':rec.hash_actual,'start':a,'end':len(body),'quote':body[a:]}
        self.assertFalse(kernel.check(PassageIndex(self.root,'Why was the expedition delayed?'),[p])['proofs'])

    def test_wording_comparison_checks_changes_without_correction_or_motive(self):
        p=kernel.wording_difference('We held the northern coastal defensive position until dawn.','We held the northern coastal defensive position until noon.')
        self.assertTrue(any(c['operation']=='replace' for c in p['alignment']))
        self.assertFalse(p['correction_relationship_established']);self.assertFalse(p['whole_document_absence_established'])
        self.assertFalse(p['version_order_established'])

    def test_independent_wording_proposals_are_reread(self):
        self.add('We held the northern coastal defensive position until dawn.');self.add('We held the northern coastal defensive position until noon.')
        index=PassageIndex(self.root,'Compare the wording about the position.')
        p=documentary.propose(index,index.passages)
        comparisons=[p for p in p if p['kind']=='wording_comparison'];self.assertTrue(comparisons)
        comparisons[0]['other']['quote']='Invented wording.'
        self.assertFalse(kernel.check(index,comparisons[:1])['proofs'])

    def test_changed_source_discards_checked_cause(self):
        rec=self.add('The expedition was delayed because of rain.');check=kernel.check
        def mutate(*args,**kw):
            result=check(*args,**kw);p=self.root/rec.path;p.write_text(p.read_text().replace('rain','snow'));return result
        with patch('mplpb_answers.documentary.kernel.check',side_effect=mutate):r=self.ask('Why was the expedition delayed?')
        self.assertFalse(r['claims']);self.assertFalse(r['answer_supported']);self.assertEqual(r['diagnostic']['code'],'source_changed')

    def test_large_punctuation_tail_is_bounded(self):
        # Regression for the preserved first long-document CPU failure.
        text=('a'*10000+'...\n')*12+'SUMMARY\nThe expedition was delayed because of rain.'
        units=list(source_units.statement_units(text))
        self.assertTrue(any(q=='The expedition was delayed because of rain.' for a,b,q in units))

    def test_source_identity_does_not_merge_events_or_authenticate_authors(self):
        self.add('The expedition was delayed because of rain.');self.add('The expedition was delayed because of rain.')
        index=PassageIndex(self.root,'expedition');anchors=[{'path':r.path,'source_id':r.id,'hash':r.hash_actual} for r in index.records]
        r=kernel.check_source_identity(index,*anchors)
        self.assertTrue(r['same_canonical_body']);self.assertFalse(r['same_ledger_occurrence'])
        self.assertFalse(r['event_identity_established']);self.assertFalse(r['independent_corroboration_established'])
        self.assertIsNone(r['same_original_bytes'])
        same=kernel.check_source_identity(index,anchors[0],anchors[0]);self.assertTrue(same['source_identity_established'])

    def test_source_identity_rechecks_content_after_indexing(self):
        rec=self.add('The expedition was delayed because of rain.');index=PassageIndex(self.root,'expedition')
        anchor={'path':rec.path,'source_id':rec.id,'hash':rec.hash_actual}
        p=self.root/rec.path;p.write_text(p.read_text().replace('rain','snow'))
        self.assertFalse(kernel.check_source_identity(index,anchor,anchor)['source_identity_established'])

    def test_reconstruction_graph_never_merges_similar_events(self):
        self.add('Ruth Stone sent the report.');self.add('Ruth Stone sent the report.')
        from mplpb_work.prose_evidence import reconstruct_report
        r=reconstruct_report(self.root,'Who sent the report?')
        graph=r['candidate_analysis']['information_map']['relationship_graph']
        self.assertEqual(graph['event_identity_merges'],0);self.assertFalse(graph['source_support_established'])
        self.assertGreaterEqual(sum(n['kind']=='event_candidate' for n in graph['nodes']),2)

    def test_unchanged_declaration_question_gets_checked_local_comparison(self):
        from tools.unprepared_sources import import_corpus
        from tools.source_roundtrip import original_passage
        corpus=Path(__file__).resolve().parents[1]/'evaluation/unprepared-originals/2026-11-16'
        root=self.root/'originals';receipt=import_corpus(corpus,root)
        question=next(c['question'] for c in json.loads((corpus/'questions.json').read_text())['cases'] if c['id']=='H05')
        r=answer_query(root,question).contract
        self.assertEqual(r['kind'],'supported_answer');self.assertTrue(r['answer_supported'])
        compared=[c for c in r['claims'] if c['proposition']['relation']=='exact_wording_comparison'];self.assertTrue(compared)
        self.assertTrue(any('self-evident' in c['text'] and 'sacred & undeniable' in c['text'] for c in compared))
        for claim in compared:
            self.assertFalse(claim['proposition']['correction_relationship_established'])
            for cite in claim['citations']:self.assertTrue(original_passage(corpus,receipt,cite)['round_trip_quote_fidelity'])
