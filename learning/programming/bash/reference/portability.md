---
title: Portability
description: "What POSIX sh actually guarantees, which common bash features aren't part of it, and when the difference is worth paying for"
type: reference
---

# Portability: POSIX `sh` vs Bash-Only

Stage 4 compressed for lookup. [Lesson 5](../lessons/0005-portability.md) covers what POSIX `sh` guarantees, which bash features fall outside it, and when the trade-off is actually worth making. This sheet is the feature table and the decision rule.

## POSIX `sh` is a specification, not a program

Any shell implementing it (dash, bash's `sh` mode, ksh, others) supports the same core feature set. This matters concretely because `/bin/sh` is not bash on many systems (dash, on many Debian-derived distributions). A script that assumes bash but is invoked via `#!/bin/sh` on such a system gets no warning; it silently runs under a different shell.

## Bash-only features with no POSIX `sh` equivalent

| Bash feature | POSIX `sh` fallback |
|---|---|
| Arrays (`arr=(a b c)`, `${arr[@]}`) | A space-separated string (with lesson 4's word-splitting care), or positional parameters |
| `[[ ... ]]` (extended test, `==` pattern matching, `&&`/`||` without chaining) | `[ ... ]` (or `test`), chained with `[ ... ] && [ ... ]` |
| `${var,,}` (lowercase), `${var/pattern/replacement}` | `tr` or `sed` for the same job |

## The discipline is declaring the dependency, not avoiding bash

| Shebang | Uses a bash-only feature | Honest? |
|---|---|---|
| `#!/bin/bash` | Yes | Yes, accurately declares bash is required |
| `#!/bin/sh` | No | Yes |
| `#!/bin/sh` | Yes | No, the shebang and the actual requirement don't match, and it breaks silently wherever `/bin/sh` isn't bash |

The mission's constraint is defaulting to POSIX `sh` portability and being explicit whenever a bash-only feature is deliberately used, not avoiding bash entirely.

## When portability is worth its cost

| Situation | Worth it? |
|---|---|
| Deployment target is uncertain or heterogeneous (an install script for multiple distributions, a build tool invoked by users with unknown default shells) | Yes |
| `/bin/sh` is the shebang for a specific, required reason | Yes |
| An internal CI script that only ever runs in a controlled environment where bash is guaranteed | No, forcing POSIX `sh` here trades away real clarity (arrays, `[[ ]]`, concise string operations) for a guarantee nothing actually needs |

POSIX `sh`'s more limited feature set often means more verbose or more careful code for the same task, so the trade-off is deliberate, not a default applied everywhere regardless of what a script actually needs.

## Before trusting a script's shebang

- [ ] A `#!/bin/sh` script contains no arrays, `[[ ]]`, or bash-only parameter expansions.
- [ ] A script using a bash-only feature declares it with `#!/bin/bash`, not `#!/bin/sh`.
- [ ] Portability was chosen deliberately (an uncertain deployment target, a required `/bin/sh` shebang), not applied by default to a script that will only ever run under bash.

## Sources

- [Docs: "Shell Command Language", POSIX.1-2017, The Open Group](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html)
- [Site: "Shell Style Guide", Google](https://google.github.io/styleguide/shellguide.html)
- [Resources](../RESOURCES.md)
