---
title: Traits and Lifetimes
description: The stage 4 reference sheet: the trait and dispatch decisions, the coherence rules, and how to read a lifetime error
type: reference
---

# Traits and Lifetimes

Lookup sheet for stage 4. The question it exists to answer: **dyn or generic, associated type or parameter, and what is this lifetime error actually asking for?**

## Generics or `dyn`

| Question | Reach for |
|---|---|
| Every value at this point in the program is the same concrete type, chosen once at compile time | A generic, `T: Trait` or `impl Trait` |
| A single collection, field or return type must hold more than one concrete type at once | `dyn Trait`, behind `&`, `&mut` or `Box` |

The deciding question is heterogeneity, not speed. A generic function bounded by `T: Area` compiles to one specialised body per `T`, so a `Vec<T>` built from it can only ever hold one concrete type: the compiler picks `T` once, at the call site, and `vec![Square { .. }, Circle { .. }]` fails with `E0308`, mismatched types, the moment the second element disagrees with the first. A trait object erases the concrete type behind a fixed-shape pointer, so `Vec<Box<dyn Area>>` and `Vec<&dyn Area>` can hold a `Square` next to a `Circle` in the same allocation.

| Choice | Costs |
|---|---|
| Generic (`T: Trait`) | One compiled copy of the function per concrete type that calls it, monomorphisation: two calling types produce two symbols in the binary, more code as types accumulate; every call in exchange is direct and inlinable |
| `&dyn Trait` | One extra pointer per value, a vtable pointer beside the data pointer, doubling a reference's size on a given target; no allocation |
| `Box<dyn Trait>` | The same doubled pointer, plus one heap allocation per value |

![On the left a Vec of a generic parameter, where every element is the same concrete type and a Circle is a type error. On the right a Vec of boxed trait objects, where every element is a data pointer beside a vtable pointer, all one width, pointing at values of different types and sizes.](images/dyn-uniform-elements.svg)

The costs in the table follow from the widths in the picture. A collection needs one element width, and the generic side spends it on the value itself, which fixes the type. The `dyn` side spends it on two pointers instead, which is where both the doubled reference and the heterogeneity come from: the same choice buys the one and costs the other.

Not every trait can fill the `dyn` side. A trait is dyn compatible only if every method can sit in a fixed vtable slot, so an associated function with no `self` (`E0038`, naming the method, with a `help` suggesting either a `&self` parameter or `where Self: Sized` to exclude that one method) and a generic method (the same code, the same `where Self: Sized` escape) are the two common ways to lose it. "Object safety" is the same property under its pre-rename name; current rustc and rustdoc call it dyn compatibility instead.

## Associated type or generic parameter

| Question | Reach for |
|---|---|
| An implementation has exactly one sensible answer for this placeholder | An associated type, `type Item;` |
| More than one answer is legitimate, and a caller or a second `impl` should say which | A generic parameter, `Trait<Rhs = Self>` |

`Iterator` is the associated-type case: a type produces one kind of item, decided once when `Iterator` is implemented, so writing `Iterator<u32>` as though `Item` were a parameter fails with `E0107`, trait takes 0 generic arguments, and the fix is `Iterator<Item = u32>`; leaving a trait object's associated type unspecified, `&dyn Iterator` with nothing further, fails the other way, `E0191`, needing `<Item = ...>` before the vtable has a fixed shape. `Add`, declared `trait Add<Rhs = Self>`, is the generic-parameter case: the standard library implements it once for `Point + Point` under the default `Rhs`, and separately for `Millimeters + Meters`, two equally sensible right-hand sides for the same left-hand type, a shape no associated type could express since an associated type is chosen once by the implementer, never once per pair. `Deref`, `type Target: ?Sized;`, is a second associated-type case: a smart pointer dereferences to exactly one target.

A bound naming two traits that each declare an associated type of the same name needs the fully qualified form, `<I as Iterator>::Item` rather than the ambiguous `I::Item` (`E0221`, ambiguous associated type).

## Coherence

For any trait and any type, at most one implementation exists for the whole crate graph, checked at compile time as the orphan rule: an `impl` is valid only if the trait is local, or the implementing type has a local type among its parameters. Breaking both at once, such as `impl fmt::Display for Vec<u8>`, is `E0117`, only traits defined in the current crate can be implemented for types defined outside of it.

| Escape | Looks like | Gives up |
|---|---|---|
| Local trait, an extension trait | `impl Shout for str` | Nothing; the foreign type keeps every existing method, plus the new one, once the trait is in scope at the call site |
| Local type, the newtype pattern | `struct Wrapper(Vec<String>);`, then `impl Display for Wrapper` | Every method the wrapped type had; `w.len()` is `E0599` until forwarded by hand or reached through `Deref` |

Forwarding a wrapped method by hand is the safer default over `Deref`: `Deref` hands over every method the target type has, present and future, and a later inherent method on the wrapper with the same name silently wins over the forwarded one, with nothing at the call site to say a collision happened.

A blanket implementation, `impl<T: Display> Label for T`, coexists with a concrete `impl Label for Tag` for as long as `Tag` has no `Display`; adding `Display` for a completely unrelated reason turns the pair into `E0119`, conflicting implementations of trait `Label` for type `Tag`, naming the blanket impl as the first one. A blanket implementation is a commitment made once on behalf of every type that will ever satisfy its bound, including ones that do not exist yet, foreclosing their own instance of the same trait.

## Reading a lifetime error

| Shape | Code | What the diagnostic carries | Honest fix | Workaround it tempts |
|---|---|---|---|---|
| Return borrows, signature does not say from where | `E0106` | Which named inputs could be the source, `borrowed from `a` or `b`` | Name one lifetime shared by every candidate input and the return | An owned return type, right only when independence from the input is actually wanted |
| A reference returned with nothing borrowed on the way in | `E0106`, then `E0515` once a lifetime is added | "there is no value for it to be borrowed from"; one `help` offers `'static`, "uncommon unless you're returning a borrowed value from a `const` or a `static`", a second offers an owned return type | Return the owned value, or take the destination as a `&mut` parameter to write into | `Box::leak`, which compiles and runs, at the cost of an allocation the program never frees |
| A borrowing struct's method does not repeat its own promise | `E0621` | "lifetime `'a` required", naming the parameter that needs it | Add the struct's own lifetime to that parameter's type | Cloning the value into an owned field, correct only once the struct is meant to own what it collects |
| A type annotation elsewhere pins the lifetime before the value exists | `E0597` | The accusation sits on the annotation, "type annotation requires that `x` is borrowed for `'static`", not on the line underlined | Drop the pinning annotation and let inference find the shortest lifetime every use actually needs | A `'static` literal, or `.clone()` on every value pushed |
| A closure fixed to one lifetime, against a bound asking for every lifetime | No code: "implementation of `Fn` is not general enough" | Two `note` lines contrasting "for any lifetime `'1`" against "for some specific lifetime `'2`" | Remove the explicit annotation and let the closure's parameter stay elided | None offered; the bound is higher-ranked, `for<'a> Fn(&'a str) -> usize`, named here but not written out until a later stage |
| Two fields of the same struct borrowing from each other | `E0505` | "move out of ... occurs here" against "borrow later used here" | Restructure so nothing borrows its own sibling field; no lifetime annotation changes this, since the struct must exist before anything could name a lifetime pointing back into it | Cloning the source, which produces two independent values rather than the self-reference asked for |

Two notation habits are worth reading rather than writing. `'1`, `'2` and further numbers are the compiler's own names for lifetimes the source never named, scratch notation for one diagnostic rather than something to write yourself; match a number to source through its own "let's call the lifetime of this reference" note, not by declaration order. `'_` is the same elision the compiler already runs, spelled out explicitly in a type position, `Formatter<'_>`, `Cow<'_, str>`, rather than left implicit; it creates nothing new, it only names what elision would have inferred anyway.

## Elision, checked against a signature

Three rules, applied in order; a signature either resolves under them or needs a name.

1. Every elided lifetime among the parameters becomes its own, independent lifetime parameter.
2. If exactly one lifetime appears among the parameters, elided or named, every elided output lifetime is assigned that one.
3. On a method, if the receiver is `&self` or `&mut self`, every elided output lifetime is assigned the receiver's.

`fn split_fields(line: &str) -> Result<(&str, &str, &str), LineError>` resolves under rule two: one input lifetime, so every slice in the returned tuple takes it. `fn name(&self) -> &str` resolves under rule three. `fn longest(a: &str, b: &str) -> &str` resolves under neither, two input lifetimes and a return that could match either, which is exactly `E0106`. Rule three is a default, not a law: a method whose body returns a parameter instead of something borrowed from `self` fails with "lifetime may not live long enough" even though nothing looks wrong at the return line itself.

## Owned, borrowed or `Cow`

| Question | Reach for |
|---|---|
| The value is read and dropped before its source goes away | A borrowing type, `struct Record<'a> { path: &'a str }` |
| The value must outlive the source it was built from | An owning type, `struct Record { path: String }` |
| A common case never allocates, a rarer case must, and both happen often enough to matter | `Cow<'a, str>`, `Borrowed` until something forces `Owned` |

This is a lifetime question, not a performance ruling in the abstract, decided by which of two things outlives the other. `Cow`'s cost is the match every reader of the type must now perform; reach for it only when a real caller's input is sometimes clean and sometimes not, since an owned copy on every call would waste the common path to cover a rare one. A generic struct pairing a type parameter with a borrow sometimes needs to say the parameter itself outlives the borrow, `T: 'a`, spelled out wherever the compiler cannot infer it from a field (`E0309`, naming the parameter type that may not live long enough). `T: 'static` is the same bound at the far end: a claim that `T` holds no borrow shorter than `'static`, not a claim that any particular value lives forever, which is why an owned `String` satisfies it unconditionally, even one created and dropped inside a few lines.

## Deliberately not in this stage

| Topic | Where it went |
|---|---|
| Variance, and the errors that look like a lifetime problem but are really about mutability | Stage 8, Judgment |
| Writing an explicit `for<'a>` bound | Stage 8, Judgment; this stage only names a higher-ranked bound when a diagnostic forces it |
| Generic associated types | Out of the arc entirely, noted only where the standard library already relies on one |
| Sharing one value across owners, `Rc`, `RefCell`, `Arc`, `Mutex` | Stage 5, Sharing and threads |
| Pinning a self-referential state | Stage 6, Async |

## Where the project should be

The stage 4 slice of the arc's rep project, `logsum`, takes its input from anything that yields lines rather than from one concrete type, and borrows the line rather than owning a copy of every field. See [the project](the-project.md) for the full brief and the state expected at the end of every stage.
