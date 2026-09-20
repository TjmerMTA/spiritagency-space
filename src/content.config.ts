import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';
import { LANGS } from './i18n';

const posts = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/posts' }),
  schema: z.object({
    title: z.string(),
    description: z.string().default(''),
    lang: z.enum(LANGS),
    pubDate: z.coerce.date(),
    updDate: z.coerce.date().optional(),
    image: z.string().optional(),
    readingTime: z.string().optional(),
    draft: z.boolean().default(false),
  }),
});

export const collections = { posts };
