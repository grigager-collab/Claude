import json
meta=json.load(open('img/meta.json'))
CW=544; SW=720; s=SW/CW; SH=round(meta['col_now']['h']*s,1)
xs=[i[0]*s for i in meta['col_four']['items']]; y0=meta['col_four']['items'][0][1]*s; sz=54*s
cx=[x+sz/2 for x in xs]; cy=y0+sz/2
tiles=[f'img/tile_{i:02d}.'+('jpg' if i==0 else 'webp') for i in range(11)]
HLOP=[2,6,7,10]            # «Олимпийка хлопковая»: чёрная, Ocean, Volcano, синяя
MODELS=[0,1,2,3]           # по одной плитке на модель (вариант Б)
RED='#D93A2B'

def ring(i,pad=9):
    return f'<rect x="{xs[i]-pad:.1f}" y="{y0-pad:.1f}" width="{sz+2*pad:.1f}" height="{sz+2*pad:.1f}" rx="12" fill="none" stroke="{RED}" stroke-width="5"/>'
def arrow_to_flow(i):
    yb=y0+sz+9; yl=y0+sz+27
    return (f'<path d="M {cx[i]:.0f} {yb:.0f} L {cx[i]:.0f} {yl:.0f} L 730 {yl:.0f}" fill="none" stroke="{RED}" '
            f'stroke-width="5" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#ah)"/>')
DEFS=f'<defs><marker id="ah" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{RED}"/></marker></defs>'

def catalog(mode):
    cells=[]
    for i,t in enumerate(tiles):
        if mode=='b' and i not in MODELS:
            cells.append('<div class="th th--gone"></div>'); continue
        cls='th'+(' th--hl' if mode=='now' and i in HLOP else '')
        cells.append(f'<div class="{cls}"><img src="{t}"></div>')
    if mode=='b':  # в Б плитки моделей стоят первыми, дальше пустые места
        cells=[c for c in cells if 'gone' not in c]+[c for c in cells if 'gone' in c]
    return '<div class="cat">'+''.join(cells)+'</div>'

def head(n,title,badge='',sub=''):
    b=f'<span class="badge">{badge}</span>' if badge else ''
    s=f'<div class="sub">{sub}</div>' if sub else ''
    return (f'<div class="top"><span>2YOUNG4U · цвета на карточке товара</span><span>{n} / 4</span></div>'
            f'<h1>{title}{b}</h1>{s}')

def shot(img,overlay):
    return (f'<div class="shot" style="width:{SW}px;height:{SH}px"><img src="img/{img}.png" style="width:{SW}px">'
            f'<svg class="ov" width="{SW}" height="{SH}">{DEFS}{overlay}</svg></div>')

def flow(cap,url,photo,title):
    return (f'<div class="flow" style="height:{SH}px"><div class="flow__cap">{cap}</div>'
            f'<div class="mini"><div class="mini__url">{url}</div><div class="mini__img"><img src="img/{photo}"></div>'
            f'<div class="mini__title">{title}</div></div></div>')

def proscons(pros,cons):
    p=''.join(f'<li>{x}</li>' for x in pros); c=''.join(f'<li>{x}</li>' for x in cons)
    return f'<div class="pc"><div><div class="pc__h">Плюсы</div><ul class="plus">{p}</ul></div><div><div class="pc__h">Минусы</div><ul class="minus">{c}</ul></div></div>'

OCEAN='photo_olimpiyka-hlopkovaya-ocean-siniy.webp'

# ── слайд 1: почему сейчас один цвет
dashed=''.join(f'<rect x="{xs[i]+3:.1f}" y="{y0+3:.1f}" width="{sz-6:.1f}" height="{sz-6:.1f}" fill="none" stroke="{RED}" stroke-width="4" stroke-dasharray="10 8"/>' for i in (1,2,3))
s1=(head(1,'Почему сейчас один цвет')
  + '<div class="row">'
  + shot('col_now', ring(0)+dashed+f'<text x="{xs[3]+sz+22:.0f}" y="{cy+9:.0f}" class="ovt">сюда хотим другие цвета</text>')
  + '<div class="side"><div class="callout">Квадратики «Цвет» показывают <b>варианты одного товара</b>.<br><br>У этого товара вариант один — коричневый. Поэтому и квадратик один.</div></div>'
  + '</div>'
  + '<ul class="bul">'
  + '<li>На сайте <b>каждый цвет — отдельный товар</b>: своя страница, артикул, фото и своя плитка в каталоге.</li>'
  + '<li>«Олимпийка хлопковая» — это 4 разных товара: чёрная, синяя, Ocean и Volcano. Друг о друге они «не знают».</li>'
  + '<li>В тестовых карточках цвета были внутри одного товара — поэтому там квадратиков было несколько.</li>'
  + '</ul>'
  + '<div class="cap">Раздел «Олимпийки и толстовки» сейчас. Красным — 4 цвета «Олимпийки хлопковой»</div>'
  + catalog('now'))

# ── слайд 2: вариант А
s2=(head(2,'Вариант А','советую','Квадратики ведут на страницы других цветов')
  + '<div class="row rel">'
  + shot('col_four', ring(2))
  + flow('<b class="red">Нажали «Ocean»</b> — открылась <b>страница Ocean</b> со всеми её фото','…/hlopkovaya-<b>ocean</b>-siniy',OCEAN,'Олимпийка хлопковая Ocean')
  + f'<svg class="ov2" width="952" height="{SH}">{DEFS}{arrow_to_flow(2)}</svg>'
  + '</div>'
  + '<div class="cap">Каталог — <b>как сейчас</b>: каждый цвет своей плиткой (11 плиток)</div>'
  + catalog('a')
  + proscons(['каталог остаётся полным','у каждого цвета все свои фото, артикул и своя ссылка','товары переделывать не нужно — я добавлю код'],
             ['при выборе цвета открывается другая страница','одна модель в каталоге — несколько плиток','новый цвет — добавить строчку в список связей (покажу где)']))

# ── слайд 3: вариант Б
s3=(head(3,'Вариант Б','','Все цвета — внутри одного товара')
  + '<div class="row rel">'
  + shot('col_one_product', ring(2))
  + flow('<b class="red">Нажали «Ocean»</b> — на этой же странице <b>сменилось фото</b>, адрес тот же','…/olimpiyka-hlopkovaya',OCEAN,'Олимпийка хлопковая')
  + f'<svg class="ov2" width="952" height="{SH}">{DEFS}{arrow_to_flow(2)}</svg>'
  + '</div>'
  + '<div class="cap">Каталог: одна плитка на модель — <b>4 плитки вместо 11</b></div>'
  + catalog('b')
  + proscons(['как в тестовых карточках: цвет меняется сразу, без перехода','одна модель — одна плитка, без повторов','новый цвет добавляется прямо в товар'],
             ['в разделе 4 плитки вместо 11','у цвета одно своё фото, остальная галерея общая на все цвета','10 товаров собрать в 3 вручную: фото, артикулы, остатки по цвету и размеру','старые ссылки на отдельные цвета перестанут работать']))

# ── слайд 4: сравнение
rows=[('На карточке','4 квадратика с фото','4 квадратика с фото'),
      ('Нажали на цвет','открывается страница этого цвета','фото меняется на этой же странице'),
      ('Фото у цвета','все свои, 6–7 штук','одно своё + общие'),
      ('Каталог олимпиек','11 плиток, как сейчас','4 плитки'),
      ('Ссылка на цвет','своя у каждого цвета','одна на модель'),
      ('Что переделать','ничего — добавлю код','10 товаров → 3, вручную')]
tr=''.join(f'<tr><th>{a}</th><td>{b}</td><td>{c}</td></tr>' for a,b,c in rows)
s4=(head(4,'Сравнение')
  + f'<table class="cmp"><thead><tr><th></th><th>А · квадратики-ссылки</th><th>Б · один товар</th></tr></thead><tbody>{tr}</tbody></table>'
  + '<div class="rec">Советую вариант А: каталог остаётся полным, а у каждого цвета — все его фото.</div>'
  + '<div class="q">Какой вариант выбираем?</div>'
  + '<div class="note"><div class="note__h">И проверьте, верно ли я понял, какие товары — цвета одной модели:</div>'
  + '<ul class="grp"><li><b>Олимпийка хлопковая</b> — чёрная, синяя, Ocean, Volcano</li>'
  + '<li><b>Олимпийка классическая</b> — Ocean, Space, Volcano</li>'
  + '<li><b>Олимпийка с принтом Ватаным</b> — белая, чёрная, синяя</li></ul></div>'
  + '<div class="note note--row"><img src="img/empty_sq.png"><div><b>Отдельно:</b> у чёрной и синей «Олимпийки хлопковой» квадратик цвета сейчас пустой — к товару не прикреплено фото цвета. Поправим в любом варианте.</div></div>')

CSS=open('slides.css').read()
html=f'''<!doctype html><html lang="ru"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Raleway:wght@400;500;600&family=Tenor+Sans&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<section class="slide" id="s1">{s1}</section>
<section class="slide" id="s2">{s2}</section>
<section class="slide" id="s3">{s3}</section>
<section class="slide" id="s4">{s4}</section>
</body></html>'''
open('slides.html','w',encoding='utf-8').write(html)
print('ok', SW, SH, [round(c) for c in cx], round(cy))
