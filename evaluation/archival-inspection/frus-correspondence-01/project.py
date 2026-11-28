"""Recover unchanged FRUS TEI document bytes and project published text."""
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys
from xml.parsers import expat

IDS = {'d156', 'd157', 'd158', 'd159', 'd160', 'd162', 'd163'}
PIN = '216cdb7649a8e29504377d4f2858351dc46331a8'
URL = 'https://raw.githubusercontent.com/HistoryAtState/frus/' + PIN + '/volumes/frus1969-76v03.xml'
RECORD = 'https://history.state.gov/historicaldocuments/frus1969-76v03/'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, data):
    with path.open('x', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def project(raw, output):
    (output/'sources').mkdir(parents=True, exist_ok=True)
    sources = []
    rows = []
    parser = expat.ParserCreate()
    page = None
    active = None
    depth = 0
    excluded = 0
    notes = 0

    def append(value):
        if active is not None:
            active['parts'].append(value)

    def start(tag, attrs):
        nonlocal page, active, depth, excluded, notes
        depth += 1
        if tag == 'div' and attrs.get('xml:id') in IDS:
            assert active is None
            active = dict(id=attrs['xml:id'], depth=depth, byte_start=parser.CurrentByteIndex,
                          parts=[], pages=[page] if page else [], refs=[])
        if tag == 'pb':
            page = (attrs.get('n'), parser.CurrentByteIndex)
            if active is not None:
                active['pages'].append(page)
        if active is None:
            return
        if tag in ('head', 'dateline', 'opener', 'p', 'signed', 'closer', 'item', 'row'):
            append('\n')
        if tag == 'note':
            notes += 1
            append('\nEditorial note: ')
        if tag == 'ref' and attrs.get('target'):
            active['refs'].append({'target': attrs['target'], 'byte_start': parser.CurrentByteIndex,
                                   'editorial_note': bool(notes)})
        if tag in ('figure', 'graphic'):
            excluded += 1

    def chars(value):
        if excluded == 0:
            append(re.sub(r'\s+', ' ', value))

    def end(tag):
        nonlocal active, depth, excluded, notes
        if active is not None:
            if tag in ('head', 'dateline', 'p', 'note', 'signed', 'item', 'row'):
                append('\n')
            if tag == 'note':
                notes -= 1
            if tag in ('figure', 'graphic'):
                excluded -= 1
            if tag == 'div' and depth == active['depth']:
                stop = raw.index(b'>', parser.CurrentByteIndex) + 1
                original = raw[active['byte_start']:stop]
                assert original.startswith(b'<div') and original.endswith(b'</div>')
                ident = active['id']
                (output/'sources'/(ident+'.xml')).write_bytes(original)
                parts = active['parts']
                text = '\n'.join(line for line in (' '.join(x.split()) for x in ''.join(parts).splitlines()) if line)
                # Locate only the publisher's printed-page break at the source
                # fragment, with exact raw bytes available in the parent XML.
                markers = [int(n) for n, _ in active['pages'] if n and n.isdecimal()]
                rows.append({'id': ident, 'url': RECORD+ident, 'file': 'sources/'+ident+'.xml',
                             'sha256': sha(original), 'volume_byte_start': active['byte_start'], 'volume_byte_end': stop,
                             'printed_pages': list(dict.fromkeys(markers)),
                             'page_markers': [{'printed_page': int(n), 'volume_byte_offset': offset,
                                               'starts_before_fragment': offset < active['byte_start']}
                                              for n, offset in active['pages'] if n and n.isdecimal()],
                             'tei_refs': active['refs'],
                             'projection_sha256': sha(text.encode()), 'projection_characters': len(text)})
                sources.append({'id': ident, 'original_path': RECORD+ident, 'original_ref': PIN,
                                'sha256': sha(text.encode()), 'text': text})
                active = None
                notes = excluded = 0
        depth -= 1

    parser.StartElementHandler = start
    parser.CharacterDataHandler = chars
    parser.EndElementHandler = end
    parser.Parse(raw, True)
    assert {r['id'] for r in rows} == IDS
    save(output/'source-map.json', {'volume_url': URL, 'volume_sha256': sha(raw), 'volume_bytes': len(raw),
         'rights': 'US government public domain; publisher CC0 1.0. See sources/publisher-license.log.',
         'edition': 'Official diplomatic editions, no claim of manuscript facsimile or original envelope.',
         'printed_pages': sorted({n for row in rows for n in row['printed_pages']}), 'sources': rows})
    save(output/'corpus.json', {'schema': 'original-record-study-corpus-v1', 'sources': sources,
         'status': 'public_development', 'independence_verified': False})


if __name__ == '__main__':
    project(gzip.decompress(Path(sys.argv[1]).read_bytes()), Path(sys.argv[2]))
