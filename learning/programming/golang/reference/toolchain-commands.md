---
title: Toolchain Commands
description: The go commands, test flags, profiling entry points and release build flags
type: reference
---

# Toolchain Commands

Lookup sheet for lessons [7](../lessons/0007-packages-and-modules.md), [28](../lessons/0028-table-driven-tests.md) through [33](../lessons/0033-modules-and-release-builds.md).

## Everyday

```bash
go run ./cmd/svc          # build and run, no binary kept
go build ./...            # compile everything
go test ./...             # run every test
go vet ./...              # static checks the compiler does not make
go fmt ./...              # canonical formatting; not negotiable
go fix ./...              # modernise to current idioms (rebuilt in Go 1.26)
go doc net/http Server    # docs for one identifier
go doc -src sync.Once Do  # its source, in the terminal
go env GOROOT             # where the standard library lives
```

## Modules

```bash
go mod init github.com/you/svc
go mod tidy                        # add what is imported, drop what is not
go mod why example.com/pkg         # why is this in the graph
go mod graph                       # the whole requirement graph
go get example.com/pkg@v1.5.0      # change a requirement
go get -u ./...                    # upgrade, deliberately
```

Minimal version selection picks the **highest of the required minimums**, not the newest published. Builds are reproducible without a lockfile; `go.sum` is a tamper check, and belongs in version control.

Module at v2 or above needs `/v2` in the module path and in imports.

`GOPRIVATE=github.com/yourorg/*` for internal modules — skips the public proxy and checksum database.

The `go` directive sets language semantics (loop variables, timer behaviour). The `toolchain` directive sets which toolchain builds it.

## Testing

```bash
go test ./...                     # cached
go test -count=1 ./...            # defeat the cache
go test -v -run 'TestParse/empty' # one subtest
go test -race ./...               # data race detector
go test -cover ./...              # coverage
go test -fuzz=FuzzRoundTrip       # open-ended fuzzing
```

| Helper | Does |
|---|---|
| `t.Run(name, fn)` | subtest — independent failure, selectable by name |
| `t.Parallel()` | run with other parallel subtests |
| `t.Helper()` | report failures at the caller's line |
| `t.Cleanup(fn)` | teardown that works with subtests and parallel tests |
| `t.Fatalf` / `t.Errorf` | stop this test / record and continue |

Message convention: `Parse(%q) = %v, want %v`.
Golden files live in `testdata/`, which the go tool ignores when building.

## Benchmarks

```go
func BenchmarkParse(b *testing.B) {
    for b.Loop() {            // Go 1.24; setup runs once, results kept alive
        Parse("1h30m")
    }
}
```

```bash
go test -bench=. -benchmem -count=10 ./... > old.txt
go test -bench=. -benchmem -count=10 ./... > new.txt
benchstat old.txt new.txt
go install golang.org/x/perf/cmd/benchstat@latest
```

`allocs/op` is the metric that reproduces across machines. One run is not a measurement.

## Profiling

```bash
go test -bench=. -cpuprofile=cpu.out -memprofile=mem.out ./...
go tool pprof cpu.out
go tool pprof -http=:8080 cpu.out             # flame graph in the browser
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30
```

Import `_ "net/http/pprof"` and serve on **localhost only**.

| Endpoint | Shows |
|---|---|
| `/debug/pprof/profile?seconds=30` | CPU |
| `/debug/pprof/heap` | memory (`inuse_space` by default) |
| `/debug/pprof/goroutine?debug=2` | every goroutine stack, with block duration |
| `/debug/pprof/goroutineleak` | provably unblockable goroutines (Go 1.27) |
| `/debug/pprof/block`, `/mutex` | waiting and contention — must be enabled first |

Inside pprof: `top`, `top -cum`, `list Func`, `web`.
**flat** = time in this function's own code. **cum** = including callees.

Heap views: `inuse_space` for a leak, `alloc_space` for GC pressure.

## Escape analysis

```bash
go build -gcflags='-m' ./... 2>&1 | grep escapes
go build -gcflags='-m -m' ./...        # the reasoning chain
```

Common causes: returning a pointer to a local, storing in something that escapes, assigning to an interface, capture by an escaping closure, unbounded `make` size.

## Release build

```bash
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build \
  -trimpath \
  -ldflags="-s -w -X main.version=$(git describe --tags --always)" \
  -o bin/svc ./cmd/svc
```

| Flag | Does |
|---|---|
| `CGO_ENABLED=0` | static binary, runs in `scratch`/`distroless` |
| `-trimpath` | strips local paths — reproducible, and no leaked home directory |
| `-ldflags="-s -w"` | strips symbols and DWARF; drop these if you need readable crashes |
| `-X pkg.Var=value` | sets a string variable at link time |

## Security

```bash
go install golang.org/x/vuln/cmd/govulncheck@latest
govulncheck ./...     # reachability-aware, so the output is short enough to act on
```

Supported releases: the two most recent major versions. Older toolchains get no security fixes.
