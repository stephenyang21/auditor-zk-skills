# unified-security-audit

One audit skill for ordinary codebases and smart contracts. It runs Cloudflare's `security-audit` workflow (recon, coverage-ledger hunting, independent validation, schema-checked `findings.json`, record verification, reporting) and adds Pashov Audit Group's Solidity expertise to it:

- **`SMART-CONTRACTS.md`**: a domain companion built from the 12 `solidity-auditor` hacking agents (math precision, permission model, economic security, execution trace, invariants, periphery, first principles, asymmetry, boundary enumeration, and the numerical/trust/flow gap hunters), plus the senior-auditor method and the four judging gates, mapped onto `confirmed` / `needs_validation` / `rejected`.
- **`SMART-CONTRACT-RECON.md`**: `x-ray` as Phase 1 Agent 1e. Entry-point map, invariant catalog, threat profile and git-risk analysis, written to the audit output directory and used to seed coverage units.
- **`SMART-CONTRACT-FUZZING.md`**: `fizz` as sandboxed Echidna/Medusa evidence for invariant candidates, and as an opt-in mode that writes a fuzz suite into the repo.

## Install

Copy or symlink this folder into your skills directory:

```bash
ln -s "$PWD" ~/.claude/skills/unified-security-audit   # run from this folder
```

## Use

```
security audit this codebase
audit these contracts                 # full audit, smart-contract companion selected
x-ray this protocol                   # pre-audit report only
generate a fuzz suite for this repo   # fizz, writes test/fizz/ after confirmation
```

Profiles (`quick`, `standard`, `deep`), scoped runs, budgets and prior-run reuse all work as in the Cloudflare skill. See `SKILL.md`.

## Safety model

The Cloudflare rules apply to every phase. Source review is read-only. Output goes outside the target. Target code (`forge test`, fuzzers, coverage) runs only in an OS-enforced sandbox with no network and only the dependencies already present. Nothing is installed or forked from a live chain. Facts only a live chain can supply become `needs_validation` records. Fuzz-suite mode is the one path that writes into the repo, and only after you confirm.

## Tests

```bash
node validate-findings.test.cjs && node validate-coverage-ledger.test.cjs
```

Attribution and upstream commits are in `NOTICE.md`.
