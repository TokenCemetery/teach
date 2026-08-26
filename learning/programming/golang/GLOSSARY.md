# Go Glossary

Canonical terms for this workspace. A term lands here once it can be used correctly, not when it is first mentioned — so this grows as lessons are earned.

## Usage in this workspace

Two words mean something narrower in Go than they do in most other languages. Carrying the wider meaning across produces code that compiles and is still wrong, so both are pinned from the start:

**Interface**:
A set of method signatures that any type satisfies implicitly by having those methods. There is no declaration of intent and no `implements`.
_Avoid_: contract, abstract class, implements relationship

**Zero value**:
The usable default a variable holds when declared without initialisation — `0`, `""`, `nil`, or a struct with each field at its own zero value. Designing types so the zero value works is idiomatic Go.
_Avoid_: null, undefined, uninitialised

## Terms

_Added as lessons establish them._
