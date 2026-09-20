# spiritagency.space

Сайт модельного агентства SpiritAgency, восстановленный из Web Archive
и перенесённый с WordPress + Elementor на **Astro 7** (статическая генерация).

## Что внутри

| | |
|---|---|
| Движок | Astro 7, `output: static`, `build.format: 'directory'` |
| Контент | Markdown в `src/content/posts/<язык>/`, коллекция с zod-схемой |
| Языки | uk (основной, без префикса), ru, pl, ro, lt, sk — `/ru/…` и т.д. |
| Статей | ~600 (uk 125, остальные по ~95) |
| JS на клиенте | нет (меню на CSS `:checked`) |
| Шрифт | Inter, самохостинг через `fonts` в `astro.config.mjs` |

## Адреса

Структура URL повторяет старый WordPress, чтобы не потерять позиции:

- `/` — главная (uk), `/ru/`, `/pl/`, `/ro/`, `/lt/`, `/sk/`
- `/blog/`, `/blog/page/2/` … и то же с языковым префиксом
- `/<слаг>/` — статья на uk, `/<язык>/<слаг>/` — перевод
- старые служебные адреса (`/ru/the-main-page-2/`, `/lt/tinklarastis/` …)
  отдают редирект на чистые — см. `legacy` в `astro.config.mjs`

`hreflang` между переводами берётся из `src/data/alternates.json` —
карта построена по данным исходного сайта, слаги у переводов разные.

## Разработка

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # dist/
npm run preview  # отдаёт готовую сборку
```

## Структура

```
src/
  content/posts/<язык>/*.md   статьи
  data/home.json              тексты главной по языкам
  data/alternates.json        карта переводов для hreflang
  i18n.ts                     языки, подписи интерфейса, помощники адресов
  paginate.ts                 разбивка на страницы в стиле WordPress
  layouts/Base.astro          <head>, SEO, hreflang, OG
  components/                 Header, Footer, Home, BlogIndex, PostCard
  pages/                      маршруты
public/img/                   картинки (wp-content/uploads)
```

## Контент

Статьи и тексты главной вытащены из снапшотов Web Archive (май 2026),
HTML переведён в Markdown, служебная разметка Elementor выброшена.
Вёрстка и стили написаны заново.
