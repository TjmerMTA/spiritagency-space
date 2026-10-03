/**
 * Анонс статьи для карточки блога.
 *
 * У статей из архива анонс записан в поле `excerpt` — ровно тот, что показывал
 * исходный сайт. У новой статьи без этого поля берём первые 20 слов текста,
 * как делал WordPress.
 */
const WORDS = 20;

function plain(markdown: string): string {
  return markdown
    .replace(/!\[[^\]]*\]\([^)]*\)/g, '')
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/<[^>]+>/g, '')
    .replace(/^\s{0,3}#{1,6}\s+/gm, '')
    .replace(/^\s*(?:[-*+]|\d+\.)\s+/gm, '')
    .replace(/(\*\*|__)(.*?)\1/gs, '$2')
    .replace(/(?<!\w)[*_](.+?)[*_](?!\w)/g, '$1');
}

export function excerptOf(post: { data: { excerpt?: string }; body?: string }): string {
  if (post.data.excerpt) return post.data.excerpt;
  const words = plain(post.body ?? '').split(/\s+/).filter(Boolean);
  return words.slice(0, WORDS).join(' ') + (words.length > WORDS ? '…' : '');
}
