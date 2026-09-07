---
title: "27. Configuration"
description: "One flat dictionary of strings where the last provider wins, three options interfaces separated by lifetime rather than by taste, and validation that waits for the first request unless you ask it not to"
type: lesson
---

# Lesson 27. Configuration

**Mission link:** Every setting your service reads arrives from somewhere you did not look at while writing the code, and gets overridden by somewhere else you also did not look at. Shipping a typed service means the settings are typed too, validated somewhere you will notice, and reachable from a class whose lifetime does not fight the way configuration is delivered.
**Primary source:** [Docs: "Configuration in ASP.NET Core", Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/)
**Prerequisites:** [Lesson 26](0026-dependency-injection.md), [Lesson 15](0015-nullable-reference-types.md)

## Warm-up

1. ▢ Why can a scoped service not be injected into a singleton, and what is that mistake called?

<details markdown="1"><summary>Check</summary>

A captive dependency: the singleton is built once and would hold that one instance for the application's lifetime, promoting the shorter lifetime. In the development environment the default provider checks for exactly this.

</details>

2. ▢ What does `public string? Name { get; set; }` declare, and what does it not do at run time?

<details markdown="1"><summary>Check</summary>

It annotates the property as possibly null so the compiler can track null-state. It is not a different type and adds no runtime checking; `string` and `string?` are both `System.String`.

</details>

3. ▢ `appsettings.json`, `appsettings.Production.json` and an environment variable all set the same key to different values. What decides which one the app sees?

<details markdown="1"><summary>Check</summary>

Not the file, not the specificity of the name, and not anything visible from inside the code that reads the value. It is decided by the order the sources were added, which is the first half of this lesson.

</details>

## Know this

**Configuration is one flat dictionary of strings, and three of those words matter.** *Flat*: hierarchy is a naming convention, produced by flattening structured data with a delimiter in the key. *Strings*: **configuration values are strings**, and **null values cannot be stored in configuration or bound to objects** ([Configuration in ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/)). *One*: every provider contributes to the same dictionary, which is why they can overwrite each other.

The delimiter changes with the source, and this is the detail that costs an afternoon:

|Where the key is written|Delimiter|
|---|---|
|The Configuration API, and JSON files|a colon, `:`, which works on all platforms|
|Environment variables|a double underscore, `__`, **supported by all platforms and automatically converted into a colon**|
|Azure Key Vault|a double dash, `--`, replaced with a colon when secrets are loaded|

A colon **does not work with environment variables on all platforms**, Bash being the documented example. So `Logging:LogLevel:Default` in a shell is not a setting with an unusual name, it is not a setting at all. Keys are otherwise **case-insensitive**, so `ConnectionString` and `connectionstring` are the same key.

**Precedence is nothing but order: the last provider added wins.** Sources are **read in the order that their configuration providers are specified**, and **if a key and value is set by more than one configuration provider, the value from the last provider added is used**. The typical sequence is `appsettings.json`, then `appsettings.{ENVIRONMENT}.json`, then user secrets in Development, then environment variables, then the command line, which **by default overrides configuration values set by all of the other configuration providers**.

There is no merge, no precedence table keyed by importance, and no way to tell from the reading code which source answered. When production disagrees with the file you are looking at, the question is which provider came later, not which file is right.

**The options pattern is how you stop reading that dictionary by hand.** Bind a section to a class and inject the class ([Options pattern in ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/options)):

```csharp
builder.Services.Configure<PositionOptions>(
    builder.Configuration.GetSection(PositionOptions.Position));
```

This is what lesson 26's guideline pointed at when it said to keep data and configuration out of the service container. The container holds a typed object; the strings stay in the configuration system.

**Three options interfaces, and they are separated by lifetime rather than by convenience:**

|Interface|Registered as|Sees updated values|Named options|May be injected into|
|---|---|---|---|---|
|`IOptions<T>`|singleton|**no**, it does not support reading configuration data after the app has started|no|any lifetime|
|`IOptionsSnapshot<T>`|**scoped**|yes, a snapshot taken when the object is constructed, recomputed per request|yes|anything except a singleton|
|`IOptionsMonitor<T>`|singleton|yes, current values **at any time**, with change notifications|yes|any lifetime|

The middle row is lesson 26 arriving in a new costume. `IOptionsSnapshot<T>` **is registered as a scoped service, so it cannot be injected into a singleton service**, which is not a rule about options at all: it is the captive dependency rule, met the first time you try to read configuration from a long-lived object. `IOptionsMonitor<T>` exists for that case, being a singleton that **retrieves current option values at any time, which is especially useful in singleton dependencies**, while `IOptionsSnapshot<T>` **provides a snapshot of the options at the time the object is constructed** and is **designed for use with transient and scoped dependencies**.

So the choice is made by answering two questions in order. Does this class need values that can change while the app runs? Then, what is the lifetime of the class doing the reading?

**Validation runs later than almost anyone expects.** Options validation runs **the first time a `TOptions` instance is created**, which is the first access to `IOptionsSnapshot<TOptions>.Value` in a request pipeline, or a call to `IOptionsMonitor<TOptions>.Get`, and **each time options are reloaded, validation runs again**. A misconfigured deployment therefore starts successfully and fails on a request, which is the worst available ordering: the deployment is green, the traffic is not, and the rollback signal arrives from users.

Moving it is one line:

```csharp
builder.Services.AddOptions<KeyOptions>()
    .Bind(builder.Configuration.GetSection(KeyOptions.Key))
    .ValidateDataAnnotations()
    .ValidateOnStart();
```

`ValidateOnStart` is the difference between a deployment that fails and a deployment that succeeds and then serves errors.

**One small trap worth carrying.** Configuration keys are case-insensitive, but **named options are case sensitive**. Two casing rules inside one subject, and the compiler enforces neither.

**One forward pointer.** Lesson 28 is Entity Framework Core, whose connection string arrives through this mechanism and whose `DbContext` is the scoped service lesson 26 described in the abstract. Lesson 29 puts routing, injection, configuration and data access into one testable service, and that is where stage 6's capstone lands.

## Practice

1. ▢ Production is using a connection string that appears in none of the repository's files. Nobody edited anything. Where do you look, and in what order?

<details markdown="1"><summary>Check</summary>

At the provider order, because there is nothing else it could be. Sources are read in the order their providers are specified and the value from the **last provider added** is the one used, so the search runs backwards along that list: the command line first, since it overrides all other providers by default, then environment variables, then `appsettings.{ENVIRONMENT}.json`, then `appsettings.json`.

An environment variable is the usual answer, and it will be spelled `ConnectionStrings__DefaultConnection`, not with a colon. Note that the code reading the value cannot tell you any of this: the configuration system hands back a string with no record of which provider produced it.

</details>

2. ▢ A singleton background service needs a timeout that operators can change without a redeploy. You inject `IOptionsSnapshot<TimeoutOptions>` and the app fails. What went wrong, and what is the right interface?

<details markdown="1"><summary>Hint</summary>

Look up the lifetime each options interface is registered with, then reread lesson 26's table.

</details>

<details markdown="1"><summary>Check</summary>

`IOptionsSnapshot<T>` is registered as a **scoped** service, so it cannot be injected into a singleton. This is a captive dependency, and it is the same failure as a singleton taking a scoped repository; options are not a special case, they are simply the place most people meet the rule for the first time.

The right interface is `IOptionsMonitor<T>`, a singleton that retrieves current option values at any time and is described as especially useful in singleton dependencies. It also supports change notifications, which is what "without a redeploy" actually asks for.

`IOptions<T>` would inject cleanly and be wrong for a different reason: it does not support reading configuration data after the app has started, so the value would be whatever it was at startup, forever, with nothing to indicate that.

</details>

3. ▢ In a Bash shell you export `Logging:LogLevel:Default=Debug`, restart the app, and the log level does not change. Why?

<details markdown="1"><summary>Check</summary>

Because the colon separator does not work with environment variable hierarchical keys on all platforms, and Bash is the documented example. The double underscore is supported everywhere and is automatically converted into a colon when the configuration is read, so the variable has to be `Logging__LogLevel__Default`.

What makes this cost time is that nothing fails. The variable is set, the app starts, and the key you meant to override was simply never in the dictionary, so the value from `appsettings.json` is still there and still correct as far as the app is concerned. Compare Key Vault, where the same flattening is spelled with a double dash instead.

</details>

4. ▢ Your options class has a required property with a data annotation, and `ValidateDataAnnotations` is configured. A deployment goes out with that setting missing. What happens, and what would you change?

<details markdown="1"><summary>Check</summary>

The deployment succeeds. Validation runs the **first time a `TOptions` instance is created**, which is the first access to `IOptionsSnapshot<T>.Value` in a request pipeline or a call to `IOptionsMonitor<T>.Get`, so the failure surfaces on a request rather than at startup, and it surfaces once per affected code path rather than once.

Add `ValidateOnStart` to the chain, alongside `Bind` and `ValidateDataAnnotations`. The app then refuses to start, which is what you want: a deployment that fails is a rollback, while a deployment that starts and then throws on traffic is an incident.

Worth noticing that validation also runs again each time options are reloaded, so a reloadable configuration can turn a healthy process unhealthy without a deploy at all.

</details>

5. ▢ Which statement is correct?

    - a) Configuration values keep the types they had in the source, so a JSON number arrives as a number and a JSON null binds to a null property
    - b) Configuration values are strings, keys are case-insensitive, and where two providers set the same key the value from the last provider added is used
    - c) `IOptions<T>` re-reads configuration when the underlying file changes, which is why it is registered as a singleton
    - d) `IOptionsSnapshot<T>` is a singleton, making it the right choice for reading options inside another singleton

<details markdown="1"><summary>Check</summary>

**b)** All three clauses are documented, and together they describe the whole model: one dictionary, string values, order decides.

(a) fails twice: values are strings, and **null values cannot be stored in configuration or bound to objects**, so a null in a source is not a way to unset something. (c) inverts `IOptions<T>`, which does **not** support reading configuration data after the app has started. (d) swaps the two interfaces: `IOptionsSnapshot<T>` is scoped and cannot go into a singleton, and `IOptionsMonitor<T>` is the singleton one.

</details>

## Real-world reps

- [ ] List the configuration providers a service you have access to registers, in order. Pick one key and say which provider wins for it.
- [ ] Find a settings class in that service. Note which options interface is injected, and the lifetime of the class injecting it.
- [ ] Tomorrow: check whether any of its options are validated at all, and if so whether validation happens at startup or on the first request.

## Going further

- [Docs: "Configuration in ASP.NET Core", Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/)
- [Docs: "Options pattern in ASP.NET Core", Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/options)
- [Docs: "Options pattern in .NET", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/core/extensions/options)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
