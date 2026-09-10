---
title: Glossary
description: "Canonical terms for Bash"
type: glossary
---

# Bash Glossary

Canonical terms for shell that survives production: what an unquoted expansion actually does, and the failure modes that follow from it.

## Terms

**Associative array**:
A bash-only array indexed by arbitrary string keys instead of sequential positions, declared with `declare -A` before assignment.
_Avoid_: hash, dictionary, map (say "associative array", the shell's own term, even though the concept is the same one those words name elsewhere)

**Command substitution**:
Running a command and replacing `$(command)` with what it wrote to standard output, trailing newlines stripped.
_Avoid_: backtick substitution (use for the older, non-nesting `` ` ` `` syntax specifically, not the concept)

**Indexed array**:
A bash-only array whose elements sit at sequential integer positions starting at `0`, created with `arr=(a b c)`.
_Avoid_: list, plain array (say "indexed array" once associative arrays are also in scope, so the two aren't confused)

**Local variable**:
A variable declared with `local` inside a function, scoped to that function call rather than persisting in the calling shell's environment.
_Avoid_: function-scoped variable (say "local variable", matching the keyword)

**Parameter expansion**:
A `${...}` form that defaults, validates, transforms, or measures a variable's value inline, rather than merely reading it back.
_Avoid_: variable substitution (reserve "substitution" for command substitution specifically, to keep the two distinct)

**Pathname expansion (globbing)**:
Replacing a word containing `*`, `?`, or `[` with the filenames that match it, applied to unquoted expansions before the shell treats the result as arguments.
_Avoid_: glob expansion (use "globbing" or the full term)

**Word splitting**:
Breaking an unquoted expansion's result into separate words wherever a character in `$IFS` (space, tab, newline by default) appears.
_Avoid_: tokenizing (a different, unrelated meaning in other contexts)
