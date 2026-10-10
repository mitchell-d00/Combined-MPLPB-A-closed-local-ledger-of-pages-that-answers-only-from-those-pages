"""Conservative answer CLI. The legacy mplpb_combined ask command retrieves candidates."""
import argparse
import json
from tools.answer_support import supported_answer
from mplpb_combined.reader import PROFILES

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root');p.add_argument('question')
    p.add_argument('--profile',choices=PROFILES,default='internal');a=p.parse_args()
    result=supported_answer(a.root,a.question,PROFILES[a.profile])
    print(json.dumps(result.to_dict(),indent=2))
    raise SystemExit({'return':0,'ambiguous':2,'not_in_corpus':3}[result.kind])
