"""Closed RPC surface. Host administration is never exposed on the seat API."""
from .errors import WorkError

SEAT_METHODS = {'snapshot', 'handoff', 'put', 'transfer', 'end', 'execute'}
HOST_METHODS = {'head', 'assign', 'revoke', 'reconcile', 'audit'}


def request(store, credential, data, host_operations=False):
    if not isinstance(data, dict) or not isinstance(data.get('op'), str):
        raise WorkError('Work request requires an operation')
    allowed = SEAT_METHODS | (HOST_METHODS if host_operations else set())
    if data['op'] not in allowed:
        raise WorkError('Unknown or unavailable work operation')
    kwargs = {k: v for k, v in data.items() if k != 'op'}
    try:
        return getattr(store, data['op'])(credential, **kwargs)
    except TypeError as exc:
        raise WorkError('Invalid work request fields') from exc
