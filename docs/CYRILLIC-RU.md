# Russian Cyrillic in Departure Mono

Research and first technical proof, 6 November 2026. The changes target Russian.

## Findings

Upstream Departure Mono 1.500 already includes all 33 uppercase and 33 lowercase
Russian letters, including Ё/ё. Cyrillic was introduced in
[1.420](https://github.com/rektdeckard/departure-mono/releases/tag/v1.420);
1.422 fixed Ё/ё and refined several forms. See the
[original change log](../public/assets/README.md).

A separate defect was found: combining acute accents (`U+0301`) on most Russian
letters were positioned one character cell too far to the right. In `за́мок`,
the mark appeared above `м`; in `молоко́`, it appeared after the word.
**Departure Mono RU, version 1.501 / RU proof 1** restores the missing top-mark
anchors. It adds no letters and preserves the original outlines.

- [Full Russian specimen](proofs/russian-specimen.svg) · [PNG](proofs/russian-specimen.png)
- [Stress marks: before and after](proofs/stress-before-after.svg)
- [Actual OTF, WOFF, and WOFF2 rendering in Chromium](proofs/browser-stress.png)
- [Font files and installation](../fonts/departure-mono-ru/README.md)
- [Machine-readable measurements](proofs/audit.json)

## Repository and source material

This repository contains the Solid/Vite website and compiled fonts. It does
not contain the author's `.glyphs` project, UFO sources, or original font build
pipeline. The [upstream maintainer confirms](https://github.com/rektdeckard/departure-mono/issues/3#issuecomment-2338727318)
that the font is built separately in Glyphs and distributed as a static asset.

`DepartureMono-Regular.*` and `DepartureMono-1.500.*` are byte-identical for
each format. The website CSS and glyph viewer use the current `Regular` files.
The older `dm.*` files contain 1,030 glyphs and are not the basis of this work.

The new build is a reproducible patch of an OTF identified by its SHA-256.
It does not reconstruct the author's editable sources.

## Geometry and adaptation principles

These measurements come from the local OTF tables and contours.

| Property | Font units | At 11 px |
| --- | ---: | ---: |
| Units per em | 550 | 11 px |
| Contour grid step | 50 | 1 px |
| Character advance | 350 | 7 px |
| Cap height | 400 | 8 px |
| Lowercase x-height | 300 | 6 px |
| Typical descender | −100 | −2 px |
| Top of Й | 550 | 11 px above baseline |
| hhea ascent / descent | 550 / −150 | 11 / −3 px |

Most letters occupy five columns within a seven-column cell. Д/д and Ж/ж use
the full cell width; the tails of Ц/ц and Щ/щ reach the right boundary.
All contour coordinates of the 66 Russian letters lie on the 50-unit grid,
and their outlines use straight segments.

Working constraints for any future alternatives:

1. **Keep the grid and stroke weight.** Smoothing steps, introducing half-pixel
   details, or mechanically compressing wide letters changes the typeface's
   character. A module measures `font-size × 50 / 550`; use 11, 22, 33, or 44 px
   as starting sizes. Browser zoom, device pixel ratio, and fractional placement
   also affect sharpness. See the grid and size calculations in
   [Glyphs: Creating a pixel font](https://glyphsapp.com/learn/pixelfont).
2. **Keep the 350-unit advance.** Solve rhythm problems inside the fixed cell;
   proportional kerning would change alignment in code and tables. Start at
   `letter-spacing: 0`. Negative tracking is particularly risky for ДЖЩЮ.
   Review spacing at the intended reading size, as recommended in
   [Glyphs: Spacing](https://glyphsapp.com/learn/spacing).
3. **Choose related forms by construction.** Shared shapes provide useful
   reference glyphs, while distinct Cyrillic letters must remain recognizable.
   Designers discuss these principles, native-reader review, and the density
   of Ж in [Google Design: Scripting Cyrillic](https://design.google/library/scripting-cyrillic).
4. **Check encoding and positioning as well as outlines.** A character in
   `cmap` does not establish that stress marks work. Test decomposed sequences
   and GPOS in each output format. See
   [OpenType development for standard scripts](https://learn.microsoft.com/en-us/typography/script-development/standard).

## Compatible forms and combinations

The following are observations about this particular pixel design, based on
the specimens. They are not universal rules for Cyrillic type design.

| Group | Observation and decision |
| --- | --- |
| `АA ВB ЕE МM НH ОO РP СC ТT ХX` | Each pair has identical outlines. These are reliable references for matching weight and height across scripts. |
| `аa еe оo рp сc уy хx` | These outlines also match, helping mixed-script lines retain a consistent rhythm. |
| `КK`, `Жж` | К and K have different contours. Retain the original Cyrillic К; evaluate any diagonal changes beside Ж instead of automatically copying Latin K. |
| `Дд Лл` | The rectangular top and stepped left leg form a coherent pair. The base and descenders distinguish Д from Л. A triangular Д could be explored, but no advantage has been established here. |
| `Шш Щщ Цц` | Counters and tails are essential. At 11 px, a single added module substantially changes density; test `шишки`, `щука`, and `птица`. |
| `Бб Вв`, `Фф` | Lowercase б and the stem of ф extend above x-height. These differences aid recognition and affect mark attachment height. |
| `Ъъ Ыы Ьь Юю Яя` | Test `съезд`, `объём`, `мышь`, `вьюга`, and `язык`. Keep the small counters open where stems and bowls meet. |
| `Ёё Йй` | Preserve distinguishing diacritics. Й already reaches the top of the line metrics, so tight line heights need separate review. |

In the original `ддд`, adjacent bases connect at zero tracking. This is visible
in the specimen and should be assessed in the intended interface before a
redesign. The proof preserves it as an original design choice. Compare future
alternatives at 11 and 22 px, in words and mixed-script text, rather than judging
only enlarged isolated letters.

## Implementation

GPOS lookup 0 contains the Cyrillic mark-to-base lookup and existing top
anchors for ЁёЙй, but lacks anchors for the other 62 Russian letters. The patch
adds top anchors at `x = 175`, matching the author's mark alignment. Their
vertical position follows each letter's actual ink top: 400 for capitals,
usually 300 for lowercase, and 400 for б/ф.

The original acute has a lower ink boundary at 350 and its attachment anchor
at 300. Correct positioning leaves a 50-unit gap above the base letter.
The shaper gives the combining mark zero advance, so `за́мок` still occupies
five cells. The original `hmtx` stores a 350-unit width for all glyphs, including
combining marks; these metrics are preserved.

The anchors apply to the existing top-mark class, not just acute. Russian
stress is the primary tested scenario. Existing anchors, contours, `cmap`,
GSUB, and vertical metrics are preserved. fontTools compresses identical
`hmtx` entries during serialization without changing actual advances.
The separate family name allows side-by-side installation.

## Validation and limits

Automated validation of all three formats confirms:

- The original defect is reproducible. Acute positioning is checked across the
  Russian alphabet, accounting for canonical composition of Г/К + acute into Ѓ/Ќ.
- All 1,186 outlines, glyph order, character mappings, and actual metrics are preserved.
- `ЁёЙй` and `ЁёЙй` produce equivalent glyphs and positions.
- Ordinary Russian, Latin, Greek, and selected OpenType-feature samples retain
  the original shaping behavior.
- Rebuilding the pinned input produces byte-identical OTF, WOFF, and WOFF2 files.
- The bundled OFL text matches the original license.

Chromium 156 on macOS was used to check loading of all three formats, accent
pixel positions, and word widths at 11/22/33/44 px. At 44 px, the accent in `а́`
moved from x=40…47 to x=12…19 while the character advance stayed at 28 px.
The browser screenshot is linked above.

Safari/CoreText, Firefox, and Windows applications have not been checked.
Small caps with stress marks, arbitrary stacked diacritics, italics, and
regional forms for other Cyrillic languages are outside this proof's scope.
Very tall combinations such as `Й́` can exceed the existing vertical metrics;
the patch does not change the entire typeface's line spacing for those cases.

## Reproduction

From the repository root, with `uv` installed:

```sh
uv run scripts/font_ru.py build
uv run scripts/font_ru.py check
uv run scripts/font_ru.py proof
```

fontTools, Brotli, and uharfbuzz versions are pinned in the script metadata.
Validation uses [HarfBuzz through uharfbuzz](https://uharfbuzz.readthedocs.io/).
Vector specimens use actual font contours and shaped positions, without
system-font substitution.

For the browser check, start `python3 -m http.server 8769 --bind 127.0.0.1`,
then run in another terminal:

```sh
playwright-cli -s=departure-ru open http://127.0.0.1:8769/fonts/
playwright-cli -s=departure-ru run-code --filename=scripts/verify_ru_browser.cjs
```

The browser check writes `docs/proofs/browser-stress.png`. The `proof` command
writes SVG specimens and the audit JSON. The full-specimen PNG is a screenshot
of its SVG at a 1200×1510 viewport and DPR 1. Specimen captions remain in Russian.

## Licensing and publication

The font uses [SIL OFL 1.1](../public/assets/LICENSE); the website uses
[MIT](../LICENSE). OFL permits modification and redistribution subject to its
terms, including preservation of copyright and license notices. The derivative
font remains under OFL. The supplied copyright notice declares no Reserved
Font Names. A distinct family name identifies this unofficial proof and avoids
installation conflicts. See the
[official OFL modification guide](https://openfontlicense.org/how-to-modify-ofl-fonts/).

The publication target is the public fork
[miolamio/departure-mono-ru](https://github.com/miolamio/departure-mono-ru).
It includes the font builds, patch source, checks, change log, and specimens.
The contribution is Russian diacritic positioning; the upstream project retains
credit for the existing Cyrillic design. The inherited website assets still
refer to upstream, and the DreamHost workflows are restricted to the upstream
repository. Deploying a separate website is outside this publication.
