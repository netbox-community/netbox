import logging

from django.apps import apps
from django.core.cache import cache
from django.core.checks import Error, Tags, register
from django.core.exceptions import ImproperlyConfigured
from django.db import DatabaseError, InterfaceError, NotSupportedError, OperationalError, connections
from django.db.models import Index, UniqueConstraint

__all__ = (
    'check_duplicate_indexes',
    'check_postgresql_version',
    'check_redis_version',
)

# The minimum major version of PostgreSQL required by NetBox. `SHOW server_version_num` reports the
# server version as a single integer of the form MMmmmm (e.g. 150004 for PostgreSQL 15.4), so the
# major version is scaled by 10000 when comparing against it.
POSTGRESQL_MIN_VERSION = 15
POSTGRESQL_VERSION_MULTIPLIER = 10000

logger = logging.getLogger('netbox.core.checks')


@register(Tags.models)
def check_duplicate_indexes(app_configs, **kwargs):
    """
    Check for an index which is redundant to a declared unique constraint.
    """
    errors = []

    for model in apps.get_models():
        if not (meta := getattr(model, "_meta", None)):
            continue

        index_fields = {
            tuple(index.fields) for index in getattr(meta, 'indexes', [])
            if isinstance(index, Index)
        }
        constraint_fields = {
            tuple(constraint.fields) for constraint in getattr(meta, 'constraints', [])
            if isinstance(constraint, UniqueConstraint)
        }

        # Find overlapping definitions
        if duplicated := index_fields & constraint_fields:
            for fields in duplicated:
                errors.append(
                    Error(
                        f"Model '{model.__name__}' defines the same field set {fields} in both `Meta.indexes` and "
                        f"`Meta.constraints`.",
                        obj=model,
                    )
                )

    return errors


@register(Tags.database)
def check_postgresql_version(app_configs, databases=None, **kwargs):
    """
    Report an error if the PostgreSQL version is less than POSTGRESQL_MIN_VERSION.
    """
    errors = []

    # Validate only those database aliases which Django has asked us to check. A value of None means
    # that no database may be touched during this run, so there is nothing to validate: commands which
    # do intend to use a connection declare its alias (e.g. `migrate` passes the value of --database).
    # This mirrors Django's own database checks; see checks.database.check_database_backends().
    if databases is None:
        return errors

    for alias in databases:
        connection = connections[alias]

        # A plugin may register a connection to some other type of database; only PostgreSQL
        # connections are subject to NetBox's minimum version requirement.
        if connection.vendor != 'postgresql':
            continue

        try:
            with connection.cursor() as cursor:
                cursor.execute('SHOW server_version_num')
                row = cursor.fetchone()
        except NotSupportedError:
            # Django refuses to use the connection at all when the server predates the minimum version
            # which Django itself supports (BaseDatabaseWrapper.check_database_version_supported()), so
            # the query above never runs. The PostgreSQL backend registers no validation checks of its
            # own, so report the requirement here rather than letting the raw exception surface as a
            # traceback the first time something touches the database.
            errors.append(
                Error(
                    f"Database '{alias}': The configured PostgreSQL version is not supported. NetBox "
                    f"requires PostgreSQL {POSTGRESQL_MIN_VERSION} or later.",
                    hint=f'Please upgrade to PostgreSQL {POSTGRESQL_MIN_VERSION} or later.',
                    id='netbox.E001',
                )
            )
            continue
        except (ImproperlyConfigured, InterfaceError, OperationalError):
            # The database is unreachable, has yet to be provisioned, or the connection is no longer
            # usable. (InterfaceError is a sibling of DatabaseError, not a subclass, so it must be
            # named explicitly.) Leave the version unverified rather than reporting a spurious error.
            continue
        except DatabaseError:
            # The server is reachable but rejected the query (e.g. a connection pooler which intercepts
            # SHOW). Record why the version could not be determined rather than failing silently.
            logger.warning(f"Database '{alias}': Failed to determine the PostgreSQL version.", exc_info=True)
            continue

        if not row:
            logger.warning(f"Database '{alias}': `SHOW server_version_num` returned no result.")
            continue

        try:
            pg_version = int(row[0])
        except (TypeError, ValueError):
            # `SHOW server_version_num` reports an integer, but a pooler which answers the statement
            # itself may report a dotted version instead. Leave the version unverified rather than
            # raising out of the check and aborting the calling command.
            logger.warning(f"Database '{alias}': Unable to parse the PostgreSQL version from {row[0]!r}.")
            continue

        if pg_version < POSTGRESQL_MIN_VERSION * POSTGRESQL_VERSION_MULTIPLIER:
            major_version = pg_version // POSTGRESQL_VERSION_MULTIPLIER
            errors.append(
                Error(
                    f"Database '{alias}': PostgreSQL {major_version} is not supported. NetBox requires "
                    f"PostgreSQL {POSTGRESQL_MIN_VERSION} or later.",
                    hint=f'Please upgrade to PostgreSQL {POSTGRESQL_MIN_VERSION} or later.',
                    id='netbox.E001',
                )
            )

    return errors


@register(Tags.caches)
def check_redis_version(app_configs, **kwargs):
    """
    Report an error if the Redis version is less than 6.0.
    """
    errors = []
    try:
        client = cache.client.get_client()
        redis_version = tuple(int(x) for x in client.info()['redis_version'].split('.'))
        if redis_version < (6, 0):
            errors.append(
                Error(
                    f'Redis {".".join(str(x) for x in redis_version)} is not supported. NetBox requires Redis 6.0 '
                    f'or later.',
                    hint='Please upgrade to Redis 6.0 or later.',
                    id='netbox.E002',
                )
            )
    except Exception:
        pass
    return errors
