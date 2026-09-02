---
title: 27. Types That Borrow
description: Putting a lifetime parameter on a struct, and deciding whether the type should own its data instead
type: lesson
---

# Lesson 27. Types That Borrow

**Mission link:** A struct's fields decide, before a method is written, whether every caller must keep the source data alive as long as the struct does or whether the struct pays for its own copy, and guessing wrong spreads a lifetime parameter through every type that touches it, or wastes an allocation nobody asked for.
**Primary source:** [std::borrow::Cow](https://doc.rust-lang.org/std/borrow/enum.Cow.html)
**Prerequisites:** [Lesson 26](0026-lifetimes-are-not-durations.md), [Lesson 7](0007-structs.md)

## Warm-up

1. ▢ Lesson 26 distinguished a lifetime, a region the compiler checks, from a duration, something that is measured. In `fn longest<'a>(a: &'a str, b: &'a str) -> &'a str`, what would giving `a` and `b` two separate lifetime parameters instead of one actually change about how long the strings behind them live?

<details markdown="1"><summary>Check</summary>

Nothing: no annotation changes how long a binding lives. Two separate parameters just let the compiler track two different regions instead of forcing the shorter one onto both, which loosens what the function accepts without touching either string's actual lifetime.

</details>

2. ▢ Lesson 7 defined a struct's fields once and let every `impl` block's methods use them without repeating their types. Given that, what would you expect an `impl` block to need if one of the struct's fields holds a generic type parameter `T`, the way a field of type `Option<T>` does?

<details markdown="1"><summary>Check</summary>

The `impl` block has to declare that same parameter, `impl<T> Container<T>`: a struct's own generic parameters are not automatically in scope inside its `impl` blocks, they are declared there again, and a lifetime parameter works the same way.

</details>

## Know this

### A struct that borrows

`struct Record<'a> { path: &'a str }` promises that for as long as any particular `Record` exists, the `str` behind its `path` field is valid for at least `'a`. Nothing here differs from a function's lifetime parameter: a struct is just another place a reference can be stored, and the compiler needs the same name for the borrow's region.

```rust
struct Record<'a> {
    path: &'a str,
}

impl<'a> Record<'a> {
    fn path(&self) -> &str {
        self.path
    }
}

fn main() {
    let line = String::from("/index 200 1200");
    let record = Record { path: &line[..6] };
    println!("{}", record.path());
}
```

This prints `/index`. Leaving `'a` off the `impl` block does not fall back to some default; it is rejected outright:

```text
error[E0726]: implicit elided lifetime not allowed here
 --> src/main.rs:5:6
  |
5 | impl Record {
  |      ^^^^^^ expected lifetime parameter
  |
help: indicate the anonymous lifetime
  |
5 | impl Record<'_> {
  |            ++++
```

The parameter has to appear on the struct and on every `impl` block for the same reason a struct's own type parameters do: `Record` is a family of types, one per lifetime a caller supplies, and an `impl` block that omits the parameter cannot say which member of the family it targets. What the compiler then stops you doing is building a `Record` whose `path` outlives its source:

```rust
struct Record<'a> {
    path: &'a str,
}

fn main() {
    let record;
    {
        let line = String::from("/index 200 1200");
        record = Record { path: &line[..6] };
    }
    println!("{}", record.path);
}
```

```text
error[E0597]: `line` does not live long enough
  --> src/main.rs:9:34
   |
 8 |         let line = String::from("/index 200 1200");
   |             ---- binding `line` declared here
 9 |         record = Record { path: &line[..6] };
   |                                  ^^^^ borrowed value does not live long enough
10 |     }
   |     - `line` dropped here while still borrowed
11 |     println!("{}", record.path);
   |                    ----------- borrow later used here
```

`Record` did not change between the two examples; only the relative lifetimes of `record` and `line` did, and the struct's promise is what caught it.

### E0621: the struct's promise binds its methods too

A struct that stores a borrow constrains what its methods may do with values passed in afterwards too, not just how it is built. Take `struct Holder<'a> { seen: Vec<&'a str> }` with a method meant to remember a string:

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

`s: &str` carries its own elided lifetime, unrelated to `'a` and good only for the call. `self.seen` can only hold `&'a str` values, so pushing `s` in would let a shorter borrow sit inside a `Vec` typed for `'a`, the dangling reference the borrow checker exists to prevent. The struct already promised that everything in `seen` lives at least `'a`; the method's signature has to repeat that promise, because nothing in the body tells the compiler which lifetime the caller intended. Adding `'a` to `s`'s type, as the `help` shows, is the method agreeing with the struct it belongs to:

```rust
impl<'a> Holder<'a> {
    fn keep(&mut self, s: &'a str) {
        self.seen.push(s);
    }
}
```

This compiles, and `holder.keep("hello")` stores the borrow exactly where `Holder`'s definition said it would live.

### Owning versus borrowing, decided by who outlives whom

A type that touches borrowed data has three honest shapes, and the choice between them is about who outlives whom, not which is faster. A borrowing type is right when it is used and dropped before its source goes away:

```rust
struct BorrowedLine<'a> {
    raw: &'a str,
}

fn parse(line: &str) -> BorrowedLine<'_> {
    BorrowedLine { raw: line }
}
```

An owning type is right when the type has to survive its source, such as a value pushed into a `Vec` that is still read after the line it came from is gone:

```rust
struct OwnedLine {
    raw: String,
}

fn parse(line: &str) -> OwnedLine {
    OwnedLine { raw: line.to_owned() }
}
```

Both compile and print the same text; the difference shows only when the source disappears while the parsed value is still needed, which the borrowing shape cannot survive and the owning shape can. Between these sits `Cow`, the standard library's answer to "sometimes": a clone-on-write smart pointer that "can enclose and provide immutable access to borrowed data, and clone the data lazily when mutation or ownership is required", in the documentation's words, with two variants, `Borrowed(&'a B)` and `Owned(<B as ToOwned>::Owned)`. It earns its complexity only when a common case needs no allocation but a rarer case does:

```rust
use std::borrow::Cow;

fn normalise(path: &str) -> Cow<'_, str> {
    if path.contains("//") {
        Cow::Owned(path.replace("//", "/"))
    } else {
        Cow::Borrowed(path)
    }
}

fn main() {
    let plain = normalise("/index");
    let messy = normalise("/index//extra");
    println!("{plain} {messy}");
}
```

Matching on the result shows `plain` comes back `Cow::Borrowed`, with no allocation at all, and only `messy` becomes `Cow::Owned` after the `replace`. A type that is always borrowed or always owned does not need this; reach for `Cow` only when a real caller sometimes has clean input and sometimes does not, and an owned copy on every call would waste the common path.

### `T: 'a` bounds

A generic struct that stores a type parameter and a borrow sometimes needs to say the type parameter itself outlives the borrow, written `T: 'a`. The Reference states this precisely: "`T: 'a` means that all lifetime parameters of `T` outlive `'a`." The compiler often infers this from a field like `&'a T`, but not everywhere:

```rust
struct Wrapper<'a, T> {
    label: &'a str,
    value: T,
}

impl<'a, T: std::fmt::Debug> Wrapper<'a, T> {
    fn boxed(self) -> Box<dyn std::fmt::Debug + 'a> {
        Box::new(self.value)
    }
}
```

```text
error[E0309]: the parameter type `T` may not live long enough
 --> src/main.rs:8:9
  |
6 | impl<'a, T: std::fmt::Debug> Wrapper<'a, T> {
  |      -- the parameter type `T` must be valid for the lifetime `'a` as defined here...
7 |     fn boxed(self) -> Box<dyn std::fmt::Debug + 'a> {
8 |         Box::new(self.value)
  |         ^^^^^^^^^^^^^^^^^^^^ ...so that the type `T` will meet its required lifetime bounds
```

Boxing `self.value` into a trait object tagged `'a` requires that `T` contains no borrow shorter than `'a`, and nothing in `Wrapper`'s fields said so. Adding the bound the `help` suggests fixes it:

```rust
impl<'a, T: std::fmt::Debug + 'a> Wrapper<'a, T> {
    fn boxed(self) -> Box<dyn std::fmt::Debug + 'a> {
        Box::new(self.value)
    }
}
```

### The two meanings of `'static`

`&'static T` is a reference valid for the whole program, the lifetime string literals get because their text is stored directly in the binary. `T: 'static` is a different claim: it says `T`'s own lifetime parameters, if any, are all `'static`, so `T` holds no borrow that could go stale, not that some particular value lives forever. An owned type such as `String` satisfies `T: 'static` unconditionally, having no lifetime parameter to fail the bound, even when the value is created and dropped in a few lines:

```rust
fn store_static<T: 'static>(value: T) -> Box<T> {
    Box::new(value)
}

static GREETING: &str = "hello";

fn main() {
    let reference: &'static str = GREETING;
    println!("{reference}");

    let boxed = {
        let owned = String::from("owns heap data, created in a short-lived scope");
        store_static(owned)
    };
    println!("{boxed}");
}
```

This compiles and prints both lines; the `String` created inside the inner block is gone as a binding by the time `main` ends, yet it satisfied `T: 'static` the entire time. Reading `T: 'static` as "must live forever" is the misreading worth killing: the bound only rules out a `T` that borrows something shorter-lived, such as `&'b str` for some `'b` that is not `'static`. It is a claim about the type's shape, not a promise about any one value's lifespan.

### Self-referential structs

A struct that borrows from its own other field, such as a type whose `pointer` field is meant to point at its own `value` field, does not compile, because building the struct always borrows `value` before the struct exists to name a lifetime against. The standard library has no way to express this relationship, since every lifetime parameter names a borrow from somewhere else, and "somewhere else" cannot mean "this same value, once it exists." This is exactly the problem the pinning material in the async stage addresses, once a generated future's own state must hold a borrow into its other state.

```rust
struct SelfRef<'a> {
    value: String,
    pointer: &'a str,
}

fn main() {
    let value = String::from("hello");
    let pointer = &value;
    let s = SelfRef { value, pointer };
    println!("{}", s.pointer);
}
```

```text
error[E0505]: cannot move out of `value` because it is borrowed
 --> src/main.rs:9:23
  |
7 |     let value = String::from("hello");
  |         ----- binding `value` declared here
8 |     let pointer = &value;
  |                   ------ borrow of `value` occurs here
9 |     let s = SelfRef { value, pointer };
  |                       ^^^^^  ------- borrow later used here
  |                       |
  |                       move out of `value` occurs here
```

The `help` that follows suggests cloning `value`, trimmed here because it is a workaround rather than a fix: cloning gives `pointer` a borrow of a second, independent string, not of the field the struct actually stores, so the struct still would not be self-referential, it would just stop looking like it was trying to be.

## Practice

1. ▢ Predict the error code before compiling this.

   ```rust
   struct Pair<'a> {
       left: &'a str,
       right: &'a str,
   }

   impl Pair {
       fn left(&self) -> &str {
           self.left
       }
   }
   ```

<details markdown="1"><summary>Check</summary>

It is `E0726`, implicit elided lifetime not allowed here, with a `help` suggesting `Pair<'_>`. The struct has one lifetime parameter and the `impl` block has to name it, exactly as it would a type parameter.

</details>

2. ▢ Add `fn last(&mut self, s: &str)` to `Holder<'a> { seen: Vec<&'a str> }`, pushing `s` onto `seen` without changing its type. Predict the error code, then compile and apply the `help`'s fix.

<details markdown="1"><summary>Hint</summary>

`seen` can only ever hold `&'a str` values; ask what lifetime `s: &str` actually carries on its own.

</details>

<details markdown="1"><summary>Check</summary>

It is `E0621`, with a `help` adding `&'a str` to `s`'s type. `s`'s elided lifetime is unrelated to `'a` and generally shorter, so pushing it into `seen` would let a short-lived borrow sit inside a `Vec` typed for the struct's own lifetime; writing `s: &'a str` repeats the promise the struct already made.

</details>

3. ▢ For `normalise` from this lesson, predict which `Cow` variant a call with `"/a/b/c"` returns, and which a call with `"/a//b"` returns. Match on both results to check.

<details markdown="1"><summary>Check</summary>

`"/a/b/c"` returns `Cow::Borrowed`, since it contains no `//` and the function never allocates. `"/a//b"` returns `Cow::Owned`, since `replace` has to build a new `String`. The signature does not say which one a caller gets; only the input does.

</details>

4. ▢ Predict whether this compiles, and if not, which error code names the missing bound.

   ```rust
   struct Tagged<'a, T> {
       tag: &'a str,
       inner: T,
   }

   impl<'a, T: Clone> Tagged<'a, T> {
       fn boxed_clone(&self) -> Box<dyn std::any::Any + 'a> {
           Box::new(self.inner.clone())
       }
   }
   ```

<details markdown="1"><summary>Hint</summary>

`Box::new` here has to produce a trait object tagged `'a`, and `T` is not otherwise related to `'a` anywhere in the struct.

</details>

<details markdown="1"><summary>Check</summary>

It does not compile: `E0309`, since boxing `self.inner.clone()` into a `dyn Any + 'a` requires `T: 'a` and nothing declares it. Changing the bound to `T: Clone + 'a` fixes it.

</details>

5. ▢ Name the error code before compiling this, where one field borrows from another field of the same struct.

   ```rust
   struct Node<'a> {
       label: String,
       view: &'a str,
   }

   fn main() {
       let label = String::from("root");
       let view = &label;
       let node = Node { label, view };
       println!("{}", node.view);
   }
   ```

<details markdown="1"><summary>Check</summary>

It is `E0505`: constructing `node` needs to move `label` in while `view` still borrows it, and no lifetime annotation changes that, since the struct has to exist before anything could name a lifetime pointing back into it.

</details>

## Real-world reps

- [ ] Convert your project's line record to borrow every field it can from the line it was parsed from, rather than owning a copy of each one, keeping the pre-stage-4 file alongside it so the diff is there to read.
- [ ] Confirm the summary type that accumulates results across every line still owns what it stores, then note in one comment which piece forced which choice: the record survives one line and can borrow, the summary survives every line and cannot.
- [ ] Tomorrow: find any `.to_owned()` or `.clone()` in your parser that exists only to satisfy the borrow checker rather than because the value must outlive its source, and check whether a lifetime parameter can replace it.

## Going further

- [Lifetime bounds](https://doc.rust-lang.org/reference/trait-bounds.html#lifetime-bounds): the Reference's rule for what `T: 'a` requires and how implied bounds infer it unwritten
- [E0621](https://doc.rust-lang.org/error_codes/E0621.html): the diagnostic for a signature that does not match the lifetime the function body needs
- [E0309](https://doc.rust-lang.org/error_codes/E0309.html): the diagnostic for a type parameter that may not outlive the lifetime it is boxed into
- [The Static Lifetime](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html#the-static-lifetime): the Book's warning against reaching for `'static` before checking whether the reference should really live that long
- [Traits and lifetimes](../reference/traits-and-lifetimes.md): the stage 4 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
