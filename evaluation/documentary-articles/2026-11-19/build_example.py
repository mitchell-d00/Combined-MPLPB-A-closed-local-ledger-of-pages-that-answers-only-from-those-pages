"""Fictional shared-account and conflict demonstration, not historical scoring."""
import argparse
import html
import json
from pathlib import Path

from mplpb_combined import ledger as L
from mplpb_work.article import assemble, render


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', required=True, type=Path)
    out = p.parse_args().output
    out.mkdir(parents=True, exist_ok=False)
    root = out/'ledger'
    body = 'Nora Finch appointed Ellis Marsh.'
    original = L.write(root, doc_id='ACCOUNT-1', title='Archive', scope='archive',
                       body_html='<pre>'+html.escape(body)+'</pre>')
    for i in range(2, 4):
        L.write(root, doc_id='ACCOUNT-'+str(i), title='Archive', scope='archive',
                body_html='<pre>'+html.escape(body)+'</pre>',
                derived_from=[original.id+'@'+original.hash])
    plan = {'title': 'Fictional appointment research', 'questions': ['Who appointed Ellis Marsh?']}
    before = assemble(root, plan)
    L.write(root, doc_id='COUNTER-1', title='Archive', scope='archive',
            body_html='<pre>Nora Finch did not appoint Ellis Marsh.</pre>')
    after = assemble(root, plan)
    result = {'scope': 'Author-written fictional demonstration; neither account is certified as historically true.',
              'plan': plan, 'before_counteraccount': before, 'after_counteraccount': after,
              'checks': {'shared_root_has_three_appearances': len(before['provenance']['shared_declared_roots'][0]['source_ids']) == 3,
                         'independent_witness_count_unknown': before['provenance']['independent_witness_count'] is None,
                         'counteraccount_preserved_as_conflict': after['sections'][0]['report']['native_answer']['kind'] == 'conflict',
                         'no_article_support': not before['answer_supported'] and not after['answer_supported']}}
    (out/'example.json').write_text(json.dumps(result, indent=2)+'\n')
    print(render(after))
    return 0 if all(result['checks'].values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
