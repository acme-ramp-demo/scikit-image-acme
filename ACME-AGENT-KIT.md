# Acme agent kit

New engineers took 3–4 weeks to land a clean first change in this library,
because its conventions lived in reviewers' heads. This kit writes those
conventions down where Cursor's agent follows them, and backs the important
ones with checks that fail the commit and fail CI.

This repository is scikit-image, used as a stand-in for Acme's core library.
Everything Acme-specific lives in the files below; the rest is upstream.

## What's here

| Path                                               | What it does                                                                                                             |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `.cursor/rules/00-project-map.mdc`                 | Where code lives: `_skimage2` is the implementation, `skimage` and `skimage2` are shims; tests are mirrored in two trees |
| `.cursor/rules/10-python-style.mdc`                | Imports, dtypes, row/column naming, numpydoc, Cython                                                                     |
| `.cursor/rules/20-deprecations.mdc`                | When an API change needs a deprecation cycle; checklist for removing one                                                 |
| `.cursor/rules/30-testing.mdc`                     | Fixed seeds, warnings as errors, both test trees, what makes a good test                                                 |
| `.cursor/rules/40-boundaries.mdc`                  | What a change may pull in, and what to do when a boundary blocks you                                                     |
| `.cursor/rules/50-ai-use-policy.mdc`               | What the agent does on its own and what it hands back to the engineer                                                    |
| `.cursor/skills/first-contribution/`               | Guided first change: pick a ticket, map it, write a plan, stop for approval                                              |
| `.importlinter`                                    | `_skimage2` must never import the `skimage` or `skimage2` shims                                                          |
| `tools/acme/check_boundaries.py`, `allowlist.toml` | Library code may only import declared dependencies or baselined packages                                                 |
| `.pre-commit-config.yaml` (`acme-boundaries` hook) | Runs the dependency check before each commit                                                                             |
| `.github/workflows/acme-guardrails.yaml`           | Runs both checks on every PR; on merge, a mocked release waits for approval in the `acme-release` environment            |

## How to run it

Python 3.12 or newer. Keep the virtual environment **outside** the repository;
the Meson build refuses dependencies installed inside the source tree.

    python -m venv ~/.venvs/scikit-image-acme
    source ~/.venvs/scikit-image-acme/bin/activate
    pip install -r requirements/build.txt -r requirements/test.txt pre-commit
    pip install --no-build-isolation -e .
    pre-commit install

Run the checks directly:

    python tools/acme/check_boundaries.py
    cd src && PYTHONPATH=. lint-imports --config ../.importlinter

Run import-linter from an environment without the editable install, or point
`PYTHONPATH` at `src` as above; the editable install hides source files from it.

## Changing the kit

- **Rules are code.** Change them by pull request. When an agent gets something
  wrong, sharpen the rule rather than working around it.
- **The dependency baseline** in `allowlist.toml` records packages the library
  already imported when the policy started. Only new imports fail. Adding an
  entry widens what code may import, so it needs a reason and DevOps approval.
- **The local hook is a convenience; CI is the gate.** Pre-commit only runs where
  someone has installed it.

## Live, mocked, synthesized

- **Live:** the library, its tests, the rules and skill, both checks, CI, and the
  release approval.
- **Mocked:** the deploy step prints `MOCK DEPLOY` instead of publishing.
- **Synthesized:** Acme's context policy and dependency allowlist; Acme itself
  is fictional.
