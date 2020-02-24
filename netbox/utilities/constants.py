COLOR_CHOICES = (
    ('aa1409', 'Dark red'),
    ('f44336', 'Red'),
    ('e91e63', 'Pink'),
    ('ffe4e1', 'Rose'),
    ('ff66ff', 'Fuschia'),
    ('9c27b0', 'Purple'),
    ('673ab7', 'Dark purple'),
    ('3f51b5', 'Indigo'),
    ('2196f3', 'Blue'),
    ('03a9f4', 'Light blue'),
    ('00bcd4', 'Cyan'),
    ('009688', 'Teal'),
    ('00ffff', 'Aqua'),
    ('2f6a31', 'Dark green'),
    ('4caf50', 'Green'),
    ('8bc34a', 'Light green'),
    ('cddc39', 'Lime'),
    ('ffeb3b', 'Yellow'),
    ('ffc107', 'Amber'),
    ('ff9800', 'Orange'),
    ('ff5722', 'Dark orange'),
    ('795548', 'Brown'),
    ('c0c0c0', 'Light grey'),
    ('9e9e9e', 'Grey'),
    ('607d8b', 'Dark grey'),
    ('111111', 'Black'),
    ('ffffff', 'White'),
)


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
