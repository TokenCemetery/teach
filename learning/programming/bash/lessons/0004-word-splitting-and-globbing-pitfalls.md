---
title: 4. Word Splitting and Globbing Pitfalls
description: Common footguns beyond a bare missing quote, where quoting alone isn't the whole fix
type: lesson
---

# Lesson 4. Word Splitting and Globbing Pitfalls

**Mission link:** This is stage 3, a single-lesson stage bridging quoting and error handling (stages 1-2) to the footguns that survive even careful quoting: looping over unquoted output, glob patterns that match nothing, and array-adjacent traps specific to bash.
**Primary source:** [Site: "Bash Pitfalls", Greg's Wiki](https://mywiki.wooledge.org/BashPitfalls)
**Prerequisites:** [Lesson 3](0003-strict-mode-and-trap.md), [Word splitting](../GLOSSARY.md)

## Warm-up

1. ▢ Why does `set -e` not treat a failing command inside an `if` condition as fatal?

<details markdown="1"><summary>Check</summary>

`set -e`'s exemption for `if`/`while` conditions (and `&&`/`||`, negation with `!`) exists because those contexts are explicitly testing the command's exit status themselves; treating that expected, checked failure as script-ending would defeat the purpose of writing a conditional at all.

</details>

2. ▢ Why does `set -o pipefail` matter for a pipeline like `grep pattern file | sort`?

<details markdown="1"><summary>Check</summary>

Without `pipefail`, the pipeline's exit status is only `sort`'s, which almost always succeeds regardless of what `grep` did. `pipefail` makes the pipeline's status the rightmost nonzero status among all stages, so a `grep` failure is no longer hidden behind a trivially-succeeding `sort`.

</details>

## Know this

### `for f in $(ls *.txt)` is broken even with quoting nowhere obviously missing

A classic pitfall: `for f in $(ls *.txt); do ...; done` looks reasonable, and there's no unquoted variable holding a value with spaces to blame. The bug is structural: `$(ls *.txt)` is itself an unquoted command substitution, so its entire output undergoes word splitting regardless of what individual filenames look like, breaking on any filename containing a space or newline. The actual fix isn't a quote at all; it's not using `ls` for this in the first place: `for f in *.txt; do ...; done` lets the shell's own globbing produce the file list directly as separate words, with no intermediate string to split.

### A glob that matches nothing is passed through literally, not silently empty

`for f in *.txt; do ...; done` in a directory with no `.txt` files doesn't skip the loop as you might expect; by default, bash passes the literal, unmatched pattern `*.txt` through as a single word, and the loop runs once with `f` set to the literal string `*.txt`. This is a real, common footgun precisely because it looks like it should mean "for each matching file, do nothing if there are none," but actually means "for each matching file, or the literal pattern if nothing matches." `shopt -s nullglob` changes this so an unmatched glob expands to nothing at all instead of the literal pattern, which is usually what a script actually wants.

### Word splitting on command substitution output still needs `$IFS` awareness

Even a properly double-quoted `"$(command)"` preserves the *content* faithfully as a single string, including internal newlines, but code that then processes that string with something like an unquoted `for word in $output` loop reintroduces word splitting on `$IFS`. This is a common mistake in scripts that quote correctly at the point of capturing output but then iterate over the captured value carelessly; the fix is either restructuring to avoid iterating over unquoted split output at all (reading line-by-line with `while IFS= read -r line`, or using an array) or being deliberate about exactly which characters should separate words.

### Reading a line, correctly, needs more than `while read line`

`while read line; do ...; done < file` looks like the natural way to process a file line by line, but has two default gaps: `read` without `-r` interprets backslashes in the input specially (mangling any line containing a literal backslash), and leading/trailing whitespace gets stripped by default word splitting inside `read` unless `IFS=` is set for the read. The corrected, defensive form, `while IFS= read -r line; do ...; done < file`, is worth recognizing as a unit rather than assuming the naive version is close enough.

## Practice

1. ▢ Why is `for f in $(ls *.txt)` broken even for filenames with no spaces, once a directory has a file with a space in its name?

<details markdown="1"><summary>Hint</summary>

Consider what happens to the entire output of `$(ls *.txt)` as one unquoted expansion, not to any single filename in isolation.

</details>

<details markdown="1"><summary>Check</summary>

`$(ls *.txt)` is an unquoted command substitution, so its whole output undergoes word splitting on `$IFS`, regardless of which filenames appear in it. A filename containing a space gets split into two separate loop iterations instead of being treated as one filename, the same failure mode as an unquoted variable, just arrived at through a command substitution instead.

</details>

2. ▢ What does `for f in *.txt; do echo "$f"; done` print in a directory with no `.txt` files, by default, and why?

<details markdown="1"><summary>Check</summary>

It prints the literal string `*.txt` once, since bash's default behavior for an unmatched glob is to pass the pattern through unexpanded as a single literal word, running the loop body once with that literal value, rather than skipping the loop entirely.

</details>

3. ▢ What does `shopt -s nullglob` change about the previous question's behavior, and why would a script want that?

<details markdown="1"><summary>Check</summary>

With `nullglob` enabled, an unmatched glob expands to nothing at all instead of the literal pattern, so the `for` loop simply doesn't execute when there are no matching files, which is almost always the behavior a script actually intends when it writes "for each matching file."

</details>

4. ▢ Why is `while read line; do ...; done < file` an incomplete way to read a file line by line, and what's the corrected form?

<details markdown="1"><summary>Check</summary>

Without `-r`, `read` interprets backslashes specially, mangling any line containing a literal backslash; without setting `IFS=` for the read, leading and trailing whitespace on each line gets stripped by default word splitting inside `read`. The corrected form is `while IFS= read -r line; do ...; done < file`, which disables both of these default behaviors.

</details>

5. ▢ Which claim correctly describes a pitfall beyond a bare missing quote?

   - a) `for f in $(ls *.txt)` is safe as long as no variable inside it is unquoted
   - b) An unmatched glob like `*.txt` is passed through literally by default, and `for f in $(ls *.txt)` breaks on filenames with spaces regardless of quoting elsewhere, since the command substitution itself is the unquoted expansion
   - c) `while read line` correctly handles every line in a file as long as the file itself is quoted in the redirection
   - d) Double-quoting a command substitution's output automatically prevents word splitting in any later loop that processes it

<details markdown="1"><summary>Check</summary>

**b)** That's the precise, structural nature of both pitfalls in this lesson. (a) is false: `$(ls *.txt)` itself is the unquoted expansion at fault, independent of any variable. (c) is false: the redirection target isn't the issue; `read` needs `-r` and `IFS=` to handle backslashes and whitespace correctly. (d) is false: quoting protects the captured string itself, but a later unquoted loop over that string (`for word in $output`) reintroduces word splitting regardless of how it was captured.

</details>

## Real-world reps

- [ ] Find a shell script you have access to that loops over the output of `ls`, `find`, or a similar command. Check whether it would break on a filename containing a space, and whether an unmatched glob elsewhere in the script would run the loop body on a literal pattern instead of skipping it.
- [ ] Find (or write) a `while read` loop reading a file line by line. Check whether it uses `-r` and `IFS=`, and construct a test line (containing a backslash, or leading/trailing spaces) that would expose the gap if it doesn't.
- [ ] Tomorrow: read at least five more entries from Bash Pitfalls beyond quoting (lesson 1) and this lesson's specific cases, and note which ones involve a mistake you'd have made yourself.

## Going further

- [Site: "Bash Pitfalls", Greg's Wiki](https://mywiki.wooledge.org/BashPitfalls)
- [Docs: "Shell Command Language", POSIX.1-2017, The Open Group](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
