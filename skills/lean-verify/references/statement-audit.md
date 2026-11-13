# Original problem, formal statement, and completeness

## Establish the intended target independently

In awards mode, read the catalog entry at the pinned base; for other inputs, obtain the original source through input routing. Read the exact statement in the original webpage/paper, preserving version, section/page, and access time. Record revisions at PR head and their reasons. When a catalog summary does not determine the mathematical scope, consult the original source. State any conflict rather than silently choosing a convenient version.

For each problem, write down objects and definitions, quantifier order, premises, conclusions, all subproblems, permitted proof/disproof approaches, and ambiguities in the original wording. When external mathematical references are needed, use original papers, author materials, or authoritative definitions. Search snippets, PR descriptions, and generated explanations are not complete evidence.

## Coverage matrix

Keep the [target manifest](automation.md) requirements and targets synchronized. Enumerate original requirements before mapping declarations; do not delete an unproved requirement to make manifest validation pass. The script checks whether every recorded requirement has a target or an explicit uncovered marker. It does not check whether all natural-language requirements were listed or whether manually assigned `full` coverage is true.

| Original requirement/source location | Exact mathematical meaning | Lean declaration/definition and pinned lines | Verified correspondence | Coverage and evidence |
| --- | --- | --- | --- | --- |
| One row per quantifier, condition, conclusion, or subproblem | Specify scope and boundaries | Use fully qualified names | Equivalence, implication, mismatch, unknown | Full/partial/uncovered/pending review |

Focus on:

- **Quantifiers:** the order of `∀`/`∃`, whether an existential constant is uniform over all parameters, and whether arbitrary size or infinitely many cases were replaced by a fixed bound or one instance.
- **Objects:** `ℕ`, `ℤ`, `ℚ`, `ℝ`; finite/general sets; finite/infinite dimensions; simple graphs/multigraphs; and matching measure, topological, or algebraic structures.
- **Ranges and boundaries:** zero/positive values, empty sets, open/closed endpoints, strict/non-strict inequalities, degenerate cases, dimension restrictions, truncated natural subtraction, integer/natural division, and coercions.
- **Assumptions:** section variables, implicit instances, unused/generalized parameters, `Fact P`, `[Nonempty α]`, and regularity/measurability/computability conditions that strengthen the original premises. An axiom-free `P → P` is not a proof of P.
- **Definitions and notation:** `Problem := True`, empty domains, constant-zero functions, custom `Prime`/`Continuous`, namespaces shadowing standard concepts, instances overriding standard operations, and the desired conclusion embedded in a structure field or typeclass.
- **Logical scope:** both directions of equivalences, existence and uniqueness, upper and lower bounds, optimality, all parameter families/dimensions, and every subproblem in a combined entry.
- **Proofs and disproofs:** a counterexample satisfying every premise and violating the conclusion can fully refute a universal conjecture. Finite samples or one positive instance cannot solve an infinitude or arbitrary-parameter problem. Independence, undecidability, or relative consistency require the metamathematical conclusion asked for by the original problem.
- **Conditional results:** theorem parameters, lemma premises, and unproved claims in external certificates cannot be counted as completed steps. A successful build establishes only the result under those assumptions.

Trace the main theorem through key lemmas and definitions. Trusted library theorems may be reused without reproving foundations, but verify their versions, mathematical content, and applicability to the problem's assumptions. For problematic dependencies, show the shortest chain: target → lemma/definition → unproved premise or mismatched object.

## Independent bridges

Create additional `.lean` files in the audit directory, importing actual target modules without editing submitted files. Define `IntendedStatement` from the original problem and provide `example : IntendedStatement := by ...` where possible. Include and check any proved equivalence transformations needed to connect the theorem.

Inspect `#check @Namespace.target` and declarations with sufficiently detailed printing; use `set_option pp.all true` when needed. Custom notation or pretty-printers may conceal the actual objects, so inspect expanded definitions and expressions exported through trusted tools.

Importing a submitted module also loads its extensions. Ordinary bridges help detect accidental mismatches but do not independently rule out malicious elaborators or kernel bypasses. For such concerns, use a trusted challenge and isolated export/comparison tools rather than repeating the submitter's `#print` logs.

A mechanically generated bridge is not automatically the correct specification. Explain each correspondence against the original mathematical source. When the mathematics exceeds what can be established or references are missing, identify which correspondence requires expert confirmation.

## Avoid common misjudgments

| Observation | Supported conclusion |
| --- | --- |
| Only the README's default build target succeeds | It is not yet established that the proof target was checked. |
| `theorem target (h : IntendedStatement) : IntendedStatement := h` | Circular assumption; being axiom-free does not solve the problem. |
| The target transitively depends on `sorryAx` | The target proof is incomplete, even with exit code 0. |
| An unrelated demonstration file contains `sorry`, but the target does not depend on it | Report repository quality separately from target completeness; do not automatically reject the target. |
| The problem requires infinitely many cases, but only one instance is proved | Partial coverage or a statement mismatch, not a complete solution. |
| A complete valid counterexample to a universal conjecture is constructed | Potentially a complete disproof; verify every premise and the negated conclusion. |
| The target directly/indirectly uses native-evaluation axioms | Record extended trust and check the mechanism for that version; this is not equivalent to a placeholder proof. |
| Printing or axiom-check commands fail and the log contains no `sorryAx` | Verification is incomplete; absence of the keyword does not establish absence of gaps. |
