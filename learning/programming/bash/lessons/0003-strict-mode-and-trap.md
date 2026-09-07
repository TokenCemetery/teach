---
title: 3. Strict Mode and trap
description: What each flag in set -euo pipefail actually changes, its real gaps, and using trap to clean up reliably when a script fails
type: lesson
---

# Lesson 3. Strict Mode and trap

**Mission link:** This is stage 2's capstone. Lesson 2 established that bash continues past a failed command by default and that a pipeline's exit status hides everything but its last stage; this lesson is the standard defensive setup that closes both gaps, plus `trap`, for what happens when a script needs to fail visibly and clean up after itself.
**Primary source:** [Article: "Use the Unofficial Bash Strict Mode (Unless You Looove Debugging)", Aaron Maxwell](http://redsymbol.net/articles/unofficial-bash-strict-mode/)
**Prerequisites:** [Lesson 2](0002-exit-status.md), [Word splitting](../GLOSSARY.md)

## Warm-up

1. ▢ What does bash do by default when a command in the middle of a script fails, and why is this the actual problem rather than a neutral default?

<details markdown="1"><summary>Check</summary>

By default, bash continues to the next command regardless of the previous one's exit status; nothing stops the script unless something explicitly checks and reacts to the failure. This often produces a confusing failure several steps later, or silent wrong behavior, instead of a clear failure at the point something actually went wrong.

</details>

2. ▢ Why does checking `$?` after a pipeline (`cmd1 | cmd2`) not necessarily tell you whether `cmd1` succeeded?

<details markdown="1"><summary>Check</summary>

By default, a pipeline's exit status is only the last command's (`cmd2`'s), regardless of whether earlier stages failed, so a failure in `cmd1` can be silently hidden behind a `cmd2` that "succeeds" trivially (like counting zero lines).

</details>

## Know this

### `set -e`: stop on the first unchecked failure

`set -e` (`errexit`) makes the script exit immediately if any command's exit status is nonzero, instead of continuing to the next line. This directly closes lesson 2's default-continues problem for the common case. It has real, well-documented exceptions worth knowing rather than assuming universal coverage: a command's failure is *not* fatal under `set -e` if it's part of an `if`/`while` condition, negated with `!`, or on the left side of `&&`/`||`, since those contexts are explicitly checking the status themselves, which is exactly the point.

### `set -u`: fail on an unset variable instead of silently using an empty string

`set -u` (`nounset`) makes referencing an unset variable an error instead of silently substituting an empty string. Without it, a typo (`$fiel` instead of `$file`) or a variable that was supposed to be set earlier but wasn't produces an empty string with no warning, which then flows into whatever command uses it, frequently with dangerous results (`rm -rf "$dir/"` when `$dir` is unset and unquoted becomes `rm -rf /`, a well-known catastrophic Bash Pitfall). `set -u` turns that silent substitution into an immediate, loud failure at the point of the typo.

### `set -o pipefail`: make a pipeline's status reflect any stage's failure

`set -o pipefail` changes a pipeline's exit status to be the *rightmost* nonzero status among all its stages (or zero if all succeeded), instead of always being just the last command's. This directly closes lesson 2's pipeline gap: `grep pattern file | sort` now reports a failure if `grep` itself failed (a missing file, for instance), not just if `sort` somehow failed. Combined, `set -euo pipefail` is what most people mean by bash's "strict mode," though the name is unofficial and the primary source is explicit that it's a convention, not a language feature with that name.

### What strict mode still doesn't catch, and where `trap` comes in

Strict mode is not a substitute for actually checking results that matter, and it has real limits: a command in a pipeline that fails but whose failure is deliberately ignored (`grep pattern file || true`) is still allowed to continue by design, and `set -e`'s exemptions (the `if`/`&&`/`||` cases above) mean a habit of testing commands can accidentally suppress `errexit`'s protection if not understood. `trap` complements strict mode for the layer it doesn't address at all: guaranteed cleanup. `trap 'cleanup_function' EXIT` runs `cleanup_function` whenever the script exits, for any reason, success, a `set -e` triggered failure, or a signal like `Ctrl-C` (`SIGINT`), which is how a script reliably removes a temp file or releases a lock even when it exits somewhere unexpected partway through.

## Practice

1. ▢ Why does `set -e` not treat a failing command inside an `if` condition as fatal, even though `set -e` is active?

<details markdown="1"><summary>Check</summary>

`set -e`'s exemption for `if`/`while` conditions (and `&&`/`||` and negation with `!`) exists because those contexts are explicitly testing the command's exit status themselves; treating that expected, checked failure as script-ending would defeat the purpose of writing a conditional at all.

</details>

2. ▢ A script does `rm -rf "$dir/"` where `$dir` was supposed to be set earlier but a typo left it unset. Without `set -u`, what happens, and how does `set -u` change the outcome?

<details markdown="1"><summary>Hint</summary>

Consider what an unset variable expands to by default, and what `"$dir/"` becomes once that substitution happens.

</details>

<details markdown="1"><summary>Check</summary>

Without `set -u`, an unset `$dir` silently expands to an empty string, so `"$dir/"` becomes just `/`, and the script runs `rm -rf /`, attempting to recursively delete the root filesystem. With `set -u`, referencing the unset `$dir` is itself an immediate error, stopping the script before the dangerous command ever runs.

</details>

3. ▢ Why does `set -o pipefail` matter for `grep pattern file | sort`, specifically?

<details markdown="1"><summary>Check</summary>

Without `pipefail`, this pipeline's exit status is only `sort`'s, which almost always succeeds regardless of what `grep` did. With `pipefail`, the pipeline's status becomes the rightmost nonzero status among all stages, so a `grep` failure (like the file not existing) is no longer silently hidden behind a trivially-succeeding `sort`.

</details>

4. ▢ Why isn't `set -euo pipefail` alone enough to guarantee a temp file gets cleaned up if the script fails partway through?

<details markdown="1"><summary>Check</summary>

Strict mode stops the script on an unchecked failure, but stopping isn't the same as cleaning up: nothing about `set -euo pipefail` removes a temp file or releases a lock on the way out. `trap 'cleanup_function' EXIT` is what guarantees cleanup runs regardless of how or why the script exits (success, a strict-mode-triggered failure, or a signal), which strict mode alone doesn't provide.

</details>

5. ▢ Which claim correctly describes `set -euo pipefail` and `trap`?

    - a) `set -e` makes every nonzero exit status fatal, with no exceptions, including inside `if` conditions
    - b) `set -e` stops on an unchecked failure, `set -u` catches unset-variable typos, `set -o pipefail` makes a pipeline's status reflect any stage's failure, and `trap` provides guaranteed cleanup that strict mode alone doesn't
    - c) `trap` is redundant once strict mode is enabled, since strict mode already handles cleanup
    - d) A command deliberately ignored with `|| true` will still stop the script under `set -e`

<details markdown="1"><summary>Check</summary>

**b)** That's the precise, complementary role each piece plays. (a) is false: `set -e` explicitly exempts commands in `if`/`while` conditions and similar checked contexts. (c) is false: strict mode stops execution on failure but does nothing about cleanup on the way out, which is exactly what `trap` adds. (d) is false: `|| true` deliberately converts the command's exit status to success, which is precisely what lets it continue past `set -e` by design.

</details>

## Real-world reps

- [ ] Find a shell script you have access to. Check whether it starts with `set -euo pipefail` (or an equivalent), and if it does, look for at least one place where a command's failure is deliberately allowed to continue (via `|| true` or similar) and confirm that's intentional.
- [ ] For the same script (or one you write for this rep), add a `trap '...' EXIT` that cleans up a temp resource, and confirm it runs both on a normal successful exit and after forcing an early failure.
- [ ] Tomorrow: read the primary source in full, including its discussion of `IFS` hardening alongside strict mode, and note why it's often recommended alongside `set -euo pipefail` rather than being one of its three flags.

## Going further

- [Article: "Use the Unofficial Bash Strict Mode (Unless You Looove Debugging)", Aaron Maxwell](http://redsymbol.net/articles/unofficial-bash-strict-mode/)
- [Site: "Bash Pitfalls", Greg's Wiki](https://mywiki.wooledge.org/BashPitfalls)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
