__all__ = (
    'title',
    'trailing_slash',
)


def title(value):
    """
    Improved implementation of str.title(); retains all existing uppercase letters.
    """
    return ' '.join([w[0].upper() + w[1:] for w in str(value).split()])


def trailing_slash(value):
    """
    Remove a leading slash (if any) and include a trailing slash, except for empty strings.
    """
    return f'{value.strip("/")}/' if value else ''
