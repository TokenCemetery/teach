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
- [Docs: "Task asynchronous programming model", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/task-asynchronous-programming-model)
  Official docs on `async`/`await` and the `Task`-based model underneath it: what actually happens to a method's execution when it awaits. Use for: understanding `async`/`await` as a mechanism, before comparing it to Java's virtual threads.
- [Docs: "Language Integrated Query (LINQ)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/linq/)
  Official docs for LINQ's query and method syntax over any enumerable source. Use for: the primary source for the LINQ-against-Stream-API comparison the mission names.
- [Docs: "ASP.NET Core fundamentals", Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/introduction-to-aspnet-core)
  Official entry point for building and structuring an ASP.NET Core backend service. Use for: the concrete service-building context this workspace ships a typed, tested service against.

## Gaps

- No source yet directly contrasting C#'s `async`/`await` against Java 21 virtual threads side by side, as opposed to reading each mechanism's own docs separately and inferring the comparison; worth closing once lesson design reaches that stage.
