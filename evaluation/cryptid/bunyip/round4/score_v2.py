"""Version the fixture-to-admitted-HTML coordinate join for Round 4."""
import argparse
from copy import deepcopy
import hashlib
import html
from pathlib import Path

import score as original
from tools.cryptid_trial_v5 import read, save, sha


def score(phase, key_path, armdir):
    origin = {}
    registry = original.HOME/phase/'registry.json'
    for row in read(registry)['cases']:
        for source in read(original.ROOT/row['packet']/'case.json')['sources']:
            fixture = source['body_html'].encode()
            heading = ('<h1>'+html.escape(' '.join(source['title'].split()), quote=False)+'</h1>\n').encode()
            origin[hashlib.sha256(fixture).hexdigest()] = (fixture, heading)

    match_admitted = original.match

    def translated_match(claim, target, records):
        translated = deepcopy(target)
        for witness in translated['witnesses']:
            fixture, heading = origin[witness['body_html_sha256']]
            lo, hi = witness['start_byte'], witness['end_byte']
            assert fixture[lo:hi] == witness['quote'].encode()
            witness.update(start_byte=lo+len(heading), end_byte=hi+len(heading),
                           body_html_sha256=hashlib.sha256(heading+fixture).hexdigest())
        return match_admitted(claim, translated, records)

    original.match = translated_match
    try:
        result = original.score(phase, key_path, armdir)
    finally:
        original.match = match_admitted
    result['projection_adapter_sha256'] = sha(Path(__file__))
    result['policy'] = 'fixture_to_admitted_html_coordinate_correction_v2'
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('diagnostic','fresh'))
    for name in ('key','run','output'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    result = score(args.phase,args.key,args.run)
    save(args.output,result)
    print(result['reader'],result['counts'])
