#!/usr/bin/env python3
"""Verify a built wheel's metadata matches the repository's declared inputs.

Checks:
  1. Version equals the PEP 440 version computed from netbox/release.yaml, reusing the
     same compute_version the hatchling metadata hook uses at build time.
  2. Core Requires-Dist entries (those without an "extra ==" marker) match
     requirements.txt exactly, so the published wheel pins the tested dependency set.
  3. Provides-Extra equals the expected set of optional-dependency groups.
  4. Each aggregate extra equals the union of its component extras, comparing the wheel
     metadata against itself (immune to backend specifier normalization). pyproject.toml
     duplicates these requirement strings literally; this catches drift, for example a
     plugin pin bumped in one place only. Aggregates must not reference netbox itself,
     which would defeat this guard.
"""

import importlib.util
import re
import sys
import zipfile
from collections import defaultdict
from email.parser import Parser
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

# Every optional-dependency group in pyproject.toml, as normalized (PEP 685) extra names.
EXPECTED_EXTRAS = frozenset({
    'branching',
    'custom-objects',
    'dev',
    'git',
    'ldap',
    'recommended-plugins',
    'remote-auth',
    's3',
    'saml2',
    'sentry',
    'swift',
})

# Aggregate extra -> the component extras whose entries it must equal the union of.
AGGREGATE_EXTRAS = {
    'remote-auth': ('ldap', 'saml2'),
    'recommended-plugins': ('branching', 'custom-objects'),
}

# hatchling 1.30 writes extra markers with single quotes; other tools use double quotes.
EXTRA_MARKER = re.compile(r'\bextra\s*==\s*["\']([^"\']+)["\']')


def read_metadata(wheel_path):
    with zipfile.ZipFile(wheel_path) as archive:
        name = next(n for n in archive.namelist() if n.endswith('.dist-info/METADATA'))
        return Parser().parsestr(archive.read(name).decode())


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


def normalize(requirement):
    return requirement.strip().lower().replace(' ', '')


def split_requires(metadata):
    """Split Requires-Dist entries into core requirements and a per-extra mapping."""
    core = set()
    by_extra = defaultdict(set)
    for entry in metadata.get_all('Requires-Dist') or []:
        requirement, _, marker = entry.partition(';')
        match = EXTRA_MARKER.search(marker)
        if match:
            by_extra[match.group(1)].add(normalize(requirement))
        else:
            core.add(normalize(entry))
    return core, by_extra


def check_version(metadata, root, hatch_metadata):
    release_text = (root / 'netbox' / 'release.yaml').read_text()
    version = hatch_metadata._read_release_field(release_text, 'version')
    if not version:
        return ['unable to read version from netbox/release.yaml']
    designation = hatch_metadata._read_release_field(release_text, 'designation')
    expected = hatch_metadata.compute_version(version, designation)
    if metadata['Version'] != expected:
        return [f'version mismatch: wheel has {metadata["Version"]}, release.yaml computes {expected}']
    return []


def _diff_errors(expected, actual, label):
    """Build 'missing'/'unexpected' error messages for the set difference of expected vs actual."""
    errors = []
    if missing := sorted(expected - actual):
        errors.append(f'{label} missing from wheel: {missing}')
    if unexpected := sorted(actual - expected):
        errors.append(f'unexpected {label} in wheel: {unexpected}')
    return errors


def check_core_requires(core, root, hatch_metadata):
    # Parse with the hook's own parser so the verifier cannot drift from the build.
    pins = hatch_metadata.read_requirements((root / 'requirements.txt').read_text())
    return _diff_errors({normalize(pin) for pin in pins}, core, 'core requirements')


def check_extras(metadata, by_extra):
    provided = frozenset(metadata.get_all('Provides-Extra') or [])
    errors = _diff_errors(EXPECTED_EXTRAS, provided, 'extras')
    for aggregate, components in AGGREGATE_EXTRAS.items():
        expected = set().union(*(by_extra[component] for component in components))
        actual = by_extra[aggregate]
        if actual != expected:
            errors.append(
                f'extra [{aggregate}] must equal the union of {list(components)}: '
                f'missing {sorted(expected - actual)}, unexpected {sorted(actual - expected)}'
            )
        if self_refs := sorted(r for r in actual if canonicalize_name(Requirement(r).name) == 'netbox'):
            errors.append(f'extra [{aggregate}] must not reference netbox itself: {self_refs}')
    return errors


def main(argv):
    if len(argv) != 2:
        print('usage: verify_wheel_metadata.py <wheel>')
        return 2
    root = Path(__file__).resolve().parent.parent
    hatch_metadata = load_hatch_metadata()
    metadata = read_metadata(argv[1])
    core, by_extra = split_requires(metadata)
    errors = [
        *check_version(metadata, root, hatch_metadata),
        *check_core_requires(core, root, hatch_metadata),
        *check_extras(metadata, by_extra),
    ]
    if errors:
        print('Wheel metadata does not match the repository:')
        for error in errors:
            print(f'  - {error}')
        return 1
    print(f'OK: wheel {metadata["Version"]} matches release.yaml, requirements.txt, and expected extras')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
