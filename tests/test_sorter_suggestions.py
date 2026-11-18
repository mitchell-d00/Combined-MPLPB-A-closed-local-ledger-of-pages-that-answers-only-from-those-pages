import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mplpb_work import sorter as core
from mplpb_work import sorter_suggestions as review


class SorterSuggestionsTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); self.raw=self.root/'raw';self.raw.mkdir()

    def source(self,name,text):
        (self.raw/name).write_bytes(text.encode('utf-8'))

    def run_review(self,query,*,synonyms=True,relater=False,custom=None,mode='compare'):
        graph=core.sort_directory(self.raw,mode=mode);before=copy.deepcopy(graph)
        result=review.suggestions(graph,self.raw,query,synonym_ranker=synonyms,candidate_relater=relater,user_glossary=custom)
        self.assertEqual(graph,before)
        return result

    def test_disabled_outputs_equal_core_in_both_modes(self):
        self.source('a.txt','Mara sent a report.\n\nIvo received a report.')
        for mode in ['not-compared','compare']:
            graph=core.sort_directory(self.raw,mode=mode)
            self.assertEqual(review.suggestions(graph,self.raw,'report'),graph)

    def test_distinct_exact_neighbor_signals_and_unicode_byte_spans(self):
        self.source('a.txt','Zoë sent a report.\r\n\r\nIvo received a report.')
        result=self.run_review('sent report')
        signals=[s for h in result['ranked_hits'] for s in h['signals']]
        self.assertTrue(any(s['kind']=='exact' and s['original_phrase']=='sent' for s in signals))
        self.assertTrue(any(s['kind']=='synonym' and s['original_phrase']=='received' for s in signals))
        for s in signals:
            span=s['span'];raw=(self.raw/span['path']).read_bytes()
            self.assertEqual(raw[span['byte_start']:span['byte_end']].decode(),s['original_phrase'])
            self.assertEqual(raw.decode()[span['char_start']:span['char_end']],s['original_phrase'])

    def test_ambiguous_glossary_exposes_both_senses(self):
        self.source('a.txt','The river shore meets the lender.')
        custom={'groups':[{'name':'bank-water','terms':['bank','shore']},{'name':'bank-money','terms':['bank','lender']}]}
        result=self.run_review('bank',custom=custom)
        self.assertEqual(set(result['ranked_hits'][0]['neighbor_groups']),{'bank-water','bank-money'})
        self.assertIn('bank',result['ranked_hits'][0]['ambiguous_vocabulary_terms'])

    def test_negation_plan_receipt_distinct_and_both_opposed_passages_visible(self):
        self.source('a.txt','Mara planned to send the report.\n\nMara did not send the report.\n\nIvo received the report.')
        result=self.run_review('send report')
        quotes=[h['span']['text'] for h in result['ranked_hits']]
        self.assertIn('Mara planned to send the report.',quotes)
        self.assertIn('Mara did not send the report.',quotes)
        self.assertIn('Ivo received the report.',quotes)
        self.assertTrue(all(h['assessment']['answer_supported'] is False for h in result['ranked_hits']))
        self.assertFalse(result['source_authority_changed'])

    def test_shared_subject_never_identity_or_duplicate(self):
        self.source('a.txt','Subject: Cedar\n\nMara sent a report.')
        self.source('b.txt','Subject: Cedar\n\nIvo planned a journey.')
        result=self.run_review('Cedar',relater=True)
        kinds={l['kind'] for l in result['candidate_links']}
        self.assertIn('shared_subject_review',kinds)
        self.assertNotIn('possible_duplicate_appearances',kinds)
        self.assertNotIn('possible_conflicting_versions',kinds)

    def test_quoted_header_does_not_create_primary_identity(self):
        self.source('a.txt','Record-ID: ABC-101\n\nMara sent a report.')
        self.source('b.txt','An example:\n\n```\nRecord-ID: ABC-101\n```\n\nIvo received a report.')
        result=self.run_review('report',relater=True)
        self.assertFalse(any(l['kind'] in {'possible_duplicate_appearances','possible_conflicting_versions'} for l in result['candidate_links']))

    def test_missing_link_has_no_invented_target(self):
        self.source('a.txt','Record-ID: ABC-101\n\nThis corrects XYZ-999 only.')
        result=self.run_review('corrects',relater=True)
        self.assertTrue(result['unresolved_references'])
        self.assertTrue(all(r['target'] is None for r in result['unresolved_references']))
        self.assertFalse(any(l['kind']=='possible_correction' for l in result['candidate_links']))

    def test_explicit_versions_and_corrections_are_candidate_endpoints(self):
        self.source('a.txt','Record-ID: ABC-101\n\nMara sent the report.')
        self.source('b.txt','Record-ID: ABC-101\n\nMara did not send the report.')
        self.source('c.txt','Record-ID: XYZ-202\n\nThis corrects ABC-101 only.')
        result=self.run_review('report correction',relater=True)
        self.assertIn('possible_conflicting_versions',{l['kind'] for l in result['candidate_links']})
        for link in result['candidate_links']:
            for key in ['left','right']:
                e=link[key];s=e['span'];raw=(self.raw/s['path']).read_bytes()
                self.assertEqual(raw[s['byte_start']:s['byte_end']].decode(),s['text'])
                self.assertTrue(e['occurrence_id'])
            self.assertFalse(link['assessment']['answer_supported']);self.assertFalse(link['applied'])
            self.assertEqual(link['identity'],'unresolved');self.assertEqual(link['causation'],'unresolved')

    def test_changed_source_refuses_replay(self):
        self.source('a.txt','Mara sent a report.');graph=core.sort_directory(self.raw)
        self.source('a.txt','Mara did not send a report.')
        with self.assertRaises(core.SortError):review.suggestions(graph,self.raw,'sent',synonym_ranker=True)

    def test_literal_glossary_validation(self):
        for value in [{'groups':[{'name':'x','terms':['bank','.*']}]},{'groups':[{'name':'x','terms':['bank','BANK']}]},{'groups':'bank'}]:
            with self.assertRaises(core.SortError):review.glossary(value)

    def test_forged_score_and_links_fail_fresh_replay(self):
        self.source('a.txt','Mara sent a report.')
        result=self.run_review('sent report');review.verify_suggestions(result,self.raw)
        result['ranked_hits'][0]['rank_score']=999
        with self.assertRaises(core.SortError):review.verify_suggestions(result,self.raw)

    def test_cli_off_exact_delegation_and_on_mandatory_label(self):
        self.source('a.txt','Mara sent a report.')
        off=self.root/'off.json';on=self.root/'on.json'
        base=[sys.executable,'-m','mplpb_work.sorter_suggestions','sort',str(self.raw)]
        first=subprocess.run(base+['--output',str(off)],capture_output=True,text=True)
        self.assertEqual(first.returncode,0,first.stderr)
        self.assertEqual(json.loads(off.read_text()),core.sort_directory(self.raw))
        second=subprocess.run(base+['--synonym-ranker','--query','received report','--output',str(on)],capture_output=True,text=True)
        self.assertEqual(second.returncode,0,second.stderr)
        self.assertIn(review.NOTICE,second.stdout);self.assertEqual(json.loads(on.read_text())['label'],review.NOTICE)
        peruse=subprocess.run([sys.executable,'-m','mplpb_work.sorter_suggestions','peruse',str(on),'--sources',str(self.raw)],capture_output=True,text=True)
        self.assertEqual(peruse.returncode,0,peruse.stderr);self.assertIn(review.NOTICE,peruse.stdout)
        self.assertIn('original_phrase',peruse.stdout)


if __name__=='__main__':unittest.main()
