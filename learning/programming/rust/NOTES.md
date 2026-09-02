# Rust Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- **Lessons are written for a general reader, deliberately.** No machine, OS, editor or installed version appears in any lesson, reference sheet, `README.md` or `RESOURCES.md`. Requested explicitly; do not personalise the lesson material to whoever is running the session.
- Mission is the full arc: zero to senior specialist, assuming no prior Rust and no systems-programming background. Start at stage 1 rather than calibrating against a particular reader.
- Skill-heavy topic, and the compiler is the answer key. Every early lesson should have a "predict what the compiler says, then compile" rep, because that is the only way the borrow rules stop feeling arbitrary.
- Reps must fit one sitting.

## State

Stages 1 and 2 are written: lessons 0001 to 0013, plus three reference sheets, `ownership-and-borrowing.md`, `the-project.md` and `data-and-control.md`. Stages 3 to 8 are unwritten.

**Baseline, rechecked before stage 2: rustc 1.98.0, edition 2024.** The toolchain was two releases behind when the stage started and was updated first. Recheck again before stage 3 rather than assuming this still holds.

Lesson 0006 is the stage's capstone and the piece worth protecting. It teaches reading the compiler's three spans, the five error codes stage 1 actually produces, and the four honest fixes against the four workarounds. It is the direct answer to the stage's success criterion, and it is also where the "what not to do here" rule below is made explicit for a reader rather than kept as a note.

**How the glossary is populated here.** The skill's test, that a term lands once it can be used correctly, is about a learner's demonstration. These lessons have no single learner, so the test is applied to the material: a term lands when a lesson has taught it well enough for a reader to use it. Stage 1 added eight terms alongside the four pinned ones. Keep doing this per stage, and do not add a term the lessons have not earned.

## The rep project, settled

**Resolved before stage 2, and published as `reference/the-project.md`.** The open thread asked for a crate that grows across the arc, and named a command-line tool as the obvious candidate because it needs no framework. That instinct was right; what needed deciding was which tool, and the decision was made by building the stage 2 slice and running it.

**The project is a line-oriented log summariser**: it reads records from a text stream, models each line as an enum, rejects the malformed ones, and reports a summary. Verified on the current stable toolchain, rustc 1.98.0 with edition 2024, with **no dependencies at all**: the prototype parses a seven-line input into 3 requests, 1 note, 1 blank and 2 rejected lines, totals 2000 bytes for `/index` and 90 for `/login`, and names the busiest path. That matters because stage 2 has no vocabulary for adding a dependency, so a project that needs one before stage 3 would have to be introduced twice.

Why this one rather than the other obvious candidates, argued from what each stage needs:

- **Its core model wants an enum with payloads**, which is stage 2's own done-when clause: a line is a request, a note, or blank, and the parse either produces one or fails. A word-count clone has nothing worth modelling as an enum; a to-do application needs serialisation, which means a dependency, before stage 3.
- **Its failure surface is genuinely `Option` and `Result`**, not a contrivance: a field can be missing and a number can fail to parse, so `ok_or`, `map_err` and `?` all appear because the problem needs them.
- **It is iterator-shaped and needs a map**, which covers the rest of stage 2 without inventing exercises.
- **Every later stage has a real hook.** Stage 3 splits it into a library and a binary and gives it a proper error type, which the prototype's `ParseError` with its `Display` implementation already gestures at. Stage 4 generalises the input source behind a trait and takes borrowed lines rather than owned strings. Stage 5 parallelises across files with threads and channels. Stage 6 reads from many sources with async I/O. Stage 7 measures the per-line allocation cost and only then considers a faster path. Stage 8 publishes it, versions its public API, and reviews it.

The reps grow it a piece at a time, one per lesson, so no lesson asks for a build that does not fit a sitting. The sheet records what state the project should be in at the end of each stage, so a reader who skipped a rep knows what to catch up on.

## What execution changed

### Stage 2

All compiled on **rustc 1.98.0, edition 2024**, which is what `cargo new` now produces.

- **The recheck mattered before a single lesson was written.** The toolchain here was 1.96.1 and the current stable was 1.98.0, two releases behind, so it was updated first. This workspace's version policy says to check the release announcement rather than recall a feature's release, and this is the stage where that stopped being theoretical.
- **Two edition-2024 changes land squarely in stage 2's material, and both were verified by compiling the same code on both editions.** Let chains, `if let Some(x) = a && let Some(y) = b`, compile on 2024 and fail on 2021 with `error: let chains are only allowed in Rust 2024 or later`, pointing at each `let`; they stabilised in release 1.88. And an explicit `&` pattern may no longer be mixed with an implicit borrow: `map.iter().max_by_key(|(_, &b)| b)` compiles on 2021 and fails on 2024 with `error: cannot explicitly dereference within an implicitly-borrowing pattern`, with a note that a non-reference pattern on a reference type implicitly borrows and a help suggesting `|&(_, &b)| b`. Because `cargo new` defaults to 2024, a reader copying either shape from an older post hits it immediately, which is why lesson 0011 leads with binding modes rather than filing them under advanced.
- **My spec's `E0503` claim was too general, and lesson 0012's author found the boundary.** Reading a local that a closure has mutably borrowed, before the iterator chain is consumed, gives `E0503` when the local is `Copy`, which is what my own `i32` probe produced, and `E0502` when it is not, because reading a `Vec` through `println!` is itself a new borrow. Both were compiled. The lesson teaches the one its own example produces and names it as lesson 3's rule arriving in a new place.
- **The sizes are verified and the promises are separated from the numbers.** On this target `Option<&u8>` and `&u8` are both 8, `Option<Box<u8>>` is 8, `Option<&str>` and `&str` are both 16, `Option<u8>` is 2, a two-`f64` variant enum is 24, and the project's `Line` enum is 40, exactly the size of a bare struct holding the same three fields, because the discriminant fits in the padding after a `u16`. The niche cases are documented guarantees; the rest are this target's numbers and the lessons say so.
- **Iterator laziness is proven rather than asserted**: a `map` whose closure pushes to a log leaves the log empty when the chain is dropped unconsumed and full when it is collected.
- **Two lesson authors were killed mid-run by a session limit, and the two failure modes need different handling.** Lessons 0008 and 0009 had been written before their authors died, so every quoted diagnostic and size in them was re-verified centrally: `E0061`, both `E0382`s, `E0308`, `E0507` with its `consider cloning` help, and all six size claims reproduce byte for byte. Lessons 0011 and 0012 had not been written, so they were redone from scratch rather than salvaged from their scratch files. The rule worth carrying: a lesson whose author dies after writing needs central verification, and one whose author dies before writing needs a fresh run.
- **The audit found one real defect in the interrupted work and two attribution slips.** Lesson 0009's panic transcripts omitted the thread identifier this release prints, while lesson 0010 included it and explained that it varies per run; 0009 now matches the compiler and carries the same explanation. Lesson 0010 attributed a plain `for` and `match` loop to lesson 0012, which owns iterator chains rather than control flow, and now says so. Nothing else in the seven lessons contradicted anything else, and the sheet writer reproduced every diagnostic, size, edition split and output independently.
- **Both standing rules held.** No lesson reaches for `Rc`, `RefCell`, `Arc`, `Mutex` or a thread, confirmed by grep, and the one borrow-checker-adjacent moment, the compiler suggesting `.clone()` for `E0507` in lesson 0009, is explicitly named as the wrong fix with `Option::take` given as the design.
- **One gate-4 limitation, recorded because it will recur.** `fasterthanli.me`, a pre-existing entry in `RESOURCES.md` rather than anything stage 2 cited, answers 200 and then stalls the body for an automated client: a `curl` gets the status and about nineteen kilobytes before timing out at ninety seconds. It is a live page, not a dead link, and the same category as the vendor hosts that answer a scripted request with a 403. All sixty links this stage touched were checked, and that is the only one that needed a manual look.
- **`RESOURCES.md` needed nothing.** Stage 2 cited the Book, the standard library, the Reference, the error index and the release blog, all already listed, and the gaps section already records that release notes are read from the blog. Recording that as a non-change rather than inventing an entry.

## On the arc

Eight stages, which is more than the other workspaces here, and the reason is that Rust has three separate hard walls rather than one: ownership in stage 1, lifetimes and traits in stage 4, and async in stage 6. Compressing any of them produces a reader who copies patterns.

Two boundaries worth revisiting once lessons exist:

- Stage 5 and stage 6 could merge into one concurrency stage. They stay apart because sharing across threads is understandable from ownership alone, and async is a separate model layered on top.
- Stage 7 pairs `unsafe` with performance. The link is real, since most `unsafe` in application code is written for speed that was never measured, and the pairing is meant to make that visible. If it reads as two topics, it splits.

## What not to do here

- Do not teach a fight with the borrow checker as a set of workarounds. `clone`, `Rc<RefCell<_>>` and lifetime annotations all make an error go away, and a lesson that reaches for one without saying what the design should have been teaches the wrong habit permanently.
- Do not reach `unsafe` before stage 7. The Rustonomicon is listed for that stage only, and quoting it earlier makes the safe subset look optional.

## Version policy

The arc names no Rust version. Where a lesson depends on an edition or a stabilised feature, it says which, and checks the release announcement rather than recalling it. Async and trait features move fastest, so a claim that something "cannot be expressed" dates quickly.

## Open threads

- Resolved: the rep project is the log summariser in `reference/the-project.md`. See "The rep project, settled" above.
- Cancellation safety in async is under-sourced. Stage 6 may be the first place the session has to do real source-finding work rather than teaching.
- Variance and higher-ranked trait bounds are unplaced. Currently implied by stage 4, but they may deserve their own late lesson, closer to stage 8, where API design makes them matter.
- Comparisons to other workspaces are tempting here, particularly ownership against garbage collection and async against goroutines. Keep them as pointers to a glossary term in the other workspace rather than importing its material.
