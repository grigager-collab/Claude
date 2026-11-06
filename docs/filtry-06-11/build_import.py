# Файл импорта свойств и разделов (CSV для «Каталог товаров» → «Импорт»).
# Строки собираются из каталога на сайте как есть: название, текст, цены, старые цены, остатки, артикулы,
# варианты и фото вариантов — с сайта; меняются только Category и Characteristics (правила — pravila.py).
# Запуск: python3 build_import.py live.json out.csv [--only extid,extid | --skip extid,extid]
import csv, json, re, sys
from pravila import CHARS, SEP, sku, target

A = json.load(open(sys.argv[1]))
OUT = sys.argv[2]
only = skip = None
if len(sys.argv) > 4 and sys.argv[3] == '--only': only = set(sys.argv[4].split(','))
if len(sys.argv) > 4 and sys.argv[3] == '--skip': skip = set(sys.argv[4].split(','))
HEAD = (['Brand', 'SKU', 'Mark', 'Category', 'Title', 'Description', 'Text', 'Photo', 'Price', 'Quantity', 'Price Old', 'Editions',
         'Modifications', 'External ID', 'Parent UID'] + ['Characteristics:' + k for k in CHARS] + ['Weight', 'Length', 'Width', 'Height'])
n = lambda s: str(s or '').replace(' ', '').replace('\xa0', '')
colour = lambda v: re.sub(r'\s*#[0-9a-fA-F]{6}$', '', v)


def colour_value(p, name):
    """Цвет варианта так, как он записан в Tilda: «Коричневый #6b4423».
    API отдаёт у варианта цвет без кода («Коричневый»); если в файле написать так,
    импорт добавит товару второе значение цвета без кода (так случилось 06.11 у 75 товаров).
    Берём первое значение из набора опций товара с тем же названием — исходное, с кодом."""
    vals = next((o['values'] for o in json.loads(p.get('json_options') or '[]') if o.get('title') == 'Цвет'), [])
    return next((v for v in vals if colour(v) == name), name)
rows, report = [], []
for p in sorted(A, key=lambda p: p['title']):
    ext = p['externalid']
    if (only and ext not in only) or (skip and ext in skip): continue
    assert not p.get('descr') and not p.get('mark') and '<' not in p['text'], p['title']
    assert (p['pack_m'], p['pack_x'], p['pack_y'], p['pack_z']) == (0, 0, 0, 0), p['title']
    t, cats, why = target(p, A)
    par = {h: '' for h in HEAD}
    par.update({'Brand': p['brand'], 'Category': ';'.join(cats), 'Title': p['title'], 'Text': p['text'], 'External ID': ext,
                'Weight': '0', 'Length': '0', 'Width': '0', 'Height': '0'})
    for k in CHARS: par['Characteristics:' + k] = SEP.join(t[k])
    rows.append(par)
    for e in p['editions']:
        assert e['img'] and e['sku'] and e['externalid'], (p['title'], e)
        v = {h: '' for h in HEAD}
        v.update({'SKU': e['sku'], 'Title': '%s - %s - %s' % (p['title'], e['Размер'], colour(e['Цвет'])), 'Photo': e['img'],
                  'Price': n(e['price']), 'Quantity': n(e['quantity']), 'Price Old': n(e['priceold']),
                  'Editions': 'Размер:%s;Цвет:%s' % (e['Размер'], colour_value(p, e['Цвет'])), 'External ID': e['externalid'], 'Parent UID': ext,
                  'Weight': '0', 'Length': '0', 'Width': '0', 'Height': '0'})
        rows.append(v)
    report.append((sku(p), p['title'], cats, t, why))
with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=HEAD, delimiter=';', quoting=csv.QUOTE_MINIMAL); w.writeheader(); w.writerows(rows)
json.dump(report, open(OUT + '.report.json', 'w'), ensure_ascii=False, indent=0)
print('товаров:', len(report), 'строк:', len(rows), '→', OUT)
