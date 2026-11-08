import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from tools import prepare_owner_corpus as C


class OwnerCorpusTests(unittest.TestCase):
    def test_exact_excerpt_and_frozen_question_screening(self):
        question='What is the frozen telescope marker color?'
        safe='This is original owner writing about revisable working context and bounded source claims. Its conditions remain attached.'
        text=safe+'\n\n'+question+' The expected answer is in this paragraph.'
        rows,rejected=C.passages(text,{C.normalized(question)})
        self.assertEqual(rejected,1);self.assertEqual(len(rows),1)
        row=rows[0];self.assertEqual(text[row['start']:row['end']],row['text'])
        self.assertEqual(row['sha256'],hashlib.sha256(row['text'].encode()).hexdigest())

    def test_capture_is_attributed_candidate_not_trained_or_ratified(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder);repo={'name':'work','owner':{'login':'owner'},'default_branch':'main','private':False,'license':{'spdx_id':'MIT'}}
            body=b'An owner-authored paragraph about a topic with its own limits, assumptions and context. These words are source material, not proof of truth.'
            result=C.collect([repo],base/'new','owner','Owner grants use of their own writing.',fetcher=lambda u:body,root=base)
            self.assertEqual(result['sources_captured'],1);self.assertFalse(result['training_has_run'])
            self.assertFalse(result['ready_for_supervised_fine_tuning']);self.assertEqual(result['sources'][0]['observed_repository_license'],'MIT')
            with self.assertRaisesRegex(ValueError,'new output'):C.collect([],base/'new','owner','permission',root=base)

    def test_other_owners_private_repositories_and_forks_are_excluded(self):
        repos=[{'name':'private','owner':{'login':'owner'},'private':True},
               {'name':'foreign','owner':{'login':'elsewhere'}},
               {'name':'fork','owner':{'login':'owner'},'fork':True}]
        with tempfile.TemporaryDirectory() as d:
            def blocked(url):raise AssertionError('Excluded repository requested')
            result=C.collect(repos,Path(d)/'out','owner','Own work only',fetcher=blocked,root=Path(d))
            self.assertEqual(result['repositories_considered'],0)

    def test_permission_and_existing_output_are_explicit(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,'permission'):C.collect([],Path(d)/'out','owner','',root=Path(d))
