Plan approved by Jimmy Ungerman in Grok Bot.

# Remove deprecated `num_workers` from `cycle_spin`

## Scope

Remove every live trace of the deprecated parameter `num_workers` on `skimage.restoration.cycle_spin` (subpackage: **restoration**), scheduled for version 0.28 in `TODO.txt`. Callers use the keyword-only parameter `workers`, which has been the replacement since 0.26 (`start_version="0.26"`, `stop_version="0.28"` on `@deprecate_parameter`).

The implementation lives in `src/_skimage2/restoration/_cycle_spin.py`. `src/skimage/restoration/_cycle_spin.py` re-exports that function. `src/skimage2/restoration` forwards the restoration namespace and has no copy of the function.

Search already run: `num_workers` across `src`, `tests`, `doc`, and `TODO.txt`. Hits are only the files listed below, plus the historical 0.26 release note.

Resulting signature:

```python
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

`workers` stays keyword-only. `func_kw` stays positional-or-keyword and moves into the slot `num_workers` occupies today.

## Files

### `src/_skimage2`

- `src/_skimage2/restoration/_cycle_spin.py` — Drop the `@deprecate_parameter(deprecated_name="num_workers", new_name="workers", ...)` decorator, drop `num_workers=DEPRECATED` from the signature, and drop the now-unused `deprecate_parameter` and `DEPRECATED` imports. Keep `warn` and `utils.channel_as_last_axis`. The source docstring never names `num_workers` (the decorator injects an "Other Parameters" entry at runtime via `modify_docstring=True`), so the docstring body stays as written. Rules: `20-deprecations.mdc` checklist items 1–4; `00-project-map.mdc` (implementation lives in `_skimage2`).

### `src/skimage`

- No edit. `src/skimage/restoration/_cycle_spin.py` re-exports `cycle_spin`. `src/skimage/restoration/__init__.pyi` keeps the public name `cycle_spin` and does not spell the signature. Rule: `00-project-map.mdc` (v1 tree is a shim).

### `src/skimage2`

- No edit. `src/skimage2/restoration/__init__.py` forwards `__getattr__`, `__dir__`, and `__all__` to `_skimage2.restoration`. Rule: `00-project-map.mdc` (namespace wiring only).

### `tests/skimage`

- `tests/skimage/restoration/test_denoise.py` — Delete `test_cycle_spinner_deprecate_num_workers` (the `pytest.mark.parametrize("num_workers", ...)` test, its `xfail_without_pywt` and `filterwarnings` decorators, and the `pytest.warns(FutureWarning, match=".*`num_workers` is deprecated")` block). Delete the `assert_stacklevel` import, which this test is the only user of. Leave `test_cycle_spinning_workers` and `test_cycle_spinning_multichannel`. Rules: `20-deprecations.mdc` item 5; `30-testing.mdc` (both trees; warnings are errors).
- `tests/skimage/test_migration.py` — Update the `SKIMAGE_API` snapshot. `test_public_skimage_api` records `inspect.signature`, which follows `__wrapped__` to the real signature and renders `DEPRECATED` as `<DEPRECATED>`. Replace

  `skimage.restoration:cycle_spin(x, func, max_shifts, shift_steps=1, num_workers=<DEPRECATED>, func_kw=None, *, workers=None, channel_axis=None)`

  with

  `skimage.restoration:cycle_spin(x, func, max_shifts, shift_steps=1, func_kw=None, *, workers=None, channel_axis=None)`.

  Rules: `20-deprecations.mdc` item 6; `00-project-map.mdc` (public v1 signature snapshot).

### `tests/skimage2`

- `tests/skimage2/restoration/test_denoise.py` — Same deletion as the `tests/skimage` copy: remove `test_cycle_spinner_deprecate_num_workers` and the unused `assert_stacklevel` import. The two files differ only in import roots (`skimage` vs `_skimage2`). There is no `tests/skimage2` migration snapshot. Rules: `20-deprecations.mdc` item 5; `30-testing.mdc`.

### Docs

- `doc/examples/filters/plot_cycle_spinning.py` — No edit. It calls `cycle_spin` with keyword `func_kw` and `channel_axis` and does not pass `num_workers`. Rule: `20-deprecations.mdc` item 6 (`doc/examples` must not mention the old name for this function).
- `doc/source/release_notes/release_0.26.rst` — Leave unchanged. It records that 0.26 deprecated `num_workers` in favor of `workers`. The removal checklist grep is `src`, `tests`, and `doc/examples`, which excludes historical release notes.

### `TODO.txt`

- Delete the version 0.28 bullet "Remove all traces of deprecated parameter `num_workers` in `skimage.restoration.cycle_spin`." Leave the neighboring `num_threads` / `rolling_ball` bullet in place. Rule: `20-deprecations.mdc` item 7.

## Conventions applied

From `20-deprecations.mdc` (completing a deprecation):

1. Remove `@deprecate_parameter` in `src/_skimage2/restoration/_cycle_spin.py`.
2. Remove `num_workers` from the signature.
3. Remove unused `deprecate_parameter` and `DEPRECATED` imports. Keep `warn`.
4. Source docstring has no old-name sentence to delete. Removing the decorator also removes the runtime "Other Parameters" / `.. deprecated:: 0.26` block (`Deprecated in favor of workers`).
5. Remove `test_cycle_spinner_deprecate_num_workers` in both `tests/skimage/restoration/test_denoise.py` and `tests/skimage2/restoration/test_denoise.py`.
6. After the edit, `num_workers` must not remain under `src`, `tests`, or `doc/examples` for this function. The migration snapshot is part of that sweep.
7. Delete the matching `TODO.txt` item.
8. The pull request description (written later, by the engineer) gets a `release-note` block. Draft for that block, per `CONTRIBUTING.md`:

```release-note
Remove the deprecated parameter `num_workers` from `skimage.restoration.cycle_spin`.
Use the `workers` parameter instead.
```

From `00-project-map.mdc`: edit the `_skimage2` implementation; leave the `skimage` re-export and the `skimage2` namespace forwarder alone; update both restoration test trees. Public `__all__` entries stay, because the function stays public.

From `10-python-style.mdc`: this is a scheduled signature removal, so the deprecation-cycle rule applies and is already satisfied (warning since 0.26, removal at 0.28). No new gallery example. No dtype, RNG, or import-style cleanup beyond the unused names on the existing import line. The in-function example still calls `np.random.standard_normal` with the global generator; that example stays untouched.

From `30-testing.mdc`: warnings fail the suite, so the `FutureWarning` test has to go with the parameter. `assert_stacklevel` is removed with it so ruff stays clean. Existing worker coverage stays.

From `40-boundaries.mdc`: no new dependency, no vendored edit, no new import from `skimage` or `skimage2` into `_skimage2`, no network.

From `50-ai-use-policy.mdc`: the code edit, once approved, is mechanical. It goes in its own commit with an `Assisted-by:` trailer. The engineer chooses any extra tests and writes the final PR text. This plan file is committed later with that change, not in this step.

Upstream `doc/source/development/deprecations.md` agrees: a renamed keyword needs a cycle, and warnings stay for two releases (0.26 introduced, 0.28 removes). It points new deprecations at `release_dev.rst`; completing one is documented with the `release-note` block in `20-deprecations.mdc` and `CONTRIBUTING.md`.

## Test approach

No new algorithmic tests. Behavior of `workers` is already covered by `test_cycle_spinning_workers` (`workers=1`, `workers=4`, `workers=None`) and `test_cycle_spinning_multichannel` in both trees.

Checks that belong with the removal:

- `tests/skimage/test_migration.py::test_public_skimage_api` fails until the snapshot matches the signature above. That is the regression check that `num_workers` left the public signature.
- `grep -rn "num_workers" src tests doc/examples TODO.txt` returns no hits.
- A repo-wide grep still hits `doc/source/release_notes/release_0.26.rst` only.

Run, after the edit exists:

```bash
spin test -- tests/skimage/restoration tests/skimage2/restoration tests/skimage/test_migration.py
```

`test_migration.py` sits outside `tests/skimage/restoration/`, so the restoration-only path would miss the snapshot. Before push (later stage): `pre-commit run --files <changed>`, `python tools/acme/check_boundaries.py`, and `spin test --test-modified --doctest`.

Edge cases to offer the engineer at stage 4 (the engineer picks; none are written in this step):

- Passing `num_workers=` raises `TypeError`. Reason: proves the deprecated keyword is gone, which is the ticket.
- A positional `func_kw` dict in the fifth argument still reaches `func`. Reason: deleting `num_workers` shifts that parameter forward by one.
- `workers=1`, `workers=None`, and `workers` omitted still match today's results. Reason: the replacement parameter and its default must keep the dask / serial paths working. Already covered if the existing worker test is left in place.

## Risks

- Positional calls that passed `num_workers` as the fifth argument will bind that value to `func_kw` after the removal. Calls that also passed `func_kw` positionally as the sixth argument will raise `TypeError`. Keyword `workers=` is unchanged. This is the 0.28 removal the decorator already announced.
- Rendered docs lose the injected "Other Parameters" entry for `num_workers` because that text is added by the decorator, not stored in the source docstring.
- Leaving the `assert_stacklevel` import in either `test_denoise.py` fails ruff under pre-commit.
- The 0.26 release note still contains the string `num_workers`. Deleting it would rewrite history. Leave it.
- `rolling_ball`'s `num_threads` deprecation is a separate 0.28 TODO item. This change does not touch `_rolling_ball.py` or its tests.
- The cycle-spin doctest uses the global NumPy RNG and `# doctest: +IGNORE_WARNINGS`. Changing that example is outside this ticket.

## Out of scope

- Code edits, commits, pushes, and pull requests. Those wait until this plan is approved.
- `deprecate_parameter` / `DEPRECATED` themselves in `_skimage2._shared.utils`.
- The `num_threads` removal on `skimage.restoration.rolling_ball`.
