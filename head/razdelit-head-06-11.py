# Разделить код HEAD (06.11.2026).
# На страницах /tproduct/ Tilda обрезает HEAD после 46 919 знаков (весь был 50 404) — дальше страницы нет,
# экран белый. В HEAD оставляем только пометку страниц карточек: она должна сработать до отрисовки.
# Остальные блоки — без изменений, в том же порядке — в новый блок «HTML-код» (T123), самым первым
# в «Шапке 1.1», выше конструктора шапки: так стили стоят раньше всего, что ими оформлено.
# В конце блока — размер квадрата цвета в попапе каталога (там он схлопывался в точку).
#
# Стили блока при загрузке переезжают обратно в HEAD — сразу за оставшимся скриптом (id="t2y-head-anchor"),
# то есть на прежнее место. Иначе порядок правил меняется: часть стилей Tilda добавляет в HEAD позже нашего
# кода, и из тела страницы наш CSS начинал их перебивать (проверка 06.11: меню шапки на ПК уже на 4–10 px,
# шрифт в окне корзины 16 вместо 14 px). Скрипты не переезжают — им место не важно.
#
# Запуск из корня репозитория: python3 head/razdelit-head-06-11.py
SRC = 'head/HEAD-na-sayte-06-11-2026.html'   # HEAD, снятый с сайта 06.11 (между nominify)
h = open(SRC, encoding='utf-8').read()
TOP_END = h.index('<!-- ══════════ ШАПКА — КОРЗИНА')
i = h.index('<script>\n/* Помечаем страницы карточек')
j = h.index('</script>', i) + len('</script>')
marker = h[i:j]
moved = h[TOP_END:i] + h[j:]
assert h[TOP_END:].replace(marker, '') == moved and moved.count('<script>') == h.count('<script>') - 1
assert moved.count('<style') == moved.count('<style>') == 13
moved = moved.replace('<style>', '<style data-t2y-head>')
anchor = marker.replace('<script>', '<script id="t2y-head-anchor">', 1)

# Добавлено после публикации 06.11: на /tproduct/ теперь видна страница, а на ней только HEAD (шапки нет).
TPRODUCT = '''<style>
/* Список характеристик под описанием товара («Основной материал: …», «Сезон: …», «Коллекция: …»)
   в попапе каталога и на /tproduct/ не показываем: это свойства для фильтров, «Коллекция» —
   скрытое. На страницах товаров /p/ такого списка и так нет. */
.js-catalog-prod-all-charcs,
.js-store-prod-all-charcs { display: none !important; }
</style>
<script>
/* /tproduct/ — стандартная страница товара Tilda. «Шапки» с нашим кодом на ней нет,
   поэтому «BUY NOW» → «В корзину» — здесь. */
(function () {
  if (location.pathname.indexOf('/tproduct/') === -1) return;
  function fix() {
    var l = document.querySelectorAll('.js-catalog-prod-popup-buy-btn-txt, .js-store-prod-popup-buy-btn-txt');
    for (var i = 0; i < l.length; i++) {
      if (/buy\s*now/i.test(l[i].textContent)) l[i].textContent = 'В корзину';
    }
  }
  document.addEventListener('DOMContentLoaded', fix);
  window.addEventListener('load', fix);
  var n = 0, t = setInterval(function () { fix(); if (++n > 30) clearInterval(t); }, 300);
})();
</script>
'''

NEW_HEAD = '''<!-- ═══ 2young4u.ru — КОД HEAD, 06.11.2026 ═══
     Здесь пометка страниц карточек: она должна сработать до отрисовки.
     Весь остальной общий код — в блоке «HTML-код», первом в «Шапке 1.1»
     (в репозитории head/HEAD-v-shapke-T123.html).
     HEAD не раздувать: на страницах /tproduct/ Tilda обрезает его после ~46 тыс. знаков,
     и страница товара открывается пустой.
     id="t2y-head-anchor" не убирать: к этому месту блок из «Шапки» возвращает свои стили.
     Ещё здесь — то, что нужно и на /tproduct/ (там нет шапки): скрыть список
     характеристик и «BUY NOW» → «В корзину». Якорь — последним. -->
''' + TPRODUCT + anchor + '\n'

SWATCH = '''
<!-- ══════════ ЦВЕТ В ПОПАПЕ КАТАЛОГА — КВАДРАТ 56×56 (06.11.2026) ══════════ -->
<style data-t2y-head>
/* В попапе каталога у рамки образца цвета нет своего размера, а картинка внутри —
   100% рамки (правило «Цвет: убираем ДВОЙНУЮ рамку» выше), и образец схлопывался в точку.
   Размер — как на страницах товаров /p/: 56×56. */
.t-catalog__prod-popup__container .t-product__option-item_image,
html.t2y-card-page .t-product__option-item_image {
  width: 56px !important;
  height: 56px !important;
  box-sizing: border-box !important;
}
</style>
'''

MOVER = '''
<!-- ══════════ СТИЛИ ЭТОГО БЛОКА — ОБРАТНО В HEAD, НА ПРЕЖНЕЕ МЕСТО ══════════ -->
<script>
/* Все <style data-t2y-head> выше переносим в HEAD сразу за скриптом id="t2y-head-anchor" —
   туда, где этот код стоял раньше. Так порядок правил тот же, что был в HEAD:
   после стилей Tilda, загруженных раньше, и до тех, что Tilda добавит позже.
   Если якоря нет (HEAD не обновлён) — стили остаются здесь и всё равно работают. */
(function () {
  var a = document.getElementById('t2y-head-anchor');
  if (!a || !a.parentNode) return;
  var list = document.querySelectorAll('style[data-t2y-head]');
  var ref = a.nextSibling;
  for (var i = 0; i < list.length; i++) {
    if (list[i].parentNode !== a.parentNode) a.parentNode.insertBefore(list[i], ref);
  }
})();
</script>
'''

NEW_BLOCK = '''<!-- ════════════════════════════════════════════════════════════════
     2Y4U — КОД ИЗ HEAD В «ШАПКЕ 1.1». 06.11.2026
     КУДА: «Шапка 1.1» → новый блок «HTML-код» (T123) САМЫМ ПЕРВЫМ, выше
     конструктора шапки. Стили должны стоять раньше шапки, иначе она мигнёт.
     ПОЧЕМУ: на страницах /tproduct/ Tilda обрезает HEAD после ~46 тыс. знаков —
     страница товара была пустой. В HEAD осталась только пометка страниц карточек.
     Внутри — блоки бывшего HEAD без изменений, в том же порядке; в конце —
     размер квадрата цвета в попапе каталога и скрипт, который возвращает
     стили блока в HEAD, на прежнее место (к скрипту id="t2y-head-anchor").
     Блок «HTML-код» со всем остальным кодом «Шапки» (SHAPKA-T123.html) — не трогать.
     ════════════════════════════════════════════════════════════════ -->
''' + moved + SWATCH + MOVER

open('head/HEAD-06-11.html', 'w', encoding='utf-8').write(NEW_HEAD)
open('head/HEAD-v-shapke-T123.html', 'w', encoding='utf-8').write(NEW_BLOCK)
for f, s in (('HEAD-06-11.html', NEW_HEAD), ('HEAD-v-shapke-T123.html', NEW_BLOCK)):
    print('%-26s %6d знаков %6d байт' % (f, len(s), len(s.encode())))
print('было в HEAD: %d знаков, обрыв на /tproduct/ после 46 919' % len(h))
