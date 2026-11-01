# -*- coding: utf-8 -*-
"""
Страницы /p/… для 78 товаров импорта 01.11.2026: всё с VipAvenue.

    python3 -I tools/build_pages.py <папка_вывода>

Что получается в папке:
  pages.json                     — по товару: адрес, название страницы, SEO, блок текстов
  bloki/<адрес>.html             — блок HTML-кода с текстами (аккордеоны и крошки)
  import-kratkie-opisaniya.csv   — обновление каталога: «Подробное описание» = короткий текст
                                   (его Tilda переносит на страницу при привязке блока к товару)
«Детали» = текст VipAvenue (опечатки и ё поправлены) + «В комплекте: …» у костюмов и комплектов
+ «Страна производства: Россия.»
"""
import csv, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from texts import T, FIX

SRC_CSV = '/home/user/Claude/docs/import-va-01-11/import-va-01-11.csv'
SITE = 'https://2young4u.ru'
SECTION_URL = {('Мужское', 'Костюмы'): '/men/suits', ('Мужское', 'Комплекты'): '/men/sets',
               ('Мужское', 'Олимпийки и толстовки'): '/men/hoodies', ('Мужское', 'Брюки'): '/men/trousers',
               ('Мужское', 'Шорты'): '/men/shorts', ('Мужское', 'Футболки'): '/men/tshirts',
               ('Женское', 'Костюмы'): '/women/suits', ('Женское', 'Олимпийки'): '/women/hoodies',
               ('Женское', 'Брюки'): '/women/trousers'}
# ё и опечатки VipAvenue — во всех «Деталях»
NORM = [('стрелкрй', 'стрелкой'), ('Темно-', 'Тёмно-'), ('темно-', 'тёмно-'), ('Черн', 'Чёрн'), ('черн', 'чёрн'),
        ('Желт', 'Жёлт'), ('желт', 'жёлт'), ('шелк', 'шёлк'), ('Шелк', 'Шёлк'), ('застежк', 'застёжк'),
        ('простроченн', 'прострочённ'), ('утепленн', 'утеплённ'), ('начесом', 'начёсом'), ('объемн', 'объёмн'),
        ('"велюровым начёсом"', '«велюровым начёсом»'), ('износостойкость', 'износоустойчивость'), (' еще ', ' ещё ')]
CARE = ['Стирать при температуре до 30 °C на бережном режиме.',
        'Использовать мягкие средства для цветных тканей.',
        'Не отбеливать, не использовать агрессивные пятновыводители.',
        'Сушить в расправленном виде вдали от прямых солнечных лучей и батарей.',
        'Гладить с изнаночной стороны при средней температуре.']
CARE_WOOL = ['Рекомендуется деликатная профессиональная химчистка.',
             'Не стирать в машине, не отбеливать.',
             'Сушить в расправленном виде на горизонтальной поверхности.',
             'Гладить с изнаночной стороны через влажную ткань при низкой температуре.',
             'Шёлковый подклад не выкручивать.']


def load_va():
    P = {}
    base = os.path.join(os.path.dirname(__file__), '..', 'dl')
    for g in ('men', 'women'):
        for i in (1, 2, 3):
            for p in json.load(open(os.path.join(base, '%s_p%d.json' % (g, i))))['carry']['products']:
                P[p['id']] = p
    return P


def sent(s):
    s = s.strip(' -–—\t\r')
    return s if s.endswith(('.', '!', '?')) else s + '.'


# вещи комплекта — по первым словам абзацев VipAvenue («Олимпийка …», «Брюки …», «Бежевый лонгслив …»)
GARMENTS = ['куртка-рубашка', 'пиджак', 'олимпийка', 'толстовка', 'худи', 'брюки', 'джоггеры',
            'шорты', 'футболка', 'лонгслив']


def kit(lines):
    got = []
    for line in lines[1:]:
        for w in re.findall(r'[\w-]+', line.lower())[:3]:
            if w in GARMENTS:
                if w not in got:
                    got.append(w)
                break
    if len(got) < 2:
        return None
    return 'В комплекте: %s.' % (', '.join(got[:-1]) + ' и ' + got[-1])


def details(slug, p, section):
    out = []
    for line in (p.get('description') or '').split('\n'):
        line = line.strip(' -–—\t\r')
        if not line:
            continue
        for a, b in FIX.get(slug, []) + NORM:
            line = line.replace(a, b)
        out.append(sent(line))
    if section in ('Костюмы', 'Комплекты'):
        k = kit(out)
        assert k, (slug, out)
        out.insert(1, k)
    out.append('Страна производства: Россия.')
    return out


def fabric(slug, p):
    c = re.sub(r'\s+', ' ', (p.get('consist') or '').strip())
    for a, b in FIX.get(slug, []) + NORM:
        c = c.replace(a, b)
    out = []
    m = re.match(r'(.*?)\.?\s*Подклад:\s*(.*)$', c, re.I)
    lining = None
    if m:
        c, lining = m.group(1), m.group(2)
    parts = re.split(r'\.\s*Состав 2:\s*', c)
    out.append('Состав: %s.' % parts[0].rstrip('.'))
    if len(parts) > 1:
        what = 'Лонгслив' if 'лонгслив' in (p.get('description') or '').lower() else 'Футболка'
        out.append('%s: %s.' % (what, parts[1].rstrip('.')))
    if lining:
        out.append('Подклад: %s.' % lining.rstrip('.').replace('100% ', '').replace('шелк', 'шёлк'))
    out += CARE_WOOL if 'шерсть' in c.lower() else CARE
    return out


def model(p):
    mp = p.get('modelParameters')
    if not mp:
        # прочерки: на мужских карточках код «Шапки» (часть 4) подставит 188 см и XL/L
        return ['Рост модели: — см.', 'На модели размер: —.']
    m = re.match(r'\s*([\d/]+)\s*,\s*размер на модели\s*[–-]\s*(\d+)', mp)
    params, ru = m.group(1), m.group(2)
    intl = None
    for o in p.get('offers') or []:   # «M / 44» — международный / российский
        s = (o.get('sizesString') or '').split(' / ')
        if len(s) == 2 and s[1].strip() == ru:
            intl = s[0].strip()
            break
    return ['Параметры модели: %s.' % params, 'На модели размер: %s.' % ('%s (%s)' % (intl, ru) if intl else ru + ' RU')]


def block(it, title, det, fab, mod):
    g, sub = it['cat'].split(';')[1].split('>>>')
    p = lambda xs: ' '.join('<p>%s</p>' % x for x in xs)
    return ('<!-- 2Y4U: тексты страницы товара «%s» (%s), 01.11.2026 -->\n'
            '<div class="t2y-acc-source"\n'
            '     data-crumb-parent="%s" data-crumb-parent-url="%s"\n'
            '     data-crumb-name="%s" data-crumb-url="%s">\n'
            '  <div data-title="Детали"> %s </div>\n'
            '  <div data-title="Ткань, состав, уход"> %s </div>\n'
            '  <div data-title="Параметры модели на фото"> %s </div>\n'
            '</div>\n') % (title, it['art'], g, '/men' if g == 'Мужское' else '/women',
                           sub, SECTION_URL[(g, sub)], p(det), p(fab), p(mod))


def main(dst):
    os.makedirs(os.path.join(dst, 'bloki'), exist_ok=True)
    P = load_va()
    plan = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'plan.json')))
    assert set(T) == {x['slug'] for x in plan}, set(T) ^ {x['slug'] for x in plan}
    pages = []
    for it in plan:
        p = P[it['id']]; slug = it['slug']
        short, seo_t, seo_d = T[slug]
        g, sub = it['cat'].split(';')[1].split('>>>')
        det, fab, mod = details(slug, p, sub), fabric(slug, p), model(p)
        html = block(it, it['name'], det, fab, mod)
        open(os.path.join(dst, 'bloki', slug + '.html'), 'w', encoding='utf-8').write(html)
        pages.append(dict(slug=slug, url='/p/' + slug, name=it['name'], color=it['col'], art=it['art'],
                          gender=g, section=sub, page_title='%s — %s, %s' % (it['name'], it['col'].lower(), it['art']),
                          short=short, seo_title=seo_t, seo_descr=seo_d, block=html,
                          price=it['price'], old=it['old']))
    json.dump(pages, open(os.path.join(dst, 'pages.json'), 'w'), ensure_ascii=False, indent=1)

    # обновление каталога: короткий текст в «Подробное описание»; фото не трогаем (колонки нет)
    rows = list(csv.DictReader(open(SRC_CSV, encoding='utf-8'), delimiter=';'))
    head = [h for h in rows[0].keys() if h not in ('Photo', 'Url')]
    short = {x['slug']: x['short'] for x in pages}
    with open(os.path.join(dst, 'import-kratkie-opisaniya.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=head, delimiter=';', quoting=csv.QUOTE_MINIMAL, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            if not r['Parent UID']:
                r = dict(r, Text=short[r['External ID']])
            w.writerow(r)
    # Файл со ссылками («Ссылка» товара → /p/<адрес>) собирается в самом конце, когда страницы
    # готовы, — с остатками и ценами, снятыми с сайта в тот день, чтобы импорт их не сбросил.
    print('страниц:', len(pages))


if __name__ == '__main__':
    main(sys.argv[1])
