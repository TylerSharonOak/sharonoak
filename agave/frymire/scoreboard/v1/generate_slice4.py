#!/usr/bin/env python3
"""Generate Slice 4 HTML from results.json."""

import html
import json
from pathlib import Path

DIR = Path(__file__).resolve().parent
RESULTS = json.loads((DIR / "results.json").read_text())

TAG = {
    "high": "tag-high",
    "medium": "tag-med",
    "watch": "tag-watch",
}


def fmt_leaders(leaders: list) -> str:
    parts = []
    for item in leaders[:3]:
        title = html.escape(item["title"])
        pos = item["position"]
        brand = item.get("brand")
        if brand == "Frymire":
            parts.append(f"<strong>#{pos} {title}</strong>")
        elif brand:
            parts.append(f"#{pos} {title} <em>({brand})</em>")
        else:
            parts.append(f"#{pos} {title}")
    return "<br />".join(parts)


def fmt_giants(giants: dict) -> str:
    if not giants:
        return "—"
    return ", ".join(f"{name} #{pos}" for name, pos in sorted(giants.items(), key=lambda x: x[1]))


def fmt_frymire(pos) -> str:
    if pos is None:
        return '<span class="tag tag-high">Not in top 5</span>'
    if pos <= 3:
        return f'<span class="tag tag-watch">#{pos}</span>'
    return f'<span class="tag tag-med">#{pos}</span>'


def build_table(service: str) -> str:
    rows = [r for r in RESULTS["results"] if r["service"] == service]
    body = []
    for row in rows:
        enc = row["encroachment"]
        body.append(
            f"""            <tr>
              <td>{html.escape(row["market"])}</td>
              <td><code>{html.escape(row["q"])}</code></td>
              <td>{fmt_leaders(row["leaders"])}</td>
              <td>{fmt_frymire(row["frymire_position"])}</td>
              <td>{fmt_giants(row["giant_positions"])}</td>
              <td><span class="tag {TAG[enc]}">{enc.title()}</span></td>
            </tr>"""
        )
    return "\n".join(body)


fetched = RESULTS["fetched_at"][:10]
provider = RESULTS["provider"]
credits = RESULTS["credits_used"]
count = RESULTS["query_count"]
frymire_hits = sum(1 for r in RESULTS["results"] if r["frymire_position"])
giant_hits = sum(1 for r in RESULTS["results"] if r["giant_positions"])

print(
    f"""      <section>
        <h2>Slice 4 — live local pack (ValueSerp / Traject)</h2>
        <p>
          <strong>Live pull:</strong> {fetched} UTC · {count} queries · {credits} API credits ·
          provider: {provider} (Traject Data <code>search_type=places</code>).
          Google Maps local results per market centroid — not per-ZIP. Compare to Slice 3 public
          research above; rankings will differ by query phrasing and geo precision.
        </p>
        <p>
          <strong>Query set:</strong> one HVAC + one plumbing core-intent query per market
          (<code>ac repair &#123;city&#125; TX</code>, <code>plumber &#123;city&#125; TX</code>).
          Full list in <a href="queries.json">queries.json</a>.
        </p>

        <div class="note">
          <h3>Headline signals ({fetched})</h3>
          <table>
            <thead>
              <tr>
                <th>Signal</th>
                <th>Live data</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Frymire in top 5</td>
                <td><strong>{frymire_hits} of {count}</strong> queries — not visible on any core query in this pull</td>
              </tr>
              <tr>
                <td>Giants in top 5</td>
                <td><strong>{giant_hits} of {count}</strong> — Berkeys visible in Frisco plumbing (#5), Carrollton HVAC (#5), Carrollton plumbing (#2)</td>
              </tr>
              <tr>
                <td>vs Slice 3</td>
                <td>Slice 3 giants (Baker Brothers, Rescue Air) held broad Dallas <em>web</em> local pack; this Maps pull surfaces different leaders per submarket</td>
              </tr>
            </tbody>
          </table>
        </div>

        <h3 style="font-family: Fraunces, serif; font-size: 1.1rem; margin: 1.5rem 0 0.65rem">
          Live map pack — HVAC
        </h3>
        <table>
          <thead>
            <tr>
              <th>Market</th>
              <th>Query</th>
              <th>Top 3 visible</th>
              <th>Frymire</th>
              <th>Giants</th>
              <th>Encroachment</th>
            </tr>
          </thead>
          <tbody>
{build_table("hvac")}
          </tbody>
        </table>

        <h3 style="font-family: Fraunces, serif; font-size: 1.1rem; margin: 1.5rem 0 0.65rem">
          Live map pack — plumbing
        </h3>
        <table>
          <thead>
            <tr>
              <th>Market</th>
              <th>Query</th>
              <th>Top 3 visible</th>
              <th>Frymire</th>
              <th>Giants</th>
              <th>Encroachment</th>
            </tr>
          </thead>
          <tbody>
{build_table("plumbing")}
          </tbody>
        </table>

        <p class="source">
          Source: Traject Data Places API ({provider}), fetched {fetched} UTC.
          Raw JSON: <a href="results.json">results.json</a>.
          Re-run: <code>python3 fetch_local_pack.py</code> (requires
          <code>VALUESERP_API_KEY</code> or <code>SERPWOW_API_KEY</code>).
        </p>
      </section>"""
)
