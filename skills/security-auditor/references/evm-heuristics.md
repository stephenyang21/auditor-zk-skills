# EVM Heuristics and Protocol Primers

#### When to use this file

Use it with `lenses-smart-contracts.md` on Solidity/Vyper targets. These are **triggers, not a checklist**: match each trigger against the code in front of you, and apply the check only when it fires. Most were taken from real findings that blind audits missed, so treat a fired trigger as mandatory work. Pick primers from the protocol class identified in `context.md` § 5. Adapted from Zealynx Security's Krait (MIT), which itself draws on pashov/skills, PlamenTSV/plamen, and forefy/.context (all MIT).

Hand hunters the fired triggers and the selected primer sections verbatim, together with the lens blocks they belong to.

## Mechanical sweeps (run on every in-scope contract)

These need no judgment, only completeness. Write the tables down.

- **Sibling modifier diff.** For each contract, build a `| function | modifiers / inline guards |` table of all state-changing functions. Flag any function missing a guard its siblings carry (`autoCheckpoint`, `whenNotPaused`, `nonReentrant`, `updateReward`).
- **Constant audit.** For every named constant (`WAD`, `RAY`, `BPS`, `PRECISION`, `ONE_HUNDRED_*`), check that its value matches its name, that it is used in the right context (percentage vs absolute), and that every use site of the same formula uses the same constant.
- **Missing inverse.** set without unset, add without remove, lock without unlock, pause without unpause, grant without revoke. Configuration that can only be added becomes a permanent misconfiguration risk.
- **Missing restriction coverage.** For each blocklist, pause, or role restriction, list every value-exit path (transfer, withdraw, unstake, redeem, claim, bridge-out). One unrestricted exit makes the restriction useless.
- **Missing reward checkpoint.** Every balance or stake change must settle the reward accumulator first.
- **Paired validation.** Deposit validates X; does withdraw? Mint validates; does burn? Encode normalizes; does decode?
- **Parameter transition safety.** For each setter, check what happens to existing positions, in-flight operations, and already-accrued values (retroactive effects).
- **Core-function DoS.** Unbounded loops over user-growable arrays, external calls whose revert bricks the function, and dust or zero-value calls that block others.

## Trigger heuristics

**Business logic**
- *Multi-step process*: can the steps run out of order, be skipped, or be replayed?
- *Dual accounting (internal counter + `balanceOf`)*: can they diverge through donations or direct transfers?
- *Withdrawal queue*: front-run the request? Is the exchange rate fixed at request time or at fulfilment?
- *Whitelist/blacklist*: can value move through an intermediary to bypass it?
- *Liquidation*: over-extraction, self-liquidation profit, oracle-triggered liquidation; is liquidation always profitable (all collateral types, minimum size, positions too large to liquidate)?
- *Auction/timelock*: griefing, expired execution, timestamp edges.
- *Circular collateral*: is a token valued from a TVL that includes itself (a reflexive death spiral)?

**Calls, callbacks, reentrancy**
- *User-controlled call target or calldata*: drains approvals held by the contract?
- *Callback after a state change* (ERC721/1155 receivers, ERC777, hooks, flash-loan callbacks): re-entry, revert-to-block-liquidation, stale state during the window?
- *Multicall/batch*: `msg.value` reused across calls; per-call restrictions bypassed; balances from unfinalized earlier interactions spent.
- *Cross-function reentrancy*: function A is `nonReentrant`, function B is not, and both touch shared state.
- *Read-only reentrancy*: a view read by other protocols during a callback window (the Curve class).
- *Transient storage*: `TSTORE` values not cleared, stale within a multicall, or used as a reentrancy lock without care.
- *Transfer hooks*: a `_beforeTokenTransfer` restriction that also blocks the admin burn meant to handle restricted addresses.

**Math, precision, constants**
- *Division by a denominator the attacker can inflate* (supply, reserves) via flash loan to force rounding to zero.
- *Asset↔share conversions*: opposite rounding directions; can `mint(1)` pay 0?
- *Library precision mismatch*: two similarly named math libraries with different scales (1e6 vs 1e27).
- *Wrapper decimals*: cToken/vToken decimals used to scale the underlying amount (off by 10^10).
- *Cross-chain decimals*: the same token with different decimals on different chains.
- *Manual loop increment with `continue`*: does `continue` skip `unchecked { i++; }`? That is an infinite loop.

**Tokens and ETH**
- *Payable*: `msg.value` checked against amounts; excess locked; refunds on partial failure; forced ETH via `selfdestruct`.
- *ETH to arbitrary recipients*: a recipient with no `receive()` bricks the function; prefer pull or WETH.
- *Zero-value operations as griefing*: `deposit(0)` updates `lastDepositBlock` and blocks a victim's same-block withdrawal.
- *Permit*: is the permit's token checked against the expected asset? Permit2 front-running and nonce invalidation griefing.

**Signatures and hashing**
- *EIP-712/permit*: chain ID, contract, and nonce in the domain; `ecrecover` returning `address(0)`; malleability; expiry.
- *Hash field completeness*: a hashed struct must include every field. A missing field lets anyone substitute it.
- *`abi.encodePacked` with several dynamic or adjacent variable-length args* used as a key: collisions.
- *Cross-chain replay*: global vs per-chain nonces; account creation salt that does not depend on the chain.

**Access control and deployment**
- *Initializers*: `_disableInitializers()` in the implementation constructor; direct implementation init; front-run initialization.
- *Periphery contracts*: adapters, routers, and bridge tokens with unguarded setters (`setRouter()` open to anyone).
- *Roles granted but never revocable*, admin able to grant critical roles, or a non-critical role compromise leading to fund loss.
- *CREATE (nonce-based) factory deployment*: address theft through reorg on L2s and sidechains. *CREATE2*: predictable salt, front-run deployment, destroy-and-redeploy state reset.
- *Ownership transfer*: one-step transfer to a wrong address means permanent loss.

**External integrations**
- *Permissionless external functions* (`getReward`, `harvest`, `claim` callable on the contract's behalf): front-running breaks assumed state.
- *External shutdown or migration* (killed Curve pool, deprecated Aave market, Convex shutdown): is there a fallback?
- *Silent external failure*: a call returns without effect instead of reverting.
- *`skim`/`sweep`/`rescue`/`claimRewards`*: where do the tokens actually go?
- *Chainlink*: staleness vs heartbeat, zero or negative price, round completeness, L2 sequencer uptime, BTC feed used for WBTC.
- *Uniswap V3*: rounding of negative tick deltas, slippage and deadline on every position-manager call (`deadline = block.timestamp` is no deadline), `slot0` used as a price.
- *Curve*: killed pools, native vs wrapped coin, pool index mapping per pool type.
- *TVL counting*: tokens staked in external gauges or farms omitted from `balanceOf(this)`-based TVL.

**Governance and identity**
- *Phantom voting power*: burned, locked, or auctioned tokens still counted in the quorum denominator.
- *Delegation griefing*: checkpoint growth that makes redelegation run out of gas.
- *Removal safety*: when a gauge, market, or pool is removed, can users still unwind votes, stake, and rewards?
- *ID mutability*: position or loan IDs that change on merge or refinance, leaving consumers with stale IDs.
- *Zero-weight actors*: a 0-stake actor triggering state changes that affect others.
- *On-chain metadata*: user strings concatenated into `tokenURI` JSON without escaping.

## Protocol primers (select by protocol class)

**DEX / AMM**: first-depositor share inflation; round-trip swap profit; flash-loan price manipulation; missing slippage or deadline; factory owner draining router approvals; fee decimal scaling; LP pricing from `slot0`/spot; fee-on-transfer accounting; reentrancy during LP mint/burn; withdrawal DoS through reserve manipulation; stale TWAP; rounding direction; order splitting; pool initialization front-running; reserve manipulation by direct transfer (`sync`/`skim`); StableSwap amplification ramps; NFT pool/collection validation.

**Lending**: oracle manipulation leading to bad liquidations (the top root cause); share inflation in vault-based markets; liquidation profitability and dust positions; interest precision and accrual ordering (accrue *before* state changes); accrued interest omitted from the health factor (the most missed); borrow–repay atomicity; collateral factor misconfiguration; circular collateral; reward claims front-run; debt token decimals; health factor stale during callbacks; collateral types with no liquidation path; no accrual at zero utilization; borrow cap bypass with flash loans; external protocol shutdown; reserve factor inconsistency; debt ceiling math; bad-debt cascade during auctions; reward index unset on first stake; self-transfer breaking rebasing math; singleton references in multi-market designs.

**Staking / governance**: flash-loan votes and stake; reward harvest before state change (accumulator ordering is the top root cause); epoch boundaries; phantom voting power; missing unstake/undelegate paths; delegation griefing; double claim via transfer; vesting bypass; checkpoint overwrite on same-block operations; zero-supply quorum; cooldown bypass via self-transfer or reentrancy; parameter changes breaking in-flight operations; permissionless dust calls resetting timers; modifiers not propagated through cross-contract call chains; voting-power desync after partial unstake (the most missed).

**Proxies / upgrades**: unprotected implementation initialization (the most common); storage collisions and missing `__gap`; unrestricted upgrade permissions; delegatecall context confusion; selector clashes between proxy and implementation; front-run or reentrant initialization; a UUPS implementation that loses `upgradeTo` (the most missed); signature replay across implementations; immutables in implementations; delegatecall to a codeless address; transparent-proxy admin restrictions; predictable clone salts.

**GameFi / NFT**: mint cap bypass; transfer hooks that skip game-state updates; randomness manipulation (on-chain sources, revert-to-reroll, selective VRF fulfilment); user-chosen attributes; reward loops and flash-loan farming; marketplace front-running; lock bypass through external marketplaces; uncapped emissions; Sybil multiplication; metadata injection; cross-chain duplication; emergency pause trapping assets; royalty accounting errors (the most missed).

**Bridges / cross-chain**: unauthorized message processing and untrusted remotes (the top root cause); message replay (nonce, uniqueness, cross-chain); lock–mint supply conservation; finality assumptions; validator thresholds; signature malleability; LayerZero minimum destination gas; destination liquidity assumptions; stale swap parameters on arrival; bridge token access control; missing circuit breakers; refund routing on failure; source and destination diverging after partial failure (the most missed).

**Wallets / Safe / account abstraction**: EIP-712 typehash mismatches, compared character by character (the top root cause); Safe version interface differences (1.3/1.4/1.5 guards and modules); module gas-refund drains; uninitialized implementations; module enable/disable validation; guards bypassed via `execTransactionFromModule` (the most missed); cross-chain and cross-Safe signature replay; delegatecall restriction bypass; validator registration without proof of ownership; nonce gaps; fallback handler manipulation; recovery exploits; ERC-4337 EntryPoint caller checks, signatures not bound to nonce or chain, and banned opcodes in validation; EIP-7702 delegation risks (re-delegation, storage collisions with prior code, `tx.origin` assumptions).

**Vaults (ERC-4626)**: virtual shares/offset present (else first-depositor inflation); `max*`/`preview*` consistent with execution; rounding direction per function; `totalAssets` manipulable by donation; withdrawal limits that brick `redeem`.
