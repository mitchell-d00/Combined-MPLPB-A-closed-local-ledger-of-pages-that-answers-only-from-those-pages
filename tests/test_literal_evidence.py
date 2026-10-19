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
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, doc_id="T-0001", title="Aster", scope="Aster event",
                  body="The Aster event began in March 2018.")
            query = "When did the Aster event begin?"
            self.assertEqual(supported_answer(tmp, query).kind, "return")
            self.assertEqual(supported_answer(tmp, query, PROFILES["external"]).kind,
                             "return")
            self.assertEqual(supported_answer(tmp, query, Profile("blocked", -1, False)).kind,
                             "not_in_corpus")


if __name__ == "__main__":
    unittest.main()
