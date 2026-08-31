---
title: 1. References Are Values
description: A variable holds a primitive or a reference, and every assignment and argument copies that
type: lesson
---

# Lesson 1. References Are Values

**Mission link:** Java has exactly one parameter-passing rule, and almost every argument about "pass by reference" comes from not having it. Settling it now removes a class of bug from every lesson after this one.
**Primary source:** [The Java Language Specification, 4.3 Reference Types and Values](https://docs.oracle.com/javase/specs/jls/se25/html/jls-4.html#jls-4.3)
**Prerequisites:** none, this is the first lesson.

## Know this

A variable in Java holds one of two things: a **primitive value**, or a **reference** to an object. There is no third case, and there is no way to hold an object itself.

```java
int count = 3;              // the variable holds the value 3
String name = "svc";        // the variable holds a reference to a String
```

The eight primitive types are `boolean`, `byte`, `short`, `char`, `int`, `long`, `float` and `double`. Everything else, including arrays, is an object and reached through a reference.

### Assignment copies what the variable holds

```java
List<String> a = new ArrayList<>();
List<String> b = a;          // copies the reference, not the list
b.add("x");
System.out.println(a);       // [x]
```

One list exists, and two variables refer to it. That is **aliasing**, and it is not a special case: it is what assignment always does. For a primitive, the copied thing is the value itself, so there is nothing to share.

### Java is pass by value, with no exceptions

Every argument is copied into the parameter. For a reference, the thing copied is the reference:

```java
static void addOne(List<String> items) {
    items.add("one");        // reaches the caller's list
}

static void replace(List<String> items) {
    items = new ArrayList<>();   // rebinds the local parameter only
    items.add("two");
}
```

`addOne` changes what the caller sees. `replace` cannot: it received a copy of the reference, and pointing that copy somewhere else has no effect on the caller's variable.

So the rule is: **a method can change the object you handed it, and can never change which object your variable refers to.** "Pass by reference" would mean the second was possible, and in Java it is not.

There is no `out` parameter and no way to swap two caller variables in a method. Return a value instead, or return a record holding both.

### Fields have defaults, local variables do not

Every field and array element is initialised before use ([JLS 4.12.5](https://docs.oracle.com/javase/specs/jls/se25/html/jls-4.html#jls-4.12.5)):

| Type | Default |
|---|---|
| numeric primitives | `0`, or `0.0` |
| `boolean` | `false` |
| `char` | the code point zero, written `\u0000` |
| any reference type | `null` |

Local variables get no default. Reading one before assigning it is a compile error, not a runtime surprise, which is the compiler doing you a favour:

```java
int total;
System.out.println(total);   // error: variable total might not have been initialized
```

That asymmetry is worth remembering: the compiler protects locals and cannot protect fields, which is why a field defaulting to `null` is the beginning of lesson 4.

## Practice

1. ▢ Predict the output.

   ```java
   int[] first = {1, 2, 3};
   int[] second = first;
   second[0] = 99;
   System.out.println(first[0]);
   ```

<details markdown="1"><summary>Check</summary>

`99`.

An array is an object, so `second` holds a copy of the reference and both variables refer to one array. The `int` elements inside it are values, but the array holding them is shared.

</details>

2. ▢ What does this print, and why do the two calls differ?

   ```java
   static void mutate(StringBuilder sb) { sb.append("!"); }
   static void reassign(StringBuilder sb) { sb = new StringBuilder("new"); }

   StringBuilder text = new StringBuilder("hi");
   mutate(text);
   reassign(text);
   System.out.println(text);
   ```

<details markdown="1"><summary>Hint</summary>

Ask, for each method, whether it reaches through the reference or writes to the parameter variable itself.

</details>

<details markdown="1"><summary>Check</summary>

`hi!`.

`mutate` called a method on the object, which is the caller's object, so the change is visible. `reassign` assigned to its own parameter, which is a copy of the reference, and the caller's `text` was never involved.

</details>

3. ▢ Write a method that swaps the values of two `int` variables belonging to the caller. If it cannot be done, say what the caller should do instead.

<details markdown="1"><summary>Check</summary>

It cannot be done. The parameters are copies, and there is nothing to assign back into.

The caller either swaps in place, or the method returns both values in something that holds two: an `int[]`, or better a record such as `record Pair(int a, int b) {}`. Wrapping the values in a mutable holder object to make it work is a workaround for a rule that is not going to change, and it reads badly.

</details>

4. ▢ Which of these compiles?

   ```java
   class Config {
       int retries;                    // a
       String name;                    // b
       void run() {
           int local;                  // c
           System.out.println(local);  // d
       }
   }
   ```

<details markdown="1"><summary>Check</summary>

Lines a, b and c compile. Line d does not: `variable local might not have been initialized`.

Fields are given defaults, so `retries` is `0` and `name` is `null` without anything being written. A declaration of a local is fine on its own, and reading it before assignment is the error.

</details>

5. ▢ A method signature is `void process(List<Order> orders)`. What may a caller assume, and what must a caller check the documentation for?

<details markdown="1"><summary>Check</summary>

A caller may assume their variable will still refer to the same list afterwards. That is guaranteed by the language.

A caller must check whether the method mutates that list: adding, removing, sorting or reordering are all possible, and the signature says nothing about them. That is why a method that mutates an argument should say so, and why a method that must not is better written to take the data and return a result.

</details>

## Real-world reps

- [ ] Write the `mutate` and `reassign` pair yourself and run it. Then make `reassign` also call `append` after the assignment, and predict what the caller sees before running it.
- [ ] Take a method in code you know that accepts a collection. Decide from its body alone whether the caller's collection can change, then check whether the documentation says so.
- [ ] Tomorrow: explain to someone, without the words "pointer" or "pass by reference", why a method can empty your list but cannot replace it. If it will not go into words, the model is not there yet.

## Going further

- [JLS 4.3, Reference Types and Values](https://docs.oracle.com/javase/specs/jls/se25/html/jls-4.html#jls-4.3): what a reference is, in the language's own words
- [JLS 4.12.5, Initial Values of Variables](https://docs.oracle.com/javase/specs/jls/se25/html/jls-4.html#jls-4.12.5): the default table, and which variables get one
- [Java Language Basics](https://dev.java/learn/language-basics/): the official tutorial for variables and types
- [Glossary](../GLOSSARY.md): `Reference` is pinned there, because carrying the word from another language is exactly the failure this lesson prevents
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
