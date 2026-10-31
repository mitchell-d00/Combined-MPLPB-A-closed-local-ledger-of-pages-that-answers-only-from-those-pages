"""Actual loopback HTTP protocol fixtures; no installed model or accuracy claim."""
import copy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
import unittest
from mplpb_answers.local_reader import OllamaLocalReader
from mplpb_answers.evidence_contract import ReaderError, loads


class LocalReaderTests(unittest.TestCase):
    def setUp(self):
        self.requests=[]; self.mode='ok'
        owner=self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args): pass
            def send(self,value,status=200):
                body=value if isinstance(value,bytes) else json.dumps(value).encode()
                self.send_response(status); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
            def do_GET(self):
                owner.requests.append(('GET',self.path))
                if owner.mode=='redirect': return self.send({},302)
                if owner.mode=='oversized': return self.send(b' '*1000001)
                metadata={'name':'fixture:latest','digest':'a'*64,'size':1000,'details':{'format':'gguf'}}
                if owner.mode=='cloud': metadata['remote_host']='https://remote.invalid'
                if owner.mode=='changed': metadata['digest']='b'*64
                return self.send({'models':[metadata]})
            def do_POST(self):
                data=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                owner.requests.append(('POST',self.path,data))
                if owner.mode=='redirect': return self.send({},302)
                if owner.mode=='tool': return self.send({'done':True,'message':{'content':'{}','tool_calls':[{}]}})
                if owner.mode=='truncated': return self.send({'done':True,'done_reason':'length','message':{'content':'{}'}})
                if owner.mode=='pipeline':
                    payload=json.loads(data['messages'][1]['content']); task=payload['task']; request=payload['data']
                    if task=='plan': out={'question':request['question'],'queries':[]}
                    elif task=='read':
                        passage=request['passages'][0]
                        out={'question':request['question'],'outcome':'answer','claims':[{'text':passage['text'],'qualifiers':[],'citations':[{'passage':passage['id'],'quote':passage['text']}]}],'missing':[],'clarification':'','confidence':0.9}
                    else: out={'question':request['question'],'verdict':'accept','checks':[{'claim':0,'supported':True,'subject_matches':True,'relation_matches':True,'constraints_preserved':True,'reason':'Specified protocol fixture'}],'complete':True,'missing':[],'confidence':0.9}
                    return self.send({'done':True,'done_reason':'stop','message':{'content':json.dumps(out)}})
                return self.send({'done':True,'done_reason':'stop','message':{'content':'{"value":"fixture"}','thinking':'PRIVATE-REASONING-NEVER-RETURN'}})
        self.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True); self.thread.start()
        self.addCleanup(self.server.server_close); self.addCleanup(self.server.shutdown)
        self.endpoint='http://127.0.0.1:'+str(self.server.server_port)

    def reader(self): return OllamaLocalReader('fixture',self.endpoint,model_digest='a'*64)

    def test_no_calls_at_construction_and_explicit_pinned_metadata(self):
        reader=self.reader(); self.assertEqual(self.requests,[])
        identity=reader.describe()
        self.assertEqual(identity['reader']['digest'],'sha256:'+'a'*64)
        self.assertFalse(identity['independence_verified'])
        output=reader.complete('read',{'question':'Example?'},{'type':'object'})
        self.assertEqual(output,{'value':'fixture'})
        request=self.requests[-1][2]
        self.assertFalse(request['stream']); self.assertFalse(request['think'])
        self.assertNotIn('tools',request)
        self.assertNotIn('PRIVATE-REASONING',json.dumps(output))

    def test_loopback_only_no_dns_paths_credentials_or_cloud_aliases(self):
        for endpoint in ('https://127.0.0.1:11434','http://localhost:11434','http://example.com:11434',
                         'http://192.168.1.1:11434','http://user:pass@127.0.0.1:11434','http://127.0.0.1/api/chat','http://127.0.0.1?x=1'):
            with self.subTest(endpoint=endpoint), self.assertRaises(ValueError):
                OllamaLocalReader('fixture',endpoint)
        with self.assertRaises(ValueError): OllamaLocalReader('fixture:cloud',self.endpoint)
        with self.assertRaises(ValueError): OllamaLocalReader('fixture-cloud',self.endpoint)
        self.assertEqual(self.requests,[])

    def test_redirect_remote_model_and_changed_digest_fail_before_source_request(self):
        for mode in ('redirect','cloud','changed','oversized'):
            self.mode=mode
            with self.subTest(mode=mode), self.assertRaises(ReaderError): self.reader().describe()
        self.assertTrue(all(r[0]=='GET' for r in self.requests))

    def test_truncated_or_tool_output_is_rejected(self):
        for mode in ('tool','truncated','redirect'):
            self.mode=mode
            with self.subTest(mode=mode), self.assertRaises(ReaderError):
                self.reader().complete('read',{'question':'Example?'},{'type':'object'})

    def test_duplicate_json_fields_and_nan_are_rejected(self):
        for value in ('{"a":1,"a":2}','{"a":NaN}','{"a":Infinity}'):
            with self.assertRaises(ReaderError): loads(value)

    def test_actual_adapter_is_wired_through_the_whole_query_pipeline(self):
        import tempfile
        from mplpb_combined.ledger import write
        from mplpb_answers.pipeline import answer_query
        self.mode='pipeline'
        with tempfile.TemporaryDirectory() as root:
            write(root,doc_id='T-0001',title='Operating notes',scope='operations',body='Drain the queue before restarting the worker.')
            result=answer_query(root,'How should an operator restart safely?',mode='assisted',reader=self.reader()).contract
            self.assertEqual(result['kind'],'model_assisted_answer')
            self.assertFalse(result['answer_supported'])
            self.assertEqual(result['claims'][0]['citations'][0]['quote'],'Drain the queue before restarting the worker.')
            self.assertEqual(len([r for r in self.requests if r[0]=='POST']),3)

    def test_same_model_cannot_silently_override_a_required_digest(self):
        with self.assertRaises(ValueError):
            OllamaLocalReader('fixture',self.endpoint,model_digest='a'*64,reviewer_digest='b'*64)
        self.assertEqual(self.requests,[])
