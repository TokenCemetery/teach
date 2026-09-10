---
title: Bash
description: "Write shell that survives production: quoting, exit status, the failure modes, and knowing when to stop and use a real language"
type: topic
---

# Learning: Bash

Be able to write and maintain shell scripts for CI pipelines, deployment and operational tooling that do not quietly break on a bad input or an unset variable, and to recognise when a script has outgrown shell and belongs in a real language instead.

**Latest lesson:** [17. shellcheck, shfmt, and Testing a Script](lessons/0017-shellcheck-shfmt-and-testing-a-script.md)

## Success looks like

- Write a CI/deployment script or an operational utility that handles quoting, exit status and common failure modes correctly, and explain why each choice was necessary.
- Given a shell script, name the specific way it would break on an edge case (unquoted expansion, unset variable, a command's exit status ignored).
- Recognise when a script has outgrown shell's judgment-free zone and say why the job now belongs in `programming/python` instead.

## Constraints

- Assumes no prior shell scripting experience.
- Written for POSIX `sh` portability rather than bash-only idioms, even though bash is the topic's home; a bash-only feature is called out as such when used.
- Touches `awk`/`sed` only where a script genuinely needs them, not as topics of their own.

## Out of scope

- Everything past the point a script should have stopped being shell: `programming/python` is where it goes next.

## The arc

Eleven stages, quoting to shellcheck, shfmt and testing. A stage takes several lessons and the boundaries are soft; what makes a stage done is the capability, not the lesson count.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. Quoting | 0001 | The single habit that prevents the most common way shell scripts break in production | Can quote correctly and explain why an unquoted expansion breaks |
| 2. Exit status and error handling | 0002 to 0003 | `$?`, the unofficial strict mode (`set -euo pipefail`), `trap` | Can write a script that handles exit status and failure correctly |
| 3. Word splitting and globbing pitfalls | 0004 | The Bash Pitfalls list, the common footguns beyond quoting | Given a script, can name the specific edge case it would break on |
| 4. Portability | 0005 | POSIX `sh` versus bash-only idioms, when each matters | Can write portable `sh` and call out a bash-only feature explicitly |
| 5. `awk`/`sed` where needed | 0006 | Using each only where a script genuinely needs it | Can reach for `awk`/`sed` for a real need without over-using them |
| 6. Knowing when to stop | 0007 | Recognising shell has outgrown its judgment-free zone | Can say why a given job now belongs in `programming/python` |
| 7. Shell fundamentals | 0008 to 0009 | Variables, command substitution, control flow (`if`/`case`/loops), functions, `local`, return status vs output | Can write a script using variables, command substitution and control flow, and organise repeated work into correctly-scoped functions |
| 8. Parameter expansion and arrays | 0010 to 0011 | Defaulting/erroring on unset (`${v:-}`, `${v:?}`), stripping (`${v%%}`), substitution, indexed and associative arrays | Can default, validate and transform a value inline, and hold a list or a map without encoding it into a string |
| 9. Redirection and composition | 0012 to 0013 | Redirection order, file descriptors, here-docs, why a piped `while` loop loses its variables, process substitution | Can redirect streams correctly and explain why a variable set inside a piped loop doesn't survive it |
| 10. Arguments and job control | 0014 to 0015 | `getopts`, a usage/help convention, signals, background jobs, `wait` | Can parse a script's own flags and arguments, and manage background work and its own shutdown correctly |
| 11. Safety and tooling | 0016 to 0017 | `mktemp`, the `eval`/injection surface, ShellCheck, `shfmt`, testing with bats/shunit2 | Can create temp files and dynamic commands safely, and use static analysis and tests to catch what review alone would miss |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-quoting.md) | Quoting | The single habit that prevents the most common way shell scripts break in production |
| [0002](lessons/0002-exit-status.md) | Exit Status | What $? actually reports, why bash keeps running after a failed command by default, and the second most common way a script breaks in production |
| [0003](lessons/0003-strict-mode-and-trap.md) | Strict Mode and trap | What each flag in set -euo pipefail actually changes, its real gaps, and using trap to clean up reliably when a script fails |
| [0004](lessons/0004-word-splitting-and-globbing-pitfalls.md) | Word Splitting and Globbing Pitfalls | Common footguns beyond a bare missing quote, where quoting alone isn't the whole fix |
| [0005](lessons/0005-portability.md) | Portability | What POSIX sh actually guarantees, which common bash features aren't part of it, and when the difference actually matters |
| [0006](lessons/0006-awk-and-sed-where-needed.md) | awk and sed Where Needed | Recognizing the shape of task sed and awk each fit, and reaching for one only when a script genuinely needs it, not as a habit |
| [0007](lessons/0007-knowing-when-to-stop.md) | Knowing When to Stop | The concrete signals that a script has outgrown shell's judgment-free zone, and why the job now belongs in a real language instead |
| [0008](lessons/0008-variables-command-substitution-and-control-flow.md) | Variables, Command Substitution, and Control Flow | The shell's own vocabulary for holding a value, capturing a command's output, and branching or looping over it |
| [0009](lessons/0009-functions-local-and-return-status-vs-output.md) | Functions, local, and Return Status vs Output | Organizing repeated work into a function, and the sharpest thing a shell function does differently from a function in almost every other language |
| [0010](lessons/0010-parameter-expansion.md) | Parameter Expansion | Defaulting, erroring, and stripping a value inline, without reaching for a separate command |
| [0011](lessons/0011-arrays.md) | Arrays (Indexed and Associative) | Holding more than one value without encoding structure into a string, and the one quoting form that keeps each element intact |
| [0012](lessons/0012-redirection-file-descriptors-and-here-docs.md) | Redirection, File Descriptors, and Here-Docs | Sending a command's output somewhere other than the screen, precisely, and feeding it a block of input inline |
| [0013](lessons/0013-pipes-subshells-and-process-substitution.md) | Pipes, Subshells, and Process Substitution | Why a variable set inside a piped loop vanishes the moment the pipe ends, and the bash-only fix that keeps it |
| [0014](lessons/0014-argument-parsing-with-getopts.md) | Argument Parsing with getopts and a Usage Convention | Parsing a script's own flags and arguments the same disciplined way it's supposed to parse everything else |
| [0015](lessons/0015-signals-background-jobs-and-wait.md) | Signals, Background Jobs, and wait | Running work concurrently inside one script, and making sure a script's own shutdown doesn't orphan it |
| [0016](lessons/0016-mktemp-safe-temp-files-and-the-eval-injection-surface.md) | mktemp, Safe Temp Files, and the eval/Injection Surface | Creating a temporary file that can't be predicted or hijacked, and why eval turns untrusted input into arbitrary code |
| [0017](lessons/0017-shellcheck-shfmt-and-testing-a-script.md) | shellcheck, shfmt, and Testing a Script | The tool that catches most of a script's quiet breakages before it ever runs, and how to test the rest |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources
- [Quoting and Pitfalls](reference/quoting-and-pitfalls.md): the quoting rule, where it bites, and the Bash Pitfalls that survive careful quoting
- [Exit Status and Error Handling](reference/exit-status-and-error-handling.md): `$?`, `set -euo pipefail`'s flags and real exceptions, and `trap` for guaranteed cleanup
- [Portability](reference/portability.md): POSIX `sh` vs bash-only features, the shebang-honesty rule, and when the trade-off is worth it
- [awk, sed, and Knowing When to Stop](reference/awk-sed-and-when-to-stop.md): matching the tool to the task's shape, and the concrete signals a script has outgrown shell

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
