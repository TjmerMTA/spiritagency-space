#!/usr/bin/env bash
# Выкладка на GitHub Pages: собрать и залить dist/ в ветку gh-pages.
# Actions не используем — у токена нет scope workflow, ветка надёжнее.
set -euo pipefail
cd "$(dirname "$0")"

npm run build

tmp=$(mktemp -d)
cp -R dist/. "$tmp/"
touch "$tmp/.nojekyll"          # иначе Pages прячет папки, начинающиеся с _

git worktree remove --force .gh-pages 2>/dev/null || true
git worktree add --detach .gh-pages
cd .gh-pages
git checkout --orphan gh-pages
git rm -rq --cached . 2>/dev/null || true
find . -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -R "$tmp/." .
git add -A
git commit -qm "Сборка $(date '+%Y-%m-%d %H:%M')"
git push -f origin gh-pages
cd ..
git worktree remove --force .gh-pages
rm -rf "$tmp"
echo "Готово: https://spiritagency.space/"
