# Citation

Template only. A candidate narrative must explicitly identify its pending status.

## English

Describe the mathematical result, public evidence, and published decision or pending review status. Do not claim a candidate has received an award.

For a contribution entering public review, also identify:

- Contribution type: mathematical solution or Lean formalization.
- JSP problem and accepted submission PR.
- Public-notice start: when the candidate was added to the candidates register and public notice began, not a PR merge time. Record the start and scheduled end in UTC, 14 full days apart; preserve date-only precision for historical entries.
- Current pending status; an unresolved challenge or relevant pending PR review prevents public review from concluding.

An accepted solver awaiting formalization has no review start or end yet. Keep
published dates consistent with the [public notice table](../../candidates/README.md#candidate-register).
Retain completed public-review dates when the contribution becomes an announced
award. Do not include private identity checks, payment/delivery information,
application-time logs or correspondence.

### Public-review completion check

Complete this check before concluding public review. Check the current PR list for
the same problem and contribution type, regardless of submitter. Include PRs that
could affect correctness, contribution attribution or priority; unrelated changes
do not block completion.

- Checked at (UTC): REPLACE_WITH_CHECK_TIME_OR_NOT_YET_CHECKED
- Scope: JSP-______ / mathematical solution or Lean formalization.
- Relevant pending PRs found: REPLACE_WITH_PR_LINKS_NONE_OR_NOT_YET_CHECKED
- Review results: for each relevant PR, record its link, whether review is pending
  or complete, the outcome, and a link to the public review conclusion. If none
  were found, explicitly record `None` after checking.
- Conclusion: REPLACE_WITH_NOT_YET_CHECKED_WAIT_FOR_REVIEW_OR_READY_TO_CONCLUDE
- Basis for the conclusion: REPLACE_WITH_REMAINING_BLOCKERS_OR_COMPLETED_CHECKS

Use `Ready to conclude` only after the full 14-day period has elapsed, all relevant
PR reviews are complete and no unresolved challenge remains. If a review is still
pending, record `Wait for review` and repeat this check once it is complete.
Waiting alone does not restart the clock. An accepted replacement starts a new
period when it is added to `candidates/` and its public notice begins. Completing
public review does not replace recipient identity checks or written confirmation.
