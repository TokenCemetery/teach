# Agent instructions

## What this repository is

A place to learn topics over many sessions. One topic lives in one directory:
`learning/<domain>/<topic>/`.

Keep all state in files. No session remembers the last one, so write every durable fact where it is already read:

- What the user demonstrably learned: that topic's `learning-records/`.
- What is true about the user: that topic's `NOTES.md`.
- What a future session needs to know about this repository: this file, or the teach skill.

## Teaching

Read `.agents/skills/teach/SKILL.md` before you create or edit any file under `learning/`. It defines every path and the teaching workflow. It points to two more files:

- `FORMATS.md`: what each file must contain.
- `PUBLISHING.md`: front matter, rendering, and what the published site needs.

Follow that skill. Do not invent your own workflow. A personal skill named `teach` may exist outside this repository. Where the two disagree, the file in this repository wins.

## Editing rules

If your change makes a project document wrong, fix that document in the same change.

## Checking your work

`learning/` is the source of a published site. After any change under it, run:

```bash
.venv/bin/properdocs build --strict
```

After any change to a Markdown file anywhere in the repository, run the same lint CI runs. Its rules live in `.markdownlint.yaml`:

```bash
npx --yes markdownlint-cli2@0.23.3 "**/*.md" "#.venv" "#site" "#**/node_modules"
```

After any change to a ```` ```mermaid ```` fence, or to `extra.mermaid_version` in `properdocs.yml`, parse every diagram with the Mermaid version the site pins, as CI does. Neither the build nor the lint looks inside the fence:

```bash
npm ci --prefix .agents/tools && node .agents/tools/check-mermaid.mjs
```

A valid fence can still break in the build. After any change to `properdocs.yml`, `hooks.py`, `overrides/` or `pyproject.toml`, build, then check the diagrams as the browser receives them. CI runs this before every deploy:

```bash
node .agents/tools/check-mermaid.mjs --site site
```

The build checks front matter and navigation. It does not check that a collapsed answer rendered. Read `.agents/skills/teach/PUBLISHING.md` for the checks the build cannot do.

## Track work in GitHub Issues

When you find a bug, notice a problem worth fixing later, or plan a new feature, open a GitHub issue for it. Do not leave it in chat or in a local notes file: the issue is what keeps the history of the problem and the progress on it.

```console
gh issue list --state all --search "keyword sort:created-asc"   # look for an existing issue first, oldest first
gh issue create --title "..." --body-file body.md --label "bug,P2"
```

- Before you fix something, check that an issue for it exists, in the open ones and the closed ones alike. If none does, open it first, then fix it: the record of what was wrong is worth as much as the fix.
- The exception is a defect that exists only in changes you have not committed yet. Correcting your own work in progress is part of the task at hand, not project history, so fix it and file nothing.
- Title states what is wrong or what should exist. Body gives the steps to reproduce, or what "done" looks like, plus the files involved.
- Write the body to a file and pass `--body-file`. Inline in double quotes, the shell runs every backtick in it as a command, which silently deletes the path or the identifier you were quoting.
- Label only from what `.github/workflows/labels.yml` declares.
- Give every issue, open or closed, one type and one priority. Type is `bug`, `feature`, `refactor`, `chore`, `docs` or `security`. Priority runs `P0` for critical through `P3` for low. Add any of `needs-triage`, `needs-repro`, `blocked`, `declined`, `stale` and `help-wanted` that apply.
- An issue for a new track closes only when the track is complete: every file the `teach` skill defines, every lesson the arc names written and listed in the lesson table, and the `reference/` sheets those lessons send readers back to. A scaffold, or an arc with only its first lessons written, leaves the issue open. Say so in the issue's "Done when".
- Record progress on the issue as you go, commenting on what you found and what you tried, so the next person does not repeat the investigation.
- Reference the issue from the commit or pull request that fixes it (`Fixes #12`), so it closes together with the change.

## Writing rules

- Write no placeholders. One exception: `templates/learning-workspace/` keeps its `{placeholder}` markers.
- Use no em dashes in prose. Rewrite the sentence with a comma, colon, period, parentheses, or a conjunction. Pick the one the sentence wants. Never swap the character mechanically.
