---
title: 21. Traits as Shared Behaviour
description: How a trait names behaviour several types can provide, and why the trait has to be in scope before you can use it
type: lesson
---

# Lesson 21. Traits as Shared Behaviour

**Mission link:** Two unrelated types in a codebase that both need to report progress, or both need to compare equal, either get that behaviour copied by hand into each one or get it named once as a trait and implemented per type, and the second choice is the one every later lesson in this stage assumes you can already make.
**Primary source:** [Defining Shared Behavior with Traits](https://doc.rust-lang.org/book/ch10-02-traits.html)
**Prerequisites:** [Lesson 7](0007-structs.md), [Lesson 15](0015-designing-an-error-type.md)

## Warm-up

1. ▢ Lesson 7 gave a struct's own methods a home inside an `impl` block, written for exactly one type. A trait also declares methods, but not for any one type yet. What changes about a method once it moves from a plain `impl` block into a trait's own declaration, before that trait has been implemented for anything?

<details markdown="1"><summary>Check</summary>

Nothing about how the method reads, its receiver and its body still work the same way. What changes is ownership of the name: a plain `impl` block's method belongs to the one type it is written on, while a trait's declaration names behaviour that any number of types can later promise to provide, each with its own `impl Trait for Type` block.

</details>

2. ▢ Lesson 15 had you implement `std::error::Error` by hand on your own error enum, including a `source` method, and later call `err.source()` on a value of that enum. `source` is declared on `Error`, not on your enum. Beyond writing the `impl`, what has to be true wherever `.source()` is called for that call to compile?

<details markdown="1"><summary>Check</summary>

`std::error::Error` itself has to be in scope at the call site, usually through `use std::error::Error;`, and lesson 15's examples already had it in scope without dwelling on the requirement. This lesson makes that requirement explicit and shows exactly what happens when it is missing.

</details>

## Know this

### A trait names behaviour, and a default can lean on what is required

A trait declaration lists methods without saying which type provides them yet. A required method has only a signature; a default method has a body, and that body can call a required method the same way any method calls another:

```rust
trait Announce {
    fn kind(&self) -> &'static str;
    fn announce(&self) -> String {
        format!("this is a {}", self.kind())
    }
}
```

`kind` is required: any type implementing `Announce` must supply it. `announce` is a default: it calls `self.kind()` without knowing yet which type's `kind` that will turn out to be. Two types can implement the same trait and treat that default differently, one leaving it alone and one replacing it:

```rust
struct Bike;
struct Car;

impl Announce for Bike {
    fn kind(&self) -> &'static str {
        "bike"
    }
}

impl Announce for Car {
    fn kind(&self) -> &'static str {
        "car"
    }

    fn announce(&self) -> String {
        format!("vroom, a {}", self.kind())
    }
}
```

`Bike`'s `impl` block never mentions `announce`, so it inherits the default, and `Car`'s overrides it. Calling both directly, with no generic function and no `dyn` anywhere in sight, shows each behaviour:

```rust
println!("{}", Bike.announce());
println!("{}", Car.announce());
```

```text
this is a bike
vroom, a car
```

`Bike.announce()` runs the default body, which itself called `Bike`'s `kind`; `Car.announce()` runs the version `Car` wrote instead. Both are ordinary method calls on ordinary types: nothing here needed a type parameter or a trait object, because the caller always knew, at the call site, exactly which concrete type it was calling through.

### The trait has to be in scope

This is the single most common confusion about traits, and it has nothing to do with the trait itself being wrong. A method declared on a trait is only callable with dot syntax where that trait is in scope, even when the `impl` exists and the type is right there. Split a trait and its `impl` into one module and call the method from another, without importing the trait:

```rust
mod shapes {
    pub trait Shape {
        fn area(&self) -> f64;
    }

    pub struct Square {
        pub side: f64,
    }

    impl Shape for Square {
        fn area(&self) -> f64 {
            self.side * self.side
        }
    }
}

mod report {
    use crate::shapes::Square;

    pub fn show(sq: Square) {
        println!("{}", sq.area());
    }
}
```

`report` imports `Square` but not `Shape`, and that omission is the whole bug:

```text
error[E0599]: no method named `area` found for struct `Square` in the current scope
   |
 3 |         fn area(&self) -> f64;
   |            ---- the method is available for `Square` here
...
21 |         println!("{}", sq.area());
   |                           ^^^^ method not found in `Square`
   |
   = help: items from traits can only be used if the trait is in scope
help: trait `Shape` which provides `area` is implemented but not in scope; perhaps you want to import it
   |
18 +     use crate::shapes::Shape;
   |
```

The compiler already knows the fix: it points at the trait's own declaration to say the method exists for this type, then names the exact rule, `items from traits can only be used if the trait is in scope`, then suggests the precise `use` line. Adding `use crate::shapes::Shape;` to `report`, alongside the existing import of `Square`, is enough, and the same `sq.area()` call now compiles and prints `9`. Nothing about `Square` or `Shape` changed; the only difference is that the trait providing `area` is now nameable from where `area` is called. A struct's own methods, from lesson 7, never had this problem, because they were never routed through a trait's name in the first place; this is the one new failure mode a trait introduces, and it reads as a scope problem rather than a design problem the moment you know to look for it.

### Writing `Display` by hand, deriving the rest

Some standard-library traits are worth implementing by hand, because the implementation is a decision, and some are worth deriving, because the implementation is mechanical. `Display` is the first kind: formatting a value for a person is a choice about what that person needs to see, so the standard library gives you no derive for it at all. Trying one fails before it even reaches type checking:

```text
error: cannot find derive macro `Display` in this scope
 --> src/main.rs:1:10
  |
1 | #[derive(Display)]
  |          ^^^^^^^
```

There is simply no macro named `Display` to find; the standard library only ever expects you to write `fmt` by hand:

```rust
use std::fmt;

struct Tally {
    requests: u64,
    rejected: u64,
}

impl fmt::Display for Tally {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} requests, {} rejected", self.requests, self.rejected)
    }
}
```

`Debug`, `Clone` and `PartialEq` are the opposite case: each has an obvious, mechanical definition, so `derive` writes it precisely, one line per trait:

```rust
#[derive(Debug, Clone, PartialEq, Default)]
struct Tally {
    requests: u64,
    rejected: u64,
}
```

`Default` belongs on this list only where a sensible zero already exists, and it does here: no requests and no rejections is a legitimate starting `Tally`, not a value invented to satisfy the compiler. Deriving it requires every field to implement `Default` in turn, which `u64` does, and `Tally::default()` then builds one without you writing a constructor for the empty case. Compiling all four derives together and exercising each confirms they cooperate: `println!("{:?}", tally.clone())` prints the fields, `tally == tally.clone()` is `true`, and `Tally::default()` prints as `Tally { requests: 0, rejected: 0 }`.

### `Display` gives you `ToString` for free

The standard library ships `impl<T> ToString for T where T: Display + ?Sized`, one blanket implementation covering every type that implements `Display`. Writing `fmt::Display` by hand for `Tally` is therefore the only work needed before `.to_string()` also works on it:

```rust
let report = Tally { requests: 10, rejected: 2 };
let line: String = report.to_string();
```

`line` is `"10 requests, 2 rejected"`, produced by a method this lesson never defined; it comes from `ToString`, satisfied automatically the moment `Display` is. A type with no `Display` has no such method, and the two ways of asking for one fail differently. `println!("{}", value)` on a `#[derive(Debug)]`-only type fails at the format string itself:

```text
error[E0277]: `Sensor` doesn't implement `std::fmt::Display`
 --> src/main.rs:8:20
  |
8 |     println!("{}", s);
  |               --   ^ `Sensor` cannot be formatted with the default formatter
  |
  = note: in format strings you may be able to use `{:?}` (or {:#?} for pretty-print) instead
```

while `value.to_string()` on the same type fails as an ordinary missing method:

```text
error[E0599]: `Sensor` doesn't implement `std::fmt::Display`
   |
 2 | struct Sensor {
   | ------------- method `to_string` not found for this struct because it doesn't satisfy `Sensor: ToString` or `Sensor: std::fmt::Display`
...
 9 |     println!("{}", s.to_string());
   |                      ^^^^^^^^^ method cannot be called on `Sensor` due to unsatisfied trait bounds
   |
   = note: the following trait bounds were not satisfied:
           `Sensor: std::fmt::Display`
           which is required by `Sensor: ToString`
```

A further note in that second diagnostic points into the standard library's own source by an absolute filesystem path; it is trimmed here, and the fact it names, that `Display` is the trait `to_string` needs, is already stated in the lines kept.

### Trait methods and inherent methods can share a name

A type can have an inherent method, one written in a plain `impl` block on that type, with the same name as a method it also gets through a trait. Method-call syntax resolves this in one direction only, favouring the inherent method:

```rust
trait Countdown {
    fn start(&self) -> &'static str {
        "counting down from the trait"
    }
}

struct Timer;

impl Timer {
    fn start(&self) -> &'static str {
        "counting up from the inherent method"
    }
}

impl Countdown for Timer {}
```

```rust
println!("{}", Timer.start());
println!("{}", Countdown::start(&Timer));
```

```text
counting up from the inherent method
counting down from the trait
```

`Timer.start()` finds the inherent method before it ever looks at any trait `Timer` implements, silently, with no warning that a trait method by the same name was shadowed. The trait's version is not gone, only unreachable through dot syntax on this type; naming the trait explicitly, `Countdown::start(&Timer)`, reaches it directly. An inherent method is written closer to the type than any trait can be, and that is exactly why it wins first.

## Practice

1. ▢ Predict what `Nightingale.call()` and `Crow.call()` each print, given a trait with a default and one type that overrides it.

   ```rust
   trait Bird {
       fn sound(&self) -> &'static str;
       fn call(&self) -> String {
           format!("a bird says {}", self.sound())
       }
   }

   struct Nightingale;
   struct Crow;

   impl Bird for Nightingale {
       fn sound(&self) -> &'static str {
           "a song"
       }
   }

   impl Bird for Crow {
       fn sound(&self) -> &'static str {
           "a caw"
       }
       fn call(&self) -> String {
           format!("a crow just went {}", self.sound())
       }
   }
   ```

<details markdown="1"><summary>Check</summary>

`Nightingale.call()` prints `a bird says a song`, running the inherited default with its own `sound`. `Crow.call()` prints `a crow just went a caw`, running the version `Crow` wrote instead, which still calls `self.sound()` internally.

</details>

2. ▢ A trait `Loud` and a struct `Drum` implementing it live in a module `instruments`; a second module `player` imports `Drum` and calls `d.shout()`. Name the error code before compiling, then add the one import that fixes it.

   ```rust
   mod instruments {
       pub trait Loud {
           fn shout(&self) -> String;
       }

       pub struct Drum;

       impl Loud for Drum {
           fn shout(&self) -> String {
               String::from("BOOM")
           }
       }
   }

   mod player {
       use crate::instruments::Drum;

       pub fn play(d: Drum) {
           println!("{}", d.shout());
       }
   }
   ```

<details markdown="1"><summary>Hint</summary>

`player` imports the type `Loud` is implemented for, but not `Loud` itself.

</details>

<details markdown="1"><summary>Check</summary>

It is `E0599`, the same shape as this lesson's centrepiece: no method named `shout` found for struct `Drum` in the current scope, with a `help` suggesting `use crate::instruments::Loud;` alongside the existing import of `Drum`. Adding it compiles and prints `BOOM`.

</details>

3. ▢ Predict whether `#[derive(Display)]` on a struct compiles, and if not, what kind of error it is before the compiler even checks the struct's fields.

<details markdown="1"><summary>Check</summary>

It does not compile: error: cannot find derive macro `Display` in this scope, with no error code at all. `Display` has no derive macro anywhere in the standard library, since formatting for a person is always a decision, not a mechanical transformation of a type's fields.

</details>

4. ▢ `Sensor` below derives `Debug` only. Predict what happens for each of the two lines, and whether they fail with the same error.

   ```rust
   #[derive(Debug)]
   struct Sensor {
       id: u32,
   }

   fn main() {
       let s = Sensor { id: 7 };
       println!("{}", s);
       println!("{}", s.to_string());
   }
   ```

<details markdown="1"><summary>Hint</summary>

One line asks the formatting machinery for a trait `Sensor` does not have; the other calls a method that only exists because of that same trait.

</details>

<details markdown="1"><summary>Check</summary>

Both fail, but differently. `println!("{}", s)` gives `E0277`, `Sensor` doesn't implement `std::fmt::Display`, reported against the format string itself. `s.to_string()` gives `E0599`, an ordinary missing-method error, because `ToString`'s blanket implementation needs `Display` and `Sensor` has only `Debug`.

</details>

5. ▢ `Cup` has an inherent `fill` and also implements a trait `Container` with a default `fill`. Predict what `Cup.fill()` prints, and what would need to change to reach the trait's version instead.

   ```rust
   trait Container {
       fn fill(&self) -> &'static str {
           "filled by the trait"
       }
   }

   struct Cup;

   impl Cup {
       fn fill(&self) -> &'static str {
           "filled by the inherent method"
       }
   }

   impl Container for Cup {}
   ```

<details markdown="1"><summary>Check</summary>

`Cup.fill()` prints `filled by the inherent method`: an inherent method always wins over a trait method of the same name in dot-call syntax, with no warning that the trait's version was shadowed. Reaching the trait's version needs fully qualified syntax instead, `Container::fill(&Cup)`, which prints `filled by the trait`.

</details>

## Real-world reps

- [ ] Give your `logsum` project's summary type a hand-written `Display` implementation covering every count and every per-path total it already tracks, so that printing the finished report becomes one `println!` instead of a sequence of them.
- [ ] Derive `Default` for the accumulator your summariser builds up while it reads lines, and replace whatever manual zero-value construction that accumulator used since stage 2 with `Accumulator::default()`, or your own type's name in its place.
- [ ] Tomorrow: leave a note above the summary type saying that a later rep in this stage will change what the summariser reads from, to anything that yields lines rather than one concrete type; do not make that change now, since a different lesson owns it.

## Going further

- [Appendix C: Derivable Traits](https://doc.rust-lang.org/book/appendix-03-derivable-traits.html): what `derive` generates for `Debug`, `Clone`, `PartialEq` and `Default`, and why `Display` is deliberately absent from the list
- [ToString in std::string](https://doc.rust-lang.org/std/string/trait.ToString.html): the blanket implementation over every `Display` type, and the panic it documents if `Display` itself misbehaves
- [E0599](https://doc.rust-lang.org/error_codes/E0599.html): the diagnostic behind a missing method, whether the trait providing it is merely out of scope or never implemented at all
- [Display in std::fmt](https://doc.rust-lang.org/std/fmt/trait.Display.html): the trait behind `{}`, and the one `fmt` method it requires
- [Traits and lifetimes](../reference/traits-and-lifetimes.md): the stage 4 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
