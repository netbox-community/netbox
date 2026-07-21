#!/usr/bin/env python3
"""Verify a built sdist ships only the intended configuration templates.

The sdist is a published artifact in its own right. It must contain the two tracked
configuration templates and must NOT contain a live configuration.py (which holds
SECRET_KEY and database credentials), any other local configuration*.py variant, or
any ldap_config*.py (which holds LDAP bind credentials). The wheel guard alone is not
enough: a wheel rebuilt from the sdist re-applies the wheel excludes, so it can come
out clean even when the sdist itself leaks a file.
"""

import sys
import tarfile
from pathlib import PurePosixPath

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


def main(argv):
    if len(argv) != 2:
        print('usage: verify_sdist_contents.py <sdist>')
        return 2
    found = configuration_members(argv[1])
    missing = sorted(ALLOWED - found)
    unexpected = sorted(found - ALLOWED)
    if missing or unexpected:
        print('Sdist configuration files are not as expected:')
        if missing:
            print(f'  - missing templates: {missing}')
        if unexpected:
            print(f'  - unexpected (possible secret leak): {unexpected}')
        return 1
    print(f'OK: sdist ships only the {len(ALLOWED)} configuration templates')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
