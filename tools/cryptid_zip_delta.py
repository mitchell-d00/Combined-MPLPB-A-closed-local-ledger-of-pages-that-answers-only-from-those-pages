"""Losslessly retain a full committed ZIP using an unchanged base ZIP.

This storage encoding is not a smaller source distribution: reconstruction
produces the exact original full ZIP, verified by its frozen SHA-256. Source
archives, packets, keys and scores are never rewritten. Only byte-identical
compressed member payloads may be copied from the explicitly hashed base.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import zipfile

MAGIC = b'MPLPB-ZIP-DELTA-1\n'
CHUNK = 1024 * 1024


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').digest()


def read_exact(stream, length):
    value = stream.read(length)
    if len(value) != length:
        raise ValueError('Truncated ZIP storage encoding')
    return value


def payload_offset(stream, info):
    stream.seek(info.header_offset)
    header = read_exact(stream, 30)
    if header[:4] != b'PK\x03\x04':
        raise ValueError('Invalid ZIP local header')
    name, extra = struct.unpack('<HH', header[26:30])
    return info.header_offset + 30 + name + extra


def range_sha(stream, start, length):
    stream.seek(start)
    digest = hashlib.sha256()
    while length:
        data = read_exact(stream, min(CHUNK, length))
        digest.update(data)
        length -= len(data)
    return digest.digest()


def encode(base, target, output):
    base, target, output = map(Path, (base, target, output))
    if output.exists():
        raise FileExistsError(output)
    base_hash, target_hash = sha(base), sha(target)
    copied = literal = operations = 0
    with zipfile.ZipFile(base) as old_zip, zipfile.ZipFile(target) as new_zip:
        old_members = {item.filename: item for item in old_zip.infolist()}
        members = sorted(new_zip.infolist(), key=lambda item: item.header_offset)
        with base.open('rb') as old, target.open('rb') as new, output.open('xb') as raw:
            with gzip.GzipFile(filename='', mode='wb', fileobj=raw, compresslevel=9, mtime=0) as encoded:
                encoded.write(MAGIC + base_hash + target_hash + struct.pack('<Q', target.stat().st_size))

                def literals(start, length):
                    nonlocal literal, operations
                    new.seek(start)
                    while length:
                        data = read_exact(new, min(CHUNK, length))
                        encoded.write(b'L' + struct.pack('<Q', len(data)) + data)
                        literal += len(data)
                        operations += 1
                        length -= len(data)

                cursor = 0
                for item in members:
                    start = payload_offset(new, item)
                    if start < cursor:
                        raise ValueError('Overlapping ZIP members')
                    literals(cursor, start - cursor)
                    prior = old_members.get(item.filename)
                    reusable = bool(prior and item.compress_size and
                                    (prior.compress_type, prior.compress_size, prior.file_size, prior.CRC) ==
                                    (item.compress_type, item.compress_size, item.file_size, item.CRC))
                    if reusable:
                        old_start = payload_offset(old, prior)
                        reusable = range_sha(old, old_start, item.compress_size) == range_sha(new, start, item.compress_size)
                    if reusable:
                        encoded.write(b'C' + struct.pack('<QQ', old_start, item.compress_size))
                        copied += item.compress_size
                        operations += 1
                    else:
                        literals(start, item.compress_size)
                    cursor = start + item.compress_size
                literals(cursor, target.stat().st_size - cursor)
                encoded.write(b'E')
    result = {'schema': 'mplpb-lossless-source-zip-storage-v1', 'base_zip': str(base),
              'base_sha256': base_hash.hex(), 'full_target_zip_sha256': target_hash.hex(),
              'full_target_zip_bytes': target.stat().st_size, 'delta': str(output),
              'delta_sha256': sha(output).hex(), 'delta_bytes': output.stat().st_size,
              'copied_byte_identical_payload_bytes': copied, 'literal_bytes': literal,
              'operations': operations, 'meaning': 'Full source ZIP retained losslessly as unchanged base plus delta; not a scoped or partial source archive.'}
    verify(base, output)
    result['reconstructed_full_zip_hash_verified'] = True
    return result


def decode(base, delta, destination=None):
    base, delta = map(Path, (base, delta))
    digest = hashlib.sha256()
    written = operations = 0
    with gzip.open(delta, 'rb') as encoded, base.open('rb') as old:
        if read_exact(encoded, len(MAGIC)) != MAGIC:
            raise ValueError('Unknown source ZIP storage format')
        base_hash, target_hash = read_exact(encoded, 32), read_exact(encoded, 32)
        expected_size = struct.unpack('<Q', read_exact(encoded, 8))[0]
        if sha(base) != base_hash or expected_size > 8 * 1024**3:
            raise ValueError('Wrong base ZIP or invalid target bound')
        while True:
            kind = read_exact(encoded, 1)
            if kind == b'E':
                break
            operations += 1
            if operations > 2000000:
                raise ValueError('Operation bound exceeded')
            if kind == b'L':
                length = struct.unpack('<Q', read_exact(encoded, 8))[0]
                source = encoded
            elif kind == b'C':
                offset, length = struct.unpack('<QQ', read_exact(encoded, 16))
                if offset + length > base.stat().st_size:
                    raise ValueError('Copy outside base ZIP')
                old.seek(offset)
                source = old
            else:
                raise ValueError('Unknown source ZIP storage operation')
            if written + length > expected_size:
                raise ValueError('Output exceeds frozen target size')
            while length:
                data = read_exact(source, min(CHUNK, length))
                digest.update(data)
                if destination is not None:
                    destination.write(data)
                written += len(data)
                length -= len(data)
        if encoded.read(1) or written != expected_size or digest.digest() != target_hash:
            raise ValueError('Reconstructed source ZIP hash or length mismatch')
    return {'status': 'PASS', 'full_zip_sha256': target_hash.hex(), 'full_zip_bytes': written,
            'base_sha256': base_hash.hex(), 'operations': operations}


def verify(base, delta):
    return decode(base, delta)


def restore(base, delta, output):
    output = Path(output)
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=output.parent, prefix='.source-zip-', delete=False) as stream:
        temporary = Path(stream.name)
        try:
            result = decode(base, delta, stream)
        except BaseException:
            temporary.unlink()
            raise
    temporary.rename(output)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['encode', 'verify', 'restore'])
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--delta', type=Path, required=True)
    parser.add_argument('--target', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    if args.command == 'encode':
        if not args.target:
            parser.error('encode requires --target')
        result = encode(args.base, args.target, args.delta)
    elif args.command == 'restore':
        if not args.output:
            parser.error('restore requires --output')
        result = restore(args.base, args.delta, args.output)
    else:
        result = verify(args.base, args.delta)
    if args.receipt:
        with args.receipt.open('x') as stream:
            json.dump(result, stream, indent=2)
    print(json.dumps(result))
