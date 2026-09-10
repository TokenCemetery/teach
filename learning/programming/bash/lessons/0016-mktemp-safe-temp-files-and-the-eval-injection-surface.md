---
title: 16. mktemp, Safe Temp Files, and the eval/Injection Surface
description: Creating a temporary file that can't be predicted or hijacked, and why eval turns untrusted input into arbitrary code
type: lesson
---

# Lesson 16. mktemp, Safe Temp Files, and the eval/Injection Surface

**Mission link:** Stage 11 opens the mission's safety half directly. Lesson 15 handled a script's own concurrency and shutdown; this lesson is two of the sharpest ways a script that otherwise looks correct still gets exploited: a guessable temp filename, and a string built from untrusted input handed to `eval`.
**Primary source:** [Site: "Shell Style Guide", Google](https://google.github.io/styleguide/shellguide.html)
**Prerequisites:** [Lesson 15](0015-signals-background-jobs-and-wait.md), [Word splitting](../GLOSSARY.md)

## Warm-up

1. ▢ Why does `$?` immediately after `cmd &` almost never report what a script actually wants to know?

<details markdown="1"><summary>Check</summary>

It reports whether *starting* the background job succeeded (almost always `0`), not `cmd`'s eventual exit status, since `cmd` hasn't necessarily finished by the time `$?` is checked; that requires `wait "$pid"` later.

</details>

2. ▢ Why does a script launching background jobs need to explicitly forward `SIGTERM` to them?

<details markdown="1"><summary>Check</summary>

A background job is a separate process; the script's own termination doesn't automatically propagate to it. Without a `trap` forwarding the signal, background children become orphaned, still running after the script that started them is gone.

</details>

## Know this

### A predictable temp filename is an attack surface, not just an aesthetic choice

A script that builds a temp filename itself, `/tmp/app.$$` (`$$` being the script's own PID), makes that name predictable to anything else on the same machine, including a hostile process watching for it. An attacker who predicts the name can create a **symlink** at that exact path, pointing at a file the script has no business touching, before the script ever runs; when the script then writes to "its" temp file, it's actually following the symlink and writing to (or, worse, truncating) whatever the attacker pointed it at. This is a real, historically-exploited class of bug (a **symlink attack** / **TOCTOU** race, "time of check to time of use"), not a hypothetical: checking "does this path exist" and then creating a file at it are two separate steps an attacker can act between.

### `mktemp`: unpredictable, exclusive, and correctly permissioned in one step

`mktemp` creates a file (or, with `-d`, a directory) with a name nothing could have predicted in advance, atomically, so there's no window between checking a name is free and claiming it for an attacker to exploit, and with restrictive permissions (mode `600`, readable and writable only by the file's owner) from the moment it's created rather than as an afterthought. `tmpfile=$(mktemp)` is the whole pattern; pairing it with lesson 3's cleanup `trap`, `trap 'rm -f "$tmpfile"' EXIT`, guarantees the file is removed whether the script succeeds, fails, or is interrupted, closing both the security risk and the "script leaves junk in `/tmp` forever" annoyance in the same line.

![Two panels. On the left, a script writes to a predictable path like slash tmp slash app dot dollar-dollar, built from its own process id. An attacker who can guess that name in advance creates a symlink at that path pointing at a sensitive file before the script runs, so the script's write lands on the attacker's chosen target instead of a fresh temp file. On the right, mktemp creates a file with a random, unpredictable name atomically, so there is nothing for an attacker to pre-create a symlink at, and no race window between checking the name is free and creating the file.](images/predictable-tmpname-vs-mktemp.svg)

### `eval`: re-parsing a string as shell code, exactly the shape SQL injection takes in a database

`eval STRING` takes `STRING` and runs it as if it had been typed directly into the shell, a second full parse-and-execute pass over whatever that string happens to contain. `eval "some_command $user_input"` is exactly as dangerous as building a SQL query by concatenating unsanitized user input into it: if `user_input` is `"; rm -rf ~"`, the shell doesn't see one argument containing a semicolon, it sees two full commands to run in sequence, because `eval` deliberately re-parses the string from scratch, quoting and all. The rule this lesson is named for: **never `eval` a string built from input the script doesn't fully control**, the same discipline as never concatenating untrusted input directly into a SQL query.

### Building a command dynamically without `eval`: an array, not a string

The common reason a script reaches for `eval` in the first place, building up a command with a variable number of arguments or flags, has a safer answer: an array (lesson 11). `cmd=(rsync -av); [ "$dry_run" = 1 ] && cmd+=(--dry-run); cmd+=("$src" "$dst"); "${cmd[@]}"` builds the same flexible command without ever re-parsing a string, since each array element is already a distinct, already-quoted argument that never gets tokenized a second time. This closes the injection surface entirely, not by sanitizing the input more carefully, but by never handing untrusted content to a step that re-interprets it as code at all.

## Practice

1. ▢ A script does `tmpfile="/tmp/report.$$"` and later writes report data to it. What specific attack does this expose the script to, and why does the script's own logic look correct while still being exploitable?

<details markdown="1"><summary>Hint</summary>

Consider what a second, hostile process running on the same machine could do to that exact path before the script gets there.

</details>

<details markdown="1"><summary>Check</summary>

A symlink attack: since `$$` (the PID) is predictable, an attacker who anticipates or observes it can create a symlink at `/tmp/report.<pid>` pointing at a file the attacker wants overwritten, before the script writes anything. The script's own write logic is entirely correct; the vulnerability is the filename being guessable at all, which is exactly what `mktemp` removes.

</details>

2. ▢ Rewrite `tmpfile="/tmp/report.$$"` to use `mktemp`, and add the cleanup this lesson (and lesson 3) recommend pairing with it.

<details markdown="1"><summary>Check</summary>

`tmpfile=$(mktemp)` followed by `trap 'rm -f "$tmpfile"' EXIT`, guaranteeing an unpredictable, mode-600 file that's removed automatically on any exit path, success, failure, or an interrupting signal.

</details>

3. ▢ A script builds `eval "grep $pattern $file"`, where `$pattern` comes from a command-line argument. A caller passes `pattern` as `foo; rm -rf ~`. What actually happens, and why doesn't quoting `$pattern` at the call site fix it?

<details markdown="1"><summary>Check</summary>

`eval` re-parses the entire string a second time, so the semicolon inside `$pattern` is interpreted as a command separator rather than literal text, running `grep foo` followed by a completely separate `rm -rf ~`. Quoting `$pattern` where it's first assigned doesn't help, since `eval` strips a layer of quoting away as part of its second parse; the fix is not using `eval` on untrusted input at all, building the command as an array instead.

</details>

4. ▢ Rewrite the grep example above (lesson practice 3) as an array-based command, avoiding `eval` entirely.

<details markdown="1"><summary>Check</summary>

`cmd=(grep "$pattern" "$file"); "${cmd[@]}"` (or simply `grep "$pattern" "$file"` directly, if no additional flags need to be conditionally assembled). Either way, `$pattern` is passed as a single, already-delimited argument to `grep`; nothing re-parses it as shell syntax, so an embedded `;` is just a literal character in the search pattern, not a command separator.

</details>

5. ▢ Which claim correctly describes the risk `eval` introduces with untrusted input?

    - a) `eval` is dangerous only when the string it's given contains a typo
    - b) `eval` re-parses its argument as shell code a second time, so any shell metacharacter in untrusted input (`;`, `` ` ``, `|`) is interpreted as syntax rather than literal text, the same class of risk as building a SQL query from unsanitized input
    - c) Quoting the variable passed to `eval` at the point it's assigned fully neutralizes the risk
    - d) An array-based command is exactly as vulnerable as `eval`, since both involve building a command from variable parts

<details markdown="1"><summary>Check</summary>

**b)** That's the exact mechanism, and the direct analogy to SQL injection this lesson draws. (a) is false: the risk is structural, present in correctly-formed input too, not just malformed input. (c) is false: `eval`'s second parse strips a layer of quoting, which is exactly why quoting at assignment time doesn't protect against it. (d) is false: an array never re-parses its elements as code, which is precisely what makes it safe where `eval` isn't.

</details>

## Real-world reps

- [ ] Find a script you have access to that builds a temp filename itself (`$$`, a fixed name, a timestamp) rather than using `mktemp`. Rewrite it to use `mktemp` paired with a cleanup `trap`.
- [ ] Search for `eval` in any scripts you maintain. For each occurrence, check whether the string it's given can ever contain untrusted input, and if so, whether it can be rewritten using an array instead.
- [ ] Tomorrow: read the primary source's guidance on `eval` and temp files in full, and note any additional risk or mitigation it names that this lesson didn't cover.

## Going further

- [Site: "Shell Style Guide", Google](https://google.github.io/styleguide/shellguide.html)
- [Site: "Bash Pitfalls", Greg's Wiki](https://mywiki.wooledge.org/BashPitfalls)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
