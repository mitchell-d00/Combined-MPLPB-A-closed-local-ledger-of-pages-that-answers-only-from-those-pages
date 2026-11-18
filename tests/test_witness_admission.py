import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from mplpb_answers.pipeline import answer_query
from mplpb_answers import prose_retrieval
from mplpb_combined.ledger import write
from tools.unprepared_sources import import_corpus
from mplpb_answers.passages import PassageIndex
from mplpb_answers.passage_admission import Budget
from mplpb_answers import documentary_verify


class WitnessAdmissionTests(unittest.TestCase):
    def test_duplicate_source_span_is_charged_once_before_cutoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            record=write(tmp,doc_id='DOC-101',title='Appointment',scope='appointment',origin='human',body_html='<p>Ruth Stone appointed Mira Vale.</p>')
            index=PassageIndex(tmp,'Who appointed Mira Vale?')
            from mplpb_answers.body_text import body_text
            body=body_text(record.body_html);span=documentary_verify.citation(record,body,0,len(body))
            budget=Budget(index,1,8000)
            self.assertTrue(budget.offer([span],'first question part'))
            self.assertTrue(budget.offer([dict(span),dict(span)],'second question part'))
            self.assertEqual(budget.report()['passages_admitted'],1)
            self.assertEqual(budget.report()['characters_admitted'],len(body))

    def test_generic_two_part_proof_respects_two_slots(self):
        with tempfile.TemporaryDirectory() as tmp:
            for n,text in enumerate(['Ruth Stone appointed Mira Vale.','Orin Hale appointed Lena Grey.']):
                write(tmp,doc_id='DOC-'+str(n),title='Appointment',scope='appointment',origin='human',body_html='<p>'+text+'</p>')
            question='Who appointed Mira Vale, and who appointed Lena Grey?'
            full=answer_query(tmp,question,max_passages=2,max_chars=8000).contract
            self.assertTrue(full['answer_supported']);self.assertEqual(len(full['claims']),2)
            self.assertEqual(full['documentary_support']['admission']['passages_admitted'],2)
            limited=answer_query(tmp,question,max_passages=1,max_chars=8000).contract
            self.assertFalse(limited['answer_supported'])
            self.assertLessEqual(limited['documentary_support']['admission']['passages_admitted'],1)

    def test_untrusted_hint_cannot_reinstate_withdrawn_source(self):
        from mplpb_combined.ledger import withdraw
        from mplpb_answers.body_text import body_text
        with tempfile.TemporaryDirectory() as tmp:
            record=write(tmp,doc_id='DOC-101',title='Appointment',scope='appointment',origin='human',body_html='<p>Ruth Stone appointed Mira Vale.</p>')
            body=body_text(record.body_html)
            hint={'source_id':record.id,'path':record.path,'hash':record.hash_actual,'text':body,'body_start':0,
                  'suggestion_class':'exact_source_id_match','answer_supported':True}
            withdraw(tmp,record.id,note='withdrawn')
            answer=answer_query(tmp,'Who appointed Mira Vale?',source_hints=[hint]).contract
            self.assertFalse(answer['answer_supported']);self.assertFalse(answer['claims'])

    def test_h05_complete_at_original_budget_despite_high_darwin_search_hints(self):
        corpus=Path(__file__).resolve().parents[1]/'evaluation/unprepared-originals/2026-11-16'
        question=next(c['question'] for c in json.loads((corpus/'questions.json').read_text())['cases'] if c['id']=='H05')
        ordinary=prose_retrieval.retrieve
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'ledger';receipt=import_corpus(corpus,root)
            darwin={r['id'] for r in receipt['records'] if r['original_id']=='DARWIN-1887'}
            def swamped(index,max_passages=12,max_chars=12000,seed=None):
                base=ordinary(index,max_passages,max_chars,seed=seed);selected=[];used=0
                hints=[dict(p,sorter_node_id='review-'+p['id'],suggestion_class='synonym_or_shared_wording',
                            retrieval_score=10000,sorter_basis='Shared truth vocabulary only; review candidate.')
                       for p in index.passages if p['source_id'] in darwin and 'truth' in p['text'].lower()]
                for p in hints+base['passages']:
                    if len(selected)<max_passages and used+len(p['text'])<=max_chars:selected.append(p);used+=len(p['text'])
                return dict(base,passages=selected)
            with patch.object(prose_retrieval,'retrieve',swamped):
                answer=answer_query(root,question,max_passages=12,max_chars=8000).contract
            self.assertEqual(answer['kind'],'supported_answer')
            self.assertTrue(answer['answer_supported'])
            self.assertTrue(any('sacred & undeniable' in c['text'] and 'self-evident' in c['text'] for c in answer['claims']))
            budget=answer['documentary_support']['admission']
            self.assertLessEqual(budget['passages_admitted'],12);self.assertLessEqual(budget['characters_admitted'],8000)
            self.assertGreater(budget['review_only_hint_count'],0)
            self.assertEqual(budget['search_only_hints_admitted'],0)

    def test_relevant_contradiction_cannot_be_hidden_by_one_passage_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for number,text in enumerate(['Ruth Stone appointed Mira Vale.','Ruth Stone did not appoint Mira Vale.']):
                write(root,doc_id='DOC-'+str(number),title='Appointment record',scope='appointment record',origin='human',body_html='<p>'+text+'</p>')
            answer=answer_query(root,'Who appointed Mira Vale?',max_passages=1,max_chars=8000).contract
            self.assertFalse(answer['answer_supported'])
            self.assertIn(answer['kind'],{'conflict','abstain','partial_answer'})
            self.assertEqual(answer['diagnostic']['code'],'contradictory_passages_pruned')
            budget=answer['documentary_support']['admission']
            self.assertTrue(budget['relevant_counterevidence_did_not_fit'])
            self.assertLessEqual(budget['passages_admitted'],1)


if __name__=='__main__':unittest.main()
