"""Console entry point for pip-installed NetBox."""

import os
import sys
from importlib.metadata import PackageNotFoundError, version

# Commands handled here must not require Django settings. These names are intentionally
# reserved by the console wrapper and are never dispatched to Django management commands.
_HELP = """usage: {prog} <command> [options]

Pre-configuration commands (no NetBox configuration required):
  {prog} version         Print the installed NetBox package version.
  {prog} setup           Scaffold local deployment files for a pip-installed instance.
  {prog} secret-key      Generate a new 50-character SECRET_KEY value.

Any other command is dispatched to the Django management commands, which require a
valid NetBox configuration, e.g.:
  {prog} upgrade
  {prog} check
  {prog} createsuperuser

Run "{prog} setup --help" for scaffolding options, and "{prog} help" (once configured)
for the full management command listing."""


def _prog():
    if sys.argv and sys.argv[0]:
        name = os.path.basename(sys.argv[0])
        # `python -m netbox` executes __main__.py; show the user-facing name instead.
        if name != '__main__.py':
            return name
    return 'netbox'


def _print_version():
    try:
        print(version('netbox'))
    except PackageNotFoundError:  # pragma: no cover - only in a non-installed checkout
        print('unknown')


def _version(args, prog):
    if args in (['-h'], ['--help']):
        print(f'usage: {prog} version\n\nPrint the installed NetBox package version.')
        return 0
    if args:
        print(f'{prog} version: unexpected arguments: {" ".join(args)}', file=sys.stderr)
        return 2
    # Resolved before importing Django, so it works without configuration.
    _print_version()
    return 0


def _secret_key(args, prog):
    if args in (['-h'], ['--help']):
        print(f'usage: {prog} secret-key\n\nGenerate a new 50-character SECRET_KEY value.')
        return 0
    if args:
        print(f'{prog} secret-key: unexpected arguments: {" ".join(args)}', file=sys.stderr)
        return 2
    # Deferred so the command works before Django or a configuration exists.
    from utilities.secret_key import generate_secret_key
    print(generate_secret_key())
    return 0


def main(argv=None):
    prog = _prog()
    args = list(sys.argv[1:] if argv is None else argv)

    if not args or args[0] in ('-h', '--help'):
        print(_HELP.format(prog=prog))
        return 0

    if args[0] in ('version', '--version'):
        return _version(args[1:], prog)

    if args[0] == 'secret-key':
        return _secret_key(args[1:], prog)

    if args[0] == 'setup':
        # Deferred so the command works before Django or a configuration exists.
        from netbox.scaffold import main as setup_main
        return setup_main(args[1:], prog=f'{prog} setup')

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netbox.settings')

    # Deferred on purpose: Django must not import until DJANGO_SETTINGS_MODULE is set.
    from django.core.management import execute_from_command_line

    execute_from_command_line([prog, *args])
    return 0
