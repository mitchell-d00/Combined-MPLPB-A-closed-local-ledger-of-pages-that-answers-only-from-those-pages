"""Clean full ZIP materialization with internal content deduplication only.

Every byte is read from the frozen archive, never a checkout. Identical regular
members share an inode inside the new extraction to fit this host's disk. Final
manifest validation detects any subsequent source mutation.
"""
import argparse,hashlib,json,os,tempfile,zipfile
from pathlib import Path

def extract(archive,target,receipt):
    assert not target.exists() and not receipt.exists();target.mkdir(parents=True);known={};names=set();logical=physical=members=0
    with zipfile.ZipFile(archive) as z:
        for item in z.infolist():
            p=Path(item.filename);mode=item.external_attr>>16
            if p.is_absolute() or '..' in p.parts or str(p) in names or mode&0o170000==0o120000:raise ValueError('Unsafe or duplicate ZIP member')
            names.add(str(p));out=target/p
            if item.is_dir():out.mkdir(parents=True,exist_ok=True);continue
            out.parent.mkdir(parents=True,exist_ok=True);hasher=hashlib.sha256();size=0
            with tempfile.NamedTemporaryFile(dir=out.parent,delete=False) as f:
                temporary=Path(f.name)
                with z.open(item) as src:
                    for chunk in iter(lambda:src.read(1024*1024),b''):f.write(chunk);hasher.update(chunk);size+=len(chunk)
            assert size==item.file_size
            signature=(hasher.hexdigest(),mode&0o777)
            if signature in known:temporary.unlink();os.link(known[signature],out)
            else:temporary.rename(out);os.chmod(out,mode&0o777 or 0o644);known[signature]=out;physical+=size
            logical+=size;members+=1
    record={'schema':'cryptid-clean-zip-extraction-v1','zip_sha256':hashlib.file_digest(archive.open('rb'),'sha256').hexdigest(),'members':members,'logical_bytes':logical,'distinct_content_bytes':physical,'deduplicated_bytes':logical-physical,'extraction':str(target),'method':'All member payloads streamed from ZIP with CRC checks; identical files hardlinked only within fresh extraction, no checkout links; source hashes must be rechecked after tests.'}
    with receipt.open('x') as f:json.dump(record,f,indent=2)
    print(json.dumps(record))
if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ['archive','target','receipt']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();extract(a.archive,a.target,a.receipt)
