---
title: "22. xUnit and NUnit"
description: "The per-test instance rule that leaves xUnit no setup attribute to need, the word theory meaning two different things, and the parallelism a shared fixture quietly costs"
type: lesson
---

# Lesson 22. xUnit and NUnit

**Mission link:** Stage 5 begins here, and it is done when someone else can clone, build, test and run what you wrote. A test that passes only because it happened to run first is worse than no test, so the first thing worth learning about a C# test framework is not its assertion syntax but its lifecycle: who constructs the class your tests live in, and how often.
**Primary source:** [Docs: "Unit testing C# in .NET using dotnet test and xUnit", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-csharp-with-xunit)
**Prerequisites:** [Lesson 21](0021-async-streams.md), [Lesson 10](0010-interfaces.md), [Lesson 6](0006-exceptions.md)

## Warm-up

1. ▢ What does a `using` statement guarantee, and what must a type implement to be used with one?

<details markdown="1"><summary>Check</summary>

`IDisposable`. The instance is disposed when control leaves the block, explicitly including departure by exception, which is what makes it deterministic cleanup rather than a hope.

</details>

2. ▢ Lesson 21 named a second disposal interface. Which one, and what does it change?

<details markdown="1"><summary>Check</summary>

`IAsyncDisposable`, whose `DisposeAsync` is awaited, reached through `await using`. It exists because cleanup can itself be an asynchronous operation, and an async enumerator's cleanup usually is.

</details>

3. ▢ A framework constructs one instance of your class and then calls three of its methods, in an order it chooses. What can go wrong that would not go wrong with three fresh instances?

<details markdown="1"><summary>Check</summary>

Anything held in a field survives from one call into the next, so a method can pass because of what an earlier one left behind, and the suite's result depends on the order chosen. It also cannot safely be run in parallel, because the three calls share mutable state. Hold that thought: the two frameworks in this lesson answer this question differently, and almost everything else about them follows from that answer.

</details>

## Know this

**Two frameworks, and the difference that is not cosmetic.** xUnit and NUnit both find tests by attribute, both ship a test-project template, and both are first-class in the .NET tooling. Comparing their attribute names is the shallow reading. The difference that changes how you write a test class is that they disagree about **who owns the instance**.

**xUnit creates a new instance of the test class for every test.** The consequence is stated directly by the documentation: because a new instance is created for every test that is run, **any code placed into the constructor of the test class will be run for every single test** ([Sharing Context between Tests](https://xunit.net/docs/shared-context)). So the constructor *is* the setup, and `IDisposable.Dispose` *is* the teardown. There is no setup attribute in xUnit because, given that rule, there is nothing for one to do.

One restriction falls out of using a constructor for it: you cannot call asynchronous methods in a constructor. For an async startup and cleanup, implement `IAsyncLifetime`, which gives you `InitializeAsync` and `DisposeAsync`. In xUnit v3 that `DisposeAsync` comes from `IAsyncDisposable`, which you may implement on its own when all you need is async cleanup.

**NUnit shares one instance across the fixture.** NUnit's `LifeCycle` enumeration has two values, and the documentation labels the first of them: `LifeCycle.SingleInstance` means **a single instance is created and shared for all test cases**, and **this is the default**; `LifeCycle.InstancePerTestCase` means a new instance is created for each test case ([FixtureLifeCycle](https://docs.nunit.org/articles/nunit/writing-tests/attributes/fixturelifecycle.html), added in NUnit 3.13). Because the default shares, NUnit needs a place to undo the sharing, and that is `[SetUp]`, which marks a method NUnit calls immediately before each test in the fixture, for per-test state that should not leak between cases ([SetUp](https://docs.nunit.org/articles/nunit/writing-tests/attributes/setup.html)). Its companions are `[TearDown]`, `[OneTimeSetUp]` and `[OneTimeTearDown]`.

Read the two together and the vocabulary stops being arbitrary:

|Question|xUnit|NUnit|
|---|---|---|
|Marks the class|nothing needed|`[TestFixture]`|
|Marks a test|`[Fact]`|`[Test]`|
|Same code, several inputs|`[Theory]` with `[InlineData(...)]`|`[TestCase(...)]`|
|Asserts|`Assert.False(result, message)`|`Assert.That(result, Is.False, message)`|
|Before each test|the constructor|a method marked `[SetUp]`|
|After each test|`Dispose`|a method marked `[TearDown]`|
|Instances of the class|one per test|one per fixture, by default|

The last row explains the two above it. **Isolation is xUnit's default and sharing is the feature; sharing is NUnit's default and isolation is the feature.** Neither is wrong, but a habit carried across in either direction produces tests that pass for the wrong reason.

**Facts and theories, and a word that means two things.** xUnit distinguishes them by what the test claims: **facts are tests which are always true, testing invariant conditions**, while **theories are tests which are only true for a particular set of data** ([Getting Started with xUnit.net v3](https://xunit.net/docs/getting-started/v3/getting-started)). A theory's data comes from attributes, most simply `[InlineData]`, one per case:

```csharp
[Theory]
[InlineData(-1)]
[InlineData(0)]
[InlineData(1)]
public void IsPrime_ValuesLessThan2_ReturnFalse(int value)
{
    var result = _primeService.IsPrime(value);

    Assert.False(result, $"{value} should not be prime");
}
```

NUnit writes the same test with `[TestCase]`, which **creates a suite of tests that execute the same code but have different input arguments**, and asserts through its constraint model ([Unit testing C# with NUnit and .NET Core](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-csharp-with-nunit)):

```csharp
[TestCase(-1)]
[TestCase(0)]
[TestCase(1)]
public void IsPrime_ValuesLessThan2_ReturnFalse(int value)
{
    var result = _primeService?.IsPrime(value);

    Assert.That(result, Is.False, $"{value} should not be prime");
}
```

The trap is that NUnit **also** has a `[Theory]`, and it is not this. NUnit theories are fed by `[Datapoint]` and `[DatapointSource]` attributes ([NUnit attributes](https://docs.nunit.org/articles/nunit/writing-tests/attributes.html)). So the word tells you nothing on its own: the `using` at the top of the file is what says which mechanism you are reading.

**Sharing in xUnit has three scopes, and you pick one by name.** Since every test gets a fresh instance, anything expensive has to be shared deliberately, and the shared object always arrives the same way, as a constructor argument:

|What you want shared|How you ask|
|---|---|
|A clean context per test|the constructor, plus `Dispose`|
|One context for all tests in a class|`IClassFixture<T>` on the test class|
|One context across several classes|a `[CollectionDefinition("name")]` class carrying `ICollectionFixture<T>`, and `[Collection("name")]` on each test class|
|One context for the whole assembly|`[assembly: AssemblyFixture(typeof(T))]`, new in v3|

In every case the fixture's own constructor holds the startup code and its `Dispose` the cleanup, and xUnit creates it before any of the tests run and disposes it after they have all finished.

**And a shared fixture is not free, because of how xUnit parallelises.** The default parallel mode is `collections`, and by default **there is a test collection per test class**. Tests in one class therefore do not run in parallel against each other, while tests in different classes do ([Running Tests in Parallel](https://xunit.net/docs/running-tests-in-parallel)). The documentation's own measurement: a 3-second and a 5-second test in one class take about 8 seconds, and take about 5 seconds once they are split into two classes.

Put those two rules side by side and the cost of a collection fixture is visible before you pay it. Adding `[Collection("Db")]` to four classes is what lets them share the fixture, and it is the same act that puts them in one collection, so they no longer run in parallel against each other. The assembly fixture is the exception the documentation calls out: unlike collection fixtures, **there is no change in parallelization when using an assembly fixture**.

**One forward pointer.** This lesson is deliberately only the frameworks' own vocabulary. Replacing a real dependency with something you control is lesson 23; the project file, the package references and `dotnet test` itself are lesson 24, which closes stage 5. What to take forward now is the lifecycle question, because it is the one to ask of any test class you are handed: how many times is this constructed, and what is still alive from the test before?

## Practice

1. ▢ A test class has a `private readonly List<string> _log` field that each of its three tests appends one entry to and then asserts the count of. The same code, once under xUnit and once under NUnit with no lifecycle attribute. What happens?

<details markdown="1"><summary>Check</summary>

Under xUnit it passes. A new instance of the test class is created for every test, so `_log` is a fresh list each time and every test sees a count of one.

Under NUnit it does not, or worse, it does so unreliably. The default is `LifeCycle.SingleInstance`, one instance shared for all test cases, so the second test sees two entries and the third sees three, and which test fails depends on the order they run in.

Two fixes, and they are the two philosophies. Reset the field from a `[SetUp]` method, which is the NUnit-shaped answer. Or apply `[FixtureLifeCycle(LifeCycle.InstancePerTestCase)]`, available since NUnit 3.13, which buys xUnit's model. The documentation notes the second is useful where test case parallelism matters, and that is not a coincidence: a shared instance is exactly what makes parallel cases unsafe.

</details>

2. ▢ A reviewer asks why your xUnit test class has no setup method. What is the answer, and what changes if the setup has to `await` something?

<details markdown="1"><summary>Check</summary>

Because there is no setup attribute to be missing. xUnit creates a new instance of the test class for every test, so the constructor already runs before every single test, and `IDisposable.Dispose` runs after it. A setup attribute would only be another name for the constructor.

If the preparation is asynchronous, that is the one place the design pinches, since a constructor cannot await. Implement `IAsyncLifetime` for `InitializeAsync` and `DisposeAsync`. In v3 the async cleanup half comes from `IAsyncDisposable`, so a class that only needs async teardown can implement that alone.

</details>

3. ▢ Four test classes need one database, seeded once. Which xUnit feature, and what does choosing it cost?

<details markdown="1"><summary>Hint</summary>

The feature is named for the scope it shares across. The cost is in a different document: the one about running tests in parallel.

</details>

<details markdown="1"><summary>Check</summary>

A collection fixture. Write the fixture class with the seeding in its constructor and the cleanup in `Dispose`, write a class marked `[CollectionDefinition("Db")]` carrying `ICollectionFixture<DatabaseFixture>`, mark all four test classes `[Collection("Db")]`, and take the fixture as a constructor argument wherever a class needs it.

The cost is parallelism. The default parallel mode is `collections` and tests within a single collection do not run in parallel against each other. Normally each class is its own collection, so those four classes ran concurrently; naming a shared collection is precisely what stops that. You have traded wall-clock time for one seeded database, which is often the right trade, but it should be a decision rather than a surprise.

If the context genuinely belongs to the whole test assembly, the v3 assembly fixture shares it without that trade, since the documentation states there is no change in parallelization when using one.

</details>

4. ▢ You open a file and see a `[Theory]` on a method. What do you know?

<details markdown="1"><summary>Check</summary>

Less than the word suggests, because both frameworks have one and they are different features.

In xUnit a theory is a test that is only true for a particular set of data, as opposed to a fact, which tests an invariant condition; its cases usually come from `[InlineData]`. In NUnit, `[Theory]` is a separate mechanism supplied by `[Datapoint]` and `[DatapointSource]`, and the everyday parameterised test there is `[TestCase]`.

So read the `using` first. This is a small instance of a habit the arc keeps returning to: a familiar-looking name is not a shared meaning, and the framework a file imports decides what its attributes do.

</details>

5. ▢ Which statement is correct?

   - a) Both frameworks construct the test class once per class, which is why both provide a setup attribute
   - b) xUnit constructs a new instance for every test, so its constructor is the setup, while NUnit shares one instance per fixture by default and therefore needs `[SetUp]`
   - c) By default, xUnit runs the tests inside a single test class in parallel against each other
   - d) Marking several classes with `[Collection]` shares a fixture between them and leaves their parallelism unchanged

<details markdown="1"><summary>Check</summary>

**b)** That is the lifecycle difference the rest of each framework's vocabulary follows from.

(a) is wrong about xUnit, and would leave its constructor running once per class rather than once per test. (c) inverts the default: the parallel mode is `collections` with one collection per class, so tests in the same class do not run in parallel against each other while tests in different classes do. (d) describes the assembly fixture, not the collection fixture; the documentation singles out the assembly fixture as the one that changes no parallelization, and a shared collection serialises the classes in it.

</details>

## Real-world reps

- [ ] Open a C# test project you have access to and name the framework from the attributes alone, before looking at anything else.
- [ ] Find a test class with a mutable field. Work out whether it would still pass if the framework reused one instance across its tests, and whether it currently depends on the order they run in.
- [ ] Tomorrow: find a test class that builds something expensive per test. Decide which of the four sharing scopes it actually needs, and what that choice would cost in parallelism.

## Going further

- [Docs: "Unit testing C# in .NET using dotnet test and xUnit", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-csharp-with-xunit)
- [Docs: "Unit testing C# with NUnit and .NET Core", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-csharp-with-nunit)
- [Docs: "Sharing Context between Tests", xUnit.net](https://xunit.net/docs/shared-context)
- [Docs: "Running Tests in Parallel", xUnit.net](https://xunit.net/docs/running-tests-in-parallel)
- [Docs: "Attributes", NUnit](https://docs.nunit.org/articles/nunit/writing-tests/attributes.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
