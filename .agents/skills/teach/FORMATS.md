# File formats

What each file in a workspace must contain, one section per file type. `SKILL.md` is the entry point; open this when you are writing one of these files.

Every template below omits the front matter for brevity. It is still required; see [`PUBLISHING.md`](PUBLISHING.md).

## `README.md`

The landing page a visitor opens, on GitHub and on the site. Carries the mission that grounds every teaching decision, and the index of what has been taught.

```md
# Learning: {Topic}

{1-3 sentences. The concrete real-world goal. What changes in the user's life or work when they have this skill? Avoid "to understand X" — push for the outcome underneath.}

**Latest lesson:** [{NNNN} — {Title}](lessons/NNNN-slug.md)

## Success looks like

- {A specific, observable thing the user will be able to do}

## Constraints

- {Time, budget, prior commitments, learning preferences — anything that bounds the approach}

## Out of scope

- {Adjacent topics the user does not want to chase now}

## The arc

{N} stages. Not a lesson list — a stage takes several lessons, and the boundaries are soft.

|Stage|Covers|Done when|
|---|---|---|
|1. {Name}|{What it covers}|{The capability that closes the stage}|

## Lessons

Work through these in order.

|#|Lesson|Teaches|
|---|---|---|
|[0001](lessons/0001-slug.md)|{Title}|{The one win it delivers}|

## Reference

- [Glossary](GLOSSARY.md) — canonical terms for this topic
- [Resources](RESOURCES.md) — trusted sources, each annotated with what it covers
- [{Cheat sheet}](reference/slug.md) — {when to reach for it}

## How this works

Each lesson is short and self-contained. Answer keys are collapsed — recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Bring anything unclear back to the teaching session.
```

Rules:

- Concrete beats abstract: "Run a half marathon by October" over "get fitter"; "Ship a Rust CLI to my team" over "learn Rust".
- Keep the mission itself under a screen. Past that it has stopped being a compass. The arc may sit between it and the lesson table: stages answer "how far along am I", which the flat index cannot.
- The arc is the shape of the course, so it is public. It is not a plan of what to teach next — that is a working note.
- Keep each table row to number, title, and one clause. This is an index, not a summary. A table that has drifted from `lessons/` is worse than no table.
- Do not link `NOTES.md` or `learning-records/` from here. Working notes and a record of the user's corrected misconceptions stay unadvertised, whether or not the repository is public.

## `RESOURCES.md`

The curated set of trusted sources. Every claim in a lesson can be traced back to something listed here.

```md
# {Topic} Resources

## Knowledge

- [Article: "How Much Should I Train?" — Greg Nuckols, Stronger By Science](https://example.com)
  Evidence-based review of volume landmarks. Use for: weekly set targets per muscle group.

## Gaps

- {An area the mission needs and no good source covers yet}
```

Rules:

- High-trust only. Primary sources, recognised experts, peer-reviewed work, official documentation. Marketing dressed as education stays out.
- Readable sources only — see Wisdom in [`SKILL.md`](SKILL.md). A community is not a source, however good it is.
- Annotate every entry with one line: what it covers, when to reach for it. A bare link is useless in three months.
- Check that every link resolves before listing it, and prune sources that turn out to be shallow, wrong, or off-mission.

## `GLOSSARY.md`

The canonical language of the workspace. Lessons, reference sheets, and records all adhere to it.

```md
# {Topic} Glossary

{One or two sentences on what this glossary covers.}

## Terms

**Progressive overload**:
Systematically increasing the demand on a muscle over time, via load, volume, or intensity.
_Avoid_: pushing harder, levelling up
```

Rules:

- This records compressed understanding; it is not a dictionary the user reads to learn.
- Be opinionated. Pick the best word for a concept and list the rest as aliases to avoid.
- Definitions are one or two sentences and say what the term **is**, not how to do it.
- Use glossary terms inside glossary definitions.
- Resolve loose field usage explicitly: "In this workspace, 'set' always means a working set."
- Group under subheadings when natural clusters emerge, such as `## Anatomy` or `## Syntax`. A flat list under `## Terms` is right until it stops being scannable.
- Revise in place as understanding deepens.

## `learning-records/`

`learning-records/NNNN-<slug>.md`, numbered one above the highest existing file.

```md
# {Short title of what was learned or established}

{1-3 sentences: what was learned, or what prior knowledge was established, and why it changes what to teach next.}
```

That is the whole format — a single paragraph is a complete record. Add **Evidence** (how the user demonstrated it) or **Implications** (what it unlocks or rules out) only when non-obvious.

## `lessons/`

`lessons/NNNN-<slug>.md`, numbered one above the highest existing lesson.

```md
# Lesson {N} — {Title}

**Mission link:** {the one line connecting this to the mission}
**Primary source:** [{title}]({url})
**Prerequisites:** [Lesson {N-1}](NNNN-slug.md), [{term}](../GLOSSARY.md)

## Warm-up

{Two or three recall prompts from earlier lessons, same collapsed shape as Practice. Skip in lesson 0001.}

## Know this

{The minimum knowledge the skill needs. Short paragraphs. Cite claims inline where a source exists.}

## Practice

{Retrieval prompts, ordered easy to hard. Interleave a related skill where it fits.}

1. ▢ {Prompt}

<details markdown="1"><summary>Check</summary>

{Answer, plus why the wrong instinct is wrong.}

</details>

## Real-world reps

- [ ] {Something to do today, away from the screen}
- [ ] {Something to do tomorrow — spacing is the point}

## Going further

- [{Reference sheet}](../reference/slug.md)
- [{Primary source}]({url})
- [{A further source, when the next step needs more than this lesson gave}]({url})

---

Not landing? Reread the primary source at the top — this lesson compresses it, and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
```

The closing block is fixed text — copy it verbatim. Lessons are read by people with no teaching session attached to them, so it points at the material and at the issue tracker rather than at a teacher.

See [Rendering](PUBLISHING.md#rendering) for the constraints the `<details>` blocks have to satisfy.

## `reference/`

`reference/<slug>.md`. The compressed essence of what lessons taught, built for quick lookup: syntax tables, algorithms, flowcharts, pose sequences, routines, checklists.

Lessons are rarely revisited; these are. Optimise for scanning — tables and short lists over prose — and keep them printable.
