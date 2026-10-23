# Diff review (PRs, commits, branches)

Review a change for the security consequences it introduces, removes, or exposes. Classify by **risk, not size**: a two-line change can be critical. Adapted from Trail of Bits' differential-review (CC BY-SA 4.0).

## 1. Triage the change

Resolve the base and head refs, list the changed files, and size the codebase:

| Codebase | Strategy |
|---|---|
| Small (<20 files) | Read every changed file and its direct dependencies; run full `git blame` on changed regions. |
| Medium (20–200) | Changed files plus one hop of callers and callees; prioritize high-risk files. |
| Large (200+) | Critical paths only: auth, value movement, parsing, crypto, external calls. |

Rate each changed hunk:
- **High**: authentication, authorization, crypto, value transfer, external calls, deserialization or parsing, validation removed or weakened, permission or role changes, upgrade logic.
- **Medium**: business logic, state changes, new public APIs, configuration defaults.
- **Low**: comments, tests, UI text, logging.

Treat refactors as high until shown otherwise; refactors break invariants.

## 2. Analyze each high and medium hunk

- **Removed code first.** For every deleted or weakened check, run `git blame` and `git log -S` on it. Why was it added? Does the change re-open the bug it fixed?
- **New surface.** New entry points, parameters, roles, and storage go through the relevant `lenses-*.md` and `domains/*.md` blocks, as in Step 3.
- **Changed assumptions.** Compare the guarantees before and after for every caller of a changed function. A stricter return value or a new revert can break callers too.

## 3. Blast radius

For each high-risk changed function, count its direct and transitive callers (`rg`, the language server, or a call graph) and list the externally reachable entry points among them. Name the count; do not estimate it.

## 4. Test coverage of the change

List the changed lines and branches that no test exercises: check whether tests changed alongside the code, and read the existing tests for the changed functions. Untested high-risk changes raise priority. Never run the target's tests outside the `proof.md` rules.

## 5. Adversarial pass

For each high-risk hunk, write the attacker model (who can reach it and with what), the concrete attack the change enables, and how it compares with the pre-change baseline. Hand each concrete attack to Step 4 as a candidate.

## 6. Report

Write `<out>/DIFF-REVIEW.md`:
- the refs, the files reviewed, the strategy, and the explicit coverage limits;
- verified findings (from `findings.json`), each tied to a changed line and, for regressions, the commit that originally fixed it;
- removed security code and its history;
- blast radius per high-risk function;
- untested high-risk changes;
- the confidence level, and what was not reviewed.

Quality bar: every changed file is accounted for, `git blame` has been run on every removed check, blast radius is computed for every high-risk change, and attack scenarios are concrete.
