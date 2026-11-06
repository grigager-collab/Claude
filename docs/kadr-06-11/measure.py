import json, re, sys
import numpy as np
from PIL import Image
items = json.load(open('kadr/items.json'))
BG = {'kostyum-shelk-vatanym': None, 'kostyum-povsednevnyy-vatanym': None, 'kostyum-vatanym-print': None, 'kostyum-sportivnyy-vatanym': None,
      'kostyum-hlopkovyy-winter-tale-siniy': 0.89, 'tolstovka-hlopkovaya-siniy': None, 'bryuki-sportivnye-siniy': None,
      'olimpiyka-s-printom-vatanym-chernyy': 0.80}
KADR = [(r'костюм|kostyum|комплект', 'костюм'), (r'брюки|шорты|bryuki|shorty', 'низ'),
        (r'олимпийк|толстовк|френч|худи|свитшот|бомбер|куртк|футболк|лонгслив|olimpiyka|tolstovka|french', 'верх')]
OLDF = {'костюм': 0.80, 'низ': 0.70, 'верх': 0.56}
def cat(t):
    for rx, c in KADR:
        if re.search(rx, t, re.I): return c
    return '?'
def bounds(path):
    im = np.asarray(Image.open(path).convert('RGB')).astype(int)
    h, w, _ = im.shape
    pts = [im[2:7, 2:7], im[2:7, w-7:w-2], im[h-7:h-2, 2:7], im[h-7:h-2, w-7:w-2]]
    cs = np.array([np.median(p.reshape(-1, 3), axis=0) for p in pts])
    if cs.min() < 225 or (cs.max(axis=0) - cs.min(axis=0)).max() > 12: return None, cs.mean(axis=0)
    bg = cs.mean(axis=0)
    delta = (bg[None, None, :] - im).max(axis=2)
    obj = delta > 14
    rows = obj.sum(axis=1); cols = obj.sum(axis=0)
    ys = np.where(rows >= 3)[0]; xs = np.where(cols >= 3)[0]
    if not len(ys) or not len(xs): return None, bg
    y0, y1, x0, x1 = ys[0], ys[-1] + 1, xs[0], xs[-1] + 1
    if x0 <= 0 or y0 <= 0 or x1 >= w or y1 >= h: return 'edge', bg
    return [round(x0 / w, 3), round(y0 / h, 3), round(x1 / w, 3), round(y1 / h, 3), round(h / w, 3)], bg
C = 4 / 3
out = []
for it in items:
    r, bg = bounds('kadr/src/' + it['file'] + '.bin')
    it['bbox'] = r if isinstance(r, list) else r; it['bgc'] = [int(x) for x in bg]
    it['cat'] = cat(it['title'] + ' ' + it['url'])
    s = it['url'].split('/p/')[-1] if '/p/' in it['url'] else ''
    it['slugp'] = s
    if isinstance(r, list):
        pw, ph, a = r[2] - r[0], r[3] - r[1], r[4]
        # как показано сейчас: в BG — кадр кода, иначе как на фото
        if s in BG:
            f = BG[s] or OLDF.get(it['cat'], 0)
            R = min(f * C / (ph * a), 0.84 / pw)
            it['now_h'] = round(ph * a * R / C, 3); it['now_w'] = round(pw * R, 3)
        else:
            it['now_h'] = round(ph, 3); it['now_w'] = round(pw, 3)
    out.append(it)
json.dump(out, open('kadr/measured.json', 'w'), ensure_ascii=False)
import collections
for c in ('костюм', 'низ', 'верх', '?'):
    xs = [x for x in out if x['cat'] == c]
    ok = [x for x in xs if isinstance(x['bbox'], list)]
    hs = sorted(x['now_h'] for x in ok)
    print(c, len(xs), 'измерено', len(ok), '| высота вещи сейчас: мин %.2f медиана %.2f макс %.2f' % (hs[0], hs[len(hs)//2], hs[-1]) if hs else '')
    for x in xs:
        if not isinstance(x['bbox'], list): print('   не измерено:', x['title'], x['bbox'], x['bgc'])
for s in ('kostyum-hlopkovyy-winter-tale-siniy', 'bryuki-hlopkovye-forest-zelenyy', 'bryuki-sportivnye-siniy', 'olimpiyka-vatanym', 'tolstovka-hlopkovaya-siniy', 'olimpiyka-hlopkovaya-chernyy', 'olimpiyka-klassicheskaya-ocean-siniy', 'kostyum-gorodskoy-forest-zelenyy'):
    x = [i for i in out if i['slugp'] == s][0]
    print('%-40s %s  сейчас высота %.2f ширина %.2f, сверху %.3f снизу %.3f (по фото)' % (s, x['cat'], x['now_h'], x['now_w'], x['bbox'][1], 1 - x['bbox'][3]))
