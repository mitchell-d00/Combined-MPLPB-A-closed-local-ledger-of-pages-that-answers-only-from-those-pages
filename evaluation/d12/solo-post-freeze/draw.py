"""Seeded FRUS public-source draw for the D12 post-freeze pilot."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import re
from urllib.request import urlopen
from xml.etree import ElementTree as ET
from xml.parsers import expat

TEI = "{http://www.tei-c.org/ns/1.0}"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def get(url):
    with urlopen(url, timeout=30) as response:
        raw = response.read(12_000_001)
        if len(raw) > 12_000_000:
            raise ValueError("Volume exceeds download limit")
        return raw


def text_without_notes(node):
    pieces = [node.text or ""]
    for child in node:
        if child.tag in {TEI + "lb", TEI + "pb"}:
            pieces.append(" ")
        if child.tag != TEI + "note":
            pieces.append(text_without_notes(child))
        pieces.append(child.tail or "")
    return "".join(pieces)


def project(doc):
    content = []
    for node in doc:
        blocks = list(node) if node.tag in {TEI + "opener", TEI + "closer"} else [node]
        for block in blocks:
            normalized = " ".join(text_without_notes(block).split())
            if normalized:
                content.append(normalized)
    return "\n\n".join(content) + "\n"


def exact_spans(raw, wanted):
    parser = expat.ParserCreate()
    stack = []
    offsets = {}

    def start(name, attrs):
        ident = attrs.get("xml:id")
        stack.append((name, ident, parser.CurrentByteIndex))

    def end(name):
        _, ident, begin = stack.pop()
        if ident in wanted and name == "div":
            stop = parser.CurrentByteIndex
            if raw[stop:stop+6] != b"</div>":
                raise ValueError("Unexpected historical document closing tag")
            offsets[ident] = (begin, stop + 6)

    parser.StartElementHandler = start
    parser.EndElementHandler = end
    parser.Parse(raw, True)
    return offsets


def sample(raw, rng):
    docs = {doc.get(XML_ID): doc for doc in ET.fromstring(raw).iter(TEI + "div")
            if doc.get("type") == "document" and doc.get("subtype") == "historical-document"}
    texts = {ident: project(doc) for ident, doc in docs.items()}
    short = {ident for ident, text in texts.items() if 140 <= len(text.split()) <= 680}
    edges = set()
    for ident in short:
        for ref in docs[ident].iter(TEI + "ref"):
            target = ref.get("target", "").removeprefix("#")
            if target in short and target != ident:
                edges.add((ident, target))
    if not edges:
        return None, len(docs), len(short), 0
    chosen = rng.choice(sorted(edges))
    return [(ident, texts[ident]) for ident in chosen], len(docs), len(short), len(edges)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--seed", required=True, type=int)
    args = parser.parse_args()
    root = args.folder
    sources = root / "inputs" / "sources"
    sources.mkdir(parents=True)
    volumes = root / "downloaded-volumes"
    volumes.mkdir()
    archive = (root / "archive-commit.txt").read_text().strip()
    base = f"https://raw.githubusercontent.com/HistoryAtState/frus/{archive}"
    pool = sorted(path for path in (root / "archive-paths.txt").read_text().splitlines()
                  if re.fullmatch(r"volumes/frus(?:193[3-9]|194[0-9]|195[0-9]|196[0-8])[^/]*\.xml", path))
    rng = random.Random(args.seed)
    rng.shuffle(pool)
    attempts, packets = [], []
    for path in pool:
        volume = Path(path).stem
        url = f"{base}/{path}"
        row = {"volume": volume, "url": url, "started_utc": datetime.now(timezone.utc).isoformat()}
        attempts.append(row)
        try:
            raw = get(url)
            (volumes / f"{volume}.xml").write_bytes(raw)
            row.update(volume_sha256=sha(raw), volume_bytes=len(raw))
            pair, documents, short, links = sample(raw, rng)
            row.update(historical_documents=documents, short_documents=short, eligible_links=links)
            if pair is None:
                row["status"] = "no_short_cross_reference"
                continue
            spans = exact_spans(raw, {ident for ident, _ in pair})
            packet = f"P{len(packets)+1:02}"
            items = []
            for letter, (ident, body) in zip("AB", pair):
                record = f"{packet}-{letter}"
                begin, end = spans[ident]
                fragment = raw[begin:end]
                (sources / f"{record}.xml").write_bytes(fragment)
                (sources / f"{record}.txt").write_text(body, encoding="utf-8")
                items.append({"id": record, "archive_id": ident, "volume": volume,
                              "url": f"https://history.state.gov/historicaldocuments/{volume}/{ident}",
                              "volume_url": url, "volume_sha256": sha(raw), "byte_span": [begin, end],
                              "xml_sha256": sha(fragment), "text_sha256": sha(body.encode())})
            row.update(status="selected", packet=packet, pair=[item["archive_id"] for item in items])
            packets.append({"id": packet, "sources": items})
            if len(packets) == 6:
                break
        except (OSError, ValueError, ET.ParseError, expat.ExpatError) as exc:
            row.update(status="failed", error=f"{type(exc).__name__}: {exc}")
    save(root / "draw-receipt.json", {"seed": args.seed, "archive_commit": archive,
         "eligible_volume_count": len(pool), "attempts": attempts, "packets": packets})
    if len(packets) != 6:
        raise SystemExit("Unable to acquire six distinct packets")
    save(root / "inputs" / "sources.json", packets)


if __name__ == "__main__":
    main()
