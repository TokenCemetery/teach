---
title: Learning Workspaces
description: Every topic in this repository, grouped by domain
type: index
---

# Learning Workspaces

Grouped by domain, one directory per topic. Each topic is a self-contained workspace driven by the `teach` skill: a mission, an ordered set of lessons, and the reference material those lessons earned.

## Topics

| Domain | Topic | Mission | Lessons |
|---|---|---|---|
| programming | [Go](programming/golang/) | Own Go on a team: design, ship and operate a production service | 37 |
| programming | [Java](programming/java/) | Own a Java service: model it in modern Java, then operate what the JVM does with it | 49 |
| programming | [Python](programming/python/) | Own Python in production: ship it typed, tested, packaged and profiled | 44 |
| programming | [Rust](programming/rust/) | Own Rust: design with ownership instead of fighting the borrow checker, then ship the crate | 63 |
| programming | [SQL](programming/sql/) | Own the database: write the query, read the plan, design the schema, survive the concurrency | 48 |
| programming | [TypeScript](programming/typescript/) | Own a TypeScript codebase: make the compiler reject the states that should not exist | 49 |
| llm | [Adapter fine-tuning](llm/finetuning/) | Decide whether to fine-tune, run it, prove it worked, ship it | 27 |

## Starting a topic

```bash
cp -r templates/learning-workspace learning/<domain>/<topic-slug>
```

Then run the `teach` skill and name the topic. It reads the workspace, fills in the mission by interviewing you, and writes the first lesson.

A domain is a grouping, not a workspace: it holds topic directories and nothing else. Add a new one when a second topic would share it.

## Layout

```text
learning/
├── <domain>/              # programming, llm, …
│   └── <topic>/           # one workspace per topic
├── .nav.yml               # sidebar order/titles for the published site
└── README.md              # this index
```

Each workspace:

```text
learning/<domain>/<topic>/
├── README.md              # mission, success criteria, lesson index
├── GLOSSARY.md            # canonical terms for this topic
├── RESOURCES.md           # trusted sources, known gaps
├── NOTES.md               # preferences and working notes
├── lessons/               # NNNN-slug.md, one tight win each
├── reference/             # cheat sheets, built for lookup
└── learning-records/      # NNNN-slug.md, what was demonstrably learned
```

Lessons number from `0001` within each workspace. Workspaces may link to each other, but a link is a pointer rather than an inclusion: it does not pull another topic's material into this mission. Prefer linking a glossary term or a reference sheet over a lesson, because those are written for lookup and land on any reader.

The `teach` skill owns the format of every file here. Read [its spec](https://github.com/TokenCemetery/teach/blob/main/.agents/skills/teach/SKILL.md) before hand-authoring one.

## License

Everything on this site is [CC BY 4.0](https://github.com/TokenCemetery/teach/blob/main/LICENSE-CONTENT). Copy it, translate it, teach from it, build on it, commercially or not. Just say where it came from.