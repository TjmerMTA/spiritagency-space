# DNS spiritagency.space

## Как было до переноса (снято 20.09.2026)

Домен зарегистрирован на GoDaddy, но зона жила у стороннего провайдера —
серверы имён `ns110.inhostedns.com`, `ns210.inhostedns.net`, `ns310.inhostedns.org`
(панель adm.tools / ukraine.com.ua). Записать что-либо через GoDaddy было нельзя,
пока NS смотрели туда.

| Тип | Имя | Значение |
|---|---|---|
| A | @ | 185.104.45.111 |
| AAAA | @ | 2a06:6440:0:2d6f::1 |
| A | * (wildcard) | 185.68.16.115, 185.104.45.111 |
| MX | @ | 0 mx.services. |
| TXT | @ | `v=spf1 include:_spf.ukraine.com.ua ~all` |
| TXT | @ | `google-site-verification=UxJTUpccuP1qKjCRZO9rwjlKEQ1s86VhUxg4rRDxKVk` |

Чего в зоне **не было**: DKIM (проверены селекторы default, google, mail, dkim,
selector1/2, k1, s1, s2, smtp, mandrill, zoho, protonmail1, dkim1), DMARC, CAA, SRV.
Отдельных записей на поддомены тоже нет — всё, что отвечало (dev2, blog, mail,
webmail, cpanel, ftp…), ловил wildcard.

Веб-хостинг 185.104.45.111 жив на портах 80/443, но отдаёт 404 — сайта там нет.
SMTP на 185.104.45.111 и 185.68.16.115 закрыт, почта ходит через `mx.services`.

## Как стало

NS переключены на стандартные GoDaddy, зона ведётся в GoDaddy.

| Тип | Имя | Значение | Зачем |
|---|---|---|---|
| A | @ | 185.199.108.153 | GitHub Pages |
| A | @ | 185.199.109.153 | GitHub Pages |
| A | @ | 185.199.110.153 | GitHub Pages |
| A | @ | 185.199.111.153 | GitHub Pages |
| CNAME | www | tjmertta.github.io | GitHub Pages |
| MX | @ | 0 mx.services. | почта как была |
| TXT | @ | `v=spf1 include:_spf.ukraine.com.ua ~all` | почта как была |
| TXT | @ | `google-site-verification=…` | Search Console |

AAAA и wildcard не переносились: первый вёл на мёртвый хост, второй отправлял
любой поддомен туда же. Понадобятся — завести отдельно.

## Откат

Вернуть у регистратора серверы имён `ns110.inhostedns.com`, `ns210.inhostedns.net`,
`ns310.inhostedns.org` — зона у прежнего провайдера при этом не удаляется
и поднимется в том виде, что в таблице выше.
