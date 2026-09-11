---
title: The Module System
description: The stage 8 sheet, with the three conditions for cross-module access, what each directive actually does, and where a jar's code ends up depending on which path launched it
type: reference
---

# The Module System

## The three conditions for cross-module access

All three, or the type is unreachable. See [lesson 50](../lessons/0050-the-module-system.md).

| Condition | What it checks |
|---|---|
| The type itself is `public` | the ordinary visibility keyword, necessary but no longer sufficient on its own |
| Its package is `exported` by its own module | a public type in an unexported package is invisible past the module boundary |
| The using module `requires` (reads) the exporting module | an edge in the module graph, built at launch by module resolution |

## What each directive actually does

See [lesson 50](../lessons/0050-the-module-system.md).

| Directive | At compile time | At run time |
|---|---|---|
| `exports pkg` | a module that `requires` this one can compile against `pkg`'s public types | the same access continues |
| `opens pkg` | the package stays exactly as encapsulated as if neither directive existed; nothing compiles against it directly | reflection reaches every member, public or not, via `setAccessible` |
| `open module` | opens every package the module contains, as if each carried its own `opens` | same, for all packages; a further `opens` on one of them is then a compile error |

## Where a jar's code ends up

The same file behaves differently depending only on which path it is placed on at launch. See [lesson 50](../lessons/0050-the-module-system.md).

| Situation | Becomes | Encapsulation |
|---|---|---|
| Has `module-info.class`, on the module path | A named module | Full: `requires`/`exports` enforced by the compiler and the runtime |
| A plain jar, no descriptor, on the module path | An automatic module | None: exports and opens every package it contains, for compatibility |
| Any jar's classes, loaded from the class path | Merged into the one unnamed module | None: reads every module in the graph, exports and opens all of its own packages |

## Building a runtime image with jlink

`jlink --module-path <path> --add-modules <mod> --output <dir>` links only the named modules' transitive `requires` closure into a working `bin/java`. See [lesson 51](../lessons/0051-runtime-images.md).

| Fact | Consequence |
|---|---|
| Only explicit (named) modules can be linked | an application depending on even one automatic module cannot be linked into an image at all, not degraded, refused |
| Services are not bound by default | a module supplying a `ServiceLoader` implementation needs `--add-modules` naming it explicitly, or `--bind-services` for all of them |
| Optional (`requires static`) dependencies are not resolved automatically | an application that runs fine normally can still fail to include an optional dependency in a linked image |
| `--strip-debug`, `--compress={0,1,2}`, `--include-locales` | the documentation's own worked example: 23M stripped and compressed versus 36M without, same module set |

## jpackage: modular versus non-modular input

`jpackage` builds or accepts a runtime image and produces a platform application image or installer. See [lesson 51](../lessons/0051-runtime-images.md).

| Input | What happens |
|---|---|
| `-m module/class`, a real module | passed straight to jlink; the identical automatic-module refusal applies |
| `--main-class` + `--main-jar`, non-modular | jlink is run with a default platform module set instead of linking the app's own code; the jar rides inside the image as ordinary classpath content |
| `--runtime-image <dir>` | a pre-built image is copied in instead of jpackage running jlink itself |
| No `--jlink-options` given | defaults to `--strip-native-commands --strip-debug --no-man-pages --no-header-files` |

## Reflection and annotation retention

The two primitives every out-of-scope framework is built from. See [lesson 52](../lessons/0052-reflection-and-annotations.md).

| Retention | Reaches the class file? | Reflectively visible? |
|---|---|---|
| `SOURCE` | No, discarded by the compiler | No |
| `CLASS` (the default if `@Retention` is omitted) | Yes | No, the VM need not keep it |
| `RUNTIME` | Yes | Yes, via `getAnnotation`/`isAnnotationPresent` |

`@Target` restricts which kinds of declarations an annotation may be placed on, checked by the compiler; it says nothing about retention, which is a separate, orthogonal declaration.

Reflection operates within the same encapsulation lesson 50 already described: `setAccessible` on a member in a package that is neither exported nor opened throws `InaccessibleObjectException`, regardless of the member's own visibility keyword.

## Symptom to cause

Populated only from failures the lessons actually reproduced.

| Symptom | What it actually means |
|---|---|
| A compile error naming a package as inaccessible, on a type that is `public` | strong encapsulation: the package is not exported, or the calling module does not read the exporting one; `public` alone stopped being sufficient (lesson 50) |
| `InaccessibleObjectException` from `setAccessible(true)` | the target package is neither `exported` nor `opened`; before the module system, `setAccessible` could reach any private member of any jar with no such gate (lesson 50) |
| A missing `requires` module is reported before any application code runs at all | module resolution follows every `requires` edge outward from the initial module at launch, and fails immediately if one is missing, earlier than the class-path era's `NoClassDefFoundError` (lesson 50) |
| `jlink` fails on a dependency that runs fine normally | that dependency has no `module-info.class` of its own, so it became an automatic module the moment it hit the module path, and `jlink` only links explicit modules (lesson 51) |
| A service or an optional dependency the application uses is missing from a linked image | `jlink`'s resolution does not bind services or resolve `requires static` dependencies by default, unlike an ordinary launch (lesson 51) |
| A custom annotation compiles, attaches, and is never seen by `getAnnotation`/`isAnnotationPresent` | it has no `@Retention(RetentionPolicy.RUNTIME)`; with `@Retention` omitted the default is `CLASS`, recorded in the class file but not kept by the VM at run time (lesson 52) |
| `InaccessibleObjectException` from a framework's own reflective field access, on a package that is `exported` | `exports` grants compile- and run-time access to public members only; reflective access to a field, public or not, needs `opens` specifically (lesson 52) |

## Sources

- [Introduction to Modules in Java, dev.java](https://dev.java/learn/modules/intro/): module declarations, `requires`, `exports`, strong encapsulation, module resolution and the module graph
- [Reflective Access with Open Modules and Open Packages, dev.java](https://dev.java/learn/modules/opening-for-reflection/): `opens`, open modules, and exactly what changes at compile time versus run time
- [Code on the Class Path - the Unnamed Module, dev.java](https://dev.java/learn/modules/unnamed-module/): the unnamed module's name, dependencies and exports
- [Incremental Modularization with Automatic Modules, dev.java](https://dev.java/learn/modules/automatic-module/): what an automatic module exports and opens, and why
- [The jlink Command, Oracle](https://docs.oracle.com/en/java/javase/25/docs/specs/man/jlink.html): options, the automatic-module refusal, and the stripping/compression examples
- [The jpackage Command, Oracle](https://docs.oracle.com/en/java/javase/25/docs/specs/man/jpackage.html): modular versus non-modular input, and the default jlink options
- [Creating Runtime and Application Images with JLink, dev.java](https://dev.java/learn/jlink/): worked examples of building a runtime image and an application image
- [Package java.lang.reflect, Oracle](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/package-summary.html): what reflection is, and its own encapsulation and security restrictions
- [RetentionPolicy, Oracle](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/annotation/RetentionPolicy.html): the three constants
- [Retention, Oracle](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/annotation/Retention.html): the documented `CLASS` default when `@Retention` is omitted
