# auditor-zk-skills

Security-audit skills for coding agents (Claude Code, Codex and similar), covering ordinary codebases, smart contracts and zero-knowledge circuits.

| Skill | What it does |
|---|---|
| [`unified-security-audit`](skills/unified-security-audit/) | Cloudflare's six-phase audit workflow (recon, coverage-ledger hunting, independent validation, schema-checked `findings.json`, verification, reports) plus Pashov Audit Group's Solidity expertise: 12 hacking-agent attack classes and judging gates, `x-ray` pre-audit recon, and `fizz` Echidna/Medusa fuzzing. |
| [`circom-auditor`](skills/circom-auditor/) | Circom circuit review for soundness, completeness, privacy and constraint bugs, using a 17-agent parallel workflow or a local single-agent pass. |

## Install

```bash
git clone https://github.com/stephenyang21/auditor-zk-skills.git
mkdir -p ~/.claude/skills
ln -s "$PWD/auditor-zk-skills/skills/unified-security-audit" ~/.claude/skills/unified-security-audit
ln -s "$PWD/auditor-zk-skills/skills/circom-auditor" ~/.claude/skills/circom-auditor
```

## Use

```
security audit this codebase
audit these contracts
x-ray this protocol
generate a fuzz suite for this repo
audit the Circom circuits in this repo
```

## Tests

```bash
cd skills/unified-security-audit
node validate-findings.test.cjs && node validate-coverage-ledger.test.cjs
```

## License and attribution

MIT (see [`LICENSE`](LICENSE)). `unified-security-audit` builds on [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) and [pashov/skills](https://github.com/pashov/skills), both MIT. Their licenses, the upstream commits and a list of modified files are in [`skills/unified-security-audit/NOTICE.md`](skills/unified-security-audit/NOTICE.md) and `skills/unified-security-audit/licenses/`.

These skills support human review and do not replace a formal audit.
