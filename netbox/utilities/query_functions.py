from django.contrib.postgres.aggregates import JSONBAgg
from django.contrib.postgres.aggregates.mixins import OrderableAggMixin
from django.db.models import F, Func


class CollateAsChar(Func):
    """
    Disregard localization by collating a field as a plain character string. Helpful for ensuring predictable ordering.
    """
    function = 'C'
    template = '(%(expressions)s) COLLATE "%(function)s"'


class OrderableJSONBAgg(OrderableAggMixin, JSONBAgg):
    """
    TODO in Django 3.2 ordering is supported natively on JSONBAgg so this is no longer needed.
    """
    template = '%(function)s(%(distinct)s%(expressions)s %(ordering)s)'


class EmptyGroupByJSONBAgg(OrderableJSONBAgg):
    """
    JSONBAgg is a builtin aggregation function which means it includes the use of a GROUP BY clause.
    When used as an annotation for collecting config context data objects, the GROUP BY is
    incorrect. This subclass overrides the Django ORM aggregation control to remove the GROUP BY.

    TODO in Django 3.2 ordering is supported natively on JSONBAgg so we only need to inherit from JSONBAgg.
    """
    contains_aggregate = False
