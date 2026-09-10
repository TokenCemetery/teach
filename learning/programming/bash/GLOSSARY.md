---
title: Glossary
description: "Canonical terms for Bash"
type: glossary
---

# Bash Glossary

Canonical terms for shell that survives production: what an unquoted expansion actually does, and the failure modes that follow from it.

## Terms

**Command substitution**:
Running a command and replacing `$(command)` with what it wrote to standard output, trailing newlines stripped.
_Avoid_: backtick substitution (use for the older, non-nesting `` ` ` `` syntax specifically, not the concept)

**Local variable**:
A variable declared with `local` inside a function, scoped to that function call rather than persisting in the calling shell's environment.
_Avoid_: function-scoped variable (say "local variable", matching the keyword)

**Pathname expansion (globbing)**:
Replacing a word containing `*`, `?`, or `[` with the filenames that match it, applied to unquoted expansions before the shell treats the result as arguments.
_Avoid_: glob expansion (use "globbing" or the full term)

**Word splitting**:
Breaking an unquoted expansion's result into separate words wherever a character in `$IFS` (space, tab, newline by default) appears.
_Avoid_: tokenizing (a different, unrelated meaning in other contexts)
