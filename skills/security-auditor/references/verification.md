# Step 4 — Verify

Each verifier is a fresh **skeptic** that did not hunt the candidate and never sees another verifier's conclusion. Its job is to try to refute the claim from source and bounded local evidence, then return exactly one record. Hunters bias toward seeing bugs and overrating them; the skeptic corrects that, and must not overcorrect into rejecting a real attack on speculative grounds.

## Verifier input

Give the skeptic: the candidate; its unit's checks and evidence paths; the `ARCHITECTURE.md` facts needed to read the path; the `Validation rules` of every lens or domain file the unit used, verbatim; this file; `proof.md`; the sandbox rules; the field lists from `reporting.md`; and any prior record with the same fingerprint.

## The procedure

### 1. Restate the claim

Before any analysis, write in your own words:
- the exact claim (`heap overflow in parse_header() when content_length > 4096`);
- the root cause (`no bounds check before memcpy at src/http.c:142`);
- the trigger, and who can send it;
- the impact claimed;
- the threat model: the privilege the code runs with, whether it is sandboxed, and what the attacker can already do;
- the bug class (pick its row in § Class-specific checks).

If the claim cannot be restated coherently, it collapses here. About half of false positives do.

### 2. Triage brocards (cheap dismissals first)

Stop at the first failure and record its number.

1. **No vulnerability without a threat model.** "An attacker with [capability] can [action] to achieve [impact]" must be fillable.
2. **No exploit from the heavens.** If the required capability already includes the impact, there is no vulnerability.
3. **No vulnerability outside usage.** The path must be reachable by a real caller in this codebase or a documented integration.
4. **No vulnerability from standard behavior.** Correctly implementing the specification is not a flaw in this code. It *is* a flaw if the code promises to be stricter than the spec and fails at that.
5. **No vulnerability from documented behavior.** Documented, warned-about behavior used as documented counts against the downstream misuser, not this code.
6. **No cure worse than the disease.** Note it when the only fix would cost more than the risk; this lowers priority and does not by itself reject.
7. **The report is neither necessary nor sufficient.** A CVE, scanner rule ID, or CVSS score proves nothing either way; judge only the technical merit.

### 3. Gates (sequential; a failed gate settles the verdict)

**Gate A — Attack execution.** Trace the claimed path from the attacker's first action to the harm. Read every guard, check, modifier, constraint, framework default, and type-system guarantee on it.
- A specific line that stops the attack before harm (quote it and trace how it blocks) → `rejected`.
- An interruption that is only speculative ("the deployer would set X", "the caller would notice", "an honest prover wouldn't") → not a stop; continue.

**Gate B — Reachability and math bounds.** The vulnerable state must be reachable through normal usage, ordinary inputs, or common environmental behavior (weird tokens, retries, concurrency that actually exists).
- Earlier validation or conditional flow makes the condition mathematically impossible → `rejected`. Show the algebra: "line 98 ensures `size ≥ 16`, so `size − 12 ≥ 4`."
- Reachable only through a deployment fact, configuration, provider behavior, or deployed parameter that the source does not fix → `needs_validation`, naming the fact.
- Reachable only through privileged action outside normal operation → `rejected`, unless Gate C's amplifier rule applies.

**Gate C — Trigger.** An actor below the boundary must be able to trigger it.
- Harm that needs a trusted role (admin, owner, operator, trusted setup, designated prover) to act maliciously or against documented intent → `rejected`, unless the record names a concrete unprivileged **amplifier**:
  - a **race**: a privileged update mid-flow that a user exploits before it propagates;
  - a **retroactive sweep**: a privileged update rewrites a value already credited;
  - an **asymmetric formula**: privileged output feeds a formula an unprivileged actor profits from;
  - an **access gap**: the access mechanism itself is broken (missing guard, tautological check, unprotected initializer).
  With an amplifier, judge the unprivileged path.
- Same-principal or self-harm effects are not boundary crossings → `rejected`.

**Gate D — Real impact.** Name the identifiable victim and the material harm: code execution, privilege gain, cross-principal data read or write, auth bypass, theft or freezing of funds, insolvency, a soundness break, or a shared-availability loss an unprivileged actor triggers.
- Operational robustness, self-impact, or dust with no compounding → `rejected` (record it as hardening if useful).
- Defense in depth failing while the primary control holds → `rejected`.

**Gate E — Environment.** Check protections outside the immediate code: sandboxing, allocator hardening, framework auto-escaping, parameterized queries, CSP, OS permissions, the language's memory safety.
- One that fully prevents exploitation → `rejected`.
- One whose presence is decisive but not visible in source → `needs_validation`.
- Mitigations that only raise cost → lower likelihood; do not reject.

**Gate F — Proof.** Follow `proof.md`. Reproduce the minimum observed result in the sandbox: a test assertion, sanitizer report, state delta, bad witness, or rendered policy.
- Reproduced → eligible for `confirmed`.
- Sandbox, toolchain, or dependency unavailable → `needs_validation`, naming that blocker and the exact test you would run.
- Attempted and the effect did not occur → re-check Gates A and B. Reject if the source explains why; otherwise `needs_validation`, with the discrepancy.

### 4. Devil's advocate (before returning `confirmed`)

Write the strongest one-paragraph argument that this is *not* a vulnerability, using the false-positive checklist below, then answer it with evidence. If you cannot answer it, the verdict is not `confirmed`.

### 5. Return one record

```json
{"decision": "confirmed|needs_validation|rejected", "record": { "...": "fields per reporting.md for that verdict" }}
```

A corrected record replaces the hunter's wording. Keep the fingerprint whenever the root cause is the same.

## False-positive checklist

Apply every item to every candidate:

1. **Full validation chain.** Trace backward to *all* validation before the dangerous operation, not just the nearest lines.
2. **Conditional reachability.** Do the conditions needed to reach this line make the bad value impossible (`buffer[len-4]` reached only when `len > 12`)?
3. **Defensive code.** An assertion or check that blocks the scenario is protection, not vulnerability.
4. **Data source.** Is the value attacker-controlled, or a constant, internal configuration, trusted installer output, or an API return already validated?
5. **Bounds logic.** Relationships between checks and later arithmetic (`size ≥ MIN` with `MIN ≥ sizeof(hdr)` means no underflow).
6. **TOCTOU proof.** Show the value can actually change between check and use.
7. **API contract.** Many APIs bound their own writes or manage their own memory; read the contract first.
8. **Concurrency proof.** Show that concurrent access is actually possible under the real threading and locking model.
9. **Pattern ≠ analysis.** "Looks like a known bug" and "similar code elsewhere was vulnerable" are not evidence for this instance.
10. **Real vs theoretical impact.** Would it actually lead to execution, privilege, disclosure, or loss of value?
11. **Primary vs defense-in-depth.** Is the failing control the one that matters?
12. **Production path.** Test-only, debug-only, setup-only, and dead code are not production vulnerabilities, unless they ship and are reachable.
13. **Language and framework guarantees.** Memory corruption in safe Rust, Go without `unsafe`/cgo, or managed runtimes is almost always false. ORM parameterization and template auto-escaping hold unless explicitly bypassed.

Rationalizations to reject in yourself: "it looks dangerous, so it is", "skipping the full trace for efficiency", "this is clearly critical", "similar code was vulnerable elsewhere", "we can't prove it's *not* exploitable" (the claim carries the burden).

## Class-specific checks

| Class | Also verify |
|---|---|
| Memory corruption | What is corrupted, its size and offset, attacker control, whether it gives a primitive (read/write, pointer overwrite) or only a crash, allocator hardening, and for UAF who frees, who reuses, and whether the replacement is controlled. |
| Logic / auth | Compare against the spec or docs, not just the code; map all state transitions; check *every* auth path for a secondary check. Logic bugs pass bounds proofs, so clean math does not clear them. |
| Race / TOCTOU | The real window, whether the attacker can widen it, the threading model, every synchronization primitive, and for filesystems whether the attacker controls the path in between. |
| Integer | Exact types and ranges at each step, signed (UB) vs unsigned, every cast and promotion, and whether the wrapped value reaches a size, index, bound, or balance. |
| Crypto | Parameters against current standards, RNG source and seeding, nonce reuse in practice, whether a timing observer can actually measure, and test vectors against a reference. |
| Injection | Every encode/decode step between source and sink, framework escaping actually enabled, the exact sink context (HTML body, attribute, JS, URL, shell, SQL identifier vs value), and canonicalization before checks. |
| Disclosure | What exactly leaks and whether it helps an attacker; for uninitialized reads, that the memory really is uninitialized there; for errors, that they reach the attacker. |
| DoS | The amplification ratio, permanence, worst-case input proven to trigger it (not just claimed), restart behavior, and that the target is shared, not self-only. |
| Deserialization | Attacker control of the bytes, a usable gadget chain in the actual dependency graph, and type allowlists or filters. |
| Smart contract | Pashov's four gates and severity scale in `lenses-smart-contracts.md` § Validation rules; fee-on-transfer, rebasing, blocklist, and pausable tokens are plausible for any arbitrary-token path. |
| ZK circuit | `lenses-zk.md` § Validation rules: give the bad witness concretely. |

## Severity (confirmed only)

Rate `likelihood` and `impact`, then `overall_severity`, never above the demonstrated impact:

- **critical**: an unauthenticated or unprivileged actor gains code execution, full data-store access, takeover of arbitrary accounts, or theft or permanent freezing of material funds, with no unusual preconditions.
- **high**: full defeat of an explicit control with real consequences: auth bypass, cross-tenant read or write, stored script execution against other users, authenticated code execution, theft under achievable state, insolvency, a soundness break, or an unprivileged remote stop of a shared service or chain.
- **medium**: a real boundary violation with limited blast radius, uncommon preconditions, a temporary freeze, broken ERC or interface guarantees that integrators rely on, or an admin action exploitable via a named amplifier.
- **low**: disclosure of non-secret internals, or an effect needing sustained effort for minimal gain.
- **informational**: a confirmed minimal-impact observation, mainly useful as a step in a larger chain.

The test between high and medium: does the result *fully defeat* an explicit control for a consequential action, or only weaken it? If you cannot state the concrete damage, the severity is lower than it feels.

## Confidence (confirmed only)

Start at **high**. Drop to **medium** for each of: a specific but achievable required state, bounded non-compounding impact, or a proof that needed a mock of external behavior. Drop to **low** when two apply. An incomplete trace is never confirmed at any confidence.

## Chains

After every candidate has a verdict, review the `rejected` and `needs_validation` records together. Two weak records combine when one record's output satisfies the other's missing precondition: an info leak supplying a token, a low-privilege write reaching a privileged reader, or a DoS forcing a fallback path. Give each plausible chain its own fingerprint (`chain:<fp-a>+<fp-b>`) and send it through this procedure with a fresh skeptic.

## Verify-only mode

When the user asks whether specific findings are real, run § The procedure for each one. Run all restatements first, since they collapse the obvious ones; then do the rest, cheapest first. End with counts and two lists: true positives with a one-line description, and false positives with the brocard or gate that failed and the quoted line.
