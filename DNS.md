# Sharon Oak — GitHub Pages

Static holding-company site for **sharonoak.com**.

## Deploy

Repo: publish this folder to a GitHub Pages repo (e.g. `TylerYost/sharonoak`) with Pages source = `main` / root.

## DNS cutover (from current Apache host → GitHub Pages)

1. In the GitHub repo: **Settings → Pages → Custom domain** = `sharonoak.com` (and enable HTTPS once DNS propagates).
2. At your DNS provider, replace the current A/CNAME records that point at Apache with GitHub Pages records:

**Apex (`sharonoak.com`) — A records** (GitHub Pages):

| Type | Host | Value |
|---|---|---|
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |

Optional IPv6 AAAA: `2606:50c0:8000::153` … `8003::153` (see [GitHub Pages custom domain docs](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)).

**www — CNAME:**

| Type | Host | Value |
|---|---|---|
| CNAME | `www` | `tyleryost.github.io` |

(Use your GitHub username/org Pages host. If the repo is under a different account, use `<account>.github.io`.)

3. Wait for DNS + GitHub certificate provisioning (often &lt;1 hour, sometimes longer).
4. Confirm `https://sharonoak.com` loads this holding page and Agave Apps links to `https://agaveapps.com`.

**Leave AgaveApps.com on its current host** until you stand up dynamic hosting.
