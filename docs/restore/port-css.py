#!/usr/bin/env python3
"""Кладёт оригинальные стили сайта в src/styles/original/ и собирает из них три набора
(главная, блог, статья) — в том порядке, в каком их подключал WordPress.

Источники: original-src/css (снимок архива 24.03.2026), original-src/stock
(штатные файлы темы и Elementor, которых в архиве нет — взяты с wordpress.org
тех же версий) и <style> из самой страницы.

В файлах меняется только то, без чего они не заработают вне WordPress:
  - адреса картинок: …/wp-content/uploads/ → /img/;
  - имя шрифта: "Montserrat" → var(--font-montserrat), потому что Astro отдаёт
    шрифт под своим именем через эту переменную;
  - незакрытый блок в конце пользовательского CSS закрывается, пустые правила «{}»
    и ссылка на несуществующую картинку убираются — сборщик на них спотыкается,
    а браузер и так их пропускал.
Сами правила не правятся: нужна другая вёрстка — пиши поверх, в home-fixes.css.
Исключение — библиотека блоков WordPress: из неё выброшены правила для блоков редактора.

Запуск из корня проекта: python3 docs/restore/port-css.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = Path(__file__).resolve().parent / 'original-src'
OUT = ROOT / 'src/styles/original'

# Файлы: имя в src/styles/original/ → откуда взять.
#   css/…, stock/…  — файл из original-src;
#   inline:<id,…>   — <style id="…"> со страницы (после «@» — с какой, по умолчанию главная);
#   inline-body@…   — безымянный <style> шаблона статьи (стоит в теле страницы).
SOURCES = {
    'wp-inline.css': 'inline:wp-img-auto-sizes-contain-inline-css,wp-emoji-styles-inline-css',
    'block-library.css': 'stock/block-library.min.css',
    'wp-global-styles.css': 'inline:global-styles-inline-css',
    'hello-style.min.css': 'css/style.min.css',
    'hello-theme.min.css': 'css/theme.min.css',
    'custom-frontend.min.css': 'css/custom-frontend.min.css',
    'post-6.css': 'css/post-6.css',
    'widget-image.min.css': 'css/widget-image.min.css',
    'widget-menu-anchor.min.css': 'css/widget-menu-anchor.min.css',
    'custom-widget-icon-list.min.css': 'css/custom-widget-icon-list.min.css',
    'custom-pro-widget-nav-menu.min.css': 'css/custom-pro-widget-nav-menu.min.css',
    'widget-heading.min.css': 'css/widget-heading.min.css',
    'fadeInLeft.min.css': 'css/fadeInLeft.min.css',
    'widget-off-canvas.min.css': 'css/widget-off-canvas.min.css',
    'custom-widget-icon-box.min.css': 'css/custom-widget-icon-box.min.css',
    'widget-spacer.min.css': 'stock/widget-spacer.min.css',
    'post-9.css': 'css/post-9.css',
    'wp-custom.css': 'inline:wp-custom-css',
    'single-post.css': 'inline-body@post-uk.html',
    'post-906.css': 'css/post-906.css',
}

# Порядок подключения — как в <head> соответствующей страницы оригинала.
# Пропущены: admin-bar и dashicons (панель администратора), header-footer темы,
# post-72 и post-912 — под них на страницах нет ни одного элемента; шрифты Roboto
# и Roboto Slab — видимого текста ими нет.
COMMON = ['hello-style.min.css', 'hello-theme.min.css', 'custom-frontend.min.css', 'post-6.css',
          'widget-image.min.css', 'widget-menu-anchor.min.css', 'custom-widget-icon-list.min.css']
BUNDLES = {
    'home.css': ['wp-inline.css', 'wp-global-styles.css', *COMMON,
                 'custom-pro-widget-nav-menu.min.css', 'widget-heading.min.css', 'fadeInLeft.min.css',
                 'widget-off-canvas.min.css', 'custom-widget-icon-box.min.css', 'widget-spacer.min.css',
                 'post-9.css', 'wp-custom.css', 'post-906.css', 'home-fixes.css'],
    'blog.css': ['wp-inline.css', 'block-library.css', 'wp-global-styles.css', *COMMON,
                 'wp-custom.css', 'post-906.css'],
    'post.css': ['wp-inline.css', 'block-library.css', 'wp-global-styles.css', *COMMON,
                 'wp-custom.css', 'single-post.css', 'post-906.css'],
}

# Библиотека блоков WordPress — 120 КБ правил для блоков редактора, которых в статьях
# нет: тексты хранятся в Markdown и таких классов не получают. Оставляем только правила,
# способные сработать на обычной разметке (ol, ul, img, figure, .screen-reader-text…).
BLOCK_ONLY = re.compile(r'\.(?:wp-block|wp-element|has-|is-|blocks-|block-editor|editor-styles|wp-lightbox|components-)')


def split_selectors(prelude: str) -> list[str]:
    parts, depth, cur = [], 0, ''
    for ch in prelude:
        depth += ch in '([' 
        depth -= ch in ')]'
        if ch == ',' and depth == 0:
            parts.append(cur)
            cur = ''
        else:
            cur += ch
    return parts + [cur]


def prune_blocks(css: str) -> str:
    out, i = [], 0
    while i < len(css):
        open_at = css.find('{', i)
        if open_at < 0:
            break
        depth, j = 1, open_at + 1
        while depth:
            depth += {'{': 1, '}': -1}.get(css[j], 0)
            j += 1
        prelude, body = css[i:open_at].strip(), css[open_at + 1:j - 1]
        i = j
        if prelude.startswith(('@media', '@supports')):
            inner = prune_blocks(body)
            if inner:
                out.append(f'{prelude}{{{inner}}}')
        elif prelude.startswith('@'):
            out.append(f'{prelude}{{{body}}}')
        else:
            keep = [sel for sel in split_selectors(prelude) if not BLOCK_ONLY.search(sel)]
            if keep:
                out.append(f'{",".join(keep)}{{{body}}}')
    return ''.join(out)


def port(css: str) -> str:
    css = re.sub(r'(?:https?://(?:www\.)?spiritagency\.space/wp-content/uploads/|(?:\.\./)+public/img/)', '/img/', css)
    css = css.replace('"Montserrat"', 'var(--font-montserrat)')
    # Elementor оставляет пустые правила «{}» без селектора — сборщик на них падает.
    css = re.sub(r'(?<=\})\s*\{\}', '', css)
    # Фон шапки блога ссылался на файл, которого на сервере не было (в архиве — 404).
    css = re.sub(r"\s*background: url\('/wp-content/themes/your-theme/[^;]+;", '', css)
    css = css.strip()
    # Пользовательский CSS оригинала обрывается на «a {» — браузер такое прощает,
    # сборщик нет. Закрываем блок так же, как это молча делал браузер.
    css += '}' * (css.count('{') - css.count('}'))
    return css + '\n'


def inline(ids: str, page_name: str = 'home-uk.html') -> str:
    page = (SRC / page_name).read_text(encoding='utf-8')
    parts = []
    for style_id in ids.split(','):
        m = re.search(r'<style id=[\'"]%s[\'"][^>]*>(.*?)</style>' % re.escape(style_id), page, flags=re.S)
        parts.append(f'/* <style id="{style_id}"> */\n' + m.group(1).strip())
    return '\n\n'.join(parts)


def inline_body(page_name: str) -> str:
    """Стили шаблона статьи: безымянный <style> сразу после </main>."""
    page = (SRC / page_name).read_text(encoding='utf-8')
    m = re.search(r'</main>\s*<style>(.*?)</style>', page, flags=re.S)
    return f'/* <style> из шаблона статьи, {page_name} */\n' + m.group(1).strip()


def read(source: str) -> str:
    if source.startswith('inline-body@'):
        return inline_body(source.split('@')[1])
    if source.startswith('inline:'):
        return inline(source[7:])
    css = (SRC / source).read_text(encoding='utf-8')
    if source.endswith('block-library.min.css'):
        return prune_blocks(css.replace('@charset "UTF-8";', ''))
    return css


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, source in SOURCES.items():
        css = read(source)
        (OUT / name).write_text(port(css), encoding='utf-8')
        print(f'{name:40} {len(css):>7}')
    for bundle, files in BUNDLES.items():
        index = f'/* Оригинальные стили, порядок как на WordPress. Собрано docs/restore/port-css.py */\n'
        index += ''.join(f"@import './{name}';\n" for name in files)
        (OUT / bundle).write_text(index, encoding='utf-8')


if __name__ == '__main__':
    main()
