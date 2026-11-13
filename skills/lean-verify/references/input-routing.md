# Input routing: awards, Erdős, and direct source

First distinguish verification of an existing proof from a question about methods or skills. Method questions do not trigger source deployment or a pass/fail judgment on an arbitrary submission. Keep the review read-only with respect to the submission: do not automatically repair proofs, modify the catalog, or publish comments.

## Awards PR

First check whether the submission includes a Lean proof to verify. This skill does not apply to mathematical solutions, papers, or solver information alone; do not start a Lean environment or request a self-check report for them. For combined submissions, verify only the Lean part. A missing Lean proof does not invalidate a solver's mathematical submission.

Follow SKILL.md for base/head snapshots, JSP entries, discussions, and external proof revisions. JSP and Erdős numbers are independent; when the catalog cites Erdős, retain both identifiers and evidence for their mapping.

## Erdős problem number or URL

1. Confirm that the input is an Erdős number. Ask if a bare number could mean a PR, JSP entry, or Erdős problem. The website homepage alone does not identify a verification target.
2. Read the complete original problem, context, variants, and cited sources at `https://www.erdosproblems.com/N`, recording retrieval time. Separate the main problem, additional questions, and special cases. If access is limited, try original papers or traceable snapshots and record their versions and gaps; search snippets cannot establish that the original problem was checked.
3. Follow page links and leads from [teorth/erdosproblems](https://github.com/teorth/erdosproblems) and [Formal Conjectures](https://github.com/google-deepmind/formal-conjectures). Inspect their current data formats rather than treating a field name or path as a permanent interface. Cached database status is only a lead; check its source and update time.
4. **Pin three distinct objects:** the original problem source; the formal statement file and commit; and the actual solution repository/commit/declaration. Follow external proof links from statement files. Building the statement repository does not verify an external proof. A generic repository URL or single `.lean` link does not establish that a complete solution exists.
5. Classify the available material: statement only / claimed partial result / claimed conditional result / claimed complete proof or disproof / no proof source located. Distinguish website mathematical status from Lean proof status. A placeholder `sorry` in a statement repository does not imply that an external solution contains `sorry`; inspect the actual target proof chain.
6. If several solutions exist, use the user-specified version first. Otherwise list candidates and their claimed scope rather than arbitrarily selecting one and declaring the problem verified. Continue reading the original problem and candidate metadata, and ask which version to check when necessary. For branch-only inputs, pin a temporary audit snapshot as described in SKILL.md; do not present it as the historical submission.

When no source is found, report "No verifiable solution source has been located," not that no Lean proof exists. If the material is clearly only an unproved statement, conclude that this statement is not a complete solution without extending that judgment to every result for the problem. Retain explicit assumptions in conditional literature results and apply the main skill's completeness criteria; website inclusion does not relax acceptance standards.

## Direct proof repository, commit, file, or another PR

- Require an identifiable original problem source and declarations to check. Look in the README/body first and ask only if necessary. The source author's reformulation cannot be the sole specification.
- For other GitHub PRs, also snapshot base/head and the complete relevant discussion. Pin source repositories and problem records separately. For non-PR inputs, mark PR fields not applicable.
- For Gists, attachments, or single files, record revisions/content hashes following the reproduction reference. The script requires a Git+Lake project. If unavailable, use a controlled harness for manual checks, but do not call a harness build the original project build.
- Without an awards PR, phrase the fourth conclusion as "Does it meet the Lean completeness requirements for this verification?" Identify this skill's criteria or the user's specified criteria. Do not imply endorsement by the Erdős website, maintainers, or prize organizers.
