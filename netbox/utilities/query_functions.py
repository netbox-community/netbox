from django.contrib.postgres.aggregates import JSONBAgg
from django.db.models import F, Func


class CollateAsChar(Func):
    """
    Disregard localization by collating a field as a plain character string. Helpful for ensuring predictable ordering.
    """
    function = 'C'
    template = '(%(expressions)s) COLLATE "%(function)s"'


class EmptyGroupByJSONBAgg(JSONBAgg):
    """
    JSONBAgg is a builtin aggregation function which means it includes the use of a GROUP BY clause.
    When used as an annotation for collecting config context data objects, the GROUP BY is
    incorrect. This subclass overrides the Django ORM aggregation control to remove the GROUP BY.
    """
    contains_aggregate = False
