import netaddr
from django.conf import settings
from django.db.models import Count, Prefetch
from django.db.models.expressions import RawSQL
from django.shortcuts import get_object_or_404, redirect, render
from django_tables2 import RequestConfig

from dcim.models import Device, Interface
from utilities.paginator import EnhancedPaginator
from utilities.utils import get_subquery
from utilities.views import (
    BulkCreateView, BulkDeleteView, BulkEditView, BulkImportView, ObjectView, ObjectDeleteView, ObjectEditView,
    ObjectListView,
)
from virtualization.models import VirtualMachine, VMInterface
from . import filters, forms, tables
from .choices import *
from .constants import *
from .models import Aggregate, IPAddress, Prefix, RIR, Role, Service, VLAN, VLANGroup, VRF
from .utils import add_available_ipaddresses, add_available_prefixes, add_available_vlans


#
# VRFs
#

class VRFListView(ObjectListView):
    queryset = VRF.objects.prefetch_related('tenant')
    filterset = filters.VRFFilterSet
    filterset_form = forms.VRFFilterForm
    table = tables.VRFTable


class VRFView(ObjectView):
    queryset = VRF.objects.all()

    def get(self, request, pk):

        vrf = get_object_or_404(self.queryset, pk=pk)
        prefix_count = Prefix.objects.restrict(request.user, 'view').filter(vrf=vrf).count()

        return render(request, 'ipam/vrf.html', {
            'vrf': vrf,
            'prefix_count': prefix_count,
        })


class VRFEditView(ObjectEditView):
    queryset = VRF.objects.all()
    model_form = forms.VRFForm
    template_name = 'ipam/vrf_edit.html'


class VRFDeleteView(ObjectDeleteView):
    queryset = VRF.objects.all()


class VRFBulkImportView(BulkImportView):
    queryset = VRF.objects.all()
    model_form = forms.VRFCSVForm
    table = tables.VRFTable


class VRFBulkEditView(BulkEditView):
    queryset = VRF.objects.prefetch_related('tenant')
    filterset = filters.VRFFilterSet
    table = tables.VRFTable
    form = forms.VRFBulkEditForm


class VRFBulkDeleteView(BulkDeleteView):
    queryset = VRF.objects.prefetch_related('tenant')
    filterset = filters.VRFFilterSet
    table = tables.VRFTable


#
# RIRs
#

class RIRListView(ObjectListView):
    queryset = RIR.objects.annotate(aggregate_count=Count('aggregates')).order_by(*RIR._meta.ordering)
    filterset = filters.RIRFilterSet
    filterset_form = forms.RIRFilterForm
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
            aggregate_list = Aggregate.objects.restrict(request.user).filter(prefix__family=family, rir=rir)
            for aggregate in aggregate_list:

                queryset = Prefix.objects.restrict(request.user).filter(
                    prefix__net_contained_or_equal=str(aggregate.prefix)
                )

                # Find all consumed space for each prefix status (we ignore containers for this purpose).
                active_prefixes = netaddr.cidr_merge(
                    [p.prefix for p in queryset.filter(status=PrefixStatusChoices.STATUS_ACTIVE)]
                )
                reserved_prefixes = netaddr.cidr_merge(
                    [p.prefix for p in queryset.filter(status=PrefixStatusChoices.STATUS_RESERVED)]
                )
                deprecated_prefixes = netaddr.cidr_merge(
                    [p.prefix for p in queryset.filter(status=PrefixStatusChoices.STATUS_DEPRECATED)]
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


class RIREditView(ObjectEditView):
    queryset = RIR.objects.all()
    model_form = forms.RIRForm


class RIRDeleteView(ObjectDeleteView):
    queryset = RIR.objects.all()


class RIRBulkImportView(BulkImportView):
    queryset = RIR.objects.all()
    model_form = forms.RIRCSVForm
    table = tables.RIRTable


class RIRBulkDeleteView(BulkDeleteView):
    queryset = RIR.objects.annotate(aggregate_count=Count('aggregates')).order_by(*RIR._meta.ordering)
    filterset = filters.RIRFilterSet
    table = tables.RIRTable


#
# Aggregates
#

class AggregateListView(ObjectListView):
    queryset = Aggregate.objects.prefetch_related('rir').annotate(
        child_count=RawSQL('SELECT COUNT(*) FROM ipam_prefix WHERE ipam_prefix.prefix <<= ipam_aggregate.prefix', ())
    ).order_by(*Aggregate._meta.ordering)
    filterset = filters.AggregateFilterSet
    filterset_form = forms.AggregateFilterForm
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


class AggregateView(ObjectView):
    queryset = Aggregate.objects.all()

    def get(self, request, pk):

        aggregate = get_object_or_404(self.queryset, pk=pk)

        # Find all child prefixes contained by this aggregate
        child_prefixes = Prefix.objects.restrict(request.user, 'view').filter(
            prefix__net_contained_or_equal=str(aggregate.prefix)
        ).prefetch_related(
            'site', 'role'
        ).annotate_depth(
            limit=0
        )

        # Add available prefixes to the table if requested
        if request.GET.get('show_available', 'true') == 'true':
            child_prefixes = add_available_prefixes(aggregate.prefix, child_prefixes)

        prefix_table = tables.PrefixDetailTable(child_prefixes)
        if request.user.has_perm('ipam.change_prefix') or request.user.has_perm('ipam.delete_prefix'):
            prefix_table.columns.show('pk')

        paginate = {
            'paginator_class': EnhancedPaginator,
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
            'show_available': request.GET.get('show_available', 'true') == 'true',
        })


class AggregateEditView(ObjectEditView):
    queryset = Aggregate.objects.all()
    model_form = forms.AggregateForm
    template_name = 'ipam/aggregate_edit.html'


class AggregateDeleteView(ObjectDeleteView):
    queryset = Aggregate.objects.all()


class AggregateBulkImportView(BulkImportView):
    queryset = Aggregate.objects.all()
    model_form = forms.AggregateCSVForm
    table = tables.AggregateTable


class AggregateBulkEditView(BulkEditView):
    queryset = Aggregate.objects.prefetch_related('rir')
    filterset = filters.AggregateFilterSet
    table = tables.AggregateTable
    form = forms.AggregateBulkEditForm


class AggregateBulkDeleteView(BulkDeleteView):
    queryset = Aggregate.objects.prefetch_related('rir')
    filterset = filters.AggregateFilterSet
    table = tables.AggregateTable


#
# Prefix/VLAN roles
#

class RoleListView(ObjectListView):
    queryset = Role.objects.annotate(
        prefix_count=get_subquery(Prefix, 'role'),
        vlan_count=get_subquery(VLAN, 'role')
    )
    table = tables.RoleTable


class RoleEditView(ObjectEditView):
    queryset = Role.objects.all()
    model_form = forms.RoleForm


class RoleDeleteView(ObjectDeleteView):
    queryset = Role.objects.all()


class RoleBulkImportView(BulkImportView):
    queryset = Role.objects.all()
    model_form = forms.RoleCSVForm
    table = tables.RoleTable


class RoleBulkDeleteView(BulkDeleteView):
    queryset = Role.objects.all()
    table = tables.RoleTable


#
# Prefixes
#

class PrefixListView(ObjectListView):
    queryset = Prefix.objects.prefetch_related('site', 'vrf__tenant', 'tenant', 'vlan', 'role')
    filterset = filters.PrefixFilterSet
    filterset_form = forms.PrefixFilterForm
    table = tables.PrefixDetailTable
    template_name = 'ipam/prefix_list.html'

    def alter_queryset(self, request):
        # Show only top-level prefixes by default (unless searching)
        limit = None if request.GET.get('expand') or request.GET.get('q') else 0
        return self.queryset.annotate_depth(limit=limit)


class PrefixView(ObjectView):
    queryset = Prefix.objects.prefetch_related('vrf', 'site__region', 'tenant__group', 'vlan__group', 'role')

    def get(self, request, pk):

        prefix = get_object_or_404(self.queryset, pk=pk)

        try:
            aggregate = Aggregate.objects.restrict(request.user, 'view').get(
                prefix__net_contains_or_equals=str(prefix.prefix)
            )
        except Aggregate.DoesNotExist:
            aggregate = None

        # Parent prefixes table
        parent_prefixes = Prefix.objects.restrict(request.user, 'view').filter(
            Q(vrf=prefix.vrf) | Q(vrf__isnull=True)
        ).filter(
            prefix__net_contains=str(prefix.prefix)
        ).prefetch_related(
            'site', 'role'
        ).annotate_depth()
        parent_prefix_table = tables.PrefixTable(list(parent_prefixes), orderable=False)
        parent_prefix_table.exclude = ('vrf',)

        # Duplicate prefixes table
        duplicate_prefixes = Prefix.objects.restrict(request.user, 'view').filter(
            vrf=prefix.vrf, prefix=str(prefix.prefix)
        ).exclude(
            pk=prefix.pk
        ).prefetch_related(
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


class PrefixPrefixesView(ObjectView):
    queryset = Prefix.objects.all()

    def get(self, request, pk):

        prefix = get_object_or_404(self.queryset, pk=pk)

        # Child prefixes table
        child_prefixes = prefix.get_child_prefixes().restrict(request.user, 'view').prefetch_related(
            'site', 'vlan', 'role',
        ).annotate_depth(limit=0)

        # Add available prefixes to the table if requested
        if child_prefixes and request.GET.get('show_available', 'true') == 'true':
            child_prefixes = add_available_prefixes(prefix.prefix, child_prefixes)

        prefix_table = tables.PrefixDetailTable(child_prefixes)
        if request.user.has_perm('ipam.change_prefix') or request.user.has_perm('ipam.delete_prefix'):
            prefix_table.columns.show('pk')

        paginate = {
            'paginator_class': EnhancedPaginator,
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
            'show_available': request.GET.get('show_available', 'true') == 'true',
        })


class PrefixIPAddressesView(ObjectView):
    queryset = Prefix.objects.all()

    def get(self, request, pk):

        prefix = get_object_or_404(self.queryset, pk=pk)

        # Find all IPAddresses belonging to this Prefix
        ipaddresses = prefix.get_child_ips().restrict(request.user, 'view').prefetch_related(
            'vrf', 'primary_ip4_for', 'primary_ip6_for'
        )

        # Add available IP addresses to the table if requested
        if request.GET.get('show_available', 'true') == 'true':
            ipaddresses = add_available_ipaddresses(prefix.prefix, ipaddresses, prefix.is_pool)

        ip_table = tables.IPAddressTable(ipaddresses)
        if request.user.has_perm('ipam.change_ipaddress') or request.user.has_perm('ipam.delete_ipaddress'):
            ip_table.columns.show('pk')

        paginate = {
            'paginator_class': EnhancedPaginator,
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
            'show_available': request.GET.get('show_available', 'true') == 'true',
        })


class PrefixEditView(ObjectEditView):
    queryset = Prefix.objects.all()
    model_form = forms.PrefixForm
    template_name = 'ipam/prefix_edit.html'


class PrefixDeleteView(ObjectDeleteView):
    queryset = Prefix.objects.all()
    template_name = 'ipam/prefix_delete.html'


class PrefixBulkImportView(BulkImportView):
    queryset = Prefix.objects.all()
    model_form = forms.PrefixCSVForm
    table = tables.PrefixTable


class PrefixBulkEditView(BulkEditView):
    queryset = Prefix.objects.prefetch_related('site', 'vrf__tenant', 'tenant', 'vlan', 'role')
    filterset = filters.PrefixFilterSet
    table = tables.PrefixTable
    form = forms.PrefixBulkEditForm


class PrefixBulkDeleteView(BulkDeleteView):
    queryset = Prefix.objects.prefetch_related('site', 'vrf__tenant', 'tenant', 'vlan', 'role')
    filterset = filters.PrefixFilterSet
    table = tables.PrefixTable


#
# IP addresses
#

class IPAddressListView(ObjectListView):
    queryset = IPAddress.objects.prefetch_related(
        'vrf__tenant', 'tenant', 'nat_inside'
    )
    filterset = filters.IPAddressFilterSet
    filterset_form = forms.IPAddressFilterForm
    table = tables.IPAddressDetailTable


class IPAddressView(ObjectView):
    queryset = IPAddress.objects.prefetch_related('vrf__tenant', 'tenant')

    def get(self, request, pk):

        ipaddress = get_object_or_404(self.queryset, pk=pk)

        # Parent prefixes table
        parent_prefixes = Prefix.objects.restrict(request.user, 'view').filter(
            vrf=ipaddress.vrf, prefix__net_contains=str(ipaddress.address.ip)
        ).prefetch_related(
            'site', 'role'
        )
        parent_prefixes_table = tables.PrefixTable(list(parent_prefixes), orderable=False)
        parent_prefixes_table.exclude = ('vrf',)

        # Duplicate IPs table
        duplicate_ips = IPAddress.objects.restrict(request.user, 'view').filter(
            vrf=ipaddress.vrf, address=str(ipaddress.address)
        ).exclude(
            pk=ipaddress.pk
        ).prefetch_related(
            'nat_inside'
        )
        # Exclude anycast IPs if this IP is anycast
        if ipaddress.role == IPAddressRoleChoices.ROLE_ANYCAST:
            duplicate_ips = duplicate_ips.exclude(role=IPAddressRoleChoices.ROLE_ANYCAST)
        duplicate_ips_table = tables.IPAddressTable(list(duplicate_ips), orderable=False)

        # Related IP table
        related_ips = IPAddress.objects.restrict(request.user, 'view').exclude(
            address=str(ipaddress.address)
        ).filter(
            vrf=ipaddress.vrf, address__net_contained_or_equal=str(ipaddress.address)
        )
        related_ips_table = tables.IPAddressTable(related_ips, orderable=False)

        paginate = {
            'paginator_class': EnhancedPaginator,
            'per_page': request.GET.get('per_page', settings.PAGINATE_COUNT)
        }
        RequestConfig(request, paginate).configure(related_ips_table)

        return render(request, 'ipam/ipaddress.html', {
            'ipaddress': ipaddress,
            'parent_prefixes_table': parent_prefixes_table,
            'duplicate_ips_table': duplicate_ips_table,
            'related_ips_table': related_ips_table,
        })


class IPAddressEditView(ObjectEditView):
    queryset = IPAddress.objects.all()
    model_form = forms.IPAddressForm
    template_name = 'ipam/ipaddress_edit.html'

    def alter_obj(self, obj, request, url_args, url_kwargs):

        if 'interface' in request.GET:
            try:
                obj.assigned_object = Interface.objects.get(pk=request.GET['interface'])
            except (ValueError, Interface.DoesNotExist):
                pass

        elif 'vminterface' in request.GET:
            try:
                obj.assigned_object = VMInterface.objects.get(pk=request.GET['vminterface'])
            except (ValueError, VMInterface.DoesNotExist):
                pass

        return obj


class IPAddressAssignView(ObjectView):
    """
    Search for IPAddresses to be assigned to an Interface.
    """
    queryset = IPAddress.objects.all()

    def dispatch(self, request, *args, **kwargs):

        # Redirect user if an interface has not been provided
        if 'interface' not in request.GET:
            return redirect('ipam:ipaddress_add')

        return super().dispatch(request, *args, **kwargs)

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

            addresses = self.queryset.prefetch_related('vrf', 'tenant')
            # Limit to 100 results
            addresses = filters.IPAddressFilterSet(request.POST, addresses).qs[:100]
            table = tables.IPAddressAssignTable(addresses)

        return render(request, 'ipam/ipaddress_assign.html', {
            'form': form,
            'table': table,
            'return_url': request.GET.get('return_url', ''),
        })


class IPAddressDeleteView(ObjectDeleteView):
    queryset = IPAddress.objects.all()


class IPAddressBulkCreateView(BulkCreateView):
    queryset = IPAddress.objects.all()
    form = forms.IPAddressBulkCreateForm
    model_form = forms.IPAddressBulkAddForm
    pattern_target = 'address'
    template_name = 'ipam/ipaddress_bulk_add.html'


class IPAddressBulkImportView(BulkImportView):
    queryset = IPAddress.objects.all()
    model_form = forms.IPAddressCSVForm
    table = tables.IPAddressTable


class IPAddressBulkEditView(BulkEditView):
    queryset = IPAddress.objects.prefetch_related('vrf__tenant', 'tenant')
    filterset = filters.IPAddressFilterSet
    table = tables.IPAddressTable
    form = forms.IPAddressBulkEditForm


class IPAddressBulkDeleteView(BulkDeleteView):
    queryset = IPAddress.objects.prefetch_related('vrf__tenant', 'tenant')
    filterset = filters.IPAddressFilterSet
    table = tables.IPAddressTable


#
# VLAN groups
#

class VLANGroupListView(ObjectListView):
    queryset = VLANGroup.objects.prefetch_related('site').annotate(
        vlan_count=Count('vlans')
    ).order_by(*VLANGroup._meta.ordering)
    filterset = filters.VLANGroupFilterSet
    filterset_form = forms.VLANGroupFilterForm
    table = tables.VLANGroupTable


class VLANGroupEditView(ObjectEditView):
    queryset = VLANGroup.objects.all()
    model_form = forms.VLANGroupForm


class VLANGroupDeleteView(ObjectDeleteView):
    queryset = VLANGroup.objects.all()


class VLANGroupBulkImportView(BulkImportView):
    queryset = VLANGroup.objects.all()
    model_form = forms.VLANGroupCSVForm
    table = tables.VLANGroupTable


class VLANGroupBulkDeleteView(BulkDeleteView):
    queryset = VLANGroup.objects.prefetch_related('site').annotate(
        vlan_count=Count('vlans')
    ).order_by(*VLANGroup._meta.ordering)
    filterset = filters.VLANGroupFilterSet
    table = tables.VLANGroupTable


class VLANGroupVLANsView(ObjectView):
    queryset = VLANGroup.objects.all()

    def get(self, request, pk):
        vlan_group = get_object_or_404(self.queryset, pk=pk)

        vlans = VLAN.objects.restrict(request.user, 'view').filter(group_id=pk).prefetch_related(
            Prefetch('prefixes', queryset=Prefix.objects.restrict(request.user))
        )
        vlans = add_available_vlans(vlan_group, vlans)

        vlan_table = tables.VLANDetailTable(vlans)
        if request.user.has_perm('ipam.change_vlan') or request.user.has_perm('ipam.delete_vlan'):
            vlan_table.columns.show('pk')
        vlan_table.columns.hide('site')
        vlan_table.columns.hide('group')

        paginate = {
            'paginator_class': EnhancedPaginator,
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
    queryset = VLAN.objects.prefetch_related(
        Prefetch('prefixes', Prefix.objects.unrestricted()),
        'site', 'group', 'tenant', 'role'
    )
    filterset = filters.VLANFilterSet
    filterset_form = forms.VLANFilterForm
    table = tables.VLANDetailTable


class VLANView(ObjectView):
    queryset = VLAN.objects.prefetch_related('site__region', 'tenant__group', 'role')

    def get(self, request, pk):

        vlan = get_object_or_404(self.queryset, pk=pk)
        prefixes = Prefix.objects.restrict(request.user, 'view').filter(vlan=vlan).prefetch_related(
            'vrf', 'site', 'role'
        )
        prefix_table = tables.PrefixTable(list(prefixes), orderable=False)
        prefix_table.exclude = ('vlan',)

        return render(request, 'ipam/vlan.html', {
            'vlan': vlan,
            'prefix_table': prefix_table,
        })


class VLANMembersView(ObjectView):
    queryset = VLAN.objects.all()

    def get(self, request, pk):

        vlan = get_object_or_404(self.queryset, pk=pk)
        members = vlan.get_members().restrict(request.user, 'view').prefetch_related('device', 'virtual_machine')

        members_table = tables.VLANMemberTable(members)

        paginate = {
            'paginator_class': EnhancedPaginator,
            'per_page': request.GET.get('per_page', settings.PAGINATE_COUNT)
        }
        RequestConfig(request, paginate).configure(members_table)

        return render(request, 'ipam/vlan_members.html', {
            'vlan': vlan,
            'members_table': members_table,
            'active_tab': 'members',
        })


class VLANEditView(ObjectEditView):
    queryset = VLAN.objects.all()
    model_form = forms.VLANForm
    template_name = 'ipam/vlan_edit.html'


class VLANDeleteView(ObjectDeleteView):
    queryset = VLAN.objects.all()


class VLANBulkImportView(BulkImportView):
    queryset = VLAN.objects.all()
    model_form = forms.VLANCSVForm
    table = tables.VLANTable


class VLANBulkEditView(BulkEditView):
    queryset = VLAN.objects.prefetch_related('site', 'group', 'tenant', 'role')
    filterset = filters.VLANFilterSet
    table = tables.VLANTable
    form = forms.VLANBulkEditForm


class VLANBulkDeleteView(BulkDeleteView):
    queryset = VLAN.objects.prefetch_related('site', 'group', 'tenant', 'role')
    filterset = filters.VLANFilterSet
    table = tables.VLANTable


#
# Services
#

class ServiceListView(ObjectListView):
    queryset = Service.objects.prefetch_related('device', 'virtual_machine')
    filterset = filters.ServiceFilterSet
    filterset_form = forms.ServiceFilterForm
    table = tables.ServiceTable
    action_buttons = ('export',)


class ServiceView(ObjectView):
    queryset = Service.objects.prefetch_related(
        Prefetch('ipaddresses', IPAddress.objects.unrestricted())
    )

    def get(self, request, pk):

        service = get_object_or_404(self.queryset, pk=pk)

        return render(request, 'ipam/service.html', {
            'service': service,
        })


class ServiceEditView(ObjectEditView):
    queryset = Service.objects.prefetch_related(
        Prefetch('ipaddresses', IPAddress.objects.unrestricted())
    )
    model_form = forms.ServiceForm
    template_name = 'ipam/service_edit.html'

    def alter_obj(self, obj, request, url_args, url_kwargs):
        if 'device' in url_kwargs:
            obj.device = get_object_or_404(
                Device.objects.restrict(request.user),
                pk=url_kwargs['device']
            )
        elif 'virtualmachine' in url_kwargs:
            obj.virtual_machine = get_object_or_404(
                VirtualMachine.objects.restrict(request.user),
                pk=url_kwargs['virtualmachine']
            )
        return obj

    def get_return_url(self, request, service):
        return service.parent.get_absolute_url()


class ServiceBulkImportView(BulkImportView):
    queryset = Service.objects.all()
    model_form = forms.ServiceCSVForm
    table = tables.ServiceTable


class ServiceDeleteView(ObjectDeleteView):
    queryset = Service.objects.all()


class ServiceBulkEditView(BulkEditView):
    queryset = Service.objects.prefetch_related('device', 'virtual_machine')
    filterset = filters.ServiceFilterSet
    table = tables.ServiceTable
    form = forms.ServiceBulkEditForm


class ServiceBulkDeleteView(BulkDeleteView):
    queryset = Service.objects.prefetch_related('device', 'virtual_machine')
    filterset = filters.ServiceFilterSet
    table = tables.ServiceTable
