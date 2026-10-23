# General Lenses

#### When to use this file

Always. These classes apply to every codebase. Domain and lens files add depth for specific boundaries; they never replace these. Split large targets per subsystem and per class.

## Core discipline (include in every hunter prompt that uses this file)

```
- A flag is not a finding. Trace from attacker-controlled input to a real effect on someone else, past every control on the path.
- Name the right check for the right resource via the right mechanism. That a permission check exists says nothing about whether it is the correct one.
- Data you validated on the way in is untrusted when a different path wrote it, or when it re-enters a new context (second-order).
- Read the default, not the name. Ask what happens when configuration is absent, empty, zero, or null; the unconfigured state is often the insecure one.
- Intended same-principal authority, self-impact, and documented behavior used as documented are not findings.
```

## Core classes

**Injection**
Trace untrusted input to a dangerous sink. Web: SQL/NoSQL, HTML, shell, templates, file paths, redirects, deserialization, LDAP/XPath, headers. Libraries: buffer operations, parsers, format strings. CLIs: command construction, path handling, environment interpolation. Services: queries, message serialization, logs, caches, search indexes, analytics. Look for indirect injection (stored safely, used unsafely elsewhere) and injection through keys, field names, headers, and metadata, not just values.

**Access control**
Verify that a caller cannot exceed its authority: a second path to the same state change with a weaker check; request-body fields that override what the permission system restricts; endpoints that check authentication but not authorization; one resource with several access paths and inconsistent checks; bulk, batch, export, and import paths that skip per-item checks; IDs that are guessable or caller-chosen with no ownership check (IDOR). For complex models, split authentication bypass from authorization logic.

**Business logic**
Hunt logic errors by hand; scanners do not find them. State machines: skip steps, go backwards, replay a completed flow, recover from partial failure without rollback. Races with business impact: check-then-act without atomicity (double spend, double approve, lost update). Numbers: negative, zero, overflow, precision loss, string/number coercion. Implicit trust in data from storage, config, other components, or plugins. Time: expiry, scheduling, rate windows, clock skew, exact boundary moments. Default and fallback posture: missing config, a disabled feature flag, an unavailable dependency, a system mid-migration.

**Resource and file handling**
Path traversal (symlinks, encoded sequences, null bytes); SSRF (redirects, DNS rebinding, URL-parser differentials); unsafe deserialization, archive extraction (zip slip), temporary files; TOCTOU between a check and a use on the filesystem.

**Cryptography and secrets**
Weak randomness for tokens, keys, or nonces; hardcoded secrets, or secrets in logs, errors, URLs, or client responses; broken key derivation, missing MAC verification, nonce reuse; non-constant-time comparison of secrets; primitive misuse (ECB, unauthenticated encryption, static IVs); crypto failures that fall back to no crypto. For implementation-level timing and memory hygiene, add `lenses-native-crypto.md`.

**Feature abuse and data leakage**
Export, backup, or snapshot as exfiltration (data above the caller's level, other users' data, deleted or private content). Import or restore as injection (overwrites, records that skip validation, writes to collections the caller cannot write). Search, filter, and sort as an oracle for hidden data. Enumeration through error, timing, size, or status differences. Preview or draft tokens that unlock more than one item. Notification, webhook, or callback URLs as SSRF.

**Chained vulnerabilities and trust boundaries**
Connect concrete outputs into later trust decisions: multi-step boundary failures; the exact guarantee component A produces vs what component B assumes (truncation, coercion, normalization, tenant scope); second-order use (a field name becomes a JSON path, a slug becomes a file path, stored text becomes a template or URL); token, key, plugin, OAuth, MCP, or agent scope growth after delegation, refresh, caching, or role change; setup, migration, soft-delete, revoke, and cache-expiry windows; undelete, restore, and rollback without current authorization.

**Sharp edges**
APIs and configurations where the easy path is the insecure one.
- Algorithm or mode chosen by untrusted input (JWT `alg: none`, RS256→HS256 confusion, caller-selected hash or cipher).
- Dangerous defaults: `timeout=0`, `max_attempts=0`, `key=""`, or null meaning "accept all"; boolean defaults that disable a control; negative values with undefined meaning.
- Primitive APIs that take raw bytes or strings for keys, nonces, ciphertexts, and signatures, so arguments can be swapped without a type error; `==` on MACs where a constant-time compare exists.
- Configuration cliffs: one option or combination that silently drops protection (a `verify=False` reachable from config; a permissive and a strict flag where the permissive one wins).
- Silent failures: errors swallowed into success, validators that return a falsy value instead of raising, `catch {}` around security checks.
- Stringly-typed security: roles, scopes, permissions, or URLs compared as strings with prefix, case, or Unicode ambiguity.

**Insecure defaults**
Report only when the insecure value is what the running system actually uses.
- **Fail-open switches**: a security control off when its config is absent (`REQUIRE_AUTH = env("REQUIRE_AUTH", "false")`). Skip it if the unconfigured value is the secure one, or the flag is never consulted where enforcement happens.
- **Fallback secrets**: a literal default feeding signing, encryption, session, or token machinery (`env.get("SECRET_KEY", "dev-secret")`). The finding is that the app *runs* with it; `env["X"]` crashing is safe.
- **Default credentials**: seeded admin accounts, example passwords, or test keys that work in production builds.
- **Debug and introspection**: stack traces, driver errors, debug servers, or admin consoles reachable by lower-privileged parties, whether default-on or unconditional. You need both the default *and* an exposure path.
- **Permissive access**: `public-read` ACLs, world-writable modes on sensitive files, `Access-Control-Allow-Origin: *` with credentials, open bind addresses for internal services. Ask who gains access, not how wide the value looks.
- **Weak crypto defaults**: MD5/SHA-1 for integrity or passwords, small keys, ECB, TLS verification off by default.

**Wildcard**
No assigned category; find what the others miss. Read the strangest code and ask why it exists. Look at half-finished, experimental, or bolted-on features; API calls the UI never makes; hidden or undocumented routes, parameters, and headers; features mixed in ways their designers did not plan for (localization + preview + caching; import + plugins + webhooks); reverted security fixes and commented-out checks in git history; irreversible actions and their confirmation binding; assumptions about the environment (local DB, accurate clock, trustworthy DNS, case-sensitive filesystem); and what the tests do *not* test. Verify every "this is safe because…" comment. Read anything named `temp`, `hack`, or `legacy` closely.

**Obvious things**
Thorough and literal; check every item and report each result after tracing impact. Hardcoded secrets (`password`, `secret`, `apikey`, `token`, `Bearer`, `-----BEGIN`); security TODO/FIXME/HACK comments; debug or dev mode reachable in production by env var, query parameter, or header; test or seed credentials that work in production; unprotected `/debug`, `/admin`, `/metrics`, `/env`, `/config`, `/.env`; committed `.env`, `*.pem`, `*.key`, `credentials.json`; a `.gitignore` that misses secrets; unpinned dependencies or known-CVE lockfile entries; `eval`, `exec`, `Function()`, `child_process`, or dynamic `import()` with dynamic input; wildcard CORS with credentials; cookies missing `HttpOnly`, `Secure`, or `SameSite` (only if the cookie is sensitive and JS doesn't need it); open redirects (`redirect`, `return`, `next`, `url`, `goto`); HTTP-only endpoints; stack traces or SQL errors in production responses.

## Universal moves (apply across the above)

- Map the principals, the assets, every writer of each security-relevant value, and every sink. Then connect the lowest-trust principal at the start to an asset at the end.
- Start at sinks and side effects and work backward through controls; start at entry points and work forward through transformations. Meet in the middle.
- For every control, find the parallel path that reaches the same effect: batch, admin/force, legacy, retry, async/queued, import, migration, error handler. The strongest control must apply after inputs are final and before every effect.
- Compare each component's actual guarantee with what the next component assumes.
- Treat masking code as a lead: clamps to zero, swallowed exceptions, `min`/`max` caps, and early returns that exist because a value "shouldn't" be out of range. Ask which invariant broke to make that code necessary, and whether an attacker can drive it.
- Run a "what's missing" sweep: inverse operations (set/unset, grant/revoke, lock/unlock), restriction coverage on every exit path, paired validation (create validates; does update?), and safe behavior when a parameter changes under existing state.

## Validation rules (apply before reporting ANY finding here)

1. Name the attacker and their starting capability, the input they control, the control that should stop them, the boundary, the affected principal or asset, and the observed result.
2. The trace runs from a real lower-trust entry point to the claimed sink, with every control on the path read and shown to fail.
3. Do not strengthen the effect: a crash is not code execution, ordinary load is not shared outage, and a same-principal action is not privilege gain.
4. A deployment, proxy, provider, browser, or identity fact that the source does not show, but that decides the claim, makes it `needs_validation` with that fact named.
5. Defense-in-depth advice without a reachable violation is hardening, not a finding.
