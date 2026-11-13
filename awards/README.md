# Confirmed awards

For [MathDB pilot problems](../problems/mathdb-pilot.md), use the
[new confirmation and payment rules](../docs/award-process-mathdb.md#5-announcement-and-payment)
and the [pilot rows below](#mathdb-pilot-awards). Preserve the existing award
register and historical decisions. The legacy process described below applies
to legacy records; no historical reward is automatically recalculated.

Only confirmed, publicly announced awards belong here.
Follow the [confirmation and delivery process](../docs/award-process.md#step-3-recipient-confirmation-and-award-delivery)
before publishing an award.

Record each awarded contribution in English Markdown, identifying the JSP
problem, contribution type, recipients, announcement link,
completed public-review dates and supporting evidence. Mathematical solution and
Lean formalization contributions are recorded separately. Update the candidate
register for the awarded contribution. Change only that role's claim status
from **Unclaimed** to **Claimed** in the problem index when it moves from
`candidates/` to `awards/`, and retain that status after its candidate entry is
removed. Any other eligible role still in candidate review remains **Unclaimed**.

See the [record guide](../docs/records.md) and optional [Markdown templates](../docs/templates/).

## Award register

Contributions with a public-review end of 2026-10-03 were moved from the candidate
register on that date at the maintainer's direction. Neel Somani's mathematical
solutions were moved on 2026-10-14 at the maintainer's direction.
Review dates retain the date-only UTC precision of the original candidate records.
Problem links provide the recorded contribution attribution and proof evidence.

| Problem ID | Contribution type | Recipients | Public-review start (UTC) | Public-review end (UTC) |
| --- | --- | --- | --- | --- |
| [JSP-000239](../problems/catalog-0201-0300.md#JSP-000239) | Mathematical solution | Neel Somani | 2026-09-30 | 2026-10-14 |
| [JSP-000305](../problems/catalog-0301-0400.md#JSP-000305) | Lean formalization | Wouter van Doorn | 2026-09-19 | 2026-10-03 |
| [JSP-000327](../problems/catalog-0301-0400.md#JSP-000327) | Mathematical solution | Neel Somani | 2026-09-30 | 2026-10-14 |
| [JSP-000371](../problems/catalog-0301-0400.md#JSP-000371) | Lean formalization | Wouter van Doorn | 2026-09-19 | 2026-10-03 |
| [JSP-000381](../problems/catalog-0301-0400.md#JSP-000381) | Lean formalization | Wouter van Doorn | 2026-09-19 | 2026-10-03 |
| [JSP-000526](../problems/catalog-0501-0600.md#JSP-000526) | Mathematical solution | Wouter van Doorn; Yanyang Li; Quanyu Tang | 2026-09-19 | 2026-10-03 |
| [JSP-000526](../problems/catalog-0501-0600.md#JSP-000526) | Lean formalization | Wouter van Doorn | 2026-09-19 | 2026-10-03 |
| [JSP-000866](../problems/catalog-0801-0900.md#JSP-000866) | Mathematical solution | Quanyu Tang | 2026-09-19 | 2026-10-03 |
| [JSP-001001](../problems/catalog-1001-1022.md#JSP-001001) | Mathematical solution | Yanyang Li; Quanyu Tang | 2026-09-19 | 2026-10-03 |

### MathDB pilot awards

Publish a category only after the team's qualification, identity and personal
written confirmations, 14-day public review, resolved material objections and
applicable payment conditions are complete. Both Solution and Exposition require
current complete Lean verification of the original problem or MathDB's explicit
adoption of external evidence before announcement and payment.
The formalizer's own award is not a prerequisite. Retain fixed versions, evidence,
claim and candidate-history links; the register records no levels or estimates.

No MathDB pilot awards have been announced yet.

| Problem ID | Category | Confirmed recipients | Rules version | MathDB / fixed evidence | Claim issue | Completed public review (UTC start/end) | Announcement and retained candidate history | Payment status and team confirmation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

Distinguish `Announced / awaiting payment` from `Paid`; the latter requires the
team's confirmed payment result, without publishing private payment details.
Closing an issue, elapsed notice or an agent notification is not payment evidence.
The team retains any later correction/revocation and its evidence in the history.

Use category `Solution`, `Lean` or `Exposition`. After updating these rows and the
candidate table, run `python3 scripts/mathdb_pilot.py build` and commit the generated
index/pilot page. The category's `Awarded` registration state reports this announced
record; the detailed record controls any later correction/revocation and whether
payment has been confirmed.
