from django.urls import reverse

from ipam.models import ASN, Aggregate, ASNRange, IPAddress, IPRange
from netbox.ui.breadcrumbs import Breadcrumb, BreadcrumbTrail, register_breadcrumbs


@register_breadcrumbs
class ASNRangeBreadcrumbs(BreadcrumbTrail):
    model = ASNRange
    items = (
        Breadcrumb('rir', url=lambda o: f"{reverse('ipam:asnrange_list')}?rir_id={o.pk}"),
    )


@register_breadcrumbs
class ASNBreadcrumbs(BreadcrumbTrail):
    model = ASN
    items = (
        Breadcrumb('rir', url=lambda rir: f"{reverse('ipam:asn_list')}?rir_id={rir.pk}"),
    )


@register_breadcrumbs
class AggregateBreadcrumbs(BreadcrumbTrail):
    model = Aggregate
    items = (
        Breadcrumb('rir', url=lambda o: f"{reverse('ipam:aggregate_list')}?rir_id={o.pk}"),
    )


@register_breadcrumbs
class IPRangeBreadcrumbs(BreadcrumbTrail):
    model = IPRange
    items = (
        Breadcrumb('vrf', url=lambda o: f"{reverse('ipam:iprange_list')}?vrf_id={o.pk}"),
    )


@register_breadcrumbs
class IPAddressBreadcrumbs(BreadcrumbTrail):
    model = IPAddress
    items = (
        Breadcrumb('vrf', url=lambda o: f"{reverse('ipam:ipaddress_list')}?vrf_id={o.pk}"),
    )
