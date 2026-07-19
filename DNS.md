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

## Source of truth

Edit files in the SharonOak workspace under `sites/sharonoak/`, then push to `TylerSharonOak/sharonoak`.
