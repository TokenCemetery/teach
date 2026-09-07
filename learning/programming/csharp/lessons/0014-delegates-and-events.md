---
title: "14. Delegates and Events"
description: "A delegate as a type whose signature includes its return type, the invocation list where one throwing handler stops the rest, and what the event keyword takes away from callers"
type: lesson
---

# Lesson 14. Delegates and Events

**Mission link:** Lesson 13 said a lambda compiles to a delegate. This is what a delegate actually is, and events are the pattern C# builds on top of it, with a keyword Java has no equivalent for.
**Primary source:** [Docs: "Using Delegates", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/delegates/using-delegates)
**Prerequisites:** [Lesson 13](0013-linq.md), [Lesson 11](0011-generics.md)

## Warm-up

1. ▢ A LINQ query is assigned to a variable, the source is then modified, and only afterwards is the variable iterated. Which data does the query see?

<details markdown="1"><summary>Check</summary>

The modified data. A query is not executed until you iterate over the query variable, so the query variable holds a question rather than an answer, and iterating twice asks twice.

</details>

2. ▢ The same `Where` call compiles to two different things depending on what it queries. What are they, and why does the difference matter?

<details markdown="1"><summary>Check</summary>

A **delegate** over an in-memory sequence, so the lambda is compiled code run per element, or an **expression tree** over a queryable source, a data structure a provider can translate into SQL. It matters because a translated query can only contain what the provider understands.

</details>

3. ▢ Why is `Action<in T>` contravariant and `Func<out T>` covariant?

<details markdown="1"><summary>Check</summary>

Because of where `T` appears. `Action<T>` only consumes a `T`, an input position, so `in` applies and an `Action<Animal>` is usable where an `Action<Dog>` is wanted. `Func<T>` only produces one, an output position, so `out` applies.

</details>

## Know this

**A delegate is a type.** Specifically, a type that represents references to methods with a particular parameter list and return type, and the documentation's other description is worth having too: a type that safely encapsulates a method, similar to a function pointer in C, except object-oriented, type safe and secure ([Using Delegates](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/delegates/using-delegates)). Instantiate one with a method name or a lambda, and invoking it calls the method with the arguments you passed.

Java's answer to the same problem is a functional interface: a type you declare as an interface with a single method. C#'s is a type declared as a delegate, and the framework ships the ones you usually want, `Func`, `Action` and `Predicate`, which is why most C# code never declares a delegate type at all. That is also what lesson 13 meant: a lambda over an in-memory sequence becomes an instance of a delegate type.

**One precision that catches people, and it is the opposite of the overloading rule.** In method overloading, a method's signature does **not** include its return value. In the context of delegates it **does**: a method must have a return type compatible with the delegate's. So two methods that could not be overloads of each other can be indistinguishable to a delegate, and a method that differs only in return type does not fit.

**Delegates are multicast, and this is where the hazards live.** You can assign several methods to one delegate instance with `+`, producing a delegate that contains a **list** of them, and calling it invokes them **in order**. Only delegates of the same type combine, and `-` removes a component. Combining leaves the original delegates unchanged.

Then three documented consequences, and the first two are the ones to remember:

- **If any method throws an exception that is not caught inside it, the exception passes to the caller of the delegate and no subsequent methods in the invocation list are called.** One badly behaved handler silences every handler after it.
- **If the delegate has a return value or `out` parameters, you get those of the last method invoked.** Every earlier return value is discarded, which is why a multicast delegate with a return type is almost always a design mistake.
- Reference parameters are passed to each method in turn, so a change made by one is visible to the next.

**Events are the delegate model, which is the observer pattern.** A subscriber registers with a provider and receives notifications; the sender pushes, the receiver defines the response. The class that raises the event is the **publisher** and the classes that handle it are **subscribers**.

The `event` keyword declares a member whose type is a **delegate type**. Users attach executable code by supplying **event handlers**, which are delegate instances added to the event, and when the object triggers the event it invokes **all** supplied handlers. What the keyword changes is what outside code may do: event users can **add or remove** their handlers, and that is all. They cannot assign over the list, clear it, or raise the event themselves.

That restriction is the whole value, and it is worth comparing with the alternative. A public delegate **field** would let any caller do `handlers = MyHandler`, discarding every other subscriber, or invoke it to fake a notification. Java has no `event` keyword, so the equivalent is a listener interface with `addXListener` and `removeXListener` methods written by hand, and nothing in the language stops a class from also exposing the list. `event` is that convention promoted into the language and enforced.

**Four documented properties that read as a design checklist.**

|Property|What it means for your code|
|---|---|
|The publisher decides when it is raised; subscribers decide what happens|The publisher must not depend on any particular subscriber existing|
|An event may have many subscribers, and a subscriber may handle many events|Neither side owns the other|
|**Events that have no subscribers are never raised**|The raise site has to cope with there being no handlers at all|
|Handlers are invoked **synchronously**|A slow handler blocks the publisher, and every handler after it|

**And the convention to follow.** In the .NET class library, events are based on the `EventHandler` delegate and the `EventArgs` base class, with the generic `EventHandler<TEventArgs>` for events carrying data. The naming pattern is that every event data class ends with the `EventArgs` suffix, and `EventArgs` is both the usual base type and what you use when the event carries no data at all, passing `EventArgs.Empty`. Following that convention is how your event looks like every other event in the framework, which matters more here than it sounds: subscribers recognise the shape.

## Practice

1. ▢ `delegate void Callback(string s);` and a method `string Describe(string s)`. The method does not fit the delegate. Why, given that overload resolution ignores return types?

<details markdown="1"><summary>Check</summary>

Because the two contexts use different definitions of a signature. For overloading, a method's signature does not include the return value, so you cannot overload on return type alone. For delegates it **does**, and the documentation says so explicitly: a method must have a return type compatible with the delegate's declared return type.

So `Describe` is simply not a `Callback`, and the fix is a delegate type that returns `string`, or `Func<string, string>` from the framework. Worth holding as a general reading habit: when a compiler error says a method does not match a delegate and the parameters look right, check the return type first.

</details>

2. ▢ A delegate has three methods in its invocation list. The second throws an exception it does not catch. Predict what the caller sees and whether the third method runs. Then say what happens if the delegate has a return value.

<details markdown="1"><summary>Hint</summary>

The invocation list is walked in order. Ask what an uncaught exception does to a walk.

</details>

<details markdown="1"><summary>Check</summary>

The exception passes to the caller of the delegate, and **no subsequent methods are called**, so the third method never runs. The first one has already run and its effects stand, which makes this a partial-completion failure rather than a clean one.

If the delegate has a return value or `out` parameters, the caller gets those of the **last method invoked**, and every earlier result is discarded. That is why a multicast delegate with a meaningful return type is nearly always a mistake: you are collecting answers and keeping one, chosen by registration order.

The practical rule for an event: a handler that can throw should catch its own exceptions, because if it does not, it takes every later subscriber down with it and the publisher gets the exception from a call it made on someone else's behalf.

</details>

3. ▢ You could declare `public Action<Order> OrderPlaced;` as a plain field instead of `public event Action<Order> OrderPlaced;`. What does the keyword take away, and what does that buy?

<details markdown="1"><summary>Check</summary>

It takes away everything except `+=` and `-=` for outside code. Event users can add or remove their own handlers and nothing else.

With a plain field, any caller can write `OrderPlaced = MyHandler`, silently discarding every other subscriber, or invoke it to fabricate a notification that never happened. Both are bugs that are invisible at the declaration and hard to find later, because the code doing the damage looks like an ordinary assignment.

What it buys, then, is that the publisher keeps sole control of two things: who is in the list stays additive from outside, and raising remains the publisher's decision. Java's equivalent is `addListener` and `removeListener` written by hand, which achieves the same thing by convention and can be undermined by any class that also exposes the list.

</details>

4. ▢ Two documented facts: events with no subscribers are never raised, and handlers are invoked synchronously. What does each one require of the code that raises the event?

<details markdown="1"><summary>Check</summary>

The first means the raise site cannot assume there is anyone to notify: with no subscribers there is nothing to invoke, so raising has to cope with an empty handler list rather than treating notification as guaranteed. Code that reads as though the event always reaches someone is wrong on the first run with no subscribers.

The second means the publisher pays for its subscribers. Handlers run synchronously, in order, on the publisher's thread, so a slow handler delays the publisher and every handler queued behind it, and a handler that blocks stops the whole notification. A publisher raising an event inside a lock, or on a UI thread, has handed control to code it does not own. If the work must be slow, that belongs to the subscriber to move elsewhere, and stage 4 is where the tools for doing so arrive.

</details>

5. ▢ Which claim about a multicast delegate is correct?

   - a) A multicast delegate calls every handler, and later exceptions are collected together
   - b) A multicast delegate stops at the first handler that throws an exception
   - c) A multicast delegate returns the combined results of every handler it invoked
   - d) A multicast delegate invokes its handlers in an unspecified and nondeterministic order

<details markdown="1"><summary>Check</summary>

**b)** An uncaught exception passes to the caller and no subsequent methods in the invocation list are called. (a) describes what you might wish happened, and no such aggregation exists here. (c) is wrong in a specific way worth knowing: you get the return value of the last method invoked, and the rest are discarded. (d) is wrong too, and its wrongness matters: the list is invoked **in order**, which is why the last registration decides a return value and why one throwing handler determines which of the others ran.

</details>

## Real-world reps

- [ ] Find an event declaration in C# you have access to. Check whether it follows the `EventHandler` and `EventArgs` convention, and whether a subscriber would recognise its shape.
- [ ] Find an event handler that can throw. Decide what happens to the other subscribers when it does, and whether anyone would notice.
- [ ] Tomorrow: search a codebase you can reach for a public delegate-typed field with no `event` keyword. For each, work out what an outside caller could do to it that the author did not intend.

## Going further

- [Docs: "Using Delegates", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/delegates/using-delegates)
- [Docs: "Handling and raising events", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/standard/events/)
- [Docs: "The event keyword", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/event)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
