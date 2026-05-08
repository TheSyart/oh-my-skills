# `.agent/dev-plan.md` Template

Use this template for Standard and Strict workflows. For Light workflows, use it only when the user explicitly asks for a plan.

## Single Source Of Truth

For Standard and Strict workflows, this file is the single source of truth for:

- scope
- decisions
- active task
- blockers
- validation
- review
- risks
- unverified items

Update this file before moving to a new task, checkpoint, or final delivery.

```md
# Agent Development Plan

## Single Source Of Truth

For Standard and Strict workflows, this file is the single source of truth for scope, decisions, active task, blockers, validation, review, risks, and unverified items.

Update this file before moving to a new task, checkpoint, or final delivery.

## Project Goal

Describe the problem this development work must solve.

## Original Request

Record the user's original request.

## Clarified Requirements

State the clarified behavior, inputs, outputs, constraints, and edge cases.

- Goal:
- Users / actors:
- Inputs:
- Outputs:
- Edge cases:
- Constraints:

## Current Scope

Define what this version will implement.

## Non-goals

Define what this version will not implement.

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Risk Level

Light / Standard / Strict

Rationale:

## Role Execution Mode

- Overall mode: Agent Team / Subagent / Self-review
- Planning mode:
- Implementation mode:
- Review mode:
- Reason:
- Fallback reason, if any:

## Checkpoints

| Checkpoint | Status | Evidence | Role Evidence | Blockers |
| --- | --- | --- | --- | --- |
| Plan | pending / passed / blocked |  |  |  |
| First Slice | pending / passed / blocked |  |  |  |
| Release | pending / passed / blocked |  |  |  |

## Decision Log

| Decision | Rationale | Date/Context |
| --- | --- | --- |
|  |  |  |

## Existing Project Analysis

Relevant structure, existing modules, commands, patterns, and constraints discovered from the repository.

## Technical Approach

Implementation approach, data flow, interfaces, reuse points, and risks.

- Architecture summary:
- Existing patterns to reuse:
- Module boundaries:
- Data flow:
- Interfaces / contracts:
- Validation strategy:
- Risks:

## Module Breakdown

Each module must include:

- Goal
- Scope
- Files or areas likely affected
- Atomic tasks
- Acceptance checks
- Dependencies or sequencing constraints

### Module 1

- Goal:
- Scope:
- Likely affected files / areas:
- Dependencies:
- Acceptance checks:
- [ ] Atomic task 1
- [ ] Atomic task 2

### Module 2

- Goal:
- Scope:
- Likely affected files / areas:
- Dependencies:
- Acceptance checks:
- [ ] Atomic task 1
- [ ] Atomic task 2

## Active Task Policy

Only one atomic task may be active at a time.

Before selecting the next task:

- the current task must be complete, blocked, or explicitly deferred
- validation records must be updated
- review records must be updated when applicable
- blockers must be cleared or recorded

## Next Atomic Task

Only one task may be active at a time.

- Module:
- Task:
- Why this task is next:
- Expected verifiable outcome:
- Status: not started / in progress / blocked / validating / review / complete / deferred

## Current Progress

Brief status summary.

## Changed Files

- `path/to/file`

## Validation Records

| Command / Check | Result | Notes |
| --- | --- | --- |
|  |  |  |

If no validation command was found, record:

`No validation command was found. Performed best available focused verification instead.`

## Review Records

| Review Pass | Result | Notes |
| --- | --- | --- |
| Code quality |  |  |
| Complexity |  |  |
| Anti-spaghetti rules |  |  |

## Role Review Records

| Checkpoint | Role | Mode | Result | Evidence | Required Fixes | Risks | Unverified Items |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Plan | Requirement Analyst | Agent Team / Subagent / Self-review |  |  |  |  |  |
| Plan | Product / Scope Designer | Agent Team / Subagent / Self-review |  |  |  |  |  |
| Plan | Architect | Agent Team / Subagent / Self-review |  |  |  |  |  |
| Plan | Planner | Agent Team / Subagent / Self-review |  |  |  |  |  |
| First Slice | Developer | Agent Team / Subagent / Self-review |  |  |  |  |  |
| First Slice | Tester | Agent Team / Subagent / Self-review |  |  |  |  |  |
| First Slice | Reviewer | Agent Team / Subagent / Self-review |  |  |  |  |  |
| First Slice | Complexity Controller | Agent Team / Subagent / Self-review |  |  |  |  |  |
| Release | Tester | Agent Team / Subagent / Self-review |  |  |  |  |  |
| Release | Reviewer | Agent Team / Subagent / Self-review |  |  |  |  |  |
| Release | Complexity Controller | Agent Team / Subagent / Self-review |  |  |  |  |  |
| Release | Planner | Agent Team / Subagent / Self-review |  |  |  |  |  |

## Blockers

Validation failure, unclear requirements, review rejection, unrelated changes, temporary/debug code, or other blockers.

## Unverified Items

| Item | Reason Not Verified | Risk | Follow-up |
| --- | --- | --- | --- |
|  |  | low / medium / high |  |

## Risks And Follow-ups

Remaining risks, unverified items, and recommended next steps.
```
