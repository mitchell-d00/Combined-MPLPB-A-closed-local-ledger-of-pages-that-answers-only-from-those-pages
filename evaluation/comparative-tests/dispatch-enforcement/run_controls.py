"""Measure fixture execution through the supported MPLPB work entry points."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing, contextmanager
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import threading
import time

PIN = '6ba371ca07dd9269f28af762ed1971ad484fb6b5'
BOUNDARIES = ('python', 'seat_rpc', 'loopback_http')
SCENARIOS = ('authorized', 'source_changed', 'revoked', 'tool_not_granted',
             'operation_not_granted', 'stale_revision', 'missing_capability', 'duplicate_requests',
             'source_changed_after_reservation')


def events(path):
    with closing(sqlite3.connect(path)) as db:
        return [json.loads(row[0])['type'] for row in db.execute('SELECT body FROM events ORDER BY seq')]


@contextmanager
def transport(boundary, fixture):
    from mplpb_work import WorkError
    from mplpb_work.api import request

    if boundary != 'loopback_http':
        def local(token, body):
            try:
                if boundary == 'python':
                    result = fixture.store.execute(token, **{k: v for k, v in body.items() if k != 'op'})
                else:
                    result = request(fixture.store, token, body)
                return {'receipt': result['receipt']['status']}
            except WorkError as error:
                return {'rejection': type(error).__name__}
        yield local
        return

    from tools.ledger_ui import App, handler
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler(App(
        topic_base=fixture.base / 'topics', work_store=fixture.store)))
    worker = threading.Thread(target=server.serve_forever, kwargs={'poll_interval': 0.02}, daemon=True)
    worker.start()

    def post(token, body):
        connection = HTTPConnection('127.0.0.1', server.server_port, timeout=5)
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        try:
            connection.request('POST', '/api/work', body=json.dumps(body), headers=headers)
            response = connection.getresponse()
            message = json.loads(response.read())
            if response.status == 200:
                return {'receipt': message['receipt']['status'], 'http_status': 200}
            return {'rejection': 'http', 'http_status': response.status}
        finally:
            connection.close()
    try:
        yield post
    finally:
        server.shutdown()
        worker.join(timeout=5)
        server.server_close()


def fixture_for():
    from tests.test_specialist_continuity import ContinuityTests
    fixture = ContinuityTests()
    try:
        fixture.setUp()
        fixture.prepare()
    except Exception:
        fixture.doCleanups()
        raise
    return fixture


def measure(boundary, scenario):
    fixture = fixture_for()
    try:
        marker = fixture.base / 'effect.txt'
        database = fixture.base / 'work' / 'work.sqlite3'
        def local_effect(request):
            with marker.open('a', encoding='utf-8') as stream:
                stream.write(request['idempotency_key'] + '\n')
            return fixture.adapter(request)
        fixture.store.executors['fixture.run.v1'] = local_effect
        if scenario == 'tool_not_granted':
            fixture.assign('builder', 'builder-2', tools=[], predecessor='builder-1')
        if scenario == 'operation_not_granted':
            fixture.assign('builder', 'builder-2', operations=[], predecessor='builder-1')

        token = fixture.tokens['builder']
        def change_source():
            source = fixture.corpus / fixture.source.path
            source.write_text(source.read_text().replace('is discontinued', 'is available', 1))
        if scenario == 'source_changed':
            change_source()
        if scenario == 'revoked':
            fixture.store.revoke(fixture.host, 'builder', fixture.store.head(fixture.host)['hash'])
            head = fixture.store.head(fixture.host)['hash']
        else:
            head = fixture.store.snapshot(token)['head']
        body = {'op': 'execute', 'id': 'A1', 'expected_revision': 2 if scenario == 'stale_revision' else 1,
                'expected_head': head}
        if scenario == 'missing_capability':
            token = ''

        before = events(database)
        if scenario == 'source_changed_after_reservation':
            # Fault injection after the durable reservation, before the second check.
            transaction = fixture.store._transaction
            changed = False
            @contextmanager
            def change_after_reservation():
                nonlocal changed
                with transaction() as state:
                    yield state
                if not changed and events(database)[len(before):] == ['start']:
                    change_source()
                    changed = True
            fixture.store._transaction = change_after_reservation
        with transport(boundary, fixture) as call:
            if scenario == 'duplicate_requests':
                barrier = threading.Barrier(2, timeout=5)
                def submit():
                    barrier.wait()
                    return call(token, body)
                with ThreadPoolExecutor(max_workers=2) as pool:
                    pending = [pool.submit(submit) for _ in range(2)]
                    responses = [f.result(timeout=10) for f in pending]
            else:
                responses = [call(token, body)]
        after = events(database)
        effect_count = len(marker.read_text().splitlines()) if marker.exists() else 0
        added = after[len(before):]
        successful = sum(row.get('receipt') == 'passed' for row in responses)
        rejected = sum('rejection' in row and row.get('http_status', 400) in {400, 401, 403, 409}
                       for row in responses)
        expected = int(scenario in {'authorized', 'duplicate_requests'})
        passed = (after[:len(before)] == before and successful == effect_count == len(fixture.calls) == expected
                  and rejected == len(responses) - expected
                  and added == (['start', 'finish'] if expected else []))
        if scenario == 'source_changed_after_reservation':
            passed = (changed and after[:len(before)] == before and effect_count == len(fixture.calls) == 0
                      and added == ['start', 'finish'] and responses[0].get('receipt') == 'indeterminate')
        return {'boundary': boundary, 'scenario': scenario, 'responses': responses,
                'effects': effect_count, 'adapter_calls': len(fixture.calls), 'events_added': added,
                'passed': passed}
    finally:
        fixture.doCleanups()


def cli_default(repo):
    from mplpb_work.model import OPERATIONS
    from mplpb_work.store import digest
    fixture = fixture_for()
    try:
        fixture.now[0] = time.time()
        result = fixture.store.assign(fixture.host, seat='builder', instance='builder-cli',
            model={'name':'fixture','provider':'fixture','version':'1','context_policy_hash':digest({'policy':'fixture'})},
            contract={'operations': sorted(OPERATIONS), 'tools':['fixture.run.v1'], 'scopes':['T1'],
                      'share_with':fixture.roles, 'profile':'internal', 'expires_at':fixture.now[0]+300},
            continues_work_of='builder-1', expected_head=fixture.store.head(fixture.host)['hash'])
        token = result['credential']
        token_file = fixture.base / 'capability.json'
        token_file.touch(mode=0o600, exist_ok=False)
        token_file.write_text(json.dumps(token))
        command = [sys.executable, '-B', '-m', 'mplpb_work', 'request',
                   str(fixture.base/'work'), '--credential-file', str(token_file)]
        def call(body):
            return subprocess.run(command, cwd=repo, input=json.dumps(body), text=True,
                                  capture_output=True, timeout=15)

        snapshot = call({'op': 'snapshot'})
        snapshot.check_returncode()
        view = json.loads(snapshot.stdout)
        permission = next(row['permission'] for row in view['records'] if row['id'] == 'A1')
        body = {'op':'execute','id':'A1','expected_revision':1, 'expected_head':view['head']}
        database = fixture.base/'work'/'work.sqlite3'
        before = events(database)
        process = call(body)
        after = events(database)
        error = json.loads(process.stderr) if process.stderr else {}
        return {'boundary': 'stock_cli', 'scenario': 'no_adapter_registered', 'exit_code': process.returncode,
                'permission': permission, 'events_added': after[len(before):],
                'passed': permission == 'blocked' and process.returncode == 2 and error.get('operation_completed') is False
                and error.get('error') == 'Action is not currently permissible' and before == after}
    finally:
        fixture.doCleanups()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checkout', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    repo = args.checkout.resolve()
    revision = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
    if revision != PIN or subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain'], text=True):
        parser.error(f'Use a clean checkout at {PIN}')
    sys.path.insert(0, str(repo))
    cases = [measure(boundary, scenario) for boundary in BOUNDARIES for scenario in SCENARIOS]
    cases.append(cli_default(repo))
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump({'revision': revision, 'python': sys.version.split()[0], 'cases': cases}, stream, indent=2)
        stream.write('\n')
    count = sum(row['passed'] for row in cases)
    print(f'{count}/{len(cases)} controls passed')
    return int(count != len(cases))


if __name__ == '__main__':
    raise SystemExit(main())
