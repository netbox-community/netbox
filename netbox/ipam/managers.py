from django.db import models

from ipam.lookups import Host, Inet


class IPAddressManager(models.Manager):

    def get_queryset(self):
        """
        By default, PostgreSQL will order INETs with shorter (larger) prefix lengths ahead of those with longer
        (smaller) masks. This makes no sense when ordering IPs, which should be ordered solely by family and host
        address. We can use HOST() to extract just the host portion of the address (ignoring its mask), but we must
        then re-cast this value to INET() so that records will be ordered properly. We are essentially re-casting each
        IP address as a /32 or /128.
        """
        qs = super().get_queryset()
        return qs.order_by(Inet(Host('address')))
