#!/usr/bin/env python3
"""Verify requirements.txt is consistent with base_requirements.txt.

Guards against dependency drift before publishing. The wheel sources its pinned
dependencies from requirements.txt, which must stay in sync with the maintainer
policy in base_requirements.txt (same package set, and every pin satisfies its
declared constraint).
"""

import importlib.util
import sys
from pathlib import Path

from packaging.requirements import Requirement


def load_hatch_metadata():
    """Load scripts/packaging/hatch_metadata.py by path.

    scripts/packaging is not a package (no __init__.py), and importing it by name would
    collide with the third-party packaging distribution, so load it from its file path.
    """
    path = Path(__file__).resolve().parent / 'packaging' / 'hatch_metadata.py'
    spec = importlib.util.spec_from_file_location('netbox_hatch_metadata', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse(path, hatch_metadata):
    reqs = {}
    for line in hatch_metadata.read_requirements(Path(path).read_text()):
        req = Requirement(line)
        reqs[req.name.lower().replace('_', '-')] = req
    return reqs


def check(base, pinned):
    errors = []
    only_base = sorted(set(base) - set(pinned))
    only_pinned = sorted(set(pinned) - set(base))
    if only_base:
        errors.append(f"In base_requirements.txt but not requirements.txt: {only_base}")
    if only_pinned:
        errors.append(f"In requirements.txt but not base_requirements.txt: {only_pinned}")
    for name in sorted(set(base) & set(pinned)):
        if base[name].extras != pinned[name].extras:
            errors.append(
                f"{name}: extras differ (base {sorted(base[name].extras)} vs "
                f"requirements.txt {sorted(pinned[name].extras)})"
            )
        spec = pinned[name].specifier
        if not spec or not all(s.operator == '==' for s in spec):
            errors.append(f"{name}: requirements.txt must pin exactly (got '{pinned[name]}')")
            continue
        version = next(iter(spec)).version
        if not base[name].specifier.contains(version, prereleases=True):
            errors.append(f"{name}: pinned {version} violates base constraint '{base[name].specifier}'")
    return errors


def main():
    root = Path(__file__).resolve().parent.parent
    hatch_metadata = load_hatch_metadata()
    errors = check(
        parse(root / 'base_requirements.txt', hatch_metadata),
        parse(root / 'requirements.txt', hatch_metadata),
    )
    if errors:
        print("Dependency drift detected:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("OK: requirements.txt is consistent with base_requirements.txt")
    return 0


if __name__ == '__main__':
    sys.exit(main())
