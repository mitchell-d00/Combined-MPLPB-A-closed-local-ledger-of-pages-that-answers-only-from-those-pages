"""Replay the native worker from an allowlisted checkout without custody files."""
from pathlib import Path
import os
import sys

implementation, packet, work, counterexample = map(Path, sys.argv[1:5])
task = sys.argv[5]
if task not in {'bt-erratum', 'polybius-retained', 'polybius-added'}:
    raise SystemExit('Choose bt-erratum, polybius-retained, or polybius-added')
implementation, packet, work, counterexample = (
    path.resolve() for path in (implementation, packet, work, counterexample))
sys.path.insert(0, str(implementation))
sys.dont_write_bytecode = True
os.environ['TMPDIR'] = str(work)
read_roots = (implementation, packet, work, Path(sys.base_prefix).resolve())

def guard(event, args):
    if event in {'open', 'os.listdir', 'os.scandir'}:
        target = args[0]
        if not isinstance(target, (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(target)).resolve()
        write = event == 'open' and bool(args[2] & (
            os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC))
        roots = (work,) if write else read_roots
        if not any(path.is_relative_to(root) for root in roots):
            raise PermissionError('Read boundary excludes path: ' + str(path))
    if event == 'subprocess.Popen' and list(args[1]) != ['git', 'rev-parse', 'HEAD']:
        raise PermissionError('Only the revision readback subprocess is allowed')

sys.addaudithook(guard)
try:
    counterexample.read_bytes()
except PermissionError:
    print('Unlisted test file was blocked')
else:
    raise RuntimeError('Read boundary did not block the unlisted test path')
dummy = work / 'worker-receipt.json'
if task == 'bt-erratum':
    from tools.pole_authentic import run
    run(packet, dummy, implementation)
else:
    from tools.pole_remaining import polybius
    polybius(packet, dummy)
