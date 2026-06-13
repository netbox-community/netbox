import heapq

import netaddr
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, F, OuterRef, Q, Subquery, Value
from django.db.models.expressions import RawSQL
from django.db.models.functions import Cast, NullIf, Round

from utilities.query import count_related
from utilities.querysets import RestrictedQuerySet

from .fields import IPAddressField
from .lookups import Host

__all__ = (
    'ASNRangeQuerySet',
    'IPAddressQuerySet',
    'IPRangeQuerySet',
    'PrefixQuerySet',
    'VLANGroupQuerySet',
    'VLANQuerySet',
)

# The host portion of an IP address (mask ignored), in the same form as the
# ipam_ipaddress_host expression index.
HOST_ADDRESS = Cast(Host('address'), output_field=IPAddressField())


def _merge_intervals(intervals):
    """
    Return the union of (start, end) netaddr.IPAddress intervals, merged and sorted.
    """
    if not intervals:
        return []

    intervals = sorted(intervals)
    merged = [intervals[0]]

    for start, end in intervals[1:]:
        current_start, current_end = merged[-1]
        # Adjacency math in int space; netaddr raises at the address-space maximum.
        if start.version == current_end.version and int(start) <= int(current_end) + 1:
            merged[-1] = (current_start, max(current_end, end))
        else:
            merged.append((start, end))

    return merged


class ASNRangeQuerySet(RestrictedQuerySet):

    def annotate_asn_counts(self):
        """
        Annotate the number of ASNs which appear within each range.
        """
        from .models import ASN

        # Because ASN does not have a foreign key to ASNRange, we create a fake column "_" with a consistent value
        # that we can use to count ASNs and return a single value per ASNRange.
        asns = ASN.objects.filter(
            asn__gte=OuterRef('start'),
            asn__lte=OuterRef('end')
        ).order_by().annotate(_=Value(1)).values('_').annotate(c=Count('*')).values('c')

        return self.annotate(asn_count=Subquery(asns))


class IPAddressQuerySet(RestrictedQuerySet):

    def count_distinct_hosts(self, exclude_intervals=()):
        """
        Count distinct host addresses, optionally excluding (start, end) netaddr.IPAddress intervals.
        """
        queryset = self
        for start, end in exclude_intervals:
            queryset = queryset.exclude(address__host_between=(start, end))

        return queryset.aggregate(count=Count(HOST_ADDRESS, distinct=True))['count']

    def count_distinct_hosts_pair(self, bounds, bounded_exclude=(), total_exclude=()):
        """
        Return two distinct host counts computed in a single scan, as a dict:
        'bounded' counts hosts within the (first_ip, last_ip) bounds excluding the
        bounded_exclude intervals; 'total' counts all hosts excluding the
        total_exclude intervals. Interval arguments match the output of
        IPRangeQuerySet.get_intervals(). Avoids a second scan of the host expression
        index when both counts are needed. Use only when both counts are needed (e.g.
        Prefix.get_ip_usage_summary()); single-purpose callers should prefer
        count_distinct_hosts().
        """
        # The deduplicated column is already a bare host; plain comparisons beat
        # the host_between lookup here, which would re-wrap it in HOST()::inet.
        bounded_q = Q(host_address__range=(str(bounds[0]), str(bounds[1])))
        for start, end in bounded_exclude:
            bounded_q &= ~Q(host_address__range=(str(start), str(end)))
        total_q = Q()
        for start, end in total_exclude:
            total_q &= ~Q(host_address__range=(str(start), str(end)))

        hosts = self.order_by().annotate(host_address=HOST_ADDRESS).values('host_address').distinct()
        return hosts.aggregate(
            bounded=Count('host_address', filter=bounded_q),
            # An empty Q is falsy; fall back to a plain count of all hosts.
            total=Count('host_address', filter=total_q or None),
        )

    def _iter_distinct_hosts(self, first_ip, last_ip, batch_size):
        """
        Yield the distinct occupied hosts in [first_ip, last_ip] in ascending order,
        fetched in LIMIT batches that resume just past the last seen host. (A
        server-side cursor is unsuitable here: on autocommit connections Django
        declares it WITH HOLD, which materializes the full result at DECLARE.)
        """
        resume = first_ip
        while True:
            # order_by() first clears the default ordering, which would otherwise
            # leak into SELECT and break distinct().
            hosts = list(
                self.filter(address__host_between=(resume, last_ip))
                .order_by()
                .annotate(host_address=HOST_ADDRESS)
                .values_list('host_address', flat=True)
                .distinct()
                .order_by('host_address')[:batch_size]
            )
            for host in hosts:
                yield host.ip
            if len(hosts) < batch_size:
                return
            last_host = hosts[-1].ip
            if int(last_host) >= int(last_ip):
                return
            resume = netaddr.IPAddress(int(last_host) + 1, version=last_host.version)

    def available_intervals(self, first_ip, last_ip, exclude_intervals=(), batch_size=5000):
        """
        Yield the unoccupied (start, end) netaddr.IPAddress intervals (inclusive)
        within [first_ip, last_ip], in ascending order. exclude_intervals are
        (start, end) netaddr.IPAddress pairs; they are merged and sorted internally,
        intervals of a foreign address family are ignored, and addresses they cover
        count as occupied. Consumption is lazy: a caller that stops early stops
        fetching host batches.
        """
        if batch_size < 1:
            raise ValueError('batch_size must be greater than zero')

        first_int, last_int = int(first_ip), int(last_ip)
        version = first_ip.version

        if first_int > last_int:
            return
        # Normalize: the sweep below requires sorted, non-overlapping, same-family intervals.
        exclude_intervals = _merge_intervals([
            (start, end)
            for start, end in exclude_intervals
            if start.version == end.version == version
        ])
        intervals = [(int(start), int(end)) for start, end in exclude_intervals]

        # Fast path: one merged excluded interval covers the entire span.
        if intervals and intervals[0][0] <= first_int and intervals[0][1] >= last_int:
            return

        hosts = (
            (int(host), int(host))
            for host in self._iter_distinct_hosts(first_ip, last_ip, batch_size)
        )

        candidate = first_int
        # Ties on `start` are harmless; the sweep handles overlapping intervals.
        for start, end in heapq.merge(intervals, hosts):
            if end < candidate:
                continue
            if start > candidate:
                yield (
                    netaddr.IPAddress(candidate, version=version),
                    netaddr.IPAddress(min(start - 1, last_int), version=version),
                )
            candidate = max(candidate, end + 1)
            if candidate > last_int:
                return

        if candidate <= last_int:
            yield (
                netaddr.IPAddress(candidate, version=version),
                netaddr.IPAddress(last_int, version=version),
            )

    def first_available_host(self, first_ip, last_ip, exclude_intervals=()):
        """
        Return the first host in [first_ip, last_ip] neither present nor in an excluded interval (or None).
        """
        interval = next(self.available_intervals(first_ip, last_ip, exclude_intervals), None)
        return interval[0] if interval else None


class IPRangeQuerySet(RestrictedQuerySet):

    def get_intervals(self, first_ip=None, last_ip=None):
        """
        Return ranges as merged (start, end) netaddr.IPAddress intervals, optionally clipped to the bounds.
        """
        intervals = []

        # order_by() clears the default ordering; _merge_intervals() sorts anyway.
        for start_address, end_address in self.order_by().values_list('start_address', 'end_address'):
            start, end = start_address.ip, end_address.ip

            if first_ip is not None:
                if end < first_ip:
                    continue
                start = max(start, first_ip)

            if last_ip is not None:
                if start > last_ip:
                    continue
                end = min(end, last_ip)

            intervals.append((start, end))

        return _merge_intervals(intervals)


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


class VLANGroupQuerySet(RestrictedQuerySet):

    def annotate_utilization(self):
        from .models import VLAN

        # NullIf guards against legacy rows where total_vlan_ids was miscounted to
        # 0 by the pre-fix VLANGroup.save(); without it, the annotation 500s.
        return self.annotate(
            vlan_count=count_related(VLAN, 'group'),
            utilization=Round(F('vlan_count') * 100.0 / NullIf(F('total_vlan_ids'), Value(0)), 2),
        )


class VLANQuerySet(RestrictedQuerySet):

    def get_for_site(self, site):
        """
        Return all VLANs in the specified site
        """
        from .models import VLANGroup
        q = Q()
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

        return self.filter(
            Q(group__in=VLANGroup.objects.filter(q)) |
            Q(site=site) |
            Q(group__scope_id__isnull=True, site__isnull=True) |  # Global group VLANs
            Q(group__isnull=True, site__isnull=True)  # Global VLANs
        )

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
        site = vm.site
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
            # Looking all possible cluster scopes
            if vm.cluster.scope_type == ContentType.objects.get_by_natural_key('dcim', 'location'):
                site = site or vm.cluster.scope.site
                q |= Q(
                    scope_type=ContentType.objects.get_by_natural_key('dcim', 'location'),
                    scope_id__in=vm.cluster.scope.get_ancestors(include_self=True)
                )
            elif vm.cluster.scope_type == ContentType.objects.get_by_natural_key('dcim', 'site'):
                site = site or vm.cluster.scope
                q |= Q(
                    scope_type=ContentType.objects.get_by_natural_key('dcim', 'site'),
                    scope_id=vm.cluster.scope.pk
                )
            elif vm.cluster.scope_type == ContentType.objects.get_by_natural_key('dcim', 'sitegroup'):
                q |= Q(
                    scope_type=ContentType.objects.get_by_natural_key('dcim', 'sitegroup'),
                    scope_id__in=vm.cluster.scope.get_ancestors(include_self=True)
                )
            elif vm.cluster.scope_type == ContentType.objects.get_by_natural_key('dcim', 'region'):
                q |= Q(
                    scope_type=ContentType.objects.get_by_natural_key('dcim', 'region'),
                    scope_id__in=vm.cluster.scope.get_ancestors(include_self=True)
                )
        # VM can be assigned to a site without a cluster so checking assigned site independently
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
