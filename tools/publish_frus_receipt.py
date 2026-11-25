"""Publish a receipt while withholding text from permission-reprinted sources."""
import argparse
import hashlib
import json
from pathlib import Path


def redact(value):
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if key in {'text', 'quote', 'body', 'body_html', 'html'} and isinstance(item, str) and item:
                result[key+'_sha256'] = hashlib.sha256(item.encode()).hexdigest()
                result[key+'_characters'] = len(item)
            else:
                result[key] = redact(item)
        return result
    return [redact(item) for item in value] if isinstance(value, list) else value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('receipt', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--restricted', nargs='+', required=True)
    args = parser.parse_args()
    raw = args.receipt.read_bytes()
    data = json.loads(raw)
    if not isinstance(data, dict) or not isinstance(data.get('cases'), list) or 'runtime_sha256' not in data:
        raise ValueError('Expected an execution receipt, never a custody key')
    for number, row in enumerate(data['cases']):
        records = row.get('records', row.get('receipts', []))
        if any(record['id'] in args.restricted for record in records):
            data['cases'][number] = redact(row)
    data.update(complete_private_receipt_sha256=hashlib.sha256(raw).hexdigest(),
                permission_reprinted_bodies_and_excerpts_omitted=True)
    with args.output.open('x') as stream:
        stream.write(json.dumps(data, indent=2, ensure_ascii=False)+'\n')


if __name__ == '__main__':
    main()
