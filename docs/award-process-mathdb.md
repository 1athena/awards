# How to participate and claim a reward through MathDB

[Home](../README.md) · [Pilot problems](../problems/mathdb-pilot.md) · [Legacy process](award-process.md)

[MathDB](https://mathdb.com/) is a partner of The Justin Sun Prize and a community
platform for mathematical definitions, theorems, conjectures and open problems.
It brings together research updates, discussions and explanatory materials;
see [About MathDB](https://mathdb.com/about).

In this pilot, MathDB's role is to review mathematical solutions and expositions,
verify Lean formalizations and submit reviewed contribution materials through
this process. The prize team determines final qualification, award decisions
and payment.

Rules version: **mathdb**. This is the new process for the 50 problems in the
[pilot register](../problems/mathdb-pilot.md). Other problems continue under the
legacy process until their migration is announced. We recommend the new process
for participating problems and intend to extend it to the remaining problem bank.
Adding a MathDB link alone does not migrate a problem.

This repository change prepares the pilot. Formal automatic claims begin after
activation is announced and the official MathDB account is configured. The
[pilot page](../problems/mathdb-pilot.md) records rollout and any unresolved scope;
resolve those questions before automatic handoff for the affected problem.

Problem levels and estimated rewards are not recorded in this repository.

## Contributions and conditions

| Category | Share of the formally announced problem reward | Required evidence |
| --- | --- | --- |
| Solution | 50% | Complete mathematical solution of the original problem, accepted mathematical review, original public date and earliest-valid-contributor evidence. |
| Lean | 30% | Complete formalization of the original problem, corresponding mathematical solution, fixed proof version, verification, original public date and earliest-valid-contributor evidence. |
| Exposition | 20% | Reviewed video, article or other explanation, and a committee decision identifying the first contributor whose exposition satisfies the committee. |

Each category is reviewed, recorded and publicly reviewed separately. These are
category shares, not a reward for every upload or every person whose materials
pass a technical check. The team confirms the applicable formally announced
reward and any joint-author allocation; the catalog supplies no reward estimate.

**Solution and Exposition awards are both gated by verification of a complete
Lean formalization of the original problem.** Each category keeps its own review,
attribution and reward share. The Lean formalizer need not claim or receive an
award first, and a Solution claim or award is not a prerequisite for Lean or
Exposition.

The [problem index](../problems/README.md#mathdb-pilot-claim-status-columns) shows
independent Solution (under Solver) and Lean registration states; the
[pilot page](../problems/mathdb-pilot.md#pilot-register) also shows Exposition:
blank when no record is published, otherwise `Candidate` or `Awarded`. They summarize the public registers,
not technical acceptance, committee selection, pending claim issues or payment.
Exposition also requires its own content review and committee selection. Catalog
Solved/Lean flags alone do not establish the required Lean verification.

Solution and Lean each require their own complete original result to have become
public **after 2026-01-01**, and the claimant to be the earliest valid contributor
for that problem and category. Compare independently verifiable public history,
including earlier results before the cutoff. Re-uploading, re-verifying or opening
a new issue does not change a result's date or priority. A record stating only
2026-01-01, an uncertain timezone or an unresolved priority conflict goes to the
team for clarification; the agent must not infer qualification.

The cutoff is not automatically applied to Exposition. Content approval or the
earliest upload cannot replace the committee's decision, date and selected version.
Expositions may be submitted for an open problem, but must distinguish proved
statements from unresolved claims and identify citations and original
contributions. Announcement and payment wait for complete Lean verification.

## 1. Select the problem and submit to MathDB

Use the JSP entry and its confirmed MathDB link. Check the exact statement, field,
dimension, hypotheses and conclusion. Report a missing or incorrect mapping using
the [correction form](../.github/ISSUE_TEMPLATE/correction.yml); resolve it before
automatic handoff.

Links display no status prefix. Catalog metadata records unresolved formulations
and page-statement issues;
`Matching page pending` means a full corresponding page has not been located.
These are independent of reward-candidate status. The catalog notes also record related
and alternative pages for review. They do not change the approved formulation by
themselves. JSP-000002 asks whether P equals NP; a complete proof of either
equality or separation resolves that question. JSP-001024 (metric SYZ) and
JSP-001072 (Hodge-theoretic mirror symmetry) are separate problems with separate
qualification records. JSP-001040 selects the sphere restriction statement in
dimensions n>=3 and its full exponent range. Do not substitute a non-effective
Vojta bound for the selected effective-Mordell problem. JSP-001049 links to the
algorithmic form at [MathDB #332964](https://mathdb.com/p/332964/algorithmic-mordell-conjecture):
compute all points on any genus-at-least-two curve over a number field or finite
extension. This supplies an effective height bound for each input but does not
prescribe linear or polynomial uniform dependence; a stronger quantitative
formulation requires an explicit scope decision.

Submit the relevant materials through MathDB's available submission entry point:

- **Solution:** proof or publication, fixed version, theorem/pages, authors and
  contributions, statement correspondence and original public-history evidence.
- **Lean:** original repository, branch and full 40-character commit SHA, proof
  files and target theorems, toolchain and dependencies, reproduction instructions,
  statement correspondence, axiom audit and corresponding mathematical solution.
- **Exposition:** stable material link, fixed version and publication date, authors,
  topic, cited sources and the reviewed content.

Only a complete solution and a complete Lean proof qualify in their categories.
A target proof must not depend on `sorry`, `admit` or additional unproved
assumptions replacing missing steps. A successful build alone is insufficient.
Uploading someone else's work does not make the uploader the contributor.

**The pilot does not require a proof-submission PR or a merged PR before claiming.**
PRs may still maintain public catalog records; they are not an application gate
for this version. Legacy PRs and earlier submissions remain relevant evidence.

## 2. Review and check reward conditions

MathDB reviews the mathematical solution, verifies Lean and original-problem
coverage, and reviews exposition content. The committee separately selects the
first satisfactory exposition. Each conclusion must identify the actual author,
category, exact material version, scope, UTC date and a report or team-checkable
record. A public page saying "claimed solved", community approval or an author
assertion is not a final accepted review.

MathDB may verify and adopt an existing external Lean verification record rather
than always rebuilding. Adoption must explicitly identify the original repository,
fixed proof version, full problem coverage, completeness and external evidence.
An existing "Lean proof: Yes" catalog flag alone is not adoption.

The agent also checks the date and priority evidence for Solution/Lean or the
committee decision for Exposition. Missing or uncertain evidence pauses only the
affected category. No formal automatic claim or successful-claim notification is
sent for that category until these checks pass.

<a id="3-agent-claim-and-personal-confirmation"></a>

## 3. MathDB submission and personal confirmation

MathDB submits or updates a **Claim Reward** issue after the category's technical
and reward-condition checks pass, using the
[MathDB form](../.github/ISSUE_TEMPLATE/claim-reward-mathdb.yml). Record the public
contributors, their roles and the material versions. Submission, contribution
attribution and recipient confirmation are reviewed separately by the prize team.

In the title, `categories` lists the selected contribution roles, for example
`Solution, Lean, Exposition`. The form's checkboxes mean mathematical solution author,
Lean formalization author and exposition author; any combination is allowed.
Every selected role needs its corresponding materials. A role already published
for this JSP in the candidate or award register cannot be added through a new
claim; updates to its registered claim remain allowed. Use the
[Correction](../.github/ISSUE_TEMPLATE/correction.yml) or
[Formal dispute](../.github/ISSUE_TEMPLATE/dispute.yml) form to challenge an existing
record. The static GitHub form cannot disable options for individual problems;
the post-submission check reports conflicts against the current registers.

MathDB should update the existing issue for the same problem and contribution
record when adding later qualifying roles. Search open and closed claims,
historical PRs, candidates, awards and disputes, and keep related records linked.
Preserve personal statements and team decisions; append updates without
overwriting them.

After creating or updating the issue, MathDB sends a notification from its
official mailbox to the contributor, with Cc and Reply-To set to
**thejustinsunprize@hejustinsun.com**. It includes the issue, passed categories,
versions, verification and qualification evidence, and required personal response.
Issue creation and notification are separate recoverable tasks: a mail failure
must not create another issue or be described as delivery.

The prize team requests personal confirmation and private identity evidence from
the intended recipients, with the issue and relevant contribution records linked.
After determining the proposed categories, reward and public attribution, the
team obtains the intended recipients' written confirmation of those terms.

The team independently reviews qualification, priority, attribution, duplicates,
the committee decision and applicable reward. An issue or email does not approve
an award. Use the [MathDB claim form](../.github/ISSUE_TEMPLATE/claim-reward-mathdb.yml).

## 4. Public review for each category

Administrators publish accepted categories in the
[candidate register](../candidates/README.md#mathdb-pilot-candidates), linking the
claim, MathDB problem, fixed material and verification/committee evidence. Record
explicit UTC start and scheduled end, separated by 14 full days, and the rule
version. Public review starts at the category's actual candidate publication,
not at submission, verification, issue creation, email or a historical PR merge.

**Accepted Solution and Exposition contributions may be claimed and publicly
reviewed before complete Lean evidence is available.** After public review, both
remain pending until the Lean condition is met; neither may be announced or paid
before then. Complete Lean evidence can come from MathDB verification or explicit
adoption of external records, and the formalizer need not claim or receive an
award first. Lean and Exposition do not wait for a solver to register a claim.

Identity checks may proceed during public review. Use an authorized public account
or candidate identifier while identity is pending. Every recipient must complete
identity verification and personal written confirmation before announcement.

Submit objections through the [formal dispute form](../.github/ISSUE_TEMPLATE/dispute.yml).
MathDB handles technical/content re-review; the prize team resolves attribution,
priority, qualification and reward issues. Hold affected categories while material
objections are unresolved. A successful replacement or substantive version or
recipient change requires review and a fresh 14-day notice for the affected
category. Ordinary text corrections and migration of an unchanged record do not
restart its clock. An unsuccessful objection preserves the original start.

## 5. Announcement and payment

After public review, the team checks current technical/committee conclusions,
original date and priority, resolved objections and related pending submissions,
identity, personal confirmations and the applicable award and payment conditions.
Before either announcing or paying a Solution or Exposition award, the team must
confirm current verification of a complete Lean formalization for that problem,
including any explicitly adopted external verification record.

Publish the confirmed category in the
[award register](../awards/README.md#mathdb-pilot-awards), retain its completed
public-review dates, evidence and claim links, and update the candidate record.
Keep other categories pending as appropriate. Record **announced / awaiting
payment** separately from **paid**; only a team-confirmed payment result permits
the latter. Closing an issue or reaching the review end is not payment evidence.

If verification, external adoption or a committee decision is withdrawn or its
scope reduced, the agent updates affected claims and notifies the contributors
and team. Loss of complete Lean evidence also holds related Solution and
Exposition announcements and payments.
The team handles corrections or revocation of previously announced or paid awards
and preserves their history.

## Private information and transition

Send private identity evidence, email addresses, payment details and delivery
information only through the official email channel or controlled systems. Do not
include them in public GitHub issues or MathDB pages. MathDB notifications identify
MathDB as sender; official prize-team mail comes from **@hejustinsun.com**. The team
never asks for private keys or seed phrases.

Retain the [legacy process](award-process.md), old claims, PRs, public-review dates
and awards. For a migrated pending application, record both rule versions and an
explicit team transition decision in its existing claim. MathDB may adopt prior
verification, but its new upload/adoption date does not replace original dates.
Unchanged candidates retain their existing public-review clock. Previously
announced or paid awards are not automatically recalculated using new shares.

Future expansion updates the approved register and mapping, announces the
effective rule version/time and states how existing applications transition.
Until that happens, problems outside the register continue under the legacy rules.
