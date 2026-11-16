"""Source-adjacent preformatted context; not historical semantic accuracy."""
import hashlib
import html
import json
from pathlib import Path
import tempfile
import unittest

from mplpb_combined.ledger import write
from mplpb_answers.body_text import body_text
from mplpb_answers.evidence_contract import validate_proposal
from mplpb_answers.passages import PassageIndex


ROOT = Path(__file__).resolve().parents[1]


class HistoricalPassageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def page(self, body):
        return write(self.root, doc_id='CONTEXT-0001', title='Original witness',
                     scope='historical research', origin='machine', body_html=body)

    def test_wrapped_condition_and_conclusion_share_one_citable_passage(self):
        quote = ('If the archived instrument is sealed,\n'
                 'retain its original calibration record\n'
                 'with the instrument. A later copy is not independent evidence.')
        rec = self.page('<p>Préface Ω.</p><pre>'+html.escape(quote)+'</pre>')
        pack = PassageIndex(self.root, 'What accompanies the sealed instrument?').retrieve(
            ['sealed instrument calibration'], max_passages=1, max_chars=1000)
        self.assertEqual(len(pack['passages']), 1)
        passage = pack['passages'][0]
        self.assertEqual(passage['text'], quote)
        self.assertFalse(passage['context_truncated'])
        question = 'What accompanies the sealed instrument?'
        proposal = {'question':question, 'outcome':'answer', 'claims':[
            {'text':quote, 'qualifiers':[], 'citations':[{'passage':passage['id'], 'quote':quote}]}],
            'missing':[], 'clarification':'', 'confidence':0.9}
        citation = validate_proposal(proposal, question, pack['passages'])[0]['citations'][0]
        body = body_text(rec.body_html)
        self.assertEqual(body[citation['body_start']:citation['body_end']], quote)
        self.assertEqual(citation['body_start'], len('Préface Ω.\n'))

    def test_actual_pinned_original_and_wrapper_bytes_are_unchanged(self):
        manifest = json.loads((ROOT/'docs/research/mplpb-originality/mplpb-sources.json').read_text())
        source = manifest['sources']['local-web']
        path = ROOT/source['path']
        original = path.read_bytes()
        self.assertEqual(hashlib.sha256(original).hexdigest(), source['sha256'])
        rec = self.page('<pre>'+html.escape(original.decode())+'</pre>')
        wrapper = self.root/rec.path
        before = wrapper.read_bytes()
        index = PassageIndex(self.root, 'How do the local web and crawler relate?')
        body = body_text(rec.body_html)
        self.assertTrue(index.passages)
        self.assertLess(len(index.passages), len(body.splitlines())//2)
        for passage in index.passages:
            start = passage['body_start']
            self.assertEqual(body[start:start+len(passage['text'])], passage['text'])
            self.assertEqual(passage['hash'], rec.hash)
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(wrapper.read_bytes(), before)

    def test_negated_preconditions_crossing_context_boundary_stay_with_instruction(self):
        for condition in ('If the seal is intact,', 'If the seal is not intact,'):
            with self.subTest(condition=condition), tempfile.TemporaryDirectory() as root:
                # Place the condition just before the context boundary. The
                # following instruction must carry it into the next window.
                padding = ('Background register entry.\n'*43)
                quote = condition+'\nTransfer the archival instrument with its calibration certificate.'
                rec = write(root, doc_id='PAIR-0001', title='Minimal pair', scope='archive',
                            body_html='<pre>'+padding+quote+'</pre>')
                index = PassageIndex(root, 'How should staff transfer the archival instrument?')
                pack = index.retrieve(['transfer archival instrument calibration'],
                                      max_passages=1, max_chars=2400)
                self.assertEqual(len(pack['passages']), 1)
                passage = pack['passages'][0]
                self.assertIn(quote, passage['text'])
                self.assertTrue(passage['context_truncated'])
                body = body_text(rec.body_html)
                start = passage['body_start']
                self.assertEqual(body[start:start+len(passage['text'])], passage['text'])

    def test_ordinary_paragraphs_are_not_fused_and_repeated_pre_offsets_are_exact(self):
        repeated = 'A wrapped archival statement\ncontinues on this source line.'
        raw = ('<h1 title="a > b">HEADING-ONLY</h1><p>Separate first paragraph.</p>'
               '<p>Separate second paragraph.</p><pre>'+repeated+'</pre>'
               '<p>'+repeated.replace('\n', '<br>')+'</p><pre>'+repeated+'</pre>')
        rec = self.page(raw)
        index = PassageIndex(self.root, 'What does the archival statement say?')
        body = body_text(rec.body_html)
        texts = [p['text'] for p in index.passages]
        self.assertIn('Separate first paragraph.', texts)
        self.assertIn('Separate second paragraph.', texts)
        self.assertEqual(texts.count(repeated), 2)
        repeated_starts = [p['body_start'] for p in index.passages if p['text']==repeated]
        self.assertEqual(len(set(repeated_starts)), 2)
        self.assertNotIn('HEADING-ONLY', '\n'.join(texts))
        for passage in index.passages:
            start = passage['body_start']
            self.assertEqual(body[start:start+len(passage['text'])], passage['text'])

    def test_large_pre_contexts_preserve_coverage_and_report_incomplete_context(self):
        text = '\n'.join('Archival entry %03d retains its date and qualification.' % i
                         for i in range(160))
        rec = self.page('<pre>'+text+'</pre>')
        index = PassageIndex(self.root, 'What qualifications accompany archival entries?')
        body = body_text(rec.body_html)
        intervals = [(p['body_start'], p['body_start']+len(p['text'])) for p in index.passages]
        for position, char in enumerate(body):
            if not char.isspace():
                self.assertTrue(any(begin<=position<end for begin,end in intervals), position)
        self.assertTrue(all(p['context_truncated'] for p in index.passages))
        pack = index.retrieve(['archival qualification'], max_passages=2, max_chars=2400)
        self.assertLessEqual(len(pack['passages']), 2)
        self.assertLessEqual(sum(len(p['text']) for p in pack['passages']), 2400)
        self.assertFalse(pack['search_complete'])

    def test_single_long_pre_line_retains_overlapping_window_limit(self):
        text = 'Calibration condition and retained context. '*200
        rec = self.page('<pre>'+text+'</pre>')
        index = PassageIndex(self.root, 'Which calibration condition is retained?')
        body = body_text(rec.body_html)
        self.assertGreater(len(index.passages), 1)
        self.assertTrue(all(len(p['text'])<=4250 for p in index.passages))
        self.assertTrue(all(p['context_truncated'] for p in index.passages))
        for passage in index.passages:
            start=passage['body_start']
            self.assertEqual(body[start:start+len(passage['text'])], passage['text'])


if __name__=='__main__':
    unittest.main()
