---
title: Glossary
description: "Canonical terms for C#"
type: glossary
---

# C# Glossary

Canonical terms for owning a C# service, and for naming precisely where a Java instinct misleads.

## Terms

**ActivitySource / Activity**:
.NET's native tracing types, predating the OpenTelemetry spec: `ActivitySource` is what the spec calls a Tracer, `Activity` is what it calls a Span. `StartActivity()` returns `null` and skips allocating an `Activity` when no listener is registered, making instrumentation nearly free until an exporter is actually configured.
_Avoid_: assuming `StartActivity()` always allocates (it checks for a registered, interested listener first, and skips creation entirely when there is none)

**AllowAnonymous**:
An override that opts a specific endpoint out of a service's default authorization requirement, letting an unauthenticated caller reach it. Applied to lesson 39's health-check endpoints, since an orchestrator checking liveness or readiness never authenticates at all.
_Avoid_: assuming a health-check endpoint is reachable by default once authorization is required (every endpoint inherits the default requirement unless deliberately opted out)

**ArrayPool&lt;T&gt;**:
A cooperative, caller-managed pool of reusable arrays (`ArrayPool<T>.Shared` is the general-purpose instance): `Rent(n)` hands back an existing array of at least the requested size or allocates a new one, and `Return` puts it back. There is no finalizer that returns a forgotten array, so a missing `Return` is a real leak.
_Avoid_: assuming the pool cleans up a forgotten rental automatically (nothing reclaims an unreturned array; sustained forgetting depletes the pool and forces new allocations)

**ASP.NET Core JSON defaults**:
The settings ASP.NET Core configures on top of the bare `System.Text.Json` serializer for its own JSON formatter: camelCase property names, case-insensitive matching, and quoted-number deserialization, all different from the bare library's own defaults.
_Avoid_: assuming a serializer test built with a bare `JsonSerializerOptions` matches what an actual endpoint produces (the bare library defaults to unchanged casing and case-sensitive matching; only ASP.NET Core's own formatter reconfigures both)

**Authorization policy**:
A bundle of one or more requirements, evaluated by a handler against a user's claims, requested by an endpoint with `[Authorize(Policy = "...")]` or `RequireAuthorization(...)` rather than an inline permission check. The simplest form, claims-based presence checking, just confirms a named claim exists (`RequireClaim("EmployeeNumber")`), regardless of its value.
_Avoid_: conflating it with authentication (a policy is evaluated against the identity authentication already established; it never establishes identity itself)

**Background GC**:
The mode that lets managed threads keep running while a generation 2 collection proceeds on a dedicated background thread (one for workstation GC, one per logical processor for server GC). Only ever applies to generation 2; generation 0 and generation 1 collections are always non-concurrent.
_Avoid_: assuming it removes all pausing (a foreground GC can still suspend every thread if generation 0 or 1 needs to collect while a background generation 2 collection is running)

**Behavioral change**:
A change that keeps a member's public signature both binary- and source-compatible while its runtime behavior itself differs (a different exception type, a different computed result). Announced by neither a compile error nor a load failure, discoverable only by running the code.
_Avoid_: assuming a compiler or loader would catch this (it's the one category of breaking change that passes both checks silently)

**Binary compatibility**:
Whether an already-compiled consumer can load and run against a new version without recompiling. Adding a method doesn't affect it; removing or altering a public signature a compiled caller references does. Bumping only `AssemblyVersion`, with no public API text changed at all, is enough to break it on its own.
_Avoid_: assuming source compatibility implies binary compatibility (a change can recompile cleanly for everyone and still fail an already-built binary that never recompiles, the `AssemblyVersion` case)

**ClaimsPrincipal**:
The identity authentication produces, which authorization then evaluates a policy's requirements against. Authentication's whole job is providing this; authorization is a separate, distinct decision about what it's permitted to do.
_Avoid_: assuming authentication and authorization are the same check (identifying a caller and deciding what that caller may do are documented as separate concerns, the second relying on but distinct from the first)

**Dispose pattern**:
The full `IDisposable` implementation: a public, non-virtual `Dispose()` that calls `protected virtual void Dispose(bool disposing)` then `GC.SuppressFinalize(this)`, with a guard flag so a repeated call is a safe no-op. The `disposing` parameter is `true` from `Dispose()` itself (safe to touch other managed objects) and `false` from a finalizer (other managed objects may already be gone).
_Avoid_: putting cleanup logic directly in `Dispose()` (the logic belongs in the overridable `Dispose(bool disposing)`, so a derived class can extend it without changing the public entry point)

**DisposeAsyncCore**:
A `protected virtual ValueTask` method holding a non-sealed class's asynchronous managed-resource cleanup, awaited by the public `DisposeAsync()` before it calls `Dispose(false)` (not `true`, to avoid repeating the managed cleanup) and `GC.SuppressFinalize(this)`. A sealed class skips it and cleans up directly inside `DisposeAsync()`.
_Avoid_: calling `Dispose(true)` after it (that would redo the managed-resource cleanup `DisposeAsyncCore` already performed asynchronously)

**dotnet-counters**:
A lightweight, ad-hoc health-monitoring CLI tool that observes performance counters (`EventCounter`/`Meter`) on a running process, cheap enough to run continuously. Used to notice a symptom (CPU, GC, exceptions) before reaching for a deeper trace.
_Avoid_: using it to find a specific hot stack (it reports aggregate counters, not call stacks; that is `dotnet-trace`'s job)

**dotnet-trace**:
A cross-platform CLI tool that captures a diagnostic trace over a time window, producing a `.nettrace` file viewable as a call tree with Total/Self time per method. Its default profile samples call stacks statistically (~100 Hz), low overhead, at the cost of possibly undercounting a very fast, short-lived hot path.
_Avoid_: capturing from process launch (the first window mixes JIT warm-up and tiered recompilation into what should be a steady-state trace; capture after the service has served real traffic)

**Finalizer**:
A last-resort method the garbage collector calls before reclaiming an object, worth adding only when a class directly owns an unmanaged resource. Its job is to call `Dispose(false)` as a fallback for when nobody ever called `Dispose()`; `GC.SuppressFinalize(this)` inside a well-behaved `Dispose()` skips it entirely for that instance.
_Avoid_: adding one to a class that only holds other managed, already-disposable objects (it costs an extra step before reclamation for no benefit, since those objects should clean up themselves)

**Foreground GC**:
A generation 0 or generation 1 collection that runs while a background generation 2 collection is in progress, suspending every managed thread (including pausing the background collection) until it finishes.
_Avoid_: treating this as a failure of background GC (background GC only ever promised concurrency for generation 2; generation 0 and 1 were never concurrent to begin with)

**Generation (GC)**:
One of three age-based divisions (0, 1, 2) of the managed heap. Every new object starts in generation 0; surviving a collection promotes it to the next generation. The split lets a collection reclaim memory in a small, frequently-turned-over portion of the heap instead of the whole thing.
_Avoid_: assuming an object is collected once, wherever it lives (an object is repeatedly re-examined and promoted across generations until it either dies or reaches generation 2)

**Global packages folder**:
The local cache where a resolved NuGet package version is stored. Can hold onto a previously resolved version after a package is rebuilt and repacked, so a consumer's retest may silently keep running the stale, cached version until the cache is cleared.
_Avoid_: assuming a correct version number in a project file guarantees the newly rebuilt bits are what's actually running (the cache can still be serving an older resolution of that version)

**JsonSerializerContext**:
A source-generated, partial class (`[JsonSerializable(typeof(T))]`, optionally `[JsonSourceGenerationOptions(...)]`) whose settings are computed once at compile time instead of resolved through runtime reflection, needed for AOT compilation and faster than the reflection-based path. Constructing it with an explicit `JsonSerializerOptions` instance overrides the attribute's settings silently.
_Avoid_: assuming the attribute's settings always apply (the constructor overload taking an explicit `JsonSerializerOptions` instance uses that instance instead, regardless of what `[JsonSourceGenerationOptions]` specified)

**Large Object Heap (LOH)**:
A separate heap for objects above a size threshold, bypassing the generation 0 to 1 to 2 promotion path entirely. Sometimes called generation 3, but it is only collected as part of a generation 2 collection, never as cheaply as a small object dying in generation 0.
_Avoid_: assuming a large object gets its own cheap, frequent collection (it rides along with the most expensive kind of collection this system has, generation 2)

**Liveness check**:
A health check answering "has this process crashed and does it need to be restarted." Should exclude every dependency check (a slow-starting dependency is not a crash) so only an actual process failure fails it.
_Avoid_: running the same checks as readiness (a slow-but-not-broken dependency would then trigger an unnecessary restart, which hits the same slow startup all over again)

**Log level**:
The severity a log call states (`Trace`, `Debug`, `Information`, `Warning`, `Error`, `Critical`, or `None` to suppress everything), filtered against a configured minimum that decides what actually gets emitted. The minimum is a configuration value, not something the calling code needs to know or change per environment.
_Avoid_: hardcoding different log calls per environment (only the configured minimum level should change; the same `LogDebug`/`LogWarning` calls stay in the code everywhere)

**Memory&lt;T&gt;**:
A heap-safe wrapper over a contiguous region of memory, complementary to `Span<T>`: not a ref struct, so it can be a field, captured by a closure, or held across an `await`. Convert to a `Span<T>` via `.Span` for the synchronous window that needs the fast view.
_Avoid_: assuming it is just a slower `Span<T>` (it exists specifically for the scenarios `Span<T>`'s ref-struct restrictions rule out, not as a general-purpose alternative)

**MemoryDiagnoser**:
A BenchmarkDotNet diagnoser that reports bytes allocated per operation (via `GC.GetAllocatedBytesForCurrentThread`) and `GenX` columns for collections per 1,000 operations. Counts managed heap allocations only.
_Avoid_: assuming it counts every kind of allocation (`stackalloc`'d memory is never on the managed heap, so it never appears in the `Allocated` column at all)

**Message template**:
A logging call's fixed string with named placeholders (`"Getting user {UserId}"`), passed separately from its values so a structured logging provider keeps each placeholder as its own named, queryable property in the emitted log entry.
_Avoid_: string interpolation (`$"Getting user {userId}"` collapses everything into one flat string before the logger sees it, destroying the structure a template preserves)

**ObsoleteAttribute**:
Marks a member deprecated: `error: false` (default) produces a suppressible `CS0618` warning, `error: true` a `CS0619` compiler error, a deliberate escalation path rather than two unrelated settings. Every unconfigured obsoletion shares those standard IDs, so a custom `DiagnosticId` (plus a `UrlFormat` pointing at migration docs) is what lets one specific obsoletion be suppressed without silencing every other one in the project.
_Avoid_: suppressing the standard `CS0618`/`CS0619` diagnostic ID project-wide to acknowledge one deprecation (that silences every other unconfigured obsoletion too; give the one being acknowledged its own `DiagnosticId` instead)

**Pre-release version (NuGet)**:
Any version with a hyphenated suffix (`-alpha`, `-beta`, `-rc`, or any other string); NuGet enforces nothing about what the suffix means, only that its presence marks the version pre-release. Excluded from an ordinary restore by default; dropping the suffix produces the stable version, which then takes precedence.
_Avoid_: assuming NuGet checks or enforces a suffix's specific meaning (`-alpha` vs `-beta` vs anything else is a team's own convention, not something the tool validates)

**Readiness check**:
A health check answering "is this instance ready to receive requests right now." Can legitimately report unhealthy during a slow startup dependency without the process having crashed, which is exactly what should route traffic away from it without triggering a restart.
_Avoid_: conflating it with liveness (a failed readiness check should stop traffic, not restart the process; only a failed liveness check should do that)

**ref struct**:
A struct restricted so it can never be promoted to the managed heap: it cannot be boxed, cannot be a field of an ordinary class, cannot be the element type of an array, cannot be captured by a lambda or local function, and cannot be used across an `await` or `yield` boundary. `Span<T>` is the canonical example.
_Avoid_: treating the restrictions as independent rules to memorise (every one of them is the same guarantee stated a different way: a ref struct can never outlive the stack frame or memory it was created to view)

**Reference type**:
A type (every `class`) where assigning a variable of that type copies a reference, not the underlying data; two variables can point at the same object, and a mutation through either is visible through both.
_Avoid_: object type (ambiguous with C#'s `object` base type)

**Server GC**:
A GC flavor that collects across multiple threads, typically one per logical processor, built for a server application needing high throughput and scalability. Can cause contention when many processes each running server GC share the same small number of CPUs.
_Avoid_: assuming it is always the better choice for a service (many small processes sharing one host, each running server GC, compete for the same CPUs; workstation GC with concurrent GC disabled is the documented fix for that shape of deployment)

**Source compatibility**:
Whether existing source code still compiles successfully against a new version, a separate question from binary compatibility. Adding a member to a published interface is source-incompatible for any external implementer, whose code no longer satisfies the interface until the new member is added.
_Avoid_: assuming it's the same check as binary compatibility (a caller that only invokes through an interface, rather than implementing it, isn't affected by an interface-member addition the same way an implementer is)

**Span&lt;T&gt;**:
A type-safe, allocation-free view over a contiguous region of existing memory (an array, a string, a `stackalloc`'d buffer). Slicing produces another view over the same memory, never a copy. A ref struct, so it can never be stored on the heap or held across an `await`.
_Avoid_: assuming a slice copies data (a slice is a view over the same underlying memory; a write through it is visible through the original)

**stackalloc**:
An expression that allocates a block of memory directly on the stack, discarded automatically when the allocating method returns; never garbage collected, never explicitly freed. Since C# 7.2, assignable directly to `Span<T>`/`ReadOnlySpan<T>` without `unsafe`, since a ref struct's restrictions already guarantee it can't outlive that stack frame.
_Avoid_: sizing it from unbounded input (the stack is small and fixed, roughly 1 MB on a 64-bit process; overrunning it throws an unrecoverable `StackOverflowException` that terminates the process)

**Value type**:
A type (every `struct`, plus the built-in numeric types) where assigning, passing, or returning a variable of that type copies the entire value; two variables of a value type are always independent copies.
_Avoid_: primitive type (too narrow; a user-defined struct is a value type too)

**Workstation GC**:
The default GC flavor for a standalone app, collecting with essentially one thread. A hosted app's default flavor is decided by its host rather than always defaulting to workstation.
_Avoid_: assuming a hosted service always defaults to workstation GC (the host, such as ASP.NET Core, decides the default flavor a hosted app starts with)
