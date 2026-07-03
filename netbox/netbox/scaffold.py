"""`netbox setup`: scaffold a pip-installed NetBox instance root.

This helper intentionally avoids importing Django or NetBox settings so it can run before a
local configuration exists. Dispatched from the `netbox` console script (netbox.cli), it copies
bundled example deployment files into place - adapting the canonical systemd units for a pip
install (EnvironmentFile, no --pythonpath, console-script rqworker) and rewriting the
instance-root path to the chosen target - scaffolds the conf/ package, and creates an empty
local_requirements.txt. conf/configuration.py, conf/__init__.py, local_requirements.txt, and
netbox.env are never overwritten once they exist.
"""

import argparse
import sys
from importlib.resources import files
from pathlib import Path

# bundled example name -> placement ('target' = instance root, 'systemd' = systemd dir)
_PLACEMENT = {
    'gunicorn.py': 'target',
    'nginx.conf': 'target',
    'apache.conf': 'target',
    'netbox.env': 'target',
    'netbox.service': 'systemd',
    'netbox-rq.service': 'systemd',
}

# Functional adaptations applied to the bundled CANONICAL contrib files for a pip install,
# before the instance-root rendering below. nginx.conf and apache.conf need no rules because
# _render() already collapses the source-layout static path. test_scaffold pins every
# anchor against contrib/, so an upstream contrib edit fails CI rather than `netbox setup`.
_PIP_TRANSFORMS = {
    'netbox.service': (
        # Optional per-instance overrides (NETBOX_ROOT) for pip installs.
        (
            'PIDFile=/var/tmp/netbox.pid\n',
            'PIDFile=/var/tmp/netbox.pid\nEnvironmentFile=-/opt/netbox/netbox.env\n',
        ),
        # The venv provides the import path; a stale source tree must not shadow the package.
        (' --pythonpath /opt/netbox/netbox', ''),
    ),
    'netbox-rq.service': (
        (
            'Group=netbox\n',
            'Group=netbox\nEnvironmentFile=-/opt/netbox/netbox.env\n',
        ),
        # The console script replaces manage.py under pip.
        (
            'ExecStart=/opt/netbox/venv/bin/python3 /opt/netbox/netbox/manage.py rqworker high default low\n',
            'ExecStart=/opt/netbox/venv/bin/netbox rqworker high default low\n',
        ),
    ),
}


def _examples_dir():
    return files('netbox') / '_data' / 'examples'


def _config_template():
    return files('netbox') / 'configuration_example.py'


def _render(text, target):
    """Rewrite the canonical /opt/netbox instance-root paths in a bundled template to target.

    Templates use /opt/netbox as the instance root, and /opt/netbox/netbox/... for the
    source-layout paths in configuration_example.py. Rewrite both, longest prefix first, so the
    config example collapses to the pip defaults (<target>/<name>). For the default target this
    is a no-op for the service/web files.
    """
    # Rewrite to a unique placeholder first, then to target, so a target that itself contains
    # /opt/netbox (e.g. /opt/netbox-prod) is not double-rewritten.
    marker = '\x00NETBOX_ROOT\x00'
    text = text.replace('/opt/netbox/netbox/', f'{marker}/').replace('/opt/netbox', marker)
    return text.replace(marker, str(target))


def _write(destination, data, *, force, written):
    if destination.exists() and not force:
        print(f"Skipping existing {destination}")
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    written.append(str(destination))
    print(f"Wrote {destination}")


def _apply_pip_transforms(name, text):
    """Adapt a bundled canonical contrib file for a pip install; fail loudly on a stale rule."""
    for old, new in _PIP_TRANSFORMS.get(name, ()):
        if old not in text:
            raise RuntimeError(f'{name}: expected contrib template anchor not found: {old!r}')
        text = text.replace(old, new)
    return text


def _write_rendered(destination, source, target, *, force, written):
    text = _apply_pip_transforms(destination.name, source.read_bytes().decode('utf-8'))
    rendered = _render(text, target).encode('utf-8')
    _write(destination, rendered, force=force, written=written)


def scaffold_instance(target, systemd_dir, *, force=False):
    target = Path(target)
    systemd_dir = Path(systemd_dir)
    root = str(target)
    examples = _examples_dir()
    written = []

    for name, placement in _PLACEMENT.items():
        destination = (target if placement == 'target' else systemd_dir) / name
        # netbox.env is user-owned once created (like local_requirements.txt); --force skips it
        file_force = force and name != 'netbox.env'
        _write_rendered(destination, examples / name, root, force=file_force, written=written)

    # Scaffold the conf/ package. configuration.py is never clobbered, and __init__.py is
    # create-if-missing: once it exists it is user-owned configuration package state.
    conf = target / 'conf'
    _write(conf / '__init__.py', b'', force=False, written=written)
    config = conf / 'configuration.py'
    if config.exists():
        print(f"Skipping existing {config}")
    else:
        _write_rendered(config, _config_template(), root, force=force, written=written)

    # An empty local_requirements.txt makes the optional plugin/package step discoverable and
    # the documented "pip install -r local_requirements.txt" safe. force=False even under --force
    # so a re-run never erases a user's plugin requirements.
    _write(target / 'local_requirements.txt', b'', force=False, written=written)

    return written


def main(argv=None, *, prog='netbox setup'):
    parser = argparse.ArgumentParser(
        prog=prog,
        description="Scaffold local deployment files for a pip-installed NetBox instance "
                    "(conf/, gunicorn.py, netbox.env, service and web server examples, "
                    "local_requirements.txt).",
    )
    parser.add_argument('--target', default='/opt/netbox', help="NetBox instance root (NETBOX_ROOT).")
    parser.add_argument('--systemd-dir', default='/etc/systemd/system', help="Directory for the systemd unit files.")
    parser.add_argument('--force', action='store_true',
                        help="Overwrite generated deployment files. Never overwrite conf/__init__.py, "
                             "conf/configuration.py, local_requirements.txt, or netbox.env once they exist.")
    args = parser.parse_args(argv)

    if not _examples_dir().is_dir():
        print(
            f'{prog}: the bundled deployment examples are not present in this installation. '
            'This command is available only from the installed netbox package (pip/wheel); '
            'for an archive or Git installation, follow the standard installation guide instead.',
            file=sys.stderr,
        )
        return 1

    for argument, value in (('--target', args.target), ('--systemd-dir', args.systemd_dir)):
        if not Path(value).is_absolute():
            parser.error(f"{argument} must be an absolute path (got '{value}')")

    scaffold_instance(args.target, args.systemd_dir, force=args.force)
    return 0
