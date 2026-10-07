#!/usr/bin/env python3
"""Render docs/Combined_MPLPB.md as .txt and .pdf.

    python3 tools/make_paper.py            # both
    python3 tools/make_paper.py --txt      # text only; needs nothing installed

The Markdown file is the source of record. The text rendering uses only the
standard library. The PDF rendering needs reportlab, which is a documentation
dependency: the mplpb_combined package never imports it.

The parser handles the subset of Markdown the paper is written in: headings,
paragraphs, bullet and numbered lists, fenced code, pipe tables, rules, and
inline bold, italic and code.
"""
import re
import sys
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
SRC = HERE / "docs" / "Combined_MPLPB.md"
WIDTH = 78


# ---------------------------------------------------------------- parsing --

def parse(md: str):
    """Return a list of blocks: (kind, payload)."""
    blocks, lines, i = [], md.splitlines(), 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
        elif ln.startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            blocks.append(("code", lines[i + 1:j]))
            i = j + 1
        elif re.match(r"^#{1,4} ", ln):
            level = len(ln) - len(ln.lstrip("#"))
            blocks.append((f"h{level}", ln[level:].strip()))
            i += 1
        elif ln.strip() == "---":
            blocks.append(("rule", None))
            i += 1
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            blocks.append(("table", rows))
        elif re.match(r"^(- |\d+\. )", ln):
            items, ordered = [], bool(re.match(r"^\d+\. ", ln))
            while i < len(lines) and re.match(r"^(- |\d+\. )", lines[i]):
                item = re.sub(r"^(- |\d+\. )", "", lines[i])
                i += 1
                while i < len(lines) and lines[i].startswith("  ") and lines[i].strip():
                    item += " " + lines[i].strip()
                    i += 1
                items.append(item)
            blocks.append(("ol" if ordered else "ul", items))
        else:
            para = [ln.strip()]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(
                    r"^(#{1,4} |```|\||- |\d+\. |---$)", lines[i]):
                para.append(lines[i].strip())
                i += 1
            blocks.append(("p", " ".join(para)))
    return blocks


def plain(s: str) -> str:
    s = re.sub(r"`([^`]*)`", r"\1", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
    s = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"\1", s)
    return s


# ------------------------------------------------------------------- text --

def text_table(rows):
    rows = [[plain(c) for c in r] for r in rows]
    n = len(rows[0])
    natural = [max(len(r[c]) for r in rows) for c in range(n)]
    budget = WIDTH - 2 * (n - 1)
    widths = natural[:]
    while sum(widths) > budget:
        k = widths.index(max(widths))
        widths[k] -= 1
    out = []
    for ri, r in enumerate(rows):
        wrapped = [textwrap.wrap(r[c], widths[c]) or [""] for c in range(n)]
        for k in range(max(len(w) for w in wrapped)):
            out.append("  ".join((w[k] if k < len(w) else "").ljust(widths[c])
                                 for c, w in enumerate(wrapped)).rstrip())
        if ri == 0:
            out.append("  ".join("-" * widths[c] for c in range(n)))
        elif len(rows) > 2 and max(len(w) for w in wrapped) > 1:
            out.append("")
    while out and not out[-1]:
        out.pop()
    return out


def to_text(blocks) -> str:
    out = []
    for kind, data in blocks:
        if kind == "h1":
            t = plain(data).upper()
            out += [t, "=" * len(t), ""]
        elif kind == "h2":
            t = plain(data)
            out += ["", t, "-" * len(t), ""]
        elif kind in ("h3", "h4"):
            out += textwrap.wrap(plain(data), WIDTH) + [""]
        elif kind == "rule":
            out += ["-" * WIDTH, ""]
        elif kind == "p":
            out += textwrap.wrap(plain(data), WIDTH) + [""]
        elif kind == "code":
            out += ["    " + ln for ln in data] + [""]
        elif kind in ("ul", "ol"):
            for n, item in enumerate(data, 1):
                lead = f"{n}. " if kind == "ol" else "- "
                out += textwrap.wrap(plain(item), WIDTH, initial_indent=lead,
                                     subsequent_indent=" " * len(lead))
            out.append("")
        elif kind == "table":
            out += text_table(data) + [""]
    return "\n".join(out).rstrip() + "\n"


# -------------------------------------------------------------------- pdf --

def rl_inline(s: str) -> str:
    """Markdown inline marks to reportlab's paragraph markup."""
    parts = re.split(r"(`[^`]*`)", s)
    out = []
    for part in parts:
        esc = part.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if part.startswith("`") and part.endswith("`") and len(part) >= 2:
            out.append(f'<font face="Courier" size="8.5">{esc[1:-1]}</font>')
        else:
            esc = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", esc)
            esc = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<i>\1</i>", esc)
            out.append(esc)
    return "".join(out)


def to_pdf(blocks, target: Path) -> None:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        HRFlowable, ListFlowable, ListItem, Paragraph, Preformatted, SimpleDocTemplate,
        Spacer, Table, TableStyle,
    )

    ink = colors.HexColor("#1a1a1a")
    grey = colors.HexColor("#666666")
    rule = colors.HexColor("#bbbbbb")
    base = dict(fontName="Times-Roman", fontSize=10.5, leading=14.5, textColor=ink,
                alignment=TA_LEFT)
    S = {
        "p": ParagraphStyle("p", spaceAfter=7, **base),
        "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=22, leading=26,
                             spaceAfter=4, textColor=ink),
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=14, leading=18,
                             spaceBefore=14, spaceAfter=7, textColor=ink, keepWithNext=1),
        "h3": ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=11, leading=15,
                             spaceBefore=8, spaceAfter=5, textColor=ink, keepWithNext=1),
        "sub": ParagraphStyle("sub", fontName="Helvetica", fontSize=11.5, leading=15,
                              spaceAfter=12, textColor=grey),
        "li": ParagraphStyle("li", spaceAfter=3, **base),
        "cell": ParagraphStyle("cell", fontName="Times-Roman", fontSize=9, leading=11.5,
                               textColor=ink),
        "head": ParagraphStyle("head", fontName="Helvetica-Bold", fontSize=8.5, leading=11,
                               textColor=ink),
        "code": ParagraphStyle("code", fontName="Courier", fontSize=8, leading=10.4,
                               textColor=ink, leftIndent=8, spaceAfter=8, spaceBefore=2),
    }
    doc = SimpleDocTemplate(str(target), pagesize=letter, leftMargin=1.05 * inch,
                            rightMargin=1.05 * inch, topMargin=0.95 * inch,
                            bottomMargin=0.95 * inch, title="Combined MPLPB",
                            author="Mitchell D. McPhetridge",
                            subject="MPLPB-COMBINED-017 v3")
    avail = letter[0] - 2.1 * inch
    story, seen_h1, first_h3 = [], False, True

    for kind, data in blocks:
        if kind == "h1":
            story.append(Paragraph(rl_inline(data), S["h1"]))
            seen_h1 = True
        elif kind == "h2":
            story.append(Paragraph(rl_inline(data), S["h2"]))
        elif kind in ("h3", "h4"):
            style = S["sub"] if (seen_h1 and first_h3) else S["h3"]
            first_h3 = False
            story.append(Paragraph(rl_inline(data), style))
        elif kind == "rule":
            story.append(Spacer(1, 4))
            story.append(HRFlowable(width="100%", thickness=0.5, color=rule))
            story.append(Spacer(1, 6))
        elif kind == "p":
            story.append(Paragraph(rl_inline(data), S["p"]))
        elif kind == "code":
            story.append(Preformatted("\n".join(data), S["code"]))
        elif kind in ("ul", "ol"):
            items = [ListItem(Paragraph(rl_inline(x), S["li"]), leftIndent=16) for x in data]
            story.append(ListFlowable(items, bulletType="1" if kind == "ol" else "bullet",
                                      start=None if kind == "ol" else "\u2022",
                                      bulletFontSize=9, leftIndent=16))
            story.append(Spacer(1, 5))
        elif kind == "table":
            n = len(data[0])
            longest = [max(len(plain(r[c])) for r in data) for c in range(n)]
            weights = [min(max(w + 2, 11), 46) for w in longest]
            widths = [avail * w / sum(weights) for w in weights]
            rows = [[Paragraph(rl_inline(c), S["head"] if ri == 0 else S["cell"]) for c in r]
                    for ri, r in enumerate(data)]
            t = Table(rows, colWidths=widths, repeatRows=1)
            t.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LINEBELOW", (0, 0), (-1, 0), 0.8, ink),
                ("LINEBELOW", (0, 1), (-1, -1), 0.25, rule),
                ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.append(t)
            story.append(Spacer(1, 10))

    def furniture(canvas, d):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(grey)
        canvas.drawString(1.05 * inch, 0.6 * inch, "Combined MPLPB \u00b7 MPLPB-COMBINED-017 v3")
        canvas.drawRightString(letter[0] - 1.05 * inch, 0.6 * inch, str(d.page))
        canvas.restoreState()

    doc.build(story, onFirstPage=furniture, onLaterPages=furniture)


def main(argv) -> int:
    blocks = parse(SRC.read_text(encoding="utf-8"))
    txt = SRC.with_suffix(".txt")
    txt.write_text(to_text(blocks), encoding="utf-8")
    print("wrote", txt.relative_to(HERE))
    if "--txt" in argv:
        return 0
    try:
        import reportlab  # noqa: F401
    except ImportError:
        print("reportlab is not installed; the PDF was not built (pip install reportlab)")
        return 1
    pdf = SRC.with_suffix(".pdf")
    to_pdf(blocks, pdf)
    print("wrote", pdf.relative_to(HERE))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
