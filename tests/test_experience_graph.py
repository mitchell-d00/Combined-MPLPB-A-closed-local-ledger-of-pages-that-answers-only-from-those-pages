"""Live graph changes can direct inspection and preserve strict proof boundaries."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing, redirect_stdout
import io
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from mplpb_answers.__main__ import main
from mplpb_answers.advanced import advanced_query
from mplpb_answers.experience_graph import append, history, previous, read_pass
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import withdraw, write
from tests.test_general_answers import FixtureReader


class ExperienceGraphTests(unittest.TestCase):
    question = 'How should an operator restart safely?'

    def setUp(self):
        folder = TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.ledger = Path(folder.name) / 'ledger'
        self.graph = Path(folder.name) / 'experience.sqlite'

    def page(self, ident, body, scope='restart operator safely'):
        return write(self.ledger, doc_id=ident, title='Source text', scope=scope,
                     body=body, when='2026-11-24T00:00Z')

    def ask(self, **kwargs):
        return advanced_query(self.ledger, self.question, experience_graph=self.graph, **kwargs)

    def test_read_after_write_advances_existing_lookup_to_investigate(self):
        self.page('OPS-A', 'Drain the queue before restarting the worker.')
        strict = answer_query(self.ledger, self.question).contract
        first = self.ask()
        self.assertEqual(first['inspection']['path'], 'lookup')
        self.assertIn('lookup', first['experience']['graph']['nodes'][0]['flags'])
        self.assertEqual(first['inspection']['detail']['source_ids'], ['OPS-A'])
        original = read_pass(self.graph, first['experience']['pass_id'])
        self.assertEqual(original, first['experience']['graph'])
        second = self.ask()
        self.assertEqual(second['inspection']['path'], 'investigate')
        self.assertIn('investigate', second['experience']['graph']['nodes'][0]['flags'])
        self.assertFalse(second['inspection']['answer_supported'])
        self.assertEqual(second['strict'], strict)
        self.assertTrue(any(edge['kind'] == 'followed_by' for edge in second['experience']['graph']['edges']))
        self.assertEqual(read_pass(self.graph, first['experience']['pass_id']), original)

    def test_explicit_follow_up_still_controls_the_route(self):
        self.page('OPS-A', 'Drain the queue before restarting the worker.')
        self.ask()
        result = self.ask(follow_up='none')
        self.assertIsNone(result['inspection'])
        self.assertEqual(result['experience']['graph']['nodes'][0]['requested_flag'], 'none')
        self.assertFalse(result['answer_supported'])

    def test_changed_source_prevents_reuse_even_if_strict_outcome_matches(self):
        self.page('OPS-A', 'Drain the queue before restarting the worker.')
        first = self.ask()
        self.page('OTHER', 'The notice describes an unrelated room.', 'room')
        second = self.ask()
        self.assertEqual(second['inspection']['path'], 'lookup')
        self.assertFalse(any(node['type'] == 'previous_pass'
                             for node in second['experience']['graph']['nodes']))
        revised = read_pass(self.graph, second['flag_sync']['pass_id'], include_version=True)
        self.assertEqual(revised['version']['supersedes'], first['flag_sync']['pass_id'])
        withdraw(self.ledger, 'OPS-A')
        final = self.ask()
        self.assertFalse(final['answer_supported'])
        self.assertNotEqual(first['experience']['pass_id'], final['experience']['pass_id'])
        self.assertNotIn('Drain the queue', final['experience']['presentation']['text'])

    def test_verified_relation_has_native_citations_and_boundaries(self):
        self.page('R-A', 'The July 3 coastal meeting was moved to July 6. Its docket number remains CM-19.', 'meeting')
        self.page('R-B', 'Coastal meeting docket CM-19 opened July 6.', 'meeting')
        question = 'Do sources R-A and R-B describe the same event?'
        result = advanced_query(self.ledger, question, experience_graph=self.graph)
        self.assertTrue(result['answer_supported'])
        self.assertEqual(result['strict'], answer_query(self.ledger, question).contract)
        current = result['experience']
        nodes = current['graph']['nodes']
        self.assertEqual({node['source_id'] for node in nodes if node['type'] == 'source_span'}, {'R-A', 'R-B'})
        self.assertIn('documentary_event_identity', [node['relation'] for node in nodes if node['type'] == 'relation'])
        self.assertIn('Outside-world confirmation remains open.', current['presentation']['text'])
        self.assertTrue(any(edge['kind'] == 'bounded_by' for edge in current['graph']['edges']))

    def test_bad_graph_withholds_graph_scoped_proof_without_overwriting_file(self):
        self.page('P-A', 'The kettle color is blue.', 'kettle color')
        self.graph.write_bytes(b'Not a usable SQLite graph.')
        result = advanced_query(self.ledger, 'What is the kettle color?', experience_graph=self.graph)
        self.assertFalse(result['answer_supported'])
        self.assertEqual(result['strict']['diagnostic']['code'], 'FLAG_MISMATCH')
        self.assertEqual(result['strict']['claims'], [])
        self.assertTrue(answer_query(self.ledger, 'What is the kettle color?').contract['answer_supported'])
        self.assertEqual(self.graph.read_bytes(), b'Not a usable SQLite graph.')

    def test_fabricated_graph_text_cannot_become_proof(self):
        self.page('OPS-A', 'Drain the queue before restarting the worker.')
        first = self.ask()
        with closing(sqlite3.connect(self.graph)) as db, db:
            db.execute('UPDATE passes SET graph=? WHERE id=?',
                       (json.dumps({'proof': 'The operation happened.'}), first['flag_sync']['pass_id']))
        second = self.ask()
        self.assertNotIn('The operation happened.', json.dumps(second))
        self.assertEqual(second['strict']['diagnostic']['code'], 'FLAG_MISMATCH')
        self.assertFalse(second['answer_supported'])

    def test_mismatching_node_and_edge_flags_block_direct_strict_and_show_diff(self):
        self.page('P-A', 'The kettle color is blue.', 'kettle color')
        question = 'What is the kettle color?'
        first = answer_query(self.ledger, question, experience_graph=self.graph)
        self.assertTrue(first.contract['answer_supported'])
        path = read_pass(self.graph, first.sync['pass_id'])
        source = next(node for node in path['nodes'] if node['type'] == 'source_span')
        source['flags'].remove('eligible')
        source['flags'].append('retired')
        edge = next(edge for edge in path['edges'] if edge['kind'] == 'cites')
        edge['flags'].remove('eligible')
        with closing(sqlite3.connect(self.graph)) as db, db:
            db.execute('UPDATE passes SET graph=? WHERE id=?', (json.dumps(path), first.sync['pass_id']))
        second = answer_query(self.ledger, question, experience_graph=self.graph)
        self.assertEqual(second.contract['diagnostic']['code'], 'FLAG_MISMATCH')
        self.assertEqual(second.contract['claims'], [])
        self.assertEqual(second.contract['sources'], [])
        self.assertEqual(second.legacy()['text'], '')
        diff = second.sync['differences']
        self.assertTrue(any(row['path'][0] == 'edge' for row in diff))
        self.assertTrue(any('eligible' in row['missing_from_graph'] and 'retired' in row['extra_in_graph']
                            for row in diff))
        self.assertTrue(answer_query(self.ledger, question).contract['answer_supported'])

    def test_no_eligible_evidence_explains_void_without_requesting_guess(self):
        self.page('OPS-A', 'Drain the queue before restarting the worker.')
        withdraw(self.ledger, 'OPS-A')
        reader = FixtureReader('Unused')
        result = self.ask(follow_up='assisted', reader=reader)
        self.assertIsNone(result['inspection'])
        self.assertEqual(reader.calls, [])
        self.assertIsNone(result['flag_sync']['helper'])
        self.assertIn('No eligible source evidence', result['experience']['presentation']['text'])

    def test_cited_assisted_interpretation_stays_separate_when_requested(self):
        quote = 'Drain the queue before restarting the worker.'
        self.page('OPS-A', quote)
        result = self.ask(follow_up='assisted', reader=FixtureReader(quote))
        self.assertFalse(result['strict']['answer_supported'])
        self.assertEqual(result['strict']['claims'], [])
        self.assertEqual(result['inspection']['label'], 'Educated guess · cited interpretation')
        self.assertFalse(result['inspection']['answer_supported'])
        self.assertTrue(result['inspection']['detail']['claims'][0]['citations'])

    def test_strict_helper_suggests_proof_step_without_source_promotion(self):
        self.page('OPS-A', 'Drain the queue before restarting the worker.')
        result = answer_query(self.ledger, self.question, experience_graph=self.graph)
        self.assertFalse(result.contract['answer_supported'])
        helper = result.sync['helper']
        self.assertFalse(helper['answer_supported'])
        self.assertEqual(helper['citations'], [])
        self.assertEqual(helper['seam'], 'interpretation_unsupported')
        self.assertTrue(any(node['type'] == 'helper' for node in result.sync['path']['nodes']))

    def test_source_change_during_write_discards_presentation(self):
        self.page('P-A', 'The kettle color is blue.', 'kettle color')

        def changed(*args):
            pass_id = append(*args)
            withdraw(self.ledger, 'P-A')
            return pass_id

        with patch('mplpb_answers.experience_graph.append', side_effect=changed):
            result = advanced_query(self.ledger, 'What is the kettle color?', experience_graph=self.graph)
        self.assertEqual(result['status'], 'source_changed')
        self.assertIsNone(result['strict'])
        self.assertNotIn('experience', result)

    def test_sqlite_serializes_concurrent_passes(self):
        def record(_):
            return append(self.graph, 'scope', 'state', None, [], None, {'nodes': [], 'edges': []})
        with ThreadPoolExecutor(max_workers=4) as pool:
            ids = list(pool.map(record, range(8)))
        self.assertEqual(sorted(ids), list(range(1, 9)))

    def test_concurrent_strict_queries_share_one_current_version(self):
        self.page('P-A', 'The kettle color is blue.', 'kettle color')
        question = 'What is the kettle color?'
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda _: answer_query(self.ledger, question, experience_graph=self.graph),
                                    range(8)))
        self.assertTrue(all(result.contract['answer_supported'] for result in results))
        self.assertEqual(len({result.sync['pass_id'] for result in results}), 1)
        tags = results[0].sync['path']['system_tags']
        self.assertIn('pass:source-body', tags)
        self.assertIn('eligible', tags)

    def test_superseded_state_does_not_supply_routing_hints(self):
        graph = {'nodes': [], 'edges': []}
        first = append(self.graph, 'scope', 'first-state', 'lookup', ['OLD'], None, graph)
        second = append(self.graph, 'scope', 'next-state', None, [], None, graph)
        self.assertIsNone(previous(self.graph, 'scope', 'first-state'))
        versions = history(self.graph, first)
        self.assertEqual([(row['pass_id'], row['status']) for row in versions],
                         [(second, 'current'), (first, 'retired')])
        self.assertEqual(versions[0]['supersedes'], first)
        self.assertEqual(read_pass(self.graph, first), graph)

    def test_altered_inspection_flags_withhold_before_display(self):
        self.page('P-A', 'The kettle color is blue.', 'kettle color')

        def changed(*args):
            pass_id = append(*args)
            if len(args) == 7:  # The inspection appends after Strict's path is checked.
                path = read_pass(self.graph, pass_id)
                path['system_tags'].remove('eligible')
                with closing(sqlite3.connect(self.graph)) as db, db:
                    db.execute('UPDATE passes SET graph=? WHERE id=?', (json.dumps(path), pass_id))
            return pass_id

        with patch('mplpb_answers.experience_graph.append', side_effect=changed):
            result = advanced_query(self.ledger, 'What is the kettle color?', experience_graph=self.graph)
        self.assertEqual(result['strict']['diagnostic']['code'], 'FLAG_MISMATCH')
        self.assertEqual(result['strict']['claims'], [])
        self.assertEqual(result['flag_sync']['differences'][0]['missing_from_graph'], ['eligible'])

    def test_altered_route_summary_cannot_direct_another_pass(self):
        self.page('OPS-A', 'Drain the queue before restarting the worker.')
        first = self.ask()
        with closing(sqlite3.connect(self.graph)) as db, db:
            db.execute('UPDATE passes SET candidates=? WHERE id=?',
                       (json.dumps(['ALTERED']), first['experience']['pass_id']))
        result = self.ask()
        self.assertEqual(result['strict']['diagnostic']['code'], 'FLAG_MISMATCH')
        self.assertIsNone(result['inspection'])

    def test_cli_reads_a_committed_graph_pass(self):
        self.page('OPS-A', 'Drain the queue before restarting the worker.')
        output = io.StringIO()
        with redirect_stdout(output):
            main(['advanced', str(self.ledger), self.question, '--experience-graph', str(self.graph), '--json'])
        saved = json.loads(output.getvalue())['experience']
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(['experience-pass', str(self.graph), str(saved['pass_id'])]), 0)
        restored = json.loads(output.getvalue())
        self.assertEqual(restored.pop('version')['pass_id'], saved['pass_id'])
        self.assertEqual(restored, saved['graph'])
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(['experience-pass', str(self.graph), str(saved['pass_id']), '--history']), 0)
        self.assertEqual(json.loads(output.getvalue())[0]['status'], 'current')
