---
title: Resources
description: "Trusted sources for C#"
type: resources
---

# C# Resources

## Knowledge

- [Docs: "Types (C# reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/types/)
  Official docs on C#'s value-type/reference-type split, the distinction that decides where a struct belongs versus a class. Use for: the type-system foundation everything else in this workspace assumes.
- [Docs: "Structure types (C# reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/struct)
  Official reference for when a struct is the right choice, and what copy semantics and allocation behavior it brings that a class doesn't. Use for: naming precisely where a Java habit (everything is a class) misleads.
- [Docs: "Exception-handling statements (C# reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/exception-handling-statements)
  Official reference for `try`, `catch`, `finally` and `throw`, including `throw` as an expression, and the `when` exception filter with the section that justifies it: a filter does not unwind the stack, so a false filter leaves the original stack trace unchanged, while a clause that catches and rethrows has already lost it. Also the ordering rules a filter relaxes. Use for: handling only some exceptions of a type without destroying the trace.
- [Docs: "Handling and throwing exceptions in .NET", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/standard/exceptions/)
  The common-exceptions table with what each one's presence implies, including that `NullReferenceException` and `IndexOutOfRangeException` are thrown by the runtime only, so they indicate a bug rather than a condition to handle. Use for: reading an exception type as a diagnosis.
- [Docs: "using statement (C# reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/using)
  Official reference for `using` as C#'s deterministic cleanup: the instance is disposed when control leaves the block, explicitly including departure by exception, plus the `using` declaration form and `await using` for `IAsyncDisposable`. Use for: the counterpart to Java's try-with-resources.
- [Docs: "Selection statements (C# reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/selection-statements)
  Official reference for `if` and `switch`, including the two rules a Java background needs: every switch section must end with `break`, `goto` or `return` and falling through is a compiler error, while multiple labels on one section are supported deliberately. Also that a switch matches patterns rather than only constants, and how the switch statement differs from the switch expression. Use for: writing a `switch` without importing Java's fall-through.
- [Docs: "Iteration statements (C# reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/iteration-statements)
  Official reference for `for`, `foreach`, `do` and `while`, with the part worth reading closely: `foreach` needs only a public parameterless `GetEnumerator` (an extension method counts) returning a type with `Current` and `MoveNext`, so it works on types implementing no interfaces, and an explicitly typed iteration variable can throw `InvalidCastException` at run time. Use for: why a type can iterate without being queryable.
- [Docs: "Jump statements (C# reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/jump-statements)
  Official reference for `break`, `continue`, `return` and `goto`, including `goto` to escape a nested loop and `goto case` inside a switch, with the tip to refactor nested loops into separate methods instead. Use for: the C# answer to Java's labelled break, which C# does not have.
- [Docs: "Collections and Data Structures", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/standard/collections/)
  Orientation for the collection types: the advice to prefer generic collections, a table matching a scenario to a type, algorithmic complexity for the mutable types against their immutable counterparts, and the statement that any type implementing `IEnumerable<T>` is a queryable type that LINQ can query. Use for: choosing a container, and for why LINQ is defined over an interface rather than over a class.
- [API: "Dictionary<TKey,TValue>", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.dictionary-2)
  Reference with the failure modes spelled out in its own example: the read indexer throws `KeyNotFoundException` for an absent key, `Add` throws `ArgumentException` for a duplicate one, and `TryGetValue` is recommended where misses are expected. Also the hash-table caveats, that retrieval speed depends on `TKey`'s hashing and that a key must not change in a way that affects its hash while in use. Use for: the operation table every dictionary read should be checked against.
- [API: "IEnumerable<T>", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.ienumerable-1)
  Reference for the one-method interface behind `foreach`, declared `IEnumerable<out T>`, implemented by `List<T>`, `Dictionary<TKey,TValue>`, `Stack<T>` and the rest. Use for: writing a signature that asks only to enumerate, and as the definition the LINQ and `IAsyncEnumerable` lessons both build on.
- [Docs: "Built-in types (C# reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/built-in-types)
  The keyword-to-.NET-type table, with the statement that the keywords are aliases and interchangeable with the types they name (so `int` is `System.Int32`, and `float` is `System.Single`). Use for: reading any signature, and for why C# has no primitive-versus-wrapper split to import from Java.
- [Docs: "Floating-point numeric types (C# reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/floating-point-numeric-types)
  Range, precision and size for `float`, `double` and `decimal` side by side, plus which of them provide the not-a-number and infinity constants (`float` and `double` do, `decimal` does not). Use for: defending a numeric type choice from the numbers, money especially.
- [Docs: "String interpolation using $", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/tokens/interpolated)
  Official reference for `$"..."`: the hole's grammar of expression, optional width and optional format string, that a null expression renders as the empty string, brace escaping, interpolated verbatim and raw string literals (including the multiple-`$` rule for embedding braces), and the compilation section with its warning that a handler might not evaluate every interpolation expression, so side effects might not occur. Use for: formatting output, and for why an interpolation hole must not do work.
- [Docs: "Nullable value types (C# reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/nullable-value-types)
  Official reference for `T?` as `Nullable<T>`: that its default value represents null as an instance whose `HasValue` is false, the four ways to get a value out and which of them throw, lifted operators propagating null (with `bool?`'s `&` and `|` as the exception), the rule that `<`, `>`, `<=` and `>=` all return false against null so opposite comparisons are not opposites, and boxing, which yields a null reference or the boxed underlying value rather than the wrapper. Use for: nullable numbers without the Java `Integer` instinct, and for why `GetType()` cannot see nullability.
- [Docs: "Task asynchronous programming model", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/task-asynchronous-programming-model)
  Official docs on `async`/`await` and the `Task`-based model underneath it: what actually happens to a method's execution when it awaits. Use for: understanding `async`/`await` as a mechanism, before comparing it to Java's virtual threads.
- [Docs: "Language Integrated Query (LINQ)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/linq/)
  Official docs for LINQ's query and method syntax over any enumerable source. Use for: the primary source for the LINQ-against-Stream-API comparison the mission names.
- [Docs: "ASP.NET Core fundamentals", Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/introduction-to-aspnet-core)
  Official entry point for building and structuring an ASP.NET Core backend service. Use for: the concrete service-building context this workspace ships a typed, tested service against.

## Gaps

- No source yet directly contrasting C#'s `async`/`await` against Java 21 virtual threads side by side, as opposed to reading each mechanism's own docs separately and inferring the comparison; worth closing once lesson design reaches that stage.
