"""Explicit offline lexical references. Never expands ledger ownership words."""
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import re
import zipfile
from tools import deterministic_mind as M
from tools import wiki_live_eval as W

BASE=Path(__file__).resolve().parents[1]/'resources'
MANIFEST_SHA256='6a04e78dba6e9decc2259c4df40d9140e28998ebdabcf040e384611e88fd1e6f'

def manifest(base=BASE):
    raw=(base/'manifest.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=MANIFEST_SHA256:
        raise ValueError('Reference resource manifest pin differs')
    return json.loads(raw)

def verify(base=BASE):
    m=manifest(base)
    for archive in m.get('transport_archives',[]):
        target=base/archive['path']
        if not target.exists():
            chunks=[]
            for part in archive['parts']:
                path=(base/part['path']).resolve()
                if base.resolve() not in path.parents:
                    raise ValueError('Reference part path invalid')
                raw=path.read_bytes()
                if hashlib.sha256(raw).hexdigest()!=part['sha256']:
                    raise ValueError('Reference archive part bytes differ: '+part['path'])
                chunks.append(raw)
            raw=b''.join(chunks)
            if hashlib.sha256(raw).hexdigest()!=archive['sha256']:
                raise ValueError('Reference reconstructed archive pin differs')
            target.write_bytes(raw)
    for item in m['files']:
        path=(base/item['path']).resolve()
        if base.resolve() not in path.parents or hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:
            raise ValueError('Reference resource bytes differ: '+item['path'])
    return m

def encyclopedia_root():
    verify()
    snapshot=BASE/'encyclopedia/capture'
    data=json.loads((snapshot/'manifest.json').read_text())
    errors=W.stored_errors(snapshot,data)+W.code_errors(data['code'])
    if errors:raise ValueError('Reference encyclopedia blocked: '+'; '.join(errors))
    return snapshot/'corpus'

@lru_cache(maxsize=16)
def archive_json(path,sha,name):
    with zipfile.ZipFile(path) as archive:return json.loads(archive.read(name))

@lru_cache(maxsize=1)
def synset_index(path,sha):
    return json.loads(gzip.decompress(Path(path).read_bytes()))

def lookup(word):
    m=verify();archive=m['resources'][0];path=BASE/archive['path']
    index_info=next(r for r in m['resources'] if r['name']=='MPLPB derived WordNet synset file index')
    index=synset_index(str(BASE/index_info['path']),index_info['sha256'])
    word=word.strip().casefold()
    if not re.fullmatch(r"[a-z][a-z '\-]{0,79}",word):raise ValueError('Use one English word or short phrase')
    with zipfile.ZipFile(path) as z:
        name='entries-'+word[0]+'.json'
        if name not in z.namelist():return [],m
    entry=archive_json(str(path),archive['sha256'],name).get(word,{})
    senses=[]
    for pos,value in entry.items():
        for sense in value.get('sense',[]):
            identifier=sense['synset'];name=index.get(identifier)
            if not name:raise ValueError('WordNet derived index incomplete')
            source=archive_json(str(path),archive['sha256'],name)[identifier]
            senses.append({'id':identifier,'part_of_speech':pos,'definitions':source.get('definition',[]),'synonyms':source.get('members',[]),'examples':source.get('example',[]),'relations':{k:v for k,v in source.items() if k in {'hypernym','hyponym','antonym','similar','meronym','holonym'}}})
    return senses,m

def lookup_forms(word):
    """Conservative lexical fallback; never expands ledger ownership fields."""
    word=word.strip().casefold()
    senses,m=lookup(word)
    if senses:return word,senses,m
    candidates=[]
    if word.endswith('ies'):candidates.append(word[:-3]+'y')
    if word.endswith('es'):candidates.append(word[:-2])
    if word.endswith('s') and not word.endswith('ss'):candidates.append(word[:-1])
    for base in candidates:
        if len(base)<2:continue
        senses,m=lookup(base)
        if senses:return base,senses,m
    return word,[],m

def handle(message,context):
    command=message.strip()
    if command.casefold().strip('?.!') in {'language resources','reference resources','grammar resources','grammar guide'}:
        m=verify()
        return M.reply('reference','Offline references: Open English WordNet 2025 for definitions, synonyms and sense relations; CMU Link Grammar English data for language structures; 23 bundled revision-pinned Simple English Wikipedia pages, plus on-demand access to English and Simple English Wikipedia through the source selector. Captured articles are saved locally; the whole encyclopedia is not bundled.\n\nTry “define dog”, “synonyms dog”, or choose the Reference encyclopedia corpus. Grammar data is archived for development; this app does not run the Link Grammar parser. Synonyms never become page ownership words automatically.',context,'REFERENCE-CATALOG',authority='resource_catalog',suggestions=['define dog','synonyms dog','show my MPLPB'],resources=m['resources'])
    match=re.fullmatch(r'(?:define|dictionary|synonyms(?: for)?|thesaurus)\s+(.{1,80})|what does (.{1,80}) mean[?.!]*',command,re.I)
    if not match:return None
    word=(match[1] or match[2]).rstrip('?.!').strip();headword,senses,m=lookup_forms(word)
    if not senses:return M.reply('reference_missing','No exact entry for “'+word+'” in Open English WordNet 2025. Try a dictionary headword. This is not a claim that the word does not exist.',context,'REFERENCE-MISSING',authority='lexical_reference',suggestions=['language resources'])
    lines=['Open English WordNet 2025 · '+headword+'\nMeanings are separate senses; synonyms are not interchangeable in every context.']
    if headword!=word.casefold():lines.append('No exact entry for '+word+'; showing the possible base form '+headword+'.')
    for sense in senses[:12]:
        lines.append(sense['id']+' ('+sense['part_of_speech']+')\n'+'; '.join(sense['definitions'])+'\nSynset words: '+', '.join(sense['synonyms']))
    if len(senses)>12:lines.append('Showing 12 of '+str(len(senses))+' senses.')
    archive=m['resources'][0]
    lines.append('Source: '+archive['url']+'\nLicense: CC-BY-4.0 · Open English WordNet Community, derived from Princeton WordNet.')
    return M.reply('reference','\n\n'.join(lines),context,'REFERENCE-EXACT',authority='lexical_reference',sources=[{'id':'OEWN-2025','hash':archive['sha256'],'path':'resources/'+archive['path'],'url':archive['url'],'license':'CC-BY-4.0'}],senses=senses[:12],suggestions=['language resources','show my MPLPB'])
