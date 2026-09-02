---
title: 26. Lifetimes Are Not Durations
description: What a lifetime parameter says about the relation between borrows, and what elision had been doing for you all along
type: lesson
---

# Lesson 26. Lifetimes Are Not Durations

**Mission link:** Most engineers meet a lifetime error and reach for `'static` or a fresh `<'a>` like a light switch, hoping something turns on; that only produces a second, worse error, because a lifetime annotation is not a control you pull, it is a claim the compiler checks.
**Primary source:** [Validating References with Lifetimes](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html#validating-references-with-lifetimes)
**Prerequisites:** [Lesson 3](0003-borrowing.md), [Lesson 6](0006-reading-a-borrow-error.md)

## Warm-up

1. ▢ Lesson 3's rule was one sentence: any number of shared borrows or one mutable borrow, never both, and every borrow must stay valid for as long as it is used. Which half does this lesson pick up, the aliasing half or the "valid for as long as it is used" half?

<details markdown="1"><summary>Check</summary>

The second half. Stage 1's examples all lived inside one function body, where the compiler can just watch a borrow's last use. A lifetime parameter carries that same promise across a function boundary, where the caller and the callee each know only their own half of the story.

</details>

2. ▢ Lesson 6 named two codes as stage 4's material without teaching them, in one sentence. Which codes, and what did that sentence say?

<details markdown="1"><summary>Check</summary>

`E0106`, a missing lifetime specifier, and `E0597`, a value that does not live long enough. Lesson 6 said both mean "the compiler cannot work out how long a reference is meant to be valid." This lesson takes that sentence apart: one code needs your help, the other means you already lost.

</details>

## Know this

### A lifetime parameter is a relation, never a duration

The glossary already says this precisely: a lifetime is a constraint the compiler checks, not a duration it measures, and annotating one relates the lifetimes of inputs and outputs without ever making a value live longer. That claim is worth testing, not trusting, so break a program on purpose and "fix" it with an annotation:

```rust
fn borrow(x: &i32) -> &i32 {
    x
}

fn main() {
    let r;
    {
        let x = 5;
        r = borrow(&x);
    }
    println!("r: {r}");
}
```

`x` is dropped at the end of the inner block while `r` still borrows it, so this fails:

```text
error[E0597]: `x` does not live long enough
  --> src/main.rs:9:20
   |
 8 |         let x = 5;
   |             - binding `x` declared here
 9 |         r = borrow(&x);
   |                    ^^ borrowed value does not live long enough
10 |     }
   |     - `x` dropped here while still borrowed
11 |     println!("r: {r}");
   |                   - borrow later used here
```

`borrow`'s signature is already elided down to the one honest relation it could have: the return borrows from `x`. Write that relation out explicitly instead of leaving it elided:

```rust
fn borrow<'a>(x: &'a i32) -> &'a i32 {
    x
}
```

Recompiling the identical `main` produces the identical diagnostic, same line, same span. The annotation added no information the compiler lacked, since elision had already inferred this relation; spelling it out cannot extend `x`'s scope, because a lifetime parameter never had that power. The only change that compiles is changing where `x` lives:

```rust
fn main() {
    let x = 5;
    let r;
    {
        r = borrow(&x);
    }
    println!("r: {r}");
}
```

`x` now outlives its only borrow, the signature is back to whichever form you like, and the fix was never in the angle brackets.

### `E0106`: the question elision cannot answer alone

Lesson 6 filed this away as stage 4's business; here is the case that produces it, two candidate strings and no hint which one the return relates to:

```rust
fn longest(x: &str, y: &str) -> &str {
    if x.len() > y.len() { x } else { y }
}
```

```text
error[E0106]: missing lifetime specifier
 --> src/main.rs:1:33
  |
1 | fn longest(x: &str, y: &str) -> &str {
  |               ----     ----     ^ expected named lifetime parameter
  |
  = help: this function's return type contains a borrowed value, but the signature does not say whether it is borrowed from `x` or `y`
help: consider introducing a named lifetime parameter
  |
1 | fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
  |           ++++     ++          ++          ++
```

That `help` line is the whole lesson: the compiler is not confused about how long anything lives, it is stuck on identity, borrowed from `x` or `y`, which only you can answer since the body's branches differ at every call. Naming `'a` answers it by claiming both parameters share a lifetime, so the return can claim it too:

```rust
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```

This compiles for any two calls, even from wildly different scopes, because `'a` is not a fixed span. At each call site the compiler substitutes the overlap of whatever `x` and `y` live for, then checks the return against it. The signature states a relation the caller supplies; it never dictates a duration.

### The three elision rules, from the Reference

Elision is the Reference's own rules for inferring what you would otherwise write; every signature you have used since stage 1 already applied one of them.

Rule one: "each elided lifetime in the parameters becomes a distinct lifetime parameter." Lesson 14's `fn read_record_a(count: &str, line: &str) -> Result<(i32, String), String>` needs no more: `count` and `line` get independent lifetimes, unforced to match, since the return borrows from neither.

Rule two: "if there is exactly one lifetime used in the parameters (elided or not), that lifetime is assigned to all elided output lifetimes." Lesson 20's `fn split_fields(line: &str) -> Result<(&str, &str, &str), LineError>` applies it three times over: with only one input lifetime available, every slice in the returned tuple is assigned `line`'s lifetime, since none can point anywhere else.

Rule three applies only to methods: "if the receiver has type `&Self` or `&mut Self`, then the lifetime of that reference to `Self` is assigned to all elided output lifetime parameters." Lesson 6 already had you read `fn name(&self) -> &str` in passing; this rule desugars it to `fn name<'s>(&'s self) -> &'s str`. That choice is usually right, but it is a choice, not a law, and worth seeing fail:

```rust
struct Cache {
    note: String,
}

impl Cache {
    fn note_or(&self, fallback: &str) -> &str {
        fallback
    }
}
```

Elision assigns the output to `self`'s lifetime, so the compiler expects a return borrowed from `self`. The body returns `fallback` instead, borrowed from an entirely different, unnamed lifetime, and the mismatch is real:

```text
error: lifetime may not live long enough
 --> src/main.rs:5:9
  |
4 |     fn note_or(&self, fallback: &str) -> &str {
  |                -                - let's call the lifetime of this reference `'1`
  |                |
  |                let's call the lifetime of this reference `'2`
5 |         fallback
  |         ^^^^^^^^ method was supposed to return data with lifetime `'2` but it is returning data with lifetime `'1`
  |
help: consider introducing a named lifetime parameter and update trait if needed
  |
4 |     fn note_or<'a>(&self, fallback: &'a str) -> &'a str {
  |               ++++                   ++          ++
```

Returning `&self.note` instead compiles without any annotation at all, because that is the one relation rule three already promised.

### Reading `'a` in a signature you did not write

Once you can read a rule, you can read it in code you never wrote. The standard library's `Chars` iterator carries a lifetime, `Chars<'a>` (how a struct comes to carry one is lesson 27's subject), and its `as_str` method reads `pub fn as_str(&self) -> &'a str`. Against rule three's usual habit, this promises something surprising: the returned slice is tied to `'a`, the original string's lifetime, not to `&self`. That is why this compiles:

```rust
fn main() {
    let mut chars = "abc".chars();
    let rest: &str;
    {
        chars.next();
        rest = chars.as_str();
    }
    println!("{rest}");
}
```

`rest` survives past the block and past further use of `chars` because it never borrowed `chars`, only the string `chars` was built from. A signature elided to `&self`'s lifetime instead would have tied `rest` to `chars`, and this would not compile.

A second one, `pub const fn from_utf8(v: &[u8]) -> Result<&str, Utf8Error>`, is written elided; rule two says what it means: `fn from_utf8<'a>(v: &'a [u8]) -> Result<&'a str, Utf8Error>`. The promise is that the `&str` borrows the bytes you passed in rather than a copy, so those bytes must stay alive for as long as you keep the result.

### Anonymous lifetimes, and the numbers the compiler invents

`'_` is not a wildcard, it is the same elision machinery invoked outside a function signature, most often a type position: `Formatter<'_>`, which lesson 15 already had you write, means "infer this the way elision would." `&'_ str` is the same placeholder on a reference. Neither creates a lifetime; both ask the compiler to fill in one it can already work out.

When a diagnostic must talk about two never-named lifetimes, it invents numbers for that message alone. `note_or`'s error did this: `'1` is `fallback`'s lifetime, `'2` is `self`'s, with the note lines pointing at each `&` in turn. The numbering is not something you write; it is scratch notation for one error, and a different diagnostic on the same function could number the pair the other way round. Map a number back to source by finding its "let's call the lifetime of this reference" note and reading the span it underlines, not by assuming reading order.

### `'static`, and the trap it sets

A `&'static str` borrows data that lives for the whole program, most often a string literal: `let s: &'static str = "hello";` compiles because the literal is `'static`. The trap: `'static` is one of `E0106`'s own suggestions, and taking it without meaning it treats a workaround as a fix:

```text
help: consider using the `'static` lifetime, but this is uncommon unless you're returning a borrowed value from a `const` or a `static`
```

Adding it to a function returning a reference to a local cannot make that local live for the whole program, so the compiler moves to a sharper complaint, closer to the truth but still a wall. Lesson 28 tours that shape properly; treat any `'static` you did not choose on purpose as a question deferred, not answered.

## Practice

1. ▢ Predict the error code, and what the `help` line will say the ambiguity is between, before compiling.

   ```rust
   fn pick(a: &str, b: &str, c: &str) -> &str {
       if a.len() > b.len() { a } else { c }
   }
   ```

<details markdown="1"><summary>Check</summary>

`E0106`. The `help` line names all three candidates, `a`, `b`, or `c`, because elision reasons about the signature's shape rather than which branches the body actually takes.

</details>

2. ▢ Predict which of these two methods on the same struct compiles, then compile both.

   ```rust
   struct Cache { note: String }

   impl Cache {
       fn a(&self, fallback: &str) -> &str { &self.note }
       fn b(&self, fallback: &str) -> &str { fallback }
   }
   ```

<details markdown="1"><summary>Hint</summary>

Elision's third rule already decided, before either body was written, what the output lifetime is tied to.

</details>

<details markdown="1"><summary>Check</summary>

`a` compiles: it returns something borrowed from `self`, exactly what rule three assigned. `b` fails with the same "lifetime may not live long enough" shape shown above, since `fallback` was never the lifetime elision picked.

</details>

3. ▢ Take the `borrow` example from this lesson's opening, keep `<'a>`, and instead of moving `x`, wrap `x`, `r`'s binding, and the `println!` in one shared block. Predict whether that compiles, then check.

<details markdown="1"><summary>Check</summary>

It compiles. The annotation never changed; what changed is that `x` and its only borrow now share a scope ending after the borrow's last use, the same non-lexical-lifetimes reasoning lesson 3 covered, just carried across a function call.

</details>

4. ▢ Given `pub fn as_str(&self) -> &'a str` on `Chars<'a>`, predict whether this compiles before running it.

   ```rust
   fn keep_going() -> &'static str {
       let mut chars = "abc".chars();
       chars.next();
       chars.as_str()
   }
   ```

<details markdown="1"><summary>Hint</summary>

Ask what `'a` is tied to on `Chars<'a>`, and whether the string literal `"abc"` happens to already be `'static`.

</details>

<details markdown="1"><summary>Check</summary>

It compiles. `"abc"` is a string literal, so `'static`, which makes `Chars`'s own `'a` equal to `'static`, and `as_str`'s return is tied to `'a`, not to the iterator. Change `"abc"` to a runtime `String` and it fails, since `'a` is now tied to a local that does not live for the whole program.

</details>

5. ▢ In the `note_or` error, which lifetime, `'1` or `'2`, belongs to `self`, and which note line tells you, rather than declaration order?

<details markdown="1"><summary>Hint</summary>

Read the two "let's call the lifetime of this reference" notes as pointers, not as a numbered list.

</details>

<details markdown="1"><summary>Check</summary>

`'2` belongs to `self`. The note attached to `&self`'s span says so directly; the closing line only makes sense once each number is matched to its span, not assumed to follow "first parameter, second parameter."

</details>

## Real-world reps

- [ ] For every function in your project that returns a borrow, note which elision rule applies, what it resolves the output to, and whether the body actually returns that.
- [ ] Construct one small function, taking the line plus one other borrowed value and returning whichever you pick, where elision cannot resolve the output; confirm `E0106` before adding the lifetime parameter that fixes it. Do not restructure any type yet, that is tomorrow's rep.
- [ ] Tomorrow: pick your parser's line-splitting helper and confirm its returned slices are borrowed from the line, not copied, since that is the shape lesson 27 builds on.

## Going further

- [Validating References with Lifetimes](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html#validating-references-with-lifetimes): the chapter this lesson compresses
- [Lifetime elision](https://doc.rust-lang.org/reference/lifetime-elision.html): the three rules quoted here, plus the cases this lesson left out
- [E0106](https://doc.rust-lang.org/error_codes/E0106.html): the diagnostic for a missing lifetime specifier
- [Chars](https://doc.rust-lang.org/std/str/struct.Chars.html): whose `as_str` ties its return to the original string, not to `self`
- [Traits and lifetimes](../reference/traits-and-lifetimes.md): the stage 4 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
