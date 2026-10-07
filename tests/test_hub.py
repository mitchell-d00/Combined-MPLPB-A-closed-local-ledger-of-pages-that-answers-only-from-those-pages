import shutil
import unittest

from mplpb_combined import ledger as L, reader as R
from tests.support import LedgerTest, WHEN

OPEN = R.Profile("open", None, False)   # scope only


class TestHub(LedgerTest):
    def setUp(self):
        super().setUp()
        self.kiln = self.tmp / "kiln"; self.kiln.mkdir()
        self.garden = self.tmp / "garden"; self.garden.mkdir()
        self.hub = self.tmp / "hub"; self.hub.mkdir()
        self.k = self.page("Bisque", "Bisque firing schedule", "unlabelled bucket",
                           body="Kiln words.", root=self.kiln)
        self.g = self.page("Compost", "Compost turning schedule", body="Garden words.",
                           root=self.garden)
        self.pk = self.page("Kiln corpus", "Kiln and firing", body="POINTER BODY",
                            root=self.hub, kind="pointer", points_to="../kiln")
        self.pg = self.page("Garden corpus", "Garden and compost", body="POINTER BODY",
                            root=self.hub, kind="pointer", points_to="../garden")

    def test_a_pointer_routes_to_the_owner_and_the_owner_answers(self):
        a = R.answer(self.hub, "bisque firing", OPEN)
        self.assertEqual((a.kind, a.record.id), (R.RETURN, self.k.id))
        self.assertEqual(a.text.splitlines()[-1], "Kiln words.")
        self.assertIn("points to ../kiln", a.route[0])

    def test_a_hub_never_answers_as_the_owner(self):
        for q in ("kiln", "garden compost", "firing", "bisque", "kiln garden", "zebra"):
            a = R.answer(self.hub, q, OPEN)
            self.assertNotIn("POINTER BODY", a.text, q)
            if a.record:
                self.assertNotEqual(a.record.kind, "pointer", q)

    def test_an_unreachable_owner_is_named_and_not_impersonated(self):
        shutil.rmtree(self.kiln)
        a = R.answer(self.hub, "kiln firing", OPEN)
        self.assertEqual(a.kind, R.NOT_IN_CORPUS)
        self.assertIn("not reachable", a.reason)
        self.assertIsNone(a.record)

    def test_two_pointers_owning_one_question_are_not_merged(self):
        a_ = self.page("Kiln tools", "Shared tools", root=self.hub, kind="pointer",
                       points_to="../kiln")
        b_ = self.page("Garden tools", "Shared tools", root=self.hub, kind="pointer",
                       points_to="../garden")
        a = R.answer(self.hub, "shared tools", OPEN)
        self.assertEqual(a.kind, R.AMBIGUOUS)
        self.assertEqual({r.id for r, _ in a.candidates}, {a_.id, b_.id})
        self.assertEqual(a.text, "")

    def test_a_question_no_pointer_declares_is_put_to_each_corpus(self):
        a = R.answer(self.hub, "unlabelled bucket", OPEN)
        self.assertEqual((a.kind, a.record.id), (R.RETURN, self.k.id))
        self.assertIn("each corpus was asked", a.route[0])

    def test_fan_out_with_two_claimants_stops(self):
        a = R.answer(self.hub, "schedule", OPEN)
        self.assertEqual(a.kind, R.AMBIGUOUS)
        self.assertIn("does not merge", a.reason)
        self.assertEqual(a.text, "")

    def test_fan_out_with_no_claimant_is_not_in_corpus(self):
        self.assertEqual(R.answer(self.hub, "zebra", OPEN).kind, R.NOT_IN_CORPUS)

    def test_pointer_loops_end_in_a_refusal(self):
        self.page("Back to hub", "Looping loop", root=self.kiln, kind="pointer",
                  points_to="../hub")
        self.page("To kiln again", "Looping loop", root=self.hub, kind="pointer",
                  points_to="../kiln")
        a = R.answer(self.hub, "looping", OPEN)
        self.assertEqual(a.kind, R.NOT_IN_CORPUS)

    def test_the_profile_travels_with_the_question(self):
        L.derive(self.kiln, [self.k.id], title="Digest", scope="Weekly digest", prefix="T",
                 when=WHEN)
        self.assertEqual(R.answer(self.hub, "weekly digest", R.PROFILES["external"]).kind,
                         R.NOT_IN_CORPUS)
        self.assertEqual(R.answer(self.hub, "weekly digest", R.PROFILES["internal"]).kind,
                         R.RETURN)


if __name__ == "__main__":
    unittest.main()
