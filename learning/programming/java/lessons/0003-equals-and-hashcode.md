---
title: 3. The equals and hashCode Contract
description: Break the contract and a hash collection loses your object without raising anything
type: lesson
---

# Lesson 3. The equals and hashCode Contract

**Mission link:** A `HashMap` that cannot find an entry it definitely contains is one of the hardest bugs to read, and it is always this contract. Records remove most of the work, and only if you know what they are doing for you.
**Primary source:** [`Object.hashCode`, Java SE 25 API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Object.html)
**Prerequisites:** [Lesson 2](0002-identity-and-equality.md)

## Warm-up

1. ▢ Why does `==` on two `Integer` values holding `128` return `false`?

<details markdown="1"><summary>Check</summary>

Autoboxing goes through `Integer.valueOf`, which caches only `-128` to `127`, so each `128` is a distinct object and `==` compares identity.

</details>

2. ▢ Which comparison is null-safe on both sides?

<details markdown="1"><summary>Check</summary>

`Objects.equals(a, b)`. It is `true` when both are `null`, `false` when one is, and delegates to `equals` otherwise.

</details>

## Know this

`equals` has a specified contract, and so does its relationship with `hashCode`. Both are stated on `Object` and both are enforced by nothing.

**`equals` must be:**

- **reflexive:** `x.equals(x)` is true.
- **symmetric:** `x.equals(y)` and `y.equals(x)` agree.
- **transitive:** if `x.equals(y)` and `y.equals(z)`, then `x.equals(z)`.
- **consistent:** repeated calls give the same answer while nothing relevant changes.
- **null-rejecting:** `x.equals(null)` is false, never an exception.

**And the rule that ties the two together:** if `x.equals(y)`, then `x.hashCode() == y.hashCode()`.

The reverse is not required. Two unequal objects may share a hash code, which is an ordinary collision and costs a little performance. Equal objects with different hash codes is a correctness bug.

### What breaks when only `equals` is overridden

A `HashMap` finds an entry by hashing the key to a bucket and then comparing within that bucket. If two equal keys hash differently, they land in different buckets and are never compared:

```java
class Point {
    final int x, y;
    Point(int x, int y) { this.x = x; this.y = y; }
    @Override public boolean equals(Object o) {
        return o instanceof Point p && p.x == x && p.y == y;
    }
    // no hashCode: inherits identity hashing
}

Map<Point, String> map = new HashMap<>();
map.put(new Point(1, 1), "origin-ish");
map.get(new Point(1, 1));       // null
map.containsKey(new Point(1, 1));  // false
```

Nothing throws. The map is not corrupt and answers every question consistently with its own rules. The object is simply in a bucket nobody will look in again, and a `HashSet` will happily hold two members that are `equals`.

### A mutable key is the same bug on a delay

Hashing happens once, at insertion. Change a field the hash depends on and the entry is stranded in the old bucket:

```java
Set<List<String>> set = new HashSet<>();
List<String> key = new ArrayList<>(List.of("a"));
set.add(key);
key.add("b");
set.contains(key);      // false, even though the set holds this exact object
```

So a key must be effectively immutable in every field that `equals` and `hashCode` read. That is the real reason to prefer immutable types as keys, and it is why `List` as a key is a mistake even though it is legal.

### Records do this correctly for you

```java
record Point(int x, int y) {}
```

A record generates `equals` and `hashCode` from all its components, plus `toString` and accessors. The generated `equals` compares the record's own class and every component, so it is symmetric and transitive by construction.

Two things a record does not do: it does not make components deeply immutable, so `record Order(List<Item> items)` still hands out the caller's mutable list and remains a poor key; and it does not stop you overriding the generated methods, which you should only do with a reason you can write down.

Before records, the reliable spelling was `Objects.equals` per field with `Objects.hash(...)` for the hash. That is still what you write for a class that cannot be a record.

### The `instanceof` against `getClass` decision

```java
// permits equality with subclasses, and risks breaking symmetry
if (!(o instanceof Point)) return false;

// refuses equality across classes, and keeps symmetry
if (o == null || getClass() != o.getClass()) return false;
```

If a subclass adds state and inherits `equals`, a parent instance can equal a child instance while the reverse is false, which breaks symmetry and quietly breaks collections. Two ways out: use `getClass()`, or make the class `final`. A record is implicitly final, which is one more reason it is the default answer.

## Practice

1. ▢ A class overrides `equals` and not `hashCode`. Predict the two prints, and say what is thrown.

   ```java
   Set<Point> set = new HashSet<>();
   set.add(new Point(1, 1));
   set.add(new Point(1, 1));
   System.out.println(set.size());
   System.out.println(set.contains(new Point(1, 1)));
   ```

<details markdown="1"><summary>Check</summary>

`2`, then `false`. Nothing is thrown.

Both objects hashed to different buckets, so the set never noticed they were equal, and the lookup went to a third bucket. The absence of an exception is the whole problem: the collection is behaving exactly as specified, given a key that breaks the contract.

</details>

2. ▢ Two objects are not equal but have the same `hashCode`. Is that legal, and what does it cost?

<details markdown="1"><summary>Check</summary>

Legal. Only the forward direction is required, so unequal objects may collide.

It costs a little lookup time, because the map compares with `equals` within the bucket. A `hashCode` that returns a constant is legal and turns every hash lookup into a linear scan, which is the pathological version of the same thing.

</details>

3. ▢ Which of these is safe to use as a `HashMap` key?

   - a) `record Id(long value) {}`
   - b) `record Tags(List<String> names) {}`
   - c) `class Counter { int n; }` with `equals` and `hashCode` on `n`
   - d) `StringBuilder`

<details markdown="1"><summary>Hint</summary>

Ask, for each one, whether anything the hash depends on can change after the object is in the map.

</details>

<details markdown="1"><summary>Check</summary>

**a)** only.

Option b holds a mutable list, and the generated `hashCode` reads it, so a caller who still holds that list can strand the entry. Option c is mutable in exactly the field the hash uses. Option d does not override `equals` at all, so it is identity-keyed, which is legal but almost never what anyone means.

</details>

4. ▢ This `equals` compiles and passes its unit test. Name two defects.

   ```java
   class User {
       String email;
       int loginCount;
       @Override public boolean equals(Object o) {
           if (!(o instanceof User)) return false;
           return ((User) o).email.equals(email);
       }
       @Override public int hashCode() { return email.hashCode(); }
   }
   ```

<details markdown="1"><summary>Check</summary>

First, `email` is mutable and both methods read it, so changing it after the object is in a hash collection strands the entry. Making the field `final` fixes it.

Second, both methods throw `NullPointerException` when `email` is `null`, which is a legal state for a field. `Objects.equals(((User) o).email, email)` and `Objects.hashCode(email)` fix that.

Two more worth mentioning in review: `instanceof` permits a subclass to break symmetry, and the class is a candidate for `record User(String email, int loginCount)` if `loginCount` belongs in equality, which is a design question the code has not answered.

</details>

5. ▢ You need equality on two of a class's five fields, not all five. Is a record still the right tool?

<details markdown="1"><summary>Check</summary>

Usually not, and the question is worth asking before deciding.

A record generates equality over all components, so a record whose `equals` you override is fighting its own design and confuses every reader who assumes the generated behaviour. If two fields identify the object and three describe it, that is a hint that the two are an identity worth its own type: `record UserId(String email, String tenant)`, held as one component.

If the class genuinely must be a mutable entity with partial equality, write a plain class, make the equality fields `final`, and document which fields participate. Then expect the design to be questioned, because partial equality surprises people.

</details>

## Real-world reps

- [ ] Write the broken `Point`, put it in a `HashSet` twice, and watch `size()` return 2. Then add `hashCode` and watch it return 1. Two minutes, and the bug becomes unmistakable afterwards.
- [ ] Take the mutable-key example with a `List` in a `HashSet` and reproduce the `contains` returning false for an object the set holds.
- [ ] Tomorrow: find a class in code you know that overrides `equals`. Check whether it overrides `hashCode`, whether the fields it reads are final, and whether it could have been a record.

## Going further

- [`Object.hashCode`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Object.html): the contract as specified, including what a good hash distributes
- [`Objects`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Objects.html): `equals`, `hash` and `requireNonNull`, the three helpers this lesson leans on
- [`HashMap`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/HashMap.html): what the documentation says about keys that change
- [Using Records to Model Immutable Data](https://dev.java/learn/records/): what is generated, and what is not
- [Equality, hashing and ordering](../reference/equality-hashing-and-ordering.md): the reference sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
