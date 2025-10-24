from django.conf import settings

from netbox.graphql.schema import schema_v1, schema_v2

__all__ = (
    'get_default_schema',
)


def get_default_schema():
    """
    Returns the GraphQL schema corresponding to the value of the NETBOX_GRAPHQL_DEFAULT_SCHEMA setting.
    """
    if settings.GRAPHQL_DEFAULT_VERSION == 2:
        return schema_v2
    return schema_v1
