# Engineered Vibe Coding Workflow

Use this reference when the task needs more detail than the hard rules in `SKILL.md`.

## Workflow State Model

For Standard and Strict workflows, `.agent/dev-plan.md` is the single source of truth.

It must drive:

- scope
- decisions
- active task
- blockers
- validation
- review
- risks
- unverified items

Do not rely on memory when `.agent/dev-plan.md` exists. Read and update it before moving between tasks or checkpoints.

## Reference Reading Matrix

| Situation | Read |
| --- | --- |
| Risk classification is unclear | `references/workflow.md` |
| Creating or updating `.agent/dev-plan.md` | `references/dev-plan-template.md` |
| Before implementation of Standard / Strict work | `references/workflow.md`, `.agent/dev-plan.md` |
| Before review or final delivery | `references/review-checklists.md`, `.agent/dev-plan.md` |
| Validation failed | `references/workflow.md`, `.agent/dev-plan.md` |
| Role-based planning or review is required | `references/roles.md`, `.agent/dev-plan.md` |
| Behavior is unclear | relevant file in `references/examples/` |

## Risk Levels

### Light

Use Light only when all are true:

- The change is single-file or tightly local.
- The change is a small fix, copy edit, or local bug.
- The change does not alter core business logic, state, public interfaces, security, data, build, CI, deployment, or dependencies.

Required workflow:

1. Inspect the directly relevant file or symbols.
2. Confirm the change is still Light after inspection.
3. If the user explicitly requested a plan, create or update `.agent/dev-plan.md`.
4. Make the smallest necessary change.
5. Run focused validation if available.
6. Review for unrelated edits, temporary code, and obvious regressions.
7. Report changed files, validation, review result, and unverified items.

### Standard

Use Standard for:

- Multi-file changes.
- New features.
- User-visible behavior changes.
- Medium refactors.
- Work requiring task decomposition.

Required workflow:

1. Inspect relevant project structure before asking questions.
2. Ask only non-discoverable product, business, security, or irreversible decision questions.
3. Create or update `.agent/dev-plan.md`.
4. Record the Risk Level and Decision Log.
5. Split the work into modules and atomic tasks.
6. Keep exactly one active Next Atomic Task.
7. Pass Checkpoint Plan before implementation.
8. Implement the First Slice as the active task.
9. Pass Checkpoint First Slice before expanding scope.
10. Implement only the active task.
11. Run available validation commands.
12. Update validation and review records.
13. Continue only after gates pass.

### Strict

Use Strict for:

- Ambiguous requirements.
- Architecture changes.
- Authentication, authorization, permissions, payments, or security-sensitive work.
- Database migrations or data model changes.
- Public API changes.
- Large refactors.
- Production critical paths.
- Dependency upgrades.
- Build, CI, or deployment changes.

Required workflow:

1. Complete requirement analysis before design.
2. Complete product and scope design before architecture.
3. Complete architecture planning before implementation.
4. Create or update `.agent/dev-plan.md` before editing code.
5. Record non-goals, risks, acceptance criteria, and decision rationale.
6. Pass Checkpoint Plan before implementation.
7. Implement the First Slice as the active task.
8. Pass Checkpoint First Slice before expanding scope.
9. Implement only one atomic task at a time.
10. Treat failed validation, unclear requirements, review rejection, unrelated edits, or temporary code as blockers.

When uncertain, escalate to Strict.

## Planning Chain

For Standard and Strict workflows, follow this planning chain before implementation:

1. Requirements: clarify the goal, users, inputs, outputs, edge cases, non-goals, and acceptance criteria.
2. Architecture: inspect existing structure, identify reuse points, define module boundaries, data flow, interfaces, validation strategy, and risks.
3. Module breakdown: split the work into coherent modules with clear goals, scope, affected areas, dependencies, and acceptance checks.
4. Atomic task breakdown: break each module into small verifiable tasks. Each task must have one expected outcome and a focused validation path.

Do not start implementation while requirements, architecture, module boundaries, or atomic tasks are still vague.

## Checkpoint Plan

Use for Standard and Strict workflows before implementation.

### Entry Criteria

- The task is classified as Standard or Strict.

### Required Actions

- Inspect relevant repository structure.
- Create or update `.agent/dev-plan.md`.
- Clarify requirements, non-goals, and acceptance criteria.
- Record risk level and rationale.
- Record current scope, non-goals, and acceptance criteria.
- Record existing project analysis.
- Record architecture and technical approach.
- Define module breakdown.
- Break every module into atomic tasks.
- Define the First Slice.
- Discover validation commands or best available focused checks.
- Complete required role passes for Checkpoint Plan: Requirement Analyst, Product / Scope Designer, Architect, and Planner.

### Exit Criteria

- `.agent/dev-plan.md` exists and is current.
- Risk level is recorded.
- Scope and non-goals are recorded.
- Acceptance criteria are recorded.
- Architecture and module boundaries are recorded.
- Every module has atomic tasks.
- Exactly one Next Atomic Task is active.
- First Slice is defined.
- Validation strategy is recorded.
- Required role passes for Checkpoint Plan are recorded with evidence.
- Blockers are empty or explicitly accepted by the user.

### Blockers

- Requirements are unclear.
- Scope is too broad.
- No acceptance criteria.
- No First Slice.
- Unknown validation strategy.
- Irreversible decision requires user confirmation.

## First Slice Rule

For Standard and Strict workflows, the first atomic task must be the smallest verifiable vertical slice that proves:

- the technical approach
- file boundaries
- existing project patterns
- validation commands
- review gates

Avoid empty scaffolding as the First Slice. Prefer a tiny real behavior that can be validated.

Do not use empty directories, placeholder files, or purely cosmetic scaffolding as the First Slice unless scaffolding itself is the requested deliverable.

## Checkpoint First Slice

Use after the First Slice implementation.

### Entry Criteria

- Checkpoint Plan has passed.
- First Slice task is implemented.
- `.agent/dev-plan.md` has been updated with changed files and validation records.

### Required Actions

- Run the discovered validation command or best available focused check.
- Review whether the selected architecture and file boundaries still make sense.
- Review whether the implementation follows existing project patterns.
- Review whether the remaining plan should be adjusted.
- Record evidence in `.agent/dev-plan.md`.
- Complete required role passes for Checkpoint First Slice: Developer, Tester, Reviewer, and Complexity Controller.

### Exit Criteria

- First Slice validation passed or blockers are clearly recorded.
- Review result is recorded.
- Any plan adjustment is recorded in Decision Log.
- Required role passes for Checkpoint First Slice are recorded with evidence.
- The next atomic task is selected only after First Slice passes.

### Blockers

- Validation failed.
- First Slice was only empty scaffolding.
- Architecture or file boundaries appear wrong.
- Existing patterns were bypassed.
- The next task is selected before review.

## Checkpoint Release

Use before final delivery for Standard and Strict workflows.

### Entry Criteria

- All planned required tasks are complete or explicitly deferred.
- Validation records exist.
- Review records exist.

### Required Actions

- Run final applicable validation.
- Apply the review checklist.
- Apply anti-spaghetti red lines.
- Record blockers, risks, and unverified items.
- Perform the self-review protocol.
- Complete required role passes for Checkpoint Release: Tester, Reviewer, Complexity Controller, and Planner.
- Ensure final response fields are complete.

### Exit Criteria

- Required checks passed, or failures are reported as blockers.
- Review result is Pass, or Fail is reported with required fixes.
- Unverified items are explicitly listed.
- Required role passes for Checkpoint Release are recorded with evidence.
- Final response includes all required fields.

### Blockers

- Missing validation records.
- Missing review records.
- Failed checks hidden or minimized.
- Unverified items omitted.
- Final response template fields missing.

## Repository Discovery

Before asking the user, discover answers from the repository:

- Frameworks, runtimes, package managers, and project structure.
- Entry points, modules, existing abstractions, and naming conventions.
- Existing tests and validation commands.
- Existing docs, README guidance, CI jobs, hooks, and build scripts.

Ask the user only when the answer is not discoverable or requires product, business, security, or irreversible judgment.

## Validation Command Discovery

Discover commands from:

- `package.json`
- `pyproject.toml`
- `Cargo.toml`
- `pom.xml`
- `build.gradle`
- `pubspec.yaml`
- `Makefile`
- CI configs
- `README`

Never invent validation commands. Never bypass configured hooks or validation commands.

If no validation command is found, report:

`No validation command was found. Performed best available focused verification instead.`

## Quality Gates

Quality gates are blockers, not suggestions. Stop progression when:

- Available validation commands exist but were not run.
- Configured hooks or validation commands were bypassed.
- lint, typecheck, test, or build fails.
- Unrelated files were modified.
- Existing behavior was removed without explicit user request.
- Temporary, debug, TODO-as-implementation, or unfinished code remains.
- Hardcoded sensitive values were introduced.
- Existing project abstractions were bypassed.
- Reviewer checklist fails.

## Failure Loop

When a gate fails:

1. Stop progression.
2. Record the failure in `.agent/dev-plan.md`.
3. Identify the smallest fix.
4. Apply only that fix.
5. Re-run the failed check first.
6. Re-run broader checks if needed.
7. Update the review record.

Do not continue to the next atomic task until the blocker is cleared or explicitly accepted by the user.

After fixing a blocker, return to the checkpoint that originally failed. Do not jump directly to later tasks or final delivery.

If a role pass fails, return to the checkpoint where that role pass was required. Do not continue to the next atomic task until the failed role pass is fixed, re-run, and recorded.

## Role Execution

Use role passes for Standard and Strict workflows.

Prefer the strongest available execution mode:

1. Agent Team Review / Execution
2. Subagent Review / Execution
3. Main Agent Self-Review

Do not silently choose self-review when Agent Team or subagent review is available.

Do not pretend that Agent Team or subagent execution occurred. Use those modes only when the environment actually supports them.

Read `references/roles.md` for role definitions, required role passes, output format, fallback rules, and checkpoint mapping.
