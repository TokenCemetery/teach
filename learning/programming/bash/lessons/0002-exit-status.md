---
title: 2. Exit Status
description: What $? actually reports, why bash keeps running after a failed command by default, and the second most common way a script breaks in production
type: lesson
---

# Lesson 2. Exit Status

**Mission link:** Stage 2 opens exit status and error handling. Quoting (lesson 1) prevents one class of production failure; this lesson is the other half of "shell that survives production," a script that actually notices when something it ran has failed.
**Primary source:** [Docs: "Shell Command Language", POSIX.1-2017, The Open Group](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html)
**Prerequisites:** [Lesson 1](0001-quoting.md), [Word splitting](../GLOSSARY.md)

## Warm-up

1. ▢ What two things happen to an unquoted `$variable` or `$(command)` expansion that don't happen to a double-quoted one?

<details markdown="1"><summary>Check</summary>

Word splitting (breaking the result into separate words on `$IFS` characters) and pathname expansion / globbing (replacing a word containing `*`, `?`, or `[` with matching filenames).

</details>

2. ▢ `file="notes final.txt"` and a script runs `rm $file`. What actually happens?

<details markdown="1"><summary>Check</summary>

Word splitting breaks the unquoted expansion into two separate arguments, `notes` and `final.txt`, so `rm` tries to remove two files with those exact names instead of one file named `notes final.txt`, and the intended file is left untouched.

</details>

## Know this

### Every command reports success or failure as a number, whether or not anyone checks

Every command that finishes running sets an **exit status**: an integer from 0 to 255, where **0 means success** and **any nonzero value means failure**, by POSIX convention. This isn't optional or something a command has to opt into; it's how every command, built-in, and script communicates its outcome to whatever called it. `$?` holds the exit status of the most recently executed command, and it's overwritten by the *next* command that runs, including a command as innocuous-looking as `echo` or `[ -f ... ]`, so it has to be captured or checked immediately after the command whose status matters.

### Bash keeps going by default, which is the actual problem

Unless told otherwise, a shell script's default behavior is to run each command in sequence regardless of whether the previous one succeeded or failed. A command failing doesn't stop the script; it just leaves a nonzero value in `$?` that nothing is obligated to look at. This is the second most common way a script breaks in production, right after quoting: a command partway through a script fails (a directory doesn't exist, a network call times out, a file is missing), and the script sails on to the next line as if nothing happened, often producing a confusing failure several steps later instead of a clear one at the actual point of failure.

### Checking exit status directly, versus letting it slip past unnoticed

The direct check is `if command; then ... else ... fi`, or the shorthand `command || handle_failure`, both of which branch on the command's own exit status without needing to read `$?` explicitly. A subtler trap: `$?` only reflects the *last* command run, so `grep pattern file; echo "exit code was $?"` is fine, but inserting any command, even something that looks like a no-op, between the command you care about and the check silently discards the value you meant to inspect. This is why checking a critical command's status immediately, or capturing it into a variable right away (`command; status=$?`), matters more than it looks like it should.

### A pipeline's exit status is, by default, only its last command's

`cmd1 | cmd2` returns the exit status of `cmd2` by default, regardless of whether `cmd1` succeeded or failed. A script checking `$?` after a pipeline is checking only whether the *last* stage worked, which can silently hide a failure earlier in the pipe (a `grep` that failed to find anything feeding an unrelated `sort` that always "succeeds" on empty input). This gap is exactly what `set -o pipefail` (covered as part of lesson 3's strict-mode capstone) exists to close.

## Practice

1. ▢ What does an exit status of `0` mean, and what does any nonzero value mean?

<details markdown="1"><summary>Check</summary>

`0` means the command succeeded. Any nonzero value (1 through 255) means the command failed in some way, by POSIX convention that every command, built-in, or script follows.

</details>

2. ▢ A script runs `mkdir /some/dir`, then two lines later checks `if [ $? -eq 0 ]; then ...`. What's wrong with this, even if `mkdir` actually failed?

<details markdown="1"><summary>Hint</summary>

Consider what happened to `$?` in between the command that mattered and the check.

</details>

<details markdown="1"><summary>Check</summary>

`$?` only holds the exit status of the *most recently run* command, so whatever ran on the lines between `mkdir` and the check overwrote it. The check is now inspecting the status of whatever ran right before it, not `mkdir`'s actual result, so it can report success even if `mkdir` genuinely failed.

</details>

3. ▢ Why does bash continue running a script's remaining commands by default after one of them fails, and why is this described as the actual problem rather than a neutral default?

<details markdown="1"><summary>Check</summary>

A shell script's default behavior is to execute each command in sequence regardless of the previous command's exit status; nothing stops the script unless something explicitly checks and reacts to a failure. This is a problem because a failure partway through often produces a confusing, unrelated failure several steps later, or silent wrong behavior, instead of a clear failure at the actual point something went wrong.

</details>

4. ▢ A pipeline `grep "error" logfile.txt | wc -l` is used to check whether any errors exist, then the script inspects `$?` afterward. Why might this check give a misleading answer regardless of whether `grep` actually found a match?

<details markdown="1"><summary>Check</summary>

By default, a pipeline's exit status is only the *last* command's, here `wc -l`, which almost always succeeds (it can count zero lines just as easily as many). So `$?` after this pipeline reflects whether `wc -l` ran successfully, not whether `grep` actually matched anything or failed for an unrelated reason (like the logfile not existing), silently hiding the information the script actually wanted.

</details>

5. ▢ Which claim correctly describes exit status?

    - a) Only commands that explicitly opt into it report an exit status; most commands leave `$?` unchanged
    - b) A nonzero exit status means failure, `$?` reflects only the most recently run command, and a script continues past a failed command unless something explicitly checks and reacts to it
    - c) A pipeline's exit status always reflects whether every stage of the pipe succeeded
    - d) `$?` is only relevant for scripts that use `if` statements

<details markdown="1"><summary>Check</summary>

**b)** That's the precise, load-bearing set of facts this lesson covers. (a) is false: every command sets an exit status, whether or not it's checked. (c) is false: by default a pipeline's exit status is only its last command's, exactly the gap `pipefail` (lesson 3) closes. (d) is false: `$?` matters any time a script's later behavior depends on whether an earlier command actually succeeded, `if` or otherwise.

</details>

## Real-world reps

- [ ] Find a shell script you have access to that runs more than one command in sequence. Check whether it verifies each command's exit status, or just assumes success and moves on.
- [ ] For a command in that script whose failure would matter, deliberately make it fail (a missing file, a bad argument) and observe what the script actually does, versus what you'd want it to do.
- [ ] Tomorrow: find one pipeline (`cmd1 | cmd2`) in a real script and determine what its exit status would be if the first command failed but the second one still produced output, without running it.

## Going further

- [Docs: "Shell Command Language", POSIX.1-2017, The Open Group](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html)
- [Article: "Use the Unofficial Bash Strict Mode (Unless You Looove Debugging)", Aaron Maxwell](http://redsymbol.net/articles/unofficial-bash-strict-mode/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
