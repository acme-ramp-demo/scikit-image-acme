# Remove `num_threads` from `rolling_ball`

## Scope

Complete the 0.28 deprecation of the `num_threads` parameter on `skimage.restoration.rolling_ball` in the **restoration** subpackage. Callers use `workers` (added in 0.26). Passing `num_threads` will raise `TypeError` after this change.

`workers=None` still means "let OpenMP choose the thread count" (`workers` is passed through as `0`). That behavior stays.

## Files

### `src/_skimage2` (the implementation)

- `src/_skimage2/restoration/_rolling_ball.py` — Remove `@deprecate_parameter`, the `num_threads=DEPRECATED` argument, the now-unused `deprecate_parameter` and `DEPRECATED` imports, and only the docstring line "Replaces deprecated parameter `num_threads`." Keep `.. versionadded:: 0.26`. The `workers` parameter and its description stay. Deprecations checklist items 1–4. Approved 2026-10-22.

### `src/skimage` and `src/skimage2` (no edits)

- `src/skimage/restoration/_rolling_ball.py` re-exports the implementation. Project map: v1 is a shim, so the signature change shows up here automatically.
- `src/skimage2/restoration/__init__.py` forwards `__getattr__` to `_skimage2`. No namespace wiring change.

### Cython (no edit)

- `src/_skimage2/restoration/_rolling_ball_cy.pyx` uses `num_threads=workers` on OpenMP `prange`. That is the compiler directive, not the deprecated public parameter. Leave both call sites (around lines 134 and 223).

### `tests/skimage`

- `tests/skimage/restoration/test_rolling_ball.py` — Delete `test_deprecated_num_threads` and the `inspect` import, which exists only for that test. `test_workers` already calls `workers=None`, `1`, and `2`. Checklist item 5; testing rule (both trees).
- `tests/skimage/test_migration.py` — Update the recorded signature so it no longer contains `num_threads=<DEPRECATED>`:

  `skimage.restoration:rolling_ball(image, *, radius=100, kernel=None, nansafe=False, workers=None)`

### `tests/skimage2`

- `tests/skimage2/restoration/test_rolling_ball.py` — Same deletion as the v1 test. The file imports from `_skimage2` and otherwise mirrors the v1 test, which is why both copies change.

### Docs

- No edit under `doc/examples` or `doc/source/release_notes/`. `release_0.26.rst` records that the deprecation started and stays as history.
- The removal is documented in a `release-note` block in the PR description (checklist item 8), drafted at PR time:

  ```release-note
  Remove the deprecated parameter `num_threads` from `skimage.restoration.rolling_ball`. Use `workers` instead.
  ```

### `TODO.txt`

- Delete the 0.28 bullet "Remove all traces of deprecated parameter `num_threads` in `skimage.restoration.rolling_ball`." Checklist item 7.

## Conventions applied

- Deprecations checklist in `.cursor/rules/20-deprecations.mdc`, all 8 items.
- Implementation lives in `_skimage2`; `skimage` and `skimage2` only re-export (project map).
- Tests are mirrored, so both `tests/skimage/restoration` and `tests/skimage2/restoration` change (testing rule).
- AI policy: this is a mechanical deprecation removal, so the agent may make the edits in a commit with an `Assisted-by:` trailer. The engineer writes the PR description.

## Test approach

No new behavior to specify. Removing the deprecation test is the test change. `test_workers` already covers the replacement parameter.

No `TypeError` test for a rejected `num_threads` argument. Approved 2026-10-22: that would only lock the signature, and `test_workers` already covers the replacement.

Run, after the edit:

```
spin test -- tests/skimage/restoration tests/skimage2/restoration
```

Before push: `pre-commit run --files <changed>`, `python tools/acme/check_boundaries.py`, and `spin test --test-modified --doctest`.

## Risks

- Editing the Cython `prange(..., num_threads=workers)` calls would change threading, not the public API. Those lines stay.
- Dropping `num_threads` from only one of the two test files leaves a warning-assertion test that fails once the decorator is gone.
- Leaving the migration-test signature stale fails `tests/skimage/test_migration.py`.
- Deleting the `versionadded` note must not delete the `workers` parameter description above it.
- `release_0.26.rst` mentions `num_threads` on purpose. A final grep of `src`, `tests`, and `doc/examples` should be clean of the public parameter; that release note is the expected leftover.

## Out of scope

`num_workers` on `skimage.restoration.cycle_spin` is a separate 0.28 item and is not part of this change.
