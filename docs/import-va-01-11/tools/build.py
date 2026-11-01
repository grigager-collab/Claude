# -*- coding: utf-8 -*-
"""
Товары VipAvenue → CSV импорта каталога Tilda (2young4u.ru), 01.11.2026.

    python3 -I tools/build.py photos <папка_фото>        # первое фото: фон #F4F3EF
    python3 -I tools/build.py csv <папка_фото> <база_url> <выход.csv>

Формат CSV — как в docs/feed-to-tilda.py (правила в docs/tilda-reference.md, п. 16):
родитель + строка на размер, у родителя пустые Price/Quantity/SKU/Editions,
Parent UID варианта = External ID родителя. «Url» пустой: пока у товара нет своей
страницы /p/…, витрина открывает стандартную карточку Tilda.
"""
import json, os, re, sys, csv, subprocess
import numpy as np
from PIL import Image

BG = (244, 243, 239)          # #F4F3EF — цвет фона с образца Григория (01.11)
SIZES = ["S", "M", "L", "XL", "2XL", "3XL"]   # решение заказчицы 08.10: у всех S–3XL
QTY = 10

HEADER = ["Brand", "SKU", "Mark", "Category", "Title", "Description", "Text",
          "Photo", "Price", "Quantity", "Price Old", "Editions", "Modifications",
          "External ID", "Parent UID",
          "Characteristics:Основной материал", "Characteristics:Подклад",
          "Characteristics:Цвет", "Characteristics:Сезон",
          "Characteristics:Стиль", "Characteristics:Капсула",
          "Weight", "Length", "Width", "Height", "Url"]

COLOR_FIX = {"Черный": "Чёрный", "Кремовый": "Белый", "Зеленый": "Зелёный", "Желтый": "Жёлтый"}
COLOR_HEX = {"Синий": "#073763", "Белый": "#fffae5", "Чёрный": "#1d1d1d", "Серый": "#cccccc",
             "Бежевый": "#e8dcc8", "Голубой": "#9dc3e6", "Коричневый": "#6b4423",
             "Зелёный": "#4a6741", "Жёлтый": "#f0d264", "Бордовый": "#7b241c"}
# у вещей из нескольких цветов — основной (по фото: костюм, а не футболка или принт)
PRIMARY = {"21260216": "Синий", "21260416": "Коричневый", "21260417": "Коричневый",
           "21260218": "Синий", "21260115": "Синий", "21260114": "Синий",
           "21260314": "Чёрный", "22130310": "Белый", "21090201": "Белый"}
# свои артикулы вместо VA (Кристина, 01.11): вторые тёмно-синие брюки со стрелкой — коллекция 22
ART_FIX = {503677: "22270202"}   # на VA «Брюки хлопковые Space» 21260202-2
# опечатки в текстах VA
TYPO = {"стрелкрй": "стрелкой", "Cиние": "Синие", "хопковые": "хлопковые"}

TRANSLIT = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
    ["a","b","v","g","d","e","e","zh","z","i","y","k","l","m","n","o","p","r","s","t","u","f","h","c","ch","sh","sch","","y","","e","yu","ya"]))


def slugify(t):
    t = t.lower()
    out = "".join(TRANSLIT.get(ch, ch if ch.isalnum() else "-") for ch in t)
    return re.sub(r"-+", "-", out).strip("-")


def load_va():
    P = {}
    for g in ("men", "women"):
        for i in (1, 2, 3):
            for p in json.load(open(f"dl/{g}_p{i}.json"))["carry"]["products"]:
                p["_g"] = g
                P[p["id"]] = p
    return P


def color_of(p):
    if p["article"] in PRIMARY:
        return PRIMARY[p["article"]]
    names = [c["name"] for c in p.get("colors") or []]
    c = names[0] if names else ""
    return COLOR_FIX.get(c, c)


def category(p):
    g = "Мужское" if p["_g"] == "men" else "Женское"
    name, sec = p["name"], p["section"]["url"]
    if name.startswith("Костюм-тройка") or name.startswith("Комплект"):
        sub = "Комплекты"
    elif "/suits/" in sec:
        sub = "Костюмы"
    elif re.match(r"(Олимпийка|Толстовка|Худи|Бомбер)", name):
        sub = "Олимпийки и толстовки" if g == "Мужское" else "Олимпийки"
    elif re.match(r"Брюки", name):
        sub = "Брюки"
    elif re.match(r"Шорты", name):
        sub = "Шорты"
    elif re.match(r"(Футболка|Лонгслив)", name):
        sub = "Футболки"
    else:
        raise SystemExit("нет раздела: %s %s" % (p["article"], name))
    cat = "%s;%s>>>%s" % (g, g, sub)
    if "Ватаным" in name:
        cat += ";Капсулы;Капсулы>>>Ватаным"
    return cat


def material(consist):
    m = re.search(r"[а-яё]+", consist.lower())
    return m.group(0).capitalize() if m else ""


def lining(consist):
    m = re.search(r"подклад:?\s*\d+%\s*([а-яё]+)", consist.lower())
    if not m:
        return "Без подклада"
    w = m.group(1)
    return {"шелк": "Шёлк", "шёлк": "Шёлк"}.get(w, w.capitalize())


def style(p):
    sec = p["section"]["url"]
    return "Спортивный" if ("tracksuits" in sec or "sportswear" in sec) else "Повседневный"


def text_of(p):
    d = p.get("description") or ""
    for a, b in TYPO.items():
        d = d.replace(a, b)
    parts = [x.strip(" -–—\t\r") for x in d.split("\n")]
    parts = [x for x in parts if x]
    t = " ".join(x if x.endswith((".", "!", "?")) else x + "." for x in parts)
    consist = re.sub(r"\s+", " ", (p.get("consist") or "").strip()).rstrip(".")
    if consist:
        t += " Состав: " + consist + "."
    return t


def plan():
    P = load_va()
    sel = json.load(open("selection.json"))
    site_slugs = set()
    for x in json.load(open("site/site_all.json")):
        u = (x.get("url") or "").rstrip("/")
        if "/p/" in u:
            site_slugs.add(u.split("/p/")[-1])
    items, seen = [], {}
    for pid in sel["men"] + sel["women"]:
        p = P[pid]
        col = color_of(p)
        base = slugify("%s %s" % (p["name"], col))
        if p["_g"] == "women":
            base = "zh-" + base
        items.append(dict(p=p, col=col, base=base))
        seen[base] = seen.get(base, 0) + 1
    out = []
    for it in items:
        p, base = it["p"], it["base"]
        art = ART_FIX.get(p["id"], p["article"])
        slug = base
        if seen[base] > 1 or base in site_slugs:
            slug = base + "-" + slugify(art)
        out.append(dict(id=p["id"], g=p["_g"], art=art, name=p["name"].replace("  ", " ").strip(),
                        col=it["col"], slug=slug, cat=category(p),
                        price="%.2f" % float(p["price"]),
                        old="%.2f" % float(p["priceNotDiscount"]) if p["discountPercent"] else "",
                        va_price=p["price"], disc=p["discountPercent"],
                        text=text_of(p), mat=material(p.get("consist") or ""),
                        lin=lining(p.get("consist") or ""), style=style(p),
                        season="Зима" if "winter tale" in p["name"].lower() else "Всесезон",
                        capsule="Ватаным" if "Ватаным" in p["name"] else "",
                        photos=[m["url"] for m in (p.get("mediaFiles") or [])],
                        va_url="https://vipavenue.ru" + p["url"]))
    assert len({x["slug"] for x in out}) == len(out), "адреса повторяются"
    return out


def photos(dst):
    os.makedirs(dst, exist_ok=True)
    os.makedirs("src1", exist_ok=True)
    report = []
    for it in plan():
        src = "src1/%s.webp" % it["slug"]
        u = it["photos"][0]
        for url in (u, u, u.replace("media2.vipavenue.ru", "cdn.vipavenue.ru")):
            if os.path.exists(src) and os.path.getsize(src) > 0:
                break
            subprocess.run(["curl", "-sS", "--retry", "4", "--retry-all-errors", "-o", src, url])
        assert os.path.getsize(src) > 0, u
        im = Image.open(src).convert("RGB")
        a = np.asarray(im).astype(np.float32)
        h, w, _ = a.shape
        k = max(8, w // 40)
        corners = np.concatenate([a[:k, :k].reshape(-1, 3), a[:k, -k:].reshape(-1, 3),
                                  a[-k:, :k].reshape(-1, 3), a[-k:, -k:].reshape(-1, 3)])
        white = float(corners.min(1).mean())
        # умножение на цвет фона: фон исходника (обычно белый, бывает чуть розовый — 255/251/253)
        # становится ровно #F4F3EF, вещь темнеет не больше чем на 4 %
        src_bg = np.median(corners, axis=0)
        k_rgb = np.array(BG, np.float32) / np.maximum(src_bg, 1)
        out = Image.fromarray(np.clip(np.rint(a * k_rgb), 0, 255).astype(np.uint8))
        # все первые фото — 900×1200 (3:4), как остальные карточки: 4:5 уменьшаем и добавляем
        # фон сверху и снизу (фон ровный, стыка нет)
        if (w, h) != (900, 1200):
            out.thumbnail((900, 1200), Image.LANCZOS)
            canvas = Image.new("RGB", (900, 1200), BG)
            canvas.paste(out, ((900 - out.width) // 2, (1200 - out.height) // 2))
            out = canvas
        out.save(os.path.join(dst, it["slug"] + ".jpg"), quality=90, optimize=True)
        report.append((it["slug"], w, h, round(white, 1)))
    for r in report:
        if r[3] < 250:
            print("фон не белый:", r)
    print("готово фото:", len(report), "| размеры:", sorted({(r[1], r[2]) for r in report}))


def build_csv(dst, base_url, out_csv):
    rows = []
    for it in plan():
        f = os.path.join(dst, it["slug"] + ".jpg")
        assert os.path.exists(f), f
        par = {k: "" for k in HEADER}
        par.update({"Brand": "2young4u", "Category": it["cat"], "Title": it["name"], "Text": it["text"],
                    "Photo": " ".join([base_url.rstrip("/") + "/" + it["slug"] + ".jpg"] + it["photos"][1:]),
                    "External ID": it["slug"],
                    "Characteristics:Основной материал": it["mat"], "Characteristics:Подклад": it["lin"],
                    "Characteristics:Цвет": it["col"], "Characteristics:Сезон": it["season"],
                    "Characteristics:Стиль": it["style"], "Characteristics:Капсула": it["capsule"]})
        for d in ("Weight", "Length", "Width", "Height"):
            par[d] = "0"
        rows.append(par)
        hexv = COLOR_HEX.get(it["col"], "#cccccc")
        for s in SIZES:
            v = {k: "" for k in HEADER}
            v.update({"SKU": it["art"], "Title": "%s - %s - %s" % (it["name"], s, it["col"]),
                      "Price": it["price"], "Price Old": it["old"], "Quantity": str(QTY),
                      "Editions": "Размер:%s;Цвет:%s %s" % (s, it["col"], hexv),
                      "External ID": "%s-%s" % (it["slug"], s.lower()), "Parent UID": it["slug"]})
            for d in ("Weight", "Length", "Width", "Height"):
                v[d] = "0"
            rows.append(v)
    with open(out_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        w.writerows(rows)
    json.dump(plan(), open("plan.json", "w"), ensure_ascii=False, indent=1)
    print("%s — товаров: %d, строк: %d" % (out_csv, len(rows) // 7, len(rows)))


if __name__ == "__main__":
    if sys.argv[1] == "photos":
        photos(sys.argv[2])
    elif sys.argv[1] == "csv":
        build_csv(sys.argv[2], sys.argv[3], sys.argv[4])
