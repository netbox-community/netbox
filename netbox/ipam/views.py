from __future__ import unicode_literals

from django_tables2 import RequestConfig
import netaddr

from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import View

from dcim.models import Device
from utilities.paginator import EnhancedPaginator
from utilities.views import (
    BulkAddView, BulkDeleteView, BulkEditView, BulkImportView, ObjectDeleteView, ObjectEditView, ObjectListView,
)
from . import filters, forms, tables
from .models import (
    Aggregate, IPAddress, PREFIX_STATUS_ACTIVE, PREFIX_STATUS_DEPRECATED, PREFIX_STATUS_RESERVED, Prefix, RIR, Role,
    Service, VLAN, VLANGroup, VRF,
)


def add_available_prefixes(parent, prefix_list):
    """
    Create fake Prefix objects for all unallocated space within a prefix.
    """

    # Find all unallocated space
    available_prefixes = netaddr.IPSet(parent) ^ netaddr.IPSet([p.prefix for p in prefix_list])
    available_prefixes = [Prefix(prefix=p) for p in available_prefixes.iter_cidrs()]

    # Concatenate and sort complete list of children
    prefix_list = list(prefix_list) + available_prefixes
    prefix_list.sort(key=lambda p: p.prefix)

    return prefix_list


def add_available_ipaddresses(prefix, ipaddress_list, is_pool=False):
    """
    Annotate ranges of available IP addresses within a given prefix. If is_pool is True, the first and last IP will be
    considered usable (regardless of mask length).
    """

    output = []
    prev_ip = None

    # Ignore the network and broadcast addresses for non-pool IPv4 prefixes larger than /31.
    if prefix.version == 4 and prefix.prefixlen < 31 and not is_pool:
        first_ip_in_prefix = netaddr.IPAddress(prefix.first + 1)
        last_ip_in_prefix = netaddr.IPAddress(prefix.last - 1)
    else:
        first_ip_in_prefix = netaddr.IPAddress(prefix.first)
        last_ip_in_prefix = netaddr.IPAddress(prefix.last)

    if not ipaddress_list:
        return [(
            int(last_ip_in_prefix - first_ip_in_prefix + 1),
            '{}/{}'.format(first_ip_in_prefix, prefix.prefixlen)
        )]

    # Account for any available IPs before the first real IP
    if ipaddress_list[0].address.ip > first_ip_in_prefix:
        skipped_count = int(ipaddress_list[0].address.ip - first_ip_in_prefix)
        first_skipped = '{}/{}'.format(first_ip_in_prefix, prefix.prefixlen)
        output.append((skipped_count, first_skipped))

    # Iterate through existing IPs and annotate free ranges
    for ip in ipaddress_list:
        if prev_ip:
            diff = int(ip.address.ip - prev_ip.address.ip)
            if diff > 1:
                first_skipped = '{}/{}'.format(prev_ip.address.ip + 1, prefix.prefixlen)
                output.append((diff - 1, first_skipped))
        output.append(ip)
        prev_ip = ip

    # Include any remaining available IPs
    if prev_ip.address.ip < last_ip_in_prefix:
        skipped_count = int(last_ip_in_prefix - prev_ip.address.ip)
        first_skipped = '{}/{}'.format(prev_ip.address.ip + 1, prefix.prefixlen)
        output.append((skipped_count, first_skipped))

    return output


#
# VRFs
#

class VRFListView(ObjectListView):
    queryset = VRF.objects.select_related('tenant')
    filter = filters.VRFFilter
    filter_form = forms.VRFFilterForm
    table = tables.VRFTable
    template_name = 'ipam/vrf_list.html'


class VRFView(View):

    def get(self, request, pk):

        vrf = get_object_or_404(VRF.objects.all(), pk=pk)
        prefix_table = tables.PrefixBriefTable(
            list(Prefix.objects.filter(vrf=vrf).select_related('site', 'role'))
        )
        prefix_table.exclude = ('vrf',)

        return render(request, 'ipam/vrf.html', {
            'vrf': vrf,
            'prefix_table': prefix_table,
        })


class VRFCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipam.add_vrf'
    model = VRF
    form_class = forms.VRFForm
    template_name = 'ipam/vrf_edit.html'
    default_return_url = 'ipam:vrf_list'


class VRFEditView(VRFCreateView):
    permission_required = 'ipam.change_vrf'


class VRFDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'ipam.delete_vrf'
    model = VRF
    default_return_url = 'ipam:vrf_list'


class VRFBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'ipam.add_vrf'
    model_form = forms.VRFCSVForm
    table = tables.VRFTable
    default_return_url = 'ipam:vrf_list'


class VRFBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'ipam.change_vrf'
    cls = VRF
    filter = filters.VRFFilter
    form = forms.VRFBulkEditForm
    template_name = 'ipam/vrf_bulk_edit.html'
    default_return_url = 'ipam:vrf_list'


class VRFBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipam.delete_vrf'
    cls = VRF
    filter = filters.VRFFilter
    default_return_url = 'ipam:vrf_list'


#
# RIRs
#

class RIRListView(ObjectListView):
    queryset = RIR.objects.annotate(aggregate_count=Count('aggregates'))
    filter = filters.RIRFilter
    filter_form = forms.RIRFilterForm
    table = tables.RIRTable
    template_name = 'ipam/rir_list.html'

    def alter_queryset(self, request):

        if request.GET.get('family') == '6':
            family = 6
            denominator = 2 ** 64  # Count /64s for IPv6 rather than individual IPs
        else:
            family = 4
            denominator = 1

        rirs = []
        for rir in self.queryset:

            stats = {
                'total': 0,
                'active': 0,
                'reserved': 0,
                'deprecated': 0,
                'available': 0,
            }
            aggregate_list = Aggregate.objects.filter(family=family, rir=rir)
            for aggregate in aggregate_list:

                queryset = Prefix.objects.filter(prefix__net_contained_or_equal=str(aggregate.prefix))

                # Find all consumed space for each prefix status (we ignore containers for this purpose).
                active_prefixes = netaddr.cidr_merge([p.prefix for p in queryset.filter(status=PREFIX_STATUS_ACTIVE)])
                reserved_prefixes = netaddr.cidr_merge([p.prefix for p in queryset.filter(status=PREFIX_STATUS_RESERVED)])
                deprecated_prefixes = netaddr.cidr_merge([p.prefix for p in queryset.filter(status=PREFIX_STATUS_DEPRECATED)])

                # Find all available prefixes by subtracting each of the existing prefix sets from the aggregate prefix.
                available_prefixes = (
                    netaddr.IPSet([aggregate.prefix]) -
                    netaddr.IPSet(active_prefixes) -
                    netaddr.IPSet(reserved_prefixes) -
                    netaddr.IPSet(deprecated_prefixes)
                )

                # Add the size of each metric to the RIR total.
                stats['total'] += aggregate.prefix.size / denominator
                stats['active'] += netaddr.IPSet(active_prefixes).size / denominator
                stats['reserved'] += netaddr.IPSet(reserved_prefixes).size / denominator
                stats['deprecated'] += netaddr.IPSet(deprecated_prefixes).size / denominator
                stats['available'] += available_prefixes.size / denominator

            # Calculate the percentage of total space for each prefix status.
            total = float(stats['total'])
            stats['percentages'] = {
                'active': float('{:.2f}'.format(stats['active'] / total * 100)) if total else 0,
                'reserved': float('{:.2f}'.format(stats['reserved'] / total * 100)) if total else 0,
                'deprecated': float('{:.2f}'.format(stats['deprecated'] / total * 100)) if total else 0,
            }
            stats['percentages']['available'] = (
                100 -
                stats['percentages']['active'] -
                stats['percentages']['reserved'] -
                stats['percentages']['deprecated']
            )
            rir.stats = stats
            rirs.append(rir)

        return rirs

    def extra_context(self):

        totals = {
            'total': sum([rir.stats['total'] for rir in self.queryset]),
            'active': sum([rir.stats['active'] for rir in self.queryset]),
            'reserved': sum([rir.stats['reserved'] for rir in self.queryset]),
            'deprecated': sum([rir.stats['deprecated'] for rir in self.queryset]),
            'available': sum([rir.stats['available'] for rir in self.queryset]),
        }

        return {
            'totals': totals,
        }


class RIRCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipam.add_rir'
    model = RIR
    form_class = forms.RIRForm

    def get_return_url(self, request, obj):
        return reverse('ipam:rir_list')


class RIREditView(RIRCreateView):
    permission_required = 'ipam.change_rir'


class RIRBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipam.delete_rir'
    cls = RIR
    filter = filters.RIRFilter
    default_return_url = 'ipam:rir_list'


#
# Aggregates
#

class AggregateListView(ObjectListView):
    queryset = Aggregate.objects.select_related('rir').extra(select={
        'child_count': 'SELECT COUNT(*) FROM ipam_prefix WHERE ipam_prefix.prefix <<= ipam_aggregate.prefix',
    })
    filter = filters.AggregateFilter
    filter_form = forms.AggregateFilterForm
    table = tables.AggregateTable
    template_name = 'ipam/aggregate_list.html'

    def extra_context(self):
        ipv4_total = 0
        ipv6_total = 0

        for a in self.queryset:
            if a.prefix.version == 4:
                ipv4_total += a.prefix.size
            elif a.prefix.version == 6:
                ipv6_total += a.prefix.size / 2 ** 64

        return {
            'ipv4_total': ipv4_total,
            'ipv6_total': ipv6_total,
        }


class AggregateView(View):

    def get(self, request, pk):

        aggregate = get_object_or_404(Aggregate, pk=pk)

        # Find all child prefixes contained by this aggregate
        child_prefixes = Prefix.objects.filter(
            prefix__net_contained_or_equal=str(aggregate.prefix)
        ).select_related(
            'site', 'role'
        ).annotate_depth(
            limit=0
        )
        child_prefixes = add_available_prefixes(aggregate.prefix, child_prefixes)

        prefix_table = tables.PrefixTable(child_prefixes)
        if request.user.has_perm('ipam.change_prefix') or request.user.has_perm('ipam.delete_prefix'):
            prefix_table.base_columns['pk'].visible = True

        paginate = {
            'klass': EnhancedPaginator,
            'per_page': request.GET.get('per_page', settings.PAGINATE_COUNT)
        }
        RequestConfig(request, paginate).configure(prefix_table)

        # Compile permissions list for rendering the object table
        permissions = {
            'add': request.user.has_perm('ipam.add_prefix'),
            'change': request.user.has_perm('ipam.change_prefix'),
            'delete': request.user.has_perm('ipam.delete_prefix'),
        }

        return render(request, 'ipam/aggregate.html', {
            'aggregate': aggregate,
            'prefix_table': prefix_table,
            'permissions': permissions,
        })


class AggregateCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipam.add_aggregate'
    model = Aggregate
    form_class = forms.AggregateForm
    template_name = 'ipam/aggregate_edit.html'
    default_return_url = 'ipam:aggregate_list'


class AggregateEditView(AggregateCreateView):
    permission_required = 'ipam.change_aggregate'


class AggregateDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'ipam.delete_aggregate'
    model = Aggregate
    default_return_url = 'ipam:aggregate_list'


class AggregateBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'ipam.add_aggregate'
    model_form = forms.AggregateCSVForm
    table = tables.AggregateTable
    default_return_url = 'ipam:aggregate_list'


class AggregateBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'ipam.change_aggregate'
    cls = Aggregate
    filter = filters.AggregateFilter
    form = forms.AggregateBulkEditForm
    template_name = 'ipam/aggregate_bulk_edit.html'
    default_return_url = 'ipam:aggregate_list'


class AggregateBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipam.delete_aggregate'
    cls = Aggregate
    filter = filters.AggregateFilter
    default_return_url = 'ipam:aggregate_list'


#
# Prefix/VLAN roles
#

class RoleListView(ObjectListView):
    queryset = Role.objects.all()
    table = tables.RoleTable
    template_name = 'ipam/role_list.html'


class RoleCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipam.add_role'
    model = Role
    form_class = forms.RoleForm

    def get_return_url(self, request, obj):
        return reverse('ipam:role_list')


class RoleEditView(RoleCreateView):
    permission_required = 'ipam.change_role'


class RoleBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipam.delete_role'
    cls = Role
    default_return_url = 'ipam:role_list'


#
# Prefixes
#

class PrefixListView(ObjectListView):
    queryset = Prefix.objects.select_related('site', 'vrf__tenant', 'tenant', 'vlan', 'role')
    filter = filters.PrefixFilter
    filter_form = forms.PrefixFilterForm
    table = tables.PrefixTable
    template_name = 'ipam/prefix_list.html'

    def alter_queryset(self, request):
        # Show only top-level prefixes by default (unless searching)
        limit = None if request.GET.get('expand') or request.GET.get('q') else 0
        return self.queryset.annotate_depth(limit=limit)


class PrefixView(View):

    def get(self, request, pk):

        prefix = get_object_or_404(Prefix.objects.select_related(
            'vrf', 'site__region', 'tenant__group', 'vlan__group', 'role'
        ), pk=pk)

        try:
            aggregate = Aggregate.objects.get(prefix__net_contains_or_equals=str(prefix.prefix))
        except Aggregate.DoesNotExist:
            aggregate = None

        # Count child IP addresses
        ipaddress_count = IPAddress.objects.filter(
            vrf=prefix.vrf, address__net_host_contained=str(prefix.prefix)
        ).count()

        # Parent prefixes table
        parent_prefixes = Prefix.objects.filter(
            Q(vrf=prefix.vrf) | Q(vrf__isnull=True)
        ).filter(
            prefix__net_contains=str(prefix.prefix)
        ).select_related(
            'site', 'role'
        ).annotate_depth()
        parent_prefix_table = tables.PrefixBriefTable(parent_prefixes)
        parent_prefix_table.exclude = ('vrf',)

        # Duplicate prefixes table
        duplicate_prefixes = Prefix.objects.filter(
            vrf=prefix.vrf, prefix=str(prefix.prefix)
        ).exclude(
            pk=prefix.pk
        ).select_related(
            'site', 'role'
        )
        duplicate_prefix_table = tables.PrefixBriefTable(list(duplicate_prefixes))
        duplicate_prefix_table.exclude = ('vrf',)

        # Child prefixes table
        child_prefixes = Prefix.objects.filter(
            vrf=prefix.vrf, prefix__net_contained=str(prefix.prefix)
        ).select_related(
            'site', 'role'
        ).annotate_depth(limit=0)
        if child_prefixes:
            child_prefixes = add_available_prefixes(prefix.prefix, child_prefixes)
        child_prefix_table = tables.PrefixTable(child_prefixes)
        if request.user.has_perm('ipam.change_prefix') or request.user.has_perm('ipam.delete_prefix'):
            child_prefix_table.base_columns['pk'].visible = True

        paginate = {
            'klass': EnhancedPaginator,
            'per_page': request.GET.get('per_page', settings.PAGINATE_COUNT)
        }
        RequestConfig(request, paginate).configure(child_prefix_table)

        # Compile permissions list for rendering the object table
        permissions = {
            'add': request.user.has_perm('ipam.add_prefix'),
            'change': request.user.has_perm('ipam.change_prefix'),
            'delete': request.user.has_perm('ipam.delete_prefix'),
        }

        return render(request, 'ipam/prefix.html', {
            'prefix': prefix,
            'aggregate': aggregate,
            'ipaddress_count': ipaddress_count,
            'parent_prefix_table': parent_prefix_table,
            'child_prefix_table': child_prefix_table,
            'duplicate_prefix_table': duplicate_prefix_table,
            'permissions': permissions,
            'return_url': prefix.get_absolute_url(),
        })


class PrefixIPAddressesView(View):

    def get(self, request, pk):

        prefix = get_object_or_404(Prefix.objects.all(), pk=pk)

        # Find all IPAddresses belonging to this Prefix
        ipaddresses = IPAddress.objects.filter(
            vrf=prefix.vrf, address__net_host_contained=str(prefix.prefix)
        ).select_related(
            'vrf', 'interface__device', 'primary_ip4_for', 'primary_ip6_for'
        )
        ipaddresses = add_available_ipaddresses(prefix.prefix, ipaddresses, prefix.is_pool)

        ip_table = tables.IPAddressTable(ipaddresses)
        if request.user.has_perm('ipam.change_ipaddress') or request.user.has_perm('ipam.delete_ipaddress'):
            ip_table.base_columns['pk'].visible = True

        paginate = {
            'klass': EnhancedPaginator,
            'per_page': request.GET.get('per_page', settings.PAGINATE_COUNT)
        }
        RequestConfig(request, paginate).configure(ip_table)

        # Compile permissions list for rendering the object table
        permissions = {
            'add': request.user.has_perm('ipam.add_ipaddress'),
            'change': request.user.has_perm('ipam.change_ipaddress'),
            'delete': request.user.has_perm('ipam.delete_ipaddress'),
        }

        return render(request, 'ipam/prefix_ipaddresses.html', {
            'prefix': prefix,
            'ip_table': ip_table,
            'permissions': permissions,
            'bulk_querystring': 'vrf_id={}&parent={}'.format(prefix.vrf or '0', prefix.prefix),
        })


class PrefixCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipam.add_prefix'
    model = Prefix
    form_class = forms.PrefixForm
    template_name = 'ipam/prefix_edit.html'
    default_return_url = 'ipam:prefix_list'


class PrefixEditView(PrefixCreateView):
    permission_required = 'ipam.change_prefix'


class PrefixDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'ipam.delete_prefix'
    model = Prefix
    template_name = 'ipam/prefix_delete.html'
    default_return_url = 'ipam:prefix_list'


class PrefixBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'ipam.add_prefix'
    model_form = forms.PrefixCSVForm
    table = tables.PrefixTable
    default_return_url = 'ipam:prefix_list'


class PrefixBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'ipam.change_prefix'
    cls = Prefix
    filter = filters.PrefixFilter
    form = forms.PrefixBulkEditForm
    template_name = 'ipam/prefix_bulk_edit.html'
    default_return_url = 'ipam:prefix_list'


class PrefixBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipam.delete_prefix'
    cls = Prefix
    filter = filters.PrefixFilter
    default_return_url = 'ipam:prefix_list'


#
# IP addresses
#

class IPAddressListView(ObjectListView):
    queryset = IPAddress.objects.select_related('vrf__tenant', 'tenant', 'interface__device', 'nat_inside')
    filter = filters.IPAddressFilter
    filter_form = forms.IPAddressFilterForm
    table = tables.IPAddressTable
    template_name = 'ipam/ipaddress_list.html'


class IPAddressView(View):

    def get(self, request, pk):

        ipaddress = get_object_or_404(IPAddress.objects.select_related('interface__device'), pk=pk)

        # Parent prefixes table
        parent_prefixes = Prefix.objects.filter(
            vrf=ipaddress.vrf, prefix__net_contains=str(ipaddress.address.ip)
        ).select_related(
            'site', 'role'
        )
        parent_prefixes_table = tables.PrefixBriefTable(list(parent_prefixes))
        parent_prefixes_table.exclude = ('vrf',)

        # Duplicate IPs table
        duplicate_ips = IPAddress.objects.filter(
            vrf=ipaddress.vrf, address=str(ipaddress.address)
        ).exclude(
            pk=ipaddress.pk
        ).select_related(
            'interface__device', 'nat_inside'
        )
        duplicate_ips_table = tables.IPAddressBriefTable(list(duplicate_ips))

        # Related IP table
        related_ips = IPAddress.objects.select_related(
            'interface__device'
        ).exclude(
            address=str(ipaddress.address)
        ).filter(
            vrf=ipaddress.vrf, address__net_contained_or_equal=str(ipaddress.address)
        )
        related_ips_table = tables.IPAddressBriefTable(list(related_ips))

        return render(request, 'ipam/ipaddress.html', {
            'ipaddress': ipaddress,
            'parent_prefixes_table': parent_prefixes_table,
            'duplicate_ips_table': duplicate_ips_table,
            'related_ips_table': related_ips_table,
        })


class IPAddressCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipam.add_ipaddress'
    model = IPAddress
    form_class = forms.IPAddressForm
    template_name = 'ipam/ipaddress_edit.html'
    default_return_url = 'ipam:ipaddress_list'


class IPAddressEditView(IPAddressCreateView):
    permission_required = 'ipam.change_ipaddress'


class IPAddressDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'ipam.delete_ipaddress'
    model = IPAddress
    default_return_url = 'ipam:ipaddress_list'


class IPAddressBulkAddView(PermissionRequiredMixin, BulkAddView):
    permission_required = 'ipam.add_ipaddress'
    pattern_form = forms.IPAddressPatternForm
    model_form = forms.IPAddressBulkAddForm
    pattern_target = 'address'
    template_name = 'ipam/ipaddress_bulk_add.html'
    default_return_url = 'ipam:ipaddress_list'


class IPAddressBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'ipam.add_ipaddress'
    model_form = forms.IPAddressCSVForm
    table = tables.IPAddressTable
    default_return_url = 'ipam:ipaddress_list'

    def save_obj(self, obj):
        obj.save()

        # Update primary IP for device if needed. The Device must be updated directly in the database; otherwise we risk
        # overwriting a previous IP assignment from the same import (see #861).
        try:
            if obj.family == 4 and obj.primary_ip4_for:
                Device.objects.filter(pk=obj.primary_ip4_for.pk).update(primary_ip4=obj)
            elif obj.family == 6 and obj.primary_ip6_for:
                Device.objects.filter(pk=obj.primary_ip6_for.pk).update(primary_ip6=obj)
        except Device.DoesNotExist:
            pass


class IPAddressBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'ipam.change_ipaddress'
    cls = IPAddress
    filter = filters.IPAddressFilter
    form = forms.IPAddressBulkEditForm
    template_name = 'ipam/ipaddress_bulk_edit.html'
    default_return_url = 'ipam:ipaddress_list'


class IPAddressBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipam.delete_ipaddress'
    cls = IPAddress
    filter = filters.IPAddressFilter
    default_return_url = 'ipam:ipaddress_list'


#
# VLAN groups
#

class VLANGroupListView(ObjectListView):
    queryset = VLANGroup.objects.select_related('site').annotate(vlan_count=Count('vlans'))
    filter = filters.VLANGroupFilter
    filter_form = forms.VLANGroupFilterForm
    table = tables.VLANGroupTable
    template_name = 'ipam/vlangroup_list.html'


class VLANGroupCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipam.add_vlangroup'
    model = VLANGroup
    form_class = forms.VLANGroupForm

    def get_return_url(self, request, obj):
        return reverse('ipam:vlangroup_list')


class VLANGroupEditView(VLANGroupCreateView):
    permission_required = 'ipam.change_vlangroup'


class VLANGroupBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipam.delete_vlangroup'
    cls = VLANGroup
    filter = filters.VLANGroupFilter
    default_return_url = 'ipam:vlangroup_list'


#
# VLANs
#

class VLANListView(ObjectListView):
    queryset = VLAN.objects.select_related('site', 'group', 'tenant', 'role').prefetch_related('prefixes')
    filter = filters.VLANFilter
    filter_form = forms.VLANFilterForm
    table = tables.VLANTable
    template_name = 'ipam/vlan_list.html'


class VLANView(View):

    def get(self, request, pk):

        vlan = get_object_or_404(VLAN.objects.select_related(
            'site__region', 'tenant__group', 'role'
        ), pk=pk)
        prefixes = Prefix.objects.filter(vlan=vlan).select_related('vrf', 'site', 'role')
        prefix_table = tables.PrefixBriefTable(list(prefixes))
        prefix_table.exclude = ('vlan',)

        return render(request, 'ipam/vlan.html', {
            'vlan': vlan,
            'prefix_table': prefix_table,
        })


class VLANCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipam.add_vlan'
    model = VLAN
    form_class = forms.VLANForm
    template_name = 'ipam/vlan_edit.html'
    default_return_url = 'ipam:vlan_list'


class VLANEditView(VLANCreateView):
    permission_required = 'ipam.change_vlan'


class VLANDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'ipam.delete_vlan'
    model = VLAN
    default_return_url = 'ipam:vlan_list'


class VLANBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'ipam.add_vlan'
    model_form = forms.VLANCSVForm
    table = tables.VLANTable
    default_return_url = 'ipam:vlan_list'


class VLANBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'ipam.change_vlan'
    cls = VLAN
    filter = filters.VLANFilter
    form = forms.VLANBulkEditForm
    template_name = 'ipam/vlan_bulk_edit.html'
    default_return_url = 'ipam:vlan_list'


class VLANBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipam.delete_vlan'
    cls = VLAN
    filter = filters.VLANFilter
    default_return_url = 'ipam:vlan_list'


#
# Services
#

class ServiceCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipam.add_service'
    model = Service
    form_class = forms.ServiceForm
    template_name = 'ipam/service_edit.html'

    def alter_obj(self, obj, request, url_args, url_kwargs):
        if 'device' in url_kwargs:
            obj.device = get_object_or_404(Device, pk=url_kwargs['device'])
        return obj

    def get_return_url(self, request, obj):
        return obj.device.get_absolute_url()


class ServiceEditView(ServiceCreateView):
    permission_required = 'ipam.change_service'


class ServiceDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'ipam.delete_service'
    model = Service
