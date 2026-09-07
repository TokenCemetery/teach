---
title: 7. Knowing When to Stop
description: The concrete signals that a script has outgrown shell's judgment-free zone, and why the job now belongs in a real language instead
type: lesson
---

# Lesson 7. Knowing When to Stop

**Mission link:** This is the final lesson of the arc. Every prior lesson made shell survive production better; this lesson is the mission's other half, recognizing when doing that is no longer the right move, and the job belongs in `programming/python` instead.
**Primary source:** [Site: "Shell Style Guide", Google](https://google.github.io/styleguide/shellguide.html)
**Prerequisites:** [Lesson 6](0006-awk-and-sed-where-needed.md), [Word splitting](../GLOSSARY.md)

## Warm-up

1. ▢ A script needs to replace every occurrence of a value in a config file. Which tool fits, `sed` or `awk`, and why?

<details markdown="1"><summary>Check</summary>

`sed`, since this is a simple, pattern-based substitution applied line by line across a file, exactly the shape of task `sed` is built for, not requiring field extraction or arithmetic the way `awk` would.

</details>

2. ▢ Why does the mission's constraint describe `awk`/`sed` as touched only where a script genuinely needs them, rather than as a default habit?

<details markdown="1"><summary>Check</summary>

Bash remains the right tool for control flow and gluing commands together; reaching for `awk`/`sed` by default, even where bash's own operations or a simple loop would handle a task fine, adds complexity and subprocess overhead without a corresponding benefit.

</details>

## Know this

### Shell has a real, describable ceiling, not just a vague feeling of complexity

**Google's Shell Style Guide** states a concrete rule most style guides only gesture at: if you are writing a script from scratch, and it exceeds 100 lines, or its logic becomes non-trivial (real data structures, error handling beyond exit-status checks, anything approaching a control flow more complex than straightforward branching), write it in a more structured language instead, from the start. This isn't a stylistic preference; it names shell's actual, structural ceiling: no native data structures beyond strings and (bash-only, lesson 5) flat arrays, no real exception handling beyond checking exit statuses (lessons 2-3), and error-prone text manipulation for anything more structured than simple substitution or field extraction (lesson 6).

### The concrete signals, not a gut feeling

Several specific, checkable signals say a script has crossed shell's ceiling: needing a data structure beyond a flat list (a dictionary, a nested structure, a real object) that shell has no native way to represent cleanly; error handling more complex than "check the exit status and branch" (retry logic with backoff, structured error types, aggregating multiple failures); manipulating structured data (JSON, a real config format) beyond what a `sed`/`awk` one-liner handles cleanly, meaning every additional feature request makes the shell version more fragile rather than more capable; or the script's own length and branching complexity making it genuinely hard to reason about what it does, the "100 lines and growing" signal named directly. Any one of these, on its own, is worth pausing on; several together is a clear stop sign.

### Why the switch is a design decision, not a failure

Recognizing a script has outgrown shell and rewriting it in Python isn't admitting the original shell script was a mistake; it's the same kind of judgment call lesson 6 asked for with `sed`/`awk`, matching the tool to the actual shape of the problem. A script that started simple and grew real branching logic, structured data, or non-trivial error handling has changed shape since it was first written, and continuing to force it into shell past that point produces exactly the fragile, hard-to-maintain code the mission opened by warning against, the same fragility a script with production-breaking quoting or exit-status bugs has, just from a different cause.

### Where the job goes: `programming/python`, and why that boundary is deliberate

This workspace's explicit boundary (`## Out of scope`) hands off exactly at this point: once a script needs real data structures, structured error handling, or genuine control-flow complexity, `programming/python` is where those capabilities exist natively rather than as workarounds. This isn't because Python is universally better than shell; it's because each tool has a real domain it fits (shell for orchestration, gluing commands, and straightforward sequential logic; Python for anything needing real data structures or complex control flow), and the discipline this mission closes on is recognizing which domain a given script's actual requirements now belong to, rather than defaulting to whichever language the script happened to start in.

## Practice

1. ▢ State the concrete line-count and complexity signal Google's Shell Style Guide gives for when to write a script in a different language from the start.

<details markdown="1"><summary>Check</summary>

If a script written from scratch would exceed 100 lines, or its logic becomes non-trivial (real data structures, error handling beyond exit-status checks, complex control flow), it should be written in a more structured language instead of shell.

</details>

2. ▢ A shell script starts needing to represent a nested structure (a list of records, each with several named fields) rather than a flat list of values. Why is this a concrete signal to stop using shell, not just an inconvenience to work around?

<details markdown="1"><summary>Hint</summary>

Consider what shell (even bash, with its flat arrays) actually offers natively for this shape of data.

</details>

<details markdown="1"><summary>Check</summary>

Shell has no native way to represent a nested or structured data shape cleanly; even bash's arrays (lesson 5) are flat lists, not records with named fields, and working around this typically means encoding structure into strings and parsing it back out, exactly the fragile text-manipulation-under-strain this lesson warns is a signal, not a solvable inconvenience.

</details>

3. ▢ Why is switching a growing shell script to Python described as a design decision rather than an admission that the original script was a mistake?

<details markdown="1"><summary>Check</summary>

The script's actual requirements changed shape as it grew (real branching, structured data, non-trivial error handling), and recognizing that shift and matching the tool to the new shape is the same kind of judgment call as choosing `sed` versus `awk` versus bash's own string handling (lesson 6). The original shell script wasn't wrong for its original, simpler scope; continuing to force the grown version into shell is what would be the actual mistake.

</details>

4. ▢ A script started as a 20-line deployment helper and has grown to include retry logic with exponential backoff, parsing a JSON config file, and branching on several structured error conditions. Apply this lesson's signals to decide whether it should stay in shell.

<details markdown="1"><summary>Check</summary>

At least two concrete signals apply: non-trivial error handling (retry logic with backoff, structured error conditions go well beyond checking an exit status) and structured data manipulation (parsing JSON is exactly the kind of structured-data task beyond a `sed`/`awk` one-liner). Either signal alone is worth pausing on; both together is a clear case for rewriting it in `programming/python`, where JSON parsing and structured error handling exist natively.

</details>

5. ▢ Which claim correctly describes knowing when to stop using shell?

   - a) Any script that uses `sed` or `awk` has already outgrown shell and should be rewritten
   - b) Concrete, checkable signals (real data structures, non-trivial error handling, structured data manipulation, a script exceeding roughly 100 lines) indicate shell's ceiling has been reached, and switching to a language like Python at that point is a deliberate design match, not an admission of failure
   - c) A script should never be rewritten once started in shell, regardless of how complex it becomes, since rewriting wastes the original work
   - d) Line count is the only signal that matters; a script's actual logic complexity is irrelevant as long as it stays short

<details markdown="1"><summary>Check</summary>

**b)** That's the precise, checkable set of signals this lesson (and the mission) closes on. (a) is false: lesson 6 covers using `sed`/`awk` appropriately within shell scripts, which is not itself a stopping signal. (c) is false: refusing to rewrite a script whose requirements have outgrown shell is exactly the fragility this mission warns against. (d) is false: the style guide's own rule names both line count and logic complexity (data structures, error handling) as signals, not line count alone.

</details>

## Real-world reps

- [ ] Find a shell script you have access to that's grown substantially since it was first written. Check it against this lesson's four signals (data structures, error-handling complexity, structured data manipulation, line count/branching complexity) and decide whether it's past shell's ceiling.
- [ ] For a script that does show one or more of these signals, sketch (even briefly) what the equivalent logic would look like in Python, and note specifically what becomes easier (a real dict instead of encoded strings, a real exception instead of an exit-status check).
- [ ] Tomorrow: read the primary source's full guidance on when to choose shell versus a different language, and compare its stated rule against your own intuition before reading it.

## Going further

- [Site: "Shell Style Guide", Google](https://google.github.io/styleguide/shellguide.html)
- [Docs: "Shell Command Language", POSIX.1-2017, The Open Group](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
