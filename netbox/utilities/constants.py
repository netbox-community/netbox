#
# Filter lookup expressions
#

FILTER_CHAR_BASED_LOOKUP_MAP = dict(
    n='exact',
    ic='icontains',
    nic='icontains',
    iew='iendswith',
    niew='iendswith',
    isw='istartswith',
    nisw='istartswith',
    ie='iexact',
    nie='iexact'
)

FILTER_NUMERIC_BASED_LOOKUP_MAP = dict(
    n='exact',
    lte='lte',
    lt='lt',
    gte='gte',
    gt='gt'
)

FILTER_NEGATION_LOOKUP_MAP = dict(
    n='exact'
)

FILTER_TREENODE_NEGATION_LOOKUP_MAP = dict(
    n='in'
)


# Keys for PostgreSQL advisory locks. These are arbitrary bigints used by
# the advisory_lock contextmanager. When a lock is acquired,
# one of these keys will be used to identify said lock.
#
# When adding a new key, pick something arbitrary and unique so
# that it is easily searchable in query logs.

ADVISORY_LOCK_KEYS = {
    'available-prefixes': 100100,
    'available-ips': 100200,
}

#
# HTTP Request META safe copy
#

HTTP_REQUEST_META_SAFE_COPY = [
    'CONTENT_LENGTH',
    'CONTENT_TYPE',
    'HTTP_ACCEPT',
    'HTTP_ACCEPT_ENCODING',
    'HTTP_ACCEPT_LANGUAGE',
    'HTTP_HOST',
    'HTTP_REFERER',
    'HTTP_USER_AGENT',
    'QUERY_STRING',
    'REMOTE_ADDR',
    'REMOTE_HOST',
    'REMOTE_USER',
    'REQUEST_METHOD',
    'SERVER_NAME',
    'SERVER_PORT',
]
