/**
 * Обложки для статей.
 *
 * Свои картинки статей не сохранились: Wayback заархивировал из
 * wp-content/uploads всего 25 файлов, оригинальный сервер отключён.
 * Поэтому под обложки идут настоящие фотографии с самого сайта —
 * те, что уцелели, — и раскладываются по статьям детерминированно,
 * чтобы у записи всегда была одна и та же картинка.
 */
export const COVERS = [
  '/img/2026/02/girl_unique_600x653.png',
  '/img/2026/02/unique_triptych_same_shape_684x240.png',
  '/img/2025/01/image-83.png',
  '/img/2025/01/388089_0e3a224228e64e21b17e09b73772d23amv2.png',
  '/img/2025/01/image-10.png',
  '/img/2025/01/image-7.png',
] as const;

/** Устойчивый выбор обложки по слагу — при пересборке картинка не «прыгает». */
export function coverFor(slug: string): string {
  let h = 0;
  for (const ch of slug) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
  return COVERS[h % COVERS.length];
}
