---
title: 5. Portability
description: What POSIX sh actually guarantees, which common bash features aren't part of it, and when the difference actually matters
type: lesson
---

# Lesson 5. Portability

**Mission link:** This is stage 4, a single-lesson stage. Lessons 1-4 assumed bash; this lesson is the deliberate constraint the mission itself is written under (POSIX `sh` portability, bash idioms called out explicitly), and when that constraint is actually worth paying for.
**Primary source:** [Docs: "Shell Command Language", POSIX.1-2017, The Open Group](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html)
**Prerequisites:** [Lesson 4](0004-word-splitting-and-globbing-pitfalls.md), [Word splitting](../GLOSSARY.md)

## Warm-up

1. ▢ Why is `for f in $(ls *.txt)` broken regardless of quoting inside the loop body?

<details markdown="1"><summary>Check</summary>

`$(ls *.txt)` is itself an unquoted command substitution, so its entire output undergoes word splitting on `$IFS` regardless of what filenames it contains, breaking on any filename with a space, independent of anything inside the loop body.

</details>

2. ▢ What does `shopt -s nullglob` change about an unmatched glob pattern?

<details markdown="1"><summary>Check</summary>

Without it, an unmatched glob (like `*.txt` with no matching files) is passed through as the literal pattern string; with `nullglob` enabled, it expands to nothing instead, so a `for` loop over it simply doesn't run.

</details>

## Know this

### POSIX `sh` is a guarantee about which shell you're actually targeting

**POSIX `sh`** is a specification, not a specific program: any shell that implements it (dash, the `sh` mode of bash, ksh, and others) is required to support the same core feature set. Writing a script against POSIX `sh` means it will behave the same way regardless of which POSIX-compliant shell actually runs it, which matters concretely on systems where `/bin/sh` is *not* bash (many Debian-derived systems symlink `/bin/sh` to dash specifically, a materially smaller, faster shell that does not support bash-only syntax at all). A script that assumes bash but is invoked via `#!/bin/sh` on such a system doesn't get a warning; it silently runs under a different shell and can fail or behave differently.

### Concrete bash-only features that don't exist in POSIX `sh`

Arrays (`arr=(a b c)`, `${arr[@]}`) are a bash extension with no POSIX `sh` equivalent at all; POSIX `sh` scripts needing an ordered list of values typically fall back to a space-separated string (with the word-splitting care lesson 4 covers) or positional parameters. `[[ ... ]]` (bash's extended test construct, supporting `==` pattern matching and `&&`/`||` without the classic `[ ... ] && [ ... ]` chaining) is also bash-only; POSIX `sh` requires the single-bracket `[ ... ]` (or `test`) form. String manipulation shortcuts like `${var,,}` (lowercase) or `${var/pattern/replacement}` are bash-specific too, without a direct POSIX `sh` equivalent (POSIX scripts typically reach for `tr` or `sed` for the same job).

### Calling out a bash-only feature explicitly is the actual discipline, not avoiding bash entirely

The mission's constraint isn't "never use bash"; it's writing for POSIX `sh` portability by default and being explicit whenever a bash-only feature is deliberately used, so a reader (or a script's own shebang) can immediately tell whether it needs bash specifically or will run under any POSIX shell. A `#!/bin/bash` shebang alongside a bash array is honest about the dependency; a `#!/bin/sh` shebang followed by bash-only syntax is a script that lies about its own requirements and breaks silently and confusingly on a system where `/bin/sh` isn't bash.

### When portability is actually worth the cost, and when it isn't

Portability has a real cost: POSIX `sh`'s more limited feature set often means more verbose or more careful code for the same task (string manipulation via `sed`/`tr` instead of a one-line bash parameter expansion). This is worth paying specifically when a script's actual deployment target is uncertain or heterogeneous (a package's install script that could run on many different Linux distributions or Unix variants, a build tool invoked by users with unknown default shells) or when `/bin/sh` is the shebang for a good reason (some system-level scripts are invoked via `/bin/sh` specifically, and can't assume bash regardless of what's actually installed). It's not worth paying for an internal CI script that only ever runs in a controlled, known environment where bash is guaranteed present; forcing POSIX `sh` there trades real clarity (bash's arrays, `[[ ]]`, and string operations) for a portability guarantee nothing actually needs.

## Practice

1. ▢ Why can a script that assumes bash but uses `#!/bin/sh` fail silently on some systems, rather than failing loudly and immediately?

<details markdown="1"><summary>Hint</summary>

Consider what `/bin/sh` actually points to on a system where it isn't bash.

</details>

<details markdown="1"><summary>Check</summary>

On systems where `/bin/sh` is a different POSIX-compliant shell (dash on many Debian-derived systems, for instance), the script actually runs under that shell instead of bash, with no warning that a mismatch occurred. Bash-only syntax then either produces a confusing parse error or, worse, behaves subtly differently rather than failing to even start.

</details>

2. ▢ Name two bash-only features with no direct POSIX `sh` equivalent, and what a POSIX `sh` script typically does instead.

<details markdown="1"><summary>Check</summary>

Arrays (`arr=(a b c)`) have no POSIX equivalent; POSIX scripts fall back to a space-separated string or positional parameters. `[[ ... ]]` (extended test) has no POSIX equivalent; POSIX scripts use `[ ... ]` (or `test`). String manipulation shortcuts like `${var,,}` or `${var/pattern/replacement}` also have no POSIX equivalent; POSIX scripts typically use `tr` or `sed` for the same job.

</details>

3. ▢ Why is a `#!/bin/bash` shebang alongside bash array syntax considered honest, while a `#!/bin/sh` shebang alongside the same syntax is not?

<details markdown="1"><summary>Check</summary>

The `#!/bin/bash` shebang accurately declares that the script needs bash specifically, so whoever runs it knows exactly what's required. `#!/bin/sh` declares the script is meant to run under any POSIX-compliant shell, which bash array syntax contradicts; the script's stated requirement and its actual requirement don't match, so it can silently fail on any system where `/bin/sh` isn't bash.

</details>

4. ▢ A team writes an internal CI script that only ever runs in a controlled environment where bash is guaranteed installed. Should it be written for POSIX `sh` portability? Why or why not?

<details markdown="1"><summary>Check</summary>

Not necessarily: portability is worth its cost specifically when the deployment target is uncertain or heterogeneous, or when `/bin/sh` is required for a specific reason. In a controlled environment where bash is guaranteed, forcing POSIX `sh` trades away real clarity (bash's arrays, `[[ ]]`, concise string operations) for a guarantee the script doesn't actually need, since it will only ever run under bash anyway.

</details>

5. ▢ Which claim correctly describes the portability discipline this lesson covers?

    - a) A script should never use any bash-only feature under any circumstances
    - b) POSIX `sh` is a specification multiple shells implement identically; the discipline is defaulting to portable syntax and explicitly declaring (via shebang and awareness) whenever a bash-only feature is deliberately used, reserving that trade-off for when the deployment target actually needs it
    - c) `/bin/sh` is always bash, so there's no practical difference between targeting `/bin/sh` and targeting bash directly
    - d) Portability is always worth its cost, regardless of how certain or controlled a script's deployment environment is

<details markdown="1"><summary>Check</summary>

**b)** That's the precise, conditional discipline this lesson describes. (a) is false: the mission's constraint is portability by default with bash features used and declared deliberately, not a ban on bash. (c) is false and is exactly the mismatch this lesson warns about, since `/bin/sh` is dash (or another shell) on many real systems. (d) is false: a controlled, bash-guaranteed environment gets no benefit from forcing POSIX `sh` and loses real clarity by doing so.

</details>

## Real-world reps

- [ ] Find a shell script you have access to with a `#!/bin/sh` shebang. Check whether it actually uses any bash-only syntax (arrays, `[[ ]]`, `${var,,}`-style expansions), which would make its shebang inaccurate.
- [ ] For that same script, check `/bin/sh` on the system it's meant to run on (or a similar one) to see what shell it actually resolves to, and whether that matches the script's assumptions.
- [ ] Tomorrow: read the primary source's introduction in full, and note one feature it specifies that surprised you, either because it's more limited than bash or because it's supported more broadly than expected.

## Going further

- [Docs: "Shell Command Language", POSIX.1-2017, The Open Group](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html)
- [Site: "Shell Style Guide", Google](https://google.github.io/styleguide/shellguide.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
