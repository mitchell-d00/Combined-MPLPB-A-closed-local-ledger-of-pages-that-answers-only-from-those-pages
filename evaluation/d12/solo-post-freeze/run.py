"""Run pinned native paths on public questions and source text only."""
import argparse
from collections import Counter
from copy import copy
import hashlib
from html import escape
import json
from pathlib import Path
import re
import shutil
import subprocess
from tempfile import TemporaryDirectory

from mplpb_answers.advanced import advanced_query
from mplpb_answers.passages import PassageIndex
from mplpb_answers.pipeline import answer_query
from mplpb_answers.support import candidate_answer
from mplpb_combined.ledger import Ledger, write
from mplpb_combined.reader import PROFILES
from mplpb_work.investigation import investigate
from mplpb_work.sorter_v2 import sort_directory, verify_graph

BUDGET = (3, 8000)
PROFILE = PROFILES["internal"]
STOP = set("what which who when where why how the did does do can could should would to of by on a an and for in with is was they it he she had has these this that or as at from".split())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def save(path, value):
    with path.open("x", encoding="utf-8") as out:
        json.dump(value, out, ensure_ascii=False, indent=2)
        out.write("\n")


def tokens(text):
    return set(re.findall(r"[^\W_]+", text.casefold())) - STOP


def pack(passages):
    packed, seen, remaining = [], set(), BUDGET[1]
    for passage in passages:
        if passage["id"] not in seen and len(passage["text"]) <= remaining:
            packed.append(passage)
            seen.add(passage["id"])
            remaining -= len(passage["text"])
        if len(packed) == BUDGET[0]:
            break
    return packed


def candidate_ids(graph, question):
    by_id = {node["id"]: node for node in graph["nodes"]}
    query = tokens(question)
    ranked = Counter()
    for edge in graph["edges"]:
        if not edge.get("comparison_only"):
            continue
        nodes = [by_id[item] for item in dict.fromkeys(
            [edge["from"], edge["to"], *edge["evidence_nodes"]]) if item in by_id]
        paths = {node["span"]["path"] for node in nodes}
        paths.update(candidate["path"] for candidate in edge.get("candidates", []))
        if len(paths) < 2:
            continue
        overlap = query & tokens(" ".join(node["span"].get("text", "") for node in nodes))
        if overlap:
            for path in paths:
                ranked[Path(path).stem] += len(overlap)
    return sorted(ranked, key=lambda ident: (-ranked[ident], ident))


def run(packet_dir, output, commit):
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    if revision != commit or subprocess.check_output(["git", "status", "--porcelain"]):
        raise ValueError("Expected a clean checkout at the frozen engine revision")
    packets = load(packet_dir / "sources.json")
    cases = load(packet_dir / "questions.json")
    rows, graphs, records = [], {}, []
    output.mkdir()
    for packet in packets:
        ident = packet["id"]
        with TemporaryDirectory(prefix="mplpb-d12-post-freeze-") as scratch:
            base = Path(scratch)
            original = base / "text"
            original.mkdir()
            root = base / "ledger"
            for source in packet["sources"]:
                source_id = source["id"]
                body = packet_dir / "sources" / f"{source_id}.txt"
                xml = body.with_suffix(".xml")
                if sha(body) != source["text_sha256"] or sha(xml) != source["xml_sha256"]:
                    raise ValueError(f"Source digest differs for {source_id}")
                shutil.copyfile(body, original / body.name)
                html = "".join("<p>" + escape(p) + "</p>"
                               for p in body.read_text().strip().split("\n\n"))
                rec = write(root, doc_id=source_id, title=f"Imported record {source_id}",
                            scope="public historical records", body_html=html, origin="machine",
                            when="2026-11-23T00:00Z")
                records.append({"id": source_id, "path": rec.path, "hash": rec.hash,
                                "projection_sha256": sha(body), "url": source["url"]})
            initial = [(rec.path, rec.hash_actual) for rec in Ledger(root).records]
            graph = sort_directory(original, mode="compare")
            verify_graph(graph, original)
            graphs[ident] = graph
            for case in cases:
                if case["packet"] != ident:
                    continue
                query = case["question"]
                strict = answer_query(root, query, PROFILE).contract
                advanced = advanced_query(root, query, PROFILE)
                if advanced["strict"] != strict:
                    raise ValueError("Advanced changed the standalone strict contract")
                candidate, _ = candidate_answer(root, query, PROFILE)
                investigation = investigate(root, query, profile=PROFILE)
                if investigation["answer_supported"]:
                    raise ValueError("Expert investigation promoted a proof claim")
                index = PassageIndex(root, query, PROFILE)
                terms = tokens(query)
                scored = [(len(terms & tokens(p["text"])), p) for p in index.passages]
                baseline = pack(p for score, p in sorted(scored, key=lambda item: (
                    -item[0], item[1]["source_id"], item[1]["body_start"])) if score)
                native = index.retrieve([query], *BUDGET)["passages"]
                hints = candidate_ids(graph, query)
                if hints:
                    preferred = copy(index)
                    preferred.passages = [passage for passage in index.passages
                                          if passage["source_id"] in hints]
                    preferred.sources = [source for source in index.sources if source["id"] in hints]
                    sorter_first = pack(preferred.retrieve([query], *BUDGET)["passages"] + native)
                else:
                    sorter_first = native
                rows.append({"id": case["id"], "question": query, "strict": strict, "advanced": advanced,
                             "assisted_unconfigured": answer_query(root, query, PROFILE, mode="assisted").contract,
                             "lookup": {"kind": candidate.kind,
                                        "source_ids": [candidate.record.id] if candidate.record
                                        else [record.id for record, _ in candidate.candidates]},
                             "investigation": investigation, "sorter_source_candidates": hints,
                             "discovery": {"term_overlap": baseline, "native": native,
                                           "sorter_first": sorter_first}})
            if initial != [(rec.path, rec.hash_actual) for rec in Ledger(root).records]:
                raise ValueError("Evaluation changed the ledger")
    save(output / "run.json", {"engine": commit, "engine_run_script_sha256": sha(Path(__file__)),
                              "questions_sha256": sha(packet_dir / "questions.json"),
                              "source_manifest_sha256": sha(packet_dir / "sources.json"),
                              "profile": PROFILE.name, "discovery_budget": list(BUDGET),
                              "records": records, "cases": rows})
    save(output / "sorter-graphs.json", graphs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()
    run(args.inputs, args.output, args.commit)
