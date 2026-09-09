---
title: "awk, sed, and Knowing When to Stop"
description: "Matching sed and awk to the shape of task each fits, reaching for them only where genuinely needed, and the concrete signals a script has outgrown shell entirely"
type: reference
---

# `awk`, `sed`, and Knowing When to Stop

Stages 5 and 6 compressed for lookup. [Lesson 6](../lessons/0006-awk-and-sed-where-needed.md) covers matching `sed`/`awk` to the shape of a task and reaching for them only when genuinely needed; [lesson 7](../lessons/0007-knowing-when-to-stop.md) covers the concrete signals that a script has outgrown shell entirely. This sheet is the tool-selection table and the stop signals.

## Matching the tool to the task's shape

| Tool | Fits | Doesn't fit |
|---|---|---|
| `sed` | Line-based, pattern-driven find-and-transform: substitution (`s/pattern/replacement/`), deleting matching lines, editing a file in place (`-i`) | Field extraction, arithmetic, anything needing a line split into columns |
| `awk` | Field-oriented processing: pattern-action per line, fields (`$1`, `$2`, ...) on a delimiter, arithmetic, associative arrays | A one-line substitution with no field structure involved, where `sed`'s simplicity fits better |
| Bash's own string operations (`${var/pattern/replacement}`, `case`) | A single variable's value, not a stream of lines | A stream of lines or a file, where spawning bash logic per line is far more expensive than one `sed`/`awk` pass |

Reaching for `sed` to do column extraction, or `awk` for a bare substitution, usually signals the wrong tool for the task's actual shape, not a stylistic choice.

## The discipline: invoked from bash, not replacing it

`awk`/`sed` are touched only where a script genuinely needs text-processing capability that neither bash's own string operations nor a simple loop provide efficiently, not as a default habit for every line of output. Bash remains the right tool for control flow (loops, conditionals, gluing other programs' output together); `sed`/`awk` are invoked for a specific line-editing or field-extraction step, then control returns to bash. A script built entirely from nested `awk` scripts glued together is usually a sign the task has outgrown shell (below), not a sign `awk` was the right choice throughout.

## The concrete signals that a script has outgrown shell

Google's Shell Style Guide names a specific rule: if a script written from scratch would exceed 100 lines, or its logic becomes non-trivial, write it in a more structured language instead, from the start.

| Signal | Why shell can't absorb it cleanly |
|---|---|
| A data structure beyond a flat list (a dictionary, a nested structure, a record with named fields) | Shell has no native way to represent it; even bash's arrays (lesson 5) are flat, so working around this means encoding structure into strings and parsing it back out |
| Error handling beyond "check the exit status and branch" (retry with backoff, structured error types, aggregating multiple failures) | Shell's error handling (lessons 2-3) is exit-status checking; nothing native supports richer error structure |
| Structured data (JSON, a real config format) beyond a `sed`/`awk` one-liner | Every additional feature request makes the shell version more fragile, not more capable |
| The script's own length or branching complexity makes it genuinely hard to reason about (the "100 lines and growing" signal) | Directly named by Google's Shell Style Guide as its own stop condition |

Any one signal alone is worth pausing on; several together is a clear stop sign.

## Where the job goes, and why the switch isn't a failure

`programming/python` is where real data structures, structured error handling, and complex control flow exist natively rather than as shell workarounds. Recognizing a script has crossed this ceiling and switching languages is the same kind of judgment call as choosing `sed` versus `awk` versus bash's own string handling: matching the tool to the problem's actual current shape, not an admission the original shell script was a mistake. A script's requirements can change shape as it grows; continuing to force a grown script into shell past that point produces the same fragility a production-breaking quoting or exit-status bug does, from a different cause.

## Before reaching for a text-processing tool, or deciding to stop

- [ ] The task's shape (line substitution, field extraction, or a single value) determines the tool, not habit or whichever tool was used last.
- [ ] `sed`/`awk` are called from bash for a specific step, not used to replace bash's own control flow throughout a script.
- [ ] A growing script is checked against all four signals (data structures, error-handling complexity, structured-data manipulation, length/branching) before adding another workaround to keep it in shell.
- [ ] A script past shell's ceiling is rewritten as a deliberate tool match, not patched further to avoid a rewrite.

## Sources

- [Docs: "A Sed and Awk Micro-Primer", Advanced Bash-Scripting Guide, TLDP](https://tldp.org/LDP/abs/html/sedawk.html)
- [Site: "Shell Style Guide", Google](https://google.github.io/styleguide/shellguide.html)
- [Resources](../RESOURCES.md)
