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
    nie='iexact',
    empty='empty',
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
    'HTTP_X_FORWARDED_FOR',
    'QUERY_STRING',
    'REMOTE_ADDR',
    'REMOTE_HOST',
    'REMOTE_USER',
    'REQUEST_METHOD',
    'SERVER_NAME',
    'SERVER_PORT',
]
