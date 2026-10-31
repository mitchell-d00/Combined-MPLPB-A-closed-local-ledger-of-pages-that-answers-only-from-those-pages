"""Manage a local specialist work ledger; credentials never go in command arguments."""
import argparse
import json
import os
from pathlib import Path
import sys
from .store import WorkStore
from .errors import WorkError
from .api import request


def read_json(path):
    text = sys.stdin.read(64001) if path == '-' else Path(path).read_text()
    if len(text) > 64000:
        raise WorkError('Request exceeds 64 KB')
    return json.loads(text)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init', help='initialize; print the host credential once')
    init.add_argument('directory')
    init.add_argument('--corpus', action='append', default=[], metavar='NAME=PATH')
    call = sub.add_parser('request', help='submit JSON using an explicit credential file or MPLPB_WORK_TOKEN')
    call.add_argument('directory')
    call.add_argument('--credential-file')
    call.add_argument('--input', default='-', help='request JSON file; default stdin')
    args = parser.parse_args(argv)
    try:
        if args.command == 'init':
            corpora = {}
            for item in args.corpus:
                key, separator, value = item.partition('=')
                if not separator or key in corpora:
                    raise WorkError('Corpora require unique NAME=PATH entries')
                corpora[key] = value
            store, credential = WorkStore.create(args.directory, corpora)
            result = {'authority_credential': credential, 'head': store.head(credential)}
        else:
            credential = os.environ.get('MPLPB_WORK_TOKEN', '')
            if args.credential_file:
                value = read_json(args.credential_file)
                credential = value if isinstance(value, str) else value.get('credential', value.get('authority_credential', ''))
            result = request(WorkStore(args.directory), credential, read_json(args.input), host_operations=True)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (WorkError, OSError, ValueError, KeyError) as exc:
        print(json.dumps({'error': str(exc), 'operation_completed': False}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
