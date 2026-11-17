"""Offline sorter fixtures establish textual fidelity/boundaries, not history."""
import contextlib
import copy
import hashlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from mplpb_work import sorter as S
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import Ledger
from mplpb_combined.reader import PROFILES

FIXTURES=Path(__file__).parent/'fixtures'/'sorter'


class SorterTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name);self.root=self.base/'sources';self.root.mkdir()

    def put(self,name,text):
        path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(text if isinstance(text,bytes) else text.encode('utf-8'));return path

    def fixtures(self):
        for path in FIXTURES.iterdir():self.put(path.name,path.read_bytes())

    def graph(self,mode='compare',**kw):return S.sort_directory(self.root,mode,**kw)

    def scope_fixtures(self):
        for path in (FIXTURES.parent/'sorter_header_scope').iterdir():
            self.put(path.name,path.read_bytes())

    def test_fenced_example_is_observation_not_primary_identity_member(self):
        self.scope_fixtures();raw=self.graph('not-compared');compared=self.graph()
        self.assertEqual(raw['sources'],compared['sources'])
        self.assertEqual(raw['nodes'],compared['nodes'])
        self.assertEqual(raw['edges'],compared['edges'][:len(raw['edges'])])
        by_id={n['id']:n for n in compared['nodes']}
        cluster=next(e for e in compared['edges'] if e['kind']=='candidate_identity_cluster')
        paths={by_id[n]['span']['path'] for n in cluster['members']}
        self.assertEqual(paths,{'01-original.md','02-repeated.md'})
        example=next(n for n in compared['nodes'] if n['kind']=='header_identifier' and n['span']['path']=='03-example.md')
        self.assertEqual(example['header_role'],'embedded_text_observation')
        self.assertFalse(example['primary_identity_eligible'])
        self.assertEqual(example['span']['text'],'MAIL-001')
        occurrence=by_id[example['occurrence']]
        self.assertEqual(occurrence['identity_role'],'textual_appearance_only')
        self.assertEqual(S.verify_graph(compared,self.root)['status'],'source_fidelity_replayed')

    def test_embedded_header_does_not_partition_real_record_occurrences(self):
        self.put('records.md','Message-ID: REAL-001\nSubject: First\n\nThe initial account.\n\n```text\nMessage-ID: FAKE-001\nSubject: Example\n```\n\nMessage-ID: REAL-002\nSubject: Second\n\nThe later account.')
        graph=self.graph();occ=[n for n in graph['nodes'] if n['kind']=='source_occurrence']
        self.assertEqual(len(occ),2)
        embedded=next(n for n in graph['nodes'] if n['kind']=='header_identifier' and n['value']=='FAKE-001')
        self.assertFalse(embedded['primary_identity_eligible'])
        self.assertEqual(embedded['occurrence'],occ[0]['id'])
        real=next(n for n in graph['nodes'] if n['kind']=='header_identifier' and n['value']=='REAL-002')
        self.assertEqual(occ[1]['span']['char_start'],graph['sources'][0]['bytes']-len('Message-ID: REAL-002\nSubject: Second\n\nThe later account.'))
        self.assertEqual(real['occurrence'],occ[1]['id'])

    def assert_scope_invariants(self):
        before={p.name:p.read_bytes() for p in self.root.iterdir() if p.is_file()}
        raw=self.graph('not-compared');graph=self.graph()
        self.assertEqual(raw['sources'],graph['sources']);self.assertEqual(raw['nodes'],graph['nodes'])
        self.assertEqual(raw['edges'],graph['edges'][:len(raw['edges'])])
        self.assertTrue(all(e['comparison_only'] for e in graph['edges'][len(raw['edges']):]))
        for item in graph['sources']+graph['nodes']+graph['edges']+[graph]:
            for flag in ('answer_supported','source_support_established','historical_truth_independently_verified'):
                self.assertIs(item['assessment'][flag],False)
        for node in graph['nodes']:
            span=node['span'];source=before[span['path']]
            if 'text' in span:
                self.assertEqual(source[span['byte_start']:span['byte_end']].decode('utf-8'),span['text'])
                self.assertEqual(source.decode('utf-8')[span['char_start']:span['char_end']],span['text'])
        self.assertEqual(S.verify_graph(graph,self.root)['status'],'source_fidelity_replayed')
        self.assertEqual(graph,self.graph())
        self.assertEqual(before,{p.name:p.read_bytes() for p in self.root.iterdir() if p.is_file()})
        return graph

    def test_structural_header_role_keeps_real_identifiers_despite_quoted_body(self):
        body='Message-ID: MAIL-001\nSubject: Deployment\nAlice wrote “the notice is ready”.'
        self.put('a.md',body);self.put('b.md',body)
        graph=self.assert_scope_invariants()
        ids=[n for n in graph['nodes'] if n['kind']=='header_identifier']
        self.assertTrue(all(n['primary_identity_eligible'] for n in ids))
        self.assertTrue(all(n['scope']!='unqualified_text' for n in ids))
        cluster=next(e for e in graph['edges'] if e['kind']=='candidate_identity_cluster')
        self.assertEqual(len(cluster['members']),2)

    def test_backtick_tilde_and_longer_nested_fences_keep_only_real_boundaries(self):
        for marker in ('```','~~~','````'):
            with self.subTest(marker=marker):
                body='Message-ID: REAL-001\n\nFirst body.\n\n'+marker+'text\nMessage-ID: FAKE-001\n'+marker+'not-a-closer\nMessage-ID: FAKE-002\n'+marker+'\n\nMessage-ID: REAL-002\n\nSecond body.'
                self.put('records.md',body);graph=self.assert_scope_invariants()
                self.assertEqual(len([n for n in graph['nodes'] if n['kind']=='source_occurrence']),2)
                headers={n['value']:n for n in graph['nodes'] if n['kind']=='header_identifier'}
                self.assertTrue(headers['REAL-001']['primary_identity_eligible']);self.assertTrue(headers['REAL-002']['primary_identity_eligible'])
                self.assertFalse(headers['FAKE-001']['primary_identity_eligible']);self.assertFalse(headers['FAKE-002']['primary_identity_eligible'])

    def test_blockquotes_forwarded_and_delimited_quotes_preserve_header_observations(self):
        wrappers=[('> Message-ID: MAIL-001\n> Subject: Deployment\n> Copied only.','blockquote_context'),
                  ('-----Original Message-----\nMessage-ID: MAIL-001\nSubject: Deployment\nCopied only.\n-----End original message-----','forwarded_or_quoted_context'),
                  ('Begin forwarded message:\nMessage-ID: MAIL-001\nCopied only.\n# Documentation example\nEnd forwarded message','forwarded_or_quoted_context'),
                  ('On Monday Alice wrote:\nMessage-ID: MAIL-001\nCopied only.\nEnd quote','forwarded_or_quoted_context'),
                  ('“\nMessage-ID: MAIL-001\nCopied only.\n”','quotation_context')]
        self.put('a.md','Message-ID: MAIL-001\n\nThe original notice.')
        self.put('b.md','Message-ID: MAIL-001\n\nThe original notice.')
        for wrapper,context in wrappers:
            with self.subTest(context=context,wrapper=wrapper):
                self.put('quoted.md',wrapper);graph=self.assert_scope_invariants()
                quoted=next(n for n in graph['nodes'] if n['kind']=='header_identifier' and n['span']['path']=='quoted.md')
                self.assertEqual(quoted['header_context'],context);self.assertFalse(quoted['primary_identity_eligible'])
                cluster=next(e for e in graph['edges'] if e['kind']=='candidate_identity_cluster')
                self.assertEqual(len(cluster['members']),2)
                review=next(e for e in graph['edges'] if e['kind']=='embedded_identifier_review' and e['from']==quoted['id'])
                self.assertEqual(set(review['matching_primary_occurrences']),set(cluster['members']))

    def test_example_heading_and_unfenced_example_introduction_are_not_declarations(self):
        self.put('a.md','Message-ID: MAIL-001\n\nOriginal.');self.put('b.md','Message-ID: MAIL-001\n\nOriginal.')
        for intro in ('# Documentation example\n','The following sample is not a source communication.\n'):
            self.put('example.md',intro+'Message-ID: MAIL-001\n\nDemonstration only.')
            graph=self.assert_scope_invariants();cluster=next(e for e in graph['edges'] if e['kind']=='candidate_identity_cluster')
            self.assertEqual(len(cluster['members']),2)
            occurrence=next(n for n in graph['nodes'] if n['kind']=='source_occurrence' and n['span']['path']=='example.md')
            self.assertEqual(occurrence['identity_role'],'textual_appearance_only')

    def test_unclosed_forward_and_fence_do_not_escape_via_nested_heading(self):
        for opening in ('-----Original Message-----','~~~text'):
            self.put('nested.md','Message-ID: REAL-001\n\nOuter.\n\n'+opening+'\nMessage-ID: COPY-001\n\n# Nested content\nMessage-ID: COPY-002\n')
            graph=self.assert_scope_invariants()
            self.assertEqual(len([n for n in graph['nodes'] if n['kind']=='source_occurrence']),1)
            copies=[n for n in graph['nodes'] if n['kind']=='header_identifier' and n['value'].startswith('COPY')]
            self.assertEqual(len(copies),2);self.assertTrue(all(not n['primary_identity_eligible'] for n in copies))

    def test_embedded_status_and_date_do_not_classify_outer_document(self):
        self.put('example.md','```text\nMessage-ID: MAIL-001\nStatus: retired\nDate sent: June 3, 1841\n```')
        graph=self.assert_scope_invariants();occ=next(n for n in graph['nodes'] if n['kind']=='source_occurrence')
        self.assertEqual(occ['declared_status_candidates'],[])
        self.assertEqual(occ['provisional_ledger_status'],'undetermined_candidate')
        self.assertTrue(all(n['date_role']=='unresolved' for n in graph['nodes'] if n['kind']=='date_expression'))
        self.assertTrue(any(n['kind']=='declared_status' and n['span']['text']=='retired' for n in graph['nodes']))

    def test_real_correction_ignores_embedded_target_and_quoted_correction_stays_review_only(self):
        self.put('original.md','Document-ID: REC-001\n\nTwelve crates were requested.')
        self.put('example.md','```text\nDocument-ID: REC-001\n```')
        self.put('correction.md','Document-ID: NOTE-001\n\nCorrection to REC-001 changes only the requested count to ten crates.')
        self.put('quoted.md','Document-ID: NOTE-002\n\n-----Original Message-----\nCorrection to REC-001 changes only the destination.\n-----End original message-----')
        graph=self.assert_scope_invariants();nodes={n['id']:n for n in graph['nodes']}
        corrections=[e for e in graph['edges'] if e['kind']=='possible_partial_correction']
        self.assertEqual(len(corrections),1)
        self.assertEqual(nodes[corrections[0]['from']]['span']['path'],'correction.md')
        self.assertEqual(nodes[corrections[0]['to']]['span']['path'],'original.md')
        quoted_ref=next(n for n in graph['nodes'] if n['kind']=='reference_mention' and n['span']['path']=='quoted.md')
        review=next(e for e in graph['edges'] if e['kind']=='unresolved_reference_review' and e['from']==quoted_ref['id'])
        self.assertEqual(review['reason'],'qualified_or_quoted_reference')

    def test_embedded_only_target_is_not_resolved_as_a_primary_record(self):
        self.put('quote.md','~~~\nDocument-ID: REC-001\n~~~')
        self.put('correction.md','Document-ID: NOTE-001\n\nCorrection to REC-001 changes only the count.')
        graph=self.assert_scope_invariants()
        review=next(e for e in graph['edges'] if e['kind']=='unresolved_reference_review')
        self.assertEqual(review['reason'],'embedded_only_target')
        self.assertFalse(any(e['kind'].startswith('possible_') for e in graph['edges']))

    def test_different_identifiers_with_identical_subject_and_body_never_merge(self):
        body='Subject: Same title\n\nThe clerk sent the notice.'
        self.put('a.md','Message-ID: FIRST-001\n'+body)
        self.put('b.md','Message-ID: SECOND-001\n'+body)
        graph=self.assert_scope_invariants()
        self.assertFalse(any(e['kind']=='candidate_identity_cluster' for e in graph['edges']))
        self.assertTrue(any(e['kind']=='shared_header_review' for e in graph['edges']))

    def test_scoped_unicode_crlf_headers_keep_exact_original_coordinates(self):
        self.put('a.md','\ufeffMessage-ID: MAIL-001\r\nSubject: Réception 🌍\r\n\r\nÉmile sent a notice.\r\n')
        self.put('b.md','Message-ID: MAIL-001\nSubject: Réception 🌍\n\nÉmile sent a changed notice.\n')
        self.put('example.md','# Documentation example\r\n~~~text\r\nMessage-ID: MAIL-001\r\nSubject: Zoë\r\n~~~\r\n')
        graph=self.assert_scope_invariants();cluster=next(e for e in graph['edges'] if e['kind']=='candidate_identity_cluster')
        self.assertEqual(len(cluster['members']),2);self.assertTrue(cluster['changed_bodies'])
        bad=copy.deepcopy(graph)
        next(n for n in bad['nodes'] if n['kind']=='header_identifier' and n['span']['path']=='example.md')['primary_identity_eligible']=True
        bad['graph_sha256']=S.digest({k:v for k,v in bad.items() if k!='graph_sha256'})
        with self.assertRaises(S.SortError):S.verify_graph(bad,self.root)

    def test_comparison_budget_does_not_change_extracted_header_roles(self):
        self.scope_fixtures()
        raw=self.graph('not-compared',limits={'comparisons':1});graph=self.graph(limits={'comparisons':1})
        self.assertEqual(raw['nodes'],graph['nodes']);self.assertEqual(raw['sources'],graph['sources'])
        self.assertIn('comparison_budget',graph['limits_or_exclusions'])

    def test_bom_at_example_container_start_does_not_hide_scope(self):
        self.put('a.md','Message-ID: MAIL-001\n\nOriginal.');self.put('b.md','Message-ID: MAIL-001\n\nOriginal.')
        for example in ('\ufeff```text\r\nMessage-ID: MAIL-001\r\n```','\ufeff# Documentation example\nMessage-ID: MAIL-001','\ufeff> Message-ID: MAIL-001'):
            self.put('example.md',example);graph=self.assert_scope_invariants()
            self.assertEqual(len(next(e for e in graph['edges'] if e['kind']=='candidate_identity_cluster')['members']),2)

    def test_nested_forward_closing_only_inner_message_does_not_expose_outer_quote(self):
        self.put('nested.md','Message-ID: REAL-001\n\nOuter.\n\nBegin forwarded message:\nMessage-ID: COPY-001\n\nBegin forwarded message:\nMessage-ID: COPY-002\n# Documentation example\nEnd forwarded message\nMessage-ID: COPY-003\nEnd forwarded message\n\nMessage-ID: REAL-002\n\nNew record.')
        graph=self.assert_scope_invariants()
        self.assertEqual(len([n for n in graph['nodes'] if n['kind']=='source_occurrence']),2)
        headers={n['value']:n for n in graph['nodes'] if n['kind']=='header_identifier'}
        self.assertTrue(headers['REAL-002']['primary_identity_eligible'])
        self.assertTrue(all(not headers[n]['primary_identity_eligible'] for n in ('COPY-001','COPY-002','COPY-003')))

    def test_stages_are_inspectable_without_resolving_identity_or_authority(self):
        self.fixtures();limits=S.limits_for()
        extracted=S.extract(self.root,limits)
        self.assertFalse(any(n['kind']=='candidate_identity_cluster' for n in extracted['nodes']))
        self.assertTrue(all(n['assessment']['status']=='unassessed_candidate' for n in extracted['nodes']))
        S.assign_statuses(extracted)
        self.assertTrue(any(n['assessment']['status']=='possible_event_candidate' for n in extracted['nodes']))
        graph=S.emit_graph(extracted,'not-compared',limits)
        self.assertFalse(graph['comparison_performed']);self.assertFalse(graph['assessment']['answer_supported'])
        self.assertTrue(any(n.get('provisional_ledger_status')=='current_candidate' for n in graph['nodes']))

    def test_emission_rejects_a_caller_promoting_candidate_status(self):
        self.put('a.txt','The clerk sent the report.')
        limits=S.limits_for();data=S.assign_statuses(S.extract(self.root,limits))
        data['nodes'][0]['assessment']['answer_supported']=True
        with self.assertRaises(S.SortError):S.emit_graph(data,'not-compared',limits)

    def test_urls_are_literal_offline_mentions_not_fetches(self):
        self.put('url.txt','See https://example.org/archive/record for context.')
        with patch('urllib.request.urlopen',side_effect=AssertionError('network call')):
            with patch('socket.create_connection',side_effect=AssertionError('network call')):
                graph=self.graph()
        url=next(n for n in graph['nodes'] if n['kind']=='literal_url')
        self.assertFalse(url['fetched'])

    def test_both_modes_keep_identical_sources_keys_and_distinct_occurrences(self):
        self.fixtures();a=self.graph('not-compared');b=self.graph()
        self.assertEqual(a['sources'],b['sources'])
        self.assertEqual(a['nodes'],b['nodes'])
        self.assertEqual(json.dumps(a['nodes']),json.dumps(b['nodes']))
        self.assertEqual(a['edges'],b['edges'][:len(a['edges'])])
        self.assertTrue(all(e['comparison_only'] for e in b['edges'][len(a['edges']):]))
        self.assertFalse(a['comparison_performed']);self.assertTrue(b['comparison_performed'])
        self.assertTrue(a['complete']);self.assertTrue(b['complete'])
        self.assertEqual(len([n for n in a['nodes'] if n['kind']=='source_occurrence']),8)
        self.assertNotIn('candidate_identity_cluster',{n['kind'] for n in a['nodes']})
        self.assertTrue({e['kind'] for e in a['edges']} <= {'contains_statement','contains_extracted_item','textual_cooccurrence'})
        self.assertTrue(all('resolution' not in n for n in a['nodes']))

    def test_identical_message_appearances_remain_distinct_and_not_independent_events(self):
        data='Message-ID: MSG-001\nSubject: Same\n\nThe clerk sent the report.\n'
        self.put('a.txt',data);self.put('b.txt',data)
        g=self.graph();occ=[n for n in g['nodes'] if n['kind']=='source_occurrence'];clusters=[e for e in g['edges'] if e['kind']=='candidate_identity_cluster']
        self.assertEqual(len(occ),2);self.assertNotEqual(occ[0]['id'],occ[1]['id'])
        self.assertEqual(len(clusters),1);self.assertFalse(clusters[0]['changed_bodies'])
        self.assertTrue(all(n['event_identity'] is None and not n['independent_event_established'] for n in occ))
        self.assertEqual(set(clusters[0]['members']),{n['id'] for n in occ})

    def test_changed_bodies_under_same_identifier_require_review_without_merging(self):
        self.put('a.txt','Message-ID: MSG-001\nSubject: Cargo\n\nThe clerk sent twelve crates.')
        self.put('b.txt','Message-ID: MSG-001\nSubject: Cargo\n\nThe clerk sent ten crates.')
        g=self.graph();cluster=next(e for e in g['edges'] if e['kind']=='candidate_identity_cluster')
        self.assertTrue(cluster['changed_bodies']);self.assertEqual(cluster['assessment']['status'],'needs_review')
        self.assertEqual(len(cluster['members']),2)
        self.assertTrue(any(e['kind']=='shared_header_review' and e['changed_bodies'] for e in g['edges']))

    def test_subject_alone_never_builds_identity_cluster_or_chronology(self):
        self.put('a.txt','Subject: Same title\nDate: June 3, 1841\n\nThe clerk sent a crate.')
        self.put('b.txt','Subject: Same title\nDate: June 3, 1941\n\nThe sailor arrived in port.')
        g=self.graph();self.assertFalse(any(e['kind']=='candidate_identity_cluster' for e in g['edges']))
        self.assertTrue(any(e['kind']=='shared_header_review' for e in g['edges']))
        self.assertFalse(any('before' in e['kind'] or 'after' in e['kind'] for e in g['edges']))

    def test_partial_correction_window_does_not_retire_original_or_rewrite_claims(self):
        self.fixtures();g=self.graph()
        edge=next(e for e in g['edges'] if e['kind']=='possible_partial_correction')
        self.assertEqual(edge['correction_window']['expressions'],{'from_expression':'June 5, 1841','until_expression':'June 7, 1841'})
        self.assertFalse(edge['correction_window']['applied'])
        self.assertIn('only the requested count',edge['claim_scope_quote'])
        target=next(n for n in g['nodes'] if n['id']==edge['to'])
        self.assertIn({'value':'current','evidence_node':target['declared_status_candidates'][0]['evidence_node']},target['declared_status_candidates'])
        old=next(n for n in g['nodes'] if n['kind']=='statement' and 'twelve crates for' in n['span']['text'])
        self.assertIn('destination remains',old['span']['text'])
        self.assertFalse(old['assessment']['source_support_established'])

    def test_missing_intermediate_never_becomes_resolved_reference_to_similar_document(self):
        self.put('a.txt','Message-ID: MSG-001\n\nSee ABSENT-009 for the next record.\nThe same distinctive phrase remains here.')
        self.put('c.txt','Message-ID: MSG-003\n\nThe same distinctive phrase remains here.')
        g=self.graph();ref=next(n for n in g['nodes'] if n['kind']=='reference_mention')
        review=next(e for e in g['edges'] if e['kind']=='unresolved_reference_review' and e['from']==ref['id'])
        self.assertEqual(review['reason'],'missing_or_outside_budget')
        self.assertFalse(any(e['kind']=='explicit_reference_candidate' for e in g['edges']))
        self.assertFalse(g['transitive_paths_generated'])
        self.assertTrue(any(n['kind']=='phrase_key' for n in g['nodes']))

    def test_ambiguous_identifier_keeps_correction_wording_without_guessing_target(self):
        self.fixtures();self.put('ambiguous.txt','Message-ID: NOTE-005\n\nCorrection to MAIL-001 changes only the count. Effective from June 8, 1841.')
        g=self.graph();ref=next(n for n in g['nodes'] if n['kind']=='reference_mention' and n['span']['path']=='ambiguous.txt')
        review=next(e for e in g['edges'] if e['kind']=='unresolved_reference_review' and e['from']==ref['id'])
        self.assertEqual(review['reason'],'ambiguous_identifier')
        self.assertIn('June 8, 1841',review['correction_window']['expressions']['from_expression'])
        self.assertFalse(any(e['kind'].startswith('possible_') and e['from']==ref['occurrence'] for e in g['edges']))

    def test_negated_conditional_and_quoted_corrections_not_positive_edges(self):
        self.fixtures();g=self.graph()
        refs=[n for n in g['nodes'] if n['kind']=='reference_mention' and n['span']['path']=='07_negated.txt']
        self.assertTrue(refs)
        self.assertTrue(all(n['scope']!='unqualified_text' for n in refs))
        self.assertFalse(any(e['kind'].startswith('possible_') and e['from']==refs[0]['occurrence'] for e in g['edges']))

    def test_fenced_correction_remains_scope_unresolved_across_blank_lines(self):
        self.put('original.txt','Document-ID: REC-001\n\nThe original account.')
        self.put('quoted.md','Message-ID: NOTE-001\n\n```text\n\nCorrection to REC-001 changes only the count.\n\n```')
        g=self.graph();ref=next(n for n in g['nodes'] if n['kind']=='reference_mention')
        self.assertEqual(ref['scope'],'quoted_or_format_scope_unresolved')
        self.assertFalse(any(e['kind'].startswith('possible_') for e in g['edges']))

    def test_utf8_bom_crlf_and_multibyte_spans_round_trip_without_normalizing(self):
        path=self.put('accent.md','\ufeffSubject: Réception\r\nDate received: June 3, 1841\r\n\r\nÉmile wrote “merci” to Zoë.\r\n')
        raw=path.read_bytes();text=raw.decode('utf-8');g=self.graph()
        self.assertEqual(path.read_bytes(),raw)
        self.assertEqual(g['sources'][0]['raw_sha256'],S.sha(raw))
        for node in g['nodes']:
            span=node.get('span')
            if span and 'text' in span:
                self.assertEqual(text[span['char_start']:span['char_end']],span['text'])
                self.assertEqual(raw[span['byte_start']:span['byte_end']].decode('utf-8'),span['text'])
        date=next(n for n in g['nodes'] if n['kind']=='date_expression')
        self.assertEqual(date['date_role'],'document_received')

    def test_two_messages_in_one_file_are_distinct_layout_occurrences(self):
        self.put('letters.txt','Message-ID: MSG-001\nSubject: Same\n\nFirst body.\n\nMessage-ID: MSG-001\nSubject: Same\n\nSecond body.')
        g=self.graph();occ=[n for n in g['nodes'] if n['kind']=='source_occurrence']
        self.assertEqual(len(occ),2)
        self.assertLessEqual(occ[0]['span']['char_end'],occ[1]['span']['char_start'])
        self.assertTrue(next(e for e in g['edges'] if e['kind']=='candidate_identity_cluster')['changed_bodies'])

    def test_prior_snapshot_retains_original_statements_and_assessments_after_change(self):
        path=self.put('a.txt','Message-ID: MSG-001\n\nOriginal statement.')
        first=self.graph();prior=json.dumps(first,indent=2)
        path.write_text('Message-ID: MSG-001\n\nRevised statement.')
        new=self.graph('not-compared',prior_text=prior)
        self.assertEqual(new['prior_assessment']['snapshot_json'],prior)
        self.assertIn('Original statement',new['prior_assessment']['snapshot_json'])
        self.assertEqual(json.loads(new['prior_assessment']['snapshot_json'])['nodes'],first['nodes'])
        self.assertNotEqual(first['sources'][0]['raw_sha256'],new['sources'][0]['raw_sha256'])
        self.assertFalse(new['comparison_performed'])

    def test_replay_rejects_changed_source_even_same_size_and_mtime(self):
        path=self.put('a.txt','Subject: Cargo\n\nThe clerk sent ten crates.')
        graph=self.graph();before=path.stat()
        path.write_bytes(path.read_bytes().replace(b'ten',b'two'))
        os.utime(path,ns=(before.st_atime_ns,before.st_mtime_ns))
        with self.assertRaises(S.SortError):S.verify_graph(graph,self.root)

    def test_forged_source_support_or_edges_fail_even_with_recomputed_graph_digest(self):
        self.fixtures();g=self.graph()
        for mutate in (lambda x:x['nodes'][0]['assessment'].update(answer_supported=True),
                       lambda x:x['edges'][0].update(kind='proven_cause')):
            bad=copy.deepcopy(g);mutate(bad);bad['graph_sha256']=S.digest({k:v for k,v in bad.items() if k!='graph_sha256'})
            with self.assertRaises(S.SortError):S.verify_graph(bad,self.root)

    def test_source_inventory_change_during_run_refuses_old_output(self):
        self.put('a.txt','Subject: Cargo\n\nThe clerk sent a crate.')
        original=S.extract
        def race(root,limits):
            result=original(root,limits);self.put('new.txt','A newly available source.');return result
        with patch.object(S,'extract',race):
            with self.assertRaisesRegex(S.SortError,'inventory changed'):self.graph()

    def test_explicit_budgets_and_invalid_utf8_report_partial_without_authority(self):
        self.fixtures()
        for limits in ({'files':1},{'nodes':2},{'edges':1},{'statements':1},{'statement_chars':10},{'file_bytes':1}):
            with self.subTest(limits=limits):
                g=self.graph(limits=limits);self.assertFalse(g['complete']);self.assertTrue(g['limits_or_exclusions'])
                self.assertFalse(g['assessment']['answer_supported'])
        self.put('bad.txt',b'\xff\xfe invalid')
        g=self.graph();self.assertIn('invalid_utf8',g['limits_or_exclusions'])
        self.assertTrue(any(s.get('decoding')=='rejected_invalid_utf8' for s in g['sources']))
        with self.assertRaises(S.SortError):self.graph(limits={'files':True})
        with self.assertRaises(S.SortError):self.graph(limits={'files':1000000})

    def test_symlinks_and_fifo_not_read_and_unsafe_graph_paths_refuse(self):
        self.put('a.txt','A source statement.')
        (self.root/'link.txt').symlink_to(self.base/'private.txt')
        os.mkfifo(self.root/'pipe.txt')
        g=self.graph();self.assertIn('symlink_excluded',g['limits_or_exclusions'])
        self.assertIn('non_regular_file_excluded',g['limits_or_exclusions'])
        with self.assertRaises(S.SortError):S._read(self.root,'../private.txt',1024)

    def test_sealed_snapshot_is_retired_and_reader_refuses_every_profile(self):
        self.fixtures();g=self.graph();ledger=self.base/'ledger'
        result=S.export_retired(g,self.root,ledger)
        self.assertEqual(result['status'],'retired_candidate_snapshot')
        self.assertFalse(result['assessment']['answer_supported'])
        page=next(r for r in Ledger(ledger).records if r.id=='SORTER-CANDIDATES')
        self.assertEqual(page.status,'retired');self.assertTrue(page.intact)
        self.assertEqual(page.origin,'machine');self.assertFalse(page.ratified_by)
        from mplpb_combined.provenance_gate import gather
        for profile in PROFILES.values():
            gate=gather(ledger,'sorter candidate inspection',profile)
            self.assertEqual(gate.sources,[])
            exclusion=next(x for x in gate.excluded if x['id']=='SORTER-CANDIDATES')
            if profile.name!='external':self.assertEqual(exclusion['reason'],'retired')
            else:self.assertTrue(exclusion['reason'])
            for as_of in (None,'1841-06-01'):
                answer=answer_query(ledger,'Which record corrects the cargo request?',profile,as_of=as_of).contract
                self.assertFalse(answer['answer_supported']);self.assertEqual(answer['claims'],[])
        with self.assertRaises(S.SortError):S.export_retired(g,self.root,ledger)

    def test_native_snapshot_validates_and_is_inspectable_in_both_modes(self):
        # HTML delimiters, CRLF and Unicode must survive inside source quotations.
        self.put('raw.md','Record-ID: CASE-1\r\nOwner: Alice\r\n\r\nÉmile wrote </pre> & <script>nothing</script>.\r\n')
        from mplpb_combined.record import body_of
        import html
        for mode in ('not-compared','compare'):
            graph=self.graph(mode);ledger=self.base/mode
            receipt=S.export_retired(graph,self.root,ledger)
            self.assertEqual(receipt['native_validation'],{'errors':0,'warnings':0,'graph_roundtrip_verified':True})
            page=next(r for r in Ledger(ledger).records if r.id=='SORTER-CANDIDATES')
            self.assertEqual(Ledger(ledger).findings(),[])
            payload=html.unescape(body_of((ledger/page.path).read_text()).split('<pre>',1)[1][:-6])
            self.assertEqual(json.loads(payload),graph)
            for command in (['validate',str(ledger),'--strict'],['show',str(ledger),'SORTER-CANDIDATES']):
                result=subprocess.run([sys.executable,'-m','mplpb_answers']+command,capture_output=True,text=True,timeout=20)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('Unverified sorter candidate snapshot',result.stdout)
            for profile in PROFILES.values():
                result=answer_query(ledger,'What is Owner for record CASE-1?',profile).contract
                self.assertFalse(result['answer_supported']);self.assertEqual(result['claims'],[])

    def test_native_validation_error_or_warning_does_not_publish_snapshot(self):
        from mplpb_combined.ledger import Finding
        self.put('a.txt','A source statement.');graph=self.graph()
        for level in ('error','warning'):
            target=self.base/level
            with patch('mplpb_combined.ledger.Ledger.findings',return_value=[Finding(level,'TEST','snapshot.html','injected native finding')]):
                with self.assertRaisesRegex(S.SortError,'Native snapshot validation failed'):
                    S.export_retired(graph,self.root,target)
            self.assertFalse(target.exists())

    def test_validly_sealed_but_wrong_snapshot_body_is_not_published(self):
        from mplpb_combined.ledger import write
        self.put('a.txt','A source statement.');graph=self.graph();target=self.base/'wrong-body'
        def substituted(root,**kwargs):
            kwargs['body_html']='<pre>{"altered":true}</pre>'
            return write(root,**kwargs)
        with patch('mplpb_combined.ledger.write',side_effect=substituted):
            with self.assertRaisesRegex(S.SortError,'body differs'):
                S.export_retired(graph,self.root,target)
        self.assertFalse(target.exists())

    def test_failed_export_does_not_publish_a_current_candidate(self):
        self.put('a.txt','A source statement.');graph=self.graph();target=self.base/'ledger'
        with patch('mplpb_combined.ledger.withdraw',side_effect=OSError('fixture interruption')):
            with self.assertRaises(OSError):S.export_retired(graph,self.root,target)
        self.assertFalse(target.exists())

    def test_cli_modes_peruse_refusal_and_no_output_overwrite_or_input_write(self):
        self.fixtures();path=self.base/'graph.json'
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(S.main(['sort',str(self.root),'--mode','not compared','--output',str(path)]),0)
            self.assertEqual(S.main(['verify',str(path),'--sources',str(self.root)]),0)
            self.assertEqual(S.main(['peruse',str(path),'--sources',str(self.root),'--max-items','3']),0)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(S.main(['sort',str(self.root),'--output',str(path)]),2)
            self.assertEqual(S.main(['sort',str(self.root),'--output',str(self.root/'graph.json')]),2)
        self.assertEqual(path.stat().st_mode&0o777,0o600)
        self.assertFalse((self.root/'graph.json').exists())

    def test_all_graph_items_remain_non_authoritative_and_ids_are_reversible(self):
        self.fixtures();g=self.graph();by_id={n['id']:n for n in g['nodes']}
        self.assertEqual(len(by_id),len(g['nodes']))
        for item in g['nodes']+g['edges']+g['sources']+[g]:
            self.assertFalse(item['assessment']['answer_supported'])
            self.assertFalse(item['assessment']['source_support_established'])
            self.assertFalse(item['assessment']['historical_truth_independently_verified'])
        for edge in g['edges']:
            self.assertIn(edge['from'],by_id);self.assertIn(edge['to'],by_id)
            for evidence in edge['evidence_nodes']:self.assertIn(evidence,by_id)
        self.assertEqual(S.verify_graph(g,self.root)['status'],'source_fidelity_replayed')
        self.assertEqual(self.graph(),g)
