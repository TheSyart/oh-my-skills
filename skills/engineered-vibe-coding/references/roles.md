# Role Execution Model

Use this reference for role-based planning, implementation, validation, review, and self-review fallback.

## Review Execution Priority

Use the strongest available role execution mode:

1. **Agent Team Review / Execution**: use when the environment supports multiple specialized agents. Each role should review or execute from its own responsibility and produce independent output.
2. **Subagent Review / Execution**: use when isolated subagents are available but a full agent team is not. Assign focused review or execution tasks to independent subagents.
3. **Main Agent Self-Review**: use only when Agent Team Review and Subagent Review are unavailable. The main agent must simulate each required role strictly and record evidence.

Do not pretend that Agent Team or subagent execution occurred. Use Agent Team or subagent modes only when the environment actually supports them. Otherwise, fall back to Main Agent Self-Review and record the fallback reason in `.agent/dev-plan.md`.

## Required Role Passes By Workflow

### Light

Required:

- Developer
- Reviewer

Optional:

- Tester
- Complexity Controller

Light work may use Main Agent Self-Review unless the user explicitly asks for Agent Team or subagent review.

### Standard

Required:

- Requirement Analyst
- Product / Scope Designer
- Architect
- Planner
- Developer
- Tester
- Reviewer
- Complexity Controller

Use Agent Team Review when available. If not available, use Subagent Review. If neither is available, use Main Agent Self-Review and record the fallback reason.

### Strict

Required:

- Requirement Analyst
- Product / Scope Designer
- Architect
- Planner
- Developer
- Tester
- Reviewer
- Complexity Controller

Strict workflows should prefer Agent Team Review. If Agent Team Review is unavailable, use Subagent Review when available. Main Agent Self-Review is fallback only and must record evidence for every role.

Strict workflows must complete Requirement -> Design -> Architecture -> Implementation in order.

For Strict workflows, Main Agent Self-Review fallback must be recorded as a risk.

## Roles

### Requirement Analyst

Responsibility:

- Clarify goal, users, inputs, outputs, constraints, edge cases, non-goals, and acceptance criteria.
- Identify unclear or missing requirements.
- Block implementation if requirements are too vague.

Reject if:

- Goal is unclear.
- Acceptance criteria are missing.
- Scope is too broad.
- Non-goals are not defined for Standard / Strict work.

### Product / Scope Designer

Responsibility:

- Define current version scope.
- Define non-goals.
- Define user flow, interaction states, error states, and future expansion.
- Prevent scope creep.

Reject if:

- Current scope is not bounded.
- Future goals are mixed into current implementation.
- User-visible behavior is ambiguous.

### Architect

Responsibility:

- Inspect existing code structure.
- Identify reuse points, module boundaries, data flow, interfaces, and risks.
- Prevent architecture drift and unnecessary new abstractions.

Reject if:

- Existing abstractions are bypassed without reason.
- Module boundaries are unclear.
- New abstractions are introduced without need.
- Data flow or public interface changes are not explained.

### Planner

Responsibility:

- Maintain `.agent/dev-plan.md`.
- Split work into modules and atomic tasks.
- Ensure exactly one active task.
- Track checkpoints, blockers, validation, review, risks, and unverified items.

Reject if:

- `.agent/dev-plan.md` is missing for Standard / Strict work.
- More than one atomic task is active.
- Checkpoint evidence is missing.
- Blockers are hidden or unresolved.

### Developer

Responsibility:

- Implement only the active atomic task.
- Make the smallest necessary change.
- Follow existing project patterns.
- Avoid unrelated edits.

Reject if:

- Implementation changes unrelated files.
- Implementation expands scope.
- Existing behavior is removed without explicit request.
- Temporary or debug code remains.

### Tester

Responsibility:

- Validate happy path, error path, edge cases, regression risks, and compatibility.
- Discover and run available validation commands.
- Report skipped or unavailable checks.

Reject if:

- Available validation commands were skipped.
- Failed validation is minimized or hidden.
- Unverified items are not reported.

### Reviewer

Responsibility:

- Protect long-term codebase health.
- Check unrelated edits, duplicate code, naming, hidden side effects, missing tests, missing error handling, and maintainability risk.
- Reject code that passes functionally but damages the codebase.

Reject if:

- The implementation passes functionally but creates maintainability debt.
- Naming is vague.
- Responsibilities are mixed.
- Tests or error handling are missing without explanation.

### Complexity Controller

Responsibility:

- Detect god files, god functions, mixed responsibilities, hidden coupling, over-abstraction, and unnecessary dependencies.
- Reject implementations that make future extension harder.

Reject if:

- A file or function grows significantly without decomposition.
- Local state was enough but global state was added.
- A dependency was added for a trivial problem.
- The solution makes future extension harder.

## Role Output Format

Every required role pass must output:

- Role:
- Mode: Agent Team / Subagent / Self-review
- Result: Pass / Fail
- Evidence:
- Required Fixes:
- Risks:
- Unverified Items:

If any required role returns Fail, progression is blocked until fixes are applied or the user explicitly accepts the risk.

## Fallback Rule

When Agent Team Review or Subagent Review is unavailable, the main agent may perform self-review.

Self-review must still produce separate outputs for each required role.

Do not merge all roles into one generic statement such as `review passed`.

Record fallback reason in `.agent/dev-plan.md` under Role Review Records.

## Evidence Rule

A role pass is not valid without evidence.

Bad:

- `Reviewer passed.`

Good:

- `Reviewer passed. Evidence: no unrelated files changed; validation command passed; implementation reused existing API client; no new dependencies added.`

## Role Review And Checkpoints

Role passes should map to checkpoints:

### Checkpoint Plan

Required role passes:

- Requirement Analyst
- Product / Scope Designer
- Architect
- Planner

### Checkpoint First Slice

Required role passes:

- Developer
- Tester
- Reviewer
- Complexity Controller

### Checkpoint Release

Required role passes:

- Tester
- Reviewer
- Complexity Controller
- Planner

If any required role fails at a checkpoint, return to the failure loop.
