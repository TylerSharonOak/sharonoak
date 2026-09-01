# Frymire Scoreboard — Delivery Options

Internal reference for Tyler / Sharon Oak.

| Artifact | Path | Audience |
|---|---|---|
| Internal dossier | [`/agave/frymire/scoreboard/v1/`](https://sharonoak.com/agave/frymire/scoreboard/v1/) | Sharon Oak / Agave working notes |
| **Customer Territory Scoreboard** | [`/agave/frymire/scoreboard/v1/report/`](https://sharonoak.com/agave/frymire/scoreboard/v1/report/) | Showable report (Allison · Granite Comfort before Frymire leadership) |

Supporting files: `queries.json`, `results.json`, `fetch_local_pack.py`, `generate_slice4.py`, `generate_report.py`.

---

## 1. Customer report (primary show piece)

**What:** Short Territory Scoreboard — hero, three stats, 8×2 status grid, three defend actions. Generated from `results.json`. No sprint backlog, no Slice labels.

**Refresh:**

```bash
cd agave/frymire/scoreboard/v1
python3 fetch_local_pack.py    # needs VALUESERP_API_KEY or SERPWOW_API_KEY
python3 generate_report.py     # writes report/index.html
python3 generate_slice4.py     # optional — refresh internal Slice 4 fragment
```

**Pros:** Phone-friendly, print-to-PDF, versioned in git, Agave Apps product frame.

**Cons:** Static until regenerate; share gated on Allison sign-off.

**Share gate:** Do not send `report/` to Frymire leadership until Allison · Granite Comfort approves.

---

## 2. Static HTML dossier on sharonoak.com (internal)

**What:** Full sprint dossier with Slice 3 research + Slice 4 live tables.

**Pros:** Zero hosting cost, private link, full methodology.

**Cons:** Not customer-ready — use `report/` for external-facing reviews.

---

## 3. JSON data file + generated HTML

**What:** `results.json` is source of truth; generators rebuild customer report and Slice 4.

**Next step:** GitHub Action on weekly cron (see `.github/workflows/frymire-scoreboard-refresh.yml`) with API key secret → commit updated JSON + HTML.

---

## 4. Google Sheet / CSV export

**What:** Flatten `results.json` to one row per query.

**Pros:** Familiar for ops / vendors.

**Cons:** Loses narrative framing.

---

## 5. agaveapps.com dynamic product (later)

**What:** Hosted scoreboard with login, scheduled pulls, encroachment alerts.

**Pros:** Recurring product path from this Frymire template.

**Cons:** Build after Allison / Frymire external validation.

---

## 6. PDF from print

**What:** Browser print → Save as PDF from `report/` (print CSS included).

**Pros:** Email attachment for leadership who won't click links.

---

## Recommendation

Use **customer `report/`** for Allison and (after gate) Frymire. Keep dossier for Sharon Oak. Automate refresh with weekly Action when API secret is configured.

## API key note

`fetch_local_pack.py` reads, in order: `VALUESERP_API_KEY`, `VALUE_SERP_API_KEY`, `VALUESERP_KEY`, `SERPWOW_API_KEY`, `TRAJECT_API_KEY`. Configure in Cloud Agent or GitHub Actions secrets for automated runs.
