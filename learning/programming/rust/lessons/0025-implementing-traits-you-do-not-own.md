---
title: 25. Implementing Traits You Do Not Own
description: Coherence, the newtype pattern, and why a blanket implementation is a commitment rather than a convenience
type: lesson
---

# Lesson 25. Implementing Traits You Do Not Own

**Mission link:** A crate that adds a single blanket `impl<T: Display> Label for T` has just forbidden every type in that crate, and every type in every crate that depends on it, from ever getting its own `Label` implementation, and the compiler will not say so until someone tries.
**Primary source:** [Implementations](https://doc.rust-lang.org/reference/items/implementations.html)
**Prerequisites:** [Lesson 21](0021-traits-as-shared-behaviour.md), [Lesson 16](0016-conversions-and-boundaries.md)

## Warm-up

1. ▢ Lesson 21 showed that a trait's methods are callable only where the trait itself is in scope, and named the diagnostic for calling one that is not. Which error code was that, and what did the compiler's `help` suggest doing about it?

<details markdown="1"><summary>Check</summary>

It was `E0599`, with `items from traits can only be used if the trait is in scope`, and a `help` naming the exact `use` line that brings the trait into scope.

</details>

2. ▢ Lesson 16 met the orphan rule already, attempting a `From` between two types neither owned by that crate. Which error code did that give, and which two types did the diagnostic name as not defined in the current crate?

<details markdown="1"><summary>Check</summary>

`E0117`, naming `ParseIntError` and `std::fmt::Error` as the two foreign types, since owning neither of them is exactly what the rule blocks.

</details>

## Know this

### Coherence: one implementation, decided globally

For any trait and any type, a program has at most one implementation of that trait for that type, decided once for the whole crate graph rather than per call site. If two crates were each free to implement the same trait for the same foreign type, a program depending on both would have two competing implementations on offer, with no principled way to choose between them: which one a call resolves to would depend on link order, and could change the moment either dependency shipped an update. Coherence is the rule that this never happens: exactly one implementation exists for a trait and type pair, so a method call resolves to the same code regardless of which dependency wrote it. That guarantee is what makes adding a dependency safe at all; without it, a crate you have never heard of could change which method your existing code calls, and you would find out only once behaviour shifted underneath you.

### The orphan rule, verified

Coherence is checked at compile time as the orphan rule, which lesson 16 has already produced once at the `From` boundary. The same rule blocks any other foreign-for-foreign implementation the same way:

```rust
use std::fmt;

impl fmt::Display for Vec<u8> {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{:?}", self)
    }
}
```

```text
error[E0117]: only traits defined in the current crate can be implemented for types defined outside of the crate
 --> src/main.rs:3:1
  |
3 | impl fmt::Display for Vec<u8> {
  | ^^^^^^^^^^^^^^^^^^^^^^-------
  |                       |
  |                       `Vec` is not defined in the current crate
  |
  = note: impl doesn't have any local type before any uncovered type parameters
  = note: for more information see https://doc.rust-lang.org/reference/items/implementations.html#orphan-rules
  = note: define and implement a trait or new type instead
```

The Reference states the rule behind that diagnostic precisely: an implementation is valid only if the trait is a local trait, or the implementing type has a local type among its parameters. That is two escapes and exactly two: write the trait yourself, or write the type yourself. `Display` and `Vec` are both foreign, so `Vec<u8>` fails both and nothing short of taking one of them compiles. The rest of this lesson is those two escapes, plus a shape that looks like neither and is actually the second one in disguise.

### The newtype pattern

The second escape, a local type, does not require redesigning the foreign type. Wrapping it in a tuple struct of your own is enough, because the wrapper is local even though its one field is not:

```rust
use std::fmt;

struct Wrapper(Vec<String>);

impl fmt::Display for Wrapper {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "[{}]", self.0.join(", "))
    }
}

fn main() {
    let w = Wrapper(vec!["hello".to_string(), "world".to_string()]);
    println!("{w}");
}
```

That compiles and prints `[hello, world]`. `Vec<String>` never gained a `Display`; a second crate could wrap the same `Vec<String>` in its own newtype and give it a different `Display` with no conflict, because the two implementations are for two different types. The cost is that the wrapper is genuinely a new type with none of `Vec`'s own methods, even though underneath it is nothing but a `Vec`:

```rust
fn main() {
    let w = Wrapper(vec!["hello".to_string()]);
    println!("{}", w.len());
}
```

```text
error[E0599]: no method named `len` found for struct `Wrapper` in the current scope
  --> src/main.rs:13:22
   |
 3 | struct Wrapper(Vec<String>);
   | -------------- method `len` not found for this struct
...
13 |     println!("{}", w.len());
   |                      ^^^ method not found in `Wrapper`
   |
   = help: items from traits can only be used if the trait is implemented and in scope
   = note: the following trait defines an item `len`, perhaps you need to implement it:
           candidate #1: `ExactSizeIterator`
help: one of the expressions' fields has a method of the same name
   |
13 |     println!("{}", w.0.len());
   |                      ++
```

The suggested `w.0.len()` works, but writing `.0` at every call site defeats the point of wrapping in the first place, which is that callers should not need to know what is inside.

### Two ways to answer that

The first way is a `Deref` implementation, which lets the compiler insert the field access for you:

```rust
use std::ops::Deref;

impl Deref for Wrapper {
    type Target = Vec<String>;

    fn deref(&self) -> &Vec<String> {
        &self.0
    }
}
```

With that in place, `w.len()` compiles and returns `1`: the compiler tries `Wrapper`'s own methods first, finds none, then tries the type `Wrapper` derefs to and finds `len` there. The second way forwards explicitly, writing the one method the wrapper needs to offer:

```rust
impl Wrapper {
    fn len(&self) -> usize {
        self.0.len()
    }
}
```

This also compiles and returns `1`, without a `Deref` in sight. Both are honest; they differ in how much of the inner type leaks through. `Deref` hands over every method the target has, present and future, and the standard library's own guidance says not to implement it unless a value "transparently behaves like a value of the target type", warning against it where "the type has methods that are likely to collide with methods on the target type" or where "committing to deref coercion as part of the public API is not desirable". The collision is not hypothetical: if `Wrapper` later grows its own `len` for an unrelated reason, that inherent method silently wins over the one `Deref` would have forwarded. Explicit forwarding never collides by surprise, since each forwarded method is a line chosen deliberately, which is why it is the safer default: only the operations the wrapper needs cross the boundary.

### Extension traits

The first escape, a local trait, is the standard way to add a method to a type you do not own at all, wrapper or not. Declare a trait locally and implement it for the foreign type directly:

```rust
trait Shout {
    fn shout(&self) -> String;
}

impl Shout for str {
    fn shout(&self) -> String {
        self.to_uppercase() + "!"
    }
}

fn main() {
    println!("{}", "hello".shout());
}
```

This compiles and prints `HELLO!`, and the orphan rule allows it without a wrapper, because `Shout` is local even though `str` is not. The one requirement it carries is the same one lesson 21 already met: the trait has to be in scope wherever `.shout()` is called, or the call does not resolve.

```text
error[E0599]: no method named `shout` found for reference `&'static str` in the current scope
  --> src/main.rs:14:28
   |
14 |     println!("{}", "hello".shout());
   |                            ^^^^^ method not found in `&'static str`
   |
   = help: items from traits can only be used if the trait is in scope
help: trait `Shout` which provides `shout` is implemented but not in scope; perhaps you want to import it
   |
 1 + use crate::shout::Shout;
   |
```

Adding the suggested `use` is the whole fix; nothing about `Shout` or `str` changes. This is the idiom's name for a reason: it extends what a foreign type can do, from the caller's side, without touching the type or waiting for its owner to add the method.

### Blanket implementations, and the commitment they make

A blanket implementation covers every type satisfying a bound, in one `impl`, rather than one type at a time:

```rust
use std::fmt;

trait Label {
    fn label(&self) -> String;
}

impl<T: fmt::Display> Label for T {
    fn label(&self) -> String {
        format!("{self}")
    }
}

struct Tag(u32);

impl Label for Tag {
    fn label(&self) -> String {
        format!("tag#{}", self.0)
    }
}
```

This compiles, and `Tag(7).label()` gives `tag#7`, because `Tag` has no `Display`: the blanket impl does not apply to it, so the concrete `impl Label for Tag` is the only candidate. That coexistence lasts only as long as `Tag` avoids `Display`. Adding it, for a completely unrelated reason such as logging, changes the picture entirely:

```rust
impl fmt::Display for Tag {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "tag#{}", self.0)
    }
}
```

```text
error[E0119]: conflicting implementations of trait `Label` for type `Tag`
  --> src/main.rs:21:1
   |
 7 | impl<T: fmt::Display> Label for T {
   | --------------------------------- first implementation here
...
21 | impl Label for Tag {
   | ^^^^^^^^^^^^^^^^^^ conflicting implementation for `Tag`
```

Both blocks compiled, which is what makes this the sharpest demonstration of the cost: `impl<T: Display> Label for T` removed, from every type in the crate, the option of ever writing its own `impl Label` once that type also implements `Display`. The conflict was not created by touching `Label` or `Tag`'s implementation at all; it arrived from `impl Display for Tag`, which has nothing to do with `Label` on its face. A blanket implementation is a commitment made once, on behalf of every type that will ever satisfy its bound, including ones that do not exist yet.

## Practice

1. ▢ Predict whether wrapping a `HashMap<String, u32>` in a local tuple struct and implementing `Display` on the wrapper compiles, and predict the error code if `Display` is implemented directly on `HashMap<String, u32>` instead. Then compile both.

   ```rust
   use std::collections::HashMap;
   use std::fmt;

   struct Registry(HashMap<String, u32>);

   impl fmt::Display for Registry {
       fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
           write!(f, "{} entries", self.0.len())
       }
   }
   ```

<details markdown="1"><summary>Check</summary>

The wrapped version compiles, since `Registry` is local even though `HashMap` is not. Implementing `Display` directly on `HashMap<String, u32>` gives `E0117`, naming `HashMap` as not defined in the current crate, the same failure `Vec<u8>` gave above.

</details>

2. ▢ Using the `Registry` from the item above, predict what happens when the code below is added, and which error code names the problem.

   ```rust
   fn main() {
       let r = Registry(HashMap::new());
       r.get("x");
   }
   ```

<details markdown="1"><summary>Hint</summary>

`Registry` has exactly one method, and it is not called `get`.

</details>

<details markdown="1"><summary>Check</summary>

It fails with `E0599`, no method named `get` found for struct `Registry` in the current scope, and the compiler's own fix suggestion is `r.0.get("x")`, reaching into the wrapped field directly.

</details>

3. ▢ Predict whether this compiles as written, and then predict what happens if `main` calls `values.average()` from outside the `stats` module without an extra line. Compile both.

   ```rust
   mod stats {
       pub trait Average {
           fn average(&self) -> f64;
       }

       impl Average for [i32] {
           fn average(&self) -> f64 {
               self.iter().sum::<i32>() as f64 / self.len() as f64
           }
       }
   }

   fn main() {
       let values = [2, 4, 6];
       println!("{}", values.average());
   }
   ```

<details markdown="1"><summary>Check</summary>

The trait and its implementation compile on their own, since `Average` is local and `[i32]` is not, the orphan rule's first escape. The call in `main` fails with `E0599` until `use crate::stats::Average;` is added, because the trait is implemented but not in scope, exactly the shape lesson 21 already showed.

</details>

4. ▢ Predict whether this pair compiles, then predict what happens once `Widget` gains `#[derive(Debug)]`.

   ```rust
   use std::fmt;

   trait Show {
       fn show(&self) -> String;
   }

   impl<T: fmt::Debug> Show for T {
       fn show(&self) -> String {
           format!("{self:?}")
       }
   }

   struct Widget;

   impl Show for Widget {
       fn show(&self) -> String {
           "widget".to_string()
       }
   }
   ```

<details markdown="1"><summary>Hint</summary>

Ask which types the blanket implementation currently applies to, and whether `Widget` is one of them yet.

</details>

<details markdown="1"><summary>Check</summary>

It compiles as written, because `Widget` has no `Debug` and so the blanket implementation does not apply to it. Deriving `Debug` on `Widget` turns it into `E0119`, conflicting implementations of trait `Show` for type `Widget`, pointing at the blanket `impl<T: fmt::Debug> Show for T` as first implementation here.

</details>

5. ▢ Predict what `ids.len()` prints, given both a `Deref` to `Vec<u32>` and an inherent method of the same name.

   ```rust
   use std::ops::Deref;

   struct Ids(Vec<u32>);

   impl Deref for Ids {
       type Target = Vec<u32>;

       fn deref(&self) -> &Vec<u32> {
           &self.0
       }
   }

   impl Ids {
       fn len(&self) -> usize {
           999
       }
   }

   fn main() {
       let ids = Ids(vec![1, 2, 3]);
       println!("{}", ids.len());
   }
   ```

<details markdown="1"><summary>Hint</summary>

Method resolution checks the receiver's own inherent methods before it ever tries what the receiver derefs to.

</details>

<details markdown="1"><summary>Check</summary>

It prints `999`. The inherent `len` on `Ids` wins over the `Vec`'s `len` reachable through `Deref`, silently, with nothing at the call site to say a collision happened.

</details>

## Real-world reps

- [ ] Wrap your project's byte total in a newtype, `Bytes(u64)`, with a `Display` implementation that formats it as a human-readable size rather than a bare integer; give it exactly the arithmetic your summariser performs on a running total, by forwarding or by `Deref`, and write one line above that implementation saying which of the two you chose and why.
- [ ] Add a local extension trait for whatever produces your input's lines, giving it a method your summariser has been computing by hand inline, such as counting the lines that are neither blank nor comments, and move that computation into the trait's default method.
- [ ] Tomorrow: list every `impl` your project has written for a type it does not own, whether by newtype or by extension trait, and note next to each one which of the orphan rule's two escapes it used.

## Going further

- [Orphan rules](https://doc.rust-lang.org/reference/items/implementations.html#orphan-rules): the coherence rule behind `E0117`, stated as the trait or the type needing to be local
- [E0117](https://doc.rust-lang.org/error_codes/E0117.html): the diagnostic for implementing a foreign trait for a foreign type
- [E0119](https://doc.rust-lang.org/error_codes/E0119.html): the diagnostic for two implementations of the same trait for the same type
- [std::ops::Deref](https://doc.rust-lang.org/std/ops/trait.Deref.html): the trait behind deref coercion, and its own guidance on when implementing it is and is not a good idea
- [Implementing External Traits with the Newtype Pattern](https://doc.rust-lang.org/book/ch20-02-advanced-traits.html#implementing-external-traits-with-the-newtype-pattern): the Book's chapter on the pattern this lesson leans on
- [Traits and lifetimes](../reference/traits-and-lifetimes.md): the stage 4 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
