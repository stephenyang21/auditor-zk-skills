# Proof — bounded local evidence

A proof shows the **minimum** effect that settles a claim, and nothing more. It exists to convince the owner that the defect is real and to give them a regression test. It is not an exploit.

## Where proofs may run

Run target code only in an execution environment that the person running the audit has already set up and trusts to enforce the `SKILL.md` controls: no external network, a minimal environment, a read-only target, writes confined to scratch, and resource limits. This skill does not build that environment. If none is available, or you cannot confirm that it enforces those controls, run nothing. Record the candidate as `needs_validation`, with the blocker "no trusted sandbox" and the exact test you would have run.

Always work on a disposable copy under `<out>/scratch/<agent>/`, never on the target itself. Use only dependencies already present in the copy.

## What counts as an observed result

| Domain | Acceptable minimum evidence |
|---|---|
| Web, API, service | A unit or integration test against a locally started instance with dummy principals, showing the unauthorized dummy record, the wrong authorization decision, or the rendered unsafe output. |
| Library, parser, CLI | A minimal harness or existing test showing the wrong return value, the accepted malformed input, or a sanitizer report. |
| Native code | A sanitizer (ASan/UBSan/TSan/MSan) or Miri report on a small input, or a deterministic crash at the claimed operation. |
| Smart contract | A Foundry or Hardhat test on an in-process EVM that deploys the in-scope contracts with dummy actors and mock tokens, performs the attack sequence, and asserts the balance, share, or state delta, or the revert that bricks a path. |
| Other chains | A program or mock-runtime test showing the unauthorized state change or the panic. |
| ZK circuit | The bad witness, with the constraint check passing on it. |
| Config, IaC, policy | A locally rendered manifest or policy evaluation with dummy identities, showing the permitted action. |
| Crypto implementation | Emitted assembly showing the secret-dependent branch or division, or a memory read showing the unwiped secret, in a local build. |

A proof's output must name the effect in its own terms: an assertion message, a sanitizer line, a printed delta. "Test passed" alone is not evidence.

**Assert the harm, not the mechanism.** "The function can be called", "the state can be reached", or "the path exists" proves nothing. The assertion must be the impact premise from `verification.md`: the victim's balance drops by X, the attacker's balance rises by at least Y funded by the pool, tenant B's request returns tenant A's record, the honest user's withdrawal reverts.

## Defect-mutation check (required before `confirmed`)

A passing proof written by the same reasoning that produced the finding can quietly build a world where the finding is true. Pin it to the defect:

1. **Correct the defect, not the fix.** In the scratch copy, change only the defective line or lines to their correct form: the missing check added, the wrong constant corrected, `<` made `<=`, the skipped state write restored. This is the smallest semantic inverse of the defect. Ignore the recommended remediation.
2. **Re-run the identical proof, unchanged.**
3. **Read the result.**
   - The proof now fails or reverts → it is **pinned**: the cited defect causes the effect. Record this as part of the observed result.
   - The proof still passes → it is **not pinned**: the harness produces the effect independently of the cited line. Do not confirm. Re-examine the root cause; if it cannot be pinned, the record is `needs_validation` with the blocker "proof not pinned to the cited defect".
4. **Optionally, check the fix.** Apply the proposed remediation separately and re-run. If it does not stop the proof, the remediation is wrong, but that says nothing about whether the bug is real.

When the correct form of the line is unclear, say so and record why the check could not run.

## Where a proof stops

- At the first observation that demonstrates the effect: one dummy record, one wrong value, one balance delta.
- Before persistence, payload chains, privilege escalation beyond the claim, data exfiltration, or any effect on shared state.
- Never stress-test, saturate resources, generate cost, or repeat beyond what determinism requires.
- Never contact deployed endpoints, live chains, forks of live chains, registries, identity providers, paid APIs, or other users' data.
- Use dummy credentials, keys, accounts, and data only.

## Choosing the proof

Prefer, in order: an existing test you can extend; a minimal new test of the claimed path; a property test; a bounded fuzz campaign.

- **Property tests** suit claims about round-trips, conservation, idempotence, monotonicity, or "for every input" rules. Write one property for exactly the invariant the candidate breaks, using the framework the project already has (for example Hypothesis, fast-check, proptest, Foundry invariant tests, Echidna, or Medusa). Shrink the counterexample and turn it into a deterministic regression test.
- **Stateful fuzzing** suits claims that need call sequences, many actors, or accumulated rounding. Use handlers only for the entry points on the candidate's trace, assert only the violated invariant, keep the run short and bounded, and replay the shrunk sequence as a deterministic test. Rule out a harness bug before calling a violation real. A clean campaign is coverage evidence, not proof that the code is safe. For generating a full fuzz suite as a deliverable, use the `fizz` workflow in `unified-security-audit` with the user's agreement.

## Recording evidence

For each local check, record: the command, the exact input or fixture, the names of any environment variables you set (never their secret values, and never the ambient environment), the result, and the evidence file. The parent copies only the expected output files from scratch to `<out>/evidence/<agent>/`. It copies only regular files within a stated size bound: never symlinks, never by glob, and never an archive extracted in place. Evidence that fails those checks is discarded. If that evidence was decisive, the candidate becomes `needs_validation`.

Put the minimum fixture or test in the record's `execution.payloads`, the steps in `execution.instructions`, and the actual output in `execution.observed_result`.
