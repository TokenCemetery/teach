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

Phase 4 next. Phase 5 last, because it produces the largest and least reviewable diffs.

## Done

### Phase 1: rules and metadata, 2026-08-31

Four commits, one per task. The rules themselves now live where they are read, so what is worth keeping here is only what the files do not say.

- **1.0** `AGENTS.md` names two exceptions to the no-TODOs rule: the template, for its `{placeholder}` markers, and this file.
- **1.1** Sourcing is the work when `RESOURCES.md` is thin. Restored from upstream into `## Grounding`, with the branch repeated at `### Setup` step 4 because that is where the target is chosen and where the omission would bite.
- **1.2** Glossary subheadings allowed. Both live glossaries, not just the Go one, had already grown a `## Usage in this workspace` section, which is stronger evidence for the rule than upstream carrying it. Neither term list was regrouped: both are still scannable flat, and the rule says a flat list is right until it stops being.
- **1.3** Metadata corrected. `author` dropped because it named a repository; `upstream` carries that, with `upstream_path` and `upstream_version` so the claim is checkable against a specific tree. `version: "2.0.0"` asserts incompatibility with upstream rather than lag. Left open deliberately: nothing consumes `version`, so its semantics are a convention this repository owes itself, not a contract.

### Phase 2: stop shipping empty directories, 2026-08-31

Two commits, split by argument rather than by directory: `assets/` went because the concept does not port, and the rest went because the skill already said to create directories lazily.

- Ten `.gitkeep` files, not eight. Two of them sat in `learning/programming/golang/lessons/` and `reference/`, which had since filled with real files, so they were holding open a directory that no longer needed holding. Worth knowing that the count in a plan is a snapshot: check before deleting, do not trust the list.
- `assets/` is gone from both layout trees, the path table and the reuse rule. The reuse rule kept `reference/`, which is where a drill bank now belongs; phase 4.3 depends on that.
- `### Setup` step 2 now says a missing `learning-records/` means no record has been earned. Without that, lazy creation and an unconditional read contradict each other, and the agent hitting it would guess.
- Copying the template now yields four markdown files and no directories, verified with a real `cp -r`.

### Phase 3: split the skill into three files, 2026-08-31

One commit, because a split is not divisible: any smaller step leaves the skill describing a structure it does not have.

- Sizes came out at 161, 184 and 57 lines against the plan's 157, 181 and 54. The four extra lines are the two new file headers.
- Cut with a script rather than by hand, then diffed line multisets between the old file and the three new ones. Everything the diff reported lost was a heading demotion or one of four cross-references that used to point inside the same file. Worth repeating on any future move: a split is exactly the change where a careful reader misses a dropped rule.
- `FORMATS.md` links `PUBLISHING.md` for front matter and rendering, and `SKILL.md` for Wisdom, which owns the readable-sources rule. Anchors used: `FORMATS.md#lessons` and `PUBLISHING.md#rendering`.
- Two stale claims elsewhere surfaced and were fixed on the way: `README.md` still listed `.agents/memory/` in its layout, and its MIT exception named one file when the directory now holds three.
- Left alone deliberately: `README.md` says the skill came from `mattpocock/skills` via `PromptPasture/agent.md`. Phase 1.3 dropped that chain from the skill metadata because the upstream copy does not corroborate it, but absence of corroboration is not disproof, and attribution is the one claim not to trim on a hunch. Someone who knows whether that fork is real should decide.
