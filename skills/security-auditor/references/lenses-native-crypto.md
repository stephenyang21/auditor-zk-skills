# Native-Code and Crypto-Implementation Lenses

#### When to use this file

Reach for this file for C/C++ userspace, Rust (especially `unsafe`, FFI, concurrency, and async), and any code that implements or handles cryptographic secrets. Pair it with `domains/memory-safety-and-binary.md`, which holds the deep memory-safety, kernel, binary-loader, and JIT classes. This file supplies the per-language question sets and the two crypto-implementation lenses. Question groups are adapted from Trail of Bits' c-review, rust-review, constant-time-analysis, and zeroize-audit (CC BY-SA 4.0).

## Core discipline (include in every hunter prompt that uses this file)

```
- Fix the threat model first: REMOTE (network input), LOCAL_UNPRIVILEGED (another local user or sandboxed process), or both. A bug only a fully privileged local user can trigger is not a boundary crossing.
- C semantics are the substance, not the labels: integer promotion, signedness, width, implicit conversion, and undefined behavior decide whether a check works. Signed overflow is UB, so a post-hoc `if (a + b < a)` check may be deleted by the compiler.
- Unsigned subtraction that can go below zero wraps to a value that passes every upper-bound check written for the non-wrapping case. Check it at every size and index.
- Every call whose failure matters: is its result checked, against the convention that function actually uses? A negative return assigned to size_t makes the following check unreachable.
- In Rust, safe code that can drive `unsafe` code into UB is the bug, wherever the unsafe block is. Check every invariant an `unsafe` block or `unsafe impl` relies on against all safe callers.
- Prove with sanitizers (ASan/UBSan/TSan/MSan, Miri) or a minimal harness inside the sandbox. Without one, a memory-safety claim needs an exact byte-level trace.
```

## C and C++ question groups

**Memory bounds**
Buffer overflow and out-of-bounds read; `memcpy`/`memmove`/`memset` sizes (negative signed values converted to size_t, unchecked syscall returns, `sizeof` on a pointer); overlapping buffers; flexible array members.

**String handling**
Missing termination, `strncpy` that leaves strings unterminated, length vs size confusion, truncation that changes meaning.

**Format and input APIs**
Attacker-controlled format strings; ignored `snprintf` return values (truncation, or a later write past the end); the `*scanf` family leaving targets uninitialized on partial match; `%s` with no width; banned APIs (`gets`, `strcpy`, `sprintf`) fed attacker data.

**Object lifecycle**
Uninitialized data; null dereference; use-after-free, double free, and dangling pointers (including error paths that free and then continue); leaks that reach a DoS; struct fields that must stay consistent with each other.

**Integer safety**
Overflow, truncation, and signedness in size arithmetic: `n * sizeof(T)` unchecked; `a + b` compared after it has already wrapped; 64-bit lengths stored in `int`; growth patterns (doubling, header + body); out-of-bounds comparisons with mixed signedness.

**Conversions and undefined behavior**
Operator precedence (`&` vs `==`, shifts); type confusion through unions, casts, and tagged structs; UB the optimizer exploits (strict aliasing, shift overflow, null checks after dereference).

**Return values and errno**
Ignored allocation, open, verify, or write failures; the wrong success convention; failures logged but not propagated; `errno` read without being reset, or clobbered by the logging call; EINTR handling (retry, except `close`, which must not be retried).

**Files and sockets**
`open` flags (`O_NOFOLLOW`, `O_EXCL`, `O_CLOEXEC`), permissions, symlink and TOCTOU races, temp files, socket state machines, and file-descriptor reuse after close.

**Concurrency**
Data races, check-then-use on shared state, non-thread-safe library calls, and signal handlers that call async-signal-unsafe functions or touch shared state.

**Ambient state and DoS**
Missing access checks in privileged daemons; privilege drops in the wrong order or unchecked (`setuid` before `setgid`, unchecked return values); trusted environment variables (`PATH`, `LD_*`, `TMPDIR`); time handling; algorithmic and resource DoS.

**Library API contracts**
`qsort` comparators that are not total orders; regex APIs (catastrophic backtracking, unchecked match groups); `va_start`/`va_end` pairing.

**C++ lifetime and class semantics** (C++ only)
Two `shared_ptr` control blocks built from one raw pointer; raw pointers that outlive a `unique_ptr`; use after move; lambdas that capture by reference and outlive their scope; iterator invalidation; static initialization order; virtual calls in constructors and destructors; exception safety leaving invariants broken.

**Windows** (Windows targets only)
`CreateProcess` with unquoted paths or command-line injection; cross-process handles; token privileges; service DACLs; DLL planting and search order; path canonicalization (8.3 names, ADS, device names); installer races; named-pipe impersonation and squatting; legacy CryptoAPI misuse.

**Build hardening**
Missing stack protector, FORTIFY_SOURCE, PIE/ASLR, RELRO, NX, or CFI where the threat model makes exploitation of another bug practical. This class is hardening unless it combines with a real bug.

## Rust question groups

**Unsafe boundary**
Safe APIs that let callers violate an `unsafe` block's preconditions; `unsafe impl Send/Sync` on types that are not; `set_len` over uninitialized memory; reads of uninitialized or padding bytes; union type punning; references to packed fields.

**Memory safety in unsafe**
Out-of-bounds pointer arithmetic, use-after-free through raw pointers, double free and invalid free, dangling `CString::as_ptr`, `mem::forget` or skipped destructors that leak or double-drop, and panics during unwinding inside unsafe sections that leave state half-initialized.

**FFI**
ABI mismatch (`extern "C"` signatures, `repr(C)` padding, `bool`/enum validity), ownership across the boundary (who frees, with which allocator), panics unwinding across `extern "C"`, opaque pointers that lose lifetimes, closures passed as callbacks, and `dyn Trait` across FFI.

**Concurrency and async**
Atomic orderings too weak for the protocol; `static mut`; shared memory races; lock ordering and poisoning; blocking calls (`std::fs`, `std::sync::Mutex`, `thread::sleep`) inside async tasks; cancellation-unsafe code across `.await` (state mutated before an `.await` that may be dropped); `select!` bias that starves branches.

**Panic and recursion DoS**
`unwrap`/`expect`, slicing at non-char boundaries, out-of-bounds indexing, `RefCell` double borrows, and assertions reachable from untrusted input; unbounded recursion in deserialization, `Drop`, or `Display`/`Debug` that overflows the stack.

**Logic and conversions**
Arithmetic overflow in release builds (wraps silently); lossy `as` casts and `From`/`Into` impls; float edge cases (NaN, ±0, infinity) in comparisons and keys; `Ord`/`Eq`/`Hash` inconsistencies and keys mutated inside collections; non-constant-time comparison of secrets (`==` on `&[u8]`); serialize/deserialize struct mismatches; non-determinism where determinism is required.

**Input and OS**
`Path::join` with absolute or `..` components (path traversal); raw file-descriptor lifecycle; TOCTOU on filesystem checks; discarded `Result`s; unflushed `BufWriter` on drop; MSRV and deprecated APIs with known soundness bugs.

## Constant-time code

Use this when code computes on secrets: keys, plaintext, nonces, MAC tags, password hashes, or private scalars.
- **Secret-dependent branches**: `if`, `?:`, `&&`/`||` short-circuit, early `return`, or loop bounds that depend on secret data.
- **Secret-dependent memory access**: table lookups or array indexes derived from secrets (S-boxes, windowed exponentiation without constant-time selection).
- **Variable-time instructions**: `/` and `%` on secret-derived values (KyberSlash), and variable-latency multiply or shift on some targets.
- **Comparisons**: `memcmp`, `==`, `strcmp`, `Arrays.equals`, or early-exit loops on MACs, tags, or tokens. Require a constant-time compare (`CRYPTO_memcmp`, `subtle::ConstantTimeEq`, `hmac.compare_digest`, `crypto.timingSafeEqual`).
- **Compiler-introduced leaks**: the source looks branch-free, but the optimizer emits branches or `div`. Confirm by inspecting the emitted assembly (`-O2` and release profiles), not just the source.
Report only when the secret is attacker-relevant (a remote or co-located observer exists) and no vetted library owns the guarantee. Cache and microarchitectural channels are out of scope for static inspection; mark them needs_validation.

## Secret zeroization

Use this for C/C++/Rust code that holds keys, seeds, passwords, tokens, or PII in memory.
- Find every secret's allocation, copies (struct assignment, `memcpy`, `clone`, `Vec` growth that reallocates, `String` formatting), and lifetime end. Each copy needs wiping.
- A wipe must survive optimization. Plain `memset` before `free` or scope exit is a dead store the compiler may remove. Require `explicit_bzero`, `memset_s`, `SecureZeroMemory`, `OPENSSL_cleanse`, a volatile loop, or Rust `zeroize`/`Zeroizing`. Confirm with IR or assembly when possible.
- Check every exit path, including errors, early returns, panics, and exceptions.
- Check registers and stack spills, swap (`mlock`), core dumps, logging and `Debug`/`Display` impls, and `Drop` order. Rust `Copy` types and moves leave unzeroized copies behind.
Severity depends on an attacker who can read that memory later (another process, a crash dump, swap, a cold boot). A missing wipe in a short-lived CLI with no such reader is hardening.

## Universal moves (apply across the above)

- Start at every place untrusted bytes enter (parsers, decoders, network handlers, IPC, file loaders) and follow the length and index values, not only the data.
- For every allocation, find who frees it, on every path. For every lock, find every path that releases it.
- For every `unsafe` block, write down its safety precondition and find the safe caller that can break it.
- For every secret, trace its whole lifetime: creation, copies, comparisons, wipes.

## Validation rules (apply before reporting ANY finding here)

1. Name the threat model, the attacker-controlled input, the exact faulting operation, and the observed effect (sanitizer report, Miri error, crash with a controlled value, a timing-dependent branch in emitted assembly, a secret remaining in memory).
2. A crash is availability only. Claim corruption or code execution only when you demonstrated control over the corrupted value or target.
3. Respect compile-time bounds, API contracts, and earlier validation that make the condition mathematically impossible (see `verification.md` § False-positive checklist). Prove math bounds algebraically.
4. Without a sanitizer or harness run, a memory-safety candidate needs an exact byte-level trace, or it is needs_validation with the build blocker named.
