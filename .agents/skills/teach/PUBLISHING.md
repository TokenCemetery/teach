# Publishing

What every published page needs, how the two renderers differ, and what to check before presenting a lesson. `SKILL.md` is the entry point for teaching; this file governs the output.

## Front Matter

Every published page opens with YAML front matter. `NOTES.md` and `learning-records/` are exempt: they never reach the site, and nothing but the teaching session reads them.

```yaml
---
title: Short label, for the sidebar and the browser tab
description: One clause saying what a reader gets from this page
type: index | topic | lesson | reference | glossary | resources
---
```

- **`title`** is the short form, not a copy of the `#` heading. The two are read in different places: the site renders `title` as the visible page heading and hides the markdown `#`, while GitHub shows the `#` and never sees the front matter. So the `#` heading carries the long name for a GitHub reader, and `title` carries the short one for the sidebar, where a long name clips mid-word. A lesson drops the word "Lesson", since it already sits under `Lessons`.
- **`description`** is one clause, no trailing period. For a lesson it is the same clause as its row in the workspace `README.md` table, and the front matter is canonical: change it here first, then match the table.
- **`type`** names the shape of the page, so a reader, human or machine, knows what it is before reading it. Use exactly one of the six values.

**Quote a value that starts with punctuation, or contains a colon followed by a space.** Both make the front matter invalid YAML, and the failure is silent: MkDocs drops the whole block, falls back to the filename for the page title, emits no description, and `--strict` reports nothing. A lesson whose `description` opened with `%w` shipped that way. The scripted parse below is what catches it.

Do not add a date. The site derives `created_at` and `updated_at` from git history, and a hand-written date goes stale the first time someone forgets it.

`order` is read by the theme and overrides a page's position in the navigation. Leave it out while lesson filenames still sort correctly on their own number.

## Rendering

`learning/` is the `docs_dir` of a MkDocs site, and the same files are read on GitHub. Both renderers have to be right.

- Keep `markdown="1"` on every `<details>`. Python-Markdown needs it, through the `md_in_html` extension, to parse the answer inside. GitHub ignores the attribute, so the file stays correct in both.
- Leave a blank line after `<summary>` and before `</details>`.
- Keep every `<details>` block at column zero, always. The constraint is indentation, not nesting, so read these three together:
  - Never indent a block to sit inside a list item. It looks tidier and breaks the site: `md_in_html` does not parse HTML nested in a list, and the answer reverts to literal markdown. `sane_lists` carries the Practice numbering across the break instead.
  - One `<details>` may sit inside another when both stay at column zero and both keep `markdown="1"`. Verified on a built page: the inner block renders as HTML and its markdown becomes `<p>` and `<code>`.
  - Two blocks in a row work too, and the numbering resumes after either shape.
- A single newline is a line break, as it is on GitHub. Lesson header blocks, glossary definitions and worked calculations rely on it. This holds only because no prose here is hard-wrapped, so keep it that way and write a paragraph on one line.
- `mkdocs.yml` owns the extensions these rules depend on: `md_in_html`, `sane_lists`, `nl2br`, `pymdownx.highlight`, `pymdownx.superfences`. Removing one breaks every lesson at once.

Not everything in a workspace is published. `mkdocs.yml` excludes `NOTES.md` and `learning-records/`: they hold the learner's state (preferences, disclosed background, corrected misconceptions) and stay out of the site whether or not the repository is public.

Everything else is published, `RESOURCES.md` included. Workspace `README.md` files and lessons link to it, and a reader deserves the sources a claim rests on as much as the claim itself.

## Verification

Before presenting the lesson, confirm by reading:

- Every answer key is correct and collapsed, with no formatting tells.
- Terminology matches `GLOSSARY.md`.
- No placeholders remain.
- The `README.md` table has a row for the new lesson, its clause is the same as the lesson's front-matter `description`, and the **Latest lesson** pointer names it.

Then confirm by running `.venv/bin/mkdocs build --strict`.

A clean strict build proves the navigation resolves. It proves less than it looks like it proves: not that the answer keys survived, and not even that the front matter parsed. So open the built page, `site/<domain>/<topic>/lessons/<slug>/index.html`, and check three things that look fine in the source and break silently:

- The `<title>` is the front matter `title`. When the YAML fails to parse, MkDocs falls back to the filename and says nothing.
- Markdown inside each `<details>` rendered as `<p>` and `<code>`, not as literal backticks. It reverts when `markdown="1"` is missing.
- Each Practice list resumed with `<ol start="N">` after an answer. It restarts at 1 when the `<details>` block is indented instead of sitting at column zero.

One rendering trap is worth knowing before you write, because it is invisible in the source and silent in a strict build. **Never put `<` immediately followed by `?` inside a collapsible block.** Python-Markdown's HTML block parser reads `<?` as the start of a processing instruction, and that parser runs before inline code is protected, so backticks do not save it: a single `` `List<?>` `` inside a `<details markdown="1">` block stops `md_in_html` processing that block *and every later block in the file*, which ships the raw tag and the unparsed markdown to the page. Write `<code>List&lt;?&gt;</code>` instead, which renders identically. A space is already safe, so `` `Map<String, ?>` `` needs no change. The checker below catches both the cause and the effect.

A second rendering trap, from the same family and found the same way. **A backslash does not escape a backtick inside an inline code span.** An author whose span content is itself backtick-delimited, which happens constantly once template literal types are in play, reaches for `` `...\`inner\`...` `` and gets a span that ends at the first inner backtick, leaking a stray `</code>` and a literal backslash into the middle of a sentence. Use a fenced block for a diagnostic, or a padded doubled delimiter for a short span. Note the one legitimate case the checker deliberately allows: a span whose whole content is a single backslash, as when a lesson discusses a line-continuation escape, which is why the rule looks for two escaped backticks on a line rather than one.

Do not read for the structural checks, run them: `python3 .agents/tools/check-workspace.py learning/<domain>/<topic>`, which takes one or more workspaces and exits non-zero on any problem. It covers front matter and its keys, the H1 against the front-matter title, the three bold lines, section presence and order, `<details markdown="1">` at column zero with a blank line after `<summary>` and before `</details>`, balanced tags, the closing block byte for byte, dashes, draft markers, machine-specific strings, relative links, contiguous numbering, README rows against lesson front matter, and glossary ordering. Extend that script rather than writing a new one; where a rule is one workspace's local convention it belongs in its `CONVENTIONS` entry, not in the shared rules.

Two traps when checking external links. Strip fenced and inline code first, or code that looks like link syntax, such as the Go generics in `Map[T, U any](s []T)`, reports as a broken link. And send a browser user agent, because some hosts answer a scripted one with a 403 that reads as a dead link.
