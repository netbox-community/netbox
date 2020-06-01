from django.db.models import Manager

from ipam.lookups import Host, Inet
from utilities.querysets import RestrictedQuerySet


class IPAddressManager(Manager.from_queryset(RestrictedQuerySet)):

    def get_queryset(self):
        """
        By default, PostgreSQL will order INETs with shorter (larger) prefix lengths ahead of those with longer
        (smaller) masks. This makes no sense when ordering IPs, which should be ordered solely by family and host
        address. We can use HOST() to extract just the host portion of the address (ignoring its mask), but we must
        then re-cast this value to INET() so that records will be ordered properly. We are essentially re-casting each
        IP address as a /32 or /128.
        """
        return super().get_queryset().order_by(Inet(Host('address')))
