# Izdat

Шрифт заголовков сайта «Издательство пиццы». Основа — **Forum** © 2011 Denis Masharov (SIL Open Font License 1.1, Reserved Font Name «Forum»; лицензия — `../OFL.txt`).

Изменения: горизонтальное сжатие ×0.85 (ширина заглавных ≈ на 10% шире, чем у CoFo Cinema1909, — только общая пропорция, контуры CoFo не использовались), упрощённые засечки у заглавных с прямыми штрихами (вынос ×0.6), хинтинг убран, имя — Izdat.

Сборка: `pip install fonttools brotli` → `python build.py 0.85 0.6` → `Izdat-Regular.ttf`; woff2 — `fontTools` c `flavor='woff2'`.
