# Smart-Contract Fuzzing (fizz)

#### When to use this file

This file brings in the Pashov Audit Group `fizz` skill (vendored, MIT, at `pashov/fizz/`) in two separate roles. Pick the role from the request:

- **Campaign evidence** — inside a full audit, a hunter or Phase 3 verifier holding an `Invariants`, `Numerical gap`, `Math precision`, or `Asymmetry` candidate from `SMART-CONTRACTS.md` may run a bounded stateful fuzz campaign as its local observation. Nothing is written to the target.
- **Fuzz-suite mode** — the user explicitly asks to generate, sync, or convert a fuzz suite ("fizz", "build a fuzz harness", "invariant suite", or a post-audit request to turn findings into properties). This is a deliverable written into the target repository, and it runs outside the six-phase audit.

## Campaign evidence

Use this when a unit test cannot reach the violating state directly: the claim depends on a sequence of calls, many actors, or accumulated rounding. Prefer a plain Foundry test whenever one settles the claim.

1. Run everything inside the OS-enforced sandbox from `SKILL.md`, against a disposable copy of the target in your assigned `scratch/`. `forge`, `medusa`, or `echidna` must already be installed, and every dependency (`lib/forge-std`, `node_modules/`) must already be in the copy. Do not run `ensure_foundry.sh`, `forge install`, or any package install. A missing tool or dependency is a `needs_validation` blocker naming it.
2. Build the smallest harness that can express the claim, using the vendored templates in `pashov/fizz/templates/` (`Base.sol`, `Actor.sol`, `Properties.sol`, `utils/PropertiesAsserts.sol`, `utils/MockERC20.sol`, `handlers/Handlers.sol`) and the patterns in `pashov/fizz/references/handler-patterns.md` and `property-generation.md`. Deploy only the in-scope contracts with dummy actors and mock tokens, write handlers only for the entry points on the candidate's trace, and write exactly one property: the candidate's violated invariant, taken from its trace or its `x-ray/invariants.md` block.
3. Run one fuzzer with explicit low limits: `medusa fuzz --timeout 300` (set `workers` low in `medusa.json`) or `echidna . --contract FuzzTester --config echidna.yaml --timeout 300`. Never run both at once. Do not start the wrappers' browser log viewer.
4. A violation counts only after you rule out a harness bug. Replay the shrunk call sequence as a deterministic `test_repro_<property>` Foundry test, following fizz Step 11 "Generate Violation Repros", and rerun it. The repro output is the observed result; declare it and the campaign log in the promotion allowlist.
5. A clean campaign is coverage evidence for the unit, not proof the invariant holds. Record it as a `local` check with the achieved coverage and limits.

## Fuzz-suite mode

Read `pashov/fizz/SKILL.md` and follow its Steps 0–11 with these overrides; where they disagree, this list wins:

1. `{SKILL_PATH}` is `<skill-dir>/pashov/fizz`. Skip the banner. Resolve `{MODE}` and `{AGENT_MODEL}` as upstream does.
2. Before Step 1, confirm with the user that the suite will be written into the target at `test/fizz/` and `fizz_data/` (or paths they choose). This mode modifies the target repository, and the audit workflow never does.
3. Step 1: `ensure_foundry.sh` may create `foundry.toml` and run `forge install foundry-rs/forge-std`, which uses the network. Ask before running it. If the user declines, require `lib/forge-std` to be present and stop with that blocker otherwise.
4. Step 3: replace the x-ray Acquisition Protocol. If a previous audit run left `<output-dir>/x-ray/x-ray.md`, copy that `x-ray/` folder into `{PROJECT_ROOT}/x-ray/`, with the user's agreement, or point Step 3 at it in place. Otherwise produce one by following [SMART-CONTRACT-RECON.md](SMART-CONTRACT-RECON.md) in guidance mode. Do not clone or install skills from the network.
5. Step 9: when a `findings.json` from a previous audit exists, add every `confirmed` record's violated invariant as a SHOULD-HOLD property and every smart-contract `needs_validation` record's claim as an EXPLORATORY property, citing the fingerprint in the property's spec line. These become regression properties for the fix.
6. Steps 8, 10, and 11 compile and run target code. Run them only inside the `SKILL.md` sandbox. When the sandbox cannot be enforced, generate the suite, stop before running it, and give the user the exact commands (`medusa fuzz`, `echidna . --contract FuzzTester --config echidna.yaml`).
7. For follow-up work on an existing suite, read `pashov/fizz/skills/fizz-sync/SKILL.md` (source drift: quarantine stale properties, regenerate drifted handlers) or `pashov/fizz/skills/fizz-convert/SKILL.md` (turn `PROPERTIES.md` entries into Solidity assertions), with `{SKILL_PATH}` set the same way.

After a full audit of on-chain code finishes, offer fuzz-suite mode in one line when `REPORT.md` contains confirmed invariant-class findings or `On-chain=No` invariants that no unit could settle.
