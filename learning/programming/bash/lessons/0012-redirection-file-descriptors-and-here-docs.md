---
title: 12. Redirection, File Descriptors, and Here-Docs
description: Sending a command's output somewhere other than the screen, precisely, and feeding it a block of input inline
type: lesson
---

# Lesson 12. Redirection, File Descriptors, and Here-Docs

**Mission link:** Stage 9 opens composing commands rather than holding values. This lesson is redirection: sending a command's output or error stream somewhere specific, in an order that actually matters, before lesson 13 covers composing whole commands together with pipes and subshells.
**Primary source:** [Docs: "Shell Command Language", POSIX.1-2017, The Open Group](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html)
**Prerequisites:** [Lesson 11](0011-arrays.md), [Word splitting](../GLOSSARY.md)

## Warm-up

1. ▢ Given `hosts=(web1 "web 2" web3)`, what does `for h in "${hosts[@]}"; do echo "[$h]"; done` print?

<details markdown="1"><summary>Check</summary>

Three lines: `[web1]`, `[web 2]`, `[web3]`. The quoted `@` form expands to each element as its own word, so the space inside `"web 2"` stays part of that one element.

</details>

2. ▢ A script requires `API_KEY` with no sensible default. Which parameter expansion form is built for exactly this?

<details markdown="1"><summary>Check</summary>

`${API_KEY:?API_KEY must be set}`: if unset or empty, it prints that message to standard error and exits immediately with a nonzero status, rather than silently substituting an empty string.

</details>

## Know this

### Three numbered streams, and the operators that redirect them

Every process starts with three open file descriptors: **`0`** (standard input, what a command reads), **`1`** (standard output, what it normally prints), and **`2`** (standard error, where diagnostics go so they can be told apart from real output). `>` redirects `1` to a file, truncating it first; `>>` does the same but appends. `<` redirects `0` to read from a file instead of the terminal or a pipe. `2>` redirects file descriptor `2` specifically; `2>&1` points file descriptor `2` at wherever `1` currently points, not at a file named `1`, which is the single most common source of confusion in this whole area. `/dev/null` is the standard place to redirect output a script genuinely doesn't want, `command > /dev/null 2>&1` discarding both streams entirely.

### Redirections apply left to right, so order changes the result

`cmd > file 2>&1` and `cmd 2>&1 > file` look almost identical and do different things, because redirections are set up strictly in the order they're written. `cmd > file 2>&1` first points `1` at `file`, then points `2` at wherever `1` now points (`file`), so both streams end up in `file`. `cmd 2>&1 > file` first points `2` at wherever `1` currently points (the terminal, if nothing redirected it yet), then points `1` at `file`, so `2` is already committed to the terminal and stays there while only `1` moves to `file`. Reading a redirection chain as "set this stream, then set the next one, based on where things stand right now" is the only way to predict the result correctly.

![Two timelines showing redirections applied left to right. On the left, cmd greater-than file, then 2 greater-than ampersand 1: stdout is redirected to file first, then stderr is pointed at wherever stdout currently points, which is now file, so both streams end up in file. On the right, cmd 2 greater-than ampersand 1, then greater-than file: stderr is pointed at wherever stdout currently points, which is still the terminal, and only afterward is stdout redirected to file, so stderr still goes to the terminal while stdout alone goes to file.](images/redirection-order-matters.svg)

### Custom file descriptors: opening one deliberately, without borrowing 0-2

`exec 3< file` opens file descriptor `3` for reading from `file`, in the current shell (not a subshell), leaving it open across subsequent commands until it's explicitly closed (`exec 3<&-`) or the script exits. This is the tool for reading from two sources at once without one interfering with the other, or for holding a file descriptor open for a lock (`flock` commonly uses one this way). It's a step beyond what most scripts need day to day, worth knowing exists once `0`, `1`, and `2` alone stop being enough.

### Here-docs and here-strings: inline input without a separate file

`<<EOF ... EOF` (a **here-doc**) feeds everything between the two `EOF` markers to a command's standard input, as if it had been typed there; the closing marker has to start at the beginning of its line unless `<<-EOF` is used, which allows it to be indented to match the surrounding code. `<<'EOF' ... EOF` (the delimiter quoted) suppresses variable expansion and command substitution inside the block, useful for a literal template; leaving it unquoted expands `$variables` inside it normally. **`<<<`** (a **here-string**, bash-only) is the same idea for a single value already in hand: `cmd <<< "$value"` feeds `$value` plus a trailing newline to `cmd`'s standard input, without needing a multi-line block at all.

## Practice

1. ▢ A script runs `backup.sh > /var/log/backup.log 2>&1`. Where do the script's normal output and its error messages each end up?

<details markdown="1"><summary>Check</summary>

Both end up in `/var/log/backup.log`. `>` first points stdout at the log file; `2>&1` then points stderr at wherever stdout currently points, which is now that same file, so both streams are captured together.

</details>

2. ▢ Rewrite `cmd 2>&1 > results.txt` to send both stdout and stderr into `results.txt`, and explain why the original doesn't do that.

<details markdown="1"><summary>Hint</summary>

Consider what `2>&1` actually points at when it runs before anything has redirected stdout yet.

</details>

<details markdown="1"><summary>Check</summary>

The fix is `cmd > results.txt 2>&1` (stdout redirected first, then stderr pointed at wherever stdout now points). The original doesn't work because `2>&1` runs first, pointing stderr at wherever stdout was pointing at that moment (the terminal), before `> results.txt` redirects stdout away; stderr is left on the terminal while only stdout moves to the file.

</details>

3. ▢ What does `cat <<'EOF'` (quoted delimiter) do differently from `cat <<EOF` (unquoted) if the here-doc's body contains `$HOME`?

<details markdown="1"><summary>Check</summary>

With the quoted delimiter (`<<'EOF'`), `$HOME` is passed through literally, unexpanded. With the unquoted form (`<<EOF`), `$HOME` is expanded to its actual value before the text reaches the command, the same as any other double-quoted context.

</details>

4. ▢ A script needs to feed a single already-known string, held in a variable, to a command's standard input, without writing a multi-line here-doc for it. What's the concise, bash-only way to do this?

<details markdown="1"><summary>Check</summary>

A here-string: `cmd <<< "$value"`, which feeds `$value` (plus a trailing newline) directly to `cmd`'s standard input in one line, no opening and closing delimiter needed.

</details>

5. ▢ Which claim correctly explains why `cmd > file 2>&1` and `cmd 2>&1 > file` behave differently?

    - a) `2>&1` always means "redirect stderr to the file named 1", regardless of where it appears
    - b) Redirections are applied strictly in the order written; `2>&1` points file descriptor 2 at wherever file descriptor 1 currently points, so its effect depends on whether stdout was already redirected when it runs
    - c) The two forms are equivalent; bash reorders redirections before executing them
    - d) `2>&1` only has an effect when it appears before any other redirection

<details markdown="1"><summary>Check</summary>

**b)** That's the exact mechanism: `2>&1` redirects to wherever `1` points at that moment in the left-to-right sequence, not to a fixed target. (a) is false: `2>&1` means "point at wherever 1 points," never a literal file named `1`. (c) is false: bash applies redirections in the written order, with no reordering. (d) is false: `2>&1` has an effect wherever it appears; that effect just depends on stdout's redirection state at that point.

</details>

## Real-world reps

- [ ] Find a script you have access to that redirects both stdout and stderr, and check whether `2>&1` comes after the file redirection (correct, for combining both into one file) or before it (likely a bug, unless leaving stderr on the terminal was the actual intent).
- [ ] Find (or write) a script using a here-doc to generate a config file or template, and check whether its delimiter is quoted or not, and whether that matches what the template actually needs (literal `$` characters versus expanded variables).
- [ ] Tomorrow: read the primary source's section on redirection operators in full, including any form (like `>|` to force overwrite under `noclobber`) this lesson didn't cover.

## Going further

- [Docs: "Shell Command Language", POSIX.1-2017, The Open Group](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html)
- [Docs: "Bash Reference Manual", GNU](https://www.gnu.org/software/bash/manual/bash.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
