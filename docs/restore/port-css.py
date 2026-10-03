#!/usr/bin/env python3
"""Кладёт оригинальные стили сайта в src/styles/original/ в том же порядке,
в каком их подключала главная на WordPress.

Источники: original-src/css (снимок архива 24.03.2026), original-src/stock
(штатные файлы темы и Elementor, которых в архиве нет — взяты с wordpress.org
тех же версий) и <style> из самой страницы.

В файлах меняется только то, без чего они не заработают вне WordPress:
  - адреса картинок: …/wp-content/uploads/ → /img/;
  - имя шрифта: "Montserrat" → var(--font-montserrat-full), потому что Astro отдаёт
    шрифт под своим именем через эту переменную;
  - незакрытый блок в конце пользовательского CSS закрывается, пустые правила «{}»
    и ссылка на несуществующую картинку убираются — сборщик на них спотыкается,
    а браузер и так их пропускал.
Сами правила не правятся: нужна другая вёрстка — пиши поверх, в home-fixes.css.

Запуск из корня проекта: python3 docs/restore/port-css.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = Path(__file__).resolve().parent / 'original-src'
OUT = ROOT / 'src/styles/original'

# Порядок подключения на главной (см. <head> в original-src/home-uk.html).
# Пропущены: admin-bar и dashicons (панель администратора), header-footer темы,
# post-72 и post-912 — на главной под них нет ни одного элемента; шрифты Roboto
# и Roboto Slab — видимого текста ими на главной нет.
ORDER = [
    ('wp-inline.css', 'inline:wp-img-auto-sizes-contain-inline-css,wp-emoji-styles-inline-css,global-styles-inline-css'),
    ('hello-style.min.css', 'css/style.min.css'),
    ('hello-theme.min.css', 'css/theme.min.css'),
    ('custom-frontend.min.css', 'css/custom-frontend.min.css'),
    ('post-6.css', 'css/post-6.css'),
    ('widget-image.min.css', 'css/widget-image.min.css'),
    ('widget-menu-anchor.min.css', 'css/widget-menu-anchor.min.css'),
    ('custom-widget-icon-list.min.css', 'css/custom-widget-icon-list.min.css'),
    ('custom-pro-widget-nav-menu.min.css', 'css/custom-pro-widget-nav-menu.min.css'),
    ('widget-heading.min.css', 'css/widget-heading.min.css'),
    ('fadeInLeft.min.css', 'css/fadeInLeft.min.css'),
    ('widget-off-canvas.min.css', 'css/widget-off-canvas.min.css'),
    ('custom-widget-icon-box.min.css', 'css/custom-widget-icon-box.min.css'),
    ('widget-spacer.min.css', 'stock/widget-spacer.min.css'),
    ('post-9.css', 'css/post-9.css'),
    ('wp-custom.css', 'inline:wp-custom-css'),
    ('post-906.css', 'css/post-906.css'),
]


def port(css: str) -> str:
    css = re.sub(r'(?:https?://(?:www\.)?spiritagency\.space/wp-content/uploads/|(?:\.\./)+public/img/)', '/img/', css)
    css = css.replace('"Montserrat"', 'var(--font-montserrat-full)')
    # Elementor оставляет пустые правила «{}» без селектора — сборщик на них падает.
    css = re.sub(r'(?<=\})\s*\{\}', '', css)
    # Фон шапки блога ссылался на файл, которого на сервере не было (в архиве — 404).
    css = re.sub(r"\s*background: url\('/wp-content/themes/your-theme/[^;]+;", '', css)
    css = css.strip()
    # Пользовательский CSS оригинала обрывается на «a {» — браузер такое прощает,
    # сборщик нет. Закрываем блок так же, как это молча делал браузер.
    css += '}' * (css.count('{') - css.count('}'))
    return css + '\n'


def inline(ids: str) -> str:
    page = (SRC / 'home-uk.html').read_text(encoding='utf-8')
    parts = []
    for style_id in ids.split(','):
        m = re.search(r'<style id=[\'"]%s[\'"][^>]*>(.*?)</style>' % re.escape(style_id), page, flags=re.S)
        parts.append(f'/* <style id="{style_id}"> */\n' + m.group(1).strip())
    return '\n\n'.join(parts)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, source in ORDER:
        css = inline(source[7:]) if source.startswith('inline:') else (SRC / source).read_text(encoding='utf-8')
        (OUT / name).write_text(port(css), encoding='utf-8')
        print(f'{name:40} {len(css):>7}')
    index = '/* Оригинальные стили главной, порядок как на WordPress. Собрано docs/restore/port-css.py */\n'
    index += ''.join(f"@import './{name}';\n" for name, _ in ORDER)
    index += "@import './home-fixes.css';\n"
    (OUT / 'home.css').write_text(index, encoding='utf-8')


if __name__ == '__main__':
    main()
