---
title: Exit Status and Error Handling
description: "$?, the unofficial strict mode (set -euo pipefail), what each flag actually changes and its real gaps, and trap for guaranteed cleanup"
type: reference
---

# Exit Status and Error Handling

Stage 2 compressed for lookup. [Lesson 2](../lessons/0002-exit-status.md) covers `$?` and why bash keeps going after a failure by default; [lesson 3](../lessons/0003-strict-mode-and-trap.md) covers the standard defensive setup that closes those gaps, plus `trap`. This sheet is the flags, their exceptions, and what still isn't covered.

## `$?`: what it holds, and where it slips

Every command sets an exit status: `0` for success, any nonzero value (1-255) for failure, by POSIX convention. `$?` holds only the *most recently run* command's status, overwritten by whatever runs next, including something as innocuous-looking as `echo`.

| Habit | What goes wrong |
|---|---|
| `mkdir /some/dir` then checking `$?` two lines later | Whatever ran in between overwrote `$?`; the check now reflects that command, not `mkdir` |
| `cmd1 \| cmd2`, then checking `$?` | Default pipeline status is only `cmd2`'s; a failing `cmd1` feeding a trivially-succeeding `cmd2` (like `wc -l` counting zero lines) is invisible |

Fix: check or capture immediately (`command; status=$?`), or branch directly (`if command; then ... else ... fi`, or `command || handle_failure`).

## `set -euo pipefail`: the unofficial strict mode

| Flag | Changes | Real exception |
|---|---|---|
| `set -e` (`errexit`) | Exits immediately on any command's nonzero status, instead of continuing | Not fatal inside an `if`/`while` condition, negated with `!`, or on the left of `&&`/`||`, since those contexts are already checking the status themselves |
| `set -u` (`nounset`) | Referencing an unset variable is an error, instead of silently substituting an empty string | None; this is the one flag without a documented exception |
| `set -o pipefail` | A pipeline's exit status becomes the rightmost nonzero status among all stages, instead of always the last one | None on its own, but a deliberately ignored stage (`grep pattern file \|\| true`) still lets the pipeline continue by design |

**Why `set -u` matters concretely.** `rm -rf "$dir/"` with `$dir` unset (a typo, a variable that was supposed to be set earlier) silently becomes `rm -rf /` without `set -u`; with it, referencing the unset variable is an immediate, loud error before the dangerous command runs.

## What strict mode still doesn't cover

- A command whose failure is deliberately ignored (`|| true`) is still allowed to continue, by design, not a gap to patch.
- `set -e`'s own exemptions (`if`/`&&`/`||`) mean a habit of testing commands can accidentally suppress `errexit`'s protection if the exemption isn't understood.
- Nothing about `set -euo pipefail` cleans anything up on the way out. Stopping is not the same as cleaning up.

## `trap`: guaranteed cleanup, for any exit reason

```text
trap 'cleanup_function' EXIT
```

Runs `cleanup_function` whenever the script exits, for any reason: success, a `set -e`-triggered failure, or a signal like `Ctrl-C` (`SIGINT`). This is the layer strict mode doesn't address at all, and it's how a script reliably removes a temp file or releases a lock even when it exits somewhere unexpected partway through.

## Before trusting a script's error handling

- [ ] A command's exit status is checked or captured immediately after it runs, not after any intervening command, however innocuous-looking.
- [ ] A pipeline's status is understood as either "last stage only" (default) or "rightmost nonzero" (`pipefail`), not assumed to reflect every stage without checking which mode is active.
- [ ] The script starts with `set -euo pipefail` (or an explicit, commented reason it doesn't), and every deliberately-ignored failure (`|| true`) is intentional, not accidental.
- [ ] Any resource that must be cleaned up (a temp file, a lock) is released via `trap ... EXIT`, not by a cleanup step that only runs on the script's normal, successful path.

## Sources

- [Docs: "Shell Command Language", POSIX.1-2017, The Open Group](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html)
- [Article: "Use the Unofficial Bash Strict Mode (Unless You Looove Debugging)", Aaron Maxwell](http://redsymbol.net/articles/unofficial-bash-strict-mode/)
- [Site: "Bash Pitfalls", Greg's Wiki](https://mywiki.wooledge.org/BashPitfalls)
- [Resources](../RESOURCES.md)
