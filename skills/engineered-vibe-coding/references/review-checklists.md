# Review Checklists

Use this reference before review, quality gates, and final delivery for Standard and Strict work. Use the relevant parts for Light work.

## Self-Review Protocol

Before final delivery:

1. Check the final response against the required template.
2. Confirm changed files, validation results, review result, blockers, risks, and unverified items are present.
3. Confirm failed gates are reported as blockers, not hidden as notes.
4. Fix missing or failed items before claiming completion.

Never hide failed gates in the final response. Report them as blockers.

## Reviewer Output Format

Reviewer result must use:

- Mode: Agent Team / Subagent / Self-review
- Result: Pass / Fail
- Evidence:
- Required Fixes:
- Risks:
- Unverified Items:

If the result is Fail, progression is blocked until required fixes are applied or explicitly accepted by the user.

## Quality Gate Checklist

Progression is blocked if any item is true:

- Available validation commands exist but were not run.
- Configured hooks or validation commands were bypassed.
- lint, typecheck, test, or build failed.
- Unrelated files were modified.
- Existing behavior was removed without explicit user request.
- Temporary, debug, TODO-as-implementation, or unfinished code remains.
- Hardcoded sensitive values were introduced.
- Existing project abstractions were bypassed.
- Reviewer checklist failed.

## Test Checklist

Check what applies:

- Happy path.
- Error path.
- Edge cases.
- Regression risk.
- Existing behavior compatibility.
- Unit test need.
- Integration test need.
- Manual verification need.
- Unverified items that must be reported.

## Reviewer Checklist

The reviewer is adversarial but constructive. The reviewer protects long-term codebase health, not the developer's ego.

Review for:

- Unrelated changes.
- Duplicate code.
- Mixed responsibilities.
- Over-abstraction.
- Vague naming.
- Hidden side effects.
- Test gaps.
- Future maintenance risk.
- Files or functions grew significantly because of this change.
- Missing error handling.
- Missing edge case handling.
- Unnecessary dependencies.
- Public interface compatibility.
- Whether cohesive components, services, helpers, or tests should be extracted when the project already uses that pattern.

## Anti-Spaghetti Control Model

Spaghetti code is controlled by layered gates, not by style advice.

The gates are:

1. **Requirement Gate**: unclear requirements block implementation.
2. **Architecture Gate**: missing module boundaries, unclear data flow, or unexplained public interface changes block implementation.
3. **Module Breakdown Gate**: broad work must be split into modules and atomic tasks.
4. **First Slice Gate**: the first implementation must prove the technical approach, file boundaries, existing patterns, validation commands, and review gates.
5. **Quality Gate**: failed validation blocks progression.
6. **Reviewer Gate**: maintainability failures block progression even if functionality works.
7. **Complexity Gate**: god files, god functions, mixed responsibilities, hidden coupling, over-abstraction, and unnecessary dependencies block progression.
8. **Failure Loop**: failed gates must return to the failed checkpoint.

If any gate fails, do not continue to the next atomic task.

## Anti-Spaghetti Red Lines

Reject implementation if it:

1. Creates a god file or god function.
2. Mixes UI, business logic, persistence, and network logic without reason.
3. Duplicates existing logic instead of reusing project patterns.
4. Adds global state when local state is enough.
5. Adds dependencies for trivial problems.
6. Creates hidden coupling between unrelated modules.
7. Changes public interfaces without updating callers and tests.
8. Leaves TODO, FIXME, or debug code as unfinished implementation.
9. Uses vague names like `data`, `temp`, `helper`, `manager`, or `process` without context.
10. Makes future extension harder than the current code.

## Final Response Templates

### Light

- Summary:
- Changed files:
- Validation:
- Review result:
- Unverified items:
- Notes:

### Standard / Strict

- Risk level:
- Role execution mode:
- Completed tasks:
- Changed files:
- Validation results:
- Review result:
- Blockers or risks:
- Unverified items:
- Recommended next step:

Never omit a field. If a field has no content, write `None`. If it was not verified, write `Not verified` and explain why.

## Final Delivery Checklist

For Light workflow, include:

- Summary.
- Changed files.
- Validation.
- Review result.
- Unverified items.
- Notes.

For Standard or Strict workflow, include:

- Risk level.
- Role execution mode.
- Completed tasks.
- Changed files.
- Validation results.
- Review result.
- Blockers or risks.
- Unverified items.
- Recommended next step.

Never claim a task is complete when required validation was skipped, failed, or remains unverified.
