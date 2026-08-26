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

## Wisdom (Communities)

- [r/golang](https://www.reddit.com/r/golang/)
  Active and quick to correct un-idiomatic code. Use for: "is this the Go way" design questions.

- [Gophers Slack](https://invite.slack.golangbridge.org/)
  Large practitioner community with topic channels, including `#performance` and `#reviews`. Use for: review of real code and narrow tooling problems.

- [Go Forum](https://forum.golangbridge.org/)
  Threaded and searchable, so answers survive. Use for: longer design questions worth a written answer.

## Gaps

- Go's release cadence outpaces every book listed here. Version-sensitive claims need checking against the release notes before being taught as current.
- No trusted source chosen yet for production service architecture in Go — stage 4 needs one.
- No source chosen yet for gRPC specifically, if stage 4 goes that way.
