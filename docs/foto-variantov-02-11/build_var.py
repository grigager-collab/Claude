# Фото у размеров (вариантов) = главное фото товара. Галерею товара не трогаем (у родителя Photo пусто).
import csv, json, html, re, sys
OUT = sys.argv[1]
A = {p.get('externalid'): p for p in json.load(open('site_now.json'))}
rows = list(csv.DictReader(open('/home/user/Claude/docs/stranicy-tovarov-01-11/import-kratkie-opisaniya.csv', encoding='utf-8'), delimiter=';'))
head = list(rows[0].keys()); head.insert(head.index('Text') + 1, 'Photo')
num = lambda s: str(s or '').replace(' ', '').replace('\xa0', '')
todo, skip = [], []
for r in rows:
    if not r['Parent UID']:
        p = A[r['External ID']]
        (skip if all(e.get('img') for e in p['editions']) else todo).append(r['External ID'])
def build(ids, fn):
    n = 0
    with open(fn, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=head, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in rows:
            pid = r['Parent UID'] or r['External ID']
            if pid not in ids: continue
            p = A[pid]; r = dict(r)
            main = json.loads(p['gallery'])[0]['img']
            if not r['Parent UID']:
                live_text = html.unescape(re.sub(r'<br\s*/?>', '\n', p.get('text') or '')).strip()
                assert live_text == r['Text'], (pid, live_text[:60], r['Text'][:60])
                assert p['title'] == r['Title']
                r['Photo'] = ''; n += 1
            else:
                e = {x['externalid']: x for x in p['editions']}[r['External ID']]
                assert e['sku'] == r['SKU']
                r['Quantity'] = num(e['quantity']); r['Price'] = num(e['price']); r['Price Old'] = num(e['priceold'])
                r['Photo'] = main
            w.writerow(r)
    return n
test = ['kostyum-povsednevnyy-volcano-korichnevyy']
assert test[0] in todo, test
print('тест:', build(set(test), OUT + '/test-1-tovar.csv'), 'товар')
print('все:', build(set(todo) - set(test), OUT + '/foto-variantov-ostalnye.csv'), 'товаров; уже с фото (пропущены):', skip)
