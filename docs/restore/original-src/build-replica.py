#!/usr/bin/env python3
"""Собирает из сырых снимков Web Archive локальные копии оригинала, которые
открываются без сети архива: стили — из css/ и stock/, картинки — из public/img.

Зачем: майские снимки (последние целые) ссылаются на CSS с ?ver=1778…, которого
в архиве нет, и через web.archive.org рисуются без оформления. Те же файлы стилей
сохранены в архиве в марте 2026 (структура страницы та же: 117 элементов, id совпадают).

Запуск: python3 build-replica.py  →  replica/*.html
"""
import re
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / 'replica'
OUT.mkdir(exist_ok=True)

CSS = {p.name for p in (HERE / 'css').glob('*.css')}
STOCK = {p.name for p in (HERE / 'stock').glob('*.css')}
STOCK_ALIAS = {'style.min.css?block-library': 'block-library.min.css'}

FONTS = (
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=Montserrat:ital,wght@0,100..900;1,100..900&'
    'family=Roboto:ital,wght@0,100..900;1,100..900&'
    'family=Roboto+Slab:wght@100..900&display=swap">'
)


def css_link(match: re.Match) -> str:
    tag = match.group(0)
    href = re.search(r"href=['\"]([^'\"]+)", tag).group(1)
    name = href.split('?')[0].rsplit('/', 1)[-1]
    if 'block-library' in href:
        return '<link rel="stylesheet" href="../stock/block-library.min.css">'
    if name in ('montserrat.css', 'roboto.css', 'robotoslab.css'):
        return FONTS if name == 'montserrat.css' else ''
    if name in ('admin-bar.min.css', 'dashicons.min.css'):
        return ''
    if name in CSS:
        return f'<link rel="stylesheet" href="../css/{name}">'
    if name in STOCK:
        return f'<link rel="stylesheet" href="../stock/{name}">'
    # CSS переводов (post-1410.css и т.п.) в архиве нет. Переводы — копии украинской
    # страницы с теми же id элементов, поэтому берём её стили, сменив только префикс.
    m = re.fullmatch(r'post-(\d+)\.css', name)
    if m and m.group(1) in DERIVED:
        base = DERIVED[m.group(1)]
        t = (HERE / 'css' / f'post-{base}.css').read_text(encoding='utf-8')
        (OUT / name).write_text(t.replace(f'.elementor-{base} ', f'.elementor-{m.group(1)} ').replace('../../../../public', '../../../../../public'), encoding='utf-8')
        return f'<link rel="stylesheet" href="{name}"><!-- восстановлено из post-{base}.css -->'
    return f'<!-- нет в архиве: {href} -->'


DERIVED: dict[str, str] = {}


def build(src: Path) -> None:
    s = src.read_text(encoding='utf-8')
    DERIVED.clear()
    page = re.search(r'page-id-(\d+)', s)
    if page and 'class="home ' in s:
        DERIVED[page.group(1)] = '9'
    for num, loc in re.findall(r'class="elementor elementor-(\d+) elementor-location-(header|footer)', s):
        DERIVED.setdefault(num, {'header': '912', 'footer': '906'}[loc])
    for own in ('9', '906', '912', '6', '72'):
        DERIVED.pop(own, None)
    s = re.sub(r"<link[^>]+rel=['\"]stylesheet['\"][^>]*>", css_link, s)
    # Скрипты Elementor не нужны: без них страница статична, как на скриншоте.
    s = re.sub(r'<script\b(?![^>]*ld\+json).*?</script>', '', s, flags=re.S)
    # Ленивые фоны Elementor включает скриптом — без него фоны остались бы скрыты.
    s = re.sub(r'<style>\s*\.e-con\.e-parent:nth-of-type.*?</style>', '', s, flags=re.S)
    s = re.sub(r"<style id='admin-bar-inline-css'>.*?</style>", '', s, flags=re.S)
    s = re.sub(r'<div id="wpadminbar".*?</div>\s*(?=<a class="skip-link|<header|<div data-elementor-type)', '', s, flags=re.S)
    s = s.replace('elementor-invisible', '')
    s = s.replace('admin-bar ', '')
    # Картинки и фоны — из репозитория.
    s = re.sub(r'https?://(?:www\.)?spiritagency\.space/wp-content/uploads/(\d{4}/\d{2}/)', r'../../../../public/img/\1', s)
    (OUT / src.name).write_text(s, encoding='utf-8')


for css in (HERE / 'css').glob('*.css'):
    t = css.read_text(encoding='utf-8')
    t2 = re.sub(r'https?://(?:www\.)?spiritagency\.space/wp-content/uploads/(\d{4}/\d{2}/)', r'../../../../public/img/\1', t)
    if t2 != t:
        css.write_text(t2, encoding='utf-8')

for html in sorted(HERE.glob('*.html')):
    build(html)
    print('ok', html.name)
