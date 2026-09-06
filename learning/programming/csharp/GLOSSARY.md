---
title: Glossary
description: "Canonical terms for C#"
type: glossary
---

# C# Glossary

Canonical terms for owning a C# service, and for naming precisely where a Java instinct misleads.

## Terms

**Reference type**:
A type (every `class`) where assigning a variable of that type copies a reference, not the underlying data; two variables can point at the same object, and a mutation through either is visible through both.
_Avoid_: object type (ambiguous with C#'s `object` base type)

**Value type**:
A type (every `struct`, plus the built-in numeric types) where assigning, passing, or returning a variable of that type copies the entire value; two variables of a value type are always independent copies.
_Avoid_: primitive type (too narrow; a user-defined struct is a value type too)
