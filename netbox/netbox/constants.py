# Prefix for nested serializers
# TODO: Remove in v4.1
NESTED_SERIALIZER_PREFIX = 'Nested'

# RQ queue names
RQ_QUEUE_DEFAULT = 'default'
RQ_QUEUE_HIGH = 'high'
RQ_QUEUE_LOW = 'low'

# Keys for PostgreSQL advisory locks. These are arbitrary bigints used by the advisory_lock
# context manager. When a lock is acquired, one of these keys will be used to identify said lock.
# When adding a new key, pick something arbitrary and unique so that it is easily searchable in
# query logs.
ADVISORY_LOCK_KEYS = {
    # Available object locks
    'available-prefixes': 100100,
    'available-ips': 100200,
    'available-vlans': 100300,
    'available-asns': 100400,

    # MPTT locks
    'region': 105100,
    'sitegroup': 105200,
    'location': 105300,
    'tenantgroup': 105400,
    'contactgroup': 105500,
    'wirelesslangroup': 105600,
    'inventoryitem': 105700,
    'inventoryitemtemplate': 105800,
}

# Default view action permission mapping
DEFAULT_ACTION_PERMISSIONS = {
    'add': {'add'},
    'import': {'add'},
    'export': {'view'},
    'bulk_edit': {'change'},
    'bulk_delete': {'delete'},
}

# General-purpose tokens
CENSOR_TOKEN = '********'
CENSOR_TOKEN_CHANGED = '***CHANGED***'

# Placeholder text for empty tables
EMPTY_TABLE_TEXT = 'No results found'
