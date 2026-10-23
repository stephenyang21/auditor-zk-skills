# ZK Circuit Lenses

#### When to use this file

Reach for this file for zero-knowledge circuits: Circom templates first, and the same ideas carry over to Noir, Halo2, gnark, and other R1CS/PLONKish circuits. Also use it for the on-chain verifier and the host code that builds public inputs. The threat model is a **malicious prover**: anyone may supply any witness, and only the constraints stand in the way. Distilled from zkSecurity's `circom-auditor` (MIT, © 2026 zkSecurity; included in this repository), which has the full 48-vector catalog under `skills/circom-auditor/references/attack-vectors/`. For a dedicated Circom pass, run that skill.

## Core discipline (include in every hunter prompt that uses this file)

```
- Witness generators do not constrain the prover; only the constraint system does. "The witness code always computes it correctly" is not a defense.
- Every `<--` is a constraint hole until a paired `===`/`<==` pins the same value. `assert(...)` is not a constraint; the verifier never sees it.
- Every comparator (`LessThan(N)` etc.) needs its operands range-checked by `Num2Bits(M ≤ N)`. Every `Num2Bits(254)` on BN254 needs `_strict` or an alias check.
- Every divisor in `<-- a / b` needs `IsZero(b).out === 0` upstream. Every mux/merkle selector needs `s * (s - 1) === 0`.
- Every public input must appear in at least one constraint. A proof must be bound to the caller's intent: recipient, amount, nullifier, chain or context.
- A candidate is a concrete witness: field values that satisfy every constraint yet violate the protocol's intent. Work in the field (values near p, zero, p - k), not over the integers.
```

## Attack classes

**Signal flow**
`<--` with no paired constraint; an output declared but never assigned; witness-only division checked by one polynomial identity; XOR via `a + b - 2ab` without booleanity or recomposition; shifts and rotations rebuilt from free signals; decompositions with no recomposition check.

**Range and comparators**
Comparator inputs that are not range-checked; comparator outputs instantiated but never consumed; `Num2Bits(254)` aliasing on BN254; BigInt limbs bounded individually without a `< modulus` check; `PackBytes`/`BytesToField` inputs not byte-checked; tagged templates that skip their own constraint, and consumers fed non-conforming values.

**Field arithmetic**
Narrow accumulators that overflow mod p before comparison or hashing; elliptic-curve formulas that collapse on equal inputs or the point at infinity; scalar `0` accepted; "already reduced" comments with no constraint behind them; `/` (field inverse) confused with `\` (integer division); `~x` reducing mod p; comparisons normalized to `(-p/2, p/2]`.

**Selectors and multiplexers**
An enabler flag that collapses a gated check to `0 === 0` (`flag * (a - b) === 0`, where the prover sets `flag = 0`); non-boolean mux or merkle-path selectors; array selection via `LessThan(idx, n)` instead of sum-of-equalities; loop bounds smaller than the index domain; one-hot decoders without `IsZero` pairing; several valid witnesses for one public output.

**Accumulators**
Multiplicative accumulators seeded with input data instead of `1`; per-key sums filtered by the wrong side's key, so the output side smuggles entries.

**Protocol binding**
A proof not bound to the caller's intent (recipient, amount, action); static commitments missing a per-action variable (linkability); a zero or sentinel leaf accepted as membership; public inputs never constrained (also removed by `-O2` when they appear only linearly); a verifier toggle hard-coded off; low-entropy or context-free nullifiers (double spend, deanonymization); expiry fed into a hash but never compared; comparisons that leak private data when a privacy flag is off; free precomputed points with no message binding; `_temp`/`_final` signal confusion; signature-gadget preconditions not enforced at the call site; Poseidon domain separation and variable-length collisions; Merkle depth, intermediate-node-as-leaf, and truncated-leaf issues; circuit↔host or circuit↔verifier format mismatches; prover-controlled data that bricks liveness; hardcoded sizes and implicit parameter relations.

**Encoding and language**
Regex circuits that over- or under-accept through masking and complement classes; base64/UTF-8 mismatches; variables and functions that generate no constraints until something consumes them; shadowing in nested scopes.

**Verifier and setup**
On-chain verifier input checks (each public input `< r`; points on the curve and in the subgroup); verification key matching the circuit; trusted-setup assumptions (toxic waste, a phase-2 contribution with no ceremony); proof replay across chains or contracts when public inputs omit chain ID or contract address.

## Universal moves (apply across the above)

- For every signal, classify it as constrained or only assigned. For every template, list the preconditions it assumes about its inputs and find the caller that enforces each one.
- Start from the protocol intent (what an accepted proof must imply) and look for a witness that satisfies the constraints without that implication.
- Try boundary witnesses: 0, 1, p − 1, p − k, values ≥ 2^N for N-bit checks, and repeated or degenerate inputs.

## Validation rules (apply before reporting ANY finding here)

1. **Attack execution**: give the bad witness, with field values, and show it satisfies every constraint on the path. A refutation must quote the exact constraint that pins the value; "no honest prover would pick that" is not a refutation.
2. **Reachability**: any prover can supply any witness, and honest inputs near the field boundary count. Reject only when an upstream constraint makes the witness impossible.
3. **Trigger**: harm that needs the trusted setup or a designated prover to misbehave needs a named unprivileged path (a leaked or unverified setup, a public entry template, a setup-assumed invariant the circuit never enforces).
4. **Impact**: soundness breaks (forgery, double spend, membership or range bypass, replay), permanent completeness breaks for honest provers, and meaningful privacy leaks are eligible for `confirmed`.
5. **Proof**: where `circom`/`snarkjs` are installed locally, compile and generate the bad witness inside the sandbox, and show the constraint check passing (`snarkjs wtns check` or an equivalent). Otherwise give the witness algebraically and mark the run blocker.
