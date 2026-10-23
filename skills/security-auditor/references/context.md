# Step 1 — Map the system

Build understanding, not verdicts. Nothing in this step names a vulnerability or a fix. When code relies on something nobody checks, write that down plainly; hunting decides whether it matters.

## 1. Launch in parallel

**Deterministic scripts** (run by the parent; they only read the target):

- Solidity: `python3 -I <skill-dir>/scripts/entry_points.py <src-dir>`. It reads whole function headers, so formatter-split headers are not missed. `bash <skill-dir>/scripts/enumerate.sh <root> <src-dir>` gives file, nSLOC, and test inventory.
- Any Git repo: `python3 -I <skill-dir>/scripts/analyze_git_security.py --repo <root> --src-dir <src-dir> --json <out>/context/git-signals.json`. It reports fix-like commits, changes to dangerous areas, late changes, forked dependencies, tech debt, and hotspots.
- Other stacks: list routes, handlers, RPC methods, CLI commands, message consumers, and exported functions with `rg`. Prefer framework registries (router tables, IDL/ABI, protobuf services, `#[program]`, `Msg` services) over guesses.

**Installed static analyzers** (optional, local only, never installed by you). Run Semgrep, CodeQL, Slither, Aderyn, cargo-audit/cargo-geiger, gosec, bandit, Tealer, or Caracal only if one is already present and its database or build needs no network. Treat every hit as a **lead**, not a finding. Write them to `tool-leads.md` with `file:line` and the rule ID.

**Recon agents** (`research` role, read-only, return facts with `file:line`):

```text
1a PRODUCT & STACK — Product type, users, operators, and trust-sensitive actions.
   Languages, frameworks, build and test commands that run offline with present
   dependencies (do not run them), deployment modes visible in source, comparable
   software, and missing toolchains.
1b PRINCIPALS & CONTROLS — Every lower-trust principal and its intended authority.
   Authentication and authorization at each surface, per-resource and tenant scope,
   privilege changes, revocation, recovery, and fallback paths. For each control,
   say whether it is source-visible or depends on an unobserved deployment fact.
1c SURFACES & SINKS — Every place external or lower-trust input enters (HTTP, RPC,
   messages, files and archives, CLI/env/config, plugins and dependencies, CI, cloud
   events, model context and tool calls, deep links, IPC, contract calls, cross-chain
   messages). For each, trace the major transformations, stored copies, and
   security-relevant sinks, and note parallel paths to the same effect.
1d LOCAL PROOF CAPABILITY — Which tests or fixtures can validate boundaries with
   dummy data, and whether this machine can enforce the SKILL.md sandbox controls.
   List commands that would fetch dependencies, publish, or touch shared state, and
   mark them prohibited.
```

Add one focused recon agent per materially distinct subsystem or deployment mode these four do not cover.

## 2. Function context records (hot code)

For value-moving, authorization, parsing, and cryptographic functions, have agents write one record per function to `<out>/context/functions/<name>.md`, returning only a one-line index entry. Each record has these parts:

- **Guarantees**: what is always true after the function returns, each with the line that shows it.
- **Assumptions**: what the function takes on faith, each with what establishes it. If nothing does, write **`nothing found`**.
- **Calls**: each callee, what the caller needs from it, and whether the callee actually provides it. Follow the calls: read the callee along every path, not just the success path. A limit "looks enforced" because the value came back from a function whose name suggests a check.
- **Open questions**: what is still unclear. An honest open question beats a confident wrong answer.

Copy every `nothing found` assumption to `assumptions.md`. When two records disagree, quote both and leave them unreconciled; that disagreement is a fact about the code.

## 3. Entry-point classification

For each entry point, record the caller class (permissionless / authenticated user / role-gated (name the role) / admin / initializer / internal-only), the parameters with their trust level (user-controlled, user-signed, operator-provided, derived), the downstream call chain, the state modified, the value flow (in/out/none), and the reentrancy, CSRF, or replay guard if relevant. A function with no modifier but with an inline `msg.sender`/session/role check is gated, not permissionless; read the body before classifying it. Then build **flow paths**: for each major value- or privilege-moving entry point, chain its preconditions back to the writers of those preconditions, and back to deployment or setup. The scan output wins over any summary.

## 4. Invariant synthesis

Write `invariants.md` as heading blocks (`#### G-N`, `#### I-N`, `#### X-N`, `#### E-N`) so later files can cite them.

- **G — enforced guards.** Every `require`/`assert`/`if-revert`/validation that references persistent state, quoted with `file:line` and a one-line purpose.
- **I — single-component invariants.** Derive them by walking:
  1. **Conservation**: Δ-pairs written in the same function (`Δ(total) = +x`, `Δ(bal[u]) = +x`). If any writer touches one side without the other, record partial conservation. A flow that should move value but has no Δ is a negative-conservation observation.
  2. **Guard lift**: for each guard, ask whether it implies a property that must hold across all calls ("every position ≥ MIN"). If so, find every write site of that variable. If all sites enforce the guard → `enforced: yes`. If any site lacks it → `enforced: no`, citing the unguarded write. This is the highest-signal output.
  3. **Ratio**: `A = B * C / D` formulas, noting whether snapshots are taken before or after other writes.
  4. **State machine**: one-shot latches and cycles. Drop toggles that can flip back.
  5. **Temporal**: comparisons of time or block against stored deadlines; checked-then-updated vs updated-then-checked.
  6. **Documented**: NatSpec, comments, and spec-stated global properties, tagged `(per spec)`, then confirmed or contradicted by the walks above.
- **X — cross-component.** A caller's assumption about a callee's state, where the callee can change that state on its own. Include both sides only when both are in scope.
- **E — economic / system.** Higher-order properties derived from cited I/X IDs; a property is `enforced: no` if any of its sources is.

Drop any row you cannot verify at the cited lines. "Could not verify" is not a row.

## 5. Threat profile and signals

- Classify the system (for example: web SaaS, API gateway, CLI, library, agent/tool runtime, vault, AMM, lending market, bridge, perps, staking, governance, NFT market, rollup or circuit). Write down that class's typical adversaries and attack goals, its lifecycle phase (pre-launch, live, upgrade), and its external dependencies (identity providers, queues, oracles, tokens, bridges, hooks). For on-chain code, list centralization: for each privileged role, which actions are instant vs timelocked, which can redirect funds, and which are pausable.
- From `git-signals.json`: reverted or re-applied security fixes, guards removed, late changes to dangerous areas, and forked dependencies. Each one becomes a lead.
- Code kept only for backward compatibility counts only when it has no active callers, no comment says it is intentional, and history shows its mechanism was removed.

## 6. Domain routing

Select a lens or domain file because recon found the boundary it describes, not because a language or dependency name appears.

| Recon found | Select |
|---|---|
| Any software | `lenses-general.md` (always) |
| HTTP, sessions, OAuth/OIDC/SAML/JWT, MFA, API keys, proxies, caches | `domains/web-protocol-and-auth.md` |
| Browser, SPA, extension, webview, postMessage, CORS, DOM rendering | `domains/client-side.md` |
| IAM, IaC, containers, Kubernetes, serverless, ingress | `domains/cloud-and-deployment.md` |
| Dependencies, CI, release, signing, updates, plugins | `domains/supply-chain-and-release.md` |
| LLM, RAG, agent memory, tool calling, MCP | `domains/ai-and-llm.md` |
| gRPC, GraphQL, protobuf, custom protocols, queues, webhooks | `domains/protocols-rpc-and-messaging.md` |
| Untrusted work against shared CPU, memory, queues, quotas, spend | `domains/resource-exhaustion-and-availability.md` |
| Multi-tenant stores, caches, search, export, backup, deletion | `domains/data-isolation-and-lifecycle.md` |
| Native apps, deep links, exported components, daemons, local IPC | `domains/desktop-mobile-and-local-ipc.md` |
| C/C++/unsafe Rust, parsers, FFI, kernels, firmware, JITs | `domains/memory-safety-and-binary.md` + `lenses-native-crypto.md` |
| Cryptographic code, secret handling | `lenses-native-crypto.md` |
| Solidity/Vyper/EVM | `lenses-smart-contracts.md` |
| Solana, Cosmos, Substrate, Cairo, TON, Algorand | `lenses-other-chains.md` (+ `lenses-smart-contracts.md` for economic and math lenses) |
| Circom or other ZK circuits | `lenses-zk.md` |

The domain files say "Phase 1"; read that as this step. They are used alongside `lenses-general.md`. Hand hunters a domain file's `Core discipline`, its chosen class blocks, `Universal moves`, and `Validation rules`, all verbatim.

## 7. ARCHITECTURE.md (≤1,000 words)

1. The product, its principals with their intended authority, and the protected assets.
2. The comparable baseline, if one is source-grounded. Use it to calibrate, never to dismiss.
3. The stack, deployment paths, and offline build/test limits.
4. Entry surfaces and the key source-to-sink and lifecycle paths.
5. The trust boundaries, each with its strongest source-visible control.
6. Counts: `enforced: no` invariants and `nothing found` assumptions, with pointers to the files.
7. The selected lens and domain files, and the boundary that justifies each.
8. Prior-run gaps and revalidation targets.
