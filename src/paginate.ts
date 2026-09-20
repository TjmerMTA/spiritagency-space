/**
 * Ручная разбивка на страницы: адреса как в старом WordPress —
 * /blog/ , /blog/page/2/ , /blog/page/3/ …
 * Astro-шный paginate() даёт /blog/2/, поэтому считаем сами.
 */
export const PAGE_SIZE = 12;

export interface PageInfo<T> {
  data: T[];
  currentPage: number;
  lastPage: number;
  url: { prev?: string; next?: string; current: string };
}

export function pages<T>(items: T[], root: string, size = PAGE_SIZE) {
  const last = Math.max(1, Math.ceil(items.length / size));
  const url = (n: number) => (n === 1 ? root : `${root}page/${n}/`);
  return Array.from({ length: last }, (_, i) => {
    const n = i + 1;
    const info: PageInfo<T> = {
      data: items.slice(i * size, i * size + size),
      currentPage: n,
      lastPage: last,
      url: {
        current: url(n),
        prev: n > 1 ? url(n - 1) : undefined,
        next: n < last ? url(n + 1) : undefined,
      },
    };
    /** суффикс пути относительно корня раздела: '' | 'page/2' */
    const suffix = n === 1 ? undefined : `page/${n}`;
    return { suffix, page: info };
  });
}
