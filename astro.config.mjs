// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { fontProviders } from 'astro/config';

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

export default defineConfig({
  site: 'https://spiritagency.space',
  trailingSlash: 'always',
  build: { format: 'directory' },
  redirects: legacy,
  // Шрифт хостится сами: без render-blocking запроса к Google Fonts
  fonts: [
    {
      name: 'Montserrat',
      cssVariable: '--font-montserrat',
      provider: fontProviders.google(),
      weights: [400, 600, 800],
      subsets: ['latin', 'latin-ext', 'cyrillic', 'cyrillic-ext'],
      styles: ['normal'],
      display: 'swap',
      fallbacks: ['system-ui', 'sans-serif'],
    },
  ],
  integrations: [sitemap({ i18n: { defaultLocale: 'uk', locales: { uk: 'uk-UA', ru: 'ru-RU', pl: 'pl-PL', ro: 'ro-RO', lt: 'lt-LT', sk: 'sk-SK' } } })],
});
