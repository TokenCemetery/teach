---
title: 28. Reading a Lifetime Error
description: The shapes a lifetime error takes, each with the honest fix and the workaround it tempts you into
type: lesson
---

# Lesson 28. Reading a Lifetime Error

**Mission link:** Every lifetime error this stage produces reduces to one of five shapes, and an engineer who has not sorted them reaches for `.clone()` or `'static` on reflex instead of reading what the compiler actually said.
**Primary source:** [Rust error codes index](https://doc.rust-lang.org/error_codes/error-index.html)
**Prerequisites:** [Lesson 26](0026-lifetimes-are-not-durations.md), [Lesson 27](0027-types-that-borrow.md)

## Warm-up

1. ▢ Lesson 26 said a lifetime is a constraint the compiler checks, not a duration it extends. Given `fn first<'a>(s: &'a str) -> &'a str`, does writing `'a` make the returned borrow live any longer than it otherwise would?

<details markdown="1"><summary>Check</summary>

No. The annotation adds no runtime behaviour; it only states a relationship that was already true, that whatever `first` returns borrows from the same place `s` does, so the compiler can check callers against it.

</details>

2. ▢ Lesson 27 distinguished a struct that owns its fields from one that borrows them. Why does a `&'a str` field turn every method touching it into a question the compiler must answer, when an owned `String` field never does?

<details markdown="1"><summary>Check</summary>

An owned field makes the struct responsible for the value, so no method needs to say how long anything lives beyond the struct's own lifetime. A borrowed field stands in for a value someone else owns, so every method touching it must satisfy the compiler that the borrow outlives the field's declared lifetime, the promise this lesson's second shape breaks.

</details>

## Know this

### E0106: the signature has not said where the return borrows from

The most common shape is a return type that borrows without saying from where:

```rust
fn longest(a: &str, b: &str) -> &str {
    if a.len() > b.len() { a } else { b }
}
```

```text
error[E0106]: missing lifetime specifier
 --> src/main.rs:1:33
  |
1 | fn longest(a: &str, b: &str) -> &str {
  |               ----     ----     ^ expected named lifetime parameter
  |
  = help: this function's return type contains a borrowed value, but the signature does not say whether it is borrowed from `a` or `b`
help: consider introducing a named lifetime parameter
  |
1 | fn longest<'a>(a: &'a str, b: &'a str) -> &'a str {
  |           ++++     ++          ++          ++
```

The `help` line carries the lesson: the function can return either `a` or `b` at runtime, so the compiler has no single input to copy the lifetime from. The honest fix names the relationship, adding `<'a>` to both parameters and the return type. The workaround, an owned `String`, removes the question instead of answering it, correct when an independent value is genuinely wanted, a habit otherwise.

### E0621: a borrowing type's method has to repeat its own promise

A struct that borrows carries its lifetime as a type parameter, and that parameter is not assumed automatically by every reference that touches the field:

```rust
struct Holder<'a> {
    seen: Vec<&'a str>,
}

impl<'a> Holder<'a> {
    fn keep(&mut self, s: &str) {
        self.seen.push(s);
    }
}
```

```text
error[E0621]: explicit lifetime required in the type of `s`
 --> src/main.rs:7:9
  |
7 |         self.seen.push(s);
  |         ^^^^^^^^^^^^^^^^^ lifetime `'a` required
  |
help: add explicit lifetime `'a` to the type of `s`
  |
6 |     fn keep(&mut self, s: &'a str) {
  |                            ++
```

`s` arrives with some anonymous lifetime, and pushing it into `self.seen` demands it live as long as `'a`, which nothing in `keep`'s signature claims. The honest fix is exactly the `help`: write `s: &'a str`, repeating the struct's promise on the method that needs it. The workaround is cloning `s` into an owned `String` before storing it, correct once `Holder` is meant to own what it collects, a quiet redesign otherwise.

### Returning a reference to a local: the value dies with the function

A function that borrows nothing on its way in has nothing to borrow on its way out:

```rust
fn make() -> &str {
    let s = String::from("hi");
    &s
}
```

```text
error[E0106]: missing lifetime specifier
 --> src/main.rs:1:14
  |
1 | fn make() -> &str {
  |              ^ expected named lifetime parameter
  |
  = help: this function's return type contains a borrowed value, but there is no value for it to be borrowed from
help: consider using the `'static` lifetime, but this is uncommon unless you're returning a borrowed value from a `const` or a `static`
  |
1 | fn make() -> &'static str {
  |               +++++++
help: instead, you are more likely to want to return an owned value
  |
1 - fn make() -> &str {
1 + fn make() -> String {
  |
```

Naming a lifetime explicitly moves the failure rather than removing it: `fn make<'a>() -> &'a str` compiles the signature, then fails in the body, `` E0515: cannot return reference to local variable `s` ``, since `s` is dropped at the end of `make` regardless of the signature. The honest fix is one of rustc's own two suggestions above: return the owned `String`, or take the destination as a `&mut` parameter to write into. The workaround is leaking it:

```rust
fn make() -> &'static str {
    let s = String::from("hi");
    Box::leak(s.into_boxed_str())
}
```

This compiles and runs, costing exactly what it looks like: the allocation is never freed, a fair trade for a handful of values computed once at start-up, a slow leak otherwise.

### E0597 when an annotation elsewhere made the demand

The clearest information is not always under the caret. A `Vec` annotated to hold `&'static str` pins every element to that lifetime before a single value goes in:

```rust
fn main() {
    let mut v: Vec<&'static str> = Vec::new();
    let owned = String::from("hi");
    v.push(&owned);
}
```

```text
error[E0597]: `owned` does not live long enough
 --> src/main.rs:4:12
  |
2 |     let mut v: Vec<&'static str> = Vec::new();
  |                ----------------- type annotation requires that `owned` is borrowed for `'static`
3 |     let owned = String::from("hi");
  |         ----- binding `owned` declared here
4 |     v.push(&owned);
  |            ^^^^^^ borrowed value does not live long enough
5 |     println!("{v:?}");
6 | }
  | - `owned` dropped here while still borrowed
```

The underlined span is `&owned`, but the accusation sits two lines above, `` type annotation requires that `owned` is borrowed for `'static` ``. Nothing about `v`'s declaration looks wrong alone, and a reader who reads only the caret looks for a bug in `push` that is not there. The honest fix stops pinning the element type to `'static`: `Vec<&str>` with no annotation infers the shortest lifetime every pushed element satisfies. The workaround is making `owned` satisfy the annotation, either a `'static` literal, which only works for whole-program data, or cloning every value pushed, paying `.clone()` per push instead of once at the signature.

### The higher-ranked wall, which has no error code

A bound such as `F: Fn(&str) -> usize` asks for a closure that works for every lifetime a caller might supply, a higher-ranked bound, not one particular borrow. A closure pinned to one lifetime fails it, with no error code at all:

```rust
fn call_it<F: Fn(&str) -> usize>(f: F) -> usize {
    f("hi")
}

fn main() {
    let closure = |s: &'static str| s.len();
    let r = call_it(closure);
    println!("{r}");
}
```

```text
error: implementation of `Fn` is not general enough
 --> src/main.rs:7:13
  |
7 |     let r = call_it(closure);
  |             ^^^^^^^^^^^^^^^^ implementation of `Fn` is not general enough
  |
  = note: closure with signature `fn(&'2 str) -> usize` must implement `Fn<(&'1 str,)>`, for any lifetime `'1`...
  = note: ...but it actually implements `Fn<(&'2 str,)>`, for some specific lifetime `'2`
```

The same pair repeats for `FnOnce`, trimmed here as it says nothing new. "For any lifetime `'1`" is what `call_it` asked for; "for some specific lifetime `'2`" is what the closure offers, one fixed lifetime rather than every one. The honest fix removes the annotation and lets `|s: &str| s.len()` infer: the body never needed `'static`, only the explicit type did.

A second failure in the same family looks unrelated until the note is read: a closure returning a borrow of something it captured, checked against the same kind of bound:

```rust
fn call_it2<F: Fn(&str) -> &str>(f: F) {
    let r = f("hi");
    println!("{r}");
}

fn main() {
    let owned = String::from("hello");
    call_it2(|_s: &str| &owned);
}
```

```text
error[E0597]: `owned` does not live long enough
 --> src/main.rs:8:26
  |
7 |     let owned = String::from("hello");
  |         ----- binding `owned` declared here
8 |     call_it2(|_s: &str| &owned);
  |              ---------- -^^^^^
  |              |          ||
  |              |          |borrowed value does not live long enough
  |              |          returning this value requires that `owned` is borrowed for `'static`
  |              value captured here
9 | }
  | - `owned` dropped here while still borrowed
```

This time the code is `E0597`, but the wall is the same: `Fn(&str) -> &str` promises a return borrowed from the argument for any lifetime, and a closure returning a borrow of its own captured `owned` can only offer one specific lifetime, exactly what the note states. The honest fix stops returning a borrow of a capture: take the value from the argument, or return an owned `String` and clone. Writing the quantifier out explicitly answers both failures; it is a later stage's tool, so it stops here at its name, a higher-ranked bound.

### Reading the vocabulary, and the four workarounds

Three pieces of notation carry information once you know what they mean. `'1` and `'2` are the compiler's own names for lifetimes the source never named; seeing them signals that the lifetimes in conflict are anonymous, not that anything is broken. `'_` is the same idea written by hand, a way to say a lifetime exists without naming it, which an opt-in lint suggests when an elided lifetime should be spelled out:

```text
error: hidden lifetime parameters in types are deprecated
 --> src/main.rs:5:11
  |
5 | fn bar(f: Foo) {
  |           ^^^ expected lifetime parameter
  |
help: indicate the anonymous lifetime
  |
5 | fn bar(f: Foo<'_>) {
  |              ++++
```

Every `E0597` above also carries three spans worth telling apart: where the value was declared (`` binding `owned` declared here ``), where a borrow of it outlives it (`borrowed value does not live long enough`), and where it is dropped (`` `owned` dropped here while still borrowed ``). The first two say what conflicts; the third says when it becomes real, usually the end of the smallest enclosing scope rather than a suspicious line.

The four workarounds in this stage are stage 1's four, aimed at a lifetime instead of a borrow:

| Workaround | What it actually costs |
|---|---|
| Adding `'static` | Legitimate only for data that already lives for the whole program, such as a literal; elsewhere it is a promise the value cannot keep, which starts a search for how to make it true, usually leaking or cloning |
| `.clone()` or `.to_owned()` | An allocation and a second, independent value, correct when the two are meant to diverge and a reflex when they are not |
| Leaking | Memory never freed for the program's life, acceptable for a handful of values computed once and never again, a slow leak otherwise |
| A shared-ownership type | Turns a compile-time question into a runtime-managed one; the sharing stage owns when that call is right, and reaching for it here to silence an error is the wrong reason |

Each one compiles. None answers what the compiler actually asked, how long the value needs to live and who is responsible for it; the honest fixes above answer that, and the workarounds change the subject.

## Practice

1. ▢ Predict the error code and the `help`, then compile it.

   ```rust
   fn pick(a: &str, b: &str, first: bool) -> &str {
       if first { a } else { b }
   }
   ```

<details markdown="1"><summary>Check</summary>

The error is `E0106`. The `help` says the return type is borrowed but not whether from `a` or `b`, the same shape as `longest`; the honest fix names a lifetime shared by both parameters and the return type.

</details>

2. ▢ This struct means to borrow the lines it is told to keep. Predict the code, then fix it without cloning.

   ```rust
   struct Recent<'a> {
       lines: Vec<&'a str>,
   }

   impl<'a> Recent<'a> {
       fn note(&mut self, line: &str) {
           self.lines.push(line);
       }
   }
   ```

<details markdown="1"><summary>Hint</summary>

Compare `note`'s parameter with `keep`'s parameter above.

</details>

<details markdown="1"><summary>Check</summary>

The error is `E0621`, the same reason as `Holder::keep`. Change `line: &str` to `line: &'a str`, since `note` only ever accepts a borrow that already outlives the struct.

</details>

3. ▢ Compile this as written, then add `<'a>` to the signature and compile again. Predict the code both times.

   ```rust
   fn wrap() -> &str {
       let owned = String::from("wrapped");
       &owned
   }
   ```

<details markdown="1"><summary>Hint</summary>

The first version has no lifetime in its signature to fail against; the second one does.

</details>

<details markdown="1"><summary>Check</summary>

As written, the error is `E0106`, since the return type borrows nothing the compiler was given. With `fn wrap<'a>() -> &'a str`, the signature compiles and the body fails instead, `` E0515, cannot return reference to local variable `owned` ``, since `owned` is dropped at the end of the function regardless.

</details>

4. ▢ Predict which line the compiler blames, and why it is not the `push`.

   ```rust
   fn main() {
       let mut tags: Vec<&'static str> = Vec::new();
       let label = String::from("draft");
       tags.push(&label);
   }
   ```

<details markdown="1"><summary>Check</summary>

The error is `` E0597, `label` does not live long enough ``, and the accusation lands on `let mut tags: Vec<&'static str>`, quoted back as `` type annotation requires that `label` is borrowed for `'static` ``. The `push` is where the conflict surfaces; the annotation is where it was created.

</details>

5. ▢ Why does removing the explicit `&'static str` from this closure's parameter make it compile?

   ```rust
   fn call_it<F: Fn(&str) -> usize>(f: F) -> usize {
       f("hi")
   }

   fn main() {
       println!("{}", call_it(|s: &'static str| s.len()));
   }
   ```

<details markdown="1"><summary>Hint</summary>

`F: Fn(&str) -> usize` is a promise about every lifetime, not one.

</details>

<details markdown="1"><summary>Check</summary>

The bound is higher-ranked: the closure must work for any lifetime, not only `'static`. Annotating the parameter `&'static str` fixes it to one lifetime, failing with `` error: implementation of `Fn` is not general enough ``. Leaving it inferred, `|s: &str| s.len()`, keeps the closure general enough to match.

</details>

## Real-world reps

- [ ] Change your project's summariser to take `impl Iterator<Item = &'a str>` instead of one concrete input type, and store borrowed lines instead of owned copies; classify each lifetime error you meet by the five shapes above before fixing it.
- [ ] Add a method to a struct that already borrows, one that takes a reference without repeating the struct's own lifetime; predict `E0621` before compiling, then decide whether the honest fix or a clone is right for that field.
- [ ] Tomorrow: find one `'static` or `.clone()` already silencing a lifetime error in your code, remove it, read the diagnostic underneath, and write one sentence saying which of the five shapes it was.

## Going further

- [Rust error codes index](https://doc.rust-lang.org/error_codes/error-index.html): every code with a minimal reproduction
- [Error code E0106](https://doc.rust-lang.org/error_codes/E0106.html), [Error code E0515](https://doc.rust-lang.org/error_codes/E0515.html): a missing lifetime specifier, and returning a value the function owns
- [Error code E0621](https://doc.rust-lang.org/error_codes/E0621.html): a borrow needing a lifetime already declared elsewhere
- [Error code E0597](https://doc.rust-lang.org/error_codes/E0597.html): a borrowed value that does not live long enough
- [Trait and lifetime bounds](https://doc.rust-lang.org/reference/trait-bounds.html#higher-ranked-trait-bounds): the explicit bound named here but left for later
- [Traits and lifetimes](../reference/traits-and-lifetimes.md): the stage 4 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
