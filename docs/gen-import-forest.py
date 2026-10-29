# -*- coding: utf-8 -*-
"""
Зелёная коллекция Forest (29.10.2026) — 8 новых карточек.

Источник: таблица Кристины «Новые артикулы 2young4 U.xlsx» (цены, размеры,
остатки, состав, названия) + фото с Яндекс.Диска «04 - зеленый интерлок и 2 фут»,
папка «900:1200». Фото отобраны и пережаты скриптом docs/forest-foto.py,
лежат в images/forest/<артикул>/01.jpg… — Tilda скачивает их по прямым ссылкам.

ЗАПУСК:
    python3 docs/gen-import-forest.py

ПОЛУЧАЕТСЯ:
    docs/import-forest-zelenyy.csv  — файл импорта в каталог Tilda
    docs/bloki-forest.html          — тексты аккордеонов для страниц /p/…

Описания, состав и параметры модели — с VipAvenue (docs/forest-vipavenue.json,
снято 29.10.2026 со страницы бренда): Григорий — «если чего-то нет у нас, ориентир
VipAvenue». Свои тексты в PRODUCTS — запасные, на случай если товара там нет.

Формат CSV — как в gen-import-csv.py (правила в docs/tilda-reference.md, разд. 16).
⚠️ ПРИ ИМПОРТЕ: «Группировка вариантов товара» → «Группировать по Parent UID».
"""
import csv
import json
import os

BRANCH = "claude/project-thread-2noe0n"
RAW = "https://raw.githubusercontent.com/grigager-collab/Claude/%s/images/forest" % BRANCH
HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "..", "images", "forest")

# В таблице Кристины размеры M, L, XL, XXL. На сайте пишем 2XL (как у всех товаров).
SIZES = ["M", "L", "XL", "2XL"]
QTY = 5                       # «Остаток на складе 2YOUNG4U» из таблицы
COLOR = "Зелёный"
HEX = "#4a6741"               # тот же зелёный, что уже есть в каталоге
SOSTAV = "75% хлопок, 20% полиэстер, 5% эластан"

CAT_SUITS = "Мужское;Мужское>>>Костюмы"
CAT_SETS = "Мужское;Мужское>>>Комплекты"
CAT_HOODIES = "Мужское;Мужское>>>Олимпийки и толстовки"
CAT_PANTS = "Мужское;Мужское>>>Брюки"
CAT_TSHIRTS = "Мужское;Мужское>>>Футболки"

CRUMB = {CAT_SUITS: ("Костюмы", "/men/suits"), CAT_SETS: ("Комплекты", "/men/sets"),
         CAT_HOODIES: ("Олимпийки и толстовки", "/men/hoodies"),
         CAT_PANTS: ("Брюки", "/men/trousers"), CAT_TSHIRTS: ("Футболки", "/men/tshirts")}

# Куски описаний — общие у вещей, из которых собраны костюмы и тройки
JACKET = ("Олимпийка полуприлегающего силуэта с длинными рукавами, эластичными "
          "манжетами и поясом, {collar}, прорезными карманами, застежкой на молнию "
          "и вышитым {logo} логотипом бренда.")
STOYKA = "воротником-стойкой"
DICAPRIO = "отложным воротником"
PANTS = ("Брюки прямого кроя со стандартной посадкой, эластичным поясом на кулиске, "
         "прорезными карманами и простроченными стрелками, которые визуально "
         "вытягивают силуэт.")
TEE_BEIGE = ("Бежевая футболка прямого кроя с короткими рукавами и круглым вырезом "
             "горловины завершает образ.")

PRODUCTS = [
 dict(sku="22270811", price="29900.00", cat=CAT_SUITS, style="Повседневный",
      title="Костюм в городском стиле Forest", slug="kostyum-gorodskoy-forest-zelenyy",
      text=["Зелёный костюм из смесового хлопка от 2YOUNG4U.",
            JACKET.format(collar=DICAPRIO, logo="в тон"), PANTS]),
 dict(sku="22270812", price="27900.00", cat=CAT_SUITS, style="Спортивный",
      title="Костюм в спортивном стиле Forest", slug="kostyum-sportivnyy-forest-zelenyy",
      text=["Зелёный костюм из смесового хлопка от 2YOUNG4U.",
            JACKET.format(collar=STOYKA, logo="в тон"), PANTS]),
 dict(sku="22270821", price="30900.00", cat=CAT_SETS, style="Повседневный",
      title="Костюм-тройка в городском стиле Forest",
      slug="kostyum-troyka-gorodskoy-forest-zelenyy",
      text=["Зелёный костюм-тройка из смесового хлопка от 2YOUNG4U: олимпийка, "
            "брюки и бежевая футболка.",
            JACKET.format(collar=DICAPRIO, logo="бежевым"), PANTS, TEE_BEIGE]),
 dict(sku="22270822", price="29900.00", cat=CAT_SETS, style="Спортивный",
      title="Костюм-тройка в спортивном стиле Forest",
      slug="kostyum-troyka-sportivnyy-forest-zelenyy",
      text=["Зелёный костюм-тройка из смесового хлопка от 2YOUNG4U: олимпийка, "
            "брюки и бежевая футболка.",
            JACKET.format(collar=STOYKA, logo="бежевым"), PANTS, TEE_BEIGE]),
 dict(sku="22270801", price="15900.00", cat=CAT_HOODIES, style="Спортивный",
      title="Олимпийка хлопковая Forest", slug="olimpiyka-hlopkovaya-forest-zelenyy",
      text=["Зелёная олимпийка из смесового хлопка от 2YOUNG4U.",
            "Модель полуприлегающего силуэта с длинными рукавами, эластичными "
            "манжетами и поясом, воротником-стойкой, прорезными карманами, "
            "застежкой на молнию и вышитым в тон логотипом бренда."]),
 dict(sku="22270803", price="16900.00", cat=CAT_HOODIES, style="Повседневный",
      title="Олимпийка повседневная Forest", slug="olimpiyka-povsednevnaya-forest-zelenyy",
      text=["Зелёная олимпийка из смесового хлопка от 2YOUNG4U.",
            "Модель полуприлегающего силуэта с длинными рукавами, эластичными "
            "манжетами и поясом, отложным воротником, прорезными карманами, "
            "застежкой на молнию и вышитым в тон логотипом бренда."]),
 dict(sku="22270802", price="13150.00", cat=CAT_PANTS, style="Повседневный",
      title="Брюки хлопковые Forest", slug="bryuki-hlopkovye-forest-zelenyy",
      text=["Зелёные брюки из смесового хлопка от 2YOUNG4U.",
            "Модель прямого кроя со стандартной посадкой, эластичным поясом на "
            "кулиске, прорезными карманами и простроченными стрелками, которые "
            "визуально вытягивают силуэт. Брюки впишутся в городской стиль и "
            "дополнят повседневные образы."]),
 dict(sku="22270709", price="4500.00", cat=CAT_TSHIRTS, style="Повседневный",
      title="Футболка Forest", slug="futbolka-forest-zelenyy",
      text=["Зелёная футболка из интерлока на основе хлопка от 2YOUNG4U.",
            "Модель прямого кроя с короткими рукавами и круглым вырезом горловины "
            "с трикотажной окантовкой. Футболка станет базой как для спортивных "
            "образов, так и для повседневных аутфитов с джинсами, шортами или брюками."]),
]

HEADER = ["Brand", "SKU", "Mark", "Category", "Title", "Description", "Text", "Photo",
          "Price", "Quantity", "Price Old", "Editions", "Modifications",
          "External ID", "Parent UID",
          "Characteristics:Основной материал", "Characteristics:Подклад",
          "Characteristics:Цвет", "Characteristics:Сезон", "Characteristics:Стиль",
          "Characteristics:Капсула", "Weight", "Length", "Width", "Height", "Url"]

# VipAvenue: описание списком через «-», рост/параметры модели, размер RU 52 = XL
VA = json.load(open(os.path.join(HERE, "forest-vipavenue.json"), encoding="utf-8"))
MODEL = ["Параметры модели: 187/116/80/88.", "На модели размер: XL (52)."]
for p in PRODUCTS:
    va = VA.get(p["sku"])
    if va and va.get("descr"):
        p["text"] = [t.strip(" -") for t in va["descr"].split("\n") if t.strip(" -")]
        if va.get("consist"):
            p["sostav"] = va["consist"]

CARE = [
    "Стирать при температуре до 30 °C на бережном режиме.",
    "Использовать мягкие средства для цветных тканей.",
    "Не отбеливать, не использовать агрессивные пятновыводители.",
    "Сушить в расправленном виде вдали от прямых солнечных лучей и батарей.",
    "Гладить с изнаночной стороны при средней температуре.",
]


def photos(sku):
    files = sorted(f for f in os.listdir(os.path.join(IMG, sku)) if f.endswith(".jpg"))
    return " ".join("%s/%s/%s" % (RAW, sku, f) for f in files)


def write_csv(path):
    rows = []
    for p in PRODUCTS:
        url = "https://2young4u.ru/p/" + p["slug"]
        parent = dict.fromkeys(HEADER, "")
        parent.update({"Brand": "2young4u", "Category": p["cat"], "Title": p["title"],
                       "Text": " ".join(p["text"]), "Photo": photos(p["sku"]),
                       "External ID": p["slug"],
                       "Characteristics:Основной материал": "Хлопок",
                       "Characteristics:Подклад": "Без подклада",
                       "Characteristics:Цвет": COLOR,
                       "Characteristics:Сезон": "Всесезон",
                       "Characteristics:Стиль": p["style"],
                       "Weight": "0", "Length": "0", "Width": "0", "Height": "0",
                       "Url": url})
        rows.append(parent)
        for s in SIZES:
            v = dict.fromkeys(HEADER, "")
            v.update({"SKU": p["sku"], "Title": "%s - %s - %s" % (p["title"], s, COLOR),
                      "Price": p["price"], "Quantity": str(QTY),
                      "Editions": "Размер:%s;Цвет:%s %s" % (s, COLOR, HEX),
                      "External ID": "%s-%s" % (p["slug"], s.lower()),
                      "Parent UID": p["slug"],
                      "Weight": "0", "Length": "0", "Width": "0", "Height": "0"})
            rows.append(v)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER, delimiter=";", quoting=csv.QUOTE_MINIMAL,
                           lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def write_blocks(path):
    L = ["<!-- ================================================================",
         "     ЗЕЛЁНАЯ КОЛЛЕКЦИЯ FOREST — тексты для страниц карточек (29.10.2026).",
         "     На странице товара блок «Другое → HTML-код»: выделить всё и вставить",
         "     кусок своего товара (ищи по адресу /p/… в комментарии).",
         "     Описания, состав и параметры модели — как на VipAvenue.",
         "     ================================================================ -->"]
    for p in PRODUCTS:
        name, curl = CRUMB[p["cat"]]
        L += ["", "<!-- ====== /p/%s ======" % p["slug"],
              "         %s · артикул %s ====== -->" % (p["title"], p["sku"]),
              '<div class="t2y-acc-source"',
              '     data-crumb-parent="Мужское" data-crumb-parent-url="/men"',
              '     data-crumb-name="%s" data-crumb-url="%s">' % (name, curl),
              '  <div data-title="Детали">']
        L += ["    <p>%s</p>" % esc(t) for t in p["text"]]
        L += ["    <p>Страна производства: Россия.</p>", "  </div>",
              '  <div data-title="Ткань, состав, уход">',
              "    <p>Состав: %s.</p>" % p.get("sostav", SOSTAV)]
        L += ["    <p>%s</p>" % c for c in CARE]
        L += ["  </div>", '  <div data-title="Параметры модели на фото">',
              "    <p>%s</p>" % MODEL[0], "    <p>%s</p>" % MODEL[1],
              "  </div>", "</div>"]
    open(path, "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    n = write_csv(os.path.join(HERE, "import-forest-zelenyy.csv"))
    write_blocks(os.path.join(HERE, "bloki-forest.html"))
    print("import-forest-zelenyy.csv — строк: %d, товаров: %d" % (n, len(PRODUCTS)))
