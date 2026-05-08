# Example: Standard Feature

## User Prompt

"Add a user settings page."

## Risk Classification

Standard.

Reason:

- New user-visible feature.
- Likely multi-file change.
- Requires task decomposition.

## Required Workflow

- Inspect routes, pages, state, API, and existing patterns.
- Create or update `.agent/dev-plan.md`.
- Pass Checkpoint Plan.
- Define First Slice.
- Implement First Slice before expanding scope.
- Pass Checkpoint First Slice.
- Continue one atomic task at a time.
- Pass Checkpoint Release before final delivery.

## Example First Slice

Create a minimal settings page route using existing layout patterns, display a static current-user settings placeholder, and run discovered validation.

## Review Mode

Prefer Agent Team Review when available.

If Agent Team Review is unavailable, use Subagent Review.

If both are unavailable, use Main Agent Self-Review and record the fallback reason in `.agent/dev-plan.md`.

## Example Role Review Record

- Role: Architect
- Mode: Subagent
- Result: Pass
- Evidence: Existing route pattern was reused; no new routing abstraction introduced.
- Required Fixes: None
- Risks: API integration not implemented in First Slice.
- Unverified Items: Real API response shape.

## Final Response Shape

- Risk level:
- Role execution mode:
- Completed tasks:
- Changed files:
- Validation results:
- Review result:
- Blockers or risks:
- Unverified items:
- Recommended next step:
