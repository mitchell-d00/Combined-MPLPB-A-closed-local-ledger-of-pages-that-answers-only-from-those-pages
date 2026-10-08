"""Explicit known-file save slot. No filesystem discovery, crawling or model."""
import json
from pathlib import Path
from tools import chat_logic as C
from tools.topic_chat_sources import atomic_json

class SessionStore:
    def __init__(self, path):
        self.path = Path(path)

    def load(self):
        if not self.path.exists():
            return {}
        value = json.loads(self.path.read_text(encoding='utf-8'))
        content = value.get('content', {})
        if value.get('sha256') != C.digest(content) or content.get('schema') != 1:
            raise ValueError('Session save failed integrity check; retained unchanged. Restore a trusted backup.')
        sessions = content['sessions']
        if not isinstance(sessions, dict) or any(not C.verify_log(s['log']) for s in sessions.values()):
            raise ValueError('Saved session transcript failed continuity check; retained unchanged.')
        return sessions

    def save(self, sessions):
        content = {'schema': 1, 'sessions': sessions}
        atomic_json(self.path, {'content': content, 'sha256': C.digest(content)})
