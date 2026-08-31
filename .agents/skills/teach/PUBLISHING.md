# Publishing

What every published page needs, how the two renderers differ, and what to check before presenting a lesson. `SKILL.md` is the entry point for teaching; this file governs the output.

## Front Matter

Every published page opens with YAML front matter. `NOTES.md` and `learning-records/` are exempt: they never reach the site, and nothing but the teaching session reads them.

```yaml
---
title: Short label, for the sidebar and the browser tab
description: One clause — what a reader gets from this page
type: index | topic | lesson | reference | glossary | resources
---
```

- **`title`** is the short form, not a copy of the `#` heading. The two are read in different places: the site renders `title` as the visible page heading and hides the markdown `#`, while GitHub shows the `#` and never sees the front matter. So the `#` heading carries the long name for a GitHub reader, and `title` carries the short one for the sidebar, where a long name clips mid-word. A lesson drops the word "Lesson" — it already sits under `Lessons`.
- **`description`** is one clause, no trailing period. For a lesson it is the same clause as its row in the workspace `README.md` table, and the front matter is canonical: change it here first, then match the table.
- **`type`** names the shape of the page, so a reader — human or machine — knows what it is before reading it. Use exactly one of the six values.

Do not add a date. The site derives `created_at` and `updated_at` from git history, and a hand-written date goes stale the first time someone forgets it.

`order` is read by the theme and overrides a page's position in the navigation. Leave it out while lesson filenames still sort correctly on their own number.

## Rendering

`learning/` is the `docs_dir` of a MkDocs site, and the same files are read on GitHub. Both renderers have to be right.

- Keep `markdown="1"` on every `<details>`. Python-Markdown needs it, through the `md_in_html` extension, to parse the answer inside. GitHub ignores the attribute, so the file stays correct in both.
- Leave a blank line after `<summary>` and before `</details>`.
- Keep the `<details>` block at column zero. Indenting it to nest inside a list item looks tidier and breaks the site: `md_in_html` does not parse HTML nested in a list, and the answer reverts to literal markdown. `sane_lists` carries the Practice numbering across the break instead.
- A single newline is a line break, as it is on GitHub. Lesson header blocks, glossary definitions and worked calculations rely on it. This holds only because no prose here is hard-wrapped — keep it that way and write a paragraph on one line.
- `mkdocs.yml` owns the extensions these rules depend on: `md_in_html`, `sane_lists`, `nl2br`, `pymdownx.highlight`, `pymdownx.superfences`. Removing one breaks every lesson at once.

Not everything in a workspace is published. `mkdocs.yml` excludes `NOTES.md` and `learning-records/`: they hold the learner's state — preferences, disclosed background, corrected misconceptions — and stay out of the site whether or not the repository is public.

Everything else is published, `RESOURCES.md` included. Workspace `README.md` files and lessons link to it, and a reader deserves the sources a claim rests on as much as the claim itself.

## Verification

Before presenting the lesson, confirm by reading:

- Every answer key is correct and collapsed, with no formatting tells.
- Terminology matches `GLOSSARY.md`.
- No placeholders remain.
- The `README.md` table has a row for the new lesson, its clause is the same as the lesson's front-matter `description`, and the **Latest lesson** pointer names it.

Then confirm by running `.venv/bin/mkdocs build --strict`.

A clean strict build proves the front matter parses and the navigation resolves. It does **not** prove the answer keys survived, so open the built page — `site/<domain>/<topic>/lessons/<slug>/index.html` — and check two things that look fine in the source and break silently:

- Markdown inside each `<details>` rendered as `<p>` and `<code>`, not as literal backticks. It reverts when `markdown="1"` is missing.
- Each Practice list resumed with `<ol start="N">` after an answer. It restarts at 1 when the `<details>` block is indented instead of sitting at column zero.

After a bulk edit, script the structural checks over `learning/**/*.md` rather than reading for them: front matter keys present with `type` one of the six, `<details markdown="1">` at column zero with a blank line after `<summary>` and before `</details>`, tags balanced, every relative link resolving, and every lesson `description` matching its README row.

Two traps when checking external links. Strip fenced and inline code first, or code that looks like link syntax — Go generics such as `Map[T, U any](s []T)` — reports as a broken link. And send a browser user agent, because some hosts answer a scripted one with a 403 that reads as a dead link.
