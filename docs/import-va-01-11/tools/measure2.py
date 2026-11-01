# уточнённый центр модели: (1) середина фигуры по строкам, (2) середина самого длинного
# сплошного куска фигуры в строке (туловище без отставленных рук); крупные планы — отдельно
import sys, json
import numpy as np
from PIL import Image
def mask_of(path):
    im = Image.open(path).convert('RGB'); im.thumbnail((450, 600))
    a = np.asarray(im).astype(np.float32); h, w, _ = a.shape
    edge = max(4, w // 40)
    L = np.median(a[:, :edge], axis=1); R = np.median(a[:, -edge:], axis=1)
    t = np.linspace(0, 1, w)[None, :, None]
    bg = L[:, None, :] * (1 - t) + R[:, None, :] * t
    d = np.sqrt(((a - bg) ** 2).sum(2))
    corner = np.concatenate([a[:h // 10, :w // 10].reshape(-1, 3), a[:h // 10, -w // 10:].reshape(-1, 3)]).mean(0)
    return d > (18 if corner.min() > 235 else 28), w, h
def runs(row):
    idx = np.where(row)[0]
    if not len(idx): return None
    br = np.where(np.diff(idx) > 2)[0]
    starts = np.r_[idx[0], idx[br + 1]]; ends = np.r_[idx[br], idx[-1]]
    k = np.argmax(ends - starts)
    return (starts[k] + ends[k]) / 2, (idx[0] + idx[-1]) / 2
def measure(path):
    m, w, h = mask_of(path)
    area = m.mean()
    ys = np.where(m.sum(1) > w * 0.01)[0]; xs = np.where(m.sum(0) > h * 0.02)[0]
    if not len(ys) or not len(xs): return None
    y0, y1 = ys[0], ys[-1]
    torso, span = [], []
    for y in range(y0, y0 + int((y1 - y0) * 0.5), 2):
        r = runs(m[y])
        if r: torso.append(r[0]); span.append(r[1])
    return dict(area=round(float(area), 3), x0=round(xs[0] / w, 3), x1=round(xs[-1] / w, 3),
                torso=round(float(np.median(torso)) / w, 3) if torso else None,
                span=round(float(np.median(span)) / w, 3) if span else None)
M = json.load(open(sys.argv[1])); out = {}
for f in M:
    out[f] = measure(f)
json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False, indent=0)
