from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from utilities.querysets import RestrictedQuerySet


class PrefixQuerySet(RestrictedQuerySet):

    def annotate_tree(self):
        """
        Annotate the number of parent and child prefixes for each Prefix. Raw SQL is needed for these subqueries
        because we need to cast NULL VRF values to integers for comparison. (NULL != NULL).
        """
        return self.extra(
            select={
                'parents': 'SELECT COUNT(U0."prefix") AS "c" '
                           'FROM "ipam_prefix" U0 '
                           'WHERE (U0."prefix" >> "ipam_prefix"."prefix" '
                           'AND COALESCE(U0."vrf_id", 0) = COALESCE("ipam_prefix"."vrf_id", 0))',
                'children': 'SELECT COUNT(U1."prefix") AS "c" '
                            'FROM "ipam_prefix" U1 '
                            'WHERE (U1."prefix" << "ipam_prefix"."prefix" '
                            'AND COALESCE(U1."vrf_id", 0) = COALESCE("ipam_prefix"."vrf_id", 0))',
            }
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

        return self.filter(
            Q(group__in=VLANGroup.objects.filter(q)) |
            Q(site=device.site) |
            Q(group__isnull=True, site__isnull=True)  # Global VLANs
        )

    def get_for_virtualmachine(self, vm):
        """
        Return all VLANs available to the specified VirtualMachine.
        """
        from .models import VLANGroup

        # Find all relevant VLANGroups
        q = Q()
        if vm.cluster.site:
            if vm.cluster.site.region:
                q |= Q(
                    scope_type=ContentType.objects.get_by_natural_key('dcim', 'region'),
                    scope_id__in=vm.cluster.site.region.get_ancestors(include_self=True)
                )
            if vm.cluster.site.group:
                q |= Q(
                    scope_type=ContentType.objects.get_by_natural_key('dcim', 'sitegroup'),
                    scope_id__in=vm.cluster.site.group.get_ancestors(include_self=True)
                )
            q |= Q(
                scope_type=ContentType.objects.get_by_natural_key('dcim', 'site'),
                scope_id=vm.cluster.site_id
            )
        if vm.cluster.group:
            q |= Q(
                scope_type=ContentType.objects.get_by_natural_key('virtualization', 'clustergroup'),
                scope_id=vm.cluster.group_id
            )
        q |= Q(
            scope_type=ContentType.objects.get_by_natural_key('virtualization', 'cluster'),
            scope_id=vm.cluster_id
        )

        return self.filter(
            Q(group__in=VLANGroup.objects.filter(q)) |
            Q(site=vm.cluster.site) |
            Q(group__isnull=True, site__isnull=True)  # Global VLANs
        )
