---
name: exec-status-report
description: Turn a project schedule (e.g. critical-path-mapper's schedule.json) plus raw, unstructured team progress notes into an executive-ready status report with an evidence-backed RAG rating, risks, and decisions needed. Use when asked for a status update, exec summary, or RAG/red-amber-green report on an in-flight project.
---

# exec-status-report

Turns a static plan (a `schedule.json`, ideally from `critical-path-mapper`) and this
period's raw progress notes into a judged, structured `status.json`, which a
deterministic script then renders into an exec-ready report.

## Inputs

1. **`schedule.json`** — the planned schedule: task ids, teams, planned start/finish
   dates, slack days, and whether each task is on the critical path. This is the
   *plan*, not the *actuals*.
2. **Raw progress notes** — freeform text (standup notes, Slack summaries, whatever
   the teams actually wrote down) describing what happened this period: what
   finished, what's late and why, what's blocked, what got resolved. This is
   unstructured and inconsistent by nature — that's what you're being asked to make
   sense of.
3. **`as_of`** — the date this report is being written for.

## What you produce

A single `status.json` matching the schema below. This is the judgment step — the
render script does no interpretation at all, so get the reconciliation right here.

### Step 1: Reconcile actuals against the plan, per task

For every task mentioned in the progress notes, compare what actually happened to
what `schedule.json` planned:

- **Finished late** — note how many days late, and whether the task is on the
  critical path or near-critical (small slack). A day late on a zero-slack critical
  task is a real slip; a day late on a task with 8 days of slack is not.
- **In progress, behind plan** — same comparison, using the team's own revised
  estimate if they gave one.
- **Slack consumed without a confirmed slip yet** — e.g. a near-critical task took
  longer than planned but still finished inside its slack window. Not a slip, but
  worth flagging if slack dropped sharply (more than half consumed).
- **Resolved risk / finished early / no news** — real status reports should carry
  good news too. If a previously-open risk got closed out this period, or a task
  finished ahead of plan, say so explicitly — don't only escalate.

### Step 2: Assign a RAG status per epic, using this rubric — not a vibe

- **RED**: a critical-path task has confirmed slipped with no identified way to
  recover the finish date, or there's a high-severity blocker with no owner or ETA.
- **AMBER**: a critical or near-critical task is behind plan but there's an
  identified mitigation, or a near-critical task's slack has been meaningfully eaten
  (more than half) without yet causing a confirmed slip, or an open risk exists but
  has an owner and a stated plan.
- **GREEN**: every critical-path task is on or ahead of plan, no near-critical task
  has had its slack meaningfully eaten, and there's no open high-severity risk
  without an owner.

Ground every rating in a specific number — days late, days of slack remaining,
days until a decision is needed — not "things are progressing well." An exec reading
the rationale should be able to independently check it against `schedule.json`.

### Step 3: Roll up to an overall status

Overall status is the **worst rating among load-bearing epics** — i.e. epics that
contain a critical-path or near-critical task. Don't let a red status on an
off-critical-path task (lots of slack, doesn't threaten the finish date) drag the
whole project to red; that's the same critical-path-vs-off-path distinction
`critical-path-mapper` draws, applied to status reporting instead of scheduling.

### Step 4: Surface risks, milestones, and decisions needed

- **Risks**: anything that could still threaten the schedule — a blocker, an
  unconfirmed dependency, a vendor issue. Every risk needs an `owner_team` and a
  concrete `ask` (what you need from someone, not just "keep an eye on it").
- **Decisions needed**: anything only a decision-maker above the team can resolve —
  e.g. "accept a 1-day slip, or authorize parallel work to hold the date." State the
  actual options, not just "there's a risk here."

## Output schema — `status.json`

```json
{
  "project": "string",
  "as_of": "YYYY-MM-DD",
  "overall_status": "green | amber | red",
  "overall_status_rationale": "string — cites specific tasks/numbers",
  "schedule_summary": {
    "target_finish": "YYYY-MM-DD",
    "business_days_remaining": 0,
    "on_track": true
  },
  "epics": [
    {
      "id": "string",
      "name": "string",
      "status": "green | amber | red",
      "status_rationale": "string",
      "highlights": ["string, optional — good news worth calling out"]
    }
  ],
  "risks": [
    {
      "id": "string",
      "summary": "string",
      "severity": "low | medium | high",
      "owner_team": "string",
      "ask": "string — the specific thing you need",
      "linked_tasks": ["task ids, optional"]
    }
  ],
  "milestones": [
    {"date": "YYYY-MM-DD", "description": "string"}
  ],
  "decisions_needed": [
    {"summary": "string", "owner": "string", "needed_by": "YYYY-MM-DD"}
  ]
}
```

## Then render it

Run `skill/scripts/render_status.py status.json --outdir <dir>`. It validates the
schema (every status/severity value is one of the allowed enums, every risk has an
owner and an ask) and produces:

- `status_report.md` — the full exec-ready report
- `status_brief.md` — a short version for pasting into Slack or the top of an email
- `status_report.html` — the same report as a single self-contained, styled HTML file

Re-running after editing `status.json` is instant — the render step has no judgment
in it, so the same input always produces the same output.
