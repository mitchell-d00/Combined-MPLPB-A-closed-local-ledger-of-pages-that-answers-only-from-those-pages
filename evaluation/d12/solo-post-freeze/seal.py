"""Separate the benchmark inputs from the witnessed source key and seal both."""
import hashlib
import json
from pathlib import Path
import sys

root = Path(sys.argv[1])
questions, gold = [], []
for line in (root / "custody/key-source.tsv").read_text().splitlines():
    ident, family, question, answer, *raw_anchors = line.split("\t")
    packet = ident.rsplit("-", 1)[0]
    anchors = []
    for item in raw_anchors:
        source, quote = item.split("|", 1)
        text = (root / "inputs" / "sources" / f"{source}.txt").read_text()
        if source.rsplit("-", 1)[0] != packet or text.count(quote) != 1:
            raise ValueError(f"{ident}: anchor must occur once in its named source: {quote}")
        start = text.index(quote)
        anchors.append({"source": source, "quote": quote,
                        "text_span": [start, start + len(quote)]})
    questions.append({"id": ident, "packet": packet, "question": question})
    gold.append({"id": ident, "family": family, "expected": answer, "anchors": anchors})
if len({row["id"] for row in questions}) != 24:
    raise ValueError("Expected six packets of four distinct questions")
for path, contents in ((root / "inputs/questions.json", questions), (root / "custody/key.json", gold)):
    with path.open("x") as stream:
        json.dump(contents, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
files = sorted(path for path in (root / "inputs").rglob("*") if path.is_file())
with (root / "inputs.sha256").open("x") as stream:
    for path in files:
        stream.write(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(root)}\n")
