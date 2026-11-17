"""Bounded local artifact byte inspection, never delivery or historical truth."""
import hashlib
import os
from pathlib import PurePosixPath
import re
import stat
from .errors import WorkError

MAX_ARTIFACT_BYTES = 8 * 1024 * 1024


def inspect(directory, relative_path, expected_sha256):
    """Read only regular files beneath work/artifacts without following links."""
    if (not isinstance(relative_path, str) or len(relative_path)>1000
            or not relative_path or '\\' in relative_path
            or any(p in {'', '.', '..'} for p in relative_path.split('/'))
            or PurePosixPath(relative_path).is_absolute()):
        raise WorkError('Artifact must be a bounded relative path beneath work/artifacts')
    if not isinstance(expected_sha256, str) or not re.fullmatch(r'[0-9a-f]{64}', expected_sha256):
        raise WorkError('Artifact requires an exact raw SHA-256 pin')
    if not hasattr(os, 'O_NOFOLLOW') or os.open not in os.supports_dir_fd:
        raise WorkError('Local artifact inspection requires native no-follow filesystem support')
    fd = file_fd = None
    try:
        fd = os.open(directory/'artifacts', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        parts = relative_path.split('/')
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd);fd = child
        file_fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        before = os.fstat(file_fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size>MAX_ARTIFACT_BYTES:
            raise WorkError('Artifact must be a regular file of at most 8 MiB')
        size = 0; digest = hashlib.sha256()
        while True:
            chunk = os.read(file_fd, min(65536, MAX_ARTIFACT_BYTES+1-size))
            if not chunk:break
            size += len(chunk)
            if size>MAX_ARTIFACT_BYTES:raise WorkError('Artifact exceeded read budget')
            digest.update(chunk)
        after = os.fstat(file_fd)
        pins = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        if pins(before)!=pins(after) or size!=after.st_size:
            raise WorkError('Artifact changed during inspection')
        actual = digest.hexdigest()
        return {'relative_path':relative_path, 'raw_sha256':actual, 'bytes':size,
                'matches_expected':actual==expected_sha256,
                'basis':'bounded_local_file_read', 'observed_identity':'bytes_at_inspection_time',
                'delivery_verified':False, 'read_by_person_verified':False,
                'completion_verified':False, 'content_truth_verified':False}
    except OSError as exc:
        raise WorkError('Artifact is unavailable or unsafe to inspect') from exc
    finally:
        if file_fd is not None:os.close(file_fd)
        if fd is not None:os.close(fd)
