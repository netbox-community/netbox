from django.contrib.contenttypes.models import ContentType
from django.db.models import Prefetch
from django.db.models.expressions import RawSQL
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from dcim.filtersets import InterfaceFilterSet
from dcim.models import Interface, Site
from dcim.tables import SiteTable
from netbox.views import generic
from utilities.tables import configure_table
from utilities.utils import count_related
from virtualization.filtersets import VMInterfaceFilterSet
from virtualization.models import VMInterface
from . import filtersets, forms, tables
from .constants import *
from .models import *
from .models import ASN
from .utils import add_requested_prefixes, add_available_ipaddresses, add_available_vlans


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
        aggregates_table = tables.AggregateTable(aggregates, exclude=('rir', 'utilization'))
        configure_table(aggregates_table, request)

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
# ASNs
#

class ASNListView(generic.ObjectListView):
    queryset = ASN.objects.annotate(
        site_count=count_related(Site, 'asns'),
    )
    filterset = filtersets.ASNFilterSet
    filterset_form = forms.ASNFilterForm
    table = tables.ASNTable


class ASNView(generic.ObjectView):
    queryset = ASN.objects.all()

    def get_extra_context(self, request, instance):
        sites = instance.sites.restrict(request.user, 'view')
        sites_table = SiteTable(sites)
        configure_table(sites_table, request)

        return {
            'sites_table': sites_table,
            'sites_count': sites.count()
        }


class ASNEditView(generic.ObjectEditView):
    queryset = ASN.objects.all()
    model_form = forms.ASNForm


class ASNDeleteView(generic.ObjectDeleteView):
    queryset = ASN.objects.all()


class ASNBulkImportView(generic.BulkImportView):
    queryset = ASN.objects.all()
    model_form = forms.ASNCSVForm
    table = tables.ASNTable


class ASNBulkEditView(generic.BulkEditView):
    queryset = ASN.objects.annotate(
        site_count=count_related(Site, 'asns')
    )
    filterset = filtersets.ASNFilterSet
    table = tables.ASNTable
    form = forms.ASNBulkEditForm


class ASNBulkDeleteView(generic.BulkDeleteView):
    queryset = ASN.objects.annotate(
        site_count=count_related(Site, 'asns')
    )
    filterset = filtersets.ASNFilterSet
    table = tables.ASNTable


#
# Aggregates
#

class AggregateListView(generic.ObjectListView):
    queryset = Aggregate.objects.annotate(
        child_count=RawSQL('SELECT COUNT(*) FROM ipam_prefix WHERE ipam_prefix.prefix <<= ipam_aggregate.prefix', ())
    )
    filterset = filtersets.AggregateFilterSet
    filterset_form = forms.AggregateFilterForm
    table = tables.AggregateTable


class AggregateView(generic.ObjectView):
    queryset = Aggregate.objects.all()


class AggregatePrefixesView(generic.ObjectChildrenView):
    queryset = Aggregate.objects.all()
    child_model = Prefix
    table = tables.PrefixTable
    filterset = filtersets.PrefixFilterSet
    template_name = 'ipam/aggregate/prefixes.html'

    def get_children(self, request, parent):
        return Prefix.objects.restrict(request.user, 'view').filter(
            prefix__net_contained_or_equal=str(parent.prefix)
        ).prefetch_related('site', 'role', 'tenant', 'vlan')

    def prep_table_data(self, request, queryset, parent):
        # Determine whether to show assigned prefixes, available prefixes, or both
        show_available = bool(request.GET.get('show_available', 'true') == 'true')
        show_assigned = bool(request.GET.get('show_assigned', 'true') == 'true')

        return add_requested_prefixes(parent.prefix, queryset, show_available, show_assigned)

    def get_extra_context(self, request, instance):
        return {
            'bulk_querystring': f'within={instance.prefix}',
            'active_tab': 'prefixes',
            'first_available_prefix': instance.get_first_available_prefix(),
            'show_available': bool(request.GET.get('show_available', 'true') == 'true'),
            'show_assigned': bool(request.GET.get('show_assigned', 'true') == 'true'),
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
    filterset = filtersets.RoleFilterSet
    filterset_form = forms.RoleFilterForm
    table = tables.RoleTable


class RoleView(generic.ObjectView):
    queryset = Role.objects.all()

    def get_extra_context(self, request, instance):
        prefixes = Prefix.objects.restrict(request.user, 'view').filter(
            role=instance
        )

        prefixes_table = tables.PrefixTable(prefixes, exclude=('role', 'utilization'))
        configure_table(prefixes_table, request)

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
    table = tables.PrefixTable
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
            'site', 'role', 'tenant'
        )
        parent_prefix_table = tables.PrefixTable(
            list(parent_prefixes),
            exclude=('vrf', 'utilization'),
            orderable=False
        )

        # Duplicate prefixes table
        duplicate_prefixes = Prefix.objects.restrict(request.user, 'view').filter(
            vrf=instance.vrf, prefix=str(instance.prefix)
        ).exclude(
            pk=instance.pk
        ).prefetch_related(
            'site', 'role'
        )
        duplicate_prefix_table = tables.PrefixTable(
            list(duplicate_prefixes),
            exclude=('vrf', 'utilization'),
            orderable=False
        )

        return {
            'aggregate': aggregate,
            'parent_prefix_table': parent_prefix_table,
            'duplicate_prefix_table': duplicate_prefix_table,
        }


class PrefixPrefixesView(generic.ObjectChildrenView):
    queryset = Prefix.objects.all()
    child_model = Prefix
    table = tables.PrefixTable
    filterset = filtersets.PrefixFilterSet
    template_name = 'ipam/prefix/prefixes.html'

    def get_children(self, request, parent):
        return parent.get_child_prefixes().restrict(request.user, 'view').prefetch_related(
            'site', 'vrf', 'vlan', 'role', 'tenant',
        )

    def prep_table_data(self, request, queryset, parent):
        # Determine whether to show assigned prefixes, available prefixes, or both
        show_available = bool(request.GET.get('show_available', 'true') == 'true')
        show_assigned = bool(request.GET.get('show_assigned', 'true') == 'true')

        return add_requested_prefixes(parent.prefix, queryset, show_available, show_assigned)

    def get_extra_context(self, request, instance):
        return {
            'bulk_querystring': f"vrf_id={instance.vrf.pk if instance.vrf else '0'}&within={instance.prefix}",
            'active_tab': 'prefixes',
            'first_available_prefix': instance.get_first_available_prefix(),
            'show_available': bool(request.GET.get('show_available', 'true') == 'true'),
            'show_assigned': bool(request.GET.get('show_assigned', 'true') == 'true'),
        }


class PrefixIPRangesView(generic.ObjectChildrenView):
    queryset = Prefix.objects.all()
    child_model = IPRange
    table = tables.IPRangeTable
    filterset = filtersets.IPRangeFilterSet
    template_name = 'ipam/prefix/ip_ranges.html'

    def get_children(self, request, parent):
        return parent.get_child_ranges().restrict(request.user, 'view').prefetch_related(
            'vrf', 'role', 'tenant',
        )

    def get_extra_context(self, request, instance):
        return {
            'bulk_querystring': f"vrf_id={instance.vrf.pk if instance.vrf else '0'}&parent={instance.prefix}",
            'active_tab': 'ip-ranges',
            'first_available_ip': instance.get_first_available_ip(),
        }


class PrefixIPAddressesView(generic.ObjectChildrenView):
    queryset = Prefix.objects.all()
    child_model = IPAddress
    table = tables.IPAddressTable
    filterset = filtersets.IPAddressFilterSet
    template_name = 'ipam/prefix/ip_addresses.html'

    def get_children(self, request, parent):
        return parent.get_child_ips().restrict(request.user, 'view').prefetch_related('vrf', 'tenant')

    def prep_table_data(self, request, queryset, parent):
        show_available = bool(request.GET.get('show_available', 'true') == 'true')
        if show_available:
            return add_available_ipaddresses(parent.prefix, queryset, parent.is_pool)

        return queryset

    def get_extra_context(self, request, instance):
        return {
            'bulk_querystring': f"vrf_id={instance.vrf.pk if instance.vrf else '0'}&parent={instance.prefix}",
            'active_tab': 'ip-addresses',
            'first_available_ip': instance.get_first_available_ip(),
        }


class PrefixEditView(generic.ObjectEditView):
    queryset = Prefix.objects.all()
    model_form = forms.PrefixForm


class PrefixDeleteView(generic.ObjectDeleteView):
    queryset = Prefix.objects.all()


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


class IPRangeIPAddressesView(generic.ObjectChildrenView):
    queryset = IPRange.objects.all()
    child_model = IPAddress
    table = tables.IPAddressTable
    filterset = filtersets.IPAddressFilterSet
    template_name = 'ipam/iprange/ip_addresses.html'

    def get_children(self, request, parent):
        return parent.get_child_ips().restrict(request.user, 'view').prefetch_related(
            'vrf', 'role', 'tenant',
        )

    def get_extra_context(self, request, instance):
        return {
            'active_tab': 'ip-addresses',
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
    table = tables.IPAddressTable


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
        parent_prefixes_table = tables.PrefixTable(
            list(parent_prefixes),
            exclude=('vrf', 'utilization'),
            orderable=False
        )

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
        configure_table(related_ips_table, request)

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

    def alter_object(self, obj, request, url_args, url_kwargs):

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

        elif 'fhrpgroup' in request.GET:
            try:
                obj.assigned_object = FHRPGroup.objects.get(pk=request.GET['fhrpgroup'])
            except (ValueError, FHRPGroup.DoesNotExist):
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

        vlans_table = tables.VLANTable(vlans, exclude=('site', 'group', 'prefixes'))
        if request.user.has_perm('ipam.change_vlan') or request.user.has_perm('ipam.delete_vlan'):
            vlans_table.columns.show('pk')
        configure_table(vlans_table, request)

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
# FHRP groups
#

class FHRPGroupListView(generic.ObjectListView):
    queryset = FHRPGroup.objects.annotate(
        member_count=count_related(FHRPGroupAssignment, 'group')
    )
    filterset = filtersets.FHRPGroupFilterSet
    filterset_form = forms.FHRPGroupFilterForm
    table = tables.FHRPGroupTable


class FHRPGroupView(generic.ObjectView):
    queryset = FHRPGroup.objects.all()

    def get_extra_context(self, request, instance):
        # Get assigned IP addresses
        ipaddress_table = tables.AssignedIPAddressesTable(
            data=instance.ip_addresses.restrict(request.user, 'view').prefetch_related('vrf', 'tenant'),
            orderable=False
        )

        # Get assigned interfaces
        members_table = tables.FHRPGroupAssignmentTable(
            data=FHRPGroupAssignment.objects.restrict(request.user, 'view').filter(group=instance),
            orderable=False
        )
        members_table.columns.hide('group')

        return {
            'ipaddress_table': ipaddress_table,
            'members_table': members_table,
            'member_count': FHRPGroupAssignment.objects.filter(group=instance).count(),
        }


class FHRPGroupEditView(generic.ObjectEditView):
    queryset = FHRPGroup.objects.all()
    model_form = forms.FHRPGroupForm
    template_name = 'ipam/fhrpgroup_edit.html'

    def get_return_url(self, request, obj=None):
        return_url = super().get_return_url(request, obj)

        # If we're redirecting the user to the FHRPGroupAssignment creation form,
        # initialize the group field with the FHRPGroup we just saved.
        if return_url.startswith(reverse('ipam:fhrpgroupassignment_add')):
            return_url += f'&group={obj.pk}'

        return return_url


class FHRPGroupDeleteView(generic.ObjectDeleteView):
    queryset = FHRPGroup.objects.all()


class FHRPGroupBulkImportView(generic.BulkImportView):
    queryset = FHRPGroup.objects.all()
    model_form = forms.FHRPGroupCSVForm
    table = tables.FHRPGroupTable


class FHRPGroupBulkEditView(generic.BulkEditView):
    queryset = FHRPGroup.objects.all()
    filterset = filtersets.FHRPGroupFilterSet
    table = tables.FHRPGroupTable
    form = forms.FHRPGroupBulkEditForm


class FHRPGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = FHRPGroup.objects.all()
    filterset = filtersets.FHRPGroupFilterSet
    table = tables.FHRPGroupTable


#
# FHRP group assignments
#

class FHRPGroupAssignmentEditView(generic.ObjectEditView):
    queryset = FHRPGroupAssignment.objects.all()
    model_form = forms.FHRPGroupAssignmentForm
    template_name = 'ipam/fhrpgroupassignment_edit.html'

    def alter_object(self, instance, request, args, kwargs):
        if not instance.pk:
            # Assign the interface based on URL kwargs
            content_type = get_object_or_404(ContentType, pk=request.GET.get('interface_type'))
            instance.interface = get_object_or_404(content_type.model_class(), pk=request.GET.get('interface_id'))
        return instance


class FHRPGroupAssignmentDeleteView(generic.ObjectDeleteView):
    queryset = FHRPGroupAssignment.objects.all()


#
# VLANs
#

class VLANListView(generic.ObjectListView):
    queryset = VLAN.objects.all()
    filterset = filtersets.VLANFilterSet
    filterset_form = forms.VLANFilterForm
    table = tables.VLANTable


class VLANView(generic.ObjectView):
    queryset = VLAN.objects.prefetch_related('site__region', 'tenant__group', 'role')

    def get_extra_context(self, request, instance):
        prefixes = Prefix.objects.restrict(request.user, 'view').filter(vlan=instance).prefetch_related(
            'vrf', 'site', 'role'
        )
        prefix_table = tables.PrefixTable(list(prefixes), exclude=('vlan', 'utilization'), orderable=False)

        return {
            'prefix_table': prefix_table,
        }


class VLANInterfacesView(generic.ObjectChildrenView):
    queryset = VLAN.objects.all()
    child_model = Interface
    table = tables.VLANDevicesTable
    filterset = InterfaceFilterSet
    template_name = 'ipam/vlan/interfaces.html'

    def get_children(self, request, parent):
        return parent.get_interfaces().restrict(request.user, 'view')

    def get_extra_context(self, request, instance):
        return {
            'active_tab': 'interfaces',
        }


class VLANVMInterfacesView(generic.ObjectChildrenView):
    queryset = VLAN.objects.all()
    child_model = VMInterface
    table = tables.VLANVirtualMachinesTable
    filterset = VMInterfaceFilterSet
    template_name = 'ipam/vlan/vminterfaces.html'

    def get_children(self, request, parent):
        return parent.get_vminterfaces().restrict(request.user, 'view')

    def get_extra_context(self, request, instance):
        return {
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
# Service templates
#

class ServiceTemplateListView(generic.ObjectListView):
    queryset = ServiceTemplate.objects.all()
    filterset = filtersets.ServiceTemplateFilterSet
    filterset_form = forms.ServiceTemplateFilterForm
    table = tables.ServiceTemplateTable


class ServiceTemplateView(generic.ObjectView):
    queryset = ServiceTemplate.objects.all()


class ServiceTemplateEditView(generic.ObjectEditView):
    queryset = ServiceTemplate.objects.all()
    model_form = forms.ServiceTemplateForm


class ServiceTemplateDeleteView(generic.ObjectDeleteView):
    queryset = ServiceTemplate.objects.all()


class ServiceTemplateBulkImportView(generic.BulkImportView):
    queryset = ServiceTemplate.objects.all()
    model_form = forms.ServiceTemplateCSVForm
    table = tables.ServiceTemplateTable


class ServiceTemplateBulkEditView(generic.BulkEditView):
    queryset = ServiceTemplate.objects.all()
    filterset = filtersets.ServiceTemplateFilterSet
    table = tables.ServiceTemplateTable
    form = forms.ServiceTemplateBulkEditForm


class ServiceTemplateBulkDeleteView(generic.BulkDeleteView):
    queryset = ServiceTemplate.objects.all()
    filterset = filtersets.ServiceTemplateFilterSet
    table = tables.ServiceTemplateTable


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


class ServiceCreateView(generic.ObjectEditView):
    queryset = Service.objects.all()
    model_form = forms.ServiceCreateForm
    template_name = 'ipam/service_create.html'


class ServiceEditView(generic.ObjectEditView):
    queryset = Service.objects.prefetch_related('ipaddresses')
    model_form = forms.ServiceForm
    template_name = 'ipam/service_edit.html'


class ServiceDeleteView(generic.ObjectDeleteView):
    queryset = Service.objects.all()


class ServiceBulkImportView(generic.BulkImportView):
    queryset = Service.objects.all()
    model_form = forms.ServiceCSVForm
    table = tables.ServiceTable


class ServiceBulkEditView(generic.BulkEditView):
    queryset = Service.objects.prefetch_related('device', 'virtual_machine')
    filterset = filtersets.ServiceFilterSet
    table = tables.ServiceTable
    form = forms.ServiceBulkEditForm


class ServiceBulkDeleteView(generic.BulkDeleteView):
    queryset = Service.objects.prefetch_related('device', 'virtual_machine')
    filterset = filtersets.ServiceFilterSet
    table = tables.ServiceTable
