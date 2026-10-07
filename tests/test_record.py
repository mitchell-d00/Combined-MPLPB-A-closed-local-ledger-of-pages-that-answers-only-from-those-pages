import unittest

from mplpb_combined import ledger as L
from mplpb_combined.record import (
    Ref, compute_hash, format_refs, parse_page, parse_refs, render_page, upsert_meta,
)
from tests.support import LedgerTest


class TestPageFormat(unittest.TestCase):
    def fields(self, **kw):
        base = {"document-id": "X-0001", "scope": "A scope", "status": "current",
                "origin": "human", "origin-depth": "0"}
        base.update(kw)
        return base

    def test_rendered_page_declares_the_hash_a_reader_recomputes(self):
        rec = parse_page(render_page(self.fields(), "Title", "<p>Body</p>"), "x.html")
        self.assertTrue(rec.intact)
        self.assertEqual(rec.hash, rec.hash_actual)

    def test_six_formula_fields_are_all_readable(self):
        rec = parse_page(render_page(self.fields(**{"derived-from": "P-0001@sha256:ab"}),
                                     "T", "<p>B</p>"), "x.html")
        self.assertEqual(rec.id, "X-0001")
        self.assertEqual(rec.scope, "A scope")
        self.assertEqual(rec.status, "current")
        self.assertTrue(rec.hash.startswith("sha256:"))
        self.assertEqual(rec.derived_from, [Ref("P-0001", "sha256:ab")])
        self.assertEqual(rec.depth_declared, 0)

    def test_status_is_outside_the_hash(self):
        text = render_page(self.fields(), "T", "<p>B</p>")
        retired = parse_page(upsert_meta(text, "status", "retired"), "x.html")
        self.assertEqual(retired.status, "retired")
        self.assertTrue(retired.intact)

    def test_every_other_field_is_inside_the_hash(self):
        text = render_page(self.fields(), "T", "<p>B</p>")
        for name, value in (("scope", "Another scope"), ("origin-depth", "3"),
                            ("origin", "machine"), ("document-id", "X-0002")):
            self.assertFalse(parse_page(upsert_meta(text, name, value), "x.html").intact, name)

    def test_body_and_title_are_inside_the_hash(self):
        text = render_page(self.fields(), "T", "<p>B</p>")
        self.assertFalse(parse_page(text.replace("<p>B</p>", "<p>C</p>"), "x.html").intact)
        self.assertFalse(parse_page(text.replace("<title>T<", "<title>U<"), "x.html").intact)

    def test_underscore_and_hyphen_field_names_are_one_field(self):
        html = ('<html><head><title>T</title><meta name="mplpb:origin_depth" content="2">'
                '<meta name="mplpb:document_id" content="A-1"></head><body></body></html>')
        rec = parse_page(html, "a.html")
        self.assertEqual((rec.id, rec.depth_declared), ("A-1", 2))

    def test_upsert_replaces_either_spelling_in_place(self):
        html = ('<html><head><meta name="mplpb:origin_depth" content="2"></head>'
                '<body></body></html>')
        out = upsert_meta(html, "origin-depth", "5")
        self.assertEqual(out.count("mplpb:origin"), 1)
        self.assertEqual(parse_page(out, "a.html").depth_declared, 5)

    def test_special_characters_survive_the_round_trip(self):
        f = self.fields(scope='Quotes "and" <angles> & ampersands')
        rec = parse_page(render_page(f, "A < B & C", "<p>x</p>"), "x.html")
        self.assertEqual(rec.scope, 'Quotes "and" <angles> & ampersands')
        self.assertEqual(rec.title, "A < B & C")
        self.assertTrue(rec.intact)

    def test_refs_parse_pinned_unpinned_and_placeholders(self):
        refs = parse_refs("A-1@sha256:ff, B-2 \u2014 none")
        self.assertEqual(refs, [Ref("A-1", "sha256:ff"), Ref("B-2")])
        self.assertEqual(format_refs(refs), "A-1@sha256:ff B-2")

    def test_hash_is_deterministic_and_field_order_free(self):
        a = compute_hash({"scope": "s", "document-id": "i"}, "t", "b")
        b = compute_hash({"document-id": "i", "scope": "s"}, "t", "b")
        self.assertEqual(a, b)

    def test_index_pages_are_recognised_by_name_category_or_kind(self):
        for path, extra in (("index.html", ""), ("spoke/_index.html", ""),
                            ("a.html", '<meta name="mplpb:category" content="Sub-Index">'),
                            ("b.html", '<meta name="mplpb:kind" content="index">')):
            rec = parse_page(f"<html><head>{extra}</head><body></body></html>", path)
            self.assertEqual(rec.kind, "index", path)


class TestAlteration(LedgerTest):
    def test_edited_body_is_quarantined_and_reported(self):
        rec = self.page("Kiln", "Kiln firing schedule", body="Climb slowly.")
        self.edit(rec, "Climb slowly.", "Climb fast.")
        led = L.Ledger(self.root)
        self.assertEqual(led.quarantine_reason(led.records[0]), "altered")
        self.assertEqual(led.servable(), [])
        self.assertIn("C2", self.codes(level="error"))

    def test_edited_depth_is_caught_by_the_hash(self):
        a = self.page("A", "alpha source")
        d = L.derive(self.root, [a.id], title="D", scope="delta digest", prefix="T", when="x")
        self.edit(d, 'mplpb:origin-depth" content="1"', 'mplpb:origin-depth" content="0"')
        self.assertIn("C2", self.codes(level="error"))


if __name__ == "__main__":
    unittest.main()
