"""Verify frozen originals and reverse canonical citation coordinates to raw bytes.

Canonical text normalizes layout. raw_excerpt is the untouched contiguous source
slice, with markup/layout retained. These are distinct outputs, never conflated.
"""
import re
from tools.unprepared_sources import verify, inside, sha, projected
from mplpb_answers.body_text import body_text


from mplpb_answers.source_projection import projection_offsets


def original_passage(directory,receipt,evidence):
    manifest=verify(directory)
    matches=[r for r in receipt['records'] if r['id']==evidence['source_id'] and r['path']==evidence['path'] and r['hash']==evidence['hash']]
    if len(matches)!=1:raise ValueError('No unique imported original mapping')
    record=matches[0];sources=[s for s in manifest['sources'] if s['id']==record['original_id']]
    if len(sources)!=1:raise ValueError('No original source')
    source=sources[0];raw=inside(directory,source['path']).read_bytes();text=raw.decode(source['encoding'])
    if sha(raw)!=record['original_sha256']:raise ValueError('Original revision changed')
    fragment=text;offset=0
    if source['media_type']=='text/html':
        m=re.search(r'<body\b[^>]*>([\s\S]*)</body\s*>',text,re.I)
        if not m:raise ValueError('Missing body envelope')
        fragment=m[1];offset=m.start(1)
    projection,starts,ends=projection_offsets(fragment,source['media_type']=='text/html')
    a=record['projection_character_start']+evidence['body_start'];b=record['projection_character_start']+evidence['body_end']
    if type(a) is not int or type(b) is not int or not 0<=a<b<=len(projection) or projection[a:b]!=evidence['quote']:raise ValueError('Canonical evidence changed')
    positions=[i for i in range(a,b) if starts[i]>=0 and ends[i]>=0]
    if not positions:raise ValueError('No raw source characters')
    ca=offset+min(starts[i] for i in positions);cb=offset+max(ends[i] for i in positions)
    ba=len(text[:ca].encode(source['encoding']));bb=len(text[:cb].encode(source['encoding']))
    excerpt=raw[ba:bb].decode(source['encoding'])
    return {'original_id':source['id'],'original_sha256':sha(raw),'original_url':source['url'],
        'original_character_start':ca,'original_character_end':cb,'original_byte_start':ba,'original_byte_end':bb,
        'raw_excerpt':excerpt,'raw_excerpt_sha256':sha(raw[ba:bb]),'canonical_quote':projection[a:b],
        'projection_version':record['projection_version'],'round_trip_quote_fidelity':True,
        'semantic_relationship_verified':False,'answer_supported':False,
        'notice':'Raw excerpt retains source markup and layout; canonical quote uses the existing normalized projection.'}
