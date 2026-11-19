"""POSIX staged ledger generations with one atomic publication pointer.

Native readers use STORE/current unchanged. Generations are immutable through
this API and hash checked; trusted filesystem owners can still alter files.
Process interruption tests are not physical power-loss certification.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import uuid
import time
from contextlib import contextmanager

from mplpb_answers.evidence_contract import canonical, loads
from mplpb_combined.ledger import LOG_DIR, LOCK_NAME
from . import classing

STEPS=('staged','synced','generation_installed','pointer_prepared','pointer_replaced','store_synced')


def _checkpoint(name):
    """Fault-injection seam for subprocess tests; no environment-controlled exit."""


def _digest(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def _sync_directory(path):
    fd=os.open(str(path),os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)


def _store(path):
    if os.name!='posix' or not hasattr(os,'O_DIRECTORY'):
        raise ValueError('Generation publication requires POSIX symlinks, rename and directory fsync')
    root=Path(path).absolute()
    if root.is_symlink():raise ValueError('Store root must not be a symlink')
    if not root.parent.is_dir():raise ValueError('Create the store parent directory first')
    root.mkdir(mode=0o700,exist_ok=True)
    if any(root.glob('*.html')):raise ValueError('Use a separate generation store, not an existing ledger root')
    directory=root/'generations'
    if directory.is_symlink():raise ValueError('Generation directory must not be a symlink')
    directory.mkdir(exist_ok=True)
    _sync_directory(root);_sync_directory(root.parent)
    return root


@contextmanager
def _lock(root):
    """POSIX advisory lock released by the OS if its writer terminates."""
    import fcntl
    fd=os.open(str(root/'.generation-lock'),os.O_CREAT|os.O_RDWR|getattr(os,'O_NOFOLLOW',0),0o600)
    deadline=time.monotonic()+5
    try:
        while True:
            try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);break
            except BlockingIOError:
                if time.monotonic()>=deadline:raise ValueError('Generation store is busy')
                time.sleep(0.05)
        yield
    finally:
        os.close(fd)


def _manifest(ledger,parent,receipt):
    files=classing._files(ledger)
    return {'schema':'mplpb-ledger-generation-v1','parent':parent,
            'ledger_files':{p.as_posix():hashlib.sha256(raw).hexdigest() for p,raw in files.items()},
            'receipt':receipt,'answer_supported':False,'historical_truth_independently_verified':False}


def validate_generation(store,ident):
    if not isinstance(ident,str) or len(ident)!=64 or any(c not in '0123456789abcdef' for c in ident):
        raise ValueError('Invalid generation ID')
    root=Path(store).absolute();generation=root/'generations'/ident
    if any(p.is_symlink() for p in (root,generation,root/'generations',generation/'ledger',generation/'manifest.json')):
        raise ValueError('Symlinked generation')
    with (generation/'manifest.json').open('rb') as stream:raw=stream.read(2*1024*1024+1)
    if len(raw)>2*1024*1024:raise ValueError('Generation manifest exceeds budget')
    manifest=loads(raw.decode('utf-8'))
    if (manifest.get('schema')!='mplpb-ledger-generation-v1' or _digest(manifest)!=ident
        or manifest.get('answer_supported') is not False or manifest.get('historical_truth_independently_verified') is not False):
        raise ValueError('Generation manifest changed')
    actual={p.as_posix():hashlib.sha256(raw).hexdigest() for p,raw in classing._files(generation/'ledger').items()}
    if actual!=manifest['ledger_files']:raise ValueError('Generation bytes changed')
    errors,_=classing._validate(generation/'ledger')
    if errors:raise ValueError('Generation fails native ledger validation')
    return generation/'ledger',manifest


def current(store):
    root=Path(store).absolute();pointer=root/'current'
    if not pointer.is_symlink():raise ValueError('No committed current-generation pointer')
    relative=Path(os.readlink(pointer))
    if relative.is_absolute() or len(relative.parts)!=3 or relative.parts[0]!='generations' or relative.parts[2]!='ledger':
        raise ValueError('Current pointer escapes generation layout')
    ledger,manifest=validate_generation(root,relative.parts[1])
    return relative.parts[1],ledger,manifest


def _switch(root,ident):
    validate_generation(root,ident)
    temporary=root/('.current-'+uuid.uuid4().hex)
    try:
        os.symlink('generations/'+ident+'/ledger',temporary)
        _checkpoint('pointer_prepared')
        os.replace(temporary,root/'current')
        _checkpoint('pointer_replaced')
        _sync_directory(root)
        _checkpoint('store_synced')
    finally:
        temporary.unlink(missing_ok=True)


def _publish(root,stage,parent,receipt):
    errors,_=classing._validate(stage/'ledger')
    if errors:raise ValueError('Staged generation fails native validation')
    _checkpoint('staged')
    manifest=_manifest(stage/'ledger',parent,receipt);ident=_digest(manifest)
    (stage/'manifest.json').write_text(canonical(manifest)+'\n',encoding='utf-8')
    for path in stage.rglob('*'):
        if path.is_file():
            with path.open('rb') as stream:os.fsync(stream.fileno())
    for path in sorted((p for p in stage.rglob('*') if p.is_dir()),key=lambda p:len(p.parts),reverse=True):
        _sync_directory(path)
    _sync_directory(stage);_checkpoint('synced')
    destination=root/'generations'/ident
    if destination.exists():validate_generation(root,ident)
    else:os.replace(stage,destination)
    _sync_directory(root/'generations');_checkpoint('generation_installed')
    _switch(root,ident)
    return {'schema':'mplpb-generation-publication-v1','generation':ident,'parent':parent,
            'reader_path':str(root/'current'),'answer_supported':False,
            'historical_truth_independently_verified':False,'receipt':receipt}


def initialize(ledger,store):
    """Copy an intact existing ledger; original bytes are never changed."""
    source=Path(ledger).resolve();root=_store(store)
    if root==source or root in source.parents or source in root.parents:raise ValueError('Store and source must be disjoint')
    with _lock(root):
        if (root/'current').exists() or (root/'current').is_symlink():raise ValueError('Store already has a current pointer')
        before=classing._files(source)
        with tempfile.TemporaryDirectory(dir=root,prefix='.staging-') as temporary:
            stage=Path(temporary)/'generation'
            shutil.copytree(source,stage/'ledger',ignore=lambda directory,names:[LOCK_NAME] if Path(directory)==source/LOG_DIR else [])
            if classing._files(stage/'ledger')!=before or classing._files(source)!=before:
                raise ValueError('Original ledger changed during staging')
            return _publish(root,stage,None,{'operation':'initialize_existing_ledger','answer_supported':False})


def build(review,dump,store,*,ratify_by=None,reviewed_by=None):
    root=_store(store)
    if root==Path(dump).resolve() or root in Path(dump).resolve().parents or Path(dump).resolve() in root.parents:
        raise ValueError('Store and dump must be disjoint')
    with _lock(root):
        parent=None;old=None
        if (root/'current').is_symlink() or (root/'current').exists():parent,old,_=current(root)
        with tempfile.TemporaryDirectory(dir=root,prefix='.staging-') as temporary:
            stage=Path(temporary)/'generation';stage.mkdir()
            if old:shutil.copytree(old,stage/'ledger')
            receipt=classing.build(review,dump,stage/'ledger',append=bool(old),
                                   ratify_by=ratify_by,reviewed_by=reviewed_by)
            receipt=dict(receipt,ledger='current')  # Do not persist a temporary path as a source identity.
            if parent and current(root)[0]!=parent:raise ValueError('Current generation changed during staging')
            if classing.sorter_v2.sort_directory(dump,'compare')['graph_sha256']!=review['sorter']['graph_sha256']:
                raise ValueError('Dump changed before generation publication')
            return _publish(root,stage,parent,receipt)


def inspect(store,max_generations=32):
    """Read-only recovery inspection. Never infer that an orphan is committed."""
    from itertools import islice
    if type(max_generations) is not int or not 1<=max_generations<=64:raise ValueError('Invalid inspection budget')
    root=Path(store).absolute();active=None;error=None
    try:active=current(root)[0]
    except (ValueError,OSError) as exc:error=str(exc)
    directory=root/'generations';paths=list(islice(directory.iterdir(),max_generations+1)) if directory.is_dir() else []
    rows=[]
    for path in sorted(paths[:max_generations]):
        try:validate_generation(root,path.name);state='committed_current' if path.name==active else 'complete_unselected'
        except (ValueError,OSError):state='invalid'
        rows.append({'generation':path.name,'state':state})
    return {'current':active,'current_error':error,'generations':rows,'inspection_truncated':len(paths)>max_generations,
            'automatic_recovery_performed':False,'answer_supported':False}


def recover(store,generation):
    """Explicit operator selection, preserving every complete prior generation."""
    root=_store(store)
    with _lock(root):
        _switch(root,generation)
    return inspect(root)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    init=sub.add_parser('init');init.add_argument('ledger');init.add_argument('--store',required=True)
    writer=sub.add_parser('build');writer.add_argument('review');writer.add_argument('--dump',required=True)
    writer.add_argument('--store',required=True);writer.add_argument('--ratify-by');writer.add_argument('--reviewed-by')
    probe=sub.add_parser('inspect');probe.add_argument('--store',required=True)
    recovery=sub.add_parser('recover');recovery.add_argument('--store',required=True);recovery.add_argument('--select',required=True)
    a=p.parse_args(argv)
    try:
        if a.command=='init':result=initialize(a.ledger,a.store)
        elif a.command=='build':result=build(classing._load_review(a.review),a.dump,a.store,ratify_by=a.ratify_by,reviewed_by=a.reviewed_by)
        elif a.command=='inspect':result=inspect(a.store)
        else:result=recover(a.store,a.select)
        print(json.dumps(result,indent=2));return 0
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print(json.dumps({'error':str(exc),'answer_supported':False}));return 2


if __name__=='__main__':raise SystemExit(main())
