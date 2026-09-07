---
title: "26. Dependency Injection"
description: "Three lifetimes as claims the container enforces only where it can see them, the long-lived service that silently promotes a short-lived one, and why nobody disposes what the container made"
type: lesson
---

# Lesson 26. Dependency Injection

**Mission link:** A typed, tested service is assembled by a container you did not write, from registrations you did. Getting the implementation wrong fails on the first request. Getting the lifetime wrong compiles, passes a smoke test, and then serves one user's data to another under load, which is why this lesson spends most of its time on the second kind of mistake.
**Primary source:** [Docs: "Dependency injection guidelines", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection-guidelines)
**Prerequisites:** [Lesson 25](0025-routing-and-middleware.md), [Lesson 22](0022-xunit-and-nunit.md), [Lesson 6](0006-exceptions.md)

## Warm-up

1. ▢ Lesson 23 stopped one step short: a class takes `IPaymentGateway` in its constructor, and a test passes a substitute. Who passes the real one?

<details markdown="1"><summary>Check</summary>

Nothing you wrote. Something else constructs the class and supplies the argument, and that something is this lesson's subject. Constructor injection is the same mechanism in both cases; only the supplier changes.

</details>

2. ▢ Under xUnit, what decides how long a test class instance lives, and what question did that force you to ask?

<details markdown="1"><summary>Check</summary>

The framework does: one instance per test. The question it forced was what survives between tests, and which things you want shared badly enough to ask for it by name. Replace "test" with "request" and you have this lesson.

</details>

3. ▢ What does a `using` statement decide, and who decides it?

<details markdown="1"><summary>Check</summary>

When `Dispose` is called: at the end of the block, including on the way out through an exception. The code holding the object decides. Worth noticing now, because for objects that arrive through a container that decision is no longer yours.

</details>

## Know this

**A registration says two things, and only one of them fails loudly.** Which implementation to use, and how long an instance may live ([Dependency injection in ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection)):

```csharp
builder.Services.AddTransient<IOperationTransient, Operation>();
builder.Services.AddScoped<IOperationScoped, Operation>();
builder.Services.AddSingleton<IOperationSingleton, Operation>();
```

Name the wrong implementation and the first request tells you. Name the wrong lifetime and nothing tells you, because a lifetime is not a promise the type system can check.

**Scoped is the lifetime a service revolves around, and it is defined by the scope, not by the request.** In an app that processes requests the scope is usually the request, but the mechanism is an `IServiceScope`, and two documented consequences follow from that being the real rule. First, if a scoped service is created in the root container, **the service's lifetime is effectively promoted to singleton**, because only the root container disposes it, at shutdown ([.NET dependency injection](https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection)). Second, stated as an anti-pattern in its own right: when you are **not creating a scope or within an existing scope, the service becomes a singleton**.

Both sentences describe the same failure. A scoped registration does not make anything scoped; being resolved inside a scope does.

**Captive dependency: the case that reads as correct.** The term, coined by Mark Seemann, is for **a longer-lived service holding a shorter-lived service captive**. The documentation's example is a singleton `Foo` whose constructor takes a scoped `Bar`, and its verdict is that this **seems valid on the surface** and is a misconfiguration: `Foo` is instantiated once and holds that one `Bar` for its whole lifetime.

|Holder|Held|What happens|
|---|---|---|
|Singleton|Scoped|**Misconfiguration.** One instance is captured for the application's lifetime, and the shorter lifetime is silently promoted|
|Singleton|Transient|Allowed, but the instance lives as long as the singleton, and the documentation warns it **might also require thread safety** depending on how the singleton uses it|
|Scoped|Transient|The transient lives as long as that scope|
|Anything|Something longer-lived|Fine, since nothing is being held past its intended life|

**There is a check, and it is worth knowing exactly how far it reaches.** When an app runs **in the development environment** and builds its host with `CreateApplicationBuilder`, the default service provider verifies that scoped services are not resolved from the root service provider and are not injected into singletons. You can also ask for it directly by passing `validateScopes: true` to `BuildServiceProvider`, which produces an `InvalidOperationException`.

Read the qualifier rather than the promise. This is a development-environment check on the container's own graph. It is a good reason to run the app in Development before shipping, and not a reason to believe the shape of your lifetimes has been proved.

**Middleware is where this bites first, and lesson 25 already set it up.** A middleware's position in the pipeline is fixed at startup, and so is its construction: it is built once for the application, not once per request. So the documentation gives a rule with a reason attached. To use scoped services in middleware, **inject the service into the middleware's `Invoke` or `InvokeAsync` method**, because **using constructor injection throws a runtime exception: it forces the scoped service to behave like a singleton**. The alternative is factory-based middleware, which is **activated per client request**, and can therefore take scoped services in its constructor after all.

**Disposal is not your job, and doing it anyway is the bug.** The container is responsible for cleanup of the types it creates, calling `Dispose` on `IDisposable` and `DisposeAsync` on `IAsyncDisposable`, and **services resolved from the container should never be disposed by the developer**. The schedule follows the lifetime: transient and scoped instances are disposed **at the end of the scope in which they were resolved**, typically the end of the request, and singletons when the container itself is disposed, usually at application shutdown.

Three guidelines fall out of that, and the third is the one that catches careful people:

- Do not register `IDisposable` instances with a transient lifetime; use a factory so the instance can be disposed deliberately.
- Do not resolve transient or scoped `IDisposable` instances in the root scope.
- **Receiving an `IDisposable` dependency through DI does not require the receiver to implement `IDisposable`**, and the receiver **should not call `Dispose` on that dependency**.

Also worth filing away, because it contradicts an intuition most people have: **scopes are not hierarchical, and there is no special connection among scopes.**

**Thread safety, stated as narrowly as the documentation states it.** Resolving services from the built-in container is thread-safe: once an `IServiceProvider` or `IServiceScope` is built, it is safe to resolve from several threads. The note attached to that is the part to keep, because thread safety **of the container only guarantees that constructing and resolving services is safe**, and **any service, especially a singleton, that holds shared mutable state must implement its own synchronization logic if accessed concurrently**. Choosing `AddSingleton` is choosing to write that synchronization.

**Two recommendations to adopt now rather than learn later.** Avoid the service locator pattern: do not call `GetService` to fetch an instance where DI would have supplied it, and treat injecting a factory that resolves dependencies at run time as the same mistake in a better coat. And avoid storing data or configuration in the container, which has its own mechanism.

**One forward pointer.** That mechanism is the options pattern, which is lesson 27. Lesson 28 is Entity Framework Core, whose `DbContext` is the scoped service this lesson has been describing in the abstract, and 29 assembles the whole thing into something testable, which is where stage 6's capstone lands.

## Practice

1. ▢ A caching service is registered with `AddSingleton` and takes a repository registered with `AddScoped` in its constructor. It compiles and the first request works. What is this called, what is actually happening, and when do you find out?

<details markdown="1"><summary>Check</summary>

A **captive dependency**: a longer-lived service holding a shorter-lived one captive. The cache is instantiated once, so it captures one repository instance and keeps it for the application's lifetime, which promotes that repository's effective lifetime from per-scope to per-application.

When you find out depends on what the repository holds. If it holds per-request state, you find out when two requests interleave and one sees the other's data, which is a load-dependent bug that a smoke test cannot produce. If it holds a database context, you find out when it has accumulated tracked entities for hours.

The one thing that would have told you early is running the app in the development environment, where the default provider checks that scoped services are not injected into singletons, or asking for the same check explicitly with `validateScopes: true` and getting an `InvalidOperationException`. Note what that means in reverse: an app whose first run in a Development environment is never performed has no such check.

</details>

2. ▢ A middleware takes a scoped service in its constructor. It throws at run time. Why, and what are the two documented ways to fix it?

<details markdown="1"><summary>Hint</summary>

Lesson 25 said where a middleware sits is fixed at startup. Ask when it is built.

</details>

<details markdown="1"><summary>Check</summary>

Because a middleware is constructed once for the application, so constructor injection **forces the scoped service to behave like a singleton**, and the documentation says that throws a runtime exception rather than quietly allowing it. This is the captive dependency of item 1, in the one place the framework refuses it outright.

The two fixes are documented side by side. Inject the service into `Invoke` or `InvokeAsync`, so it is resolved per request from that request's scope. Or use factory-based middleware, which is activated per client request, and can therefore take the scoped service in its constructor.

The useful generalisation: ask how often a thing is built before deciding what it may hold. That question has now been asked of a test class, a middleware and a service, and given a different answer each time.

</details>

3. ▢ A service receives an `HttpClient` through DI and implements `IDisposable` to dispose it in `Dispose`, on the reasoning that whatever holds a disposable should release it. What is wrong?

<details markdown="1"><summary>Check</summary>

Both halves. **Receiving an `IDisposable` dependency through DI does not require the receiver to implement `IDisposable`**, and the receiver **should not call `Dispose` on that dependency**. The container is responsible for cleaning up what it created, and services resolved from it should never be disposed by the developer.

The reasoning being applied is lesson 6's, and it was right there: the code holding the object decides when it is released. What changed is ownership. The object did not come from a `new` you wrote, so the lifetime is not yours to end, and ending it early hands the next scope an already-disposed instance if the registration is a singleton.

The container's own schedule is worth memorising instead: transient and scoped instances are disposed at the end of the scope in which they were resolved, which in a request-processing app is usually the end of the request, and singletons when the container is disposed at shutdown.

</details>

4. ▢ A background job resolves a scoped service directly from the application's root provider rather than creating a scope. The registration still says `AddScoped`. What lifetime does it actually have?

<details markdown="1"><summary>Check</summary>

Singleton, in effect. A scoped service created in the root container has **its lifetime effectively promoted to singleton**, because the root container is the only thing that will dispose it, and that happens at shutdown. The documentation names the general case separately: when you are not creating a scope or within an existing scope, the service becomes a singleton.

So `AddScoped` is not a property of the service. It is an instruction about what happens when the service is resolved inside a scope, and resolving it outside one does not fail, it just does something else. The fix is to create an `IServiceScope` for the unit of work and resolve inside it, remembering that scopes are not hierarchical and have no special connection to one another.

</details>

5. ▢ Which statement is correct?

    - a) The container disposes singletons only, so transient and scoped instances must be disposed by whoever resolved them
    - b) A singleton taking a scoped dependency holds one instance of it for the application's lifetime, and the development-time scope check reports that as an error
    - c) Resolving services from the container is thread-safe, so the singleton instances it returns are thread-safe as well
    - d) Injecting a scoped service into a middleware constructor is the documented way to use scoped services in middleware

<details markdown="1"><summary>Check</summary>

**b)** That is the captive dependency, and the check that catches it runs in the development environment, or on demand with `validateScopes: true`.

(a) is backwards: transient and scoped instances are disposed at the end of the scope in which they were resolved, and services resolved from the container should never be disposed by the developer. (c) overreads the guarantee, which covers constructing and resolving only; a service holding shared mutable state must implement its own synchronization. (d) is the thing that throws, and the documented ways are `Invoke`/`InvokeAsync` injection or factory-based middleware.

</details>

## Real-world reps

- [ ] Open a `Program.cs` you have access to and list its registrations by lifetime. For each singleton, name what it holds.
- [ ] Find one singleton with mutable state and decide whether anything synchronises access to it.
- [ ] Tomorrow: find a class that both receives a dependency through DI and implements `IDisposable`. Work out which of the two disposables it actually owns.

## Going further

- [Docs: "Dependency injection guidelines", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection-guidelines)
- [Docs: "Dependency injection in ASP.NET Core", Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection)
- [Docs: ".NET dependency injection", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
