export const LANGS = ['uk', 'ru', 'pl', 'ro', 'lt', 'sk'] as const;
export type Lang = (typeof LANGS)[number];

export const DEFAULT_LANG: Lang = 'uk';

/** Метка языка в переключателе */
export const LANG_LABEL: Record<Lang, string> = {
  uk: 'UA', ru: 'RU', pl: 'PL', ro: 'RO', lt: 'LT', sk: 'SK',
};

/** Значение атрибута lang="" */
export const HTML_LANG: Record<Lang, string> = {
  uk: 'uk-UA', ru: 'ru-RU', pl: 'pl-PL', ro: 'ro-RO', lt: 'lt-LT', sk: 'sk-SK',
};

export const TELEGRAM = 'https://t.me/SpiritOriginal';

type Ui = {
  promo: string; about: string; blog: string; income: string; guarantees: string;
  advance: string; apply: string; blogTitle: string; blogLead: string;
  readMore: string; readingTime: string; published: string; updated: string;
  author: string; home: string; allPosts: string; related: string;
  prev: string; next: string; page: string; rights: string; menu: string;
};

export const UI: Record<Lang, Ui> = {
  uk: {
    promo: 'Просування OnlyFans', about: 'Про нас', blog: 'Блог', income: 'Прибуток',
    guarantees: 'Гарантії', advance: 'Аванс $150', apply: 'Подати кандидатуру',
    blogTitle: 'Наш блог', blogLead: 'Статті про просування, безпеку та заробіток на OnlyFans',
    readMore: 'Читати далі', readingTime: 'Час читання', published: 'Опубліковано',
    updated: 'Оновлено', author: 'Автор', home: 'Головна', allPosts: 'Усі статті',
    related: 'Схожі статті', prev: 'Назад', next: 'Далі', page: 'Сторінка',
    rights: 'Усі права захищено', menu: 'Меню',
  },
  ru: {
    promo: 'Продвижение OnlyFans', about: 'О нас', blog: 'Блог', income: 'Доход',
    guarantees: 'Гарантии', advance: 'Аванс $150', apply: 'Подать кандидатуру',
    blogTitle: 'Наш блог', blogLead: 'Статьи о продвижении, безопасности и заработке на OnlyFans',
    readMore: 'Читать далее', readingTime: 'Время чтения', published: 'Опубликовано',
    updated: 'Обновлено', author: 'Автор', home: 'Главная', allPosts: 'Все статьи',
    related: 'Похожие статьи', prev: 'Назад', next: 'Далее', page: 'Страница',
    rights: 'Все права защищены', menu: 'Меню',
  },
  pl: {
    promo: 'Promocja OnlyFans', about: 'O nas', blog: 'Blog', income: 'Zysk',
    guarantees: 'Gwarancje', advance: 'Zaliczka $150', apply: 'Zgłoś kandydaturę',
    blogTitle: 'Nasz blog', blogLead: 'Artykuły o promocji, bezpieczeństwie i zarobkach na OnlyFans',
    readMore: 'Czytaj dalej', readingTime: 'Czas czytania', published: 'Opublikowano',
    updated: 'Zaktualizowano', author: 'Autor', home: 'Strona główna', allPosts: 'Wszystkie artykuły',
    related: 'Podobne artykuły', prev: 'Wstecz', next: 'Dalej', page: 'Strona',
    rights: 'Wszelkie prawa zastrzeżone', menu: 'Menu',
  },
  ro: {
    promo: 'Promovare OnlyFans', about: 'Despre noi', blog: 'Blog', income: 'Profit',
    guarantees: 'Garanții', advance: 'Avans $150', apply: 'Trimite candidatura',
    blogTitle: 'Blogul nostru', blogLead: 'Articole despre promovare, siguranță și câștiguri pe OnlyFans',
    readMore: 'Citește mai mult', readingTime: 'Timp de citire', published: 'Publicat',
    updated: 'Actualizat', author: 'Autor', home: 'Acasă', allPosts: 'Toate articolele',
    related: 'Articole similare', prev: 'Înapoi', next: 'Înainte', page: 'Pagina',
    rights: 'Toate drepturile rezervate', menu: 'Meniu',
  },
  lt: {
    promo: 'Skatinimas OnlyFans', about: 'Apie mus', blog: 'Tinklaraštis', income: 'Pelnas',
    guarantees: 'Garantijos', advance: 'Avansas $150', apply: 'Pateikti kandidatūrą',
    blogTitle: 'Mūsų tinklaraštis', blogLead: 'Straipsniai apie skatinimą, saugumą ir uždarbį OnlyFans',
    readMore: 'Skaityti toliau', readingTime: 'Skaitymo laikas', published: 'Paskelbta',
    updated: 'Atnaujinta', author: 'Autorius', home: 'Pradžia', allPosts: 'Visi straipsniai',
    related: 'Panašūs straipsniai', prev: 'Atgal', next: 'Toliau', page: 'Puslapis',
    rights: 'Visos teisės saugomos', menu: 'Meniu',
  },
  sk: {
    promo: 'Propagácia OnlyFans', about: 'O nás', blog: 'Blog', income: 'Zisk',
    guarantees: 'Záruky', advance: 'Záloha $150', apply: 'Poslať kandidatúru',
    blogTitle: 'Náš blog', blogLead: 'Články o propagácii, bezpečnosti a zárobku na OnlyFans',
    readMore: 'Čítať ďalej', readingTime: 'Čas čítania', published: 'Publikované',
    updated: 'Aktualizované', author: 'Autor', home: 'Domov', allPosts: 'Všetky články',
    related: 'Podobné články', prev: 'Späť', next: 'Ďalej', page: 'Strana',
    rights: 'Všetky práva vyhradené', menu: 'Menu',
  },
};

/** Корень языка: uk — без префикса, остальные — /xx/ */
export const home = (lang: Lang) => (lang === DEFAULT_LANG ? '/' : `/${lang}/`);
export const blogRoot = (lang: Lang) => (lang === DEFAULT_LANG ? '/blog/' : `/${lang}/blog/`);
export const postUrl = (lang: Lang, slug: string) =>
  lang === DEFAULT_LANG ? `/${slug}/` : `/${lang}/${slug}/`;
