#!/usr/bin/env python3
"""Verify a built wheel ships the required bundled data and only the intended configuration templates.

The wheel must contain the tracked configuration templates and must NOT contain a
live configuration.py (which holds SECRET_KEY and database credentials), any other
local configuration*.py variant, or any ldap_config*.py (which holds LDAP bind
credentials). This guards against a dirty or manual build leaking secrets into a
published artifact. The wheel must also ship the runtime-critical bundled data
(release metadata, templates, translations, static assets, deployment examples), so
a broken build fails here with a precise message instead of at smoke-test time.
"""

import sys
import zipfile
from pathlib import PurePosixPath

# The scan covers the entire wheel; only these two tracked templates (at netbox/<name> after the
# wheel `sources = ["netbox"]` strip) are allowed to ship.
ALLOWED = {
    'netbox/configuration_example.py',
    'netbox/configuration_testing.py',
}

# Runtime-critical bundled data; mirrors the force-include table in pyproject.toml.
REQUIRED_FILES = {
    'netbox/_data/release.yaml',
    'netbox/_data/examples/gunicorn.py',
    'netbox/_data/examples/netbox.service',
    'netbox/_data/examples/netbox-rq.service',
    'netbox/_data/examples/nginx.conf',
    'netbox/_data/examples/apache.conf',
    'netbox/_data/examples/netbox.env',
}
REQUIRED_PREFIXES = (
    'netbox/_data/templates/',
    'netbox/_data/translations/',
    'netbox/_data/project-static/dist/',
    'netbox/_data/project-static/img/',
    'netbox/_data/project-static/js/',
)


def configuration_members(names):
    """Return the set of configuration*.py members anywhere inside the wheel."""
    members = set()
    for name in names:
        path = PurePosixPath(name)
        # Scan the whole wheel: any configuration*.py outside the two tracked templates, or any
        # ldap_config*.py at all, is a leak, wherever it sits in the archive.
        if path.suffix == '.py' and (path.name.startswith('configuration') or path.name.startswith('ldap_config')):
            members.add(name)
    return members


def missing_runtime_data(names):
    """Return the sorted list of required bundled files and prefixes absent from the wheel."""
    missing = sorted(REQUIRED_FILES - names)
    missing += [prefix for prefix in REQUIRED_PREFIXES if not any(name.startswith(prefix) for name in names)]
    return missing


def main(argv):
    if len(argv) != 2:
        print('usage: verify_wheel_contents.py <wheel>')
        return 2
    with zipfile.ZipFile(argv[1]) as archive:
        names = set(archive.namelist())
    found = configuration_members(names)
    missing = sorted(ALLOWED - found)
    unexpected = sorted(found - ALLOWED)
    missing_data = missing_runtime_data(names)
    if missing or unexpected or missing_data:
        print('Wheel contents are not as expected:')
        if missing:
            print(f'  - missing templates: {missing}')
        if unexpected:
            print(f'  - unexpected (possible secret leak): {unexpected}')
        if missing_data:
            print(f'  - missing runtime data: {missing_data}')
        return 1
    print(f'OK: wheel ships the required bundled data and only the {len(ALLOWED)} configuration templates')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
