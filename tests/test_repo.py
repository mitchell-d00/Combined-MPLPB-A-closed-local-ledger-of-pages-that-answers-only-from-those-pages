"""Tests of the repository as shipped: CLI, examples, kill test, dependency surface."""
import ast
import contextlib
import hashlib
import inspect
import io
import json
import sys
import unittest
from pathlib import Path

from mplpb_combined import __main__ as cli, killtest, ledger as L, reader as R
from tests.support import LedgerTest

REPO = Path(__file__).resolve().parent.parent
STUDIO = REPO / "examples" / "studio"
PROBES = REPO / "killtest" / "probes.json"

ALLOWED_IMPORTS = {
    "__future__", "argparse", "collections", "contextlib", "dataclasses", "datetime",
    "hashlib", "html", "json", "math", "os", "pathlib", "re", "sys", "tempfile", "time", "typing",
}


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = cli.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class TestDependencySurface(unittest.TestCase):
    def test_the_package_imports_only_a_short_list_of_standard_modules(self):
        for path in sorted((REPO / "mplpb_combined").glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [a.name.split(".")[0] for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0:
                    names = [(node.module or "").split(".")[0]]
                for n in names:
                    self.assertIn(n, ALLOWED_IMPORTS, f"{path.name} imports {n}")

    def test_nothing_that_could_reach_a_network_or_run_a_model_is_imported(self):
        banned = {"socket", "urllib", "http", "ssl", "ftplib", "smtplib", "subprocess",
                  "sqlite3", "requests", "asyncio"}
        self.assertFalse(banned & ALLOWED_IMPORTS)


class TestCli(LedgerTest):
    def test_exit_codes_tell_the_three_cases_apart(self):
        r = str(self.root)
        self.assertEqual(run("write", r, "--title", "Bisque", "--scope", "Bisque firing schedule",
                             "--body", "Climb slowly.", "--prefix", "K")[0], 0)
        run("write", r, "--title", "Glaze", "--scope", "Glaze firing schedule", "--prefix", "K")
        self.assertEqual(run("ask", r, "bisque")[0], 0)
        self.assertEqual(run("ask", r, "firing schedule")[0], 2)
        self.assertEqual(run("ask", r, "capital of France")[0], 3)

    def test_revise_derive_ratify_history_and_validate(self):
        r = str(self.root)
        run("write", r, "--title", "Bisque", "--scope", "Bisque schedule", "--prefix", "K")
        self.assertEqual(run("revise", r, "K-0001", "--body", "v2")[0], 0)
        self.assertEqual(run("derive", r, "--from", "K-0002", "--title", "Digest",
                             "--scope", "Weekly digest", "--prefix", "K")[0], 0)
        code, out, _ = run("ask", r, "weekly digest", "--profile", "external")
        self.assertEqual(code, 3)
        self.assertIn("withheld by profile external", out)
        self.assertEqual(run("ratify", r, "K-0003", "--who", "Dana Reviewer")[0], 0)
        self.assertEqual(run("ask", r, "weekly digest", "--profile", "external")[0], 0)
        code, out, _ = run("history", r, "K-0001")
        self.assertEqual(len(out.strip().splitlines()), 2)
        self.assertEqual(run("validate", r, "--strict")[0], 0)

    def test_a_refused_write_exits_one_and_says_why(self):
        code, _, err = run("revise", str(self.root), "NOPE-1", "--body", "x")
        self.assertEqual(code, 1)
        self.assertIn("refused", err)

    def test_validate_exits_one_on_an_altered_page(self):
        rec = self.page("A", "alpha", body="original")
        self.edit(rec, "original", "changed")
        code, out, _ = run("validate", str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("C2", out)

    def test_json_answer_carries_the_hash_of_what_was_returned(self):
        rec = self.page("A", "alpha")
        _, out, _ = run("ask", str(self.root), "alpha", "--json")
        d = json.loads(out)
        self.assertEqual((d["kind"], d["id"], d["hash"]), ("return", rec.id, rec.hash))

    def test_show_reads_a_retired_page_and_says_it_is_retired(self):
        a = self.page("A", "alpha", body="old words")
        L.revise(self.root, a.id, body="new words", when="x")
        _, out, _ = run("show", str(self.root), a.id)
        self.assertIn("old words", out)
        self.assertIn("RETIRED", out)


@unittest.skipUnless(STUDIO.is_dir(), "examples not built; run tools/build_examples.py")
class TestShippedExamples(unittest.TestCase):
    def test_every_example_corpus_validates_clean_and_strict(self):
        for name in ("studio", "spec", "hub"):
            found = L.Ledger(REPO / "examples" / name).findings()
            self.assertEqual([str(f) for f in found], [], name)

    def test_the_examples_rebuild_to_the_same_bytes(self):
        sys.path.insert(0, str(REPO / "tools"))
        before = {p.relative_to(REPO).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in sorted((REPO / "examples").rglob("*"))
                  if p.is_file() and p.relative_to(REPO / "examples").parts[0] in {"studio", "spec", "hub"}}
        import build_examples
        # Rebuild in isolation: other UI tests can still read the shipped corpora.
        import tempfile
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            with patch.object(build_examples, 'HERE', target):
                for build in (build_examples.build_studio, build_examples.build_spec,
                              build_examples.build_hub):
                    build()
            after = {p.relative_to(target).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in sorted((target / "examples").rglob("*")) if p.is_file()}
        self.assertEqual(before, after)

    def test_the_spec_corpus_answers_questions_about_its_own_format(self):
        a = R.answer(REPO / "examples" / "spec", "two pages claim the same question")
        self.assertEqual((a.kind, a.record.title), (R.RETURN, "The answer rule"))

    def test_the_hub_routes_into_both_corpora(self):
        hub = REPO / "examples" / "hub"
        self.assertEqual(R.answer(hub, "wedging").record.id, "STUDIO-0015")
        self.assertEqual(R.answer(hub, "validation checks").record.id, "SPEC-0008")

    def test_retired_studio_pages_are_kept_and_never_served(self):
        led = L.Ledger(STUDIO)
        retired = [r for r in led.records if led.effective_status(r) == "retired"]
        self.assertEqual(len(retired), 4)
        served = {r.id for r in led.servable()}
        self.assertFalse(served & {r.id for r in retired})


@unittest.skipUnless(PROBES.exists() and STUDIO.is_dir(), "kill test inputs missing")
class TestKillTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res = killtest.run(STUDIO, PROBES)

    def test_the_probe_file_matches_its_frozen_hash(self):
        self.assertEqual(self.res["probe_hash"], "OK")

    def test_every_probe_is_scored_once_per_arm(self):
        self.assertEqual(self.res["n"], len(json.loads(PROBES.read_text())["probes"]))
        for c in self.res["classes"].values():
            for arm in killtest.ARMS:
                self.assertEqual(sum(c[arm].values()), c["n"])

    def test_the_scorer_has_no_branch_on_probe_or_arm(self):
        src = inspect.getsource(killtest.score)
        for word in ("probe", "arm", "id", "class", "scoped", "stripped"):
            self.assertNotIn(word, src.replace("expect_kind", "").replace("expect_doc", ""))

    def test_the_stripped_arms_never_see_a_declared_field(self):
        pages = killtest.stripped_pages(L.Ledger(STUDIO))
        for text in pages.values():
            self.assertNotIn("mplpb:", text)
            self.assertNotIn("sha256:", text)
        src = inspect.getsource(killtest.run_stripped) + inspect.getsource(killtest.run_top1)
        for word in ("scope", "status", "when_to_use", "depth", "Ledger"):
            self.assertNotIn(word, src)

    def test_stripped_and_scoped_arms_share_one_decision_function(self):
        self.assertIn("decide(", inspect.getsource(killtest.run_stripped))
        self.assertIn("decide(", inspect.getsource(R.answer))

    def test_shipped_results_are_the_results_this_code_produces(self):
        shipped = json.loads((REPO / "killtest" / "results.json").read_text(encoding="utf-8"))
        self.assertEqual(shipped["classes"], self.res["classes"])
        self.assertEqual(shipped["scope_only"], self.res["scope_only"])

    def test_held_out_results_are_shipped_as_they_came_out(self):
        held = REPO / "killtest" / "probes_heldout.json"
        self.assertEqual(killtest.check_hash(held), "OK")
        fresh = killtest.run(STUDIO, held)
        shipped = json.loads((REPO / "killtest" / "results_heldout.json").read_text(encoding="utf-8"))
        self.assertEqual(shipped["classes"], fresh["classes"])
        wrong = sum(c["scoped"]["wrong_return"] for c in fresh["classes"].values())
        self.assertEqual(wrong, 1)        # 3 before not-for; recorded in docs/FIXLOG.md
        self.assertEqual(fresh["not_for_ignored"]["wrong_return"], 3)

    def test_adjacent_results_are_shipped_as_they_came_out(self):
        adj = REPO / "killtest" / "probes_adjacent.json"
        self.assertEqual(killtest.check_hash(adj), "OK")
        fresh = killtest.run(STUDIO, adj)
        shipped = json.loads((REPO / "killtest" / "results_adjacent.json").read_text(encoding="utf-8"))
        self.assertEqual(shipped["classes"], fresh["classes"])
        self.assertEqual(shipped["not_for_ignored"], fresh["not_for_ignored"])
        wrong = sum(c["scoped"]["wrong_return"] for c in fresh["classes"].values())
        self.assertEqual(wrong, 3)        # the field did not close the gap; recorded as run

    def test_the_second_run_is_kept_too(self):
        v2 = json.loads((REPO / "killtest" / "v2" / "results_heldout.json").read_text(encoding="utf-8"))
        self.assertEqual(sum(c["scoped"]["wrong_return"] for c in v2["classes"].values()), 3)

    def test_the_first_run_is_kept_not_overwritten(self):
        v1 = json.loads((REPO / "killtest" / "v1" / "results.json").read_text(encoding="utf-8"))
        tally = {o: sum(c["scoped"][o] for c in v1["classes"].values())
                 for o in killtest.OUTCOMES}
        self.assertEqual(tally, {"correct": 41, "wrong_return": 0, "wrong_refusal": 15})

    def test_the_scoped_reader_made_no_false_return_on_the_first_probe_set(self):
        wrong = sum(c["scoped"]["wrong_return"] for c in self.res["classes"].values())
        self.assertEqual(wrong, 0)


if __name__ == "__main__":
    unittest.main()


class TestDocsAndParts(unittest.TestCase):
    def test_the_text_paper_is_a_fresh_render_of_the_markdown(self):
        sys.path.insert(0, str(REPO / "tools"))
        import make_paper
        md = (REPO / "docs" / "Combined_MPLPB.md").read_text(encoding="utf-8")
        txt = (REPO / "docs" / "Combined_MPLPB.txt").read_text(encoding="utf-8")
        self.assertEqual(make_paper.to_text(make_paper.parse(md)), txt)

    @unittest.skipUnless((REPO / "parts").is_dir(), "parts/ not present")
    def test_example_sites_from_the_earlier_tools_adopt_cleanly(self):
        import shutil
        import tempfile
        sites = ["local-mirror/site", "smart-local/site", "swarm/site/corpus-a",
                 "swarm/site/corpus-b", "networked/Seed"]
        for rel in sites:
            tmp = Path(tempfile.mkdtemp(prefix="mplpb-adopt-"))
            try:
                root = tmp / "site"
                shutil.copytree(REPO / "parts" / rel, root)
                self.assertTrue(L.seal(root, when="2026-01-01T00:00Z"), rel)
                led = L.Ledger(root)
                self.assertEqual([str(f) for f in led.findings() if f.level == "error"], [], rel)
                self.assertTrue(led.servable(), rel)
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
