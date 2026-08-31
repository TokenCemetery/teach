# TODO

Planned work on the repository itself, not on any topic's lessons. Every item here came out of validating `.agents/skills/teach/SKILL.md` against the upstream skill it was forked from, at `github.com/mattpocock/skills`, path `skills/productivity/teach`, repository version 1.2.3, checked on 2026-08-30.

Each phase is written to be run on its own, in its own session, without the conversation that produced it. That is deliberate: a phase states why the change is wanted, which file to open, what the file says now, what it should say, and how to check the result. If a phase cannot be executed from what is written here, that is a defect in this file.

## How to run a phase

1. Read `AGENTS.md`, then `.agents/skills/teach/SKILL.md`.
2. Read only the phase you are running.
3. Anchors are quoted strings, not line numbers, because line numbers move. Search for the quoted text.
4. Run the phase's verification before reporting. Every phase includes one.
5. When a phase is finished, replace it with an entry under `## Done`, keeping what was decided rather than the fact that it happened.

All five planned phases are done. What is left is under Remaining.

## Remaining, outside a phase

**Build a drill bank for the Go workspace, stages 1 to 3.** `FORMATS.md` now recognises the sheet type and nothing uses it. Lessons 0001 to 0021, retrieval questions with collapsed answers, grouped by stage. This is content authoring rather than repository work, so it belongs in a teaching session that has the lessons open, not in a plan phase. It was optional in phase 4 and stayed optional.

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

### Phase 4: interactivity within markdown, 2026-08-31

Five commits. The spike answered its own question in one build, and the answer changed what got adopted.

- **4.1** Both variants render. A `<details>` inside a `<details>` at column zero parses correctly, inner markdown becomes `<p>` and `<code>`, and numbering resumes after either shape. The existing warning in Rendering was about indenting a block into a list item, and its wording invited the wrong inference; it now says so. Recorded in `PUBLISHING.md`.
- **4.2** Adopted the sibling form, and not because nesting failed. Nesting works, but a hint you can only reach by opening the answer is not a hint, so the technical result did not decide it. Applied to lesson 0003 on the two prediction items; the recall items were left alone deliberately.
- **4.3** Drill bank recognised in `FORMATS.md` as a `reference/` sheet, with the caveat that it is the one sheet not built for scanning. Building the Go one moved to Remaining above.
- **4.4** Predict-then-run named in Lesson Design.
- Not verified: how a nested `<details>` renders on GitHub. The site was checked on a real build; GitHub was not, because checking it means pushing the scratch file or sending content to a rendering API. The sibling form we adopted is the shape already in use, so nothing shipped depends on the unverified case.

### Phase 5, wave 1: documentation, templates and the skill, 2026-08-31

Three commits: the rule, then the six documentation and template files, then the three skill files. 69 dashes rewritten, 3 held.

- **5.1** The rule went into `AGENTS.md` first, and had to say more than the suggested wording. Recording "no em dashes in prose" while 1357 sit in the lessons would have put the rule and the repository straight into the disagreement that phase 2 existed to fix, so the rule names the backlog as a backlog.
- What the rewrites actually needed: a colon where the second half explains the first, which covered most of them; parentheses for a mid-sentence aside; a conjunction or a full stop for the rest. No instance wanted the same replacement as its neighbour, which is the argument against a scripted pass in one line.
- Two traps found, both in YAML. `site_description` in `mkdocs.yml` needed quoting once it contained a colon and a space, and the same rewrite in the front matter template of `PUBLISHING.md` would have shipped an example that does not parse. It reads "One clause saying what" now.
- Three dashes were held back in the lesson template, because each was shared verbatim with 64 published lessons and could not move without them. They moved in waves 2 and 3, below.

### D2: the linking rule and communities, decided 2026-08-31

Softened, and the softening changed the axis rather than carving an exception. The old rule banned communities on three objections: an account, a delay, and an answer nobody can retrieve. Only the third is inherent to the venue. The other two describe posting a question, not reading what is already there.

So the test is now how the destination is used. A subreddit read as an archive of practitioner reports is a source; the same subreddit framed as somewhere to post and wait is not. `RESOURCES.md` may carry a `## Wisdom (Communities)` section, with the annotation naming what is there to read.

- Three of the four fine-tuning entries pass unchanged in substance and had their annotations rewritten to say why: r/LocalLLaMA, the Hugging Face forums, MLX Discussions.
- The EleutherAI Discord fails on retrievability and was replaced with the EleutherAI blog, in `RESOURCES.md` and in lessons 0020 and 0027. The entry states the omission so a later session does not add it back as an oversight.
- Nothing came back in the Go workspace. The link removed there was the Gophers Slack, a closed chat, which fails the softened rule for the same reason it failed the strict one. That is the check worth repeating when a rule is relaxed: confirm the earlier deletions were not collateral.

### Phase 5, waves 2 and 3: both workspaces, 2026-08-31

Fifteen commits, one per stage plus the mechanical passes. 1429 dashes at the start of the phase, zero at the end.

- The split between mechanical and prose held up, and doing the mechanical passes first was worth it. 309 instances fell to three regex passes over both workspaces: link text (comma for a publisher, colon for a section within a document, period for a lesson number), the annotation after a link (colon), and code comments (comma). The other 1120 were rewritten one at a time.
- What the prose actually wanted, in rough order of frequency: a colon where the second half explains the first; "because", "since" or "so" where the dash carried a causal claim; parentheses or a comma pair for a mid-sentence aside; a full stop where the clause could stand alone. Almost no instance wanted the same replacement as its neighbour, which is the concrete argument against a scripted pass.
- Four instances were not punctuation at all. Three were `—` used as a table cell meaning "not applicable" and one was a heading separator; each became the thing it actually meant, which is a small improvement the dash had been hiding.
- Three dashes held back from the earlier wave moved with the workspaces as planned: the lesson heading, its front matter `title`, and the fixed closing block. Titles took a period rather than a colon, since a colon in an unquoted YAML scalar does not parse.
- Found on the way out, and unrelated to dashes: lesson 0009's front matter opened with `%w`, so the whole block was invalid YAML. MkDocs silently titled the page from its filename and `--strict` said nothing. Fixed, and `PUBLISHING.md` no longer claims a clean strict build proves the front matter parses.
- One check to distrust: an early structural pass reported 259 indented `<details>` blocks. The regex used `\s+`, which matches a newline, so every block at column zero matched. Re-run with `[ \t]+` it reports none. A lint that finds a problem in every file is more likely to be wrong than the repository is.

### Verified against the deployed site, 2026-08-31

Everything above had been checked against a local build. Re-checked against `https://tokencemetery.github.io/teach/` after the deploy, by fetching every page in the sitemap and asserting on the DOM rather than by reading.

- 158 pages, 988 `<details>` blocks. All collapsed by default, all with a `<summary>`, none containing a literal backtick, none with escaped `&lt;details` markup. No page title derived from a filename, every page carrying a `description`.
- Zero em dashes in the rendered text of any page.
- Lesson 0009 renders as "9. Wrapping, Is and As" with its description present, which is the front matter fix confirmed on the artifact that was actually broken.
- The scratch spike file returns 404, and the fine-tuning `RESOURCES` page shows the softened linking rule live: the communities section is there, r/LocalLLaMA is there with its archive wording, the EleutherAI Discord is gone and its blog is in its place.
- **The one thing local verification could not reach: GitHub's renderer.** Checked on `github.com` directly. The sibling `Hint` and `Check` blocks render as collapsible details with markdown parsed inside (`<p>` and `<code>`, no backticks), and GitHub continues the Practice numbering across the break with `<ol start="2">` through `<ol start="5">`, exactly as the site does. The dual-renderer contract holds for the adopted form. Nested `<details>` on GitHub remains unverified and unused.
- A placeholder lint reported 14 pages. All false positives: Go composite literals such as `{Name: "original"}` and the routing wildcard `{path...}`. Same failure as the earlier `{id}` and `TODO` false positives, and the reason a lint over lesson prose has to strip code first.

**Defect found by this pass, unrelated to any phase.** `mkdocs.yml` had no `site_url`, so MkDocs wrote every `<loc>` in `sitemap.xml` as `None./...` and emitted no canonical link on any page. Across seven locales that leaves nothing marking which URL is canonical. Fixed; the sitemap now carries real URLs and hreflang alternates. The theme emits no per-page hreflang tags either way.
