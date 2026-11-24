"""Lint a .pptx for the 'too AI' layout and wording signals found in the audit.

Usage: python -I lint_deck.py deck.pptx [deck2.pptx ...]

Read-only. Counts top-level shapes plus group children. Thresholds are calibrated on 10 decks (see reference/audit_report.md);
they are warnings, not hard failures. bold_ratio is reported but has no threshold:
it did not separate AI drafts from user-accepted decks.
"""
import re
import sys

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE, MSO_SHAPE_TYPE
from pptx.util import Pt

THRESH = {
    "chars_per_slide_avg": 450,   # user decks: 170-570
    "chars_max_slide": 900,
    "min_font_pt": 10,            # body text below this reads as "too small"
    "small_font_ratio": 0.25,     # share of chars at <=10pt
    "text_cards": 12,             # rounded boxes holding >40 chars (diagram boxes don't count)
    "title_formula_ratio": 0.4,   # titles shaped like "X: Y" or "X - Y"
    "allcaps_labels": 3,
    "this_slide_lines": 1,        # "This slide shows ..." style subtitles
    "source_lines": 2,
}


def walk(shapes):
    for sh in shapes:
        yield sh
        if sh.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from walk(sh.shapes)


def lint(path):
    prs = Presentation(path)
    slides = list(prs.slides)
    n = len(slides)
    chars_per, shapes_per = [], []
    total = small = bold_chars = 0
    min_pt = None
    rounded = 0
    titles = []
    allcaps = this_slide = source = 0
    for s in slides:
        sc = 0
        shs = list(walk(s.shapes))
        shapes_per.append(len(shs))
        for sh in shs:
            if sh.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE and sh.has_text_frame:
                try:
                    if (sh.auto_shape_type == MSO_SHAPE.ROUNDED_RECTANGLE
                            and len(sh.text_frame.text.strip()) > 40):
                        rounded += 1
                except Exception:
                    pass
            if getattr(sh, "has_table", False) and sh.has_table:
                for row in sh.table.rows:
                    for cell in row.cells:
                        # table text is not counted in chars_*: dense tables are fine
                        for p in cell.text_frame.paragraphs:
                            for r in p.runs:
                                if r.font.size is not None:
                                    pt = r.font.size.pt
                                    min_pt = pt if min_pt is None else min(min_pt, pt)
                                    if pt <= 10:
                                        small += len(r.text.strip())
                continue
            if not sh.has_text_frame:
                continue
            for p in sh.text_frame.paragraphs:
                line = "".join(r.text for r in p.runs).strip()
                if not line:
                    continue
                if re.fullmatch(r"[A-Z][A-Z0-9 /&'\-]{3,29}", line):
                    allcaps += 1
                if re.match(r"(?i)this (slide|table|page|chart)\b", line):
                    this_slide += 1
                if re.match(r"(?i)source\s*[:：]", line):
                    source += 1
                for r in p.runs:
                    k = len(r.text.strip())
                    if not k:
                        continue
                    sc += k
                    if r.font.bold:
                        bold_chars += k
                    if r.font.size is not None:
                        pt = r.font.size.pt
                        min_pt = pt if min_pt is None else min(min_pt, pt)
                        if pt <= 10:
                            small += k
        chars_per.append(sc)
        total += sc
        t = s.shapes.title
        if t is not None and t.has_text_frame:
            titles.append(t.text_frame.text.strip())
    formula = sum(1 for t in titles if re.search(r"\S\s*[:：]\s*\S|\s[—–-]\s", t))
    m = {
        "slides": n,
        "chars_per_slide_avg": round(total / n) if n else 0,
        "chars_max_slide": max(chars_per) if chars_per else 0,
        "min_font_pt": min_pt,
        "small_font_ratio": round(small / total, 2) if total else 0,
        "bold_ratio": round(bold_chars / total, 2) if total else 0,
        "text_cards": rounded,
        "shapes_max_slide_info": max(shapes_per) if shapes_per else 0,
        "title_formula_ratio": round(formula / len(titles), 2) if titles else 0,
        "allcaps_labels": allcaps,
        "this_slide_lines": this_slide,
        "source_lines": source,
    }
    warns = []
    for k, lim in THRESH.items():
        v = m[k]
        if v is None:
            continue
        bad = v < lim if k == "min_font_pt" else v > lim
        if bad:
            warns.append(f"{k}={v} (limit {lim})")
    return m, warns


if __name__ == "__main__":
    for f in sys.argv[1:]:
        m, w = lint(f)
        print(f"== {f}")
        print("   " + ", ".join(f"{k}={v}" for k, v in m.items()))
        print(f"   WARN x{len(w)}: " + ("; ".join(w) if w else "none"))
