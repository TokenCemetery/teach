---
title: 6. awk and sed Where Needed
description: Recognizing the shape of task sed and awk each fit, and reaching for one only when a script genuinely needs it, not as a habit
type: lesson
---

# Lesson 6. awk and sed Where Needed

**Mission link:** This is stage 5, a single-lesson stage. Every prior stage stayed inside bash's own built-in capabilities; this lesson is the one place the mission deliberately reaches outside them, and the discipline of doing so only when the task actually calls for it.
**Primary source:** [Docs: "A Sed and Awk Micro-Primer", Advanced Bash-Scripting Guide, TLDP](https://tldp.org/LDP/abs/html/sedawk.html)
**Prerequisites:** [Lesson 5](0005-portability.md), [Word splitting](../GLOSSARY.md)

## Warm-up

1. ▢ Why can a script that assumes bash but uses `#!/bin/sh` fail silently on some systems?

<details markdown="1"><summary>Check</summary>

On systems where `/bin/sh` is a different POSIX-compliant shell (dash, for instance), the script runs under that shell instead of bash with no warning, and bash-only syntax either produces a confusing error or behaves subtly differently rather than failing to start at all.

</details>

2. ▢ Name two bash-only features with no direct POSIX `sh` equivalent.

<details markdown="1"><summary>Check</summary>

Arrays (`arr=(a b c)`) and `[[ ... ]]` (extended test) are both bash-only; POSIX scripts fall back to space-separated strings or positional parameters, and `[ ... ]` (or `test`), respectively.

</details>

## Know this

### sed's shape: a stream editor for line-based, find-and-transform tasks

`sed` (stream editor) reads input line by line and applies simple, pattern-based edits: substitution (`s/pattern/replacement/`), deletion of matching lines, or operating on a specific line range. It fits precisely the shape of "find this pattern in each line and change it" or "keep only lines matching (or not matching) this pattern," and its `-i` flag can edit a file in place, which is why it shows up constantly in shell scripts doing lightweight text substitution (rewriting a config value, stripping comments, normalizing line endings) without needing a full programming construct for the job.

### awk's shape: field-oriented processing, not just text substitution

`awk` is a small, complete programming language built around a pattern-action model: for each input line, it checks a pattern (often a regex, but can be any condition) and, if it matches, runs an action, with built-in support for splitting a line into fields (`$1`, `$2`, ...) on a delimiter, arithmetic, and associative arrays. This fits a materially different shape of task than `sed`: extracting or computing something from structured, delimited data (summing a column of numbers, printing the third field of every matching line, counting occurrences), not just transforming text in place. Reaching for `sed` to do column-based extraction, or `awk` for a one-line substitution, usually signals the wrong tool for the shape of the actual task.

### The discipline: called from bash, not replacing bash's own logic

The mission's constraint is specific: `awk`/`sed` are touched only where a script genuinely needs the text-processing capability neither bash's own string operations nor a simple loop provide efficiently, not used as the default way to process every line of output. Bash itself remains the right tool for control flow (loops, conditionals, calling other programs and gluing their output together); `sed`/`awk` are invoked *from* a bash script for the specific line-editing or field-extraction step, then control returns to bash. A script that does everything through nested `awk` scripts glued together with bash is usually a sign the actual task has outgrown shell in the direction lesson 7 covers, not a sign `awk` was the right choice throughout.

### Recognizing when neither is actually the right call

Some tasks that look like "reach for sed/awk" are better served by bash's own built-in parameter expansion (`${var/pattern/replacement}`, bash-only per lesson 5, or `case` pattern matching) when the data is a single variable rather than a stream of lines, avoiding the overhead and subprocess cost of invoking an external tool for something bash can already do internally. The judgment call this lesson asks for isn't "always prefer sed/awk over bash string handling" or the reverse; it's matching the actual shape of the task (a single value versus a stream of lines or records) to the tool actually built for that shape.

## Practice

1. ▢ A script needs to replace every occurrence of `old-value` with `new-value` in a config file. Which tool fits, and why?

<details markdown="1"><summary>Check</summary>

`sed`, using `s/old-value/new-value/g` with the `-i` flag to edit in place. This is exactly `sed`'s shape: a simple, pattern-based substitution applied line by line across a file, not requiring field extraction or arithmetic.

</details>

2. ▢ A script needs to sum the values in the third column of a CSV file. Which tool fits, and why would the other one be an awkward choice?

<details markdown="1"><summary>Hint</summary>

Consider what "the third column" requires the tool to understand about the line's structure.

</details>

<details markdown="1"><summary>Check</summary>

`awk` fits, since it splits each line into fields on a delimiter and supports arithmetic natively (`awk -F, '{sum += $3} END {print sum}'`). `sed` has no native concept of fields or arithmetic; it operates on whole lines or pattern matches within them, so summing a specific column is not the shape of task it's built for.

</details>

3. ▢ Why does the mission's constraint describe `awk`/`sed` as touched "only where a script genuinely needs" them, rather than treating them as a default text-processing habit?

<details markdown="1"><summary>Check</summary>

Bash itself remains the right tool for control flow and gluing commands together; reaching for `awk`/`sed` by default, even for tasks bash's own string operations or a simple loop handle fine, adds unnecessary complexity and subprocess overhead. They're meant to be invoked for the specific capability neither bash nor a simple loop provides efficiently, not as a substitute for bash's own logic throughout a script.

</details>

4. ▢ A script needs to replace a substring in a single variable's value, not a file or stream of lines. Why might bash's own `${var/pattern/replacement}` be the better fit than piping the value through `sed`?

<details markdown="1"><summary>Check</summary>

The data here is a single value, not a stream of lines, so bash's own built-in parameter expansion handles the substitution directly, without the overhead of spawning an external `sed` process for a job bash can already do internally. This matters specifically because the data's shape (one value, not a stream) doesn't call for `sed`'s line-oriented capability at all.

</details>

5. ▢ Which claim correctly describes choosing between `sed`, `awk`, and bash's own capabilities?

   - a) `awk` should always be preferred over `sed`, since it's a more complete language
   - b) Match the tool to the actual shape of the task: `sed` for line-based pattern substitution, `awk` for field-oriented extraction or computation, and bash's own string handling for a single value that doesn't need stream processing at all
   - c) `sed` and `awk` should replace bash's control flow (loops, conditionals) wherever possible for consistency
   - d) Using `sed` or `awk` at all indicates a script has outgrown shell and should be rewritten in Python

<details markdown="1"><summary>Check</summary>

**b)** That's the precise judgment call this lesson asks for, matching tool to task shape. (a) is false: `sed`'s simplicity is the right fit for pure substitution tasks; `awk`'s extra power isn't free. (c) is false: bash remains the right tool for control flow and orchestration; `sed`/`awk` are invoked for specific text-processing steps, not to replace bash's own logic. (d) is false: using `sed`/`awk` appropriately, for the shape of task they fit, is exactly what "shell that survives production" looks like; lesson 7 covers a different, more structural signal for outgrowing shell.

</details>

## Real-world reps

- [ ] Find a shell script you have access to that uses `sed` or `awk`. Check whether the tool used actually matches the task's shape (line substitution for `sed`, field extraction or computation for `awk`), or whether the other tool (or bash's own string handling) would have been a better fit.
- [ ] Find a place in that same script (or one you know of) where bash's own string operations or a loop handle something that's instead being piped through `sed` or `awk` unnecessarily, and consider what removing that dependency would look like.
- [ ] Tomorrow: read the primary source's brief introduction to both tools in full, and write one sentence distinguishing the shape of task each was actually designed for.

## Going further

- [Docs: "A Sed and Awk Micro-Primer", Advanced Bash-Scripting Guide, TLDP](https://tldp.org/LDP/abs/html/sedawk.html)
- [Site: "Bash Pitfalls", Greg's Wiki](https://mywiki.wooledge.org/BashPitfalls)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
