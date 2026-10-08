#!/usr/bin/env python3
"""Capture a new wiki snapshot, then verify it before lexical smoke scoring.

Historical incomplete snapshots are never repaired by inventing missing pins.
Raw response bytes and full local pages are retained separately. Authorship is
unknown; local retrieval and external withholding are scored separately.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mplpb_combined import ledger as L, reader as R, provenance_gate as G
from tools import wiki_render as WR

KIT = ROOT / 'evaluation/wiki'
APIS = {'simple': 'https://simple.wikipedia.org/w/api.php',
        'english': 'https://en.wikipedia.org/w/api.php'}
UA = 'mplpb-wiki-eval/2.0 (local provenance and refusal smoke check)'


class SourceUnavailable(RuntimeError):
    """A failed fetch is not a changed source or a scored evaluation."""
    def __init__(self, status, retry_after=None):
        self.status = status
        self.retry_after = retry_after
        super().__init__('wiki HTTP ' + str(status) + '; not scored' +
                         ('; Retry-After: ' + retry_after if retry_after else ''))


def stamp():
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def request_url(api, titles):
    return api + '?' + urllib.parse.urlencode({
        'action': 'query', 'format': 'json', 'redirects': 1,
        'prop': 'revisions', 'rvslots': 'main',
        'rvprop': 'ids|timestamp|content|sha1|slotsha1|contentmodel', 'titles': '|'.join(titles)})


def request(api, titles):
    url = request_url(api, titles)
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read()
            metadata = {'url': url, 'retrieved_at': datetime.now(timezone.utc).isoformat(),
                        'http_status': response.status, 'content_type': response.headers.get('Content-Type', '')}
    except urllib.error.HTTPError as exc:
        raise SourceUnavailable(exc.code, exc.headers.get('Retry-After')) from exc
    pages(raw)  # reject malformed/error responses before creating any snapshot
    return raw, metadata


def pages(raw):
    payload = json.loads(raw.decode('utf-8'))
    if payload.get('error'):
        raise ValueError('Wiki API error: ' + str(payload['error']))
    return {p['title']: p for p in payload['query']['pages'].values() if 'missing' not in p}


def engine_hash():
    h = hashlib.sha256()
    for p in sorted((ROOT / 'mplpb_combined').glob('*.py')):
        h.update(p.name.encode()); h.update(b'\0'); h.update(p.read_bytes())
    return h.hexdigest()


def code_pins():
    revision = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True)
    return {'engine_sha256': engine_hash(), 'checker_sha256': digest(Path(__file__).read_bytes()),
            'renderer_sha256': renderer_pin()['sha256'],
            'base_revision': revision.stdout.strip() if revision.returncode == 0 else None,
            'notice': 'Byte consistency only; not authenticated authorship or independent validation.'}


def code_errors(pins):
    errors = []
    if engine_hash() != pins.get('engine_sha256'):
        errors.append('engine bytes differ from capture pin')
    if digest(Path(__file__).read_bytes()) != pins.get('checker_sha256'):
        errors.append('checker bytes differ from capture pin')
    if renderer_pin()['sha256'] != pins.get('renderer_sha256'):
        errors.append('renderer bytes differ from capture pin')
    if Path(WR.__file__).resolve() != ROOT / 'tools/wiki_render.py':
        errors.append('imported renderer outside pinned local file')
    for name, module in list(sys.modules.items()):
        if name == 'mplpb_combined' or name.startswith('mplpb_combined.'):
            path = getattr(module, '__file__', None)
            if path and (ROOT / 'mplpb_combined').resolve() not in Path(path).resolve().parents:
                errors.append('imported engine module outside pinned package: ' + name)
    return errors


def source_pin(page):
    try:
        rev = page['revisions'][0]
        slot = rev['slots']['main']
        text = slot['*']
        sha1 = slot['sha1']
    except (KeyError, TypeError, IndexError) as exc:
        raise ValueError('revision has no readable main slot and SHA-1') from exc
    if slot.get('contentmodel') != 'wikitext' or not isinstance(text, str):
        raise ValueError('main slot is not readable wikitext')
    if hashlib.sha1(text.encode('utf-8')).hexdigest() != sha1:
        raise ValueError('main slot SHA-1 disagrees with received wikitext')
    return {'revid': rev['revid'], 'slot_sha1': sha1,
            'wikitext_sha256': digest(text.encode('utf-8'))}


def renderer_pin():
    return {'version': WR.VERSION, 'sha256': digest(Path(WR.__file__).read_bytes())}


def source_body(page, api):
    source_pin(page)
    site = api.split('/w/api.php')[0]
    rev = page['revisions'][0]
    return (WR.render(rev['slots']['main']['*']) + '\n\nSource: ' + site + '/wiki/' +
            urllib.parse.quote(page['title'].replace(' ', '_')) +
            '?oldid=' + str(rev['revid']) +
            '\nLicense: CC BY-SA 4.0; Wikipedia contributors.\n'
            'Source authorship: unknown; contributor identity is not authenticated by this capture.')


def capture(dest=None, api=APIS['simple'], spec=None):
    if api not in APIS.values():
        raise ValueError('unsupported wiki API')
    spec = spec or json.loads((KIT / 'titles.json').read_text())
    titles = spec['fetched']
    if len(titles) < 2 or len(set(titles)) != len(titles) or set(titles) & set(spec['absent']):
        raise ValueError('title lists must be distinct, disjoint, and contain at least two fetched titles')
    dest = Path(dest) if dest else KIT / 'captures' / stamp()
    dest = dest.resolve()
    if dest.exists():
        raise FileExistsError('snapshot exists; use a new directory: ' + str(dest))
    raw, metadata = request(api, titles)
    predecessors = []
    paths = list(dest.parent.glob('*/manifest.json'))
    pointer_root = dest.parent.parent if dest.parent.name == 'captures' else dest.parent
    pointer = pointer_root / 'head.json'
    if pointer.exists():
        head = json.loads(pointer.read_text())
        candidate = (pointer_root / head['snapshot']).resolve()
        if pointer_root.resolve() not in candidate.parents:
            raise ValueError('head escapes wiki tree')
        path = candidate / 'manifest.json'
        if digest(path.read_bytes()) != head['manifest_sha256']:
            raise ValueError('head manifest pin mismatch')
        paths.append(path)
    for path in paths:
        try:
            old = json.loads(path.read_text())
            if (old.get('api') == api and old.get('labels', {}).get('fetched') == titles
                    and not stored_errors(path.parent, old)):
                predecessors.append((old['request']['retrieved_at'], str(path), path, old))
        except (OSError, KeyError, ValueError, TypeError):
            continue
    history = None
    if predecessors:
        _, _, path, old = max(predecessors, key=lambda entry: entry[:2])
        history = history_link(path.parent, old, metadata, 'fresh capture observation')
    return capture_response(dest, api, spec, raw, metadata, history)


def capture_response(dest, api, spec, raw, metadata, history=None):
    """Archive the response actually observed, without fetching replacement bytes."""
    dest = Path(dest).resolve()
    if dest.exists():
        raise FileExistsError('snapshot exists; use a new directory: ' + str(dest))
    titles = spec['fetched']
    live = pages(raw)
    for title in titles:
        p = live.get(title)
        if not p or not p.get('revisions'):
            raise ValueError('requested title has no complete source payload: ' + title)
        source_pin(p)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.wiki-capture-', dir=dest.parent) as temp:
        stage = Path(temp) / 'snapshot'; stage.mkdir()
        (stage / 'response.json').write_bytes(raw)
        records = []
        (stage / 'source').mkdir()
        (stage / 'source/renderer.py').write_bytes(Path(WR.__file__).read_bytes())
        when = metadata['retrieved_at']
        for i, title in enumerate(titles, 1):
            p = live[title]; rev = p['revisions'][0]
            pin = source_pin(p)
            source_path = f'source/wiki-{i:04d}.wiki'
            (stage / source_path).write_bytes(rev['slots']['main']['*'].encode('utf-8'))
            rec = L.write(stage / 'corpus', title=title, scope=title, when_to_use=title,
                          body=source_body(p, api), prefix='WIKI', doc_id=f'WIKI-{i:04d}',
                          origin='machine', source_authorship='unknown', external='no',
                          owner='unknown', when=when, note='captured source revision ' + str(rev['revid']))
            records.append({'id': rec.id, 'title': title, 'path': rec.path,
                            'pageid': p['pageid'], 'revid': rev['revid'],
                            'source_revision_at': rev.get('timestamp'),
                            'observed_at': when,
                            'source_url': api.split('/w/api.php')[0] + '/wiki/' +
                                urllib.parse.quote(title.replace(' ', '_')),
                            'revision_url': api.split('/w/api.php')[0] + '/wiki/' +
                                urllib.parse.quote(title.replace(' ', '_')) + '?oldid=' + str(rev['revid']),
                            'slot_sha1': pin['slot_sha1'],
                            'wikitext_sha256': pin['wikitext_sha256'],
                            'wikitext_path': source_path,
                            'rendered_sha256': digest(source_body(p, api).encode('utf-8')),
                            'served_page_sha256': digest((stage / 'corpus' / rec.path).read_bytes())})
        manifest = {'schema': 3, 'renderer': renderer_pin(), 'api': api, 'request': metadata,
                    'response_sha256': digest(raw), 'code': code_pins(), 'labels': spec,
                    'pages': records, 'local_profile': 'internal', 'external_expected': 'withheld',
                    'independence_verified': False,
                    'notice': 'External-source text, title-list labels; not blinded human evaluation.'}
        if history:
            manifest['history'] = history
            manifest['status'] = 'retained observation; not scored by capture'
            conflicts = []
            for p in records:
                old = history.get('previous_source_pins', {}).get(p['title'])
                observed = {key: p[key] for key in ('revid', 'slot_sha1', 'wikitext_sha256')}
                if old and old['revid'] == p['revid'] and old != observed:
                    conflicts.append({'title': p['title'], 'expected': old, 'observed': observed})
            if conflicts:
                manifest['same_revision_conflicts'] = conflicts
                manifest['status'] = 'archived revision conflict; not scored'
        (stage / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        if dest.exists():
            raise FileExistsError('snapshot appeared during capture')
        os.rename(stage, dest)
    return dest


def history_link(snapshot, manifest, metadata, reason):
    previous = str(snapshot.relative_to(ROOT)) if ROOT in snapshot.parents else str(snapshot)
    return {'reason': reason,
               'previous_capture': previous,
               'previous_manifest_sha256': digest((snapshot / 'manifest.json').read_bytes()),
               'previous_response_sha256': manifest['response_sha256'],
               'observed_at': metadata['retrieved_at'], 'source_api': manifest['api'],
               'previous_source_pins': {
                   p['title']: {key: p[key] for key in ('revid', 'slot_sha1', 'wikitext_sha256')}
                   for p in manifest['pages'] if 'wikitext_sha256' in p},
               'scored': False}


def archive_drift(snapshot, manifest, raw, metadata, changed):
    """Keep old evidence untouched and retain the new observation separately."""
    archive_root = (snapshot.parent.parent if snapshot.parent.name in {'captures', 'archives'}
                    else snapshot.parent) / 'archives'
    dest = archive_root / stamp()
    history = history_link(snapshot, manifest, metadata,
                           'revision-slot source differs; retained without scoring')
    history['changes'] = changed
    try:
        capture_response(dest, manifest['api'], manifest['labels'], raw, metadata, history)
    except ValueError as exc:
        # A deleted/missing title is still dated evidence, not a complete corpus.
        dest.mkdir(parents=True, exist_ok=False)
        (dest / 'response.json').write_bytes(raw)
        history['incomplete'] = str(exc)
        (dest / 'observation.json').write_text(json.dumps(history, indent=2) + '\n')
    return {'previous_capture': history['previous_capture'],
            'observed_archive': str(dest.relative_to(ROOT)) if ROOT in dest.parents else str(dest),
            'observed_at': metadata['retrieved_at'], 'scored': False}


def stored_errors(snapshot, manifest):
    errors = []
    if manifest.get('schema') != 3:
        return ['historical extract snapshot has no revision-slot pins; preserved, not scored by this checker']
    if manifest.get('api') not in APIS.values():
        return ['unsupported snapshot API']
    try:
        raw = (snapshot / 'response.json').read_bytes()
        if digest(raw) != manifest['response_sha256']:
            return ['stored raw response differs from capture pin']
        original = pages(raw)
        if manifest.get('renderer') != renderer_pin():
            return ['renderer version differs; source not evaluated; create a newly rendered capture']
        if digest((snapshot / 'source/renderer.py').read_bytes()) != manifest['renderer']['sha256']:
            return ['retained local renderer bytes differ from capture pin']
        spec = manifest['labels']; pinned = manifest['pages']
        if len(pinned) != len(spec['fetched']) or [p['title'] for p in pinned] != spec['fetched']:
            errors.append('page list differs from captured labels')
        if len(set(p['id'] for p in pinned)) != len(pinned):
            errors.append('duplicate manifest page ids')
        corpus = (snapshot / 'corpus').resolve()
        actual = {p.relative_to(corpus).as_posix() for p in corpus.rglob('*.html')}
        expected = {p['path'] for p in pinned}
        if actual != expected:
            errors.append('local HTML inventory differs from capture')
        for p in pinned:
            source = original[p['title']]
            pin = source_pin(source)
            if any(p.get(key) != value for key, value in pin.items()):
                errors.append(p['title'] + ': revision-slot pin missing or mismatched')
            source_path = (snapshot / p['wikitext_path']).resolve()
            if snapshot.resolve() not in source_path.parents:
                errors.append(p['title'] + ': wikitext path escapes snapshot')
            elif source_path.read_bytes() != source['revisions'][0]['slots']['main']['*'].encode('utf-8'):
                errors.append(p['title'] + ': retained wikitext differs from saved revision')
            if digest(source_body(source, manifest['api']).encode('utf-8')) != p.get('rendered_sha256'):
                errors.append(p['title'] + ': local derived text pin mismatched')
            if source['pageid'] != p['pageid'] or source['revisions'][0]['revid'] != p['revid']:
                errors.append(p['title'] + ': source identity mismatched')
            path = (corpus / p['path']).resolve()
            if corpus not in path.parents:
                errors.append(p['title'] + ': local page escapes snapshot'); continue
            if digest(path.read_bytes()) != p.get('served_page_sha256'):
                errors.append(p['title'] + ': complete served page differs from pin')
            # Bind local text to the saved API response, not two unrelated hashes.
            rec = L.Ledger(corpus).by_id.get(p['id'], [])
            if len(rec) != 1 or not rec[0].intact:
                errors.append(p['title'] + ': local record invalid'); continue
            rec = rec[0]
            from mplpb_combined.record import plain_to_html, text_of
            expected_text = text_of(plain_to_html(source_body(source, manifest['api'])))
            body_text = text_of(rec.body_html.split('</h1>', 1)[-1]).strip()
            if body_text != expected_text.strip():
                errors.append(p['title'] + ': local body is not the recorded source transformation')
            if rec.fields.get('source-authorship') != 'unknown' or rec.fields.get('external') != 'no':
                errors.append(p['title'] + ': source declaration or delivery policy differs from contract')
            if (rec.title != p['title'] or rec.scope != p['title'] or
                    rec.when_to_use != p['title'] or rec.origin != 'machine' or
                    rec.fields.get('owner') != 'unknown'):
                errors.append(p['title'] + ': local metadata differs from source transformation')
    except (OSError, KeyError, ValueError, TypeError) as exc:
        errors.append('stored provenance invalid: ' + str(exc))
    return errors


def smoke_rows(corpus, manifest):
    rows = []
    def add(question, mode, ok, outcome, source=None):
        rows.append({'question': question, 'mode': mode, 'passed': bool(ok),
                     'outcome': outcome, 'id': source})
    for p in manifest['pages']:
        a = R.answer(corpus, p['title'], R.PROFILES['internal'])
        add(p['title'], 'local title', a.kind == R.RETURN and a.record.id == p['id'], a.kind,
            a.record.id if a.record else None)
        a = R.answer(corpus, p['title'], R.PROFILES['external'])
        add(p['title'], 'external ask withheld', a.kind == R.NOT_IN_CORPUS, a.kind)
        g = G.gather(corpus, p['title'], R.PROFILES['external'])
        add(p['title'], 'external gate withheld', not g.sources, g.kind)
    for title in manifest['labels']['absent']:
        a = R.answer(corpus, title, R.PROFILES['internal'])
        add(title, 'absent title', a.kind == R.NOT_IN_CORPUS, a.kind)
    pair = ' '.join(p['title'] for p in manifest['pages'][:2])
    a = R.answer(corpus, pair, R.PROFILES['internal'])
    add(pair, 'two titles must not choose one', a.kind != R.RETURN, a.kind)
    return rows


def check(snapshot, live=True, report=None):
    snapshot = Path(snapshot).resolve()
    result = {'snapshot': str(snapshot.relative_to(ROOT)) if ROOT in snapshot.parents else str(snapshot),
              'checked_at': datetime.now(timezone.utc).isoformat(),
              'score_basis': 'local deterministic revision-lead rendering; not live API extract',
              'scored': False, 'independence_verified': False, 'errors': [], 'live': [], 'rows': []}
    live_raw = None
    try:
        manifest = json.loads((snapshot / 'manifest.json').read_text())
        result['errors'] = stored_errors(snapshot, manifest)
        if manifest.get('same_revision_conflicts'):
            result['errors'].append('capture conflicts with an already pinned revision; retained, not scored')
        if not result['errors']:
            result['errors'] += code_errors(manifest['code'])
        if not result['errors'] and live:
            live_raw, metadata = request(manifest['api'], [p['title'] for p in manifest['pages']])
            current = pages(live_raw); result['live_request'] = metadata
            for p in manifest['pages']:
                source = current.get(p['title'])
                observed = None
                invalid = None
                if source:
                    try:
                        observed = source_pin(source)
                    except (KeyError, ValueError, TypeError, IndexError) as exc:
                        invalid = str(exc)
                expected = {key: p[key] for key in ('revid', 'slot_sha1', 'wikitext_sha256')}
                matched = bool(source) and source.get('pageid') == p['pageid'] and observed == expected
                result['live'].append({
                    'title': p['title'], 'source_match': matched,
                    'expected': expected, 'observed': observed, 'invalid_source': invalid,
                    'same_revision_conflict': bool(source) and
                        source.get('revisions', [{}])[0].get('revid') == p['revid'] and not matched})
                # Generated API fields are diagnostics only, never source pins or scored text.
                saved = pages((snapshot / 'response.json').read_bytes())[p['title']]
                if source and saved.get('extract') != source.get('extract'):
                    result.setdefault('renderer_observations', []).append({
                        'title': p['title'], 'kind': 'API extract differs',
                        'source_match': matched, 'scored_text': 'local deterministic revision rendering'})
                if not matched:
                    result['errors'].append(p['title'] + ': revision-slot source changed or invalid; not scored')
            changed = [row for row in result['live'] if not row['source_match']]
            if changed:
                result['archive'] = archive_drift(snapshot, manifest, live_raw, metadata, changed)
        if not result['errors']:
            result['rows'] = smoke_rows(snapshot / 'corpus', manifest)
            result['scored'] = True
            result['failures'] = sum(not row['passed'] for row in result['rows'])
            result['paraphrases_unscored'] = [
                {'question': p['question'], 'outcome': R.answer(snapshot / 'corpus', p['question']).kind}
                for p in manifest['labels'].get('paraphrases', [])]
            if live and result['failures'] == 0:
                result['head'] = promote_head(snapshot, manifest, result['live_request'])
        result['verification'] = 'live' if live else 'offline replay only'
    except SourceUnavailable as exc:
        result['errors'].append(str(exc))
        result['source_failure'] = {'http_status': exc.status, 'retry_after': exc.retry_after}
        result['verification'] = 'live source unavailable'
    except Exception as exc:
        result['errors'].append('check failed: ' + str(exc))
    write_report(result, report, live_raw)
    return result


def write_report(result, report, live_raw=None):
    if report:
        report = Path(report); report.parent.mkdir(parents=True, exist_ok=True)
        with report.open('x', encoding='utf-8') as out:
            out.write(json.dumps(result, indent=2) + '\n')
        if live_raw is not None:
            with report.with_suffix('.live-response.json').open('xb') as out:
                out.write(live_raw)


def promote_head(snapshot, manifest, metadata):
    """Publish only a passing live observation; offline replay cannot move head."""
    root = snapshot.parent.parent if snapshot.parent.name in {'captures', 'archives'} else snapshot.parent
    pointer = root / 'head.json'
    previous = json.loads(pointer.read_text()) if pointer.exists() else None
    observed_at = metadata['retrieved_at']
    if (previous and previous['source_api'] == manifest['api'] and
            (previous['verified_at'] > observed_at or
             previous['captured_at'] > manifest['request']['retrieved_at'])):
        return {'promoted': False, 'reason': 'older observation', 'current': previous}
    head = {'snapshot': os.path.relpath(snapshot, root),
            'manifest_sha256': digest((snapshot / 'manifest.json').read_bytes()),
            'response_sha256': manifest['response_sha256'], 'source_api': manifest['api'],
            'captured_at': manifest['request']['retrieved_at'], 'verified_at': observed_at,
            'scored': True, 'failures': 0}
    with tempfile.NamedTemporaryFile(mode='w', prefix='.head-', dir=root, delete=False) as out:
        json.dump(head, out, indent=2); out.write('\n'); temp = Path(out.name)
    os.replace(temp, pointer)
    return {'promoted': True, 'current': head}


def sync(snapshot=None, report=None):
    """Verify current head, then verify one archived successor; never loop."""
    first_report = Path(report).with_suffix('.previous.json') if report else None
    previous = check(snapshot or latest(), live=True, report=first_report)
    if (previous.get('archive') and not any(
            row.get('same_revision_conflict') for row in previous['live'])):
        archive = Path(previous['archive']['observed_archive'])
        if not archive.is_absolute():
            archive = ROOT / archive
        result = check(archive, live=True, report=report)
        result['transition'] = {'previous_snapshot': previous['snapshot'],
                                'previous_scored': False, 'archive': previous['archive'],
                                'previous_report': str(first_report) if first_report else None}
        # The final report includes the transition; check already wrote its evidence.
        if report:
            transition = Path(report).with_suffix('.transition.json')
            with transition.open('x') as out:
                json.dump(result['transition'], out, indent=2); out.write('\n')
        return result
    write_report(previous, report)
    return previous


def run(dest=None, api=APIS['simple'], report=None):
    """Explicit fresh capture plus strict live check; never repin an older run."""
    try:
        snapshot = capture(dest, api)
    except SourceUnavailable as exc:
        result = {'scored': False, 'rows': [], 'live': [], 'errors': [str(exc)],
                  'checked_at': datetime.now(timezone.utc).isoformat(),
                  'independence_verified': False, 'verification': 'live source unavailable',
                  'source_failure': {'http_status': exc.status, 'retry_after': exc.retry_after}}
        write_report(result, report)
        return result
    return check(snapshot, live=True, report=report)


def latest():
    pointer = KIT / 'head.json'
    if pointer.exists():
        head = json.loads(pointer.read_text())
        candidate = (KIT / head['snapshot']).resolve()
        if KIT.resolve() not in candidate.parents:
            raise ValueError('head escapes wiki tree')
        if digest((candidate / 'manifest.json').read_bytes()) != head['manifest_sha256']:
            raise ValueError('head manifest pin mismatch')
        return candidate
    candidates = sorted((KIT / 'captures').glob('*/manifest.json'))
    if not candidates:
        raise ValueError('no complete new capture; run fetch first (historical snapshot remains incomplete)')
    return candidates[-1].parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['fetch', 'check', 'run', 'sync'])
    parser.add_argument('--snapshot', type=Path)
    parser.add_argument('--wiki', choices=APIS, default='simple')
    parser.add_argument('--offline', action='store_true', help='replay only; no claim of live verification')
    args = parser.parse_args()
    if args.offline and args.command != 'check':
        parser.error('--offline is only valid with check')
    try:
        if args.command == 'fetch':
            print('New immutable capture:', capture(args.snapshot, APIS[args.wiki])); return 0
        report = KIT / 'reports' / (args.command + '-' + stamp() + '.json')
        if args.command == 'run':
            result = run(args.snapshot, APIS[args.wiki], report=report)
        elif args.command == 'sync':
            result = sync(args.snapshot, report=report)
        else:
            result = check(args.snapshot or latest(), live=not args.offline, report=report)
        print(json.dumps(result, indent=2))
        return 2 if not result['scored'] else (1 if result['failures'] else 0)
    except (OSError, ValueError, SourceUnavailable) as exc:
        print(str(exc), file=sys.stderr); return 2


if __name__ == '__main__':
    raise SystemExit(main())
