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
    gt='gt',
    empty='isnull',
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
    'HTTP_X_FORWARDED_HOST',
    'HTTP_X_FORWARDED_PORT',
    'HTTP_X_FORWARDED_PROTO',
    'HTTP_X_REAL_IP',
    'QUERY_STRING',
    'REMOTE_ADDR',
    'REMOTE_HOST',
    'REMOTE_USER',
    'REQUEST_METHOD',
    'SERVER_NAME',
    'SERVER_PORT',
]


#
# CSV-style format delimiters
#

CSV_DELIMITERS = {
    'comma': ',',
    'semicolon': ';',
    'tab': '\t',
}


#
# HTML allowed tags & attributes
#

HTML_ALLOWED_TAGS = {
    "a", "b", "blockquote", "br", "code", "dd", "del", "div", "dl", "dt", "em", "h1", "h2", "h3", "h4", "h5", "h6",
    "hr", "i", "img", "li", "ol", "p", "pre", "strong", "table", "tbody", "td", "th", "thead", "tr", "ul"
}

HTML_ALLOWED_ATTRIBUTES = {
    "a": {"href", "title"},
    "div": {"class"},
    "h1": {"id"},
    "h2": {"id"},
    "h3": {"id"},
    "h4": {"id"},
    "h5": {"id"},
    "h6": {"id"},
    "img": {"alt", "src", "title"},
    "td": {"align"},
    "th": {"align"},
}
