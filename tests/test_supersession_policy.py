"""Policy examples for successor authority.

Expected reads were fixed in SUPERSESSION_POLICY.md before these checks.
Published kill-test probes are not inputs. Where 478a86b disagrees, the test
asserts that disagreement so a green run is not agreement.
"""
import hashlib
import unittest
from pathlib import Path

from mplpb_combined import ledger as L
from mplpb_combined import reader as R
from mplpb_combined.record import parse_page, upsert_meta
from tests.support import LedgerTest, WHEN

PROBE_FILES = (
    "killtest/probes.json",
    "killtest/probes_heldout.json",
    "killtest/probes_adjacent.json",
    "killtest/probes.sha256",
)
FROZEN_PROBE_HASHES = {
    "killtest/probes.json": "fd0f8b1d61a206dcbb612fdc7503ab339a09ec02aebf576b27554c1fb4cb9076",
    "killtest/probes_heldout.json": "097fa2ef7bf47661329a00b4c6c68ada4502553d69459952995e1e65184cb184",
    "killtest/probes_adjacent.json": "9dfb4ecc4da5a03cb9fb3860d25f9ff856e07f9384016b6b17953af72669f3ba",
    "killtest/probes.sha256": "1c4556f219981adb7902c593d3c2204a66327bbb3f6f3d578b4f2308aa2c3b3d",
}


def probe_hashes(repo: Path) -> dict:
    return {
        rel: hashlib.sha256((repo / rel).read_bytes()).hexdigest()
        for rel in PROBE_FILES
        if (repo / rel).is_file()
    }


class PolicyExamples(LedgerTest):
    def rewrite(self, rec, name, value, seal=True):
        path = self.root / rec.path
        text = upsert_meta(path.read_text(encoding="utf-8"), name, value)
        if seal:
            text = upsert_meta(text, "hash", parse_page(text, rec.path).hash_actual)
        path.write_text(text, encoding="utf-8")

    def pair(self):
        old = self.page("Schedule", "kiln schedule", body="Original schedule.")
        new = L.revise(self.root, old.id, body="Replacement schedule.", when=WHEN)
        self.edit(old, 'content="retired"', 'content="current"')
        return old, new

    def answer(self, question="kiln schedule"):
        return R.answer(self.root, question)

    def effective(self, doc_id):
        led = L.Ledger(self.root)
        return led.effective_status(led.by_id[doc_id][0])

    def test_p1_valid_replacement_retires_predecessor(self):
        old = self.page("Schedule", "kiln schedule", body="Original schedule.")
        new = L.revise(self.root, old.id, body="Replacement schedule.", when=WHEN)
        self.assertEqual(self.effective(old.id), "retired")
        self.assertEqual(self.answer().record.id, new.id)

    def test_p2_damaged_replacement_does_not_retire(self):
        old, new = self.pair()
        self.edit(new, "Replacement schedule.", "Damaged schedule.")
        self.assertEqual(self.effective(old.id), "current")
        self.assertEqual(self.answer().record.id, old.id)

    def test_p3_duplicate_id_does_not_retire(self):
        old, new = self.pair()
        (self.root / "copy.html").write_text((self.root / new.path).read_text(), encoding="utf-8")
        self.assertEqual(self.effective(old.id), "current")
        self.assertEqual(self.answer().record.id, old.id)

    def test_p4_missing_pin_does_not_retire(self):
        old, new = self.pair()
        self.rewrite(new, "supersedes", old.id)
        self.assertEqual(self.effective(old.id), "current")
        self.assertEqual(self.answer().record.id, old.id)

    def test_p5_wrong_pin_does_not_retire(self):
        old, new = self.pair()
        self.rewrite(new, "supersedes", old.id + "@sha256:wrong")
        self.assertEqual(self.effective(old.id), "current")
        self.assertEqual(self.answer().record.id, old.id)

    def test_p6_invalid_origin_or_depth_does_not_retire(self):
        old, new = self.pair()
        original = (self.root / new.path).read_text(encoding="utf-8")
        for name, value in (("origin", "unknown"), ("origin-depth", "9")):
            with self.subTest(name=name):
                (self.root / new.path).write_text(original, encoding="utf-8")
                self.rewrite(new, name, value)
                self.assertEqual(self.effective(old.id), "current")
                self.assertEqual(self.answer().record.id, old.id)

    def test_p7_withdraw_does_not_restore_predecessor(self):
        old = self.page("Schedule", "kiln schedule", body="Original schedule.")
        new = L.revise(self.root, old.id, body="Replacement schedule.", when=WHEN)
        L.withdraw(self.root, new.id, when=WHEN)
        self.assertEqual(self.effective(old.id), "retired")
        self.assertEqual(self.effective(new.id), "retired")
        self.assertIsNone(self.answer().record)

    def test_p8_restore_is_an_explicit_new_revision(self):
        old = self.page("Schedule", "kiln schedule", body="Original schedule.")
        new = L.revise(self.root, old.id, body="Replacement schedule.", when=WHEN)
        L.withdraw(self.root, new.id, when=WHEN)
        with self.assertRaises(ValueError):
            L.revise(self.root, old.id, body="Original schedule.", when=WHEN)
        restored = L.write(
            self.root, title="Restored schedule", scope="kiln schedule",
            body="Original schedule.", supersedes=[new.id], when=WHEN,
        )
        self.assertEqual(self.effective(old.id), "retired")
        self.assertEqual(self.effective(new.id), "retired")
        self.assertEqual(self.answer().record.id, restored.id)
        self.assertEqual(restored.supersedes[0].id, new.id)

    def test_p8_cannot_supersede_behind_a_later_head(self):
        old = self.page("Schedule", "kiln schedule", body="Original schedule.")
        mid = L.revise(self.root, old.id, body="Replacement schedule.", when=WHEN)
        head = L.revise(self.root, mid.id, body="Later schedule.", when=WHEN)
        with self.assertRaises(ValueError):
            L.write(
                self.root, title="Fork", scope="kiln schedule",
                body="Original schedule.", supersedes=[old.id], when=WHEN,
            )
        self.assertEqual(self.effective(old.id), "retired")
        self.assertEqual(self.effective(mid.id), "retired")
        self.assertEqual(self.answer().record.id, head.id)

    def test_p8_withdrawn_chain_must_pin_the_terminal_head(self):
        old = self.page("Schedule", "kiln schedule", body="Original schedule.")
        mid = L.revise(self.root, old.id, body="Replacement schedule.", when=WHEN)
        L.withdraw(self.root, mid.id, when=WHEN)
        with self.assertRaises(ValueError):
            L.write(
                self.root, title="Skip head", scope="kiln schedule",
                body="Original schedule.", supersedes=[old.id], when=WHEN,
            )
        restored = L.write(
            self.root, title="Restored from head", scope="kiln schedule",
            body="Original schedule.", supersedes=[mid.id], when=WHEN,
        )
        self.assertEqual(restored.supersedes[0].id, mid.id)
        self.assertEqual(self.effective(old.id), "retired")
        self.assertEqual(self.answer().record.id, restored.id)

    def test_p8_cannot_supersede_predecessor_while_replacement_is_current(self):
        old = self.page("Schedule", "kiln schedule", body="Original schedule.")
        new = L.revise(self.root, old.id, body="Replacement schedule.", when=WHEN)
        with self.assertRaises(ValueError):
            L.write(
                self.root, title="Fork", scope="kiln schedule",
                body="Original schedule.", supersedes=[old.id], when=WHEN,
            )
        self.assertEqual(self.effective(old.id), "retired")
        self.assertEqual(self.answer().record.id, new.id)

    def test_p9_wrong_basis_pin_is_not_served(self):
        basis = self.page("Basis", "kiln basis", body="Basis text.")
        derived = L.derive(
            self.root, [basis.id], title="Derivative", scope="kiln derivative",
            body="Derived text.", when=WHEN,
        )
        self.rewrite(derived, "derived-from", basis.id + "@sha256:wrong")
        led = L.Ledger(self.root)
        self.assertIn("C6", {f.code for f in led.findings()})
        self.assertNotIn(derived.id, {r.id for r in led.servable()})
        self.assertIsNone(self.answer("kiln derivative").record)

    def test_p9_stale_derivative_is_withheld_until_rechecked(self):
        basis = self.page("Basis", "kiln basis", body="Basis text.")
        derived = L.derive(
            self.root, [basis.id], title="Derivative", scope="kiln derivative",
            body="Derived text.", when=WHEN,
        )
        replacement = L.revise(self.root, basis.id, body="Replacement basis.", when=WHEN)
        led = L.Ledger(self.root)
        self.assertEqual(led.effective_status(led.by_id[basis.id][0]), "retired")
        self.assertNotIn(derived.id, {r.id for r in led.servable()})
        self.assertIsNone(self.answer("kiln derivative").record)
        rechecked = L.write(
            self.root, title="Rechecked derivative", scope="kiln derivative",
            body="Derived text.", derived_from=[replacement.id],
            supersedes=[derived.id], when=WHEN,
        )
        self.assertEqual(self.answer("kiln derivative").record.id, rechecked.id)

    def test_published_probes_are_not_this_suite(self):
        repo = Path(__file__).resolve().parents[1]
        hashes = probe_hashes(repo)
        self.assertEqual(hashes, FROZEN_PROBE_HASHES)
