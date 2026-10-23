# Notice

`security-auditor` is licensed under **CC BY-SA 4.0** (see `LICENSE`), because it adapts material from Trail of Bits' skills, which use that licence. If you share modified versions of this skill, they must also be released under CC BY-SA 4.0.

## Sources

| Source | Licence | Used in |
|---|---|---|
| [trailofbits/skills](https://github.com/trailofbits/skills) @ `196a907`, © Trail of Bits | CC BY-SA 4.0 | Function context records and "nothing found" assumptions (audit-context-building); verification procedure, gates, false-positive checklist, class-specific checks (fp-check); triage brocards (vulnerability-triage-brocards, after William Woodruff's "Brocards for vulnerability triage"); variant method (variant-analysis); diff mode (differential-review); sharp edges and insecure defaults; weird-token checklist and non-EVM chain lenses (building-secure-contracts); dimensional analysis; C/C++, Rust, constant-time, and zeroization question sets (c-review, rust-review, constant-time-analysis, zeroize-audit); property-based testing guidance. |
| [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) @ `c1c8a8c`, © Cloudflare, Inc. | MIT | Operating modes, safety rules, boundary-and-result requirement, three verdicts, coverage planning and critic waves, prior-run reuse, profiles and budget, core attack classes, severity anchors, report structure. Files copied with only their cross-reference names changed: `references/domains/*.md`, `scripts/validate-findings.cjs`, `scripts/report-schema.json`. |
| [pashov/skills](https://github.com/pashov/skills) @ `eacfc09`, © AI Skills Contributors | MIT | Attacker mindset and reasoning tools (senior-auditor SOP); 12 smart-contract lenses and judging gates (solidity-auditor); multi-pass known-findings rule; Simplified Technical English finding language; invariant synthesis, entry-point classification, threat profile, and readiness verdict (x-ray); stateful fuzzing guidance (fizz). Scripts copied unchanged: `scripts/entry_points.py`, `scripts/analyze_git_security.py`, `scripts/enumerate.sh`. |
| `circom-auditor` (this repository), © stephenyang21 | MIT | ZK circuit lens (`references/lenses-zk.md`). |

The MIT licence notices for the Cloudflare and Pashov material are reproduced in `licenses/`. New material in this skill (`SKILL.md`, the workflow structure, `scripts/check_coverage.py`, and the merged reference files) is © stephenyang21 and released under CC BY-SA 4.0.
