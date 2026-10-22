---
name: first-contribution
description: Guide a new engineer through their first scoped change in this library, from picking a ticket to an opened PR. Use when someone says they're new, asks how to start, or asks to work a TODO.txt or good-first-issue item.
---

# First contribution

Walk the engineer through these stages in order. Stop at each **Checkpoint** and wait for them. Follow the rules in `.cursor/rules/`.

## 1. Pick and scope

- If no ticket is given, offer 3 candidates from `TODO.txt` for the current or next version (completing a deprecation is the ideal first task: mechanical, convention-heavy, easy to review).
- Restate the task in one sentence and name the subpackage.

## 2. Map the change (no edits yet)

- Find every place the change touches. For a deprecation removal, run `grep -rn "<name>" src tests doc TODO.txt`.
- List files grouped by tree: `src/_skimage2`, `src/skimage`, `src/skimage2`, `tests/skimage`, `tests/skimage2`, docs, `TODO.txt`.
- For each file, one line on what changes and which rule requires it.

**Checkpoint: the plan.** Write the plan to `plans/<ticket-slug>.md` (scope, files, conventions applied, test approach, risks). This file is what the PM approves in Grok Bot (Gate 1). Do not edit code until it is approved.

## 3. Make the change

- Mechanical edits: do them, in a commit with an `Assisted-by:` trailer.
- Anything algorithmic: explain what's needed and let the engineer write it.
- Explain each convention as you apply it ("the test exists in both trees because...") so the engineer learns it, not just ships it.

## 4. Tests

- Propose edge cases, one line of reasoning each. The engineer picks.
- Scaffold the chosen tests; the engineer confirms assertions.
- Run `spin test -- tests/skimage/<sub> tests/skimage2/<sub>`.

## 5. Self-review before push

- Run `pre-commit run --files <changed>` and `python tools/acme/check_boundaries.py`.
- Walk the relevant rule checklists (for deprecations, all 8 items in `20-deprecations.mdc`) and mark each done or not.
- Run `spin test --test-modified --doctest`.

## 6. Open the PR

- Draft a checklist for the PR description: what changed, which parts used AI, the `release-note` block. The engineer writes the final words.
- Push a branch and open the PR. The review Automation and CI take it from there.
