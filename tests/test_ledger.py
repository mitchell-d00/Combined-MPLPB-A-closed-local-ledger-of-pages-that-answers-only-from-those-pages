import json
import os
import threading
import unittest

from mplpb_combined import ledger as L, reader as R
from tests.support import LedgerTest, WHEN

OPEN = R.Profile("open", None, False)   # scope only


class TestRevision(LedgerTest):
    def test_a_change_writes_a_new_page_and_retires_the_old_one(self):
        old = self.page("Bisque", "Bisque schedule", body="950 C")
        new = L.revise(self.root, old.id, body="1000 C", when=WHEN)
        led = L.Ledger(self.root)
        self.assertNotEqual(new.id, old.id)
        self.assertEqual(led.effective_status(led.by_id[old.id][0]), "retired")
        self.assertEqual(led.by_id[old.id][0].status, "retired")
        self.assertIn("950 C", led.by_id[old.id][0].text)          # not overwritten
        self.assertTrue(led.by_id[old.id][0].intact)               # and not altered
        a = R.answer(self.root, "bisque schedule", OPEN)
        self.assertEqual((a.kind, a.record.id), (R.RETURN, new.id))
        self.assertEqual(self.codes(), [])

    def test_the_successor_pins_the_hash_of_what_it_replaced(self):
        old = self.page("Bisque", "Bisque schedule")
        new = L.revise(self.root, old.id, body="new", when=WHEN)
        self.assertEqual(new.supersedes[0].hash, old.hash)

    def test_a_crash_between_write_and_retire_is_still_read_correctly(self):
        old = self.page("Bisque", "Bisque schedule", body="950 C")
        new = L.revise(self.root, old.id, body="1000 C", when=WHEN)
        self.edit(old, 'mplpb:status" content="retired"', 'mplpb:status" content="current"')
        a = R.answer(self.root, "bisque schedule", OPEN)
        self.assertEqual((a.kind, a.record.id), (R.RETURN, new.id))
        self.assertIn("C9", self.codes(level="warning"))
        self.assertNotIn("C2", self.codes())

    def test_a_retired_page_cannot_be_revised_again(self):
        old = self.page("Bisque", "Bisque schedule")
        L.revise(self.root, old.id, body="v2", when=WHEN)
        with self.assertRaises(ValueError):
            L.revise(self.root, old.id, body="v3", when=WHEN)

    def test_a_fork_is_ambiguous_to_the_reader_and_an_error_to_the_validator(self):
        old = self.page("Bisque", "Bisque schedule")
        a = L.revise(self.root, old.id, body="A", when=WHEN)
        text = (self.root / a.path).read_text(encoding="utf-8")
        from mplpb_combined.record import parse_page, upsert_meta
        twin = upsert_meta(text, "document-id", "T-0099")
        twin = upsert_meta(twin, "hash", parse_page(twin, "x").hash_actual)
        (self.root / "t-0099.html").write_text(twin, encoding="utf-8")
        self.assertEqual(R.answer(self.root, "bisque schedule", OPEN).kind, R.AMBIGUOUS)
        self.assertIn("C10", self.codes(level="error"))

    def test_history_walks_the_chain_oldest_first(self):
        v1 = self.page("Bisque", "Bisque schedule")
        v2 = L.revise(self.root, v1.id, body="2", when=WHEN)
        v3 = L.revise(self.root, v2.id, body="3", when=WHEN)
        for start in (v1.id, v2.id, v3.id):
            self.assertEqual([r.id for r in L.Ledger(self.root).history(start)],
                             [v1.id, v2.id, v3.id])

    def test_withdraw_retires_without_a_successor_and_keeps_the_file(self):
        rec = self.page("Bisque", "Bisque schedule")
        L.withdraw(self.root, rec.id, when=WHEN)
        self.assertTrue((self.root / rec.path).exists())
        self.assertEqual(R.answer(self.root, "bisque", OPEN).kind, R.NOT_IN_CORPUS)

    def test_a_page_is_never_overwritten(self):
        self.page("A", "alpha", doc_id="T-0001")
        with self.assertRaises(ValueError):
            self.page("B", "beta", doc_id="T-0001")
        os.remove(self.root / "_log" / "ledger.jsonl")
        (self.root / "t-0002.html").write_text("occupied", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            self.page("C", "gamma")


class TestDepth(LedgerTest):
    def d(self, rec):
        led = L.Ledger(self.root)
        return led.depth(led.by_id[rec.id][0])

    def test_a_human_source_is_depth_zero(self):
        self.assertEqual(self.d(self.page("A", "alpha")), 0)

    def test_a_machine_page_from_nothing_is_depth_one(self):
        self.assertEqual(self.d(self.page("A", "alpha", origin="machine")), 1)

    def test_derivation_adds_one(self):
        a = self.page("A", "alpha")
        b = L.derive(self.root, [a.id], title="B", scope="beta", prefix="T", when=WHEN)
        c = L.derive(self.root, [b.id], title="C", scope="gamma", prefix="T", when=WHEN)
        self.assertEqual([self.d(x) for x in (a, b, c)], [0, 1, 2])
        self.assertEqual(c.depth_declared, 2)

    def test_derivation_adds_one_whoever_derives(self):
        a = self.page("A", "alpha")
        b = L.derive(self.root, [a.id], title="B", scope="beta", prefix="T", when=WHEN,
                     origin="human")
        self.assertEqual(self.d(b), 1)

    def test_many_parents_take_the_deepest(self):
        a = self.page("A", "alpha")
        b = L.derive(self.root, [a.id], title="B", scope="beta", prefix="T", when=WHEN)
        c = L.derive(self.root, [b.id], title="C", scope="gamma", prefix="T", when=WHEN)
        d = L.derive(self.root, [a.id, c.id], title="D", scope="delta", prefix="T", when=WHEN)
        self.assertEqual(self.d(d), 3)

    def test_derivation_does_not_copy_the_hash(self):
        a = self.page("A", "alpha")
        b = L.derive(self.root, [a.id], title="B", scope="beta", prefix="T", when=WHEN)
        self.assertNotEqual(a.hash, b.hash)
        self.assertEqual(b.derived_from[0].hash, a.hash)

    def test_revision_cannot_launder_depth(self):
        m = self.page("M", "mu", origin="machine")
        d2 = L.derive(self.root, [m.id], title="D", scope="delta", prefix="T", when=WHEN)
        human_edit = L.revise(self.root, d2.id, body="tidied", origin="human", when=WHEN)
        self.assertEqual(self.d(human_edit), 2)
        m2 = L.revise(self.root, m.id, body="tidied", origin="human", when=WHEN)
        self.assertEqual(self.d(m2), 1)

    def test_a_machine_revision_of_a_human_source_is_no_longer_depth_zero(self):
        a = self.page("A", "alpha")
        self.assertEqual(self.d(L.revise(self.root, a.id, body="x", origin="machine", when=WHEN)), 1)

    def test_ratification_resets_depth_keeps_lineage_and_names_the_person(self):
        a = self.page("A", "alpha")
        b = L.derive(self.root, [a.id], title="B", scope="beta", prefix="T", when=WHEN)
        r = L.ratify(self.root, b.id, "Dana Reviewer", when=WHEN)
        self.assertEqual(self.d(r), 0)
        self.assertEqual(r.ratified_by, "Dana Reviewer")
        self.assertEqual(r.origin, "machine")
        self.assertEqual([x.id for x in r.derived_from], [a.id])
        self.assertIn("ratified by Dana Reviewer", R.answer(self.root, "beta", OPEN).citation())
        with self.assertRaises(ValueError):
            L.ratify(self.root, r.id, "  ")

    def test_understated_depth_is_an_error_and_is_not_believed(self):
        a = self.page("A", "alpha")
        b = L.derive(self.root, [a.id], title="B", scope="beta", prefix="T", when=WHEN)
        from mplpb_combined.record import parse_page, upsert_meta
        p = self.root / b.path
        text = upsert_meta(p.read_text(encoding="utf-8"), "origin-depth", "0")
        text = upsert_meta(text, "hash", parse_page(text, "x").hash_actual)   # a careful liar
        p.write_text(text, encoding="utf-8")
        self.assertIn("C8", self.codes(level="error"))
        self.assertEqual(self.d(b), 1)

    def test_a_profile_withholds_what_is_too_deep_and_says_so(self):
        a = self.page("A", "alpha")
        b = L.derive(self.root, [a.id], title="B", scope="beta digest", prefix="T", when=WHEN)
        ext = R.answer(self.root, "beta digest", R.PROFILES["external"])
        self.assertEqual(ext.kind, R.NOT_IN_CORPUS)
        self.assertEqual([(r.id, d) for r, d in ext.withheld], [(b.id, 1)])
        self.assertEqual(R.answer(self.root, "beta digest", R.PROFILES["internal"]).kind, R.RETURN)
        L.ratify(self.root, b.id, "Dana Reviewer", when=WHEN)
        self.assertEqual(R.answer(self.root, "beta digest", R.PROFILES["external"]).kind, R.RETURN)

    def test_no_path_serves_a_page_above_the_limit(self):
        a = self.page("A", "alpha")
        b = L.derive(self.root, [a.id], title="B", scope="beta", prefix="T", when=WHEN)
        L.derive(self.root, [b.id], title="C", scope="gamma", prefix="T", when=WHEN)
        for q in ("alpha", "beta", "gamma", "alpha beta gamma", "beta gamma"):
            ans = R.answer(self.root, q, R.Profile("p", 0, 0.0))
            served = [ans.record] if ans.record else []
            served += [r for r, _ in ans.candidates]
            for r in served:
                self.assertEqual(L.Ledger(self.root).depth(r), 0, q)


class TestValidation(LedgerTest):
    def test_a_clean_ledger_has_no_findings(self):
        a = self.page("A", "alpha")
        L.derive(self.root, [a.id], title="B", scope="beta", prefix="T", when=WHEN)
        self.assertEqual(self.codes(), [])

    def test_deleting_a_parent_breaks_the_child(self):
        a = self.page("A", "alpha")
        L.derive(self.root, [a.id], title="B", scope="beta", prefix="T", when=WHEN)
        os.remove(self.root / a.path)
        self.assertIn("C5", self.codes(level="error"))

    def test_swapping_a_parent_for_a_different_page_with_its_id_is_caught(self):
        a = self.page("A", "alpha", body="original")
        L.derive(self.root, [a.id], title="B", scope="beta", prefix="T", when=WHEN)
        from mplpb_combined.record import render_page
        fields = dict(L.Ledger(self.root).by_id[a.id][0].fields)
        (self.root / a.path).write_text(render_page(fields, "A", "<p>substituted</p>"),
                                        encoding="utf-8")
        codes = self.codes(level="error")
        self.assertIn("C6", codes)            # the child's pin no longer matches
        self.assertNotIn("C2", codes)         # though the forgery is self-consistent

    def test_duplicate_ids_are_an_error(self):
        a = self.page("A", "alpha")
        (self.root / "copy.html").write_text((self.root / a.path).read_text(encoding="utf-8"),
                                             encoding="utf-8")
        self.assertIn("C3", self.codes(level="error"))

    def test_a_hand_written_page_is_unsealed_until_sealed(self):
        (self.root / "note.html").write_text(
            '<html><head><title>Note</title><meta name="mplpb:document-id" content="N-1">'
            '<meta name="mplpb:scope" content="grog definition"></head>'
            '<body><p>Pre-fired clay.</p></body></html>', encoding="utf-8")
        self.assertEqual(R.answer(self.root, "grog", OPEN).kind, R.NOT_IN_CORPUS)
        self.assertIn("C1", self.codes(level="error"))
        self.assertEqual(L.seal(self.root, when=WHEN), ["note.html"])
        self.assertEqual(R.answer(self.root, "grog", OPEN).kind, R.RETURN)
        self.assertEqual(self.codes(level="error"), [])
        self.assertEqual(L.seal(self.root, when=WHEN), [])

    def test_seal_never_blesses_an_altered_page(self):
        rec = self.page("A", "alpha", body="original")
        self.edit(rec, "original", "changed")
        self.assertEqual(L.seal(self.root, when=WHEN), [])
        self.assertIn("C2", self.codes(level="error"))

    def test_stray_files_are_reported_and_never_read(self):
        (self.root / "loose.html").write_text("<html><body>kiln kiln kiln</body></html>",
                                              encoding="utf-8")
        self.assertIn("C13", self.codes(level="warning"))
        self.assertEqual(R.answer(self.root, "kiln", OPEN).kind, R.NOT_IN_CORPUS)

    def test_a_lineage_loop_is_reported_not_followed_forever(self):
        a = self.page("A", "alpha")
        b = L.derive(self.root, [a.id], title="B", scope="beta", prefix="T", when=WHEN)
        from mplpb_combined.record import upsert_meta
        p = self.root / a.path
        p.write_text(upsert_meta(p.read_text(encoding="utf-8"), "derived-from", b.id),
                     encoding="utf-8")
        self.assertIn("C12", self.codes(level="error"))
        L.Ledger(self.root).depth(L.Ledger(self.root).by_id[b.id][0])


class TestLogAndLock(LedgerTest):
    def test_every_write_and_retirement_is_logged_in_a_chain(self):
        a = self.page("A", "alpha")
        L.revise(self.root, a.id, body="2", when=WHEN)
        log = L.read_log(self.root)
        self.assertEqual([e["event"] for e in log], ["write", "revise", "retire"])
        self.assertEqual([e["seq"] for e in log], [1, 2, 3])
        self.assertEqual(log[1]["prev"], log[0]["entry_hash"])

    def test_editing_the_log_breaks_the_chain(self):
        a = self.page("A", "alpha")
        L.revise(self.root, a.id, body="2", when=WHEN)
        p = L.log_path(self.root)
        lines = p.read_text(encoding="utf-8").splitlines()
        first = json.loads(lines[0]); first["time"] = "1999-01-01T00:00Z"
        p.write_text("\n".join([json.dumps(first)] + lines[1:]) + "\n", encoding="utf-8")
        self.assertIn("C14", self.codes(level="error"))

    def test_identifiers_are_allocated_and_never_reused(self):
        a = self.page("A", "alpha")
        b = self.page("B", "beta")
        self.assertEqual((a.id, b.id), ("T-0001", "T-0002"))
        os.remove(self.root / b.path)
        self.assertEqual(self.page("C", "gamma").id, "T-0003")

    def test_concurrent_writers_get_distinct_ids_and_one_log(self):
        errors = []

        def work(i):
            try:
                self.page(f"P{i}", f"scope{i}")
            except Exception as e:  # pragma: no cover
                errors.append(e)

        threads = [threading.Thread(target=work, args=(i,)) for i in range(12)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        self.assertEqual(errors, [])
        led = L.Ledger(self.root)
        self.assertEqual(len(led.by_id), 12)
        self.assertEqual(self.codes(), [])

    def test_a_held_lock_refuses_a_second_writer_and_a_stale_one_is_cleared(self):
        with L.ledger_lock(self.root):
            with self.assertRaises(L.LedgerBusy):
                with L.ledger_lock(self.root, wait=0.1):
                    pass
        lock = self.root / "_log" / ".lock"
        lock.write_text("dead writer", encoding="utf-8")
        os.utime(lock, (1, 1))
        self.page("A", "alpha")

    def test_refusing_to_build_on_an_altered_page(self):
        a = self.page("A", "alpha", body="original")
        self.edit(a, "original", "changed")
        with self.assertRaises(ValueError):
            L.derive(self.root, [a.id], title="B", scope="beta", prefix="T", when=WHEN)
        with self.assertRaises(KeyError):
            L.derive(self.root, ["NOPE-1"], title="B", scope="beta", prefix="T", when=WHEN)


if __name__ == "__main__":
    unittest.main()
