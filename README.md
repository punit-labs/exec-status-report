# exec-status-report

A [Claude Code Skill](https://docs.claude.com/en/docs/claude-code/skills) that turns a
project schedule plus this period's raw team progress notes into an executive-ready
status report: an evidence-backed RAG rating, a risk register with owners and asks,
and the decisions that actually need a call.

## The problem

Status reports either take real synthesis (reconciling what teams actually said
against the plan) or they don't — and the ones that skip it tend to either sugarcoat
a real slip as "amber" because the number sounds small, or escalate everything to red
because one off-critical-path task is late and nobody checked whether that task
actually threatens the finish date. Both failure modes come from the same root
cause: nobody re-derived the RAG rating from the schedule math, they just vibed it.

## What it does

1. You give Claude a schedule — [`critical-path-mapper`](https://github.com/punit-labs/critical-path-mapper)'s
   `schedule.json` is the natural source, since it already has planned dates, slack,
   and which tasks are on the critical path — plus this period's raw progress notes
   (standup notes, a Slack thread, whatever teams actually wrote).
2. Following the rubric in [`skill/SKILL.md`](skill/SKILL.md), Claude reconciles
   actuals against plan per task (finished late / behind plan / slack consumed /
   resolved early), assigns each epic a RAG status grounded in a specific number —
   days late, days of slack left — not a feeling, and rolls up an overall status
   from the worst **load-bearing** epic (one that actually contains a critical-path
   or near-critical task), so an off-path delay can't drag the whole project red.
3. That judgment is written to one `status.json` file.
4. A small deterministic script, [`skill/scripts/render_status.py`](skill/scripts/render_status.py),
   validates it (every status/severity value is a real enum, every risk has an owner
   and an ask) and renders:
   - `status_report.md` — the full exec-ready report
   - `status_brief.md` — a condensed version for pasting into Slack or an email
   - `status_report.html` — the same report as a single self-contained, styled page

Same split as the first two projects: the model does the reconciliation and judgment
call, plain code does the formatting — so re-rendering after editing `status.json` is
instant, and the report can't drift out of sync with the data behind it.

## Demo

[`examples/schedule.json`](examples/schedule.json) is `critical-path-mapper`'s worked
example — the same "Nimbus Expense" backlog, already scheduled. Extending that story:
[`examples/progress_updates.md`](examples/progress_updates.md) is what the teams
actually reported at the Aug 14 checkpoint, partway through the plan.

**Live demo:** [punit-labs.github.io/exec-status-report](https://punit-labs.github.io/exec-status-report/)
— the actual rendered `status_report.html` for the example below.

Result — [`examples/status.json`](examples/status.json), rendered to
[`examples/output/`](examples/output/):

**🔴 RED.** The critical path had already slipped one business day by the time this
report was written (a zero-slack task hit an unplanned permissions issue, and the
next zero-slack task on the chain absorbed that delay with no way to compress it
further) — moving the finish date from 2026-08-20 to 2026-08-21. The report still
surfaces the good news alongside it: a previously-open, PRD-unresolved compliance
question got closed out the same week, and two epics are fully green. The report
doesn't average those out — a real, unrecoverable slip on the critical path makes the
project red regardless of what else went well, and the rationale says exactly why.

![Terminal demo: running render_status.py against the example status.json, producing a real RAG-rated status report](assets/demo.gif)

## Using it

1. Copy `skill/` into your Claude Code skills directory (project-level:
   `.claude/skills/exec-status-report/`, or user-level:
   `~/.claude/skills/exec-status-report/`).
2. In Claude Code: "write a status report for this project" / "what's our RAG status"
   / "turn this schedule and these standup notes into an exec update."
3. Claude writes `status.json`, then runs `render_status.py` to produce the report
   and the brief.
4. Send `status_brief.md` for a quick update, or `status_report.md` when the detail
   (risk owners, specific asks, decisions needed) matters.

Requires only Python 3 (stdlib only, no dependencies) for the render step.

## Design notes

- **RAG is a rubric, not a vibe.** `SKILL.md` gives Claude specific, checkable
  conditions for red/amber/green (a confirmed slip with no recovery plan is red,
  full stop) instead of leaving "how bad is this" to a feeling — the same judgment
  the first two projects apply to story points and critical-path risk, applied here
  to status reporting.
- **Overall status is the worst load-bearing epic, not the worst epic.** A red status
  on a task with 11 days of slack shouldn't make the whole project read as red; only
  epics that actually touch the critical or near-critical path can drag the overall
  rating down — mirroring `critical-path-mapper`'s on-path/near-critical/off-path
  distinction.
- **Good news is part of the report, not an afterthought.** The rubric explicitly
  asks for resolved risks and early finishes, not just what's late — a status report
  that only ever escalates isn't trustworthy either.
- **The renderer validates what the model can't guarantee.** `render_status.py`
  rejects any `status.json` with an invalid RAG/severity value or a risk missing an
  owner or an ask, so a malformed judgment fails loudly instead of shipping a report
  with a blank cell where an accountable owner should be.
- **`status.json` also feeds the flagship.** Along with the other three tools'
  outputs, it's one of the four inputs to
  [`tpm-command-center`](https://github.com/punit-labs/tpm-command-center), which
  aggregates the whole pipeline into one dashboard.

## License

MIT — see [LICENSE](LICENSE).
