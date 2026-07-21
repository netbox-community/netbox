"""`netbox setup`: create the local configuration files for a pip-installed NetBox instance.

Runs before Django or a local configuration exists (dispatched from the `netbox` console
script, netbox.cli). Scaffolds conf/__init__.py and conf/configuration.py (copied verbatim
from the bundled configuration_example.py template) and an empty local_requirements.txt,
then copies the bundled deployment examples (gunicorn, systemd units, nginx, apache, uwsgi,
netbox.env) unmodified into <target>/contrib/. Nothing is generated or rewritten; adapting
and installing the examples (paths, systemd, the web server) remains the administrator's
job. Existing files are never overwritten.
"""

import argparse
import sys
from importlib.resources import files
from pathlib import Path


def _bundled_data_dir():
    return files('netbox') / '_data'


def _config_template():
    return files('netbox') / 'configuration_example.py'


def _contrib_dir():
    return files('netbox') / '_data' / 'contrib'


def _write(destination, data):
    if destination.exists():
        print(f'Skipping existing {destination}')
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    print(f'Wrote {destination}')
    return True


def scaffold_instance(target):
    target = Path(target)
    conf = target / 'conf'
    items = [
        (conf / '__init__.py', b''),
        (conf / 'configuration.py', _config_template().read_bytes()),
        # An empty local_requirements.txt makes the optional plugin step discoverable and
        # the documented "pip install -r local_requirements.txt" safe.
        (target / 'local_requirements.txt', b''),
        # Bundled deployment examples, copied byte-verbatim; adapting them is the admin's job.
        # is_file() skips __pycache__: pip's post-install bytecode compilation of gunicorn.py
        # (the only .py file among the examples) leaves one alongside the real files.
        *(
            (target / 'contrib' / example.name, example.read_bytes())
            for example in sorted(_contrib_dir().iterdir(), key=lambda entry: entry.name)
            if example.is_file()
        ),
    ]
    return [str(destination) for destination, data in items if _write(destination, data)]


def main(argv=None, *, prog='netbox setup'):
    parser = argparse.ArgumentParser(
        prog=prog,
        description=(
            'Create the local configuration files for a pip-installed NetBox instance '
            '(conf/configuration.py copied verbatim from the bundled template, plus an empty '
            'local_requirements.txt), and copy the bundled deployment examples (gunicorn, '
            'systemd units, nginx, apache, uwsgi, netbox.env) unmodified into '
            "<target>/contrib/. Nothing is generated or rewritten; adapting and installing "
            "the examples is the administrator's job. Existing files are never overwritten."
        ),
    )
    parser.add_argument('--target', default='/opt/netbox', help='NetBox instance root (NETBOX_ROOT).')
    args = parser.parse_args(argv)

    if not _bundled_data_dir().is_dir():
        print(
            f'{prog}: this NetBox installation does not include the bundled package data. '
            'This command is available only from the installed netbox package (pip/wheel); '
            'for an archive or Git installation, follow the standard installation guide instead.',
            file=sys.stderr,
        )
        return 1
    if not Path(args.target).is_absolute():
        parser.error(f"--target must be an absolute path (got '{args.target}')")

    scaffold_instance(args.target)
    return 0
