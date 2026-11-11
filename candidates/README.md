# Public candidates

For [MathDB pilot problems](../problems/mathdb-pilot.md), use the
[new category-specific process](../docs/award-process-mathdb.md#4-public-review-for-each-category)
and the shared [Candidate register](#candidate-register) below. Solution and Exposition may
enter public review before complete Lean verification exists; the agent claim
does not itself publish a candidate. The legacy prerequisites in the following paragraphs
apply only to legacy records. Existing review dates and records are retained.

For legacy records, administrators maintain the public notice table after any
required participant PR merges. Each contribution type's
14-day review starts when its candidate is added for public notice, once the
mathematical solution and Lean proof have passed review and verification.

Follow the [award process](../docs/award-process.md#the-14-day-public-review) for
publication, challenges, replacements and review completion. Solver applications
awaiting formalization remain in their claim issue or submission PR without an
active review clock. Both claim statuses remain **Unavailable** unless the
problem bank's shared **Eligible to claim** flag is **Yes**, requiring both a
mathematical solution and a Lean proof. Once eligible, each role remains
**Unclaimed** while listed here for public review. Change only the awarded role
to **Claimed** when its contribution moves from `candidates/` to a confirmed
award record in `awards/`. Opening a claim issue, publishing a candidate or
completing its review period alone does not mark a role **Claimed**.

## Candidate register

The review-start columns record when each contribution type's public notice
began, using UTC. Existing date-only entries retain their recorded publication
dates; no time of day is inferred from a PR merge. Empty cells mean that no candidate for that role is
published in this register. They do not mean the problem lacks a mathematical
solution or Lean formalization. Problem IDs link to the problem bank for public
contribution attribution and evidence. Publication is not an award or recipient
identity confirmation; identity checks and written confirmation remain required.

| Problem ID | Solver review start (UTC) | Mathematical solver | Lean review start (UTC) | Lean formalizer |
| --- | --- | --- | --- | --- |
| [JSP-000007](../problems/catalog-0001-0100.md#JSP-000007) |  |  | 2026-11-11 | [Ziyang Qin; Yuan Liao; Ayush Khaitan; Bennett Chow (Qin and Liao contributed equally)](https://github.com/TheJustinSunPrize/awards/issues/5558) |
| [JSP-000110](../problems/catalog-0101-0200.md#JSP-000110) | 2026-10-30 | Liam Kruer; Jensen Kohlmeyer; Liam Price (equal coauthors) | 2026-10-30 | Liam Kruer; Jensen Kohlmeyer; Liam Price (equal coauthors) |
| [JSP-000697](../problems/catalog-0601-0700.md#JSP-000697) |  |  | 2026-10-30 | [peilinliu66-dev](https://github.com/peilinliu66-dev) |

Contributions whose public-review periods ran
from 2026-09-19 to 2026-10-03 or from 2026-09-30 to 2026-10-14
have moved to the [award register](../awards/README.md#award-register).

For legacy records, when a role is awarded, replace its active candidate cell
with a labeled link to the award record and retain its completed review dates in that record. The other
role keeps its own clock. Change the awarded role's claim status from
**Unclaimed** to **Claimed** in the problem index when moving it to the award
register, and retain that status after its candidate entry is removed.
Remove a problem row once neither role remains a
candidate. If a contribution is invalidated without an accepted replacement,
remove its active candidate and review dates and retain the history. If no valid
formalization remains, retain the solver application without an active clock.
Detailed identity checks, payment/delivery information and correspondence stay
out of this public register.

MathDB pilot candidates use the same register: Solution maps to Mathematical
solver and Lean to Lean formalizer. When an Exposition candidate is accepted,
append `Exposition review start (UTC)` and `Exposition author` columns to this
table, leaving those cells empty for other records. Link each category's public
claimant names to its claim issue. Keep the rules version, MathDB problem, fixed
material, review/committee evidence, outstanding conditions and scheduled end
in the linked claim or registration PR. Use an explicit UTC start at actual
publication and a scheduled end 14 full days later; proposed entries remain
`Pending actual publication`. Existing notice dates remain unchanged.

Only administrators publish or amend candidates. A substantive recipient/version
replacement restarts only the affected category after review. When awarded,
retain completed dates and evidence in the award register and clear the active
candidate's date and names (a labeled award link may remain); remove the row
when no active categories remain. Do not duplicate active candidate and award
records. Identity and personal written confirmations are required before
announcement. Complete Lean verification/adoption is also required before
Solution or Exposition announcement/payment; Exposition requires its committee
decision. These conditions are tracked separately from the public-review clock.

After updating the register, run `python3 scripts/mathdb_pilot.py build` and
commit the generated index/pilot page. Only the corresponding pilot category's
public-registration state changes. Opening a claim or passing technical/content
review alone does not publish a candidate.
