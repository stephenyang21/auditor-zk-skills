# Step 5 — Hunt variants

One root cause usually has several instances, and they are rarely in the module where the first one turned up. Adapted from Trail of Bits' variant-analysis (CC BY-SA 4.0).

## 1. State the root cause

Write *why* the code is wrong, not what it does: "amount used before measuring the received balance", not "deposit() is buggy". Then list the directions a variant could hide in:
- the **same mistake, other places**: sibling functions, copies of the code, other contracts, services, or language bindings;
- **related identifiers**: other names for the same concept (`amount`, `value`, `qty`; `owner`, `admin`, `authority`);
- **other manifestations**: the same faulty assumption expressed differently (a missing check, a check on the wrong variable, a check after use);
- **data-type edges**: the same flow with other types (native vs token, signed vs unsigned, bytes vs string).

## 2. Exact match first

Write a search (`rg`, Semgrep, CodeQL, or an AST query, whichever tool is installed) that matches **only** the known instance, and confirm it hits. A pattern that matches nothing means the bug is misunderstood; fix that before generalizing.

## 3. Generalize one element at a time

Climb from the exact match toward the pattern family. Change one element per step (a literal becomes a metavariable, one callee becomes a family, intra-procedural becomes taint flow). Run the search and read *every* match after each change. Stop climbing when more than half the matches are noise. Changing several elements at once makes the noise impossible to attribute.

Common failures: searching only the original module; matching one attribute and missing the family around it; chasing one manifestation of a root cause that has several; never trying null, empty, and boundary inputs on the candidates.

## 4. Triage

Each match goes through `verification.md` with a fresh skeptic and its own fingerprint, unless it shares the root cause **and** the fix of an existing record. In that case, add its trace to that record instead.

## 5. Record

Add a variant note to the confirmed record's report entry: the root cause, the patterns tried (including those that failed), the match counts, the verdicts, and, when it is cheap to state, a CI rule (Semgrep, CodeQL, or a lint) that would catch a regression.

## Variants-only mode

Given a known bug and no full audit, run steps 1–5 directly and report the instances found, the patterns used, and the recommended CI rule.
