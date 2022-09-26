from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.db.models.expressions import RawSQL

from utilities.querysets import RestrictedQuerySet


class PrefixQuerySet(RestrictedQuerySet):

    def annotate_hierarchy(self):
        """
        Annotate the depth and number of child prefixes for each Prefix. Cast null VRF values to zero for
        comparison. (NULL != NULL).
        """
        return self.annotate(
            hierarchy_depth=RawSQL(
                'SELECT COUNT(DISTINCT U0."prefix") AS "c" '
                'FROM "ipam_prefix" U0 '
                'WHERE (U0."prefix" >> "ipam_prefix"."prefix" '
                'AND COALESCE(U0."vrf_id", 0) = COALESCE("ipam_prefix"."vrf_id", 0))',
                ()
            ),
            hierarchy_children=RawSQL(
                'SELECT COUNT(U1."prefix") AS "c" '
                'FROM "ipam_prefix" U1 '
                'WHERE (U1."prefix" << "ipam_prefix"."prefix" '
                'AND COALESCE(U1."vrf_id", 0) = COALESCE("ipam_prefix"."vrf_id", 0))',
                ()
            )
        )


class VLANQuerySet(RestrictedQuerySet):

    def get_for_device(self, device):
        """
        Return all VLANs available to the specified Device.
        """
        from .models import VLANGroup

        # Find all relevant VLANGroups
        q = Q()
        if device.site.region:
            q |= Q(
                scope_type=ContentType.objects.get_by_natural_key('dcim', 'region'),
                scope_id__in=device.site.region.get_ancestors(include_self=True)
            )
        if device.site.group:
            q |= Q(
                scope_type=ContentType.objects.get_by_natural_key('dcim', 'sitegroup'),
                scope_id__in=device.site.group.get_ancestors(include_self=True)
            )
        q |= Q(
            scope_type=ContentType.objects.get_by_natural_key('dcim', 'site'),
            scope_id=device.site_id
        )
        if device.location:
            q |= Q(
                scope_type=ContentType.objects.get_by_natural_key('dcim', 'location'),
                scope_id__in=device.location.get_ancestors(include_self=True)
            )
        if device.rack:
            q |= Q(
                scope_type=ContentType.objects.get_by_natural_key('dcim', 'rack'),
                scope_id=device.rack_id
            )

        # Return all applicable VLANs
        return self.filter(
            Q(group__in=VLANGroup.objects.filter(q)) |
            Q(site=device.site) |
            Q(group__scope_id__isnull=True, site__isnull=True) |  # Global group VLANs
            Q(group__isnull=True, site__isnull=True)  # Global VLANs
        )

    def get_for_virtualmachine(self, vm):
        """
        Return all VLANs available to the specified VirtualMachine.
        """
        from .models import VLANGroup

        # Find all relevant VLANGroups
        q = Q()
        site = vm.site or vm.cluster.site
        if vm.cluster:
            # Add VLANGroups scoped to the assigned cluster (or its group)
            q |= Q(
                scope_type=ContentType.objects.get_by_natural_key('virtualization', 'cluster'),
                scope_id=vm.cluster_id
            )
            if vm.cluster.group:
                q |= Q(
                    scope_type=ContentType.objects.get_by_natural_key('virtualization', 'clustergroup'),
                    scope_id=vm.cluster.group_id
                )
        if site:
            # Add VLANGroups scoped to the assigned site (or its group or region)
            q |= Q(
                scope_type=ContentType.objects.get_by_natural_key('dcim', 'site'),
                scope_id=site.pk
            )
            if site.region:
                q |= Q(
                    scope_type=ContentType.objects.get_by_natural_key('dcim', 'region'),
                    scope_id__in=site.region.get_ancestors(include_self=True)
                )
            if site.group:
                q |= Q(
                    scope_type=ContentType.objects.get_by_natural_key('dcim', 'sitegroup'),
                    scope_id__in=site.group.get_ancestors(include_self=True)
                )
        vlan_groups = VLANGroup.objects.filter(q)

        # Return all applicable VLANs
        q = (
            Q(group__in=vlan_groups) |
            Q(group__scope_id__isnull=True, site__isnull=True) |  # Global group VLANs
            Q(group__isnull=True, site__isnull=True)  # Global VLANs
        )
        if site:
            q |= Q(site=site)

        return self.filter(q)
