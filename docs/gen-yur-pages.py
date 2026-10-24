# -*- coding: utf-8 -*-
"""
Генератор ЮРИДИЧЕСКИХ СТРАНИЦ из документов заказчицы (.docx).

Тексты — как есть, без правки: «полностью копируем-вставляем». Скрипт только
переводит разметку Word в HTML: заголовки, абзацы, списки, жирное, переносы
строк, ссылки. Поправит заказчица документ — положить новый .docx в
docs/yur/ под тем же именем и запустить скрипт снова.

ЗАПУСК:
    python3 docs/gen-yur-pages.py

ЧТО ПОЛУЧАЕТСЯ (блоки «Другое → HTML-код», T123):
    pages/oferta.html    — /oferta: оферта + Приложения 1 и 2
    pages/politika.html  — /politika-obrabotki-persdannyh
    pages/soglasie.html  — /soglasie

НА СТРАНИЦУ НЕ ИДУТ:
    - строки до заголовка документа: там адрес страницы («2young4U.ru/oferta»),
      это пометка для нас, а не текст для покупателя;
    - в согласии раздел «Как разместить на сайте» — инструкция разработчику.

Блок длиннее LIMIT байт режется на части по границе раздела: размер блока
HTML-кода в Tilda нигде не описан, а поле HEAD обрезало всё после 64 КБ.
"""
import html
import os
import re
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YUR = os.path.join(ROOT, "docs", "yur")
OUT = os.path.join(ROOT, "pages")

LIMIT = 61000  # байт на один блок T123: запас ~4 КБ до 64 КБ, где обрезался HEAD

DOCS = [
    {
        "src": "oferta.docx",
        "out": "oferta.html",
        "url": "/oferta",
        "seo_title": "Публичная оферта — 2YOUNG4U",
        "seo_descr": "Публичная оферта 2young4U: оформление и оплата заказа, "
                     "доставка, отказ от заказа, возврат и замена изделий.",
        "toc": True,
    },
    {
        "src": "politika-persdannyh.docx",
        "out": "politika.html",
        "url": "/politika-obrabotki-persdannyh",
        "seo_title": "Политика обработки персональных данных — 2YOUNG4U",
        "seo_descr": "Как 2young4U обрабатывает и защищает персональные данные "
                     "пользователей сайта и покупателей.",
        "toc": True,
    },
    {
        "src": "soglasie-reklama.docx",
        "out": "soglasie.html",
        "url": "/soglasie",
        "seo_title": "Согласие на получение рекламной информации — 2YOUNG4U",
        "seo_descr": "Текст согласия на получение рекламной и информационной "
                     "рассылки бренда 2young4U.",
        "toc": False,
        "stop_at": "Как разместить на сайте",
    },
]

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")


# ───────────────────────── чтение .docx ─────────────────────────

def read_docx(path):
    """Абзацы документа: стиль, признак списка и HTML содержимого."""
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
        rels = z.read("word/_rels/document.xml.rels").decode("utf-8")
    links = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', rels))

    paras = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", xml, flags=re.S):
        style = re.search(r'<w:pStyle w:val="([^"]+)"', p)
        paras.append({
            "style": style.group(1) if style else "",
            "list": "<w:numPr>" in p,
            "html": para_html(p, links),
            "text": para_text(p),
        })
    return paras


def para_text(p):
    p = re.sub(r"<w:br [^>]*/>", "\n", p)
    parts = re.findall(r"<w:t(?: [^>]*)?>([^<]*)</w:t>|(\n)", p)
    return html.unescape("".join(a or b for a, b in parts)).strip()


def run_html(r):
    """Один кусок текста Word → HTML: текст, переносы строк, жирное."""
    out = []
    for m in re.finditer(r"<w:t(?: [^>]*)?>([^<]*)</w:t>|<w:br [^>]*/>|<w:tab/>", r):
        if m.group(0).startswith("<w:br"):
            out.append("<br>")
        elif m.group(0) == "<w:tab/>":
            out.append(" ")
        else:
            out.append(html.escape(html.unescape(m.group(1)), quote=False))
    text = "".join(out)
    bold = re.search(r'<w:b/>|<w:b w:val="(?:1|true)"/>', r)
    return text, bool(bold)


def para_html(p, links):
    pieces = []  # (html, жирное, ссылка)
    body = re.sub(r"<w:pPr>.*?</w:pPr>", "", p, flags=re.S)
    for m in re.finditer(r'<w:hyperlink [^>]*r:id="(rId\d+)"[^>]*>(.*?)</w:hyperlink>'
                         r"|<w:r[ >].*?</w:r>", body, flags=re.S):
        if m.group(1):
            href = links.get(m.group(1), "")
            for r in re.findall(r"<w:r[ >].*?</w:r>", m.group(2), flags=re.S):
                t, b = run_html(r)
                pieces.append((t, b, href))
        else:
            t, b = run_html(m.group(0))
            pieces.append((t, b, ""))

    # склеиваем соседние куски с одинаковым оформлением
    merged = []
    for t, b, href in pieces:
        if not t:
            continue
        if merged and merged[-1][1] == b and merged[-1][2] == href:
            merged[-1][0] += t
        else:
            merged.append([t, b, href])

    out = []
    for t, b, href in merged:
        # перенос строки в конце ссылки — вынести наружу
        tail = ""
        while t.endswith("<br>") and href:
            t, tail = t[:-4], tail + "<br>"
        # В оферте у почты текст «sales@», а ссылка внутри — на «official@»
        # (текст правили, ссылку нет). Ведём туда, что человек видит.
        shown = html.unescape(re.sub(r"<[^>]+>", "", t)).strip()
        if href.startswith("mailto:") and EMAIL_RE.fullmatch(shown):
            href = "mailto:" + shown
        if b:
            t = "<b>" + t + "</b>"
        if href:
            t = '<a href="%s">%s</a>' % (html.escape(href), t)
        out.append(t + tail)
    s = "".join(out).strip()
    s = re.sub(r"(<br>\s*)+$", "", s)
    return link_emails(s)


def link_emails(s):
    """Почту — кликабельной: на телефоне сразу открывается письмо.
    Только в тексте: не внутри тегов и не внутри готовых ссылок."""
    def repl(m):
        e = m.group(0).rstrip(".")
        rest = m.group(0)[len(e):]
        return '<a href="mailto:%s">%s</a>%s' % (e, e, rest)

    out, in_link = [], False
    for piece in re.split(r"(<[^>]+>)", s):
        if piece.startswith("<"):
            if re.match(r"<a[\s>]", piece):
                in_link = True
            elif piece == "</a>":
                in_link = False
            out.append(piece)
        elif in_link:
            out.append(piece)
        else:
            out.append(EMAIL_RE.sub(repl, piece))
    return "".join(out)


# ───────────────────────── разметка страницы ─────────────────────────

def level(style):
    m = re.match(r"Heading(\d)", style)
    return int(m.group(1)) if m else 0


def is_appendix(text):
    return bool(re.match(r"Приложение\s*№\s*\d", text))


def build(doc):
    paras = read_docx(os.path.join(YUR, doc["src"]))

    # всё до первого заголовка 1-го уровня — пометки для нас
    start = next(i for i, p in enumerate(paras) if level(p["style"]) == 1)
    paras = paras[start:]
    if doc.get("stop_at"):
        stop = next(i for i, p in enumerate(paras) if p["text"].startswith(doc["stop_at"]))
        paras = paras[:stop]
    paras = [p for p in paras if p["text"]]

    items = []        # (вид, html, якорь)
    toc = []          # (якорь, текст)
    part = 0          # 0 — основной текст, N — Приложение N
    sec_level = None  # какой стиль Word в этой части — разделы
    expect_sub = False

    for i, p in enumerate(paras):
        lv, text = level(p["style"]), p["text"]

        if i == 0:
            items.append(("title", p["html"], ""))
            expect_sub = True
            continue
        if is_appendix(text):
            part = int(re.search(r"\d+", text).group())
            anchor = "pril-%d" % part
            items.append(("part", p["html"], anchor))
            toc.append((anchor, text))
            sec_level, expect_sub = None, True
            continue
        if expect_sub and lv:
            items.append(("subtitle", p["html"], ""))
            if part and toc:  # «Приложение №1 — Отказ от заказа…»
                toc[-1] = (toc[-1][0], toc[-1][1] + " — " + text)
            expect_sub = False
            continue
        expect_sub = False

        if lv:
            if sec_level is None or lv <= sec_level:
                sec_level = lv
                num = re.match(r"(\d+)\.", text)
                anchor = ("p-" if not part else "pril-%d-" % part) + (num.group(1) if num else str(i))
                items.append(("h", p["html"], anchor))
                if not part:
                    toc.append((anchor, text))
            else:
                items.append(("sub", p["html"], ""))
        elif p["list"]:
            items.append(("li", p["html"], ""))
        else:
            items.append(("p", p["html"], ""))
    return items, toc


def render(items, toc, with_toc):
    out, in_list = [], False
    for kind, h, anchor in items:
        if kind not in ("p", "li"):
            # в Word заголовки жирные; у Tenor жирного нет — браузер нарисует
            # «фальшивый», поэтому вес задаёт только стиль
            h = re.sub(r"</?b>", "", h)
        if kind != "li" and in_list:
            out.append("    </ul>")
            in_list = False
        if kind == "title":
            out.append('    <h1 class="t2y-doc__title">%s</h1>' % h)
        elif kind == "subtitle":
            out.append('    <p class="t2y-doc__subtitle">%s</p>' % h)
            if with_toc and toc and not out_has_toc(out):
                out.append(render_toc(toc))
        elif kind == "part":
            out.append('    <h2 class="t2y-doc__part" id="%s">%s</h2>' % (anchor, h))
        elif kind == "h":
            out.append('    <h2 class="t2y-doc__h" id="%s">%s</h2>' % (anchor, h))
        elif kind == "sub":
            out.append('    <h3 class="t2y-doc__sub">%s</h3>' % h)
        elif kind == "li":
            if not in_list:
                out.append('    <ul class="t2y-doc__list">')
                in_list = True
            out.append("      <li>%s</li>" % h)
        else:
            out.append("    <p>%s</p>" % h)
    if in_list:
        out.append("    </ul>")
    return out


def out_has_toc(lines):
    return any("t2y-doc__toc" in l for l in lines)


def render_toc(toc):
    rows = "\n".join('        <li><a href="#%s">%s</a></li>' % (a, html.escape(t, quote=False))
                     for a, t in toc)
    return ('    <details class="t2y-doc__toc">\n'
            "      <summary>Содержание</summary>\n"
            '      <ul>\n%s\n      </ul>\n'
            "    </details>" % rows)


CSS = """<style>
.t2y-doc {
  padding: 110px 20px 80px;
  box-sizing: border-box;
  background: #ffffff;
}
.t2y-doc__inner { max-width: 760px; margin: 0 auto; }
/* ровные цифры: номера пунктов, ИНН, даты читаются легче */
.t2y-doc { font-variant-numeric: lining-nums; }
.t2y-doc__title + p { margin-top: 18px; }
.t2y-doc_cont { padding-top: 0; }

.t2y-doc__title {
  font-family: 'Tenor Sans', 'Tenor', Arial, sans-serif;
  font-weight: 400;
  font-size: 24px;
  line-height: 1.25;
  letter-spacing: .02em;
  color: #000000;
  margin: 0 0 10px;
}
.t2y-doc__subtitle {
  font-family: 'Raleway', Arial, sans-serif;
  font-weight: 400;
  font-size: 17px;
  line-height: 1.45;
  color: #000000;
  margin: 0 0 24px;
}
.t2y-doc__part {
  font-family: 'Tenor Sans', 'Tenor', Arial, sans-serif;
  font-weight: 400;
  font-size: 22px;
  line-height: 1.3;
  color: #000000;
  margin: 56px 0 6px;
  padding-top: 32px;
  border-top: 1px solid #e5e5e5;
}
.t2y-doc__h {
  font-family: 'Tenor Sans', 'Tenor', Arial, sans-serif;
  font-weight: 400;
  font-size: 19px;
  line-height: 1.35;
  color: #000000;
  margin: 32px 0 10px;
}
.t2y-doc__sub {
  font-family: 'Raleway', Arial, sans-serif;
  font-weight: 600;
  font-size: 15px;
  line-height: 1.5;
  color: #000000;
  margin: 20px 0 8px;
}
/* якорь из оглавления не должен прятаться под закреплённую шапку */
.t2y-doc [id] { scroll-margin-top: 90px; }

.t2y-doc p,
.t2y-doc__list li {
  font-family: 'Raleway', Arial, sans-serif;
  font-weight: 300;
  font-size: 15px;
  line-height: 1.65;
  color: #333333;
  margin: 0 0 10px;
  overflow-wrap: break-word;
}
.t2y-doc .t2y-doc__subtitle { color: #000000; font-weight: 400; font-size: 17px; }
.t2y-doc__list { margin: 0 0 14px; padding-left: 20px; }
.t2y-doc__list li { margin-bottom: 6px; }
.t2y-doc b { font-weight: 600; color: #000000; }
.t2y-doc a {
  color: #000000 !important;
  text-decoration: none !important;
  border-bottom: 1px solid #bbbbbb;
}

/* Оглавление: свёрнуто, раскрывается по нажатию — без скриптов */
.t2y-doc__toc { margin: 0 0 32px; padding: 0 20px; background: #f6f6f6; }
.t2y-doc__toc summary {
  list-style: none;
  cursor: pointer;
  position: relative;
  padding: 16px 30px 16px 0;
  font-family: 'Raleway', Arial, sans-serif;
  font-weight: 500;
  font-size: 15px;
  color: #000000;
}
.t2y-doc__toc summary::-webkit-details-marker { display: none; }
.t2y-doc__toc summary::after {
  content: '+';
  position: absolute; right: 0; top: 50%;
  transform: translateY(-50%);
  font-size: 22px; font-weight: 300;
}
.t2y-doc__toc[open] summary::after { content: '−'; }
.t2y-doc__toc ul { list-style: none; margin: 0; padding: 0 0 14px; }
.t2y-doc__toc li {
  font-family: 'Raleway', Arial, sans-serif;
  font-weight: 300;
  font-size: 14px;
  line-height: 1.5;
  margin: 0 0 9px;
}
.t2y-doc__toc a { border-bottom: none; }

@media screen and (min-width: 640px) {
  .t2y-doc { padding-top: 150px; }
  .t2y-doc_cont { padding-top: 0; }
  .t2y-doc__title { font-size: 32px; }
  .t2y-doc__part { font-size: 26px; }
  .t2y-doc__h { font-size: 21px; }
}
</style>"""


def header(doc, block_note):
    return """<!-- ════════════════════════════════════════════════════════════════
     %s.  Собрано из %s скриптом docs/gen-yur-pages.py.
     ТЕКСТ — КАК В ДОКУМЕНТЕ ЗАКАЗЧИЦЫ, руками не править: поправить .docx
     и запустить скрипт заново.

     КУДА: новая страница, адрес %s.
%s
     Шапка и подвал подставятся сами.

     SEO (Настройки страницы → SEO):
       Заголовок:  %s
       Описание:   %s
     ════════════════════════════════════════════════════════════════ -->
""" % (doc["title_note"], "docs/yur/" + doc["src"], doc["url"], block_note,
       doc["seo_title"], doc["seo_descr"])


def wrap(lines, cont=False):
    cls = "t2y-doc t2y-doc_cont" if cont else "t2y-doc"
    return ('<div class="%s">\n  <div class="t2y-doc__inner">\n' % cls
            + "\n".join(lines) + "\n  </div>\n</div>")


def block_size(lines):
    return len((wrap(lines) + "\n\n" + css_min()).encode("utf-8"))


def split_blocks(lines):
    """Если всё не влезает в LIMIT — сначала отделяем приложения (основной
    текст и приложения — разные блоки), и только если кусок всё равно велик,
    режем его по началу раздела."""
    if block_size(lines) <= LIMIT:
        return [lines]
    parts, cur = [], []
    for l in lines:
        if cur and 'class="t2y-doc__part"' in l and not any('class="t2y-doc__part"' in x for x in cur):
            parts.append(cur)
            cur = []
        cur.append(l)
    parts.append(cur)

    blocks = []
    for part in parts:
        cur = []
        for l in part:
            starts = 'class="t2y-doc__h"' in l or 'class="t2y-doc__part"' in l
            if cur and starts and block_size(cur + [l]) > LIMIT:
                blocks.append(cur)
                cur = []
            cur.append(l)
        blocks.append(cur)
    return blocks


def css_min():
    """CSS без комментариев и отступов — каждый байт блока на счету."""
    c = re.sub(r"/\*.*?\*/", "", CSS, flags=re.S)
    c = re.sub(r"\n\s*", "\n", c)
    return re.sub(r"\n+", "\n", c).strip()


def main():
    for doc in DOCS:
        items, toc = build(doc)
        doc["title_note"] = re.sub(r"<[^>]+>", "", items[0][1])
        lines = render(items, toc, doc["toc"])
        blocks = split_blocks(lines)

        if len(blocks) == 1:
            note = ('     Один блок «Другое → HTML-код» (T123), вставить ВСЁ содержимое файла.')
            text = header(doc, note) + "\n" + wrap(blocks[0]) + "\n\n" + css_min() + "\n"
        else:
            note = ("     Текст длинный — %d блока «Другое → HTML-код» (T123) подряд,\n"
                    "     каждый между метками «БЛОК N … конец БЛОКА N». Блоки — по порядку." % len(blocks))
            parts = [header(doc, note)]
            for n, b in enumerate(blocks, 1):
                parts.append("\n<!-- ═══════════════ БЛОК %d из %d (копировать отсюда) ═══════════════ -->\n" % (n, len(blocks)))
                parts.append(wrap(b, cont=n > 1) + "\n\n" + css_min() + "\n")
                parts.append("<!-- ═══════════════ конец БЛОКА %d ═══════════════ -->\n" % n)
            text = "".join(parts)

        path = os.path.join(OUT, doc["out"])
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        sizes = [block_size(b) for b in blocks]
        print("%-14s %d абзацев, блоков: %d, байт: %s" % (doc["out"], len(items), len(blocks), sizes))


if __name__ == "__main__":
    main()
