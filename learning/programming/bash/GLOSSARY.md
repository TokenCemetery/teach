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

**Background job**:
A command started with a trailing `&`, running without blocking the script that started it; its PID is available in `$!` immediately afterward.
_Avoid_: async task, thread (neither applies; a background job is a separate process, not a lighter-weight unit inside one)

**Command substitution**:
Running a command and replacing `$(command)` with what it wrote to standard output, trailing newlines stripped.
_Avoid_: backtick substitution (use for the older, non-nesting `` ` ` `` syntax specifically, not the concept)

**File descriptor**:
A number identifying an open input or output stream for a process; `0`, `1`, and `2` are standard input, output, and error, and a script may open others.
_Avoid_: file handle (a term from other languages; this workspace says "file descriptor", matching the shell's own numbering)

**Here-doc**:
A `<<DELIMITER ... DELIMITER` block that feeds its contents to a command's standard input inline, without a separate file.
_Avoid_: heredoc (one word; use the hyphenated form for consistency across lessons)

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

**Process substitution**:
A bash-only `<(command)` or `>(command)` form that lets a command's output or input be treated as a readable or writable file, without a pipe or a temporary file.
_Avoid_: process piping (this is not a pipe; the whole point is that it avoids a pipeline's subshell)

**Signal**:
An asynchronous notification sent to a process (`SIGTERM`, `SIGINT`, `SIGKILL`, and others), caught with `trap` unless it's `SIGKILL`, which cannot be handled at all.
_Avoid_: interrupt (reserve for `SIGINT` specifically, which is what `Ctrl-C` sends; "signal" is the general term)

**Subshell**:
A copy of the current shell's environment, forked to run a command or block; an assignment or a `cd` made inside it never affects the shell that forked it.
_Avoid_: child process (true but imprecise here; "subshell" specifically names a forked copy of the shell itself, not any child process)

**Symlink attack**:
Pre-creating a symlink at a predictable path a script is about to write to, so the script's write follows the link to a file the attacker chose instead.
_Avoid_: TOCTOU race (a broader, more general term for the same shape of bug; say "symlink attack" for this specific instance of it)

**Word splitting**:
Breaking an unquoted expansion's result into separate words wherever a character in `$IFS` (space, tab, newline by default) appears.
_Avoid_: tokenizing (a different, unrelated meaning in other contexts)
