from __future__ import unicode_literals

import netaddr
from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View
from django_tables2 import RequestConfig

from dcim.models import Device, Interface
from utilities.paginator import EnhancedPaginator
from utilities.views import (
    BulkCreateView, BulkDeleteView, BulkEditView, BulkImportView, ObjectDeleteView, ObjectEditView, ObjectListView,
)
from virtualization.models import VirtualMachine
from . import filters, forms, tables
from .constants import IPADDRESS_ROLE_ANYCAST, PREFIX_STATUS_ACTIVE, PREFIX_STATUS_DEPRECATED, PREFIX_STATUS_RESERVED
from .models import Aggregate, IPAddress, Prefix, RIR, Role, Service, VLAN, VLANGroup, VRF


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


def add_available_vlans(vlan_group, vlans):
    """
    Create fake records for all gaps between used VLANs
    """
    MIN_VLAN = 1
    MAX_VLAN = 4094

    if not vlans:
        return [{'vid': MIN_VLAN, 'available': MAX_VLAN - MIN_VLAN + 1}]

    prev_vid = MAX_VLAN
    new_vlans = []
    for vlan in vlans:
        if vlan.vid - prev_vid > 1:
            new_vlans.append({'vid': prev_vid + 1, 'available': vlan.vid - prev_vid - 1})
        prev_vid = vlan.vid

    if vlans[0].vid > MIN_VLAN:
        new_vlans.append({'vid': MIN_VLAN, 'available': vlans[0].vid - MIN_VLAN})
    if prev_vid < MAX_VLAN:
        new_vlans.append({'vid': prev_vid + 1, 'available': MAX_VLAN - prev_vid})

    vlans = list(vlans) + new_vlans
    vlans.sort(key=lambda v: v.vid if type(v) == VLAN else v['vid'])

    return vlans


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
        prefix_table = tables.PrefixTable(
            list(Prefix.objects.filter(vrf=vrf).select_related('site', 'role')), orderable=False
        )
        prefix_table.exclude = ('vrf',)

        return render(request, 'ipam/vrf.html', {
            'vrf': vrf,
            'prefix_table': prefix_table,
        })


class VRFCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipam.add_vrf'
    model = VRF
    model_form = forms.VRFForm
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
    queryset = VRF.objects.select_related('tenant')
    filter = filters.VRFFilter
    table = tables.VRFTable
    form = forms.VRFBulkEditForm
    default_return_url = 'ipam:vrf_list'


class VRFBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipam.delete_vrf'
    queryset = VRF.objects.select_related('tenant')
    filter = filters.VRFFilter
    table = tables.VRFTable
    default_return_url = 'ipam:vrf_list'


#
# RIRs
#

class RIRListView(ObjectListView):
    queryset = RIR.objects.annotate(aggregate_count=Count('aggregates'))
    filter = filters.RIRFilter
    filter_form = forms.RIRFilterForm
    table = tables.RIRDetailTable
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
                active_prefixes = netaddr.cidr_merge(
                    [p.prefix for p in queryset.filter(status=PREFIX_STATUS_ACTIVE)]
                )
                reserved_prefixes = netaddr.cidr_merge(
                    [p.prefix for p in queryset.filter(status=PREFIX_STATUS_RESERVED)]
                )
                deprecated_prefixes = netaddr.cidr_merge(
                    [p.prefix for p in queryset.filter(status=PREFIX_STATUS_DEPRECATED)]
                )

                # Find all available prefixes by subtracting each of the existing prefix sets from the aggregate prefix.
                available_prefixes = (
                    netaddr.IPSet([aggregate.prefix]) -
                    netaddr.IPSet(active_prefixes) -
                    netaddr.IPSet(reserved_prefixes) -
                    netaddr.IPSet(deprecated_prefixes)
                )

                # Add the size of each metric to the RIR total.
                stats['total'] += int(aggregate.prefix.size / denominator)
                stats['active'] += int(netaddr.IPSet(active_prefixes).size / denominator)
                stats['reserved'] += int(netaddr.IPSet(reserved_prefixes).size / denominator)
                stats['deprecated'] += int(netaddr.IPSet(deprecated_prefixes).size / denominator)
                stats['available'] += int(available_prefixes.size / denominator)

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


class RIRCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipam.add_rir'
    model = RIR
    model_form = forms.RIRForm
    default_return_url = 'ipam:rir_list'


class RIREditView(RIRCreateView):
    permission_required = 'ipam.change_rir'


class RIRBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'ipam.add_rir'
    model_form = forms.RIRCSVForm
    table = tables.RIRTable
    default_return_url = 'ipam:rir_list'


class RIRBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipam.delete_rir'
    queryset = RIR.objects.annotate(aggregate_count=Count('aggregates'))
    filter = filters.RIRFilter
    table = tables.RIRTable
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
    table = tables.AggregateDetailTable
    template_name = 'ipam/aggregate_list.html'

    def extra_context(self):
        ipv4_total = 0
        ipv6_total = 0

        for aggregate in self.queryset:
            if aggregate.prefix.version == 6:
                # Report equivalent /64s for IPv6 to keep things sane
                ipv6_total += int(aggregate.prefix.size / 2 ** 64)
            else:
                ipv4_total += aggregate.prefix.size

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

        prefix_table = tables.PrefixDetailTable(child_prefixes)
        if request.user.has_perm('ipam.change_prefix') or request.user.has_perm('ipam.delete_prefix'):
            prefix_table.columns.show('pk')

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
    model_form = forms.AggregateForm
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
    queryset = Aggregate.objects.select_related('rir')
    filter = filters.AggregateFilter
    table = tables.AggregateTable
    form = forms.AggregateBulkEditForm
    default_return_url = 'ipam:aggregate_list'


class AggregateBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipam.delete_aggregate'
    queryset = Aggregate.objects.select_related('rir')
    filter = filters.AggregateFilter
    table = tables.AggregateTable
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
    model_form = forms.RoleForm
    default_return_url = 'ipam:role_list'


class RoleEditView(RoleCreateView):
    permission_required = 'ipam.change_role'


class RoleBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'ipam.add_role'
    model_form = forms.RoleCSVForm
    table = tables.RoleTable
    default_return_url = 'ipam:role_list'


class RoleBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipam.delete_role'
    queryset = Role.objects.all()
    table = tables.RoleTable
    default_return_url = 'ipam:role_list'


#
# Prefixes
#

class PrefixListView(ObjectListView):
    queryset = Prefix.objects.select_related('site', 'vrf__tenant', 'tenant', 'vlan', 'role')
    filter = filters.PrefixFilter
    filter_form = forms.PrefixFilterForm
    table = tables.PrefixDetailTable
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

        # Parent prefixes table
        parent_prefixes = Prefix.objects.filter(
            Q(vrf=prefix.vrf) | Q(vrf__isnull=True)
        ).filter(
            prefix__net_contains=str(prefix.prefix)
        ).select_related(
            'site', 'role'
        ).annotate_depth()
        parent_prefix_table = tables.PrefixTable(list(parent_prefixes), orderable=False)
        parent_prefix_table.exclude = ('vrf',)

        # Duplicate prefixes table
        duplicate_prefixes = Prefix.objects.filter(
            vrf=prefix.vrf, prefix=str(prefix.prefix)
        ).exclude(
            pk=prefix.pk
        ).select_related(
            'site', 'role'
        )
        duplicate_prefix_table = tables.PrefixTable(list(duplicate_prefixes), orderable=False)
        duplicate_prefix_table.exclude = ('vrf',)

        return render(request, 'ipam/prefix.html', {
            'prefix': prefix,
            'aggregate': aggregate,
            'parent_prefix_table': parent_prefix_table,
            'duplicate_prefix_table': duplicate_prefix_table,
        })


class PrefixPrefixesView(View):

    def get(self, request, pk):

        prefix = get_object_or_404(Prefix.objects.all(), pk=pk)

        # Child prefixes table
        child_prefixes = prefix.get_child_prefixes().select_related(
            'site', 'vlan', 'role',
        ).annotate_depth(limit=0)

        # Annotate available prefixes
        if child_prefixes:
            child_prefixes = add_available_prefixes(prefix.prefix, child_prefixes)

        prefix_table = tables.PrefixDetailTable(child_prefixes)
        if request.user.has_perm('ipam.change_prefix') or request.user.has_perm('ipam.delete_prefix'):
            prefix_table.columns.show('pk')

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

        return render(request, 'ipam/prefix_prefixes.html', {
            'prefix': prefix,
            'first_available_prefix': prefix.get_first_available_prefix(),
            'prefix_table': prefix_table,
            'permissions': permissions,
            'bulk_querystring': 'vrf_id={}&within={}'.format(prefix.vrf.pk if prefix.vrf else '0', prefix.prefix),
            'active_tab': 'prefixes',
        })


class PrefixIPAddressesView(View):

    def get(self, request, pk):

        prefix = get_object_or_404(Prefix.objects.all(), pk=pk)

        # Find all IPAddresses belonging to this Prefix
        ipaddresses = prefix.get_child_ips().select_related(
            'vrf', 'interface__device', 'primary_ip4_for', 'primary_ip6_for'
        )
        ipaddresses = add_available_ipaddresses(prefix.prefix, ipaddresses, prefix.is_pool)

        ip_table = tables.IPAddressTable(ipaddresses)
        if request.user.has_perm('ipam.change_ipaddress') or request.user.has_perm('ipam.delete_ipaddress'):
            ip_table.columns.show('pk')

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
            'first_available_ip': prefix.get_first_available_ip(),
            'ip_table': ip_table,
            'permissions': permissions,
            'bulk_querystring': 'vrf_id={}&parent={}'.format(prefix.vrf.pk if prefix.vrf else '0', prefix.prefix),
            'active_tab': 'ip-addresses',
        })


class PrefixCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipam.add_prefix'
    model = Prefix
    model_form = forms.PrefixForm
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
    queryset = Prefix.objects.select_related('site', 'vrf__tenant', 'tenant', 'vlan', 'role')
    filter = filters.PrefixFilter
    table = tables.PrefixTable
    form = forms.PrefixBulkEditForm
    default_return_url = 'ipam:prefix_list'


class PrefixBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipam.delete_prefix'
    queryset = Prefix.objects.select_related('site', 'vrf__tenant', 'tenant', 'vlan', 'role')
    filter = filters.PrefixFilter
    table = tables.PrefixTable
    default_return_url = 'ipam:prefix_list'


#
# IP addresses
#

class IPAddressListView(ObjectListView):
    queryset = IPAddress.objects.select_related(
        'vrf__tenant', 'tenant', 'nat_inside'
    ).prefetch_related(
        'interface__device', 'interface__virtual_machine'
    )
    filter = filters.IPAddressFilter
    filter_form = forms.IPAddressFilterForm
    table = tables.IPAddressDetailTable
    template_name = 'ipam/ipaddress_list.html'


class IPAddressView(View):

    def get(self, request, pk):

        ipaddress = get_object_or_404(IPAddress.objects.select_related('vrf__tenant', 'tenant'), pk=pk)

        # Parent prefixes table
        parent_prefixes = Prefix.objects.filter(
            vrf=ipaddress.vrf, prefix__net_contains=str(ipaddress.address.ip)
        ).select_related(
            'site', 'role'
        )
        parent_prefixes_table = tables.PrefixTable(list(parent_prefixes), orderable=False)
        parent_prefixes_table.exclude = ('vrf',)

        # Duplicate IPs table
        duplicate_ips = IPAddress.objects.filter(
            vrf=ipaddress.vrf, address=str(ipaddress.address)
        ).exclude(
            pk=ipaddress.pk
        ).select_related(
            'nat_inside'
        ).prefetch_related(
            'interface__device'
        )
        # Exclude anycast IPs if this IP is anycast
        if ipaddress.role == IPADDRESS_ROLE_ANYCAST:
            duplicate_ips = duplicate_ips.exclude(role=IPADDRESS_ROLE_ANYCAST)
        duplicate_ips_table = tables.IPAddressTable(list(duplicate_ips), orderable=False)

        # Related IP table
        related_ips = IPAddress.objects.prefetch_related(
            'interface__device'
        ).exclude(
            address=str(ipaddress.address)
        ).filter(
            vrf=ipaddress.vrf, address__net_contained_or_equal=str(ipaddress.address)
        )
        related_ips_table = tables.IPAddressTable(list(related_ips), orderable=False)

        return render(request, 'ipam/ipaddress.html', {
            'ipaddress': ipaddress,
            'parent_prefixes_table': parent_prefixes_table,
            'duplicate_ips_table': duplicate_ips_table,
            'related_ips_table': related_ips_table,
        })


class IPAddressCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipam.add_ipaddress'
    model = IPAddress
    model_form = forms.IPAddressForm
    template_name = 'ipam/ipaddress_edit.html'
    default_return_url = 'ipam:ipaddress_list'

    def alter_obj(self, obj, request, url_args, url_kwargs):

        interface_id = request.GET.get('interface')
        if interface_id:
            try:
                obj.interface = Interface.objects.get(pk=interface_id)
            except (ValueError, Interface.DoesNotExist):
                pass

        return obj


class IPAddressEditView(IPAddressCreateView):
    permission_required = 'ipam.change_ipaddress'


class IPAddressAssignView(PermissionRequiredMixin, View):
    """
    Search for IPAddresses to be assigned to an Interface.
    """
    permission_required = 'ipam.change_ipaddress'

    def dispatch(self, request, *args, **kwargs):

        # Redirect user if an interface has not been provided
        if 'interface' not in request.GET:
            return redirect('ipam:ipaddress_add')

        return super(IPAddressAssignView, self).dispatch(request, *args, **kwargs)

    def get(self, request):

        form = forms.IPAddressAssignForm()

        return render(request, 'ipam/ipaddress_assign.html', {
            'form': form,
            'return_url': request.GET.get('return_url', ''),
        })

    def post(self, request):

        form = forms.IPAddressAssignForm(request.POST)
        table = None

        if form.is_valid():

            queryset = IPAddress.objects.select_related(
                'vrf', 'tenant', 'interface__device', 'interface__virtual_machine'
            ).filter(
                vrf=form.cleaned_data['vrf'],
                address__istartswith=form.cleaned_data['address'],
            )[:100]  # Limit to 100 results
            table = tables.IPAddressAssignTable(queryset)

        return render(request, 'ipam/ipaddress_assign.html', {
            'form': form,
            'table': table,
            'return_url': request.GET.get('return_url', ''),
        })


class IPAddressDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'ipam.delete_ipaddress'
    model = IPAddress
    default_return_url = 'ipam:ipaddress_list'


class IPAddressBulkCreateView(PermissionRequiredMixin, BulkCreateView):
    permission_required = 'ipam.add_ipaddress'
    form = forms.IPAddressBulkCreateForm
    model_form = forms.IPAddressBulkAddForm
    pattern_target = 'address'
    template_name = 'ipam/ipaddress_bulk_add.html'
    default_return_url = 'ipam:ipaddress_list'


class IPAddressBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'ipam.add_ipaddress'
    model_form = forms.IPAddressCSVForm
    table = tables.IPAddressTable
    default_return_url = 'ipam:ipaddress_list'


class IPAddressBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'ipam.change_ipaddress'
    queryset = IPAddress.objects.select_related('vrf__tenant', 'tenant').prefetch_related('interface__device')
    filter = filters.IPAddressFilter
    table = tables.IPAddressTable
    form = forms.IPAddressBulkEditForm
    default_return_url = 'ipam:ipaddress_list'


class IPAddressBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipam.delete_ipaddress'
    queryset = IPAddress.objects.select_related('vrf__tenant', 'tenant').prefetch_related('interface__device')
    filter = filters.IPAddressFilter
    table = tables.IPAddressTable
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
    model_form = forms.VLANGroupForm
    default_return_url = 'ipam:vlangroup_list'


class VLANGroupEditView(VLANGroupCreateView):
    permission_required = 'ipam.change_vlangroup'


class VLANGroupBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'ipam.add_vlangroup'
    model_form = forms.VLANGroupCSVForm
    table = tables.VLANGroupTable
    default_return_url = 'ipam:vlangroup_list'


class VLANGroupBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipam.delete_vlangroup'
    queryset = VLANGroup.objects.select_related('site').annotate(vlan_count=Count('vlans'))
    filter = filters.VLANGroupFilter
    table = tables.VLANGroupTable
    default_return_url = 'ipam:vlangroup_list'


class VLANGroupVLANsView(View):
    def get(self, request, pk):

        vlan_group = get_object_or_404(VLANGroup.objects.all(), pk=pk)

        vlans = VLAN.objects.filter(group_id=pk)
        vlans = add_available_vlans(vlan_group, vlans)

        vlan_table = tables.VLANDetailTable(vlans)
        if request.user.has_perm('ipam.change_vlan') or request.user.has_perm('ipam.delete_vlan'):
            vlan_table.columns.show('pk')
        vlan_table.columns.hide('site')
        vlan_table.columns.hide('group')

        paginate = {
            'klass': EnhancedPaginator,
            'per_page': request.GET.get('per_page', settings.PAGINATE_COUNT)
        }
        RequestConfig(request, paginate).configure(vlan_table)

        # Compile permissions list for rendering the object table
        permissions = {
            'add': request.user.has_perm('ipam.add_vlan'),
            'change': request.user.has_perm('ipam.change_vlan'),
            'delete': request.user.has_perm('ipam.delete_vlan'),
        }

        return render(request, 'ipam/vlangroup_vlans.html', {
            'vlan_group': vlan_group,
            'first_available_vlan': vlan_group.get_next_available_vid(),
            'vlan_table': vlan_table,
            'permissions': permissions,
        })


#
# VLANs
#

class VLANListView(ObjectListView):
    queryset = VLAN.objects.select_related('site', 'group', 'tenant', 'role').prefetch_related('prefixes')
    filter = filters.VLANFilter
    filter_form = forms.VLANFilterForm
    table = tables.VLANDetailTable
    template_name = 'ipam/vlan_list.html'


class VLANView(View):

    def get(self, request, pk):

        vlan = get_object_or_404(VLAN.objects.select_related(
            'site__region', 'tenant__group', 'role'
        ), pk=pk)
        prefixes = Prefix.objects.filter(vlan=vlan).select_related('vrf', 'site', 'role')
        prefix_table = tables.PrefixTable(list(prefixes), orderable=False)
        prefix_table.exclude = ('vlan',)

        return render(request, 'ipam/vlan.html', {
            'vlan': vlan,
            'prefix_table': prefix_table,
        })


class VLANMembersView(View):

    def get(self, request, pk):

        vlan = get_object_or_404(VLAN.objects.all(), pk=pk)
        members = vlan.get_members().select_related('device', 'virtual_machine')

        members_table = tables.VLANMemberTable(members)

        paginate = {
            'klass': EnhancedPaginator,
            'per_page': request.GET.get('per_page', settings.PAGINATE_COUNT)
        }
        RequestConfig(request, paginate).configure(members_table)

        return render(request, 'ipam/vlan_members.html', {
            'vlan': vlan,
            'members_table': members_table,
            'active_tab': 'members',
        })


class VLANCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipam.add_vlan'
    model = VLAN
    model_form = forms.VLANForm
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
    queryset = VLAN.objects.select_related('site', 'group', 'tenant', 'role')
    filter = filters.VLANFilter
    table = tables.VLANTable
    form = forms.VLANBulkEditForm
    default_return_url = 'ipam:vlan_list'


class VLANBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipam.delete_vlan'
    queryset = VLAN.objects.select_related('site', 'group', 'tenant', 'role')
    filter = filters.VLANFilter
    table = tables.VLANTable
    default_return_url = 'ipam:vlan_list'


#
# Services
#

class ServiceListView(ObjectListView):
    queryset = Service.objects.select_related('device', 'virtual_machine')
    filter = filters.ServiceFilter
    filter_form = forms.ServiceFilterForm
    table = tables.ServiceTable
    template_name = 'ipam/service_list.html'


class ServiceView(View):

    def get(self, request, pk):

        service = get_object_or_404(Service, pk=pk)

        return render(request, 'ipam/service.html', {
            'service': service,
        })


class ServiceCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipam.add_service'
    model = Service
    model_form = forms.ServiceForm
    template_name = 'ipam/service_edit.html'

    def alter_obj(self, obj, request, url_args, url_kwargs):
        if 'device' in url_kwargs:
            obj.device = get_object_or_404(Device, pk=url_kwargs['device'])
        elif 'virtualmachine' in url_kwargs:
            obj.virtual_machine = get_object_or_404(VirtualMachine, pk=url_kwargs['virtualmachine'])
        return obj

    def get_return_url(self, request, service):
        return service.parent.get_absolute_url()


class ServiceEditView(ServiceCreateView):
    permission_required = 'ipam.change_service'


class ServiceDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'ipam.delete_service'
    model = Service


class ServiceBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'ipam.change_service'
    queryset = Service.objects.select_related('device', 'virtual_machine')
    filter = filters.ServiceFilter
    table = tables.ServiceTable
    form = forms.ServiceBulkEditForm
    default_return_url = 'ipam:service_list'


class ServiceBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipam.delete_service'
    queryset = Service.objects.select_related('device', 'virtual_machine')
    filter = filters.ServiceFilter
    table = tables.ServiceTable
    default_return_url = 'ipam:service_list'
