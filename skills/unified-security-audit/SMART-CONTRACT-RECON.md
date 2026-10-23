# Smart-Contract Reconnaissance (x-ray)

#### When to use this file

Use this file in Phase 1 whenever Agent 1a or 1c reports in-scope on-chain code (`.sol`/`.vy` sources, `foundry.toml`, `hardhat.config.*`, deploy scripts). It adds one focused reconnaissance agent, **Agent 1e**, built from the Pashov Audit Group `x-ray` skill (vendored, MIT, at `pashov/x-ray/`), and it defines how smart-contract coverage units are seeded. It runs after the four baseline agents and before the coverage ledger is written. Repeat the `SKILL.md` budget gate before launching Agent 1e, like any focused reconnaissance agent.

In guidance mode, a user who asks only for an x-ray, readiness report, or pre-audit report gets the x-ray deliverable alone: follow the steps below with `<output-dir>` replaced by a user-confirmed directory outside the target (default `~/security-audit-skill/<repo-name>/x-ray-<N>`), and skip ledger seeding.

## How the upstream x-ray runs here

Read `pashov/x-ray/SKILL.md` and its `references/threats.md` and `references/templates.md`. Follow its Steps 1–3 with these overrides; where this list and the upstream file disagree, this list wins:

1. `$SKILL_DIR` is `<skill-dir>/pashov/x-ray`. Every upstream `x-ray/` output path becomes `<output-dir>/x-ray/`. Nothing is written inside the target.
2. Skip the banner, the remote `VERSION` fetch, and the mandatory TodoWrite tracking.
3. Step 1: the parent runs `enumerate.sh`, `entry_points.py`, and `analyze_git_security.py --json <output-dir>/x-ray/git-security-analysis.json` itself. These are vendored skill scripts that only read the target and its Git history, so they are not target-controlled execution. Run Python with `-I`.
4. Step 1 coverage (`forge coverage` / `npx hardhat coverage`) compiles and runs target code. Run it only inside the OS-enforced sandbox from `SKILL.md`, against a disposable scratch copy, with dependencies already present. Otherwise record `coverage metrics unavailable — sandbox or dependencies not available` and continue; test existence still comes from enumeration.
5. Step 2 (source reads, entry-point classification, flow paths, backwards-compatibility detection, centralization and pause analysis, protocol classification, invariant synthesis) is Agent 1e's work, below. Upstream "Path B" fact-extraction subagents become additional focused `research` agents only after the budget gate funds each one.
6. Step 3: the parent writes `x-ray.md`, `entry-points.md`, `invariants.md`, and `architecture.json` under `<output-dir>/x-ray/` from Agent 1e's result, then runs `generate_svg.py` on that JSON. Delete `git-security-analysis.json` after Step 3 as upstream does.
7. Keep the upstream verification gates: the scan-verified entry-point list wins over summaries, every inferred invariant cites its Δ-pair, lifted guard plus all write sites, edge, temporal predicate, or NatSpec line, and anything unverifiable is dropped or written as "could not determine".

**Agent 1e: Smart-contract x-ray** (subagent_type: `research`)

```text
Read the on-chain sources at <target> (source dir <src-dir>). Do not use network access,
do not compile, and do not run target code. You are given the enumerate.sh output, the
entry_points.py output, git-security-analysis.json, and the x-ray reference files
threats.md and templates.md. Perform x-ray Step 2 exactly as pashov/x-ray/SKILL.md
defines it (2, 2b, 2b-flow, 2c, 2d, 2e, 2f, 2g), including its verification gates, and
return, with repository-relative file:line references:
1. Per-contract facts: type, inheritance, roles/modifiers, value-holding state, external
   calls, fund flows, delta writes, guard predicates, one-shot transitions.
2. Every entry point classified permissionless / role-gated / admin-only / initializer,
   with caller, parameter trust, call chain, state modified, value flow, reentrancy guard.
3. Protocol flow paths as arrow chains.
4. Protocol type (and hybrid), phase, external-call classification, and the matching
   threat profile, temporal threats, and composability threats from threats.md.
5. The invariant catalog: G-N enforced guards; I-N single-contract, X-N cross-contract,
   and E-N economic invariants, each with On-chain=Yes/No and its derivation.
6. Centralization and pause coverage per privileged role; backwards-compatibility code.
Return facts only; mark every unverified claim "could not confirm".
```

## Architecture summary additions

Add to `architecture.md`, inside its 1,000-word cap: the protocol type and phase, the permissionless entry-point count and the highest-value ones, privileged roles with which actions are instant versus timelocked, the external dependencies (tokens accepted, oracles, bridges, hooks), and the count of `On-chain=No` invariants. Point to `<output-dir>/x-ray/` for the full catalogs rather than copying them.

## Seeding smart-contract coverage units

Select `SMART-CONTRACTS.md` blocks from the boundaries recon found, as `RECONNAISSANCE.md` requires, and seed units with these canonical references:

- `surface` — one entry point or a closely related entry-point group from the scan-verified list, e.g. `src/Vault.sol#Vault.withdraw(uint256,address,address)`. Group permissionless value-moving functions per contract; give each initializer, upgrade, and role-grant path its own surface.
- `boundary` — the guard that should hold: a modifier, inline sender check, or invariant, e.g. `src/Vault.sol#onlyOwner` or `x-ray/invariants.md#I-17`. Use `permissionless` plus the contract path for unguarded entry points.
- `subsystem` — the contract or package directory.
- `attack_class` — `SMART-CONTRACTS.md#<class name>`, e.g. `SMART-CONTRACTS.md#Math precision`.

Seed every applicable single-lens class per subsystem. Seed each gap class (`Numerical gap`, `Trust gap`, `Flow gap`) once per pair of subsystems that share value or state; for a single-subsystem target, seed each once. Under the `quick` profile, use the coarse all-in-scope subsystem identity from `RECONNAISSANCE.md` with all twelve classes. Under `deep`, split surfaces per entry point and add lifecycle modes for initialization, normal operation, paused or emergency mode, and upgrade.

Every `On-chain=No` invariant and every unguarded write site in `invariants.md` must be the `boundary` of at least one unit, normally an `Invariants` or `Permission model` unit. A coverage critic treats an unmapped one as a missing unit.

Rank smart-contract units with the `HUNTING.md` priority order, reading "lowest-trust entry surfaces" as permissionless value-moving entry points and "most valuable resources" as custody of user funds, mint authority, ownership, and upgrade authority.

## Hunter context

For units that select `SMART-CONTRACTS.md` blocks, the parent appends to part 3 of the hunter prompt the `entry-points.md` blocks for the assigned surfaces and the `invariants.md` blocks whose IDs appear in the assigned boundaries or whose locations fall in the assigned starting paths, copied verbatim. Record the copied IDs in a parent bookkeeping field on each unit so the coverage critic can check them.
