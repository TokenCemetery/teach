---
title: "31. Reviewing a C# Codebase"
description: "The difference between a style opinion and a cost you can name, a review pass ordered by what the compiler will never tell you, and the habits this arc has been collecting since lesson 1"
type: lesson
---

# Lesson 31. Reviewing a C# Codebase

**Mission link:** The mission ends here: given C# written with a habit that merely compiles, name the habit and rewrite it idiomatically. Every earlier lesson collected one of those habits and, more importantly, the cost that makes it a habit rather than a preference. This lesson is the index, and the argument for reviewing in the order that puts the invisible failures first.
**Primary source:** [Docs: "Common C# code conventions", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)
**Prerequisites:** [Lesson 30](0030-two-comparisons-with-java.md), [Lesson 16](0016-expression-bodied-members.md), [Lesson 1](0001-structs-and-classes.md)

## Warm-up

1. ▢ Name one thing a C# compiler will happily accept that this arc has argued you should not write.

<details markdown="1"><summary>Check</summary>

There are many, and the point of the question is that the list is long: `async void` on something that is not an event handler, a scoped service injected into a singleton, an assertion on a non-virtual member, a class where value semantics were wanted. None of them is a compiler error, and that is exactly what makes them worth a review.

</details>

2. ▢ What was wrong with mocking a class whose members are not `virtual`?

<details markdown="1"><summary>Check</summary>

Two things, both silent: the real code runs inside what you believed was a fake, and an assertion on a non-overridable member does not run an assertion at all, so it passes even when the call never happened.

</details>

3. ▢ A reviewer writes "this should be a record". Is that a review comment?

<details markdown="1"><summary>Check</summary>

Not yet. It is a preference until it names what the current code costs. This lesson is largely about the difference between those two sentences.

</details>

## Know this

**A review comment is worth what its cost statement is worth.** "Make this a record" is an opinion, and the author is entitled to disagree with it. "This type has value semantics in every other respect, so as a class two equal orders compare unequal, and the dictionary lookup two files away silently misses" is a cost, and there is nothing to disagree with. The whole arc has been assembling the second kind of sentence, which is why it spent so long on what each construct actually does at run time.

Three questions turn a reaction into a comment:

- **What does this construct promise?**
- **Who pays for the promise, and in what currency?** A signature, a lock, a round trip, a lifetime.
- **When would you find out it was broken?** This is the one that ranks the finding.

**Give the mechanical half to the tools, and mean it.** Conventions exist for readability, consistency and collaboration, and the documentation is clear that they are enforceable rather than negotiable in review: enable **code analysis** to enforce the rules you choose, and add an **`.editorconfig`** so the editor applies them, after which **code analysis produces warnings and diagnostics when it detects rule violations** and **each CI build notifies developers when they violate any of the rules** ([Common C# code conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)).

A human review spent on brace placement is a review not spent on a captive dependency. Configure the first, then never discuss it again.

**Some guidance is still a judgment, and the conventions say so in the language of costs.** Three from the same page are worth carrying into a review, because each names a consequence rather than a taste:

- **Only catch exceptions that can be properly handled**, and avoid catching general exceptions, with the documentation's own rule that sample code should not catch `System.Exception` without an exception filter. Use specific exception types.
- **Use asynchronous programming with `async` and `await` for I/O-bound operations**, and be cautious of deadlocks.
- Use implicit typing **when the type is obvious from the right side of the assignment**, and **do not assume the type is clear from a method name**. A type counts as clear when the right side is a `new` operator, an explicit cast, or a literal.

That third one is a reading rule disguised as a writing rule. `var total = Compute();` tells a reviewer nothing, and a reviewer who cannot see the type cannot see the cost.

**The review pass, ordered by what the compiler will never tell you.** This is the arc as a checklist. Read the third column first, because it is what decides which comment to write when you only have the attention for one:

|What you see|What it costs|How you would find out|
|---|---|---|
|A class where the values are compared, not identified|reference equality, so two equal values are unequal and a lookup misses|a wrong result, eventually (lessons 1, 8)|
|`catch (Exception)` with no filter, or `throw ex` in the handler|the stack trace, and errors you had no plan for|an unactionable log entry (lesson 6)|
|`async void` outside an event handler|the caller's only way to observe completion or failure|an unobserved exception, or a silent no-op (lesson 18)|
|Sequential `await`s over independent work|the overlap you meant to have|a latency number nobody questions (lesson 19)|
|A method that can take time and takes no `CancellationToken`|a decision made on the caller's behalf|never, which is the problem (lesson 20)|
|An assertion on a non-virtual member of a substituted class|the test|the test passes forever (lesson 23)|
|`AddSingleton` on something holding a scoped dependency|the shorter lifetime, silently promoted|under load, or in the development-time scope check (lesson 26)|
|`IOptions<T>` where the value must change while running|the reconfiguration|never, since it fails by doing nothing (lesson 27)|
|Two operations started on one `DbContext` before either is awaited|the context, and possibly the data|intermittently, or as corruption (lesson 28)|
|A `PackageReference` version read as a pin|reproducibility|a build that changed with no commit (lesson 24)|

Notice the third column. Almost none of these announce themselves. That is the argument for reviewing in this order rather than top to bottom through the file: the findings worth your attention are the ones no other mechanism will report.

**Name the habit, then write the replacement.** The mission asks for both halves, and the second is not politeness. A comment that names a cost and stops leaves the author holding a verdict with no move, and the most common result is a change that relocates the problem. "Take a `CancellationToken` and pass it to the calls inside" is a review. "This is not cancellable" is a complaint.

**Where the arc leaves you, honestly.** You can model a domain and defend the choice from what the CLR does; read and write `async` code and say what happens to a method at each `await`; query with LINQ and know where the query stops being SQL; ship a service whose lifetimes, configuration and data access agree with each other; and take an unfamiliar C# file apart by asking what each construct promises and who pays.

What this arc did not cover is worth saying too, because knowing the edge of your own map is part of the same skill: Unity and game development, CLR internals past what explains value semantics and `async`, parallel LINQ, and the security and operational concerns of running the service you can now build. Each of those is a topic, not a footnote, and treating them as gaps you know about is more useful than the feeling of having finished.

## Practice

1. ▢ Two reviewers comment on the same line, which reads `catch (Exception) { }`. One writes "don't swallow exceptions". The other writes something better. What?

<details markdown="1"><summary>Check</summary>

Something that names the cost and the replacement. For example: this catches errors nobody planned for, so a bug in the block above becomes a silent no-op and the log has nothing in it; catch the specific exception you can act on, or add an exception filter, and let the rest go up.

Both comments point at the same line and only one is actionable. The convention behind it is stated as a rule with a reason: **only catch exceptions that can be properly handled**, avoid catching general exceptions, and use specific exception types.

There is a second-order cost worth adding when the block sits in a loop over tracked entities. Swallowing the failure does not undo the modifications already made in earlier iterations, and `SaveChanges` will still write them, so the empty handler converts a loud failure into a partial write.

</details>

2. ▢ Sort these into "an analyzer should catch this" and "only a person will catch this": brace placement, a scoped service injected into a singleton, `System.String` written instead of `string`, and a repository interface whose method cannot be cancelled.

<details markdown="1"><summary>Check</summary>

Analyzer: brace placement and `System.String` instead of `string`, both mechanical, both covered by conventions, both enforceable through an `.editorconfig` and code analysis so that **each CI build notifies developers when they violate any of the rules**.

Person, mostly: the missing `CancellationToken`, because whether a method can take long enough to be worth cancelling is a judgment about the method's job.

The scoped service in a singleton is the interesting one, because it belongs to a third category: not an analyzer, but not a person either. The development-time scope check finds it, and `validateScopes: true` finds it on demand. The review skill there is knowing that the mechanism exists and that it only runs when someone runs the app in Development.

That three-way split is the practical form of this lesson. Automate the mechanical, know which failures have their own detector, and spend the human attention on what is left.

</details>

3. ▢ A file is full of `var`. Which of these declarations does the guidance allow, and why does it matter to a reviewer rather than to the compiler?

   - `var message = "This is clearly a string.";`
   - `var count = ExampleClass.ResultSoFar();`
   - `var order = new Order();`

<details markdown="1"><summary>Check</summary>

The first and third. Implicit typing is for when **the type is obvious from the right side of the assignment**, and a type counts as clear when the right side is a `new` operator, an explicit cast, or a literal value. The second breaks the rule the guidance states directly: **do not assume the type is clear from a method name**.

Why it matters to a reviewer is the part worth keeping. Every finding in this lesson's table depends on knowing what type something is. Is it a struct or a class, a `Task` or a `ValueTask`, an `IOptions<T>` or an `IOptionsSnapshot<T>`, an `IQueryable<T>` that will become SQL or an `IEnumerable<T>` that already left the database. A `var` whose type is not apparent does not slow the compiler down at all; it hides exactly the information a review runs on.

</details>

4. ▢ Which statement is correct?

   - a) A good review finds every deviation from the team's conventions, since consistency is what conventions are for
   - b) The findings worth a reviewer's attention are the ones no other mechanism reports, because most of them fail silently
   - c) Naming the cost is enough; proposing the rewrite is the author's job
   - d) A construct that compiles and passes its tests has been reviewed by better tools than a person

<details markdown="1"><summary>Check</summary>

**b)** Conventions are enforceable by code analysis and an `.editorconfig`, so a person spending attention there is duplicating a build step, while the failures this arc collected mostly announce themselves late or not at all.

(a) describes work a tool does better and never gets tired of. (c) leaves the author with a verdict and no move, which is how a problem gets relocated instead of fixed, and the mission asks for both halves for that reason. (d) is refuted by most of the table: a mocked non-virtual member passes its test precisely because it is broken, and a captive dependency compiles perfectly.

</details>

5. ▢ **The last exercise.** Review this. Name at least four habits, and for each say what it costs and what you would write instead.

```csharp
public class OrderService
{
    private readonly ApplicationDbContext _db;

    public OrderService(ApplicationDbContext db) => _db = db;

    public async void Recalculate(IEnumerable<int> orderIds, decimal multiplier)
    {
        var tasks = orderIds.Select(id => _db.Orders.FindAsync(id).AsTask());
        var orders = await Task.WhenAll(tasks);

        foreach (var order in orders)
        {
            try
            {
                order.Total = order.Subtotal * multiplier;
            }
            catch (Exception)
            {
            }
        }

        await _db.SaveChangesAsync();
    }
}
```

<details markdown="1"><summary>Check</summary>

**`async void` on a method that is not an event handler.** It costs the caller every means of knowing this finished or failed: the task cannot be awaited, and an exception has nowhere to go. Return `Task`, and make the caller await it.

**`Task.WhenAll` over several operations on one `DbContext`.** EF Core does not support multiple parallel operations on the same instance, explicitly including parallel async queries, and the injected context is one instance for the request. It costs the context, and undetected, the data. Await each lookup in turn, or fetch them in a single query, which is better here anyway: one round trip instead of many.

**No `CancellationToken`.** A method that hits the database for every identifier it is given can take arbitrarily long, and a caller who has stopped caring has no way to say so. Take a token, pass it to the EF calls and to `SaveChangesAsync`.

**`catch (Exception) { }` around an assignment.** It catches errors nobody planned for and produces nothing to investigate. Worse in this exact position: the entities are tracked, so the modifications made before the swallowed failure are still pending, and `SaveChangesAsync` writes them. A partial recalculation is committed and reported as success. Remove the handler, or catch the one exception you can act on.

**One more, for the reader who has the whole arc in view.** The mutation is invisible as a database write. There is no update call, only an assignment to a tracked entity, which is the whole point of change tracking and the reason the previous finding is as bad as it is. If this method were ever changed to normalise a field for display, that too would be written.

A rewrite that fixes all of it is shorter than the original: a `Task`-returning method taking a `CancellationToken`, one query loading the orders it needs, a loop that assigns, and one `SaveChangesAsync`. That is the shape the mission was asking for, and being able to produce it from a first reading is what the last thirty lessons were for.

</details>

## Real-world reps

- [ ] Take a C# file you did not write and run this lesson's table down it. Note which findings you could state as a cost, and which are still preferences.
- [ ] Check whether the repository has an `.editorconfig` and code analysis enabled. If not, that is the first review comment, and it retires a whole category of them.
- [ ] Tomorrow: write one review comment that names a cost and proposes the rewrite, and notice how differently it is answered.

## Going further

- [Docs: "Common C# code conventions", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)
- [Docs: "Handling and throwing exceptions in .NET", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/standard/exceptions/)
- [Docs: "async keyword", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/async)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
