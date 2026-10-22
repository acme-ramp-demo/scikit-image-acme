# Acme agent kit (overlay for scikit-image)

Copy the contents of this folder into the root of the scikit-image repo.

Built against upstream `b700edc` (2026-10-09).

## What's here

| Path | What it is | Status |
| --- | --- | --- |
| `.cursor/rules/00-project-map.mdc` | Three package trees, mirrored tests, commands | From upstream docs and code |
| `.cursor/rules/10-python-style.mdc` | Imports, dtypes, coordinates, numpydoc, Cython | From `doc/source/development/guidelines.md` |
| `.cursor/rules/20-deprecations.mdc` | When a cycle is needed; 8-item removal checklist | From `deprecations.md` plus repo inspection |
| `.cursor/rules/30-testing.mdc` | RNG, strict warnings, parallel threads, what to test | From `testing.md` and the AI policy |
| `.cursor/rules/40-boundaries.mdc` | Code and context boundaries | Import direction is upstream; context policy is synthesized |
| `.cursor/rules/50-ai-use-policy.mdc` | What the agent may do on its own | Adapted from upstream `CONTRIBUTING.md` AI policy |
| `.cursor/skills/first-contribution/` | Guided first-change workflow with a plan checkpoint | New |
| `.importlinter` | `_skimage2` must not import `skimage`/`skimage2` | Enforces an upstream convention |
| `tools/acme/check_boundaries.py` + `allowlist.toml` | Third-party imports must be declared or baselined | Synthesized Acme policy |
| `.github/workflows/acme-guardrails.yaml` | Runs both checks; mocked release behind an approval environment | Deploy is mocked |
| `.pre-commit-config.yaml` (appended) | `acme-boundaries` hook runs the allowlist check before commit | New |

## Verified (2026-10-22)
- Build: `pip install --no-build-isolation -e .` takes about 5.5 minutes. Do it before the session.
- `tests/skimage/filters` + `tests/skimage/exposure`: 4,218 passed in 30 s.
- Import contract: kept on the clean repo; broken by an injected `from skimage.util import ...` in `_skimage2`.
- Allowlist: passes on the clean repo with the baseline; fails on an injected `import requests`.

## Running import-linter
Run it from an environment **without** the editable install (the meson editable hook hides source files from it):
`cd src && PYTHONPATH=. lint-imports --config ../.importlinter`

## Demo ticket
`TODO.txt` 0.28: remove deprecated `num_threads` from `skimage.restoration.rolling_ball`. Touches `src/_skimage2/restoration/_rolling_ball.py`, both `tests/*/restoration/test_rolling_ball.py`, `TODO.txt`, and a release note.

## To verify in Cursor
- Skill location (`.cursor/skills/<name>/SKILL.md`) and that the agent picks it up.
- Rules load as expected (`alwaysApply` vs. `globs`).
