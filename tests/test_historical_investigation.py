"""Expert relation crawling preserves evidence and coordinator boundaries."""
import contextlib
import hashlib
import html
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from mplpb_combined.ledger import write, Ledger
from mplpb_combined.reader import PROFILES
from mplpb_work.investigation import investigate


class HistoricalInvestigationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'corpus'

    def page(self, identifier, doc, related='', version='v1', **kwargs):
        body='Document ID: '+doc+'\nUpdated: 1900-01-01 '+version+'\n'
        if related:body+='Related: '+related+'\n'
        return write(self.root,doc_id=identifier,title='Archive witness',scope='archival records',
                     body_html='<pre>'+html.escape(body)+'</pre>',**kwargs)

    def crawl(self, **kwargs):
        return investigate(self.root,'Inspect archival records and declared relations',start_source_ids=['SRC-0001'],**kwargs)

    def test_crawls_only_declared_ids_through_existing_expert_receipts(self):
        self.page('SRC-0001','DOC-101','DOC-202 v1')
        self.page('SRC-0002','DOC-202','DOC-303 v1')
        self.page('SRC-0003','DOC-303')
        before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.rglob('*') if p.is_file()}
        report=self.crawl()
        self.assertEqual(report['status'],'evidence_report')
        self.assertEqual({s['id'] for s in report['sources']},{'SRC-0001','SRC-0002','SRC-0003'})
        self.assertEqual([r['status'] for r in report['relations']],['traversed','traversed'])
        self.assertEqual(len(report['receipts']),3)
        self.assertTrue(all(r['status']=='passed' for r in report['receipts']))
        self.assertFalse(report['answer_supported']);self.assertFalse(report['truth_verified'])
        self.assertFalse(report['chronology']['historical_event_order_verified'])
        for item in report['observations']:
            self.assertIn(item,report['verification']['verified'])
        self.assertEqual(before,{p:hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.rglob('*') if p.is_file()})
        self.assertNotIn('credential',json.dumps(report))

    def test_adaptive_search_prioritizes_uncovered_evidence_within_a_hop(self):
        def source(identifier, lines):
            write(self.root, doc_id=identifier, title="Station archive", scope="station archive",
                  body_html="<pre>" + html.escape("\n".join(lines)) + "</pre>")

        source("SRC-0001", ["Document ID: DOC-101", "Related: DOC-202, DOC-303, DOC-404"])
        source("SRC-0002", ["Document ID: DOC-202", "Receipt and dispatch for the station."])
        source("SRC-0003", ["Document ID: DOC-303", "Receipt and dispatch duplicates."])
        source("SRC-0004", ["Document ID: DOC-404", "Authorization for the station."])
        options = {"start_source_ids": ["SRC-0001"], "max_sources": 3}
        question = "Find receipt, dispatch and authorization in the station archive"
        baseline = investigate(self.root, question, **options)
        report = investigate(self.root, question, adaptive_search=True, **options)
        self.assertEqual([s["id"] for s in baseline["sources"]], ["SRC-0001", "SRC-0002", "SRC-0003"])
        self.assertEqual([s["id"] for s in report["sources"]], ["SRC-0001", "SRC-0002", "SRC-0004"])
        self.assertEqual(report["adaptive_search"], {"deepest_visited_hop": 1, "completed_hop": 0})
        self.assertTrue(any(r["status"] == "source_or_character_budget" for r in report["relations"]))
        self.assertFalse(report["answer_supported"])
        self.assertEqual(report["observations"], report["verification"]["verified"])

    def test_adaptive_search_prioritizes_explicit_supersession_and_keeps_hops(self):
        write(self.root, doc_id='SRC-0001', title='Archive witness', scope='archival records',
              body_html='<pre>Document ID: DOC-101\nRelated: DOC-202, DOC-303\nSupersedes: DOC-303</pre>')
        write(self.root, doc_id='SRC-0002', title='Archive witness', scope='archival records',
              body_html='<pre>Document ID: DOC-202\nSupersedes: DOC-404</pre>')
        self.page('SRC-0003', 'DOC-303')
        self.page('SRC-0004', 'DOC-404')
        report = self.crawl(adaptive_search=True, max_sources=3)
        self.assertEqual([s['id'] for s in report['sources']], ['SRC-0001', 'SRC-0003', 'SRC-0002'])
        self.assertEqual(report['adaptive_search'], {'deepest_visited_hop': 1, 'completed_hop': 1})
        report = self.crawl(adaptive_search=True)
        self.assertEqual(report['adaptive_search'], {'deepest_visited_hop': 2, 'completed_hop': 2})
        self.assertTrue(all(edge['status'] == 'traversed' for edge in report['relations']))

    def test_adaptive_search_preserves_restrictions_and_cli_contract(self):
        self.page('SRC-0001', 'DOC-101', 'DOC-202, DOC-303')
        self.page('SRC-0002', 'DOC-202', external='no')
        self.page('SRC-0003', 'DOC-303')
        from mplpb_answers.__main__ import main
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = main(['investigate', str(self.root), 'archival records',
                         '--source', 'SRC-0001', '--profile', 'external', '--adaptive-search'])
        self.assertEqual(code, 0)
        report = json.loads(stream.getvalue())
        self.assertEqual([s['id'] for s in report['sources']], ['SRC-0001', 'SRC-0003'])
        self.assertEqual([edge['status'] for edge in report['relations']], ['target_unavailable', 'traversed'])
        self.assertNotIn('SRC-0002', stream.getvalue())
        self.assertFalse(report['answer_supported'])
        with self.assertRaisesRegex(ValueError, 'adaptive_search must be a boolean'):
            self.crawl(adaptive_search=1)

    def test_hop_source_and_character_budgets_do_not_become_evidence(self):
        self.page('SRC-0001','DOC-101','DOC-202 v1')
        self.page('SRC-0002','DOC-202')
        for options in ({'max_hops':0},{'max_sources':1}):
            with self.subTest(options=options):
                report=self.crawl(**options)
                self.assertEqual([s['id'] for s in report['sources']],['SRC-0001'])
                self.assertNotEqual(report['relations'][0]['status'],'traversed')
                self.assertFalse(report['answer_supported'])
        for options in ({'max_hops':True},{'max_hops':6},{'max_sources':0},{'max_chars':999}):
            with self.assertRaises(ValueError):self.crawl(**options)

    def test_ambiguous_ids_and_unidentified_titles_stop(self):
        self.page('SRC-0001','DOC-101','DOC-202')
        self.page('SRC-0002','DOC-202',version='v1')
        self.page('SRC-0003','DOC-202',version='v2')
        report=self.crawl()
        self.assertEqual(len(report['sources']),1)
        self.assertEqual(report['relations'][0]['status'],'ambiguous_target')
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp,doc_id='SRC-0001',title='Guessing forbidden',scope='archival records',
                  body_html='<pre>Document ID: DOC-101\nRelated: An unnamed secret companion.</pre>')
            result=investigate(tmp,'archival records',start_source_ids=['SRC-0001'])
            self.assertEqual(result['relations'][0]['status'],'unresolved_target_identifier')

    def test_cycle_is_bounded_and_version_binding_is_exact(self):
        self.page('SRC-0001','DOC-101','DOC-202 v2')
        self.page('SRC-0002','DOC-202',version='v1')
        self.page('SRC-0003','DOC-202','DOC-101 v1',version='v2')
        report=self.crawl(max_hops=5)
        self.assertEqual({s['id'] for s in report['sources']},{'SRC-0001','SRC-0003'})
        self.assertTrue(all(e['status']=='traversed' for e in report['relations']))
        self.assertEqual(len(report['relations']),2)

    def test_negated_relations_do_not_license_crawl_hops(self):
        self.page('SRC-0001','DOC-101','Not related to DOC-202 v1')
        self.page('SRC-0002','DOC-202')
        report=self.crawl()
        self.assertEqual([s['id'] for s in report['sources']],['SRC-0001'])
        self.assertEqual(report['relations'][0]['status'],'unresolved_target_identifier')
        self.assertIn('Not related',report['relations'][0]['citation']['quote'])

    def test_large_unvisited_source_does_not_abort_bounded_header_discovery(self):
        self.page('SRC-0001','DOC-101')
        write(self.root,doc_id='SRC-0002',title='Large witness',scope='archival records',
              body_html='<pre>Document ID: LARGE-202\nUpdated: 1901-01-01 v1\n## Body\n'+'x'*1000001+'</pre>')
        report=self.crawl(max_chars=1000)
        self.assertEqual(report['status'],'evidence_report')
        self.assertEqual([s['id'] for s in report['sources']],['SRC-0001'])
        self.assertLessEqual(report['discovery_characters_examined'],1000000)

    def test_complete_index_resolves_beyond_old_limit_and_detects_ambiguity(self):
        from mplpb_combined.record import render_page
        from mplpb_work.investigation import _crawl
        seed = self.page('SRC-0001', 'DOC-101', 'DOC-202 v1')
        original = dict(Ledger(self.root).by_id[seed.id][0].fields)
        for i in range(2, 257):
            identity = f'SRC-{i:04d}'
            fields = {**original, 'document-id': identity}
            body = f'<pre>Document ID: PADDING-{i:04d}</pre>'
            (self.root/f'{identity.lower()}.html').write_text(render_page(fields, identity, body))
        self.page('SRC-0257', 'DOC-202')
        options = (self.root, 'archival records', PROFILES['internal'], ['SRC-0001'],
                   2, 5, 12000)
        report = _crawl(*options, adaptive_search=True)
        self.assertTrue(report['discovery_complete'])
        self.assertEqual(report['relations'][0]['status'], 'traversed')
        self.page('SRC-0258', 'DOC-202')
        report = _crawl(*options, adaptive_search=True)
        self.assertEqual(report['relations'][0]['status'], 'ambiguous_target')

    def test_classing_provenance_ends_related_field_without_becoming_a_target(self):
        write(self.root, doc_id='SRC-0001', title='Archive witness', scope='archival records',
              body_html=('<pre>Document ID: DOC-101</pre><pre>Related: DOC-202</pre>'
                         '<pre>Classing source SHA-256: sha256:bogus</pre>'))
        self.page('SRC-0002', 'DOC-202')
        report = self.crawl(adaptive_search=True)
        self.assertEqual([(e['target_document_id'], e['status']) for e in report['relations']],
                         [('DOC-202', 'traversed')])
        self.assertEqual(report['relations'][0]['citation']['quote'], 'Related: DOC-202')

    def test_original_question_exclusions_and_external_profile_hold_at_each_hop(self):
        self.page('SRC-0001','DOC-101','DOC-202 v1')
        self.page('SRC-0002','DOC-202',not_for='sensitive')
        report=investigate(self.root,'sensitive archival records',start_source_ids=['SRC-0001'])
        self.assertEqual(len(report['sources']),1)
        self.assertEqual(report['relations'][0]['status'],'target_unavailable')
        self.assertNotIn('SRC-0002',json.dumps(report))
        with self.assertRaises(ValueError):
            investigate(self.root,'sensitive archival records',start_source_ids=['SRC-0002'])

    def test_external_restriction_is_not_laundered_by_related_link(self):
        self.page('SRC-0001','DOC-101','DOC-202 v1')
        self.page('SRC-0002','DOC-202',external='no')
        report=self.crawl(profile=PROFILES['external'])
        self.assertEqual([s['id'] for s in report['sources']],['SRC-0001'])
        self.assertEqual(report['relations'][0]['status'],'target_unavailable')
        self.assertNotIn('SRC-0002',json.dumps(report))

    def test_real_original_replay_preserves_all_source_pins(self):
        from tools.evaluate_historical_experts import evaluate
        report=evaluate()
        self.assertTrue(report['summary']['expected_originals_reached'])
        self.assertEqual(report['summary']['expert_stages_passed'],3)
        self.assertTrue(report['summary']['negative_supersession_qualification_preserved'])
        self.assertFalse(report['summary']['answer_supported'])

    def test_changed_source_during_expert_run_discards_old_text(self):
        rec=self.page('SRC-0001','DOC-101','DOC-202 v1')
        from mplpb_work.historical_evidence import extract
        changed=[False]
        def mutate(body,*args,**kwargs):
            result=extract(body,*args,**kwargs)
            if not changed[0]:
                changed[0]=True
                path=self.root/rec.path
                path.write_text(path.read_text().replace('DOC-202','SECRET-CHANGED'))
            return result
        with patch('mplpb_work.investigation.documentary.extract',side_effect=mutate):
            report=self.crawl()
        self.assertEqual(report['status'],'needs_recheck')
        self.assertEqual(report['observations'],[])
        self.assertEqual(report['sources'],[])
        self.assertNotIn('DOC-202',json.dumps(report))
        self.assertNotIn('SECRET-CHANGED',json.dumps(report))

    def test_persistent_work_is_recoverable_and_cli_is_explicit(self):
        self.page('SRC-0001','DOC-101')
        directory=Path(self.tmp.name)/'work'
        result=self.crawl(work_directory=directory)
        self.assertTrue(result['work_retained'])
        from mplpb_work import WorkStore
        token=json.loads((directory/'host-credential.json').read_text())['authority_credential']
        audit=WorkStore(directory).audit(token)
        records=[e['payload']['record'] for e in audit['events'] if e['type']=='put']
        completed=[r for r in records if r['kind']=='task' and r['payload']['state']=='done']
        self.assertEqual(len(completed),1)
        source_pins=[r for r in records if r['kind']=='evidence']
        self.assertEqual(len(source_pins),1)
        from mplpb_answers.__main__ import main
        stream=io.StringIO()
        with contextlib.redirect_stdout(stream):
            code=main(['investigate',str(self.root),'archival records','--source','SRC-0001'])
        self.assertEqual(code,0)
        self.assertFalse(json.loads(stream.getvalue())['answer_supported'])
        with self.assertRaises(FileExistsError):self.crawl(work_directory=directory)

    def test_source_change_during_task_completion_discards_old_findings(self):
        self.page('SRC-0001','DOC-101','DOC-202 v1')
        from mplpb_work.store import WorkStore
        original=WorkStore.put
        def change_after_completion(store,*args,**kwargs):
            result=original(store,*args,**kwargs)
            if kwargs.get('kind')=='task' and kwargs['payload']['state']=='done':
                self.page('SRC-0002','DOC-202')
            return result
        with patch.object(WorkStore,'put',new=change_after_completion):
            report=self.crawl(adaptive_search=True)
        self.assertEqual(report['status'],'needs_recheck')
        self.assertEqual(report['observations'],[])
        self.assertEqual(report['relations'],[])
        self.assertNotIn('adaptive_search',report)
        self.assertNotIn('DOC-202',json.dumps(report))


if __name__=='__main__':unittest.main()
