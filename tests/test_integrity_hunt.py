"""Adversarial regressions discovered against the published b98ee7e release."""
import tempfile
import unittest
from pathlib import Path

from mplpb_combined import ledger as L, reader as R
from mplpb_combined.record import read_page
from tools.ledger_ui import App


class LedgerIntegrityHunt(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "corpus"
        self.root.mkdir()

    def test_withdrawn_record_cannot_be_revived_with_unhashed_status(self):
        rec = L.write(self.root, title="Lab door", scope="lab door code",
                      body="The lab door code is 4471.")
        L.withdraw(self.root, rec.id, note="code rotated")
        file = self.root / rec.path
        file.write_text(file.read_text().replace('content="retired"',
                                                  'content="current"'))
        led = L.Ledger(self.root)
        self.assertEqual(R.answer(self.root, "lab door code").kind,
                         R.NOT_IN_CORPUS)
        self.assertEqual(led.effective_status(led.by_id[rec.id][0]), "retired")
        self.assertIn("C16", [v.code for v in led.findings() if v.level == "error"])

    def test_corrupt_existing_history_cannot_authorize_answers(self):
        rec = L.write(self.root, title="Lab entry", scope="lab entry",
                      body="The laboratory has one entry.")
        log = L.log_path(self.root)
        content = log.read_text()
        log.write_text(content.replace('"event": "write"', '"event": "retire"'))
        self.assertEqual(R.answer(self.root, "lab entry").kind, R.NOT_IN_CORPUS)
        led = L.Ledger(self.root)
        self.assertTrue(led.log_corrupt)
        self.assertIn("C14", [v.code for v in led.findings() if v.level == "error"])
        self.assertTrue((self.root / rec.path).exists())

    def test_duplicate_metadata_never_serves_or_silently_withdraws(self):
        rec = L.write(self.root, title="Old policy", scope="visitor badge policy",
                      body="Visitors need no badge.")
        file = self.root / rec.path
        file.write_text(file.read_text().replace(
            '<meta name="mplpb:status" content="current">',
            '<meta name="mplpb:status" content="current">'
            '<meta name="mplpb:status" content="current">'))
        self.assertEqual(R.answer(self.root, "visitor badge policy").kind,
                         R.NOT_IN_CORPUS)
        self.assertIn("C17", [v.code for v in L.Ledger(self.root).findings()])
        with self.assertRaises(ValueError):
            L.withdraw(self.root, rec.id)

    def test_seal_refuses_unhashed_duplicate_status_metadata(self):
        p = self.root / "legacy.html"
        p.write_text('<html><head><title>Legacy</title>'
                     '<meta name="mplpb:document-id" content="LEG-1">'
                     '<meta name="mplpb:scope" content="legacy policy">'
                     '<meta name="mplpb:status" content="current">'
                     '<meta name="mplpb:status" content="current">'
                     '</head><body><p>Deprecated.</p></body></html>')
        self.assertEqual(L.seal(self.root), [])
        self.assertIn("C17", [v.code for v in L.Ledger(self.root).findings()])
        self.assertNotEqual(R.answer(self.root, "legacy policy").kind, R.RETURN)

    def test_body_svg_title_and_meta_cannot_change_header(self):
        rec = L.write(self.root, title="Kiln wiring", scope="kiln wiring diagram",
                      body_html=('<p>See diagram.</p><svg><title>Do not touch</title>'
                                 '<rect/></svg><meta name="mplpb:status" '
                                 'content="retired">'))
        read = read_page(self.root, self.root / rec.path)
        self.assertTrue(read.intact)
        self.assertEqual(read.title, "Kiln wiring")
        self.assertEqual(read.status, "current")
        self.assertFalse(read.problems)


class RetrievalSafetyHunt(unittest.TestCase):
    def test_numeric_glaze_variants_do_not_return_cone_six(self):
        root = Path(__file__).resolve().parents[1] / "examples" / "studio"
        for q in ("What is the glaze firing schedule to cone 04 in the electric kiln?",
                  "What is the glaze firing schedule to cone 10 in the electric kiln?"):
            with self.subTest(q=q):
                result = R.answer(root, q)
                self.assertNotEqual(result.kind, R.RETURN)

    def test_severe_burn_does_not_bypass_serious_injury_exclusion(self):
        root = Path(__file__).resolve().parents[1] / "examples" / "studio"
        question = "How do I treat a severe burn from hot ware?"
        self.assertNotEqual(R.answer(root, question).kind, R.RETURN)

    def test_negation_must_not_be_ignored(self):
        positive = "Is it safe to skip the bisque firing schedule?"
        negative = "Is it not safe to skip the bisque firing schedule?"
        self.assertNotEqual(R.terms(positive), R.terms(negative))
        root = Path(__file__).resolve().parents[1] / "examples" / "studio"
        self.assertNotEqual(R.answer(root, negative).kind, R.RETURN)

    def test_unicode_words_stay_whole(self):
        self.assertIn("schrühbrand", R.terms("Schrühbrand"))
        self.assertIn("обжиг", R.terms("Что такое обжиг?"))
        root = Path(__file__).resolve().parents[1] / "examples" / "studio"
        result = R.answer(root, "Что такое обжиг?")
        self.assertNotEqual(result.reason, "the question has no content words")

    def test_unsupportable_ask_has_no_empty_candidate_tags(self):
        app = App(topic_base=Path(tempfile.mkdtemp()) / "topics")
        result = app.query({"corpus":"studio", "question":
                            "What is the glaze firing schedule to cone 6 in the electric kiln?"})
        self.assertEqual(result["reader"]["kind"], "not_in_corpus")
        self.assertFalse([c for c in result["reader"]["candidates"]
                          if not c["matched"]])
        # Inspection remains available, explicitly as candidate-only.
        inspected = app.query({"corpus":"studio", "mode":"candidates",
                               "question":"What is the glaze firing schedule to cone 6 in the electric kiln?"})
        self.assertIn(inspected["reader"]["kind"],
                      ("candidate_only", "ambiguous", "not_in_corpus"))


class AskInterfaceHunt(unittest.TestCase):
    def test_inspect_and_strict_are_distinct_in_shipped_ui(self):
        html = (Path(__file__).resolve().parents[1] / "index.html").read_text()
        self.assertIn('id="ask-reader-mode"', html)
        self.assertIn('mode:$(' + "'ask-reader-mode').value", html)
        self.assertIn("visibleSources", html)
        self.assertIn("Candidate pages", html)
        self.assertIn("Strict mode found no verified answer", html)


if __name__ == "__main__":
    unittest.main()
