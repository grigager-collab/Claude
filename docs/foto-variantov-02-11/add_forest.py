# Добавить 8 товаров Forest в файл фото размеров: строки собраны из каталога на сайте как есть
import csv, json, sys
F = sys.argv[1]
A = [p for p in json.load(open('site_now.json')) if 'forest' in p['url']]
CAT = {'364366089229': 'Мужское', '721916436563': 'Мужское>>>Костюмы', '340704419763': 'Мужское>>>Комплекты',
       '184306918613': 'Мужское>>>Олимпийки и толстовки', '398503895993': 'Мужское>>>Брюки', '140064050063': 'Мужское>>>Футболки'}
num = lambda s: str(s or '').replace(' ', '').replace('\xa0', '')
rows = list(csv.DictReader(open(F, encoding='utf-8'), delimiter=';'))
head = list(rows[0].keys())
assert len(A) == 8
for p in A:
    assert '<' not in p['text'] and '&' not in p['text'], p['title']
    parts = [str(x) for x in json.loads(p['partuids'])]
    ch = {c['title']: c['value'] for c in p['characteristics']}
    main = json.loads(p['gallery'])[0]['img']
    par = {h: '' for h in head}
    par.update({'Brand': p['brand'], 'Category': ';'.join(CAT[x] for x in parts), 'Title': p['title'], 'Text': p['text'],
                'External ID': p['externalid'], 'Weight': '0', 'Length': '0', 'Width': '0', 'Height': '0'})
    for t in ('Основной материал', 'Подклад', 'Цвет', 'Сезон', 'Стиль', 'Капсула'):
        par['Characteristics:' + t] = ch.get(t, '')
    rows.append(par)
    for e in p['editions']:
        v = {h: '' for h in head}
        v.update({'SKU': e['sku'], 'Title': '%s - %s - %s' % (p['title'], e['Размер'], e['Цвет']), 'Photo': main,
                  'Price': num(e['price']), 'Quantity': num(e['quantity']), 'Price Old': num(e['priceold']),
                  'Editions': 'Размер:%s;Цвет:%s' % (e['Размер'], e['Цвет']), 'External ID': e['externalid'],
                  'Parent UID': p['externalid'], 'Weight': '0', 'Length': '0', 'Width': '0', 'Height': '0'})
        rows.append(v)
with open(F, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=head, delimiter=';', quoting=csv.QUOTE_MINIMAL); w.writeheader(); w.writerows(rows)
print('товаров в файле:', sum(1 for r in rows if not r['Parent UID']), 'строк:', len(rows))
