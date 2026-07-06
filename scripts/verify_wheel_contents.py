#!/usr/bin/env python3
"""Verify a built wheel ships the required bundled data and only the intended configuration templates.

The wheel must contain the tracked configuration templates and must NOT contain a
live configuration.py (which holds SECRET_KEY and database credentials), any other
local configuration*.py variant, or any ldap_config*.py (which holds LDAP bind
credentials). This guards against a dirty or manual build leaking secrets into a
published artifact. The wheel must also ship the runtime-critical bundled data
(release metadata, templates, translations, static assets, documentation sources,
deployment examples), so a broken build fails here with a precise message instead of
at smoke-test time. main() also cross-checks pyproject.toml's wheel force-include
table against REQUIRED_FILES/REQUIRED_PREFIXES/ALLOWED, so an addition there without
matching verifier coverage fails too.
"""

import sys
import tomllib
import zipfile
from pathlib import Path, PurePosixPath

# The scan covers the entire wheel; only these two tracked templates (at netbox/<name> after the
# wheel `sources = ["netbox"]` strip) are allowed to ship.
ALLOWED = {
    'netbox/configuration_example.py',
    'netbox/configuration_testing.py',
}

# Runtime-critical bundled data; mirrors the force-include table in pyproject.toml.
# Hand-maintained, not derived: main() cross-checks pyproject.toml's wheel
# force-include table against these sets (plus ALLOWED) in the other direction, so a
# force-include added there without matching coverage here also fails.
REQUIRED_FILES = {
    'netbox/_data/contrib/apache.conf',
    'netbox/_data/contrib/gunicorn.py',
    'netbox/_data/contrib/netbox-rq.service',
    'netbox/_data/contrib/netbox.env',
    'netbox/_data/contrib/netbox.service',
    'netbox/_data/contrib/nginx.conf',
    'netbox/_data/contrib/uwsgi.ini',
    'netbox/_data/mkdocs.yml',
    'netbox/_data/release.yaml',
}
REQUIRED_PREFIXES = (
    'netbox/_data/docs/',
    'netbox/_data/project-static/dist/',
    'netbox/_data/project-static/img/',
    'netbox/_data/project-static/js/',
    'netbox/_data/templates/',
    'netbox/_data/translations/',
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


def uncovered_force_includes(pyproject_path):
    """Return wheel force-include destinations in pyproject.toml not covered by this verifier.

    REQUIRED_FILES/REQUIRED_PREFIXES/ALLOWED stay hand-owned and independent of pyproject.toml
    (a full derivation would let a deleted force-include line shrink the expectations with it
    and go silently green), so this only catches drift in one direction: a force-include added
    to pyproject.toml without matching verifier coverage. A deleted force-include line still
    fails the REQUIRED_FILES/REQUIRED_PREFIXES checks in missing_runtime_data().
    """
    with open(pyproject_path, 'rb') as handle:
        pyproject = tomllib.load(handle)
    force_include = pyproject['tool']['hatch']['build']['targets']['wheel']['force-include']
    uncovered = []
    for destination in force_include.values():
        # The wheel's `sources = ["netbox"]` setting strips one leading "netbox/" segment from
        # every path, including these force-include destinations.
        stripped = destination.removeprefix('netbox/')
        if stripped in REQUIRED_FILES or stripped in ALLOWED or f'{stripped}/' in REQUIRED_PREFIXES:
            continue
        uncovered.append(destination)
    return sorted(uncovered)


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
    pyproject_path = Path(__file__).resolve().parents[1] / 'pyproject.toml'
    uncovered = uncovered_force_includes(pyproject_path)
    if missing or unexpected or missing_data or uncovered:
        print('Wheel contents are not as expected:')
        if missing:
            print(f'  - missing templates: {missing}')
        if unexpected:
            print(f'  - unexpected (possible secret leak): {unexpected}')
        if missing_data:
            print(f'  - missing runtime data: {missing_data}')
        if uncovered:
            print(f'  - pyproject.toml force-includes not covered by this verifier: {uncovered}')
        return 1
    print(f'OK: wheel ships the required bundled data and only the {len(ALLOWED)} configuration templates')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
