# Step 3 — Hunt

Before launch, the parent sets each assigned unit to `in_progress` with a lowercase `owner` id, and creates `<out>/scratch/<agent>/` and `<out>/evidence/<agent>/`. Hunters read source and the provided context. They write only to their own scratch directory, and return one JSON result. They never edit the target, `coverage.json`, `findings.json`, or another agent's files.

One hunter may own a few closely related units in one component. Never combine unrelated boundaries just to save agents. Launch a whole wave in parallel.

## Hunter prompt (in this order)

1. **Role.** "You are an attacker hunting source-grounded security failures in the units below. Return exactly one JSON object matching the contract at the end."
2. `ARCHITECTURE.md`, verbatim.
3. The assigned units from `coverage.json`, plus every `context_refs` excerpt (entry-point blocks, invariant blocks, function records), verbatim.
4. Each selected lens or domain block, verbatim: `Core discipline`, the chosen classes, `Universal moves`, `Validation rules`. Never pass names alone.
5. Excluded blocks, each with its reason, and peer-owned unit ids not to duplicate.
6. The hunter method below.
7. Under `deep` passes 2+: the known-findings list (§ Passes).
8. Scratch and evidence paths, the sandbox rules from `SKILL.md`, the result contract below, and the `confirmed` and `needs_validation` field lists from `reporting.md`.

## Hunter method (include verbatim)

```text
## How to hunt

You are an attacker, not the code's author. When a path looks wrong, deepen it: chain
it, find more victims, lower the precondition cost, and escalate it to its worst
real variant. A crash may hide corruption; a DoS may hide theft. A separate skeptic
will try to refute you. Your job is to bring it a complete, concrete attack.

THINK WITH THREE TOOLS.
- Feynman (always first): before judging a function, explain in plain words what it
  does. Where your explanation turns vague or leans on jargon, an assumption is hiding.
- Socratic: for each line ask why it is there and what it assumes, two or three whys
  deep. "Because the name says so" is not an answer.
- Inversion: once you know what the code should do, ask how to make it not do that.
  What value slips past each check? What state are you in just before each write?

WORK FROM A CONCRETE INVARIANT.
1. Name the lower-trust actor and what it starts with.
2. Name the value, action, transition, or selector it controls.
3. Find the control that should reject, bind, isolate, limit, or revoke it.
4. Trace the exact path after that decision, following every call into the callee.
5. Stop at the smallest affected dummy record, wrong value, state delta, or effect.
6. State the source change and regression test that enforce the invariant.

READ AT DEPTH. Follow input through parsing, identity, authorization, normalization,
state, derived copies, and the final sink. Read sibling, legacy, batch, admin/force,
retry, callback, cancellation, migration, and error paths that reach the same effect,
and compare their controls for equivalence, not just presence. Compare what one
component guarantees with what the next one assumes.

TRY THE SAD PATHS. Absent, empty, zero, negative, max, over-limit, duplicate, mixed
encoding, stale, revoked, reordered, concurrent, partially migrated, failed
dependency, and rollback states, wherever the interface accepts them.

WEAPONIZE PATTERNS. When you find a root cause, search every path your units own for
the same mistake by name and by shape. Establish each instance's conditions on its
own. Return instances outside your units under "uncovered".

PROVE LOCALLY, MINIMALLY. Prefer an existing test, a minimal harness, or a small
fixture, run only inside the sandbox, with present dependencies and dummy data. If
the sandbox cannot be enforced, do not execute: keep the trace and name the blocker.

BOUND YOUR DEPTH. Trace only paths that reach your boundary or that it relies on.
When an invariant is settled either way, record the disposition and move on.

A candidate needs: a complete file:line trace from entry point to sink, the strongest
control on the path and why it fails, concrete values or a call sequence, and the
conditions. A path missing a step is not a candidate yet: keep tracing, or mark the
unit blocked with the exact missing step. A required fact that source and sandbox
cannot supply (deployment config, provider behavior, deployed parameter, real token
behavior) makes it needs_validation, with that fact named. Use one source-derived
fingerprint per root cause (pattern ^[A-Za-z0-9][A-Za-z0-9._:/@+-]*$, for example
Vault:withdraw:rounding-direction or api:POST-/users/:id:idor). Never put a line
number, agent, wave, or severity in it.
```

## Result contract

```json
{
  "units": [
    {
      "id": "U-014",
      "disposition": "covered|candidate|blocked",
      "checks": [{"agent": "h-07", "method": "source|local", "paths": ["src/Vault.sol"],
                  "result": "what the reading or test established",
                  "evidence": "evidence/h-07/withdraw-roundtrip.txt or null"}],
      "fingerprints": [],
      "unresolved": []
    }
  ],
  "candidates": [ { "proposed_verdict": "confirmed|needs_validation", "...": "fields per reporting.md" } ],
  "hardening": ["concrete non-finding note with file:line"],
  "uncovered": [{"surface": "", "boundary": "", "lens": "", "subsystem": "", "paths": [], "reason": ""}]
}
```

Every assigned unit appears exactly once. The parent copies the dispositions into `coverage.json` and moves expected evidence files from scratch into `evidence/<agent>/`. Only regular files are moved: never symlinks or directories, never by glob, and each file must be under its size bound. The parent re-runs the checker and seeds `uncovered` entries as new units. A malformed result leaves its units `planned` for reassignment.

## Passes (`deep`)

Pass 1 runs normally. Before each later pass, write `<out>/known-findings.md`: every fingerprint so far, grouped by component, each with its bug-class label and title. Give the hunters these instructions:

> These findings are not false positives and not off limits. Spend your **effort** on ground this list does not name. Still **report every bug you reach, listed or not**, in full: silence reads as "nobody found it". When you report a bug in a class listed for the same component, reuse that exact label, so the same bug keeps the same fingerprint.

Later passes rerun the same lenses over the same units, seeded with new reassignments from the critic. Stop early when a pass adds no new fingerprint.
