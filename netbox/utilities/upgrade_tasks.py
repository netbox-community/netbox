"""Implementation helpers for the `upgrade` management command.

The command runs the NetBox application-level tasks that prepare the database and
static assets after the package and configuration are already in place - for both a
fresh installation and an upgrade. It does not perform host or bootstrap work
(creating the virtual environment, installing packages, configuring services); that
stays in upgrade.sh and the documented pip steps.
"""

import os
import subprocess

from django.conf import settings
from django.core.management import call_command

__all__ = ('add_upgrade_arguments', 'run_upgrade_tasks')


def add_upgrade_arguments(parser):
    parser.add_argument('--no-input', action='store_true', dest='no_input',
                        help="Do not prompt for user input.")
    parser.add_argument('--readonly', action='store_true', dest='readonly',
                        help="Skip all tasks that modify the database or filesystem "
                             "(no migrations, no static collection).")
    parser.add_argument('--skip-migrations', action='store_true', dest='skip_migrations',
                        help="Skip applying database migrations.")
    parser.add_argument('--skip-static', action='store_true', dest='skip_static',
                        help="Skip collecting static files.")
    parser.add_argument('--skip-reindex', action='store_true', dest='skip_reindex',
                        help="Skip rebuilding the search index.")
    parser.add_argument('--build-docs', action='store_true', dest='build_docs',
                        help="Build the local documentation (requires the documentation source tree).")


def _docs_source_root():
    # mkdocs.yml sits beside the application root (one level above BASE_DIR in a checkout);
    # a wheel install has no documentation sources, so this returns None there.
    candidate = os.path.dirname(settings.BASE_DIR)
    return candidate if os.path.isfile(os.path.join(candidate, 'mkdocs.yml')) else None


def run_upgrade_tasks(command, *, no_input=False, readonly=False,
                      skip_migrations=False, skip_static=False, skip_reindex=False,
                      build_docs=False):
    out, style = command.stdout, command.style
    out.write(style.SUCCESS("Running NetBox upgrade tasks..."))

    # Database migrations (writes to the database)
    if skip_migrations or readonly:
        out.write("Skipping database migrations.")
    else:
        out.write("Applying database migrations...")
        call_command('migrate', interactive=not no_input, stdout=out)

    # Missing cable paths (writes to the database)
    if not readonly:
        out.write("Checking for missing cable paths...")
        call_command('trace_paths', no_input=no_input, stdout=out)

    # Documentation (filesystem; needs the documentation source tree)
    if readonly and build_docs:
        out.write("Skipping documentation build.")
    elif build_docs:
        docs_root = _docs_source_root()
        if docs_root is None:
            out.write(style.WARNING("Skipping documentation build (documentation source tree not found)."))
        else:
            out.write("Building documentation...")
            subprocess.run(['zensical', 'build'], cwd=docs_root, check=True)

    # Static files (filesystem)
    if skip_static or readonly:
        out.write("Skipping static file collection.")
    else:
        out.write("Collecting static files...")
        call_command('collectstatic', interactive=not no_input, stdout=out)

    # Stale content types (writes to the database)
    if not readonly:
        out.write("Removing stale content types...")
        call_command('remove_stale_contenttypes', interactive=not no_input, stdout=out)

    # Search index (writes to the database)
    if skip_reindex or readonly:
        out.write("Skipping search index rebuild.")
    else:
        out.write("Rebuilding the search index (lazily)...")
        call_command('reindex', lazy=True, stdout=out)

    # Expired sessions (writes to the database)
    if not readonly:
        out.write("Clearing expired sessions...")
        call_command('clearsessions', stdout=out)

    out.write(style.SUCCESS("Finished NetBox upgrade tasks."))
