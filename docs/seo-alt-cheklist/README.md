# Чек-лист SEO и alt (02.11.2026)

Опубликован: https://claude.ai/artifact/5sNoHiwiRCBnxsNwoMLFN9

- `seo-i-alt.html` — то, что опубликовано.
- `template.html` — разметка без данных.
- Сборка: `docs/tools/seo-i-alt-02-11-build.py` — делает `docs/seo-i-alt-02-11.md` и `data.json`, данные вставляются в шаблон вместо `/*DATA*/`.
- Отметки хранятся в базе чек-листа:
  - `done/<ключ>` `{done, at}` — ставит Григорий;
  - `check/<ключ>` `{state: ok|issue, note, at}` — ставит Claude после проверки на сайте.
- Ключ: `home`, `aboutus`, `vatanym`, `men-suits`, …, `p-<адрес товара>`, `shop`, `women-blazers`, `women-sets`, `shapka`.
