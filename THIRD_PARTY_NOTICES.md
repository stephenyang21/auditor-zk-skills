# Third-party notices

| Path | Upstream | Commit | License | Changes |
|---|---|---|---|---|
| `skills/circom-auditor/` | [zksecurity/zk-skills](https://github.com/zksecurity/zk-skills) (`skills/circom-auditor`, v0.1.0) | `f56ed63` | MIT, © 2026 zkSecurity | None. Licence added at `skills/circom-auditor/LICENSE`. |
| `third_party/krait/` | [ZealynxSecurity/krait](https://github.com/ZealynxSecurity/krait) | `76e5ac7` | MIT, © 2025-2026 Zealynx Security | Copied without `.git` and `node_modules`. In `patterns/web2-typescript/api-key-leakage.yaml`, two example Stripe-format keys were replaced with `sk_live_EXAMPLE_REDACTED_NOT_A_REAL_KEY` so secret scanning does not flag them. Its checklist plugin is listed in `.claude-plugin/marketplace.json` with source `./third_party/krait/checklist`. |
| `third_party/trailofbits/` | [trailofbits/skills](https://github.com/trailofbits/skills) | `196a907` | CC BY-SA 4.0, © Trail of Bits | None. Copied as is, except the `.git` directory. This repository's `.claude-plugin/marketplace.json` lists its plugins with `source` paths rewritten to `./third_party/trailofbits/plugins/<name>`. |
| `skills/unified-security-audit/` (backbone) | [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | `c1c8a8c` | MIT, © Cloudflare, Inc. | See `skills/unified-security-audit/NOTICE.md`. |
| `skills/security-auditor/` (adapted material) | trailofbits/skills, cloudflare/security-audit-skill, pashov/skills, zksecurity/zk-skills, ZealynxSecurity/krait | see `skills/security-auditor/NOTICE.md` | CC BY-SA 4.0 for the combined skill | See `skills/security-auditor/NOTICE.md`. |
| `skills/unified-security-audit/pashov/` and adapted files | [pashov/skills](https://github.com/pashov/skills) | `eacfc09` | MIT, © AI Skills Contributors | See `skills/unified-security-audit/NOTICE.md`. |

To update the Trail of Bits copy, replace `third_party/trailofbits/` with a fresh checkout without `.git`, regenerate its plugin entries in `.claude-plugin/marketplace.json`, run `claude plugin validate .`, and update the commit above.
