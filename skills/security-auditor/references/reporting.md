# Step 6 — Report

`findings.json` is the source of truth; prose is derived from it and never changes a verdict, severity, blocker, or demonstrated impact. Validate with `node <skill-dir>/scripts/validate-findings.cjs <out>/findings.json` (the schema is `scripts/report-schema.json`).

## `findings.json` fields

A top-level array of records, sorted lexicographically by `fingerprint` with each fingerprint appearing once (the validator rejects any other order). Every record has `verdict`, `fingerprint`, `title`, `description`, `trace`, and `evidence`.

- `trace`: ordered `{kind, file, line, scope, description}` entries. `kind` is `entrypoint` for the first, `sink` for the last, and `propagation` in between. Paths are repository-relative and lines are positive integers.
- `evidence`: `{file, line, description}` entries for the controls and facts the verdict relies on.

| verdict | Additional required fields |
|---|---|
| `confirmed` | `root_cause`, `intended_behavior`, `conditions` (`{kind, description}`, where kind is one of `authentication_level`, `authorization_role`, `user_interaction`, `system_configuration`, `network_routing`, `environmental_dependency`, `data_state`, `timing_dependency`, `third_party_dependency`), `execution` (`attacker_perspective`, `payloads`, `instructions`, `observed_result`), `remediation` (`strategy`, optional `code_changes[{file_name, fixed_code}]`), `severity` (`likelihood{score,reason}`, `impact{score,reason}`, `overall_severity`), `confidence{score,reason}` |
| `needs_validation` | `claimed_root_cause`, `blockers` (the exact missing facts), `validation_plan` (`local` and/or `deployment`, an owner-observed check, never a live probe by you). No severity. |
| `rejected` | `claimed_root_cause`, `reason` (the brocard or gate that failed, with the line that disproves the claim) |

Severity scores use `informational|low|medium|high|critical`; confidence uses `low|medium|high`. The fingerprint stays the same for the same root cause across verdicts and runs.

## Finding language

Owners must be able to act on every sentence. Write `title` and `description` in Simplified Technical English:

1. One sentence, one idea. A description is one sentence of 25 words or fewer.
2. Active voice; the actor comes first. "An unprivileged caller withdraws more shares than it deposited."
3. Simple present tense: the code does this today.
4. No `-ing` clauses, no metaphor, idiom, or slang; keep the articles (`the`, `a`).
5. At most three nouns in a row; use one word for one thing throughout.
6. Say what happens, not how bad it is; severity words belong only in the severity field.
7. Cause before effect, in sentence order.
8. A title is one clause of 12 words or fewer, in present tense, naming the actor and the effect.

Identifiers, code, diffs, bug-class labels, and fingerprints are written exactly as they appear in source.

## `REPORT.md`

1. **Run statement**: profile, scope, source ref, budget (planned vs spent), prior runs used, and the statement that execution was source-review plus sandboxed local checks only. A `quick`, scoped, budget-limited, or incomplete run says plainly that it is partial, and lists any unverified fingerprints.
2. **Posture**: one short paragraph.
3. **Confirmed findings table**: severity, title, boundary crossed, and the one-line observed result.
4. **Each confirmed finding**: title line; location (`file:line` of the root cause); description; lower-trust actor; conditions; minimal reproduction and observed result; impact and priority rationale; the fix as a diff when it is small, plus the regression test; the variant note from Step 5.
5. **Needs validation table**: title, trace, exact blocker, local next step, and owner-observed check. No severity.
6. **Worth manual review**: records revived by the revival review (`verification.md` § Revival) that a fresh skeptic could not settle. Each one gets a title, its trace, the original rejection reason, and the revival argument. These are not findings and carry no severity.
7. **Hardening notes** and positive patterns, kept separate from findings.
8. **Coverage**: unit counts per status, important exclusions and deferrals, the final critic result, and the statement that no single run exhausts a target.

A clean run may have zero confirmed findings. Say so, with the coverage limits, and do not invent low-severity findings to fill the report.

## `FINDINGS.md`

For each confirmed record of medium severity or above, give the full trace and evidence, the dummy actor and the affected dummy resource, the exact reproduction (payloads, instructions, observed output), the invariant it proves, the conditions, and the remediation with its regression test.

## `NEEDS-VALIDATION.md`

For each `needs_validation` record: the trace, the verified evidence, the exact blocker, the affected boundary, and the local and owner-observed plans. These are prioritized leads, not vulnerabilities.

## Readiness report (map-only mode)

From Step 1 outputs, write `<out>/READINESS.md`, under 500 lines:

1. **Overview**: the system class, components in scope with nSLOC, how the parts fit together, and backward-compatibility code.
2. **Threat and trust model**: actors and adversaries, trust boundaries and what each one actually protects, key attack surfaces (each linked to the invariant or assumption IDs it touches), centralization (instant vs timelocked privileged actions), and dependency risks.
3. **Invariants**: counts by type and the `enforced: no` items, with a pointer to `context/invariants.md`.
4. **Documentation quality**, and claims tagged `(per spec)` vs code-verified.
5. **Tests**: what exists (unit, fuzz, invariant, formal, fork), from file enumeration, never inferred from a failed run; then the gaps, ranked by audit impact.
6. **Git history**: contributors, hotspots, security-relevant commits, removed guards, late changes, forked dependencies, and tech-debt markers. State the analyzed branch and commit.
7. **Verdict**: the lowest of three tiers, Tests, Docs, and Access control, each rated EXPOSED, FRAGILE, ADEQUATE, HARDENED, or FORTIFIED. Drop one tier if security-critical paths carry TODOs. Give 3–5 measurable structural facts, with no security claims or speculation.
