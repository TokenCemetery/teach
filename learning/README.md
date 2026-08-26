# Learning Workspaces

One directory per topic. Each is a self-contained workspace driven by the `teach` skill: a mission, an ordered set of lessons, and the reference material those lessons earned.

## Topics

| Topic | Mission | Lessons |
|---|---|---|
| _none yet_ | | |

## Starting a topic

```bash
cp -r learning/_template learning/<topic-slug>
```

Then run the `teach` skill and name the topic. It reads the workspace, fills in the mission by interviewing you, and writes the first lesson.

`_template/` is a copy source, not a workspace — leave it out of the table above.

## Workspace layout

```text
learning/<topic>/
├── README.md              # mission, success criteria, lesson index
├── GLOSSARY.md            # canonical terms for this topic
├── RESOURCES.md           # trusted sources, communities, known gaps
├── NOTES.md               # preferences and working notes
├── lessons/               # NNNN-slug.md — one tight win each
├── reference/             # cheat sheets, built for lookup
├── learning-records/      # NNNN-slug.md — what was demonstrably learned
└── assets/                # diagrams, drill banks, printable cards
```

The `teach` skill owns the format of every file here. Read its `SKILL.md` before hand-authoring one.
