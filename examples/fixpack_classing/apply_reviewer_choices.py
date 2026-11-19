"""Stand-in for a person editing review.json (the README walkthrough choices).

In real use a person makes these choices by editing the file. This script exists
only so the walkthrough is reproducible.
"""
import json
import sys

src, dst = sys.argv[1], sys.argv[2]
r = json.load(open(src, encoding='utf-8'))
drafts = {d['source']['path']: d for d in r['drafts']}
# Fictional scripted choices, not actual independent reviewers.
for draft in drafts.values(): draft['decision'] = 'accept'
drafts['diary.md']['decision'] = 'reject'                      # no record; reported speech only
drafts['ship-9a.txt']['decision'] = drafts['ship-9b.txt']['decision'] = 'accept'
drafts['ship-8.txt']['reviewer_fields'].append({               # literal quote from SHIP-8's own sentence
    'label': 'Cargo', 'value': 'thirty-eight barrels',
    'quote': 'the cargo count changes only to thirty-eight barrels'})
drafts['ship-7.txt']['ratify'] = True                         # the reviewer stands behind SHIP-7
for x in r['decisions']:
    if x['kind'] == 'duplicate_id':
        x['choice'] = 'second_supersedes_first'
    elif x['kind'] == 'partial_correction':
        x.update(choice='field_correction', corrects_field='cargo')
    elif x['kind'] == 'declared_status':
        x['choice'] = 'withdraw_after_write'
    else:
        x['choice'] = 'ignore'                                 # e.g. the Letter 42 correction is left unapplied
json.dump(r, open(dst, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print('wrote', dst)
