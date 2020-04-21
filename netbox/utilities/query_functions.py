from django.db.models import F, Func


class CollateAsChar(Func):
    """
    Disregard localization by collating a field as a plain character string. Helpful for ensuring predictable ordering.
    """
    function = 'C'
    template = '(%(expressions)s) COLLATE "%(function)s"'
