---
title: 1. Quoting
description: The single habit that prevents the most common way shell scripts break in production
type: lesson
---

# Lesson 1. Quoting

**Mission link:** Quoting is the first thing "write shell that survives production" actually means in practice. Most of the failure modes this mission covers trace back to a missing quote somewhere.
**Primary source:** [Docs: "Shell Command Language", POSIX.1-2017, The Open Group](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html)
**Prerequisites:** none

## Know this

### What an unquoted expansion actually does

Write `$file` or `$(some command)` without quotes, and before the shell treats the result as one argument, it runs two more steps on it:

- **Word splitting**: the result is split into separate words wherever a character in `$IFS` (space, tab, newline, by default) appears.
- **Pathname expansion (globbing)**: if any resulting word contains a glob character (`*`, `?`, `[`), the shell tries to match it against filenames and replaces it with whatever matches, if anything does.

Both of these happen to *the result of expansion*, not to what you wrote. `rm $file` doesn't mean "remove the file named by `$file`"; it means "remove whatever files result from splitting and globbing the value of `$file`." Those are usually the same thing, until they aren't.

### Where this actually bites

If `file="notes final.txt"`, then `rm $file` doesn't try to remove one file called `notes final.txt`. Word splitting turns it into two words, `notes` and `final.txt`, and `rm` receives them as two separate arguments: it tries to remove a file called `notes` and a file called `final.txt`, either or both of which may not exist, while the file you actually meant to remove is untouched.

Globbing compounds this. If a variable's value happens to contain `*` (a filename with a literal asterisk, or a value built from unsanitized input), an unquoted expansion of it can silently turn into a list of every file in the current directory that happens to match. A script that does `rm $pattern` with an unquoted, attacker- or accident-influenced `$pattern` is a well-known way to delete far more than intended. [Bash Pitfalls](https://mywiki.wooledge.org/BashPitfalls) catalogs many concrete variations of exactly this failure.

### Double quotes vs. single quotes vs. none

- **Unquoted** (`$var`): word splitting and globbing both apply. Almost never what you want for a variable holding a filename, a path, or any value that might contain whitespace.
- **Double-quoted** (`"$var"`): word splitting and globbing are suppressed, but variable and command substitution still happen. `"$HOME/data"` still expands `$HOME`; it just won't be split or globbed afterward. **This is the default you should reach for.**
- **Single-quoted** (`'$var'`): nothing is expanded at all. The characters between the quotes are completely literal, including `$`, backticks, and everything else. Use this only when you specifically want the literal text `$var`, not its value, such as inside an `awk` script or when documenting a variable name in a message.

The practical rule this lesson is built around: **quote every variable and command substitution expansion with double quotes, unless you have a specific, commented reason to want word splitting or globbing to happen.** That specific reason is rare enough that its absence is the default worth defending, not the exception.

### Tooling catches this class of bug automatically

[ShellCheck](https://www.shellcheck.net/) flags a missing quote around an expansion (its warning code for this is `SC2086`) before the script ever runs, along with an explanation of exactly what could go wrong. Running it is cheap enough that there's rarely a reason not to, for any script meant to survive contact with real input.

## Practice

1. ▢ In one sentence, what two things happen to an unquoted `$variable` or `$(command)` expansion that do not happen to a double-quoted one?

<details markdown="1"><summary>Check</summary>

Word splitting (breaking the result into separate words on `$IFS` characters) and pathname expansion / globbing (replacing a word containing `*`, `?`, or `[` with matching filenames).

</details>

2. ▢ `file="notes final.txt"` and a script runs `rm $file`. What actually happens, and why?

<details markdown="1"><summary>Check</summary>

Word splitting breaks the unquoted expansion into two separate arguments, `notes` and `final.txt`, so `rm` tries to remove two files with those exact names rather than one file named `notes final.txt`. Neither of those two files necessarily exists, and the intended file is left untouched. Quoting it as `rm "$file"` passes the whole string as one argument.

</details>

3. ▢ A variable holds `path='$HOME/data'` (set with single quotes at assignment time, so it literally contains the four characters `$`, `H`, `O`, `M`, and so on). Later, the script does `echo "$path"` versus `echo '$path'`. What does each print, and why do they differ?

<details markdown="1"><summary>Hint</summary>

The quoting at the point of *use* (`echo`) controls this, not the quoting used when `path` was originally assigned.

</details>

<details markdown="1"><summary>Check</summary>

`echo "$path"` performs variable expansion (double quotes still expand `$path` itself into its stored value, the literal string `$HOME/data`), then prints that value without further splitting or globbing: `$HOME/data`. `echo '$path'` is single-quoted, so nothing is expanded at all, printing the four characters `$path` literally, not the variable's value. The distinction is entirely about the quoting used at the point where `$path` is referenced.

</details>

4. ▢ Which of these lines is safe against both word splitting and globbing for a variable that might contain spaces or glob characters?

   - a) `cp $source $dest`
   - b) `cp "$source" "$dest"`
   - c) `cp '$source' '$dest'`
   - d) `cp ${source} ${dest}`

<details markdown="1"><summary>Check</summary>

**b)** `cp "$source" "$dest"`. (a) and (d) are both unquoted (the braces in `${source}` only affect parsing of the variable name, not splitting or globbing) and remain vulnerable. (c) is single-quoted, so it would literally try to copy files named `$source` and `$dest` rather than the values those variables hold.

</details>

## Real-world reps

- [ ] Find a shell script you have access to (your own, or an open-source one) and run [ShellCheck](https://www.shellcheck.net/) against it. Note every `SC2086` warning it produces.
- [ ] Pick one of those warnings (or, if none exist, deliberately write a small script with an unquoted expansion) and construct an input value that makes the unquoted version misbehave. Confirm that adding quotes fixes it.
- [ ] Tomorrow: read three or four entries from Bash Pitfalls in full, and write down which ones you'd have written yourself before this lesson.

## Going further

- [Article: "Use the Unofficial Bash Strict Mode (Unless You Looove Debugging)", Aaron Maxwell](http://redsymbol.net/articles/unofficial-bash-strict-mode/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
