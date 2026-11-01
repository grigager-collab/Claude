# превью импорта: первое фото (уже на фоне #F4F3EF), название, артикул, цена, раздел
import json, sys, os
from PIL import Image, ImageDraw, ImageFont
dst = sys.argv[1]; P = json.load(open('plan.json'))
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
FB = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
FT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
ORDER = ['Костюмы', 'Комплекты', 'Олимпийки и толстовки', 'Олимпийки', 'Брюки', 'Шорты', 'Футболки']
def sub(c): return c.split(';')[1].split('>>>')[1]
def fit(d, t, font, w):
    if d.textlength(t, font=font) <= w: return t
    while t and d.textlength(t + '…', font=font) > w: t = t[:-1]
    return t + '…'
def sheet(items, out, title):
    items = sorted(items, key=lambda x: (ORDER.index(sub(x['cat'])), x['name']))
    TW, TH = 180, 240; cols = 6; rows = (len(items) + cols - 1) // cols
    S = Image.new('RGB', (cols * (TW + 12) + 12, 50 + rows * (TH + 66)), 'white'); d = ImageDraw.Draw(S)
    d.text((12, 14), title, font=FT, fill=(0, 0, 0))
    for k, it in enumerate(items):
        im = Image.open(os.path.join(dst, 'foto1', it['slug'] + '.jpg')).convert('RGB'); im.thumbnail((TW, TH))
        x = 12 + (k % cols) * (TW + 12); y = 50 + (k // cols) * (TH + 66); S.paste(im, (x, y))
        price = int(float(it['price'])); disc = (' (VA −%d%%)' % it['disc']) if it['disc'] else ''
        d.text((x, y + TH + 4), fit(d, it['name'], FB, TW), font=FB, fill=(0, 0, 0))
        d.text((x, y + TH + 22), fit(d, '%s · %s ₽%s' % (it['art'], format(price, ',').replace(',', ' '), disc), F, TW), font=F, fill=(0, 0, 0))
        d.text((x, y + TH + 40), fit(d, sub(it['cat']) + (' · Ватаным' if it['capsule'] else ''), F, TW), font=F, fill=(120, 120, 120))
    S.save(out, quality=85); print(out, S.size, len(items))
men = [p for p in P if p['g'] == 'men']; women = [p for p in P if p['g'] == 'women']
sheet(men, dst + '/prevyu-muzhskoe.jpg', 'Мужское — %d новых товаров (первое фото на фоне #F4F3EF)' % len(men))
sheet(women, dst + '/prevyu-zhenskoe.jpg', 'Женское — %d новых товаров' % len(women))
