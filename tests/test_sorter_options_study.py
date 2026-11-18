import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from mplpb_combined.ledger import write,withdraw
from mplpb_answers.body_text import body_text
from mplpb_answers.passages import PassageIndex
from mplpb_work import sorter
from tools.sorter_options_study import merge,Locator
from tools.unprepared_challenge import sha


class SorterOptionsStudyTests(unittest.TestCase):
    def test_common_guard_reserves_both_source_discovery_passages(self):
        a={'path':'a','body_start':0,'text':'Original first source.','retrieval_reason':'source-facet'}
        b={'path':'b','body_start':0,'text':'Original second source.','retrieval_reason':'source-facet'}
        unrelated={'path':'c','body_start':0,'text':'c'*7800,'sorter_node_id':'hint'}
        index=SimpleNamespace(exact_status=None,sources=[{'path':p} for p in ['a','b','c']],unchanged=lambda:True)
        pack=merge(index,{'passages':[a,b],'sources':index.sources},[unrelated],12,8000)
        self.assertEqual(pack['passages'][:2],[a,b]);self.assertLessEqual(sum(len(p['text']) for p in pack['passages']),8000)

    def test_exact_route_has_no_intervention(self):
        base={'passages':[]};index=SimpleNamespace(exact_status='matched')
        self.assertIs(merge(index,base,[{'text':'untrusted'}],12,8000),base)

    def test_layout_roundtrip_and_fresh_retirement_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);raw=root/'raw';raw.mkdir();text='Zoë planned to send the report.\r\n\r\nIvo did not receive it.'
            (raw/'a.txt').write_bytes(text.encode());record=write(root/'ledger',doc_id='DOC-101',scope='report',title='report',origin='human',body_html='<pre>'+text+'</pre>')
            binding={'a.txt':{'id':record.id,'hash':record.hash_actual,'projection_sha256':sha(body_text(record.body_html).encode())}}
            graph=sorter.sort_directory(raw);node=next(n for n in graph['nodes'] if n['kind']=='statement')
            locator=Locator(binding,{'a.txt':text});index=PassageIndex(root/'ledger','report')
            mapped=locator.span(index,node['span']);self.assertIsNotNone(mapped)
            a,b=mapped[1:];self.assertEqual(body_text(record.body_html)[a:b],node['span']['text'])
            withdraw(root/'ledger',record.id,note='permission withdrawn')
            self.assertIsNone(locator.span(PassageIndex(root/'ledger','report'),node['span']))


if __name__=='__main__':unittest.main()
