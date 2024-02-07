import strawberry
import strawberry_django
from strawberry import auto
from ipam import models, filtersets
from netbox.graphql import filters


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
class ASNFilter(filtersets.ASNFilterSet):
    id: auto


@strawberry_django.filter(models.ASNRange, lookups=True)
class ASNRangeFilter(filtersets.ASNRangeFilterSet):
    id: auto


@strawberry_django.filter(models.Aggregate, lookups=True)
class AggregateFilter(filtersets.AggregateFilterSet):
    id: auto


@strawberry_django.filter(models.FHRPGroup, lookups=True)
class FHRPGroupFilter(filtersets.FHRPGroupFilterSet):
    id: auto


@strawberry_django.filter(models.FHRPGroupAssignment, lookups=True)
class FHRPGroupAssignmentFilter(filtersets.FHRPGroupAssignmentFilterSet):
    id: auto


@strawberry_django.filter(models.IPAddress, lookups=True)
class IPAddressFilter(filtersets.IPAddressFilterSet):
    id: auto


@strawberry_django.filter(models.IPRange, lookups=True)
class IPRangeFilter(filtersets.IPRangeFilterSet):
    id: auto


@strawberry_django.filter(models.Prefix, lookups=True)
class PrefixFilter(filtersets.PrefixFilterSet):
    id: auto


@strawberry_django.filter(models.RIR, lookups=True)
class RIRFilter(filtersets.RIRFilterSet):
    id: auto


@strawberry_django.filter(models.Role, lookups=True)
class RoleFilter(filtersets.RoleFilterSet):
    id: auto


@strawberry_django.filter(models.RouteTarget, lookups=True)
class RouteTargetFilter(filtersets.RouteTargetFilterSet):
    id: auto


@strawberry_django.filter(models.Service, lookups=True)
class ServiceFilter(filtersets.ServiceFilterSet):
    id: auto


@strawberry_django.filter(models.ServiceTemplate, lookups=True)
class ServiceTemplateFilter(filtersets.ServiceTemplateFilterSet):
    id: auto


@strawberry_django.filter(models.VLAN, lookups=True)
class VLANFilter(filtersets.VLANFilterSet):
    id: auto


@strawberry_django.filter(models.VLANGroup, lookups=True)
class VLANGroupFilter(filtersets.VLANGroupFilterSet):
    id: auto


@strawberry_django.filter(models.VRF, lookups=True)
class VRFFilter(filtersets.VRFFilterSet):
    id: auto
