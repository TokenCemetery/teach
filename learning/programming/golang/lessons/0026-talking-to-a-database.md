---
title: 26 — Talking to a Database
description: sql.DB is a pool, every call takes a context, and an unclosed Rows holds a connection
type: lesson
---

# Lesson 26 — Talking to a Database

**Mission link:** The database is where a Go service's concurrency model meets a resource with a hard limit. Most production database incidents are pool configuration and unclosed rows, not queries.
**Primary source:** [Accessing relational databases — The Go Authors](https://go.dev/doc/database/)
**Prerequisites:** [Lesson 25](0025-graceful-shutdown.md), [Lesson 9](0009-wrapping-is-and-as.md)

## Warm-up

1. ▢ Why must `srv.Shutdown` get a fresh context rather than the cancelled one?

<details markdown="1"><summary>Check</summary>

An already-cancelled context makes `Shutdown` return immediately, dropping every in-flight request. Use `context.WithTimeout(context.Background(), d)`.

</details>

2. ▢ What does a failing liveness probe mean, and what does a failing readiness probe mean?

<details markdown="1"><summary>Check</summary>

Liveness: restart me. Readiness: take me out of rotation. Dependency checks belong in readiness — putting them in liveness turns a database blip into a restart storm.

</details>

## Know this

### `*sql.DB` is a pool, not a connection

```go
db, err := sql.Open("pgx", dsn)   // does not connect
if err != nil {
    return fmt.Errorf("open db: %w", err)
}
defer db.Close()

if err := db.PingContext(ctx); err != nil {   // this connects
    return fmt.Errorf("ping db: %w", err)
}
```

`sql.Open` validates arguments and returns immediately — it does not talk to the database, which is why a wrong password produces a healthy-looking startup and a failure on the first query. `Ping` at startup, per Lesson 23.

A `*sql.DB` is safe for concurrent use and is meant to be **one per database, for the life of the process**. Passing it around is correct; opening one per request is a bug that exhausts connections.

### Configure the pool deliberately

```go
db.SetMaxOpenConns(25)
db.SetMaxIdleConns(25)
db.SetConnMaxLifetime(30 * time.Minute)
db.SetConnMaxIdleTime(5 * time.Minute)
```

The default for `MaxOpenConns` is **unlimited**, which means a traffic spike opens connections until the database refuses them — and a database refusing connections fails everything, not just the excess. Set it to something your database can serve, sized against `max_connections` divided across every instance and every other client.

Set `MaxIdleConns` to the same value as `MaxOpenConns` unless you have a reason not to; a lower idle count makes the pool close and reopen connections under normal load, and connection setup with TLS is not cheap. `ConnMaxLifetime` keeps connections rotating so a failover or a DNS change is picked up.

### Always the context variants

`QueryContext`, `QueryRowContext`, `ExecContext`, `BeginTx`. The non-context forms exist for compatibility and give up the one thing that makes a database call safe under load: cancellation. With a context, a client disconnect or a request deadline stops the query rather than leaving it running.

### Rows hold a connection until closed

```go
rows, err := db.QueryContext(ctx, `SELECT id, name FROM users WHERE org = $1`, orgID)
if err != nil {
    return nil, fmt.Errorf("query users: %w", err)
}
defer rows.Close()

var users []User
for rows.Next() {
    var u User
    if err := rows.Scan(&u.ID, &u.Name); err != nil {
        return nil, fmt.Errorf("scan user: %w", err)
    }
    users = append(users, u)
}
return users, rows.Err()
```

Three things in that block are load-bearing:

- **`defer rows.Close()`** — an open `Rows` holds a pooled connection. Leak enough and the pool is empty while the database is idle, which looks like a database problem and is not.
- **`rows.Err()`** — `rows.Next()` returns false both at the end of the result set and on error. Without the check, a mid-iteration failure looks like a short result. Skipping it is the most common silent data bug in Go database code.
- **Placeholders, never concatenation.** `$1` for Postgres, `?` for MySQL and SQLite. String-building a query with user input is SQL injection, and no amount of escaping by hand is the right answer.

`QueryRowContext` for a single row defers its error to `Scan`, which returns `sql.ErrNoRows` when there is nothing. Translate that at the boundary into your own `ErrNotFound`, per Lesson 9 — otherwise `database/sql` is part of your package's API.

### Transactions

```go
tx, err := db.BeginTx(ctx, nil)
if err != nil {
    return fmt.Errorf("begin: %w", err)
}
defer tx.Rollback()   // no-op after a successful Commit

if _, err := tx.ExecContext(ctx, `UPDATE ...`); err != nil {
    return fmt.Errorf("update: %w", err)
}
return tx.Commit()
```

`defer tx.Rollback()` immediately after `BeginTx` is the idiom: it covers every early return and every panic, and it does nothing once `Commit` has succeeded. A transaction holds one connection for its whole life, so a transaction that spans an HTTP call to another service is holding a scarce resource across a network — the Lesson 19 rule about locks, applied to a pool.

### NULL

A SQL `NULL` will not scan into a `string`. Use `sql.NullString` and friends, or a pointer, or fix the schema with `NOT NULL DEFAULT ''` — which is usually the better answer, because a nullable column that is never meaningfully null is a lie the type system has to carry forever.

### Drivers and helpers

`database/sql` needs a driver: `github.com/jackc/pgx/v5` for Postgres is the current default choice. On top of it, `sqlx` reduces `Scan` boilerplate and `sqlc` generates typed code from SQL. All are optional — the standard library is entirely usable, and the concepts above do not change under any of them.

## Practice

1. ▢ `sql.Open` returns no error but the first query fails with an authentication error. Why?

<details markdown="1"><summary>Check</summary>

`sql.Open` does not connect. It parses the DSN and prepares the pool; the first actual connection happens lazily on first use.

`db.PingContext(ctx)` at startup forces it, turning a runtime surprise into a failed deploy — the Lesson 23 rule about validating what you control.

</details>

2. ▢ Under load, queries start failing with pool timeouts while the database itself is idle. What do you look for?

<details markdown="1"><summary>Check</summary>

A `Rows` that is not closed. Each leaked one holds a connection out of the pool forever, so the pool drains while the database sees almost no work.

Check for a `QueryContext` without a `defer rows.Close()`, and for early returns between the query and the defer. A transaction that is neither committed nor rolled back does the same thing.

</details>

3. ▢ What does `rows.Err()` tell you that the loop does not?

   - a) Whether any rows matched the query at all
   - b) Whether iteration stopped early from an error
   - c) Whether the connection returned to the pool
   - d) Whether the scan destination types were wrong

<details markdown="1"><summary>Check</summary>

**b)** Whether iteration stopped early from an error.

`rows.Next()` returns false for two different reasons — the result set ended, or something failed — and the loop cannot tell them apart. Without `rows.Err()`, a network failure halfway through 10,000 rows returns 4,000 rows and a nil error, and the caller has no way to know.

Option a is answered by the length of the result. Option d surfaces from `Scan` directly.

</details>

4. ▢ Why is `db.SetMaxOpenConns` worth setting even when the default is "unlimited"?

<details markdown="1"><summary>Check</summary>

Because unlimited means a traffic spike opens connections until the database refuses them, and a database at its connection limit fails *every* client — including the ones that were behaving.

Bounding the pool converts an unbounded failure into local queuing: requests wait for a connection, deadlines fire, and the database keeps serving. It is the same bounded-fan-out argument as Lesson 15, applied to a resource someone else owns.

</details>

5. ▢ Interleaving Lesson 9: your repository returns `sql.ErrNoRows` to the HTTP layer. What is wrong with that?

<details markdown="1"><summary>Check</summary>

`database/sql` is now part of the repository's API. Every caller matching on `sql.ErrNoRows` breaks the day you move to a driver that returns something else, or to a cache in front of the query — with no compile error.

Translate at the boundary: match `sql.ErrNoRows` inside the repository and return your own `store.ErrNotFound`. One small mapping there keeps the persistence choice replaceable.

</details>

## Real-world reps

- [ ] Write a repository with `Get` and `List` against SQLite or Postgres. Include `defer rows.Close()`, `rows.Err()`, and the `sql.ErrNoRows` translation.
- [ ] Set `SetMaxOpenConns(2)` and fire twenty concurrent requests. Watch them queue rather than fail, then add a short context deadline and watch them fail cleanly instead of piling up.
- [ ] Tomorrow: check `SetMaxOpenConns` across every service that shares one database, and add up the totals against the server's `max_connections`. That sum is frequently a surprise.

## Going further

- [Accessing relational databases](https://go.dev/doc/database/) — the official tutorial and the pool documentation
- [`database/sql` package](https://pkg.go.dev/database/sql)
- [`pgx`](https://pkg.go.dev/github.com/jackc/pgx/v5) — the current default Postgres driver
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top — this lesson compresses it, and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
