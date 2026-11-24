"""Regression for canonical witness boundaries in the FRUS experiment importer."""
import unittest

from mplpb_answers.body_text import body_text
from tools.pole_focus_extend import frus_fragment, frus_rendered


class FrusProjectionTests(unittest.TestCase):
    source = {'encoding': 'utf-8', 'document_id': 'd7'}

    def test_folds_delivery_lines_and_preserves_source_markup(self):
        page = ('<nav>unrelated site navigation</nav>'
                '<div CLASS="tei-div3" id="d7">\n<p>First &amp;\r\n  second <i>terms</i>.</p>'
                '<p>Another<br>line.</p><pre>X\n  Y</pre><!-- unchanged\ncomment -->'
                '</div><div>site footer</div>').encode()
        raw = frus_fragment(page, self.source)
        projected = frus_rendered(page, self.source)
        self.assertIn('First &\nsecond terms.', body_text(raw))
        self.assertIn('First & second terms.\nAnother\nline.', body_text(projected))
        self.assertIn('<pre>X\n  Y</pre><!-- unchanged\ncomment -->', projected)
        self.assertIn('<div CLASS="tei-div3" id="d7">', projected)
        self.assertIn('&amp;', projected)
        self.assertNotIn('site footer', projected)

    def test_ambiguous_or_unclosed_envelope_withholds_projection(self):
        one = b'<div class="tei-div3" id="d7">document</div>'
        for page in (one + one, one.removesuffix(b'</div>'), b'<p>other page</p>'):
            with self.subTest(page=page), self.assertRaises(ValueError):
                frus_rendered(page, self.source)
