---
title: 32. Test Doubles
description: Five kinds of stand-in, when a real object beats all of them, and what a mock quietly stops testing
type: lesson
---

# Lesson 32. Test Doubles

**Mission link:** Owning a service means being able to test it apart from the collaborators it talks to, and a test double is how you cut that wire, but the wrong double turns the test into a description of the double instead of a check on the service.
**Primary source:** [`Mockito`, mockito-core 5.23.0 API](https://javadoc.io/doc/org.mockito/mockito-core/latest/org.mockito/org/mockito/Mockito.html)
**Prerequisites:** [Lesson 29](0029-your-first-test.md), [Lesson 9](0009-interfaces.md)

## Warm-up

1. ▢ `PriceLookup` below declares one abstract method and nothing else. What does that make it, and what is the smallest thing that can supply an instance of it without writing a class? `interface PriceLookup { double priceOf(String sku); }`

<details markdown="1"><summary>Check</summary>

A functional interface (lesson 9): exactly one abstract method beyond whatever it inherits from `Object`. A lambda, `sku -> 0.50`, supplies an instance directly, since the compiler builds the implementing object around the lambda body. Nothing about that changes when the interface is being used to stand in for a real collaborator in a test rather than for production wiring, which is most of what this lesson relies on.

</details>

## Know this

A test double is anything that stands in for a real collaborator so a test can exercise one unit without dragging its dependencies along. Gerard Meszaros named five kinds in *xUnit Test Patterns*, and the words get used interchangeably in conversation in a way that hides real differences, so it is worth being precise about which one a piece of code actually is.

### The five kinds, precisely

- **Dummy**: passed in because a signature demands something, and never used for anything else. *Use it when* the collaborator is irrelevant to the behaviour under test and only needs to compile.
- **Stub**: returns canned answers to calls it receives, nothing more. *Use it when* the code under test asks a question and takes a different path depending on the answer, and the test needs to control which path runs.
- **Spy**: a stub that also records what happened to it, for later inspection. *Use it when* you need the canned answer and also need to check afterwards that a particular call happened, without the object failing the test itself.
- **Mock**: a stub with expectations about how it will be called, expectations the test checks. *Use it when* the point of the test genuinely is the interaction: that a particular method was called, with particular arguments, a particular number of times.
- **Fake**: a real, working implementation, simplified for tests, such as an in-memory map standing in for a database table. *Use it when* the collaborator's behaviour across several calls matters, not just one canned answer.

Mockito's own vocabulary blurs two of these on purpose. What Mockito calls a "mock" behaves as a stub until you call `verify` on it, at which point it behaves as Meszaros's mock; what Mockito calls `spy()` wraps a *real* object and delegates to it unless a method is explicitly stubbed, closer to a partial fake that also records calls. Knowing Meszaros's five names first turns Mockito's two words from confusing shorthand into a specific, checkable claim about what a given line of test code is doing.

### Hand-write a stub first

A test double is an ordinary class before it is a framework feature, and it is worth seeing that once, without a library anywhere in sight. Take the interface from the warm-up and a class that uses it:

```java
interface PriceLookup {
    double priceOf(String sku);
}

class Checkout {
    private final PriceLookup prices;

    Checkout(PriceLookup prices) {
        this.prices = prices;
    }

    double total(List<String> skus) {
        return skus.stream().mapToDouble(prices::priceOf).sum();
    }
}
```

The classic, Meszaros-era stub is a class that implements the interface and returns fixed answers:

```java
class FixedPriceLookup implements PriceLookup {
    @Override
    public double priceOf(String sku) {
        return switch (sku) {
            case "APPLE" -> 0.50;
            case "BREAD" -> 2.20;
            default -> throw new IllegalArgumentException("unstubbed sku: " + sku);
        };
    }
}
```

`PriceLookup` has exactly one method, so the class collapses to a lambda with identical behaviour, and nothing about the test changes:

```java
PriceLookup stub = sku -> switch (sku) {
    case "APPLE" -> 0.50;
    case "BREAD" -> 2.20;
    default -> throw new IllegalArgumentException("unstubbed sku: " + sku);
};
Checkout checkout = new Checkout(stub);
assertEquals(2.70, checkout.total(List.of("APPLE", "BREAD")), 0.0001);
```

Both versions were run, and both pass:

```text
[INFO] Running example.StubCheckoutTest
[INFO] Tests run: 2, Failures: 0, Errors: 0, Skipped: 0
```

Records and lambdas make hand-written doubles cheap for single-method interfaces in a way the older literature does not assume, since it mostly predates lambdas. A wider interface still gets a genuine hand-written class, no more mysterious than `FixedPriceLookup` above: a `default` throw for anything not deliberately catered for turns a silently wrong answer into a loud one, which is what makes a stub trustworthy rather than merely convenient.

### Mockito, enough to use it well

Add the dependency at test scope, alongside JUnit:

```xml
<dependency>
    <groupId>org.mockito</groupId>
    <artifactId>mockito-core</artifactId>
    <version>5.23.0</version>
    <scope>test</scope>
</dependency>
```

The four calls that cover most of what a test needs are `mock`, `when(...).thenReturn(...)`, `verify`, and `ArgumentCaptor`:

```java
PriceLookup prices = mock(PriceLookup.class);
when(prices.priceOf("APPLE")).thenReturn(0.50);

Checkout checkout = new Checkout(prices);
double total = checkout.total(List.of("APPLE"));

assertEquals(0.50, total, 0.0001);
verify(prices).priceOf("APPLE");
verifyNoMoreInteractions(prices);
```

`mock(PriceLookup.class)` builds an object of that type with no behaviour of its own. `when(...).thenReturn(...)` gives one method call a canned answer, which is the stub half. `verify` checks that a call actually happened, which is the mock half, and `verifyNoMoreInteractions` checks that nothing else was called on the same object, which is what turns "this call happened" into "and no other call did". `ArgumentCaptor` inspects the value a real call actually carried, rather than only matching it against something written in advance:

```java
Ledger ledger = mock(Ledger.class);
TransferService service = new TransferService(ledger);
service.transfer("alice", "bob", 40);

ArgumentCaptor<Integer> amount = ArgumentCaptor.forClass(Integer.class);
verify(ledger).credit(eq("bob"), amount.capture());
assertEquals(40, amount.getValue());
```

Run, both tests pass:

```text
[INFO] Running example.MockitoBasicsTest
[INFO] Tests run: 2, Failures: 0, Errors: 0, Skipped: 0
```

### The default-return trap

An unstubbed method on a mock does not fail and does not complain. It returns `null` for an object type, `0` for a numeric type, `false` for `boolean`, and does nothing at all for `void`. That default can happen to be exactly the value a test expects, and when it is, the test passes without the mock ever having been asked the real question. Take an access check:

```java
interface AccessPolicy {
    boolean isAuthorized(String userId, String resource);
}

class ResourceGate {
    private final AccessPolicy policy;
    ResourceGate(AccessPolicy policy) { this.policy = policy; }
    boolean open(String userId, String resource) {
        return policy.isAuthorized(userId, resource);
    }
}
```

and a test that mocks the policy without stubbing it:

```java
AccessPolicy policy = mock(AccessPolicy.class);
ResourceGate gate = new ResourceGate(policy);
assertFalse(gate.open("alice", "vault"));
```

This passes, and it is meant to look reassuring: access was denied. Now run the identical test against a second implementation that never consults the policy at all:

```java
class BrokenResourceGate {
    private final AccessPolicy policy;
    BrokenResourceGate(AccessPolicy policy) { this.policy = policy; }
    boolean open(String userId, String resource) {
        return false;
    }
}
```

```text
[INFO] Running example.DefaultReturnTrapTest
[INFO] Tests run: 2, Failures: 0, Errors: 0, Skipped: 0
```

Both pass, with the identical assertion, and one of them never calls the collaborator at all. The unstubbed mock's `false` and the broken gate's hardcoded `false` are indistinguishable to `assertFalse`, so the test cannot tell a correctly wired denial from a denial that happens for no reason. This is the single most valuable thing to notice about mocks: an assertion on a mock's output is only as strong as the stubbing behind it, and an unstubbed method silently stands in for "whatever the JVM's default happens to be", not for "the collaborator's real answer". Adding one line exposes the broken gate immediately:

```java
verify(policy).isAuthorized("alice", "vault");
```

```text
Wanted but not invoked:
accessPolicy.isAuthorized("alice", "vault");
Actually, there were zero interactions with this mock.
```

The fix is not to stop using mocks. It is to never let an assertion on a mock's boundary rest on a value the test never actually stubbed, and to verify the call itself whenever the *fact of the call* is part of what the test claims to check.

### When not to use a double

A pure function needs none: if `total` only combines its arguments with no collaborator at all, call it and assert on the return value, since there is nothing to stand in for.

A record or value object needs none either (lesson 8): a `Money` or an `OrderLine` is compared with `equals`, built with its constructor, and never wired up as a dependency, so there is no seam for a double to occupy.

A fake beats a mock the moment a collaborator receives more than one call in a test, because a mock encodes the exact sequence of calls the test expected, while a fake encodes the collaborator's actual behaviour and answers whatever sequence of calls arrives. `TransferService` moves money by debiting one account and crediting another:

```java
class TransferService {
    private final Ledger ledger;
    TransferService(Ledger ledger) { this.ledger = ledger; }
    void transfer(String from, String to, int amount) {
        ledger.debit(from, amount);
        ledger.credit(to, amount);
    }
}
```

A fake `Ledger` backed by a map answers `balanceOf` correctly no matter which order `debit` and `credit` ran in:

```java
InMemoryLedger ledger = new InMemoryLedger();
ledger.seed("alice", 100);
ledger.seed("bob", 0);
new TransferService(ledger).transfer("alice", "bob", 40);
assertEquals(60, ledger.balanceOf("alice"));
assertEquals(40, ledger.balanceOf("bob"));
```

Do not mock a type you do not own. A mock encodes your belief about how a library behaves, not the library's actual behaviour, and an upgrade, a fixed bug, or a documented edge case can quietly falsify that belief while your mock keeps agreeing with you. Wrap the type behind a small interface of your own and mock that instead, or use whatever real, simplified stand-in the library ships, such as `Clock.fixed(...)` for `java.time.Clock`, which is a real `Clock` and needs no mock at all.

An over-specified mock test breaks on a refactor that changes no behaviour, and that is a test costing more than it protects. The mock test above pinned the *order* of the two calls:

```java
InOrder order = inOrder(ledger);
order.verify(ledger).debit("alice", 40);
order.verify(ledger).credit("bob", 40);
```

Refactor `transfer` to credit the destination before debiting the source. Final balances are unaffected, since the two accounts are independent:

```java
void transfer(String from, String to, int amount) {
    ledger.credit(to, amount);
    ledger.debit(from, amount);
}
```

Rerun both tests. The fake-based test still passes, because it only ever asked about the final state:

```text
[INFO] Running example.FakeLedgerTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
```

The mock-based test fails, on a change that broke nothing a caller could observe:

```text
[INFO] Running example.OverSpecifiedMockTest
Verification in order failure
Wanted but not invoked:
ledger.credit("bob", 40);
Wanted anywhere AFTER following interaction:
ledger.debit("alice", 40);
[ERROR] Tests run: 1, Failures: 1, Errors: 0, Skipped: 0
```

The fake test protected behaviour. The mock test protected an implementation detail that was never part of the contract, and the refactor did exactly what refactors are supposed to do: change how, not what.

### `verify` versus `assert`

Asserting checks a return value or an observable state: what the code under test produced. Verifying checks an interaction: which method the code under test chose to call, with which arguments, how many times. Both are legitimate, but `assert` should be reached for first, because it tests the promise a unit makes to its caller, while `verify` tests the choices the current implementation happens to make to keep that promise. The ledger refactor is the demonstration: the promise was "the balances end up correct", and only the assertion-based test was actually checking it. Reach for `verify` when the interaction genuinely is the promise, such as confirming a notification was sent exactly once, where `assert` has no state left to look at.

### A short note on mocking `static` and `final`

Since Mockito 5.0.0, the default mock maker mocks final classes and methods with no extra setup, and a separate call, `mockStatic`, mocks static methods within a scoped, try-with-resources block, both confirmed by running them against 5.23.0. Needing either one is usually the design saying something: a static method or a `final` class with no seam is a sign of a hidden global dependency, and an interface around it is often the better fix, not because Mockito cannot cope but because the next reader of the production code still cannot substitute anything without it.

### The warning Mockito 5.23.0 prints on this baseline

Running the full suite on JDK 25 prints this, on every run that touches a mock, without anything added to provoke it:

```text
Mockito is currently self-attaching to enable the inline-mock-maker. This will no longer work in future releases of the JDK. Please add Mockito as an agent to your build as described in Mockito's documentation: https://javadoc.io/doc/org.mockito/mockito-core/latest/org.mockito/org/mockito/Mockito.html#0.3
WARNING: A Java agent has been loaded dynamically
WARNING: If a serviceability tool is in use, please run with -XX:+EnableDynamicAgentLoading to hide this warning
WARNING: Dynamic loading of agents will be disallowed by default in a future release
```

This is JEP 451's restriction on dynamic agent loading: Mockito's inline mock maker attaches a Java agent to instrument classes at runtime, and from Java 21 onward the JVM warns whenever that happens without the agent being declared up front. The warning is harmless today and the build still succeeds, but the primary source's section 0.3 gives the fix: declare Mockito as a `-javaagent` explicitly, resolving its jar path with `maven-dependency-plugin` and passing it to Surefire's `argLine`. A project that wants the warning gone rather than merely tolerated adds that now, rather than waiting for a future JDK to turn it into a hard failure.

## Practice

1. ▢ A test constructs a `ReportGenerator` that takes an `AuditLogger` in its constructor. The test never checks anything about logging and the `AuditLogger` argument exists only so the constructor compiles. Name the kind of double and the one property that makes it that kind rather than a stub.

<details markdown="1"><summary>Check</summary>

A dummy. The defining property is that nothing about it is ever used, not even once, by the path the test exercises; a stub is used, and used for its canned answer specifically. If the test later starts asserting anything about what was logged, the dummy has quietly become a stub or a mock and should be named as one.

</details>

2. ▢ Predict what `mock(Ledger.class).balanceOf("alice")` returns with nothing stubbed, and what calling `mock(Ledger.class).credit("alice", 10)` does with nothing stubbed.

<details markdown="1"><summary>Check</summary>

`balanceOf` returns `0`, the default value for `int`, since Mockito never calls the real method. `credit` is `void`, so the unstubbed call simply does nothing at all and returns nothing to check; the mock silently accepts the call and moves on.

</details>

3. ▢ `theSameTestAlsoPassesAgainstAGateThatNeverAsksThePolicyAtAll` mocks `AccessPolicy` without stubbing it and asserts `assertFalse(gate.open(...))`. Predict whether it passes against `BrokenResourceGate`, which ignores the policy entirely, then say what single line would have caught the bug.

<details markdown="1"><summary>Hint</summary>

Ask what value an unstubbed `boolean` method returns, and whether that value happens to match what `assertFalse` wants regardless of which gate is under test.

</details>

<details markdown="1"><summary>Check</summary>

It passes, identically to the correct gate, because the unstubbed mock's default (`false`) and the broken gate's hardcoded `false` are indistinguishable to the assertion. `verify(policy).isAuthorized("alice", "vault");` catches it: against the broken gate it fails with `Wanted but not invoked... Actually, there were zero interactions with this mock`, exposing that the policy was never consulted.

</details>

4. ▢ `OverSpecifiedMockTest` uses `InOrder` to require `debit` before `credit`. `TransferService` is refactored to call `credit` before `debit`, and the final balances are unchanged. Predict which of `OverSpecifiedMockTest` and `FakeLedgerTest` fails, and name the general principle this illustrates.

<details markdown="1"><summary>Check</summary>

`OverSpecifiedMockTest` fails with `Verification in order failure`, since it asserted a call sequence that the refactor deliberately changed. `FakeLedgerTest` keeps passing, since it only ever asserted the final balances. The principle: a test that verifies interactions is coupled to the implementation's current choices, while a test that asserts state or a return value is coupled only to the contract, so the second kind survives refactors that the first kind cannot.

</details>

5. ▢ A colleague wants to mock `java.time.Clock` directly in a dozen tests to control "now". What is the objection to mocking it, and what should replace the mock?

<details markdown="1"><summary>Check</summary>

`Clock` is not a type the project owns, so a mock of it encodes a guess about how `Clock` behaves rather than `Clock`'s actual, specified behaviour, and that guess can go stale under a JDK upgrade with nothing in the test signalling it. `Clock.fixed(instant, zone)` is a real, working `Clock` supplied by the JDK itself, which makes it a fake rather than a mock, and it needs no `when` or `verify` at all: pass it in and let the code under test call it normally.

</details>

## Real-world reps

- [ ] Find a test that calls `verify` on a mock and ask whether an assertion on a return value or on state would check the same promise more directly.
- [ ] Find a mocked method in your own tests that is stubbed with `when(...).thenReturn(...)` and check whether the test still passes if you delete the stub and rely on the default return value instead; if it does, the assertion was not testing what it claimed to.
- [ ] Find a repository, DAO or client mock that receives more than one call inside a single test, and sketch what a small in-memory fake for it would look like.
- [ ] Search your test sources for `mock(` applied to a type from the JDK or a third-party library, rather than to an interface your own code declares, and note what belief about that library the mock is quietly encoding.
- [ ] Tomorrow: pick one existing mock-based test, add `verifyNoMoreInteractions` or an `ArgumentCaptor` assertion to make its interaction explicit, or replace the mock with a hand-written stub, and note whether the test got easier or harder to read.

## Going further

- [`ArgumentCaptor`, mockito-core 5.23.0 API](https://javadoc.io/doc/org.mockito/mockito-core/latest/org.mockito/org/mockito/ArgumentCaptor.html): capturing the arguments a real call carried, rather than matching them in advance
- [`MockedStatic`, mockito-core 5.23.0 API](https://javadoc.io/doc/org.mockito/mockito-core/latest/org.mockito/org/mockito/MockedStatic.html): mocking a static method within a scoped, try-with-resources block
- [Mocks Aren't Stubs, Martin Fowler](https://martinfowler.com/articles/mocksArentStubs.html): where the five-kinds vocabulary and the state-versus-behaviour distinction in this lesson both trace back to
- [Testing and build](../reference/testing-and-build.md): the reference sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
