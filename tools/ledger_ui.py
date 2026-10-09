#!/usr/bin/env python3
"""Local browser UI: python3 tools/ledger_ui.py [--root /path/to/corpus]."""
import argparse
import copy
import base64
import hashlib
import re
import json
import sys
import threading
import uuid
import asyncio
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mplpb_combined import ledger as L, reader as R, provenance_gate as G
from mplpb_combined.delivery import external_restriction
from mplpb_combined.record import text_of
from tools import wiki_live_eval as W
from tools.topic_chat_sources import TopicStore
from tools import chat_logic as C
from tools import deterministic_mind as M
from tools.mind_session import SessionStore
from tools.exploration_store import ExplorationStore
from tools import topic_crawl as TC
from tools import chat_tutor as T
from tools import reference_resources as F
from tools import grounded_chat as Q
from tools import social_chat as S
from tools import response_construction as N
from tools import chat_environment as E


class App:
    def __init__(self, custom=None, topic_base=None, session_path=None):
        self.topics = TopicStore(topic_base or ROOT / "local/topics")
        self.chat_lock = threading.RLock()
        self.session_store = SessionStore(session_path or (Path(topic_base).resolve() / 'session-save.json' if topic_base else ROOT / 'local/sessions/state.json'))
        self.sessions = self.session_store.load()
        self.collections = ExplorationStore(self.topics.base.parent / 'collections')
        self.corpora = {
            'canned': ('Patch canned · uneven names', ROOT / 'examples/patch-canned'),
            'studio': ('Pottery studio', ROOT / 'examples/studio'),
            'gate': ('D&D and budget · separate sources', ROOT / 'examples/provenance-gate/separate'),
            'dogs': ('Dog clarification', ROOT / 'examples/clarification-dogs'),
            'system': ('MPLPB · system and creator', ROOT / 'examples/system'),
            'logic': ('Chat logic · synthetic facts', ROOT / 'examples/chat-logic'),
            'reference': ('Reference encyclopedia · 23 archived Wiki pages', ROOT / 'resources/encyclopedia/capture/corpus'),
        }
        if custom:
            custom = Path(custom).resolve()
            if not custom.is_dir():
                raise ValueError('Custom corpus folder does not exist')
            self.corpora['custom'] = ('Your local corpus', custom)

    def roots(self):
        roots = dict(self.corpora)
        for key, entry in self.collections.entries().items():
            roots[key] = (entry['name'], self.collections.path(key) / 'combined')
        try:
            roots['wiki'] = ('Wiki · active local head', W.latest() / 'corpus')
        except (OSError, ValueError):
            pass
        if (self.topics.base / 'head.json').exists():
            loaded = self.topics.head()
            roots['topics'] = ('Your imported topics', self.topics.path(loaded[0]['bundle'] + '/corpus'))
        return roots

    def root(self, key):
        if key == 'reference':return F.encyclopedia_root()
        if isinstance(key, str) and key.startswith('mind-'):
            return self.collections.root(key)
        if key == 'topics':
            return self.topics.root()
        if key not in self.roots():
            raise ValueError('Unknown corpus')
        return self.roots()[key][1]

    def state(self):
        corpora = []
        for key, (label, root) in self.roots().items():
            if key.startswith('mind-'):
                try:
                    root = self.collections.root(key)
                except (OSError, ValueError, KeyError) as exc:
                    corpora.append({'key': key, 'label': label + ' · blocked; reimport or restore required',
                                    'records': len(L.Ledger(root).records), 'eligible': 0, 'reason': str(exc)})
                    continue
            ledger = L.Ledger(root)
            if key == 'topics':
                try:
                    self.topics.root()
                except ValueError:
                    label += ' · blocked; refresh required'
                    corpora.append({'key': key, 'label': label, 'records': len(ledger.records), 'eligible': 0})
                    continue
            corpora.append({'key': key, 'label': label, 'records': len(ledger.records),
                            'eligible': len(ledger.servable())})
        return {'chat_rules': C.RULES, 'corpora': corpora, 'profiles': list(R.PROFILES),
                'notice': 'Local lexical retrieval. Source declarations are not authenticated authorship.'}

    def create_collection(self, data):
        with self.chat_lock:
            return self.collections.create(data.get('name'))

    def import_source(self, data):
        with self.chat_lock:
            return self.collections.add(data.get('corpus'), data.get('title'), data.get('url'), data.get('text'))

    def reset_collection(self, data):
        return self.reset_collections({'corpora':[data.get('corpus')]})

    def reset_collections(self, data):
        with self.chat_lock:
            keys=data.get('corpora')
            entries=self.collections.entries()
            if not isinstance(keys,list) or not 1 <= len(keys) <= 32 or any(not isinstance(k,str) or k not in entries for k in keys) or len(set(keys)) != len(keys):
                raise ValueError('Select 1–32 distinct saved collections; bundled corpora cannot be cleared')
            previous = self.sessions
            updated = {sid: s for sid, s in self.sessions.items() if s['corpus'] not in keys}
            self.session_store.save(updated); self.sessions = updated
            try: return self.collections.reset_many(keys,previous)
            except Exception:
                self.session_store.save(previous); self.sessions = previous
                raise

    def topic_store(self, corpus):
        return self.collections.topics(corpus) if isinstance(corpus, str) and corpus.startswith('mind-') else self.topics

    def prepare_search(self, query, wiki):
        if wiki == 'web': raise ValueError('Hosted web crawling uses the standalone browser build; choose a Wikipedia mode in desktop mode.')
        found = self.topics.search(query, wiki)
        async def fetch(title): return W.request(W.APIS[wiki], [title])
        return asyncio.run(TC.collect(found, fetch))

    def build_search(self, query, wiki):
        plan = self.prepare_search(query, wiki)
        if not plan['sources']:
            return None, {'kind':'crawl_failed', 'message':'No pinned seed page was captured. No MPLPB was built.',
                          'search':plan['search'], 'crawl':{k:v for k,v in plan.items() if k not in {'sources','search'}},
                          'context':None, 'sources':[], 'reasoning':['Search snippets were not promoted to source evidence.']}
        collection = self.collections.create(query[:80])
        key = collection['corpus']; store = self.collections.topics(key)
        imported, failures = [], list(plan['failures'])
        original = W.request
        try:
            for source in plan['sources']:
                def supplied(api, titles, source=source):
                    if api != W.APIS[wiki] or titles != [source['requested']]: raise ValueError('Crawl import request differs')
                    return source['raw'], source['metadata']
                W.request = supplied
                try: imported.append(store.import_title(source['requested'], wiki))
                except Exception as exc: failures.append({'title':source['title'], 'reason':str(exc)})
        finally: W.request = original
        self.collections.root(key)
        crawl = {'query':query, 'wiki':wiki, 'searched_at':plan['search'].get('searched_at'),
                 'seed':plan['sources'][0]['title'], 'limits':plan['limits'], 'edges':plan['edges'],
                 'imported':[{'title':s['title'], 'pin':s['source_pin'], 'capture':s['capture']} for s in imported], 'failures':failures}
        self.collections.record_crawl(key,crawl)
        if not imported:
            return key, {'kind':'crawl_failed','message':'Pinned imports failed. The empty collection and failure record were retained.', 'crawl':crawl,'context':None,'sources':[],'reasoning':['No source answer or evaluation score claimed.']}
        context = C.context_for(self.root(key), imported[0]['title'], 'internal') if imported else None
        return key, {'kind':'built', 'message':'Built MPLPB “'+collection['name']+'” with '+str(len(imported))+' pinned pages. '+
                    ('Some linked pages failed; see the crawl record. ' if failures else '')+'Ask “what is it?” or “summarize it”, or select another exact page title.',
                    'crawl':crawl, 'context':context, 'sources':[context] if context else [],
                    'reasoning':['Bounded literal-link crawl; navigation links do not prove relationships.', 'Revision main slots pinned; no evaluation score or semantic relevance claim.']}

    def inventory(self, corpus, profile):
        root = self.root(corpus)
        if profile not in R.PROFILES:
            raise ValueError('Unknown profile')
        policy = R.PROFILES[profile]
        ledger = L.Ledger(root)
        current = {r.path for r in ledger.servable()}
        pages = []
        for rec in ledger.records:
            depth = ledger.depth(rec)
            reason = ledger.quarantine_reason(rec)
            eligible = rec.path in current
            if not reason and not eligible:
                reason = 'retired' if ledger.effective_status(rec) == 'retired' else 'not current or valid lineage'
            if eligible and external_restriction(rec, policy):
                eligible, reason = False, 'withheld by external profile'
            if eligible and policy.max_depth is not None and depth > policy.max_depth:
                eligible, reason = False, 'withheld by depth limit'
            pages.append({'id': rec.id, 'path': rec.path, 'title': rec.title,
                          'scope': rec.scope, 'status': ledger.effective_status(rec),
                          'origin': rec.origin, 'depth': depth, 'intact': rec.intact,
                          'eligible': eligible, 'reason': reason})
        return {'pages': pages, 'profile': profile,
                'eligible': sum(p['eligible'] for p in pages),
                'notice': 'Inventory lists local records; eligibility does not certify their claims.'}

    def query(self, data):
        question = data.get('question')
        if not isinstance(question, str) or not question.strip() or len(question) > 4000:
            raise ValueError('Enter a question of 1–4000 characters')
        name = data.get('profile', 'internal')
        if name not in R.PROFILES:
            raise ValueError('Unknown profile')
        if data.get('corpus') not in self.roots():raise ValueError('Unknown corpus')
        help_result=M.help_reply(question,None)
        if help_result:
            return {'help':help_result,'reader':{'kind':'help','question':question,'text':help_result['message'],'profile':name,'matched_on':'interface instruction intent'},'gate':{'sources':[]},'live_verified_by_this_query':False}
        root = self.root(data.get('corpus'))
        profile = R.PROFILES[name]
        answer = R.answer(root, question, profile)
        reader = answer.to_dict()
        reader['citation'] = answer.citation()
        if answer.record:
            reader['title'] = answer.record.title
        gate = G.gather(root, question, profile).to_dict()
        return {'reader': reader, 'gate': gate, 'live_verified_by_this_query': False}

    def page(self, corpus, path, profile):
        root = self.root(corpus)
        if profile not in R.PROFILES:
            raise ValueError('Unknown profile')
        ledger = L.Ledger(root)
        records = [r for r in ledger.servable() if r.path == path]
        if len(records) != 1:
            raise ValueError('Page is absent, altered or not current')
        rec = records[0]
        p = R.PROFILES[profile]
        if external_restriction(rec, p) or (p.max_depth is not None and ledger.depth(rec) > p.max_depth):
            raise ValueError('Page is withheld by this profile')
        return {'id': rec.id, 'title': rec.title, 'path': rec.path, 'text': text_of(rec.body_html),
                'hash': rec.hash, 'fields': rec.fields, 'depth': ledger.depth(rec)}

    def chat(self, data):
        message = data.get('message')
        if not isinstance(message, str) or not 1 <= len(message.strip()) <= 4000:
            raise ValueError('Chat needs 1–4000 characters')
        message = message.strip()
        corpus, profile = data.get('corpus'), data.get('profile', 'internal')
        if profile not in R.PROFILES or corpus not in self.roots():
            raise ValueError('Unknown corpus or profile')
        with self.chat_lock:
            sid = data.get('session')
            if sid:
                if sid not in self.sessions:
                    raise ValueError('Chat session expired; start a new chat')
                session = copy.deepcopy(self.sessions[sid])
                if session['corpus'] != corpus or session['profile'] != profile:
                    session['context'] = None
                    session.setdefault('mind',{}).pop('social',None)
                    session['corpus'], session['profile'] = corpus, profile
            else:
                if len(self.sessions) >= 32:
                    raise ValueError('Save slots full; explicitly restart an old session to free one. No session was deleted.')
                sid = uuid.uuid4().hex
                session = {'corpus': corpus, 'profile': profile, 'context': None, 'log': [], 'mind': {'notes': []}}
            if len(session['log']) >= 1000:
                raise ValueError('1000-turn save limit reached. State retained; export before an explicit restart.')
            wiki = data.get('wiki', 'simple')
            memory=session.setdefault('mind',{'notes':[]})
            if T.casual_key(message) not in {'yes','yes please','lets explore',"let's explore",'no','no thanks','keep chatting','stay casual'}:
                memory.pop('topic_offer',None)
            casual=None
            environment_result=E.handle(self,data,session,message,corpus,profile)
            open_casual=T.casual_followup(message,session['context'],memory) if environment_result is None else None
            if environment_result is None and casual is None and (T.smalltalk_candidate(message,memory) or open_casual is not None or S.candidate(message,memory)):
                try:titles=[p['title'] for p in self.inventory(corpus,profile)['pages'] if p['eligible']]
                except (ValueError,OSError):titles=[]
                casual=T.smalltalk(message,session['context'],memory,titles,corpus+'|'+profile)
                if open_casual is not None and casual.get('kind')=='smalltalk' and not casual.get('response_structure',{}).get('topic_mentions'):
                    casual=open_casual
                if 'select_topic' in casual:
                    casual=C.turn(self,corpus,self.root(corpus),profile,'topic '+casual['select_topic'],session['context'])
                elif not casual.get('response_structure',{}).get('topic_mentions'):
                    social=S.handle(message,session['context'],memory)
                    if social is not None:casual=social
            tutor=environment_result or F.handle(message,session['context']) or casual or T.conversation(message,session['context'],memory) or T.guide(message,session['context'],memory) or T.learning_request(message,session['context'])
            if tutor is not None:result=tutor
            elif T.key(message) in T.LIST:
                try:
                    pages=[p for p in self.inventory(corpus,profile)['pages'] if p['eligible']]
                    result=M.reply('collection','Your MPLPB has '+str(len(pages))+' eligible page(s).\n\n'+('\n'.join(p['title'] for p in pages[:40]) if pages else 'No eligible pages are loaded. Choose a Wikipedia mode and build a topic collection.')+'\n\nWhich page would you like to explore?',session['context'],'INVENTORY-1',authority='local_inventory',topics=[p['title'] for p in pages[:40]],suggestions=['topic '+p['title'] for p in pages[:4]]+['how do I search?','guide me'])
                except (ValueError,OSError) as exc:
                    result=M.reply('clarify','This collection is blocked: '+str(exc)+'\n\nIts saved files remain. Use search to build a fresh collection under this runtime, or refresh the old collection by explicitly reimporting its titles. You can also use the confirmed clear controls. Help still works.',None,'INVENTORY-BLOCKED',suggestions=['how do I search?','how do I clear all?','guide me'])
            elif message.lower().startswith('search '):
                if len(self.sessions) >= 32: raise ValueError('Save slots full; no crawl or collection created')
                if len(self.collections.entries()) >= 32: raise ValueError('Collection limit reached; no crawl created')
                built, result = self.build_search(message[7:].strip(), wiki)
                if built:
                    corpus = built
                    if data.get('session'): sid = uuid.uuid4().hex
                    active_guide=memory.get('guide',{}).get('active')
                    session = {'corpus':corpus,'profile':profile,'context':None,'log':[], 'mind':{'notes':[]}}
                    if active_guide:session['mind']['guide']={'active':True,'step':2}
                    if profile != 'internal':
                        result['context'], result['sources'] = None, []
                        result['message'] += ' Sources remain subject to the selected delivery profile.'
            elif message.lower().startswith('find '):
                found = self.topic_store(corpus).search(message[5:].strip(), wiki)
                result = {'kind': 'search', 'message': 'Choose a title to import. Search snippets are not local evidence.',
                          'search': found, 'sources': [], 'reasoning': ['Explicit remote topic search; no source claims inferred.'],
                          'context': session['context']}
            elif message.lower().startswith('import '):
                imported = self.topic_store(corpus).import_title(message[7:].strip(), wiki)
                corpus = corpus if corpus.startswith('mind-') else 'topics'
                context = None
                delivery_notice = ''
                try:
                    context = C.context_for(self.root(corpus), imported['title'], profile)
                except ValueError as exc:
                    delivery_notice = ' Local capture retained, but this profile/collection cannot serve it: ' + str(exc)
                result = {'kind': 'import', 'message': imported['notice'] + delivery_notice, 'imported': imported,
                          'context': context, 'sources': [context] if context else [],
                          'reasoning': ['Main revision slot SHA-1 and wikitext SHA-256 checked; raw bytes retained.']}
            elif (guide := M.help_reply(message, session['context'])) is not None:
                result = guide
            elif message.lower().strip(' ?.!') in {'who made you', 'who is your creator', 'what are you',
                   'what can you do', 'about yourself', 'who am i', 'mplpb creator', 'who created you',
                   'who are you', 'what is mplpb', 'what is your name', 'what is your purpose',
                   'who made mplpb', 'who created mplpb', 'who built you', 'tell me about yourself',
                   'what are your rules', 'what are your limits', 'how do you work'}:
                own = self.query({'corpus': 'system', 'profile': profile, 'question': 'MPLPB system creator'})
                result = {'kind': own['reader']['kind'], 'message': own['reader']['text'], 'reader': own['reader'],
                          'gate': own['gate'], 'context': session['context'], 'sources': own['gate']['sources'],
                          'reasoning': ['SELF-1: return the sealed self-reference page; creator attribution is a declaration, not identity authentication.']}
            else:
                interpreted=T.local_phrase(message)
                result = M.handle(self.root(corpus), profile, interpreted, session['context'], session.setdefault('mind', {'notes': []}))
                if result is None:
                    result = Q.handle(self, corpus, self.root(corpus), profile, interpreted, session['context'])
                if result is None:
                    result = C.turn(self, corpus, self.root(corpus), profile, interpreted, session['context'])
                if result['kind'] in {'not_in_corpus','unknown_relation'}:
                    offer = Q.missing(message,result.get('context'))
                    result['message'] += '\n\n' + offer['message']
                    result['suggestions'] = offer['suggestions']
                    result['source_offer'] = offer['source_offer']
                if interpreted!=message:result.setdefault('reasoning',[]).append({'rule':'PHRASE-1','interpreted_as':interpreted})
            if result['kind'] in {'import','built'}:
                session['environment']={'mode':'focus','corpora':[corpus],'focus_corpus':corpus if result.get('context') else None}
            if session.get('environment'):
                result['environment']=copy.deepcopy(session['environment'])
                if result.get('context') and session['environment'].get('focus_corpus'):
                    result['source_corpus']=session['environment']['focus_corpus']
                    result['sources']=[dict(s,corpus=result['source_corpus']) for s in result.get('sources',[])]
                result.setdefault('response_structure',{}).setdefault('mode',session['environment']['mode'])
                if session['environment']['mode']=='chat' and result.get('authority')=='conversation_structure':
                    result['support_notice']=E.D.NOTICE
                    result['response_structure']['mplpb_supported']=False
            if not result.get('response_structure',{}).get('intent','').startswith('social_'):
                session['mind'].pop('social',None)
            session['corpus'], session['context'] = corpus, result.get('context')
            T.followups(result,session['mind'])
            M.record(session.setdefault('mind', {'notes': []}), result)
            payload = {'question': message, 'corpus': corpus, 'profile': profile, 'response': result}
            payload['mind_version'] = M.VERSION
            payload['mind_sha256'] = hashlib.sha256(Path(M.__file__).read_bytes()).hexdigest()
            payload['grounded_chat_version'] = Q.VERSION
            payload['grounded_chat_sha256'] = hashlib.sha256(Path(Q.__file__).read_bytes()).hexdigest()
            payload['casual_rules_version']=E.D.VERSION
            payload['casual_rules_sha256']=hashlib.sha256(Path(E.D.__file__).read_bytes()).hexdigest()
            payload['environment_version'] = E.VERSION
            payload['environment_sha256'] = hashlib.sha256(Path(E.__file__).read_bytes()).hexdigest()
            payload['construction_version'] = N.VERSION
            payload['construction_sha256'] = hashlib.sha256(Path(N.__file__).read_bytes()).hexdigest()
            payload['social_chat_version'] = S.VERSION
            payload['social_chat_sha256'] = hashlib.sha256(Path(S.__file__).read_bytes()).hexdigest()
            entry = C.log_turn(session['log'], payload)
            updated = dict(self.sessions, **{sid: session})
            self.session_store.save(updated)
            self.sessions = updated
            return {'session': sid, 'corpus': corpus, 'profile': profile, 'response': result,
                    'turn': entry['index'], 'turn_sha256': entry['sha256'],
                    'mind': {'notes': list(session['mind']['notes']), 'context': session['context']},
                    'logic_version': M.VERSION, 'notice': 'Deterministic chat; explicit context and rules. No language model.'}

    def export_chat(self, data):
        with self.chat_lock:
            if data.get('session') not in self.sessions:
                raise ValueError('Unknown chat session')
            log = self.sessions[data['session']]['log']
            return {'schema': 1, 'turns': list(log), 'chain_intact': C.verify_log(log),
                    'notice': 'Hash continuity only. Not authenticated authorship, source truth or an evaluation score.'}

    def reset_chat(self, data):
        with self.chat_lock:
            updated = dict(self.sessions)
            updated.pop(data.get('session'), None)
            self.session_store.save(updated)
            self.sessions = updated
        return {'reset': True}

    def resume_chat(self, data):
        with self.chat_lock:
            sid = data.get('session')
            if sid not in self.sessions:
                raise ValueError('Saved session unavailable. Nothing was automatically restarted.')
            session = self.sessions[sid]
            return {'session': sid, 'corpus': session['corpus'], 'profile': session['profile'],
                    'context': session['context'], 'notes': list(session.get('mind', {}).get('notes', [])),
                    'turns': copy.deepcopy(session['log']), 'chain_intact': C.verify_log(session['log'])}

    def history(self, corpus=None):
        head_path = W.KIT / 'head.json'
        head = json.loads(head_path.read_text()) if head_path.exists() else None
        versions = []
        for folder in ('captures', 'archives'):
            for path in sorted((W.KIT / folder).glob('*/manifest.json'), reverse=True):
                manifest = json.loads(path.read_text())
                rel = path.parent.relative_to(W.KIT).as_posix()
                versions.append({'path': rel, 'active': bool(head and head['snapshot'] == rel),
                    'schema': manifest.get('schema'), 'source': manifest.get('api'),
                    'observed_at': manifest.get('request', {}).get('retrieved_at'),
                    'renderer': manifest.get('renderer'), 'pages': manifest.get('pages', []),
                    'history': manifest.get('history'), 'status': manifest.get('status', 'retained capture'),
                    'code_matches_now': not W.code_errors(manifest.get('code', {}))})
        versions.sort(key=lambda item: item.get('observed_at') or '', reverse=True)
        collection = None
        topics = self.topics
        if isinstance(corpus, str) and corpus.startswith('mind-'):
            self.collections.root(corpus)
            topics = self.collections.topics(corpus)
            entry = self.collections.entries()[corpus]
            collection = {'name': entry['name'], 'captures': [json.loads((self.collections.path(corpus) / 'captures' / c['id'] / 'manifest.json').read_text()) for c in entry.get('captures', [])],
                          'crawl': json.loads((self.collections.path(corpus)/'crawl.json').read_text()) if entry.get('crawl_sha256') else None}
        return {'head': head, 'versions': versions, 'topic_history': topics.history(), 'collection_history': collection,
                'notice': 'Capture and verification dates are separate. Stored passes are historical; this view makes no live request.'}

    def experiment(self):
        base = ROOT / 'docs/patch-canned/supplied'
        return {'report': json.loads((base / 'experiment/results.json').read_text()),
                'note': (base / 'EXPERIMENT.md').read_text(),
                'status': 'Supplied experiment, preserved unchanged; live claims not independently rerun.'}


def handler(app):
    html = (ROOT / 'index.html').read_bytes()
    scripts = re.findall(rb'<script>(.*?)</script>', html, re.DOTALL)
    script_pins = ' '.join("'sha256-" + base64.b64encode(hashlib.sha256(script.replace(b'\r\n', b'\n').replace(b'\r', b'\n')).digest()).decode() + "'" for script in scripts)
    class Handler(BaseHTTPRequestHandler):
        def send(self, status, body, mime='application/json; charset=utf-8'):
            if not isinstance(body, bytes):
                body = json.dumps(body, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src " + script_pins + "; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def local(self):
            port = self.server.server_port
            return self.headers.get('Host') in {f'127.0.0.1:{port}', f'localhost:{port}'}

        def do_GET(self):
            if not self.local():
                return self.send(403, {'error': 'Local host required'})
            route = urlsplit(self.path)
            try:
                if route.path in ('/', '/index.html'):
                    return self.send(200, html, 'text/html; charset=utf-8')
                if route.path == '/api/inventory':
                    q = parse_qs(route.query)
                    return self.send(200, app.inventory(q['corpus'][0], q.get('profile', ['internal'])[0]))
                if route.path == '/api/state':
                    return self.send(200, app.state())
                if route.path == '/api/history':
                    return self.send(200, app.history(parse_qs(route.query).get('corpus', [None])[0]))
                if route.path == '/api/experiment':
                    return self.send(200, app.experiment())
                if route.path == '/api/page':
                    q = parse_qs(route.query)
                    return self.send(200, app.page(q['corpus'][0], q['path'][0], q.get('profile', ['internal'])[0]))
                return self.send(404, {'error': 'Not found'})
            except (OSError, ValueError, TypeError, KeyError, W.SourceUnavailable) as exc:
                return self.send(400, {'error': str(exc)})

        def do_POST(self):
            if not self.local():
                return self.send(403, {'error': 'Local host required'})
            origin = self.headers.get('Origin')
            if origin and origin != 'http://' + self.headers.get('Host', ''):
                return self.send(403, {'error': 'Origin rejected'})
            operations = {'/api/query': app.query, '/api/chat': app.chat,
                          '/api/collections/reset-many': app.reset_collections,
                          '/api/collections/create': app.create_collection, '/api/collections/reset': app.reset_collection, '/api/source/import': app.import_source,
                          '/api/chat/resume': app.resume_chat, '/api/chat/export': app.export_chat, '/api/chat/reset': app.reset_chat}
            if self.path not in operations:
                return self.send(404, {'error': 'Not found'})
            if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                return self.send(415, {'error': 'JSON required'})
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 16384:
                    raise ValueError('Invalid request size')
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict):
                    raise ValueError('Request must be an object')
                return self.send(200, operations[self.path](data))
            except (OSError, ValueError, TypeError, KeyError, W.SourceUnavailable) as exc:
                return self.send(400, {'error': str(exc)})
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path)
    parser.add_argument('--port', type=int, default=8766)
    parser.add_argument('--open', action='store_true', help='Open the local UI in your default browser')
    args = parser.parse_args()
    app = App(args.root)
    server = ThreadingHTTPServer(('127.0.0.1', args.port), handler(app))
    print(f'Local ledger UI: http://127.0.0.1:{server.server_port}', flush=True)
    if args.open:
        import threading
        import webbrowser
        browser_url = f'http://127.0.0.1:{server.server_port}'
        if args.root:
            browser_url += '?corpus=custom'
        threading.Thread(target=webbrowser.open, args=(browser_url,), daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
