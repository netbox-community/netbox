from mptt.managers import TreeManager as TreeManager_
from mptt.querysets import TreeQuerySet as TreeQuerySet_

from django.db.models import Manager
from .querysets import RestrictedQuerySet


class TreeQuerySet(TreeQuerySet_, RestrictedQuerySet):
    """
    Mate django-mptt's TreeQuerySet with our RestrictedQuerySet for permissions enforcement.
    """
    pass


class TreeManager(Manager.from_queryset(TreeQuerySet), TreeManager_):
    """
    Extend django-mptt's TreeManager to incorporate RestrictedQuerySet().
    """
    pass
