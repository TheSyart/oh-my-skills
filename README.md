# oh-my-skills

A personal collection of agent skills.

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

