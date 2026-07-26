#!/usr/bin/env python3
"""Render a judged status.json into an exec-ready status report and brief.

Pure stdlib, no LLM involved. This script does not decide anything about
project health — it validates and formats a status.json that Claude has
already produced by reconciling a schedule against raw progress notes.
"""
import argparse
import json
import sys
from pathlib import Path

VALID_RAG = {"green", "amber", "red"}
VALID_SEVERITY = {"low", "medium", "high"}
BADGE = {"green": "\U0001F7E2", "amber": "\U0001F7E1", "red": "\U0001F534"}
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


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

    print(f"Overall status: {data['overall_status'].upper()} — output in {outdir}")


if __name__ == "__main__":
    main()
