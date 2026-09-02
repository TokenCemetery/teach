---
title: 19. JSON Columns
description: Querying a document column is ordinary SQL once you know which operator returns text and which returns JSON
type: lesson
---

# Lesson 19. JSON Columns

**Mission link:** A document column shows up in nearly every production schema eventually, holding a webhook body or an event payload nobody normalised, and the query patterns here are what separate reading one safely from silently dropping a field because a key was mistyped.
**Primary source:** [PostgreSQL, 8.14 JSON Types](https://www.postgresql.org/docs/current/datatype-json.html)
**Prerequisites:** [Lesson 1](0001-tables-rows-and-types.md), [Lesson 17](0017-lateral-joins.md)

## Warm-up

1. ▢ Lesson 1 established that declaring a column's type is a constraint the database enforces for free, rejecting a row before it is ever stored. What happens to that guarantee once the column's declared type is `jsonb`?

<details markdown="1"><summary>Check</summary>

It shrinks to almost nothing. `jsonb` only enforces that the stored value parses as JSON; once it does, the column accepts a number, a string, an object with any set of keys, or an array, so the per-field guarantees lesson 1 relied on, a fixed set of columns each with its own type, stop applying to anything inside the document.

</details>

## Know this

### `jsonb` parses, `json` validates

PostgreSQL has two JSON types, and the difference is not a formatting preference. Casting the same literal to each shows it directly:

```sql
SELECT '{"a": 1, "a": 2}'::jsonb::text AS jsonb_dup,
       '{"a": 1, "a": 2}'::json::text  AS json_dup;
```

```
jsonb_dup | json_dup
----------+-----------------
{"a": 2}  | {"a": 1, "a": 2}
```

`jsonb` keeps only the last of the two `a` keys; `json` keeps both, exactly as written. Reordering the keys in the input tells the same story from the other side:

```sql
SELECT '{"b":1,"a":2}'::jsonb::text AS jsonb_order,
       '{"b":1,"a":2}'::json::text  AS json_order;
```

```
jsonb_order      | json_order
-----------------+-------------
{"a": 2, "b": 1}  | {"b":1,"a":2}
```

`jsonb` comes back reordered into `a` before `b`; `json` comes back with the exact byte sequence submitted, including the missing spaces after the colons. `jsonb` parses the text into a structure and keeps only the structure, so a duplicate key cannot survive and key order is not part of what it stores; `json` validates that the text is well-formed and then keeps the text itself, byte for byte. `jsonb` is what to use for querying; reach for `json` only when the original document must come back byte for byte.

### The two arrow operators

`->` and `->>` are the single most useful thing in this lesson, because nearly every other JSON query is built from them. `->` returns `jsonb`, `->>` returns `text`, and `pg_typeof` proves it:

```sql
SELECT pg_typeof(payload -> 'channel')  AS arrow,
       pg_typeof(payload ->> 'channel') AS arrow2
FROM events WHERE id = 1;
```

```
arrow | arrow2
------+-------
jsonb | text
```

That is why `->` chains, each step handing another `jsonb` value to the next `->`, and `->>` only ever ends a chain, since text has nothing left to descend into. Reaching into an event's items array and out to a field's text value:

```sql
SELECT id, payload -> 'items' -> 0 ->> 'sku' AS first_sku FROM events ORDER BY id;
```

```
id | first_sku
---+----------
1  | A1
2  | A1
3  |
4  |
```

Events 1 and 2 give the first item's `sku`; events 3 and 4 give `NULL`, because event 3 has no `items` key at all and event 4's `items` is an empty array, so there is no element `0` to reach. A key that is simply absent behaves the same way: `payload -> 'nope'` is `NULL` on every row, and so is an out-of-range index such as `payload -> 'items' -> 99`. That is a design decision worth naming: reading a document never fails, so a typo in a key name is silent, returning `NULL` exactly as a genuinely missing key would.

### Containment and existence: `@>` and `?`

`@>` asks whether a document contains a given fragment, key and value together; `?` asks only whether a key is present, regardless of what it holds. Over the four events:

```sql
SELECT id FROM events WHERE payload @> '{"channel": "web"}' ORDER BY id;
SELECT id FROM events WHERE payload ? 'coupon' ORDER BY id;
```

`@>` matches events 1 and 4, the two placed through the web channel; `?` matches event 2 alone, the only one with a `coupon` key. The distinction matters once a key can hold a JSON `null`: `'{"coupon": null}'::jsonb ? 'coupon'` is true, because the key exists, while `->>` would already have turned that same value into a SQL `NULL`, indistinguishable from an absent key. `?` is the one test here that looks at the document's shape rather than its content.

### Turning a document into rows

This is the querying skill the lesson exists for: a document holds a variable number of items, and the rest of the query wants one row per item. Lesson 17 already earned `LATERAL`, and it is the tool that unnests a JSON array:

```sql
SELECT e.id AS event_id, i ->> 'sku' AS sku, (i ->> 'qty')::int AS qty
FROM events e
CROSS JOIN LATERAL jsonb_array_elements(e.payload -> 'items') AS i
ORDER BY event_id, sku;
```

```
event_id | sku | qty
---------+-----+----
1        | A1  | 2
1        | B2  | 1
2        | A1  | 5
```

`JSON_TABLE`, added to PostgreSQL in release 17, answers the identical question in one call rather than an unnest plus two casts:

```sql
SELECT e.id AS event_id, jt.sku, jt.qty
FROM events e,
     JSON_TABLE(e.payload, '$.items[*]' COLUMNS (
         sku text PATH '$.sku',
         qty  int  PATH '$.qty'
     )) AS jt
ORDER BY event_id, jt.sku;
```

returns the same three rows. What `JSON_TABLE` buys is that its columns arrive already typed: `pg_typeof(jt.qty)` is `integer`, no cast needed, where the unnested form has to write `(i ->> 'qty')::int` by hand for every field that is not text. Both forms answer the same aggregate the same way, joining document data into ordinary SQL:

```sql
SELECT sum((i ->> 'qty')::int) AS total_qty
FROM events e CROSS JOIN LATERAL jsonb_array_elements(e.payload -> 'items') AS i;
```

gives `8`, and summing `jt.qty` from the `JSON_TABLE` form above gives the same `8`.

### The path language, briefly

`jsonb_path_query`, `jsonb_path_query_array` and `jsonb_path_exists` take a path expression that can filter inside the document rather than only naming a fixed key. `jsonb_path_query(payload, '$.items[*].qty')` returns one row per matching value, three rows across events 1 and 2 (`2`, `1`, `5`). Asking for the whole set at once instead of one row per match:

```sql
SELECT id, jsonb_path_query_array(payload, '$.items[*].qty')::text AS qtys FROM events ORDER BY id;
```

```
id | qtys
---+------
1  | [2, 1]
2  | [5]
3  | []
4  | []
```

`jsonb_path_query_array` returns an empty array, not `NULL`, for both event 3, which has no `items` key, and event 4, whose `items` is already empty. A path can carry a filter in parentheses: `jsonb_path_exists(payload, '$.items[*] ? (@.qty > 3)')` matches event 2 alone, the one event with an item whose quantity exceeds three. That filter is the point of the path language: it answers a question inside the document without unnesting it first.

### What a document column costs, and what travels to SQLite

Joining an event to the order it belongs to needs an explicit cast, since a value pulled out of a document is text, never a native `bigint`:

```sql
SELECT e.id AS event_id, o.id AS order_id, o.amount
FROM events e JOIN orders o ON (e.payload ->> 'order_id')::bigint = o.id
ORDER BY e.id;
```

returns 4 rows, one per event, matching orders 101, 104, 104 and 112. Nothing enforces that the value is a real order id, because a foreign key cannot be declared on a value that lives inside a document rather than in its own column; the join above succeeds only because every payload happens to be correct. Everything else lesson 1 promised is gone the same way: no type check on any field, no `NOT NULL`, and a typo in a key reads as an absent value rather than an error, so a mistyped join condition does not fail, it simply matches nothing. Two questions follow from this cost, and this lesson deliberately answers neither: whether a column should be `jsonb` at all, rather than a set of ordinary columns, is stage 4's schema decision, and how to index one so a containment test such as `@>` stays fast is stage 6's.

The reading operators travel to SQLite largely unchanged: `->`, `->>` and `json_extract` all work there, checked directly, with the same split as PostgreSQL, `->` keeps the JSON quoting and `->>` strips it. Where PostgreSQL has `JSON_TABLE`, SQLite has `json_each` as its table-valued function for unnesting an array, and it plays the same part in a query's `FROM` clause that `jsonb_array_elements` and `LATERAL` play above.

## Practice

1. ▢ Predict the exact output of `'{"x": 1, "x": 2, "x": 3}'::jsonb::text`.

<details markdown="1"><summary>Check</summary>

`{"x": 3}`. `jsonb` keeps only the last occurrence of a duplicate key regardless of how many times it repeats, not just the second of two.

</details>

2. ▢ Predict which event ids match `payload @> '{"items": []}'`.

<details markdown="1"><summary>Hint</summary>

`@>` for arrays does not test equality; an empty array is treated as contained in any array, however many elements that array actually has.

</details>

<details markdown="1"><summary>Check</summary>

Events 1, 2 and 4, every event whose `items` is an array at all, not only event 4 whose array happens to be empty. `@>` on arrays checks that every element of the right-hand array appears on the left, and an empty right-hand array has no elements to fail that test, so it is contained in any array, empty or not. Event 3 is excluded because it has no `items` key at all, not even an empty one.

</details>

3. ▢ Predict the exact error message and SQLSTATE of `SELECT (payload ->> 'channel')::int FROM events WHERE id = 1`.

<details markdown="1"><summary>Check</summary>

`ERROR: invalid input syntax for type integer: "web"`, SQLSTATE `22P02`. `->>` always returns text, so casting it to `int` runs the ordinary text-to-integer conversion, and `web` is not a number; this is the one case where a mistake in a document query fails loudly rather than returning a silent `NULL`.

</details>

4. ▢ Predict the row count of the query below, which mistypes `order_id` as `oder_id`.

   ```sql
   SELECT e.id, o.id
   FROM events e JOIN orders o ON (e.payload ->> 'oder_id')::bigint = o.id;
   ```

<details markdown="1"><summary>Check</summary>

Zero rows. The mistyped key is absent from every payload, so `payload ->> 'oder_id'` is `NULL` on every row, the cast to `bigint` leaves it `NULL`, and `NULL = o.id` is never true for any order. The query runs without error and returns nothing, which is a harder mistake to notice than a query that fails outright.

</details>

5. ▢ Predict the exact error message and SQLSTATE of summing the `qty` column below, given that it is declared `text` rather than `int`.

   ```sql
   SELECT sum(jt.qty)
   FROM events e,
        JSON_TABLE(e.payload, '$.items[*]' COLUMNS (
            sku text PATH '$.sku',
            qty  text PATH '$.qty'
        )) AS jt;
   ```

<details markdown="1"><summary>Hint</summary>

`sum` is defined for numeric types; `JSON_TABLE` will happily hand back a text column if that is what the `COLUMNS` clause asks for, typed or not.

</details>

<details markdown="1"><summary>Check</summary>

`ERROR: function sum(text) does not exist`, SQLSTATE `42883`. Declaring the column `text` in `JSON_TABLE`'s `COLUMNS` clause is honoured exactly as written, so nothing converts it back to a number; the whole advantage of typing the column in the clause disappears if the type chosen is wrong.

</details>

6. ▢ Predict whether `'{"coupon": null}'::jsonb ? 'coupon'` is true or false.

<details markdown="1"><summary>Check</summary>

True. `?` tests only whether the key is present, never what it holds, and a key set to JSON `null` is still present. `->>` would have turned that same value into a SQL `NULL`, which reads identically to a key that was never there, so `?` is the operator that keeps the two cases apart.

</details>

## Real-world reps

- [ ] Find a document column at work and run its most common lookup key through `?` to see how often the key is actually missing rather than merely null.
- [ ] Take a query that unnests a JSON array with `LATERAL` and rewrite it with `JSON_TABLE`, checking whether any of the casts it used to need can now be dropped.
- [ ] Tomorrow: pick one field inside a document column that everyone assumes is always present, and write the one query that proves whether that assumption is actually true.

## Going further

- [8.14 JSON Types](https://www.postgresql.org/docs/current/datatype-json.html): the full comparison of `json` and `jsonb`, including the storage and indexing trade-offs stage 6 picks up
- [9.16 JSON Functions and Operators](https://www.postgresql.org/docs/current/functions-json.html): every operator and function in this lesson, plus `JSON_TABLE` and the path language in full
- [PostgreSQL 17 Release Notes](https://www.postgresql.org/docs/release/17.0/): where `JSON_TABLE` and the wider SQL/JSON feature set were added
- [JSON Functions And Operators](https://sqlite.org/json1.html): SQLite's equivalents, including `json_each` where PostgreSQL has `JSON_TABLE`
- [Beyond the basics](../reference/beyond-the-basics.md): the stage 3 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
