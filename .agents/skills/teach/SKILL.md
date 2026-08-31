---
name: teach
description: Teaches a topic across multiple sessions from a persistent learning workspace, producing short markdown lessons grounded in a stated mission. Use when the user asks to be taught or coached on something over time.
disable-model-invocation: true
argument-hint: "What would you like to learn about?"
license: MIT
metadata:
  upstream: github.com/mattpocock/skills
  upstream_path: skills/productivity/teach
  upstream_version: "1.2.3"
  version: "2.0.0"
  catalog: productivity
  category: learning
  tags: [learning, teaching, retention]
---

# Teach a Topic

Teaching is stateful. The user intends to learn this topic over many sessions, so each session reads the workspace, produces one short lesson, and records only what the session earned.

Any topic qualifies — a language, a framework, thermodynamics, yoga, sourdough.

This copy is the authoritative format for this repository. It is forked from the upstream skill and carries rules the generic version cannot know: where workspaces live, how they link, and what the published site needs. Where a personal skill of the same name disagrees, this file wins.

Two companion files hold the detail this one points at: [`FORMATS.md`](FORMATS.md) for what each file in a workspace must contain, and [`PUBLISHING.md`](PUBLISHING.md) for front matter, rendering and the checks before a lesson is presented. Open one when you are about to write the file it governs, not before.

## Workflow

### Goal

One lesson written to `lessons/NNNN-<slug>.md`, tied to the mission and inside the user's zone of proximal development, plus the state updates that lesson earned.

### Setup

1. Locate the workspace: `learning/<domain>/<topic>/` — a `README.md` sitting beside a `lessons/` directory. If the topic has no workspace yet, create one; see New Topic.
2. Read `README.md`, `NOTES.md`, `GLOSSARY.md`, `RESOURCES.md`, and `learning-records/`. List `lessons/` and `reference/` to see what has been taught, and to catch a drifted lesson table. Directories are created lazily, so a missing `learning-records/` means no record has been earned yet, not that something is broken.
3. If the mission in `README.md` is vague, interview the user on why they want this before teaching anything, then rewrite it and confirm. A bad mission is worse than no mission.
4. Choose the lesson target: what the user asked for, otherwise derive it — see Zone of Proximal Development. If no listed source covers that target, close the gap first, see Grounding.

### Loop

1. Ground the knowledge — see Grounding. Add any new source to `RESOURCES.md` with its annotation.
2. Draft one lesson — see Lesson Design and the [`lessons/` template](FORMATS.md#lessons). Number it above the highest existing lesson.
3. Write the lesson file, add its row to the `README.md` lesson table, move the **Latest lesson** pointer, then offer to open it.
4. Promote durable knowledge out of the lesson: a `reference/` sheet when the material will be consulted again, a `GLOSSARY.md` term once the user can use it correctly.
5. Write a learning record only if the session earned one — see Learning Records.

### Exit

The lesson file is written, the checks in [`PUBLISHING.md`](PUBLISHING.md) pass, the user knows where it is, and earned state updates are recorded.

### Report

The lesson path, what it teaches, how it serves the mission, its primary source, which state files changed, and the likely next lesson.

## Layout

Workspaces live at `learning/<domain>/<topic>/`. A domain directory — `programming/`, `llm/` — holds topic directories and nothing else. Never put a lesson, a mission, or a stray file directly in one.

```text
learning/<domain>/<topic>/
├── README.md              # mission, success criteria, lesson index
├── GLOSSARY.md            # canonical terms for this topic
├── RESOURCES.md           # trusted sources, known gaps
├── NOTES.md               # preferences and working notes
├── lessons/               # NNNN-slug.md — one tight win each
├── reference/             # cheat sheets, built for lookup
└── learning-records/      # NNNN-slug.md — what was demonstrably learned
```

|Path|Holds|
|---|---|
|`README.md`|Landing page: the mission, the lesson index, where a visitor starts.|
|`RESOURCES.md`|Annotated high-trust sources a reader can go and read. Gaps listed explicitly.|
|`GLOSSARY.md`|Canonical terms the user already understands. Once here, use them everywhere.|
|`lessons/NNNN-*.md`|The lessons. One tight win each.|
|`reference/*.md`|Cheat sheets: syntax, algorithms, sequences, poses, routines.|
|`learning-records/NNNN-*.md`|Evidence-grade insights that set what to teach next. The ADRs of learning.|
|`NOTES.md`|What is true about *this learner*, and nothing else.|

Create each lazily, on first need. Reuse is the default: read `reference/` before authoring, and build on what is there.

`NOTES.md` is the easiest file to abuse, because it is the only one with no reader to answer to. Hold it to one test: **would this still be true if someone else were learning this topic?** If yes, it is not a note — it is content, and it belongs in a published file where a reader can use it. Preferences, disclosed background, calibration plans, environment blockers and open questions stay. A curriculum arc, a corrected fact, a source worth trusting and a term worth pinning do not.

Lessons number from `0001` within each workspace.

## New Topic

1. Copy the template:

   ```bash
   cp -r templates/learning-workspace learning/<domain>/<topic-slug>
   ```

2. Interview the user, then write the mission into the new `README.md`. A vague mission misdirects every lesson that follows.
3. Add a row for the topic to the table in `learning/README.md`.

Never teach into `templates/learning-workspace/`. It is only a copy source, it keeps its `{placeholder}` markers, and it never appears in an index.

## Linking Across Workspaces

Workspaces may link to each other. A link is a pointer, not an inclusion: it does not move another topic's material into this mission, does not become a prerequisite the reader must finish first, and does not quietly empty the `## Out of scope` list.

Prefer the most stable target. A `GLOSSARY.md` term or a `reference/` sheet is written for lookup and lands on any reader. Lessons are ordered and assume their own prerequisites, so a link into the middle of another workspace's arc reaches someone who has not earned it. Say what the reader will find there and why they would want it.

One topic per workspace still holds. A different topic is a new workspace, not a second mission — linking is how the two connect.

## Philosophy

Deep learning needs **knowledge** from high-trust sources, **skills** from practice the user actually performs, and **wisdom** from the real world. Some topics lean knowledge-heavy (theoretical physics), others skill-heavy (yoga) — calibrate.

Separate **fluency strength** (in-the-moment retrieval) from **storage strength** (long-term retention). Fluency feels like mastery and isn't. Build storage strength through desirable difficulty: retrieval practice, spacing across sessions, interleaving related skills. For acquiring knowledge, difficulty is the enemy — it eats the working memory needed to understand. For practicing skills, difficulty is the tool.

## Lesson Design

- **Short.** Completable in one sitting. Working memory is small; one tangible win per lesson.
- **Only the knowledge the skill needs.** Teach that, then have the user practice it.
- **Self-contained feedback.** Practice carries its own answer key: recall prompts with collapsed answers, and real-world reps the user performs away from the screen. Close by inviting the user to bring answers or sticking points back to the session.
- **Answer-key discipline.** Keep answers collapsed. Hold every multiple-choice option to the same word count, and character count where possible — formatting must not leak the answer.
- **Graduated hints, where a nudge is enough.** A prediction or a debugging prompt may carry a collapsed `Hint` before its `Check`, as a sibling block rather than nested inside the answer: a hint reachable only by opening the answer is not a hint. Use it where one push gets the learner unstuck, and leave it off recall prompts, where a hint is the answer arriving early.
- **Spacing and interleaving.** Open with two or three recall items from earlier lessons, and mix related skills into practice sets rather than drilling one in isolation.
- **Predict, then run.** Where the material has a runnable or observable form, show it, ask what will happen before the user finds out, then make finding out a real-world rep. The gap between the prediction and the result is what teaches; a demonstration the user watched teaches much less.
- **Linked.** Link the `reference/` sheets, glossary terms, and prior lessons a reader would want next.
- **One primary source.** Name the single best source found for the user to read or watch.
- **Readable.** These get revisited: clean headings, short paragraphs, no walls of text.

A lesson is read on two renderers, and the collapsed answer keys are the part that breaks silently. [`PUBLISHING.md`](PUBLISHING.md) has the rules they depend on and the checks that catch it.

## Grounding

Read `RESOURCES.md` before reaching for parametric knowledge. When a claim is factual, version-sensitive, or contested and lookup is available, verify it, cite it inline, and add the source to `RESOURCES.md` with a one-line annotation.

**When `RESOURCES.md` is thin, finding sources is the work.** On a new workspace, or in an area the listed sources do not cover, spend the session locating and annotating high-trust sources instead of teaching from none. A session that produced no lesson is recoverable. A lesson grounded in nothing is not visibly missing anything, which is why it survives.

When lookup is unavailable or the material is stable and uncontested, teach from model knowledge — but never dress an uncited claim as sourced, and record what is missing under `## Gaps` so a later session can close it. Prune sources that turn out to be shallow, wrong, or off-mission.

## Zone of Proximal Development

Every lesson should feel challenging just enough. When the user hasn't named a target, derive it: the learning records give the current floor, the mission gives the direction, and the lesson goes in the gap between them.

## Learning Records

Write one when the session produced any of:

- Evidence the user can use a non-trivial concept correctly, not merely that it was covered.
- Prior knowledge the user disclosed, including the depth claimed, so it isn't re-taught.
- A corrected misconception — these predict future stumbling blocks.
- A shift in the mission driven by what the user learned.

Coverage is not learning. Do not log session activity, and do not restate a definition that already lives in `GLOSSARY.md`. When a later record overturns an earlier one, mark the old one `Status: superseded by LR-NNNN` rather than deleting it.

## Wisdom

When a question needs judgment rather than facts, answer it as well as you can, say what the answer rests on, and name what would change it. Then point the user at where that judgment is already written down — a style guide, a review checklist, a specification, a practitioner's post arguing the case — and at the real-world reps, which is where they test it themselves.

**Every link leads to a source someone can read.** The test is the annotation you would write for it: "Use for: reading X" belongs, "Use for: asking X" does not. Chats, forums and subreddits fail it however well moderated — they need an account, they answer on their own schedule, and what was said is rarely retrievable later. Documentation, specifications, books, articles and style guides pass.

This is why `RESOURCES.md` has no communities section, and why a lesson's **Going further** links sources rather than places.

## Error Paths

- The user wants a second, unrelated topic → that is a second workspace, not a second mission.
- The mission appears to have changed → confirm with the user, then update the mission in `README.md` and write a learning record.
