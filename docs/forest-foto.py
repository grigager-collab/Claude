# -*- coding: utf-8 -*-
"""
Фото зелёной коллекции Forest для карточек: отбор + кадрирование 900×1200 (3:4).

ЗАПУСК:
    python3 docs/forest-foto.py <папка с исходниками Яндекс.Диска> images/forest

Исходники — папки товаров с Диска «04 - зеленый интерлок и 2 фут» (НЕ «900:1200»:
там модели обрезаны по нос и кадры растянуты). Большие *_MAN_01/_02 — снимки бирок,
их не берём; вещь на белом — *_MAN_02/_03 маленького размера.

КАДР (29.10.2026, Григорий: «вещь по центру, сверху и снизу чуть воздуха»):
  · вещь на белом — по центру, поля сверху и снизу поровну (AIR_PACK);
  · модель в полный рост — по центру по ширине, под обувью воздух (AIR_FLOOR);
    сверху модель обрезана ещё на съёмке (по лицо), там воздуха не добавить;
  · остальные кадры на модели и детали НЕ трогаем (Григорий: «остальные не надо») —
    остаются файлы из первой версии (папка «900:1200»).
  Фон, где кадра не хватает, достраивается цветом края фото.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter, ImageOps

W, H = 900, 1200
AIR_PACK = 0.07     # поле сверху и снизу у вещи на белом — доля высоты
SIDE_PACK = 0.06    # минимальное поле по бокам у вещи на белом
AIR_FLOOR = 0.05    # воздух под обувью у кадра в полный рост

# Порядок фото в карточке: 1 — на белом, 2 — в полный рост, дальше остальное.
# FULL — какие кадры в полный рост (по ним ставим воздух под обувью).
D = {
 '22270709': ('22270709', ['3_MAN_03', '3_MOD_05', '3_MOD_02', '3_MOD_01', '3_MOD_03', '3_MOD_04'],
              {'3_MOD_05'}),
 '22270801': ('22270801', ['4_MAN_03', '6_MOD_06', '6_MOD_03', '6_MOD_02', '6_MOD_04', '6_MOD_05'],
              {'6_MOD_06'}),
 '22270802': ('22270802', ['1_MAN_02', '1_MOD_02', '5_MOD_02', '5_MOD_01', '5_MOD_03', '1_MOD_01'],
              {'1_MOD_02'}),
 '22270803': ('22270803', ['3_MAN_03', '5_MOD_08', '5_MOD_05', '5_MOD_04', '5_MOD_06', '5_MOD_07'],
              {'5_MOD_08'}),
 '22270811': ('22270811', ['5_MAN_03', '5_MOD_08', '5_MOD_09', '5_MOD_05', '5_MOD_04', '5_MOD_02',
                           '5_MOD_01', '5_MOD_06', '5_MOD_07', '5_MOD_03'],
              {'5_MOD_08', '5_MOD_09'}),
 '22270812': ('22270812', ['6_MAN_03', '6_MOD_06', '6_MOD_07', '6_MOD_03', '6_MOD_02', '5_MOD_02',
                           '5_MOD_01', '6_MOD_04', '6_MOD_05', '5_MOD_03'],
              {'6_MOD_06', '6_MOD_07'}),
 '22270821': ('22270821', ['1_MAN_03', '1_MOD_09', '1_MOD_13', '1_MOD_10', '1_MOD_05', '1_MOD_04',
                           '1_MOD_01', '1_MOD_03', '1_MOD_06', '1_MOD_08', '1_MOD_07', '1_MOD_12'],
              {'1_MOD_09', '1_MOD_13'}),
 '22270822': ('22270822', ['2_MAN_02', '2_MOD_09', '2_MOD_08', '2_MOD_03', '2_MOD_02', '1_MOD_01',
                           '1_MOD_03', '2_MOD_04', '2_MOD_05', '2_MOD_10', '1_MOD_02', '2_MOD_06'],
              {'2_MOD_09', '2_MOD_08'}),
}


def find(src, art, prefix):
    folder = [d for d in os.listdir(src) if d.startswith(art)][0]
    names = sorted(f for f in os.listdir(os.path.join(src, folder)) if f.startswith(prefix))
    # среди одноимённых берём меньший файл: большие *_MAN_* — бирки
    names.sort(key=lambda f: os.path.getsize(os.path.join(src, folder, f)))
    return os.path.join(src, folder, names[0])


def bbox(a, white):
    """Рамка вещи/модели: всё, что заметно отличается от фона."""
    g = a.astype(np.int16)
    if white:
        m = (g.min(axis=2) < 238)
    else:
        # фон — светло-серый с переходом, справа темнее: по нему центр «уезжает».
        # Ищем саму вещь — тёмную (зелёная ткань), фон и кожа светлее.
        m = (g.mean(axis=2) < 140)
    rows = np.where(m.mean(axis=1) > 0.004)[0]
    cols = np.where(m.mean(axis=0) > 0.004)[0]
    return cols[0], rows[0], cols[-1] + 1, rows[-1] + 1


def extend(im, left, top, right, bottom):
    """Расширить кадр: края фона тянем наружу и размываем шов."""
    a = np.asarray(im)
    p = np.pad(a, ((top, bottom), (left, right), (0, 0)), mode='edge')
    big = Image.fromarray(p)
    if left or top or right or bottom:
        blur = big.filter(ImageFilter.GaussianBlur(25))
        mask = Image.new('L', big.size, 255)
        mask.paste(0, (left, top, left + im.width, top + im.height))
        mask = mask.filter(ImageFilter.GaussianBlur(8))
        big = Image.composite(blur, big, mask)
    return big


def place(im, cx, top_px, scale, white):
    """Масштабировать и вырезать 900×1200 так, чтобы cx был по центру, а top_px — сверху."""
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    cx, top_px = cx * scale, top_px * scale
    x0, y0 = round(cx - W / 2), round(top_px)
    l, t = max(0, -x0), max(0, -y0)
    r, b = max(0, x0 + W - im.width), max(0, y0 + H - im.height)
    if white:
        c = Image.new('RGB', (im.width + l + r, im.height + t + b), (255, 255, 255))
        c.paste(im, (l, t))
    else:
        c = extend(im, l, t, r, b)
    return c.crop((x0 + l, y0 + t, x0 + l + W, y0 + t + H))


def frame(path, kind):
    im = ImageOps.exif_transpose(Image.open(path)).convert('RGB')
    a = np.asarray(im)
    if kind == 'pack':
        x0, y0, x1, y1 = bbox(a, True)
        s = min(H * (1 - 2 * AIR_PACK) / (y1 - y0), W * (1 - 2 * SIDE_PACK) / (x1 - x0))
        # вещь по центру: поля сверху и снизу поровну
        top = (y0 + y1) / 2 - H / 2 / s
        return place(im, (x0 + x1) / 2, top, s, True)
    x0, y0, x1, y1 = bbox(a, False)
    cx = (x0 + x1) / 2
    if kind == 'full':
        # верх кадра — как снято, обувь — с воздухом снизу
        s = H * (1 - AIR_FLOOR) / y1
        return place(im, cx, 0, s, False)
    # остальное: высота кадра целиком, по центру по ширине
    s = H / im.height
    if im.width * s < W:
        s = W / im.width
    return place(im, cx if im.width * s > W else im.width / 2, (im.height - H / s) / 2, s, False)


def main():
    src, out = sys.argv[1], sys.argv[2]
    for art, (prefix, files, full) in D.items():
        os.makedirs(os.path.join(out, art), exist_ok=True)
        for i, f in enumerate(files, 1):
            kind = 'pack' if '_MAN_' in f else ('full' if f in full else 'mod')
            if kind == 'mod':
                continue
            frame(find(src, prefix, f), kind).save(
                os.path.join(out, art, '%02d.jpg' % i), 'JPEG', quality=86, optimize=True, progressive=True)
        print(art, len(files))


if __name__ == '__main__':
    main()
