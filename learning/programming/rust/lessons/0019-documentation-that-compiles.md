---
title: 19. Documentation That Compiles
description: An example in a doc comment is a test, so the documentation that rots is the documentation nobody ran
type: lesson
---

# Lesson 19. Documentation That Compiles

**Mission link:** A public function's doc comment is the only contract most callers ever read, and an example that quietly stopped matching the code six months ago is worse than no example at all, because it still looks trustworthy right up until someone copies it into their own project.
**Primary source:** [Documentation tests](https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html)
**Prerequisites:** [Lesson 14](0014-propagating-errors.md), [Lesson 15](0015-designing-an-error-type.md)

## Warm-up

1. ▢ Lesson 14 showed that `expr?` desugars to a `match` whose `Err` arm does `return Err(From::from(e))`, which only compiles inside a function that itself returns `Result` or `Option`. A doctest's fenced block is compiled as its own tiny program, wrapped in a hidden `fn main`. Given that, what does putting `?` inside a `# Examples` block require from whatever `fn main` rustdoc generates around it?

<details markdown="1"><summary>Check</summary>

That generated `fn main` has to return `Result` or `Option` too, for exactly the reason lesson 14 gave for any function using `?`: there has to be somewhere for the early return to go. Rustdoc's `fn main` returns `()` by default, so an example that calls `?` and stops there fails for the same reason a plain function would. Making that hidden wrapper return the right thing is this lesson's third section.

</details>

2. ▢ Lesson 15 designed `ParseError`'s two variants, `MissingField` and `BadNumber`, from what its callers need to match on, not from the parser's own internals. If a doc example calls `errprobe::parse` and the call can fail two different ways depending on the input, what belongs under an `# Errors` heading so a reader can act without opening the function's body?

<details markdown="1"><summary>Check</summary>

Which variant shows up under which condition: `MissingField` when a field is absent, `BadNumber` when the byte count will not parse. That is the same distinction lesson 15's enum exists to hand a caller, now written down next to the function instead of left for someone to find by reading the `match` arms.

</details>

## Know this

### Two comments, two owners: `///` and `//!`

A `///` comment documents the item written directly below it, a function, a struct, an enum, anything with a name. A `//!` comment documents the item it is written inside, which at the top of a file is the module or crate that file defines rather than anything that follows it. Both forms hold ordinary markdown, and both are just sugar for a `#[doc = "..."]` attribute the compiler attaches to the item.

```rust
//! A tiny crate for reading one field out of a log line.
//!
//! This paragraph documents the crate itself, and lands on the crate's own
//! front page once the documentation is built.

/// Doubles the byte count read from a request line.
pub fn double_bytes(line: &str) -> Result<u64, errprobe::ParseError> {
    let (_path, bytes) = errprobe::parse(line)?;
    Ok(bytes * 2)
}
```

Running `cargo doc --no-deps` on a crate shaped like this puts the `//!` paragraph on the crate's own front page, `target/doc/<crate-name>/index.html`, and the `///` paragraph on that function's own page, `target/doc/<crate-name>/fn.double_bytes.html`, confirmed by checking the generated HTML for each paragraph's text: it shows up on the page named after what it documents, and nowhere else. Get the two forms backwards, a `//!` where a `///` belongs, and the comment attaches to the wrong item or, at the top of a file with nothing above it, to the module itself when you meant it for the first function.

### A doctest is a test, until you break it

`errprobe`'s own `parse` function already carries a fenced ` ```rust ` block under an `# Examples` heading, and `cargo test` treats that block as a test, not as prose:

```text
running 1 test
.
test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.01s

all doctests ran in 0.51s; merged doctests compilation took 0.19s
```

That heading is separate from whatever unit tests the crate has; a doctest passes under the same rule a unit test does, by compiling and running to completion without panicking. The timings on the last line vary from run to run, but the shape does not: a merged compile step, then a pass or fail count. To see the other half, write the same shape of function in a scratch crate and get the expected value wrong on purpose:

```rust
/// Doubles the byte count read from a request line.
///
/// # Examples
///
/// ```
/// let doubled = mylib::double_bytes("/index 1200")?;
/// assert_eq!(doubled, 9999);
/// # Ok::<(), errprobe::ParseError>(())
/// ```
pub fn double_bytes(line: &str) -> Result<u64, errprobe::ParseError> {
    let (_path, bytes) = errprobe::parse(line)?;
    Ok(bytes * 2)
}
```

```text
running 1 test
src/lib.rs - double_bytes (line 5) --- FAILED

failures:

---- src/lib.rs - double_bytes (line 5) stdout ----
Test executable failed (exit status: 101).

stderr:

assertion `left == right` failed
  left: 2400
 right: 9999
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace

failures:
    src/lib.rs - double_bytes (line 5)

test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.01s
```

The panic's own file and line, which named a compiler-generated temporary file rather than anything in the crate, is trimmed above; the part worth reading is `src/lib.rs - double_bytes (line 5) --- FAILED` and the assertion underneath it, which names the exact line in the doc comment that stopped being true. A reader who has only ever seen a doctest pass could reasonably assume the fenced block is decoration; this is what tells them otherwise.

### The hidden line that lets an example use `?`

A line inside a fenced block that starts with `#` is compiled along with the rest of the example but never rendered on the documentation page. `errprobe::parse`'s doctest uses exactly this to close out an example that uses `?`:

```rust
/// let (path, bytes) = errprobe::parse("/index 1200")?;
/// assert_eq!(path, "/index");
/// assert_eq!(bytes, 1200);
/// # Ok::<(), errprobe::ParseError>(())
```

A reader sees three lines; the compiler sees four, and the fourth gives the hidden `fn main` the return type warm-up item 1 said it needed, so `?` on the second line has somewhere to send an early return. Delete that line and keep the `?`, and the diagnostic names precisely the gap it was filling:

```text
error[E0277]: the `?` operator can only be used in a function that returns `Result` or `Option` (or another type that implements `FromResidual`)
 --> src/lib.rs:7:49
  |
6 | fn main() { #[allow(non_snake_case)] fn _doctest_main_src_lib_rs_5_0() {
  |                                      --------------------------------- this function should return `Result` or `Option` to accept `?`
7 | let doubled = mylib::double_bytes("/index 1200")?;
  |                                                 ^ cannot use the `?` operator in a function that returns `()`
  |
help: consider adding return type
```

The compiler's own suggestion is the hidden line itself, spelled out because rustdoc's synthetic `fn main` is visible in this diagnostic in a way it never is in a passing run. The alternative, ending every example with `.unwrap()` instead of `?` so no return type is ever needed, avoids this diagnostic entirely, but lesson 9 only defended `unwrap` for a prototype, a test, or a case already proven impossible; a doc comment is read by every caller who opens the page, and an example that reaches for `unwrap` on every fallible call teaches that habit to all of them at once, which is the opposite of what lesson 9 argued for. Ending with the hidden `Ok::<(), ErrorType>(())` line instead shows the propagate-and-handle shape a caller's own code should use, not the shortcut lesson 9 reserved for narrower cases.

### The sections a caller reads

Four headings recur across the standard library's own documentation, each answering one question a signature alone does not:

- `# Examples`: a runnable demonstration, the one section `cargo test` actually executes.
- `# Errors`: which of a `Result`-returning function's `Err` variants shows up under which condition, named rather than left as "this can fail". `errprobe::parse`'s own doc comment does this already: "Returns [`ParseError::MissingField`] when a field is absent."
- `# Panics`: every way the function can panic, named plainly enough that a caller decides whether to call it at all:

  ```rust
  /// Returns the first character of a request path.
  ///
  /// # Panics
  ///
  /// Panics if `path` is empty, since an empty path has no first character.
  pub fn first_char(path: &str) -> char {
      path.chars().next().unwrap()
  }
  ```

- `# Safety`: the invariants a caller has to uphold for a call to be sound, written once per `unsafe fn`. Stage 7 is where `unsafe` itself arrives, so this lesson only names the heading rather than using it.

None of these four is enforced by the compiler the way a missing `match` arm is; they are conventions the standard library follows consistently enough that opening almost any page under `std::` and finding a `Result`-returning or panicking function will show one. Following them is what lets a reader trust a library's docs the same way they trust the standard library's, without reading either one's source first.

### What `cargo doc` builds, and linking to another item

`cargo doc --no-deps` skips building documentation for the crate's dependencies, and `cargo doc --open` opens the result in a browser once the build finishes, both taken from the flag descriptions `cargo doc --help` prints. The output lands at `target/doc/<crate-name>/index.html`, a path relative to the crate being built rather than anywhere fixed, so the same command produces the same layout regardless of where the project sits.

Writing an item's path in brackets, `` [`double_bytes`] ``, makes rustdoc generate a link to it, resolved against the crate's own item names rather than typed out as a URL:

```rust
/// Returns the first character of a request path, alongside
/// [`double_bytes`] for the count on the same line.
pub fn first_char(path: &str) -> char {
    path.chars().next().unwrap()
}
```

The generated page carries `<a href="fn.double_bytes.html" ...>` in place of the bracketed text, confirmed by inspecting the built HTML, and this resolves even under `--no-deps` for an item in the same crate. Point the same syntax at a name that does not exist, and the build still finishes, but with a warning:

```text
warning: unresolved link to `Nonexistent`
  --> src/lib.rs:48:11
   |
48 | /// See [`Nonexistent`] for details.
   |           ^^^^^^^^^^^ no item named `Nonexistent` in scope
   |
   = note: `#[warn(rustdoc::broken_intra_doc_links)]` on by default
```

That lint is `broken_intra_doc_links`, and it warns by default, which is why a rename that breaks a doc link shows up in the build output instead of silently shipping a dead link on the page.

### Enforcing documentation, and what earns it

`#![warn(missing_docs)]` at the crate root turns an undocumented public item into a build-time warning instead of a silent gap:

```text
warning: missing documentation for a function
  --> src/lib.rs:46:1
   |
46 | pub fn undocumented_probe() {}
   |
note: the lint level is defined here
  --> src/lib.rs:7:9
   |
 7 | #![warn(missing_docs)]
```

The honest limit is right there in what the lint checks: presence, not usefulness. A one-word `///` comment satisfies `missing_docs` exactly as well as a full `# Examples` and `# Errors` block does, so passing this lint is a floor, not a finish line. What is worth the effort above that floor is the public API and the invariants a caller cannot see from the signature alone, which field can be missing and why, what input makes a function panic, what each `Err` variant means; what is not worth it is narrating the body's mechanics line by line, or a comment that only restates the signature, such as `/// Returns a u64.` on a function whose return type already says so. One more limit is worth knowing here: a doctest on a private item still runs under `cargo test`, since visibility has no bearing on whether the compiler executes it, but `cargo doc` never renders a private item's page without `--document-private-items`, so an elaborate example on a helper nobody outside the crate can call is a test with no reader, useful for the former but not the latter.

## Practice

1. ▢ A function returning `Result<u64, errprobe::ParseError>` has a doc example ending in `?` but no hidden line after it. Predict whether `cargo test` compiles this example, and if not, predict the error code.

<details markdown="1"><summary>Check</summary>

It fails to compile, with `E0277`, because the example's `?` needs the hidden `fn main` around it to return `Result` or `Option`, and with no hidden line supplying that, it stays `()`. The fix is the line this lesson keeps ending examples with, `# Ok::<(), errprobe::ParseError>(())`.

</details>

2. ▢ A crate root has `#![warn(missing_docs)]`, and one `pub fn` in it has no doc comment at all. Predict what `cargo doc` reports, then add the attribute and an undocumented function to a scratch crate to check.

<details markdown="1"><summary>Hint</summary>

The lint checks presence only, so think about what it can and cannot know about a function it has never seen a doc comment on.

</details>

<details markdown="1"><summary>Check</summary>

A warning, missing documentation for a function, pointing at the function's own line, with a note showing where the `#![warn(missing_docs)]` attribute set that lint level. Nothing about the warning depends on what the function does; an empty `///` line above it would satisfy the lint just as completely as a full write-up would.

</details>

3. ▢ A passing `# Examples` block asserts `assert_eq!(doubled, 2400)`. Predict what changes in `cargo test`'s output if that literal is changed to a wrong value, then compile both versions.

<details markdown="1"><summary>Check</summary>

The doctest's own heading, `src/lib.rs - double_bytes (line N) --- FAILED`, replaces the single `.` a passing run prints, followed by the assertion's own `left` and `right` values under a `stderr:` heading. Nothing about the surrounding unit tests changes; only the doctest's own line in the report does.

</details>

4. ▢ One doc comment reads `` /// See [`Nonexistent`] for details. `` where no item named `Nonexistent` exists in the crate. Predict whether `cargo doc` still finishes building, and name the lint behind whatever it reports.

<details markdown="1"><summary>Hint</summary>

Compare this to a missing trait implementation lesson 14 covered: does a failed link stop the build the way a failed `?` conversion stops compilation, or does it behave more like a warning?

</details>

<details markdown="1"><summary>Check</summary>

The build finishes; `broken_intra_doc_links` only warns by default; it does not fail the build. The warning names the unresolved item directly, `no item named` `Nonexistent` `in scope`, at the exact bracketed text that failed to resolve.

</details>

5. ▢ A private helper function, never `pub`, has the same `# Examples` doctest style as a public sibling. Predict whether `cargo test` runs its doctest, and whether `cargo doc --no-deps` shows that function's page to anyone reading the crate's documentation.

<details markdown="1"><summary>Check</summary>

`cargo test` runs it: doctest collection does not check visibility, only that the item has a doc comment with a fenced example. `cargo doc --no-deps` does not render it, since private items are left out of the generated pages unless the build is run with `--document-private-items`. The doctest still verifies the code works; it just never reaches a caller who could act on what it demonstrates.

</details>

## Real-world reps

- [ ] Add an `# Examples` section to every public function in your `logsum` library, including an `# Errors` section on each one that returns `Result`, and make sure at least one example ends with the hidden `Ok::<(), YourErrorType>(())` line so it can use `?` the way a caller's own code would.
- [ ] Add `#![warn(missing_docs)]` to your library's crate root, run `cargo doc --no-deps`, and fix every warning it reports before moving on.
- [ ] Tomorrow: run `cargo test` on your `logsum` library and read the doctest section of the output on its own; if every example still passes, delete one assertion's expected value on purpose, rerun, and read what the failure names before putting it back.

## Going further

- [How to write documentation](https://doc.rust-lang.org/rustdoc/how-to-write-documentation.html): the fuller structure rustdoc recommends for an item's documentation, examples included
- [Comments](https://doc.rust-lang.org/reference/comments.html): the language-level rule for `///`, `//!`, and the block forms, and exactly what item each one attaches to
- [Linking to items by name](https://doc.rust-lang.org/rustdoc/write-documentation/linking-to-items-by-name.html): the full intra-doc link syntax, including linking to a specific method or trait implementation
- [E0277](https://doc.rust-lang.org/error_codes/E0277.html): the trait-not-implemented diagnostic, also behind a missing return type on an example that uses `?`
- [Errors and API shape](../reference/errors-and-api-shape.md): the stage 3 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
