"""Compare current supported answers to a pinned pre-change implementation.

Frozen questions remain development data. No labels or source pages are edited.
Requires a git checkout containing the requested baseline object.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile

from tools import evaluate_answer_reliability as reliability
from mplpb_answers.support import code_pins

BASELINE = '251e918340c8cfe700b1157d5367e4af0a02bec6'


def git(*args):
    return subprocess.check_output(['git', *args])


def compact(report, pins, baseline):
    return {
        'baseline_commit': baseline,
        'support_code_sha256': pins,
        'evaluation_note': 'Inspected development questions; document identity is the frozen return proxy, not semantic entailment certification.',
        'datasets': {name: {
            'sha256': data['sha256'], 'role': data['role'],
            'metrics': data['metrics']['supported'],
            'rows': [dict(id=row['id'], question=row['question'],
                          expected=row['expected'], expected_doc=row.get('expected_doc'),
                          supported=row['supported']) for row in data['rows']],
        } for name, data in report['datasets'].items()},
    }


def evaluate(output, baseline=BASELINE):
    baseline = git('rev-parse', '--verify', baseline+'^{commit}').decode().strip()
    source = git('show', baseline+':mplpb_answers/support.py')
    paths = git('ls-tree', '-r', '--name-only', baseline, 'mplpb_answers').decode().splitlines()
    pins = {Path(p).name: hashlib.sha256(git('show', baseline+':'+p)).hexdigest()
            for p in paths if p.endswith('.py')}
    original = reliability.supported_answer
    try:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'baseline.py'
            path.write_bytes(source)
            spec = importlib.util.spec_from_file_location('mplpb_answers._practical_baseline', path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # Baseline support imports the unchanged current frame/procedure/literal
            # helpers. Refuse comparison if their bytes differ from the baseline.
            for name, digest in pins.items():
                if name != 'support.py' and code_pins().get(name) != digest:
                    raise ValueError('Baseline helper changed: '+name)
            reliability.supported_answer = module.supported_answer
            before = compact(reliability.evaluate(), pins, baseline)
    finally:
        reliability.supported_answer = original
    after = compact(reliability.evaluate(), code_pins(), baseline)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    for label, result in [('before', before), ('after', after)]:
        (output/(label+'.json')).write_text(json.dumps(result, separators=(',', ':'))+'\n')
    print(json.dumps({name: {'before': before['datasets'][name]['metrics'],
                             'after': data['metrics']}
                      for name, data in after['datasets'].items()}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-ref', default=BASELINE)
    parser.add_argument('--output', default='evaluation/practical-coverage')
    args = parser.parse_args()
    evaluate(args.output, args.baseline_ref)
