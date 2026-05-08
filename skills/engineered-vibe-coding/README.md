# Engineered Vibe Coding

`engineered-vibe-coding` is a draft Codex skill for engineering-grade vibe coding.

Its purpose is not to make Codex code faster. Its purpose is to stop Codex from coding carelessly during complex development tasks: unclear requirements, broad refactors, architecture changes, authentication, payments, database work, dependency upgrades, CI/build/deployment changes, or anything that can damage long-term codebase health.

## What It Does

This skill turns complex coding work into a risk-based engineering workflow:

- Classify the task as Light, Standard, or Strict before implementation.
- Inspect the repository before asking questions that can be answered from code.
- Create or update `.agent/dev-plan.md` for Standard and Strict workflows.
- Implement only one atomic task at a time.
- Discover validation commands from the project instead of inventing them.
- Never bypass configured hooks or validation commands.
- Treat failed validation, unrelated edits, temporary code, or review rejection as blockers.
- Report changed files, validation results, review result, risks, and unverified items.

## What V2 Adds

- `.agent/dev-plan.md` as the single source of truth for Standard and Strict work.
- A clearer planning chain: requirements, architecture, module breakdown, and atomic task breakdown.
- Three checkpoints: Plan, First Slice, and Release.
- First Slice as the smallest verifiable vertical slice.
- Self-review protocol before final delivery.
- Fixed final response templates.
- Short workflow examples for Light, Standard, and Strict tasks.

## What V3 Adds

- Agent Team first role execution.
- Subagent review as the second-best mode.
- Main-agent self-review only as fallback.
- New `references/roles.md` for role definitions, fallback rules, and role output format.
- Role review evidence recorded in `.agent/dev-plan.md`.
- Anti-Spaghetti Control Model explaining how layered gates prevent codebase decay.

## Workflow Levels

### Light

Use for single-file, low-risk fixes such as copy edits, tiny local bugs, or small adjustments that do not touch core business logic, state, public APIs, security, data, build, CI, deployment, or dependencies.

Light does not require `.agent/dev-plan.md` unless the user explicitly asks for a plan.

### Standard

Use for multi-file changes, new features, user-visible behavior changes, medium refactors, or work that needs task splitting.

Standard requires `.agent/dev-plan.md`, one active atomic task, validation, and review.

### Strict

Use for ambiguous requirements, architecture changes, authentication, authorization, payments, permissions, database migrations, public APIs, large refactors, security-sensitive work, production critical paths, dependency upgrades, and build/CI/deployment changes.

When uncertain, escalate to Strict.

## File Structure

```text
engineered-vibe-coding/
├── SKILL.md
├── README.md
├── README.zh-CN.md
├── agents/
│   └── openai.yaml
└── references/
    ├── workflow.md
    ├── roles.md
    ├── dev-plan-template.md
    └── review-checklists.md
```

## Important Files

- `SKILL.md`: short, hard execution rules loaded by Codex when the skill triggers.
- `references/workflow.md`: detailed Light / Standard / Strict workflow, quality gates, and failure loop.
- `references/roles.md`: role definitions, execution priority, fallback rules, and role output format.
- `references/dev-plan-template.md`: template for `.agent/dev-plan.md`.
- `references/review-checklists.md`: quality gates, test checklist, reviewer checklist, and anti-spaghetti rules.
- `references/examples/`: short examples that calibrate Light, Standard, and Strict workflow behavior.
- `agents/openai.yaml`: display metadata and default prompt.

## Validation

Validate the draft skill with:

```bash
uv run --with pyyaml python /Users/anhuike/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/anhuike/Desktop/engineered-vibe-coding
```

Expected result:

```text
Skill is valid!
```

## Installation Later

This draft currently lives on the Desktop for iteration:

```text
/Users/anhuike/Desktop/engineered-vibe-coding
```

When it is ready to install globally, move or copy it to:

```text
/Users/anhuike/.codex/skills/engineered-vibe-coding
```

For a final installable skill, consider whether to keep or remove these README files. Codex skill packages should stay lean; the core behavior belongs in `SKILL.md` and `references/`.

## Version Direction

- V1: hard engineering rules.
- V2: workflow state model with checkpoints and First Slice.
- V3: Agent-Team-first role execution with evidence.
- V4: optional automation scripts.

V3 intentionally remains workflow-only. V4 may add optional scripts:

- `init_dev_plan.py`
- `discover_quality_gates.py`
- `validate_dev_plan.py`
