---
title: "23. Mocking"
description: "The runtime proxy behind every substitution library, the C# default that decides what it is allowed to replace, and the mocked assertion that passes without the call ever happening"
type: lesson
---

# Lesson 23. Mocking

**Mission link:** A typed, tested service is testable because of how it was designed, not because of which library its tests import. Substitution libraries in C# can only replace what the language lets them override, so the question of what you can test is settled by decisions you made while modelling, several lessons before any test existed.
**Primary source:** [Docs: "Creating a substitute", NSubstitute](https://nsubstitute.github.io/help/creating-a-substitute/)
**Prerequisites:** [Lesson 22](0022-xunit-and-nunit.md), [Lesson 10](0010-interfaces.md)

## Warm-up

1. ▢ Under xUnit, what runs before every test, and why is there no attribute for it?

<details markdown="1"><summary>Check</summary>

The constructor. xUnit creates a new instance of the test class for every test, so constructor code already runs before each one, and `Dispose` after it. A setup attribute would be a second name for something the lifecycle already does.

</details>

2. ▢ What does a base-class method need before a derived class is allowed to override it?

<details markdown="1"><summary>Check</summary>

The `virtual` keyword, or `abstract`. The reference is explicit that `virtual` is what modifies a member declaration **and allows a derived class to override it** ([virtual](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/virtual)). Without it, there is nothing for a derived class to replace.

</details>

3. ▢ A library hands you an object that presents itself as your `IEmailSender`, returns whatever you told it to, and remembers what you called on it. You did not write that type and no code generator ran. Where did it come from?

<details markdown="1"><summary>Check</summary>

It was created while the test ran: a type built at run time that implements the interface. Hold on to that, because once you know a substitute is a generated type, every rule about what can and cannot be substituted stops needing to be memorised.

</details>

## Know this

**A substitute is a proxy generated at run time, and that single fact explains the rest.** FakeItEasy says it outright: it **uses Castle DynamicProxy to create fakes**, so it can fake just about **anything that could normally be overridden, extended, or implemented**, which comes to interfaces, classes that are not sealed and not static and have a constructor it can use, and delegates ([What can be faked](https://fakeiteasy.github.io/docs/stable/what-can-be-faked/)). Moq and NSubstitute rest on the same machinery. The library is writing an implementation of your interface, or a subclass of your class, while the test is running.

**So the language decides what it may replace, not the library.** Once the fake exists, its members can be overridden if they are **virtual, abstract, or an interface method when an interface is being faked**, and that list has a documented exclusion: **static members, including extension methods, cannot be overridden**. There is no dispatch to intercept for a static call, so no proxy can stand in front of one.

**And now the C# default that turns this from a footnote into a design constraint.** Java's instance methods are overridable unless you mark them `final`; C#'s are the other way round, since `virtual` is the keyword that grants permission. A class written the plain way in C# therefore exposes nothing a substitution library can touch. "I will mock the class" is a habit that survives the move from Java and stops working, which is exactly the shape of failure this workspace keeps warning about: the code compiles and the reviewer sees nothing wrong.

**The failure is silent, which is what makes it worth a lesson.** NSubstitute's documentation is the bluntest source on this, and it names two separate consequences ([Creating a substitute](https://nsubstitute.github.io/help/creating-a-substitute/)):

|What you did|What actually happens|
|---|---|
|Substituted for a class and called a non-virtual member|**Any non-virtual code in the class will actually execute.** You are running the real implementation inside what you believed was a fake|
|Asserted on a non-virtual member, as in `subClass.Received().NonVirtualCall()`|It **will not actually run an assertion**, and **will always pass, even if there are no calls** to that member, and can cause confusing problems in later tests|

Read the second row again. Not a compile error, not a failing test: a green test that asserts nothing. The documentation recommends installing NSubstitute.Analyzers to detect these cases, while noting it catches many of them and not all, so the analyzer is a safety net rather than a permission slip.

**Two libraries, one mechanism, and a difference at the call site.** Moq hands you a controller object with the substitute hanging off it, configured with `Setup` and read through `Object` ([Moq Quickstart](https://github.com/devlooped/moq/wiki/Quickstart)):

```csharp
var mock = new Mock<IFoo>();
mock.Setup(foo => foo.DoSomething("ping")).Returns(true);

IFoo foo = mock.Object;
```

NSubstitute hands you the interface itself, and you configure it by calling it ([Getting started](https://nsubstitute.github.io/help/getting-started/)):

```csharp
var calculator = Substitute.For<ICalculator>();

calculator.Add(1, 2).Returns(3);
```

Assertions in NSubstitute go through `Received()`, and in Moq through `Verify`. The difference in shape is not cosmetic once you connect it to the rule above: NSubstitute configures a substitute **by invoking it**, so if the member is not overridable, the configuration line itself has just called the real method.

**A word on the words.** Microsoft Learn gives the .NET usage and then admits the ground is unstable: **testing literature and tools use the terms fake, stub, and mock inconsistently** ([Best practices for writing unit tests](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices)). In the usage it documents, a **fake** is the generic term, a **stub** is a controllable replacement for an existing dependency, and a **mock** is the object that **decides whether or not a unit test passes or fails**, which it puts memorably: a mock **begins as a fake and remains a fake until it enters an `Assert` operation**. The same page notes the narrower classical usage, where a stub provides data, a mock verifies interactions, and a fake is a working alternative implementation. NSubstitute declines the whole argument, asking why bother naming it when what you want is an instance you have some control over. Know the definitions well enough to read a review comment, and do not spend a design meeting on them.

**One forward pointer.** Nothing here has said how the substitute reaches the code under test. In a real service it arrives through a constructor parameter that the container fills, which is lesson 26, and it is a large part of why ASP.NET Core code is written against interfaces at all. The project file and the package references that make any of this compile are lesson 24, which closes stage 5.

## Practice

1. ▢ A colleague substitutes for the concrete class `PricingService`, whose `Calculate` is not declared `virtual`, configures it to return `10`, asserts it was called, and the test passes. Name both things that are wrong.

<details markdown="1"><summary>Check</summary>

First, the configuration did not configure anything. Because a substitution library can only work with overridable members, **any non-virtual code in the class actually executes**, so the line intended to stub `Calculate` ran the real pricing logic, and the object under test is a real `PricingService` wearing a costume.

Second, the assertion is not an assertion. On a non-overridable member, `Received()` **will not actually run an assertion and will always pass, even if there are no calls** to it. The test is green, it stays green if the call is deleted, and it will stay green through the refactor it was written to protect.

The fixes are the two the language offers: extract an interface and substitute for that, or mark the member `virtual` and accept that you have made it an extension point. Adding NSubstitute.Analyzers is worth doing either way, remembering the documentation's own qualifier that it catches many of these cases but not all.

</details>

2. ▢ Why can no substitution library replace a static method, or an extension method?

<details markdown="1"><summary>Check</summary>

Because a fake works by overriding or implementing, and **static members, including extension methods, cannot be overridden**. There is no instance whose dispatch a proxy could sit in front of; the call site is bound to that method and nothing can get between them.

The design consequence is the useful half. A static helper that reads the clock, the filesystem, an environment variable or the network is a dependency you have no way to substitute, and no amount of test-framework skill will recover it. Making it an instance behind an interface is not ceremony, it is the only thing that makes the surrounding code testable at all.

</details>

3. ▢ Moq's `new Mock<IFoo>()` and NSubstitute's `Substitute.For<IFoo>()` do not give you the same kind of thing. What is the difference, and why does it matter more than style?

<details markdown="1"><summary>Hint</summary>

Look at what you pass to the code under test in each case, and at what a configuration line does in each case.

</details>

<details markdown="1"><summary>Check</summary>

Moq returns a controller. You configure it through `mock.Setup(...)`, and the object you hand to the code under test is `mock.Object`. NSubstitute returns something already typed as the interface: you configure it by calling it, as in `calculator.Add(1, 2).Returns(3)`, and you pass it directly.

It matters because of what a configuration line is. In NSubstitute, `calculator.Add(1, 2)` is a real invocation, intercepted by the proxy. That is fine for an interface, where every member is intercepted. Against a class with a non-virtual member it is the problem itself, since the call is not intercepted and the real method has just run while you were setting up the test. The API shape and the warning about substituting for classes are the same fact seen from two sides.

</details>

4. ▢ Your test creates a substitute repository that returns a fixed customer, and a substitute email sender that you assert was called once. Which of the two is a stub and which is a mock?

<details markdown="1"><summary>Check</summary>

Under the definitions Microsoft Learn documents: the repository is a **stub**, a controllable replacement for an existing dependency, there so you can avoid dealing with the real one. The email sender is a **mock**, because it is the object that decides whether the test passes or fails, and by that page's phrasing it remained a fake right up until it entered an `Assert`.

Two caveats keep this from being trivia. The same page states that the terms are used inconsistently across tools and literature, and gives the narrower classical split where a stub provides data and a mock verifies interactions. And the library you are using may refuse the distinction entirely: NSubstitute calls both of them substitutes, on the grounds that what you wanted was an instance you have some control over. The behaviour is what is real here; the noun is local vocabulary.

</details>

5. ▢ Which statement is correct?

   - a) Substitution libraries rewrite the type, so any member of any class can be replaced
   - b) A substitute is a proxy created at run time, so it can replace interface members, and virtual or abstract members of a class that is not sealed
   - c) Configuring a non-virtual member fails to compile, so the compiler protects you from this mistake
   - d) C# members are overridable unless marked `sealed`, so most classes can be substituted as written

<details markdown="1"><summary>Check</summary>

**b)** The proxy is built by implementing an interface or subclassing a class, so overridability is the whole boundary, and static and extension members fall outside it.

(a) confuses the mechanism: the library generates a new type in front of yours rather than altering yours, which is precisely why the language's rules bind it. (c) is the danger this lesson exists for, since nothing fails at all: the real code runs, and an assertion on a non-overridable member always passes. (d) inverts the C# default, where `virtual` is what allows a derived class to override, so a member is not overridable unless its declaration says so.

</details>

## Real-world reps

- [ ] Pick a class in a C# codebase you have access to and count how many of its public members a substitution library could actually replace. Most of the interesting reading is in the answer being zero.
- [ ] Find a test that substitutes for a concrete class. Check whether the members it configures are declared `virtual`, and if they are not, work out what that test currently proves.
- [ ] Tomorrow: find a static helper called from code you would like to test. Name what it makes impossible to substitute, and write down the interface it would have to become.

## Going further

- [Docs: "Creating a substitute", NSubstitute](https://nsubstitute.github.io/help/creating-a-substitute/)
- [Docs: "Getting started", NSubstitute](https://nsubstitute.github.io/help/getting-started/)
- [Docs: "Quickstart", Moq](https://github.com/devlooped/moq/wiki/Quickstart)
- [Docs: "What can be faked", FakeItEasy](https://fakeiteasy.github.io/docs/stable/what-can-be-faked/)
- [Docs: "Best practices for writing unit tests", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices)
- [Docs: "virtual (C# Reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/virtual)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
