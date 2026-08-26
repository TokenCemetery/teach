# Learning: Go

Become the engineer trusted to own Go on a team — able to design, ship and operate a production Go service, review someone else's Go and name concretely why a design is wrong, and recognise when a design imported from another language is fighting Go rather than using it.

**Latest lesson:** _none yet_

## Success looks like

- Design and ship a production service: config, structured logging, graceful shutdown, health checks, database access.
- Debug a data race and a goroutine leak in code you did not write, using `-race` and `pprof`.
- Review a colleague's PR and say precisely why an interface, a pointer receiver, or a channel is the wrong tool there.
- Predict what a concurrent program does before running it, from the scheduler and memory model rather than from experiment.
- Cut allocations with evidence from `pprof` and `benchstat`, not guesswork.
- Design a package API you can keep backwards-compatible, and know when *not* to reach for a goroutine.

## Constraints

- Assumes no prior Go. Experience in another language shortens the early stages but is not required, and it brings habits that Go will punish quietly — wrong instincts here still compile.
- Needs only the standard toolchain on any supported OS. Nothing through stage 5 requires paid tooling, a cloud account, or a second machine.
- Reps are small programs that fit one sitting. Spacing them across days is the mechanism, not an inconvenience.
- Version-sensitive material dates fast. Claims about the current release are checked against release notes rather than against books.

## Out of scope

- Other languages as subjects in their own right. Comparisons appear only where they stop a habit from being carried into Go.
- Frontend, WASM, and mobile targets.
- Kubernetes and infrastructure beyond what one Go service needs to run.
- Compiler and runtime internals past the point where they stop predicting program behaviour.

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| _none yet_ | | |

## Reference

- [Glossary](GLOSSARY.md) — canonical terms for this topic
- [Resources](RESOURCES.md) — trusted sources and communities

## How this works

Each lesson is short and self-contained. Answer keys are collapsed — recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Bring anything unclear back to the teaching session.
