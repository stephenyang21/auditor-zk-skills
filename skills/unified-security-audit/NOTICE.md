# Notice

This skill combines two MIT-licensed projects. Their licenses are in `licenses/`.

| Upstream | Commit | Used as |
|---|---|---|
| [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) (`skills/security-audit`) | `c1c8a8c` | The workflow backbone: `SKILL.md`, phase files, domain companions, `report-schema.json`, and the validators, with small cross-reference edits. |
| [pashov/skills](https://github.com/pashov/skills) | `eacfc09` | `pashov/` holds unmodified copies of `x-ray`, `fizz`, and `solidity-auditor`. `SMART-CONTRACTS.md` adapts the solidity-auditor hacking agents, senior-auditor SOP, shared rules, and judging gates. `SMART-CONTRACT-RECON.md` and `SMART-CONTRACT-FUZZING.md` run x-ray and fizz with overrides. |

Files changed from the Cloudflare copy: `SKILL.md` (name, description, smart-contract modes, workflow pointer, `x-ray/` run file), `ATTACK-CLASSES.md` (companion pointer), `RECONNAISSANCE.md` (Agent 1e pointer), `HUNTING.md` (hunter-context pointer), `VALIDATION-AND-REPORTING.md` (fuzz-evidence pointer). New files: `SMART-CONTRACTS.md`, `SMART-CONTRACT-RECON.md`, `SMART-CONTRACT-FUZZING.md`, `NOTICE.md`.

`pashov/solidity-auditor/` is kept for reference and future upstream syncs; this skill does not run its orchestration directly.
