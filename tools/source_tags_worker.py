"""Execution only: public case and native runtime, without expected results."""
import json
from pathlib import Path
import resource
import shutil

def execute():
    resource.setrlimit(resource.RLIMIT_CPU,(30,30))
    resource.setrlimit(resource.RLIMIT_FSIZE,(8*1024**2,8*1024**2))
    inputs=Path('/study');root=Path('/scratch/ledger')
    shutil.copytree(inputs/'ledger',root)
    from mplpb_answers.pipeline import answer_query
    question=json.loads((inputs/'question.json').read_text())['question']
    raw=answer_query(root,question).contract
    try:
        from mplpb_answers.source_tags import verify_proposals
    except ModuleNotFoundError as error:
        if error.name!='mplpb_answers.source_tags':raise
        tags={'status':'API_UNAVAILABLE','semantic_outcome':'NOT_RUN'}
    else:
        tags=verify_proposals(root,question,json.loads((inputs/'tags.json').read_text()))
    result={'question':question,'raw_answer':raw,'tag_validation':tags}
    with Path('/output/result.json').open('x') as f:json.dump(result,f,ensure_ascii=False)

if __name__=='__main__':execute()
