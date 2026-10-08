"""Bounded BFS over literal main-slot wiki links; links are navigation, not proof."""
import re
from tools import wiki_live_eval as W

MAX_PAGES = 5
MAX_REQUESTS = 10
MAX_DEPTH = 2

def links(page):
    source = page['revisions'][0]['slots']['main']['*']
    source = re.sub(r'<!--.*?-->', '', source, flags=re.S)
    source = re.sub(r'<nowiki\b[^>]*>.*?</nowiki>', '', source, flags=re.S | re.I)
    result = []
    for value in re.findall(r'\[\[([^\[\]]+)\]\]', source):
        title = value.split('|', 1)[0].split('#', 1)[0].replace('_', ' ').strip()
        if not title or ':' in title or any(c in title for c in '\n\r{}<>') or len(title) > 200:
            continue
        if title not in result: result.append(title)
        if len(result) >= 12: break
    return result

async def collect(found, fetch):
    results = found.get('results', [])
    if not results: return {'search':found, 'sources':[], 'edges':[], 'failures':[], 'limits':limits()}
    queue = [(results[0]['title'], None, 0)]
    requested, canonical, sources, edges, failures = set(), set(), [], [], []
    while queue and len(sources) < MAX_PAGES and len(requested) < MAX_REQUESTS:
        title, parent, depth = queue.pop(0)
        normalized = title.casefold()
        if normalized in requested: continue
        requested.add(normalized)
        try:
            raw, metadata = await fetch(title)
            pages = W.pages(raw)
            if len(pages) != 1: raise ValueError('Page missing or ambiguous')
            page = next(iter(pages.values()))
            pin = W.source_pin(page)
            if page['title'].casefold() in canonical: continue
            canonical.add(page['title'].casefold())
            sources.append({'requested':title, 'title':page['title'], 'raw':raw, 'metadata':metadata, 'pin':pin})
            if parent: edges.append({'from':parent, 'to':page['title'], 'depth':depth, 'status':'literal navigation link; not a factual relation'})
            if depth < MAX_DEPTH:
                queue.extend((child, page['title'], depth + 1) for child in links(page))
        except Exception as exc:
            failures.append({'title':title, 'reason':str(exc)})
            # A failed seed does not silently switch to a different search result.
            if parent is None: break
    return {'search':found, 'sources':sources, 'edges':edges, 'failures':failures, 'limits':limits()}

def limits():
    return {'pages':MAX_PAGES, 'page_requests':MAX_REQUESTS, 'depth':MAX_DEPTH,
            'selection':'First search result, then breadth-first literal links in source order. Not semantic topic relevance.'}
