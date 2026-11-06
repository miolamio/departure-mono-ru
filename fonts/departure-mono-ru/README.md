# Departure Mono RU — proof 1

An experimental build based on **Departure Mono 1.500** by Helena Zhang.
The upstream font already includes Russian letters. This build corrects
stress marks and other top-mark positioning for 62 existing Russian letters,
preserving the original outlines and advances.

This is an unofficial derivative. Internal version: **1.501**. Family:
**Departure Mono RU**, style: Regular. The separate name allows installation
alongside the original font.

- [DepartureMonoRU-Regular.otf](DepartureMonoRU-Regular.otf) — desktop installation.
- [DepartureMonoRU-Regular.woff2](DepartureMonoRU-Regular.woff2) — primary web format.
- [DepartureMonoRU-Regular.woff](DepartureMonoRU-Regular.woff) — additional web format.
- [OFL.txt](OFL.txt) — font license; distribute it with the font files.
- [FONTLOG.md](FONTLOG.md) — detailed changes.
- [Typography study and validation](../../docs/CYRILLIC-RU.md).

## Web usage

If these files are hosted at `/fonts/`:

```css
@font-face {
  font-family: "Departure Mono RU";
  src: url("/fonts/DepartureMonoRU-Regular.woff2") format("woff2"),
       url("/fonts/DepartureMonoRU-Regular.woff") format("woff");
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}

.russian-sample {
  font-family: "Departure Mono RU", monospace;
  font-size: 22px;
  line-height: 1.5;
  letter-spacing: 0;
  font-synthesis: none;
}
```

Test string: `за́мок — замо́к; молоко́; ПРИВЕ́Т; Ёж ждёт поезд № 42.`

## Build and check

From the repository root:

```sh
uv run scripts/font_ru.py build
uv run scripts/font_ru.py check
uv run scripts/font_ru.py proof
```

Verified with HarfBuzz and Chromium on macOS in all three formats. Other
platforms and small caps with stress marks require separate validation.
The author's full Glyphs project is not included in this repository; the
build reproduces a small patch of the compiled font.
