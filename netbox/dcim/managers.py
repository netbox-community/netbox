from django.db.models import Manager, QuerySet

from .constants import NONCONNECTABLE_IFACE_TYPES


class InterfaceQuerySet(QuerySet):

    def connectable(self):
        """
        Return only physical interfaces which are capable of being connected to other interfaces (i.e. not virtual or
        wireless).
        """
        return self.exclude(type__in=NONCONNECTABLE_IFACE_TYPES)


class InterfaceManager(Manager):

    def get_queryset(self):
        return InterfaceQuerySet(self.model, using=self._db)
