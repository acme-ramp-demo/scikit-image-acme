Plan approved by Jimmy Ungerman in Grok Bot.

# Remove deprecated `num_workers` from `skimage.restoration.cycle_spin`

## Scope

Remove the deprecated parameter `num_workers` from `skimage.restoration.cycle_spin` in the **restoration** subpackage. This completes the deprecation that started in 0.26 (`start_version="0.26"`) and is scheduled for removal in 0.28 (`stop_version="0.28"`, `TODO.txt` Version 0.28). Callers use `workers` instead.

`num_workers` is positional today. Removing it shifts every later positional parameter one slot left. `func_kw` moves from the 6th positional slot to the 5th. `workers` and `channel_axis` stay keyword-only.

## Signature

Current (`src/_skimage2/restoration/_cycle_spin.py`):

```python
@deprecate_parameter(
    deprecated_name="num_workers",
    new_name="workers",
    start_version="0.26",
    stop_version="0.28",
)
@utils.channel_as_last_axis()
def cycle_spin(
    x,
    func,
    max_shifts,
    shift_steps=1,
    num_workers=DEPRECATED,
    func_kw=None,
    *,
    workers=None,
    channel_axis=None,
):
```

After:

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

Recorded public signature in `tests/skimage/test_migration.py` (`SKIMAGE_API`), which `test_public_skimage_api` compares to `inspect.signature`:

```text
skimage.restoration:cycle_spin(x, func, max_shifts, shift_steps=1, func_kw=None, *, workers=None, channel_axis=None)
```

## Positional shift

`deprecate_parameter` (`src/_skimage2/_shared/utils.py`) warns when the 5th positional argument is present (`deprecated_idx == 4`) or when `num_workers` is passed by keyword, then assigns that value to `workers`. Passing `func_kw` in the 6th positional slot requires also passing `num_workers` in the 5th, so those callers already received `FutureWarning: Parameter `num_workers`is deprecated ... use the parameter`workers` instead`. Keyword calls that name `func_kw` and `workers` and omit `num_workers` were never warned and keep working.

After removal:

- `cycle_spin(..., workers=n)` and `cycle_spin(..., func_kw=d)` stay valid.
- `cycle_spin(..., num_workers=n)` raises `TypeError` (unexpected keyword).
- A 5th positional value binds to `func_kw`.
- A 6th positional value raises `TypeError` (too many positional arguments), because `workers` and `channel_axis` are keyword-only.

## Stacklevel

The only warning `cycle_spin` itself raises is the missing-dask `UserWarning`, via `warn(..., stacklevel=4)`. `warn` is `functools.partial(warnings.warn, stacklevel=2)`; the explicit `stacklevel=4` replaces that default, and `partial` adds no Python frame.

Frames above that `warn(...)` line today:

1. the `warn(...)` line in the `cycle_spin` body
2. the `channel_as_last_axis` wrapper
3. the `deprecate_parameter` wrapper
4. the caller

`stacklevel=4` points at the caller. Removing the outer decorator leaves the `channel_as_last_axis` frame (it calls through even when `channel_axis is None`). Set `stacklevel=3` so the warning still points at the caller.

`skimage.restoration.cycle_spin` is an `adapt_doctests` copy of the outermost wrapper, and `skimage2.restoration.cycle_spin` is the `_skimage2` object forwarded by `__getattr__`. Neither adds a further frame. One stacklevel serves both public namespaces.

`test_cycle_spinning_workers` matches that warning's message through `expected_warnings` and does not check stacklevel. Message-only tests will not catch a wrong stacklevel (deprecations rule, rehearsal gap).

## Docstring

The source docstring does not mention `num_workers`. `workers` is already documented and does not say "Replaces deprecated parameter ...". `deprecate_parameter` injects an "Other Parameters" entry at runtime (`num_workers : DEPRECATED`, "Deprecated in favor of `workers`"). Removing the decorator removes that entry. No docstring text edit.

## Files

### `src/_skimage2` (implementation)

- `src/_skimage2/restoration/_cycle_spin.py` — Drop `@deprecate_parameter`. Drop `num_workers=DEPRECATED` from the signature. Drop `deprecate_parameter` and `DEPRECATED` from `from _skimage2._shared.utils import ...`. Keep `warn` and `from _skimage2._shared import utils` (`@utils.channel_as_last_axis()` stays). Change the dask warning from `stacklevel=4` to `stacklevel=3`. Required by `20-deprecations.mdc` items 1–4 and the stacklevel gap.

### `src/skimage` (stable shim)

No source edit. `src/skimage/restoration/_cycle_spin.py` re-exports the `_skimage2` function and `adapt_doctests` copies it. `src/skimage/restoration/__init__.pyi` still lists the name `cycle_spin`. The public signature change is recorded in `tests/skimage/test_migration.py` (`00-project-map.mdc`: shims only; `20-deprecations.mdc` signature gap).

### `src/skimage2` (experimental namespace)

No source edit. `src/skimage2/restoration/__init__.py` forwards `__getattr__` / `__dir__` / `__all__` to `_skimage2.restoration`. The parameter disappears with the implementation (`00-project-map.mdc`: namespace wiring only).

### `tests/skimage`

- `tests/skimage/restoration/test_denoise.py` — Delete `test_cycle_spinner_deprecate_num_workers` (the `num_workers` parametrization, the `FutureWarning` match, and `assert_stacklevel(record, offset=-8)`). Keep the `assert_stacklevel` import: the accepted follow-up uses it in `test_cycle_spinning_workers`. Required by `20-deprecations.mdc` item 5 and `30-testing.mdc` (both trees).
- `tests/skimage/test_migration.py` — Replace the `SKIMAGE_API` string so `num_workers=<DEPRECATED>, ` is gone and `func_kw=None` follows `shift_steps=1`. Required by `20-deprecations.mdc` (recorded signature).

### `tests/skimage2`

- `tests/skimage2/restoration/test_denoise.py` — Same test deletion and the same stacklevel assertion as the `tests/skimage` copy. The two files are separate (different imports, and `binary_blobs` is called differently). Leave the other differences. Required by `20-deprecations.mdc` item 5 and `30-testing.mdc`.

There is no `tests/skimage2` copy of `test_migration.py`.

### Docs

No edit.

- `doc/examples/filters/plot_cycle_spinning.py` calls `cycle_spin` with `func_kw` and `channel_axis` as keywords. It does not pass `num_workers`.
- Leave `doc/source/release_notes/release_0.26.rst` as the record that 0.26 deprecated `num_workers`. The removal checklist grep is `src`, `tests`, and `doc/examples`, not historical release notes.

### `TODO.txt`

- Delete the Version 0.28 item "Remove all traces of deprecated parameter `num_workers` in `skimage.restoration.cycle_spin`." Leave the neighboring `num_threads` / `rolling_ball` item. Required by `20-deprecations.mdc` item 7.

## Conventions applied

`20-deprecations.mdc` removal checklist:

1. Remove `@deprecate_parameter` on `cycle_spin`.
2. Remove `num_workers` from the signature.
3. Remove unused `deprecate_parameter` and `DEPRECATED` imports.
4. Source docstring has no old-name text. The runtime "Other Parameters" entry disappears with the decorator.
5. Remove `test_cycle_spinner_deprecate_num_workers` in both `tests/skimage/restoration/test_denoise.py` and `tests/skimage2/restoration/test_denoise.py`.
6. After the edit, `grep -rn "num_workers" src tests doc/examples` should print nothing for this function.
7. Delete the matching `TODO.txt` item.
8. PR description gets a `release-note` block (draft below). The engineer writes the final words (`50-ai-use-policy.mdc`).

Also from that rule:

- Positional shift of `func_kw` is stated here and in the release note. Callers of that slot already got the `FutureWarning`, because reaching it required passing `num_workers`.
- Update `SKIMAGE_API` in `tests/skimage/test_migration.py`.
- Lower the dask warning `stacklevel` from 4 to 3.

`00-project-map.mdc`: the edit lives in `_skimage2`. `skimage` and `skimage2` only re-export, so they need no source change. Tests exist in both trees and both copies of `test_denoise.py` change. Import direction stays one-way.

`30-testing.mdc`: behavior change is covered by the signature test and by the existing `workers=` tests, which would fail if `workers` stopped working. Warnings are errors in tests, so a leftover `num_workers=` call fails. No new randomness. The stacklevel check was accepted on 2026-10-27.

`10-python-style.mdc`: this change does not restyle the existing absolute `_skimage2` imports in `_cycle_spin.py` into relative imports. Drop only the names that become unused.

`40-boundaries.mdc`: no new dependency, no import from `skimage` or `skimage2` into `_skimage2`, no vendored edits, no network.

`50-ai-use-policy.mdc`: this is a mechanical deprecation removal. The implementation commit carries an `Assisted-by:` trailer. The engineer confirms any new assertion and writes the PR text.

`doc/source/development/deprecations.md` matches these rules: a renamed keyword needs a deprecation cycle, warnings stay for two releases (0.26 and 0.27, removed in 0.28), and removal uses the existing `deprecate_parameter` helper rather than a hand-rolled warning. No disagreement to flag.

## Test approach

Keep:

- `test_cycle_spinning_workers` in both trees (`workers=1`, `workers=4`, `workers=None`).
- `test_cycle_spinning_multichannel` in both trees.
- The docstring example on `cycle_spin` (keyword `max_shifts` only).

Change:

- Delete the deprecation test in both trees.
- Update the `SKIMAGE_API` signature string.

Accepted 2026-10-27: when dask is not installed, assert the stacklevel of the missing-dask `UserWarning` inside `test_cycle_spinning_workers`, in both trees. Reason: `stacklevel` must drop from 4 to 3, and `expected_warnings` only checks the message. The two `cycle_spin` calls warn on different lines, so each call has its own `expected_warnings` block and `assert_stacklevel(record, offset=-9)`. The offset counts back to the first line of that multiline call. When dask is installed, `DASK_NOT_INSTALLED_WARNING` is `None` and the assertion is skipped. The `assert_stacklevel` import stays.

Commands after the code change (not part of this plan step):

- `grep -rn "num_workers" src tests doc/examples`
- `spin test -- tests/skimage/restoration tests/skimage2/restoration`
- Before push: `pre-commit run --files <changed>` and `python tools/acme/check_boundaries.py`
- `spin test --test-modified --doctest`

## Risks

- A caller who passed an integer `num_workers` positionally will now bind that integer to `func_kw`. `func(xs, **func_kw)` then fails. Those callers were warned during 0.26–0.27. The release note has to say `func_kw` moved one positional slot left.
- Leaving `stacklevel=4` makes the dask warning point at the `channel_as_last_axis` wrapper. Current tests still pass.
- Editing only one copy of `test_denoise.py` leaves a test that calls `num_workers=` and fails under warnings-as-errors.
- Skipping `test_migration.py` fails `test_public_skimage_api`.
- Leaving `DEPRECATED` imported fails ruff F401.
- `rolling_ball`'s `num_threads` deprecation is a separate Version 0.28 item. It stays.

## Out of scope

- `num_threads` on `skimage.restoration.rolling_ball`.
- Reordering the `workers` / `func_kw` paragraphs in the docstring. `workers` is already documented above `func_kw`.
- The global `np.random.standard_normal` in the `cycle_spin` docstring example.
- Rewriting `_cycle_spin.py` imports to relative form.
- `doc/source/release_notes/release_0.26.rst`.

## Release note

For the PR description. The engineer writes the final words.

```release-note
Remove the deprecated parameter ``num_workers`` from ``skimage.restoration.cycle_spin``.
Pass ``workers`` instead. ``num_workers`` was positional, so ``func_kw`` moves one
positional slot to the left (it is now the 5th positional parameter). ``workers`` and
``channel_axis`` stay keyword-only.
```

## Checkpoint

This file is the plan for review. No library code, tests, or `TODO.txt` edits until it is approved. The plan file is committed later, together with the change.

Implement in Cursor with the first-contribution skill, starting from this issue.
