# AGENTS.md

## What this repository is

A place to learn topics over many sessions. One topic lives in one directory:
`learning/<domain>/<topic>/`.

All state is kept in files, not in the conversation, because a topic is taught
across many sessions and no session remembers the last one. What the user
demonstrably learned goes in that topic's `learning-records/`; what is true
about them goes in its `NOTES.md`; anything a future session needs to know
about the repository itself belongs in this file or in the teach skill, which
are committed and read by everyone. There is no scratch file for durable facts —
if it is worth keeping, it is worth putting where it is already read.

Almost every task here is one of two things: teach a lesson, or update workspace
files. Anything else (templates, CI, project docs) is rare.

## Teaching

Read `.agents/skills/teach/SKILL.md` before you create or edit any file inside
a workspace. It is the entry point: it defines every path and the teaching
workflow, and points at `FORMATS.md` for what each file must contain and
`PUBLISHING.md` for front matter, rendering and what the published site needs.
Do not invent your own, and do not follow a personal skill of the same name
where the two disagree — the file in this repository wins.

## Editing rules

- The repository is the source of truth. Check files before acting on old notes
  or on what an earlier session reported.
- Change as little as possible. Do not restructure, reformat, or improve
  unrelated content unless asked.
- If your change makes a project document wrong, fix that document in the same
  change.

Before a change that touches behavior, several files, shared conventions,
structure, dependencies, or project docs, first state: what you will change,
how you will check it, and any real ambiguity. Ask one short question if the
answer would change the scope. Writing one lesson into an existing workspace
does not need this step.

## Checking your work

`learning/` is the source of a published site. After any change under it, build
with the repository virtualenv:

```bash
.venv/bin/mkdocs build --strict
```

A clean strict build is necessary and not sufficient — it validates front matter
and navigation, and cannot see a collapsed answer that failed to render.
`.agents/skills/teach/PUBLISHING.md` lists what it misses and how to check the
rest.

## Quality bar for anything you write

- Complete, specific, and consistent with itself.
- No placeholders and no TODOs. The only exceptions are
  `templates/learning-workspace/`, which keeps its `{placeholder}` markers, and
  `TODO.md`, whose subject is planned work.
- No claims you cannot support.
- Every section and example must serve the goal. Delete the rest.
- Examples must be short, complete, and match how this repository actually
  works.
- Choose the simplest version that fully solves the task. Do not add
  abstractions, options, or features nobody asked for.
- Re-read what you wrote before showing it. Fix contradictions, placeholders,
  and anything outside the request.

## Final answer

End the task by stating:

1. What you changed.
2. What you checked, and how.
3. Anything still risky or unverified.
