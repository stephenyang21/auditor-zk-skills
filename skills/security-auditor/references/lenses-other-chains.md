# Non-EVM Chain Lenses

#### When to use this file

Reach for this file when on-chain code runs outside the EVM: Solana programs (Rust/Anchor), Cosmos SDK modules, CosmWasm contracts and IBC apps, Substrate pallets, Cairo/Starknet contracts and L1↔L2 bridges, TON contracts (FunC/Tact/Tolk), and Algorand apps and smart signatures (TEAL/PyTeal). Each section lists the platform's characteristic failures. Pair it with the economic, math, invariant, asymmetry, and gap lenses in `lenses-smart-contracts.md`, which apply on every chain. Adapted from Trail of Bits' Building Secure Contracts scanners (CC BY-SA 4.0).

## Core discipline (include in every hunter prompt that uses this file)

```
- Identify the platform from source markers before choosing a section: Anchor/`solana_program` (Solana), `x/<module>` keepers and `sdk.Msg` (Cosmos), `#[pallet]` (Substrate), `#[starknet::contract]`/`felt252` (Cairo), `.fc`/`.tact`/`.tolk` (TON), TEAL/PyTeal/Beaker (Algorand).
- The runtime's account, message, and origin model is the trust boundary. Every account, message sender, origin, counterparty chain, and cross-domain message is attacker-supplied until code proves otherwise.
- Use only installed analyzers (Trail of Bits Solana lints, Tealer, Caracal, cargo clippy). Treat every hit as a lead to trace, never as a finding.
- Local proof means program tests (Anchor/`solana-program-test`, `simapp`, pallet mock runtime, Starknet Foundry, Sandbox/Blueprint, Algorand localnet in a sandbox with no external network). A behavior that only a live cluster or mainnet configuration can show is a needs_validation blocker.
```

## Solana

**Account validation**
- Missing **signer** checks on authority operations (`is_signer`, Anchor `Signer<'info>`).
- Missing **owner** checks before deserializing an account (`account.owner == program_id`, Anchor `Account<'info, T>`). Type cosplay: an account of another type with a compatible layout and no discriminator check.
- PDA validation that uses `create_program_address` with a caller-supplied bump instead of the canonical bump from `find_program_address`; seeds that two users or two purposes can collide on.
- Duplicate mutable accounts passed twice; `remaining_accounts` used without validation; account close without zeroing data and the discriminator (revival).

**Arbitrary CPI**
- `invoke`/`invoke_signed` where the program ID comes from an account the caller supplies without checking it against the expected program (fake token program, fake oracle). Anchor `Program<'info, T>` enforces this, but `UncheckedAccount` does not.
- Signer seeds forwarded into a CPI to an untrusted program.

**Sysvars and instruction introspection**
- Sysvar accounts accepted without address checks (spoofed `Instructions`, `Clock`, `Rent`), especially on older runtimes or with raw `AccountInfo`.
- Instruction introspection with absolute indexes (`load_instruction_at`) instead of indexes relative to the current one, so one verification instruction is reused for several actions.

**Arithmetic and state**
- Unchecked `+ - *` on `u64` amounts (Rust release builds wrap), `as` casts that truncate, and rounding direction in share math.
- Missing rent-exemption checks or lamport accounting after transfers; reinitialization of initialized accounts.

## Cosmos SDK, CosmWasm, and IBC

**Determinism and liveness (chain halt)**
- Non-determinism in state machine code: map iteration order, floating point, goroutines, `time.Now`, random sources, OS or network access, non-deterministic JSON encoding (including in IBC acknowledgements), and CosmWasm queries that return non-deterministic data.
- Slow or panicking `BeginBlock`/`EndBlock`/`PreBlocker` (unbounded loops over user-growable state, unchecked map or slice access, division by zero). A panic or timeout there halts the chain.
- Unbounded pagination and queries that let any user grow work per block.

**Messages and signers**
- Signer annotation mismatch: the `cosmos.msg.v1.signer` field is not the account whose authority the handler uses.
- Validation missing in the `MsgServer` handler now that `ValidateBasic` is deprecated or optional; unregistered handlers (legacy); missing error handling that commits partial state.
- AnteHandler gaps: fee, signature, or sequence checks skipped for some message types, nested `authz`/ICA messages that bypass decorators, and unordered transactions that can be replayed.

**State and bookkeeping**
- Broken bookkeeping: module accounts or escrow balances that can diverge from internal accounting, including through direct `bank` sends to module accounts, IBC transfers, or slashing.
- Bank keeper misuse (sending to blocked addresses, `SendCoins` without blocklist checks, minting permissions wider than needed); storage key prefix collisions; module initialization order; events overridden or suppressed (CacheContext event leaks); arithmetic overflow or `sdk.Dec` precision loss; governance proposal ordering and message priority; deprecated modules still wired in.
- Circuit breaker or authz bypasses; consensus validation gaps; Merkle and proof verification that accepts malformed proofs.

**IBC and CosmWasm**
- Untrusted counterparty chains and clients; `LookupModuleByPort`/`ByChannel` used for authorization; missing close-channel validation; wrong timeout or acknowledgement handling (refund twice, or never); wrong channel ordering; unpermissioned channel opening.
- Denom or voucher confusion (native vs IBC denom traces), ICS-20 v2 multi-token partial receives, inverted escrow/mint logic in packet-forward middleware, missing rate limits.
- ICA host allow-all message configuration, missing or misconfigured ICA authentication modules.
- Reentrancy through CosmWasm submessages or IBC callbacks that violates checks-effects-interactions. This has produced infinite-mint bugs. Also: wrapping `Uint256`/`Uint512` math, and Ethermint/EVM-module interactions (`evm` precompiles reaching bank state).

## Substrate

- **Bad origin**: `ensure_signed` on privileged calls that need `ensure_root` or a custom `AdminOrigin`/`ForceOrigin`, or origins wired too broadly in the runtime config.
- **Panics are DoS**: `unwrap()`, `expect()`, unchecked indexing, or division in dispatchables or hooks stall block production. All user input must go through `ensure!`.
- **Arithmetic**: `+ - * /` wrap in release builds; use `checked_*`/`saturating_*` for balances, rewards, and fees.
- **Weights and fees**: fixed weights for variable-cost work, unbenchmarked extrinsics, and unbounded input lengths enable spam and block stuffing.
- **Verify first, write last**: on pre-0.9.25 FRAME, storage writes made before a failed check persist; elsewhere, check for manual storage changes outside `#[transactional]` contexts.
- **Unsigned transactions**: `ValidateUnsigned` without replay protection, parameter validation, or source authentication.
- **Bad randomness**: `pallet_randomness_collective_flip` or `random_seed()` used where collusion matters; use BABE randomness with a subject.

## Cairo and Starknet

- **`felt252` arithmetic** wraps silently modulo the field prime; use `u128`/`u256` for amounts and comparisons.
- **L1 handlers** that do not check `from_address`, so any L1 contract can drive them.
- **L1→L2 address conversion** that does not reject values ≥ the Starknet field prime; **L1→L2 message failure** with no cancellation path, which strands funds; **overconstrained L1↔L2 coupling** that blocks progress or strands value.
- **Signature replay**: no nonce, or a domain separator missing chain ID or contract address; account abstraction `__validate__`/`__execute__` mismatches.
- Storage address collisions from `sn_keccak` variable names in upgrades; unchecked `replace_class_syscall` upgrade paths.

## TON

- **Integer as boolean**: FunC's `true` is `-1`. Positive integers used as flags, or bitwise `~` on `1`, give wrong branches.
- **Fake Jetton**: a `transfer_notification` handler that does not verify the sender is the protocol's own Jetton wallet for that master, so anyone can mint credit.
- **Gas and forward amounts**: forwarding TON or sending messages without reserving gas for the rest of execution, bounce handling that does not restore state, and send-mode flags that drain the contract (`mode 128` / `+32`).
- Asynchronous message chains: state assumed final while a reply is still in flight; replay of external messages without `seqno`/`valid_until` checks.

## Algorand

- **Rekeying**: smart signatures or apps that never check `RekeyTo == ZeroAddress`.
- **Close-out drains**: unchecked `CloseRemainderTo` (account) or `AssetCloseTo` (asset holding).
- **Fees**: smart signatures that do not bound `Fee` (the account can be drained through fees); inner transactions that do not set the fee to 0.
- **Group transactions**: no `Global.group_size()` check, or absolute group indexes that let unrelated transactions satisfy a check.
- **Replay**: no lease and no round bounds on time-based logic.
- **Access control**: `UpdateApplication`/`DeleteApplication` and privileged methods not restricted to the creator or admin.
- **Asset IDs** not validated; push transfers that fail on accounts that have not opted in (DoS); `ClearState` programs that cannot reject, leaving local state inconsistent.

## Universal moves (apply across the above)

- List every instruction, message, extrinsic, or handler with its origin or signer requirement and the accounts or state it touches. That table is the hunt plan.
- For each externally supplied account, address, program ID, counterparty, or message sender, find the line that authenticates it. No line means a candidate.
- For each panic, unbounded loop, or per-block hook, ask who controls its size or its trigger; a liveness failure on a chain is an outage for every user.
- For each cross-domain message (CPI, IBC, L1↔L2, TON message, inner transaction), follow both the success and the failure/timeout/bounce path to the final balances.

## Validation rules (apply before reporting ANY finding here)

1. Name the platform, the attacker-supplied account, message, origin, or counterparty, the missing check, and the resulting state, balance, or liveness effect.
2. Reproduce with a local program or mock-runtime test whenever the toolchain is present. A runtime-version-dependent behavior (sysvar checks, FRAME transactional semantics, IBC version) needs that version confirmed from the manifests, or else it is needs_validation.
3. A chain halt or block-production DoS is high or critical only when an unprivileged actor can trigger it; validator-only or governance-only triggers need a named unprivileged amplifier (see `lenses-smart-contracts.md` Gate 3).
4. Severity follows `lenses-smart-contracts.md` § Validation rules; add chain halt to the high/critical consequences.
