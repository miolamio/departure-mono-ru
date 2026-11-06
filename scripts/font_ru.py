# /// script
# requires-python = ">=3.10"
# dependencies = ["fonttools==4.68.0", "brotli==1.2.1", "uharfbuzz==0.57.0"]
# ///
"""Build and verify the Russian proof from the pinned upstream OTF.

Run: uv run scripts/font_ru.py build|check|proof
This is a binary patch, not a replacement for the author's Glyphs sources.
"""

import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import unicodedata

from fontTools.otlLib.builder import buildAnchor
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables
import uharfbuzz as hb


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public/assets/DepartureMono-Regular.otf"
SOURCE_HASH = "4d53f663155cf8bf7ffc8e688776e719625f7bbb80a8d90073438b249261a2e0"
OUTPUT = ROOT / "fonts/departure-mono-ru"
PROOFS = ROOT / "docs/proofs"
FAMILY = "Departure Mono RU"
PS_NAME = "DepartureMonoRU-Regular"
UPPER = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
RUSSIAN = UPPER + UPPER.lower()
VOWELS = "АЕЁИОУЫЭЮЯаеёиоуыэюя"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def load_source():
    require(sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_HASH,
            "Upstream OTF changed: review the patch before updating its SHA-256.")
    return TTFont(SOURCE, recalcTimestamp=False)


def bounds(font, name):
    glyphs = font.getGlyphSet()
    pen = BoundsPen(glyphs)
    glyphs[name].draw(pen)
    return pen.bounds


def outline(font, name):
    pen = RecordingPen()
    font.getGlyphSet()[name].draw(pen)
    return pen.value


def sfnt_bytes(font):
    stream = BytesIO()
    flavor = font.flavor
    try:
        font.flavor = None
        font.save(stream)
    finally:
        font.flavor = flavor
    return stream.getvalue()


def shape(font, text, features=None, language="ru"):
    """Return glyph origins in font units, including shaping and mark placement."""
    hb_font = hb.Font(hb.Face(sfnt_bytes(font)))
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    buffer.language = language
    hb.shape(hb_font, buffer, features or {})
    order = font.getGlyphOrder()
    x = 0
    result = []
    for info, pos in zip(buffer.glyph_infos, buffer.glyph_positions):
        result.append({"glyph": order[info.codepoint], "cluster": info.cluster,
                       "x": x + pos.x_offset, "y": pos.y_offset,
                       "advance": pos.x_advance})
        x += pos.x_advance
    return result


def patch(font):
    cmap = font.getBestCmap()
    lookup = font["GPOS"].table.LookupList.Lookup[0]
    require(lookup.LookupType == 4 and len(lookup.SubTable) == 1,
            "Expected the upstream Cyrillic mark-to-base lookup.")
    subtable = lookup.SubTable[0]
    require(subtable.ClassCount == 2, "Unexpected mark classes.")
    acute = subtable.MarkCoverage.glyphs.index(cmap[0x301])
    require(subtable.MarkArray.MarkRecord[acute].Class == 0,
            "Class 0 must be the above-base marks.")
    records = dict(zip(subtable.BaseCoverage.glyphs, subtable.BaseArray.BaseRecord))
    added = []
    for char in RUSSIAN:
        name = cmap[ord(char)]
        if name in records:
            require(records[name].BaseAnchor[0] is not None,
                    f"Review existing top anchor for {char}.")
            continue
        record = otTables.BaseRecord()
        # Same horizontal anchor as upstream Ё/Й and the combining marks.
        # Use the actual ink top: б/ф extend above the usual lowercase height.
        record.BaseAnchor = [buildAnchor(175, bounds(font, name)[3]), None]
        records[name] = record
        added.append(char)
    require(len(added) == 62, "Expected 62 absent anchors; ЁёЙй already have them.")
    order = font.getReverseGlyphMap()
    names = sorted(records, key=order.__getitem__)
    subtable.BaseCoverage.glyphs = names
    subtable.BaseArray.BaseRecord = [records[name] for name in names]
    subtable.BaseArray.BaseCount = len(names)

    names = {
        1: FAMILY, 2: "Regular", 3: f"1.501;RUProof1;{PS_NAME}",
        4: FAMILY + " Regular", 5: "Version 1.501; RU proof 1; based on upstream 1.500",
        6: PS_NAME, 10: "Unofficial Russian mark-positioning proof based on Departure Mono 1.500. "
                       "Original typeface design: Helena Zhang. See bundled FONTLOG.md.",
        16: FAMILY, 17: "Regular",
    }
    for name in font["name"].names:
        if name.nameID in names:
            name.string = names[name.nameID].encode(name.getEncoding())
    font["head"].fontRevision = 1.501
    cff = font["CFF "].cff
    cff.fontNames = [PS_NAME]
    top = cff.topDictIndex[0]
    top.FamilyName = FAMILY
    top.FullName = FAMILY + " Regular"
    top.version = "1.501"
    return added


def build():
    font = load_source()
    added = patch(font)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for flavor in (None, "woff", "woff2"):
        font.flavor = flavor
        font.save(OUTPUT / f"{PS_NAME}.{flavor or 'otf'}")
    (OUTPUT / "OFL.txt").write_bytes((ROOT / "public/assets/LICENSE").read_bytes())
    print(f"Built OTF, WOFF, WOFF2; added {len(added)} top anchors; preserved all outlines.")


def validate_font(source, font):
    require(source.getBestCmap() == font.getBestCmap(), "Character coverage changed.")
    require(source.getGlyphOrder() == font.getGlyphOrder(), "Glyph order changed.")
    require(source["hmtx"].metrics == font["hmtx"].metrics, "Advance widths changed.")
    require(font["name"].getDebugName(1) == FAMILY, "Family name was not updated.")
    require(font["CFF "].cff.fontNames == [PS_NAME], "CFF PostScript name mismatch.")
    require(font["name"].getDebugName(0) == source["name"].getDebugName(0),
            "Original copyright was altered.")
    # fontTools may compress repeated hmtx advance entries (2 records -> 1).
    # This changes hhea.numberOfHMetrics, not any actual metric.
    for field in ("ascent", "descent", "lineGap", "advanceWidthMax", "minLeftSideBearing",
                  "minRightSideBearing", "xMaxExtent", "caretSlopeRise", "caretSlopeRun"):
        require(getattr(source["hhea"], field) == getattr(font["hhea"], field),
                f"Vertical/horizontal metric changed: {field}.")
    for tag in source.keys():
        if tag not in {"GlyphOrder", "head", "name", "CFF ", "GPOS", "hmtx", "hhea"}:
            require(source.getTableData(tag) == font.getTableData(tag), f"Unexpected {tag} change.")
    for name in source.getGlyphOrder():
        require(outline(source, name) == outline(font, name), f"Changed outline: {name}.")
    cmap = font.getBestCmap()
    for char in RUSSIAN:
        require(ord(char) in cmap, f"Missing {char}.")
        name = cmap[ord(char)]
        require(font["hmtx"][name][0] == 350, f"Non-monospace {char}.")
        for operation, points in outline(font, name):
            require(operation in {"moveTo", "lineTo", "closePath"}, f"Non-pixel contour: {char}.")
            require(all(value % 50 == 0 for point in points for value in point),
                    f"Off-grid outline: {char}.")
        shaped = shape(font, char + "\u0301")
        if len(shaped) == 1:
            # Г/К + acute canonically compose to the existing Ѓ/Ќ glyphs.
            require(unicodedata.normalize("NFC", char + "\u0301") != char + "\u0301",
                    f"Unexpected mark disappearance: {char}.")
            require(shaped[0]["advance"] == 350, f"Non-monospace composed {char}.")
            continue
        require(len(shaped) == 2, f"Unexpected acute shaping: {char}.")
        base, mark = shaped
        require(mark["advance"] == 0 and base["advance"] == 350,
                f"Combining mark changes cell width: {char}.")
        require(mark["x"] == 0, f"Acute is outside its base cell: {char}.")
        mark_box = bounds(font, mark["glyph"])
        require(mark_box[1] + mark["y"] - bounds(font, name)[3] == 50,
                f"Acute lacks the one-pixel vertical gap: {char}.")

    for text in ("ЁёЙй", "Е\u0308е\u0308И\u0306и\u0306"):
        positions = lambda rows: [{k: v for k, v in row.items() if k != "cluster"} for row in rows]
        require(positions(shape(font, text)) == positions(shape(font, unicodedata.normalize("NFC", text))),
                "NFC/NFD mismatch for Ё/Й.")
        require(shape(source, text) == shape(font, text), "Existing Ё/Й behavior changed.")
    for text in (RUSSIAN, "Привет, мир! № 42 — 1 234 ₽", "Hello, world! 0123456789",
                 "café à Å ü fi ffi 1/2", "Ελληνικά", "ҐґЄєІіЇїЎў"):
        for features in ({}, {"smcp": True}, {"c2sc": True}, {"onum": True}, {"frac": True}):
            require(shape(source, text, features) == shape(font, text, features),
                    f"Unintended shaping change: {text!r}, {features}.")
    for text in ("за́мок", "замо́к", "молоко́", "по́езд", "ПРИВЕ́Т", "А́Е́И́О́У́Ы́Э́Ю́Я́"):
        shaped = shape(font, text)
        letters = sum(not unicodedata.combining(c) for c in text)
        require(sum(g["advance"] for g in shaped) == letters * 350, "Stress changes word width.")
        for g in shaped:
            if g["advance"] == 0:
                index = g["cluster"]
                cell = sum(not unicodedata.combining(c) for c in text[:index])
                require(g["x"] == cell * 350, f"Wrong stress attachment in {text}.")


def check():
    source = load_source()
    # Regression must be real: the upstream acute starts one full cell too far right.
    require(shape(source, "а́")[1]["x"] == 350, "Revisit the upstream bug reproduction.")
    for ext in ("otf", "woff", "woff2"):
        font = TTFont(OUTPUT / f"{PS_NAME}.{ext}", recalcTimestamp=False)
        validate_font(source, font)
        print(f"PASS {ext}: coverage, 1186 outlines, metrics, Russian marks, NFC/NFD, shaping regressions")
    require((OUTPUT / "OFL.txt").read_bytes() == (ROOT / "public/assets/LICENSE").read_bytes(),
            "Bundled license differs from upstream.")
    # Rebuilding the pinned input must yield byte-identical artifacts.
    rebuilt = load_source()
    patch(rebuilt)
    for ext in ("otf", "woff", "woff2"):
        rebuilt.flavor = None if ext == "otf" else ext
        stream = BytesIO()
        rebuilt.save(stream)
        require(stream.getvalue() == (OUTPUT / f"{PS_NAME}.{ext}").read_bytes(),
                f"Non-reproducible {ext} build.")
    print("PASS deterministic build and bundled OFL")


def audit():
    source = load_source()
    cmap = source.getBestCmap()
    report = {
        "source": str(SOURCE.relative_to(ROOT)), "sha256": SOURCE_HASH,
        "version": source["name"].getDebugName(5),
        "glyph_count": len(source.getGlyphOrder()), "encoded_characters": len(cmap),
        "cyrillic_0400_052F": sum(0x400 <= c <= 0x52F for c in cmap),
        "russian_letters": len(RUSSIAN), "upm": source["head"].unitsPerEm,
        "advance": 350, "grid": 50, "x_height": source["OS/2"].sxHeight,
        "cap_height": source["OS/2"].sCapHeight,
        "hhea_ascent": source["hhea"].ascent, "hhea_descent": source["hhea"].descent,
        "glyphs": [{"character": c, "codepoint": f"U+{ord(c):04X}",
                    "glyph": cmap[ord(c)], "bounds": bounds(source, cmap[ord(c)]),
                    "advance": source["hmtx"][cmap[ord(c)]][0]} for c in RUSSIAN],
        "shared_outlines": {pair: outline(source, cmap[ord(pair[0])]) ==
                            outline(source, cmap[ord(pair[1])])
                            for pair in ["АA", "ВB", "ЕE", "КK", "МM", "НH", "ОO", "РP",
                                         "СC", "ТT", "ХX", "аa", "еe", "оo", "рp", "сc", "уy", "хx"]},
        "before": shape(source, "за́мок"),
        "after": shape(TTFont(OUTPUT / f"{PS_NAME}.otf", recalcTimestamp=False), "за́мок"),
    }
    PROOFS.mkdir(parents=True, exist_ok=True)
    (PROOFS / "audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["build", "check", "proof"])
    args = parser.parse_args()
    if args.command == "build":
        build()
    elif args.command == "check":
        check()
    else:
        from font_ru_proof import proof
        audit()
        proof()
