from django.db.models import Count, IntegerField, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce

from utilities.querysets import RestrictedQuerySet

__all__ = (
    'MACBlockQuerySet',
)


class MACBlockQuerySet(RestrictedQuerySet):

    def annotate_mac_address_count(self):
        """
        Annotate the number of distinct MAC addresses within each MACBlock.
        """
        from .models import MACAddress

        mac_addresses = MACAddress.objects.filter(
            mac_address__gte=OuterRef('prefix'),
            mac_address__lte=OuterRef('_last_address'),
        ).order_by().annotate(
            group=Value(1)
        ).values('group').annotate(
            count=Count('mac_address', distinct=True)
        ).values('count')

        return self.annotate(
            mac_address_count=Coalesce(Subquery(mac_addresses, output_field=IntegerField()), 0)
        )
