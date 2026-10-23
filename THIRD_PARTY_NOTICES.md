# Third-party notices

| Path | Upstream | Commit | License | Changes |
|---|---|---|---|---|
| `third_party/trailofbits/` | [trailofbits/skills](https://github.com/trailofbits/skills) | `196a907` | CC BY-SA 4.0, © Trail of Bits | None. Copied as is, except the `.git` directory. This repository's `.claude-plugin/marketplace.json` lists its plugins with `source` paths rewritten to `./third_party/trailofbits/plugins/<name>`. |
| `skills/unified-security-audit/` (backbone) | [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | `c1c8a8c` | MIT, © Cloudflare, Inc. | See `skills/unified-security-audit/NOTICE.md`. |
| `skills/unified-security-audit/pashov/` and adapted files | [pashov/skills](https://github.com/pashov/skills) | `eacfc09` | MIT, © AI Skills Contributors | See `skills/unified-security-audit/NOTICE.md`. |

To update the Trail of Bits copy, replace `third_party/trailofbits/` with a fresh checkout without `.git`, regenerate its plugin entries in `.claude-plugin/marketplace.json`, run `claude plugin validate .`, and update the commit above.
