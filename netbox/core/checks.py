from django.apps import apps
from django.core.cache import cache
from django.core.checks import Error, Tags, Warning, register
from django.db import connection
from django.db.models import Index, UniqueConstraint

__all__ = (
    'check_duplicate_indexes',
    'check_postgresql_version',
    'check_redis_version',
)


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
def check_postgresql_version(app_configs, **kwargs):
    """
    Warn if the PostgreSQL version is less than 15, as support for PostgreSQL 14
    will be removed in NetBox v4.7.
    """
    warnings = []
    try:
        with connection.cursor() as cursor:
            cursor.execute('SHOW server_version_num')
            row = cursor.fetchone()
            pg_version = int(row[0])
        if pg_version < 150000:
            major_version = pg_version // 10000
            warnings.append(
                Warning(
                    f'Support for PostgreSQL {major_version} is deprecated and will be removed in NetBox v4.7.',
                    hint='Please upgrade to PostgreSQL 15 or later.',
                    id='netbox.W001',
                )
            )
    except Exception:
        pass
    return warnings


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
