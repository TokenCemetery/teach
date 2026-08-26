# AGENTS.md

## Repository

A persistent learning workspace. `learning/<topic>/` holds one self-contained workspace per topic — mission, lessons, reference sheets, and a record of what was demonstrably learned. Teaching state lives in the workspace, not in the conversation, because a topic is taught across many sessions.

Most work here is teaching a lesson or maintaining workspace state. Treat repository chores — templates, CI, project docs — as the exception.

## Session Start

Before any work, read `.agents/memory/MEMORY.md` and `.agents/memory/$(date -u +%Y-%m-%d).md`. Create missing files or the `.agents/memory/` directory if needed; never overwrite existing memory.

- `MEMORY.md` — durable project facts. Treat as low-confidence; verify against repo before acting.
- `YYYY-MM-DD.md` — daily task notes (UTC dates). Use for checklists and completed implementation notes.
- For substantial work needing durable documentation, create `docs/YYYY-MM-DD-task-name/` instead.

Agent memory is not learner state. What the user has learned, disclosed, or gotten wrong belongs in that topic's `learning-records/`, never in `.agents/memory/`.

## Learning Workspaces

- The `teach` skill is the source of truth for every file under `learning/<topic>/`: layout, formats, lesson design, and what earns a learning record. Read it before authoring or editing one. Do not invent variants of its formats.
- Workspaces live at `learning/<topic>/` in this repository. Do not create them elsewhere.
- `learning/_template/` is a copy source, not a workspace. Never teach into it, never add it to an index.
- Starting a topic means copying the template, then filling the mission by interviewing the user. A vague mission is worse than none — it silently misdirects every later lesson.
- `learning/README.md` carries the topic index. Add a row when a workspace is created; an index that has drifted from the directories is worse than no index.
- One topic per workspace. An unrelated second topic is a second workspace, not a second mission.

## Repository Behavior

- Repo is source of truth. Verify memory and prior notes against it before acting.
- Limit changes to the minimum required. Do not restructure, reformat, or improve unrelated content without explicit approval.
- Update project-scoped documents in the same change if behavior they describe is affected.
- Final response must state: what changed, what verification ran, and any residual risk.

## Before Editing (Non-Trivial Changes)

A change is non-trivial when it affects behavior, multiple files, shared conventions, structure, dependencies, generated artifacts, or project docs. Writing one lesson into an existing workspace is not non-trivial; changing how workspaces are structured is.

Before editing, state: requested outcome and scope, working assumptions, simplest viable approach, verification plan, and any material ambiguity. If an ambiguity could materially change scope, ask one concise question first.

## Artifact Quality

- Every artifact must be complete, actionable, internally consistent, and specific enough to verify.
- No placeholders, TODOs, unsupported claims, or missing required sections unless the user requests a draft. Placeholders are correct in `learning/_template/` and nowhere else.
- Every section, example, and abstraction must contribute to the outcome. Remove anything that does not.
- Examples must be narrow, direct, complete, and consistent with actual repo conventions.
- Introduce structure only when it reduces real complexity or follows an established pattern.
- No speculative features, unused extension points, or unrequested configurability.
- KISS: prefer the simplest complete solution. If an artifact grows beyond what the problem requires, simplify before finalizing.
- Self-review every non-trivial artifact for placeholders, contradictions, scope drift, and missing verification. Fix issues before presenting.
