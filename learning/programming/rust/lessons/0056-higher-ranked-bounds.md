---
title: 56. Higher-Ranked Bounds
description: Writing the quantifier the compiler has been printing at you, and the API shapes that need it
type: lesson
---

# Lesson 56. Higher-Ranked Bounds

**Mission link:** A senior engineer who cannot write the quantifier the compiler already assumes will get the wrong bound on a stored callback, or reach for `.clone()` the moment a closure needs to return a borrow.
**Primary source:** [Trait and lifetime bounds](https://doc.rust-lang.org/reference/trait-bounds.html#higher-ranked-trait-bounds)
**Prerequisites:** [Lesson 24](0024-generics-or-dyn-trait.md), [Lesson 28](0028-reading-a-lifetime-error.md)

## Warm-up

1. ▢ Lesson 28 met a failure with no error code at all, `` implementation of `Fn` is not general enough ``, and said the fix was a later stage's tool. What did the two notes underneath it, `` for any lifetime `'1` `` and `` for some specific lifetime `'2` ``, say the closure was missing?

<details markdown="1"><summary>Check</summary>

The bound asked for a closure that works for any lifetime a caller supplies, and the closure on offer only worked for one lifetime it was already pinned to. `'1` named what was required, `'2` named what was actually there, and that gap between "any" and "some specific" is what this lesson gives you the syntax to write down.

</details>

2. ▢ Lesson 24 put a `Square` and a `Circle` behind `Box<dyn Area>` so one collection could hold both. What did that indirection cost in pointers?

<details markdown="1"><summary>Check</summary>

A trait object doubled one pointer into two, a data pointer beside a vtable pointer, confirmed with `std::mem::size_of`, which is why a boxed closure with a quantified bound below is no stranger than any other `Box<dyn Fn>`.

</details>

## Know this

### 1. The wall from lesson 28, named in full

Lesson 28 stopped at the name. A bound such as `F: Fn(&str) -> usize` asks for a closure that works for every lifetime a caller might hand it, not one particular borrow, and a closure pinned to `&'static str` fails it with no error code:

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

Trimmed of a repeating `FnOnce` failure identical in shape, exactly as lesson 28 trimmed it. The name for "works for every lifetime" is a higher-ranked bound, and the syntax that says it out loud is `for<'a>`, read "for all `'a`". Writing it explicitly on `call_it`'s bound and comparing against the sugared form shows they mean exactly the same thing:

```rust
fn call_implicit<F: Fn(&str) -> usize>(f: F) -> usize {
    f("hi")
}

fn call_explicit<F: for<'a> Fn(&'a str) -> usize>(f: F) -> usize {
    f("hi")
}

fn main() {
    let len = |s: &str| s.len();
    println!("{}", call_implicit(len));
    println!("{}", call_explicit(len));
}
```

Both print `2`. `Fn(&str) -> usize` is not a shortened version of the quantified bound, it is the same bound: every elided-lifetime closure bound already carries an implicit `for<'a>`, which is why almost nobody writes it, and why lesson 28 could meet the failure before ever seeing the syntax behind it.

### 2. Where the sugar runs out: a return that borrows from the argument

Elision covers a bound with one borrowed parameter, but a bound whose return also borrows needs the quantifier by hand, since there is no elided form for "the same lifetime, for every lifetime". A function taking a closure that picks the longer of two borrowed strings, and returns a borrow of whichever it picked, states that with `for<'a>` on the bound and plain `&str` parameters of its own:

```rust
fn call_two<F>(f: F, a: &str, b: &str) -> String
where
    F: for<'a> Fn(&'a str, &'a str) -> &'a str,
{
    f(a, b).to_string()
}

fn longer<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() >= b.len() { a } else { b }
}

fn main() {
    let one = String::from("short");
    {
        let two = String::from("much longer string");
        println!("{}", call_two(longer, &one, &two));
    }
    let three = String::from("also short");
    println!("{}", call_two(longer, &one, &three));
}
```

This prints `much longer string` then `also short`: the same `longer` works across two calls whose borrowed strings live in entirely different, non-overlapping spans, because the bound fixed a rule that holds for every lifetime, not one lifetime. The same shape stores just as well behind a `Box` in a struct field:

```rust
struct Picker {
    pick: Box<dyn for<'a> Fn(&'a str, &'a str) -> &'a str>,
}

fn main() {
    let picker = Picker {
        pick: Box::new(|a: &str, b: &str| if a.len() >= b.len() { a } else { b }),
    };
    let one = String::from("short");
    let two = String::from("much longer string");
    let result = (picker.pick)(&one, &two);
    println!("{result}");
}
```

This prints `much longer string`. Rewriting the function's bound with a single named lifetime instead of the quantifier still compiles, since nothing about a bound requires it to be higher-ranked; the difference shows up the moment the function needs to hand the closure a borrow it made itself:

```rust
fn call_two<'a, F>(f: F, a: &'a str) -> String
where
    F: Fn(&'a str, &'a str) -> &'a str,
{
    let local = String::from("hi");
    f(a, &local).to_string()
}
```

```text
error[E0597]: `local` does not live long enough
  --> src/main.rs:6:10
   |
 1 | fn call_two<'a, F>(f: F, a: &'a str) -> String
   |             -- lifetime `'a` defined here
...
 5 |     let local = String::from("hi");
   |         ----- binding `local` declared here
 6 |     f(a, &local).to_string()
   |     -----^^^^^^-
   |     |    |
   |     |    borrowed value does not live long enough
   |     argument requires that `local` is borrowed for `'a`
 7 | }
   | - `local` dropped here while still borrowed
```

Trimmed of a further note naming the standard library's own source path for where `Fn` requires the value to outlive `'a`, which carries nothing the diagnosis needs. `'a` here is a parameter the *caller* chooses, fixed before the body runs, so it can only be as short as the caller's own arguments allow. `local` is born inside the body, after `'a` was already settled, and no choice by the caller could reach back and shrink `'a` to a value that did not exist yet. A single lifetime names one region fixed in advance; `for<'a>` names a rule satisfied afresh at every call, the only way to promise "whatever you hand me, however short, this still works".

### 3. Higher-ranked bounds on a trait you define

The same quantifier applies to a trait you own, not only to `Fn`. A trait whose method takes a borrow with its own lifetime parameter states a bound that holds for every lifetime exactly the way a closure bound does, on a `where` clause or, equivalently, on a supertrait:

```rust
trait LineCheck<'a> {
    fn interesting(&self, line: &'a str) -> bool;
}

struct NonEmpty;

impl<'a> LineCheck<'a> for NonEmpty {
    fn interesting(&self, line: &'a str) -> bool {
        !line.is_empty()
    }
}

fn count_interesting<T>(checker: &T) -> usize
where
    T: for<'a> LineCheck<'a>,
{
    let local = String::from("hi");
    if checker.interesting(&local) { 1 } else { 0 }
}

trait Verified: for<'a> LineCheck<'a> {}

impl<T> Verified for T where T: for<'a> LineCheck<'a> {}

fn takes_verified<T: Verified>(_checker: &T) {}

fn main() {
    let checker = NonEmpty;
    println!("{}", count_interesting(&checker));
    takes_verified(&checker);
}
```

This prints `1`. `count_interesting` needed the quantifier for the same reason `call_two` did: `local` is born after any lifetime the caller could have fixed, so only a bound holding for every lifetime lets the function build its own short-lived value and still hand it to `checker`. Writing `Verified` as a supertrait bounded by `for<'a> LineCheck<'a>` buys the same thing one level up: anything implementing `Verified` has a `LineCheck` that holds for every lifetime, so a function bounded by `Verified` alone inherits that generality without repeating the quantifier. Swap the `where` clause's `for<'a> LineCheck<'a>` for a single named `T: LineCheck<'a>` on `count_interesting<'a, T>`, and it fails exactly like `call_two` did, `` error[E0597]: `local` does not live long enough ``: one lifetime, fixed before the body runs, cannot cover a value the body has not made yet.

### 4. Reading the error messages this material produces

Three shapes account for most of what goes wrong here, each with a fix once named. `` implementation of `Fn` is not general enough `` is a trait-obligation check: something offered a closure that only works for one lifetime against a bound demanding every lifetime, fixed by deleting whatever pinned that lifetime, usually an explicit annotation on the closure's parameter. A close relative shows up when two named function types are compared directly instead:

```rust
fn identity(x: &str) -> &str {
    x
}

fn main() {
    let g: fn(&'static str) -> &'static str = identity;
    let f: for<'a> fn(&'a str) -> &'a str = g;
    let _ = f;
}
```

```text
error[E0308]: mismatched types
 --> src/main.rs:7:45
  |
7 |     let f: for<'a> fn(&'a str) -> &'a str = g;
  |            ------------------------------   ^ one type is more general than the other
  |            |
  |            expected due to this
  |
  = note: expected fn pointer `for<'a> fn(&'a _) -> &'a _`
             found fn pointer `fn(&'static _) -> &'static _`
```

`one type is more general than the other` is the same gap as a type mismatch instead of an unsatisfied bound: expected wants every lifetime, found offers one. The fix is identical in spirit, remove whatever fixed the found side to a single lifetime, here the explicit `'static` annotation on `g`. The third shape is not a new message but vocabulary lesson 28 already named: `'1` and `'2` are the compiler's own labels for lifetimes the source never wrote, and seeing them in either message means "any lifetime" is being weighed against "some specific one", not that anything else is broken.

### 5. Where this stops: no quantifier over types

Everything above quantifies over lifetimes. Reaching for the same idea over a type parameter, `for<T>` so a bound holds for every `T`, is not available on stable:

```rust
trait Apply<T> {
    fn apply(&self, x: T) -> T;
}

fn call_generic<F>(f: F)
where
    F: for<T> Apply<T>,
{
    let _ = f.apply(1);
}
```

```text
error[E0658]: only lifetime parameters can be used in this context
 --> src/main.rs:7:12
  |
7 |     F: for<T> Apply<T>,
  |            ^
  |
  = note: see issue #108185 <https://github.com/rust-lang/rust/issues/108185> for more information
```

What people reach for instead is moving the type parameter off the bound and onto the method itself, trading a trait-level quantifier for an ordinary generic method instantiated fresh at each call:

```rust
trait Apply {
    fn apply<T: std::fmt::Debug>(&self, x: T) -> T;
}

struct Echo;

impl Apply for Echo {
    fn apply<T: std::fmt::Debug>(&self, x: T) -> T {
        println!("{x:?}");
        x
    }
}

fn call_generic<F: Apply>(f: F) {
    let _ = f.apply(1);
    let _ = f.apply("two");
}

fn main() {
    call_generic(Echo);
}
```

This prints `1` then `"two"`. Nothing here is quantified over `T` at the bound; each call to `apply` picks its own `T` the ordinary way a generic function does, which is the ceiling this lesson leaves you at rather than a feature to chase on nightly.

## Practice

1. ▢ `Picker`'s field above is `Box<dyn for<'a> Fn(&'a str, &'a str) -> &'a str>`. Predict whether the same `picker` value can answer both calls below, whose borrowed strings come from two later, non-overlapping scopes.

   ```rust
   fn main() {
       let picker = Picker {
           pick: Box::new(|a: &str, b: &str| if a.len() >= b.len() { a } else { b }),
       };
       {
           let one = String::from("short");
           let two = String::from("much longer string");
           println!("{}", (picker.pick)(&one, &two));
       }
       {
           let three = String::from("a");
           let four = String::from("bb");
           println!("{}", (picker.pick)(&three, &four));
       }
   }
   ```

   Then change `Picker`'s field to `Box<dyn Fn(&'a str, &'a str) -> &'a str>` on a `Picker<'a>` and predict again before compiling both.

<details markdown="1"><summary>Check</summary>

With `for<'a>` on the field, both calls succeed, since the bound is satisfied afresh each call regardless of scope. With a named `'a` on `Picker<'a>` instead, all four borrows fail with `` E0597, does not live long enough ``, because the struct's one `'a` would have to outlive every borrow ever passed through it, including `picker`'s own drop, and no scope here is that long.

</details>

2. ▢ Predict whether this compiles, then compile it.

   ```rust
   fn identity(x: &str) -> &str {
       x
   }

   fn main() {
       let f: for<'a> fn(&'a str) -> &'a str = identity;
       let g: fn(&'static str) -> &'static str = f;
   }
   ```

<details markdown="1"><summary>Check</summary>

It compiles. A function general enough for every lifetime is also general enough for the one specific lifetime `'static` asks for, so assigning the quantified type to the narrower one loses nothing. The failing direction went the other way, offering only `'static` where every lifetime was required.

</details>

3. ▢ Take `count_interesting` from this lesson and replace its bound as shown, keeping `LineCheck` unchanged. Predict the error code before compiling.

   ```rust
   fn count_interesting<'a, T>(checker: &T) -> usize
   where
       T: LineCheck<'a>,
   {
       let local = String::from("hi");
       if checker.interesting(&local) { 1 } else { 0 }
   }
   ```

<details markdown="1"><summary>Check</summary>

The error is `E0597`, `` `local` does not live long enough ``, the identical shape `call_two` failed with. `local` is built inside the function after `'a` was already fixed by the caller, and a single named lifetime cannot reach back to cover a value that did not exist yet.

</details>

4. ▢ `Apply<T>` above failed behind `for<T> Apply<T>`. Predict whether the same trait compiles behind this bound instead, which quantifies a lifetime rather than the type parameter itself.

   ```rust
   struct Echo;
   impl<'a> Apply<&'a str> for Echo {
       fn apply(&self, x: &'a str) -> &'a str {
           x
       }
   }

   fn call_generic<F>(f: F)
   where
       F: for<'a> Apply<&'a str>,
   {
       let local = String::from("hi");
       println!("{}", f.apply(&local));
   }
   ```

<details markdown="1"><summary>Hint</summary>

`for<'a>` never stopped being about lifetimes; ask what kind of parameter `'a` is here, as opposed to what kind `T` was in `for<T> Apply<T>`.

</details>

<details markdown="1"><summary>Check</summary>

It compiles and prints `hi`. `T` is fixed to the concrete type `&'a str` before the bound is even written; only `'a`, a lifetime, is quantified, exactly what `for<...>` has always been allowed to quantify. The earlier failure was never about lifetimes inside a type, only about a bare type parameter standing where `for<...>` expects one.

</details>

5. ▢ A summariser function takes raw lines and a callback, trims each line into a fresh owned `String`, and returns the first one the callback accepts.

   ```rust
   fn first_interesting<F>(raw_lines: &[&str], is_interesting: F) -> Option<String>
   where
       F: for<'b> Fn(&'b str) -> Option<&'b str>,
   {
       for &line in raw_lines {
           let owned = line.trim().to_string();
           if let Some(snippet) = is_interesting(&owned) {
               return Some(snippet.to_string());
           }
       }
       None
   }
   ```

   Predict what changes if the bound is rewritten as `F: Fn(&'a str) -> Option<&'a str>` on `first_interesting<'a, F>` instead.

<details markdown="1"><summary>Hint</summary>

Ask where `owned` is created relative to where a single named `'a` would already have been fixed.

</details>

<details markdown="1"><summary>Check</summary>

Nothing about the closure changes, but the function no longer compiles at all, for any closure a caller could supply: `owned` is created inside the function after a single named `'a` would already have been fixed by the caller, the same shape as `local` in `call_two`, so `E0597` fires regardless of what the callback does with its argument.

</details>

## Real-world reps

- [ ] Give your project's line-interest callback a bound of `F: for<'a> Fn(&'a str) -> Option<&'a str>`, confirm it compiles against a closure that trims and re-slices its argument, then rewrite the bound with a single named lifetime and write down the diagnostic and why no closure could satisfy it.
- [ ] Find or introduce a boxed closure in a struct field in your project, and decide, using this lesson's `Picker` contrast, whether the field needs `for<'a>` or can use a lifetime borrowed from the struct itself.
- [ ] Tomorrow: pick a closure bound already in your project written as plain `Fn(&str) -> bool` or similar, write its fully quantified `for<'a>` form by hand, and confirm both compile identically before deleting the explicit version.

## Going further

- [Trait and lifetime bounds](https://doc.rust-lang.org/reference/trait-bounds.html#higher-ranked-trait-bounds): the Reference section this lesson teaches
- [Error code E0308](https://doc.rust-lang.org/error_codes/E0308.html): mismatched types, the code behind "one type is more general than the other"
- [Error code E0597](https://doc.rust-lang.org/error_codes/E0597.html): a borrowed value that does not live long enough
- [Error code E0658](https://doc.rust-lang.org/error_codes/E0658.html): an unstable feature was used, the code behind `for<T>`
- [Closures](https://doc.rust-lang.org/book/ch13-01-closures.html): the Book's introduction to the `Fn` family quantified here
- [Judgment](../reference/judgment.md): the stage 8 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
