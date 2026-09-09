---
title: Quoting and Pitfalls
description: "Quoting rules, word splitting and globbing, and the Bash Pitfalls that survive even careful quoting"
type: reference
---

# Quoting and Pitfalls

Stages 1 and 3 compressed for lookup. [Lesson 1](../lessons/0001-quoting.md) covers quoting itself; [lesson 4](../lessons/0004-word-splitting-and-globbing-pitfalls.md) covers the footguns that survive even careful quoting. This sheet is the quoting rule and the specific pitfalls it doesn't fix on its own.

## Quoting

An unquoted `$var` or `$(command)` expansion undergoes two more steps before the shell uses it: **word splitting** (breaking the result on `$IFS` characters, space/tab/newline by default) and **pathname expansion / globbing** (replacing a word containing `*`, `?`, or `[` with matching filenames).

| Form | Word splitting | Globbing | Variable/command expansion | Use for |
|---|---|---|---|---|
| Unquoted `$var` | Yes | Yes | Yes | Almost never, for a value that might hold whitespace or a glob character |
| `"$var"` | No | No | Yes | The default: quote every expansion unless you specifically want splitting or globbing |
| `'$var'` | No | No | No | The literal text `$var` itself, not its value (an `awk` script, documenting a variable name) |

**Where it bites.** `file="notes final.txt"`; `rm $file` splits into two words, `notes` and `final.txt`, deleting neither the intended file nor necessarily anything sensible. A variable holding a value with `*` in it, expanded unquoted, can silently expand to every matching file in the directory: `rm $pattern` with an attacker- or accident-influenced `$pattern` is a well-known way to delete far more than intended.

**Tooling catches this class of bug automatically.** [ShellCheck](https://www.shellcheck.net/)'s `SC2086` flags a missing quote around an expansion before the script ever runs.

## Pitfalls that survive careful quoting

| Pitfall | Looks fine because | Actually breaks because | Fix |
|---|---|---|---|
| `for f in $(ls *.txt)` | No obviously unquoted variable | `$(ls *.txt)` is itself an unquoted command substitution; its whole output is word-split regardless of individual filenames | `for f in *.txt; do ...; done`, letting the shell's own globbing produce the file list directly |
| An unmatched glob (`*.txt` in an empty directory) | "For each matching file" reads as "skip if none match" | Bash passes the literal, unmatched pattern through as one word by default; the loop runs once with `f` set to the literal string `*.txt` | `shopt -s nullglob`, so an unmatched glob expands to nothing |
| Iterating a properly quoted capture (`for word in $output`) | `"$(command)"` was quoted at capture time | The quoting at capture protects the string's content, but an unquoted loop over it reintroduces word splitting on `$IFS` | Read line-by-line (`while IFS= read -r line`) or use an array, instead of splitting the captured string with a bare `for` |
| `while read line; do ...; done < file` | Looks like the natural way to read a file line by line | No `-r` means backslashes are interpreted specially; no `IFS=` means leading/trailing whitespace is stripped per line | `while IFS= read -r line; do ...; done < file` |

## Before trusting a loop or a quoted expansion

- [ ] Every variable and command substitution expansion is double-quoted, unless there is a specific, commented reason for word splitting or globbing.
- [ ] No loop's file list comes from `$(ls ...)`; a bare glob (`for f in *.ext`) is used instead.
- [ ] `nullglob` is set wherever an unmatched glob should mean "nothing," not "the literal pattern."
- [ ] Any `while read` loop uses both `-r` and `IFS=`.
- [ ] [ShellCheck](https://www.shellcheck.net/) has been run against the script, with `SC2086` warnings resolved.

## Sources

- [Docs: "Shell Command Language", POSIX.1-2017, The Open Group](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html)
- [Site: "Bash Pitfalls", Greg's Wiki](https://mywiki.wooledge.org/BashPitfalls)
- [Resources](../RESOURCES.md)
