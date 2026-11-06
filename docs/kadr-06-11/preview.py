import json, numpy as np
from PIL import Image, ImageDraw, ImageFont
M = {x['slugp']: x for x in json.load(open('kadr/measured.json')) if x['slugp']}
OLD = json.load(open('kadr/measured.json'))
BG = {'kostyum-shelk-vatanym': None, 'kostyum-povsednevnyy-vatanym': None, 'kostyum-vatanym-print': None, 'kostyum-sportivnyy-vatanym': None,
      'kostyum-hlopkovyy-winter-tale-siniy': 0.89, 'tolstovka-hlopkovaya-siniy': None, 'bryuki-sportivnye-siniy': None,
      'olimpiyka-s-printom-vatanym-chernyy': 0.80}
OLDF = {'костюм': 0.80, 'низ': 0.70, 'верх': 0.56}
C = 4 / 3; F, WMAX = 0.89, 0.88
TW, TH = 210, 280
BGC = np.array([244, 243, 239])
def R_of(x, mode):
    r = x['bbox']; pw, ph, a = r[2] - r[0], r[3] - r[1], r[4]
    if mode == 'now':
        if x['slugp'] not in BG: return None
        f = BG[x['slugp']] or OLDF[x['cat']]; return min(f * C / (ph * a), 0.84 / pw)
    return min(F * C / (ph * a), WMAX / pw)
def tile(x, mode):
    t = np.tile(BGC, (TH, TW, 1)).astype(np.uint8)
    im = Image.open('kadr/src/' + x['file'] + '.bin').convert('RGB')
    R = R_of(x, mode) if isinstance(x['bbox'], list) else None
    if R is None:
        arr = np.asarray(im.resize((TW, TH), Image.LANCZOS))
        return Image.fromarray(np.minimum(arr, t))
    r = x['bbox']; a = r[4]
    w = int(round(R * TW)); h = int(round(R * TW * a))
    left = (0.5 - (r[0] + r[2]) / 2 * R) * TW; top = (C / 2 - (r[1] + r[3]) / 2 * a * R) * TW
    arr = np.asarray(im.resize((w, h), Image.LANCZOS))
    x0, y0 = int(round(left)), int(round(top))
    sx0, sy0 = max(0, -x0), max(0, -y0); dx0, dy0 = max(0, x0), max(0, y0)
    cw, chh = min(w - sx0, TW - dx0), min(h - sy0, TH - dy0)
    t[dy0:dy0+chh, dx0:dx0+cw] = np.minimum(t[dy0:dy0+chh, dx0:dx0+cw], arr[sy0:sy0+chh, sx0:sx0+cw])
    return Image.fromarray(t)
def pick(title_part, cat=None):
    for x in OLD:
        if title_part in x['slugp']: return x
    raise KeyError(title_part)
SEL = ['kostyum-hlopkovyy-winter-tale-siniy', 'kostyum-gorodskoy-forest-zelenyy', 'kostyum-povsednevnyy-space-siniy', 'kostyum-sportivnyy-vatanym',
       'bryuki-sportivnye-siniy', 'bryuki-hlopkovye-forest-zelenyy', 'bryuki-hlopkovye-space-siniy-21260202', 'shorty-hlopkovye-space-siniy',
       'olimpiyka-vatanym', 'tolstovka-hlopkovaya-siniy', 'olimpiyka-hlopkovaya-chernyy', 'olimpiyka-klassicheskaya-ocean-siniy',
       'futbolka-forest-zelenyy', 'zh-kostyum-hlopkovyy-winter-tale-siniy']
F1 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
F2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
F3 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
G = 14; COLS = 2
cell_w = TW * 2 + G; cell_h = TH + 46
W = COLS * cell_w + (COLS + 1) * 28; rows = (len(SEL) + COLS - 1) // COLS
H = 92 + rows * (cell_h + 26)
sh = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(sh)
d.text((28, 16), 'Слева — сейчас на сайте, справа — будет.', fill='black', font=F2)
d.text((28, 38), 'Вещь по центру, высота 89 % плитки, как у Winter tale; ширина не больше 88 %.', fill='black', font=F1)
for i, s in enumerate(SEL):
    x = M.get(s) or pick(s)
    cx = 28 + (i % COLS) * (cell_w + 28); cy = 82 + (i // COLS) * (cell_h + 26)
    sh.paste(tile(x, 'now'), (cx, cy)); sh.paste(tile(x, 'new'), (cx + TW + G, cy))
    d.text((cx, cy + TH + 6), x['title'][:34], fill='black', font=F2)
    d.text((cx, cy + TH + 25), 'сейчас', fill=(120, 120, 120), font=F1)
    d.text((cx + TW + G, cy + TH + 25), 'будет', fill=(0, 110, 60), font=F1)
sh.save('kadr/preview.jpg', quality=85)
print(sh.size)
