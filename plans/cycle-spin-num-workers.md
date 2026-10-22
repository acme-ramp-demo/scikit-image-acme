# Plan: remove `num_workers` from `cycle_spin`

**Task:** Remove every trace of the deprecated parameter `num_workers` on `skimage.restoration.cycle_spin` (subpackage `restoration`, `TODO.txt` Version 0.28). Callers use `workers`.

**Status:** Gate 1 plan only. No code edits until this file is approved.

`@deprecate_parameter` on `cycle_spin` has `start_version="0.26"` and `stop_version="0.28"`. Version 0.28 is the scheduled removal. The replacement keyword `workers` already exists and is keyword-only.

## Scope

In `src/_skimage2/restoration/_cycle_spin.py` only:

1. Delete the `@deprecate_parameter(deprecated_name="num_workers", ...)` decorator. Keep `@utils.channel_as_last_axis()`.
2. Delete the parameter `num_workers=DEPRECATED` from the signature.
3. Drop the now-unused names `deprecate_parameter` and `DEPRECATED` from the utils import. Keep `warn` (the dask-missing warning still uses it) and `from _skimage2._shared import utils`.
4. Lower the dask-missing `warn(..., stacklevel=4)` to `stacklevel=3`. See Human decisions.

Resulting signature:

```python
@utils.channel_as_last_axis()
def cycle_spin(
    x,
    func,
    max_shifts,
    shift_steps=1,
    func_kw=None,
    *,
    workers=None,
    channel_axis=None,
):
```

`inspect.signature` of that function is:

```text
(x, func, max_shifts, shift_steps=1, func_kw=None, *, workers=None, channel_axis=None)
```

The source docstring has no sentence that names `num_workers`. The `workers` parameter docs stay as they are. `@deprecate_parameter` (`modify_docstring=True` by default) injects an "Other Parameters" entry for `num_workers` at runtime via `_docstring_add_deprecated`. Removing the decorator removes that generated text from rendered docs. Checklist item 4 needs no source-docstring edit.

Leave the absolute `_skimage2` imports in this file as they are. Rewriting them to relative imports is outside this ticket.

Leave `num_threads` on `rolling_ball` alone. That is a separate Version 0.28 bullet.

## Files by tree

### `_skimage2`

- `src/_skimage2/restoration/_cycle_spin.py` — remove the decorator, the `num_workers` parameter, and the unused `deprecate_parameter` / `DEPRECATED` imports; set the dask warning `stacklevel` to 3. Required by `20-deprecations.mdc` items 1–3. The `stacklevel` change is the frame that disappears with the decorator (human confirmation below).
- `src/_skimage2/restoration/__init__.pyi` — leave unchanged. It lists the name `cycle_spin` and does not spell the signature (`00-project-map.mdc`: public names stay in the stub `__all__`).

### `skimage`

- `src/skimage/restoration/_cycle_spin.py` — leave unchanged. It re-exports `cycle_spin` from `_skimage2` and runs `adapt_doctests`. The public signature follows the implementation (`00-project-map.mdc`: shims only).
- `src/skimage/restoration/__init__.py` and `src/skimage/restoration/__init__.pyi` — leave unchanged. Lazy-load still exposes the name `cycle_spin`.

### `skimage2`

- `src/skimage2/restoration/__init__.py` — leave unchanged. `__getattr__` / `__dir__` / `__all__` forward to `_skimage2.restoration` (`00-project-map.mdc`: namespace wiring only).
- `src/skimage2/restoration/__init__.pyi` — leave unchanged. It star-re-exports `_skimage2.restoration`.

### `tests/skimage`

- `tests/skimage/restoration/test_denoise.py` — delete `test_cycle_spinner_deprecate_num_workers` (lines 1202–1223) and the import `from _skimage2._shared.testing import assert_stacklevel`, which that test is the only user of. Required by `20-deprecations.mdc` item 5 and `30-testing.mdc` (both trees). An unused import fails ruff.
- `tests/skimage/test_migration.py` — in `SKIMAGE_API`, replace the `cycle_spin` entry so it matches the new signature. `test_public_skimage_api` compares `inspect.signature` of the public function to this string. Required because the signature change would fail that test.

  From:

  ```text
  skimage.restoration:cycle_spin(x, func, max_shifts, shift_steps=1, num_workers=<DEPRECATED>, func_kw=None, *, workers=None, channel_axis=None)
  ```

  To:

  ```text
  skimage.restoration:cycle_spin(x, func, max_shifts, shift_steps=1, func_kw=None, *, workers=None, channel_axis=None)
  ```

  Leave the `rolling_ball` / `num_threads=<DEPRECATED>` line unchanged.

### `tests/skimage2`

- `tests/skimage2/restoration/test_denoise.py` — same deletion as the `tests/skimage` copy: `test_cycle_spinner_deprecate_num_workers` and the unused `assert_stacklevel` import. This copy imports `restoration` from `_skimage2`, so it calls the same function. The test exists in both trees because a behavior change in `_skimage2` is covered twice (`00-project-map.mdc`, `30-testing.mdc`, `20-deprecations.mdc` item 5).

There is no `skimage2` copy of `test_migration.py`. The signature snapshot lives only under `tests/skimage`.

### `docs`

- `doc/examples/filters/plot_cycle_spinning.py` — leave unchanged. It calls `cycle_spin` with `func`, `max_shifts`, `func_kw`, and `channel_axis`. It does not pass `num_workers`. Checklist item 6 includes `doc/examples`.
- `doc/source/release_notes/release_0.26.rst` — leave unchanged. The 0.26 note records that the parameter was deprecated in favor of `workers`. Checklist item 6 searches `src`, `tests`, and `doc/examples`, which does not include `doc/source/release_notes`. See Human decisions.
- No new file under `doc/`. The removal note is the `release-note` block in the PR description (`20-deprecations.mdc` item 8, `CONTRIBUTING.md`). The engineer writes the final words (`50-ai-use-policy.mdc`). Draft for that block:

  ```release-note
  Remove the deprecated parameter `num_workers` from `skimage.restoration.cycle_spin`. Use `workers` instead.
  ```

### `TODO.txt`

- Delete the Version 0.28 bullet "Remove all traces of deprecated parameter `num_workers` in `skimage.restoration.cycle_spin`." (`20-deprecations.mdc` item 7). Leave the `num_threads` / `rolling_ball` bullet above it.

## Conventions applied

Deprecation removal checklist (`20-deprecations.mdc`), each item mapped:

1. Remove `@deprecate_parameter` in `src/_skimage2/restoration/_cycle_spin.py`.
2. Remove `num_workers` from the signature.
3. Remove unused imports `deprecate_parameter` and `DEPRECATED`. Also remove the unused `assert_stacklevel` import in both denoise test files (ruff F401).
4. Source docstring does not mention `num_workers`. The runtime "Other Parameters" entry disappears with the decorator.
5. Remove `test_cycle_spinner_deprecate_num_workers` in both `tests/skimage/restoration/test_denoise.py` and `tests/skimage2/restoration/test_denoise.py`.
6. After the edit, `grep -rn "num_workers" src tests doc/examples` returns nothing for this function. The only remaining `num_workers` hit in the repo is `doc/source/release_notes/release_0.26.rst`, which is outside that grep.
7. Delete the matching `TODO.txt` bullet.
8. `release-note` block in the PR description (draft above). The engineer writes the final PR text (`50-ai-use-policy.mdc`, skill stage 6).

Other rules:

- `00-project-map.mdc`: implementation change stays in `_skimage2`. `skimage` and `skimage2` keep their shim / forwarder. Both test trees are updated. Doctest in `cycle_spin` still runs in CI.
- `10-python-style.mdc`: no new public signature beyond deleting the deprecated parameter. No new dependency. No import-style cleanup.
- `30-testing.mdc`: warnings stay errors in tests. The deprecation test is the only `FutureWarning` for this parameter; after removal, passing `num_workers` is a `TypeError`. Existing `workers` tests stay.
- `40-boundaries.mdc`: no new dependency, no vendored edit, no network, no code from outside this repo. `_skimage2` still does not import `skimage` or `skimage2`.
- `50-ai-use-policy.mdc`: the later code edit is mechanical. Put it in its own commit with an `Assisted-by: Cursor <model>` trailer. This plan does not choose new tests; it proposes cases below.

Upstream `doc/source/development/deprecations.md` agrees that keyword removal uses `deprecate_parameter` and that a cycle is required for a rename. It tells authors who *start* a deprecation to write `doc/release/release_dev.rst`. That path is not in this tree. `CONTRIBUTING.md` and rule 20 record the removal in the PR `release-note` block, which changelist turns into release notes. Flagged under Human decisions. This plan follows the local checklist.

## How it will be tested

Existing tests that stay, and would fail if `workers` or `channel_axis` broke:

- `test_cycle_spinning_workers` in both denoise files: `workers=1`, `workers=4`, and `workers=None`, including the dask-missing `UserWarning` via `expected_warnings`.
- `test_cycle_spinning_multichannel` in both denoise files: `channel_axis` still goes through `@utils.channel_as_last_axis()`.
- The doctest in `cycle_spin` (`# doctest: +IGNORE_WARNINGS`). It calls `cycle_spin` without `num_workers`.
- `tests/skimage/test_migration.py::test_public_skimage_api` after the snapshot string is updated.

Commands when implementation is allowed (skill stages 4–5; not part of this plan commit):

- Iterate: `spin test -- tests/skimage/restoration tests/skimage2/restoration`
- Also run `tests/skimage/test_migration.py::test_public_skimage_api` (it lives outside the restoration directory).
- Before push: `pre-commit run --files <changed>`, `python tools/acme/check_boundaries.py`, and `spin test --test-modified --doctest`.

Proposed cases for the engineer to accept or drop (`30-testing.mdc`, `50-ai-use-policy.mdc`). One line of reasoning each:

1. Keep `test_cycle_spinning_workers` as the regression for `workers=1`, `4`, and `None`. It already fails if the parallel and serial paths diverge.
2. Keep `test_cycle_spinning_multichannel`. Removing the outer decorator must leave `channel_as_last_axis` in place.
3. Update the `SKIMAGE_API` string and let `test_public_skimage_api` lock the new signature, including that `func_kw` is again the fifth parameter.
4. Skip a new test that calls `cycle_spin(..., num_workers=1)` and expects `TypeError`. The test would keep the name `num_workers` under `tests/`, so checklist item 6 would fail.
5. Optional: in `test_cycle_spinning_workers`, capture the dask-missing warning with `pytest.warns` and `assert_stacklevel`. Nothing checks that warning's stack today, and deleting the decorator changes the frame count. Add this only if the engineer wants the new `stacklevel` locked.

## What could break

- Keyword calls `cycle_spin(..., num_workers=...)` raise `TypeError`. That is the scheduled end of the 0.26–0.28 cycle. `workers` is unchanged.
- A fifth positional argument is `func_kw` again. Today the fifth positional is `num_workers` (`=DEPRECATED`), and the decorator copies that value onto `workers`. After removal, `cycle_spin(x, func, max_shifts, shift_steps, some_dict)` passes `some_dict` as `func_kw`. A sixth positional argument raises `TypeError` (`workers` and `channel_axis` are keyword-only).
- `test_public_skimage_api` fails until the snapshot string drops `num_workers=<DEPRECATED>`.
- Both `test_cycle_spinner_deprecate_num_workers` copies fail until deleted: `pytest.warns(FutureWarning)` sees no warning, then the unexpected keyword raises `TypeError`.
- The dask-missing warning uses `stacklevel=4` to step from `cycle_spin` through `channel_as_last_axis` and `deprecate_parameter` to the caller (`warn` is `functools.partial(warnings.warn, ...)`, which adds no Python frame; the explicit `stacklevel=4` overrides the partial's default of 2). After the outer decorator is gone, `stacklevel=4` points at the caller's caller. `expected_warnings` matches the message, so `test_cycle_spinning_workers` can still pass while the warning is attributed to the wrong line. `stacklevel=3` points at the caller. See Human decisions.
- Leaving `deprecate_parameter`, `DEPRECATED`, or `assert_stacklevel` imported fails ruff F401 under `pre-commit`.
- Editing the `rolling_ball` snapshot or its `num_threads` parameter in the same change fails `test_public_skimage_api` or the rolling-ball tests for a ticket this plan does not cover.
- The gallery example and the function doctest do not pass `num_workers`. They keep working. The doctest still uses the global NumPy RNG (`np.random.standard_normal`); that is pre-existing and stays.

## Human decisions

1. **`stacklevel` 4 → 3.** Recommendation: change it. One wrapper frame goes away; `channel_as_last_axis` remains; `3` attributes the dask-missing warning to the caller. Confirm the count before the edit, since a wrong stacklevel is silent under `expected_warnings`.
2. **TypeError test that still names `num_workers`.** Recommendation: do not add one. Checklist item 6 requires a clean grep of `src`, `tests`, and `doc/examples`. The engineer picks (proposal 4 above).
3. **`assert_stacklevel` on the dask warning.** Recommendation: add it only if you want the new stacklevel locked (proposal 5). The agent does not add it unless you say so.
4. **`doc/source/release_notes/release_0.26.rst`.** Recommendation: leave the 0.26 deprecation note. It is the historical record, and it sits outside the checklist grep. Say if you want that sentence edited anyway.
5. **Where the removal is announced.** `doc/source/development/deprecations.md` mentions `doc/release/release_dev.rst` for starting a deprecation. That file is not in this repo. Rule 20 item 8 and `CONTRIBUTING.md` use a `release-note` block in the PR description. Recommendation: follow the PR block and do not add a release-notes file. `00-project-map.mdc` says to flag an upstream disagreement; this is that flag.
6. **Scope boundary with `rolling_ball`.** Recommendation: this change is only `cycle_spin` / `num_workers`. The Version 0.28 `num_threads` bullet stays in `TODO.txt`.
