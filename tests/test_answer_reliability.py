import contextlib, io, json, tempfile, unittest
from pathlib import Path
from mplpb_combined import reader as R
from mplpb_combined.ledger import write
from mplpb_answers.frames import parse
from mplpb_answers.support import supported_answer
from mplpb_answers.__main__ import main

class ReliabilityTests(unittest.TestCase):
    def test_development_pairs(self):
        spec=json.loads(Path('evaluation/reliability/development-cases.json').read_text())
        for c in spec['cases']:
            with self.subTest(c['id']), tempfile.TemporaryDirectory() as root:
                for doc in c['documents']:write(root,**doc)
                a=supported_answer(root,c['question'])
                self.assertEqual(a.kind,c['expected'])
                if c['value']:self.assertIn(c['value'],a.text.casefold())
                if a.kind!='return':self.assertEqual((a.text,a.citation()),('',''))

    def test_cli_supported_default_and_explicit_candidates(self):
        with tempfile.TemporaryDirectory() as root:
            write(root,doc_id='T-0001',title='Aster',scope='Aster service port',body='The Other service port is 8123.')
            for mode,code,kind in [('ask',3,'not_in_corpus'),('candidates',0,'return')]:
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(main([mode,root,'What is the Aster service port?','--json']),code)
                data=json.loads(output.getvalue());self.assertEqual(data['kind'],kind)
                if mode=='candidates':self.assertFalse(data['answer_supported'])
            self.assertEqual(R.answer(root,'What is the Aster service port?').kind,'return')

    def test_shared_frame_and_preserved_constraints(self):
        forms=['When','In what year','In which year']
        frames=[parse(x+' did the Zephyr workshop open?') for x in forms]
        self.assertEqual(frames,[frames[0]]*3)
        for q in ['When did the Zephyr workshop not open?','When did the Zephyr workshop open after 1997?',
                  'In which year did the Zephyr workshop possibly open?']:
            self.assertIsNone(parse(q))

    def test_scope_specificity_cannot_hide_conflicting_evidence(self):
        with tempfile.TemporaryDirectory() as root:
            write(root,doc_id='T-0001',title='Aster',scope='Aster service port',body='The Aster service port is 8123.')
            write(root,doc_id='T-0002',title='Aster',scope='Aster',body='The Aster service port is 9123.')
            self.assertEqual(R.answer(root,'What is the Aster service port?').kind,'return')
            self.assertEqual(supported_answer(root,'What is the Aster service port?').kind,'ambiguous')

    def test_eligible_body_can_answer_without_scope_majority(self):
        with tempfile.TemporaryDirectory() as root:
            write(root,doc_id='T-0001',title='History',scope='history',body='The Zephyr workshop opened in 1997.')
            self.assertEqual(supported_answer(root,'In what year did the Zephyr workshop open?').kind,'return')
            self.assertEqual(supported_answer(root,'In what year did the Zephyr workshop open?',R.PROFILES['external']).kind,'not_in_corpus')

    def test_tampered_body_cannot_answer(self):
        with tempfile.TemporaryDirectory() as root:
            write(root,doc_id='T-0001',title='Aster',scope='Aster service port',body='The Aster service port is 8123.')
            p=next(Path(root).glob('t-*.html'));p.write_text(p.read_text().replace('8123','9123'))
            self.assertEqual(supported_answer(root,'What is the Aster service port?').kind,'not_in_corpus')

    def test_desktop_browser_query_contract_and_reload(self):
        import asyncio
        from unittest.mock import patch
        from tools.ledger_ui import App
        from browser import bridge as B
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'corpus';root.mkdir()
            write(root,doc_id='T-0001',title='Aster',scope='Aster service port',body='The Other service port is 8123.')
            app=App(custom=root,topic_base=Path(temp)/'topics')
            data={'corpus':'custom','question':'What is the Aster service port?'}
            desktop=app.query(data)
            with patch.object(B,'app',app):browser=asyncio.run(B.dispatch('/api/query',data))
            self.assertEqual(browser,desktop)
            self.assertEqual(desktop['reader']['kind'],'not_in_corpus')
            inspected=app.query(dict(data,mode='candidates'))
            self.assertEqual(inspected['reader']['kind'],'candidate_only')
            self.assertIn('Other',app.page('custom','t-0001.html','internal')['text'])
            turn=app.chat({'corpus':'custom','message':'My name is Reliability Tester','auto_wiki':False})
            reloaded=App(custom=root,topic_base=Path(temp)/'topics')
            resumed=reloaded.resume_chat({'session':turn['session']})
            self.assertTrue(resumed['chain_intact'])
