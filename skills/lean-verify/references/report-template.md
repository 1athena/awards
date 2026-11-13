# Verification report template

Write `report.md` in English by default, unless the user requests another language. Include the substantive information below and explain inapplicable items. Report each problem separately; do not transfer one problem's pass to other problems in the PR. Template prompts are not observed results.

## Conclusion

Start both the report and final response with an explicit verdict rather than "see the report." Fill in actual results using this structure; do not repeat every option unchanged:

> **Overall verdict: Verification passed / Conditional pass / Partial coverage / Verification failed / Insufficient evidence.**
>
> For the specified JSP/Erdős problem or original statement, this submission at the full proof-repository commit SHA fully solves / does not fully solve / cannot yet be confirmed to fully solve the original problem. Decisive reason: specific evidence.

| Required question | Explicit judgment | Decisive evidence |
| --- | --- | --- |
| Does the proof address the specified original problem? | Yes / No / Cannot yet determine | Correspondence of definitions, quantifiers, assumptions, and conclusions |
| Did the specified commit actually pass verification? | Yes / No / Verification incomplete | Target-check commands, exit codes, and logs |
| Does it fully solve the original problem? | Yes / No / Cannot yet determine | Coverage of all obligations, proof chain, and axiom audit |
| Does it meet the Lean completeness requirements for this verification? | Meets / Does not meet / Cannot yet determine | Assessment under SKILL.md's acceptance rules |

State actual verification levels, extended trust conditions, and scope. A successful build alone does not establish a complete solution. Network/resource blockers are not mathematical proof errors. For a conditional pass, state whether the applicable acceptance criteria accept the condition; if unknown, the acceptance judgment is "Cannot yet determine." For uncertainty, list what is missing, the affected judgments, and how to resolve it. For unmet requirements, identify the specific defects to fix. This conclusion concerns Lean proof verification, not merging, awards, or payments.

For multi-problem PRs, also provide a per-problem summary:

| Problem ID and name | Traceability | Statement correspondence | Unmodified build/target checks | Proof completeness | Full problem coverage | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| One row per problem | Verified/missing/conflicting | Matches/mismatch/unknown | Passed/failed/incomplete | Complete/gaps/unknown | Full/partial/unknown | With reasons |

Without a PR, identify this skill's completeness criteria as the acceptance standard, or state any user-specified criteria. Mark inapplicable awards base/head fields, JSP identifiers, and similar fields "Not applicable" rather than inventing values.

## Pinned evidence

- Retrieval time with timezone, PR URL, awards base/head repositories, branches, and full SHAs; whether PR head changed at the final check.
- Pinned catalog base/head links, JSP and original problem identifiers, exact problem sources, paper versions/pages.
- Lean repository URL, project root, claimed branch, branch tip, checked SHA, commit/branch ancestry, and check time.
- Original source links, commit-pinned file/line links, and all fully qualified target declarations; attachment/Gist revisions/hashes.
- Revision conflicts, missing pins, inaccessible comments/materials; distinguish temporary snapshots from submitter-specified revisions.
- `targets.json` path and hash, project/commit for each manifest, and whether the original problem, formal statement, and external proof belong to different versions.

## Mathematical statement and coverage

Provide the exact original statement, readable excerpts of the Lean target and necessary definitions, and an explanation of their correspondence. Complete the coverage matrix; list equivalence/implication bridges and their check results. Include every direction, range, subproblem, and boundary condition.

Describe minimal, reproducible mismatches, such as "the original requires all n, but the declaration covers only n ≤ 100" or "the main theorem still takes its conclusion as an argument." Do not merely label the formalization incomplete.

## Environment and execution

| Item | Observed value and evidence |
| --- | --- |
| OS/architecture/isolation | Versions, container image digest or equivalent environment, resource limits |
| Toolchain | `lean-toolchain`, Lean/Lake/Elan versions, provenance, paths |
| Dependencies | Manifest hash, actual mathlib/other dependency SHAs, cache provenance |
| Unmodified build | Command, cwd, exit code, elapsed time, log path |
| Explicit target checks | Commands/results for each module/file and whether source was rechecked |
| Semantic bridges and axiom audit | Audit files, commands, output, exit codes |
| Kernel/external cross-checks | Tool versions, configuration/targets, logs; reasons for checks not run |
| Post-run state | Source/dependency changes, untracked audit files and locations |

Report automation separately: `mechanical_status`, exit code, whether target-result counts match the manifest, input stability, and outstanding environment prerequisites. Keep semantic judgments distinct from tool results; `standard_axioms_only` is not full-problem acceptance.

## Proof dependencies and gaps

For each target, list complete `#print axioms` output and distinguish standard foundations, placeholder axioms, native computation, and custom assumptions. For unfinished steps, show the dependency path from target to problem. Identify repository-wide warnings unrelated to the target and those that enter its proof chain.

## Findings, limitations, and next steps

Order findings by their effect on complete verification. For each, include: requirement → observation → pinned code/original-source location → check logs → effect on the verdict → minimal repair or additional evidence. Distinguish confirmed defects, concerns, and environmental blockers.

List unreviewed material, external trust, and any need for expert semantic review. If diagnostic patches were used, attach the diff and separate patched results from the original submission's verdict. Do not infer award approval, payment, or author identity from reproduction results.

## Reproducible artifacts

Link `evidence/` snapshots, pinned-version manifests, environment configuration, `audit/` files, complete `logs/`, independent checker artifacts, and diagnostic patches. Record working directory, order, and actual arguments for each reproduction command so readers need not reconstruct missing context from the conversation. Remove credentials and private information before public sharing; this skill does not upload automatically.
