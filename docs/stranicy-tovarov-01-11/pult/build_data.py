# Данные для пульта: pages.json + миниатюры главных фото -> data.json
import base64, io, json, re, sys
from PIL import Image
SRC = '/home/user/Claude/docs/stranicy-tovarov-01-11/pages.json'
FOTO = '/home/user/Claude/docs/import-va-01-11/foto1/%s.jpg'
ORDER_G = ['Мужское', 'Женское']
ORDER_S = ['Костюмы', 'Комплекты', 'Олимпийки и толстовки', 'Олимпийки', 'Брюки', 'Шорты', 'Футболки']
P = json.load(open(SRC))
out = []
for p in P:
    im = Image.open(FOTO % p['slug']).convert('RGB')
    im.thumbnail((120, 160), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'JPEG', quality=74, optimize=True, progressive=True)
    secs = []
    for t, body in re.findall(r'<div data-title="([^"]+)">(.*?)</div>', p['block'], re.S):
        secs.append([t, re.findall(r'<p>(.*?)</p>', body)])
    out.append(dict(s=p['slug'], n=p['name'], c=p['color'], a=p['art'], g=p['gender'], sec=p['section'],
                    pr=p['price'], old=p['old'], pt=p['page_title'], st=p['seo_title'], sd=p['seo_descr'],
                    sh=p['short'], b=p['block'], x=secs,
                    th='data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()))
out.sort(key=lambda d: (ORDER_G.index(d['g']), ORDER_S.index(d['sec'])))
s = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
s = s.replace('</', '<\\/')   # безопасно внутри <script>
open(sys.argv[1], 'w', encoding='utf-8').write(s)
print(len(out), 'товаров,', len(s) // 1024, 'КБ')
