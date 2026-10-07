import unittest

from mplpb_combined import ledger as L, reader as R
from tests.support import LedgerTest

OPEN = R.Profile("open", None, True)       # scope first, then prose
SCOPE = R.Profile("scope", None, False)    # scope or nothing


class TestThreeCases(LedgerTest):
    def setUp(self):
        super().setUp()
        self.bisque = self.page("Bisque", "Bisque firing schedule", "raw clay; first firing")
        self.glaze = self.page("Glaze", "Glaze firing schedule", "glazed pots; second firing")

    def ask(self, q, profile=OPEN):
        return R.answer(self.root, q, profile)

    def test_exactly_one_owner_returns_that_page(self):
        a = self.ask("bisque schedule")
        self.assertEqual((a.kind, a.record.id), (R.RETURN, self.bisque.id))

    def test_returned_words_are_the_page_and_nothing_else(self):
        a = self.ask("raw clay")
        self.assertEqual(a.text, L.Ledger(self.root).by_id[self.bisque.id][0].text)
        self.assertTrue(a.record.intact)

    def test_two_owners_stop(self):
        a = self.ask("firing schedule")
        self.assertEqual(a.kind, R.AMBIGUOUS)
        self.assertEqual({r.id for r, _ in a.candidates}, {self.bisque.id, self.glaze.id})
        self.assertIsNone(a.record)
        self.assertEqual(a.text, "")

    def test_no_owner_says_not_in_corpus(self):
        a = self.ask("capital of France")
        self.assertEqual(a.kind, R.NOT_IN_CORPUS)
        self.assertEqual(a.text, "")

    def test_a_question_split_across_two_pages_is_not_blended(self):
        a = self.ask("bisque and glaze")
        self.assertEqual(a.kind, R.NOT_IN_CORPUS)      # neither declares most of it
        self.assertEqual(a.text, "")

    def test_the_page_that_declares_everything_beats_a_partial_claim(self):
        a = self.ask("glazed pots firing")
        self.assertEqual((a.kind, a.record.id), (R.RETURN, self.glaze.id))

    def test_prose_is_consulted_only_when_scope_owns_nothing_and_says_so(self):
        w = self.page("Wedging", "Wedging clay", body="The pyrometer is mentioned only here.")
        self.assertEqual(self.ask("pyrometer", SCOPE).kind, R.NOT_IN_CORPUS)
        a = self.ask("pyrometer")
        self.assertEqual((a.kind, a.record.id, a.matched_on), (R.RETURN, w.id, "prose"))
        self.assertIn("matched on prose, not on declared scope", a.citation())
        self.assertNotIn("matched on prose", self.ask("bisque schedule").citation())

    def test_scope_overrides_prose(self):
        self.page("Loading", "Kiln loading", body="Bisque firing schedule, said in passing.")
        a = self.ask("bisque schedule")
        self.assertEqual((a.record.id, a.matched_on), (self.bisque.id, "scope"))

    def test_prose_needs_every_word_and_two_such_pages_stop(self):
        self.page("A", "alpha", body="The damper sits by the flue.")
        self.page("B", "beta", body="Close the damper before lighting.")
        self.assertEqual(self.ask("damper flue").record.title, "A")
        self.assertEqual(self.ask("damper").kind, R.AMBIGUOUS)
        self.assertEqual(self.ask("damper chimney").kind, R.NOT_IN_CORPUS)

    def test_empty_and_stopword_questions_are_refused(self):
        for q in ("", "what is the", "?!"):
            self.assertEqual(self.ask(q).kind, R.NOT_IN_CORPUS, q)

    def test_word_endings_are_folded_and_nothing_else_is(self):
        for q in ("schedules", "scheduling", "scheduled"):
            self.assertEqual(self.ask(q).kind, R.AMBIGUOUS, q)
        self.assertEqual(R.stem("firing"), R.stem("fired"))
        self.assertEqual(R.stem("recycling"), R.stem("recycle"))
        self.assertEqual(R.stem("running"), "run")
        self.assertEqual(R.stem("glass"), "glass")
        self.assertEqual(R.terms("the ram's head"), {"ram", "head"})
        self.assertEqual(self.ask("timetable").kind, R.NOT_IN_CORPUS)   # no synonyms

    def test_citation_carries_id_path_status_origin_depth_hash_and_local(self):
        c = self.ask("bisque").citation()
        for part in (self.bisque.id, self.bisque.path, "current", "origin human d0",
                     "sha256:", "local"):
            self.assertIn(part, c)

    def test_decide_is_the_whole_rule(self):
        d = {"a": {"x", "y"}, "b": {"y", "z"}, "c": {"x", "y", "w"}}
        full = {"a": {"x", "y", "p"}, "b": {"y", "z", "p", "q"}, "c": {"x", "y", "w"}}
        self.assertEqual(R.decide({"z"}, d), (R.RETURN, ["b"], "scope"))
        self.assertEqual(R.decide({"y", "z"}, d), (R.RETURN, ["b"], "scope"))
        self.assertEqual(R.decide({"x", "y"}, d), (R.AMBIGUOUS, ["a", "c"], "scope"))
        self.assertEqual(R.decide({"x", "y", "w"}, d), (R.RETURN, ["c"], "scope"))  # more specific
        self.assertEqual(R.decide({"x", "m", "n"}, d), (R.NOT_IN_CORPUS, [], ""))   # 1 of 3
        self.assertEqual(R.decide({"x", "z"}, d), (R.NOT_IN_CORPUS, [], ""))        # split
        self.assertEqual(R.decide({"q"}, d, full), (R.RETURN, ["b"], "prose"))
        self.assertEqual(R.decide({"p"}, d, full), (R.AMBIGUOUS, ["a", "b"], "prose"))
        self.assertEqual(R.decide({"q", "m"}, d, full), (R.NOT_IN_CORPUS, [], ""))
        self.assertEqual(R.decide(set(), d, full), (R.NOT_IN_CORPUS, [], ""))


class TestDials(LedgerTest):
    def test_scope_ownership_needs_more_than_half_the_question(self):
        self.page("Kiln", "Kiln loading")
        self.assertEqual(R.answer(self.root, "kiln zebra giraffe", SCOPE).kind, R.NOT_IN_CORPUS)
        self.assertEqual(R.answer(self.root, "kiln zebra", SCOPE).kind, R.NOT_IN_CORPUS)
        self.assertEqual(R.answer(self.root, "kiln loading zebra", SCOPE).kind, R.RETURN)
        self.assertEqual(R.answer(self.root, "kiln", SCOPE).kind, R.RETURN)

    def test_one_stray_word_declared_elsewhere_does_not_break_ownership(self):
        f = self.page("Faults", "Glaze faults", "small holes in the fired surface")
        self.page("Cones", "Witness cones", "overfired load")
        a = R.answer(self.root, "small holes in the fired surface of the load", SCOPE)
        self.assertEqual((a.kind, a.record.id), (R.RETURN, f.id))

    def test_index_pages_never_own_a_question(self):
        self.page("Kiln", "Kiln loading")
        (self.root / "index.html").write_text(
            '<html><head><title>Index</title><meta name="mplpb:document-id" content="IDX-1">'
            '<meta name="mplpb:scope" content="kiln loading glaze clay everything">'
            '<meta name="mplpb:status" content="current"></head><body>kiln</body></html>',
            encoding="utf-8")
        a = R.answer(self.root, "kiln loading", OPEN)
        self.assertEqual((a.kind, a.record.title), (R.RETURN, "Kiln"))

    def test_shipped_profiles_get_stricter_toward_the_customer(self):
        lab, internal, external = (R.PROFILES[n] for n in ("lab", "internal", "external"))
        self.assertGreater(lab.max_depth, internal.max_depth)
        self.assertEqual(external.max_depth, 0)
        self.assertTrue(lab.prose and internal.prose)
        self.assertFalse(external.prose)



class TestNotFor(LedgerTest):
    def setUp(self):
        super().setUp()
        self.gas = self.page("Gas kiln schedule", "Glaze firing schedule in the gas kiln",
                             not_for="booking; permission; allowed")

    def test_a_page_is_set_aside_for_a_question_it_says_is_not_its_own(self):
        a = R.answer(self.root, "who is allowed to use the gas kiln", OPEN)
        self.assertEqual(a.kind, R.NOT_IN_CORPUS)
        self.assertEqual([(r.id, w) for r, w in a.set_aside], [(self.gas.id, ["allowed"])])
        self.assertIn("says it is not for: allowed", R.render(a))

    def test_the_same_page_still_owns_its_own_questions(self):
        a = R.answer(self.root, "gas kiln firing schedule", OPEN)
        self.assertEqual((a.kind, a.record.id), (R.RETURN, self.gas.id))
        self.assertEqual(a.set_aside, [])

    def test_not_for_blocks_the_prose_step_as_well(self):
        p = self.page("Rota", "Studio rota", body="Booking is by the sheet on the door.",
                      not_for="sheet")
        self.assertEqual(R.answer(self.root, "sheet on the door", OPEN).kind, R.NOT_IN_CORPUS)
        self.assertEqual(R.answer(self.root, "door", OPEN).record.id, p.id)

    def test_a_word_the_page_declares_cannot_also_be_not_for(self):
        w = self.page("Wedging", "Wedging clay for the wheel", not_for="wheel repair")
        self.assertEqual(R.not_for_terms(L.Ledger(self.root).by_id[w.id][0]), {"repair"})
        self.assertEqual(R.answer(self.root, "wedging wheel", OPEN).record.id, w.id)
        self.assertIn("C15", self.codes(level="warning"))

    def test_the_field_is_hashed_when_used_and_absent_from_the_hash_when_not(self):
        from mplpb_combined.record import compute_hash, parse_page, upsert_meta
        base = {"document-id": "X-1", "scope": "s"}
        self.assertEqual(compute_hash(base, "t", "b"), compute_hash(dict(base, **{"not-for": ""}), "t", "b"))
        self.assertNotEqual(compute_hash(base, "t", "b"),
                            compute_hash(dict(base, **{"not-for": "x"}), "t", "b"))
        text = (self.root / self.gas.path).read_text(encoding="utf-8")
        self.assertFalse(parse_page(upsert_meta(text, "not-for", "nothing"), "x").intact)

    def test_a_revision_inherits_not_for_and_can_change_it(self):
        v2 = L.revise(self.root, self.gas.id, body="new", when="x")
        self.assertEqual(v2.not_for, "booking; permission; allowed")
        v3 = L.revise(self.root, v2.id, not_for="booking", when="x")
        self.assertEqual(v3.not_for, "booking")
        self.assertEqual(R.answer(self.root, "who is allowed to use the gas kiln", OPEN).kind,
                         R.RETURN)

    def test_ignoring_the_field_is_possible_only_as_a_stated_comparison(self):
        off = R.Profile("cmp", None, True, False)
        self.assertEqual(R.answer(self.root, "who is allowed to use the gas kiln", off).kind,
                         R.RETURN)
        self.assertTrue(all(p.not_for for p in R.PROFILES.values()))


if __name__ == "__main__":
    unittest.main()
