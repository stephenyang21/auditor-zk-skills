# Step 2 — Plan coverage

`coverage.json` is the coverage claim. An agent count, an architecture summary, or a sentence like "auth reviewed" is not coverage. A unit is closed only by a check that names the paths read and what they established. The parent is the only writer of this file.

## Unit format

```json
{
  "version": 1,
  "units": [
    {
      "id": "U-014",
      "surface": "src/Vault.sol#Vault.withdraw(uint256,address,address)",
      "boundary": "context/invariants.md#I-17",
      "lens": "lenses-smart-contracts.md#Invariants",
      "subsystem": "src/vault",
      "lifecycle": "normal",
      "paths": ["src/Vault.sol", "src/lib/ShareMath.sol"],
      "blocks": ["lenses-smart-contracts.md#Core discipline", "lenses-smart-contracts.md#Invariants",
                 "lenses-smart-contracts.md#Universal moves", "lenses-smart-contracts.md#Validation rules"],
      "context_refs": ["context/invariants.md#I-17", "context/entry-points.md#Vault.withdraw"],
      "priority": 1,
      "wave": 1,
      "status": "planned",
      "owner": null,
      "checks": [],
      "fingerprints": [],
      "unresolved": [],
      "reason": null
    }
  ]
}
```

- **surface**: one entry point, or a tight group of them in one component.
- **boundary**: the control that should hold. That is a guard, a check function, a policy, or an invariant/assumption ID. Use `unguarded:<path>` when there is none.
- **lens**: `<file>#<class name>`, with the class name exactly as written in bold or as a heading in that file.
- **lifecycle**: optional. Use it under `deep`, or when a mode matters (init, normal, paused/emergency, upgrade, migration, recovery).
- **blocks**: everything the hunter will receive verbatim. For a domain or lens file, that is its `Core discipline`, the chosen classes, its `Universal moves`, and its `Validation rules`.

## States

| status | owner | checks | fingerprints | unresolved | reason |
|---|---|---|---|---|---|
| `planned` | — | — | — | — | — |
| `in_progress` | agent id | — | — | — | — |
| `covered` | agent id | ≥1 | — | — | — |
| `candidate` | agent id | ≥1 | ≥1 | optional | — |
| `blocked` | agent id | ≥1 (partial) | — | ≥1 blocking fact | — |
| `deferred` / `out_of_scope` / `not_applicable` | — | — | — | — | required |

A check is `{"agent", "method": "source"|"local", "paths": [...], "result", "evidence"}`. A `local` check's `evidence` is a file under `<out>/evidence/<agent>/`. A `source` check's `evidence` is `null`.

`scripts/check_coverage.py` enforces this table, unique IDs, unique surface/boundary/lens/lifecycle combinations, repository-relative paths, and fingerprint syntax. Pass `--skill-dir <skill-dir>` so lens references are checked too, and `--final` in Step 6.

## Seeding

Seed one unit per material **surface × boundary × lens**:

| Profile | Granularity |
|---|---|
| `quick` | subsystem-level surfaces; one unit per selected lens per subsystem |
| `standard` | entry-point groups per component; gap lenses once per pair of components that share state or value |
| `deep` | one surface per entry point; add lifecycle modes; give every prior covered unit a second pass |

Mandatory units: every `enforced: no` invariant, every `nothing found` assumption, every tool lead, every git signal (removed guard, reverted fix), and every permissionless value- or privilege-moving entry point. For a **scoped** run, seed only in-scope surfaces and record discovered out-of-scope surfaces as `out_of_scope`, never as `covered`.

## Ranking

Assign `priority` (1 = first):

1. Unauthenticated or permissionless surfaces before authenticated ones.
2. Boundaries protecting the most value: credentials, cross-tenant data, code execution, user funds, mint/upgrade/ownership authority, release signing.
3. `enforced: no`, `nothing found`, git signals, changed source, and prior gaps before re-passes.
4. Lenses that historically yield confirmed findings for this system class before speculative ones.

Break ties lexicographically by `id`, so the order stays deterministic.

## Prior runs

Read every earlier `coverage.json` and `findings.json` for this repository before seeding.

- **Prior `confirmed`, relevant source unchanged:** carry the record (same fingerprint) into Step 4 for re-verification. Tell hunters to skip only that root cause.
- **Prior `confirmed`, source changed:** seed a revalidation unit. Hunters do *not* skip it.
- **Prior `needs_validation`, `blocked`, `deferred`, `out_of_scope`, or changed-source unit:** current work. Never suppress it.
- **Prior `rejected`:** suppresses only that exact unchanged claim, not its unit.
- **Prior `quick` or scoped run:** contributes only its recorded evidence, never an implied "the rest is fine".

## Coverage critic (after every wave)

One fresh `research` agent receives `ARCHITECTURE.md`, the full `coverage.json`, the candidate fingerprints, and the `context/` lists. It reads source but writes nothing. It returns:

```json
{"missing_units": [{"surface": "", "boundary": "", "lens": "", "subsystem": "", "paths": [], "reason": ""}],
 "reassign_ids": [{"id": "", "reason": "closed without reading the weaker parallel path at file:line"}],
 "stop": false}
```

The critic looks for: unmapped entry points, unchecked parallel paths (batch, admin/force, retry, migration, callback), missing lifecycle modes, `enforced: no` / `nothing found` items with no unit, exclusions without a source-backed reason, and units closed on paths that do not reach their boundary. `stop` is true only when both lists are empty. Seed the missing units, archive reassigned units' evidence under an `attempts` list, reset them to `planned` with a new owner, and run another wave. Under `quick`, record accepted gaps as `deferred` instead of launching another wave.

## Budget

When a budget is set, count every agent launch. Before each hunter wave, reserve one post-wave critic, a final clean critic (`standard`/`deep`), and about 1 verifier per expected candidate (`quick`) or 1.5 (`standard`/`deep`); when in doubt, reserve 30% of what remains. Shrink the wave to fit, in priority order. Units that do not fit become `deferred` with reason `budget`. If candidates outnumber the verifier reserve, stop hunting, verify in fingerprint order, mark the run `incomplete`, and list every unverified fingerprint. Never exceed a user's budget silently.
