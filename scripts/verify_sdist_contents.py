#!/usr/bin/env python3
"""Verify a built sdist ships only the intended configuration templates.

The sdist is a published artifact in its own right. It must contain the two tracked
configuration templates and must NOT contain a live configuration.py (which holds
SECRET_KEY and database credentials), any other local configuration*.py variant, or
any ldap_config*.py (which holds LDAP bind credentials). The wheel guard alone is not
enough: a wheel rebuilt from the sdist re-applies the wheel excludes, so it can come
out clean even when the sdist itself leaks a file.

The sdist must also declare the Core Metadata version pinned for the sdist target in
pyproject.toml, so a backend default change cannot silently alter the artifact format.
"""

import sys
import tarfile
import tomllib
from email.parser import Parser
from pathlib import Path, PurePosixPath

# Allowed members, relative to the sdist's netbox-<version>/ root directory. The sdist
# keeps the full repository layout (no `sources` strip), unlike the wheel.
ALLOWED = {
    'netbox/netbox/configuration_example.py',
    'netbox/netbox/configuration_testing.py',
}


def configuration_members(sdist_path):
    """Return the set of configuration*.py members anywhere inside the sdist."""
    with tarfile.open(sdist_path) as archive:
        names = archive.getnames()
    members = set()
    for name in names:
        path = PurePosixPath(name)
        if path.suffix == '.py' and (path.name.startswith('configuration') or path.name.startswith('ldap_config')):
            # Strip the leading netbox-<version>/ directory for a stable comparison.
            members.add(str(PurePosixPath(*path.parts[1:])))
    return members


def expected_metadata_version():
    """Return the core-metadata-version pinned for the sdist target, or None."""
    pyproject = tomllib.loads((Path(__file__).resolve().parent.parent / 'pyproject.toml').read_text())
    return pyproject['tool']['hatch']['build']['targets'].get('sdist', {}).get('core-metadata-version')


def read_pkg_info(sdist_path):
    """Return the sdist's parsed top-level PKG-INFO, or None when the file is absent."""
    with tarfile.open(sdist_path) as archive:
        for member in archive.getmembers():
            if PurePosixPath(member.name).parts[1:] == ('PKG-INFO',):
                return Parser().parsestr(archive.extractfile(member).read().decode())
    return None


def main(argv):
    if len(argv) != 2:
        print('usage: verify_sdist_contents.py <sdist>')
        return 2
    errors = []
    found = configuration_members(argv[1])
    if missing := sorted(ALLOWED - found):
        errors.append(f'missing templates: {missing}')
    if unexpected := sorted(found - ALLOWED):
        errors.append(f'unexpected (possible secret leak): {unexpected}')
    expected = expected_metadata_version()
    if expected is None:
        errors.append('pyproject.toml does not pin core-metadata-version for the sdist target')
    elif (pkg_info := read_pkg_info(argv[1])) is None:
        errors.append('sdist is missing its top-level PKG-INFO')
    elif (actual := pkg_info['Metadata-Version']) is None:
        errors.append('sdist PKG-INFO does not declare Metadata-Version')
    elif actual != expected:
        errors.append(f'metadata version mismatch: sdist PKG-INFO has {actual}, pyproject.toml pins {expected}')
    if errors:
        print('Sdist contents are not as expected:')
        for error in errors:
            print(f'  - {error}')
        return 1
    print(f'OK: sdist ships only the {len(ALLOWED)} configuration templates and declares Metadata-Version {expected}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
