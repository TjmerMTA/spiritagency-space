// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { fontProviders } from 'astro/config';
import { readdirSync, readFileSync } from 'node:fs';

// Дата последнего изменения статьи для карты сайта — из её фронтматтера (updDate, иначе pubDate).
const lastmod = {};
for (const lang of readdirSync('./src/content/posts')) {
  for (const file of readdirSync(`./src/content/posts/${lang}`).filter((f) => f.endsWith('.md'))) {
    const head = readFileSync(`./src/content/posts/${lang}/${file}`, 'utf8').split('\n---')[0];
    const date = (head.match(/^updDate:\s*(\S+)/m) ?? head.match(/^pubDate:\s*(\S+)/m))?.[1];
    const slug = file.slice(0, -3);
    if (date) lastmod[lang === 'uk' ? `/${slug}/` : `/${lang}/${slug}/`] = new Date(date).toISOString();
  }
}

// Старые адреса WordPress → новые чистые адреса.
// Языковые главные и блоги жили на служебных слагах вида /ru/the-main-page-2/.
const legacy = {
  '/ru/the-main-page-2/': '/ru/',
  '/pl/glowna-strona/': '/pl/',
  '/ro/pagina-principala/': '/ro/',
  '/lt/pagrindinis-puslapis/': '/lt/',
  '/sk/hlavna-stranka/': '/sk/',
  '/ru/blog-2/': '/ru/blog/',
  '/pl/blog-3/': '/pl/blog/',
  '/ro/blog-4/': '/ro/blog/',
  '/lt/tinklarastis/': '/lt/blog/',
  '/sk/blog-5/': '/sk/blog/',
};

// Блог снова показывает по 100 статей на страницу, как исходный сайт. Пока сайт жил
// с 12 статьями на страницу, существовали /blog/page/3/…11/ и /<язык>/blog/page/2/…8/ —
// отправляем их туда, где эти статьи теперь.
const pager = {};
for (let n = 3; n <= 11; n++) pager[`/blog/page/${n}/`] = '/blog/page/2/';
for (const lang of ['ru', 'pl', 'ro', 'lt', 'sk']) {
  for (let n = 2; n <= 8; n++) pager[`/${lang}/blog/page/${n}/`] = `/${lang}/blog/`;
}

export default defineConfig({
  site: 'https://spiritagency.space',
  trailingSlash: 'always',
  build: { format: 'directory' },
  redirects: { ...legacy, ...pager },
  // Шрифт хостится сами: без render-blocking запроса к Google Fonts
  fonts: [
    // Сайт набран Montserrat от 300 до 900 (как оригинал); шрифт вариативный — один файл на набор знаков
    {
      name: 'Montserrat',
      cssVariable: '--font-montserrat',
      provider: fontProviders.google(),
      weights: ['300 900'],
      subsets: ['latin', 'latin-ext', 'cyrillic', 'cyrillic-ext'],
      styles: ['normal'],
      display: 'swap',
      fallbacks: ['sans-serif'],
    },
  ],
  integrations: [sitemap({
    serialize(item) {
      const date = lastmod[decodeURIComponent(new URL(item.url).pathname)];
      return date ? { ...item, lastmod: date } : item;
    },
    i18n: { defaultLocale: 'uk', locales: { uk: 'uk-UA', ru: 'ru-RU', pl: 'pl-PL', ro: 'ro-RO', lt: 'lt-LT', sk: 'sk-SK' } } })],
});
