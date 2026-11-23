"""Freeze a local or public UTF-8 source and one exact, seeded sample."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


LIMIT = 4 * 1024 * 1024


def read_bytes(stream):
    raw = stream.read(LIMIT + 1)
    if len(raw) > LIMIT:
        raise ValueError('The source exceeds the 4 MiB sample limit')
    return raw


def capture(url, file):
    if file:
        with file.open('rb') as stream:
            return read_bytes(stream), {'kind': 'local_file', 'filename': file.name}
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Use a public HTTPS source without credentials')
    request = Request(url, headers={'User-Agent': 'MPLPB-D10-research-probe/1.0'})
    with urlopen(request, timeout=20) as response:
        if urlsplit(response.geturl()).scheme != 'https':
            raise ValueError('Source redirected outside HTTPS')
        return read_bytes(response), {'kind': 'live_web', 'requested_url': url,
                                      'final_url': response.geturl(),
                                      'retrieved_at': datetime.now(timezone.utc).isoformat()}


def sample(raw, seed, source_pin):
    text = raw.decode('utf-8')
    boundaries = list(re.finditer(r'\r?\n[ \t]*(?:\r?\n)+', text))
    starts = [0, *(match.end() for match in boundaries)]
    ends = [*(match.start() for match in boundaries), len(text)]
    candidates = [(start, end) for start, end in zip(starts, ends)
                  if 100 <= end - start <= 1200 and sum(char.isalpha() for char in text[start:end]) >= 60]
    if not candidates:
        raise ValueError('No UTF-8 paragraph fits the sample boundaries')
    def rank(bounds):
        return sha256(f'{seed}\0{source_pin}\0{bounds[0]}'.encode()).digest()
    start, end = min(candidates, key=rank)
    offset = len(text[:start].encode('utf-8'))
    return offset, text[start:end].encode('utf-8')


def freeze(output, raw, origin, seed, rights_url):
    source_pin = sha256(raw).hexdigest()
    start, excerpt = sample(raw, seed, source_pin)
    end = start + len(excerpt)
    if raw[start:end] != excerpt:
        raise ValueError('Sample bytes do not match the original')
    output.mkdir()
    (output / 'source.bin').write_bytes(raw)
    (output / 'sample.txt').write_bytes(excerpt)
    receipt = {'schema': 'mplpb-d10-capture-v1', 'origin': origin, 'seed': seed,
               'rights_url': rights_url, 'encoding': 'UTF-8',
               'source': {'path': 'source.bin', 'sha256': source_pin, 'bytes': len(raw)},
               'sample': {'path': 'sample.txt', 'sha256': sha256(excerpt).hexdigest(),
                          'byte_start': start, 'byte_end': end},
               'answer_supported': False, 'state': 'source_frozen'}
    (output / 'manifest.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--url')
    source.add_argument('--file', type=Path)
    parser.add_argument('--seed', required=True)
    parser.add_argument('--rights-url')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        raw, origin = capture(args.url, args.file)
        freeze(args.output, raw, origin, args.seed, args.rights_url)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
