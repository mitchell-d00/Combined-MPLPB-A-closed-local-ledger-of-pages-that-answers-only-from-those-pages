"""Host-only Cryptid v2 staging; existing fail-closed study_sandbox machinery."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from tools import study_sandbox

PACKAGES = ('mplpb_answers', 'mplpb_combined', 'mplpb_work')
WORKERS = ('tools/pole_worker.py', 'tools/cryptid_worker_v5.py')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root):
    result = {}
    for p in sorted(root.rglob('*')):
        if p.is_symlink():
            raise ValueError('Symlinks are not admitted')
        if p.is_file():
            result[str(p.relative_to(root))] = sha(p)
    return result


def runtime_files(root):
    return [p for name in PACKAGES for p in sorted((root / name).glob('*.py'))]


def execute(implementation, inputs, output):
    """A missing/failed isolator raises; never execute the reader on the host."""
    implementation, inputs, output = map(lambda p: Path(p).resolve(), (implementation, inputs, output))
    if not shutil.which('bwrap'):
        raise ValueError('Bubblewrap is required; no direct fallback')
    output.mkdir(parents=True, exist_ok=False)
    initial = snapshot(inputs)
    with tempfile.TemporaryDirectory(prefix='bubble-wrap-') as tmp:
        tmp = Path(tmp)
        code, public, result = (tmp / n for n in ('code', 'inputs', 'outputs'))
        for p in (code, public, result):
            p.mkdir()
        staged = {}
        native=runtime_files(implementation)
        for p in native + [Path(__file__).parent.parent / p for p in WORKERS]:
            if p.is_symlink():
                raise ValueError('Symlinked runtime is not admitted')
            relative = str(p.relative_to(implementation)) if p in native else 'tools/' + p.name
            destination = code / relative
            destination.parent.mkdir(exist_ok=True, parents=True)
            shutil.copyfile(p, destination)
            staged[relative] = sha(destination)
        case = json.loads((inputs / 'case.json').read_text())
        if case.get('adapter_mode') == 'documentary':
            allowed = {'case.json'}
        else:
            allowed = {'case.json'} | {s['path'] for s in case['sources']}
        if set(initial) != allowed:
            raise ValueError('Worker packet contains unexpected files')
        for relative in sorted(allowed):
            p = inputs / relative
            p.resolve().relative_to(inputs)
            destination = public / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, destination)
        assert snapshot(public) == initial
        program = 'from tools.cryptid_worker_v5 import execute; execute()'
        args = study_sandbox.command(shutil.which('bwrap'), code, public, result, program)
        receipt = {'mechanism': 'tools.study_sandbox.command/invoke; Linux bubblewrap',
                   'runtime': staged, 'inputs': initial,
                   'worker_receives_key': False, 'generator_or_scorer_staged': False,
                   'git_metadata_or_credentials_staged': False, 'network_namespace_isolated': True,
                   'host_administrator_isolated': False, 'independence_verified': False,
                   'semantic_outcome': 'NOT_RUN', 'execution_status': 'started'}
        try:
            study_sandbox.invoke(args, transcript=output, wall_seconds=45)
            path = result / 'result.json'
            if path.is_symlink() or not path.is_file() or set(snapshot(result)) != {'result.json'}:
                raise ValueError('Missing or nonregular worker output')
            assert snapshot(public) == initial == snapshot(inputs)
            raw = path.read_bytes()
            if len(raw) > 8 * 1024**2:
                raise ValueError('Oversized worker output')
            json.loads(raw)
            (output / 'result.json').write_bytes(raw)
            receipt.update(execution_status='completed', semantic_outcome='UNSCORED', result_sha256=sha(output / 'result.json'))
        except Exception as error:
            receipt.update(execution_status='BLOCKED', error=str(error))
            raise
        finally:
            with (output / 'execution.json').open('x') as stream:
                json.dump(receipt, stream, indent=2)
    return json.loads((output / 'result.json').read_text())
