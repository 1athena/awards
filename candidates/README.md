# Public candidates

For [MathDB pilot problems](../problems/mathdb-pilot.md), use the
[new category-specific process](../docs/award-process-mathdb.md#4-public-review-for-each-category)
and the [pilot rows below](#mathdb-pilot-candidates). Solution and Exposition may
enter public review before complete Lean verification exists; the agent claim
does not itself publish a candidate. The legacy prerequisites in the following paragraphs
apply only to legacy records. Existing review dates and records are retained.

The [register below](#candidate-register) is the public notice table, maintained
by administrators after any required participant PR merges. Each contribution type's
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

The two review-start columns record when each contribution type's public notice
began, using UTC. Existing date-only entries retain their recorded publication
dates; no time of day is inferred from a PR merge. Empty cells mean that no candidate for that role is
published in this register. They do not mean the problem lacks a mathematical
solution or Lean formalization. Problem IDs link to the problem bank for public
contribution attribution and evidence. Publication is not an award or recipient
identity confirmation; identity checks and written confirmation remain required.

| Problem ID | Solver review start (UTC) | Mathematical solver | Lean review start (UTC) | Lean formalizer |
| --- | --- | --- | --- | --- |
| [JSP-000110](../problems/catalog-0101-0200.md#JSP-000110) | 2026-10-30 | Liam Kruer; Jensen Kohlmeyer; Liam Price (equal coauthors) | 2026-10-30 | Liam Kruer; Jensen Kohlmeyer; Liam Price (equal coauthors) |
| [JSP-000697](../problems/catalog-0601-0700.md#JSP-000697) |  |  | 2026-10-30 | [peilinliu66-dev](https://github.com/peilinliu66-dev) |

Contributions whose public-review periods ran
from 2026-09-19 to 2026-10-03 or from 2026-09-30 to 2026-10-14
have moved to the [award register](../awards/README.md#award-register).

When a role is awarded, replace its active candidate cell with a labeled link to
the award record and retain its completed review dates in that record. The other
role keeps its own clock. Change the awarded role's claim status from
**Unclaimed** to **Claimed** in the problem index when moving it to the award
register, and retain that status after its candidate entry is removed.
Remove a problem row once neither role remains a
candidate. If a contribution is invalidated without an accepted replacement,
remove its active candidate and review dates and retain the history. If no valid
formalization remains, retain the solver application without an active clock.
Detailed identity checks, payment/delivery information and correspondence stay
out of this public register.

### MathDB pilot candidates

Administrators add one row per accepted category and actual claimant. Use
`mathdb`, the stable claimant's public identifier, confirmed MathDB problem,
claim issue, fixed material and technical/committee evidence, and explicit UTC
start/end 14 full days apart. Category shares and formal reward decisions are
explained in the claim; this register contains no levels or estimates. Track
complete Lean verification/adoption for both Solution and Exposition as a
prerequisite for announcement and payment, separately from public review.
Exposition also requires its committee decision. Identity may be
pending during notice but is required before announcement.

No MathDB pilot candidates have been published yet.

| Problem ID | Category | Public claimant | Rules version | MathDB problem | Claim issue | Fixed material and review/selection evidence | Review start (UTC) | Scheduled end (UTC) | Outstanding condition / status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Only administrators publish or amend these rows. Link holds, disputes and team
decisions; preserve unchanged notice dates during migration. A substantive
recipient/version replacement restarts only the affected category after review.
When awarded, retain completed dates and links in the award register and remove
the active candidate row; do not duplicate active candidate and award records.

Use category `Solution`, `Lean` or `Exposition`. After updating these rows, run
`python3 scripts/mathdb_pilot.py build` and commit the generated index/pilot page.
Only the corresponding category's public-registration state changes; opening an
agent claim or passing technical/content review alone does not create a row here.
