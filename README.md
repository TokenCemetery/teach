# teach

> A persistent learning workspace. One directory per topic, taught across many sessions.

## What it does

Learning a topic properly takes more than one sitting, and the thing that usually gets lost between sittings is the state: what was already covered, what stuck, what turned out to be a misconception, which sources were worth trusting. This repository holds that state.

Topics live under [`learning/`](learning/), grouped by domain. Each is a workspace with a stated mission, an ordered set of short lessons, cheat sheets built for lookup, and a record of what was demonstrably learned. The `teach` skill reads the workspace at the start of a session, writes one lesson, and records only what the session earned.

## Getting started

### Prerequisites

- An agent that can read [`AGENTS.md`](AGENTS.md). The `teach` skill it needs
  ships with the repository, at [`.agents/skills/teach/`](.agents/skills/teach/SKILL.md).

### Starting a topic

```bash
cp -r templates/learning-workspace learning/<domain>/<topic-slug>
```

Then run the `teach` skill and name the topic. It interviews you for the mission, writes `README.md`, and produces the first lesson.

### Continuing a topic

Run the `teach` skill again. It picks up from the workspace state — no need to recap what you covered last time.

## Layout

```text
.
├── learning/
│   ├── README.md          # index of topic workspaces
│   └── <domain>/<topic>/  # one workspace per topic
├── templates/
│   └── learning-workspace/ # copy source for a new topic
└── .agents/
    └── skills/teach/      # the format spec every workspace follows
```

Conventions for agent behavior live in [`AGENTS.md`](AGENTS.md).

## Contributing

See the org-wide [CONTRIBUTING.md](https://github.com/PromptPasture/.github/blob/main/CONTRIBUTING.md).

## License

Two licenses, because the repository holds two different things.

- **Learning content** — everything under `learning/` and `templates/`:
  [CC BY 4.0](LICENSE-CONTENT). Copy it, translate it, teach from it, build on
  it, commercially or not. Just say where it came from.
- **Software and configuration** — build config, workflows, stylesheets:
  [Apache-2.0](LICENSE).

One exception: everything under
[`.agents/skills/teach/`](.agents/skills/teach/SKILL.md) is MIT, derived from
[mattpocock/skills](https://github.com/mattpocock/skills) via
[PromptPasture/agent.md](https://github.com/PromptPasture/agent.md). Its
attribution lives in the front matter of `SKILL.md`, which the other files in
that directory were split out of.
