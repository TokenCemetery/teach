# TODO

Planned work on the repository itself, not on any topic's lessons. Every item here came out of validating `.agents/skills/teach/SKILL.md` against the upstream skill it was forked from, at `github.com/mattpocock/skills`, path `skills/productivity/teach`, repository version 1.2.3, checked on 2026-08-30.

Each phase is written to be run on its own, in its own session, without the conversation that produced it. That is deliberate: a phase states why the change is wanted, which file to open, what the file says now, what it should say, and how to check the result. If a phase cannot be executed from what is written here, that is a defect in this file.

## How to run a phase

1. Read `AGENTS.md`, then `.agents/skills/teach/SKILL.md`.
2. Read only the phase you are running. The phases are ordered by dependency, so do not skip ahead without reading the ordering note at the end.
3. Anchors below are quoted strings, not line numbers, because line numbers move. Search for the quoted text.
4. Run the phase's verification before reporting. Every phase includes one.
5. When a phase is finished, move its heading to `## Done` at the bottom with the date, and leave the detail behind. What was decided is worth more than the fact that it happened.

## Open decisions

Two questions are unresolved. They block the phases named, and a session that reaches one should ask rather than choose.

**D1: how far does the em dash cleanup reach?** Phase 5 counts 1427 em dashes across 86 files. The three candidate scopes are: documentation and templates only (70 dashes, 6 files), plus the Go workspace (851, 52 files), or everything including the fine-tuning workspace (1427, 86 files). Blocks phase 5 beyond wave 1.

**D2: does the linking rule apply to `learning/llm/finetuning/`?** `SKILL.md` now states that every link must lead to a source a reader can read, never to a venue for asking. The Go workspace follows it. The fine-tuning workspace does not: it has a `## Wisdom (Communities)` section in `RESOURCES.md`, a matching front matter description, a line in its `README.md`, and links to EleutherAI Discord and r/LocalLLaMA in lessons 0017, 0020 and 0027. In lesson 0020 the body text itself leans on consulting a community, so it is not a link deletion. Until this is decided, that workspace is knowingly non-compliant with its own skill. Independent of phase 5, but if D1 reaches the fine-tuning workspace, both should be closed in one pass.

---

## Phase 1: rules and metadata

Three small additions plus one clarification. Nothing here changes behaviour of existing content, so it is safe to run first.

### 1.0 Let `AGENTS.md` permit a planning document

**Why.** `AGENTS.md` says, under `## Quality bar for anything you write`: "No placeholders and no TODOs. The only exception is `templates/learning-workspace/`." The intent is that delivered work must not ship half-done with markers in it. A cold reader can also read it as forbidding this file, and might delete it. Fix the ambiguity rather than rely on interpretation.

**Where.** `AGENTS.md`, the `## Quality bar for anything you write` section.

**Now.**

```text
- No placeholders and no TODOs. The only exception is
  `templates/learning-workspace/`.
```

**Change.** Add the second exception, keeping the file's hard wrap at roughly 78 characters:

```text
- No placeholders and no TODOs. The only exceptions are
  `templates/learning-workspace/`, which keeps its `{placeholder}` markers, and
  `TODO.md`, whose subject is planned work.
```

**Verify.** `grep -n "TODO" AGENTS.md` names both exceptions.

### 1.1 Sources first when `RESOURCES.md` is thin

**Why.** The upstream skill carries a sequencing rule the fork lost: "Before the `RESOURCES.md` is well-populated, your focus should be to find high-quality resources which will help the user acquire knowledge." Our `## Grounding` says to read `RESOURCES.md` before reaching for model knowledge, but never says that on a new workspace the session's job may be sourcing rather than teaching. Without it, a first session produces a lesson grounded in nothing, and nothing about the result looks wrong.

**Where.** `.agents/skills/teach/SKILL.md`, sections `## Grounding` and `## Workflow` (subsection `### Setup`).

**Now.** `## Grounding` opens with "Read `RESOURCES.md` before reaching for parametric knowledge." `### Setup` step 4 reads "Choose the lesson target: what the user asked for, otherwise derive it, see Zone of Proximal Development."

**Change.** Add to `## Grounding`, as its own paragraph:

> **When `RESOURCES.md` is thin, finding sources is the work.** On a new workspace, or in an area the listed sources do not cover, spend the session locating and annotating high-trust sources instead of teaching from none. A session that produced no lesson is recoverable. A lesson grounded in nothing is not visibly missing anything, which is why it survives.

Then add a sentence to `### Setup` step 4, so the branch is visible where the target is chosen:

> If no listed source covers that target, close the gap first, see Grounding.

**Verify.** Both additions present, and `mkdocs build --strict` still passes (the skill is not published, but the build is the cheap guard against an accidental edit elsewhere).

### 1.2 Glossary subheadings

**Why.** Upstream's glossary format has a rule the fork lost: group terms under subheadings when natural clusters emerge. The Go glossary independently grew a `## Usage in this workspace` section above `## Terms`, which is evidence the rule was needed and its absence was noticed in practice rather than in review.

**Where.** `.agents/skills/teach/SKILL.md`, section `## Formats`, subsection `### `GLOSSARY.md``, its `Rules:` list.

**Now.** The list has six bullets, ending "Revise in place as understanding deepens."

**Change.** Add one bullet before the last:

> - Group under subheadings when natural clusters emerge, such as `## Anatomy` or `## Syntax`. A flat list under `## Terms` is right until it stops being scannable.

**Verify.** `grep -c "subheading" .agents/skills/teach/SKILL.md` returns 1 or more. No existing glossary needs changing: the Go one already complies, and the fine-tuning one is a flat list that is still scannable.

### 1.3 Honest metadata

**Why.** The front matter makes three claims that do not hold. `upstream: github.com/PromptPasture/agent.md` is not supported by anything in the upstream copy, whose repository is `github.com/mattpocock/skills` (confirmed in its `package.json`). `version: "1.1.0"` corresponds to nothing checkable, because upstream versions the whole repository through changesets rather than per skill, and that repository is at 1.2.3. And the upstream skill has no `metadata` block at all, so the entire block is a local addition presenting itself as inherited.

**Where.** `.agents/skills/teach/SKILL.md`, YAML front matter.

**Now.**

```yaml
metadata:
  author: github.com/mattpocock/skills
  upstream: github.com/PromptPasture/agent.md
  version: "1.1.0"
  catalog: productivity
  category: learning
  tags: [learning, teaching, retention]
```

**Change.**

```yaml
metadata:
  upstream: github.com/mattpocock/skills
  upstream_path: skills/productivity/teach
  upstream_version: "1.2.3"
  version: "2.0.0"
  catalog: productivity
  category: learning
  tags: [learning, teaching, retention]
```

`author` goes because it named a repository rather than a person, and `upstream` now carries that. `license: MIT` stays where it is, outside the metadata block: upstream is MIT and the attribution has to survive. Version 2.0.0 rather than 1.2.0 because the fork is incompatible, not behind: lessons moved from HTML to markdown, and one workspace per directory became many workspaces in one repository.

**Verify.** The YAML parses. `python3 -c "import yaml,sys;print(yaml.safe_load(open('.agents/skills/teach/SKILL.md').read().split('---')[1]))"` prints the block without error.

---

## Phase 2: stop shipping empty directories

**Why.** `SKILL.md` says "Create each lazily, on first need." The template ships four empty directories and the two live workspaces ship two each, all held open by a `.gitkeep`. The rule and the repository disagree, and the repository is what gets copied. Separately, `assets/` has no purpose in a markdown workspace: upstream's `assets/` holds stylesheets, quiz widgets and simulators for HTML lessons, none of which port.

**Where.** Eight directories, each containing only `.gitkeep`:

```text
templates/learning-workspace/assets/
templates/learning-workspace/lessons/
templates/learning-workspace/reference/
templates/learning-workspace/learning-records/
learning/llm/finetuning/assets/
learning/llm/finetuning/learning-records/
learning/programming/golang/assets/
learning/programming/golang/learning-records/
```

**Change.** Delete all eight, including the `.gitkeep` files. Then remove every reference to `assets/`, which exists in exactly four places:

| File | Current text |
|---|---|
| `.agents/skills/teach/SKILL.md` | tree line ``└── assets/                # diagrams, drill banks, printable cards`` |
| `.agents/skills/teach/SKILL.md` | table row ``|`assets/*`|Reusable artifacts lessons link to, diagrams, drill banks, printable cards.|`` |
| `.agents/skills/teach/SKILL.md` | ``Create each lazily, on first need. Reuse is the default: read `reference/` and `assets/` before authoring, and build on what is there.`` |
| `learning/README.md` | tree line ``└── assets/                # diagrams, drill banks, printable cards`` |

In the third, keep the reuse rule and drop the dead half: "Reuse is the default: read `reference/` before authoring, and build on what is there." Fix the tree drawing characters so the last remaining entry uses `└──`.

Also adjust `### Setup` step 2, which currently reads "Read `README.md`, `NOTES.md`, `GLOSSARY.md`, `RESOURCES.md`, and `learning-records/`." Once directories are created lazily, `learning-records/` may not exist, and a step that reads it unconditionally is wrong. Say that its absence means no record has been earned yet.

**Do not** delete `reference/` in the two live workspaces: both hold real sheets. Only the template's copy is empty.

**Verify.** `find learning templates -type d -empty` prints nothing. `grep -rn "assets" .agents/ learning/README.md templates/` prints nothing. `mkdocs build --strict` passes. `cp -r templates/learning-workspace /tmp/probe` produces a workspace with four markdown files and no directories, which is what the lazy rule intends.

---

## Phase 3: split the skill into three files

**Why.** `SKILL.md` is 392 lines, and 181 of them (46 per cent) are file templates that matter only when writing one specific file type. Another 54 are purely about publishing. `AGENTS.md` requires reading the whole thing before editing any workspace file, so every session pays for the templates whether or not it writes one. Upstream solves this with a 140 line `SKILL.md` and four format files loaded on demand.

Run this after phases 1 and 2, so the additions and deletions do not have to be moved twice.

**Change.** Three files, not upstream's five. Front matter and rendering rules apply to all six formats in our repository, so a file per format would duplicate them six times.

| File | Sections moved into it |
|---|---|
| `SKILL.md` (stays) | Workflow, Layout, New Topic, Linking Across Workspaces, Philosophy, Lesson Design, Grounding, Zone of Proximal Development, Learning Records, Wisdom, Error Paths |
| `FORMATS.md` (new) | Formats, with all six templates and their rules |
| `PUBLISHING.md` (new) | Front Matter, Rendering, Verification |

Expected sizes: about 157, 181 and 54 lines, totalling the 392 the single file has now.

Requirements on the result:

- `SKILL.md` links both new files where the reader needs them: Formats from the Loop step that drafts a lesson, Publishing from Lesson Design and from the Exit criteria.
- Each new file opens with one sentence saying what it governs and that `SKILL.md` is the entry point.
- No rule is duplicated across files. If two files both want a rule, one owns it and the other links.
- `AGENTS.md` currently says "Read `.agents/skills/teach/SKILL.md` before you create or edit any file inside a workspace. It defines every path, every file format, and what the published site needs." After the split that sentence is wrong in detail: update it to name `SKILL.md` as the entry point and the other two as what it points at.
- `AGENTS.md` also references the skill in `## Checking your work` as the place that "lists what it misses and how to check the rest". That target moves to `PUBLISHING.md`.

**Verify.** `grep -rn "SKILL.md#" .` finds no anchor links into moved sections. `wc -l` on the three files totals within a few lines of 392. Read `SKILL.md` end to end as if new: it should be possible to orient without opening either other file.

---

## Phase 4: interactivity within markdown

**Why.** Upstream teaches skills through interactive HTML: quizzes, simulators, in-browser tasks, all built on a component library. None of it ports, because the same files are read on GitHub where no script runs. What can port is the function those things served, which is a tight feedback loop. Three candidates below, one of which needs a prototype before it can be promised.

### 4.1 Prototype graduated hints

**Why.** Practice currently offers one collapsed `Check`. A `Hint` before it would let the learner try, get a nudge, then see the answer, which is the desirable difficulty our own `## Philosophy` argues for and only half implements.

**Risk that makes this a spike rather than a task.** It needs a `<details>` inside a `<details>`. `SKILL.md` already documents that `md_in_html` does not parse HTML nested inside a list item, and nesting may fail the same way. Prototype before deciding.

**Procedure.** In a scratch lesson file, write a Practice item with a nested `Hint` inside the answer block and a sibling variant with `Hint` and `Check` as two separate blocks. Run `.venv/bin/mkdocs build --strict`, open the built HTML, and check three things: the inner block rendered as HTML rather than as literal `<details>` text, markdown inside it became `<p>` and `<code>` rather than backticks, and the surrounding ordered list still resumed with `<ol start="N">`. Check the same file on GitHub, which ignores `markdown="1"` and may behave differently.

**Outcome.** If both variants fail, record that in `PUBLISHING.md` under Rendering as a known limit and close this item. If the sibling variant works and the nested one does not, adopt the sibling form.

### 4.2 Adopt hints, if 4.1 succeeded

Write the pattern into Lesson Design and into the lesson template in `FORMATS.md`, then apply it to one Go lesson as a worked example. Lesson 0003 on slice aliasing is the best candidate: its practice items are predictions where a nudge is genuinely useful.

Do not retrofit all 37 lessons. New lessons and one example are enough to establish the pattern.

### 4.3 A drill bank as a reference type

**Why.** Upstream keeps reusable drill material in `assets/`, which phase 2 deletes. The need is real and markdown can hold it: a bank of retrieval questions per stage, built for spaced practice across sessions rather than for one sitting.

**Change.** Add it to the `reference/` description in `FORMATS.md` as a recognised sheet type, alongside syntax tables and checklists. Optionally build one for the Go workspace covering stages 1 to 3, which is where retrieval matters most.

### 4.4 Name the predict-then-run move

**Why.** The Go lessons use a pattern that is not written down anywhere: state a snippet, ask for the output before running it, then make running it a real world rep. It is the tightest feedback loop available without scripting, and right now it survives only as an author's habit.

**Change.** One bullet in Lesson Design describing it.

---

## Phase 5: em dashes

**Why.** Upstream removed every em dash from its prose and recorded the rule in its own `AGENTS.md`: rewrite the sentence with a comma, colon, period, parentheses or a conjunction, whichever the sentence actually wants, and never do a blind character substitution. Our fork predates that and is saturated. There is a second, independent argument: a heavy em dash rate reads as a machine writing tell, and 781 dashes across 37 Go lessons is roughly 19 per lesson.

**Scope.** Blocked on decision D1 beyond wave 1.

| Area | Dashes | Files |
|---|---|---|
| `.agents/skills/teach/SKILL.md`, `AGENTS.md`, `README.md`, `templates/`, `learning/README.md` | 70 | 6 |
| `learning/programming/golang` | 781 | 46 |
| `learning/llm/finetuning` | 576 | 34 |

**Cost, stated plainly.** This is about 1400 sentence level rewrites, not a `sed` run. A mechanical substitution produces worse prose than the dashes did, which is why upstream forbids it. Budget accordingly.

**Risk, stated plainly.** In the lessons the dash carries a specific move: a claim, then the reason it matters. Rewriting changes the voice, sometimes noticeably, and across several hundred edits some results will be worse than the original. That is the price of the rule rather than a side effect of doing it badly.

### 5.1 Record the rule first

Before touching any prose, add the rule to `AGENTS.md` under `## Quality bar for anything you write`. Without it the next session reintroduces dashes and the work is spent twice. This is the same lesson that removed `.agents/memory/`: a rule that is not in a committed document is not a rule.

Suggested wording, matching the file's existing voice and wrap:

```text
- No em dashes in prose. Where a sentence reaches for one, rewrite it with a
  comma, colon, period, parentheses or a conjunction, whichever the sentence
  wants. Never substitute the character mechanically.
```

### 5.2 Wave 1: documentation and templates

70 dashes in 6 files. Small enough to be a pilot, and it covers the files a future session reads before doing anything else. Judge here whether the resulting style holds up before committing to the lessons.

### 5.3 Wave 2 and beyond

One workspace per pass, with `mkdocs build --strict` and a structural lint after each. Do not mix a workspace's dash cleanup with any other change: a diff of a few hundred prose rewrites is unreviewable if something else is hiding in it.

---

## Ordering

Phases 1, 2 and 3 in that order. The rules in phase 1 are cheap to add before the file is split, and the deletions in phase 2 are cheaper before the sections move. Splitting last means the move happens once.

Phase 4 depends on phase 3 only for where its output lands, and its spike (4.1) can run at any time.

Phase 5 is independent of everything and should be last, because it produces the largest and least reviewable diffs. Its wave 1 also touches files that phases 1 to 3 are rewriting, so running it earlier means editing the same sentences twice.

## Done

Nothing yet.
