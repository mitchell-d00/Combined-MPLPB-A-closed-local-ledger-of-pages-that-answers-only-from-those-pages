import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_tools import primary_book_test as book_test


class PrimaryBookTest(unittest.TestCase):
    def test_batch_replay_score_and_integrity(self):
        raw = (
            '<html><body><p>The crew unloaded the largest wooden crates from the tall sailing ship. '
            'They brought the old maps inside and carefully counted the boxes before closing the doors.</p>'
            '<p>The clerk received several paper records at the entrance to the stone warehouse. '
            'She arranged the records in order and wrote the name of each captain in a separate book. '
            'The following morning she returned all of the signed receipts to the harbor office.</p>'
            '</body></html>'
        ).encode()
        digest = hashlib.sha256(raw).hexdigest()
        books = (('example', 'Example Author', 'Example Book', 'example_ed', 'a' * 40, (digest, digest)),)
        with tempfile.TemporaryDirectory() as temp, patch.object(book_test, 'BOOKS', books):
            root = Path(temp)
            for chapter in (1, 2):
                (root / f'example-chapter-{chapter}.xhtml').write_bytes(raw)
            first, replay = root / 'first', root / 'replay'
            for output in (first, replay):
                book_test.generate(output, '2a', root)
            inputs = first / 'engine-inputs'
            questions = book_test.read_json(inputs / 'questions.json')
            self.assertNotIn('seed', book_test.read_json(inputs / 'sources.json'))
            self.assertEqual(questions, book_test.read_json(replay / 'engine-inputs/questions.json'))
            self.assertEqual([row['id'] for row in questions], ['quote-01', 'quote-02'])
            key = book_test.read_json(first / 'custodian/answer-key.json')
            result = book_test.run(inputs, questions)
            self.assertEqual({row['outcome'] for row in book_test.score(result, key)},
                             {'withheld', 'correct_source_and_quote'})
            with self.assertRaisesRegex(ValueError, 'different question batches'):
                book_test.score(book_test.run(inputs, questions[::-1]), key)
            (inputs / 'BOOK-EXAMPLE.txt').write_text('Changed')
            with self.assertRaisesRegex(ValueError, 'Excerpt checksum mismatch'):
                book_test.run(inputs, questions)
            for chapter in (1, 2):
                (root / f'example-chapter-{chapter}.xhtml').write_text('Changed')
            with self.assertRaisesRegex(ValueError, 'Chapter checksum mismatch'):
                book_test.generate(root / 'corrupt', '2a', root)
