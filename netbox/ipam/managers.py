from django.db.models import Manager

from ipam.lookups import Host, Inet
from ipam.querysets import IPAddressQuerySet


class IPAddressManager(Manager.from_queryset(IPAddressQuerySet)):

    def get_queryset(self):
        """
        By default, PostgreSQL will order INETs with shorter (larger) prefix lengths ahead of those with longer
        (smaller) masks. This makes no sense when ordering IPs, which should be ordered solely by family and host
        address. We can use HOST() to extract just the host portion of the address (ignoring its mask), but we must
        then re-cast this value to INET() so that records will be ordered properly. We are essentially re-casting each
        IP address as a /32 or /128.

        Host addresses are not unique, so we must also order by primary key to guarantee a stable, total ordering.
        Without this tiebreaker, PostgreSQL is free to return tied rows in a different order from one query to the
        next, which causes objects to be duplicated or omitted across paginated requests.
        """
        return super().get_queryset().order_by(Inet(Host('address')), 'pk')
