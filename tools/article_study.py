"""Replay unchanged original-record questions through read-only article assembly.

Compares native contracts, not semantic correctness. Frozen seal verification
hashes recorded files, including references; expected answers are never parsed
or supplied as checker input. This is not a key-isolated evaluation.
New output directories only; original corpora and retained reports stay intact.
"""
import argparse
from collections import Counter
import csv
import gzip
import hashlib
import json
from pathlib import Path
import platform
import resource
import subprocess
import sys
import tempfile
import time

from mplpb_answers.pipeline import answer_query
from mplpb_combined.reader import PROFILES
from mplpb_work.article import assemble
from tools.sorter_first_study import FAMILIES, ROOT
from tools.unprepared_challenge import frozen
from tools.unprepared_sources import import_corpus


def file_pins(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file()}


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')


def run(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    start, cpu = time.perf_counter(), time.process_time()
    rows, packets, counts = [], [], Counter()
    unchanged = True
    seals = {}
    for family, (path, seal) in FAMILIES.items():
        corpus = ROOT/path
        frozen(corpus, seal)
        seals[family] = {'corpus': path, 'seal': seal,
            'seal_sha256': hashlib.sha256((corpus/seal).read_bytes()).hexdigest(),
            'questions_sha256': hashlib.sha256((corpus/'questions.json').read_bytes()).hexdigest()}
        cases = json.loads((corpus/'questions.json').read_text())['cases']
        with tempfile.TemporaryDirectory(prefix='mplpb-article-study-') as tmp:
            ledger = Path(tmp)/'ledger'
            receipt = import_corpus(corpus, ledger)
            save(output/(family+'-import-receipt.json'), receipt)
            before = file_pins(ledger)
            # Fixed input order and grouping; no case-specific source rule.
            for offset in range(0, len(cases), 8):
                batch = cases[offset:offset+8]
                standalone = [answer_query(ledger, c['question'], PROFILES['internal'],
                               max_passages=12, max_chars=8000).contract for c in batch]
                article = assemble(ledger, {'title': 'Original-record research dossier',
                                   'questions': [c['question'] for c in batch]},
                                   'internal', max_passages=12, max_chars=8000)
                packets.append({'family': family, 'ids': [c['id'] for c in batch],
                                'standalone': standalone, 'article': article})
                sections = article['sections']
                for n, (case, native) in enumerate(zip(batch, standalone)):
                    assembled = sections[n]['report']['native_answer'] if n < len(sections) else None
                    same = assembled == native
                    row = {'id': case['id'], 'family': family, 'question': case['question'],
                           'native_kind': native['kind'],
                           'assembled_kind': assembled['kind'] if assembled else 'withheld',
                           'exact_contract_preserved': same,
                           'answer_supported': native['answer_supported']}
                    rows.append(row)
                    counts[native['kind']] += 1
            unchanged = unchanged and before == file_pins(ledger)
        frozen(corpus, seal)
    with gzip.GzipFile(filename=str(output/'packets.json.gz'), mode='wb', mtime=0) as stream:
        stream.write(json.dumps(packets, ensure_ascii=False, sort_keys=True).encode())
    with (output/'cases.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    guards = {'all_native_contracts_preserved': all(r['exact_contract_preserved'] for r in rows),
              'ledger_files_unchanged': unchanged,
              'no_article_support_awarded': all(p['article']['answer_supported'] is False for p in packets),
              'no_automatic_cross_section_edges': all(p['article']['cross_section_relationships'] == [] for p in packets),
              'no_independence_awarded': all(p['article']['provenance']['independence_verified'] is False for p in packets)}
    report = {'schema': 'article-preservation-study-v1', 'cases': len(rows), 'articles': len(packets),
              'native_outcomes': dict(counts), 'guards': guards, 'originals': seals,
              # Exported source archives intentionally contain no .git. Do not
              # mistake an ancestor repository (or caller's Git environment)
              # for the exported implementation's identity. File pins below
              # remain available; retain the ZIP revision receipt separately.
              'revision': (subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
                           if (ROOT/'.git').exists() else None),
              'runtime_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for package in ('mplpb_answers', 'mplpb_work', 'mplpb_combined')
                  for p in sorted((ROOT/package).glob('*.py'))},
              'costs': {'wall_seconds': time.perf_counter()-start, 'cpu_seconds': time.process_time()-cpu,
                        'peak_process_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                        'source_bytes_read': None, 'human_review_seconds': None},
              'environment': {'python': sys.version, 'platform': platform.platform(),
                              'rss_units': 'Linux ru_maxrss KiB converted to bytes; whole study process'},
              'independent_semantic_review': 'NOT RUN',
              'scope': 'Development preservation check on unchanged originals. No new historical proof rule or accuracy gain. Not a blinded or key-isolated evaluation.'}
    save(output/'report.json', report)
    print(json.dumps(report, indent=2))
    return 0 if all(guards.values()) else 1


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    return run(p.parse_args().output)


if __name__ == '__main__':
    raise SystemExit(main())
