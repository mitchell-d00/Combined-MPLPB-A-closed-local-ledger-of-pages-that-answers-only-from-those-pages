"""Run a sealed operator packet from the native archive in the study sandbox."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tarfile
from tempfile import TemporaryDirectory

from tools.study_sandbox import command, invoke


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


archive, corpus, operator, runner, output, receipt = map(Path, sys.argv[1:])
assert not output.exists()
receipt.mkdir(mode=0o700)
with TemporaryDirectory(prefix='ariadne-worker-') as tmp:
    root = Path(tmp)
    code, inputs, outputs = (root/name for name in ('code', 'input', 'output'))
    for directory in (code, inputs, outputs):
        directory.mkdir()
    with tarfile.open(archive) as bundle:
        bundle.extractall(code, filter='data')
    shutil.copyfile(runner, code/'runner.py')
    shutil.copyfile(corpus, inputs/'corpus.json')
    shutil.copyfile(operator, inputs/'operator.json')
    program = (
        "from pathlib import Path; import sys, runpy;"
        "assert not Path('/workspace').exists();"
        "assert sorted(p.name for p in Path('/study').iterdir()) == ['corpus.json','operator.json'];"
        "assert not Path('/study').stat().st_mode & 0o002;"
        "sys.argv=['/app/runner.py','/study/corpus.json','/study/operator.json','/output/native.json'];"
        "runpy.run_path('/app/runner.py',run_name='__main__')"
    )
    invoke(command(shutil.which('bwrap'), code, inputs, outputs, program), transcript=receipt)
    worker_output = outputs/'native.json'
    assert worker_output.is_file() and not worker_output.is_symlink()
    captured = json.loads(worker_output.read_bytes())
    assert captured['input_sha256'] == digest(operator)
    with output.open('xb') as target:
        target.write(worker_output.read_bytes())
(receipt/'receipt.json').write_text(json.dumps({
    'mechanism':'repository Linux Bubblewrap study sandbox',
    'os_isolated':True, 'host_admin_isolated':False, 'network_namespace_isolated':True,
    'workspace_mounted':False, 'private_evaluator_material_mounted':False,
    'worker_inputs_read_only':True, 'worker_status':0,
    'archive_sha256':digest(archive), 'corpus_sha256':digest(corpus),
    'operator_sha256':digest(operator), 'native_output_sha256':digest(output),
}, indent=2)+'\n')
