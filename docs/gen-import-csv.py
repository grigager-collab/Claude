# -*- coding: utf-8 -*-
"""
Генератор CSV для импорта товаров в каталог Tilda — 2young4u.ru.
Пересобран 07.10.2026 под решения заказчицы (docs/client-decisions.md).

ЗАПУСК:
    python3 docs/gen-import-csv.py            # все товары
    python3 docs/gen-import-csv.py men        # только мужские
    python3 docs/gen-import-csv.py women      # только женские

ПРАВИЛА ФОРМАТА (почему именно так — docs/csv-format.md):
  · колонки "Tilda UID" быть НЕ должно — иначе «Empty Uniq column: uid»
    и отвергается каждая строка;
  · у РОДИТЕЛЯ пустые: Price, Quantity, SKU, Editions;
  · у ВАРИАНТА пустые: Category и все характеристики;
  · Parent UID варианта = External ID родителя;
  · несколько разделов через ';', вложенность через '>>>', ячейка в кавычках;
    родитель указывается ОТДЕЛЬНО от подраздела — Tilda разделы НЕ наследует.

⚠️ ПРИ ИМПОРТЕ ОБЯЗАТЕЛЬНО:
    «ГРУППИРОВКА ВАРИАНТОВ ТОВАРА» → «Группировать по Parent UID».
    Список СБРАСЫВАЕТСЯ между загрузками на «по SKU». Проверять каждый раз.
"""
import csv
import sys

# ─────────────────────────── ОБЩИЕ НАСТРОЙКИ ───────────────────────────

# Единая размерная сетка: от S до 3XL. Подтверждено заказчицей 08.10.2026.
SIZES = ["S", "M", "L", "XL", "2XL", "3XL"]   # решение 08.10.2026

QTY = 10          # количество на каждый размер

# Характеристики. «Коллекция» убрана: базовой коллекции как критерия нет,
# все вещи базовые по умолчанию. «Цвет» добавлен — заказчица попросила фильтр
# по цвету, а варианты товара фильтрами Tilda не покрываются.
HEADER = ["Brand", "SKU", "Mark", "Category", "Title", "Description", "Text",
          "Price", "Quantity", "Price Old", "Editions", "Modifications",
          "External ID", "Parent UID",
          "Characteristics:Основной материал",
          "Characteristics:Подклад",
          "Characteristics:Цвет",
          "Characteristics:Сезон",
          "Characteristics:Стиль",
          "Characteristics:Капсула",
          "Weight", "Length", "Width", "Height", "Url"]

# ─────────────────────────── МУЖСКИЕ ТОВАРЫ ───────────────────────────

CAT_M_SUITS   = "Мужское;Мужское>>>Костюмы"
CAT_M_HOODIES = "Мужское;Мужское>>>Олимпийки и толстовки"
CAT_M_BLAZERS = "Мужское;Мужское>>>Мягкие пиджаки"
CAT_M_PANTS   = "Мужское;Мужское>>>Брюки"
CAT_M_SHORTS  = "Мужское;Мужское>>>Шорты"

CAPSULE_VATANYM = ";Капсулы;Капсулы>>>Ватаным"

MEN = [
 dict(slug="kostyum-shelk-vatanym", sku="21260214", price="34900.00",
      title="Костюм с шёлком Ватаным", cat=CAT_M_SUITS + CAPSULE_VATANYM,
      color="Синий", hex="#073763", style="Деловой",
      lining="Шёлк", capsule="Ватаным",
      text="Тёмно-синий костюм с шёлковым воротником — сдержанный силуэт и зауженные "
           "брюки со стрелкой. Держит форму весь день и одинаково уместен на встрече "
           "и на вечернем выходе."),
 dict(slug="kostyum-povsednevnyy-vatanym", sku="21260615", price="28900.00",
      title="Костюм повседневный Ватаным", cat=CAT_M_SUITS + CAPSULE_VATANYM,
      color="Серый", hex="#cccccc", style="Повседневный", capsule="Ватаным",
      text="Серый костюм в стиле френч — прямой силуэт и лаконичный крой без лишних "
           "деталей. Основа повседневного гардероба: сочетается с футболкой так же "
           "легко, как с рубашкой."),
 dict(slug="kostyum-vatanym-print", sku="21260215", price="27700.00",
      title="Костюм Ватаным с принтом", cat=CAT_M_SUITS + CAPSULE_VATANYM,
      color="Синий", hex="#073763", style="Повседневный", capsule="Ватаным",
      text="Тёмно-синий костюм с вышивкой из шести символов на спине. Спокойный силуэт "
           "и акцент, который виден только со спины, — для тех, кто предпочитает детали, "
           "а не громкие логотипы."),
 dict(slug="kostyum-sportivnyy-vatanym", sku="21260512", price="26800.00",
      title="Костюм спортивный Ватаным", cat=CAT_M_SUITS + CAPSULE_VATANYM,
      color="Белый", hex="#fffae5", style="Спортивный", capsule="Ватаным",
      text="Молочный спортивный костюм из смесового хлопка с гербом на груди. Зауженные "
           "брюки со стрелкой держат аккуратную линию, а мягкое полотно позволяет носить "
           "его весь день."),
]

# ─────────────────────────── ЖЕНСКИЕ ТОВАРЫ ───────────────────────────

CAT_W_SUITS   = "Женское;Женское>>>Костюмы"
CAT_W_HOODIES = "Женское;Женское>>>Олимпийки"
CAT_W_BLAZERS = "Женское;Женское>>>Мягкие пиджаки"

WOMEN = [
 dict(slug="zh-kostyum-vatanym-milk", sku="26210505/02", price="25800.00",
      title="Костюм с гербом Ватаным", cat=CAT_W_SUITS + CAPSULE_VATANYM,
      color="Белый", hex="#fffae5", style="Повседневный", capsule="Ватаным",
      text="Молочный костюм из смесового хлопка с гербом — мягкая линия плеча и "
           "свободная посадка. Носится и комплектом, и по отдельности с базовыми вещами."),
 dict(slug="zh-olimpiyka-vatanym-milk", sku="26210505", price="14900.00",
      title="Олимпийка с гербом Ватаным", cat=CAT_W_HOODIES + CAPSULE_VATANYM,
      color="Белый", hex="#fffae5", style="Спортивный", capsule="Ватаным",
      text="Молочная олимпийка с гербом и воротником-стойкой. Лёгкая, держит форму "
           "и одинаково хорошо садится поверх футболки и платья."),
 dict(slug="zh-kostyum-vatanym-black", sku="26190101", price="23800.00",
      title="Костюм Ватаным чёрный", cat=CAT_W_SUITS + CAPSULE_VATANYM,
      color="Чёрный", hex="#1d1d1d", style="Повседневный", capsule="Ватаным",
      text="Чёрный костюм капсулы Ватаным — прямой силуэт без лишних деталей. "
           "Тот случай, когда один комплект закрывает и работу, и вечер."),
 dict(slug="zh-french-milk", sku="26210502", price="16800.00",
      title="Френч хлопковый молочный", cat=CAT_W_BLAZERS,
      color="Белый", hex="#fffae5", style="Деловой", capsule="",
      text="Молочный френч из смесового хлопка — воротник-стойка, накладные карманы, "
           "аккуратная посадка. Заменяет пиджак там, где он кажется слишком строгим."),
]

# ─────────────────────────── СБОРКА ───────────────────────────

def build(products):
    rows = []
    for p in products:
        # --- строка-родитель ---
        r = {k: "" for k in HEADER}
        r["Brand"] = "2young4u"
        r["Category"] = p["cat"]
        r["Title"] = p["title"]
        r["Text"] = p["text"]
        r["Characteristics:Основной материал"] = p.get("material", "Хлопок")
        r["Characteristics:Подклад"] = p.get("lining", "Без подклада")
        r["Characteristics:Цвет"] = p["color"]
        # по умолчанию «Всесезон»; зимним ставим season="Зима"
        r["Characteristics:Сезон"] = p.get("season", "Всесезон")
        r["Characteristics:Стиль"] = p["style"]
        r["Characteristics:Капсула"] = p.get("capsule", "")
        r["External ID"] = p["slug"]
        for d in ("Weight", "Length", "Width", "Height"):
            r[d] = "0"
        r["Url"] = "https://2young4u.ru/p/" + p["slug"]
        rows.append(r)

        # --- строки-варианты (по одной на размер) ---
        for size in SIZES:
            v = {k: "" for k in HEADER}
            v["SKU"] = p["sku"]
            v["Title"] = "%s - %s - %s" % (p["title"], size, p["color"])
            v["Price"] = p["price"]
            v["Quantity"] = str(QTY)
            v["Editions"] = "Размер:%s;Цвет:%s %s" % (size, p["color"], p["hex"])
            v["External ID"] = "%s-%s" % (p["slug"], size.lower())
            v["Parent UID"] = p["slug"]
            for d in ("Weight", "Length", "Width", "Height"):
                v[d] = "0"
            rows.append(v)
    return rows


def write(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEADER, delimiter=";",
                           quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    parents = len([r for r in rows if not r["Parent UID"]])
    print("%s — товаров: %d, строк: %d" % (path, parents, len(rows)))


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("all", "men"):
        write(build(MEN), "/home/user/Claude/docs/import-muzhskoe.csv")
    if what in ("all", "women"):
        write(build(WOMEN), "/home/user/Claude/docs/import-zhenskoe.csv")
