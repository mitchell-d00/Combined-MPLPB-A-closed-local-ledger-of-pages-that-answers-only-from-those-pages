"""Production entry-point contract: retrieval never masquerades as support."""
import contextlib
import io
import json
import tempfile
import unittest

from mplpb_answers.__main__ import main
from mplpb_answers.support import supported_answer
from mplpb_combined.ledger import write
from mplpb_combined.reader import answer as lexical_answer


class ReleaseAnswerContractTests(unittest.TestCase):
    QUESTION = 'What is the Aster service port?'

    def _cli(self, mode, root):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            code = main([mode, root, self.QUESTION, '--json'])
        return code, json.loads(output.getvalue())

    def test_misleading_scope_never_becomes_supported_answer(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, doc_id='T-0001', title='Aster', scope='Aster service port',
                  body='The Other service port is 8123.')
            self.assertEqual(lexical_answer(root, self.QUESTION).kind, 'return')
            supported = supported_answer(root, self.QUESTION)
            self.assertEqual(supported.kind, 'not_in_corpus')
            self.assertEqual((supported.text, supported.citation()), ('', ''))
            code, result = self._cli('ask', root)
            self.assertEqual((code, result['kind']), (3, 'not_in_corpus'))
            self.assertFalse(result.get('text'))
            code, inspection = self._cli('candidates', root)
            self.assertEqual((code, inspection['kind']), (0, 'return'))
            self.assertIs(inspection['answer_supported'], False)
            self.assertEqual(inspection['mode'], 'candidate_retrieval')

    def test_supported_body_and_ambiguous_competitor(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, doc_id='T-0001', title='Aster', scope='Aster service port',
                  body='The Aster service port is 8123.')
            code, result = self._cli('ask', root)
            self.assertEqual((code, result['kind']), (0, 'return'))
            self.assertEqual(result['answer_support']['status'], 'supported')
            write(root, doc_id='T-0002', title='Aster second note', scope='Aster service port',
                  body='The Aster service port is 9123.')
            code, result = self._cli('ask', root)
            self.assertEqual((code, result['kind']), (2, 'ambiguous'))
            self.assertFalse(result.get('text'))


if __name__ == '__main__':
    unittest.main()
