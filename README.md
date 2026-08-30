# teach

> A persistent learning workspace. One directory per topic, taught across many sessions.

## What it does

Learning a topic properly takes more than one sitting, and the thing that usually gets lost between sittings is the state: what was already covered, what stuck, what turned out to be a misconception, which sources were worth trusting. This repository holds that state.

Topics live under [`learning/`](learning/), grouped by domain. Each is a workspace with a stated mission, an ordered set of short lessons, cheat sheets built for lookup, and a record of what was demonstrably learned. The `teach` skill reads the workspace at the start of a session, writes one lesson, and records only what the session earned.

## Getting started

### Prerequisites

- An agent with the `teach` skill available.

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
└── .agents/memory/        # agent working memory
```

Conventions for agent behavior live in [`AGENTS.md`](AGENTS.md).

## Contributing

See the org-wide [CONTRIBUTING.md](https://github.com/PromptPasture/.github/blob/main/CONTRIBUTING.md).

## License

Apache-2.0 — see [LICENSE](LICENSE).
