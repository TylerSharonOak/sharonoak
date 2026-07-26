# Sharon Oak — GitHub Pages

Static holding-company site for **sharonoak.com**.

**Repo:** [TylerSharonOak/sharonoak](https://github.com/TylerSharonOak/sharonoak)  
**Pages host (before DNS):** `https://tylersharonoak.github.io/sharonoak/` (redirects to custom domain once DNS is live)

## DNS cutover (from current Apache host → GitHub Pages)

1. In the repo: **Settings → Pages** should show custom domain `sharonoak.com` (already set via API). Enable **Enforce HTTPS** after DNS propagates and the cert is ready.
2. At your DNS provider, replace the current Apache records with:

**Apex (`sharonoak.com`) — A records:**

| Type | Host | Value |
|---|---|---|
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |

Optional IPv6 AAAA: see [GitHub Pages custom domain docs](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site).

**www — CNAME:**

| Type | Host | Value |
|---|---|---|
| CNAME | `www` | `tylersharonoak.github.io` |

3. Wait for DNS + GitHub certificate (often under an hour).
4. Confirm `https://sharonoak.com` shows the holding page and Agave Apps links to `https://agaveapps.com`.

**Leave AgaveApps.com on its current host** until you stand up dynamic hosting.

## Live check (2026-07-25) — fix this

Apex currently resolves to **mixed** A records:

| IP | Status |
|---|---|
| `185.199.109.153` / `.110.` / `.111.` | GitHub Pages ✅ |
| `162.210.101.52` | **Stale (old Apache host)** — delete |
| `185.199.108.153` | **Missing** — add |

Symptom: `http://sharonoak.com/...` often works; `https://` returns **403** (wrong origin / cert never completes). Until fixed, share Scoreboard as `http://sharonoak.com/agave/rhm/scoreboard/v1/` or open the local HTML — don’t rely on HTTPS links.

**Do now at DNS provider:** remove `162.210.101.52`; ensure all four GitHub A records above; wait for cert → then Enforce HTTPS in Pages settings.

## Source of truth

Edit files in the SharonOak workspace under `sites/sharonoak/`, then push to `TylerSharonOak/sharonoak`.

## Private share pages (no nav)

Unlisted HTML — not linked from the homepage.

**Path convention:** `/{sharon-oak-project}/{client}/{client-project}/{version}/`  
Example: `agave` / `rhm` (Red Hook) / `scoreboard` / `v1`.

| Path | Purpose |
|---|---|
| [/agave/rhm/scoreboard/v1/](https://sharonoak.com/agave/rhm/scoreboard/v1/) | Project Scoreboard v1 — Red Hook / Chase |
| [/agave/rhm/](https://sharonoak.com/agave/rhm/) · [/agave/pl1-CW/](https://sharonoak.com/agave/pl1-CW/) | Redirect → current version |

Source: `sites/sharonoak/agave/rhm/scoreboard/v1/index.html` (also mirrored from `products/agave-landscape/one-pager.html`). Pages have `noindex`.
