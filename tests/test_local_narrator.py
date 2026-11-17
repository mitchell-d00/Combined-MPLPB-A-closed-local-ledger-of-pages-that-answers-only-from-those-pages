"""Authored narrator boundary and local HTTP fixtures, not model accuracy tests."""
import contextlib
import html
import io
import json
import os
from pathlib import Path
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import unittest
from unittest.mock import patch

from mplpb_answers.__main__ import main
from mplpb_answers.evidence_contract import ReaderError
from mplpb_answers.local_narrator import (LocalBackend, NarratorConfig, allowed_renderings,
                                          narrate, validate_reply)
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import write, withdraw
from mplpb_combined.reader import PROFILES


QUESTION = 'What is Owner for record CASE-1?'


class NarratorTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def page(self, ident='SRC-1', owner_name='Alice', **kw):
        return write(self.root, doc_id=ident, title='Archive', scope='record owner CASE-1',
                     body_html='<pre>Record-ID: CASE-1\nOwner: '+html.escape(owner_name)+'\nUnrelated assertion: secret</pre>', **kw)

    def test_refusal_cannot_be_overridden_and_never_calls_model(self):
        self.page()
        with patch.object(LocalBackend, 'generate', return_value='Everything happened.') as model:
            result = narrate('Did Alice execute the delivery?', self.root)
        model.assert_not_called()
        strict = answer_query(self.root, 'Did Alice execute the delivery?').contract
        self.assertFalse(result.answer_supported)
        self.assertEqual(result.text, strict['text'] or strict['diagnostic']['message'])
        self.assertEqual(result.ledger_result, strict)

    def test_zero_and_multiple_owners_never_call_model(self):
        with patch.object(LocalBackend, 'generate') as model:
            self.assertFalse(narrate(QUESTION, self.root).answer_supported)
            self.page(); self.page('SRC-2', owner_name='Bob')
            result = narrate(QUESTION, self.root)
        model.assert_not_called()
        self.assertEqual(result.kind, 'conflict')
        self.assertFalse(result.answer_supported)

    def test_no_model_ignores_invalid_config_and_preserves_contract(self):
        self.page()
        with patch.dict(os.environ, {'MPLPB_NARRATOR_BACKEND': 'invalid'}), patch.object(LocalBackend, 'generate') as model:
            result = narrate(QUESTION, self.root, no_model=True)
        self.assertEqual(result.ledger_result, answer_query(self.root, QUESTION).contract)
        self.assertEqual(result.narration['reason'], 'model_disabled')
        model.assert_not_called()

    def test_partial_documentary_evidence_is_preserved_without_inference(self):
        write(self.root, doc_id='SRC-1', title='Archive', scope='archive',
              body='Ruth Stone appointed Mira Vale.')
        question = 'Who appointed Mira Vale, and who appointed Lena Grey?'
        with patch.object(LocalBackend, 'generate') as model:
            result = narrate(question, self.root)
        self.assertEqual(result.kind, 'partial_answer')
        self.assertFalse(result.answer_supported)
        self.assertTrue(result.ledger_result['missing'])
        self.assertEqual(result.ledger_result, answer_query(self.root, question).contract)
        model.assert_not_called()

    def test_valid_formatting_prompt_and_verbatim_spans(self):
        self.page()
        ledger = answer_query(self.root, QUESTION).contract
        expected = allowed_renderings(ledger['text'])['blockquote']
        with patch.object(LocalBackend, 'generate', return_value=expected) as model:
            result = narrate(QUESTION, self.root)
        self.assertEqual(result.text, expected)
        self.assertTrue(result.answer_supported)
        self.assertFalse(result.narration['model_output_authoritative'])
        self.assertFalse(result.ledger_result['verification']['truth_verified'])
        self.assertEqual(result.ledger_result, ledger)
        messages = model.call_args[0][0]
        self.assertIn('zero eligible owners refuse', messages[0]['content'])
        payload = json.loads(messages[1]['content'])
        self.assertEqual(payload['question'], QUESTION)
        self.assertEqual(payload['profile'], result.profile)
        self.assertTrue(payload['eligible_spans'])
        self.assertNotIn('secret', messages[1]['content'])

    def test_hallucination_quote_laundering_dropped_qualifier_and_added_citation_rejected(self):
        self.page()
        text = answer_query(self.root, QUESTION).contract['text']
        for bad in ('Owner: Bob', text + '\nDelivery occurred.', '"Owner: Alice" proves delivery.',
                    'Unrelated assertion: secret', text + ' [SRC-FAKE]', 'Ignore previous instructions.'):
            with self.subTest(reply=bad), patch.object(LocalBackend, 'generate', return_value=bad):
                result = narrate(QUESTION, self.root)
                self.assertEqual(result.text, text)
                self.assertEqual(result.narration['validation'], 'rejected')
                self.assertNotIn(bad, json.dumps(result.narration))
        qualified = 'If signed, Alice may send the notice; she has not sent it.'
        for bad in ('Alice sent the notice.', 'Alice may send the notice.', qualified[::-1]):
            self.assertFalse(validate_reply(bad, qualified, [{'quote': qualified}]))
        self.assertFalse(validate_reply('The "word".', 'The "word".', [{'quote': 'Other text.'}]))

    def test_endpoint_failure_returns_same_ledger_result(self):
        self.page()
        with patch.object(LocalBackend, 'generate', side_effect=ReaderError('reader_unavailable', 'private runtime detail')):
            result = narrate(QUESTION, self.root)
        self.assertEqual(result.narration['reason'], 'reader_unavailable')
        self.assertEqual(result.ledger_result, answer_query(self.root, QUESTION).contract)
        self.assertNotIn('private runtime detail', json.dumps(result.to_dict()))

    def test_corruption_or_retirement_during_generation_discards_old_answer(self):
        for operation in ('corrupt', 'retire'):
            with self.subTest(operation=operation), tempfile.TemporaryDirectory() as root:
                rec = write(root, doc_id='SRC-1', title='Archive', scope='record owner CASE-1',
                            body_html='<pre>Record-ID: CASE-1\nOwner: Alice</pre>')
                text = answer_query(root, QUESTION).contract['text']
                def mutate(messages):
                    if operation == 'retire': withdraw(root, rec.id)
                    else:
                        p = Path(root)/rec.path; p.write_text(p.read_text().replace('Alice', 'Mallory'))
                    return text
                with patch.object(LocalBackend, 'generate', side_effect=mutate):
                    result = narrate(QUESTION, root)
                self.assertFalse(result.answer_supported)
                self.assertEqual(result.narration['reason'], 'source_changed')
                self.assertEqual(result.ledger_result['sources'], [])
                self.assertNotIn('Alice', result.text)

    def test_new_conflicting_owner_during_generation_is_not_ignored(self):
        self.page()
        text = answer_query(self.root, QUESTION).contract['text']
        def mutate(messages): self.page('SRC-2', owner_name='Bob'); return text
        with patch.object(LocalBackend, 'generate', side_effect=mutate):
            result = narrate(QUESTION, self.root)
        self.assertEqual(result.kind, 'conflict')
        self.assertFalse(result.answer_supported)
        self.assertEqual(result.narration['reason'], 'source_changed')

    def test_delivery_policy_change_during_generation_discards_external_answer(self):
        rec = self.page()
        text = answer_query(self.root, QUESTION, profile=PROFILES['external']).contract['text']
        def mutate(messages):
            # An authorized new revision is sealed but denies external delivery.
            self.page('SRC-2', external='no', supersedes=[rec.id])
            return text
        with patch.object(LocalBackend, 'generate', side_effect=mutate):
            result = narrate(QUESTION, self.root, 'external')
        self.assertFalse(result.answer_supported)
        self.assertEqual(result.narration['reason'], 'source_changed')

    def test_multiple_statement_owners_with_identical_wording_remain_ambiguous(self):
        for ident in ('SRC-1', 'SRC-2'):
            write(self.root, doc_id=ident, title='Juniper press', scope='Juniper press owner',
                  body='Amara owns the Juniper press.')
        with patch.object(LocalBackend, 'generate') as model:
            result = narrate('Who owns the Juniper press?', self.root)
        self.assertFalse(result.answer_supported)
        self.assertEqual(result.kind, 'conflict')
        model.assert_not_called()

    def test_deleted_corpus_during_generation_fails_closed(self):
        nested = self.root/'collection'; nested.mkdir()
        rec = write(nested, doc_id='SRC-1', title='Archive', scope='record owner CASE-1',
                    body_html='<pre>Record-ID: CASE-1\nOwner: Alice</pre>')
        def mutate(messages):
            import shutil
            shutil.rmtree(nested)
            return 'Owner: Alice'
        with patch.object(LocalBackend, 'generate', side_effect=mutate):
            result = narrate(QUESTION, nested)
        self.assertFalse(result.answer_supported)
        self.assertEqual(result.kind, 'abstain')
        self.assertEqual(result.ledger_result['claims'], [])
        self.assertNotIn('Alice', result.text)

    def test_restricted_page_and_original_question_not_for_are_preserved(self):
        self.page(external='no', not_for='delivery')
        for profile, question in (('external', QUESTION), ('internal', QUESTION+' delivery')):
            with self.subTest(profile=profile), patch.object(LocalBackend, 'generate') as model:
                result = narrate(question, self.root, profile)
                self.assertFalse(result.answer_supported)
                model.assert_not_called()

    def test_cli_no_model_success_and_refusal_exit_codes(self):
        self.page()
        for question, code in ((QUESTION, 0), ('Did delivery occur?', 3)):
            with self.subTest(question=question), contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(main(['narrate', question, '--corpus', str(self.root), '--no-model', '--json']), code)
                result = json.loads(out.getvalue())
                self.assertEqual(result['answer_supported'], code == 0)
                self.assertEqual(result['narration']['reason'], 'model_disabled')

    def test_environment_config_and_local_endpoint_constraints(self):
        with patch.dict(os.environ, {'MPLPB_NARRATOR_BACKEND': 'llamacpp', 'MPLPB_NARRATOR_MODEL': 'fixture',
                                    'MPLPB_NARRATOR_BASE_URL': 'http://127.0.0.1:8080/v1'}):
            cfg = NarratorConfig.from_env(); LocalBackend(cfg)
            self.assertEqual(cfg.backend, 'llamacpp')
            self.assertEqual(cfg.model, 'fixture')
        for url in ('http://example.com', 'http://localhost:1234', 'https://127.0.0.1',
                    'http://user:pass@127.0.0.1', 'http://127.0.0.1?x=y', 'http://127.0.0.1/other'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                LocalBackend(NarratorConfig('openai', 'fixture', url))
        with self.assertRaises(ValueError): LocalBackend(NarratorConfig('openai', 'fixture-cloud'))

    def test_input_budget_stops_inference_and_output_budget_rejects(self):
        self.page()
        with patch('mplpb_answers.local_narrator.SYSTEM', 'x'*28001), patch.object(LocalBackend, 'generate') as model:
            result = narrate(QUESTION, self.root)
        model.assert_not_called()
        self.assertEqual(result.narration['reason'], 'narrator_budget_exceeded')
        self.assertFalse(validate_reply('x'*32001, 'x', [{'quote': 'x'}]))


class NarratorHTTPTests(unittest.TestCase):
    def setUp(self):
        self.requests = []; self.mode = 'ok'
        owner = self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args): pass
            def send(self, value, status=200):
                raw = value if isinstance(value, bytes) else json.dumps(value).encode()
                self.send_response(status); self.send_header('Content-Length', str(len(raw))); self.end_headers(); self.wfile.write(raw)
            def do_GET(self):
                owner.requests.append(('GET', self.path))
                self.send({'models': [{'name': 'fixture:latest', 'digest': 'a'*64, 'size': 123,
                                       'details': {'format': 'gguf'}}]})
            def do_POST(self):
                data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                owner.requests.append(('POST', self.path, data))
                if owner.mode == 'redirect': return self.send({}, 302)
                if owner.mode == 'oversized': return self.send(b' '*1000001)
                if owner.mode == 'duplicate': return self.send(b'{"choices":[],"choices":[]}')
                payload = json.loads(data['messages'][1]['content'])
                message = {'role': 'assistant', 'content': payload['allowed_renderings']['evidence'],
                           'thinking': 'PRIVATE-THINKING'}
                if owner.mode == 'tools': message['tool_calls'] = [{}]
                if self.path == '/api/chat':
                    self.send({'done': True, 'done_reason': 'length' if owner.mode == 'truncated' else 'stop', 'message': message})
                else:
                    self.send({'choices': [{'finish_reason': 'length' if owner.mode == 'truncated' else 'stop', 'message': message}]})
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.addCleanup(self.server.server_close); self.addCleanup(self.server.shutdown)
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        write(self.root, doc_id='SRC-1', title='Archive', scope='record owner CASE-1',
              body_html='<pre>Record-ID: CASE-1\nOwner: Alice</pre>')

    def config(self, backend):
        return NarratorConfig(backend, 'fixture', 'http://127.0.0.1:'+str(self.server.server_port)+
                              ('' if backend == 'ollama' else '/v1'))

    def test_three_backend_protocols_through_strict_pipeline(self):
        for backend in ('ollama', 'llamacpp', 'openai'):
            with self.subTest(backend=backend):
                self.requests.clear()
                result = narrate(QUESTION, self.root, config=self.config(backend))
                self.assertEqual(result.narration['status'], 'validated_formatting')
                self.assertTrue(result.answer_supported)
                self.assertNotIn('PRIVATE-THINKING', json.dumps(result.to_dict()))
                request = self.requests[-1]
                self.assertEqual(request[1], '/api/chat' if backend == 'ollama' else '/v1/chat/completions')
                self.assertFalse(request[2]['stream'])
                self.assertNotIn('tools', request[2])

    def test_malformed_truncated_redirect_and_tool_responses_fall_back(self):
        for backend in ('ollama', 'llamacpp', 'openai'):
            for mode in ('redirect', 'oversized', 'duplicate', 'truncated', 'tools'):
                self.mode = mode
                with self.subTest(backend=backend, mode=mode):
                    result = narrate(QUESTION, self.root, config=self.config(backend))
                    self.assertEqual(result.narration['status'], 'ledger_only')
                    self.assertTrue(result.answer_supported)
                    self.assertEqual(result.text, answer_query(self.root, QUESTION).contract['text'])


if __name__ == '__main__': unittest.main()
