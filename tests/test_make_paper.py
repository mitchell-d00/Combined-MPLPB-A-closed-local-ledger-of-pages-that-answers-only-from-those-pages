"""Paper rendering preserves original publications and optional metadata."""
import contextlib
import hashlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest

from tools import make_paper as P


class PaperRenderingTests(unittest.TestCase):
    def test_selected_utf8_source_does_not_overwrite_original_paper(self):
        originals=[P.SRC.with_suffix(ext) for ext in ('.md','.txt','.pdf')]
        before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in originals}
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/'candidate.md'
            source.write_text('# Candidate report\n\nÉmile inspected `MSG-1`.\n\n```\nexact: café\n```\n',encoding='utf-8')
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(P.main(['--source',str(source),'--txt']),0)
            result=source.with_suffix('.txt').read_text(encoding='utf-8')
            self.assertIn('Émile inspected MSG-1.',result)
            self.assertIn('    exact: café',result)
            self.assertFalse(source.with_suffix('.pdf').exists())
        self.assertEqual(before,{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in originals})

    @unittest.skipUnless(importlib.util.find_spec('reportlab'),'Optional documentation dependency reportlab unavailable')
    def test_selected_pdf_metadata_and_invariant_repeat(self):
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/'candidate.md'
            source.write_text('# Candidate report\n\nCandidate only.\n',encoding='utf-8')
            args=['--source',str(source),'--title','Candidate paper','--author','Mitchell D. McPhetridge',
                  '--subject','Source-linked candidates','--footer','Candidate report v1','--invariant']
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(P.main(args),0)
                first=source.with_suffix('.pdf').read_bytes()
                self.assertEqual(P.main(args),0)
            self.assertEqual(first,source.with_suffix('.pdf').read_bytes())
            self.assertTrue(first.startswith(b'%PDF-'))
            self.assertIn(b'/Title (Candidate paper)',first)
            self.assertIn(b'/Author (Mitchell D. McPhetridge)',first)
            self.assertIn(b'/Subject (Source-linked candidates)',first)
