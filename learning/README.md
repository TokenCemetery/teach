# Learning Workspaces

Grouped by domain, one directory per topic. Each topic is a self-contained workspace driven by the `teach` skill: a mission, an ordered set of lessons, and the reference material those lessons earned.

## Topics

| Domain | Topic | Mission | Lessons |
|---|---|---|---|
| programming | [Go](programming/golang/) | Own Go on a team: design, ship and operate a production service | 0 |
| llm | [Adapter fine-tuning](llm/finetuning/) | Decide whether to fine-tune, run it, prove it worked, ship it | 27 |

## Starting a topic

```bash
cp -r templates/learning-workspace learning/<domain>/<topic-slug>
```

Then run the `teach` skill and name the topic. It reads the workspace, fills in the mission by interviewing you, and writes the first lesson.

A domain is a grouping, not a workspace — it holds topic directories and nothing else. Add a new one when a second topic would share it.

## Layout

```text
learning/
├── <domain>/              # programming, llm, …
│   └── <topic>/           # one workspace per topic
└── README.md              # this index
```

Each workspace:

```text
learning/<domain>/<topic>/
├── README.md              # mission, success criteria, lesson index
├── GLOSSARY.md            # canonical terms for this topic
├── RESOURCES.md           # trusted sources, communities, known gaps
├── NOTES.md               # preferences and working notes
├── lessons/               # NNNN-slug.md — one tight win each
├── reference/             # cheat sheets, built for lookup
├── learning-records/      # NNNN-slug.md — what was demonstrably learned
└── assets/                # diagrams, drill banks, printable cards
```

Lessons number from `0001` within each workspace. Workspaces do not link to each other; a topic that needs another topic's material is one topic.

The `teach` skill owns the format of every file here. Read its `SKILL.md` before hand-authoring one.
