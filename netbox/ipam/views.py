import netaddr
from django_tables2 import RequestConfig

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render

from dcim.models import Device
from utilities.paginator import EnhancedPaginator
from utilities.views import (
    BulkDeleteView, BulkEditView, BulkImportView, ObjectDeleteView, ObjectEditView, ObjectListView,
)

from . import filters, forms, tables
from .models import Aggregate, IPAddress, Prefix, RIR, Role, VLAN, VLANGroup, VRF


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


def add_available_ipaddresses(prefix, ipaddress_list):
    """
    Annotate ranges of available IP addresses within a given prefix.
    """

    output = []
    prev_ip = None

    # Determine first and last usable IP
    if prefix.version == 6 or (prefix.version == 4 and prefix.prefixlen == 31):
        first_ip_in_prefix = netaddr.IPAddress(prefix.first)
    else:
        first_ip_in_prefix = netaddr.IPAddress(prefix.first + 1)
    if prefix.version == 6 or (prefix.version == 4 and prefix.prefixlen == 31):
        last_ip_in_prefix = netaddr.IPAddress(prefix.last)
    else:
        last_ip_in_prefix = netaddr.IPAddress(prefix.last - 1)

    if not ipaddress_list:
        return [(
            int(last_ip_in_prefix - first_ip_in_prefix + 1),
            '{}/{}'.format(first_ip_in_prefix, prefix.prefixlen)
        )]

    # Account for any available IPs before the first real IP
    if ipaddress_list[0].address.ip != first_ip_in_prefix:
        skipped_count = int(ipaddress_list[0].address.ip - first_ip_in_prefix)
        first_skipped = '{}/{}'.format(first_ip_in_prefix, prefix.prefixlen)
        output.append((skipped_count, first_skipped))

    # Iterate through existing IPs and annotate free ranges
    for ip in ipaddress_list:
        if prev_ip:
            skipped_count = int(ip.address.ip - prev_ip.address.ip - 1)
            if skipped_count:
                first_skipped = '{}/{}'.format(prev_ip.address.ip + 1, prefix.prefixlen)
                output.append((skipped_count, first_skipped))
        output.append(ip)
        prev_ip = ip

    # Include any remaining available IPs
    if prev_ip.address.ip != last_ip_in_prefix:
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
    edit_permissions = ['ipam.change_vrf', 'ipam.delete_vrf']
    template_name = 'ipam/vrf_list.html'


def vrf(request, pk):

    vrf = get_object_or_404(VRF.objects.all(), pk=pk)
    prefixes = Prefix.objects.filter(vrf=vrf)
    prefix_table = tables.PrefixBriefTable(prefixes)

    return render(request, 'ipam/vrf.html', {
        'vrf': vrf,
        'prefix_table': prefix_table,
    })


class VRFEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipam.change_vrf'
    model = VRF
    form_class = forms.VRFForm
    cancel_url = 'ipam:vrf_list'


class VRFDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'ipam.delete_vrf'
    model = VRF
    redirect_url = 'ipam:vrf_list'


class VRFBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'ipam.add_vrf'
    form = forms.VRFImportForm
    table = tables.VRFTable
    template_name = 'ipam/vrf_import.html'
    obj_list_url = 'ipam:vrf_list'


class VRFBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'ipam.change_vrf'
    cls = VRF
    form = forms.VRFBulkEditForm
    template_name = 'ipam/vrf_bulk_edit.html'
    default_redirect_url = 'ipam:vrf_list'

    def update_objects(self, pk_list, form):

        fields_to_update = {}
        if form.cleaned_data['tenant'] == 0:
            fields_to_update['tenant'] = None
        elif form.cleaned_data['tenant']:
            fields_to_update['tenant'] = form.cleaned_data['tenant']
        for field in ['description']:
            if form.cleaned_data[field]:
                fields_to_update[field] = form.cleaned_data[field]

        return self.cls.objects.filter(pk__in=pk_list).update(**fields_to_update)


class VRFBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipam.delete_vrf'
    cls = VRF
    default_redirect_url = 'ipam:vrf_list'


#
# RIRs
#

class RIRListView(ObjectListView):
    queryset = RIR.objects.annotate(aggregate_count=Count('aggregates'))
    table = tables.RIRTable
    edit_permissions = ['ipam.change_rir', 'ipam.delete_rir']
    template_name = 'ipam/rir_list.html'


class RIREditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipam.change_rir'
    model = RIR
    form_class = forms.RIRForm
    success_url = 'ipam:rir_list'
    cancel_url = 'ipam:rir_list'


class RIRBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipam.delete_rir'
    cls = RIR
    default_redirect_url = 'ipam:rir_list'


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
    edit_permissions = ['ipam.change_aggregate', 'ipam.delete_aggregate']
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


def aggregate(request, pk):

    aggregate = get_object_or_404(Aggregate, pk=pk)

    # Find all child prefixes contained by this aggregate
    child_prefixes = Prefix.objects.filter(prefix__net_contained_or_equal=str(aggregate.prefix))\
        .select_related('site', 'role').annotate_depth(limit=0)
    child_prefixes = add_available_prefixes(aggregate.prefix, child_prefixes)

    prefix_table = tables.PrefixTable(child_prefixes)
    prefix_table.model = Prefix
    if request.user.has_perm('ipam.change_prefix') or request.user.has_perm('ipam.delete_prefix'):
        prefix_table.base_columns['pk'].visible = True
    RequestConfig(request, paginate={'klass': EnhancedPaginator}).configure(prefix_table)

    return render(request, 'ipam/aggregate.html', {
        'aggregate': aggregate,
        'prefix_table': prefix_table,
    })


class AggregateEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipam.change_aggregate'
    model = Aggregate
    form_class = forms.AggregateForm
    cancel_url = 'ipam:aggregate_list'


class AggregateDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'ipam.delete_aggregate'
    model = Aggregate
    redirect_url = 'ipam:aggregate_list'


class AggregateBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'ipam.add_aggregate'
    form = forms.AggregateImportForm
    table = tables.AggregateTable
    template_name = 'ipam/aggregate_import.html'
    obj_list_url = 'ipam:aggregate_list'


class AggregateBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'ipam.change_aggregate'
    cls = Aggregate
    form = forms.AggregateBulkEditForm
    template_name = 'ipam/aggregate_bulk_edit.html'
    default_redirect_url = 'ipam:aggregate_list'

    def update_objects(self, pk_list, form):

        fields_to_update = {}
        for field in ['rir', 'date_added', 'description']:
            if form.cleaned_data[field]:
                fields_to_update[field] = form.cleaned_data[field]

        return self.cls.objects.filter(pk__in=pk_list).update(**fields_to_update)


class AggregateBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipam.delete_aggregate'
    cls = Aggregate
    default_redirect_url = 'ipam:aggregate_list'


#
# Prefix/VLAN roles
#

class RoleListView(ObjectListView):
    queryset = Role.objects.all()
    table = tables.RoleTable
    edit_permissions = ['ipam.change_role', 'ipam.delete_role']
    template_name = 'ipam/role_list.html'


class RoleEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipam.change_role'
    model = Role
    form_class = forms.RoleForm
    success_url = 'ipam:role_list'
    cancel_url = 'ipam:role_list'


class RoleBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipam.delete_role'
    cls = Role
    default_redirect_url = 'ipam:role_list'


#
# Prefixes
#

class PrefixListView(ObjectListView):
    queryset = Prefix.objects.select_related('site', 'vrf__tenant', 'role')
    filter = filters.PrefixFilter
    filter_form = forms.PrefixFilterForm
    table = tables.PrefixTable
    edit_permissions = ['ipam.change_prefix', 'ipam.delete_prefix']
    template_name = 'ipam/prefix_list.html'

    def alter_queryset(self, request):
        # Show only top-level prefixes by default (unless searching)
        limit = None if request.GET.get('expand') or request.GET.get('q') else 0
        return self.queryset.annotate_depth(limit=limit)


def prefix(request, pk):

    prefix = get_object_or_404(Prefix.objects.select_related('site', 'vlan', 'role'), pk=pk)

    try:
        aggregate = Aggregate.objects.get(prefix__net_contains_or_equals=str(prefix.prefix))
    except Aggregate.DoesNotExist:
        aggregate = None

    # Count child IP addresses
    ipaddress_count = IPAddress.objects.filter(vrf=prefix.vrf, address__net_contained_or_equal=str(prefix.prefix))\
        .count()

    # Parent prefixes table
    parent_prefixes = Prefix.objects.filter(Q(vrf=prefix.vrf) | Q(vrf__isnull=True))\
        .filter(prefix__net_contains=str(prefix.prefix))\
        .select_related('site', 'role').annotate_depth()
    parent_prefix_table = tables.PrefixBriefTable(parent_prefixes)

    # Duplicate prefixes table
    duplicate_prefixes = Prefix.objects.filter(vrf=prefix.vrf, prefix=str(prefix.prefix)).exclude(pk=prefix.pk)\
        .select_related('site', 'role')
    duplicate_prefix_table = tables.PrefixBriefTable(duplicate_prefixes)

    # Child prefixes table
    if prefix.vrf:
        # If the prefix is in a VRF, show child prefixes only within that VRF.
        child_prefixes = Prefix.objects.filter(vrf=prefix.vrf)
    else:
        # If the prefix is in the global table, show child prefixes from all VRFs.
        child_prefixes = Prefix.objects.all()
    child_prefixes = child_prefixes.filter(prefix__net_contained=str(prefix.prefix))\
        .select_related('site', 'role').annotate_depth(limit=0)
    if child_prefixes:
        child_prefixes = add_available_prefixes(prefix.prefix, child_prefixes)
    child_prefix_table = tables.PrefixTable(child_prefixes)
    child_prefix_table.model = Prefix
    if request.user.has_perm('ipam.change_prefix') or request.user.has_perm('ipam.delete_prefix'):
        child_prefix_table.base_columns['pk'].visible = True
    RequestConfig(request, paginate={'klass': EnhancedPaginator}).configure(child_prefix_table)

    return render(request, 'ipam/prefix.html', {
        'prefix': prefix,
        'aggregate': aggregate,
        'ipaddress_count': ipaddress_count,
        'parent_prefix_table': parent_prefix_table,
        'child_prefix_table': child_prefix_table,
        'duplicate_prefix_table': duplicate_prefix_table,
    })


class PrefixEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipam.change_prefix'
    model = Prefix
    form_class = forms.PrefixForm
    fields_initial = ['site', 'vrf', 'prefix']
    cancel_url = 'ipam:prefix_list'


class PrefixDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'ipam.delete_prefix'
    model = Prefix
    redirect_url = 'ipam:prefix_list'


class PrefixBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'ipam.add_prefix'
    form = forms.PrefixImportForm
    table = tables.PrefixTable
    template_name = 'ipam/prefix_import.html'
    obj_list_url = 'ipam:prefix_list'


class PrefixBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'ipam.change_prefix'
    cls = Prefix
    form = forms.PrefixBulkEditForm
    template_name = 'ipam/prefix_bulk_edit.html'
    default_redirect_url = 'ipam:prefix_list'

    def update_objects(self, pk_list, form):

        fields_to_update = {}
        for field in ['vrf', 'tenant']:
            if form.cleaned_data[field] == 0:
                fields_to_update[field] = None
            elif form.cleaned_data[field]:
                fields_to_update[field] = form.cleaned_data[field]
        for field in ['site', 'status', 'role', 'description']:
            if form.cleaned_data[field]:
                fields_to_update[field] = form.cleaned_data[field]

        return self.cls.objects.filter(pk__in=pk_list).update(**fields_to_update)


class PrefixBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipam.delete_prefix'
    cls = Prefix
    default_redirect_url = 'ipam:prefix_list'


def prefix_ipaddresses(request, pk):

    prefix = get_object_or_404(Prefix.objects.all(), pk=pk)

    # Find all IPAddresses belonging to this Prefix
    ipaddresses = IPAddress.objects.filter(vrf=prefix.vrf, address__net_contained_or_equal=str(prefix.prefix))\
        .select_related('vrf', 'interface__device', 'primary_ip4_for', 'primary_ip6_for')
    ipaddresses = add_available_ipaddresses(prefix.prefix, ipaddresses)

    ip_table = tables.IPAddressTable(ipaddresses)
    ip_table.model = IPAddress
    if request.user.has_perm('ipam.change_ipaddress') or request.user.has_perm('ipam.delete_ipaddress'):
        ip_table.base_columns['pk'].visible = True
    RequestConfig(request, paginate={'klass': EnhancedPaginator}).configure(ip_table)

    return render(request, 'ipam/prefix_ipaddresses.html', {
        'prefix': prefix,
        'ip_table': ip_table,
    })


#
# IP addresses
#

class IPAddressListView(ObjectListView):
    queryset = IPAddress.objects.select_related('vrf__tenant', 'interface__device')
    filter = filters.IPAddressFilter
    filter_form = forms.IPAddressFilterForm
    table = tables.IPAddressTable
    edit_permissions = ['ipam.change_ipaddress', 'ipam.delete_ipaddress']
    template_name = 'ipam/ipaddress_list.html'


def ipaddress(request, pk):

    ipaddress = get_object_or_404(IPAddress.objects.select_related('interface__device'), pk=pk)

    # Parent prefixes table
    parent_prefixes = Prefix.objects.filter(vrf=ipaddress.vrf, prefix__net_contains=str(ipaddress.address.ip))
    parent_prefixes_table = tables.PrefixBriefTable(parent_prefixes)

    # Duplicate IPs table
    duplicate_ips = IPAddress.objects.filter(vrf=ipaddress.vrf, address=str(ipaddress.address))\
        .exclude(pk=ipaddress.pk).select_related('interface__device', 'nat_inside')
    duplicate_ips_table = tables.IPAddressBriefTable(duplicate_ips)

    # Related IP table
    related_ips = IPAddress.objects.select_related('interface__device').exclude(address=str(ipaddress.address))\
        .filter(vrf=ipaddress.vrf, address__net_contained_or_equal=str(ipaddress.address))
    related_ips_table = tables.IPAddressBriefTable(related_ips)

    return render(request, 'ipam/ipaddress.html', {
        'ipaddress': ipaddress,
        'parent_prefixes_table': parent_prefixes_table,
        'duplicate_ips_table': duplicate_ips_table,
        'related_ips_table': related_ips_table,
    })


class IPAddressEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipam.change_ipaddress'
    model = IPAddress
    form_class = forms.IPAddressForm
    fields_initial = ['address', 'vrf']
    template_name = 'ipam/ipaddress_edit.html'
    cancel_url = 'ipam:ipaddress_list'


class IPAddressDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'ipam.delete_ipaddress'
    model = IPAddress
    redirect_url = 'ipam:ipaddress_list'


class IPAddressBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'ipam.add_ipaddress'
    form = forms.IPAddressImportForm
    table = tables.IPAddressTable
    template_name = 'ipam/ipaddress_import.html'
    obj_list_url = 'ipam:ipaddress_list'

    def save_obj(self, obj):
        obj.save()
        # Update primary IP for device if needed
        try:
            if obj.family == 4 and obj.primary_ip4_for:
                device = obj.primary_ip4_for
                device.primary_ip4 = obj
                device.save()
            elif obj.family == 6 and obj.primary_ip6_for:
                device = obj.primary_ip6_for
                device.primary_ip6 = obj
                device.save()
        except Device.DoesNotExist:
            pass


class IPAddressBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'ipam.change_ipaddress'
    cls = IPAddress
    form = forms.IPAddressBulkEditForm
    template_name = 'ipam/ipaddress_bulk_edit.html'
    default_redirect_url = 'ipam:ipaddress_list'

    def update_objects(self, pk_list, form):

        fields_to_update = {}
        for field in ['vrf', 'tenant']:
            if form.cleaned_data[field] == 0:
                fields_to_update[field] = None
            elif form.cleaned_data[field]:
                fields_to_update[field] = form.cleaned_data[field]
        for field in ['description']:
            if form.cleaned_data[field]:
                fields_to_update[field] = form.cleaned_data[field]

        return self.cls.objects.filter(pk__in=pk_list).update(**fields_to_update)


class IPAddressBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipam.delete_ipaddress'
    cls = IPAddress
    default_redirect_url = 'ipam:ipaddress_list'


#
# VLAN groups
#

class VLANGroupListView(ObjectListView):
    queryset = VLANGroup.objects.annotate(vlan_count=Count('vlans'))
    filter = filters.VLANGroupFilter
    filter_form = forms.VLANGroupFilterForm
    table = tables.VLANGroupTable
    edit_permissions = ['ipam.change_vlangroup', 'ipam.delete_vlangroup']
    template_name = 'ipam/vlangroup_list.html'


class VLANGroupEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipam.change_vlangroup'
    model = VLANGroup
    form_class = forms.VLANGroupForm
    cancel_url = 'ipam:vlangroup_list'


class VLANGroupBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipam.delete_vlangroup'
    cls = VLANGroup
    default_redirect_url = 'ipam:vlangroup_list'


#
# VLANs
#

class VLANListView(ObjectListView):
    queryset = VLAN.objects.select_related('site', 'role')
    filter = filters.VLANFilter
    filter_form = forms.VLANFilterForm
    table = tables.VLANTable
    edit_permissions = ['ipam.change_vlan', 'ipam.delete_vlan']
    template_name = 'ipam/vlan_list.html'


def vlan(request, pk):

    vlan = get_object_or_404(VLAN.objects.select_related('site', 'role'), pk=pk)
    prefixes = Prefix.objects.filter(vlan=vlan)
    prefix_table = tables.PrefixBriefTable(prefixes)

    return render(request, 'ipam/vlan.html', {
        'vlan': vlan,
        'prefix_table': prefix_table,
    })


class VLANEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipam.change_vlan'
    model = VLAN
    form_class = forms.VLANForm
    cancel_url = 'ipam:vlan_list'


class VLANDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'ipam.delete_vlan'
    model = VLAN
    redirect_url = 'ipam:vlan_list'


class VLANBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'ipam.add_vlan'
    form = forms.VLANImportForm
    table = tables.VLANTable
    template_name = 'ipam/vlan_import.html'
    obj_list_url = 'ipam:vlan_list'


class VLANBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'ipam.change_vlan'
    cls = VLAN
    form = forms.VLANBulkEditForm
    template_name = 'ipam/vlan_bulk_edit.html'
    default_redirect_url = 'ipam:vlan_list'

    def update_objects(self, pk_list, form):

        fields_to_update = {}
        if form.cleaned_data['tenant'] == 0:
            fields_to_update['tenant'] = None
        elif form.cleaned_data['tenant']:
            fields_to_update['tenant'] = form.cleaned_data['tenant']
        for field in ['site', 'group', 'status', 'role', 'description']:
            if form.cleaned_data[field]:
                fields_to_update[field] = form.cleaned_data[field]

        return self.cls.objects.filter(pk__in=pk_list).update(**fields_to_update)


class VLANBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipam.delete_vlan'
    cls = VLAN
    default_redirect_url = 'ipam:vlan_list'
