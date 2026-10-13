"""Explicit library navigation; route declarations select scopes, never facts.

The route catalog contains metadata only. Page bodies are read only after a
single leaf has been selected, and the supported reader checks that whole leaf.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

from mplpb_combined.ledger import Ledger
from mplpb_combined.reader import PROFILES
from mplpb_combined.delivery import external_restriction
from .support import supported_answer

VERSION = 'library-routing-v1'


def key(text):
    return ' '.join(text.casefold().split())


class Library:
    def __init__(self, roots, manifest=None, resolve=None):
        self.roots = roots
        self.resolve = resolve or (lambda name: roots[name][1])
        if manifest is None:
            manifest = {'version': 1, 'root': 'main', 'nodes': [
                {'id': 'main', 'title': 'Main Index', 'parent': None}]+[
                {'id': 'shelf-'+name, 'title': label, 'parent': 'main',
                 'corpus': name, 'aliases': [name]}
                for name, (label, _) in sorted(roots.items())]}
        self.manifest = json.loads(json.dumps(manifest))
        nodes = self.manifest.get('nodes')
        if self.manifest.get('version') != 1 or not isinstance(nodes, list) or not 1 <= len(nodes) <= 10000:
            raise ValueError('Library needs version 1 and 1–10000 route nodes.')
        self.nodes = {}; self.children = {}; self.aliases = {}
        for node in nodes:
            if not isinstance(node, dict) or set(node)-{'id','title','parent','corpus','aliases'}:
                raise ValueError('Unknown library node fields.')
            ident = node.get('id'); title = node.get('title'); aliases = node.get('aliases', [])
            if not isinstance(ident, str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}', ident) or ident in self.nodes:
                raise ValueError('Library IDs must be unique safe identifiers.')
            if not isinstance(title, str) or not title.strip() or len(title)>160 or '\n' in title:
                raise ValueError('Library titles need 1–160 characters on one line.')
            if not isinstance(aliases, list) or len(aliases)>32 or any(not isinstance(a,str) or not a.strip() or len(a)>160 or '\n' in a for a in aliases):
                raise ValueError('Invalid library aliases.')
            if 'corpus' in node and (not isinstance(node['corpus'],str) or node['corpus'] not in roots):
                raise ValueError('Library leaf names an unregistered corpus.')
            self.nodes[ident] = node
            self.children[ident] = []
            for alias in [ident,title]+aliases:
                self.aliases.setdefault(key(alias), set()).add(ident)
        self.root = self.manifest.get('root')
        if not isinstance(self.root,str) or self.root not in self.nodes or self.nodes[self.root].get('parent') is not None:
            raise ValueError('Library needs one parentless root.')
        corpora = set()
        for ident,node in self.nodes.items():
            if ident != self.root:
                parent = node.get('parent')
                if not isinstance(parent,str) or parent not in self.nodes: raise ValueError('Library node has a missing parent.')
                self.children[parent].append(ident)
            if 'corpus' in node:
                if node['corpus'] in corpora: raise ValueError('Register each corpus in one leaf only.')
                corpora.add(node['corpus'])
        for ident,node in self.nodes.items():
            if 'corpus' in node and self.children[ident]: raise ValueError('A corpus leaf cannot have children.')
            seen=set(); current=ident
            while current is not None:
                if current in seen: raise ValueError('Library route cycle.')
                seen.add(current); current=self.nodes[current].get('parent')
                if len(seen)>64: raise ValueError('Library depth exceeds 64.')
            if self.root not in seen: raise ValueError('Unreachable library node.')
            self.children[ident].sort()
        self.digest=hashlib.sha256(json.dumps(self.manifest,sort_keys=True,separators=(',',':')).encode()).hexdigest()

    def path(self, ident):
        result=[]
        while ident is not None:
            result.append({'id':ident,'title':self.nodes[ident]['title'],
                           'command':'library browse '+ident})
            ident=self.nodes[ident].get('parent')
        return list(reversed(result))

    def choices(self, ids):
        return [{'id':i,'title':self.nodes[i]['title'],'command':'library choose '+i}
                for i in sorted(ids)]

    def match(self, name):
        # IDs are unambiguous explicit addresses; duplicate human aliases ask.
        return [name] if name in self.nodes else sorted(self.aliases.get(key(name), set()))

    def leaves(self, ident):
        pending=[ident]; found=[]
        while pending:
            item=pending.pop()
            if 'corpus' in self.nodes[item]: found.append(item)
            pending.extend(self.children[item])
        return sorted(found)

    def inventory(self, corpus, profile):
        root=self.resolve(corpus); ledger=Ledger(root); policy=PROFILES[profile]
        eligible=[]
        for record in ledger.servable():
            depth=ledger.depth(record)
            if record.kind == 'pointer' or external_restriction(record,policy): continue
            if policy.max_depth is not None and depth>policy.max_depth: continue
            eligible.append({'id':record.id,'title':record.title,'path':record.path,
                             'hash':record.hash,'corpus':corpus})
        return sorted(eligible,key=lambda p:(p['path'],p['id']))

    def base(self, status, ident, message, choices=(), offset=0):
        path=self.path(ident)
        total=len(choices); choices=list(choices)[offset:offset+20]
        return {'kind':status,'message':message,'context':None,'sources':[],
                'authority':'library_navigation','suggestions':[c['command'] for c in choices][:12],
                'library_route':{'version':VERSION,'catalog_sha256':self.digest,
                    'selected':ident,'path':path,'path_back':list(reversed(path)),
                    'choices':list(choices),'choices_total':total,'choices_offset':offset,'related_pages':[],
                    'metadata_is_evidence':False,'source_truth_verified':False,
                    'rule':'LIBRARY-BROAD' if status=='collection' else 'LIBRARY-NARROW'},
                'response_structure':{'intent':'library_navigation','factual_claims':False,'mplpb_supported':False}}

    def finish(self, result):
        route=result['library_route']; related=route['related_pages']
        if result['kind']=='clarify' and route['choices']:
            result['message']+='\n\nChoose scope:\n'+'\n'.join(c['title']+' ['+c['id']+']' for c in route['choices'])
        total=route['choices_total']; offset=route['choices_offset']
        if total>offset+20:
            command='library '+('choices ' if result.get('library_proof') else 'browse ')+route['selected']+' page '+str(offset//20+2)
            result['message']+='\n\nMore shelves: '+command
            result['suggestions'].append(command)
        if related:
            result['message']+='\n\nRelated pages (navigation, not answer evidence):\n'+'\n'.join(p['title']+' ['+p['corpus']+'/'+p['path']+']' for p in related)
        result['message']+='\n\nBack: '+' → '.join(p['title']+' ['+p['id']+']' for p in route['path_back'])
        if route['selected']!=self.root:result['suggestions'].append('library browse '+self.root)
        return result

    def browse(self, name=None, profile='internal', page=1):
        if not isinstance(page,int) or page<1:raise ValueError('Invalid library page.')
        if profile not in PROFILES: raise ValueError('Unknown profile.')
        matches=self.match(name or self.root)
        if len(matches)!=1:
            return self.finish(self.base('clarify',self.root,'Choose one exact library shelf; unknown or shared names are not resolved by guessing.',self.choices(matches or self.children[self.root])))
        ident=matches[0]; node=self.nodes[ident]; children=self.children[ident]
        result=self.base('collection',ident,node['title'],self.choices(children),offset=(page-1)*20)
        if children:
            result['message']+='\n\nSub-index:\n'+'\n'.join(c['title']+' ['+c['id']+']' for c in result['library_route']['choices'])
        elif 'corpus' in node:
            try: pages=self.inventory(node['corpus'],profile)
            except (ValueError,OSError,KeyError):
                result['kind']='unsupported'; result['message']='This library shelf is unavailable or fails its source checks.'
            else:
                result['message']+='\n\n'+str(len(pages))+' eligible local pages (metadata, not answers):\n'+'\n'.join(p['title']+' ['+p['path']+']' for p in pages[:20])
                result['message']+='\nAsk: library ask in '+ident+': <your question>'
                result['library_route']['pages']=pages[:20]
        else: result['message']+='\n\nThis shelf has no registered books.'
        return self.finish(result)

    def answer(self, question, name=None, profile='internal', page=1):
        if not isinstance(page,int) or page<1:raise ValueError('Invalid library page.')
        if profile not in PROFILES: raise ValueError('Unknown profile.')
        if not isinstance(question,str) or not question.strip() or len(question)>4000: raise ValueError('Enter a question of 1–4000 characters.')
        matches=self.match(name or self.root)
        if len(matches)!=1:
            result=self.base('clarify',self.root,'The shelf is unknown or ambiguous. Narrow to one listed scope.',self.choices(matches or self.children[self.root]))
        else:
            ident=matches[0]; leaves=self.leaves(ident)
            if len(leaves)!=1:
                result=self.base('clarify',ident,'No single scope owns this request yet. Choose a sub-index or book; pages from different scopes will not be blended.',self.choices(self.children[ident]),offset=(page-1)*20)
            else:
                ident=leaves[0]; corpus=self.nodes[ident]['corpus']
                result=self.base('unsupported',ident,'No eligible page supports that complete question in this scope.')
                try:
                    root=self.resolve(corpus)
                    answer=supported_answer(root,question,PROFILES[profile])
                    pages=self.inventory(corpus,profile)
                    # Pointer targets must be registered as their own library leaf.
                    if Path(answer.root).resolve()!=Path(root).resolve():
                        result['message']='This route points outside its registered book. Choose a separately registered destination shelf.'
                    elif answer.kind=='ambiguous':
                        result['kind']='clarify'; result['message']='Conflicting or multiple eligible pages within this scope. Narrow the question or revise the source conflict; no answer was selected.'
                    elif answer.kind=='return' and answer.record:
                        pin=next((p for p in pages if p['path']==answer.record.path and p['hash']==answer.record.hash),None)
                        if pin:
                            result.update(kind='return',message=answer.text+'\n\nSource: '+answer.citation(),sources=[pin],
                                          source_corpus=corpus,authority='gated_source',
                                          response_structure={'intent':'library_answer','factual_claims':True,'mplpb_supported':True})
                            result['library_route'].update(rule='LIBRARY-SPECIFIC',selected_page=pin,
                                related_pages=[p for p in pages if p['path']!=pin['path']][:3])
                            result['library_route']['support']=answer.support
                    # Absence of support is not permission to acquire or improvise.
                except (ValueError,OSError,KeyError):
                    result['message']='This library shelf is unavailable or fails its source checks. No answer was returned.'
                result['library_route']['checked_corpora']=[corpus]
        result['library_proof']={'version':VERSION,'catalog_sha256':self.digest,'question':question,'shelf':name,'profile':profile,'page':page}
        return self.finish(result)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path)
    parser.add_argument('--corpus',action='append',default=[],metavar='NAME=PATH')
    parser.add_argument('--profile',choices=sorted(PROFILES),default='internal')
    parser.add_argument('--shelf')
    parser.add_argument('--question')
    args=parser.parse_args(); roots={}
    for item in args.corpus:
        name,sep,path=item.partition('=')
        if not sep or not name or name in roots:parser.error('Use distinct --corpus NAME=PATH entries.')
        roots[name]=(name,Path(path))
    catalog=Library(roots,json.loads(args.manifest.read_text()) if args.manifest else None)
    result=catalog.answer(args.question,args.shelf,args.profile) if args.question else catalog.browse(args.shelf,args.profile)
    print(json.dumps(result,indent=2,ensure_ascii=False))


if __name__=='__main__':main()
