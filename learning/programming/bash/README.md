---
title: Bash
description: "Write shell that survives production: quoting, exit status, the failure modes, and knowing when to stop and use a real language"
type: topic
---

# Learning: Bash

Be able to write and maintain shell scripts for CI pipelines, deployment and operational tooling that do not quietly break on a bad input or an unset variable, and to recognise when a script has outgrown shell and belongs in a real language instead.

**Latest lesson:** [1. Quoting](lessons/0001-quoting.md)

## Success looks like

- Write a CI/deployment script or an operational utility that handles quoting, exit status and common failure modes correctly, and explain why each choice was necessary.
- Given a shell script, name the specific way it would break on an edge case (unquoted expansion, unset variable, a command's exit status ignored).
- Recognise when a script has outgrown shell's judgment-free zone and say why the job now belongs in `programming/python` instead.

## Constraints

- Written for POSIX `sh` portability rather than bash-only idioms, even though bash is the topic's home; a bash-only feature is called out as such when used.
- Touches `awk`/`sed` only where a script genuinely needs them, not as topics of their own.

## Out of scope

- Everything past the point a script should have stopped being shell: `programming/python` is where it goes next.

## The arc

{N} stages, {start} to {end}. Not a lesson list: a stage takes several lessons, and the boundaries are soft.

| Stage | Covers | Done when |
|---|---|---|
| 1. {Name} | {What it covers} | {The capability that closes the stage} |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-quoting.md) | Quoting | The single habit that prevents the most common way shell scripts break in production |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
