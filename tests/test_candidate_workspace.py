import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from mplpb_combined.ledger import write, withdraw
from mplpb_combined.reader import PROFILES
from mplpb_answers.pipeline import answer_query
from mplpb_work import sorter
from mplpb_work.candidate_workspace import build,verify_workspace,EXPLORATORY,ELIGIBLE,main


class CandidateWorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.raw=self.root/'processed';self.raw.mkdir();self.ledger=self.root/'originals';self.ledger.mkdir()

    def original(self,number=1,text='Mara wrote the Redwood memorandum.',**kwargs):
        return write(self.ledger,doc_id='DOC-'+str(number),title='Redwood memorandum',scope='Redwood memorandum',origin='human',body_html='<p>'+text+'</p>',**kwargs)

    def graph(self,documents):
        for name,text in documents.items():(self.raw/name).write_bytes(text.encode('utf-8'))
        return sorter.sort_directory(self.raw,mode='compare')

    def test_one_owner_exact_match_does_not_transfer_approval(self):
        r=self.original();g=self.graph({'copy.txt':'Mara wrote the Redwood memorandum.'})
        w=build(g,self.raw,self.ledger,question='Who wrote the Redwood memorandum?')
        d=w['mplpb_decision'];self.assertEqual(d['status'],'one_eligible_owner');self.assertEqual(d['page']['id'],r.id)
        self.assertTrue(d['strict_answer']['answer_supported'])
        c=next(c for c in w['candidates'] if c['kind']=='exact_match')
        self.assertEqual(c['status'],'candidate for review');self.assertFalse(c['approval_transferred']);self.assertFalse(c['answer_supported'])
        self.assertEqual(c['processed']['evidence_status'],EXPLORATORY);self.assertEqual(c['original']['evidence_status'],ELIGIBLE)
        s=c['processed']['span'];self.assertEqual((self.raw/s['path']).read_bytes()[s['byte_start']:s['byte_end']].decode(),s['text'])
        o=c['original'];self.assertEqual((self.ledger/o['path']).read_bytes()[o['byte_start']:o['byte_end']].decode(),o['raw_excerpt'])
        self.assertTrue(verify_workspace(w,g,self.raw,self.ledger)['status'])

    def test_two_eligible_owners_withhold_even_if_processed_prefers_one(self):
        self.original();self.original(2,'Ivo wrote the Redwood memorandum.')
        g=self.graph({'preferred.txt':'Mara wrote the Redwood memorandum.'})
        w=build(g,self.raw,self.ledger,question='Who wrote the Redwood memorandum?')
        d=w['mplpb_decision'];self.assertEqual(d['status'],'multiple_eligible_owners');self.assertEqual(d['eligible_owner_count'],2)
        self.assertIsNone(d['strict_answer']);self.assertEqual(len(d['competing_sources']),2);self.assertTrue(w['processed_passages'])

    def test_processed_only_topic_exploration_survives_no_owner(self):
        self.original();g=self.graph({'a.txt':'Tess studied rare lunar lichens.','b.txt':'Lunar lichens remain unresolved.'})
        w=build(g,self.raw,self.ledger,question='What about lunar lichens?')
        self.assertEqual(w['mplpb_decision']['status'],'no_eligible_owner');self.assertIsNone(w['mplpb_decision']['strict_answer'])
        self.assertEqual(len(w['processed_passages']),2);self.assertEqual(len(w['unmatched_passages']),2)
        self.assertFalse(w['answer_supported'])
        for p in w['processed_passages']:self.assertEqual(p['evidence_status'],EXPLORATORY)

    def test_processed_contradiction_is_not_a_strict_conflict(self):
        self.original();g=self.graph({'opposing.txt':'Mara did not write the Redwood memorandum.'})
        w=build(g,self.raw,self.ledger,question='Who wrote the Redwood memorandum?')
        self.assertTrue(w['mplpb_decision']['strict_answer']['answer_supported'])
        c=next(c for c in w['candidates'] if c['kind']=='conflicting_wording')
        self.assertFalse(c['answer_supported']);self.assertEqual(c['identity'],'unresolved')
        self.assertIn('did not',c['processed']['span']['text'])

    def test_only_current_eligible_owners_count(self):
        self.original();retired=self.original(2,'Ivo wrote the Redwood memorandum.');withdraw(self.ledger,retired.id,note='permission withdrawn')
        self.original(3,'Nora wrote the Redwood memorandum.',external='no')
        g=self.graph({'a.txt':'Mara wrote the Redwood memorandum.'})
        w=build(g,self.raw,self.ledger,question='Who wrote the Redwood memorandum?',profile=PROFILES['external'])
        self.assertEqual(w['mplpb_decision']['eligible_owner_count'],1)
        self.assertFalse(any(c['original']['source_id'] in {retired.id,'DOC-3'} for c in w['candidates']))

    def test_references_corrections_and_unresolved_targets_are_distinct(self):
        self.original();g=self.graph({'ref.txt':'See DOC-1 for the Redwood memorandum.','correction.txt':'Corrects DOC-1: Redwood memorandum wording remains unresolved.','missing.txt':'See DOC-99 for the Redwood memorandum.'})
        w=build(g,self.raw,self.ledger,topic='Redwood memorandum')
        kinds={c['kind'] for c in w['candidates']};self.assertIn('possible_reference',kinds);self.assertIn('possible_correction',kinds)
        self.assertTrue(any(p['span']['path']=='missing.txt' for p in w['unmatched_passages']))
        for c in w['candidates']:self.assertEqual(c['correction_status'],'unresolved')

    def test_processed_disagreements_remain_exploratory(self):
        g=self.graph({'a.txt':'Mara wrote the Redwood memorandum.','b.txt':'Mara did not write the Redwood memorandum.'})
        w=build(g,self.raw,self.ledger,topic='Redwood memorandum')
        self.assertTrue(w['processed_disagreements'])
        for d in w['processed_disagreements']:self.assertEqual(d['evidence_status'],EXPLORATORY);self.assertFalse(d['answer_supported'])

    def test_truncation_and_source_or_permission_changes_refuse_replay(self):
        r=self.original();g=self.graph({'a.txt':'Mara wrote the Redwood memorandum.','b.txt':'Ivo wrote the Redwood memorandum.'})
        w=build(g,self.raw,self.ledger,question='Who wrote the Redwood memorandum?',max_passages=1,max_chars=100)
        self.assertLessEqual(w['exploration_budget']['unique_spans'],1);self.assertTrue(w['exploration_budget']['display_truncated'])
        self.assertTrue(w['mplpb_decision']['strict_answer']['answer_supported']);self.assertEqual(w['exploration_budget']['strict_slots_consumed'],0)
        tampered=copy.deepcopy(w);tampered['processed_passages'][0]['answer_supported']=True
        with self.assertRaises(ValueError):verify_workspace(tampered,g,self.raw,self.ledger)
        withdraw(self.ledger,r.id,note='revoked')
        with self.assertRaises(ValueError):verify_workspace(w,g,self.raw,self.ledger)
        (self.raw/'a.txt').write_text('Altered source.')
        with self.assertRaises(ValueError):build(g,self.raw,self.ledger,topic='Redwood memorandum')

    def test_ambiguous_synonym_does_not_create_owner_or_relationship(self):
        g=self.graph({'bank.txt':'Tess sat by the bank.','mail.txt':'Tess planned to send the report.'})
        w=build(g,self.raw,self.ledger,question='Who received the report?')
        self.assertEqual(w['mplpb_decision']['eligible_owner_count'],0);self.assertFalse(w['candidates'])
        self.assertTrue(any('planned to send' in p['span']['text'] for p in w['processed_passages']))

    def test_quoted_and_conditional_corrections_keep_unresolved_scope(self):
        self.original();g=self.graph({'quoted.txt':'> Corrects DOC-1: Redwood memorandum.',
                                     'planned.txt':'If I revise this, it corrects DOC-1 Redwood memorandum.'})
        w=build(g,self.raw,self.ledger,topic='Redwood memorandum')
        self.assertFalse(any(c['kind']=='possible_correction' for c in w['candidates']))
        self.assertTrue(w['unresolved_references'])
        self.assertTrue(any(c['kind']=='quoted_or_qualified_reference_review' for c in w['candidates']))

    def test_original_byte_spans_preserve_entities_and_negation(self):
        self.original(text='Mara did not write the Redwood &amp; élan memorandum.')
        g=self.graph({'unicode.txt':'Mara did not write the Redwood & élan memorandum.'})
        w=build(g,self.raw,self.ledger,topic='Redwood memorandum')
        c=next(c for c in w['candidates'] if c['kind']=='exact_match')
        self.assertIn('did not',c['original']['quote']);self.assertIn('&amp;',c['original']['raw_excerpt'])
        o=c['original'];self.assertEqual((self.ledger/o['path']).read_bytes()[o['byte_start']:o['byte_end']].decode(),o['raw_excerpt'])

    def test_corrupted_original_loses_eligibility_but_not_processed_exploration(self):
        r=self.original();g=self.graph({'a.txt':'Mara wrote the Redwood memorandum.'})
        w=build(g,self.raw,self.ledger,question='Who wrote the Redwood memorandum?')
        p=self.ledger/r.path;p.write_text(p.read_text().replace('Mara wrote','Nora wrote'))
        with self.assertRaises(ValueError):verify_workspace(w,g,self.raw,self.ledger)
        fresh=build(g,self.raw,self.ledger,question='Who wrote the Redwood memorandum?')
        self.assertEqual(fresh['mplpb_decision']['status'],'no_eligible_owner')
        self.assertFalse(fresh['candidates']);self.assertTrue(fresh['processed_passages'])

    def test_cli_build_and_fresh_peruse(self):
        self.original();g=self.graph({'a.txt':'Mara wrote the Redwood memorandum.'})
        graph=self.root/'sorter.json';graph.write_text(json.dumps(g));workspace=self.root/'workspace.json'
        common=[str(graph),'--processed',str(self.raw),'--originals',str(self.ledger)]
        with patch('builtins.print'):
            self.assertEqual(main(['build']+common+['--question','Who wrote the Redwood memorandum?','--output',str(workspace)]),0)
            self.assertEqual(main(['peruse']+common+['--workspace',str(workspace)]),0)
        self.assertTrue(workspace.exists())

    def test_one_owner_without_body_support_keeps_processed_claim_exploratory(self):
        self.original(text='The Redwood memorandum remains unassigned.')
        g=self.graph({'unsupported.txt':'Mara wrote the Redwood memorandum.'})
        w=build(g,self.raw,self.ledger,question='Who wrote the Redwood memorandum?')
        self.assertEqual(w['mplpb_decision']['status'],'one_eligible_owner')
        self.assertFalse(w['mplpb_decision']['strict_answer']['answer_supported'])
        self.assertTrue(w['processed_passages']);self.assertFalse(w['processed_passages'][0]['answer_supported'])

    def test_resealing_an_exploratory_promotion_does_not_pass_fresh_replay(self):
        self.original();g=self.graph({'a.txt':'Mara wrote the Redwood memorandum.'})
        w=build(g,self.raw,self.ledger,question='Who wrote the Redwood memorandum?')
        w['processed_passages'][0]['answer_supported']=True
        w['workspace_sha256']=sorter.digest({k:v for k,v in w.items() if k!='workspace_sha256'})
        with self.assertRaises(ValueError):verify_workspace(w,g,self.raw,self.ledger)

    def test_three_disconnected_shared_words_do_not_create_a_link(self):
        self.original(text='The antique mirrors were moved by Mara; the lunar samples contain minerals.')
        g=self.graph({'unrelated.txt':'Tess observed lunar minerals beside antique mirrors.'})
        w=build(g,self.raw,self.ledger,topic='lunar minerals mirrors')
        self.assertFalse(w['candidates'])
        self.assertTrue(w['processed_passages'])

    def test_h05_strict_proof_is_unchanged_by_tiny_review_budget(self):
        from tools.unprepared_sources import import_corpus
        corpus=Path(__file__).resolve().parents[1]/'evaluation/unprepared-originals/2026-11-16'
        q=next(c['question'] for c in json.loads((corpus/'questions.json').read_text())['cases'] if c['id']=='H05')
        self.ledger.rmdir();import_corpus(corpus,self.ledger)
        g=self.graph({'truth.txt':'Darwin discussed truth and the Declaration.\n\nA Declaration comparison remains exploratory.'})
        before=answer_query(self.ledger,q,max_passages=12,max_chars=8000).contract
        w=build(g,self.raw,self.ledger,question=q,max_passages=1,max_chars=20,strict_passages=12,strict_chars=8000)
        after=answer_query(self.ledger,q,max_passages=12,max_chars=8000).contract
        self.assertTrue(before['answer_supported']);self.assertEqual(before,after)
        self.assertEqual(after['documentary_support']['admission']['characters_admitted'],4070)
        self.assertEqual(w['exploration_budget']['strict_slots_consumed'],0)
        self.assertTrue(w['exploration_budget']['display_truncated'])


if __name__=='__main__':unittest.main()
