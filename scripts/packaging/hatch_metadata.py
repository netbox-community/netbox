"""Hatchling metadata hook: derive a PEP 440 version from netbox/release.yaml.

NetBox stores the release version and any pre-release designation (for example
"beta1") separately in netbox/release.yaml. This hook combines them into a
canonical PEP 440 version so wheels publish correctly, including pre-releases.
"""

import re
from pathlib import Path

from packaging.version import Version

try:
    from hatchling.metadata.plugin.interface import MetadataHookInterface
except ModuleNotFoundError:
    # hatchling is only installed inside the isolated build environment. Fall back
    # so this module (and compute_version) remains importable for unit testing.
    MetadataHookInterface = object


def compute_version(version, designation):
    """Return a canonical PEP 440 version from a version and optional designation."""
    raw = f"{version}{designation}" if designation else version
    return str(Version(raw))


def _read_release_field(text, field):
    match = re.search(rf'^{field}:\s*"?([^"\n]+?)"?\s*$', text, re.MULTILINE)
    return match.group(1).strip() if match else None


def read_requirements(text):
    """Parse a pinned requirements.txt body into PEP 508 dependency specifiers.

    Assumes NetBox's flat "package==version" format (one top-level pin per line).
    Blank lines, comments, and pip option lines (starting with "-") are skipped.
    """
    dependencies = []
    for raw_line in text.splitlines():
        line = raw_line.split('#', 1)[0].strip()
        if not line or line.startswith('-'):
            continue
        dependencies.append(line)
    return dependencies


class NetBoxMetadataHook(MetadataHookInterface):
    def update(self, metadata):
        root = Path(self.root)

        # Version: derived from release.yaml (version + optional designation).
        release_path = root / 'netbox' / 'release.yaml'
        text = release_path.read_text()
        version = _read_release_field(text, 'version')
        if not version:
            raise ValueError(f"Unable to read 'version' from {release_path}")
        designation = _read_release_field(text, 'designation')
        metadata['version'] = compute_version(version, designation)

        # Dependencies: requirements.txt is the single pinned source of truth, so the
        # published wheel's Requires-Dist matches the tested pins, not loose ranges.
        requirements_path = root / 'requirements.txt'
        metadata['dependencies'] = read_requirements(requirements_path.read_text())
