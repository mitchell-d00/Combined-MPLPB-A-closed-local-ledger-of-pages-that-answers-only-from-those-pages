"""Classing must preserve source occurrences and explicit serving decisions."""
import copy,html,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from mplpb_work import classing
from mplpb_combined.ledger import Ledger,write

class ClassingBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.dump=self.root/'dump';self.dump.mkdir()
    def propose(self,text='Message-ID: DATA-1\nCargo: A\t\tB\n\nFull original statement.'):
        (self.dump/'a.txt').write_text(text)
        return classing.propose(self.dump,auto_accept_clean=True)
    def test_source_label_and_body_are_not_editable_extracted_evidence(self):
        for mutation in ('label','body','path'):
            r=self.propose();d=r['drafts'][0]
            if mutation=='label':d['fields'][1]['label']='Owner'
            elif mutation=='body':d['body']='original'
            else:d['source']['path']='../outside.txt'
            with self.subTest(mutation=mutation),self.assertRaises(classing.ClassingError):classing.plan(r,self.dump)
    def test_literal_internal_whitespace_is_preserved_in_native_html(self):
        r=self.propose();classing.build(r,self.dump,self.root/'ledger')
        rec=Ledger(self.root/'ledger').records[0]
        self.assertIn('A\t\tB',html.unescape(rec.body_html))
    def test_retired_draft_is_not_auto_accepted_or_silently_served(self):
        r=self.propose('Message-ID: DATA-1\nStatus: retired\n\nPrior statement.')
        self.assertEqual(r['drafts'][0]['decision'],'pending')
        r['drafts'][0]['decision']='accept'
        with self.assertRaises(classing.ClassingError):classing.build(r,self.dump,self.root/'ledger')
    def test_serving_decision_needs_an_identified_reviewer(self):
        r=self.propose('Message-ID: DATA-1\nStatus: retired\n\nPrior statement.')
        r['drafts'][0]['decision']='accept';r['decisions'][0]['choice']='withdraw_after_write'
        with self.assertRaises(classing.ClassingError):classing.build(r,self.dump,self.root/'ledger')
    def test_tampered_choice_options_cannot_authorize_unknown_operation(self):
        r=self.propose('Message-ID: DATA-1\nStatus: retired\n\nPrior statement.')
        r['drafts'][0]['decision']='accept';r['decisions'][0].update(options=['invent'],choice='invent')
        with self.assertRaises(classing.ClassingError):classing.plan(r,self.dump)
    def test_failed_append_does_not_leave_a_partial_ledger(self):
        ledger=self.root/'ledger';write(ledger,doc_id='BASE-1',title='Base',scope='base',body='Existing original.')
        r=self.propose();before={p.relative_to(ledger):p.read_bytes() for p in ledger.rglob('*') if p.is_file()}
        original=classing._apply;calls=[]
        def injected(root,*a,**kw):
            calls.append(1)
            if Path(root).resolve()==ledger.resolve():raise OSError('injected publish failure')
            return original(root,*a,**kw)
        # A staging-only native writer also passes: publication copies validated
        # bytes instead of applying a second possibly divergent writer run.
        with patch.object(classing,'_apply',side_effect=injected):
            try:classing.build(r,self.dump,ledger,append=True)
            except OSError:pass
        after={p.relative_to(ledger):p.read_bytes() for p in ledger.rglob('*') if p.is_file()}
        if len(calls)>1:self.assertEqual(before,after)

    def test_publication_error_rolls_back_changed_files(self):
        from mplpb_combined import ledger as native
        ledger=self.root/'ledger';write(ledger,doc_id='BASE-1',title='Base',scope='base',body='Existing original.')
        r=self.propose();before={p.relative_to(ledger):p.read_bytes() for p in ledger.rglob('*') if p.is_file()}
        original=native._atomic_write;calls=[]
        def injected(path,*args,**kwargs):
            if ledger.resolve() in Path(path).resolve().parents:
                calls.append(1)
                if len(calls)==2:raise OSError('injected publication error')
            return original(path,*args,**kwargs)
        with patch.object(native,'_atomic_write',side_effect=injected),self.assertRaises(OSError):
            classing.build(r,self.dump,ledger,append=True)
        self.assertGreaterEqual(len(calls),2)
        self.assertEqual(before,{p.relative_to(ledger):p.read_bytes() for p in ledger.rglob('*') if p.is_file()})

    def test_dump_change_during_rehearsal_stops_publication(self):
        r=self.propose();original=classing._apply
        def injected(*a,**kw):
            result=original(*a,**kw);(self.dump/'a.txt').write_text('Changed source.');return result
        with patch.object(classing,'_apply',side_effect=injected),self.assertRaisesRegex(classing.ClassingError,'changed'):
            classing.build(r,self.dump,self.root/'ledger')
        self.assertFalse((self.root/'ledger').exists())
