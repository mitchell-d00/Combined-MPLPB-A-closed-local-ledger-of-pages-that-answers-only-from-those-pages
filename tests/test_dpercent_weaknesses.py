import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from copy import deepcopy
from tools import dpercent as D
from tools import dpercent_expanded as E
from tools import dpercent_weaknesses as W
from tools import dpercent_weakness_batch as B
from mplpb_work import sorter_v2 as S


class WeaknessStudyTests(unittest.TestCase):
    def test_worker_mounts_verified_executor_owned_staging(self):
        from types import SimpleNamespace
        from tools import study_sandbox

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            public, key, results = root/'packets', root/'key', root/'results'
            manifest = W.prepare(public, key, count=1, seed=31)
            shard = public / manifest['shards'][0]['name']
            original, = (shard/'packets').iterdir()

            def command(bwrap, code, inputs, outputs, program):
                self.assertNotEqual(inputs, original)
                self.assertEqual(inputs.parent.parent, code.parent)
                self.assertEqual(outputs.parent, inputs.parent)
                self.assertEqual(D.files(inputs), D.files(original))
                D.save(outputs/'result.json', {'case_id': original.name})
                return ['mock-bwrap']

            run = D.subprocess.run
            with patch.object(study_sandbox, 'command', side_effect=command), patch.object(
                D.subprocess, 'run', side_effect=lambda args, *a, **k:
                SimpleNamespace(returncode=0) if args == ['mock-bwrap'] else run(args, *a, **k)
            ), patch.object(D.shutil, 'which', return_value='mock-bwrap'), patch.object(
                D.subprocess, 'check_output', return_value='fixture-revision\n'):
                result = D.run(shard, results)
            self.assertEqual(result['cases'][0]['execution'], 'completed')
            self.assertEqual(D.read(results/original.name/'result.json'), {'case_id': original.name})

    def test_batch_exit_distinguishes_failed_workers_from_scored_misses(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            public, key, results = root/'packets', root/'key', root/'results'
            packet = W.prepare(public, key, count=1, seed=31)
            (results/packet['shards'][0]['name']).mkdir(parents=True)
            for outcome, code in (('execution_failure', 1), ('invalid_output', 1), ('over_refusal', 0)):
                with self.subTest(outcome=outcome), patch.object(
                    W, 'summarize', return_value={'partial': False, 'by_family': {'class': {'outcomes': {outcome: 1}}}}
                ):
                    self.assertEqual(B.run(public, key, results), code)

    def test_registry_keeps_every_previous_family(self):
        self.assertTrue(set(D.FAMILIES) <= set(W.FAMILIES))
        self.assertTrue(set(E.FIELD_FAMILIES) <= set(W.FAMILIES))
        self.assertEqual(len(W.FAMILIES), len(set(W.FAMILIES)))
        self.assertTrue(W.PENDING)

    def test_prepare_replay_balanced_and_separate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            count = 2*len(W.FAMILIES)
            a = W.prepare(root/'a', root/'ka', count, 17, 80)
            b = W.prepare(root/'b', root/'kb', count, 17, 80)
            self.assertEqual(a, b)
            self.assertEqual(set(a['family_counts'].values()), {2})
            self.assertEqual(D.files(root/'a'), D.files(root/'b'))
            for shard in a['shards']:
                public = root/'a'/shard['name']; private = root/'ka'/shard['name']
                D.verify(public, private)
                self.assertFalse((public/'key.json').exists())
                self.assertFalse((public/'dice.json').exists())
                for folder in (public/'packets').iterdir():
                    self.assertEqual(sorted(p.name for p in folder.iterdir()), ['case.json', 'sources'])
            (root/'a'/'study.json').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'manifest'):
                W.execute_shards(root/'a', root/'ka', root/'run')

    def test_all_sorter_classes_have_inspectable_obligations(self):
        failures = []
        for number, family in enumerate(W.SORTER, 1):
            with self.subTest(family=family), tempfile.TemporaryDirectory() as temp:
                case, documents, key = W.material(number, 'sorter_'+family, D.Dice(271+number))
                root = Path(temp)
                for source, raw in documents:
                    path = root/source['path']; path.parent.mkdir(exist_ok=True); path.write_bytes(raw)
                left = S.sort_directory(root/'sources', 'not-compared')
                right = S.sort_directory(root/'sources', 'compare')
                self.assertEqual(left['nodes'], right['nodes'])
                self.assertEqual(left['sources'], right['sources'])
                self.assertFalse(any(e.get('comparison_only') for e in left['edges']))
                self.assertTrue(right['nodes'])
                # Each original UTF-8 byte slice and character slice must agree.
                for node in right['nodes']:
                    span = node['span']; raw = (root/'sources'/span['path']).read_bytes()
                    char = raw.decode()[span['char_start']:span['char_end']]
                    self.assertEqual(raw[span['byte_start']:span['byte_end']].decode(), char)
                    if 'text' in span: self.assertEqual(span['text'], char)
                right.update(nodes_identical_between_modes=True, node_labels_identical_between_modes=True,
                             all_labels_non_authoritative=True)
                checks = W.graph_checks(right, key['structural_expectations'])
                if not all(checks.values()): failures.append((family, checks))
                self.assertEqual(case['budget'], {'passages': 12, 'characters': 8000})
        # These tests verify the harness against declared obligations. Actual
        # product failures belong in frozen execution findings, not hidden here.
        self.assertEqual(failures, [])

    def test_empty_graph_cannot_satisfy_positive_discovery(self):
        _, _, key = W.material(1, 'sorter_duplicate_appearance', D.Dice(1))
        graph = {'nodes': [], 'edges': [], 'complete': True, 'nodes_identical_between_modes': True,
                 'node_labels_identical_between_modes': True, 'all_labels_non_authoritative': True}
        self.assertFalse(all(W.graph_checks(graph, key['structural_expectations']).values()))

    def test_scoring_accepts_different_feature_schemas_without_hiding_misses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); keys = root/'keys'; run = root/'run'; keys.mkdir(); run.mkdir()
            D.save(keys/'key.json', {'cases': [
                {'id': 'A', 'expected': 'answer', 'features': {'reference_punctuation': ';'}, 'automatic_answer_matcher': 'literal_field_set_v1', 'required_field_quotes': ['Deposit Date: 1850-01-01']},
                {'id': 'B', 'expected': 'answer', 'features': {}, 'automatic_answer_matcher': 'literal_field_set_v1', 'required_field_quotes': ['Deposit Date: 1850-01-01']}]})
            D.save(run/'run.json', {'partial': False})
            for ident in ('A', 'B'):
                (run/ident).mkdir()
                D.save(run/ident/'result.json', {'answer': {'claims': [{'text': 'Deposit Date: 1850-01-01', 'citations': [{'source_id': 'original'}]}]}})
            base = {'metrics': {}, 'cases': [
                {'id': 'A', 'family': 'alias_test', 'execution': 'completed', 'answer_supported': True, 'expected': 'answer', 'quotation_fidelity': True, 'outcome': 'supported_semantics_unscored'},
                {'id': 'B', 'family': 'alias_test', 'execution': 'completed', 'answer_supported': False, 'expected': 'answer', 'quotation_fidelity': True, 'outcome': 'over_refusal'}]}
            with patch.object(D, 'score', return_value=deepcopy(base)):
                report = W.score_shard(root/'public', keys, run, root/'score.json')
            self.assertEqual(report['metrics']['correct_complete_answers'], 1)
            self.assertEqual(report['metrics']['E'], .5)
            self.assertEqual(report['metrics']['E_lower_bound'], .5)
            self.assertEqual(report['metrics']['by_family']['alias_test']['detected_answer'], 1)
            self.assertEqual(report['cases'][1]['outcome'], 'over_refusal')
            self.assertNotIn('field', report['cases'][0]['features'])

    def test_partial_run_keeps_unexecuted_cases_out_of_executed_total(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); public = root/'public'; keys = root/'keys'; run = root/'run'
            manifest = W.prepare(public, keys, count=2, seed=31, shard_size=2)
            name = manifest['shards'][0]['name']; (run/name).mkdir(parents=True)
            D.save(run/name/'run.json', {'partial': True, 'cases': [],
                'packet_seal_sha256': D.sha((public/name/'seal.json').read_bytes())})
            score = W.score_shard(public/name, keys/name, run/name, run/(name+'-score.json'))
            summary = W.summarize(public, keys, run)
            self.assertIsNone(score['metrics']['E'])
            self.assertEqual(summary['executed'], 0)
            self.assertEqual(summary['completed'], 0)
            self.assertEqual(summary['execution_failed'], 0)
            self.assertEqual(summary['not_run'], 2)
            self.assertTrue(summary['partial'])

    def test_unknown_legacy_obligation_fails_closed(self):
        graph = {'nodes': [], 'edges': [], 'complete': True, 'nodes_identical_between_modes': True,
                 'node_labels_identical_between_modes': True, 'all_labels_non_authoritative': True}
        self.assertFalse(all(W.graph_checks(graph, {'new_unrecognized_requirement': True}).values()))

    def test_limits_and_custody_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for kwargs in ({'count': 0}, {'shard_size': 0}, {'seed': -1}):
                with self.assertRaises(ValueError): W.prepare(root/'p', root/'k', **kwargs)
            with self.assertRaises(ValueError): W.prepare(root/'p', root/'p'/'k')


if __name__ == '__main__': unittest.main()
