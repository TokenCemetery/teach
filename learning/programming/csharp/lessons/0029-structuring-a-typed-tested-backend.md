---
title: "29. Structuring a Typed, Tested Backend"
description: "The container as the seam a test replaces registrations through, the documented rule for choosing between a unit test and an integration test, and the stage 6 capstone of four defects that all compile"
type: lesson
---

# Lesson 29. Structuring a Typed, Tested Backend

**Mission link:** This is the lesson the mission named. Everything in it has already been taught: what a lifetime promises, where a middleware sits, where a setting comes from, what a context tracks. Structure is what you get when those four answers agree with each other, and the way to find out whether they do is to test the service through the same seam the container uses.
**Primary source:** [Docs: "Integration tests in ASP.NET Core", Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/test/integration-tests)
**Prerequisites:** [Lesson 28](0028-entity-framework-core.md), [Lesson 26](0026-dependency-injection.md), [Lesson 22](0022-xunit-and-nunit.md)

## Warm-up

1. ▢ Which lifetime does `AddDbContext` register, and what makes that the right one?

<details markdown="1"><summary>Check</summary>

Scoped. A context is a single unit of work, an HTTP request is usually a single unit of work, so tying one to the other matches the lifetime of the object to the lifetime of the job.

</details>

2. ▢ What does `IClassFixture<T>` give a test class, and what does the collection version cost?

<details markdown="1"><summary>Check</summary>

One instance of the fixture shared by every test in the class, created before any of them run and disposed after all of them finish. The collection version shares it across several classes, and puts those classes in one collection, so they stop running in parallel with each other.

</details>

3. ▢ Why can a substitution library not replace a dependency that a class constructs with `new`?

<details markdown="1"><summary>Check</summary>

Because there is nothing to intercept. A substitute is a proxy that implements an interface or overrides a member, and a constructor call inside the class is neither. The seam has to exist before the test can use it.

</details>

## Know this

**Structure here is not a new pattern. It is the four earlier answers not contradicting each other.** Stage 6 has asked four questions, and a service is structured when each is answered deliberately:

|Question|Answered by|The failure when it is not|
|---|---|---|
|How long may this object live?|the registration|a singleton holding a scoped context, promoting its lifetime silently|
|Where does this code sit in the pipeline?|the order of `Use` calls, against `UseRouting`|a middleware reading a null endpoint, or running only on a 404|
|Where does this value come from?|the provider order, bound to a validated options class|a setting that differs in production for reasons invisible in the code|
|What is one unit of work?|the scope, and the context inside it|parallel operations on one context, or an assignment written back by accident|

Notice that none of these produce a compiler error, and that all four have a documented detection mechanism attached. The point of structuring is to make each mechanism actually run.

**The seam a test uses is the container, not the class.** Lesson 23 said a substitute needs something to intercept, and lesson 26 said the container is what supplies a class's dependencies. Put those together and the testing strategy for a whole service follows: you do not replace a class, you replace a **registration**, and the rest of the application is assembled around your replacement exactly as it is in production.

**Two kinds of test, and the documentation gives the rule for choosing.** Unit tests test isolated components, using **fakes or mock objects in place of infrastructure components**. Integration tests **confirm that two or more app components work together to produce an expected result, possibly including every component required to fully process a request**, and cover infrastructure: database, file system, network appliances, and the request-response pipeline ([Integration tests in ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/test/integration-tests)).

The trade is stated plainly. Integration tests **use the actual components that the app uses in production**, require more code and data processing, and take longer to run. So: **limit the use of integration tests to the most important infrastructure scenarios**, and **if a behavior can be tested using either a unit test or an integration test, choose the unit test.**

**What an integration test needs, and where the pieces come from.** A test project that references the app being tested, which the documentation calls the **system under test** or SUT; a test web host with an in-memory `TestServer`, provided by the `Microsoft.AspNetCore.Mvc.Testing` package; and a test runner. The host is usually configured differently from the real one, using a different database or different settings.

The configuration point is a factory you inherit from:

```csharp
public class CustomWebApplicationFactory<TProgram>
    : WebApplicationFactory<TProgram> where TProgram : class
{
    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.ConfigureServices(services =>
        {
            // locate the app's database context registration, remove it,
            // and register one that points at a test database
        });
    }
}
```

`ConfigureWebHost` hands you the service collection, and the documentation's sample **finds the service descriptor for the database context and uses the descriptor to remove the service registration**, then adds a context configured for tests. That is the whole trick, and it is worth naming: the test edits the same list of registrations that lesson 26 was about, before the container is built.

**And the test class holds the factory the way lesson 22 said to hold anything expensive:**

```csharp
public class IndexPageTests :
    IClassFixture<CustomWebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public IndexPageTests(CustomWebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient(new WebApplicationFactoryClientOptions
        {
            AllowAutoRedirect = false
        });
    }
}
```

Every part of that has appeared before. `IClassFixture<T>` is lesson 22's class fixture, chosen because building a web host per test would be absurd. The factory arrives as a constructor argument because that is how xUnit supplies fixtures, which is the same shape as constructor injection everywhere else in this stage. `CreateClient` returns an `HttpClient` whose requests go through the real pipeline, so lesson 25's ordering is under test rather than assumed.

**One thing to be honest about.** An integration test exercises the pipeline, the routing and the wiring, and it does not prove your lifetimes are right. Its own host is configured differently from production, and a captive dependency that happens not to matter for a short-lived test process will pass. The scope check that catches those runs in the development environment, and it is a separate mechanism with a separate trigger. A green integration suite is evidence about behaviour, not about lifetime.

**One forward pointer.** Stage 6 ends here. Stage 7 is judgment: lesson 30 compares `async`/`await` with Java virtual threads and LINQ with the Stream API, and lesson 31 is about reading C# and naming what a construct is costing.

## Practice

1. ▢ An integration test needs the real pipeline but not the real database. What exactly does it replace, and at what moment?

<details markdown="1"><summary>Check</summary>

A registration, in `ConfigureWebHost`, before the container is built. Inheriting from `WebApplicationFactory<TProgram>` and overriding that method gives access to the service collection, and the documentation's sample locates the service descriptor for the database context, removes it, and adds one pointing at a test database.

What it does not replace is any class. `Program.cs` is untouched, the handlers are untouched, and the object graph is assembled by the same container using the same rules. That is why this works at all, and it is the reason lesson 26 was not merely background: a service whose components construct their own collaborators has no list of registrations to edit, so there is nothing for a factory to swap.

</details>

2. ▢ You can test a discount calculation either by calling the calculator directly or by sending a request through the test client and reading the response. Which, and on what grounds?

<details markdown="1"><summary>Check</summary>

The unit test, and the documentation states the rule rather than leaving it to taste: **if a behavior can be tested using either a unit test or an integration test, choose the unit test.**

The grounds are given too. Integration tests use the actual components the app uses in production, require more code and data processing, and take longer to run, so they should be limited to the most important infrastructure scenarios. A discount calculation is not infrastructure; it is a function of its inputs.

The useful reading of that rule is about what each kind of test tells you when it fails. A failing unit test names a method. A failing integration test tells you that a request did not produce the expected response, which is true of a routing mistake, a lifetime mistake, a configuration mistake and an arithmetic mistake alike.

</details>

3. ▢ A colleague proposes sharing one `CustomWebApplicationFactory` across every test class in the project, using a collection fixture. What do they gain and what do they pay?

<details markdown="1"><summary>Hint</summary>

Lesson 22 answered the second half, and the answer was not about memory.

</details>

<details markdown="1"><summary>Check</summary>

They gain one web host instead of one per class, which for an expensive factory is real. They pay parallelism: the default parallel mode is `collections` with one collection per class, so tests in different classes run in parallel today, and putting those classes in a shared collection is exactly what stops that. The suite gets one host and loses its concurrency.

There is a second cost specific to this case. A shared host means shared state in whatever the factory registered, including the test database, so tests that were independent because each had its own host now have to be independent by discipline. The v3 assembly fixture shares across the assembly without the parallelization change, which is the option worth checking before reaching for a collection.

</details>

4. ▢ Your integration suite is green. Which of stage 6's four failure modes could still be present?

<details markdown="1"><summary>Check</summary>

All four, to different degrees, and this is the question worth leaving the stage with.

A **lifetime** mistake most easily. The test host is configured differently from production, the process is short-lived, and a captive dependency whose damage needs sustained traffic will not show. The mechanism that catches it is the development-environment scope check, which is not the test suite.

A **configuration** mistake, because the test host deliberately uses different settings. Validation that only runs on first use will pass in a suite that never exercises the affected path, which is what `ValidateOnStart` is for.

A **concurrency** mistake on the context, because parallel operations on one instance are a race, and a race that is not exercised is not a failure.

A **pipeline ordering** mistake is the one an integration test is genuinely good at, since the request goes through the real pipeline. Even there it only catches the orderings your tests actually traverse.

So the honest summary is that an integration suite is evidence about behaviour on the paths it covers, and the other three mechanisms, scope validation, options validation at startup, and awaiting immediately, are not redundant with it.

</details>

5. ▢ **Stage 6 capstone.** A service has these four things in it. All of them compile and the app starts. Name each defect, say what it does, and say which mechanism would have caught it.

   - a) `OrderCache` is registered with `AddSingleton` and takes `ApplicationDbContext` in its constructor
   - b) An authorization middleware that reads `HttpContext.GetEndpoint()` is registered above an explicit `app.UseRouting()` call
   - c) `PricingOptions` is bound with `Configure<PricingOptions>(section)`, has a required property, and is read through `IOptions<PricingOptions>` by a class that operators expect to reconfigure without a redeploy
   - d) A handler starts two repository calls on the injected context and then awaits both with `Task.WhenAll`

<details markdown="1"><summary>Check</summary>

**a) A captive dependency.** The singleton is built once, so it captures one `ApplicationDbContext` and holds it for the application's lifetime, promoting a scoped object to an application-lifetime one. That context accumulates tracked entities indefinitely and is shared across requests, which is also the concurrency problem in (d) by another route. Caught by running in the development environment, where the default provider checks that scoped services are not injected into singletons, or by `validateScopes: true`.

**b) A position mistake.** The endpoint is **always null before `UseRouting`**, so the middleware reads null on every request, finds no policy, and lets everything through. Nothing throws. Caught by an integration test that requests a protected endpoint and expects to be refused, which is precisely the infrastructure scenario integration tests are for.

**c) Two configuration mistakes at once.** `IOptions<T>` **does not support reading configuration data after the app has started**, so the "reconfigure without a redeploy" expectation is silently false; the class needs `IOptionsMonitor<T>`, since it is being read by something long-lived. And with only `Configure` and no validation chain, a missing required value is discovered when the first `TOptions` instance is created rather than at startup. Caught by adding `ValidateDataAnnotations` and `ValidateOnStart`, which turns a request-time failure into a deployment failure.

**d) Parallel operations on one context.** **EF Core does not support multiple parallel operations being run on the same `DbContext` instance**, explicitly including parallel execution of async queries. The scoped registration was safe only because one thread executes a request at a time, and this removes that premise. Detected, when it is detected, as an `InvalidOperationException` about a second operation starting before the previous one completed; undetected, the documented outcome is undefined behaviour, crashes and data corruption. Caught by awaiting each call immediately, or by using separate contexts through `IServiceScopeFactory` scopes, at the cost of no longer saving together.

Read them together and the stage has a shape. Every one of the four compiles, three of the four start cleanly and serve traffic, and each has a different detector: a development-time container check, an integration test, a startup validation call, and a discipline about awaiting. Structure is choosing all four deliberately, and the reason it is worth a lesson is that no single tool tells you about more than one of them.

</details>

## Real-world reps

- [ ] Find a test project for a C# service you have access to and classify its tests: which are unit tests, which go through a test client, and whether the split matches the documented rule.
- [ ] If it has a `WebApplicationFactory`, read what its `ConfigureWebHost` replaces, and check what is left pointing at real infrastructure.
- [ ] Tomorrow: take one service and answer stage 6's four questions about it in writing. Note which answers you had to guess.

## Going further

- [Docs: "Integration tests in ASP.NET Core", Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/test/integration-tests)
- [Docs: "Dependency injection guidelines", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection-guidelines)
- [Docs: "DbContext Lifetime, Configuration, and Initialization", EF Core](https://learn.microsoft.com/en-us/ef/core/dbcontext-configuration/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
