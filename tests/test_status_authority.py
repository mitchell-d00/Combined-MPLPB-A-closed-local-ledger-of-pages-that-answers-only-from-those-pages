from mplpb_combined import ledger as L, reader as R
from mplpb_combined.record import parse_page, upsert_meta
from tests.support import LedgerTest, WHEN


class TestStatusAuthority(LedgerTest):
    def successor(self):
        old = self.page('Schedule', 'kiln schedule', body='Original.')
        new = L.revise(self.root, old.id, body='Replacement.', when=WHEN)
        self.edit(old, 'content="retired"', 'content="current"')
        return old, new

    def rewrite(self, rec, name, value, seal=True):
        path = self.root / rec.path
        text = upsert_meta(path.read_text(), name, value)
        if seal:
            text = upsert_meta(text, 'hash', parse_page(text, rec.path).hash_actual)
        path.write_text(text)

    def assert_original_current(self, old):
        led = L.Ledger(self.root)
        self.assertEqual(led.effective_status(led.by_id[old.id][0]), 'current')

    def test_altered_successor_cannot_retire_original(self):
        old, new = self.successor()
        self.edit(new, 'Replacement.', 'Corrupted.')
        self.assert_original_current(old)
        self.assertEqual(R.answer(self.root, 'kiln schedule').record.id, old.id)

    def test_unsealed_successor_cannot_retire_original(self):
        old, new = self.successor()
        self.rewrite(new, 'hash', '', seal=False)
        self.assert_original_current(old)

    def test_wrong_or_missing_pin_cannot_retire_original(self):
        for pin in ('T-0001@sha256:wrong', 'T-0001', 'MISSING@sha256:wrong'):
            with self.subTest(pin=pin):
                if not hasattr(self, 'old'):
                    self.old, self.new = self.successor()
                self.rewrite(self.new, 'supersedes', pin)
                self.assert_original_current(self.old)

    def test_duplicate_successor_cannot_retire_original(self):
        old, new = self.successor()
        (self.root / 'copy.html').write_text((self.root / new.path).read_text())
        self.assert_original_current(old)

    def test_cycle_cannot_retire_original(self):
        old, new = self.successor()
        self.rewrite(new, 'derived-from', new.id + '@' + new.hash)
        self.assert_original_current(old)

    def test_invalid_status_origin_or_depth_cannot_retire_original(self):
        old, new = self.successor()
        original = (self.root / new.path).read_text()
        for name, value in [('status', 'unknown'), ('origin', 'unknown'),
                            ('origin-depth', 'nonsense')]:
            with self.subTest(name=name):
                (self.root / new.path).write_text(original)
                self.rewrite(new, name, value)
                self.assert_original_current(old)

    def test_retired_valid_successor_keeps_original_retired(self):
        old, new = self.successor()
        L.withdraw(self.root, new.id, when=WHEN)
        led = L.Ledger(self.root)
        self.assertEqual(led.effective_status(led.by_id[old.id][0]), 'retired')

    def test_understated_depth_cannot_retire_original(self):
        old = self.page('Source', 'source', origin='machine')
        new = L.revise(self.root, old.id, body='Replacement.', when=WHEN)
        self.edit(old, 'content="retired"', 'content="current"')
        self.rewrite(new, 'origin-depth', '0')
        self.assert_original_current(old)

    def test_invalid_parent_cannot_give_successor_authority(self):
        parent = self.page('Parent', 'reference', body='Parent body.')
        old = self.page('Schedule', 'kiln schedule')
        new = L.write(self.root, title='New', scope='kiln schedule',
                      derived_from=[parent.id], supersedes=[old.id], when=WHEN)
        self.edit(old, 'content="retired"', 'content="current"')
        self.edit(parent, 'Parent body.', 'Altered parent.')
        self.assert_original_current(old)
