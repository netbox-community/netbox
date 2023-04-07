from django.contrib.contenttypes.models import ContentType
from django.db.models import Prefetch
from django.db.models.expressions import RawSQL
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _

from circuits.models import Provider, Circuit
from circuits.tables import ProviderTable
from dcim.filtersets import InterfaceFilterSet
from dcim.models import Interface, Site, Device
from dcim.tables import SiteTable
from netbox.views import generic
from utilities.utils import count_related
from utilities.views import ViewTab, register_model_view
from virtualization.filtersets import VMInterfaceFilterSet
from virtualization.models import VMInterface, VirtualMachine
from . import filtersets, forms, tables
from .constants import *
from .models import *
from .models import ASN
from .tables.l2vpn import L2VPNTable, L2VPNTerminationTable
from .utils import add_requested_prefixes, add_available_ipaddresses, add_available_vlans


#
# VRFs
#

class VRFListView(generic.ObjectListView):
    queryset = VRF.objects.all()
    filterset = filtersets.VRFFilterSet
    filterset_form = forms.VRFFilterForm
    table = tables.VRFTable


@register_model_view(VRF)
class VRFView(generic.ObjectView):
    queryset = VRF.objects.all()

    def get_extra_context(self, request, instance):
        prefix_count = Prefix.objects.restrict(request.user, 'view').filter(vrf=instance).count()
        ipaddress_count = IPAddress.objects.restrict(request.user, 'view').filter(vrf=instance).count()

        import_targets_table = tables.RouteTargetTable(
            instance.import_targets.all(),
            orderable=False
        )
        export_targets_table = tables.RouteTargetTable(
            instance.export_targets.all(),
            orderable=False
        )

        return {
            'prefix_count': prefix_count,
            'ipaddress_count': ipaddress_count,
            'import_targets_table': import_targets_table,
            'export_targets_table': export_targets_table,
        }


@register_model_view(VRF, 'edit')
class VRFEditView(generic.ObjectEditView):
    queryset = VRF.objects.all()
    form = forms.VRFForm


@register_model_view(VRF, 'delete')
class VRFDeleteView(generic.ObjectDeleteView):
    queryset = VRF.objects.all()


class VRFBulkImportView(generic.BulkImportView):
    queryset = VRF.objects.all()
    model_form = forms.VRFImportForm
    table = tables.VRFTable


class VRFBulkEditView(generic.BulkEditView):
    queryset = VRF.objects.all()
    filterset = filtersets.VRFFilterSet
    table = tables.VRFTable
    form = forms.VRFBulkEditForm


class VRFBulkDeleteView(generic.BulkDeleteView):
    queryset = VRF.objects.all()
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


@register_model_view(RouteTarget)
class RouteTargetView(generic.ObjectView):
    queryset = RouteTarget.objects.all()

    def get_extra_context(self, request, instance):
        importing_vrfs_table = tables.VRFTable(
            instance.importing_vrfs.all(),
            orderable=False
        )
        exporting_vrfs_table = tables.VRFTable(
            instance.exporting_vrfs.all(),
            orderable=False
        )

        return {
            'importing_vrfs_table': importing_vrfs_table,
            'exporting_vrfs_table': exporting_vrfs_table,
        }


@register_model_view(RouteTarget, 'edit')
class RouteTargetEditView(generic.ObjectEditView):
    queryset = RouteTarget.objects.all()
    form = forms.RouteTargetForm


@register_model_view(RouteTarget, 'delete')
class RouteTargetDeleteView(generic.ObjectDeleteView):
    queryset = RouteTarget.objects.all()


class RouteTargetBulkImportView(generic.BulkImportView):
    queryset = RouteTarget.objects.all()
    model_form = forms.RouteTargetImportForm
    table = tables.RouteTargetTable


class RouteTargetBulkEditView(generic.BulkEditView):
    queryset = RouteTarget.objects.all()
    filterset = filtersets.RouteTargetFilterSet
    table = tables.RouteTargetTable
    form = forms.RouteTargetBulkEditForm


class RouteTargetBulkDeleteView(generic.BulkDeleteView):
    queryset = RouteTarget.objects.all()
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


@register_model_view(RIR)
class RIRView(generic.ObjectView):
    queryset = RIR.objects.all()

    def get_extra_context(self, request, instance):
        aggregates = Aggregate.objects.restrict(request.user, 'view').filter(rir=instance).annotate(
            child_count=RawSQL('SELECT COUNT(*) FROM ipam_prefix WHERE ipam_prefix.prefix <<= ipam_aggregate.prefix', ())
        )
        aggregates_table = tables.AggregateTable(aggregates, user=request.user, exclude=('rir', 'utilization'))
        aggregates_table.configure(request)

        return {
            'aggregates_table': aggregates_table,
        }


@register_model_view(RIR, 'edit')
class RIREditView(generic.ObjectEditView):
    queryset = RIR.objects.all()
    form = forms.RIRForm


@register_model_view(RIR, 'delete')
class RIRDeleteView(generic.ObjectDeleteView):
    queryset = RIR.objects.all()


class RIRBulkImportView(generic.BulkImportView):
    queryset = RIR.objects.all()
    model_form = forms.RIRImportForm
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
        provider_count=count_related(Provider, 'asns')
    )
    filterset = filtersets.ASNFilterSet
    filterset_form = forms.ASNFilterForm
    table = tables.ASNTable


@register_model_view(ASN)
class ASNView(generic.ObjectView):
    queryset = ASN.objects.all()

    def get_extra_context(self, request, instance):
        # Gather assigned Sites
        sites = instance.sites.restrict(request.user, 'view')
        sites_table = SiteTable(sites, user=request.user)
        sites_table.configure(request)

        # Gather assigned Providers
        providers = instance.providers.restrict(request.user, 'view').annotate(
            count_circuits=count_related(Circuit, 'provider')
        )
        providers_table = ProviderTable(providers, user=request.user)
        providers_table.configure(request)

        return {
            'sites_table': sites_table,
            'sites_count': sites.count(),
            'providers_table': providers_table,
            'providers_count': providers.count(),
        }


@register_model_view(ASN, 'edit')
class ASNEditView(generic.ObjectEditView):
    queryset = ASN.objects.all()
    form = forms.ASNForm


@register_model_view(ASN, 'delete')
class ASNDeleteView(generic.ObjectDeleteView):
    queryset = ASN.objects.all()


class ASNBulkImportView(generic.BulkImportView):
    queryset = ASN.objects.all()
    model_form = forms.ASNImportForm
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


@register_model_view(Aggregate)
class AggregateView(generic.ObjectView):
    queryset = Aggregate.objects.all()


@register_model_view(Aggregate, 'prefixes')
class AggregatePrefixesView(generic.ObjectChildrenView):
    queryset = Aggregate.objects.all()
    child_model = Prefix
    table = tables.PrefixTable
    filterset = filtersets.PrefixFilterSet
    template_name = 'ipam/aggregate/prefixes.html'
    tab = ViewTab(
        label=_('Prefixes'),
        badge=lambda x: x.get_child_prefixes().count(),
        permission='ipam.view_prefix',
        weight=500
    )

    def get_children(self, request, parent):
        return Prefix.objects.restrict(request.user, 'view').filter(
            prefix__net_contained_or_equal=str(parent.prefix)
        ).prefetch_related('site', 'role', 'tenant', 'tenant__group', 'vlan')

    def prep_table_data(self, request, queryset, parent):
        # Determine whether to show assigned prefixes, available prefixes, or both
        show_available = bool(request.GET.get('show_available', 'true') == 'true')
        show_assigned = bool(request.GET.get('show_assigned', 'true') == 'true')

        return add_requested_prefixes(parent.prefix, queryset, show_available, show_assigned)

    def get_extra_context(self, request, instance):
        return {
            'bulk_querystring': f'within={instance.prefix}',
            'first_available_prefix': instance.get_first_available_prefix(),
            'show_available': bool(request.GET.get('show_available', 'true') == 'true'),
            'show_assigned': bool(request.GET.get('show_assigned', 'true') == 'true'),
        }


@register_model_view(Aggregate, 'edit')
class AggregateEditView(generic.ObjectEditView):
    queryset = Aggregate.objects.all()
    form = forms.AggregateForm


@register_model_view(Aggregate, 'delete')
class AggregateDeleteView(generic.ObjectDeleteView):
    queryset = Aggregate.objects.all()


class AggregateBulkImportView(generic.BulkImportView):
    queryset = Aggregate.objects.all()
    model_form = forms.AggregateImportForm
    table = tables.AggregateTable


class AggregateBulkEditView(generic.BulkEditView):
    queryset = Aggregate.objects.annotate(
        child_count=RawSQL('SELECT COUNT(*) FROM ipam_prefix WHERE ipam_prefix.prefix <<= ipam_aggregate.prefix', ())
    )
    filterset = filtersets.AggregateFilterSet
    table = tables.AggregateTable
    form = forms.AggregateBulkEditForm


class AggregateBulkDeleteView(generic.BulkDeleteView):
    queryset = Aggregate.objects.annotate(
        child_count=RawSQL('SELECT COUNT(*) FROM ipam_prefix WHERE ipam_prefix.prefix <<= ipam_aggregate.prefix', ())
    )
    filterset = filtersets.AggregateFilterSet
    table = tables.AggregateTable


#
# Prefix/VLAN roles
#

class RoleListView(generic.ObjectListView):
    queryset = Role.objects.annotate(
        prefix_count=count_related(Prefix, 'role'),
        iprange_count=count_related(IPRange, 'role'),
        vlan_count=count_related(VLAN, 'role')
    )
    filterset = filtersets.RoleFilterSet
    filterset_form = forms.RoleFilterForm
    table = tables.RoleTable


@register_model_view(Role)
class RoleView(generic.ObjectView):
    queryset = Role.objects.all()

    def get_extra_context(self, request, instance):
        prefixes = Prefix.objects.restrict(request.user, 'view').filter(
            role=instance
        )

        prefixes_table = tables.PrefixTable(prefixes, user=request.user, exclude=('role', 'utilization'))
        prefixes_table.configure(request)

        return {
            'prefixes_table': prefixes_table,
        }


@register_model_view(Role, 'edit')
class RoleEditView(generic.ObjectEditView):
    queryset = Role.objects.all()
    form = forms.RoleForm


@register_model_view(Role, 'delete')
class RoleDeleteView(generic.ObjectDeleteView):
    queryset = Role.objects.all()


class RoleBulkImportView(generic.BulkImportView):
    queryset = Role.objects.all()
    model_form = forms.RoleImportForm
    table = tables.RoleTable


class RoleBulkEditView(generic.BulkEditView):
    queryset = Role.objects.all()
    filterset = filtersets.RoleFilterSet
    table = tables.RoleTable
    form = forms.RoleBulkEditForm


class RoleBulkDeleteView(generic.BulkDeleteView):
    queryset = Role.objects.all()
    filterset = filtersets.RoleFilterSet
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


@register_model_view(Prefix)
class PrefixView(generic.ObjectView):
    queryset = Prefix.objects.all()

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
            'site', 'role', 'tenant', 'vlan',
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
            'site', 'role', 'tenant', 'vlan',
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


@register_model_view(Prefix, 'prefixes')
class PrefixPrefixesView(generic.ObjectChildrenView):
    queryset = Prefix.objects.all()
    child_model = Prefix
    table = tables.PrefixTable
    filterset = filtersets.PrefixFilterSet
    template_name = 'ipam/prefix/prefixes.html'
    tab = ViewTab(
        label=_('Child Prefixes'),
        badge=lambda x: x.get_child_prefixes().count(),
        permission='ipam.view_prefix',
        weight=500
    )

    def get_children(self, request, parent):
        return parent.get_child_prefixes().restrict(request.user, 'view').prefetch_related(
            'site', 'vrf', 'vlan', 'role', 'tenant', 'tenant__group'
        )

    def prep_table_data(self, request, queryset, parent):
        # Determine whether to show assigned prefixes, available prefixes, or both
        show_available = bool(request.GET.get('show_available', 'true') == 'true')
        show_assigned = bool(request.GET.get('show_assigned', 'true') == 'true')

        return add_requested_prefixes(parent.prefix, queryset, show_available, show_assigned)

    def get_extra_context(self, request, instance):
        return {
            'bulk_querystring': f"vrf_id={instance.vrf.pk if instance.vrf else '0'}&within={instance.prefix}",
            'first_available_prefix': instance.get_first_available_prefix(),
            'show_available': bool(request.GET.get('show_available', 'true') == 'true'),
            'show_assigned': bool(request.GET.get('show_assigned', 'true') == 'true'),
        }


@register_model_view(Prefix, 'ipranges', path='ip-ranges')
class PrefixIPRangesView(generic.ObjectChildrenView):
    queryset = Prefix.objects.all()
    child_model = IPRange
    table = tables.IPRangeTable
    filterset = filtersets.IPRangeFilterSet
    template_name = 'ipam/prefix/ip_ranges.html'
    tab = ViewTab(
        label=_('Child Ranges'),
        badge=lambda x: x.get_child_ranges().count(),
        permission='ipam.view_iprange',
        weight=600
    )

    def get_children(self, request, parent):
        return parent.get_child_ranges().restrict(request.user, 'view').prefetch_related(
            'tenant__group',
        )

    def get_extra_context(self, request, instance):
        return {
            'bulk_querystring': f"vrf_id={instance.vrf.pk if instance.vrf else '0'}&parent={instance.prefix}",
            'first_available_ip': instance.get_first_available_ip(),
        }


@register_model_view(Prefix, 'ipaddresses', path='ip-addresses')
class PrefixIPAddressesView(generic.ObjectChildrenView):
    queryset = Prefix.objects.all()
    child_model = IPAddress
    table = tables.IPAddressTable
    filterset = filtersets.IPAddressFilterSet
    template_name = 'ipam/prefix/ip_addresses.html'
    tab = ViewTab(
        label=_('IP Addresses'),
        badge=lambda x: x.get_child_ips().count(),
        permission='ipam.view_ipaddress',
        weight=700
    )

    def get_children(self, request, parent):
        return parent.get_child_ips().restrict(request.user, 'view').prefetch_related('vrf', 'tenant', 'tenant__group')

    def prep_table_data(self, request, queryset, parent):
        if not request.GET.get('q') and not request.GET.get('sort'):
            return add_available_ipaddresses(parent.prefix, queryset, parent.is_pool)
        return queryset

    def get_extra_context(self, request, instance):
        return {
            'bulk_querystring': f"vrf_id={instance.vrf.pk if instance.vrf else '0'}&parent={instance.prefix}",
            'first_available_ip': instance.get_first_available_ip(),
        }


@register_model_view(Prefix, 'edit')
class PrefixEditView(generic.ObjectEditView):
    queryset = Prefix.objects.all()
    form = forms.PrefixForm


@register_model_view(Prefix, 'delete')
class PrefixDeleteView(generic.ObjectDeleteView):
    queryset = Prefix.objects.all()


class PrefixBulkImportView(generic.BulkImportView):
    queryset = Prefix.objects.all()
    model_form = forms.PrefixImportForm
    table = tables.PrefixTable


class PrefixBulkEditView(generic.BulkEditView):
    queryset = Prefix.objects.prefetch_related('vrf__tenant')
    filterset = filtersets.PrefixFilterSet
    table = tables.PrefixTable
    form = forms.PrefixBulkEditForm


class PrefixBulkDeleteView(generic.BulkDeleteView):
    queryset = Prefix.objects.prefetch_related('vrf__tenant')
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


@register_model_view(IPRange)
class IPRangeView(generic.ObjectView):
    queryset = IPRange.objects.all()


@register_model_view(IPRange, 'ipaddresses', path='ip-addresses')
class IPRangeIPAddressesView(generic.ObjectChildrenView):
    queryset = IPRange.objects.all()
    child_model = IPAddress
    table = tables.IPAddressTable
    filterset = filtersets.IPAddressFilterSet
    template_name = 'ipam/iprange/ip_addresses.html'
    tab = ViewTab(
        label=_('IP Addresses'),
        badge=lambda x: x.get_child_ips().count(),
        permission='ipam.view_ipaddress',
        weight=500
    )

    def get_children(self, request, parent):
        return parent.get_child_ips().restrict(request.user, 'view')


@register_model_view(IPRange, 'edit')
class IPRangeEditView(generic.ObjectEditView):
    queryset = IPRange.objects.all()
    form = forms.IPRangeForm


@register_model_view(IPRange, 'delete')
class IPRangeDeleteView(generic.ObjectDeleteView):
    queryset = IPRange.objects.all()


class IPRangeBulkImportView(generic.BulkImportView):
    queryset = IPRange.objects.all()
    model_form = forms.IPRangeImportForm
    table = tables.IPRangeTable


class IPRangeBulkEditView(generic.BulkEditView):
    queryset = IPRange.objects.all()
    filterset = filtersets.IPRangeFilterSet
    table = tables.IPRangeTable
    form = forms.IPRangeBulkEditForm


class IPRangeBulkDeleteView(generic.BulkDeleteView):
    queryset = IPRange.objects.all()
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


@register_model_view(IPAddress)
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
        related_ips_table.configure(request)

        # Find services belonging to the IP
        service_filter = Q(ipaddresses=instance)

        # Find services listening on all IPs on the assigned device/vm
        try:
            if instance.assigned_object and instance.assigned_object.parent_object:
                parent_object = instance.assigned_object.parent_object

                if isinstance(parent_object, VirtualMachine):
                    service_filter |= (Q(virtual_machine=parent_object) & Q(ipaddresses=None))
                elif isinstance(parent_object, Device):
                    service_filter |= (Q(device=parent_object) & Q(ipaddresses=None))
        except AttributeError:
            pass

        services = Service.objects.restrict(request.user, 'view').filter(service_filter)

        return {
            'parent_prefixes_table': parent_prefixes_table,
            'duplicate_ips_table': duplicate_ips_table,
            'more_duplicate_ips': duplicate_ips.count() > 10,
            'related_ips_table': related_ips_table,
            'services': services,
        }


@register_model_view(IPAddress, 'edit')
class IPAddressEditView(generic.ObjectEditView):
    queryset = IPAddress.objects.all()
    form = forms.IPAddressForm
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


@register_model_view(IPAddress, 'delete')
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
    model_form = forms.IPAddressImportForm
    table = tables.IPAddressTable


class IPAddressBulkEditView(generic.BulkEditView):
    queryset = IPAddress.objects.prefetch_related('vrf__tenant')
    filterset = filtersets.IPAddressFilterSet
    table = tables.IPAddressTable
    form = forms.IPAddressBulkEditForm


class IPAddressBulkDeleteView(generic.BulkDeleteView):
    queryset = IPAddress.objects.prefetch_related('vrf__tenant')
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


@register_model_view(VLANGroup)
class VLANGroupView(generic.ObjectView):
    queryset = VLANGroup.objects.all()

    def get_extra_context(self, request, instance):
        vlans = VLAN.objects.restrict(request.user, 'view').filter(group=instance).prefetch_related(
            Prefetch('prefixes', queryset=Prefix.objects.restrict(request.user)),
            'tenant', 'site', 'role',
        ).order_by('vid')
        vlans_count = vlans.count()
        vlans = add_available_vlans(vlans, vlan_group=instance)

        vlans_table = tables.VLANTable(vlans, user=request.user, exclude=('group',))
        if request.user.has_perm('ipam.change_vlan') or request.user.has_perm('ipam.delete_vlan'):
            vlans_table.columns.show('pk')
        vlans_table.configure(request)

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


@register_model_view(VLANGroup, 'edit')
class VLANGroupEditView(generic.ObjectEditView):
    queryset = VLANGroup.objects.all()
    form = forms.VLANGroupForm


@register_model_view(VLANGroup, 'delete')
class VLANGroupDeleteView(generic.ObjectDeleteView):
    queryset = VLANGroup.objects.all()


class VLANGroupBulkImportView(generic.BulkImportView):
    queryset = VLANGroup.objects.all()
    model_form = forms.VLANGroupImportForm
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


@register_model_view(FHRPGroup)
class FHRPGroupView(generic.ObjectView):
    queryset = FHRPGroup.objects.all()

    def get_extra_context(self, request, instance):
        # Get assigned IP addresses
        ipaddress_table = tables.AssignedIPAddressesTable(
            data=instance.ip_addresses.restrict(request.user, 'view'),
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


@register_model_view(FHRPGroup, 'edit')
class FHRPGroupEditView(generic.ObjectEditView):
    queryset = FHRPGroup.objects.all()
    form = forms.FHRPGroupForm
    template_name = 'ipam/fhrpgroup_edit.html'

    def get_return_url(self, request, obj=None):
        return_url = super().get_return_url(request, obj)

        # If we're redirecting the user to the FHRPGroupAssignment creation form,
        # initialize the group field with the FHRPGroup we just saved.
        if return_url.startswith(reverse('ipam:fhrpgroupassignment_add')):
            return_url += f'&group={obj.pk}'

        return return_url

    def alter_object(self, obj, request, url_args, url_kwargs):
        # Workaround to solve #10719. Capture the current user on the FHRPGroup instance so that
        # we can evaluate permissions during the creation of a new IPAddress within the form.
        obj._user = request.user
        return obj


@register_model_view(FHRPGroup, 'delete')
class FHRPGroupDeleteView(generic.ObjectDeleteView):
    queryset = FHRPGroup.objects.all()


class FHRPGroupBulkImportView(generic.BulkImportView):
    queryset = FHRPGroup.objects.all()
    model_form = forms.FHRPGroupImportForm
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

@register_model_view(FHRPGroupAssignment, 'edit')
class FHRPGroupAssignmentEditView(generic.ObjectEditView):
    queryset = FHRPGroupAssignment.objects.all()
    form = forms.FHRPGroupAssignmentForm
    template_name = 'ipam/fhrpgroupassignment_edit.html'

    def alter_object(self, instance, request, args, kwargs):
        if not instance.pk:
            # Assign the interface based on URL kwargs
            content_type = get_object_or_404(ContentType, pk=request.GET.get('interface_type'))
            instance.interface = get_object_or_404(content_type.model_class(), pk=request.GET.get('interface_id'))
        return instance


@register_model_view(FHRPGroupAssignment, 'delete')
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


@register_model_view(VLAN)
class VLANView(generic.ObjectView):
    queryset = VLAN.objects.all()

    def get_extra_context(self, request, instance):
        prefixes = Prefix.objects.restrict(request.user, 'view').filter(vlan=instance).prefetch_related(
            'vrf', 'site', 'role', 'tenant'
        )
        prefix_table = tables.PrefixTable(list(prefixes), exclude=('vlan', 'utilization'), orderable=False)

        return {
            'prefix_table': prefix_table,
        }


@register_model_view(VLAN, 'interfaces')
class VLANInterfacesView(generic.ObjectChildrenView):
    queryset = VLAN.objects.all()
    child_model = Interface
    table = tables.VLANDevicesTable
    filterset = InterfaceFilterSet
    template_name = 'ipam/vlan/interfaces.html'
    tab = ViewTab(
        label=_('Device Interfaces'),
        badge=lambda x: x.get_interfaces().count(),
        permission='dcim.view_interface',
        weight=500
    )

    def get_children(self, request, parent):
        return parent.get_interfaces().restrict(request.user, 'view')


@register_model_view(VLAN, 'vminterfaces', path='vm-interfaces')
class VLANVMInterfacesView(generic.ObjectChildrenView):
    queryset = VLAN.objects.all()
    child_model = VMInterface
    table = tables.VLANVirtualMachinesTable
    filterset = VMInterfaceFilterSet
    template_name = 'ipam/vlan/vminterfaces.html'
    tab = ViewTab(
        label=_('VM Interfaces'),
        badge=lambda x: x.get_vminterfaces().count(),
        permission='virtualization.view_vminterface',
        weight=510
    )

    def get_children(self, request, parent):
        return parent.get_vminterfaces().restrict(request.user, 'view')


@register_model_view(VLAN, 'edit')
class VLANEditView(generic.ObjectEditView):
    queryset = VLAN.objects.all()
    form = forms.VLANForm
    template_name = 'ipam/vlan_edit.html'


@register_model_view(VLAN, 'delete')
class VLANDeleteView(generic.ObjectDeleteView):
    queryset = VLAN.objects.all()


class VLANBulkImportView(generic.BulkImportView):
    queryset = VLAN.objects.all()
    model_form = forms.VLANImportForm
    table = tables.VLANTable


class VLANBulkEditView(generic.BulkEditView):
    queryset = VLAN.objects.all()
    filterset = filtersets.VLANFilterSet
    table = tables.VLANTable
    form = forms.VLANBulkEditForm


class VLANBulkDeleteView(generic.BulkDeleteView):
    queryset = VLAN.objects.all()
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


@register_model_view(ServiceTemplate)
class ServiceTemplateView(generic.ObjectView):
    queryset = ServiceTemplate.objects.all()


@register_model_view(ServiceTemplate, 'edit')
class ServiceTemplateEditView(generic.ObjectEditView):
    queryset = ServiceTemplate.objects.all()
    form = forms.ServiceTemplateForm


@register_model_view(ServiceTemplate, 'delete')
class ServiceTemplateDeleteView(generic.ObjectDeleteView):
    queryset = ServiceTemplate.objects.all()


class ServiceTemplateBulkImportView(generic.BulkImportView):
    queryset = ServiceTemplate.objects.all()
    model_form = forms.ServiceTemplateImportForm
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
    queryset = Service.objects.prefetch_related('device', 'virtual_machine')
    filterset = filtersets.ServiceFilterSet
    filterset_form = forms.ServiceFilterForm
    table = tables.ServiceTable


@register_model_view(Service)
class ServiceView(generic.ObjectView):
    queryset = Service.objects.all()


class ServiceCreateView(generic.ObjectEditView):
    queryset = Service.objects.all()
    form = forms.ServiceCreateForm
    template_name = 'ipam/service_create.html'


@register_model_view(Service, 'edit')
class ServiceEditView(generic.ObjectEditView):
    queryset = Service.objects.all()
    form = forms.ServiceForm
    template_name = 'ipam/service_edit.html'


@register_model_view(Service, 'delete')
class ServiceDeleteView(generic.ObjectDeleteView):
    queryset = Service.objects.all()


class ServiceBulkImportView(generic.BulkImportView):
    queryset = Service.objects.all()
    model_form = forms.ServiceImportForm
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


# L2VPN

class L2VPNListView(generic.ObjectListView):
    queryset = L2VPN.objects.all()
    table = L2VPNTable
    filterset = filtersets.L2VPNFilterSet
    filterset_form = forms.L2VPNFilterForm


@register_model_view(L2VPN)
class L2VPNView(generic.ObjectView):
    queryset = L2VPN.objects.all()

    def get_extra_context(self, request, instance):
        terminations = L2VPNTermination.objects.restrict(request.user, 'view').filter(l2vpn=instance)
        terminations_table = tables.L2VPNTerminationTable(terminations, user=request.user, exclude=('l2vpn', ))
        terminations_table.configure(request)

        import_targets_table = tables.RouteTargetTable(
            instance.import_targets.prefetch_related('tenant'),
            orderable=False
        )
        export_targets_table = tables.RouteTargetTable(
            instance.export_targets.prefetch_related('tenant'),
            orderable=False
        )

        return {
            'terminations_table': terminations_table,
            'import_targets_table': import_targets_table,
            'export_targets_table': export_targets_table,
        }


@register_model_view(L2VPN, 'edit')
class L2VPNEditView(generic.ObjectEditView):
    queryset = L2VPN.objects.all()
    form = forms.L2VPNForm


@register_model_view(L2VPN, 'delete')
class L2VPNDeleteView(generic.ObjectDeleteView):
    queryset = L2VPN.objects.all()


class L2VPNBulkImportView(generic.BulkImportView):
    queryset = L2VPN.objects.all()
    model_form = forms.L2VPNImportForm
    table = tables.L2VPNTable


class L2VPNBulkEditView(generic.BulkEditView):
    queryset = L2VPN.objects.all()
    filterset = filtersets.L2VPNFilterSet
    table = tables.L2VPNTable
    form = forms.L2VPNBulkEditForm


class L2VPNBulkDeleteView(generic.BulkDeleteView):
    queryset = L2VPN.objects.all()
    filterset = filtersets.L2VPNFilterSet
    table = tables.L2VPNTable


#
# L2VPN terminations
#

class L2VPNTerminationListView(generic.ObjectListView):
    queryset = L2VPNTermination.objects.all()
    table = L2VPNTerminationTable
    filterset = filtersets.L2VPNTerminationFilterSet
    filterset_form = forms.L2VPNTerminationFilterForm


@register_model_view(L2VPNTermination)
class L2VPNTerminationView(generic.ObjectView):
    queryset = L2VPNTermination.objects.all()


@register_model_view(L2VPNTermination, 'edit')
class L2VPNTerminationEditView(generic.ObjectEditView):
    queryset = L2VPNTermination.objects.all()
    form = forms.L2VPNTerminationForm
    template_name = 'ipam/l2vpntermination_edit.html'


@register_model_view(L2VPNTermination, 'delete')
class L2VPNTerminationDeleteView(generic.ObjectDeleteView):
    queryset = L2VPNTermination.objects.all()


class L2VPNTerminationBulkImportView(generic.BulkImportView):
    queryset = L2VPNTermination.objects.all()
    model_form = forms.L2VPNTerminationImportForm
    table = tables.L2VPNTerminationTable


class L2VPNTerminationBulkEditView(generic.BulkEditView):
    queryset = L2VPNTermination.objects.all()
    filterset = filtersets.L2VPNTerminationFilterSet
    table = tables.L2VPNTerminationTable
    form = forms.L2VPNTerminationBulkEditForm


class L2VPNTerminationBulkDeleteView(generic.BulkDeleteView):
    queryset = L2VPNTermination.objects.all()
    filterset = filtersets.L2VPNTerminationFilterSet
    table = tables.L2VPNTerminationTable
