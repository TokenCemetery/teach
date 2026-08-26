# AGENTS.md

## Scope

Applies to all files under `docs/`. Governs document writing only.

## Documentation Structure

```text
docs/
├── ARCHITECTURE.md
├── DESIGN.md
├── ROADMAP.md
└── [YYYY-MM-DD-task-name]/    # one folder per task, feature, or epic
    ├── BRAINSTORM.md          # discovery and explored ideas
    ├── PRD.md                 # product requirements
    ├── SPEC.md                # technical specification
    ├── ARCHITECTURE.md        # task-scoped architecture decisions
    ├── DESIGN.md              # UI/UX decisions
    └── TASKS.md               # actionable checklist
```

- Task folder names: UTC date prefix + lowercase hyphenated name (e.g. `2026-06-04-user-auth`).
- Create a task folder only when the work needs durable product, technical, architecture, or design docs.
- Each file in a task folder is optional; create only what contributes to the requested outcome.
- Do not create a task folder just for a checklist, log, status update, or completed-task summary.
- `TASKS.md` must only exist alongside task-scoped product, technical, architecture, or design docs.

## Before Writing

- Identify the document's purpose, audience, scope, required inputs, and acceptance criteria first.
- Resolve any ambiguity that could materially change content or scope before writing.
- Read directly related documents to preserve terminology and avoid contradictions.
- Use the smallest set of documents needed. Do not create speculative documents or sections.

## Document Requirements

- Every document must be complete, actionable, internally consistent, and specific enough to verify.
- No unsupported claims, unresolved ambiguity, empty required sections, or contradictions unless the user requests a draft.
- Requirements must use unambiguous normative language with observable acceptance criteria.
- Examples must be narrow, complete, and consistent with actual repo interfaces.
- Use YAML frontmatter for document metadata when metadata is needed.
- Preserve established structure and terminology unless the request requires changing them.
- No speculative features, requirements, abstractions, or unrequested configurability.

## Consistency

- Keep requirements, terminology, examples, links, and status consistent across all documents changed in the same task.
- Do not contradict an existing `PRD.md`, `SPEC.md`, `ARCHITECTURE.md`, or `DESIGN.md` without updating it.
- `TASKS.md` items must trace to concrete requirements or deliverables in the same task folder.

## Completion Gate

- Self-review every created or materially modified document for placeholders, contradictions, ambiguity, unsupported claims, scope drift, broken references, and missing verification.
- Fix all issues before presenting. Run the repo's linting, formatting, or link-checking workflow when available.
