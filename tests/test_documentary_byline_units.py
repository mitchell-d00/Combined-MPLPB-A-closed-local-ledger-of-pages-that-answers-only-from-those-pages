"""BW-BYLINE: source metadata boundaries must retain voice and governors."""
import html
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import write

Q='What does Milan Rowe report about the writer of the herbarium ledger, without independently verifying the event?'
CLAUSE='Milan Rowe reported that Ari Calder wrote the herbarium ledger.'


class DocumentaryBylineTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)

    def source(self,text,wrapper=''):
        body='<pre>'+html.escape(text)+'</pre>'
        if wrapper:body='<'+wrapper+'>'+body+'</'+wrapper+'>'
        write(self.root,doc_id='A',title='Source',scope='archival records',origin='machine',external='yes',body_html=body)

    def ask(self,q=Q):return answer_query(self.root,q).contract
    def withhold(self):
        a=self.ask();self.assertFalse(a['answer_supported']);self.assertEqual(a['claims'],[])

    def test_unpunctuated_recorder_is_not_part_of_the_speaker(self):
        self.source('Meeting minutes.\nRecorder: Sanja Qureshi\n\n'+CLAUSE)
        a=self.ask();self.assertTrue(a['answer_supported']);p=a['claims'][0]['proposition']
        self.assertEqual(p['reporter'],'Milan Rowe');self.assertEqual(p['source_writer_or_unknown'],'Sanja Qureshi')

    def test_unpunctuated_writer_before_an_attributed_quote(self):
        self.source('Report.\nWritten by Sanja Qureshi\n\nMilan Rowe said, “Ari Calder wrote the herbarium ledger.”')
        self.assertTrue(self.ask()['answer_supported'])

    def test_punctuated_byline_preserves_existing_support(self):
        self.source('Report.\nWritten by Sanja Qureshi.\n\n'+CLAUSE)
        self.assertTrue(self.ask()['answer_supported'])

    def test_writer_cannot_acquire_the_reporters_statement(self):
        self.source('Meeting minutes.\nRecorder: Sanja Qureshi\n\n'+CLAUSE)
        a=self.ask(Q.replace('Milan Rowe','Sanja Qureshi'))
        self.assertFalse(a['answer_supported']);self.assertEqual(a['claims'],[])

    def test_leading_conditional_fragment_cannot_be_pruned(self):
        self.source('If the transcript is reliable:\nReport.\nWritten by Sanja Qureshi\n\n'+CLAUSE)
        self.withhold()

    def test_condition_on_the_byline_cannot_be_pruned(self):
        self.source('Report.\nWritten by Sanja Qureshi if the transcript is reliable\n\n'+CLAUSE)
        self.withhold()

    def test_quoted_document_cannot_supply_unqualified_authority(self):
        self.source('Report.\nWritten by Sanja Qureshi\n\n'+CLAUSE,wrapper='blockquote')
        self.withhold()

    def test_competing_writer_labels_do_not_disappear(self):
        self.source('Report.\nWritten by Sanja Qureshi\nWritten by Orin Desai\n\n'+CLAUSE)
        self.withhold()

    def test_separate_conditional_with_period_remains_a_governor(self):
        self.source('Report.\nWritten by Sanja Qureshi.\n\nIf the transcript is reliable.\n\n'+CLAUSE)
        self.withhold()


if __name__=='__main__':unittest.main()
