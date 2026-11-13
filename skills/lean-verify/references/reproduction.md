# Pinned revisions and reproduction

The commands below are operational templates. Determine values from evidence and use structured tool arguments or safely quoted shell variables; never execute PR text as a script. Assign trusted, validated values to `pr_number`, `proof_url`, `proof_sha`, `proof_branch`, `run_dir`, `target_module`, and `audit_file` before use.

## 1. Capture complete snapshots

These API examples are for awards mode. For Erdős/direct-source inputs, follow [Input routing](input-routing.md); retrieve discussion and base/head snapshots only for actual PRs.

Prefer connected GitHub tools or the following read-only APIs. `pr_number` must contain decimal digits only. Do not infer that no comments exist because a webpage did not display them.

```bash
gh api "repos/TheJustinSunPrize/awards/pulls/$pr_number"
gh api --paginate "repos/TheJustinSunPrize/awards/pulls/$pr_number/files?per_page=100"
gh api --paginate "repos/TheJustinSunPrize/awards/pulls/$pr_number/commits?per_page=100"
gh api --paginate "repos/TheJustinSunPrize/awards/issues/$pr_number/comments?per_page=100"
gh api --paginate "repos/TheJustinSunPrize/awards/pulls/$pr_number/reviews?per_page=100"
gh api --paginate "repos/TheJustinSunPrize/awards/pulls/$pr_number/comments?per_page=100"
```

Save raw responses in `evidence/`. API file/commit lists have limits; compare total counts and pagination, and fill gaps with pinned Git objects. Comments are mutable, so record comment IDs, update times, and retrieval times.

Clone each proof repository separately rather than reusing the user's checkout. First validate the expected URL protocol/host/path and full hexadecimal SHA, then run:

```bash
git clone --no-checkout -- "$proof_url" "$run_dir/sources/proof"
git -C "$run_dir/sources/proof" cat-file -t "$proof_sha"
git -C "$run_dir/sources/proof" checkout --detach "$proof_sha"
git -C "$run_dir/sources/proof" rev-parse HEAD
git -C "$run_dir/sources/proof" status --porcelain
```

If cloning did not retrieve the object, fetch that full SHA from the original repository and record the command. If unavailable, preserve the failure evidence rather than falling back to the default branch. Use separate directories per repository/commit; do not overwrite one repository with another.

For branch membership, first run `git check-ref-format "refs/heads/$proof_branch"`, fetch the branch into an audit-specific ref, and use `git merge-base --is-ancestor`. Distinguish exit codes 0 (contained), 1 (not contained), and other values (operation error). Do not split a URL at the first slash to guess a branch: branch names may contain `/`; resolve them through Git refs/API. For tags, record the original name and peeled commit SHA.

Inspect `.gitmodules`, Git LFS pointers, generated-source provenance, and nested Lean projects. Review paths and sources before downloading, then record actual object/content hashes. For a single `.lean` file, hash the original content too. Reconstructing a dependency project creates an audit harness, not the author's original project. Pin Gist/attachment revisions or content hashes and disclose missing standard repository branches/SHAs.

## 2. Set up the environment

Statically inspect `lean-toolchain`, `lakefile.lean`/`lakefile.toml`, `lake-manifest.json`, README, and CI first. Lake configuration, Lean macros, and build scripts may execute code. Prepare a real container/VM or equivalent restricted environment before building; a temporary directory alone is not isolation.

- Mount only this run's source and output directories. Do not expose SSH credentials, GitHub tokens, the user's home directory, the host Docker socket, or a writable awards checkout. Use an unprivileged user and memory/CPU/disk/runtime limits appropriate to the available environment and project size; record them and do not purchase compute without authorization.
- Restrict download-stage networking to necessary sources and disable networking during submitted-code execution where possible. Use an external trusted process for authenticated retrieval; keep authentication configuration out of the proof environment.
- Use official Lean/Elan sources. Missing tools may be installed in a run-specific tool directory or an image pinned by digest; verify provenance and available checksums. Do not change the user's global default toolchain or shell configuration, or trust a repository-supplied executable named `lean`.
- Install and use the exact version from the original `lean-toolchain`. Record Lean, Lake, and Elan versions, platform/architecture, tool paths, toolchain file, and image digest. Do not hardcode `latest` or edit the pin for convenience.
- Pin dependencies using the original manifest and verify actual checkout SHAs. Do not replace it with `lake update` or upgraded dependencies when judging the original submission. If absent, first recover pins from fixed configuration/CI. Resolve dependencies only in a separate diagnostic copy when needed, retaining the result and diff. Treat it as reproduction of the original only with independent evidence that those were its dependencies; successful floating-dependency or migrated builds do not establish that the original version passed.

If isolation is unavailable, continue static review and disclose the execution blocker. Shell access alone does not establish that arbitrary PR code is safe to run on the host.

## 3. Execute checks and retain logs

Create a manifest and run preflight following [Automation](automation.md). Automated `run` covers only the explicit module, source, and declaration checks below; dependency preparation, a clean build, and additional checkers still require separate execution and evidence. Missing lockfiles can block the script without implying mathematical failure. For non-Lake projects, attachments, or incompatible versions, perform equivalent manual checks and state the reproduction limits.

Enter the subproject containing Lake configuration. Record original source state and tool versions. Use absolute toolchain paths or a controlled PATH, clear external injections such as `LEAN_PATH`, and record the actual search path generated by Lake. Determine flags from that version's `lake --help` and `lean --help`; treat CI as a reference, not an unchecked script to execute.

Perform these steps in order, recording separate exit codes:

1. Prepare the pinned dependencies; cache provenance and SHAs must match. Do not directly trust submitter-provided `.olean` files for audited sources or custom dependencies.
2. Build the project from clean source. Ensure tracked precompiled artifacts cannot bypass rebuilding. Logs should distinguish re-elaborated targets from trusted dependencies using cached artifacts.
3. Explicitly build each target module rather than trusting default `lake build`. Modern Lake supports `lake build "+$target_module"`; verify support in the pinned version, otherwise use its explicit module target syntax or individual file checks.
4. Run `lake env lean path/to/Target.lean` on the exact target source and execute audit files. Source checking does not automatically rebuild all imports, so the preceding clean build cannot be omitted.
5. Check declarations, axioms, key definitions, and semantic bridges. Finally record `git diff`, `git status`, and dependency/manifest changes to confirm execution did not silently alter the audited source.

Keep complete stderr/stdout. Do not infer success from a final `success` line, empty stderr, or author-provided logs. Preserve the actual command's exit code through shell pipelines, for example in Bash:

```bash
set -o pipefail
lake env lean "$audit_file" 2>&1 | tee "$run_dir/logs/axioms.log"
audit_status=${PIPESTATUS[0]}
```

Save `audit_status` immediately, then verify that every expected declaration and dependency list appears. Checker failures, missing identifiers, truncated output, or nonzero exit codes require an incomplete/failed result, not approval based on absent keywords. Preserve final logs and limits for timeouts, OOM, full disks, and download failures. Retry only with justified adjustments, not indefinitely.

Example audit file; replace module and declaration names before execution:

```lean
import Submission.Main

set_option pp.all true in
#check @Submission.mainTheorem

#print Submission.mainTheorem
#print axioms Submission.mainTheorem
```

Check every target and added bridge; these example names are not actual targets. Scans for `sorry`, `admit`, `axiom`, `native_decide`, `ofReduceBool`, `trustCompiler`, `debug.skipKernelTC`, `implemented_by`, or `extern` only locate leads. Verify semantics and transitive dependencies afterward. Retain raw axiom names; mechanisms differ across versions.

## 4. Verification levels and version compatibility

Prefer kernel replay compatible with the original toolchain. Since Lean v4.28.0, the formerly standalone `lean4checker` has moved into the toolchain as `leanchecker`. Older projects may use a matching standalone checker; do not force the newest checker onto old `.olean` files. Read the actual binary's `--help` and that version's official documentation for fresh/replay modes, module selection, and dependency scope. Pin the checker commit/version and retain commands and exit codes. It still uses Lean's kernel and is not an independently implemented checker. [Official migration note](https://github.com/leanprover/lean4checker)

For award proofs or concerns about metaprograms/definition substitution, independently prepare the original-problem challenge in a trusted environment where compatible, and use a comparator with its supported external checkers. Specify the theorems/definitions, permitted axioms, and standard-library source. Do not load untrusted definitions into the challenge as its specification. Retain challenge/configuration files, exported artifact hashes, and every checker result. Running `lake comparator` without configuring real targets does not establish a completed comparison. [Lean verification levels](https://lean-lang.org/doc/reference/latest/ValidatingProofs/)

Record unavailable/incompatible tools and alternative checks. Do not upgrade the audited Lean version just to use a comparator. Report any separate migration experiment independently from the original version. If an external checker does not support native-computation dependencies, describe extended trust and incomplete verification accurately rather than declaring the original proof false.

## References

Use these links to confirm commands for the pinned version; `latest` documentation does not establish syntax for older toolchains:

- [Official Elan repository](https://github.com/leanprover/elan): installation and toolchain management.
- [Official Lake manual](https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Lake/): projects, module targets, dependencies, and comparator configuration.
- [Lean axioms](https://lean-lang.org/doc/reference/latest/Axioms/): transitive axiom dependencies of declarations.
- [Lean tactic reference](https://lean-lang.org/doc/reference/latest/Tactic-Proofs/Tactic-Reference/): `sorry`, native computation, and their trust boundaries.
