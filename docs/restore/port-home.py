#!/usr/bin/env python3
"""Переносит главную оригинала (Elementor, страница 9 + подвал 906) в проект.

Вход:  original-src/home-<язык>.html — сырые снимки Web Archive.
Выход: src/components/original/HomeBody.astro   — секции страницы (без шапки);
       src/components/original/HomeFooter.astro — подвал «Деталі співпраці»;
       src/data/home-blocks.json                — тексты по языкам, ключ = id элемента
                                                  Elementor (тот же, что в классе
                                                  elementor-element-<id>).

Разметка берётся с украинской страницы один в один: классы Elementor нужны, чтобы
работали оригинальные стили из src/styles/original/. Меняется только то, что не
влияет на вид: убраны data-* (на них стили не завязаны), адреса картинок ведут
в /img/, обёртки Wix внутри текстов очищены от классов и id.

У переводов та же структура, но часть id другая (блоки пересоздавались), поэтому
тексты сопоставляются по порядку элементов, а не по id. У русской страницы первый
экран старый и стилей к нему в архиве нет — ей даётся украинская структура, а тексты
первого экрана берутся из src/data/home.json.

Запуск из корня проекта: python3 docs/restore/port-home.py
Шапку (меню, переключатель языков, мобильная панель) скрипт не трогает — она
в HomeHeader.astro и написана руками.
"""
from __future__ import annotations

import difflib
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

ROOT = Path(__file__).resolve().parents[2]
SRC = Path(__file__).resolve().parent / 'original-src'
LANGS = ['uk', 'ru', 'pl', 'ro', 'lt', 'sk']
HEADER_ID = 'cf12209'
HERO_IMAGE_ID = '12ee214'

# Обычные пробелы. Неразрывный (U+00A0) сюда не входит нарочно: в оригинале им набиты
# пустые строки, которые держат высоту блоков, — терять его нельзя.
WS = ' \t\r\n\f'

VOID = {'img', 'br', 'hr', 'input', 'meta', 'link'}
BLOCK = {'p', 'div', 'section', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote'}
DROP_ATTRS = {'data-settings', 'data-id', 'data-element_type', 'data-widget_type', 'data-ps2id-api',
              'data-elementor-post-type', 'data-e-type'}


def load(lang: str) -> BeautifulSoup:
    return BeautifulSoup((SRC / f'home-{lang}.html').read_text(encoding='utf-8'), 'lxml')


def elements(soup: BeautifulSoup) -> list[Tag]:
    """Элементы Elementor страницы и подвала по порядку."""
    out = []
    for root in soup.select('[data-elementor-type]'):
        out += root.select('[data-id]')
    return out


def kind(el: Tag) -> str:
    return (el.get('data-widget_type') or 'container').replace('.default', '')


# ---------- тексты ----------

def clean_rich(container: Tag) -> str:
    """HTML текстового блока без мусора Wix: остаются теги, style и ссылки."""
    frag = BeautifulSoup(container.decode_contents(), 'lxml').body
    if frag is None:
        return ''
    for tag in frag.find_all(True):
        for attr in list(tag.attrs):
            if attr not in ('style', 'href', 'target', 'rel'):
                del tag[attr]
    # Обёртки без атрибутов, внутри которых только блоки, на вид не влияют.
    changed = True
    while changed:
        changed = False
        for tag in frag.find_all(['div', 'section']):
            if tag.attrs:
                continue
            has_text = any(isinstance(c, NavigableString) and c.strip(WS) for c in tag.children)
            kids = [c for c in tag.children if isinstance(c, Tag)]
            if not has_text and all(k.name in BLOCK for k in kids):
                tag.unwrap()
                changed = True
    html = frag.decode_contents().replace('\xa0', '&nbsp;')
    html = re.sub(r'[ \t\r\n\f]+', ' ', html).strip(WS)
    html = re.sub(r'> <(?=/?(?:p|div|section|ul|ol|li|h\d)\b)', '><', html)
    return html


def texts(el: Tag) -> dict[str, str]:
    """Переводимые строки одного виджета: {суффикс ключа: html}."""
    k = kind(el)
    if k == 'text-editor':
        return {'': clean_rich(el.find(class_='elementor-widget-container') or el)}
    if k == 'heading':
        return {'': re.sub(r'[ \t\r\n\f]+', ' ', el.find(class_='elementor-heading-title').decode_contents()).strip(WS)}
    if k == 'button':
        t = el.find(class_='elementor-button-text')
        return {'': t.get_text(strip=True)} if t else {}
    if k == 'icon-box':
        return {
            '.title': el.find(class_='elementor-icon-box-title').get_text(strip=True),
            '.desc': el.find(class_='elementor-icon-box-description').get_text(strip=True),
        }
    if k == 'icon-list':
        return {f'.{i}': t.get_text(strip=True) for i, t in enumerate(el.find_all(class_='elementor-icon-list-text'))}
    return {}


def blocks_for(lang: str, uk_els: list[Tag]) -> dict[str, str]:
    els = elements(load(lang))
    by_id = {e['data-id']: e for e in els}
    # Шапка у переводов собрана в другом порядке, дальше страницы совпадают —
    # сопоставляем совпавшие по типам участки, а где не вышло, ищем по id.
    by_pos: dict[int, Tag] = {}
    matcher = difflib.SequenceMatcher(None, [kind(e) for e in uk_els], [kind(e) for e in els], autojunk=False)
    for tag, i1, i2, j1, _ in matcher.get_opcodes():
        if tag == 'equal':
            for off in range(i2 - i1):
                by_pos[i1 + off] = els[j1 + off]
    out: dict[str, str] = {}
    for i, uk in enumerate(uk_els):
        src = by_id.get(uk['data-id']) or by_pos.get(i)
        if src is None or kind(src) != kind(uk):
            continue
        for suffix, html in texts(src).items():
            out[uk['data-id'] + suffix] = html
    print(f'{lang}: элементов {len(els)}, строк {len(out)}')
    return out


def hero_fallback(lang: str, have: dict[str, str]) -> dict[str, str]:
    """Первый экран для языка, у которого он в оригинале устроен иначе (ru)."""
    d = json.loads((ROOT / 'src/data/home.json').read_text(encoding='utf-8'))[lang]
    hero = d['hero']
    fb = {
        '3d5265e': 'SpiritAgency',
        '36c27b0': hero['h1'],
        '6d7d8b1': f'<p><span style="text-decoration: underline;">{hero["kicker"]}</span></p>',
        'b4e1814': f'<p>{hero["sub"]}</p>',
        'd082f63': hero['ctas'][0]['text'],
        'fc5ac2a': hero['ctas'][1]['text'],
    }
    return {k: v for k, v in fb.items() if k not in have}


# ---------- разметка ----------

def local_url(url: str) -> str:
    return re.sub(r'https?://(?:www\.)?spiritagency\.space/wp-content/uploads/', '/img/', url)


def attr_str(tag: Tag) -> str:
    parts = []
    for name, val in tag.attrs.items():
        if name in DROP_ATTRS:
            continue
        if isinstance(val, list):
            val = ' '.join(val)
        if name in ('src', 'srcset', 'href'):
            val = local_url(val)
        if name == 'srcset':
            keep = [c.strip() for c in val.split(',') if (ROOT / 'public' / c.strip().split(' ')[0].lstrip('/')).exists()]
            val = ', '.join(keep)
            if not val:
                continue
        val = val.replace('"', '&quot;')
        parts.append(f'{name}="{val}"' if val != '' or name in ('alt',) else name)
    return (' ' + ' '.join(parts)) if parts else ''


def svg(tag: Tag) -> str:
    s = str(tag)
    # <style> внутри SVG Astro принял бы за стили компонента — заливку пишем атрибутом.
    s = re.sub(r'<style[^>]*>\s*\.st0\{fill:(#[0-9A-Fa-f]+);\}\s*</style>', '', s)
    s = s.replace('class="st0"', 'fill="#ED1010"')
    return re.sub(r'\s+', ' ', s).strip().replace('viewbox=', 'viewBox=')


def emit(node, depth: int, key: str | None, out: list[str]) -> None:
    pad = '  ' * depth
    if isinstance(node, NavigableString):
        t = str(node).strip(WS).replace('\xa0', '&nbsp;')
        if t:
            out.append(pad + t)
        return
    if node.name == 'svg':
        out.append(pad + svg(node))
        return
    classes = node.get('class', [])
    if node.has_attr('data-id'):
        key = node['data-id']
        if key == HEADER_ID:
            out.append(pad + '<HomeHeader lang={lang} />')
            return
    a = attr_str(node)
    # Картинка первого экрана: в оригинале она грузилась лениво, хотя видна сразу.
    if node.name == 'img' and key == HERO_IMAGE_ID:
        a = a.replace(' loading="lazy"', '') + ' fetchpriority="high"'

    # Места, куда подставляется перевод.
    if 'elementor-widget-container' in classes and kind(node.parent) == 'text-editor':
        out.append(f"{pad}<div{a} set:html={{b['{key}']}} />")
        return
    if 'elementor-heading-title' in classes:
        out.append(f"{pad}<{node.name}{a} set:html={{b['{key}']}} />")
        return
    if 'elementor-button-text' in classes:
        out.append(f"{pad}<span{a}>{{b['{key}']}}</span>")
        return
    if 'elementor-icon-box-title' in classes:
        out.append(f"{pad}<{node.name}{a}><span>{{b['{key}.title']}}</span></{node.name}>")
        return
    if 'elementor-icon-box-description' in classes:
        out.append(f"{pad}<{node.name}{a}>{{b['{key}.desc']}}</{node.name}>")
        return
    if 'elementor-icon-list-text' in classes:
        idx = node.find_parent('ul').find_all(class_='elementor-icon-list-text').index(node)
        out.append(f"{pad}<span{a}>{{b['{key}.{idx}']}}</span>")
        return

    if node.name in VOID:
        out.append(f'{pad}<{node.name}{a} />')
        return
    kids = [c for c in node.children if not (isinstance(c, NavigableString) and not c.strip(WS))]
    if not kids:
        out.append(f'{pad}<{node.name}{a}></{node.name}>')
        return
    out.append(f'{pad}<{node.name}{a}>')
    for c in kids:
        emit(c, depth + 1, key, out)
    out.append(f'{pad}</{node.name}>')


HEAD = '''---
// Сгенерировано docs/restore/port-home.py из снимка Web Archive (страница {what}).
// Классы Elementor менять нельзя: на них держатся оригинальные стили src/styles/original/.
// Тексты — в src/data/home-blocks.json, ключ совпадает с id в классе elementor-element-<id>.
{imports}import blocks from '../../data/home-blocks.json';
import type {{ Lang }} from '../../i18n';

interface Props {{ lang: Lang }}
const {{ lang }} = Astro.props;
const b = (blocks as Record<Lang, Record<string, string>>)[lang];
---

'''


def component(root: Tag, what: str, imports: str = '') -> str:
    out: list[str] = []
    emit(root, 0, None, out)
    return HEAD.format(what=what, imports=imports) + '\n'.join(out) + '\n'


def main() -> None:
    uk = load('uk')
    uk_els = elements(uk)
    data = {}
    for lang in LANGS:
        got = blocks_for(lang, uk_els)
        got.update(hero_fallback(lang, got))
        missing = sorted(k for k in blocks_for_keys(uk_els) if k not in got)
        if missing:
            print(f'  нет строк для {lang}: {missing}')
        data[lang] = got

    comp = ROOT / 'src/components/original'
    comp.mkdir(parents=True, exist_ok=True)
    page = uk.select_one('[data-elementor-type="wp-page"]')
    footer = uk.select_one('[data-elementor-id="906"]')
    (comp / 'HomeBody.astro').write_text(
        component(page, '9', "import HomeHeader from './HomeHeader.astro';\n"), encoding='utf-8')
    (comp / 'HomeFooter.astro').write_text(component(footer, '906, подвал'), encoding='utf-8')
    (ROOT / 'src/data/home-blocks.json').write_text(
        json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('готово')


def blocks_for_keys(uk_els: list[Tag]) -> list[str]:
    keys = []
    for e in uk_els:
        if e.find_parent(attrs={'data-id': HEADER_ID}) and kind(e) != 'heading':
            continue
        keys += [e['data-id'] + s for s in texts(e)]
    return keys


if __name__ == '__main__':
    main()
