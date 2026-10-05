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
| JS на клиенте | на главной — 30 строк без библиотек (боковая панель, список языков); в блоге и статьях нет |
| Шрифт | Montserrat, самохостинг через `fonts` в `astro.config.mjs` |

## Адреса

Структура URL повторяет старый WordPress, чтобы не потерять позиции:

- `/` — главная (uk), `/ru/`, `/pl/`, `/ro/`, `/lt/`, `/sk/`
- `/blog/`, `/blog/page/2/` — по 100 статей на страницу, как на исходном сайте;
  у переводов статей меньше ста, поэтому страница одна: `/pl/blog/`
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
  content/posts/<язык>/*.md   статьи (поле excerpt — анонс для карточки блога)
  data/home.json              заголовки и описания главной по языкам
  data/home-blocks.json       тексты главной в оригинальной разметке, по языкам
  data/alternates.json        карта переводов для hreflang
  i18n.ts                     языки, подписи интерфейса, адреса, формат дат
  paginate.ts                 разбивка блога на страницы в стиле WordPress
  covers.ts                   обложки-заглушки (своих картинок у статей нет)
  excerpt.ts                  анонс статьи для карточки
  layouts/Original.astro      единственный макет: <head>, body, общий подвал
  components/Seo.astro        <head>: SEO, hreflang, OG, значок, шрифт
  components/original/        страницы в разметке исходного сайта:
                              HomePage (+ HomeHeader, HomeBody), BlogPage, PostPage, SiteFooter
  styles/original/            стили исходного сайта (не править, см. ниже)
  pages/                      маршруты
public/img/                   картинки (wp-content/uploads)
```

## Контент

Статьи вытащены из снапшотов Web Archive (май 2026), HTML переведён в Markdown.

## Поиск и превью ссылок

- `src/components/Seo.astro` — title, description, canonical, hreflang, Open Graph. Своей картинки у страницы
  нет — в превью идёт `public/og/<язык>.jpg`: первый экран главной на этом языке (1440×756 → 1200×630).
  Поменялся первый экран — переснять.
- Разметка schema.org: организация и сайт — на главной (`HomePage.astro`), статья и хлебные крошки —
  в `PostPage.astro`; сама организация описана один раз в `src/i18n.ts`.
- `src/pages/404.astro` — страница «не найдено», одна на все языки (так её отдаёт GitHub Pages).
- Картинки лежат в `public/img` парами: исходный PNG и WebP без потерь (`cwebp -lossless -z 9 -exact`);
  страницы ссылаются на WebP. Значки сайта и флаги остались PNG.
- Дата изменения статьи в карте сайта берётся из её фронтматтера — см. `astro.config.mjs`.

## Сайт — в оригинальном виде

Главная, блог и статьи повторяют исходный сайт один в один: разметка и стили взяты
из архива, а не написаны заново. Сверка — попиксельная, на ширинах от 360 до 1920.

- `docs/restore/original-src/` — сырые снимки страниц и CSS из Web Archive;
- `docs/restore/port-css.py` — кладёт стили в `src/styles/original/` и собирает три набора:
  `home.css`, `blog.css`, `post.css`;
- `docs/restore/port-home.py` — собирает `HomeBody.astro`, `SiteFooter.astro`
  и `src/data/home-blocks.json` (тексты по языкам);
- `docs/restore/port-blog.py` — записывает в статьи анонсы из карточек оригинала;
- `docs/restore/fix-bold.py` — чинит выделение жирным, сломанное при переводе в Markdown;
- `docs/restore/REPORT.md` — что отличалось, что исправлено, что осталось.

Файлы в `src/styles/original/` руками не править — они перезаписываются скриптом.
Нужна поправка — в `home-fixes.css`. Классы `elementor-*`, `blog-*` и остальные из
оригинала в разметке менять нельзя: на них держатся стили.

Шапки с меню у блога и статей нет — так было на исходном сайте; общий подвал
«Деталі співпраці» стоит на всех страницах.
