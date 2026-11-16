"""Protocol/authority controls on explicitly fictional fixtures; no human review."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import unprepared_sources as sources
from tools import unprepared_challenge as challenge
from tools import randomized_original_controls as synthetic


class OriginalChallengeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.package=self.root/'package';self.package.mkdir()
        raw=b'The fixture kettle color is blue.\n'
        (self.package/'original.txt').write_bytes(raw)
        sources.save(self.package/'corpus-manifest.json',{'schema':'unprepared-public-corpus-v1','sources':[
            {'id':'FIXTURE','url':'https://www.archives.gov/fictional-test-only','path':'original.txt',
             'sha256':sources.sha(raw),'bytes':len(raw),'encoding':'utf-8','media_type':'text/plain','rights_basis':'Explicit fictional unit fixture'}], 'provenance_files':[]})
        for name,value in [('questions.json',{'cases':[{'id':'Q1','question':'What is the fixture kettle color?'}]}),
            ('reference-draft.json',{'cases':[{'id':'Q1','citations':[]}]}),('protocol.json',{'purpose':'fictional unit controls'}),
            ('baseline-inventory.json',{'git_commit':'fixture-test-not-a-research-revision'})]:sources.save(self.package/name,value)

    def test_import_preserves_raw_bytes_and_adds_no_answer_fields(self):
        raw=(self.package/'original.txt').read_bytes()
        receipt=sources.import_corpus(self.package,self.root/'ledger')
        self.assertEqual((self.package/'original.txt').read_bytes(),raw)
        self.assertFalse(receipt['records'][0]['answer_fields_added'])
        self.assertEqual(receipt['records'][0]['wrapper_fields_added']['origin'],'machine')
        self.assertNotIn('event-id',receipt['records'][0]['wrapper_fields_added'])
        self.assertEqual(receipt['records'][0]['wrapper_fields_added']['scope'],'public historical records')

    def test_source_alteration_and_path_escape_are_rejected(self):
        (self.package/'original.txt').write_text('Changed')
        with self.assertRaises(ValueError):sources.verify(self.package)
        with self.assertRaises(ValueError):sources.inside(self.package,'../outside')

    def test_frozen_question_and_rule_changes_are_rejected(self):
        challenge.freeze(self.package)
        (self.package/'questions.json').write_text('{"cases":[]}')
        with self.assertRaises(ValueError):challenge.frozen(self.package)
        with self.assertRaises(FileExistsError):challenge.freeze(self.package)

    def test_duplicate_runtime_ids_and_reference_coverage_rejected(self):
        (self.package/'questions.json').write_text(json.dumps({'cases':[{'id':'Q1','question':'x'},{'id':'Q1','question':'y'}]}))
        with self.assertRaises(ValueError):challenge.freeze(self.package)

    def test_synthetic_separation_and_private_seed(self):
        target=self.root/'synthetic';private=self.root/'private'
        synthetic.prepare(target,private,n=2)
        manifest=sources.verify(target)
        self.assertEqual(manifest['schema'],'synthetic-control-corpus-v1')
        self.assertFalse(manifest['independent_human_blinding'])
        self.assertFalse((target/'seed.json').exists());self.assertTrue((private/'seed.json').exists())
        with self.assertRaises(ValueError):sources.acquire(target,self.root/'invalid-acquisition')
        self.assertEqual((private/'seed.json').stat().st_mode&0o777,0o600)

    def test_projection_quote_coverage_never_counts_other_sources(self):
        ref={'source_id':'A','start':10,'end':20}
        self.assertTrue(challenge.covers({'source_id':'A','body_start':5,'text':'x'*20},ref))
        self.assertFalse(challenge.covers({'source_id':'B','body_start':5,'text':'x'*20},ref))
        self.assertFalse(challenge.covers({'source_id':'A','body_start':11,'text':'x'*20},ref))

    def fixture_run(self,arm='baseline'):
        if not (self.package/'freeze.json').exists():challenge.freeze(self.package)
        run=self.root/arm;run.mkdir()
        imported=sources.import_corpus(self.package,self.root/('ledger-'+arm));sources.save(run/'import-receipt.json',imported)
        row={'case_id':'Q1','question':'What is the fixture kettle color?','execution_status':'completed','arm':arm,
             'answer':{'kind':'abstain','answer_supported':False,'claims':[]},'investigation':{},'measurements':None}
        sources.save(run/'Q1.json',row)
        seal=challenge.read(self.package/'freeze.json')
        receipt={'arm':arm,'corpus_namespace':'unprepared-public-corpus-v1','freeze_sha256':sources.sha((self.package/'freeze.json').read_bytes()),
            'protocol_sha256':seal['files']['protocol.json'],'corpus_sha256':seal['files']['corpus-manifest.json'],
            'questions_sha256':seal['files']['questions.json'],'import_receipt_sha256':sources.sha((run/'import-receipt.json').read_bytes()),
            'cases':[{'id':'Q1','sha256':sources.sha((run/'Q1.json').read_bytes()),'status':'completed'}]}
        sources.save(run/'run-receipt.json',receipt);return run

    def test_absent_humans_leave_semantic_metrics_unknown_not_zero(self):
        run=self.fixture_run();result=challenge.summary(self.package,run)
        self.assertIsNone(result['event_recall']);self.assertIsNone(result['false_positive_relationship_rate'])
        self.assertEqual(result['rows'][0]['semantic_outcome'],'unassessed')
        self.assertEqual(result['independent_human_evaluation'],'NOT RUN')

    def test_changed_run_outputs_cannot_be_compared(self):
        run=self.fixture_run();(run/'Q1.json').write_text('{}')
        with self.assertRaises(ValueError):challenge.summary(self.package,run)

    def test_corpus_mixing_is_rejected(self):
        a=self.fixture_run();b=self.fixture_run('updated')
        receipt=challenge.read(b/'run-receipt.json');receipt['corpus_namespace']='synthetic-control-corpus-v1'
        (b/'run-receipt.json').write_text(json.dumps(receipt))
        with self.assertRaises(ValueError):challenge.compare(self.package,[a,b])

    def packet_reviews(self):
        run=self.fixture_run();packets=self.root/'packets';template=challenge.packets(self.package,[run],packets)
        imported=challenge.read(run/'import-receipt.json')['records'][0]
        paths=[]
        for i in range(2):
            review=copy.deepcopy(template);review.update(reviewer_id='fictional-unit-fixture-'+str(i),reviewer_is_human=True,
                independence_attestation='TEST FIXTURE ONLY: no real participant, not research evidence')
            item=review['items'][0];item.update(outcome='unsuccessful',reference_scope='fictional fixture only',reference_complete_within_scope=True,
                chronological_errors=0,appropriate_refusal=False,unsupported_answer=False,rationale='Fixture misses a supported color statement')
            item['judgments']={k:'incorrect' if k=='completeness' else 'not_applicable' for k in challenge.DIMENSIONS}
            for kind in ('event','relationship','correction'):item[kind]={'tp':0,'fp':0,'fn':0}
            item['relationship']['negative_opportunities']=1
            item['citations']=[{'source_id':imported['id'],'source_hash':imported['hash'],'start':0,'end':len('The fixture kettle color is blue.'),'quote':'The fixture kettle color is blue.'}]
            path=self.root/('review'+str(i)+'.json');sources.save(path,review);paths.append(path)
        return packets,paths

    def test_blank_review_packets_cannot_be_scored_as_success(self):
        packets,paths=self.packet_reviews()
        blank=packets/'review-template.json'
        with self.assertRaises(ValueError):challenge.score_reviews(packets,[blank,blank])

    def test_disagreement_retained_and_agreement_does_not_authenticate_people(self):
        packets,paths=self.packet_reviews();result=challenge.score_reviews(packets,paths)
        self.assertFalse(result['independence_verified']);self.assertIsNone(result['reported_human_times']['review_seconds']['total_seconds'])
        review=challenge.read(paths[1]);review['items'][0]['chronological_errors']=1;paths[1].write_text(json.dumps(review))
        result=challenge.score_reviews(packets,paths);self.assertEqual(result['status'],'adjudication_required')
        self.assertEqual(result['disagreements'],[['baseline','Q1']])

    def test_fabricated_citations_and_contradictory_success_rejected(self):
        packets,paths=self.packet_reviews();review=challenge.read(paths[0]);review['items'][0]['citations'][0]['quote']='fabricated'
        paths[0].write_text(json.dumps(review))
        with self.assertRaises(ValueError):challenge.score_reviews(packets,paths)
        review['items'][0]['outcome']='successful';paths[0].write_text(json.dumps(review))
        with self.assertRaises(ValueError):challenge.score_reviews(packets,paths)


if __name__=='__main__':unittest.main()
