# String expansion patterns
NUMERIC_EXPANSION_PATTERN = r'\[((?:\d+[?:,-])+\d+)\]'
ALPHANUMERIC_EXPANSION_PATTERN = r'\[((?:[a-zA-Z0-9]+[?:,-])+[a-zA-Z0-9]+)\]'

# Patterns for parts of string expansion patterns
ALPHABETIC_RANGE_PATTERN = fr'(?:[A-Z]-[A-Z]|[a-z]-[a-z])'
NUMERIC_RANGE_PATTERN = r'(?:[0-9]+-[0-9]+)'
ALPHANUMERIC_SINGLETON_PATTERN = r'(?:[a-zA-Z0-9]+)'

# IP address expansion patterns
IP4_EXPANSION_PATTERN = r'\[((?:[0-9]{1,3}[?:,-])+[0-9]{1,3})\]'
IP6_EXPANSION_PATTERN = r'\[((?:[0-9a-f]{1,4}[?:,-])+[0-9a-f]{1,4})\]'

# Boolean widget choices
BOOLEAN_WITH_BLANK_CHOICES = (
    ('', '---------'),
    ('True', 'Yes'),
    ('False', 'No'),
)
