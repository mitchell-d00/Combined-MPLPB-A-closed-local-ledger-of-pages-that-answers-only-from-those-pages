"""Targeted checks for literal coverage with intact MPLPB source boundaries."""
import tempfile
import unittest
from pathlib import Path

from mplpb_answers import literal_evidence as LE
from mplpb_answers.support import supported_answer
from mplpb_combined.ledger import write
from mplpb_combined.reader import PROFILES, Profile


class LiteralEvidenceTests(unittest.TestCase):
    def _ask(self, question, text, title="Reference", scope="reference"):
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, doc_id="T-0001", title=title, scope=scope, body=text)
            return supported_answer(tmp, question)

    def test_explicit_source_span_extraction(self):
        cases = [
            ("What is Southern California often abbreviated as?",
             "Southern California, often abbreviated SoCal, is a geographic region.",
             "SoCal"),
            ("When did the 1973 oil crisis begin?",
             "The 1973 oil crisis began in October 1973 when an embargo was proclaimed.",
             "October 1973"),
            ("The atomic number of the periodic table for oxygen?",
             "Oxygen is a chemical element with symbol O and atomic number 8.", "8"),
            ("What kind of economy does Victoria have?",
             "The economy of Victoria is highly diversified: service industries dominate.",
             "highly diversified"),
            ("In what country is Normandy located?",
             "The Normans gave their name to Normandy, a region in France.", "France"),
            ("What company was formed by the merger of Sky Television and British Satellite Broadcasting?",
             "Formed in November 1990 by the equal merger of Sky Television and British Satellite Broadcasting, BSkyB became a large company.",
             "BSkyB"),
            ("What branch of theoretical computer science deals with broadly classifying computational problems by difficulty and class of relationship?",
             "Computational complexity theory is a branch of the theory of computation in theoretical computer science that focuses on classifying computational problems according to their inherent difficulty, and relating those classes to each other.",
             "Computational complexity theory"),
            ("Where was France's Huguenot population largely centered?",
             "Huguenot numbers peaked near an estimated two million by 1562, concentrated mainly in the southern and central parts of France, about one-eighth the number of French Catholics.",
             "the southern and central parts of France"),
            ("Along with geothermal and nuclear, what is a notable non-combustion heat source?",
             "Non-combustion heat sources such as solar power, nuclear power or geothermal energy may be used.",
             "solar power"),
        ]
        for question, body, value in cases:
            with self.subTest(question=question):
                result = self._ask(question, body)
                self.assertEqual(result.kind, "return")
                self.assertIn(value.casefold(), result.text.casefold())
                self.assertEqual(result.support["status"], "supported")
                self.assertEqual(result.support["spans"][0]["quote"], body)

    def test_unknown_premise_and_wrong_subject_refuse(self):
        cases = [
            ("What is Southern California often abbreviated as?",
             "Northern California, often abbreviated NorCal, is a region."),
            ("In what country is Normandy located?", "Burgundy, a region in France, is historic."),
            ("What kind of economy does Victoria have?",
             "The economy of another province is highly diversified."),
            ("When did OPEC begin?", "The 1973 oil crisis began in October 1973."),
            ("The atomic number of the periodic table for oxygen?",
             "Nitrogen is a chemical element with symbol N and atomic number 7."),
            ("Along with geothermal and nuclear, what is a notable combustion heat source?",
             "Non-combustion heat sources such as solar power, nuclear power or geothermal energy may be used."),
            ("What company was angry about the merger of Sky Television and British Satellite Broadcasting?",
             "Formed by the merger of Sky Television and British Satellite Broadcasting, BSkyB became a company."),
            ("What branch of theoretical computer science deals with broadly classifying computational problems by difficulty and class of relationship?",
             "Other research discusses computational problems by difficulty, but this sentence does not identify a branch."),
            ("Where was France's Huguenot population largely centered?",
             "Catholic population was concentrated mainly in the northern parts of France."),
            ("Where was France's Huguenot population largely centered?",
             "Huguenot numbers were concentrated mainly in the southern parts of Germany."),
        ]
        for question, body in cases:
            with self.subTest(question=question):
                result = self._ask(question, body)
                self.assertNotEqual(result.kind, "return")
                self.assertEqual(result.text, "")
                self.assertEqual(result.citation(), "")

    def test_quoted_and_hypothetical_statements_are_not_proofs(self):
        body = 'Say "The economy of Victoria is highly diversified."'
        self.assertNotEqual(self._ask("What kind of economy does Victoria have?", body).kind, "return")
        body = "If approved, the 1973 oil crisis began in October 1973."
        self.assertNotEqual(self._ask("When did the 1973 oil crisis begin?", body).kind, "return")

    def test_conflict_and_tampering_refuse(self):
        question = "When did the Aster event begin?"
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, doc_id="T-0001", title="Aster", scope="Aster event",
                  body="The Aster event began in March 2018. The Aster event began in May 2019.")
            self.assertEqual(supported_answer(tmp, question).kind, "ambiguous")
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, doc_id="T-0001", title="Aster", scope="Aster event",
                  body="The Aster event began in March 2018.")
            page = next(Path(tmp).glob("*.html"))
            page.write_text(page.read_text().replace("March 2018", "May 2019"))
            self.assertEqual(supported_answer(tmp, question).kind, "not_in_corpus")

    def test_delivery_profile_remains_enforced(self):
        query = "When did the Aster event begin?"
        # An explicit external restriction must be enforced.
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, doc_id="T-0001", title="Aster", scope="Aster event",
                  body="The Aster event began in March 2018.", external="no")
            self.assertEqual(supported_answer(tmp, query).kind, "return")
            self.assertEqual(supported_answer(tmp, query, PROFILES["external"]).kind,
                             "not_in_corpus")
        # Public, depth-zero pages are allowed by the external profile.
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, doc_id="T-0001", title="Aster", scope="Aster event",
                  body="The Aster event began in March 2018.", external="yes")
            self.assertEqual(supported_answer(tmp, query, PROFILES["external"]).kind,
                             "return")
            self.assertEqual(supported_answer(tmp, query, Profile("blocked", -1, False)).kind,
                             "not_in_corpus")


    def test_inspected_squad_development_excerpt(self):
        # Previously inspected questions, NOT an independent accuracy claim.
        from tools.evaluate_literal_coverage import run
        result = run()
        self.assertEqual(result["sample_size"], 20)
        self.assertEqual(result["answerable"], 10)
        self.assertEqual(result["answered_correctly"], 10,
                         [(r["question"], r["kind"], r["return_correct"], r["evidence_spans"])
                          for r in result["rows"] if r["expected"] == "return"
                          and not r["return_correct"]])
        self.assertEqual(result["unanswerable"], 10)
        self.assertEqual(result["correctly_non_returned"], 10)
        self.assertEqual(result["wrong_returns"], 0)


if __name__ == "__main__":
    unittest.main()
