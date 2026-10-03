#!/usr/bin/env python3
"""Чинит выделение жирным в статьях, сломанное при переводе HTML → Markdown.

При восстановлении сайта конвертер терял один из двух маркеров `**`, если жирный
фрагмент упирался в край заголовка, и оставлял пробел внутри маркеров
(`**текст **`). Markdown такое жирным не считает — на страницах были видны звёздочки.

  ### 1. **Помилки моделей OnlyFans      →  ### 1. **Помилки моделей OnlyFans**
  ### Правила колаборацій** та підхід    →  ### **Правила колаборацій** та підхід
  слово **текст **далі                   →  слово **текст** далі
  - **Назва:**Текст                      →  - <b>Назва:</b>Текст

Какой маркер потерян, видно по соседям уцелевшего: открывающий стоит перед буквой,
закрывающий — после буквы. В оригинале (см. original-src/post-uk.html) это <b>…</b>.

Запуск из корня проекта: python3 docs/restore/fix-bold.py
"""
import re
from pathlib import Path

POSTS = Path(__file__).resolve().parents[2] / 'src/content/posts'
HEADING = re.compile(r'^(#{1,6} )(.*)$')


def fix_heading(text: str) -> str:
    at = text.index('**')
    before, after = text[:at], text[at + 2:]
    opening = bool(after) and not after[0].isspace() and (not before or before[-1].isspace())
    return f'{text.rstrip()}**' if opening else f'**{text}'


def fix_pairs(line: str) -> str:
    parts = line.split('**')
    if len(parts) % 2 == 0:          # нечётное число маркеров — не трогаем
        return line
    out = parts[0]
    for i in range(1, len(parts), 2):
        inner, outer = parts[i], parts[i + 1]
        lead = inner[:len(inner) - len(inner.lstrip(' '))]
        trail = inner[len(inner.rstrip(' ')):]
        core = inner.strip(' ')
        # Пробелы выносим наружу; если снаружи уже есть пробел — второй не нужен.
        if lead and out.endswith(' '):
            lead = ''
        if trail and outer.startswith(' '):
            trail = ''
        if not core:
            out += lead + trail + outer
            continue
        # «**Назва:**Текст» Markdown жирным не считает: закрывающий маркер после знака
        # препинания и вплотную к букве. В оригинале так и было — <b>Назва:</b>Текст,
        # без пробела, поэтому пишем тегом.
        punct = lambda ch: not ch.isalnum() and not ch.isspace()
        tight_close = punct(core[-1]) and not trail and outer[:1].isalnum()
        tight_open = punct(core[0]) and not lead and out[-1:].isalnum()
        mark = ('<b>', '</b>') if tight_close or tight_open else ('**', '**')
        out += f'{lead}{mark[0]}{core}{mark[1]}{trail}{outer}'
    return out


def main() -> None:
    headings = pairs = files = 0
    for path in sorted(POSTS.glob('*/*.md')):
        text = path.read_text(encoding='utf-8')
        head, sep, body = text.partition('\n---\n')
        lines = body.split('\n')
        for i, line in enumerate(lines):
            m = HEADING.match(line)
            if m and line.count('**') == 1:
                lines[i] = m.group(1) + fix_heading(m.group(2))
                headings += 1
            fixed = fix_pairs(lines[i])
            if fixed != lines[i]:
                lines[i] = fixed
                pairs += 1
        new = head + sep + '\n'.join(lines)
        if new != text:
            path.write_text(new, encoding='utf-8')
            files += 1
    print(f'заголовков с потерянным маркером: {headings}, строк с пробелом внутри маркеров: {pairs}, файлов: {files}')


if __name__ == '__main__':
    main()
