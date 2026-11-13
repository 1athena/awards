# Target manifests and automated checks

Automation adds evidence; it does not make the final mathematical judgment. `scripts/audit.py` uses the Python 3.9+ standard library and requires no third-party Python packages. It currently supports Git+Lake projects, official release/rc toolchain pins, ordinary dotted Lean identifiers, and the tested `#print axioms` output formats. For incompatible versions, escaped identifiers, or other project layouts, use equivalent manual checks and record gaps. Tool limitations are not mathematical errors.

## 1. Create targets.json

Copy `assets/targets.example.json` into the audit directory and replace its example values. Do not execute an unfinished template. Each manifest covers one project and commit; use separate manifests for different repositories or revisions.

| Field | Meaning |
| --- | --- |
| `schema_version` | Currently 1 |
| `project.root` | Absolute path to the isolated checkout; may be a Lake subproject within the repository |
| `project.repository/commit/toolchain` | Source, full lowercase 40-character SHA, and exact `lean-toolchain` contents; separately disclose temporary snapshots in the report |
| `problems[].id/source` | Independent problem identifier/name and original source |
| `requirements[].id/description` | Each requirement independently extracted from the original problem; IDs are unique within that problem |
| `requirements[].targets` | Associated target IDs; use an empty list and `uncovered` when no checkable proof exists |
| `requirements[].coverage` | `pending/full/partial/uncovered`; a human semantic judgment, not validated as true by the script |
| `requirements[].evidence` | Required unless pending: coverage matrix, original passage, semantic review, and log locations |
| `targets[].id/problem/role` | Unique target ID, associated problem, and `theorem` or `bridge` |
| `targets[].module/source/declaration` | Module name, `.lean` path relative to the project root, and fully qualified declaration name |

List every main theorem and bridge, linking each target to at least one requirement. Retain original requirements without targets. If a problem has no proof source at all, report the missing material rather than inventing a target just to run the script. Mechanical checks establish manifest consistency, not whether the manifest includes every original obligation.

Use named theorems for independent bridges so their axioms can be audited. Place trusted auditor-created bridge modules on an importable path in the isolated copy and record them as untracked harness files. Do not modify original target sources or Lake configuration; list harness differences separately. If import requires intrusive changes, use a separate harness project/manifest or manual checks rather than silently altering the submission. Review the mapping between `module` and `source` to avoid importing a same-named module from another source.

## 2. Preflight and preparation

Run from the skill directory, replacing paths with actual values:

```bash
python3 scripts/audit.py preflight /audit/targets.json --out /audit/preflight-01
python3 scripts/audit.py prepare /audit/targets.json --out /audit/prepared-01
```

Output directories must not already exist and must be separate from the project, preventing old results from contaminating new checks. Preflight reads configuration files and Git state only; it does not run Lake/Lean or install dependencies. It records HEAD, toolchain and lockfiles, target file hashes, and gaps. Files with `role=theorem` must exist at the specified commit and match their blobs. `prepare` additionally generates audit `.lean` files for each target.

`ready_for_target_checks` means only that static prerequisites are present. Manually satisfy the listed `manual_preconditions`: real isolation, resource limits, tool provenance/actual versions, dependency checkout SHAs, trusted caches, clean source rebuilds, untracked files, and module mappings. Verify checker compatibility separately; preflight does not download or test a checker.

Handle missing lockfiles or historical versions manually under the reproduction reference, recording the guarantees achieved. Do not fabricate manifests, change pins, remove uncovered requirements, or clean away the author's uncommitted changes to make preflight pass.

## 3. Execute target checks

**Complete and record the unmodified clean build before invoking run inside an isolated environment. The script does not create that environment.** Specify the absolute path to Lake in a trusted toolchain rather than a submitter-provided binary. Clearing environment variables only avoids search-path mistakes; it is not a security sandbox.

```bash
python3 scripts/audit.py run /audit/targets.json \
  --out /audit/check-01 \
  --lake /trusted/lean-toolchain/bin/lake \
  --timeout 300
```

Record actual Lake and project Lean versions, checking the Lean release/rc against the pin. Nightly, custom toolchains, or unrecognized version output require manual verification. For each target, run explicit `lake build +Module`, check its source with `lake env lean`, and execute generated `#check @name` / `#print name` / `#print axioms name` commands. Continue other targets after one fails. Retain argument arrays, cwd, exit codes, elapsed times, complete combined logs, log hashes, script/manifest hashes, and before/after comparisons of target/configuration files and HEAD.

Each command has its own timeout; the isolated environment also needs total runtime, disk, memory, and CPU limits. Unstable inputs make the overall result `incomplete`; even observed `sorryAx` output cannot then be attributed directly to the original commit. Results do not replace before/after checks of the full source tree and dependencies. The script does not fetch dependencies, clean the project, run kernel replay, or run a comparator.

| Result | Exit code | Meaning |
| --- | --- | --- |
| `standard_axioms_only` | 0 | All manifest targets passed their checks with at most the three standard transitive axioms observed; the semantic conclusion remains `not_determined`. |
| `proof_gap` | 1 | With stable inputs, at least one checked target depends on `sorryAx`; report blockers for other targets too. |
| `trust_review_required` | 2 | Other axioms were observed and need source review. They may be placeholders or extended trust such as native computation; do not automatically declare the proof invalid. |
| `incomplete` or preflight/input error | 2 | Failed commands, timeouts, missing/duplicate/unparseable output, version mismatch, or changed inputs. Use logs to distinguish proof-check failures from environmental blockers. |

There is no one-click custom-axiom allowlist. Explain each additional trust dependency in the report; a conditional acceptance judgment requires explicit acceptance by the applicable criteria. Manually assigned coverage cannot skip targets or directly change the mechanical result.

The audit concerns target dependencies: `sorry` in unrelated files does not automatically invalidate a target. `P → P` can pass mechanically yet fail semantic review for extra/circular assumptions. Untrusted environments may influence `#print` output; these logs are neither tamper-proof certificates nor independent kernel checks. Retain the main skill's challenge and external-check requirements.

## 4. Regression checks

```bash
python3 -m unittest discover -s tests -v
```

Default tests cover manifests, failure handling, and output parsing. Simulated-output tests are not actual Lean verification. Real regression tests require an already installed trusted Lake; tests do not download or install a toolchain:

```bash
LEAN_AUDIT_TEST_LAKE=/trusted/lean-toolchain/bin/lake \
  python3 -m unittest discover -s tests -v
```

Real fixtures use only Lean's standard library, create temporary projects, and pin fixture commits. They cover valid proofs, indirect `sorry`, unrelated placeholders, extra axioms, circular assumptions, missing declarations, and modules outside the default build. The circular-assumption fixture should succeed mechanically with semantics undetermined, guarding against overclaiming automation.

The recorded real Lean regression baseline is Lean 4.32.0; other versions still need syntax/output compatibility checks. Declaration printing retains detail, while axiom-list printing disables universe display to avoid misclassifying `sorryAx.{u}` as an unknown axiom.
