"""D% reproducibility,structural challenge and scoring separation controls."""
import json
from pathlib import Path
import tempfile
import unittest
from tools import dpercent as d


class DPercentTests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)

    def prepare(self,name='a',count=60,seed=47):
        public=self.root/name;private=self.root/(name+'-private');d.prepare(public,private,count=count,seed=seed)
        return public,private

    def test_seed_replays_bytes_key_and_dice(self):
        a,ka=self.prepare();b,kb=self.prepare('b')
        self.assertEqual(d.files(a),d.files(b));self.assertEqual(d.files(ka),d.files(kb))
        self.assertEqual(d.verify(a,ka),d.verify(b,kb))
        c,kc=self.prepare('c',seed=48);self.assertNotEqual(d.files(a),d.files(c))

    def test_all_families_have_binary_expectation_and_real_scope_variants(self):
        public,private=self.prepare(count=120)
        keys=d.read(private/'key.json')['cases'];self.assertEqual({k['family'] for k in keys},set(d.FAMILIES))
        self.assertEqual({k['expected'] for k in keys},{'answer','refuse'})
        texts='\n'.join(p.read_text() for p in (public/'packets').rglob('*') if p.is_file())
        normalized=' '.join(texts.casefold().split())
        for term in ('did not','if the permit','claimed that','count should read','```text','before the'):
            self.assertTrue(term in normalized, 'Missing structural cue: '+term)
        self.assertTrue(any(term in normalized for term in ('planned to','hoped to','asked')))
        self.assertGreater(d.STRUCTURAL_COMBINATIONS,1000)
        for path in (public/'packets').glob('*/case.json'):
            case=d.read(path);self.assertNotIn('expected',case);self.assertNotIn('family',case)
            for source in case['sources']:
                raw=(path.parent/source['path']).read_text()
                self.assertNotIn('Event-ID:',raw);self.assertNotIn('Corrects:',raw);self.assertNotIn('answer_supported',raw)
        self.assertFalse(list((public/'packets').rglob('key.json')))

    def test_wrapped_crlf_unicode_and_repeated_headers_are_not_filtered(self):
        public,private=self.prepare(count=180)
        raw=[p.read_bytes() for p in (public/'packets').rglob('*') if p.is_file() and p.name!='case.json']
        self.assertTrue(any(b'\r\n' in text for text in raw));self.assertTrue(any('Marén'.encode() in text for text in raw))
        keys=d.read(private/'key.json')['cases'];case=next(k for k in keys if k['family']=='wording_change')
        sources=d.read(public/'packets'/case['id']/'case.json')['sources'];a,b=[(public/'packets'/case['id']/s['path']).read_text() for s in sources[:2]]
        self.assertEqual(a.split('\n\n')[0],b.split('\n\n')[0]);self.assertNotEqual(a,b)

    def test_frozen_sources_and_key_mutations_fail(self):
        public,private=self.prepare(count=3)
        source=next((public/'packets').rglob('record-*'));source.write_bytes(source.read_bytes()+b' changed')
        with self.assertRaises(ValueError):d.verify(public,private)
        p,k=self.prepare('b',count=3);(k/'key.json').write_text('{}')
        with self.assertRaises(ValueError):d.verify(p,k)

    def synthetic_result(self,expected,supported,match=True,quote_valid=True):
        packet=self.root/'pack';packet.mkdir();private=self.root/'private';private.mkdir();output=self.root/'run';output.mkdir()
        source='Mira Vale wrote the alder memorandum.';sid='SOURCE-0001';prop={'relation':'source_action_assertion','actor_text':'Mira Vale','action':'write','object_text':'the alder memorandum','negative':False}
        if not match:prop['actor_text']='Ivo Hart'
        q={'id':'DP00001','family':'direct_action','expected':expected,'required_propositions':[{'actor_text':'Mira Vale','action':'write','negative':False}],
           'reference_sources':[sid],'automatic_answer_matcher':'typed_proposition_v1'}
        d.save(private/'key.json',{'cases':[q]});d.save(private/'dice.json',{})
        d.save(packet/'seal.json',{'public_files':{},'key_sha256':d.sha((private/'key.json').read_bytes()),'dice_sha256':d.sha((private/'dice.json').read_bytes())})
        r={'answer':{'kind':'supported_answer' if supported else 'abstain','answer_supported':supported,'claims':[{'source_support_established':True,'proposition':prop,'citations':[{'source_id':sid,'hash':'hash','body_start':0,'body_end':len(source),'quote':source if quote_valid else 'forged'}]}] if supported else []},
           'source_receipts':[{'source_id':sid,'hash':'hash','canonical_body':source}],'retrieval':{}}
        folder=output/q['id'];folder.mkdir();d.save(folder/'result.json',r)
        d.save(output/'run.json',{'packet_seal_sha256':d.sha((packet/'seal.json').read_bytes()),'cases':[{'case_id':q['id'],'execution':'completed','sha256':d.sha((folder/'result.json').read_bytes())}]})
        return d.score(packet,private,output,self.root/'score.json')

    def test_detection_requires_proposition_and_exact_quote_not_just_flag(self):
        r=self.synthetic_result('answer',True,match=False);self.assertEqual(r['metrics']['E'],0)
        self.assertEqual(r['metrics']['E_output'],1)

    def test_fabricated_quote_does_not_score_as_detected_answer(self):
        r=self.synthetic_result('answer',True,quote_valid=False);self.assertEqual(r['metrics']['E'],0)

    def test_false_alarm_counts_supported_output_on_refuse(self):
        r=self.synthetic_result('refuse',True);self.assertEqual(r['metrics']['F'],1)

    def test_correct_refusal_does_not_raise_detection(self):
        r=self.synthetic_result('answer',False);self.assertEqual(r['metrics']['E'],0)
        self.assertEqual(r['metrics']['over_refusals'],1)

    def test_correct_complete_answer_is_counted(self):
        r=self.synthetic_result('answer',True);self.assertEqual(r['metrics']['E'],1)

    def test_unrun_and_failed_cases_do_not_become_successful_refusals(self):
        r=self.synthetic_result('refuse',False)
        path=self.root/'run/run.json';run=d.read(path);run['cases'][0]['execution']='failed';path.write_text(json.dumps(run))
        scored=d.score(self.root/'pack',self.root/'private',self.root/'run',self.root/'failed-score.json')
        self.assertIsNone(scored['metrics']['F']);self.assertEqual(scored['metrics']['execution_failures'],1)

    def test_bad_bounds_and_private_path_overlap_are_rejected(self):
        for count in (0,4097,True):
            with self.assertRaises(ValueError):d.prepare(self.root/'out',self.root/'secret',count=count)
        with self.assertRaises(ValueError):d.prepare(self.root/'same',self.root/'same')

    def test_dice_records_all_choices_without_language_filtering(self):
        dice=d.Dice(991)
        values=[dice.choose('wide',tuple(range(173))) for _ in range(1000)]
        self.assertGreater(len(set(values)),160)
        self.assertTrue(all(1<=n<=100 for roll in dice.rolls for n in roll['rolls']))
        self.assertTrue(any(not roll['accepted'] for roll in dice.rolls))

    def test_context_needed_for_positive_labels_is_present_in_source(self):
        for seed in range(30):
            case,sources,key=d.case_material(1,'instruction_statement',d.Dice(seed))
            raw=sources[0][1].decode();self.assertIn('From: ',raw);self.assertIn('To: ',raw)
            self.assertIn('Date written: ',raw)
            case,sources,key=d.case_material(1,'partial_correction',d.Dice(seed))
            first=' '.join(sources[0][1].decode().split());second=' '.join(sources[1][1].decode().split())
            date=first.split('This letter was written on ')[1].split('. ')[0]
            self.assertIn('In my letter of '+date,second)

    def test_non_boolean_support_flag_is_not_a_successful_refusal(self):
        self.synthetic_result('refuse',False)
        path=self.root/'run/DP00001/result.json';result=d.read(path)
        result['answer']['answer_supported']='false';path.write_text(json.dumps(result))
        runpath=self.root/'run/run.json';run=d.read(runpath);run['cases'][0]['sha256']=d.sha(path.read_bytes());runpath.write_text(json.dumps(run))
        report=d.score(self.root/'pack',self.root/'private',self.root/'run',self.root/'invalid-score.json')
        self.assertIsNone(report['metrics']['F']);self.assertEqual(report['metrics']['execution_failures'],1)

    def test_missing_citations_cannot_establish_detection(self):
        self.synthetic_result('answer',True)
        path=self.root/'run/DP00001/result.json';result=d.read(path)
        result['answer']['claims'][0]['citations']=[];path.write_text(json.dumps(result))
        runpath=self.root/'run/run.json';run=d.read(runpath);run['cases'][0]['sha256']=d.sha(path.read_bytes());runpath.write_text(json.dumps(run))
        report=d.score(self.root/'pack',self.root/'private',self.root/'run',self.root/'no-cite-score.json')
        self.assertEqual(report['metrics']['E'],0)


if __name__=='__main__':unittest.main()
