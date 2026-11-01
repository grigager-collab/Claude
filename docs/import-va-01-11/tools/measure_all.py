# где вещь/модель по горизонтали на каждом фото импорта (логика k35/tools/measure.py)
import sys, os, json
import numpy as np
from PIL import Image
def measure(path):
    im = Image.open(path).convert('RGB'); W0, H0 = im.size
    im.thumbnail((450, 600))
    a = np.asarray(im).astype(np.float32); h, w, _ = a.shape
    edge = max(4, w // 40)
    L = np.median(a[:, :edge], axis=1); R = np.median(a[:, -edge:], axis=1)
    t = np.linspace(0, 1, w)[None, :, None]
    bg = L[:, None, :] * (1 - t) + R[:, None, :] * t
    d = np.sqrt(((a - bg) ** 2).sum(2))
    corner = np.concatenate([a[:h // 10, :w // 10].reshape(-1, 3), a[:h // 10, -w // 10:].reshape(-1, 3)]).mean(0)
    light = corner.min() > 235
    m = d > (28 if not light else 18)
    cols = m.sum(0); rows = m.sum(1)
    xs = np.where(cols > h * 0.02)[0]; ys = np.where(rows > w * 0.01)[0]
    if not len(xs) or not len(ys):
        return None
    x0, x1, y0, y1 = xs[0], xs[-1], ys[0], ys[-1]
    top = y0 + int((y1 - y0) * 0.6)
    mids = []
    for y in range(y0, top, 2):
        r = np.where(m[y])[0]
        if len(r) > w * 0.02:
            mids.append((r[0] + r[-1]) / 2)
    body = float(np.median(mids)) / w if mids else (x0 + x1) / 2 / w
    touch = bool(x0 <= edge * 2 or x1 >= w - edge * 2)
    return dict(size=[W0, H0], fon='светлый' if light else 'серый', corner=[round(float(v)) for v in corner],
                x0=round(x0 / w, 3), x1=round(x1 / w, 3), y0=round(y0 / h, 3), y1=round(y1 / h, 3),
                box=round((x0 + x1) / 2 / w, 3), body=round(body, 3), touch=touch)
res = {}
for d in sys.argv[2:]:
    for f in sorted(os.listdir(d)):
        try:
            res[os.path.join(d, f)] = measure(os.path.join(d, f))
        except Exception as e:
            res[os.path.join(d, f)] = {'err': str(e)}
json.dump(res, open(sys.argv[1], 'w'), ensure_ascii=False, indent=0)
print('измерено', len(res))
