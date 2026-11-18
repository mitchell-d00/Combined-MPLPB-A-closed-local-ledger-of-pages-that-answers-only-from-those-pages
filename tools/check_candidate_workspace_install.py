"""Run with an installed wheel's isolated Python; checkout tools must be absent."""
import argparse
import json
from pathlib import Path
import sys
import tempfile


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);a=p.parse_args()
    from mplpb_work import sorter
    from mplpb_work.candidate_workspace import build,verify_workspace
    from mplpb_combined.ledger import write
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp);processed=root/'processed';processed.mkdir();ledger=root/'originals'
        (processed/'note.txt').write_text('Mara wrote the Redwood memorandum.',encoding='utf-8')
        write(ledger,doc_id='DOC-101',title='Redwood memorandum',scope='Redwood memorandum',origin='human',body_html='<p>Mara wrote the Redwood memorandum.</p>')
        graph=sorter.sort_directory(processed,mode='compare')
        workspace=build(graph,processed,ledger,question='Who wrote the Redwood memorandum?')
        verify_workspace(workspace,graph,processed,ledger)
        assert workspace['mplpb_decision']['strict_answer']['answer_supported']
        assert workspace['candidates'][0]['kind']=='exact_match'
        assert not workspace['candidates'][0]['answer_supported']
        assert not any(n=='tools' or n.startswith('tools.') for n in sys.modules),'Installed runtime must not import checkout tools'
        result={'status':'passed','installed_package':str(Path(sorter.__file__).resolve()),
            'isolated_python':bool(sys.flags.isolated),'exact_match_replayed':True,'strict_original_support_preserved':True,
            'processed_approval_transferred':False,'checkout_tools_imported':False,
            'scope':'Authored installed-wheel integration; not human or historical semantic validation.'}
        assert result['isolated_python'],'Run with python -I'
        if a.output:
            if a.output.exists():raise ValueError('Refuse overwrite')
            a.output.write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2))


if __name__=='__main__':main()
