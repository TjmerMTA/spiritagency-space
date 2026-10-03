#!/usr/bin/env python3
"""Переносит в статьи то, что блог оригинала показывал в карточках.

Вход:  original-src/blog-<язык>.html (у украинского ещё blog-uk-2.html) — списки статей
       из Web Archive; original-src/post-ru-seo.html — статья, которой в проекте не было.
Выход: поле `excerpt` во фронтматтере каждой статьи src/content/posts/<язык>/<слаг>.md.

Зачем отдельное поле. Анонс в карточке оригинала нельзя вывести правилом: у половины
статей он задан вручную (и обрезан на полуслове — так и было), у остальных WordPress
брал первые 20 слов текста. Поэтому анонсы взяты из снимков как есть.
Статья без `excerpt` (новая) получит первые 20 слов текста — см. src/excerpt.ts.

Запуск из корня проекта: python3 docs/restore/port-blog.py
"""
from __future__ import annotations

import html
import re
import urllib.parse
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

ROOT = Path(__file__).resolve().parents[2]
SRC = Path(__file__).resolve().parent / 'original-src'
POSTS = ROOT / 'src/content/posts'
LISTS = {
    'uk': ['blog-uk.html', 'blog-uk-2.html'],
    'ru': ['blog-ru.html'],
    'pl': ['blog-pl.html'],
    'ro': ['blog-ro.html'],
    'lt': ['blog-lt.html'],
    'sk': ['blog-sk.html'],
}
RU_MONTHS = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа',
             'сентября', 'октября', 'ноября', 'декабря']


def yaml_str(value: str) -> str:
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def cards(name: str) -> list[dict[str, str]]:
    page = (SRC / name).read_text(encoding='utf-8')
    out = []
    for block in re.findall(r'<article class="blog-card">(.*?)</article>', page, flags=re.S):
        href = re.search(r'<h2><a href="([^"]*)">', block).group(1)
        text = re.search(r'</div>\s*<p>(.*?)</p>', block, flags=re.S).group(1)
        out.append({
            'slug': urllib.parse.unquote(href.rstrip('/').split('/')[-1]),
            # Неразрывный пробел в начале анонса (есть у нескольких статей) — часть оригинала,
            # поэтому обрезаем только обычные пробелы.
            'excerpt': html.unescape(text).strip(' \t\r\n'),
        })
    return out


def set_excerpt(path: Path, excerpt: str) -> bool:
    text = path.read_text(encoding='utf-8')
    head, sep, body = text[4:].partition('\n---\n')
    lines = [l for l in head.split('\n') if not l.startswith('excerpt:')]
    at = next((i for i, l in enumerate(lines) if l.startswith('description:')), 0) + 1
    lines.insert(at, f'excerpt: {yaml_str(excerpt)}')
    new = '---\n' + '\n'.join(lines) + sep + body
    if new != text:
        path.write_text(new, encoding='utf-8')
        return True
    return False


# ---------- статья, которой не было в проекте ----------

def inline(node) -> str:
    if isinstance(node, NavigableString):
        return str(node)
    inner = ''.join(inline(c) for c in node.children)
    if node.name in ('b', 'strong'):
        return f'**{inner.strip()}**' + (' ' if inner.endswith(' ') else '')
    if node.name in ('i', 'em'):
        return f'*{inner.strip()}*'
    if node.name == 'a':
        href = re.sub(r'https?://(?:www\.)?spiritagency\.space', '', node.get('href', ''))
        return f'[{inner}]({href})'
    if node.name == 'br':
        return '\n'
    return inner


def to_markdown(content: Tag) -> str:
    out = []
    for el in content.children:
        if not isinstance(el, Tag):
            continue
        if re.fullmatch(r'h[2-6]', el.name):
            out.append('#' * int(el.name[1]) + ' ' + inline(el).strip())
        elif el.name == 'p':
            out.append(inline(el).strip())
        elif el.name in ('ul', 'ol'):
            items = el.find_all('li', recursive=False)
            out.append('\n'.join(
                (f'{i + 1}. ' if el.name == 'ol' else '- ') + inline(li).strip() for i, li in enumerate(items)))
        else:
            raise SystemExit(f'непредусмотренный тег в статье: <{el.name}>')
    return '\n\n'.join(out) + '\n'


def ru_date(value: str) -> str:
    day, month, year = value.split()
    return f'{year}-{RU_MONTHS.index(month) + 1:02d}-{int(day):02d}'


def add_missing_ru_post() -> None:
    path = POSTS / 'ru/seo-prodvizhenie-profila-onlyfans-osnovnye-tehniki.md'
    if path.exists():
        return
    page = (SRC / 'post-ru-seo.html').read_text(encoding='utf-8')
    soup = BeautifulSoup(page, 'lxml')
    info = [v.get_text(strip=True) for v in soup.select('.post-info .info-value')]
    description = soup.find('meta', attrs={'name': 'description'})['content']
    front = [
        f'title: {yaml_str(soup.select_one("h1.entry-title").get_text(strip=True))}',
        f'description: {yaml_str(description)}',
        'lang: ru',
        f'pubDate: {ru_date(info[1])}',
        f'updDate: {ru_date(info[2])}',
        f'readingTime: {yaml_str(info[3])}',
    ]
    body = to_markdown(soup.select_one('.entry-content'))
    path.write_text('---\n' + '\n'.join(front) + '\n---\n\n' + body, encoding='utf-8')
    print(f'добавлена статья {path.relative_to(ROOT)}')


def main() -> None:
    add_missing_ru_post()
    for lang, names in LISTS.items():
        found = sum((cards(n) for n in names), [])
        changed = missing = 0
        for card in found:
            path = POSTS / lang / f'{card["slug"]}.md'
            if not path.exists():
                missing += 1
                print(f'  нет статьи {lang}/{card["slug"]}')
                continue
            changed += set_excerpt(path, card['excerpt'])
        have = len(list((POSTS / lang).glob('*.md')))
        print(f'{lang}: карточек в оригинале {len(found)}, статей в проекте {have}, без статьи {missing}, записано {changed}')


if __name__ == '__main__':
    main()
