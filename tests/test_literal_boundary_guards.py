"""Literal proof boundaries are checked in source context, not proposal context."""
from pathlib import Path
import tempfile
import unittest
from mplpb_combined.ledger import write
from mplpb_combined.reader import PROFILES
from mplpb_answers.body_text import body_text
from mplpb_answers.documentary_verify import check
from mplpb_answers.passages import PassageIndex
from mplpb_answers.pipeline import answer_query


class LiteralBoundaryGuardTests(unittest.TestCase):
    def test_empty_or_padding_cannot_turn_partial_words_into_proof(self):
        for anchor,source in [('   ','Quartz.'),(' tide ','The tideline shifted.'),('C++','C++draft was noted.')]:
            with self.subTest(anchor=anchor),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);write(root,doc_id='LOG-1',title='Archive',scope='archive',body_html='<p>'+source+'</p>')
                result=answer_query(root,'Which source contains the exact words "'+anchor+'"?').contract
                self.assertFalse(result['answer_supported'])

    def test_clipped_word_is_not_a_witness_even_with_real_match_elsewhere(self):
        for source in ['The tideline shifted.','The tideline shifted before the tide changed.']:
            with self.subTest(source=source),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);record=write(root,doc_id='LOG-1',title='Archive',scope='archive',body_html='<p>'+source+'</p>')
                body=body_text(record.body_html);a=body.index('tide');b=a+4
                proposal={'kind':'literal_location','source_id':record.id,'path':record.path,
                          'hash':record.hash_actual,'start':a,'end':b,'quote':body[a:b]}
                index=PassageIndex(root,'Which source contains the exact words "tide"?',PROFILES['internal'])
                self.assertFalse(check(index,[proposal])['proofs'])
