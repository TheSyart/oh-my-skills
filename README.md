# oh-my-skills

`oh-my-skills` is my continuously maintained collection of agent skills.

This repository is where I turn useful agent workflows into reusable skill packages: not one-off prompts, not scattered notes, but small operating systems for agent work. Each skill is expected to have clear triggers, hard rules, references, examples, validation paths, and enough documentation for both humans and agents to understand how it should be used.

The collection is starting with one core skill, `engineered-vibe-coding`, and will keep evolving as I refine how agents plan, build, review, and maintain real projects.

## Why This Exists

AI coding can move quickly, but speed is not the hard part anymore. The hard part is keeping agent work controlled, reviewable, and maintainable when tasks become ambiguous or large.

`oh-my-skills` is an attempt to make that process reusable:

- Turn repeatable agent workflows into skills.
- Capture engineering rules that should not depend on memory.
- Make planning, validation, and review visible.
- Keep high-risk work from becoming rushed, unreviewed code.
- Improve skills over time based on real usage.

## Current Skill

| Skill | Status | Description |
| --- | --- | --- |
| [`engineered-vibe-coding`](skills/engineered-vibe-coding) | Draft / actively maintained | Agent-Team-first engineering workflow skill for structured coding, requirement and architecture planning, module and atomic task breakdown, checkpoints, validation, role review evidence, and anti-spaghetti gates. |

### `engineered-vibe-coding`

`engineered-vibe-coding` is designed for complex software development tasks where an agent should not simply start writing code.

It asks the agent to:

- inspect the repository before asking discoverable questions;
- classify task risk as Light, Standard, or Strict;
- clarify requirements before implementation;
- plan architecture and module boundaries;
- split modules into atomic tasks;
- use `.agent/dev-plan.md` as the source of truth for Standard and Strict work;
- pass Plan, First Slice, and Release checkpoints;
- prefer Agent Team review, then subagent review, then main-agent self-review as fallback;
- record role review evidence;
- run discovered validation commands instead of inventing commands;
- block progression when validation, review, or anti-spaghetti gates fail.

In short: small tasks stay light, but serious work gets real engineering structure.

## Repository Layout

```text
oh-my-skills/
├── README.md
├── README.zh-CN.md
├── skills.json
└── skills/
    └── engineered-vibe-coding/
        ├── SKILL.md
        ├── README.md
        ├── README.zh-CN.md
        ├── agents/
        │   └── openai.yaml
        └── references/
            ├── workflow.md
            ├── roles.md
            ├── dev-plan-template.md
            ├── review-checklists.md
            └── examples/
```

## How I Maintain This

This repository is meant to be a living collection.

I expect skills here to change as I learn from actual agent runs:

- rules may become stricter when agents skip important steps;
- references may be split when the main skill file gets too heavy;
- examples may be added when behavior needs calibration;
- validation and installation notes may change as agent platforms evolve;
- future versions may add small helper scripts only when the workflow is stable enough to automate.

The goal is not to freeze a perfect prompt. The goal is to keep improving practical agent workflows until they are reliable enough to reuse.

## Validation

Validate the current Codex-compatible skill with:

```bash
uv run --with pyyaml python /Users/anhuike/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/engineered-vibe-coding
```

Expected result:

```text
Skill is valid!
```

## Local Installation

To install `engineered-vibe-coding` into Codex locally:

```bash
cp -R skills/engineered-vibe-coding /Users/anhuike/.codex/skills/
```

The repository keeps the skill in draft form first. Install it only when you want Codex to discover it automatically.

## Version Direction

- **V1**: hard engineering rules.
- **V2**: workflow state model with checkpoints and First Slice.
- **V3**: Agent-Team-first role execution with evidence.
- **V4**: optional automation scripts, such as dev-plan initialization and validation command discovery.

## Philosophy

A good agent skill should make the agent more capable without making it sloppy.

For coding work, that means:

- plan before broad changes;
- keep scope explicit;
- split large work into smaller verified steps;
- preserve existing architecture unless there is a clear reason to change it;
- treat validation failures as blockers;
- make review evidence visible;
- leave the codebase healthier than it was found.

