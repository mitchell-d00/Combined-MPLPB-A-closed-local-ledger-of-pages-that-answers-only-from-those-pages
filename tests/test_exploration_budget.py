"""Independent discovery budgets must never become strict proof slots."""
import tempfile
import unittest
from unittest.mock import patch
from mplpb_combined.ledger import write
from mplpb_answers.pipeline import answer_query
from mplpb_work.answer_router import explore,question_parts


class ExplorationTests(unittest.TestCase):
    def test_parts_and_contrary_wording_remain_visible_without_strict_calls(self):
        with tempfile.TemporaryDirectory() as root:
            for i,text in enumerate(('The manifest describes amber cargo.','The manifest does not describe amber cargo.',
                                      'The beacon uses a cobalt lens.'),1):
                write(root,doc_id='SRC-'+str(i),title='Archive',scope='archive',body=text)
            with patch('mplpb_work.answer_router.answer_query',side_effect=AssertionError('Discovery entered proof')):
                report=explore('What amber cargo does the manifest describe, and what lens does the beacon use?',root,max_passages=3)
            self.assertFalse(report['answer_supported']);self.assertEqual(report['strict_slots_consumed'],0)
            text=' '.join(p['text'] for p in report['report']['passages'])
            self.assertIn('cobalt lens',text);self.assertIn('does not describe',text)
            self.assertLessEqual(report['report']['search_limits']['display_characters'],16000)

    def test_discovery_does_not_change_native_answer_contract(self):
        with tempfile.TemporaryDirectory() as root:
            write(root,doc_id='SRC-1',title='Archive',scope='press',body='Amara owns the Juniper press.')
            question='Who owns the Juniper press?';before=answer_query(root,question).contract
            explore(question,root,max_passages=1,max_characters=1000)
            self.assertEqual(before,answer_query(root,question).contract)

    def test_exhausted_complete_context_is_a_visible_limit(self):
        with tempfile.TemporaryDirectory() as root:
            write(root,doc_id='SRC-1',title='Archive',scope='archive',body='Archive '+'word '*500+'.')
            report=explore('Explain archive',root,max_characters=1000)
            self.assertEqual(report['report']['method'],'context_budget_exhausted')
            self.assertFalse(report['answer_supported'])

    def test_long_first_source_cannot_starve_later_sources(self):
        with tempfile.TemporaryDirectory() as root:
            write(root,doc_id='SRC-1',title='Long archive',scope='archive',
                  body_html='<pre>'+('Unrelated archive line.\n'*3000)+'</pre>')
            write(root,doc_id='SRC-2',title='Second archive',scope='archive',
                  body='The amber beacon uses a cobalt lens.')
            result=explore('What lens does the amber beacon use?',root,max_passages=3)
            self.assertTrue(any(p['source_id']=='SRC-2' for p in result['report']['passages']))
            self.assertFalse(result['answer_supported'])

    def test_wrapped_source_context_keeps_exact_slice(self):
        with tempfile.TemporaryDirectory() as root:
            text='The amber beacon\nuses a cobalt lens.\nIts keeper reports the observation.'
            write(root,doc_id='SRC-1',title='Archive',scope='archive',body_html='<pre>'+text+'</pre>')
            result=explore('What lens does the amber beacon use?',root,max_passages=3)
            passages=result['report']['passages']
            self.assertTrue(any('beacon\nuses a cobalt lens' in p['text'] for p in passages))
            for passage in passages:
                self.assertEqual(text[passage['body_start']:passage['body_end']],passage['text'])

    def test_listed_date_roles_are_separate_discovery_queries(self):
        self.assertEqual(len(question_parts('Distinguish drafting, distribution and receipt dates.')),3)


if __name__=='__main__':unittest.main()
