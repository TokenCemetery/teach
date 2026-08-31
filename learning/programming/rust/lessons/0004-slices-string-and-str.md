---
title: 4. Slices, String and str
description: A slice is a borrowed view with a length, and taking &str in an API costs callers nothing
type: lesson
---

# Lesson 4. Slices, String and str

**Mission link:** `String` against `&str` is the first API design decision every Rust programmer makes, and getting it wrong forces every caller to allocate. It is also where UTF-8 stops being an implementation detail.
**Primary source:** [The Rust Programming Language, The Slice Type](https://doc.rust-lang.org/book/ch04-03-slices.html)
**Prerequisites:** [Lesson 3](0003-borrowing.md)

## Warm-up

1. ▢ State the borrow rule in one sentence.

<details markdown="1"><summary>Check</summary>

Any number of shared borrows or exactly one mutable borrow of a value, never both, and every borrow must be valid while it is used.

</details>

2. ▢ When does a borrow end?

<details markdown="1"><summary>Check</summary>

At its last use, not at the end of the enclosing scope.

</details>

## Know this

A **slice** is a borrowed view into a contiguous sequence: a pointer plus a length, and no ownership. Two spellings matter constantly:

| Owned | Borrowed slice |
|---|---|
| `String` | `&str` |
| `Vec<T>` | `&[T]` |
| `[T; N]` (an array, owned, fixed size) | `&[T]` |

```rust
let owned = String::from("hello world");
let word: &str = &owned[0..5];      // borrows the first five bytes
let all: &str = &owned;             // borrows the whole thing
```

`&owned[0..5]` allocates nothing. It is a pointer into the existing buffer and a length, which is why slicing is cheap and why the slice cannot outlive what it borrows.

### Take `&str`, return `String`

This is the rule of thumb worth internalising immediately:

```rust
fn shout(s: &str) -> String {       // good
    s.to_uppercase()
}

fn shout_bad(s: String) -> String { // forces every caller to give up ownership
    s.to_uppercase()
}
```

A caller with a `String` can pass it to the first version with `&s` and keep it. A caller with a literal, which is already a `&'static str`, can pass it directly. A caller of the second version must either give up their `String` or clone it, and a caller with a literal must allocate one to call the function at all.

The mechanism that makes `&String` work where `&str` is expected is **deref coercion**: the compiler inserts a conversion because `String` dereferences to `str`. The same applies to `&Vec<T>` where `&[T]` is expected. So taking the borrowed slice type in a signature costs callers nothing and permits more of them.

The same reasoning generalises: prefer `&[T]` over `&Vec<T>`, and prefer `&str` over `&String`. Taking `&Vec<T>` restricts you to callers who have a `Vec` specifically, and buys nothing in return.

### String is UTF-8, so indexing is not what you expect

`String` and `str` are guaranteed to hold valid UTF-8, and the operations follow from that guarantee:

```rust
let s = String::from("héllo");

s.len();                    // 6, BYTES not characters
s.chars().count();          // 5, Unicode scalar values

let c = s[0];               // error: `String` cannot be indexed by `usize`
let sub = &s[0..2];         // compiles, and PANICS: not a char boundary
```

There is no `Index<usize>` for `String`, deliberately: a byte is not a character, and returning one would be a lie. Range slicing exists and is checked at run time, so slicing across a multi-byte character panics rather than producing invalid UTF-8.

What to write instead:

```rust
s.chars().nth(0);           // Option<char>, and O(n)
s.chars().next();           // Option<char>, the idiomatic "first character"
s.char_indices();           // (byte offset, char) pairs, for real work
s.split_whitespace();       // almost always what you actually wanted
```

One more honest caveat: `chars()` yields Unicode scalar values, not what a reader would call characters. An emoji with a modifier, or an accent written as a combining mark, is several `char`s and one grapheme cluster. The standard library deliberately stops at scalar values; grapheme segmentation lives in a crate. So "count the characters" is an under-specified request, and the right answer depends on why you are counting.

### Slices of anything, and the length that travels with them

```rust
fn sum(values: &[i32]) -> i32 {
    values.iter().sum()
}

let v = vec![1, 2, 3];
let a = [1, 2, 3];
sum(&v);            // Vec coerces
sum(&a);            // array coerces
sum(&v[1..]);       // a sub-slice, no copy
```

One function accepts a `Vec`, an array, and any window into either, with no allocation and no generics. That is the payoff for the owned-and-borrowed split, and it is the same idea as `&str`.

Because the length travels with the pointer, indexing is bounds-checked: `values[10]` on a slice of three panics with a clear message rather than reading whatever is there. Use `values.get(10)` when out of range is a normal case, and it returns `Option<&i32>`.

## Practice

1. ▢ Which signature would you write, and why?

   ```rust
   fn count_words(text: String) -> usize
   fn count_words(text: &String) -> usize
   fn count_words(text: &str) -> usize
   ```

<details markdown="1"><summary>Check</summary>

`fn count_words(text: &str) -> usize`.

It reads without taking ownership, and it accepts the widest set of callers: a `String` via deref coercion, a literal directly, and a slice of either. `&String` accepts strictly fewer callers and gains nothing. Taking `String` by value forces a caller with a literal to allocate and a caller with a `String` to give it up or clone it.

</details>

2. ▢ Predict each line.

   ```rust
   let s = String::from("héllo");
   println!("{}", s.len());
   println!("{}", s.chars().count());
   println!("{}", &s[0..2]);
   ```

<details markdown="1"><summary>Hint</summary>

`é` is not one byte. Work out how many bytes it takes in UTF-8 before predicting the third line.

</details>

<details markdown="1"><summary>Check</summary>

`6`, then `5`, then a panic: `byte index 2 is not a char boundary`.

`é` occupies two bytes, so the string is six bytes and five scalar values. The range `0..2` ends in the middle of `é`, and rather than hand back invalid UTF-8, the slice operation panics.

`&s[0..3]` would print `hé`, since three bytes is the boundary after `é`.

</details>

3. ▢ Which calls compile?

   ```rust
   fn sum(v: &[i32]) -> i32 { v.iter().sum() }

   let vec = vec![1, 2, 3];
   let arr = [1, 2, 3];
   ```

   - a) `sum(&vec)`
   - b) `sum(&arr)`
   - c) `sum(&vec[1..])`
   - d) `sum(vec)`

<details markdown="1"><summary>Check</summary>

**a)**, **b)** and **c)** compile. **d)** does not: a `Vec<i32>` is not a `&[i32]`, and passing it by value would be a move into a parameter of the wrong type.

a and b work by deref coercion, c is an ordinary sub-slice. The lesson is how much reach one `&[T]` parameter has.

</details>

4. ▢ This function takes ownership unnecessarily. Rewrite it and say what changes for its callers.

   ```rust
   fn is_admin(email: String) -> bool {
       email.ends_with("@admin.example.com")
   }
   ```

<details markdown="1"><summary>Check</summary>

```rust
fn is_admin(email: &str) -> bool {
    email.ends_with("@admin.example.com")
}
```

Callers stop giving up ownership. `is_admin(&user.email)` now works without cloning, and `is_admin("x@admin.example.com")` works without allocating a `String` first. Nothing is lost, because the function only ever read the value.

The original signature is the single most common unnecessary-allocation pattern in early Rust, and it usually appears because the author was fixing a move error the wrong way round.

</details>

5. ▢ A requirement says "truncate the display name to 10 characters". Name the three things you would have to decide before writing it.

<details markdown="1"><summary>Check</summary>

First, what a character means: bytes, `char` values, or grapheme clusters. Ten bytes can split a multi-byte character and panic; ten `char`s can split an emoji from its modifier; ten graphemes needs a crate, because the standard library stops at scalar values.

Second, what to do at the boundary: `&s[..10]` panics on a non-boundary, so the safe forms are iterating with `chars()` and taking ten, or using `char_indices` to find a real byte offset.

Third, what the truncation is for. Display width is a different question again: two `char`s can occupy one column, and some occupy two, so a layout constraint is not solved by counting anything in the string alone.

The reason to ask all three is that the requirement as written cannot be implemented correctly, and any code that pretends otherwise is choosing an interpretation silently.

</details>

## Real-world reps

- [ ] Write the `héllo` example and make it panic. Then find the byte offset that does work, using `char_indices`.
- [ ] Write a function taking `&[i32]` and call it with a `Vec`, an array, and a sub-slice of each.
- [ ] Tomorrow: find a function in any Rust you can read that takes `String` or `&Vec<T>`. Decide whether the borrowed slice type would have worked.

## Going further

- [The Slice Type](https://doc.rust-lang.org/book/ch04-03-slices.html): slices as borrowed views, with the string-slice case worked through
- [Storing UTF-8 Encoded Text with Strings](https://doc.rust-lang.org/book/ch08-02-strings.html): why indexing is refused, and what to do instead
- [`str`](https://doc.rust-lang.org/std/primitive.str.html) and [`String`](https://doc.rust-lang.org/std/string/struct.String.html): the two APIs side by side
- [`slice`](https://doc.rust-lang.org/std/primitive.slice.html): every slice method, including `get` and the chunking family
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
