# Example: Light Typo Fix

## User Prompt

"Fix this typo in the button label."

## Risk Classification

Light.

Reason:

- Local text-only change.
- No business logic, state, API, security, data, build, CI, deployment, or dependency change.

## Workflow

- Inspect the relevant file.
- Make the smallest text change.
- Run focused validation if available.
- Do not create `.agent/dev-plan.md` unless the user asks for a plan.

## Review Mode

Main Agent Self-Review is acceptable for Light work unless the user explicitly requests Agent Team or subagent review.

## Final Response Shape

- Summary:
- Changed files:
- Validation:
- Review result:
- Unverified items:
- Notes:
