# Raw progress notes — Nimbus Expense, week of Aug 10-14

Collected from team standups. As of Thursday Aug 14.

## Platform Eng

- EPIC-2-1 (shared approval-resolution service): done, but finished Aug 12, not
  Aug 11 as planned — hit an unplanned permissions issue wiring delegate routing
  into the existing approval service, took an extra day with the Identity team to
  resolve. This one had zero slack in the plan.
- EPIC-4-3 (feature flags): done early, no issues.
- EPIC-3-4 (notification lifecycle events): not started yet — blocked on EPIC-2-3.
  Team says once they start, the 4-day estimate still holds.

## Backend Eng

- EPIC-2-3 (delegation records + auto-expiry): in progress. Started Aug 12 (one day
  late, cascading from the EPIC-2-1 slip). Team estimates 3 days of work from start,
  which now points to Aug 15 — one day past the original Aug 14 target. No proposed
  way to compress it further; they're already at capacity.
- EPIC-1-2 (FX rate integration): done. Vendor's sandbox rate-limited us during load
  testing, so we added retry/backoff — cost a day. No schedule impact yet since this
  task had 2 days of slack, but we're down to 1 now and wanted to flag it rather than
  let it look fully green.
- EPIC-1-1, EPIC-1-3: on track, nothing new to report.

## Finance Eng

- EPIC-5-2 (compliance spike — export attribution rule for delegated approvals):
  resolved this week. Compliance confirmed delegate-approved expenses should be
  attributed to the original approver, not the delegate. This was the open question
  the PRD itself left unresolved — it's closed now, unblocking EPIC-5-3.
- EPIC-5-1 (export columns): on track.

## Web / Mobile Eng

- No blockers. Web and mobile currency selector work (EPIC-1-4, EPIC-1-5) delivered
  on schedule.
