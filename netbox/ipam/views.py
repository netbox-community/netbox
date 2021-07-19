from django.db.models import Prefetch
from django.db.models.expressions import RawSQL
from django.shortcuts import get_object_or_404, redirect, render

from dcim.models import Device, Interface
from netbox.views import generic
from utilities.tables import paginate_table
from utilities.utils import count_related
from virtualization.models import VirtualMachine, VMInterface
from . import filtersets, forms, tables
from .constants import *
from .models import *
from .utils import add_available_ipaddresses, add_available_prefixes, add_available_vlans


#
# VRFs
#

class VRFListView(generic.ObjectListView):
    queryset = VRF.objects.all()
    filterset = filtersets.VRFFilterSet
    filterset_form = forms.VRFFilterForm
    table = tables.VRFTable


class VRFView(generic.ObjectView):
    queryset = VRF.objects.all()

    def get_extra_context(self, request, instance):
        prefix_count = Prefix.objects.restrict(request.user, 'view').filter(vrf=instance).count()
        ipaddress_count = IPAddress.objects.restrict(request.user, 'view').filter(vrf=instance).count()

        import_targets_table = tables.RouteTargetTable(
            instance.import_targets.prefetch_related('tenant'),
            orderable=False
        )
        export_targets_table = tables.RouteTargetTable(
            instance.export_targets.prefetch_related('tenant'),
            orderable=False
        )

        return {
            'prefix_count': prefix_count,
            'ipaddress_count': ipaddress_count,
            'import_targets_table': import_targets_table,
            'export_targets_table': export_targets_table,
        }


class VRFEditView(generic.ObjectEditView):
    queryset = VRF.objects.all()
    model_form = forms.VRFForm


class VRFDeleteView(generic.ObjectDeleteView):
    queryset = VRF.objects.all()


class VRFBulkImportView(generic.BulkImportView):
    queryset = VRF.objects.all()
    model_form = forms.VRFCSVForm
    table = tables.VRFTable


class VRFBulkEditView(generic.BulkEditView):
    queryset = VRF.objects.prefetch_related('tenant')
    filterset = filtersets.VRFFilterSet
    table = tables.VRFTable
    form = forms.VRFBulkEditForm


class VRFBulkDeleteView(generic.BulkDeleteView):
    queryset = VRF.objects.prefetch_related('tenant')
    filterset = filtersets.VRFFilterSet
    table = tables.VRFTable


#
# Route targets
#

class RouteTargetListView(generic.ObjectListView):
    queryset = RouteTarget.objects.all()
    filterset = filtersets.RouteTargetFilterSet
    filterset_form = forms.RouteTargetFilterForm
    table = tables.RouteTargetTable


class RouteTargetView(generic.ObjectView):
    queryset = RouteTarget.objects.all()

    def get_extra_context(self, request, instance):
        importing_vrfs_table = tables.VRFTable(
            instance.importing_vrfs.prefetch_related('tenant'),
            orderable=False
        )
        exporting_vrfs_table = tables.VRFTable(
            instance.exporting_vrfs.prefetch_related('tenant'),
            orderable=False
        )

        return {
            'importing_vrfs_table': importing_vrfs_table,
            'exporting_vrfs_table': exporting_vrfs_table,
        }


class RouteTargetEditView(generic.ObjectEditView):
    queryset = RouteTarget.objects.all()
    model_form = forms.RouteTargetForm


class RouteTargetDeleteView(generic.ObjectDeleteView):
    queryset = RouteTarget.objects.all()


class RouteTargetBulkImportView(generic.BulkImportView):
    queryset = RouteTarget.objects.all()
    model_form = forms.RouteTargetCSVForm
    table = tables.RouteTargetTable


class RouteTargetBulkEditView(generic.BulkEditView):
    queryset = RouteTarget.objects.prefetch_related('tenant')
    filterset = filtersets.RouteTargetFilterSet
    table = tables.RouteTargetTable
    form = forms.RouteTargetBulkEditForm


class RouteTargetBulkDeleteView(generic.BulkDeleteView):
    queryset = RouteTarget.objects.prefetch_related('tenant')
    filterset = filtersets.RouteTargetFilterSet
    table = tables.RouteTargetTable


#
# RIRs
#

class RIRListView(generic.ObjectListView):
    queryset = RIR.objects.annotate(
        aggregate_count=count_related(Aggregate, 'rir')
    )
    filterset = filtersets.RIRFilterSet
    filterset_form = forms.RIRFilterForm
    table = tables.RIRTable


class RIRView(generic.ObjectView):
    queryset = RIR.objects.all()

    def get_extra_context(self, request, instance):
        aggregates = Aggregate.objects.restrict(request.user, 'view').filter(
            rir=instance
        )

        aggregates_table = tables.AggregateTable(aggregates)
        aggregates_table.columns.hide('rir')
        paginate_table(aggregates_table, request)

        return {
            'aggregates_table': aggregates_table,
        }


class RIREditView(generic.ObjectEditView):
    queryset = RIR.objects.all()
    model_form = forms.RIRForm


class RIRDeleteView(generic.ObjectDeleteView):
    queryset = RIR.objects.all()


class RIRBulkImportView(generic.BulkImportView):
    queryset = RIR.objects.all()
    model_form = forms.RIRCSVForm
    table = tables.RIRTable


class RIRBulkEditView(generic.BulkEditView):
    queryset = RIR.objects.annotate(
        aggregate_count=count_related(Aggregate, 'rir')
    )
    filterset = filtersets.RIRFilterSet
    table = tables.RIRTable
    form = forms.RIRBulkEditForm


class RIRBulkDeleteView(generic.BulkDeleteView):
    queryset = RIR.objects.annotate(
        aggregate_count=count_related(Aggregate, 'rir')
    )
    filterset = filtersets.RIRFilterSet
    table = tables.RIRTable


#
# Aggregates
#

class AggregateListView(generic.ObjectListView):
    queryset = Aggregate.objects.annotate(
        child_count=RawSQL('SELECT COUNT(*) FROM ipam_prefix WHERE ipam_prefix.prefix <<= ipam_aggregate.prefix', ())
    )
    filterset = filtersets.AggregateFilterSet
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


class AggregateView(generic.ObjectView):
    queryset = Aggregate.objects.all()

    def get_extra_context(self, request, instance):
        # Find all child prefixes contained by this aggregate
        child_prefixes = Prefix.objects.restrict(request.user, 'view').filter(
            prefix__net_contained_or_equal=str(instance.prefix)
        ).prefetch_related(
            'site', 'role'
        ).order_by(
            'prefix'
        )

        # Add available prefixes to the table if requested
        if request.GET.get('show_available', 'true') == 'true':
            child_prefixes = add_available_prefixes(instance.prefix, child_prefixes)

        prefix_table = tables.PrefixDetailTable(child_prefixes)
        if request.user.has_perm('ipam.change_prefix') or request.user.has_perm('ipam.delete_prefix'):
            prefix_table.columns.show('pk')
        paginate_table(prefix_table, request)

        # Compile permissions list for rendering the object table
        permissions = {
            'add': request.user.has_perm('ipam.add_prefix'),
            'change': request.user.has_perm('ipam.change_prefix'),
            'delete': request.user.has_perm('ipam.delete_prefix'),
        }

        return {
            'prefix_table': prefix_table,
            'permissions': permissions,
            'show_available': request.GET.get('show_available', 'true') == 'true',
        }


class AggregateEditView(generic.ObjectEditView):
    queryset = Aggregate.objects.all()
    model_form = forms.AggregateForm


class AggregateDeleteView(generic.ObjectDeleteView):
    queryset = Aggregate.objects.all()


class AggregateBulkImportView(generic.BulkImportView):
    queryset = Aggregate.objects.all()
    model_form = forms.AggregateCSVForm
    table = tables.AggregateTable


class AggregateBulkEditView(generic.BulkEditView):
    queryset = Aggregate.objects.prefetch_related('rir')
    filterset = filtersets.AggregateFilterSet
    table = tables.AggregateTable
    form = forms.AggregateBulkEditForm


class AggregateBulkDeleteView(generic.BulkDeleteView):
    queryset = Aggregate.objects.prefetch_related('rir')
    filterset = filtersets.AggregateFilterSet
    table = tables.AggregateTable


#
# Prefix/VLAN roles
#

class RoleListView(generic.ObjectListView):
    queryset = Role.objects.annotate(
        prefix_count=count_related(Prefix, 'role'),
        vlan_count=count_related(VLAN, 'role')
    )
    table = tables.RoleTable


class RoleView(generic.ObjectView):
    queryset = Role.objects.all()

    def get_extra_context(self, request, instance):
        prefixes = Prefix.objects.restrict(request.user, 'view').filter(
            role=instance
        )

        prefixes_table = tables.PrefixTable(prefixes)
        prefixes_table.columns.hide('role')
        paginate_table(prefixes_table, request)

        return {
            'prefixes_table': prefixes_table,
        }


class RoleEditView(generic.ObjectEditView):
    queryset = Role.objects.all()
    model_form = forms.RoleForm


class RoleDeleteView(generic.ObjectDeleteView):
    queryset = Role.objects.all()


class RoleBulkImportView(generic.BulkImportView):
    queryset = Role.objects.all()
    model_form = forms.RoleCSVForm
    table = tables.RoleTable


class RoleBulkEditView(generic.BulkEditView):
    queryset = Role.objects.all()
    filterset = filtersets.RoleFilterSet
    table = tables.RoleTable
    form = forms.RoleBulkEditForm


class RoleBulkDeleteView(generic.BulkDeleteView):
    queryset = Role.objects.all()
    table = tables.RoleTable


#
# Prefixes
#

class PrefixListView(generic.ObjectListView):
    queryset = Prefix.objects.all()
    filterset = filtersets.PrefixFilterSet
    filterset_form = forms.PrefixFilterForm
    table = tables.PrefixDetailTable
    template_name = 'ipam/prefix_list.html'


class PrefixView(generic.ObjectView):
    queryset = Prefix.objects.prefetch_related('vrf', 'site__region', 'tenant__group', 'vlan__group', 'role')

    def get_extra_context(self, request, instance):
        try:
            aggregate = Aggregate.objects.restrict(request.user, 'view').get(
                prefix__net_contains_or_equals=str(instance.prefix)
            )
        except Aggregate.DoesNotExist:
            aggregate = None

        # Parent prefixes table
        parent_prefixes = Prefix.objects.restrict(request.user, 'view').filter(
            Q(vrf=instance.vrf) | Q(vrf__isnull=True)
        ).filter(
            prefix__net_contains=str(instance.prefix)
        ).prefetch_related(
            'site', 'role'
        )
        parent_prefix_table = tables.PrefixTable(list(parent_prefixes), orderable=False)
        parent_prefix_table.exclude = ('vrf',)

        # Duplicate prefixes table
        duplicate_prefixes = Prefix.objects.restrict(request.user, 'view').filter(
            vrf=instance.vrf, prefix=str(instance.prefix)
        ).exclude(
            pk=instance.pk
        ).prefetch_related(
            'site', 'role'
        )
        duplicate_prefix_table = tables.PrefixTable(list(duplicate_prefixes), orderable=False)
        duplicate_prefix_table.exclude = ('vrf',)

        return {
            'aggregate': aggregate,
            'parent_prefix_table': parent_prefix_table,
            'duplicate_prefix_table': duplicate_prefix_table,
        }


class PrefixPrefixesView(generic.ObjectView):
    queryset = Prefix.objects.all()
    template_name = 'ipam/prefix/prefixes.html'

    def get_extra_context(self, request, instance):
        # Child prefixes table
        child_prefixes = instance.get_child_prefixes().restrict(request.user, 'view').prefetch_related(
            'site', 'vlan', 'role',
        )

        # Add available prefixes to the table if requested
        if child_prefixes and request.GET.get('show_available', 'true') == 'true':
            child_prefixes = add_available_prefixes(instance.prefix, child_prefixes)

        prefix_table = tables.PrefixDetailTable(child_prefixes)
        if request.user.has_perm('ipam.change_prefix') or request.user.has_perm('ipam.delete_prefix'):
            prefix_table.columns.show('pk')
        paginate_table(prefix_table, request)

        # Compile permissions list for rendering the object table
        permissions = {
            'add': request.user.has_perm('ipam.add_prefix'),
            'change': request.user.has_perm('ipam.change_prefix'),
            'delete': request.user.has_perm('ipam.delete_prefix'),
        }

        bulk_querystring = 'vrf_id={}&within={}'.format(instance.vrf.pk if instance.vrf else '0', instance.prefix)

        return {
            'first_available_prefix': instance.get_first_available_prefix(),
            'prefix_table': prefix_table,
            'permissions': permissions,
            'bulk_querystring': bulk_querystring,
            'active_tab': 'prefixes',
            'show_available': request.GET.get('show_available', 'true') == 'true',
        }


class PrefixIPAddressesView(generic.ObjectView):
    queryset = Prefix.objects.all()
    template_name = 'ipam/prefix/ip_addresses.html'

    def get_extra_context(self, request, instance):
        # Find all IPAddresses belonging to this Prefix
        ipaddresses = instance.get_child_ips().restrict(request.user, 'view').prefetch_related(
            'vrf', 'primary_ip4_for', 'primary_ip6_for'
        )

        # Add available IP addresses to the table if requested
        if request.GET.get('show_available', 'true') == 'true':
            ipaddresses = add_available_ipaddresses(instance.prefix, ipaddresses, instance.is_pool)

        ip_table = tables.IPAddressTable(ipaddresses)
        if request.user.has_perm('ipam.change_ipaddress') or request.user.has_perm('ipam.delete_ipaddress'):
            ip_table.columns.show('pk')
        paginate_table(ip_table, request)

        # Compile permissions list for rendering the object table
        permissions = {
            'add': request.user.has_perm('ipam.add_ipaddress'),
            'change': request.user.has_perm('ipam.change_ipaddress'),
            'delete': request.user.has_perm('ipam.delete_ipaddress'),
        }

        bulk_querystring = 'vrf_id={}&parent={}'.format(instance.vrf.pk if instance.vrf else '0', instance.prefix)

        return {
            'first_available_ip': instance.get_first_available_ip(),
            'ip_table': ip_table,
            'permissions': permissions,
            'bulk_querystring': bulk_querystring,
            'active_tab': 'ip-addresses',
            'show_available': request.GET.get('show_available', 'true') == 'true',
        }


class PrefixEditView(generic.ObjectEditView):
    queryset = Prefix.objects.all()
    model_form = forms.PrefixForm


class PrefixDeleteView(generic.ObjectDeleteView):
    queryset = Prefix.objects.all()
    template_name = 'ipam/prefix_delete.html'


class PrefixBulkImportView(generic.BulkImportView):
    queryset = Prefix.objects.all()
    model_form = forms.PrefixCSVForm
    table = tables.PrefixTable


class PrefixBulkEditView(generic.BulkEditView):
    queryset = Prefix.objects.prefetch_related('site', 'vrf__tenant', 'tenant', 'vlan', 'role')
    filterset = filtersets.PrefixFilterSet
    table = tables.PrefixTable
    form = forms.PrefixBulkEditForm


class PrefixBulkDeleteView(generic.BulkDeleteView):
    queryset = Prefix.objects.prefetch_related('site', 'vrf__tenant', 'tenant', 'vlan', 'role')
    filterset = filtersets.PrefixFilterSet
    table = tables.PrefixTable


#
# IP Ranges
#

class IPRangeListView(generic.ObjectListView):
    queryset = IPRange.objects.all()
    filterset = filtersets.IPRangeFilterSet
    filterset_form = forms.IPRangeFilterForm
    table = tables.IPRangeTable


class IPRangeView(generic.ObjectView):
    queryset = IPRange.objects.all()


class IPRangeIPAddressesView(generic.ObjectView):
    queryset = IPRange.objects.all()
    template_name = 'ipam/iprange/ip_addresses.html'

    def get_extra_context(self, request, instance):
        # Find all IPAddresses within this range
        ipaddresses = instance.get_child_ips().restrict(request.user, 'view').prefetch_related(
            'vrf', 'primary_ip4_for', 'primary_ip6_for'
        )

        # Add available IP addresses to the table if requested
        # if request.GET.get('show_available', 'true') == 'true':
        #     ipaddresses = add_available_ipaddresses(instance.prefix, ipaddresses, instance.is_pool)

        ip_table = tables.IPAddressTable(ipaddresses)
        if request.user.has_perm('ipam.change_ipaddress') or request.user.has_perm('ipam.delete_ipaddress'):
            ip_table.columns.show('pk')
        paginate_table(ip_table, request)

        # Compile permissions list for rendering the object table
        permissions = {
            'add': request.user.has_perm('ipam.add_ipaddress'),
            'change': request.user.has_perm('ipam.change_ipaddress'),
            'delete': request.user.has_perm('ipam.delete_ipaddress'),
        }

        return {
            'ip_table': ip_table,
            'permissions': permissions,
            'active_tab': 'ip-addresses',
            'show_available': request.GET.get('show_available', 'true') == 'true',
        }


class IPRangeEditView(generic.ObjectEditView):
    queryset = IPRange.objects.all()
    model_form = forms.IPRangeForm


class IPRangeDeleteView(generic.ObjectDeleteView):
    queryset = IPRange.objects.all()


class IPRangeBulkImportView(generic.BulkImportView):
    queryset = IPRange.objects.all()
    model_form = forms.IPRangeCSVForm
    table = tables.IPRangeTable


class IPRangeBulkEditView(generic.BulkEditView):
    queryset = IPRange.objects.prefetch_related('vrf', 'tenant')
    filterset = filtersets.IPRangeFilterSet
    table = tables.IPRangeTable
    form = forms.IPRangeBulkEditForm


class IPRangeBulkDeleteView(generic.BulkDeleteView):
    queryset = IPRange.objects.prefetch_related('vrf', 'tenant')
    filterset = filtersets.IPRangeFilterSet
    table = tables.IPRangeTable


#
# IP addresses
#

class IPAddressListView(generic.ObjectListView):
    queryset = IPAddress.objects.all()
    filterset = filtersets.IPAddressFilterSet
    filterset_form = forms.IPAddressFilterForm
    table = tables.IPAddressDetailTable


class IPAddressView(generic.ObjectView):
    queryset = IPAddress.objects.prefetch_related('vrf__tenant', 'tenant')

    def get_extra_context(self, request, instance):
        # Parent prefixes table
        parent_prefixes = Prefix.objects.restrict(request.user, 'view').filter(
            vrf=instance.vrf,
            prefix__net_contains_or_equals=str(instance.address.ip)
        ).prefetch_related(
            'site', 'role'
        )
        parent_prefixes_table = tables.PrefixTable(list(parent_prefixes), orderable=False)
        parent_prefixes_table.exclude = ('vrf',)

        # Duplicate IPs table
        duplicate_ips = IPAddress.objects.restrict(request.user, 'view').filter(
            vrf=instance.vrf,
            address=str(instance.address)
        ).exclude(
            pk=instance.pk
        ).prefetch_related(
            'nat_inside'
        )
        # Exclude anycast IPs if this IP is anycast
        if instance.role == IPAddressRoleChoices.ROLE_ANYCAST:
            duplicate_ips = duplicate_ips.exclude(role=IPAddressRoleChoices.ROLE_ANYCAST)
        # Limit to a maximum of 10 duplicates displayed here
        duplicate_ips_table = tables.IPAddressTable(duplicate_ips[:10], orderable=False)

        # Related IP table
        related_ips = IPAddress.objects.restrict(request.user, 'view').exclude(
            address=str(instance.address)
        ).filter(
            vrf=instance.vrf, address__net_contained_or_equal=str(instance.address)
        )
        related_ips_table = tables.IPAddressTable(related_ips, orderable=False)
        paginate_table(related_ips_table, request)

        return {
            'parent_prefixes_table': parent_prefixes_table,
            'duplicate_ips_table': duplicate_ips_table,
            'more_duplicate_ips': duplicate_ips.count() > 10,
            'related_ips_table': related_ips_table,
        }


class IPAddressEditView(generic.ObjectEditView):
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


# TODO: Standardize or remove this view
class IPAddressAssignView(generic.ObjectView):
    """
    Search for IPAddresses to be assigned to an Interface.
    """
    queryset = IPAddress.objects.all()

    def dispatch(self, request, *args, **kwargs):

        # Redirect user if an interface has not been provided
        if 'interface' not in request.GET and 'vminterface' not in request.GET:
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
            addresses = filtersets.IPAddressFilterSet(request.POST, addresses).qs[:100]
            table = tables.IPAddressAssignTable(addresses)

        return render(request, 'ipam/ipaddress_assign.html', {
            'form': form,
            'table': table,
            'return_url': request.GET.get('return_url'),
        })


class IPAddressDeleteView(generic.ObjectDeleteView):
    queryset = IPAddress.objects.all()


class IPAddressBulkCreateView(generic.BulkCreateView):
    queryset = IPAddress.objects.all()
    form = forms.IPAddressBulkCreateForm
    model_form = forms.IPAddressBulkAddForm
    pattern_target = 'address'
    template_name = 'ipam/ipaddress_bulk_add.html'


class IPAddressBulkImportView(generic.BulkImportView):
    queryset = IPAddress.objects.all()
    model_form = forms.IPAddressCSVForm
    table = tables.IPAddressTable


class IPAddressBulkEditView(generic.BulkEditView):
    queryset = IPAddress.objects.prefetch_related('vrf__tenant', 'tenant')
    filterset = filtersets.IPAddressFilterSet
    table = tables.IPAddressTable
    form = forms.IPAddressBulkEditForm


class IPAddressBulkDeleteView(generic.BulkDeleteView):
    queryset = IPAddress.objects.prefetch_related('vrf__tenant', 'tenant')
    filterset = filtersets.IPAddressFilterSet
    table = tables.IPAddressTable


#
# VLAN groups
#

class VLANGroupListView(generic.ObjectListView):
    queryset = VLANGroup.objects.annotate(
        vlan_count=count_related(VLAN, 'group')
    )
    filterset = filtersets.VLANGroupFilterSet
    filterset_form = forms.VLANGroupFilterForm
    table = tables.VLANGroupTable


class VLANGroupView(generic.ObjectView):
    queryset = VLANGroup.objects.all()

    def get_extra_context(self, request, instance):
        vlans = VLAN.objects.restrict(request.user, 'view').filter(group=instance).prefetch_related(
            Prefetch('prefixes', queryset=Prefix.objects.restrict(request.user))
        ).order_by('vid')
        vlans_count = vlans.count()
        vlans = add_available_vlans(vlans, vlan_group=instance)

        vlans_table = tables.VLANDetailTable(vlans)
        if request.user.has_perm('ipam.change_vlan') or request.user.has_perm('ipam.delete_vlan'):
            vlans_table.columns.show('pk')
        vlans_table.columns.hide('site')
        vlans_table.columns.hide('group')
        paginate_table(vlans_table, request)

        # Compile permissions list for rendering the object table
        permissions = {
            'add': request.user.has_perm('ipam.add_vlan'),
            'change': request.user.has_perm('ipam.change_vlan'),
            'delete': request.user.has_perm('ipam.delete_vlan'),
        }

        return {
            'vlans_count': vlans_count,
            'vlans_table': vlans_table,
            'permissions': permissions,
        }


class VLANGroupEditView(generic.ObjectEditView):
    queryset = VLANGroup.objects.all()
    model_form = forms.VLANGroupForm
    template_name = 'ipam/vlangroup_edit.html'


class VLANGroupDeleteView(generic.ObjectDeleteView):
    queryset = VLANGroup.objects.all()


class VLANGroupBulkImportView(generic.BulkImportView):
    queryset = VLANGroup.objects.all()
    model_form = forms.VLANGroupCSVForm
    table = tables.VLANGroupTable


class VLANGroupBulkEditView(generic.BulkEditView):
    queryset = VLANGroup.objects.annotate(
        vlan_count=count_related(VLAN, 'group')
    )
    filterset = filtersets.VLANGroupFilterSet
    table = tables.VLANGroupTable
    form = forms.VLANGroupBulkEditForm


class VLANGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = VLANGroup.objects.annotate(
        vlan_count=count_related(VLAN, 'group')
    )
    filterset = filtersets.VLANGroupFilterSet
    table = tables.VLANGroupTable


#
# VLANs
#

class VLANListView(generic.ObjectListView):
    queryset = VLAN.objects.all()
    filterset = filtersets.VLANFilterSet
    filterset_form = forms.VLANFilterForm
    table = tables.VLANDetailTable


class VLANView(generic.ObjectView):
    queryset = VLAN.objects.prefetch_related('site__region', 'tenant__group', 'role')

    def get_extra_context(self, request, instance):
        prefixes = Prefix.objects.restrict(request.user, 'view').filter(vlan=instance).prefetch_related(
            'vrf', 'site', 'role'
        )
        prefix_table = tables.PrefixTable(list(prefixes), orderable=False)
        prefix_table.exclude = ('vlan',)

        return {
            'prefix_table': prefix_table,
        }


class VLANInterfacesView(generic.ObjectView):
    queryset = VLAN.objects.all()
    template_name = 'ipam/vlan/interfaces.html'

    def get_extra_context(self, request, instance):
        interfaces = instance.get_interfaces().prefetch_related('device')
        members_table = tables.VLANDevicesTable(interfaces)
        paginate_table(members_table, request)

        return {
            'members_table': members_table,
            'active_tab': 'interfaces',
        }


class VLANVMInterfacesView(generic.ObjectView):
    queryset = VLAN.objects.all()
    template_name = 'ipam/vlan/vminterfaces.html'

    def get_extra_context(self, request, instance):
        interfaces = instance.get_vminterfaces().prefetch_related('virtual_machine')
        members_table = tables.VLANVirtualMachinesTable(interfaces)
        paginate_table(members_table, request)

        return {
            'members_table': members_table,
            'active_tab': 'vminterfaces',
        }


class VLANEditView(generic.ObjectEditView):
    queryset = VLAN.objects.all()
    model_form = forms.VLANForm
    template_name = 'ipam/vlan_edit.html'


class VLANDeleteView(generic.ObjectDeleteView):
    queryset = VLAN.objects.all()


class VLANBulkImportView(generic.BulkImportView):
    queryset = VLAN.objects.all()
    model_form = forms.VLANCSVForm
    table = tables.VLANTable


class VLANBulkEditView(generic.BulkEditView):
    queryset = VLAN.objects.prefetch_related('site', 'group', 'tenant', 'role')
    filterset = filtersets.VLANFilterSet
    table = tables.VLANTable
    form = forms.VLANBulkEditForm


class VLANBulkDeleteView(generic.BulkDeleteView):
    queryset = VLAN.objects.prefetch_related('site', 'group', 'tenant', 'role')
    filterset = filtersets.VLANFilterSet
    table = tables.VLANTable


#
# Services
#

class ServiceListView(generic.ObjectListView):
    queryset = Service.objects.all()
    filterset = filtersets.ServiceFilterSet
    filterset_form = forms.ServiceFilterForm
    table = tables.ServiceTable
    action_buttons = ('import', 'export')


class ServiceView(generic.ObjectView):
    queryset = Service.objects.prefetch_related('ipaddresses')


class ServiceEditView(generic.ObjectEditView):
    queryset = Service.objects.prefetch_related('ipaddresses')
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


class ServiceBulkImportView(generic.BulkImportView):
    queryset = Service.objects.all()
    model_form = forms.ServiceCSVForm
    table = tables.ServiceTable


class ServiceDeleteView(generic.ObjectDeleteView):
    queryset = Service.objects.all()


class ServiceBulkEditView(generic.BulkEditView):
    queryset = Service.objects.prefetch_related('device', 'virtual_machine')
    filterset = filtersets.ServiceFilterSet
    table = tables.ServiceTable
    form = forms.ServiceBulkEditForm


class ServiceBulkDeleteView(generic.BulkDeleteView):
    queryset = Service.objects.prefetch_related('device', 'virtual_machine')
    filterset = filtersets.ServiceFilterSet
    table = tables.ServiceTable
