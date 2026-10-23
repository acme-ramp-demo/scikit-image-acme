# Plan: remove deprecated `num_threads` from `rolling_ball`

**Checkpoint.** Gate 1 for the PM. No library code in this step. Commit this file later, together with the change.

## Scope

Remove the deprecated parameter `num_threads` from `skimage.restoration.rolling_ball` (subpackage: **restoration**), scheduled in `TODO.txt` under Version 0.28. `workers` stays as the only thread-count argument. The deprecation started in 0.26 (`start_version="0.26"`, `stop_version="0.28"`) via `@deprecate_parameter`.

This is a mechanical removal. The function body already reads `workers` and passes it into the Cython kernels. No algorithm change.

## Files

### `src/_skimage2` (implementation)

- `src/_skimage2/restoration/_rolling_ball.py` — Drop `@deprecate_parameter("num_threads", ...)`, the `num_threads=DEPRECATED` parameter, and the now-unused `deprecate_parameter` and `DEPRECATED` imports. In the `workers` docstring, delete the sentence `Replaces deprecated parameter `num_threads`.` and keep the bare `.. versionadded:: 0.26` (same form as other parameters in this tree). Leave the `workers is None → 0` body and the existing `from _skimage2._shared.utils import _supported_float_type` import style alone. Required by `20-deprecations.mdc` items 1–4.

Signature after the edit:

```python
def rolling_ball(
    image,
    *,
    radius=100,
    kernel=None,
    nansafe=False,
    workers=None,
):
```

- `src/_skimage2/restoration/_rolling_ball_cy.pyx` — **No edit.** `apply_kernel` and `apply_kernel_nan` already take `workers` and pass it as Cython `prange(..., num_threads=workers)`. That `num_threads` name is the OpenMP keyword Cython requires (lines 134 and 223). It is how `workers` is applied, and it stays.
- `src/_skimage2/restoration/__init__.pyi` — **No edit.** It exports the name `rolling_ball` and does not list parameters (`00-project-map.mdc`).

### `src/skimage` (v1 public API)

- `src/skimage/restoration/_rolling_ball.py` — **No edit.** It re-exports `rolling_ball` from `_skimage2`, so the public signature follows the implementation (`00-project-map.mdc`).
- `src/skimage/restoration/__init__.pyi` — **No edit.** Name-only export.

### `src/skimage2` (experimental namespace)

- `src/skimage2/restoration/__init__.py` and `__init__.pyi` — **No edit.** The package forwards `__getattr__` / `__all__` to `_skimage2.restoration` (`00-project-map.mdc`).

### `tests/skimage`

- `tests/skimage/restoration/test_rolling_ball.py` — Delete `test_deprecated_num_threads` (lines 101–109) and the `import inspect` that only that test uses. Keep `test_workers`. Required by `20-deprecations.mdc` item 5 and `30-testing.mdc` (both trees; warnings are errors, so a test that still expects `FutureWarning` would fail).
- `tests/skimage/test_migration.py` — Update the `SKIMAGE_API` snapshot consumed by `test_public_skimage_api`. `inspect.signature` follows the wrapped function, so the live key loses `num_threads`. Required because the public signature is asserted exactly.

From:

```text
skimage.restoration:rolling_ball(image, *, radius=100, kernel=None, nansafe=False, num_threads=<DEPRECATED>, workers=None)
```

To:

```text
skimage.restoration:rolling_ball(image, *, radius=100, kernel=None, nansafe=False, workers=None)
```

Keep the existing two-line string split in the set literal; let the formatter reflow it if it wants to.

### `tests/skimage2`

- `tests/skimage2/restoration/test_rolling_ball.py` — Same deletion as the `tests/skimage` copy: `test_deprecated_num_threads` and unused `import inspect`. The two files differ only in import paths (`skimage` vs `_skimage2`). Required by `20-deprecations.mdc` item 5 and `30-testing.mdc`.

### Docs

- `doc/examples/segmentation/plot_rolling_ball.py` — **No edit.** Calls use `radius` and `kernel` only. No `num_threads`.
- `doc/source/release_notes/release_0.26.rst` — **No edit.** That line records the 0.26 deprecation (`#7302`). It is a shipped note, not a live parameter.
- Docstrings on `rolling_ball` — Examples call `rolling_ball(image)` and `rolling_ball(image, kernel=kernel)`. They do not pass `num_threads`. The only docstring edit is the `versionadded` sentence in `_rolling_ball.py` above.

The decorator’s default `modify_docstring=True` injects an “Other Parameters” entry for `num_threads` at runtime. Removing the decorator removes that entry. There is no hand-written “Other Parameters” section in the source to delete.

### `TODO.txt`

- Delete the Version 0.28 item (lines 11–12):

  ```text
  * Remove all traces of deprecated parameter `num_threads` in
    `skimage.restoration.rolling_ball`.
  ```

  Leave the `num_workers` / `cycle_spin` item and the `binary_*` items. Required by `20-deprecations.mdc` item 7.

### `plans/`

- This file. Commit it later with the change, per the first-contribution skill. It is not a library edit.

## Conventions applied

Checklist from `20-deprecations.mdc` (“Completing a deprecation”), every item:

1. Remove `@deprecate_parameter` in `src/_skimage2/restoration/_rolling_ball.py`.
2. Remove `num_threads=DEPRECATED` from the signature. `workers=None` stays keyword-only after `*`.
3. Remove unused `deprecate_parameter` and `DEPRECATED` imports. In the tests, remove unused `inspect`.
4. Remove docstring text that names the old parameter. Keep `.. versionadded:: 0.26` with an empty body, matching `src/_skimage2/segmentation/random_walker_segmentation.py` and others.
5. Remove `test_deprecated_num_threads` in both `tests/skimage/restoration/` and `tests/skimage2/restoration/`.
6. After the edit, `grep -rn "num_threads" src tests doc/examples` should show only the two Cython `prange(..., num_threads=workers)` lines. Those are the OpenMP keyword, not the public parameter. `doc/source/release_notes/release_0.26.rst` also still contains the word; that file is outside `doc/examples` and stays.
7. Delete the `TODO.txt` item.
8. Put a `release-note` block in the PR description (engineer writes the final words). Proposed draft:

   ```release-note
   Remove the deprecated parameter `num_threads` from `skimage.restoration.rolling_ball`. Pass `workers` instead.
   ```

`00-project-map.mdc`: the edit lands in `_skimage2`. `skimage` and `skimage2` only re-export, so they stay as shims. Tests exist in both trees and both copies change.

`10-python-style.mdc`: public numpydoc docstring stays (summary, Parameters, Returns, Examples). No new dependency. No new public signature beyond deleting the scheduled parameter. Do not convert the existing `_skimage2._shared.utils` import to a relative import in this change.

`30-testing.mdc`: behavior of `workers` is already covered by `test_workers` (`None`, `1`, `2`, and `nansafe=True`). Do not add a test whose only job is “unknown keyword raises `TypeError`” unless the engineer asks; the testing rule treats that as trivial parameter validation.

`40-boundaries.mdc`: no new runtime dependency, no vendored edit, no network, no import from `skimage` into `_skimage2`. The Cython `num_threads` keyword stays because renaming it would fight the OpenMP API rather than remove the deprecated parameter.

`50-ai-use-policy.mdc`: after approval, the agent may make this mechanical edit in one commit with an `Assisted-by: Cursor <model>` trailer. The engineer writes the PR description and says which parts used AI. One draft PR.

### Disagreement to flag (do not pick silently)

`00-project-map.mdc` says `doc/source/development/deprecations.md` wins over `.cursor/rules/` when they disagree.

- The upstream page, under “Deprecation cycle”, says to record a **new** deprecation in `doc/release/release_dev.rst`. That path is not in this tree. `RELEASE.txt` builds notes at `doc/source/release_notes/release_dev.rst` from pull requests at release time.
- `CONTRIBUTING.md` (“Document changes”), `.github/PULL_REQUEST_TEMPLATE.md`, and `20-deprecations.mdc` item 8 say the note for this change is a `release-note` block in the PR description. Changelist turns that into the release notes.

The upstream paragraph describes **starting** a cycle (a future default change), not completing one. Recommendation for this removal: PR `release-note` block only. Do not add `release_dev.rst` and do not edit `release_0.26.rst`. Gate 1 confirms that recommendation.

## Test approach

No new cases unless the engineer picks one. Proposed edges, one reason each:

1. Keep `test_workers` in both trees (`workers` in `{None, 1, 2}`, default path and `nansafe=True`). Reason: the replacement argument must still be accepted on both kernels after the decorator is gone.
2. `test_public_skimage_api` in `tests/skimage/test_migration.py`. Reason: the v1 signature snapshot still contains `num_threads=<DEPRECATED>` and will fail until the string is updated.
3. Optional, engineer decides: call `rolling_ball(..., num_threads=1)` and expect `TypeError`. Reason: proves the name is gone. Skip by default; `30-testing.mdc` says not to add this kind of check only for coverage.
4. Doctests on `rolling_ball` stay as they are. Reason: they never passed `num_threads`. Run them with the pre-push command so a docstring edit cannot slip through.

Commands, after the code change (not in this step):

- Iterate: `spin test -- tests/skimage/restoration tests/skimage2/restoration tests/skimage/test_migration.py`
- Before push: `pre-commit run --files <changed>`, `python tools/acme/check_boundaries.py`, and `spin test --test-modified --doctest`.
- Warnings are errors unless `SKIMAGE_TEST_STRICT_WARNINGS=0`. Removing the tests that expected `FutureWarning` is what keeps the suite green.

## Risks

- Treating the Cython `prange` keyword as a leftover public parameter and renaming it. `workers` is already the value passed in. The keyword `num_threads` has to stay for OpenMP.
- Updating only one of the two `test_rolling_ball.py` copies. They are kept in parallel on purpose.
- Leaving `import inspect` in either test module. Ruff will report it unused (`F401`).
- Forgetting the `SKIMAGE_API` string. Restoration tests do not cover `test_public_skimage_api`.
- Deleting the `versionadded` directive along with the old name. `workers` was added in 0.26; the directive stays, the sentence that names `num_threads` goes.
- Editing `release_0.26.rst` because a repo-wide grep still hits it. That note is the historical announcement of the deprecation.
- Dropping the neighboring `TODO.txt` item for `cycle_spin`’s `num_workers`. That deprecation is a different ticket and is still open.
- Rewriting the `_shared.utils` import to a relative import while touching the line. Out of scope for this removal.

## Out of scope

- `num_workers` on `skimage.restoration.cycle_spin` (next `TODO.txt` item, still deprecated).
- Any change to ball/ellipsoid kernel math, padding, or `nansafe`.
- Gallery example, historical release notes, and the `skimage` / `skimage2` re-export shims.
