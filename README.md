# auditor-zk-skills

Security-audit skills for coding agents (Claude Code, Codex and similar), covering ordinary codebases, smart contracts and zero-knowledge circuits.

| Skill | What it does |
|---|---|
| [`security-auditor`](skills/security-auditor/) | **Recommended.** One skill that takes the best of all three sources. Cloudflare provides the workflow (coverage plan, critic waves, three verdicts, validated `findings.json`). Pashov provides the attacker mindset, the 12 smart-contract lenses, the judging gates and invariant mapping. Trail of Bits provides function-level context, the false-positive procedure and triage brocards, variant hunting, diff review, weird tokens, unit-mismatch checks, non-EVM chains, and C/Rust/crypto checks. Krait adds the impact premise, defect-mutation proof check, revival review, state-coupling and masking-code analysis, the per-component pass, risk scoring, and EVM heuristics and protocol primers. Modes: full audit, PR/diff review, verify a finding, find variants, pre-audit map. CC BY-SA 4.0. |
| [`unified-security-audit`](skills/unified-security-audit/) | Cloudflare's six-phase audit workflow (recon, coverage-ledger hunting, independent validation, schema-checked `findings.json`, verification, reports) plus Pashov Audit Group's Solidity expertise: 12 hacking-agent attack classes and judging gates, `x-ray` pre-audit recon, and `fizz` Echidna/Medusa fuzzing. |
| [`circom-auditor`](skills/circom-auditor/) | Circom circuit review for soundness, completeness, privacy and constraint bugs, using a 17-agent parallel workflow or a local single-agent pass. By [zkSecurity](https://github.com/zksecurity/zk-skills) (MIT), included unmodified. |

### Krait checklist

[`third_party/krait/`](third_party/krait/) holds a copy of Zealynx Security's [Krait](https://github.com/ZealynxSecurity/krait) (MIT), unmodified except for two example keys redacted (see `THIRD_PARTY_NOTICES.md`). Its checklist plugin is in this marketplace: 845 checks across 39 DeFi verticals, for audit-readiness scans (`/krait:scan`, `/krait:assess`, `/krait:check`). Krait's full `/krait` audit pipeline and MCP servers are not marketplace plugins; install them with its own `scripts/install.sh` if you want them. Its methodology is also built into `security-auditor`.

```
/plugin install krait --marketplace stephenyang21/auditor-zk-skills
```

### Trail of Bits plugins

[`third_party/trailofbits/`](third_party/trailofbits/) holds an unmodified copy of [trailofbits/skills](https://github.com/trailofbits/skills): 46 plugins with 97 skills, licensed **CC BY-SA 4.0**. Each one is a separate plugin in this marketplace, so you install only the ones you want.

| Plugin | What it does |
|---|---|
| [`audit-context-building`](third_party/trailofbits/plugins/audit-context-building/) | Understand a codebase before looking for bugs in it. |
| [`building-secure-contracts`](third_party/trailofbits/plugins/building-secure-contracts/) | Comprehensive smart contract security toolkit based on Trail of Bits' Building Secure Contracts framework. |
| [`burpsuite-project-parser`](third_party/trailofbits/plugins/burpsuite-project-parser/) | Search and extract data from Burp Suite project files (.burp) for security analysis |
| [`chrome-mcp-troubleshooting`](third_party/trailofbits/plugins/chrome-mcp-troubleshooting/) | Diagnose and fix Claude in Chrome MCP extension connectivity issues |
| [`constant-time-analysis`](third_party/trailofbits/plugins/constant-time-analysis/) | Detect compiler-induced timing side-channels in cryptographic code |
| [`culture-index`](third_party/trailofbits/plugins/culture-index/) | Interprets Culture Index survey results for individuals and teams |
| [`devcontainer-setup`](third_party/trailofbits/plugins/devcontainer-setup/) | Create pre-configured devcontainers with Claude Code and language-specific tooling |
| [`differential-review`](third_party/trailofbits/plugins/differential-review/) | Security-focused differential review of code changes with git history analysis and blast radius estimation |
| [`firebase-apk-scanner`](third_party/trailofbits/plugins/firebase-apk-scanner/) | Scan Android APKs for Firebase security misconfigurations including open databases, storage buckets, authentication issues, and exposed cloud functions. |
| [`gh-cli`](third_party/trailofbits/plugins/gh-cli/) | Intercepts GitHub URL fetches (WebFetch and MCP fetch tools) and curl/wget commands, redirecting to the authenticated gh CLI. |
| [`dwarf-expert`](third_party/trailofbits/plugins/dwarf-expert/) | Analyze DWARF debug information: parse and search DIEs with dwarfdump and readelf, verify debug info integrity, and write DWARF parsing code |
| [`entry-point-analyzer`](third_party/trailofbits/plugins/entry-point-analyzer/) | Analyzes smart contract codebases to identify state-changing entry points for security auditing. |
| [`mutation-testing`](third_party/trailofbits/plugins/mutation-testing/) | Configures mewt or muton campaigns, analyzes surviving mutants, and investigates bugs exposed by testing gaps. |
| [`patching-bugs`](third_party/trailofbits/plugins/patching-bugs/) | Agent-orchestrated workflow to reproduce, patch, prove and regression-check one known bug. |
| [`post-patch-validation`](third_party/trailofbits/plugins/post-patch-validation/) | Validates security patches against the reported bug, root-cause variants, and surrounding behavior. |
| [`property-based-testing`](third_party/trailofbits/plugins/property-based-testing/) | Write, review, and triage property-based tests — Hypothesis, fast-check, proptest, and Echidna or Medusa for Solidity invariants |
| [`regression-hunt`](third_party/trailofbits/plugins/regression-hunt/) | Agent-orchestrated skills for finding, reproducing and adjudicating regressions in PRs or commits. |
| [`semgrep-rule-creator`](third_party/trailofbits/plugins/semgrep-rule-creator/) | Create custom Semgrep rules for detecting bug patterns and security vulnerabilities |
| [`semgrep-rule-variant-creator`](third_party/trailofbits/plugins/semgrep-rule-variant-creator/) | Creates language variants of existing Semgrep rules with proper applicability analysis and test-driven validation |
| [`sharp-edges`](third_party/trailofbits/plugins/sharp-edges/) | Identify error-prone APIs, dangerous configurations, and footgun designs that enable security mistakes |
| [`static-analysis`](third_party/trailofbits/plugins/static-analysis/) | Static analysis toolkit with CodeQL, Semgrep, and SARIF parsing for security vulnerability detection |
| [`spec-to-code-compliance`](third_party/trailofbits/plugins/spec-to-code-compliance/) | Check code against the documentation that specifies it: one agent per requirement, divergences refuted before they are reported, evidence cited to the line |
| [`testing-handbook-skills`](third_party/trailofbits/plugins/testing-handbook-skills/) | Skills from the Trail of Bits Application Security Testing Handbook (appsec.guide) |
| [`trailmark`](third_party/trailofbits/plugins/trailmark/) | Builds source and binary code graphs for security analysis, context slicing, mutation testing, cryptographic protocol modeling, finding triage, and variant analysis. |
| [`variant-analysis`](third_party/trailofbits/plugins/variant-analysis/) | Find similar vulnerabilities and bugs across codebases using pattern-based analysis |
| [`c-review`](third_party/trailofbits/plugins/c-review/) | Comprehensive C/C++ security code review, with coverage verified against a parse of the source |
| [`rust-review`](third_party/trailofbits/plugins/rust-review/) | Comprehensive Rust security code review with specialized bug-finding agents covering the safe/unsafe boundary, memory safety in unsafe blocks, concurrency, panic-induced DoS, recursion-induced stack overflow, FFI, and async runtime hazards |
| [`modern-python`](third_party/trailofbits/plugins/modern-python/) | Modern Python best practices. |
| [`insecure-defaults`](third_party/trailofbits/plugins/insecure-defaults/) | Detects insecure default configurations including hardcoded credentials, fallback secrets, weak authentication defaults, and dangerous values in production |
| [`review-walkthrough`](third_party/trailofbits/plugins/review-walkthrough/) | Generates an interactive HTML walkthrough for reviewing code changes. |
| [`second-opinion`](third_party/trailofbits/plugins/second-opinion/) | Gets independent code reviews from Codex or Antigravity for uncommitted changes, branch diffs, and commits. |
| [`yara-authoring`](third_party/trailofbits/plugins/yara-authoring/) | YARA-X detection rule authoring with linting and quality analysis |
| [`git-cleanup`](third_party/trailofbits/plugins/git-cleanup/) | Safely analyzes and cleans up local git branches and worktrees by categorizing them as merged, squash-merged, superseded, or active work. |
| [`goal-prompt`](third_party/trailofbits/plugins/goal-prompt/) | Drafts copy-ready /goal commands for goal mode in Claude Code and Codex: verifiable completion conditions with stop bounds, normalized to a single line under the 4,000-character cap. |
| [`supply-chain-risk-auditor`](third_party/trailofbits/plugins/supply-chain-risk-auditor/) | Audit a project's npm, PyPI, and Go dependencies for supply-chain risk: version-matched advisories for direct dependencies and the full lockfile tree, abandoned upstreams, npm publisher concentration, and install scripts |
| [`zeroize-audit`](third_party/trailofbits/plugins/zeroize-audit/) | Detects missing or compiler-optimized zeroization of sensitive data with assembly and control-flow analysis |
| [`let-fate-decide`](third_party/trailofbits/plugins/let-fate-decide/) | Draws the 12 Houses of the Zodiac Tarot spread using cryptographic randomness to add 100+ bits of entropy to vague or underspecified planning. |
| [`agentic-actions-auditor`](third_party/trailofbits/plugins/agentic-actions-auditor/) | Audits GitHub Actions workflows for security vulnerabilities in AI agent integrations (Claude Code Action, Gemini CLI, OpenAI Codex, GitHub AI Inference) |
| [`code-improver`](third_party/trailofbits/plugins/code-improver/) | Improves code targets — skills, plugins, or a branch's changes — through an autonomous review-and-fix workflow with a pluggable reviewer (any installed skill or agent), a cross-round findings ledger, oscillation escalation, and a mechanical scope guard. |
| [`fp-check`](third_party/trailofbits/plugins/fp-check/) | Systematic false positive verification for security bug analysis with mandatory gate reviews |
| [`dimensional-analysis`](third_party/trailofbits/plugins/dimensional-analysis/) | Audits code for unit and decimal-scaling bugs and annotates it with dimensional comments recording the units of each value. |
| [`vulnerability-triage-brocards`](third_party/trailofbits/plugins/vulnerability-triage-brocards/) | Principled framework for triaging vulnerability reports using 7 brocards (rules of thumb). |
| [`github-triage`](third_party/trailofbits/plugins/github-triage/) | Triages a repository's open GitHub issues and pull requests via the gh CLI: optionally merges ready bot and maintainer-approved PRs and spawns review subagents for unreviewed ones, closes already-resolved issues with referenced explanations, cross-links issues with pending fix PRs, and assigns local-only priority and change-size estimates. |
| [`open-sourcing`](third_party/trailofbits/plugins/open-sourcing/) | Prepares a repository for public open-source release: secrets-history hygiene, license selection, documentation and CI readiness checks, and language-specific packaging and release guidance. |
| [`writing-lean-proofs`](third_party/trailofbits/plugins/writing-lean-proofs/) | Structured Lean 4 proof writing and library design following Mathlib conventions |
| [`modern-cpp`](third_party/trailofbits/plugins/modern-cpp/) | Modern C++ best practices (C++20/23/26). |
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

To add the combined `security-auditor` skill on its own:

```
/plugin install security-auditor --marketplace stephenyang21/auditor-zk-skills
```

To add a Trail of Bits plugin, use its name from the table above:

```
/plugin install building-secure-contracts --marketplace stephenyang21/auditor-zk-skills
/plugin install fp-check --marketplace stephenyang21/auditor-zk-skills
```

Check these before installing. Some Trail of Bits plugins change how Claude Code behaves beyond adding skills:

- `gh-cli` hooks GitHub fetches and `curl`/`wget` calls and sends them through the `gh` CLI.
- `modern-python` puts `python`/`pip` shims on the `PATH`.
- `fp-check` adds a hook.
- `zeroize-audit` starts an MCP server.

Restart Claude Code if the skills do not appear. Run `/plugin` to check that both skills are listed. To update later, run `/plugin marketplace update auditor-zk-skills`.

### Claude Code: personal skills folder

The skills load in every project:

```bash
git clone https://github.com/stephenyang21/auditor-zk-skills.git
mkdir -p ~/.claude/skills
ln -s "$PWD/auditor-zk-skills/skills/unified-security-audit" ~/.claude/skills/unified-security-audit
ln -s "$PWD/auditor-zk-skills/skills/circom-auditor" ~/.claude/skills/circom-auditor
ln -s "$PWD/auditor-zk-skills/skills/security-auditor" ~/.claude/skills/security-auditor
```

To link every Trail of Bits skill as well (each plugin keeps its skills under `plugins/<name>/skills/`):

```bash
for d in auditor-zk-skills/third_party/trailofbits/plugins/*/skills/*/; do
  ln -s "$PWD/$d" ~/.claude/skills/"$(basename "$d")"
done
```

This skills-folder method loads only the skills. It skips the plugins' hooks, agents and MCP servers, so use the plugin method when you need those.

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
   zip -r security-auditor.zip security-auditor
   # a Trail of Bits skill, e.g. fp-check:
   cd ../third_party/trailofbits/plugins/fp-check/skills && zip -r ~/fp-check.zip fp-check
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

## Tests and evals

```bash
cd skills/unified-security-audit && node validate-findings.test.cjs && node validate-coverage-ledger.test.cjs
```

[`evals/`](evals/) holds a shadow-audit benchmark: blind runs on code with publicly known bugs, scored for recall and precision with `evals/score.py`. It starts with three Circom cases from zkbugs. No results are recorded yet, so the repo makes no accuracy claims.

## License and attribution

This repository has two licences:

- `skills/security-auditor/` is **CC BY-SA 4.0**, because it adapts Trail of Bits material. See its [`NOTICE.md`](skills/security-auditor/NOTICE.md) for sources.
- `skills/circom-auditor/` is **MIT, © 2026 zkSecurity** (see [its `LICENSE`](skills/circom-auditor/LICENSE)), from [zksecurity/zk-skills](https://github.com/zksecurity/zk-skills).
- `third_party/krait/` is **MIT, © 2025-2026 Zealynx Security** (see [`third_party/krait/LICENSE`](third_party/krait/LICENSE)).
- The other skills under `skills/` and the repository's own files are **MIT** (see [`LICENSE`](LICENSE)). `unified-security-audit` builds on [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) and [pashov/skills](https://github.com/pashov/skills), both MIT. Credits and changes are in [`skills/unified-security-audit/NOTICE.md`](skills/unified-security-audit/NOTICE.md).
- `third_party/trailofbits/` is © Trail of Bits, **CC BY-SA 4.0** (see [`third_party/trailofbits/LICENSE`](third_party/trailofbits/LICENSE)). It is copied unmodified. If you change and share these files, the changes must also be CC BY-SA 4.0.

See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) for the upstream commits.

These skills support human review and do not replace a formal audit.
