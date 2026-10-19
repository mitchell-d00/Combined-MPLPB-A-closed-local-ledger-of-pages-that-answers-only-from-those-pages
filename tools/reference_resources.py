"""Explicit offline lexical references. Never expands ledger ownership words."""
from functools import lru_cache
import copy
import gzip
import hashlib
import json
from pathlib import Path
import re
import zipfile
from tools import deterministic_mind as M
from tools import context_index as CX
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
    # Historical captures keep their original engine pin permanently.
    # A reader update changes the current engine byte hash; it cannot rewrite
    # the old capture. Permit *read-only* archival reference access only when
    # every stored source, served-page, and renderer pin still validates.
    # All other code errors remain fatal; no historical verification is claimed.
    errors=W.stored_errors(snapshot,data)
    code_errors=W.code_errors(data['code'])
    errors += [e for e in code_errors if e != 'engine bytes differ from capture pin']
    if errors:raise ValueError('Reference encyclopedia blocked: '+'; '.join(errors))
    return snapshot/'corpus'

@lru_cache(maxsize=16)
def archive_json(path,sha,name):
    with zipfile.ZipFile(path) as archive:return json.loads(archive.read(name))

@lru_cache(maxsize=1)
def synset_index(path,sha):
    return json.loads(gzip.decompress(Path(path).read_bytes()))

@lru_cache(maxsize=1)
def headword_index(path,sha):
    """Keep every upstream spelling, including capitals and the nonletter bucket."""
    result={}
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if name.startswith('entries-') and name.endswith('.json'):
                for word in json.loads(archive.read(name)):
                    result.setdefault(word.casefold(),[]).append((name,word))
    return result

def lookup(word):
    m=verify();archive=m['resources'][0];path=BASE/archive['path']
    index_info=next(r for r in m['resources'] if r['name']=='MPLPB derived WordNet synset file index')
    index=synset_index(str(BASE/index_info['path']),index_info['sha256'])
    word=word.strip().casefold()
    if not word or len(word)>200 or not word.isprintable():raise ValueError('Use one word or short phrase of up to 200 characters')
    entries=headword_index(str(path),archive['sha256']).get(word,[])
    senses=[]
    seen=set()
    for entry_name,spelling in entries:
        for pos,value in archive_json(str(path),archive['sha256'],entry_name)[spelling].items():
            for sense in value.get('sense',[]):
                identifier=sense['synset'];name=index.get(identifier)
                if not name:raise ValueError('WordNet derived index incomplete')
                if identifier in seen:continue
                seen.add(identifier)
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

def handle(message,context,offset=0,mode=None):
    command=message.strip()
    if command.casefold().strip('?.!') in {'language resources','reference resources','grammar resources','grammar guide'}:
        m=verify()
        return M.reply('reference','Offline references: Open English WordNet 2025 for definitions, synonyms and sense relations; CMU Link Grammar English data for language structures; 23 bundled revision-pinned Simple English Wikipedia pages, plus on-demand access to English and Simple English Wikipedia through the source selector. Captured articles are saved locally; the whole encyclopedia is not bundled.\n\nChoose the Dictionary or Thesaurus topic, try “define dog” or “synonyms dog”, or choose the Reference encyclopedia corpus. Grammar data is archived for development; this app does not run the Link Grammar parser. Synonyms never become page ownership words automatically.',context,'REFERENCE-CATALOG',authority='resource_catalog',suggestions=['define dog','synonyms dog','show my MPLPB'],resources=m['resources'])
    match=re.fullmatch(r'(?:define|dictionary|synonyms(?: for)?|thesaurus)\s+(.{1,200})|what does (.{1,200}?) mean[?.!]*',command,re.I)
    if not match:return None
    word=(match[1] or match[2]).strip();headword,senses,m=lookup_forms(word)
    if not senses and word.rstrip('?.!') and word.rstrip('?.!')!=word:
        word=word.rstrip('?.!');headword,senses,m=lookup_forms(word)
    if not senses:return M.reply('reference_missing','No exact entry for “'+word+'” in Open English WordNet 2025. Try a dictionary headword. This is not a claim that the word does not exist.',context,'REFERENCE-MISSING',authority='lexical_reference',suggestions=['language resources'])
    lines=['Open English WordNet 2025 · '+headword+'\nMeanings are separate senses; synonyms are not interchangeable in every context.']
    if headword!=word.casefold():lines.append('No exact entry for '+word+'; showing the possible base form '+headword+'.')
    offset=max(0,min(offset,((len(senses)-1)//12)*12))
    page=senses[offset:offset+12]
    for sense in page:
        lines.append(sense['id']+' ('+sense['part_of_speech']+')\n'+'; '.join(sense['definitions'])+'\n'+('Synonyms in this sense: ' if mode=='thesaurus' else 'Synset words: ')+', '.join(sense['synonyms']))
    lines.append('Senses '+str(offset+1)+'–'+str(offset+len(page))+' of '+str(len(senses))+'.')
    archive=m['resources'][0]
    lines.append('Source: '+archive['url']+'\nLicense: CC-BY-4.0 · Open English WordNet Community, derived from Princeton WordNet.')
    choices=(['previous senses'] if offset else [])+(['next senses'] if offset+12<len(senses) else [])
    return M.reply('reference','\n\n'.join(lines),context,'REFERENCE-EXACT',authority='lexical_reference',sources=[{'id':'OEWN-2025','hash':archive['sha256'],'path':'resources/'+archive['path'],'url':archive['url'],'license':'CC-BY-4.0'}],senses=page,headword=headword,sense_page={'offset':offset,'total':len(senses)},suggestions=choices+['topic dictionary','topic thesaurus'])


def topic_request(message,session):
    """Recognize lexical navigation without constructing a reply or changing state."""
    from tools import self_knowledge as SK
    if SK.recognize(message):return False
    text=message.strip();key=text.casefold().strip('?.!')
    state=session.get('mind',{}).get('reference_topic')
    if re.fullmatch(r'(?:(?:topic|open|use)\s+)?(?:the\s+)?(dictionary|thesaurus)',key):return True
    if state and key in {'leave dictionary','leave thesaurus','close dictionary','close thesaurus','exit reference'}:return True
    if state and state.get('word') and key in {'next senses','previous senses'}:return True
    meaning=re.fullmatch(r'what does (.{1,200}?) mean[?.!]*',text,re.I)
    if meaning:return CX.key(meaning[1]) not in CX.prepare(copy.deepcopy(session))['vocabulary']
    if re.fullmatch(r'(?:define|dictionary|synonyms(?: for)?|thesaurus)\s+.{1,200}',text,re.I):return True
    if not state or not text or len(text)>200 or not text.isprintable() or len(text.split())>5:return False
    if key in {'hi','hello','hey','thanks','thank you','bye','help','just chat','chat mode','serious mode'}:return False
    return len(text.split())==1 or bool(lookup(text)[0])


def topic(message,session):
    """Explicit lexical topic state; never loads a ledger or adds ownership words."""
    text=message.strip();key=text.casefold().strip('?.!')
    mind=session.setdefault('mind',{});state=mind.get('reference_topic')
    selected=re.fullmatch(r'(?:(?:topic|open|use)\s+)?(?:the\s+)?(dictionary|thesaurus)',key)
    context=session.get('context')
    if selected:
        mode=selected[1];mind['reference_topic']={'mode':mode}
        counts=verify()['wordnet_counts']
        return M.reply('reference',mode.title()+' topic · Open English WordNet 2025\n\n'+
            format(counts['entries'],',')+' entries; '+format(counts['senses'],',')+' senses in the complete bundled edition. This is not every English word.\n\n'+
            'Enter a word, or use “define dog” or “synonyms happy”. Use “next senses” to read beyond the first page. Say “leave dictionary” to return to ordinary chat.\n\n'+
            'Definitions and sense-specific synonyms are lexical references, separate from ledger evidence. Synonyms do not expand ownership rules.',
            context,'REFERENCE-TOPIC',authority='resource_catalog',reference_topic=mode,
            suggestions=['define dog','synonyms happy','leave dictionary'])
    if state and key in {'leave dictionary','leave thesaurus','close dictionary','close thesaurus','exit reference'}:
        mind.pop('reference_topic',None)
        return M.reply('conversation','Reference topic closed. What would you like to talk about?',context,'REFERENCE-CLOSE',authority='conversation_structure')
    meaning=re.fullmatch(r'what does (.{1,200}?) mean[?.!]*',text,re.I)
    if meaning and CX.key(meaning[1]) in CX.prepare(session)['vocabulary']:
        mind.pop('reference_topic',None)
        return None
    explicit=bool(meaning or re.match(r'^(?:define|dictionary|thesaurus|synonyms(?: for)?)\s+',text,re.I))
    offset=0;command=text;mode=(state or {}).get('mode','dictionary')
    if state and key in {'next senses','previous senses'} and state.get('word'):
        offset=state.get('offset',0)+(12 if key=='next senses' else -12)
        command='define '+state['word']
    elif explicit:
        mode='thesaurus' if re.match(r'^(?:synonyms|thesaurus)\b',text,re.I) else 'dictionary'
    elif state and len(text)<=200 and text.isprintable() and len(text.split())<=5 and key not in {'hi','hello','hey','thanks','thank you','bye','help','just chat','chat mode','serious mode'}:
        # A known multiword headword is a lookup; other sentences keep normal routing.
        if len(text.split())>1 and not lookup(text)[0]:
            mind.pop('reference_topic',None);return None
        command='define '+text
    else:
        if state:mind.pop('reference_topic',None)
        return None
    result=handle(command,context,offset,mode)
    if result is None:return None
    page=result.get('sense_page',{})
    mind['reference_topic']={'mode':mode,'word':result.get('headword'),'offset':page.get('offset',0)}
    result['reference_topic']=mode
    result['suggestions']=result.get('suggestions',[])+['leave dictionary']
    return result
