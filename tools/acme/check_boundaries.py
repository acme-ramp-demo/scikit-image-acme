#!/usr/bin/env python
"""Acme boundary check: every third-party import in library code must be allowlisted.

The allowlist is built from ``pyproject.toml`` (runtime dependencies plus the
optional extras named in ``tools/acme/allowlist.toml``) plus a short list of
explicit extra entries. Anything else fails the check, with the file and line,
so a new dependency is a deliberate, human-approved change rather than a
surprise in CI.

Usage:
    python tools/acme/check_boundaries.py            # scan src/
    python tools/acme/check_boundaries.py FILE ...   # scan given files (pre-commit)
"""

import ast
import re
import sys
try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    import tomli as tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIRST_PARTY = {"_skimage2", "skimage", "skimage2"}

# Distribution name -> import name, where they differ.
IMPORT_NAMES = {"pillow": "PIL", "scikit-learn": "sklearn", "pyamg": "pyamg"}


def _req_name(req):
    """'scipy>=1.15; sys_platform != "x"' -> 'scipy'."""
    name = re.split(r"[<>=!~;\[ ]", req.strip(), maxsplit=1)[0].lower()
    return IMPORT_NAMES.get(name, name.replace("-", "_"))


def load_allowlist():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    policy = tomllib.loads((ROOT / "tools/acme/allowlist.toml").read_text())
    project = pyproject["project"]

    allowed = {_req_name(r) for r in project.get("dependencies", [])}
    extras = project.get("optional-dependencies", {})
    for extra in policy.get("allowed_extras", []):
        allowed |= {_req_name(r) for r in extras.get(extra, []) if "[" not in r}
    allowed |= set(policy.get("extra_imports", []))
    return allowed


def third_party_imports(path):
    """Yield (lineno, top-level module) for absolute, non-stdlib imports."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names = [node.module]
        else:
            continue
        for name in names:
            top = name.split(".")[0]
            if top in FIRST_PARTY or top in sys.stdlib_module_names:
                continue
            yield node.lineno, top


def main(argv):
    allowed = load_allowlist()
    if argv:
        files = [Path(p) for p in argv if p.endswith(".py")]
    else:
        files = [
            p for p in (ROOT / "src").rglob("*.py") if not {"_vendored", "_build_utils"} & set(p.parts)
        ]

    violations = []
    for path in files:
        if not path.is_absolute():
            path = ROOT / path
        if "src" not in path.parts or {"_vendored", "_build_utils"} & set(path.parts):
            continue
        for lineno, module in third_party_imports(path):
            if module.lower() not in {a.lower() for a in allowed}:
                violations.append((path.relative_to(ROOT), lineno, module))

    if violations:
        print("Boundary check FAILED: imports outside the dependency allowlist\n")
        for path, lineno, module in violations:
            print(f"  {path}:{lineno}  imports '{module}'")
        print(
            "\nTo use a new package, propose it for approval (DevOps gate in Grok Bot)."
            "\nDo not suppress this check."
        )
        return 1

    print(f"Boundary check passed ({len(files)} files, {len(allowed)} allowed packages).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
