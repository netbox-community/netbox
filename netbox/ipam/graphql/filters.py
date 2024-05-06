import strawberry_django

from ipam import filtersets, models
from netbox.graphql.filter_mixins import autotype_decorator, BaseFilterMixin

__all__ = (
    'ASNFilter',
    'ASNRangeFilter',
    'AggregateFilter',
    'FHRPGroupFilter',
    'FHRPGroupAssignmentFilter',
    'IPAddressFilter',
    'IPRangeFilter',
    'PrefixFilter',
    'RIRFilter',
    'RoleFilter',
    'RouteTargetFilter',
    'ServiceFilter',
    'ServiceTemplateFilter',
    'VLANFilter',
    'VLANGroupFilter',
    'VRFFilter',
)


@strawberry_django.filter(models.ASN, lookups=True)
@autotype_decorator(filtersets.ASNFilterSet)
class ASNFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.ASNRange, lookups=True)
@autotype_decorator(filtersets.ASNRangeFilterSet)
class ASNRangeFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.Aggregate, lookups=True)
@autotype_decorator(filtersets.AggregateFilterSet)
class AggregateFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.FHRPGroup, lookups=True)
@autotype_decorator(filtersets.FHRPGroupFilterSet)
class FHRPGroupFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.FHRPGroupAssignment, lookups=True)
@autotype_decorator(filtersets.FHRPGroupAssignmentFilterSet)
class FHRPGroupAssignmentFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.IPAddress, lookups=True)
@autotype_decorator(filtersets.IPAddressFilterSet)
class IPAddressFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.IPRange, lookups=True)
@autotype_decorator(filtersets.IPRangeFilterSet)
class IPRangeFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.Prefix, lookups=True)
@autotype_decorator(filtersets.PrefixFilterSet)
class PrefixFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.RIR, lookups=True)
@autotype_decorator(filtersets.RIRFilterSet)
class RIRFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.Role, lookups=True)
@autotype_decorator(filtersets.RoleFilterSet)
class RoleFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.RouteTarget, lookups=True)
@autotype_decorator(filtersets.RouteTargetFilterSet)
class RouteTargetFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.Service, lookups=True)
@autotype_decorator(filtersets.ServiceFilterSet)
class ServiceFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.ServiceTemplate, lookups=True)
@autotype_decorator(filtersets.ServiceTemplateFilterSet)
class ServiceTemplateFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.VLAN, lookups=True)
@autotype_decorator(filtersets.VLANFilterSet)
class VLANFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.VLANGroup, lookups=True)
@autotype_decorator(filtersets.VLANGroupFilterSet)
class VLANGroupFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.VRF, lookups=True)
@autotype_decorator(filtersets.VRFFilterSet)
class VRFFilter(BaseFilterMixin):
    pass
