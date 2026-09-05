---
title: 22. An HTTP Server Worth Operating
description: Handlers, routing patterns and the four timeouts the default server does not set
type: lesson
---

# Lesson 22. An HTTP Server Worth Operating

**Mission link:** This is the first lesson of the service you will ship. The default `http.ListenAndServe` is a demo; the difference is four fields and a routing decision.
**Primary source:** [Routing Enhancements for Go 1.22, The Go Blog](https://go.dev/blog/routing-enhancements)
**Prerequisites:** [Lesson 18](0018-context-cancellation.md), [Lesson 11](0011-implicit-interfaces.md)

## Warm-up

1. ▢ How does a goroutine leak differ from a deadlock in what the runtime tells you?

<details markdown="1"><summary>Check</summary>

The runtime reports a deadlock only when *every* goroutine is blocked. A leaking service still has a runnable listener, so nothing is reported at all. You find leaks with a goroutine profile.

</details>

2. ▢ Where does a request's deadline come from, inside a handler?

<details markdown="1"><summary>Check</summary>

`r.Context()`. Derive from it with `context.WithTimeout` and pass the result down; everything context-aware then observes the same deadline.

</details>

## Know this

The whole server API rests on one interface:

```go
type Handler interface {
    ServeHTTP(w http.ResponseWriter, r *http.Request)
}
```

`http.HandlerFunc` adapts a plain function to it. That is the extension point for routers, middleware, and testing: `httptest.NewRecorder()` is a `ResponseWriter`, so a handler is testable with no network.

### Routing

Since [Go 1.22](https://go.dev/doc/go1.22#enhanced_routing_patterns) `ServeMux` handles methods and wildcards, which is most of what a third-party router was for:

```go
mux := http.NewServeMux()
mux.HandleFunc("GET /items/{id}", getItem)
mux.HandleFunc("POST /items", createItem)
mux.HandleFunc("GET /files/{path...}", serveFile)
mux.HandleFunc("GET /health/{$}", health)   // exact match, no prefix

func getItem(w http.ResponseWriter, r *http.Request) {
    id := r.PathValue("id")
    ...
}
```

The rules worth remembering: a pattern with a method beats one without; `GET` also registers `HEAD`; `{path...}` matches all remaining segments and must come last; `{$}` anchors the end so the pattern is not a prefix match; and the *more specific* pattern wins regardless of registration order. Conflicting patterns that are equally specific panic at registration, which is at startup, where you want it.

### The four timeouts

`http.ListenAndServe(":8080", mux)` builds a `http.Server` with **no timeouts at all**. A client that opens a connection and sends one byte a minute holds a goroutine and a connection indefinitely. That is the slowloris shape, and a trivially cheap way to exhaust a service.

Construct the server yourself:

```go
srv := &http.Server{
    Addr:              ":8080",
    Handler:           mux,
    ReadHeaderTimeout: 5 * time.Second,
    ReadTimeout:       15 * time.Second,
    WriteTimeout:      30 * time.Second,
    IdleTimeout:       60 * time.Second,
}
```

| Field | Covers |
|---|---|
| `ReadHeaderTimeout` | headers only, the cheapest defence and safe to set aggressively |
| `ReadTimeout` | headers plus body; too low breaks large uploads |
| `WriteTimeout` | from end of headers to end of response; too low truncates slow responses |
| `IdleTimeout` | how long a keep-alive connection may sit unused |

![One connection drawn left to right through headers, body, handler, response and idle, with each timeout drawn as a bar over the stretch it covers. ReadHeaderTimeout covers the headers, ReadTimeout the headers and body, WriteTimeout from the end of the headers to the end of the response, and IdleTimeout only the stretch afterwards.](images/what-each-timeout-covers.svg)

The bars are the table drawn to scale, and they show one thing the rows cannot: the body sits inside two of them at once. `WriteTimeout` is timed from the end of the headers, not from the start of the response, so a slow upload spends the same seconds the write budget is counting.

There is no correct set of numbers, only numbers chosen against your slowest legitimate request. The mistake is leaving them at zero, which means infinite.

### Middleware

Middleware is a function from handler to handler:

```go
func withRequestID(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        id := uuid.NewString()
        ctx := context.WithValue(r.Context(), ctxKeyRequestID{}, id)
        w.Header().Set("X-Request-Id", id)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

srv.Handler = withRequestID(withLogging(mux))
```

No framework, no registration, no interface to satisfy: just composition, and the reason implicit interfaces from Lesson 11 matter in practice.

Order is inside-out: the outermost wrapper sees the request first and the response last. Recovery goes outermost so it catches panics from everything within, then logging, then request id, then routing.

### Handlers that can fail

`ServeHTTP` returns nothing, so error handling has to be built. The idiom that scales is a handler type that returns an error, adapted once:

```go
type apiFunc func(http.ResponseWriter, *http.Request) error

func (f apiFunc) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    if err := f(w, r); err != nil {
        writeError(w, r, err)   // one place that maps errors to status codes
    }
}
```

Now a handler writes `return fmt.Errorf("get item %s: %w", id, err)` and one function decides that `store.ErrNotFound` is a 404, a `*ValidationError` is a 400, and everything else is a 500 with the detail logged rather than returned. That mapping is exactly what Lesson 9's `errors.Is` and `errors.As` are for.

### JSON

`encoding/json` decodes from the body and encodes to the writer. Two habits: bound the read with `http.MaxBytesReader` so a large body cannot exhaust memory, and set the `Content-Type` header before writing, since writing the body commits the status code.

Go 1.27 added `encoding/json/v2`, with stricter defaults: invalid UTF-8 and duplicate object names are rejected. `encoding/json` is not deprecated and remains the default choice; reach for v2 when you want the stricter behaviour or its options.

## Practice

1. ▢ What does `http.ListenAndServe(":8080", mux)` leave unset that matters?

<details markdown="1"><summary>Check</summary>

Every timeout. The `http.Server` it builds has `ReadTimeout`, `WriteTimeout`, `ReadHeaderTimeout` and `IdleTimeout` all zero, which means no limit.

A client that opens connections and dribbles bytes holds one goroutine and one file descriptor each, indefinitely. It is the cheapest denial of service there is, and the fix is constructing the `Server` yourself.

</details>

2. ▢ Given `GET /items/{id}` and `GET /items/new`, which handles `GET /items/new`?

<details markdown="1"><summary>Check</summary>

`GET /items/new`. The more specific pattern wins, and a literal segment is more specific than a wildcard.

Registration order does not matter, which is the property that makes the Go 1.22 mux predictable and a real difference from routers that match in declaration order.

</details>

3. ▢ Which timeout is safest to set aggressively?

   - a) `ReadTimeout`, covering headers and the whole body
   - b) `WriteTimeout`, covering the response being written
   - c) `ReadHeaderTimeout`, covering only the request headers
   - d) `IdleTimeout`, covering unused keep-alive connections

<details markdown="1"><summary>Check</summary>

**c)** `ReadHeaderTimeout`, covering only the request headers.

Headers should arrive in milliseconds from any legitimate client, so a few seconds is generous and it shuts down the slowloris shape. The others are bounded by real work such as a large upload, a slow response or a client that reconnects, so tightening them breaks valid traffic first.

</details>

4. ▢ Where in the middleware chain does panic recovery belong, and why?

<details markdown="1"><summary>Check</summary>

Outermost, so it wraps everything else: a panic in any inner middleware or handler unwinds into it.

Note what it is for. `net/http` already recovers handler panics, logs a stack, and closes the connection, so the process survives either way. Your middleware exists to turn that into a 500 response and a structured log line with the request id attached, instead of a dropped connection the client has to interpret.

</details>

5. ▢ Interleaving Lesson 9: your handler gets `store.ErrNotFound` from three layers down. What should it do?

<details markdown="1"><summary>Check</summary>

Return the error, wrapped with context. One central `writeError` uses `errors.Is(err, store.ErrNotFound)` to map it to 404.

Mapping inline in each handler duplicates the policy and drifts, so the same condition becomes 404 in one place and 500 in another. Centralising it also gives one place to decide what detail is safe to return to a client versus logged internally, which is a security boundary as much as a design one.

</details>

## Real-world reps

- [ ] Build a two-route service with `GET /items/{id}` and `POST /items`, using an explicit `http.Server` with all four timeouts. Curl both routes.
- [ ] Write one middleware that adds a request id and one that logs method, path, status and duration. Compose them and confirm the order in the output.
- [ ] Tomorrow: check whether a service you operate sets `ReadHeaderTimeout`. If not, you have found a one-line hardening change.

## Going further

- [Routing Enhancements for Go 1.22, The Go Blog](https://go.dev/blog/routing-enhancements)
- [`net/http.Server`](https://pkg.go.dev/net/http#Server): read the field docs for the timeouts
- [How I write HTTP services in Go, Mat Ryer](https://grafana.com/blog/2024/02/09/how-i-write-http-services-in-go-after-13-years/)
- [Lesson 25. Graceful Shutdown](0025-graceful-shutdown.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
