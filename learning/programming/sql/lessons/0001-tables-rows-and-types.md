---
title: 1. Tables, Rows and Types
description: A column type is a constraint you get for free, and the wrong one is hard to undo
type: lesson
---

# Lesson 1. Tables, Rows and Types

**Mission link:** Every later skill in this workspace reads a table definition. The type of each column decides what the database can guarantee, what it can index, and what it will silently accept, and changing one on a large live table is the hardest routine operation there is.
**Primary source:** [PostgreSQL, 5.1 Table Basics](https://www.postgresql.org/docs/current/ddl-basics.html)
**Prerequisites:** none, this is the first lesson.

## Know this

A table is a named collection of rows. Every row has the same columns, and every column has a type the database enforces on every write. That last part is the whole reason to care about types: a type is a constraint you do not have to remember to check.

The schema this workspace uses throughout:

```sql
CREATE TABLE customers (
    id      bigint PRIMARY KEY,
    email   text NOT NULL UNIQUE,
    country text
);

CREATE TABLE orders (
    id          bigint PRIMARY KEY,
    customer_id bigint NOT NULL REFERENCES customers (id),
    amount      numeric(12, 2) NOT NULL,
    shipped_at  timestamptz
);
```

Read the nullability, because it is where the meaning lives. `email` is required. `country` may be absent, meaning unknown. `shipped_at` may be absent, meaning not yet shipped. Lesson 3 is about what the database does with those absences.

### The type choices that matter

**Text.** Use `text`. In PostgreSQL, `varchar(n)` and `text` are the same type with a length check bolted on, and there is no performance difference between them. Add a length limit only when the limit is a real business rule, and prefer a `CHECK` constraint when it is, because it can be changed. Avoid `char(n)` entirely: it pads values with spaces, which surprises every comparison afterwards ([Don't Do This](https://wiki.postgresql.org/wiki/Don%27t_Do_This)).

**Numbers.** `numeric` for money and for anything counted in exact units. `real` and `double precision` are binary floats, so `0.1 + 0.2` is not `0.3` and a sum of a million rows drifts. Use `bigint` for identifiers rather than `int`, because the day a table passes two billion rows is not the day you want to alter its primary key.

**Time.** `timestamptz`, always, for a moment in time. It stores an absolute instant and converts on the way in and out. Plain `timestamp` stores wall-clock text with no zone, which means the same value means different instants depending on who reads it. Use `date` when there genuinely is no time of day.

**Booleans and enumerations.** `boolean` for true and false. For a small closed set of states, either a `text` column with a `CHECK` constraint or a lookup table, both of which can gain a value without an exclusive lock, unlike a native `enum` type in some engines.

### Types differ between engines, and one differs radically

SQLite does not enforce column types the way the standard describes. Its types are advisory affinities, so a text value can land in an integer column unless the table is declared `STRICT` ([Datatypes in SQLite](https://www.sqlite.org/datatype3.html)). That is a deliberate design choice and it is the single biggest difference to keep in mind when a rep runs on SQLite and the lesson claims a type guarantees something.

### Inserting and reading

```sql
INSERT INTO customers (id, email, country)
VALUES (1, 'ada@example.com', 'GB'),
       (2, 'grace@example.com', NULL);

SELECT id, email FROM customers;
```

Name the columns in an `INSERT`. The shorter `INSERT INTO customers VALUES (...)` depends on column order, so it breaks the day someone adds a column, and it breaks silently if the new column happens to be type-compatible.

A row is not an object with an identity you can rely on. Two rows with identical column values are two rows, indistinguishable to the database, unless a key says otherwise. That is lesson 6, and it is why lesson 4 has to explain that a table is a bag rather than a set.

## Practice

1. ▢ For each column, name the type you would choose and say why in one clause: a product price, a user's country, an order identifier, the moment a payment settled, a phone number.

<details markdown="1"><summary>Check</summary>

- Price: `numeric`. Exact decimal arithmetic, because a float cannot represent most prices exactly.
- Country: `text`, with a `CHECK` against a code list or a foreign key to a lookup table. Codes are text, and the constraint is what makes them valid.
- Order identifier: `bigint`. Room to grow, and integers compare and index cheaply.
- Settlement moment: `timestamptz`. An absolute instant, unambiguous across zones.
- Phone number: `text`. It is not a number: it has leading zeros, plus signs and spaces, and nobody does arithmetic on it.

The phone number is the one people get wrong, and the reason is the general rule: store as a number only what you will compute with.

</details>

2. ▢ Why would you not use `double precision` for an order total?

<details markdown="1"><summary>Hint</summary>

Ask what happens when you add up a million rows, and whether two systems that each store the same total will agree it is the same.

</details>

<details markdown="1"><summary>Check</summary>

Because binary floating point cannot represent most decimal fractions exactly, so individual values are already approximations and errors accumulate across a `SUM`. Two totals that should match compare unequal, and a rounded report disagrees with the sum of its rows.

`numeric` stores decimal digits exactly, at the cost of slower arithmetic, which is the right trade for money in almost every system.

</details>

3. ▢ Which is the better reason to write `varchar(50)` instead of `text` in PostgreSQL?

   - a) It uses less storage
   - b) It is faster to compare and index
   - c) A business rule caps the value at 50
   - d) It documents the intended size

<details markdown="1"><summary>Check</summary>

**c)** A business rule caps the value at 50.

Options a and b are false: the two are the same type internally, and the length limit adds a check rather than removing work. Option d is a real motive and a weak one, because the limit will be enforced whether or not it is still true, and raising it later requires altering the column.

When the cap is a real rule, a `CHECK` constraint says the same thing and can be modified without changing the column's type.

</details>

4. ▢ A table has `created_at timestamp` and stores the value returned by the application server. The application is deployed in two regions. Name the failure.

<details markdown="1"><summary>Check</summary>

`timestamp` without a zone stores what it was given and attaches no meaning to it, so rows written from two regions record two different instants under the same-looking value. Sorting by `created_at` no longer orders events, and any window computed from it is wrong by the offset between the regions.

There is no query that repairs this after the fact, because the information about which zone each row came from was never stored. That is why the choice of `timestamptz` matters at `CREATE TABLE` time and not later.

</details>

5. ▢ A rep runs on SQLite and inserts the text `'abc'` into a column declared `INTEGER`. What happens, and what does that mean for the rest of this workspace?

<details markdown="1"><summary>Check</summary>

It succeeds. SQLite applies type affinity rather than enforcement, so a value it cannot convert is stored as text in an integer column. Declaring the table `STRICT` makes it reject the value instead.

For this workspace it means a claim like "the type prevents that" is engine-specific. PostgreSQL is the reference engine, and whenever a lesson depends on the engine enforcing something rather than merely preferring it, the lesson says which engine it is talking about.

</details>

## Real-world reps

- [ ] Create both tables from the lesson in a local database and insert the two customers. Then try to insert a customer with a `NULL` email and read the error text.
- [ ] Insert `0.1` and `0.2` into a `double precision` column and a `numeric` column, sum each, and compare the results.
- [ ] Tomorrow: open a schema you work with and find one column whose type you would change. Write down what would break during the change, not just what would be better after it.

## Going further

- [5.1 Table Basics](https://www.postgresql.org/docs/current/ddl-basics.html): creating tables, and what a column definition means
- [Chapter 8, Data Types](https://www.postgresql.org/docs/current/datatype.html): every type, with the trade-offs stated
- [8.1 Numeric Types](https://www.postgresql.org/docs/current/datatype-numeric.html): exactly where `numeric` and the float types differ
- [Don't Do This](https://wiki.postgresql.org/wiki/Don%27t_Do_This): the type choices practitioners regret, with reasons
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
