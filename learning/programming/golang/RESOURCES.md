---
title: Resources
description: Trusted sources for Go, each annotated with what it covers
type: resources
---

# Go Resources

## Knowledge

- [Docs: "Effective Go" — The Go Authors, go.dev](https://go.dev/doc/effective_go)
  The canonical idiom document. Use for: settling whether something is idiomatic.

- [Docs: "Go Code Review Comments" — The Go Authors, go.dev wiki](https://go.dev/wiki/CodeReviewComments)
  The conventions Go reviewers actually cite. Use for: review vocabulary and stage 6 judgment.

- [Docs: "The Go Memory Model" — The Go Authors, go.dev](https://go.dev/ref/mem)
  Precise statement of what concurrent programs are guaranteed to observe. Use for: reasoning about races instead of testing for them.

- [Book: "The Go Programming Language" — Donovan & Kernighan, Addison-Wesley](https://www.gopl.io/)
  Language semantics from first principles, with exercises. Use for: stages 1–3 when a mental model is missing rather than a fact.

- [Book: "100 Go Mistakes and How to Avoid Them" — Teiva Harsanyi, Manning](https://www.manning.com/books/100-go-mistakes-and-how-to-avoid-them)
  Catalogued traps with explanations of why each one is wrong. Use for: the errors developers reliably import from other languages.

- [Blog: "The Go Blog" — The Go Authors, go.dev](https://go.dev/blog/)
  Design rationale and release changes from the people who made the decisions. Use for: why Go refuses a feature, and what changed in a release.

- [Blog: Dave Cheney — dave.cheney.net](https://dave.cheney.net/)
  Deep, careful posts on errors, interfaces, and allocation. Use for: going one level below the idiom into why it holds.

- [Style guide: "Uber Go Style Guide" — Uber Engineering](https://github.com/uber-go/guide/blob/master/style.md)
  Opinionated team-scale conventions with rationale. Use for: decisions Effective Go leaves open.

- [Docs: "Go Doc Comments" — The Go Authors, go.dev](https://go.dev/doc/comment)
  The rules `go doc` and pkg.go.dev actually apply, including deprecation markers. Use for: writing an API that documents itself.

- [Docs: "Go Modules Reference" — The Go Authors, go.dev](https://go.dev/ref/mod)
  Minimal version selection, the major-version path rule, proxies and checksums. Use for: anything about `go.mod` behaviour.

- [Docs: "Go 1 and the Future of Go Programs" — The Go Authors, go.dev](https://go.dev/doc/go1compat)
  The compatibility promise, and by extension the model for your own packages. Use for: deciding whether a change is breaking.

- [Docs: "Frequently Asked Questions" — The Go Authors, go.dev](https://go.dev/doc/faq)
  Short, authoritative answers on receivers, nil errors, and stack-versus-heap. Use for: settling a question the spec answers too formally.

- [Docs: "Diagnostics" — The Go Authors, go.dev](https://go.dev/doc/diagnostics)
  Profiling, tracing, debugging and runtime instrumentation in one page. Use for: choosing the right tool before an investigation.

- [Docs: "Release History" and the per-release notes — The Go Authors, go.dev](https://go.dev/doc/devel/release)
  Exactly what changed in each release, and which versions are still supported. Use for: checking any version-sensitive claim before teaching it.

- [Article: "Go for Industrial Programming" — Peter Bourgon](https://peter.bourgon.org/go-for-industrial-programming/)
  Package boundaries, explicit wiring and observability in services that are operated. Use for: stage 4 structure decisions.

- [Article: "How I write HTTP services in Go" — Mat Ryer, Grafana Labs](https://grafana.com/blog/2024/02/09/how-i-write-http-services-in-go-after-13-years/)
  A working service layout revised over thirteen years, with the reasoning kept. Use for: handler shape, `run` functions, testing a server.

- [Reference: "Go Proverbs" — Rob Pike](https://go-proverbs.github.io/)
  The short forms of Go's design values, each linked to the talk behind it. Use for: review vocabulary, and for the arguments about restraint.

## Gaps

- Go's release cadence outpaces every book listed here. Version-sensitive claims are checked against the release notes above rather than against a book, and any lesson naming a release states which one.
- Observability beyond logging — metrics, tracing, OpenTelemetry — has no lesson and no source chosen. Stage 4 covers `slog` and health checks only.
- gRPC has no source and no lesson. Stage 4 went HTTP-first; this stays open in case the mission needs gRPC later.
- No source chosen for the Go scheduler in depth. Lesson 15 teaches only as much as predicts program behaviour, which the mission caps deliberately.
