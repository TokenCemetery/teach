# AGENTS.md

## What this repository is

A place to learn topics over many sessions. One topic lives in one directory:
`learning/<domain>/<topic>/`.

All teaching state is kept in files, not in the conversation, because a topic is
taught across many sessions.

Almost every task here is one of two things: teach a lesson, or update workspace
files. Anything else (templates, CI, project docs) is rare.

## Start of every session

1. Read `.agents/memory/MEMORY.md`.
2. Read `.agents/memory/YYYY-MM-DD.md` using today's UTC date.
3. If the directory or a file is missing, create it. Never overwrite memory that
   already exists.

What the files hold:

- `MEMORY.md` — durable project facts. May be out of date. Check the repository
  before trusting it.
- `YYYY-MM-DD.md` — today's task notes and checklists.

Never write learner state into `.agents/memory/`. What the user learned, got
wrong, or told you about themselves belongs in that topic's `learning-records/`.

## Teaching

Read `.agents/skills/teach/SKILL.md` before you create or edit any file inside
a workspace. It defines every path, every file format, and what the published
site needs. Do not invent your own, and do not follow a personal skill of the
same name where the two disagree — the file in this repository wins.

## Editing rules

- The repository is the source of truth. Check files before acting on memory or
  old notes.
- Change as little as possible. Do not restructure, reformat, or improve
  unrelated content unless asked.
- If your change makes a project document wrong, fix that document in the same
  change.

Before a change that touches behavior, several files, shared conventions,
structure, dependencies, or project docs, first state: what you will change,
how you will check it, and any real ambiguity. Ask one short question if the
answer would change the scope. Writing one lesson into an existing workspace
does not need this step.

## Quality bar for anything you write

- Complete, specific, and consistent with itself.
- No placeholders and no TODOs. The only exception is
  `templates/learning-workspace/`.
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
