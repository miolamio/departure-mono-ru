# Font change log

## 2026-11-06 — 1.501 / RU proof 1 (unofficial)

Based on Departure Mono 1.500 by Helena Zhang, from upstream commit
`75152a3`. Input OTF SHA-256:
`4d53f663155cf8bf7ffc8e688776e719625f7bbb80a8d90073438b249261a2e0`.

- Added missing top anchors to 62 existing Russian Cyrillic base glyphs in
  the original GPOS mark-to-base lookup. Existing ЁёЙй anchors are preserved.
- Corrected combining acute placement in Russian words such as `за́мок`,
  `молоко́` and `ПРИВЕ́Т`, preserving monospaced advances.
- Retained all 1,186 outlines, character mappings, glyph order, original
  copyright notices, designer attribution, GSUB and vertical metrics.
- Renamed family, full name, unique ID and PostScript/CFF names to
  Departure Mono RU / DepartureMonoRU-Regular to distinguish the proof.
- Exported OTF, WOFF and WOFF2 with a deterministic, input-hash-guarded patch.
- Included Russian proofs, regression checks and research notes.

The new anchors apply to the existing top-mark class, not just acute.
This is a compiled-font patch, not a reconstruction of the original Glyphs
source. It adds no Cyrillic letters: those were already designed and
released by the upstream project. It is not an endorsement by the original
authors. The derivative font remains under SIL OFL 1.1; see OFL.txt.
