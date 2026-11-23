"""Bounded parallel execution of independently sealed weakness-study shards.

Existing partial shards are preserved and never silently retried or overwritten.
Use a new output directory to repeat a study. Keys stay in the post-run parent.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from tools import dpercent as D
from tools import dpercent_expanded as E
from tools import dpercent_weaknesses as W


def _execute(public, destination, implementation):
    return D.run(public, destination, implementation=implementation)


def run(packets, custodian, output, implementation=D.ROOT, workers=4):
    packets, custodian, output, implementation = map(Path, (packets, custodian, output, implementation))
    if type(workers) is not int or not 1 <= workers <= 4: raise ValueError('Workers must be 1–4')
    manifest = D.read(packets/'study.json')
    if manifest != D.read(custodian/'study-copy.json'): raise ValueError('Study manifest changed')
    output.mkdir(parents=True, exist_ok=True)
    tasks = []
    for shard in manifest['shards']:
        name = shard['name']; public = packets/name; private = custodian/name
        if D.sha((public/'seal.json').read_bytes()) != shard['seal_sha256']: raise ValueError('Shard seal changed')
        D.verify(public, private)
        if not (output/name).exists(): tasks.append(name)
    errors = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        pending = {pool.submit(_execute, packets/name, output/name, implementation): name for name in tasks}
        for future in as_completed(pending):
            name = pending[future]
            try: future.result()
            except Exception as error: errors.append({'shard': name, 'error': str(error)})
            # Keys are opened only after that shard's execution returns.
            if (output/name/'run.json').exists():
                W.score_shard(packets/name, custodian/name, output/name, output/(name+'-score.json'))
            W.summarize(packets, custodian, output)
    if errors: D.save(output/'batch-errors.json', errors)
    result = W.summarize(packets, custodian, output)
    failures = {'execution_failure', 'invalid_output'}
    if errors or result['partial'] or any(failures.intersection(row['outcomes'])
                                         for row in result['by_family'].values()):
        return 1
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('packets', 'custodian', 'output'): p.add_argument('--'+name, type=Path, required=True)
    p.add_argument('--implementation', type=Path, default=D.ROOT); p.add_argument('--workers', type=int, default=4)
    a = p.parse_args(); raise SystemExit(run(a.packets, a.custodian, a.output, a.implementation, a.workers))


if __name__ == '__main__': main()
