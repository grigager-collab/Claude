# сдвиг модели в центр. Открывшийся край: ровный тон фона у края кадра (по строкам, сглаженный)
# плюс зерно фото, отражённое от края, — без «зеркального» перелома градиента у стыка.
# 4000×5000 уменьшаем до 1600×2000
import json, os, sys
import numpy as np
from PIL import Image, ImageFilter
def fill_strip(a, k, side):
    """полоса шириной k для левого (side='L') или правого края"""
    h, w, _ = a.shape
    src = a[:, :k] if side == 'L' else a[:, w - k:]
    blur = np.asarray(Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.GaussianBlur(10))).astype(np.float32)
    edge = blur[:, :6].mean(1) if side == 'L' else blur[:, w - 6:].mean(1)           # тон фона у края, по строкам
    sblur = blur[:, :k] if side == 'L' else blur[:, w - k:]
    grain = (src - sblur)[:, ::-1]                                                 # зерно, отражённое от края
    return np.clip(edge[:, None, :] + grain, 0, 255)
L = json.load(open(sys.argv[1])); dst = sys.argv[2]; os.makedirs(dst, exist_ok=True)
for x in L:
    im = Image.open(x['f']).convert('RGB')
    if im.width > 1600:
        im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32); h, w, _ = a.shape
    s = int(round(-x['off'] * w))                       # модель правее центра → сдвиг влево
    if s > 0: s = min(s, int((0.985 - x['x1']) * w))    # не упереться в край кадра
    else:     s = max(s, -int((x['x0'] - 0.015) * w))
    if s > 0:
        out = np.concatenate([fill_strip(a, s, 'L'), a[:, :w - s]], axis=1)
    elif s < 0:
        k = -s; out = np.concatenate([a[:, k:], fill_strip(a, k, 'R')], axis=1)
    else:
        out = a
    name = os.path.basename(x['f']).rsplit('.', 1)[0] + '.jpg'
    Image.fromarray(out.astype(np.uint8)).save(os.path.join(dst, name), quality=90, optimize=True)
    x['shift'] = s; x['out'] = os.path.join(dst, name)
json.dump(L, open(sys.argv[1], 'w'), indent=0)
print('выровнено', len(L))
