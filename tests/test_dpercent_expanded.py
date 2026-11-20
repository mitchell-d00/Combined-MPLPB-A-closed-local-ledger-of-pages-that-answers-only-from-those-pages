"""Authored generator invariants; no claim of independent semantic validation."""
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from tools import dpercent as base
from tools import dpercent_expanded as expanded


class ExpandedDiceTests(unittest.TestCase):
    def test_replay_seals_all_families_and_keeps_keys_separate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            seals = []
            for i in range(2):
                seals.append(expanded.prepare(root/f'public-{i}', root/f'private-{i}', 96, 9127))
                base.verify(root/f'public-{i}', root/f'private-{i}')
            self.assertEqual(seals[0], seals[1])
            keys = base.read(root/'private-0/key.json')['cases']
            self.assertEqual({k['family'] for k in keys}, set(base.FAMILIES) | set(expanded.FIELD_FAMILIES))
            public_names = base.files(root/'public-0')
            self.assertFalse(any('key.json' in p or 'dice.json' in p for p in public_names))
            for p in (root/'public-0/packets').iterdir():
                case = base.read(p/'case.json')
                self.assertNotIn('expected', case)
                self.assertNotIn('family', case)

    def test_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            expanded.prepare(root/'public', root/'private', 4, 11)
            path = next((root/'public/packets').rglob('case.json'))
            path.write_text(path.read_text()+' ')
            with self.assertRaises(ValueError):
                base.verify(root/'public', root/'private')

    def test_structural_draws_are_preserved_without_acceptance_filtering(self):
        signatures = set()
        for seed in range(100):
            dice = base.Dice(seed)
            case, docs, key = expanded.field_case(seed+1, 'field_literal', dice)
            signatures.add((case['question'], docs[0][1]))
            self.assertEqual(key['expected'], 'answer')
            self.assertIn(key['required_field_quotes'][0], docs[0][1].decode())
            self.assertGreater(len(dice.rolls), 4)
        self.assertGreater(len(signatures), 50)

    def test_invalid_limits_and_custody(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for n in (0, 4097):
                with self.assertRaises(ValueError):
                    expanded.prepare(root/'public', root/'private', n, 1)
            with self.assertRaises(ValueError):
                expanded.prepare(root/'public', root/'public/private', 1, 1)

    def test_scorer_checks_exact_values_and_does_not_award_missing_quotes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for i, (text, fidelity, expected_detection) in enumerate([
                    ('Owner: Alice', True, 1), ('Owner: Bob', True, 0),
                    ('Owner: Alice', False, 0)]):
                key = {'id': 'DP00001', 'family': 'field_literal', 'expected': 'answer',
                       'automatic_answer_matcher': 'literal_field_set_v1',
                       'required_field_quotes': ['Owner: Alice'],
                       'features': {'question_form': 0, 'field': 'Owner', 'line_ending': 'LF', 'fence': '```', 'source_count': 1}}
                base.save(root/f'private-{i}/key.json', {'cases': [key]})
                base.save(root/f'run-{i}/DP00001/result.json', {'answer': {'claims': [{'text': text}]}})
                result = {'cases': [{'id': 'DP00001', 'family': 'field_literal', 'expected': 'answer',
                           'execution': 'completed', 'answer_supported': True,
                           'quotation_fidelity': fidelity, 'outcome': 'supported_semantics_unscored'}], 'metrics': {}}
                with patch.object(base, 'score', return_value=result):
                    scored = expanded.score(root/'public', root/f'private-{i}', root/f'run-{i}', root/f'score-{i}.json')
                self.assertEqual(scored['metrics']['correct_complete_answers'], expected_detection)


if __name__ == '__main__':
    unittest.main()
