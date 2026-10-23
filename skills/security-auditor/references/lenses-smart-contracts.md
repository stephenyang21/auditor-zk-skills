# Smart-Contract Lenses (EVM / Solidity)

#### When to use this file

Reach for this file when on-chain code holds or moves value, mints or burns supply, gates protocol parameters, or relays cross-chain messages: Solidity/Vyper contracts, libraries and upgradeable proxies, DeFi protocols (vaults, AMMs, lending, staking, perps, options, stablecoins), bridges and cross-chain handlers, token and NFT contracts, and the deploy scripts that set constructor arguments, ownership, and initial state. The core data flow is *lower-trust caller or external contract → entry point → guard → storage, accounting, or token movement*. For non-EVM chains, pair `lenses-other-chains.md` with the math, economic, invariant, and gap lenses here.

Use this file alongside `lenses-general.md`. Seed units from the entry-point map and the invariant catalog built in `context.md`. Off-chain keepers, relayers, frontends, and signers are ordinary boundaries and belong to the general and domain files. Split large targets per contract subsystem. Gap lenses span two or three subsystems on purpose.

## Core discipline (include in every agent prompt for this domain)

```
- You are an attacker, not a defender. When a path looks like a bug, deepen it: chain it, find more victims, lower the precondition cost, and escalate it to its worst exploitable variant (a DoS may hide fund theft). The independent verifier, not you, tries to refute it.
- Reason with three tools. Feynman first: before reasoning about any function, explain in plain words what it does; where the explanation goes fuzzy, an assumption is hiding. Socratic: for every line ask why it is there and what it assumes, two or three whys deep. Inversion: after you understand what the code should do, ask how to make it not do that — what value slips past each check, what state you are in just before each write.
- A candidate is a concrete, unguarded attack path: caller → function → state change → impact, with concrete values, call sequences, or state deltas taken from the actual code. A path without concrete values is not yet a candidate; keep tracing or record the unit as blocked with the missing step.
- When you find a root cause in one contract, search every contract owned by your assigned units for the same pattern by function name and by code shape (check `fn` and `_fn`). Report each instance's conditions independently. Return instances outside your units under `uncovered`.
- One root cause per candidate. Fingerprint it `Contract:function:bug-class` (kebab-case bug class, e.g. `Vault:withdraw:rounding-direction`); variants needing different fixes get separate fingerprints.
- Excluded, not findings: admin-only functions doing admin things; "admin can rug" without a concrete unprivileged amplifier; self-harm-only bugs; standard DeFi trade-offs (generic MEV, rounding dust, first-depositor with MINIMUM_LIQUIDITY); linter, gas, naming, NatSpec, missing events; centralization without an exploit path. Fee-on-transfer, rebasing, blacklisting, pausable, and void-return tokens ARE plausible for any contract accepting arbitrary tokens.
- Safe patterns, do not flag without a specific break: `unchecked` in 0.8+ with correct reasoning; explicit narrowing casts in 0.8+; MINIMUM_LIQUIDITY burn; SafeERC20; `nonReentrant` (flag only cross-contract or read-only reentrancy); two-step ownership transfer; consistent protocol-favoring rounding that neither compounds nor rounds to zero.
- The target tree is read-only. Write proof-of-concept tests only in your scratch copy. Run `forge test`, `hardhat test`, or an in-process EVM only inside the approved sandbox with dependencies already present (`lib/`, `node_modules/`). Never `forge install`, never fork a live chain through an RPC URL, never broadcast, never use a real key. A fact that only a live chain can supply (deployed parameter, actual token behavior, oracle configuration, chain-specific opcode or precompile behavior) is a needs_validation blocker.
```

## Single-lens attack classes

**Math precision**
Exploit integer arithmetic: rounding errors, precision loss, decimal mismatches, overflow, and scale mixing. Map every fixed-point system (WAD, RAY, BPS, token decimals, oracle decimals), every scale conversion, and every division in a value-moving function.
- Wrong rounding direction: deposits round shares down, withdrawals round assets down, debt rounds up, fees round up. A compoundable wrong direction is critical.
- Zero-rounding: feed 1 wei / 1 share into every formula; find fees that truncate to zero, rewards that vanish against a large `totalStaked`, share calculations that round away, ratios that truncate to zero and flip a formula.
- Division before multiplication, including across function boundaries where a truncated return value is later multiplied.
- Intermediate overflow in `a * b / c` and `(x << shift) / y` with flash-loan-scale user operands.
- Decimal mismatches: hardcoded `1e18` on 6-decimal tokens, `18 - decimals` underflow for >18-decimal tokens, variable oracle decimals in code assuming constants.
- Unchecked downcasts (uint256 → uint128/uint96/uint64), sign loss on `int24`/`uint24` round-trips, cast-wrap at saturation (`uint64((x << 64) / y)` as the ratio approaches 1).
- Share-price inflation by first-depositor donation.
- Strict `<` guards that exclude the single-occupant case; division by an edge value the configuration permits (`tickSpacing`, `config.value`, `decimals` of 0 or 1).
- Interest accrual that truncates to zero on tiny principals; `a - b` underflow at insolvent or edge positions; bitmask constants in pack/unpack helpers that clear or keep the wrong adjacent field.
Candidate evidence: the arithmetic walked with actual numbers.

**Permission model**
Map every role, modifier, inline `msg.sender` check, and grant path, then exploit the gaps.
- Inconsistent guards: for every storage variable written by two or more functions, find the writer with the weakest guard, including inherited functions, overrides, and `internal` helpers reachable from differently guarded `external` functions.
- Initialization: `initialize()` callable on the implementation; front-runnable initialization; missing `initializer`/`_disableInitializers`; `address(0)` role parameters that lock out admins.
- Escalation: a role that grants itself another role, grant/revoke chains reaching `grantRole` without the intended guard, upgrade paths bypassing a timelock, `renounceRole` leaving the system unrecoverable.
- Confused deputies: contract A calls B with A's privileges or token approvals on a caller-influenced path.
- Proxies and delegatecall: storage-layout collisions, admin-slot collisions, self-destructible or re-initializable implementations.
Candidate evidence: the missing guard, the parallel function that has it, and the unauthorized call sequence.

**Economic security**
Assume unlimited capital and flash loans. Exploit external dependencies, value flows, and incentives.
- Dependency failure: a stale or reverting oracle, token, or cross-contract call that permanently blocks withdrawals, liquidations, or claims; chained failures across a pipeline.
- Token misbehavior: fee-on-transfer, rebasing, blacklist, pausable, void-return, false-return; code that uses the requested amount instead of the received amount.
- Atomic extraction: deposit → manipulate → withdraw in one transaction; price-dependent operations missing slippage or deadline protection; fee formulas pushed to zero or to overflow; the cheapest griefing vector that blocks other users.
- ERC compliance: call each operation at the reported `max*` value; query vs execution mismatches (`maxDeposit` vs `mint`); hardcoded ERC-2612 permit against non-standard tokens such as DAI.
- Sentinel addresses (`address(0)`, `_ETH_ADDRESS_`) passed to `approve`/`transfer`/`balanceOf`; low-level calls that silently succeed without moving funds.
- Shared capacity: one accounting variable consuming a shared cap to block another.
- Legitimate features weaponized: liquidity added to make governance thresholds unreachable, intentional reverts that poison refund records, choosing which provider fulfills a pending request.
Candidate evidence: who profits, how much, at what cost, with numbers.

**Execution trace**
Trace from entry point to final state through encoding, storage, branching, external calls, and state transitions.
- Within one transaction: two or more attacker-controlled inputs whose assumed relationship is never enforced (claimed amount vs sent amount, requested vs delivered token); fees deducted from one variable while the original amount flows downstream; forwarding full `msg.value` after fee subtraction; `abi.encodePacked` decoded with `abi.decode`, field-order or assembly byte-count mismatches; sentinel values (`address(0)`, `0xEeee…`, `type(uint256).max`, empty bytes) that skip validation; unvalidated external return values; stale reads across an external call; coupled variables left half-updated by an early return.
- Across transactions: functions executed in protocol states they were not designed for; acting between the steps of request → wait → execute; corrupting individual packed fields across bridge or callback legs; a setter fired while an operation is in flight; a dependency swapped while its callback is pending; residual allowance when the approved amount exceeds the consumed amount.
Candidate evidence: the controlled inputs and values, the violated implicit assumption, and the trace from entry to impact.

**Invariants**
Map what must stay true, then find the path that violates it and extract value from the broken state. Start from `context/invariants.md`: every `enforced: no` block is a lead to prove or refute.
- Map: conservation laws (Σ balances = totalSupply, deposited − withdrawn = balance), state couplings (writers of X that forget Y), capacity constraints (every path that increases a capped value), and view-vs-write guarantees.
- Break: round-trips (`deposit(X) → withdraw(all)` returns more than X at 1 wei, max uint, first and last deposit); path divergence to the same outcome; non-commuting operation orders; degenerate boundaries (zero balance, max capacity, first or last participant, empty state); cap checks skipped on settlement, fee accrual, emergency, or admin paths; value stranded by emergency transitions lacking a paired cleanup; cache-then-mutate-then-use chains; timers reset through secondary call paths; global parameters mutated during multi-block operations; `queryX` vs `doX` math that omits a fee, penalty, or accrual; partial mints that break `supply ≤ backing`; price and balance read at different points of one liquidation.
Candidate evidence: the invariant, the minimal violating call sequence, and values showing it hold before and break after.

**Periphery**
Attack the code core contracts trust implicitly — libraries, helpers, encoders/decoders, provider wrappers, abstract bases — smallest contracts first.
- Inputs the core assumes the helper validates; zero, truncated, or mismatched-length return values every caller inherits; hidden storage, approval, or balance side effects; partial interface implementations that only work on the happy path.
- Assembly byte-width bugs (`mload` reads 32 bytes over narrower packed fields); balance checks at computed addresses used as existence proofs; loops whose worst-case gas bricks a critical function.
- Provider swaps racing pending requests; encoders that truncate long recipients (`bytes32` non-EVM address → `bytes20`); library getters reading the wrong storage context; `supportsInterface` dispatch defaulting when ERC165 is absent; hardcoded magic storage IDs that were never written.
- Oracles read in the same block or transaction as the dependent write (`slot0`, single-source spot); divergence "safety checks" whose threshold makes them dead code.
Candidate evidence: the helper's flawed behavior and the core caller that trusts it.

**First principles**
Ignore named vulnerability classes. For every state-changing function: extract each assumption (balance is current, price is fresh, A ran before B, this address is who we think, value fits the type, denominator is nonzero, mapping entry exists, flag was set, no concurrent modification); find who controls the inputs; construct a multi-transaction sequence that reaches the function with the assumption broken; trace the corrupted storage to extracted value. Focus on stale reads, desynchronized coupled variables, degenerate boundaries (zero, max, first call, last item, empty array, supply of one), function B mishandling the state function A leaves behind, and assumption chains where A trusts B to validate and B trusts A.
Candidate evidence: the assumption, how it was violated, and the trace to the extracted value.

**Asymmetry**
The bug is what is missing or different across two places that should match. Enumerate, with `file:line` for both sides: operation pairs (deposit/withdraw, mint/burn, lock/unlock, encode/decode, approve/pull, request/fulfill, open/close, stake/unstake); walk pairs (modify/settle, view/modify, simulate/execute, init/teardown); branch pairs (native vs ERC20, normal vs force/admin, first-time vs subsequent, empty vs non-empty); variant pairs (`X` vs `forceX`, single vs batch, sync vs async).
- Storage-write diff: same variable written in non-mirror directions, written by one side only, or read by one side only.
- Branch diff: validation, fee deduction, or downstream call shape present in one branch and missing in the other; one branch reverts on an edge where the other silently no-ops.
- Variable lifecycle: written but never read, read but never written, multiple writers with different validation.
- Admin variants of user flows missing slippage, deadline, or manipulation guards — can a user sandwich the admin transaction?
- Bad symmetry: a re-check that became over-restrictive and causes permanent DoS; comments claiming "safety check" whose claim is wrong.
Candidate evidence: the pair or branch compared and side-by-side citations of the asymmetric write, read, or check with concrete state values.

**Boundary enumeration**
Apply a fixed set of corner-case questions to every boundary until none is unexamined. Enumerate every external call site (`call`, `staticcall`, `delegatecall`, interface calls), payable function, sentinel-address branch, caller- or message-supplied token/contract address, decoded `bytes` input, and consumed external return value.
- Each external call: no code at receiver (`.call` returns `(true, "")`, `safeTransfer` to a codeless address succeeds silently); void-return, false-return, fee-on-transfer, rebasing, blacklist, pausable, zero-approval-reverting tokens; zero, empty, and max inputs; ignored or misread return data; sentinel placeholders flowing into `IERC20` ops; ERC165 dispatch fallbacks; `onERC721Received`/`onERC1155Received` re-entry before state finalizes; custody contracts making attacker-targeted external calls with their own authority; caller-supplied fee or bonus with no upper bound.
- Each payable function: where `msg.value > 0` ends up; whether `msg.value == 0` skips a fee or pulls tokens it should not; whether `msg.value != amount` is enforced in both directions; native branches forwarding raw `msg.value` while ERC20 branches deduct a fee.
- Each sentinel branch: does the native side pay via `call{value:}` or a silent `safeTransfer(SENTINEL, …)`; does the ERC20 side honor actual decimals, return value, and transfer semantics.
- Each `bytes`/`abi.decode` input: empty input, attacker-supplied length prefixes, `bytes20(longer)` truncation, packed-encoding ambiguity, field-order mismatches across files.
Candidate evidence: the boundary exercised, the assumption the caller makes, and the actual behavior under the corner-case input with its state delta.

**Token integration**
Assume every token the protocol accepts can be weird, unless the code allowlists specific tokens. For each token-touching path, check behavior under: reentrant transfer hooks (ERC777, ERC1363, ERC721/1155 receivers); missing or `false` return values; fee on transfer and transfer of less than the amount; balance changes outside transfers (rebasing, airdrops, interest); upgradeable tokens; flash-mintable supply; blocklists and pausing; approval race protections, and reverts on zero-value approval, on approval to the zero address, or on large approvals; reverts on zero-value transfers or transfers to the zero address; several addresses for one token; low (<6) or high (>18) decimals; `transferFrom` with `src == msg.sender` treated specially; non-string metadata and injection through the token name; no-op or non-standard `permit` (DAI, WETH fallback); native-currency representations (`0xEeee…`, `address(0)`, WETH). For tokens the protocol issues, check ERC20/721 conformity (return values, events, `decimals`, allowance semantics, `safeTransferFrom` receiver checks) and owner powers (mint, pause, blocklist, upgrade).
Candidate evidence: the token behavior, the code path that assumes standard behavior, and the state or balance delta it causes.

**Dimensional analysis**
Give every numeric value a dimension `[PRECISION]{UNIT}`: for example `D18{tok}`, `D6{USDC}`, `D18{share}`, `D27{UoA/tok}` for a price, `{s}` for time, `{1}` for a dimensionless ratio. Anchor these at sources (token `decimals`, oracle answers and their `decimals()`, constants such as `WAD`/`RAY`/`BPS`, storage fields), propagate them through every assignment, call boundary, and return, then check each operation:
- Assignment: the stored dimension matches the variable's (no `D36` product stored as `D18`).
- `+`, `-`, `min`, `max`, comparisons: both sides share unit and precision (`{tok}` + `{share}` is nonsense; `D6` + `D18` is off by 1e12).
- `*`, `/`: the result's dimension is the product or quotient, and the scaling factor is applied in the right direction (multiply vs divide by `10**decimals`).
- Function boundaries and return paths: every return path yields the same dimension, and callers interpret it the same way.
- External values: oracle prices, pool reserves, and cross-contract returns are interpreted with their actual units and decimals, not assumed ones.
A ratio of what? `{tok/tok}` is not `{share/tok}`. "All decimals are 18" still mixes units.
Candidate evidence: the annotated formula, showing where the dimensions disagree, with numbers for the resulting error.

## Gap attack classes

These classes hunt bugs that only appear when two or three single-lens classes are reasoned about together. If a candidate can be stated with one lens alone, it belongs to that lens's unit: return it under `uncovered` when no peer unit owns it, and otherwise drop it.

**Numerical gap**
Seams between math precision, invariants, and boundaries.
- Precision × invariant: invariants that hold under exact arithmetic but drift under integer rounding across N operations; two formulas that should agree but round in different directions; accumulators of truncated quantities compared against untruncated totals; Σ f(segment) where callers expect f(Σ segment); tree walkers that scale on visited paths only; approvals of `out + fee` consuming `out - fee`; rates updated mid-epoch.
- Boundary × precision: formulas correct in the middle of the domain that produce zero, max, or wrong magnitude at an edge (`fee = amount * rate / SCALE` at `amount = SCALE/rate - 1`); caps checked in a different scale from the stored value; `min`/`max` across mixed scales.
- Boundary × invariant: zero-amount or early-return fast paths that skip the invariant-preserving update.
- Three-way: an edge input whose precision loss disables an invariant's enforcement (a liquidation bonus that rounds to zero makes positions unliquidatable).
Candidate evidence: the trigger input, the intermediate values, and the violated property.

**Trust gap**
Seams between the permission model, economic security, and asymmetry.
- Access × economics: a correctly guarded role whose only action calls a sandwichable primitive (`onlyKeeper` rebalance with `amountOutMin = 0`).
- Economics × asymmetry: paired formulas that are structurally but not economically symmetric (deposit at spot, withdraw at TWAP).
- Access × asymmetry: admin setters whose write moment redirects in-flight value (fee recipient changed without checkpointing accrued fees); reward recipients changeable without past-accrual checkpoints.
- Three-way: a privileged parameter change combined with an asymmetric pricing primitive that an unprivileged actor front-runs or back-runs against a user class.
Candidate evidence: the actor, the authorization path relied on, the economic delta, and the asymmetric outcome. Admin-triggered harm still needs a named unprivileged amplifier (see Validation rules).

**Flow gap**
Seams between execution trace, periphery, and first principles.
- Execution × periphery: a trace that computes a value before a periphery call and uses it after (fee-on-transfer, rebasing, sync state); delta checks `balanceAfter - balanceBefore >= amount` that revert on intended fee-on-transfer flows; callbacks and hooks (V3 mint callback, settlement hooks, ERC721 receivers) that let the user re-enter before the origin finalizes.
- Periphery × first principles: individually safe external interactions that defeat a stated guarantee ("users always receive at least X") when chained into the system.
- Execution × first principles: multi-step flows (deposit-then-claim, mint-then-bridge, lock-then-redeem) whose every step succeeds but whose end state contradicts protocol intent; user-controlled identifiers keying refund or state maps with no occupancy check; helpers that mutate state another caller depends on; position updates that settle funding with mismatched old/new size and rate; phantom state written by contract X and trusted by contract Y; thresholds pumped past a gate so legitimate updates revert; cross-chain handlers iterating user-controlled lengths past destination block gas.
- Three-way: a control path that crosses a periphery boundary and ends in a state violating protocol intent (an oracle return selecting a branch that liquidates a healthy position).
Candidate evidence: the trace (internal step → periphery interaction → end state) and the protocol guarantee the end state contradicts.

## Universal moves (apply across the above)

- Draw four maps first, reusing `context/`: the permission map (roles, modifiers, inline sender checks, grant paths), the value map (every token and native-value movement in and out), the storage-writer map (every writer of every value-holding variable), and the external-call map (every periphery touchpoint and what the caller assumes it returns).
- Start at value exits — `transfer`, `call{value:}`, `_mint`, `_burn`, share and debt updates — and work backward through guards, accounting, and inputs. Start at every `enforced: no` invariant and every unguarded write site in `context/invariants.md`.
- Compare direct, batch, admin/force, emergency, callback, and cross-chain paths to the same effect. The strongest guard must apply after inputs are final and before every value movement.
- Prove with a local test, not a narrative: write the smallest Foundry or Hardhat test in your scratch copy that deploys the in-scope contracts with dummy actors and mock tokens (including a fee-on-transfer, rebasing, or void-return mock when the claim depends on token behavior), performs the attack sequence, and asserts the balance, share, or state delta. Stop at the first assertion that demonstrates the effect.

## Validation rules (apply before reporting ANY finding here)

Every candidate passes four sequential gates. A failed gate settles the verdict; later gates are not evaluated. The gates verify that the claimed attack fires end to end; they do not ask the verifier to defend the code.

1. **Attack execution.** Trace the claimed path from caller to harm and read every guard, modifier, check, and constraint on it. A specific guard that interrupts the exploit step before harm (quote and trace the exact line) → `rejected`. An interruption that is only speculative ("the deployer would set X", "the caller would notice") does not stop the gate.
2. **Reachability.** The vulnerable state must be reachable from deployment through normal usage or common token behaviors. Structurally impossible because an enforced invariant prevents it → `rejected`. Reachable only through a deployment parameter, configured token, or oracle setting that source does not fix → `needs_validation` naming that exact parameter and the owner-observed check. Reachable only through privileged actions outside normal operation → `rejected` unless Gate 3's amplifier rule applies.
3. **Trigger.** An unprivileged actor must execute the attack. If the harm requires an admin, owner, or other trusted role to act maliciously or against documented intent → `rejected`, unless the record names a concrete unprivileged amplifier: a **race** (an admin update mid-flow that a user exploits before it propagates), a **retroactive sweep** (an admin update rewrites a pending value already credited), an **asymmetric formula** (admin output chains into a formula an unprivileged actor profits from), or an **access gap** (missing guard, tautological check, or missing initializer guard — the access mechanism itself is the bug). With an amplifier, judge the unprivileged path.
4. **Impact.** Self-harm only → `rejected`. Dust-level with no compounding → `rejected`, recorded as hardening if useful. Material loss, theft, permanent or prolonged freeze of funds, insolvency, broken supply or peg, or unauthorized control of an identifiable victim or the protocol → eligible for `confirmed`.

Then apply the evidence bar:

5. `confirmed` requires all four gates plus a bounded local observed result: a sandboxed test in a scratch copy, run with only locally present dependencies, whose output shows the balance, share, state, or revert effect. If the sandbox cannot be enforced, the toolchain is absent, or dependencies are missing, keep the source trace and record `needs_validation` with that exact blocker and the test you would run. `proof.md` § Stateful fuzzing adds a bounded invariant campaign as an alternative local observation for conservation and invariant candidates.
6. Cross-contract echo: when the same root cause is confirmed in one contract, each identical instance in another contract is validated on its own trace and receives its own fingerprint only when its fix differs.
7. Confidence: start at high. Lower to medium for each of: a specific but achievable required state, bounded non-compounding impact, or a trace that needed a mock for external behavior. Lower to low when two apply. A partial attack path is not confidence-reduced — it is not confirmed.
8. Severity calibration for this domain, never exceeding the demonstrated effect:
   - **critical** — an unprivileged actor steals or permanently freezes material user or protocol funds, mints unbacked supply, or takes ownership, upgrade, or mint authority, with no unusual preconditions.
   - **high** — the same consequences under specific but achievable state or token behavior; protocol insolvency; permanent DoS of withdrawals, redemptions, or liquidations; full bypass of a guard on a value-moving function.
   - **medium** — bounded or conditional loss, griefing that costs the attacker less than the victim, temporary freezes, broken ERC guarantees that integrators rely on, or an admin action exploitable through a named unprivileged amplifier.
   - **low** — minor non-compounding value leakage or a view/write mismatch with no on-chain consumer.
   - **informational** — a confirmed observation useful mainly as a prerequisite inside a larger finding.
9. The remediation names the invariant the contract must enforce, the narrowest change at the last trusted decision point (a guard, a received-amount measurement, a rounding direction, a checkpoint, an initializer lock), and the regression test that fails before and passes after.
