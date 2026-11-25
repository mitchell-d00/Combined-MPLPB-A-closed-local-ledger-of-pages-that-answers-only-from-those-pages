"""Fail-closed Linux isolation for the execution worker, not the host custodian."""
import os
from pathlib import Path
try:
    import resource
except ImportError:
    resource=None
import shutil
import subprocess
import sys
import tempfile


def _limits():
    if resource is None:raise OSError('Linux resource limits are unavailable')
    resource.setrlimit(resource.RLIMIT_CPU,(300,300))
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    resource.setrlimit(resource.RLIMIT_FSIZE,(50*1024**2,50*1024**2))
    resource.setrlimit(resource.RLIMIT_NOFILE,(256,256))


def command(bwrap,code,inputs,outputs,program):
    args=[bwrap,'--unshare-all','--unshare-user','--disable-userns','--die-with-parent','--new-session',
          '--cap-drop','ALL','--clearenv']
    mounted=[]
    for value in ('/usr','/lib','/lib64','/bin',sys.base_prefix):
        path=Path(value)
        if path.exists() and not any(path==p or p in path.parents for p in mounted):
            args+=['--ro-bind',str(path),str(path)];mounted.append(path)
    args+=['--ro-bind',str(code),'/app','--ro-bind',str(inputs),'/study',
           '--bind',str(outputs),'/output','--size',str(256*1024**2),'--tmpfs','/scratch',
           '--proc','/proc','--dev','/dev','--chdir','/scratch',
           '--setenv','PATH','/usr/bin:/bin','--setenv','PYTHONPATH','/app',
           '--setenv','PYTHONNOUSERSITE','1','--setenv','TMPDIR','/scratch',
           str(Path(getattr(sys,'_base_executable',sys.executable)).resolve()),'-B','-c',program]
    return args


def invoke(args, *, transcript=None, wall_seconds=600):
    try:
        with tempfile.TemporaryFile() as out,tempfile.TemporaryFile() as err:
            result=None;timed_out=False
            try:
                result=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=out,stderr=err,
                                      timeout=wall_seconds,close_fds=True,preexec_fn=_limits)
            except subprocess.TimeoutExpired:
                timed_out=True
                raise
            finally:
                if transcript is not None:
                    import json
                    for name,stream in (('stdout.log',out),('stderr.log',err)):
                        stream.seek(0)
                        with (Path(transcript)/name).open('xb') as target:
                            shutil.copyfileobj(stream,target)
                    with (Path(transcript)/'process.json').open('x') as target:
                        json.dump({'returncode':result.returncode if result else None,
                                   'timed_out':timed_out,'wall_seconds_limit':wall_seconds},target)
    except (OSError,subprocess.SubprocessError) as exc:
        raise ValueError('Execution sandbox unavailable or exceeded its resource budget; no direct fallback') from exc
    if result.returncode:
        raise ValueError('Execution sandbox failed; no direct fallback or accepted output')
    return result


def execute_sandboxed(directory):
    from tools import historical_study as study
    if sys.platform!='linux' or not shutil.which('bwrap'):
        raise ValueError('Sandboxed execution requires Linux bubblewrap; no direct fallback')
    directory=Path(directory).resolve()
    study.pinned(directory)
    if any((directory/name).exists() for name in ('run.json','review-template.json','sandbox-receipt.json')):
        raise ValueError('Refusing to overwrite study output')
    with tempfile.TemporaryDirectory(prefix='mplpb-worker-sandbox-') as temporary:
        root=Path(temporary);code=root/'code';inputs=root/'inputs';outputs=root/'outputs'
        code.mkdir();inputs.mkdir();outputs.mkdir()
        for package in ('mplpb_answers','mplpb_combined','mplpb_work','tools'):
            (code/package).mkdir()
            paths=sorted((study.ROOT/package).glob('*.py')) if package!='tools' else [study.ROOT/'tools/historical_study.py',Path(__file__)]
            for path in paths:
                if path.is_symlink():raise ValueError('Symlinked code is not admitted to worker view')
                shutil.copyfile(path,code/package/path.name)
        for name in ('corpus.json','runtime-questions.json','seal.json'):
            shutil.copyfile(directory/name,inputs/name)
        # No private directory, source question file, gold salt, reviewer file,
        # host credential, home directory, repository metadata or host tmp is mounted.
        program="from tools.historical_study import execute; execute('/study','/output')"
        invoke(command(shutil.which('bwrap'),code,inputs,outputs,program))
        for name in ('run.json','review-template.json'):
            path=outputs/name
            if path.is_symlink() or not path.is_file():
                raise ValueError('Sandbox output must be a regular file, never a symlink')
        result=study.read(outputs/'run.json');template=study.read(outputs/'review-template.json')
        if result['seal_sha256']!=study.digest(study.read(directory/'seal.json')):
            raise ValueError('Sandbox output seal mismatch')
        study.pinned(directory)
        study.save(directory/'run.json',result);study.save(directory/'review-template.json',template)
        study.save(directory/'sandbox-receipt.json',{'schema':'execution-worker-sandbox-v1',
            'run_sha256':study.digest(result),'worker_exit_status':0,
            'mechanism':'Linux bubblewrap user/mount/PID/network/IPC/UTS namespaces; nested user namespaces disabled',
            'inputs_read_only':True,'network_namespace_isolated':True,'private_gold_mounted':False,
            'environment_cleared':True,'capabilities_dropped':True,
            'cpu_seconds_limit':300,'address_space_bytes_limit':2*1024**3,
            'wall_seconds_limit':600,'file_bytes_limit':50*1024**2,
            'scratch_tmpfs_bytes_limit':256*1024**2,
            'host_administrator_isolated':False,'independence_verified':False})
        return result
