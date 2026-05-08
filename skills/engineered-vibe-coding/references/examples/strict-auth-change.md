# Example: Strict Auth Change

## User Prompt

"Change the auth flow."

## Risk Classification

Strict.

Reason:

- Authentication is security-sensitive.
- Likely changes state, API, routing, persistence, and error handling.
- User-visible and production-sensitive.

## Required Workflow

- Do not implement immediately.
- Inspect existing auth flow.
- Clarify non-discoverable business and security requirements.
- Create or update `.agent/dev-plan.md`.
- Record non-goals, acceptance criteria, risks, and decisions.
- Complete requirement analysis before design.
- Complete design before architecture.
- Complete architecture before implementation.
- Define First Slice.
- Treat failed validation or unclear requirements as blockers.

## Example First Slice

Implement the smallest verifiable auth boundary change, such as adapting one existing login state transition while preserving current behavior and running focused validation.

## Review Mode

Agent Team Review is preferred for Strict work.

If Agent Team Review is unavailable, use Subagent Review when available.

Main Agent Self-Review is fallback only and must produce separate role outputs with evidence.

If Main Agent Self-Review fallback is used for Strict work, record it as a risk in `.agent/dev-plan.md`.

## Example Role Review Record

- Role: Architect
- Mode: Subagent
- Result: Pass
- Evidence: Existing auth state transition pattern was reused; no public auth API contract was changed.
- Required Fixes: None
- Risks: Session refresh behavior not covered in First Slice.
- Unverified Items: Production identity provider response shape.

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
