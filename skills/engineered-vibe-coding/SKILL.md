---
name: engineered-vibe-coding
description: Engineering-grade vibe coding workflow for complex software development tasks. Use when Codex is asked to implement non-trivial features, refactor code, modify architecture, work across multiple files, add quality gates, clarify ambiguous requirements, create development plans, or perform structured coding with testing and code review. Also use when the user mentions engineered vibe coding, engineering workflow, coding pipeline, development plan, quality gates, anti-spaghetti-code rules, or asks Codex to avoid rushed or messy implementation.
---

# Engineered Vibe Coding

Use this skill to make complex coding work disciplined: classify risk, inspect the repository, plan only when needed, implement one atomic task at a time, validate, review, and report what remains unverified.

## Hard Rules

1. Classify risk before implementation.
2. When uncertain, escalate to the higher-risk workflow.
3. Inspect the repository before asking discoverable questions.
4. For Standard and Strict workflows, create or update `.agent/dev-plan.md`.
5. For Light workflow, create `.agent/dev-plan.md` if the user explicitly asks for a plan.
6. Implement only one atomic task at a time.
7. Discover validation commands from project files; never invent commands.
8. Never bypass configured hooks or validation commands.
9. Failed validation, unrelated edits, temporary code, or review rejection block progression.
10. Final delivery must include changed files, validation results, review result, remaining risks, and unverified items.
11. For Standard and Strict workflows, `.agent/dev-plan.md` is the single source of truth for scope, decisions, active task, blockers, validation, review, risks, and unverified items.
12. Standard and Strict workflows must pass three checkpoints: Plan, First Slice, and Release. Do not skip or silently pass checkpoints.
13. Before final delivery, perform the self-review protocol and fix missing or failed items before claiming completion.
14. For Standard and Strict workflows, clarify requirements, plan architecture, split work into modules, and break each module into atomic tasks before implementation.
15. Use the strongest available role execution mode: Agent Team first, subagent review second, main-agent self-review only as fallback. Do not silently fall back to self-review; record the chosen mode and reason.

## Risk Classification

Use **Light** only for single-file, low-risk fixes such as copy edits, tiny local bugs, or small adjustments that do not change core business logic, state, APIs, security, data, build, CI, deployment, or dependencies.

Use **Standard** for multi-file changes, new features, user-visible behavior changes, medium refactors, or work that needs task splitting.

Use **Strict** for ambiguous requirements, architecture changes, authentication, authorization, payments, permissions, database migrations, public APIs, large refactors, security-sensitive work, production critical paths, dependency upgrades, or build/CI/deployment changes. Login, auth, payment, database, dependency, build, CI, deployment, and architecture changes default to Strict.

When the risk is unclear, choose the higher-risk workflow.

## Repository Discovery

Before asking the user, inspect the repository for discoverable answers. Ask only about non-discoverable product, business, security, or irreversible decisions.

Discover validation commands from project files such as `package.json`, `pyproject.toml`, `Cargo.toml`, `pom.xml`, `build.gradle`, `pubspec.yaml`, `Makefile`, CI configs, and `README`. Never invent commands.

If no validation command is found, report: `No validation command was found. Performed best available focused verification instead.`

## References

- Read `references/workflow.md` for detailed Light, Standard, and Strict workflows, repository discovery, quality gates, and the failure loop.
- Read `references/roles.md` before role-based planning, role-based review, Agent Team review, subagent review, or self-review fallback.
- Read `references/dev-plan-template.md` before creating or updating `.agent/dev-plan.md`.
- Read `references/review-checklists.md` before code review, quality review, or final delivery for Standard and Strict work.
- Read `references/examples/` only when behavior is unclear or when calibrating Light, Standard, or Strict workflow behavior.

## Final Response Format

For Light workflow:

- Summary
- Changed files
- Validation
- Review result
- Unverified items
- Notes

For Standard or Strict workflow:

- Risk level
- Role execution mode
- Completed tasks
- Changed files
- Validation results
- Review result
- Blockers or risks
- Unverified items
- Recommended next step

Never omit required final response fields. If a field has no content, write `None`. If it was not verified, write `Not verified` and explain why.
