"""Positive/negative mapping controls plus a real public-original fresh-process workflow."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from mplpb_combined.ledger import write,revise,withdraw
from mplpb_work.prose_evidence import discover
from mplpb_work.source_mapping import reconstruct,digest
from tools.source_roundtrip import projection_offsets,original_passage
from tools.unprepared_sources import import_corpus,sha,save

ROOT=Path(__file__).resolve().parents[1]


class SourceMappingTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.ledger=self.root/'ledger';self.ledger.mkdir()
        self.question='archive letter earlier conclusion reconsidered'

    def pages(self):
        write(self.ledger,doc_id='LETTER-1',title='Fictional earlier note',scope='archive',
              body='Mira wrote an earlier letter about the archive conclusion. It might be mistaken.')
        return write(self.ledger,doc_id='LETTER-2',title='Fictional response',scope='archive',
              body='Mira reconsidered her earlier conclusion in the archive letter. She did not retract every statement.')

    def test_correction_search_is_reversible_but_does_not_resolve_predecessor(self):
        self.pages();report=discover(self.ledger,self.question)['information_map']
        corrections=[m for m in report['mappings'] if m['kind']=='correction_or_correspondence_candidate']
        self.assertTrue(corrections);self.assertTrue(report['relationships'])
        for m in corrections+report['relationships']:
            r=reconstruct(self.ledger,self.question,m)
            self.assertTrue(r['quote_fidelity']);self.assertFalse(r['semantic_relationship_verified']);self.assertFalse(r['answer_supported'])
            self.assertFalse(m['content_truth_verified'])
        self.assertTrue(all(m['predecessor'] is None for m in corrections))
        self.assertTrue(any('not retract every statement' in p['quote'] for m in corrections for p in m['evidence']))
        self.assertTrue(any('not' in m['qualification_cues'] for m in corrections))

    def test_absent_antecedent_remains_unresolved(self):
        write(self.ledger,doc_id='LETTER-1',title='Fictional',scope='archive',body='I reconsidered my earlier conclusion about the archive.')
        report=discover(self.ledger,self.question)['information_map']
        self.assertTrue(any(m['kind']=='correction_or_correspondence_candidate' for m in report['mappings']))
        self.assertFalse(report['relationships']);self.assertFalse(report['answer_supported'])

    def test_forgery_negative_coordinates_and_changed_query_rejected(self):
        self.pages();m=discover(self.ledger,self.question)['information_map']['mappings'][0]
        bad=copy.deepcopy(m);bad['evidence'][0]['quote']='A fabricated relationship.'
        self.assertFalse(reconstruct(self.ledger,self.question,bad)['quote_fidelity'])
        bad.pop('mapping_id');bad['mapping_id']=digest(bad)
        self.assertFalse(reconstruct(self.ledger,self.question,bad)['quote_fidelity'])
        bad=copy.deepcopy(m);bad['evidence'][0]['body_start']=-1;bad.pop('mapping_id');bad['mapping_id']=digest(bad)
        self.assertFalse(reconstruct(self.ledger,self.question,bad)['quote_fidelity'])
        self.assertFalse(reconstruct(self.ledger,'salary archive',m)['quote_fidelity'])
        self.assertFalse(reconstruct(self.ledger,self.question,m,'external')['quote_fidelity'])

    def test_revision_withdrawal_and_corruption_invalidate_cached_mapping(self):
        rec=self.pages();m=discover(self.ledger,self.question)['information_map']['mappings'][0]
        revise(self.ledger,rec.id,body='The archive letter conclusion has changed.')
        self.assertFalse(reconstruct(self.ledger,self.question,m)['quote_fidelity'])
        fresh=discover(self.ledger,self.question)['information_map']['mappings'][0]
        withdraw(self.ledger,'LETTER-1')
        self.assertFalse(reconstruct(self.ledger,self.question,fresh)['quote_fidelity'])

    def test_projection_keeps_negation_dates_unicode_and_raw_layout(self):
        raw='  On October 3, 1859, Mira did\t not retract café.\r\n\r\nPerhaps later.  '
        text,starts,ends=projection_offsets(raw,False)
        self.assertEqual(text,'On October 3, 1859, Mira did not retract café.\nPerhaps later.')
        self.assertEqual(raw[starts[0]:ends[-1]],raw.strip())
        text,_,_=projection_offsets('<h1>Metadata</h1><p>Not &amp; never &#233;.</p><script>bad</script>',True)
        self.assertEqual(text,'Not & never é.')

    def test_fresh_process_public_page_import_mapping_and_raw_roundtrip(self):
        # Authentic 1861 public-domain telegram/publisher framing, not authored
        # around the mapping grammar. No answer-bearing fields are added.
        corpus=self.root/'corpus';corpus.mkdir()
        original=ROOT/'evaluation/unprepared-originals/2026-11-16/originals/sumter-telegram.html'
        if not original.exists():self.fail('Public original required in source checkout')
        raw=original.read_bytes();(corpus/'original.html').write_bytes(raw)
        save(corpus/'corpus-manifest.json',{'schema':'unprepared-public-corpus-v1','sources':[
            {'id':'SUMTER','path':'original.html','sha256':sha(raw),'bytes':len(raw),'encoding':'utf-8','media_type':'text/html',
             'url':'https://www.archives.gov/milestone-documents/telegram-announcing-the-surrender-of-fort-sumter',
             'rights_basis':'1861 public-domain government record and NARA government-produced framing'}],'provenance_files':[]})
        self.ledger.rmdir();receipt=import_corpus(corpus,self.ledger)
        report=self.root/'report.json';query='Sumter telegram surrender April Anderson'
        subprocess.run([sys.executable,'-m','tools.reconstruct_original','map','--ledger',str(self.ledger),
                        '--question',query,'--output',str(report)],cwd=ROOT,check=True,capture_output=True,timeout=30)
        data=json.loads(report.read_text());maps=data['candidate_analysis']['information_map']['mappings']
        self.assertTrue(maps);self.assertFalse(data['candidate_analysis']['answer_supported'])
        mapping=next(m for m in maps if 'Anderson' in m['evidence'][0]['quote'])
        out=self.root/'reconstructed.json'
        subprocess.run([sys.executable,'-m','tools.reconstruct_original','reconstruct','--ledger',str(self.ledger),
            '--report',str(report),'--mapping-id',mapping['mapping_id'],'--corpus',str(corpus),
            '--import-receipt',str(self.ledger/'import-receipt.json'),'--output',str(out)],cwd=ROOT,check=True,capture_output=True,timeout=30)
        result=json.loads(out.read_text());self.assertTrue(result['quote_fidelity'])
        for p in result['original_passages']:
            self.assertEqual(raw[p['original_byte_start']:p['original_byte_end']].decode(),p['raw_excerpt'])
            self.assertEqual(p['original_sha256'],sha(raw));self.assertFalse(p['semantic_relationship_verified'])
        path=self.ledger/receipt['records'][0]['path'];path.write_text(path.read_text().replace('Anderson','Tampered'))
        self.assertFalse(reconstruct(self.ledger,query,mapping)['quote_fidelity'])
        (corpus/'original.html').write_bytes(raw+b'changed')
        with self.assertRaises(ValueError):original_passage(corpus,receipt,mapping['evidence'][0])


if __name__=='__main__':unittest.main()
