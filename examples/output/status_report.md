# Status Report — Nimbus Expense — Multi-Currency & Delegate Approvals

**As of:** 2026-08-14
**Overall status:** 🔴 RED

The critical path has already slipped: EPIC-2-1 (zero slack) finished one business day late on Aug 12, and EPIC-2-3 (also zero slack) is now confirmed one day behind as a result, with Backend Eng stating there's no way to compress it further. Absent a decision to compress EPIC-3-4, the project finish moves from 2026-08-20 to 2026-08-21. Overall status reflects this — the worst-rated load-bearing epic — even though the slip is one day and one open risk (the compliance question on export attribution) was resolved this period.

## Schedule

- Target finish: 2026-08-21
- Business days remaining: 5
- On track: No

## Highlights

- **EPIC-1** (Multi-currency expense submission & display): Web and mobile currency selectors (EPIC-1-4, EPIC-1-5) delivered on schedule, no issues.
- **EPIC-2** (Shared approval-resolution & delegate setup): The root cause (auth-service permissions gap) is resolved and isn't expected to recur on the remaining delegate-routing work.
- **EPIC-4** (Admin controls for rollout): EPIC-4-3 (feature flags) finished early.
- **EPIC-5** (Finance reporting export updates): Compliance confirmed the export-attribution rule this week (delegate-approved expenses attribute to the original approver) — this was the open question the PRD itself left unresolved, and it was also the single highest-severity cross-team risk on the register. It's closed.

## Epic Status

| Epic | Status | Notes |
|---|---|---|
| EPIC-1 — Multi-currency expense submission & display | 🟡 AMBER | EPIC-1-2 (FX rate integration) finished, but consumed half its schedule buffer (2d slack down to 1d) resolving a vendor sandbox rate-limit issue. No confirmed slip yet, but the remaining buffer is thin. |
| EPIC-2 — Shared approval-resolution & delegate setup | 🔴 RED | EPIC-2-1 (zero slack, on critical path) finished 1 business day late (Aug 12 vs. planned Aug 11) due to an unplanned permissions issue with the Identity team. EPIC-2-3 (also zero slack) started a day late as a result and is now projected to finish Aug 15, one day past its Aug 14 target, with Backend Eng saying they're already at capacity and can't compress further. |
| EPIC-3 — Delegate notifications & audit trail | 🟡 AMBER | EPIC-3-4 (zero slack, on critical path) hasn't started yet — blocked on EPIC-2-3. Platform Eng's own 4-day estimate is unchanged, so once unblocked this shouldn't add further delay beyond the 1 day already reflected in the project finish date, but the entire finish date now rides on that estimate holding exactly. |
| EPIC-4 — Admin controls for rollout | 🟢 GREEN | All admin/rollout work is low-risk and off the critical path with wide slack; no issues reported. |
| EPIC-5 — Finance reporting export updates | 🟢 GREEN | The compliance question this whole epic was gated on has been resolved, and the remaining work (EPIC-5-3) is now unblocked with its slack intact. |

## Risks & Blockers

| Severity | Risk | Owner | Ask |
|---|---|---|---|
| HIGH | Critical path has slipped 1 business day (EPIC-2-1 → EPIC-2-3), with no compression available on the Backend Eng side. | Platform Eng / Backend Eng | Confirm whether to accept the 1-day slip to 2026-08-21, or authorize parallel/expedited work on EPIC-3-4 to try to hold the original 2026-08-20 date. |
| MEDIUM | FX integration (EPIC-1-2) burned half its schedule buffer resolving a vendor rate-limit issue; only 1 day of slack remains if it recurs. | Backend Eng | No action needed yet — flagging so it isn't a surprise if this needs escalation next period. |
| MEDIUM | EPIC-3-4 hasn't started and the whole revised finish date depends on its 4-day estimate holding exactly, with zero slack to absorb any further surprise. | Platform Eng | None currently — monitoring. Will escalate if EPIC-2-3 slips past Aug 15. |

## Milestones

- **2026-08-15** — EPIC-2-3 (delegation records + auto-expiry) expected to complete, one day behind original plan.
- **2026-08-21** — Revised project finish date (originally 2026-08-20), pending the decision on EPIC-3-4.

## Decisions Needed

- Accept a 1-business-day slip to 2026-08-21, or authorize parallel/overtime work on EPIC-3-4 (notification lifecycle events) to try to hold the original 2026-08-20 date. (owner: Eng leadership / TPM, needed by: 2026-08-15)

