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

/** Размеры заглушек — чтобы карточки не прыгали, пока картинка грузится. */
const SIZES: Record<string, [number, number]> = {
  '/img/2026/02/girl_unique_600x653.png': [600, 653],
  '/img/2026/02/unique_triptych_same_shape_684x240.png': [684, 240],
  '/img/2025/01/image-83.png': [402, 414],
  '/img/2025/01/388089_0e3a224228e64e21b17e09b73772d23amv2.png': [875, 581],
  '/img/2025/01/image-10.png': [627, 726],
  '/img/2025/01/image-7.png': [717, 525],
  '/img/2025/01/Frame-6.png': [578, 613],
};

/** Обложка статьи с размерами: своя, если есть, иначе заглушка по слагу. */
export function coverOf(slug: string, image?: string) {
  const src = image || coverFor(slug);
  const [width, height] = SIZES[src] ?? [];
  return { src, width, height, placeholder: !image };
}

/** Устойчивый выбор обложки по слагу — при пересборке картинка не «прыгает». */
export function coverFor(slug: string): string {
  let h = 0;
  for (const ch of slug) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
  return COVERS[h % COVERS.length];
}
