# oh-my-skills

`oh-my-skills` is a personal collection of agent skills for turning loose AI-assisted work into reusable, inspectable workflows.

The repository starts with `engineered-vibe-coding`, an Agent-Team-first engineering workflow skill. It is designed for complex coding work where the agent must clarify requirements, plan architecture, split work into modules and atomic tasks, pass checkpoints, run validation, record role evidence, and block anti-maintainability patterns before delivery.

The goal is to collect skills that are not just prompts, but small operating systems for agent work: clear triggers, hard rules, references, examples, validation paths, and human-readable documentation.

## Current Focus

- Engineering-grade agent coding.
- Requirement, architecture, module, and task planning.
- Agent Team / subagent / self-review fallback rules.
- Evidence-based review and anti-spaghetti gates.
- Portable skill drafts that can later be installed into Codex or adapted to other agent environments.

## Skills

| Skill | Description |
| --- | --- |
| [`engineered-vibe-coding`](skills/engineered-vibe-coding) | Agent-Team-first engineering workflow skill for structured coding, planning, checkpoints, validation, review evidence, and anti-spaghetti gates. |

## Layout

```text
oh-my-skills/
├── skills/
│   └── engineered-vibe-coding/
└── skills.json
```

Each skill keeps its own `SKILL.md`, references, examples, and human-facing README files.

## Validation

Validate a Codex skill with:

```bash
uv run --with pyyaml python /Users/anhuike/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/engineered-vibe-coding
```

## Install Locally

To install `engineered-vibe-coding` into Codex later:

```bash
cp -R skills/engineered-vibe-coding /Users/anhuike/.codex/skills/
```
