---
title: 11. Arrays (Indexed and Associative)
description: Holding more than one value without encoding structure into a string, and the one quoting form that keeps each element intact
type: lesson
---

# Lesson 11. Arrays (Indexed and Associative)

**Mission link:** This is stage 8's capstone. Lesson 10 covered transforming one value; this lesson is holding several at once, without falling back to a space-separated string and the word-splitting fragility lesson 4 already warned against.
**Primary source:** [Docs: "Bash Reference Manual", GNU](https://www.gnu.org/software/bash/manual/bash.html)
**Prerequisites:** [Lesson 10](0010-parameter-expansion.md), [Word splitting](../GLOSSARY.md)

## Warm-up

1. ▢ Given `path="/var/log/app.log"`, what does `${path##*/}` expand to?

<details markdown="1"><summary>Check</summary>

`app.log`. `##` removes the longest match of `*/` from the front, stripping everything through the last `/`.

</details>

2. ▢ Why does `${v/pattern/replacement}` need calling out explicitly in a script meant to stay POSIX `sh`-portable?

<details markdown="1"><summary>Check</summary>

It has no POSIX `sh` equivalent at all; it's a bash-only extension, so declaring `#!/bin/sh` while using it makes a false claim about the script's actual requirements.

</details>

## Know this

### Indexed arrays: sequential positions, both bash-only

`arr=(web db cache)` creates an **indexed array**, positions `0`, `1`, `2` holding those three values; `${arr[0]}` reads the first. Indexed arrays, like `[[ ]]` and the parameter-expansion forms in lesson 10, have no POSIX `sh` equivalent at all; a portable script falls back to a space-separated string (with all of lesson 4's word-splitting care) or positional parameters instead. Appending is `arr+=(logging)`, not a re-assignment of the whole array; `${#arr[@]}` gives the element count.

![Two side-by-side structures. On the left, an indexed array, arr, with three slots at positions 0, 1, and 2 holding the values web, db, and cache. On the right, an associative array, svc, with string keys web, db, and cache, each mapping to a port number value, 8080, 5432, and 6379. Both are bash-only, with no POSIX sh equivalent.](images/indexed-vs-associative-arrays.svg)

### `${arr[@]}` versus `${arr[*]}`: the one quoting distinction that actually matters

Quoted, `"${arr[@]}"` expands to each element as its own separate word, spaces inside an element and all, exactly what a `for x in "${arr[@]}"; do` loop needs to visit each element intact regardless of what it contains. `"${arr[*]}"` instead joins every element into a single string, separated by the first character of `$IFS` (a space, by default), which is right when the goal genuinely is one combined string and wrong the moment it's mistaken for the per-element form. Unquoted, both `${arr[@]}` and `${arr[*]}` undergo word splitting and globbing the same way any other unquoted expansion does (lesson 1), erasing the distinction entirely; the whole reason to reach for `@` over `*` only exists once both are quoted.

### Associative arrays: string keys, declared before use

`declare -A svc` declares an **associative array** (string keys instead of sequential positions) before anything can be assigned into it; `svc[web]=8080` assigns, `${svc[web]}` reads. `${!svc[@]}` expands to the array's keys (not its values), the way to iterate over both together: `for key in "${!svc[@]}"; do echo "$key -> ${svc[$key]}"; done`. Associative arrays are bash-only too, and more recent than indexed arrays even within bash's own history, so a script using one is unambiguously declaring a bash dependency, not something that could plausibly have run under an older or more minimal shell by accident.

### Why an array beats encoding structure into one string

Before arrays, a script needing several related values commonly encoded them into one delimited string (`"web:db:cache"`, split on `:` later) or relied on positional parameters standing in for a list. Both work until a value itself needs to contain the delimiter, or until the encoding and decoding logic itself becomes the least reliable part of the script, exactly the kind of fragile text-manipulation-under-strain lesson 7 named as a signal shell has outgrown its judgment-free zone. An array holds each value as its own element from the start, with no delimiter to collide with and no decoding step that can go wrong.

## Practice

1. ▢ `hosts=(web1 "web 2" web3)`. What does `for h in "${hosts[@]}"; do echo "[$h]"; done` print, one line per iteration?

<details markdown="1"><summary>Hint</summary>

Consider what quoting `"${hosts[@]}"` specifically preserves about each element.

</details>

<details markdown="1"><summary>Check</summary>

Three lines: `[web1]`, `[web 2]`, `[web3]`. The quoted `@` form expands to each element as its own word, so the space inside `"web 2"` stays part of that one element rather than splitting it into two.

</details>

2. ▢ Same array, `hosts=(web1 "web 2" web3)`. What does `for h in "${hosts[*]}"; do echo "[$h]"; done` print instead?

<details markdown="1"><summary>Check</summary>

One line: `[web1 web 2 web3]`. `"${hosts[*]}"` joins every element into a single string first (on the first character of `$IFS`, a space by default), so the loop only ever sees one combined word, not three separate elements.

</details>

3. ▢ Write, in words, how to declare an associative array `port` mapping service names to port numbers, populate it with three entries, and print every key alongside its value.

<details markdown="1"><summary>Check</summary>

`declare -A port` first, since an associative array has to be declared before assignment. Then `port[web]=8080`, `port[db]=5432`, `port[cache]=6379`. To print every pair: `for key in "${!port[@]}"; do echo "$key -> ${port[$key]}"; done`, iterating `${!port[@]}` (the keys) and looking each one up in `port` inside the loop.

</details>

4. ▢ A script encodes a list of three related values as `"a:b:c"` and splits it on `:` whenever it's needed. What real risk does this carry that an array wouldn't, and what does lesson 7 call this kind of fragility?

<details markdown="1"><summary>Check</summary>

If any of the three values could ever legitimately contain a `:` itself, the encode/decode step breaks silently, splitting one value into two or merging two into one, with the delimiter choice itself becoming a source of bugs. Lesson 7 names encoding structure into a string, and the fragile decoding it requires, as exactly the kind of text-manipulation-under-strain signal that a script has outgrown shell's judgment-free zone.

</details>

5. ▢ Which claim correctly distinguishes `"${arr[@]}"` from `"${arr[*]}"`?

    - a) They are identical once both are quoted
    - b) `"${arr[@]}"` expands to each element as a separate word, preserving any spaces inside an element; `"${arr[*]}"` joins every element into one string on the first character of `$IFS`
    - c) `${arr[*]}` is the portable POSIX form; `${arr[@]}` is bash-only
    - d) Neither form is affected by quoting; both always split on whitespace regardless

<details markdown="1"><summary>Check</summary>

**b)** That's the exact distinction, and the reason `"${arr[@]}"` is the default choice for iterating elements. (a) is false: quoting is precisely what makes them differ. (c) is false: arrays themselves are bash-only, so neither form has a POSIX equivalent at all. (d) is false: unquoted, both undergo word splitting identically, erasing the distinction; it only exists once both are quoted.

</details>

## Real-world reps

- [ ] Find a script you have access to that encodes a list of values into one delimited string, and rewrite the relevant section using an indexed array instead.
- [ ] Find (or write) a loop iterating over an array without quoting the expansion (`for x in ${arr[@]}`), and confirm what breaks once an element contains a space.
- [ ] Tomorrow: read the primary source's sections on indexed and associative arrays in full, and note one array operation (slicing, negative indices, or removing an element) this lesson didn't cover.

## Going further

- [Docs: "Bash Reference Manual", GNU](https://www.gnu.org/software/bash/manual/bash.html)
- [Site: "Bash Pitfalls", Greg's Wiki](https://mywiki.wooledge.org/BashPitfalls)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
