"""Build and audit offline, sealed, explicitly UNRATIFIED MPLPB reference packs.

No HTTP requests, new dependencies, source truth assertions, or grammar changes.
Every fact is a machine-derived depth-2 page linked to a non-answering,
machine-origin source-index page; only the existing lab profile can serve it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit

from mplpb_combined.ledger import Ledger, write
from mplpb_combined.reader import PROFILES
from mplpb_answers.support import supported_answer, code_pins

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "reference_corpus/catalog.v1.json"
PROBES = ROOT / "reference_corpus/probes.v1.json"
RELEASES = ("0.0.0", "0.1.0", "0.2.0", "0.3.0")
APPROVED_HOSTS = frozenset({
    "owl.purdue.edu", "en-word.net", "www.nist.gov", "science.nasa.gov",
    "www.usgs.gov", "www.noaa.gov", "www.archives.gov",
})
ALLOWED_DOMAINS = frozenset({"language", "measurements", "astronomy", "earth", "civics"})
DESCRIPTION = re.compile(r"^The ([a-z0-9 -]{2,110}) is ([^\n]{1,220})\.$")
SOURCE_KEYS = {"id", "publisher", "url", "title", "anchor", "domain",
               "review_status", "source_bytes_pinned"}
FACT_KEYS = {"id", "subject", "value", "source", "stage", "relation",
             "question", "statement", "status"}
UNSAFE_VALUE = re.compile(
    r'\b(?:not|never|unknown|unrecorded|maybe|perhaps|possibly|probably|'
    r'apparently|reportedly|allegedly|likely|may|if|unless|might|could|'
    r'should|would|either|or)\b|["“”;]', re.I)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    probes = json.loads(PROBES.read_text(encoding="utf-8"))
    if catalog.get("schema") != "mplpb-reference-v1" or probes.get("schema") != "mplpb-reference-probes-v1":
        raise ValueError("Unknown catalogue or probe schema")
    return catalog, probes


def validate_catalog(catalog, probes):
    """Fail before writing any current page. Validate eligibility, not world truth."""
    faults = []
    sources, facts = catalog["sources"], catalog["facts"]
    by_source, ids, scopes, questions = {}, set(), set(), set()
    for source in sources:
        if not SOURCE_KEYS <= set(source):
            faults.append("Missing provenance keys in source "+str(source.get("id")))
            continue
        key = source["id"]
        url = urlsplit(source["url"])
        if key in by_source:
            faults.append("Duplicate source ID: "+key)
        by_source[key] = source
        if url.scheme != "https" or url.hostname not in APPROVED_HOSTS or url.username or url.password:
            faults.append("Source host or URL not whitelisted: "+key)
        if not source["publisher"] or not source["anchor"] or len(source["anchor"]) < 8:
            faults.append("Missing attributable source anchor: "+key)
        if source["domain"] not in ALLOWED_DOMAINS:
            faults.append("Unknown domain: "+key)
        if source["source_bytes_pinned"] is not False:
            faults.append("Claims of source-byte attestation without vendored original: "+key)
    for fact in facts:
        if not FACT_KEYS <= set(fact):
            faults.append("Missing fact fields: "+str(fact.get("id")))
            continue
        fid, subject, question = fact["id"], fact["subject"], fact["question"]
        if fid in ids or not re.fullmatch(r"REF-\d{4}", fid):
            faults.append("Duplicate/invalid fact ID: "+fid)
        ids.add(fid)
        norm_scope = subject.casefold().strip()
        if norm_scope in scopes or not re.fullmatch(r"[a-z0-9][a-z0-9 -]{1,110}", subject):
            faults.append("Duplicate/invalid narrow scope: "+subject)
        scopes.add(norm_scope)
        if question in questions or question != "What is "+subject+"?":
            faults.append("Duplicate or noncanonical when-to-use: "+question)
        questions.add(question)
        if fact["source"] not in by_source or fact["stage"] not in (1, 2, 3):
            faults.append("Missing source or release stage: "+fid)
        if fact["relation"] != "description" or fact["status"] != "machine_draft_unratified":
            faults.append("Unapproved relation or ratification claim: "+fid)
        m = DESCRIPTION.fullmatch(fact["statement"])
        if not m or m[1].casefold() != subject.casefold() or m[2] != fact["value"]:
            faults.append("Fact is not an exact finite-grammar description: "+fid)
        if UNSAFE_VALUE.search(fact["value"]):
            faults.append("Unsafe or conditional source value: "+fid)
    expected = {f["id"]: f for f in facts}
    if len(probes["probes"]) != len({p["id"] for p in probes["probes"]}):
        faults.append("Duplicate held-out probe ID")
    positive = [p for p in probes["probes"] if p["answerable"]]
    negative = [p for p in probes["probes"] if not p["answerable"]]
    if len(positive) != len(facts) or not negative:
        faults.append("Expected exactly one positive probe per fact and explicit negatives")
    for p in positive:
        if p["doc"] not in expected:
            faults.append("Positive probe with absent fact: "+p["id"])
            continue
        f = expected[p["doc"]]
        if p["first_release"] != f["stage"]:
            faults.append("Incorrect preregistered release stage: "+p["id"])
        if p["answer"] != f["statement"] and not p.get("answer_override_reviewed"):
            # Freeze first, revise catalog with an explicit audited pre-release
            # amendment; no automatic gold adaptation to corpus content.
            faults.append("Probe quote not pinned to current finite-grammar fact: "+p["id"])
    if faults:
        raise ValueError("Corpus admission rejected:\n- "+"\n- ".join(faults))
    return {"sources": len(sources), "facts": len(facts), "positive": len(positive),
            "negative": len(negative), "profile": "lab",
            "external_bytes_verified": False, "human_ratified": False}


def _source_id(catalog, key):
    for n, src in enumerate(catalog["sources"], 1):
        if src["id"] == key:
            return "SRC-"+str(n).zfill(4)
    raise KeyError(key)


def build(root, catalog, version):
    """Release snapshots are cumulative, deterministic, and never rewritten in place."""
    if version not in RELEASES:
        raise ValueError("Unknown corpus version "+version)
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    if any(root.iterdir()):
        raise ValueError("Build destination must be an empty directory; never silently update pages")
    max_stage = RELEASES.index(version)
    selected = [f for f in catalog["facts"] if f["stage"] <= max_stage]
    origins = sorted({f["source"] for f in selected})
    # These are non-answering provenance roots. Source metadata is not
    # misrepresented as publisher-authored, publisher-sealed source bytes.
    for src in catalog["sources"]:
        if src["id"] not in origins:
            continue
        sid = _source_id(catalog, src["id"])
        write(
            root, doc_id=sid, kind="source",
            title="Local source citation "+src["id"],
            scope="source citation record "+src["id"],
            when_to_use="Provenance and lineage only; not evidence text",
            body=("Attribution: "+src["publisher"]+"\n"
                  "Citation URL: "+src["url"]+"\n"
                  "Topic anchor: "+src["anchor"]+"\n"
                  "Upstream bytes pinned: no\n"
                  "Human ratification: none\n"
                  "Classification: machine-built provenance record; not upstream source text."),
            origin="machine", owner="MPLPB machine corpus builder",
            source_authorship="unknown", external="no", when="2026-11-01T00:00Z")
    for fact in selected:
        write(
            root, doc_id=fact["id"], title="Fact: "+fact["subject"],
            scope=fact["subject"], when_to_use=fact["question"],
            body=fact["statement"], origin="machine",
            derived_from=[_source_id(catalog, fact["source"])],
            owner="MPLPB machine corpus builder",
            source_authorship="declared-machine", external="no",
            when="2026-11-01T00:00Z")
    return selected


def validate_ledger(root, catalog, selected):
    ledger = Ledger(root)
    findings = ledger.findings()
    errors = [str(f) for f in findings if f.level == "error"]
    servable = ledger.servable()
    by_id = {f["id"]: f for f in selected}
    fact_servable = [r for r in servable if r.id in by_id]
    source_records = [r for r in servable if r.kind == 'source']
    if len(fact_servable) != len(selected):
        errors.append("Servable fact count differs from selected unique owners")
    if len(servable) != len(selected) + len(source_records):
        errors.append("Unexpected servable record kind in release")
    source_ids = {_source_id(catalog, x['id']) for x in catalog['sources']}
    for rec in source_records:
        if rec.id not in source_ids or not rec.intact or rec.origin != 'machine' or ledger.depth(rec) != 1:
            errors.append("Invalid provenance-source record: "+rec.id)
    scopes, questions = set(), set()
    for record in fact_servable:
        fact = by_id[record.id]
        if record.scope.casefold() in scopes or record.when_to_use.casefold() in questions:
            errors.append("Overlapping exact scope / declared question: "+record.id)
        scopes.add(record.scope.casefold())
        questions.add(record.when_to_use.casefold())
        if record.scope != fact["subject"] or record.when_to_use != fact["question"]:
            errors.append("Wrong declared scope or when-to-use: "+record.id)
        if (not record.intact or record.origin != "machine" or
                record.depth_declared != 2 or ledger.depth(record) != 2 or
                record.ratified_by or record.fields.get("external") != "no"):
            errors.append("Incorrect seal, lineage, origin, depth, ratification or delivery: "+record.id)
        if len(record.derived_from) != 1:
            errors.append("Fact has missing or multiple provenance roots: "+record.id)
        else:
            ref = record.derived_from[0]
            basis = ledger.resolve(ref)
            if (not basis or ref.hash != basis.hash_actual or basis.kind != "source"
                    or basis.origin != "machine" or basis.depth_declared != 1):
                errors.append("Fact is not pinned to a valid source citation record: "+record.id)
    if errors:
        raise AssertionError("Current-page admission failed:\n- "+"\n- ".join(errors))
    return {"intact_servable": len(fact_servable), "quarantined": len(ledger.quarantined()),
            "source_citation_pages": len(source_records),
            "errors": 0, "depth": 2, "ratified": 0,
            "not_for_default_internal_profile": True}


def observe(root, probe):
    answer = supported_answer(root, probe["question"], PROFILES["lab"])
    item = answer.record
    ret = answer.kind == "return"
    correct = (ret and item is not None and item.id == probe["doc"]
               and answer.text == probe["answer"]
               and item.intact and item.origin == "machine"
               and answer.depth == 2
               and answer.support.get("status") == "supported")
    return {
        "id": probe["id"], "question": probe["question"],
        "expected_id": probe.get("doc"), "expected_answer": probe.get("answer"),
        "kind": answer.kind, "correct_supported": bool(correct),
        "quote": answer.text, "document_id": item.id if item else None,
        "document_sha256": item.hash if item else None,
        "depth": answer.depth if item else None,
        "origin": item.origin if item else None,
        "derived_from": [dict(id=ref.id, hash=ref.hash)
                         for ref in item.derived_from] if item else [],
        "reason": answer.reason,
    }


def score(root, probes):
    rows = [observe(root, q) for q in probes]
    positive = [x for x, q in zip(rows, probes) if q["answerable"]]
    negative = [x for x, q in zip(rows, probes) if not q["answerable"]]
    correct = {x["id"] for x in positive if x["correct_supported"]}
    wrong = [x["id"] for x in rows if x["kind"] == "return" and not x["correct_supported"]]
    expected_refusals = sum(x["kind"] == "not_in_corpus" for x in negative)
    ambiguous = [x["id"] for x in rows if x["kind"] == "ambiguous"]
    return rows, {
        "answerable_total": len(positive), "correct_supported": len(correct),
        "answerable_coverage": round(len(correct) / len(positive), 6),
        "correct_refusals": expected_refusals,
        "negative_total": len(negative),
        "ambiguous": len(ambiguous), "ambiguous_ids": ambiguous,
        "wrong_returns": len(wrong), "wrong_ids": wrong,
        "unnecessary_refusals": sum(x["kind"] == "not_in_corpus" for x in positive),
    }


def evaluate(out_dir, catalog, spec):
    out_dir = Path(out_dir)
    if out_dir.exists() and any(out_dir.iterdir()):
        raise ValueError("Release output directory must be empty; never overwrite")
    out_dir.mkdir(parents=True, exist_ok=True)
    checks = validate_catalog(catalog, spec)
    all_probes = spec["probes"]
    reports, old = [], {}
    for version in RELEASES:
        root = out_dir / ("v"+version) / "ledger"
        selected = build(root, catalog, version)
        integrity = validate_ledger(root, catalog, selected)
        rows, metrics = score(root, all_probes)
        this = {x["id"]: x for x in rows}
        newly_supported = []
        new_ambiguities = []
        for p in all_probes:
            before = old.get(p["id"], {"kind": "not_in_corpus"})
            after = this[p["id"]]
            if before["kind"] == "not_in_corpus" and after["correct_supported"]:
                newly_supported.append({"probe": p["id"],
                                        "page_id": after["document_id"],
                                        "page_sha256": after["document_sha256"],
                                        "basis": after["derived_from"],
                                        "question": p["question"]})
            if before["kind"] != "ambiguous" and after["kind"] == "ambiguous":
                new_ambiguities.append({"probe": p["id"], "new_kind": "ambiguous"})
        report = {"version": version, "profile": "lab",
                  "snapshot_kind": "sealed_machine_unratified",
                  "catalog_sha256": sha256(CATALOG), "probes_sha256": sha256(PROBES),
                  "metrics": metrics, "integrity": integrity,
                  "delta": {"refusal_to_supported": newly_supported,
                            "new_ambiguities": new_ambiguities},
                  "rows": rows}
        target = out_dir / ("v"+version) / "audit.json"
        target.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
        reports.append(report)
        old = this
    manifest = {
        "schema": "mplpb-reference-release-audit-v1",
        "manifest_as_of": "2026-11-01",
        "profile_required_for_unratified_fact_pages": "lab",
        "authority": "machine-derived, unratified, cited; not independently source-byte verified",
        "source_integrity_vs_factual_accuracy": "Local SHA-256 and lineage verify byte integrity only; not independent factual correctness, publisher authorship, or current online agreement.",
        "catalog_and_probes": {"catalog": sha256(CATALOG), "probes": sha256(PROBES)},
        "admission": checks,
        "engine_code_sha256": code_pins(),
        "versions": [{k: report[k] for k in ("version", "profile", "metrics", "integrity", "delta")}
                     for report in reports],
    }
    (out_dir / "release-audit.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    if any(r["metrics"]["wrong_returns"] or r["metrics"]["ambiguous"]
           or r["integrity"]["errors"] for r in reports):
        raise AssertionError("Wrong/ambiguous returns or invalid current page: refuse release")
    expected = [0, 23, 48, 73]
    measured = [r["metrics"]["correct_supported"] for r in reports]
    if measured != expected:
        raise AssertionError("Regression in staged answer coverage; expected "
                             +str(expected)+" actual "+str(measured)
                             +"; inspect release audit rows")
    if [len(r["delta"]["refusal_to_supported"]) for r in reports] != [0, 23, 25, 25]:
        raise AssertionError("Refusal to supported delta mismatch")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True,
                        help="Must be a new empty output directory; never overwrite historical releases")
    args = parser.parse_args()
    catalog, probes = load()
    data = evaluate(args.output, catalog, probes)
    print(json.dumps([{"version": x["version"],
                       "supported": x["metrics"]["correct_supported"],
                       "ambiguous": x["metrics"]["ambiguous"],
                       "wrong": x["metrics"]["wrong_returns"],
                       "closed_refusals": len(x["delta"]["refusal_to_supported"])}
                      for x in data["versions"]], indent=2))


if __name__ == "__main__":
    main()
