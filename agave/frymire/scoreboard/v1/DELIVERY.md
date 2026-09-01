# Frymire Scoreboard — Delivery Options

Internal reference for Tyler / Sharon Oak. Current artifact: static HTML at `/agave/frymire/scoreboard/v1/`.

## 1. Static HTML on sharonoak.com (current)

**What:** Single `index.html` with embedded Slice 3 (public research) and Slice 4 (live map pack tables). Supporting files: `queries.json`, `results.json`, `fetch_local_pack.py`.

**Pros:** Zero hosting cost, private link, phone-friendly, print-to-PDF from browser, versioned in git.

**Cons:** Manual re-run to refresh live data; no filters or drill-down.

**Refresh:** `python3 fetch_local_pack.py && python3 generate_slice4.py` then re-embed or automate.

---

## 2. JSON data file + generated HTML

**What:** Keep `results.json` as source of truth; `generate_slice4.py` (or CI) rebuilds HTML on schedule.

**Pros:** Separates data from presentation; easy to diff week-over-week; same static hosting.

**Cons:** Still static until someone runs the generator.

**Next step:** GitHub Action on cron (weekly) with `VALUESERP_API_KEY` secret → commit updated `results.json` + HTML.

---

## 3. Google Sheet / CSV export

**What:** Flatten `results.json` to one row per query (market, service, query, frymire_position, giant flags, top-3 names).

**Pros:** Familiar for ops; easy share with vendors; pivot tables by market.

**Cons:** Loses narrative framing; not branded; manual or scripted export.

**Script sketch:** `python3 -c "import json,csv; ..."` from `results.json`.

---

## 4. agaveapps.com dynamic product (later)

**What:** Hosted scoreboard with client login, scheduled pulls, email alerts on encroachment.

**Pros:** Recurring revenue path; automated refresh; multi-client template from Frymire sprint.

**Cons:** Build time; needs Allison sign-off before external client access.

---

## 5. PDF from print

**What:** Browser print → Save as PDF from the HTML page (print CSS already in `index.html`).

**Pros:** Email attachment for leadership who won't click links; same artifact as web.

**Cons:** Static snapshot; no live links.

---

## 6. API / webhook (future)

**What:** Internal endpoint returns latest `results.json` for CRM or Slack bot (“Berkeys moved to #2 in Carrollton plumbing”).

**Pros:** Fits vendor accountability use case.

**Cons:** Overkill for v1 internal review.

---

## Recommendation for this sprint

Stay on **option 1** for Allison / internal review. Add **option 2** (weekly Action) if Tyler wants recurring pulls without manual runs. Defer **option 4** until Frymire external sign-off.

## API key note

`fetch_local_pack.py` reads, in order: `VALUESERP_API_KEY`, `VALUE_SERP_API_KEY`, `VALUESERP_KEY`, `SERPWOW_API_KEY`, `TRAJECT_API_KEY`. Traject Data products (ValueSerp, SERPWow) share the same Places API shape (`search_type=places`). Configure the key in Cloud Agent environment secrets or GitHub Actions secrets for automated runs.
