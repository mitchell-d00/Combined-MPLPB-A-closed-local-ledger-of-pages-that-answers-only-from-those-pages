"""Shared fixtures. Every test builds its own folder and throws it away."""
import shutil
import tempfile
import unittest
from pathlib import Path

from mplpb_combined import ledger as L

WHEN = "2026-01-01T00:00Z"


class LedgerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="mplpb-"))
        self.root = self.tmp / "corpus"
        self.root.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def page(self, title, scope, when_to_use="", body="Body text.", root=None, **kw):
        kw.setdefault("prefix", "T")
        kw.setdefault("when", WHEN)
        return L.write(root or self.root, title=title, scope=scope,
                       when_to_use=when_to_use, body=body, **kw)

    def codes(self, root=None, level=None):
        found = L.Ledger(root or self.root).findings()
        return sorted({f.code for f in found if level is None or f.level == level})

    def edit(self, rec, old, new, root=None):
        p = (root or self.root) / rec.path
        text = p.read_text(encoding="utf-8")
        assert old in text, old
        p.write_text(text.replace(old, new), encoding="utf-8")
