"""Stage exact Pole focus cases and replay full historical document sections."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil

from tools import dpercent as D, pole, pole_authentic as A

ROOT = Path(__file__).resolve().parents[1]


def focus(source_packet, source_key, public, custody, prior):
    public, custody, source_packet, source_key = pole.paths_separate(
        public, custody, source_packet, source_key)
    _, original = pole.load_packet(source_packet, source_key)
    rows = A.read(prior)['cases']
    expected = {'over_refusal': 12, 'appropriate_refusal': 20}
    ids = [row['id'] for row in rows if row['outcome'] in expected]
    keys = pole.load_keys(source_key)
    for outcome, count in expected.items():
        if sum(row['outcome'] == outcome for row in rows) != count:
            raise ValueError('Original focus outcome counts changed')
    public.mkdir()
    custody.mkdir(mode=0o700)
    cases = {}
    for case_id in ids:
        cases[case_id] = {**original['cases'][case_id], 'cohort': 'pinned',
                          'origin_seal_sha256': A.digest((source_packet / 'seal.json').read_bytes())}
        shutil.copytree(source_packet / 'packets' / case_id, public / 'packets' / case_id)
    D.save(public / 'protocol.json', {'schema': pole.SCHEMA, 'cases': cases})
    D.save(custody / 'key.json', {'schema': pole.SCHEMA, 'cases': [keys[i] for i in ids]})
    shutil.copyfile(source_key / 'dice.json', custody / 'dice.json')
    for path in custody.iterdir():
        path.chmod(0o600)
    seal = {'public_files': D.files(public),
            'key_sha256': A.digest((custody / 'key.json').read_bytes()),
            'dice_sha256': A.digest((custody / 'dice.json').read_bytes()),
            'tools': pole.tool_pins()}
    D.save(public / 'seal.json', seal)
    D.save(custody / 'seal-copy.json', seal)
    pole.load_packet(public, custody)


def frus_fragment(raw, source):
    """Keep the publisher's complete numbered document div and exclude site chrome."""
    html = raw.decode(source['encoding'])
    ident = source['document_id']
    offsets = [0, *(m.end() for m in re.finditer(r'\n', html))]

    class Section(HTMLParser):
        def __init__(self):
            super().__init__()
            self.depth = 0
            self.begin = None
            self.spans = []

        def position(self):
            row, column = self.getpos()
            return offsets[row - 1] + column

        def handle_starttag(self, tag, attrs):
            if tag != 'div':
                return
            if self.depth:
                self.depth += 1
            else:
                fields = dict(attrs)
                if fields.get('id') == ident and 'tei-div3' in fields.get('class', '').split():
                    self.begin = self.position()
                    self.depth = 1

        def handle_endtag(self, tag):
            if tag == 'div' and self.depth:
                self.depth -= 1
                if not self.depth:
                    self.spans.append((self.begin, html.index('>', self.position()) + 1))

    section = Section()
    section.feed(html)
    section.close()
    if section.depth or len(section.spans) != 1:
        raise ValueError('Expected one closed FRUS document div')
    start, stop = section.spans[0]
    return html[start:stop]


def frus_rendered(raw, source):
    """Fold delivery whitespace while keeping publisher markup byte-for-byte."""
    fragment = frus_fragment(raw, source)
    offsets = [0, *(m.end() for m in re.finditer(r'\n', fragment))]

    class RenderedWhitespace(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=False)
            self.edits = []
            self.preformatted = 0

        def handle_starttag(self, tag, attrs):
            if tag in {'pre', 'textarea', 'script', 'style'}:
                self.preformatted += 1

        def handle_endtag(self, tag):
            if tag in {'pre', 'textarea', 'script', 'style'}:
                self.preformatted -= 1

        def handle_data(self, data):
            if self.preformatted:
                return
            replacement = re.sub(r'[ \t\r\n\f]+', ' ', data)
            if replacement == data:
                return
            row, column = self.getpos()
            start = offsets[row - 1] + column
            stop = start + len(data)
            if fragment[start:stop] != data:
                raise ValueError('Text-node offset diverged from original markup')
            self.edits.append((start, stop, replacement))

    parser = RenderedWhitespace()
    parser.feed(fragment)
    parser.close()
    cursor = 0
    parts = []
    for start, stop, replacement in parser.edits:
        parts.extend((fragment[cursor:start], replacement))
        cursor = stop
    parts.append(fragment[cursor:])
    return ''.join(parts)


def prepare_prose(captures, spec, public, custody):
    from mplpb_answers.body_text import body_text
    data = A.read(spec)
    by_id = {source['id']: source for source in data['sources']}
    for case in data['cases']:
        for ident, phrase in case['anchors']:
            source = by_id[ident]
            raw = (captures / source['filename']).read_bytes()
            if raw.count(phrase.encode(source['encoding'])) != 1:
                raise ValueError(f'Original anchor must be unique in {ident}')
            for projector in (frus_fragment, frus_rendered):
                if A.normal(phrase) not in A.normal(body_text(projector(raw, source))):
                    raise ValueError(f'Anchor lost in the publisher document projection: {ident}')
    A.prepare(captures, spec, public, custody)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name, fields in {
        'focus': ('source-packet', 'source-key', 'public', 'custody', 'prior'),
        'prepare-prose': ('captures', 'spec', 'public', 'custody'),
        'run-prose': ('packet', 'output', 'implementation'),
    }.items():
        child = commands.add_parser(name)
        for field in fields:
            child.add_argument('--' + field, required=True, type=Path)
    commands.choices['run-prose'].add_argument('--raw-layout', action='store_true')
    args = vars(parser.parse_args())
    command = args.pop('command')
    if command == 'run-prose':
        projector = frus_fragment if args.pop('raw_layout') else frus_rendered
        A.run(**args, project_source=projector)
    else:
        {'focus': focus, 'prepare-prose': prepare_prose}[command](**args)


if __name__ == '__main__':
    main()
