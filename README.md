# auditor-zk-skills

Security-audit skills for coding agents (Claude Code, Codex and similar), covering ordinary codebases, smart contracts and zero-knowledge circuits.

| Skill | What it does |
|---|---|
| [`unified-security-audit`](skills/unified-security-audit/) | Cloudflare's six-phase audit workflow (recon, coverage-ledger hunting, independent validation, schema-checked `findings.json`, verification, reports) plus Pashov Audit Group's Solidity expertise: 12 hacking-agent attack classes and judging gates, `x-ray` pre-audit recon, and `fizz` Echidna/Medusa fuzzing. |
| [`circom-auditor`](skills/circom-auditor/) | Circom circuit review for soundness, completeness, privacy and constraint bugs, using a 17-agent parallel workflow or a local single-agent pass. |

## Add these skills to Claude

### Claude Code: plugin (recommended)

In Claude Code 2.1.275 or later, run:

```
/plugin install auditor-zk-skills --marketplace stephenyang21/auditor-zk-skills
```

On older versions, add the marketplace first, then install:

```
/plugin marketplace add stephenyang21/auditor-zk-skills
/plugin install auditor-zk-skills@auditor-zk-skills
```

Restart Claude Code if the skills do not appear. Run `/plugin` to check that both skills are listed. To update later, run `/plugin marketplace update auditor-zk-skills`.

### Claude Code: personal skills folder

The skills load in every project:

```bash
git clone https://github.com/stephenyang21/auditor-zk-skills.git
mkdir -p ~/.claude/skills
ln -s "$PWD/auditor-zk-skills/skills/unified-security-audit" ~/.claude/skills/unified-security-audit
ln -s "$PWD/auditor-zk-skills/skills/circom-auditor" ~/.claude/skills/circom-auditor
```

Run `git pull` in the clone to update. If a folder with the same name already exists in `~/.claude/skills`, remove it first.

### Claude Code: one project only

Copy the skills into the project's `.claude/skills/` and commit them, so everyone working on that repo gets them:

```bash
mkdir -p .claude/skills
cp -R /path/to/auditor-zk-skills/skills/* .claude/skills/
```

### Claude.ai and the Claude desktop app

1. Build one ZIP per skill. The skill folder must be at the top level of the ZIP:
   ```bash
   cd auditor-zk-skills/skills
   zip -r unified-security-audit.zip unified-security-audit
   zip -r circom-auditor.zip circom-auditor
   ```
2. In Claude, open **Settings → Capabilities** and turn on code execution. Under **Skills**, choose **Upload skill** and upload each ZIP.
3. Turn the uploaded skills on.

Both skills work best in Claude Code. They start parallel subagents, run local scripts, and write audit files. In Claude.ai, ask for a single-agent or local pass. Steps that need a local sandbox, such as Foundry tests and fuzzing, are recorded as `needs_validation` there.

### Check that it works

Ask Claude "what skills do you have?", or start a task with one of the prompts below. Claude loads the matching skill by itself. You can also name the skill directly, for example "use unified-security-audit to …".

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
