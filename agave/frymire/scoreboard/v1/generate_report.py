#!/usr/bin/env python3
"""Generate customer Territory Scoreboard HTML from results.json.

Plan decisions:
  D1=C — markets exposed big + fraction footnote
  D2=C — Agave Apps product frame with Frymire as client
  D3=A — name giants
  D4 — write report/index.html
  D5 — noindex; Allison · Granite Comfort share gate
"""

from __future__ import annotations

import html
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

DIR = Path(__file__).resolve().parent
RESULTS_PATH = DIR / "results.json"
OUT_PATH = DIR / "report" / "index.html"

STATUS_ORDER = {"exposed": 0, "contested": 1, "defending": 2}


def load_results() -> dict:
    return json.loads(RESULTS_PATH.read_text())


def status_for(row: dict) -> str:
    fry = row.get("frymire_position")
    giants = row.get("giant_positions") or {}
    enc = (row.get("encroachment") or "").lower()
    if fry is not None and fry <= 5:
        return "defending"
    if giants or enc == "high":
        return "exposed"
    return "contested"


def as_of(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y").replace(" 0", " ")
    except ValueError:
        return (iso or "")[:10]


def service_label(service: str) -> str:
    return "HVAC" if service == "hvac" else "Plumbing"


def chip(status: str) -> str:
    return f'<span class="chip chip-{status}">{status.title()}</span>'


def leaders_list(leaders: list) -> str:
    parts = []
    for item in (leaders or [])[:3]:
        title = html.escape(item.get("title") or "—")
        pos = item.get("position", "?")
        brand = item.get("brand")
        extra = f' <em>({html.escape(str(brand))})</em>' if brand else ""
        parts.append(f"<li><strong>#{pos}</strong> {title}{extra}</li>")
    return "\n".join(parts) if parts else "<li>No leaders returned</li>"


def defend_items(worst: list[dict]) -> str:
    items = []
    for row in worst[:3]:
        market = html.escape(row["market"])
        svc = service_label(row["service"])
        giants = row.get("giant_positions") or {}
        if giants:
            who = ", ".join(
                f"{html.escape(n)} at #{p}"
                for n, p in sorted(giants.items(), key=lambda x: x[1])
            )
            body = (
                f"{who} shows in the local pack while Frymire is outside the top 5. "
                f"Defend local pack visibility and the mobile book path for this trade."
            )
        else:
            top = row.get("leaders") or []
            names = ", ".join(html.escape(x.get("title", "")) for x in top[:2]) or "local independents"
            body = (
                f"Frymire is outside the top 5; leading names include {names}. "
                f"Audit Google Business Profile coverage and local presence for this city."
            )
        items.append(f"<li><strong>{market} · {svc}</strong> — {body}</li>")
    return "\n".join(items)


def build_grid_rows(market_order: list[str], by_market: dict) -> str:
    rows_html = []
    for market in market_order:
        cells = []
        for service, col in (("hvac", "hvac"), ("plumbing", "plumbing")):
            row = by_market[market].get(service)
            if not row:
                cells.append(f'<td class="cell cell-{col}">—</td>')
                continue
            st = status_for(row)
            giants = row.get("giant_positions") or {}
            giant_note = ""
            if giants:
                giant_note = (
                    '<p class="giant-note">'
                    + html.escape(
                        ", ".join(f"{n} #{p}" for n, p in sorted(giants.items(), key=lambda x: x[1]))
                    )
                    + "</p>"
                )
            cells.append(
                f"""<td class="cell cell-{col}">
                {chip(st)}
                {giant_note}
                <details>
                  <summary>Top 3</summary>
                  <ul class="leaders">{leaders_list(row.get("leaders") or [])}</ul>
                </details>
              </td>"""
            )
        rows_html.append(
            f"""<tr>
              <td class="market-name">{html.escape(market)}</td>
              {cells[0]}
              {cells[1]}
            </tr>"""
        )
    return "\n".join(rows_html)


def build_html(data: dict) -> str:
    rows = data["results"]
    giants_tracked = data.get("giants") or []
    fetched = data.get("fetched_at") or ""
    date_label = as_of(fetched)
    query_count = int(data.get("query_count") or len(rows))

    by_market: dict[str, dict[str, dict]] = defaultdict(dict)
    market_order: list[str] = []
    for row in rows:
        by_market[row["market"]][row["service"]] = row
        if row["market"] not in market_order:
            market_order.append(row["market"])

    fry_hits = sum(
        1 for r in rows if r.get("frymire_position") is not None and r["frymire_position"] <= 5
    )
    giant_hits = sum(1 for r in rows if r.get("giant_positions"))
    exposed_cells = sum(1 for r in rows if status_for(r) == "exposed")
    markets_exposed = sum(
        1
        for m in market_order
        if any(status_for(by_market[m][s]) == "exposed" for s in by_market[m])
    )

    scored = [{**r, "_status": status_for(r)} for r in rows]
    worst = sorted(
        scored,
        key=lambda r: (
            STATUS_ORDER[r["_status"]],
            0 if r.get("giant_positions") else 1,
            min(r["giant_positions"].values()) if r.get("giant_positions") else 99,
            r["market"],
            r["service"],
        ),
    )

    giants_list = ", ".join(html.escape(g) for g in giants_tracked) or "—"
    grid_rows = build_grid_rows(market_order, by_market)
    actions_html = defend_items(worst)

    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Territory Scoreboard — Frymire Home Services</title>
    <meta name="robots" content="noindex, nofollow" />
    <link rel="canonical" href="https://sharonoak.com/agave/frymire/scoreboard/v1/report/" />
    <meta
      name="description"
      content="Agave Apps Territory Scoreboard for Frymire Home Services — where competitors win the call across DFW HVAC and plumbing."
    />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Outfit:wght@400;500;600&display=swap"
      rel="stylesheet"
    />
    <style>
      :root {{
        --ink: #0f1c24;
        --ink-soft: #3d5160;
        --navy: #123047;
        --teal: #0d7377;
        --teal-mid: #14919b;
        --paper: #f4f7f8;
        --line: rgba(15, 28, 36, 0.12);
        --exposed: #9b2226;
        --contested: #9a6700;
        --defending: #1b4332;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        color: var(--ink);
        font-family: Outfit, sans-serif;
        font-size: 1.05rem;
        line-height: 1.5;
        background:
          radial-gradient(1000px 480px at 10% -10%, rgba(20, 145, 155, 0.16), transparent 55%),
          radial-gradient(800px 420px at 100% 0%, rgba(18, 48, 71, 0.1), transparent 50%),
          linear-gradient(180deg, #eef3f5 0%, var(--paper) 35%, #e8eef1 100%);
        min-height: 100vh;
      }}
      .wrap {{
        width: min(100% - 2rem, 44rem);
        margin: 0 auto;
        padding: 2rem 0 3.5rem;
      }}
      .product {{
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--teal-mid);
        margin: 0 0 0.55rem;
      }}
      .client {{
        font-family: Fraunces, serif;
        font-weight: 700;
        font-size: clamp(1.85rem, 5.5vw, 2.55rem);
        letter-spacing: -0.03em;
        line-height: 1.08;
        color: var(--navy);
        margin: 0 0 0.35rem;
      }}
      h1 {{
        font-family: Fraunces, serif;
        font-weight: 500;
        font-size: clamp(1.25rem, 3.4vw, 1.55rem);
        line-height: 1.25;
        letter-spacing: -0.02em;
        margin: 0 0 0.65rem;
        max-width: 28ch;
      }}
      .lede {{
        margin: 0 0 1rem;
        color: var(--ink-soft);
        max-width: 42ch;
      }}
      .meta {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.4rem 1.1rem;
        padding: 0.85rem 0 0;
        border-top: 1px solid var(--line);
        font-size: 0.85rem;
        color: var(--ink-soft);
      }}
      .meta strong {{ color: var(--ink); font-weight: 600; }}
      .stats {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.65rem;
        margin: 1.6rem 0 0.5rem;
      }}
      .stat {{
        background: rgba(255, 255, 255, 0.78);
        border: 1px solid var(--line);
        border-radius: 4px;
        padding: 0.9rem 0.85rem;
      }}
      .stat .num {{
        font-family: Fraunces, serif;
        font-size: clamp(1.6rem, 5vw, 2rem);
        font-weight: 700;
        color: var(--navy);
        line-height: 1;
        margin: 0 0 0.35rem;
      }}
      .stat .num.alert {{ color: var(--exposed); }}
      .stat .label {{
        font-size: 0.78rem;
        color: var(--ink-soft);
        margin: 0;
        line-height: 1.35;
      }}
      .footnote {{
        font-size: 0.8rem;
        color: var(--ink-soft);
        margin: 0.35rem 0 0;
      }}
      section {{
        margin-top: 2rem;
        padding-top: 1.4rem;
        border-top: 1px solid var(--line);
      }}
      section h2 {{
        font-family: Fraunces, serif;
        font-size: 1.25rem;
        font-weight: 700;
        margin: 0 0 0.55rem;
        letter-spacing: -0.02em;
      }}
      section > p {{ margin: 0 0 0.8rem; color: var(--ink-soft); }}
      .filters {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.4rem;
        margin: 0 0 0.85rem;
      }}
      .filters button {{
        font: inherit;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.7);
        color: var(--ink-soft);
        border-radius: 999px;
        padding: 0.35rem 0.75rem;
        cursor: pointer;
      }}
      .filters button[aria-pressed="true"] {{
        background: var(--navy);
        border-color: var(--navy);
        color: #fff;
      }}
      .legend {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem 1rem;
        font-size: 0.8rem;
        color: var(--ink-soft);
        margin: 0 0 0.9rem;
      }}
      table.grid {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.95rem;
      }}
      table.grid th,
      table.grid td {{
        text-align: left;
        vertical-align: top;
        padding: 0.7rem 0.4rem 0.7rem 0;
        border-bottom: 1px solid var(--line);
      }}
      table.grid th {{
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--ink-soft);
        font-weight: 600;
      }}
      .market-name {{
        font-weight: 600;
        color: var(--ink);
        width: 28%;
        padding-right: 0.6rem;
      }}
      body.filter-hvac .cell-plumbing,
      body.filter-plumbing .cell-hvac {{ display: none; }}
      body.filter-hvac th.col-plumbing,
      body.filter-plumbing th.col-hvac {{ display: none; }}
      .chip {{
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        padding: 0.2rem 0.5rem;
        border-radius: 3px;
        border: 1px solid transparent;
      }}
      .chip-exposed {{
        color: var(--exposed);
        border-color: rgba(155, 34, 38, 0.35);
        background: rgba(155, 34, 38, 0.08);
      }}
      .chip-contested {{
        color: var(--contested);
        border-color: rgba(154, 103, 0, 0.35);
        background: rgba(154, 103, 0, 0.08);
      }}
      .chip-defending {{
        color: var(--defending);
        border-color: rgba(27, 67, 50, 0.35);
        background: rgba(27, 67, 50, 0.08);
      }}
      .giant-note {{
        margin: 0.3rem 0 0;
        font-size: 0.78rem;
        color: var(--exposed);
        font-weight: 500;
      }}
      details {{ margin-top: 0.35rem; }}
      details summary {{
        cursor: pointer;
        font-size: 0.78rem;
        color: var(--teal-mid);
        font-weight: 600;
        list-style: none;
      }}
      details summary::-webkit-details-marker {{ display: none; }}
      ul.leaders {{
        margin: 0.35rem 0 0;
        padding-left: 1rem;
        font-size: 0.82rem;
        color: var(--ink-soft);
      }}
      ul.leaders li {{ margin: 0.2rem 0; }}
      .defend ol {{
        margin: 0.4rem 0 0;
        padding-left: 1.2rem;
        color: var(--ink-soft);
      }}
      .defend li {{ margin: 0.55rem 0; }}
      .defend strong {{ color: var(--ink); }}
      .gate {{
        margin-top: 1.5rem;
        padding: 0.9rem 1rem;
        border-radius: 4px;
        border: 1px solid rgba(154, 103, 0, 0.35);
        background: rgba(154, 103, 0, 0.08);
        font-size: 0.88rem;
        color: var(--ink-soft);
      }}
      .gate strong {{ color: var(--ink); }}
      footer {{
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid var(--line);
        font-size: 0.8rem;
        color: var(--ink-soft);
      }}
      footer a {{ color: var(--teal-mid); }}
      @media (max-width: 560px) {{
        .stats {{ grid-template-columns: 1fr; }}
        table.grid, table.grid thead, table.grid tbody,
        table.grid th, table.grid td, table.grid tr {{
          display: block;
          width: 100%;
        }}
        table.grid thead {{ display: none; }}
        table.grid tr {{
          padding: 0.85rem 0;
          border-bottom: 1px solid var(--line);
        }}
        table.grid td {{ border: none; padding: 0.25rem 0; }}
        .market-name {{
          width: 100%;
          font-size: 1.05rem;
          margin-bottom: 0.35rem;
        }}
        .cell-hvac::before,
        .cell-plumbing::before {{
          display: block;
          font-size: 0.7rem;
          text-transform: uppercase;
          letter-spacing: 0.06em;
          color: var(--ink-soft);
          margin-bottom: 0.2rem;
        }}
        .cell-hvac::before {{ content: "HVAC"; }}
        .cell-plumbing::before {{ content: "Plumbing"; }}
      }}
      @media print {{
        body {{ background: #fff; }}
        .filters {{ display: none; }}
        .gate {{ break-inside: avoid; }}
        .chip {{
          -webkit-print-color-adjust: exact;
          print-color-adjust: exact;
        }}
      }}
    </style>
  </head>
  <body>
    <div class="wrap">
      <p class="product">Agave Apps · Territory Scoreboard</p>
      <p class="client">Frymire Home Services</p>
      <h1>Where competitors win the call</h1>
      <p class="lede">
        When homeowners search for HVAC or plumbing help, these are the names Google shows first —
        by city across DFW.
      </p>
      <div class="meta">
        <span><strong>As of:</strong> {html.escape(date_label)}</span>
        <span><strong>Coverage:</strong> {len(market_order)} markets · HVAC + plumbing</span>
        <span><strong>Giants tracked:</strong> {giants_list}</span>
      </div>

      <div class="stats" aria-label="Summary">
        <div class="stat">
          <p class="num alert">{markets_exposed}</p>
          <p class="label">Markets with at least one exposed service line</p>
        </div>
        <div class="stat">
          <p class="num">{fry_hits}</p>
          <p class="label">Times Frymire appears in the local top 5</p>
        </div>
        <div class="stat">
          <p class="num">{giant_hits}</p>
          <p class="label">Times a named giant appears in the top 5</p>
        </div>
      </div>
      <p class="footnote">
        Frymire in top 5 on <strong>{fry_hits} of {query_count}</strong> core searches this pull ·
        {exposed_cells} of {query_count} service×city cells marked Exposed.
      </p>

      <section>
        <h2>Territory grid</h2>
        <p>Status by city and trade. Open Top 3 for who currently owns the pack.</p>
        <div class="filters" role="group" aria-label="Service filter">
          <button type="button" data-filter="both" aria-pressed="true">Both</button>
          <button type="button" data-filter="hvac" aria-pressed="false">HVAC</button>
          <button type="button" data-filter="plumbing" aria-pressed="false">Plumbing</button>
        </div>
        <div class="legend">
          <span><span class="chip chip-defending">Defending</span> Frymire in top 5</span>
          <span><span class="chip chip-contested">Contested</span> Absent · no tracked giant</span>
          <span><span class="chip chip-exposed">Exposed</span> Absent · giant in pack or high risk</span>
        </div>
        <table class="grid">
          <thead>
            <tr>
              <th>City</th>
              <th class="col-hvac">HVAC</th>
              <th class="col-plumbing">Plumbing</th>
            </tr>
          </thead>
          <tbody>
            {grid_rows}
          </tbody>
        </table>
      </section>

      <section class="defend">
        <h2>Defend these three</h2>
        <p>Highest-priority exposures from this pull — start here.</p>
        <ol>
          {actions_html}
        </ol>
      </section>

      <div class="gate">
        <strong>Share gate:</strong> Internal / Allison · Granite Comfort preview only.
        Do not forward to Frymire leadership until Allison signs off.
      </div>

      <footer>
        <p>
          Based on Google Maps local results for standard repair searches at each city center.
          Rankings shift by neighborhood and time of day. Giants tracked this period:
          {giants_list}.
        </p>
        <p>
          Updated {html.escape(date_label)} · Agave Apps Territory Scoreboard ·
          Prepared for Frymire Home Services ·
          <a href="mailto:tyleryost@sharonoak.com?subject=Frymire%20Territory%20Scoreboard">tyleryost@sharonoak.com</a>
        </p>
      </footer>
    </div>
    <script>
      (function () {{
        var buttons = document.querySelectorAll(".filters button");
        buttons.forEach(function (btn) {{
          btn.addEventListener("click", function () {{
            var mode = btn.getAttribute("data-filter");
            document.body.classList.remove("filter-hvac", "filter-plumbing");
            if (mode === "hvac") document.body.classList.add("filter-hvac");
            if (mode === "plumbing") document.body.classList.add("filter-plumbing");
            buttons.forEach(function (b) {{
              b.setAttribute("aria-pressed", b === btn ? "true" : "false");
            }});
          }});
        }});
      }})();
    </script>
  </body>
</html>
"""


def main() -> None:
    data = load_results()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(build_html(data), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
