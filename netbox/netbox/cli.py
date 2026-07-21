"""Console entry point for pip-installed NetBox."""

import argparse
import os
import sys
from importlib.metadata import PackageNotFoundError, version

# Commands handled here must not require Django settings. These names are intentionally
# reserved by the console wrapper and are never dispatched to Django management commands.
# 'setup' is not listed: the early-dispatch branch in main() owns it and always returns
# before this tuple is consulted.
_RESERVED_COMMANDS = ('secret-key', 'version')

_EPILOG = """Any other command is dispatched to the Django management commands, which
require a valid NetBox configuration, e.g.:
  {prog} upgrade
  {prog} check
  {prog} createsuperuser

Run "{prog} help" (once configured) for the full management command listing."""


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


def _build_parser(prog):
    parser = argparse.ArgumentParser(
        prog=prog,
        description='NetBox command line interface.',
        epilog=_EPILOG.format(prog=prog),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(
        dest='command',
        title='pre-configuration commands (no NetBox configuration required)',
    )
    subparsers.add_parser(
        'version', help='Print the installed NetBox package version.',
        description='Print the installed NetBox package version.')
    subparsers.add_parser(
        'setup', add_help=False,
        help='Create the local configuration files for a pip-installed instance.')
    subparsers.add_parser(
        'secret-key', help='Generate a new 50-character SECRET_KEY value.',
        description='Generate a new 50-character SECRET_KEY value.')
    return parser


def main(argv=None):
    prog = _prog()
    args = list(sys.argv[1:] if argv is None else argv)

    # `setup` owns its own parser (netbox.scaffold); dispatch before the wrapper parser.
    if args and args[0] == 'setup':
        # Deferred so the command works before Django or a configuration exists.
        from netbox.scaffold import main as setup_main
        return setup_main(args[1:], prog=f'{prog} setup')

    if not args:
        _build_parser(prog).print_help()
        return 0

    if args[0] in _RESERVED_COMMANDS or args[0] in ('-h', '--help', '--version'):
        parser = _build_parser(prog)
        if args[0] == '--version':
            args = ['version', *args[1:]]
        try:
            options = parser.parse_args(args)
        except SystemExit as e:  # argparse already printed help (0) or an error (2)
            return int(e.code or 0)
        if options.command == 'version':
            _print_version()
        elif options.command == 'secret-key':
            # Deferred so the command works before Django or a configuration exists.
            from utilities.secret_key import generate_secret_key
            print(generate_secret_key())
        return 0

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netbox.settings')

    # Deferred on purpose: Django must not import until DJANGO_SETTINGS_MODULE is set.
    from django.core.management import execute_from_command_line

    execute_from_command_line([prog, *args])
    return 0
