"""Vector proofs drawn from actual contours and HarfBuzz positions; no fallback fonts.

Invoked by `uv run scripts/font_ru.py proof`.
"""

from html import escape

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

from font_ru import OUTPUT, PROOFS, PS_NAME, SOURCE, UPPER, shape


PAPER = "#f4f1e8"
INK = "#262720"
MUTED = "#66675e"
ACCENT = "#aa3c28"
GRID = "#d5d2c7"


class Sheet:
    def __init__(self, height, title):
        self.height = height
        self.items = [f'<title>{escape(title)}</title>',
                      f'<rect width="1200" height="{height}" fill="{PAPER}"/>']

    def label(self, text, x, y, size=15, color=MUTED):
        self.items.append(f'<text x="{x}" y="{y}" font-family="sans-serif" '
                          f'font-size="{size}" fill="{color}">{escape(text)}</text>')

    def line(self, x1, y1, x2, y2, color=GRID):
        self.items.append(f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{color}"/>')

    def text(self, font, text, x, baseline, size, color=INK, highlight_marks=False):
        glyphs = font.getGlyphSet()
        scale = size / font["head"].unitsPerEm
        self.items.append(f'<g aria-label="{escape(text, quote=True)}">')
        for entry in shape(font, text):
            pen = SVGPathPen(glyphs)
            glyphs[entry["glyph"]].draw(pen)
            fill = ACCENT if highlight_marks and entry["advance"] == 0 else color
            self.items.append(f'<path fill="{fill}" transform="translate('
                              f'{x + entry["x"] * scale:g} {baseline - entry["y"] * scale:g}) '
                              f'scale({scale:g} {-scale:g})" d="{pen.getCommands()}"/>')
        self.items.append('</g>')

    def save(self, name):
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{self.height}" '
               f'viewBox="0 0 1200 {self.height}" role="img">\n' + '\n'.join(self.items) + '\n</svg>\n')
        (PROOFS / name).write_text(svg, encoding="utf-8")


def proof():
    PROOFS.mkdir(parents=True, exist_ok=True)
    source = TTFont(SOURCE, recalcTimestamp=False)
    font = TTFont(OUTPUT / f"{PS_NAME}.otf", recalcTimestamp=False)
    page = Sheet(1510, "Departure Mono RU — русский пробный набор")
    page.label("DEPARTURE MONO / РУССКИЙ / ПРОБА 01", 48, 42, color=ACCENT)
    page.text(font, "РУССКИЙ НАБОР", 44, 108, 55)
    page.label("Рисунок: Helena Zhang · база 1.500 · RU proof 1: исправлены привязки диакритики", 48, 143)
    page.line(48, 168, 1152, 168)
    page.label("01   АЛФАВИТ · 33 ПРОПИСНЫЕ + 33 СТРОЧНЫЕ · 44 PX", 48, 201)
    page.text(font, UPPER, 44, 260, 44)
    page.text(font, UPPER.lower(), 44, 326, 44)
    page.line(48, 354, 1152, 354)
    page.label("02   ЛАТИНИЦА / КИРИЛЛИЦА · 33 PX", 48, 388)
    page.text(font, "AА BВ EЕ KК MМ HН OО PР CС TТ XХ", 44, 442, 33)
    page.text(font, "aа eе oо pр cс yу xх   3З зэ   NИ иЙ", 44, 494, 33)
    page.label("К / K имеют разные контуры. Остальные показанные пары с общей формой совпадают.", 48, 531)
    page.line(48, 555, 1152, 555)
    page.label("03   СЛОЖНЫЕ ФОРМЫ · СЕТКА 50 ЕДИНИЦ · ШИРИНА 350", 48, 588)
    for i, char in enumerate("ДдЛлЖжФфЩщЫы"):
        x, baseline, unit = 50 + i * 92, 718, 8
        for col in range(8):
            page.line(x + col * unit, baseline - 11 * unit, x + col * unit, baseline + 2 * unit)
        for row in range(-2, 12):
            page.line(x, baseline - row * unit, x + 7 * unit, baseline - row * unit)
        page.line(x, baseline, x + 7 * unit, baseline, ACCENT)
        page.text(font, char, x, baseline, 88)
        page.label(f"U+{ord(char):04X}", x, 764, 11)
    page.line(48, 788, 1152, 788)
    page.label("04   СЛОВА И РИТМ · 33 PX · ТРЕКИНГ 0", 48, 822)
    page.text(font, "ДОЖДЬ  ЖИЗНЬ  ЩУКА  ОБЪЁМ  СЪЕЗД", 44, 873, 33)
    page.text(font, "дождь  жизнь  щука  объём  съезд", 44, 927, 33)
    page.text(font, "ннн ппп иии шшш щщщ ллл ддд жжж", 44, 981, 33)
    page.line(48, 1009, 1152, 1009)
    page.label("05   РАБОЧИЕ РАЗМЕРЫ · 11 / 22 / 33 PX", 48, 1042)
    page.text(font, "Съешь ещё этих мягких французских булок, да выпей чаю. Ёж ждёт поезд № 42.", 47, 1076, 11)
    page.text(font, "Съешь ещё этих мягких французских булок, да выпей чаю.", 46, 1125, 22)
    page.text(font, "Ёж ждёт поезд № 42. Цена: 1 234 ₽.", 45, 1183, 33)
    page.line(48, 1211, 1152, 1211)
    page.label("06   СМЕШАННЫЙ НАБОР / УДАРЕНИЯ · 22 PX", 48, 1244)
    page.text(font, 'const привет = "Hello, мир!"; // строка № 42', 46, 1290, 22)
    page.text(font, "за́мок / замо́к   молоко́   по́езд   ПРИВЕ́Т", 46, 1337, 22, highlight_marks=True)
    page.text(font, "Ё ё Й й  /  Е\u0308 е\u0308 И\u0306 и\u0306", 46, 1384, 22)
    page.label("Векторная проба: контуры OTF + позиции HarfBuzz. Для 11 px смотрите файл при масштабе 100%.", 48, 1444, 13)
    page.label("Это техническая проба. Проверка в браузерах и редакторах дополняет её; исходные глифы не перерисованы.", 48, 1468, 13)
    page.save("russian-specimen.svg")

    page = Sheet(690, "Departure Mono — исправление русских ударений, до и после")
    page.label("DEPARTURE MONO / ПОЗИЦИОНИРОВАНИЕ УДАРЕНИЯ", 48, 42, color=ACCENT)
    page.text(font, "УДАРЕНИЕ НА СВОЁМ МЕСТЕ", 44, 109, 44)
    page.label("Одинаковые контуры и ширина строк. Красным выделен комбинируемый знак U+0301.", 48, 148)
    page.line(48, 176, 1152, 176)
    page.label("ИСХОДНЫЙ 1.500 · УДАРЕНИЕ СМЕЩЕНО НА ОДНО ЗНАКОМЕСТО", 48, 216)
    page.text(source, "за́мок  замо́к  молоко́  ПРИВЕ́Т", 44, 300, 44, highlight_marks=True)
    page.line(48, 340, 1152, 340)
    page.label("RU PROOF 1 · ПРИВЯЗКА К НУЖНОЙ БУКВЕ", 48, 380)
    page.text(font, "за́мок  замо́к  молоко́  ПРИВЕ́Т", 44, 464, 44, highlight_marks=True)
    page.line(48, 504, 1152, 504)
    page.text(font, "А́ Е́ И́ О́ У́ Ы́ Э́ Ю́ Я́", 44, 572, 33, highlight_marks=True)
    page.text(font, "а́ е́ и́ о́ у́ ы́ э́ ю́ я́", 44, 627, 33, highlight_marks=True)
    page.label("Восстановлены 62 верхние привязки. Существующие привязки ЁёЙй сохранены.", 48, 666, 13)
    page.save("stress-before-after.svg")
    print("Wrote vector specimens and audit.json to docs/proofs/.")
