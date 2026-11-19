"""Exploration can suggest meanings; only the existing kernel can award support."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from mplpb_combined.ledger import write, withdraw
from mplpb_answers.pipeline import answer_query
from mplpb_work import sorter_v2 as sorter
from mplpb_work import sorter_explorer as view


class SorterExplorerTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name); self.dump = self.root/'dump'; self.dump.mkdir()
        self.ledger = self.root/'ledger'
        (self.dump/'one.md').write_bytes('Message-ID: MAIL-001\r\nFrom: Ana\r\nSubject: Beacon\r\n\r\nAna requested a café beacon inspection.\r\n'.encode())
        (self.dump/'two.md').write_text('Message-ID: MAIL-001\nFrom: Ana\nSubject: Beacon\n\nAna canceled the beacon inspection.\n')
        (self.dump/'three.md').write_text('Message-ID: MAIL-003\n\nThis corrects MAIL-999 about the beacon count.\n')

    def test_modes_keep_identical_graph_nodes_and_labels(self):
        plain = sorter.sort_directory(self.dump, 'not-compared'); compared = sorter.sort_directory(self.dump, 'compare')
        before = copy.deepcopy(compared)
        p = view.label_graph(plain, self.dump); c = view.label_graph(compared, self.dump)
        self.assertEqual(p['source_graph']['nodes'], c['source_graph']['nodes'])
        self.assertEqual(p['node_labels'], c['node_labels'])
        self.assertNotEqual(p['edge_labels'], c['edge_labels'])
        self.assertEqual(before, compared)
        self.assertFalse(c['answer_supported'])
        clusters = {e['id'] for e in compared['edges'] if e['kind']=='candidate_identity_cluster'}
        for label in c['edge_labels']:
            self.assertFalse(label['source_support_established']); self.assertFalse(label['historical_truth_independently_verified'])
            if label['item_id'] in clusters:
                self.assertIn('document_identity_candidate', label['tags']); self.assertIn('changed_body', label['tags'])
                self.assertIn('event_coreference_unverified', label['tags'])
        self.assertTrue(any('missing_link' in e['tags'] for e in c['edge_labels']))
        c['source_graph']['nodes'].clear(); self.assertEqual(before, compared)

    def test_embedded_identity_and_retired_status_remain_provisional(self):
        (self.dump/'example.md').write_text('Documentation example, not a communication.\n```text\nMessage-ID: MAIL-001\nStatus: retired\n```\n')
        (self.dump/'retired.md').write_text('Message-ID: OLD-001\nStatus: retired\n\nThe beacon note is withdrawn.\n')
        g=sorter.sort_directory(self.dump,'compare');r=view.label_graph(g,self.dump)
        occurrences={n['id']:n for n in g['nodes'] if n['kind']=='source_occurrence'}
        for edge in g['edges']:
            if edge['kind']=='candidate_identity_cluster':
                self.assertNotIn('example.md',[occurrences[o]['span']['path'] for o in edge['members']])
        self.assertTrue(any('qualified_context' in n['tags'] for n in r['node_labels']))
        self.assertTrue(any('declared_retired' in n['tags'] for n in r['node_labels']))
        self.assertIn('provisional',view.render(r))

    def test_span_labels_are_textual_checks_not_semantic_support(self):
        g = sorter.sort_directory(self.dump)
        result = view.label_graph(g, self.dump)
        for node, label in zip(g['nodes'],result['node_labels']):
            self.assertFalse(label['answer_supported']); self.assertIn('historical_truth_unverified',label['tags'])
            span=node['span'];raw=(self.dump/span['path']).read_bytes()
            if 'text' in span:
                self.assertEqual(raw[span['byte_start']:span['byte_end']].decode(),span['text'])
                self.assertIn('exact_span',label['tags'])

    def test_source_change_rejects_old_graph(self):
        g=sorter.sort_directory(self.dump)
        (self.dump/'two.md').write_text('Different bytes')
        with self.assertRaises(ValueError):view.label_graph(g,self.dump)

    def test_no_model_returns_labeled_exact_evidence_and_no_writes(self):
        before={p.name:p.read_bytes() for p in self.dump.iterdir()}
        with patch.object(view,'LocalBackend',side_effect=AssertionError('Model must remain opt-in')):
            r=view.explore_ideas('What might explain the beacon accounts?',dump=self.dump)
        self.assertTrue(r['passages']);self.assertFalse(r['answer_supported'])
        self.assertEqual(r['model']['status'],'disabled')
        self.assertTrue(all(s['kind']=='source_quote' and not s['source_support_established'] for s in r['segments']))
        self.assertEqual(before,{p.name:p.read_bytes() for p in self.dump.iterdir()})
        self.assertIn('UNOFFICIAL',view.render(r));self.assertIn('Historical truth: not independently verified',view.render(r))

    def proposal(self, **extra):
        s={'kind':'hypothesis','text':'These beacon passages might concern the same plan; that remains uncertain.',
           'citations':['P1'],'missing_evidence':['A record explicitly linking the two appearances.']}
        s.update(extra);return json.dumps({'segments':[s]})

    def test_model_can_propose_but_cannot_override_native_refusal(self):
        write(self.ledger,doc_id='DOC-1',title='Archive',scope='beacon',body='Ana requested a beacon inspection.')
        q='Did the beacon inspection cause an eclipse?'
        before=answer_query(self.ledger,q).contract
        with patch.object(view,'LocalBackend') as cls:
            cls.return_value.generate.return_value=self.proposal()
            r=view.explore_ideas(q,ledger=self.ledger,use_model=True)
        self.assertFalse(before['answer_supported']);self.assertEqual(before,r['native_mplpb']['result'])
        self.assertEqual(r['model']['status'],'unverified_interpretations')
        self.assertFalse(r['segments'][0]['answer_supported']);self.assertFalse(r['answer_supported'])
        self.assertEqual(before,answer_query(self.ledger,q).contract)
        args=cls.return_value.generate.call_args
        self.assertIn('missing links',args.args[0][0]['content'])
        self.assertEqual(args.kwargs['max_tokens'],1200)

    def test_native_supported_statement_is_separate_from_speculation(self):
        write(self.ledger,doc_id='DOC-1',title='Archive',scope='beacon',body='Owner: Ana')
        r=view.explore_ideas('What is owner for record DOC-1?',ledger=self.ledger)
        self.assertTrue(r['native_mplpb']['result']['answer_supported'])
        self.assertFalse(r['answer_supported'])
        self.assertIn('not independently verified historical truth',r['native_mplpb']['label'])

    def test_false_citations_false_quotes_and_promotion_fields_rejected(self):
        bad=[self.proposal(citations=['INVENTED']),self.proposal(kind='source_quote',text='A completed delivery occurred.'),
             self.proposal(answer_supported=True),self.proposal(text='This is a proven fact.'),
             self.proposal(missing_evidence=[]),self.proposal(citations=[]),'{"segments":[],"segments":[]}']
        for reply in bad:
            with self.subTest(reply=reply),patch.object(view,'LocalBackend') as cls:
                cls.return_value.generate.return_value=reply
                r=view.explore_ideas('Explain the beacon',dump=self.dump,use_model=True)
                self.assertEqual(r['model']['status'],'unavailable_or_rejected')
                self.assertTrue(all(s['kind']=='source_quote' for s in r['segments']))
                self.assertNotIn('proven fact',json.dumps(r))

    def test_exact_quote_and_uncited_open_question_are_not_answers(self):
        p=[{'citation_id':'P1','text':'Ana did not send the order.'}]
        quote={'kind':'source_quote','text':'Ana did not send the order.','citations':['P1'],'missing_evidence':[]}
        question={'kind':'open_question','text':'Is a receipt missing?','citations':[],'missing_evidence':[]}
        r=view._validate_reply(json.dumps({'segments':[quote,question]}),p)
        self.assertEqual(r[0]['quotation_fidelity'],'complete_cited_passage_checked')
        self.assertTrue(all(not x['answer_supported'] for x in r))
        quote['text']='send the order.'
        with self.assertRaises(ValueError):view._validate_reply(json.dumps({'segments':[quote]}),p)

    def test_restricted_and_question_excluded_native_material_never_reaches_model(self):
        for kwargs,profile in (({'external':'no'},'external'),({'not_for':'secret'},'internal')):
            with self.subTest(profile=profile),tempfile.TemporaryDirectory() as ledger:
                write(ledger,doc_id='PRIVATE-1',title='Archive',scope='beacon',body='PRIVATE-SENTINEL beacon secret',**kwargs)
                with patch.object(view,'LocalBackend',side_effect=AssertionError('No eligible context')):
                    r=view.explore_ideas('Explain beacon secret',ledger=ledger,profile=profile,use_model=True)
                self.assertNotIn('PRIVATE-SENTINEL',json.dumps(r));self.assertEqual(r['passages'],[])

    def test_external_raw_dump_is_not_even_read(self):
        with patch.object(sorter,'sort_directory',side_effect=AssertionError('Raw external access')):
            r=view.explore_ideas('Explain beacon',dump=self.dump,profile='external',use_model=True)
        self.assertTrue(r['dump_withheld']);self.assertFalse(r['passages'])

    def test_withdrawal_or_raw_change_during_model_discards_generated_output(self):
        write(self.ledger,doc_id='DOC-1',title='Archive',scope='beacon',body='Ana requested a beacon inspection.')
        def withdraw_during(*args,**kwargs):withdraw(self.ledger,'DOC-1');return self.proposal()
        with patch.object(view,'LocalBackend') as cls:
            cls.return_value.generate.side_effect=withdraw_during
            with self.assertRaisesRegex(ValueError,'changed'):
                view.explore_ideas('Explain beacon',ledger=self.ledger,use_model=True)
        def change_during(*args,**kwargs):(self.dump/'two.md').write_text('Changed beacon.');return self.proposal()
        with patch.object(view,'LocalBackend') as cls:
            cls.return_value.generate.side_effect=change_during
            with self.assertRaises(ValueError):view.explore_ideas('Explain beacon',dump=self.dump,use_model=True)

    def test_unreachable_backend_falls_back_to_source_inspection(self):
        with patch.object(view,'LocalBackend',side_effect=OSError('Unavailable')):
            r=view.explore_ideas('Explain beacon',dump=self.dump,use_model=True)
        self.assertEqual(r['model']['status'],'unavailable_or_rejected');self.assertTrue(r['segments'])

    def test_cli_labels_both_modes_and_free_question(self):
        for args in (['sort',str(self.dump),'--mode','compare','--json'],['ask','What ideas might connect the beacon notes?','--dump',str(self.dump),'--json']):
            p=subprocess.run([sys.executable,'-m','mplpb_work.sorter_explorer']+args,capture_output=True,text=True,timeout=30)
            self.assertEqual(p.returncode,0,p.stderr);value=json.loads(p.stdout)
            self.assertFalse(value['answer_supported']);self.assertIn('UNOFFICIAL',value['label'])


if __name__=='__main__':unittest.main()
