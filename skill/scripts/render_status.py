#!/usr/bin/env python3
"""Render a judged status.json into an exec-ready status report and brief.

Pure stdlib, no LLM involved. This script does not decide anything about
project health — it validates and formats a status.json that Claude has
already produced by reconciling a schedule against raw progress notes.
"""
import argparse
import html
import json
import sys
from pathlib import Path

VALID_RAG = {"green", "amber", "red"}
VALID_SEVERITY = {"low", "medium", "high"}
BADGE = {"green": "\U0001F7E2", "amber": "\U0001F7E1", "red": "\U0001F534"}
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}

CHIP_COLORS = {
    "green": ("#0f5132", "#d1e7dd"),
    "amber": ("#664d03", "#fff3cd"),
    "red": ("#842029", "#f8d7da"),
    "high": ("#842029", "#f8d7da"),
    "medium": ("#664d03", "#fff3cd"),
    "low": ("#41464b", "#e2e3e5"),
}


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def load_status(path):
    with open(path) as f:
        data = json.load(f)

    for field in ("project", "as_of", "overall_status", "overall_status_rationale",
                  "schedule_summary", "epics"):
        if field not in data:
            fail(f"status.json missing required top-level field '{field}'")

    if data["overall_status"] not in VALID_RAG:
        fail(f"overall_status '{data['overall_status']}' must be one of {sorted(VALID_RAG)}")

    ss = data["schedule_summary"]
    for field in ("target_finish", "business_days_remaining", "on_track"):
        if field not in ss:
            fail(f"schedule_summary missing required field '{field}'")

    for i, epic in enumerate(data.get("epics", [])):
        for field in ("id", "name", "status", "status_rationale"):
            if field not in epic:
                fail(f"epics[{i}] missing required field '{field}'")
        if epic["status"] not in VALID_RAG:
            fail(f"epics[{i}] ('{epic['id']}') status '{epic['status']}' must be one of {sorted(VALID_RAG)}")

    for i, risk in enumerate(data.get("risks", [])):
        for field in ("id", "summary", "severity", "owner_team", "ask"):
            if field not in risk:
                fail(f"risks[{i}] missing required field '{field}'")
        if risk["severity"] not in VALID_SEVERITY:
            fail(f"risks[{i}] ('{risk['id']}') severity '{risk['severity']}' must be one of {sorted(VALID_SEVERITY)}")

    for i, m in enumerate(data.get("milestones", [])):
        for field in ("date", "description"):
            if field not in m:
                fail(f"milestones[{i}] missing required field '{field}'")

    for i, d in enumerate(data.get("decisions_needed", [])):
        for field in ("summary", "owner", "needed_by"):
            if field not in d:
                fail(f"decisions_needed[{i}] missing required field '{field}'")

    return data


def write_status_report(data, outdir):
    lines = []
    lines.append(f"# Status Report — {data['project']}")
    lines.append("")
    lines.append(f"**As of:** {data['as_of']}")
    lines.append(f"**Overall status:** {BADGE[data['overall_status']]} {data['overall_status'].upper()}")
    lines.append("")
    lines.append(data["overall_status_rationale"])
    lines.append("")

    ss = data["schedule_summary"]
    lines.append("## Schedule")
    lines.append("")
    lines.append(f"- Target finish: {ss['target_finish']}")
    lines.append(f"- Business days remaining: {ss['business_days_remaining']}")
    lines.append(f"- On track: {'Yes' if ss['on_track'] else 'No'}")
    lines.append("")

    highlights = []
    for epic in data["epics"]:
        for h in epic.get("highlights", []):
            highlights.append(f"- **{epic['id']}** ({epic['name']}): {h}")
    if highlights:
        lines.append("## Highlights")
        lines.append("")
        lines.extend(highlights)
        lines.append("")

    lines.append("## Epic Status")
    lines.append("")
    lines.append("| Epic | Status | Notes |")
    lines.append("|---|---|---|")
    for epic in data["epics"]:
        badge = BADGE[epic["status"]]
        lines.append(f"| {epic['id']} — {epic['name']} | {badge} {epic['status'].upper()} | {epic['status_rationale']} |")
    lines.append("")

    risks = sorted(data.get("risks", []), key=lambda r: SEVERITY_ORDER.get(r["severity"], 99))
    if risks:
        lines.append("## Risks & Blockers")
        lines.append("")
        lines.append("| Severity | Risk | Owner | Ask |")
        lines.append("|---|---|---|---|")
        for r in risks:
            lines.append(f"| {r['severity'].upper()} | {r['summary']} | {r['owner_team']} | {r['ask']} |")
        lines.append("")

    milestones = data.get("milestones", [])
    if milestones:
        lines.append("## Milestones")
        lines.append("")
        for m in milestones:
            lines.append(f"- **{m['date']}** — {m['description']}")
        lines.append("")

    decisions = data.get("decisions_needed", [])
    if decisions:
        lines.append("## Decisions Needed")
        lines.append("")
        for d in decisions:
            lines.append(f"- {d['summary']} (owner: {d['owner']}, needed by: {d['needed_by']})")
        lines.append("")

    (outdir / "status_report.md").write_text("\n".join(lines) + "\n")


def write_status_brief(data, outdir):
    lines = []
    lines.append(f"# Status Brief — {data['project']} ({data['as_of']})")
    lines.append("")
    lines.append(f"{BADGE[data['overall_status']]} **{data['overall_status'].upper()}** — {data['overall_status_rationale']}")
    lines.append("")

    risks = sorted(data.get("risks", []), key=lambda r: SEVERITY_ORDER.get(r["severity"], 99))[:3]
    if risks:
        lines.append("**Top risks:**")
        for i, r in enumerate(risks, 1):
            lines.append(f"{i}. {r['summary']} — {r['ask']} ({r['owner_team']})")
        lines.append("")

    decisions = data.get("decisions_needed", [])
    if decisions:
        lines.append("**Decisions needed:**")
        for d in decisions:
            lines.append(f"- {d['summary']} (needed by {d['needed_by']})")
        lines.append("")

    (outdir / "status_brief.md").write_text("\n".join(lines) + "\n")


def _chip(label, key, size="normal"):
    fg, bg = CHIP_COLORS[key]
    cls = "chip chip-lg" if size == "lg" else "chip"
    return f'<span class="{cls}" style="color:{fg};background:{bg};">{html.escape(label)}</span>'


def write_status_html(data, outdir):
    esc = html.escape
    overall = data["overall_status"]
    ss = data["schedule_summary"]

    highlights = []
    for epic in data["epics"]:
        for h in epic.get("highlights", []):
            highlights.append((epic["id"], epic["name"], h))

    risks = sorted(data.get("risks", []), key=lambda r: SEVERITY_ORDER.get(r["severity"], 99))
    milestones = data.get("milestones", [])
    decisions = data.get("decisions_needed", [])

    parts = []
    parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Status Report — {esc(data['project'])}</title>
<style>
  :root {{ color-scheme: light; }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 2.5rem 1.25rem 4rem;
    background: #f6f7f9;
    color: #1a1d21;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    line-height: 1.5;
  }}
  .container {{ max-width: 880px; margin: 0 auto; }}
  .card {{
    background: #fff;
    border: 1px solid #e3e5e8;
    border-radius: 10px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.25rem;
  }}
  h1 {{ font-size: 1.5rem; margin: 0 0 0.25rem; }}
  h2 {{ font-size: 1.05rem; margin: 0 0 0.85rem; color: #40454c; }}
  .as-of {{ color: #6b7280; font-size: 0.9rem; margin: 0 0 1rem; }}
  .rationale {{ margin: 0.75rem 0 0; }}
  .chip {{
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    white-space: nowrap;
  }}
  .chip-lg {{ padding: 0.35rem 1rem; font-size: 0.95rem; }}
  .stat-row {{ display: flex; gap: 1rem; flex-wrap: wrap; }}
  .stat {{ flex: 1 1 160px; }}
  .stat .label {{ font-size: 0.78rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.03em; }}
  .stat .value {{ font-size: 1.15rem; font-weight: 600; margin-top: 0.15rem; }}
  ul {{ margin: 0; padding-left: 1.25rem; }}
  li {{ margin-bottom: 0.4rem; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.92rem; }}
  th, td {{ text-align: left; padding: 0.6rem 0.5rem; border-bottom: 1px solid #eceef1; vertical-align: top; }}
  th {{ color: #6b7280; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.03em; font-weight: 600; }}
  tr:last-child td {{ border-bottom: none; }}
  .callout {{
    border-left: 4px solid #664d03;
    background: #fff9e6;
    border-radius: 6px;
    padding: 0.9rem 1.1rem;
  }}
  .callout li {{ margin-bottom: 0.6rem; }}
  .callout li:last-child {{ margin-bottom: 0; }}
  .meta {{ color: #6b7280; }}
</style>
</head>
<body>
<div class="container">

  <div class="card">
    <h1>{esc(data['project'])}</h1>
    <p class="as-of">As of {esc(data['as_of'])}</p>
    {_chip(overall.upper(), overall, size="lg")}
    <p class="rationale">{esc(data['overall_status_rationale'])}</p>
  </div>

  <div class="card">
    <h2>Schedule</h2>
    <div class="stat-row">
      <div class="stat"><div class="label">Target finish</div><div class="value">{esc(ss['target_finish'])}</div></div>
      <div class="stat"><div class="label">Business days remaining</div><div class="value">{esc(str(ss['business_days_remaining']))}</div></div>
      <div class="stat"><div class="label">On track</div><div class="value">{'Yes' if ss['on_track'] else 'No'}</div></div>
    </div>
  </div>
""")

    if highlights:
        parts.append('  <div class="card">\n    <h2>Highlights</h2>\n    <ul>\n')
        for eid, ename, h in highlights:
            parts.append(f"      <li><strong>{esc(eid)}</strong> ({esc(ename)}): {esc(h)}</li>\n")
        parts.append("    </ul>\n  </div>\n")

    parts.append('  <div class="card">\n    <h2>Epic Status</h2>\n    <table>\n')
    parts.append("      <tr><th>Epic</th><th>Status</th><th>Notes</th></tr>\n")
    for epic in data["epics"]:
        parts.append(
            f"      <tr><td>{esc(epic['id'])} — {esc(epic['name'])}</td>"
            f"<td>{_chip(epic['status'].upper(), epic['status'])}</td>"
            f"<td>{esc(epic['status_rationale'])}</td></tr>\n"
        )
    parts.append("    </table>\n  </div>\n")

    if risks:
        parts.append('  <div class="card">\n    <h2>Risks &amp; Blockers</h2>\n    <table>\n')
        parts.append("      <tr><th>Severity</th><th>Risk</th><th>Owner</th><th>Ask</th></tr>\n")
        for r in risks:
            parts.append(
                f"      <tr><td>{_chip(r['severity'].upper(), r['severity'])}</td>"
                f"<td>{esc(r['summary'])}</td><td>{esc(r['owner_team'])}</td>"
                f"<td>{esc(r['ask'])}</td></tr>\n"
            )
        parts.append("    </table>\n  </div>\n")

    if milestones:
        parts.append('  <div class="card">\n    <h2>Milestones</h2>\n    <ul>\n')
        for m in milestones:
            parts.append(f"      <li><strong>{esc(m['date'])}</strong> — {esc(m['description'])}</li>\n")
        parts.append("    </ul>\n  </div>\n")

    if decisions:
        parts.append('  <div class="card">\n    <h2>Decisions Needed</h2>\n    <ul class="callout">\n')
        for d in decisions:
            parts.append(
                f"      <li>{esc(d['summary'])} "
                f'<span class="meta">(owner: {esc(d["owner"])}, needed by: {esc(d["needed_by"])})</span></li>\n'
            )
        parts.append("    </ul>\n  </div>\n")

    parts.append("</div>\n</body>\n</html>\n")

    (outdir / "status_report.html").write_text("".join(parts))


def main():
    parser = argparse.ArgumentParser(description="Render a status.json into a status report and brief.")
    parser.add_argument("status_json", help="Path to status.json")
    parser.add_argument("--outdir", required=True, help="Output directory")
    args = parser.parse_args()

    data = load_status(args.status_json)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    write_status_report(data, outdir)
    write_status_brief(data, outdir)
    write_status_html(data, outdir)

    print(f"Overall status: {data['overall_status'].upper()} — output in {outdir}")


if __name__ == "__main__":
    main()
