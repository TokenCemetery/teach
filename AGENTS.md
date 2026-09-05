# Agent instructions

## What this repository is

A place to learn topics over many sessions. One topic lives in one directory:
`learning/<domain>/<topic>/`.

Keep all state in files. No session remembers the last one, so write every durable fact where it is already read:

- What the user demonstrably learned: that topic's `learning-records/`.
- What is true about the user: that topic's `NOTES.md`.
- What a future session needs to know about this repository: this file, or the teach skill.

Never leave a durable fact in a scratch file or in the conversation.

## Teaching

Read `.agents/skills/teach/SKILL.md` before you create or edit any file under `learning/`. It defines every path and the teaching workflow. It points to two more files:

- `FORMATS.md`: what each file must contain.
- `PUBLISHING.md`: front matter, rendering, and what the published site needs.

Follow that skill. Do not invent your own workflow. A personal skill named `teach` may exist outside this repository. Where the two disagree, the file in this repository wins.

## Editing rules

- The repository is the source of truth. Read the files before you act. Do not trust old notes or what an earlier session reported.
- Change as little as possible.
- Do not restructure, reformat, or improve unrelated content unless asked.
- If your change makes a project document wrong, fix that document in the same change.

State your plan first when a change touches behavior, several files, shared conventions, structure, dependencies, or project docs. Say what you will change, how you will check it, and any real ambiguity. Ask one short question if the answer would change the scope. Writing one lesson into an existing workspace needs no plan.

## Checking your work

`learning/` is the source of a published site. After any change under it, run:

```bash
.venv/bin/mkdocs build --strict
```

The build checks front matter and navigation. It does not check that a collapsed answer rendered. Read `.agents/skills/teach/PUBLISHING.md` for the checks the build cannot do.

## Track work in GitHub Issues

When you find a bug, notice a problem worth fixing later, or plan a new feature, open a GitHub issue for it. Do not leave it in chat or in a local notes file — the issue is what keeps the history of the problem and the progress on it.

```console
gh issue list --state all --search "keyword"   # look for an existing issue first
gh issue create --title "..." --body "..." --label bug
```

- Before you fix something, check that an issue for it exists — search the open and the closed ones. If none does, open it first, then fix it: the record of what was wrong is worth as much as the fix.
- The exception is a defect that exists only in changes you have not committed yet. Correcting your own work in progress is part of the task at hand, not project history — fix it and file nothing.
- Title states what is wrong or what should exist. Body gives the steps to reproduce, or what "done" looks like, plus the files involved. `gh issue create` skips the forms in `.github/ISSUE_TEMPLATE/`, so cover the same fields in the body yourself.
- Use the labels that already exist: `bug`, `enhancement`, `documentation`, `accessibility`.
- Record progress on the issue as you go — comment on what you found and what you tried, so the next person does not repeat the investigation.
- Reference the issue from the commit or pull request that fixes it (`Fixes #12`), so it closes together with the change.

`.agents/TODO.md` is a leftover local list, not the tracker. Everything it held is filed as an issue now; do not add new items to it.

## Quality bar for anything you write

- Be complete and specific, and stay consistent with yourself.
- Write no placeholders and no TODOs. Two exceptions: `templates/learning-workspace/` keeps its `{placeholder}` markers, and `.agents/TODO.md`, which is git-ignored, holds planned work.
- Make no claim you cannot support.
- Use no em dashes in prose. Rewrite the sentence with a comma, colon, period, parentheses, or a conjunction. Pick the one the sentence wants. Never swap the character mechanically.
- Delete any section or example that does not serve the goal.
- Keep examples short and complete. Match how this repository actually works.
- Choose the simplest version that fully solves the task. Add no abstraction, option, or feature nobody asked for.
- Re-read your work before you show it. Fix contradictions, placeholders, and anything outside the request.

## Final answer

End the task by stating:

1. What you changed.
2. What you checked, and how.
3. Anything still risky or unverified.
