"""Locally verifiable improvements; no human historical review is simulated."""
import hashlib
import html
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from mplpb_combined import record
from mplpb_combined.ledger import write
from mplpb_answers.pipeline import answer_query
from mplpb_work import WorkError


class ParseCacheTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.rec = write(self.root, doc_id='SRC-1', title='Witness', scope='archive owner record',
                         body_html='<pre>Record-ID: CASE-1\nOwner: Alice</pre>')
        self.path = self.root/self.rec.path
        record._parsed_content.cache_clear()
        self.addCleanup(record._parsed_content.cache_clear)

    def test_repeated_reads_reuse_parsing_but_return_independent_records(self):
        raw = self.path.read_bytes()
        with patch.object(record, '_parse_content', wraps=record._parse_content) as parser:
            first = record.read_page(self.root, self.path)
            first.fields['status'] = 'retired'; first.problems.append(('fake', 'problem'))
            second = record.read_page(self.root, self.path)
            self.assertEqual(parser.call_count, 1)
        self.assertNotEqual(second.status, 'retired'); self.assertNotIn(('fake', 'problem'), second.problems)
        self.assertEqual(self.path.read_bytes(), raw)
        self.assertEqual(second.hash_actual, self.rec.hash_actual)

    def test_status_and_declared_hash_are_part_of_cache_key(self):
        text = self.path.read_text()
        first = record.parse_page(text, 'one.html')
        retired = record.upsert_meta(text, 'status', 'retired')
        second = record.parse_page(retired, 'two.html')
        self.assertEqual(second.status, 'retired')
        self.assertEqual(first.hash_actual, second.hash_actual)
        corrupted_pin = record.upsert_meta(text, 'hash', 'sha256:'+'0'*64)
        self.assertFalse(record.parse_page(corrupted_pin, 'three.html').intact)
        self.assertTrue(record.parse_page(text, 'one.html').intact)

    def test_same_size_same_mtime_corruption_is_reloaded_after_warmup(self):
        question = 'What is Owner for record CASE-1?'
        before = answer_query(self.root, question).contract
        self.assertTrue(before['answer_supported'])
        metadata = self.path.stat()
        raw = self.path.read_bytes(); changed = raw.replace(b'Owner: Alice', b'Owner: Orina')
        self.assertEqual(len(raw), len(changed)); self.path.write_bytes(changed)
        os.utime(self.path, ns=(metadata.st_atime_ns, metadata.st_mtime_ns))
        after = answer_query(self.root, question).contract
        self.assertFalse(after['answer_supported'])
        self.assertEqual(after['claims'], [])

    def test_path_dependent_kind_and_policy_changes_not_cached(self):
        text = '<html><head><title>Example</title></head><body>Same body</body></html>'
        self.assertEqual(record.parse_page(text, 'index.html').kind, 'index')
        self.assertEqual(record.parse_page(text, 'page.html').kind, 'page')
        from mplpb_combined.reader import PROFILES
        question = 'What is Owner for record CASE-1?'
        self.assertTrue(answer_query(self.root, question, PROFILES['external']).contract['answer_supported'])
        text = record.upsert_meta(self.path.read_text(), 'external', 'no')
        # A legal revision of the source pin, not a corruption fixture.
        parsed = record.parse_page(text, self.rec.path)
        self.path.write_text(record.upsert_meta(text, 'hash', parsed.hash_actual))
        self.assertFalse(answer_query(self.root, question, PROFILES['external']).contract['answer_supported'])

    def test_cache_is_bounded_and_oversized_text_is_not_retained(self):
        for i in range(record.PARSE_CACHE_MAX_ENTRIES+2):record.parse_page('<body>'+str(i)+'</body>', 'page.html')
        self.assertEqual(record._parsed_content.cache_info().currsize, record.PARSE_CACHE_MAX_ENTRIES)
        info = record._parsed_content.cache_info()
        record.parse_page('<body>'+'x'*(record.PARSE_CACHE_MAX_CHARS+1)+'</body>', 'large.html')
        self.assertEqual(record._parsed_content.cache_info(), info)


class LocalStorageTests(unittest.TestCase):
    from tests.test_scoped_extensions import WorkExtensionTests as _Fixture
    from tests.test_answer_boundaries import OperationalReceiptBoundaryTests as _Operational
    setUp = _Fixture.setUp
    put = _Fixture.put
    execute = _Operational.execute

    def create_artifact(self, contents=b'actual output bytes'):
        base = self.store.directory/'artifacts'; base.mkdir(exist_ok=True)
        path = base/'result.bin'; path.write_bytes(contents)
        return path, hashlib.sha256(contents).hexdigest()

    def store_receipt(self, execution, path='result.bin', pin=None):
        return self.store.record_external_receipt(self.host, receipt=execution, kind='STORE',
            artifact='Host description alone is insufficient for byte inspection',
            local_artifact=path, expected_artifact_sha256=pin,
            expected_head=self.store.head(self.host)['hash'])

    def test_real_storage_check_recheck_and_mutation_do_not_promote_truth(self):
        execution = self.execute('A1'); path, pin = self.create_artifact()
        receipt = self.store_receipt(execution, pin=pin)
        observed = receipt['local_storage']
        self.assertEqual(observed['raw_sha256'], pin)
        self.assertTrue(observed['matches_expected'])
        self.assertFalse(observed['delivery_verified']); self.assertFalse(observed['read_by_person_verified'])
        self.assertFalse(receipt['external_world_verified']); self.assertFalse(receipt['answer_supported'])
        head = self.store.head(self.host)
        verify = lambda: self.store.verify_storage_receipt(self.host, receipt_id=receipt['id'])
        self.assertEqual(verify()['status'], 'intact')
        path.write_bytes(b'changed output')
        self.assertEqual(verify()['status'], 'changed')
        path.unlink(); self.assertEqual(verify()['status'], 'unavailable')
        self.assertEqual(self.store.head(self.host), head)
        from mplpb_work.api import request
        with self.assertRaises(WorkError):request(self.store, self.token, {'op':'verify_storage_receipt','receipt_id':receipt['id']})

    def test_missing_wrong_pin_or_unsafe_path_never_appends_a_receipt(self):
        execution = self.execute('A1'); _, pin = self.create_artifact()
        head = self.store.head(self.host)
        for name, digest in [('missing', pin), ('../work.sqlite3', pin), ('/tmp/file', pin),
                             ('result.bin', '0'*64), ('result.bin', None)]:
            with self.subTest(name=name, digest=digest):
                with self.assertRaises(WorkError):self.store_receipt(execution, name, digest)
                self.assertEqual(self.store.head(self.host), head)

    def test_symlinks_directories_fifo_and_oversized_artifacts_rejected(self):
        execution = self.execute('A1'); path, pin = self.create_artifact()
        base = path.parent
        (base/'link').symlink_to(path)
        (base/'dirlink').symlink_to(base, target_is_directory=True)
        (base/'directory').mkdir()
        os.mkfifo(base/'fifo')
        from mplpb_work.local_artifacts import MAX_ARTIFACT_BYTES
        with (base/'large').open('wb') as file:file.truncate(MAX_ARTIFACT_BYTES+1)
        for name in ('link', 'dirlink/result.bin', 'directory', 'fifo', 'large'):
            with self.subTest(name=name):
                with self.assertRaises(WorkError):self.store_receipt(execution, name, pin)

    def test_artifact_change_during_read_does_not_append(self):
        from mplpb_work import local_artifacts
        execution = self.execute('A1'); path, pin = self.create_artifact()
        original = os.read; changed = []
        def mutate(fd, count):
            data = original(fd, count)
            if not changed:
                changed.append(True); path.write_bytes(b'Z'*path.stat().st_size)
            return data
        head = self.store.head(self.host)
        with patch.object(local_artifacts.os, 'read', mutate):
            with self.assertRaises(WorkError):self.store_receipt(execution, pin=pin)
        self.assertEqual(self.store.head(self.host), head)

    def test_local_storage_cannot_prove_delivery(self):
        execution = self.execute('A1'); _, pin = self.create_artifact()
        with self.assertRaises(WorkError):
            self.store.record_external_receipt(self.host, receipt=execution, kind='READ', artifact='claim',
                local_artifact='result.bin', expected_artifact_sha256=pin,
                expected_head=self.store.head(self.host)['hash'])


class EvidencePresentationTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        write(self.root, doc_id='SRC-1', title='Archive', scope='archive',
              body_html='<pre>Ruth Stone appointed Mira Vale.</pre>')

    def test_obligations_link_only_to_displayed_checked_claims(self):
        question = 'Who appointed Mira Vale, and who appointed Lena Grey?'
        answer = answer_query(self.root, question).contract
        goals = answer['documentary_support']['obligations']
        self.assertEqual(goals[0]['evidence_claim_indices'], [0])
        self.assertEqual(goals[1]['evidence_claim_indices'], [])
        self.assertFalse(answer['answer_supported'])
        from mplpb_work.prose_evidence import render_reconstruction
        report = {'question':question, 'status':'research_report', 'native_answer':answer,
                  'candidate_analysis':{}, 'model_candidates':None}
        rendered = render_reconstruction(report)
        self.assertIn('who appointed lena grey', rendered.lower())
        self.assertIn('canonical ', rendered); self.assertIn('Ruth Stone appointed Mira Vale.', rendered)
        self.assertIn('unverified and never promoted', rendered)
        self.assertIn('Snapshot only', rendered)
        self.assertIn('partial_answer', rendered)

    def test_undisplayed_evidence_never_gets_a_visible_claim_index(self):
        write(self.root, doc_id='SRC-2', title='Archive', scope='archive',
              body_html='<pre>Orin Hale appointed Lena Grey. Ruth Stone appointed Mira Vale.</pre>')
        c=answer_query(self.root, 'Who appointed Mira Vale, and who appointed Lena Grey?', max_passages=1).contract
        self.assertFalse(c['answer_supported'])
        for goal in c['documentary_support']['obligations']:
            self.assertTrue(all(i<len(c['claims']) for i in goal['evidence_claim_indices']))
        self.assertTrue(any(g['undisplayed_evidence_count'] for g in c['documentary_support']['obligations']))

    def test_changed_source_report_hides_all_old_evidence(self):
        from mplpb_work.prose_evidence import render_reconstruction
        text=render_reconstruction({'status':'source_changed','question':'Who appointed Mira Vale?',
                                    'native_answer':{'claims':[{'text':'OLD QUOTE'}]}})
        self.assertNotIn('OLD QUOTE', text)
        self.assertIn('no old evidence accepted', text)

    def test_cli_text_mode_runs_real_reconstruction_and_default_remains_json(self):
        import contextlib
        import io
        import json
        from mplpb_answers.__main__ import main
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(['reconstruct', str(self.root), 'Who appointed Mira Vale?', '--format', 'text']), 0)
        self.assertIn('Question parts:', output.getvalue())
        self.assertIn('Ruth Stone appointed Mira Vale.', output.getvalue())
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(['reconstruct', str(self.root), 'Who appointed Mira Vale?']), 0)
        self.assertEqual(json.loads(output.getvalue())['status'], 'research_report')
