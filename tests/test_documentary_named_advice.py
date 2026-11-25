"""Grounding and refusal checks for a partial source-reported advice answer."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import write


QUESTION = ('What transport-planning emphasis did Morgan recommend to Patel before her inspection trip, '
            'and what framework did Patel say she presented in her meetings?')
CONTEXT = 'The focus of the discussion was Director Patel’s upcoming inspection trip.'
ADVICE = 'Ms. Morgan recommended that Director Patel emphasize “scheduled service” in transport planning.'


class NamedAdviceTests(unittest.TestCase):
    def ask(self, question=QUESTION, body=None, duplicate=False, max_passages=12):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            text = body or f'<p>{CONTEXT}</p><p>{ADVICE}</p>'
            write(root, doc_id='SOURCE-A', title='Meeting notes', scope='minutes', body_html=text)
            if duplicate:
                write(root, doc_id='SOURCE-B', title='Meeting copy', scope='minutes', body_html=text)
            return answer_query(root, question, max_passages=max_passages).contract

    def test_checks_only_advice_with_speaker_topic_and_upcoming_scope(self):
        answer = self.ask()
        self.assertEqual(answer['kind'], 'partial_answer')
        self.assertFalse(answer['answer_supported'])
        self.assertEqual(len(answer['claims']), 1)
        self.assertEqual(answer['claims'][0]['proposition']['adviser'], 'Morgan')
        self.assertEqual(answer['claims'][0]['proposition']['recipient'], 'Patel')
        self.assertEqual([c['quote'] for c in answer['claims'][0]['citations']], [CONTEXT, ADVICE])
        self.assertTrue(answer['missing'])

    def test_withholds_missing_or_competing_evidence(self):
        for options in (
            {'question': QUESTION.replace('Morgan', 'Rivera')},
            {'question': QUESTION.replace('transport-planning', 'budget')},
            {'body': f'<p>{ADVICE}</p>'},
            {'body': f'<p>{CONTEXT}</p><blockquote>{ADVICE}</blockquote>'},
            {'body': f'<p>{CONTEXT}</p><p>{ADVICE}</p><p>{ADVICE.replace("scheduled service", "on-demand service")}</p>'},
            {'body': f'<p>Fictional example.</p><p>{CONTEXT}</p><p>{ADVICE}</p>'},
            {'body': f'<p>{CONTEXT}</p><p>{ADVICE}</p><p>{ADVICE.replace("recommended that", "did not recommend that")}</p>'},
            {'body': f'<p>{CONTEXT}</p><p>{ADVICE}</p><p>{ADVICE.replace("recommended that", "never recommended that")}</p>'},
            {'max_passages': 1},
            {'duplicate': True},
        ):
            with self.subTest(options=options):
                answer = self.ask(**options)
                self.assertEqual(answer['kind'], 'abstain')
                self.assertFalse(answer['claims'])
