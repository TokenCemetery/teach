---
title: 24. Generics or dyn Trait
description: The two dispatch strategies, what each one costs, and the question that actually decides between them
type: lesson
---

# Lesson 24. Generics or dyn Trait

**Mission link:** A senior engineer who reaches for `Box<dyn Trait>` out of habit pays an indirection cost for nothing, and one who reaches for a generic out of habit discovers only when a caller needs a mixed collection that the signature cannot serve them without a rewrite.
**Primary source:** [Trait object types](https://doc.rust-lang.org/reference/types/trait-object.html)
**Prerequisites:** [Lesson 22](0022-trait-bounds-and-generic-functions.md), [Lesson 23](0023-associated-types.md)

## Warm-up

1. ▢ Lesson 22 showed that a generic function bounded by a trait compiles to one copy per concrete type it is called with, confirmed by counting symbols in the built binary. What did that count show for `total_static` called with two types, and what does it say about how the choice is made?

<details markdown="1"><summary>Check</summary>

Two symbols containing `total_static` appeared, one per concrete type, against one symbol for the `&dyn Area` version. The choice is made at compile time, per call site, and it duplicates the function body rather than sharing it.

</details>

2. ▢ Lesson 23 distinguished an associated type from a generic parameter on the same trait. What does writing `&dyn Iterator` with no further annotation report, and what does the compiler suggest to fix it?

<details markdown="1"><summary>Check</summary>

`E0191`: the value of the associated type `Item` must be specified, because a trait object needs every associated type pinned down to have a fixed layout. The suggested fix inserts `<Item = /* Type */>`.

</details>

## Know this

### The decision is heterogeneity, not speed

A generic parameter and a trait object both let a function accept anything implementing a trait, and the difference that matters is not which one runs faster. It is whether a single collection, field or return type has to hold more than one concrete type at once. A generic function bounded by `T: Area` compiles to one specialised body per `T`, so a `Vec<T>` built from it can only ever hold one concrete type: the compiler picks `T` once, at the call site, and every element must agree. A trait object erases the concrete type behind a fixed-shape pointer, so a `Vec<Box<dyn Area>>` can hold a `Square` next to a `Circle` in the same allocation. Everything else here, the sizes, the compatibility rule, the capture change, is evidence for that one sentence: reach for `dyn` when the types genuinely differ at a single point in the program, and reach for a generic everywhere else.

### Holding different types in one collection

A `Square` and a `Circle` both implementing `Area` can sit in the same `Vec` once they are behind a trait object, whether owned or borrowed:

```rust
trait Area {
    fn area(&self) -> f64;
}

struct Square { side: f64 }
impl Area for Square {
    fn area(&self) -> f64 { self.side * self.side }
}

struct Circle { radius: f64 }
impl Area for Circle {
    fn area(&self) -> f64 { std::f64::consts::PI * self.radius * self.radius }
}

fn total_dyn(shapes: &[Box<dyn Area>]) -> f64 {
    shapes.iter().map(|s| s.area()).sum()
}

let boxed: Vec<Box<dyn Area>> = vec![Box::new(Square { side: 2.0 }), Box::new(Circle { radius: 1.0 })];
total_dyn(&boxed); // 7.141592653589793
```

`&dyn Area` does the same without an allocation per element, borrowing from values owned elsewhere:

```rust
let sq = Square { side: 2.0 };
let ci = Circle { radius: 1.0 };
let refs: Vec<&dyn Area> = vec![&sq, &ci];
```

Both iterate with the same `map` and `sum` a generic would use. Asking a generic to do the job fails before the function is even called, because building the collection itself needs one type:

```rust
fn total_generic<T: Area>(shapes: Vec<T>) -> f64 {
    shapes.iter().map(|s| s.area()).sum()
}

let mixed = vec![Square { side: 2.0 }, Circle { radius: 1.0 }];
```

```text
error[E0308]: mismatched types
  --> src/main.rs:51:44
   |
51 |     let mixed = vec![Square { side: 2.0 }, Circle { radius: 1.0 }];
   |                                            ^^^^^^^^^^^^^^^^^^^^^^ expected `Square`, found `Circle`
```

`vec!` infers one element type from the first item and holds every other item to it, so a `Square` and a `Circle` cannot share a `Vec<T>` no matter what `T: Area` bound `total_generic` declares: no `T` is both types at once. That failure, not a difference in speed, is the whole argument for `dyn`.

### What a trait object is at runtime

A trait object is two pointers where a plain reference is one: a pointer to the data and a pointer to a vtable, the concrete type's table of function pointers for that trait. On this target, confirmed with `std::mem::size_of`, a `&Square` is 8 bytes, a `&dyn Area` is 16, a `Box<dyn Area>` is 16, and a `Vec<Box<dyn Area>>` is 24, the `Vec`'s own pointer, length and capacity, unaffected by what it points at. The exact numbers belong to this target; what is guaranteed everywhere is the doubling, one pointer becoming two the moment a reference or a `Box` turns into a trait object. That second pointer is also the entire cost: no boxing happens for `&dyn Area`, only for owning forms like `Box<dyn Area>`, and calling through either one is a single indirect call via the vtable rather than a search.

### Dyn compatibility

Not every trait can be turned into a trait object, and the compiler's name for the property that allows it is dyn compatibility. Older material calls this object safety, the term before a coordinated rename moved the Reference, rustc's diagnostics and rustdoc onto the new wording: the compiler's own messages changed in Rust 1.83 and rustdoc followed in 1.84, and unusually for a user-visible change neither release's notes mention it, which is worth knowing because it means the old term will keep turning up in otherwise current writing. The most common way to lose it is an associated function with no `self`, because there is no value to look up a vtable through:

```rust
trait Builder {
    fn new() -> Self;
}

fn use_builder(_b: &dyn Builder) {}
```

```text
error[E0038]: the trait `Builder` is not dyn compatible
 --> src/main.rs:5:21
  |
5 | fn use_builder(_b: &dyn Builder) {}
  |                     ^^^^^^^^^^^ `Builder` is not dyn compatible
  |
note: for a trait to be dyn compatible it needs to allow building a vtable
      for more information, visit <https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility>
 --> src/main.rs:2:8
  |
1 | trait Builder {
  |       ------- this trait is not dyn compatible...
2 |     fn new() -> Self;
  |        ^^^ ...because associated function `new` has no `self` parameter
help: consider turning `new` into a method by giving it a `&self` argument
  |
2 |     fn new(&self) -> Self;
  |            +++++
help: alternatively, consider constraining `new` so it does not apply to trait objects
  |
2 |     fn new() -> Self where Self: Sized;
  |                      +++++++++++++++++
```

The second common reason is a generic method, because a vtable has one fixed slot per method and a generic method would need one slot per type it is ever called with:

```rust
trait Processor {
    fn process<T>(&self, x: T);
}

fn use_processor(_p: &dyn Processor) {}
```

```text
error[E0038]: the trait `Processor` is not dyn compatible
 --> src/main.rs:5:23
  |
5 | fn use_processor(_p: &dyn Processor) {}
  |                       ^^^^^^^^^^^^^ `Processor` is not dyn compatible
  |
note: for a trait to be dyn compatible it needs to allow building a vtable
      for more information, visit <https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility>
 --> src/main.rs:2:8
  |
1 | trait Processor {
  |       --------- this trait is not dyn compatible...
2 |     fn process<T>(&self, x: T);
  |        ^^^^^^^ ...because method `process` has generic type parameters
  = help: consider moving `process` to another trait
```

Both diagnostics point at the same requirement, a fixed vtable, and the first `help` shows the honest fix: adding `where Self: Sized` to the offending method excludes that one method from `dyn` use, rather than reshaping the whole trait around its least flexible member.

### `impl Trait` in return position, and what changed in 2024

Returning `impl Trait` hides the concrete type while still giving the caller one fixed type, unlike `dyn`, which erases it. What such a return type may borrow from changed with the 2024 edition, in both directions, on the same source:

```rust
fn chars_of(s: &str) -> impl Iterator<Item = char> {
    s.chars()
}
```

On edition 2021 this fails, because the hidden type borrows from `s` but the written bound never says so:

```text
error[E0700]: hidden type for `impl Iterator<Item = char>` captures lifetime that does not appear in bounds
 --> src/bin/0024_capture.rs:2:5
  |
1 | fn chars_of(s: &str) -> impl Iterator<Item = char> {
  |                ----     -------------------------- opaque type defined here
  |                |
  |                hidden type `Chars<'_>` captures the anonymous lifetime defined here
2 |     s.chars()
  |     ^^^^^^^^^
  |
help: add a `use<...>` bound to explicitly capture `'_`
  |
1 | fn chars_of(s: &str) -> impl Iterator<Item = char> + use<'_> {
```

On edition 2024 it compiles unchanged, because the default now captures every lifetime in scope. The reverse case shows the cost of that default:

```rust
fn counter(v: &Vec<i32>) -> impl Fn() -> usize {
    let n = v.len();
    move || n
}

fn main() {
    let c;
    {
        let v = vec![1, 2, 3];
        c = counter(&v);
    }
    println!("{}", c());
}
```

The closure only captures `n`, a plain `usize`, and never touches `v` again, but on edition 2024 the returned `impl Fn` is still treated as if it borrowed from `v`:

```text
error[E0597]: `v` does not live long enough
  --> src/bin/0024_capture.rs:17:21
   |
16 |         let v = vec![1, 2, 3];
   |             - binding `v` declared here
17 |         c = counter(&v);
   |                     ^^ borrowed value does not live long enough
18 |     }
   |     - `v` dropped here while still borrowed
19 |     println!("{}", c());
   |                    - borrow later used here
   |
note: this call may capture more lifetimes than intended, because Rust 2024 has adjusted the `impl Trait` lifetime capture rules
   |
help: use the precise capturing `use<...>` syntax to make the captures explicit
   |
 5 | fn counter(v: &Vec<i32>) -> impl Fn() -> usize + use<> {
```

The same code compiles on edition 2021, where nothing is captured unless the bound names it. `use<...>` answers the question either edition leaves open by default: `use<'_>` says the hidden type keeps exactly that lifetime, and `use<>` says it keeps nothing. The `use<...>` syntax itself, precise capturing, stabilised in Rust 1.82 for free functions, which is why it is available as the fix on both editions rather than only on 2024.

### When each strategy is wrong

A generic is the wrong tool when nothing about the call site needs a specialised body: lesson 22 measured two compiled copies for two concrete types called through one generic function, and every further type adds another copy, code the linker carries with no caller ever needing those types to coexist. A trait object is the wrong tool in a loop that runs millions of times per second, not because the vtable lookup is slow, but because a call through a vtable is an indirect call to a function the compiler cannot see the body of at that call site, which rules out inlining the callee and everything inlining would otherwise let the compiler do. Neither cost shows up from reading the signature; both come from asking whether the call site needs one type fixed at compile time or several accepted at once, the same question this lesson opened with.

## Practice

1. ▢ This trait has a method that returns `Self` with no `self` parameter. Predict the error code before compiling `fn use_it(_c: &dyn Cache) {}` against it.

   ```rust
   trait Cache {
       fn empty() -> Self;
   }
   ```

<details markdown="1"><summary>Check</summary>

It is `E0038`: `Cache` is not dyn compatible, because `empty` has no `self` parameter, the same shape as `Builder::new` above.

</details>

2. ▢ Add `where Self: Sized` to `empty` above, following the diagnostic's second `help`, and predict whether `&dyn Cache` now compiles. Then compile it and try calling `Cache::empty()` through a `dyn Cache` value.

<details markdown="1"><summary>Hint</summary>

The constraint excludes that one method from the vtable rather than granting the whole trait an exception.

</details>

<details markdown="1"><summary>Check</summary>

`&dyn Cache` now compiles, since the trait's remaining shape allows a vtable. Calling `empty` through a `dyn Cache` value does not compile, because `where Self: Sized` excludes exactly that method, the trade the diagnostic offered rather than a way around it.

</details>

3. ▢ Predict `std::mem::size_of::<Vec<&dyn Area>>()` before running it, using what this lesson said about `Vec<Box<dyn Area>>`.

<details markdown="1"><summary>Hint</summary>

A `Vec`'s own struct is a pointer, a length and a capacity; none of those three change size depending on what the pointer points at.

</details>

<details markdown="1"><summary>Check</summary>

It is 24 on this target, identical to `Vec<Box<dyn Area>>`, because a `Vec`'s own three words do not depend on whether its element is a thin pointer, a fat pointer or anything else of a fixed size.

</details>

4. ▢ Predict which edition, 2021 or 2024, rejects `counter` and `main` as written in this lesson's `impl Trait` example, then compile on both and confirm.

<details markdown="1"><summary>Check</summary>

Edition 2024 rejects it with `E0597`, because the default capture rule ties the returned `impl Fn` to `v`'s lifetime even though the closure never uses `v` after computing `n`. Edition 2021 compiles it, because nothing captures a lifetime the bound does not name.

</details>

5. ▢ A colleague wants to change `fn render<W: std::io::Write>(&self, out: &mut W)`, called from exactly one call site with one concrete writer, to `fn render(&self, out: &mut dyn std::io::Write)`, arguing the trait object reads simpler. Using this lesson's opening decision, what question should settle it, and what is the answer here?

<details markdown="1"><summary>Check</summary>

The question is whether any call site needs more than one concrete type through this signature. With one caller and one writer type it does not, so the generic costs nothing beyond one compiled copy and the trait object buys nothing but an extra pointer and a lost inlining opportunity; the change is a style preference dressed up as a design one.

</details>

## Real-world reps

- [ ] Find a generic function in your own code bounded by a trait, invent a call site needing two different concrete types through the same value, and use this lesson's question, not a guess about speed, to decide whether it should become `Box<dyn Trait>` or stay generic.
- [ ] In your project, add a `Reporter` trait, implement it for a plain-text form and a machine-readable form, and let a runtime flag pick which one runs the summary through; choose between a generic parameter and `Box<dyn Reporter>` and write the justification as a comment, naming whether the collection question or the dispatch-cost question decided it.
- [ ] Tomorrow: rebuild this lesson's `Vec<Box<dyn Area>>` as a `Vec<&dyn Area>` borrowing from values kept alive in an outer scope, and confirm the borrow checker accepts it only once every borrowed value outlives the vector.

## Going further

- [Dyn compatibility](https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility): the Reference's rule for which traits can build a vtable
- [E0038](https://doc.rust-lang.org/error_codes/E0038.html): the diagnostic for a trait that is not dyn compatible
- [RPIT lifetime capture rules](https://doc.rust-lang.org/edition-guide/rust-2024/rpit-lifetime-capture.html): the edition guide's page on the 2024 change this lesson demonstrated
- [Using Trait Objects to Abstract over Shared Behavior](https://doc.rust-lang.org/book/ch18-02-trait-objects.html): the Book's introduction to dynamic dispatch and its trade-offs
- [Traits and lifetimes](../reference/traits-and-lifetimes.md): the stage 4 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
