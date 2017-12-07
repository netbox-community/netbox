from __future__ import unicode_literals

from operator import attrgetter

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import escape
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from django.views.generic import View
from natsort import natsorted

from circuits.models import Circuit
from extras.models import Graph, TopologyMap, GRAPH_TYPE_INTERFACE, GRAPH_TYPE_SITE, UserAction
from ipam.models import Prefix, Service, VLAN
from utilities.forms import ConfirmationForm
from utilities.paginator import EnhancedPaginator
from utilities.views import (
    BulkComponentCreateView, BulkDeleteView, BulkEditView, BulkImportView, ComponentCreateView, ComponentDeleteView,
    ComponentEditView, ObjectDeleteView, ObjectEditView, ObjectListView,
)
from virtualization.models import VirtualMachine
from . import filters, forms, tables
from .constants import CONNECTION_STATUS_CONNECTED
from .models import (
    ConsolePort, ConsolePortTemplate, ConsoleServerPort, ConsoleServerPortTemplate, Device, DeviceBay,
    DeviceBayTemplate, DeviceRole, DeviceType, Interface, InterfaceConnection, InterfaceTemplate, Manufacturer,
    InventoryItem, Platform, PowerOutlet, PowerOutletTemplate, PowerPort, PowerPortTemplate, Rack, RackGroup,
    RackReservation, RackRole, Region, Site,
)


class BulkDisconnectView(View):
    """
    An extendable view for disconnection console/power/interface components in bulk.
    """
    model = None
    form = None
    template_name = 'dcim/bulk_disconnect.html'

    def disconnect_objects(self, objects):
        raise NotImplementedError()

    def post(self, request, pk):

        device = get_object_or_404(Device, pk=pk)
        selected_objects = []

        if '_confirm' in request.POST:
            form = self.form(request.POST)
            if form.is_valid():
                count = self.disconnect_objects(form.cleaned_data['pk'])
                messages.success(request, "Disconnected {} {} on {}".format(
                    count, self.model._meta.verbose_name_plural, device
                ))
                return redirect(device.get_absolute_url())

        else:
            form = self.form(initial={'pk': request.POST.getlist('pk')})
            selected_objects = self.model.objects.filter(pk__in=form.initial['pk'])

        return render(request, self.template_name, {
            'form': form,
            'device': device,
            'obj_type_plural': self.model._meta.verbose_name_plural,
            'selected_objects': selected_objects,
            'return_url': device.get_absolute_url(),
        })


#
# Regions
#

class RegionListView(ObjectListView):
    queryset = Region.objects.annotate(site_count=Count('sites'))
    table = tables.RegionTable
    template_name = 'dcim/region_list.html'


class RegionCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_region'
    model = Region
    model_form = forms.RegionForm

    def get_return_url(self, request, obj):
        return reverse('dcim:region_list')


class RegionEditView(RegionCreateView):
    permission_required = 'dcim.change_region'


class RegionBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_region'
    model_form = forms.RegionCSVForm
    table = tables.RegionTable
    default_return_url = 'dcim:region_list'


class RegionBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_region'
    cls = Region
    queryset = Region.objects.annotate(site_count=Count('sites'))
    table = tables.RegionTable
    default_return_url = 'dcim:region_list'


#
# Sites
#

class SiteListView(ObjectListView):
    queryset = Site.objects.select_related('region', 'tenant')
    filter = filters.SiteFilter
    filter_form = forms.SiteFilterForm
    table = tables.SiteDetailTable
    template_name = 'dcim/site_list.html'


class SiteView(View):

    def get(self, request, slug):

        site = get_object_or_404(Site.objects.select_related('region', 'tenant__group'), slug=slug)
        stats = {
            'rack_count': Rack.objects.filter(site=site).count(),
            'device_count': Device.objects.filter(site=site).count(),
            'prefix_count': Prefix.objects.filter(site=site).count(),
            'vlan_count': VLAN.objects.filter(site=site).count(),
            'circuit_count': Circuit.objects.filter(terminations__site=site).count(),
            'vm_count': VirtualMachine.objects.filter(cluster__site=site).count(),
        }
        rack_groups = RackGroup.objects.filter(site=site).annotate(rack_count=Count('racks'))
        topology_maps = TopologyMap.objects.filter(site=site)
        show_graphs = Graph.objects.filter(type=GRAPH_TYPE_SITE).exists()

        return render(request, 'dcim/site.html', {
            'site': site,
            'stats': stats,
            'rack_groups': rack_groups,
            'topology_maps': topology_maps,
            'show_graphs': show_graphs,
        })


class SiteCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_site'
    model = Site
    model_form = forms.SiteForm
    template_name = 'dcim/site_edit.html'
    default_return_url = 'dcim:site_list'


class SiteEditView(SiteCreateView):
    permission_required = 'dcim.change_site'


class SiteDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_site'
    model = Site
    default_return_url = 'dcim:site_list'


class SiteBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_site'
    model_form = forms.SiteCSVForm
    table = tables.SiteTable
    default_return_url = 'dcim:site_list'


class SiteBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_site'
    cls = Site
    queryset = Site.objects.select_related('region', 'tenant')
    filter = filters.SiteFilter
    table = tables.SiteTable
    form = forms.SiteBulkEditForm
    default_return_url = 'dcim:site_list'


#
# Rack groups
#

class RackGroupListView(ObjectListView):
    queryset = RackGroup.objects.select_related('site').annotate(rack_count=Count('racks'))
    filter = filters.RackGroupFilter
    filter_form = forms.RackGroupFilterForm
    table = tables.RackGroupTable
    template_name = 'dcim/rackgroup_list.html'


class RackGroupCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_rackgroup'
    model = RackGroup
    model_form = forms.RackGroupForm

    def get_return_url(self, request, obj):
        return reverse('dcim:rackgroup_list')


class RackGroupEditView(RackGroupCreateView):
    permission_required = 'dcim.change_rackgroup'


class RackGroupBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_rackgroup'
    model_form = forms.RackGroupCSVForm
    table = tables.RackGroupTable
    default_return_url = 'dcim:rackgroup_list'


class RackGroupBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_rackgroup'
    cls = RackGroup
    queryset = RackGroup.objects.select_related('site').annotate(rack_count=Count('racks'))
    filter = filters.RackGroupFilter
    table = tables.RackGroupTable
    default_return_url = 'dcim:rackgroup_list'


#
# Rack roles
#

class RackRoleListView(ObjectListView):
    queryset = RackRole.objects.annotate(rack_count=Count('racks'))
    table = tables.RackRoleTable
    template_name = 'dcim/rackrole_list.html'


class RackRoleCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_rackrole'
    model = RackRole
    model_form = forms.RackRoleForm

    def get_return_url(self, request, obj):
        return reverse('dcim:rackrole_list')


class RackRoleEditView(RackRoleCreateView):
    permission_required = 'dcim.change_rackrole'


class RackRoleBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_rackrole'
    model_form = forms.RackRoleCSVForm
    table = tables.RackRoleTable
    default_return_url = 'dcim:rackrole_list'


class RackRoleBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_rackrole'
    cls = RackRole
    queryset = RackRole.objects.annotate(rack_count=Count('racks'))
    table = tables.RackRoleTable
    default_return_url = 'dcim:rackrole_list'


#
# Racks
#

class RackListView(ObjectListView):
    queryset = Rack.objects.select_related(
        'site', 'group', 'tenant', 'role'
    ).prefetch_related(
        'devices__device_type'
    ).annotate(
        device_count=Count('devices', distinct=True)
    )
    filter = filters.RackFilter
    filter_form = forms.RackFilterForm
    table = tables.RackDetailTable
    template_name = 'dcim/rack_list.html'


class RackElevationListView(View):
    """
    Display a set of rack elevations side-by-side.
    """

    def get(self, request):

        racks = Rack.objects.select_related(
            'site', 'group', 'tenant', 'role'
        ).prefetch_related(
            'devices__device_type'
        )
        racks = filters.RackFilter(request.GET, racks).qs
        total_count = racks.count()

        # Pagination
        paginator = EnhancedPaginator(racks, 25)
        page_number = request.GET.get('page', 1)
        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)

        # Determine rack face
        if request.GET.get('face') == '1':
            face_id = 1
        else:
            face_id = 0

        return render(request, 'dcim/rack_elevation_list.html', {
            'paginator': paginator,
            'page': page,
            'total_count': total_count,
            'face_id': face_id,
            'filter_form': forms.RackFilterForm(request.GET),
        })


class RackView(View):

    def get(self, request, pk):

        rack = get_object_or_404(Rack.objects.select_related('site__region', 'tenant__group', 'group', 'role'), pk=pk)

        nonracked_devices = Device.objects.filter(rack=rack, position__isnull=True, parent_bay__isnull=True)\
            .select_related('device_type__manufacturer')
        next_rack = Rack.objects.filter(site=rack.site, name__gt=rack.name).order_by('name').first()
        prev_rack = Rack.objects.filter(site=rack.site, name__lt=rack.name).order_by('-name').first()

        reservations = RackReservation.objects.filter(rack=rack)

        return render(request, 'dcim/rack.html', {
            'rack': rack,
            'reservations': reservations,
            'nonracked_devices': nonracked_devices,
            'next_rack': next_rack,
            'prev_rack': prev_rack,
            'front_elevation': rack.get_front_elevation(),
            'rear_elevation': rack.get_rear_elevation(),
        })


class RackCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_rack'
    model = Rack
    model_form = forms.RackForm
    template_name = 'dcim/rack_edit.html'
    default_return_url = 'dcim:rack_list'


class RackEditView(RackCreateView):
    permission_required = 'dcim.change_rack'


class RackDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_rack'
    model = Rack
    default_return_url = 'dcim:rack_list'


class RackBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_rack'
    model_form = forms.RackCSVForm
    table = tables.RackImportTable
    default_return_url = 'dcim:rack_list'


class RackBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_rack'
    cls = Rack
    queryset = Rack.objects.select_related('site', 'group', 'tenant', 'role')
    filter = filters.RackFilter
    table = tables.RackTable
    form = forms.RackBulkEditForm
    default_return_url = 'dcim:rack_list'


class RackBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_rack'
    cls = Rack
    queryset = Rack.objects.select_related('site', 'group', 'tenant', 'role')
    filter = filters.RackFilter
    table = tables.RackTable
    default_return_url = 'dcim:rack_list'


#
# Rack reservations
#

class RackReservationListView(ObjectListView):
    queryset = RackReservation.objects.all()
    filter = filters.RackReservationFilter
    filter_form = forms.RackReservationFilterForm
    table = tables.RackReservationTable
    template_name = 'dcim/rackreservation_list.html'


class RackReservationCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_rackreservation'
    model = RackReservation
    model_form = forms.RackReservationForm

    def alter_obj(self, obj, request, args, kwargs):
        if not obj.pk:
            obj.rack = get_object_or_404(Rack, pk=kwargs['rack'])
            obj.user = request.user
        return obj

    def get_return_url(self, request, obj):
        return obj.rack.get_absolute_url()


class RackReservationEditView(RackReservationCreateView):
    permission_required = 'dcim.change_rackreservation'


class RackReservationDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_rackreservation'
    model = RackReservation

    def get_return_url(self, request, obj):
        return obj.rack.get_absolute_url()


class RackReservationBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_rackreservation'
    cls = RackReservation
    queryset = RackReservation.objects.select_related('rack', 'user')
    filter = filters.RackReservationFilter
    table = tables.RackReservationTable
    form = forms.RackReservationBulkEditForm
    default_return_url = 'dcim:rackreservation_list'


class RackReservationBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_rackreservation'
    cls = RackReservation
    table = tables.RackReservationTable
    default_return_url = 'dcim:rackreservation_list'


#
# Manufacturers
#

class ManufacturerListView(ObjectListView):
    queryset = Manufacturer.objects.annotate(devicetype_count=Count('device_types'))
    table = tables.ManufacturerTable
    template_name = 'dcim/manufacturer_list.html'


class ManufacturerCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_manufacturer'
    model = Manufacturer
    model_form = forms.ManufacturerForm

    def get_return_url(self, request, obj):
        return reverse('dcim:manufacturer_list')


class ManufacturerEditView(ManufacturerCreateView):
    permission_required = 'dcim.change_manufacturer'


class ManufacturerBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_manufacturer'
    model_form = forms.ManufacturerCSVForm
    table = tables.ManufacturerTable
    default_return_url = 'dcim:manufacturer_list'


class ManufacturerBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_manufacturer'
    cls = Manufacturer
    queryset = Manufacturer.objects.annotate(devicetype_count=Count('device_types'))
    table = tables.ManufacturerTable
    default_return_url = 'dcim:manufacturer_list'


#
# Device types
#

class DeviceTypeListView(ObjectListView):
    queryset = DeviceType.objects.select_related('manufacturer').annotate(instance_count=Count('instances'))
    filter = filters.DeviceTypeFilter
    filter_form = forms.DeviceTypeFilterForm
    table = tables.DeviceTypeTable
    template_name = 'dcim/devicetype_list.html'


class DeviceTypeView(View):

    def get(self, request, pk):

        devicetype = get_object_or_404(DeviceType, pk=pk)

        # Component tables
        consoleport_table = tables.ConsolePortTemplateTable(
            natsorted(ConsolePortTemplate.objects.filter(device_type=devicetype), key=attrgetter('name')),
            show_header=False
        )
        consoleserverport_table = tables.ConsoleServerPortTemplateTable(
            natsorted(ConsoleServerPortTemplate.objects.filter(device_type=devicetype), key=attrgetter('name')),
            show_header=False
        )
        powerport_table = tables.PowerPortTemplateTable(
            natsorted(PowerPortTemplate.objects.filter(device_type=devicetype), key=attrgetter('name')),
            show_header=False
        )
        poweroutlet_table = tables.PowerOutletTemplateTable(
            natsorted(PowerOutletTemplate.objects.filter(device_type=devicetype), key=attrgetter('name')),
            show_header=False
        )
        interface_table = tables.InterfaceTemplateTable(
            list(InterfaceTemplate.objects.order_naturally(
                devicetype.interface_ordering
            ).filter(device_type=devicetype)),
            show_header=False
        )
        devicebay_table = tables.DeviceBayTemplateTable(
            natsorted(DeviceBayTemplate.objects.filter(device_type=devicetype), key=attrgetter('name')),
            show_header=False
        )
        if request.user.has_perm('dcim.change_devicetype'):
            consoleport_table.columns.show('pk')
            consoleserverport_table.columns.show('pk')
            powerport_table.columns.show('pk')
            poweroutlet_table.columns.show('pk')
            interface_table.columns.show('pk')
            devicebay_table.columns.show('pk')

        return render(request, 'dcim/devicetype.html', {
            'devicetype': devicetype,
            'consoleport_table': consoleport_table,
            'consoleserverport_table': consoleserverport_table,
            'powerport_table': powerport_table,
            'poweroutlet_table': poweroutlet_table,
            'interface_table': interface_table,
            'devicebay_table': devicebay_table,
        })


class DeviceTypeCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_devicetype'
    model = DeviceType
    model_form = forms.DeviceTypeForm
    template_name = 'dcim/devicetype_edit.html'
    default_return_url = 'dcim:devicetype_list'


class DeviceTypeEditView(DeviceTypeCreateView):
    permission_required = 'dcim.change_devicetype'


class DeviceTypeDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_devicetype'
    model = DeviceType
    default_return_url = 'dcim:devicetype_list'


class DeviceTypeBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_devicetype'
    model_form = forms.DeviceTypeCSVForm
    table = tables.DeviceTypeTable
    default_return_url = 'dcim:devicetype_list'


class DeviceTypeBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_devicetype'
    cls = DeviceType
    queryset = DeviceType.objects.select_related('manufacturer').annotate(instance_count=Count('instances'))
    filter = filters.DeviceTypeFilter
    table = tables.DeviceTypeTable
    form = forms.DeviceTypeBulkEditForm
    default_return_url = 'dcim:devicetype_list'


class DeviceTypeBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_devicetype'
    cls = DeviceType
    queryset = DeviceType.objects.select_related('manufacturer').annotate(instance_count=Count('instances'))
    filter = filters.DeviceTypeFilter
    table = tables.DeviceTypeTable
    default_return_url = 'dcim:devicetype_list'


#
# Device type components
#

class ConsolePortTemplateCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_consoleporttemplate'
    parent_model = DeviceType
    parent_field = 'device_type'
    model = ConsolePortTemplate
    form = forms.ConsolePortTemplateCreateForm
    model_form = forms.ConsolePortTemplateForm
    template_name = 'dcim/device_component_add.html'


class ConsolePortTemplateBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_consoleporttemplate'
    parent_model = DeviceType
    parent_field = 'device_type'
    cls = ConsolePortTemplate
    parent_cls = DeviceType
    table = tables.ConsolePortTemplateTable


class ConsoleServerPortTemplateCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_consoleserverporttemplate'
    parent_model = DeviceType
    parent_field = 'device_type'
    model = ConsoleServerPortTemplate
    form = forms.ConsoleServerPortTemplateCreateForm
    model_form = forms.ConsoleServerPortTemplateForm
    template_name = 'dcim/device_component_add.html'


class ConsoleServerPortTemplateBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_consoleserverporttemplate'
    cls = ConsoleServerPortTemplate
    parent_cls = DeviceType
    table = tables.ConsoleServerPortTemplateTable


class PowerPortTemplateCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_powerporttemplate'
    parent_model = DeviceType
    parent_field = 'device_type'
    model = PowerPortTemplate
    form = forms.PowerPortTemplateCreateForm
    model_form = forms.PowerPortTemplateForm
    template_name = 'dcim/device_component_add.html'


class PowerPortTemplateBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_powerporttemplate'
    cls = PowerPortTemplate
    parent_cls = DeviceType
    table = tables.PowerPortTemplateTable


class PowerOutletTemplateCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_poweroutlettemplate'
    parent_model = DeviceType
    parent_field = 'device_type'
    model = PowerOutletTemplate
    form = forms.PowerOutletTemplateCreateForm
    model_form = forms.PowerOutletTemplateForm
    template_name = 'dcim/device_component_add.html'


class PowerOutletTemplateBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_poweroutlettemplate'
    cls = PowerOutletTemplate
    parent_cls = DeviceType
    table = tables.PowerOutletTemplateTable


class InterfaceTemplateCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_interfacetemplate'
    parent_model = DeviceType
    parent_field = 'device_type'
    model = InterfaceTemplate
    form = forms.InterfaceTemplateCreateForm
    model_form = forms.InterfaceTemplateForm
    template_name = 'dcim/device_component_add.html'


class InterfaceTemplateBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_interfacetemplate'
    cls = InterfaceTemplate
    parent_cls = DeviceType
    table = tables.InterfaceTemplateTable
    form = forms.InterfaceTemplateBulkEditForm


class InterfaceTemplateBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_interfacetemplate'
    cls = InterfaceTemplate
    parent_cls = DeviceType
    table = tables.InterfaceTemplateTable


class DeviceBayTemplateCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_devicebaytemplate'
    parent_model = DeviceType
    parent_field = 'device_type'
    model = DeviceBayTemplate
    form = forms.DeviceBayTemplateCreateForm
    model_form = forms.DeviceBayTemplateForm
    template_name = 'dcim/device_component_add.html'


class DeviceBayTemplateBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_devicebaytemplate'
    cls = DeviceBayTemplate
    parent_cls = DeviceType
    table = tables.DeviceBayTemplateTable


#
# Device roles
#

class DeviceRoleListView(ObjectListView):
    queryset = DeviceRole.objects.annotate(
        device_count=Count('devices', distinct=True),
        vm_count=Count('virtual_machines', distinct=True)
    )
    table = tables.DeviceRoleTable
    template_name = 'dcim/devicerole_list.html'


class DeviceRoleCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_devicerole'
    model = DeviceRole
    model_form = forms.DeviceRoleForm

    def get_return_url(self, request, obj):
        return reverse('dcim:devicerole_list')


class DeviceRoleEditView(DeviceRoleCreateView):
    permission_required = 'dcim.change_devicerole'


class DeviceRoleBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_devicerole'
    model_form = forms.DeviceRoleCSVForm
    table = tables.DeviceRoleTable
    default_return_url = 'dcim:devicerole_list'


class DeviceRoleBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_devicerole'
    cls = DeviceRole
    queryset = DeviceRole.objects.annotate(device_count=Count('devices'))
    table = tables.DeviceRoleTable
    default_return_url = 'dcim:devicerole_list'


#
# Platforms
#

class PlatformListView(ObjectListView):
    queryset = Platform.objects.annotate(device_count=Count('devices'))
    table = tables.PlatformTable
    template_name = 'dcim/platform_list.html'


class PlatformCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_platform'
    model = Platform
    model_form = forms.PlatformForm

    def get_return_url(self, request, obj):
        return reverse('dcim:platform_list')


class PlatformEditView(PlatformCreateView):
    permission_required = 'dcim.change_platform'


class PlatformBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_platform'
    model_form = forms.PlatformCSVForm
    table = tables.PlatformTable
    default_return_url = 'dcim:platform_list'


class PlatformBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_platform'
    cls = Platform
    queryset = Platform.objects.annotate(device_count=Count('devices'))
    table = tables.PlatformTable
    default_return_url = 'dcim:platform_list'


#
# Devices
#

class DeviceListView(ObjectListView):
    queryset = Device.objects.select_related('device_type__manufacturer', 'device_role', 'tenant', 'site', 'rack',
                                             'primary_ip4', 'primary_ip6')
    filter = filters.DeviceFilter
    filter_form = forms.DeviceFilterForm
    table = tables.DeviceDetailTable
    template_name = 'dcim/device_list.html'


class DeviceView(View):

    def get(self, request, pk):

        device = get_object_or_404(Device.objects.select_related(
            'site__region', 'rack__group', 'tenant__group', 'device_role', 'platform'
        ), pk=pk)
        console_ports = natsorted(
            ConsolePort.objects.filter(device=device).select_related('cs_port__device'), key=attrgetter('name')
        )
        cs_ports = ConsoleServerPort.objects.filter(device=device).select_related('connected_console')
        power_ports = natsorted(
            PowerPort.objects.filter(device=device).select_related('power_outlet__device'), key=attrgetter('name')
        )
        power_outlets = PowerOutlet.objects.filter(device=device).select_related('connected_port')
        interfaces = Interface.objects.order_naturally(
            device.device_type.interface_ordering
        ).filter(
            device=device
        ).select_related(
            'connected_as_a__interface_b__device', 'connected_as_b__interface_a__device',
            'circuit_termination__circuit'
        ).prefetch_related('ip_addresses')
        device_bays = natsorted(
            DeviceBay.objects.filter(device=device).select_related('installed_device__device_type__manufacturer'),
            key=attrgetter('name')
        )
        services = Service.objects.filter(device=device)
        secrets = device.secrets.all()

        # Find up to ten devices in the same site with the same functional role for quick reference.
        related_devices = Device.objects.filter(
            site=device.site, device_role=device.device_role
        ).exclude(
            pk=device.pk
        ).select_related(
            'rack', 'device_type__manufacturer'
        )[:10]

        # Show graph button on interfaces only if at least one graph has been created.
        show_graphs = Graph.objects.filter(type=GRAPH_TYPE_INTERFACE).exists()

        return render(request, 'dcim/device.html', {
            'device': device,
            'console_ports': console_ports,
            'cs_ports': cs_ports,
            'power_ports': power_ports,
            'power_outlets': power_outlets,
            'interfaces': interfaces,
            'device_bays': device_bays,
            'services': services,
            'secrets': secrets,
            'related_devices': related_devices,
            'show_graphs': show_graphs,
        })


class DeviceInventoryView(View):

    def get(self, request, pk):

        device = get_object_or_404(Device, pk=pk)
        inventory_items = InventoryItem.objects.filter(
            device=device, parent=None
        ).select_related(
            'manufacturer'
        ).prefetch_related(
            'child_items'
        )

        return render(request, 'dcim/device_inventory.html', {
            'device': device,
            'inventory_items': inventory_items,
        })


class DeviceStatusView(PermissionRequiredMixin, View):
    permission_required = 'dcim.napalm_read'

    def get(self, request, pk):

        device = get_object_or_404(Device, pk=pk)

        return render(request, 'dcim/device_status.html', {
            'device': device,
        })


class DeviceLLDPNeighborsView(PermissionRequiredMixin, View):
    permission_required = 'dcim.napalm_read'

    def get(self, request, pk):

        device = get_object_or_404(Device, pk=pk)
        interfaces = Interface.objects.order_naturally(
            device.device_type.interface_ordering
        ).connectable().filter(
            device=device
        ).select_related(
            'connected_as_a', 'connected_as_b'
        )

        return render(request, 'dcim/device_lldp_neighbors.html', {
            'device': device,
            'interfaces': interfaces,
        })


class DeviceConfigView(PermissionRequiredMixin, View):
    permission_required = 'dcim.napalm_read'

    def get(self, request, pk):

        device = get_object_or_404(Device, pk=pk)

        return render(request, 'dcim/device_config.html', {
            'device': device,
        })


class DeviceCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_device'
    model = Device
    model_form = forms.DeviceForm
    template_name = 'dcim/device_edit.html'
    default_return_url = 'dcim:device_list'


class DeviceEditView(DeviceCreateView):
    permission_required = 'dcim.change_device'


class DeviceDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_device'
    model = Device
    default_return_url = 'dcim:device_list'


class DeviceBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_device'
    model_form = forms.DeviceCSVForm
    table = tables.DeviceImportTable
    template_name = 'dcim/device_import.html'
    default_return_url = 'dcim:device_list'


class ChildDeviceBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_device'
    model_form = forms.ChildDeviceCSVForm
    table = tables.DeviceImportTable
    template_name = 'dcim/device_import_child.html'
    default_return_url = 'dcim:device_list'

    def _save_obj(self, obj_form):

        obj = obj_form.save()

        # Save the reverse relation to the parent device bay
        device_bay = obj.parent_bay
        device_bay.installed_device = obj
        device_bay.save()

        return obj


class DeviceBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_device'
    cls = Device
    queryset = Device.objects.select_related('tenant', 'site', 'rack', 'device_role', 'device_type__manufacturer')
    filter = filters.DeviceFilter
    table = tables.DeviceTable
    form = forms.DeviceBulkEditForm
    default_return_url = 'dcim:device_list'


class DeviceBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_device'
    cls = Device
    queryset = Device.objects.select_related('tenant', 'site', 'rack', 'device_role', 'device_type__manufacturer')
    filter = filters.DeviceFilter
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


#
# Console ports
#

class ConsolePortCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_consoleport'
    parent_model = Device
    parent_field = 'device'
    model = ConsolePort
    form = forms.ConsolePortCreateForm
    model_form = forms.ConsolePortForm
    template_name = 'dcim/device_component_add.html'


@permission_required('dcim.change_consoleport')
def consoleport_connect(request, pk):

    consoleport = get_object_or_404(ConsolePort, pk=pk)

    if request.method == 'POST':
        form = forms.ConsolePortConnectionForm(request.POST, instance=consoleport)
        if form.is_valid():
            consoleport = form.save()
            msg = 'Connected <a href="{}">{}</a> {} to <a href="{}">{}</a> {}'.format(
                consoleport.device.get_absolute_url(),
                escape(consoleport.device),
                escape(consoleport.name),
                consoleport.cs_port.device.get_absolute_url(),
                escape(consoleport.cs_port.device),
                escape(consoleport.cs_port.name),
            )
            messages.success(request, mark_safe(msg))
            UserAction.objects.log_edit(request.user, consoleport, msg)
            return redirect('dcim:device', pk=consoleport.device.pk)

    else:
        form = forms.ConsolePortConnectionForm(instance=consoleport, initial={
            'site': request.GET.get('site'),
            'rack': request.GET.get('rack'),
            'console_server': request.GET.get('console_server'),
            'connection_status': CONNECTION_STATUS_CONNECTED,
        })

    return render(request, 'dcim/consoleport_connect.html', {
        'consoleport': consoleport,
        'form': form,
        'return_url': reverse('dcim:device', kwargs={'pk': consoleport.device.pk}),
    })


@permission_required('dcim.change_consoleport')
def consoleport_disconnect(request, pk):

    consoleport = get_object_or_404(ConsolePort, pk=pk)

    if not consoleport.cs_port:
        messages.warning(
            request, "Cannot disconnect console port {}: It is not connected to anything.".format(consoleport)
        )
        return redirect('dcim:device', pk=consoleport.device.pk)

    if request.method == 'POST':
        form = ConfirmationForm(request.POST)
        if form.is_valid():
            cs_port = consoleport.cs_port
            consoleport.cs_port = None
            consoleport.connection_status = None
            consoleport.save()
            msg = 'Disconnected <a href="{}">{}</a> {} from <a href="{}">{}</a> {}'.format(
                consoleport.device.get_absolute_url(),
                escape(consoleport.device),
                escape(consoleport.name),
                cs_port.device.get_absolute_url(),
                escape(cs_port.device),
                escape(cs_port.name),
            )
            messages.success(request, mark_safe(msg))
            UserAction.objects.log_edit(request.user, consoleport, msg)
            return redirect('dcim:device', pk=consoleport.device.pk)

    else:
        form = ConfirmationForm()

    return render(request, 'dcim/consoleport_disconnect.html', {
        'consoleport': consoleport,
        'form': form,
        'return_url': reverse('dcim:device', kwargs={'pk': consoleport.device.pk}),
    })


class ConsolePortEditView(PermissionRequiredMixin, ComponentEditView):
    permission_required = 'dcim.change_consoleport'
    model = ConsolePort
    parent_field = 'device'
    model_form = forms.ConsolePortForm


class ConsolePortDeleteView(PermissionRequiredMixin, ComponentDeleteView):
    permission_required = 'dcim.delete_consoleport'
    model = ConsolePort
    parent_field = 'device'


class ConsolePortBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_consoleport'
    cls = ConsolePort
    parent_cls = Device
    table = tables.ConsolePortTable


class ConsoleConnectionsBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.change_consoleport'
    model_form = forms.ConsoleConnectionCSVForm
    table = tables.ConsoleConnectionTable
    default_return_url = 'dcim:console_connections_list'


#
# Console server ports
#

class ConsoleServerPortCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_consoleserverport'
    parent_model = Device
    parent_field = 'device'
    model = ConsoleServerPort
    form = forms.ConsoleServerPortCreateForm
    model_form = forms.ConsoleServerPortForm
    template_name = 'dcim/device_component_add.html'


@permission_required('dcim.change_consoleserverport')
def consoleserverport_connect(request, pk):

    consoleserverport = get_object_or_404(ConsoleServerPort, pk=pk)

    if request.method == 'POST':
        form = forms.ConsoleServerPortConnectionForm(request.POST)
        if form.is_valid():
            consoleport = form.cleaned_data['port']
            consoleport.cs_port = consoleserverport
            consoleport.connection_status = form.cleaned_data['connection_status']
            consoleport.save()
            msg = 'Connected <a href="{}">{}</a> {} to <a href="{}">{}</a> {}'.format(
                consoleport.device.get_absolute_url(),
                escape(consoleport.device),
                escape(consoleport.name),
                consoleserverport.device.get_absolute_url(),
                escape(consoleserverport.device),
                escape(consoleserverport.name),
            )
            messages.success(request, mark_safe(msg))
            UserAction.objects.log_edit(request.user, consoleport, msg)
            return redirect('dcim:device', pk=consoleserverport.device.pk)

    else:
        form = forms.ConsoleServerPortConnectionForm(initial={
            'site': request.GET.get('site'),
            'rack': request.GET.get('rack'),
            'device': request.GET.get('device'),
            'connection_status': CONNECTION_STATUS_CONNECTED,
        })

    return render(request, 'dcim/consoleserverport_connect.html', {
        'consoleserverport': consoleserverport,
        'form': form,
        'return_url': reverse('dcim:device', kwargs={'pk': consoleserverport.device.pk}),
    })


@permission_required('dcim.change_consoleserverport')
def consoleserverport_disconnect(request, pk):

    consoleserverport = get_object_or_404(ConsoleServerPort, pk=pk)

    if not hasattr(consoleserverport, 'connected_console'):
        messages.warning(
            request, "Cannot disconnect console server port {}: Nothing is connected to it.".format(consoleserverport)
        )
        return redirect('dcim:device', pk=consoleserverport.device.pk)

    if request.method == 'POST':
        form = ConfirmationForm(request.POST)
        if form.is_valid():
            consoleport = consoleserverport.connected_console
            consoleport.cs_port = None
            consoleport.connection_status = None
            consoleport.save()
            msg = 'Disconnected <a href="{}">{}</a> {} from <a href="{}">{}</a> {}'.format(
                consoleport.device.get_absolute_url(),
                escape(consoleport.device),
                escape(consoleport.name),
                consoleserverport.device.get_absolute_url(),
                escape(consoleserverport.device),
                escape(consoleserverport.name),
            )
            messages.success(request, mark_safe(msg))
            UserAction.objects.log_edit(request.user, consoleport, msg)
            return redirect('dcim:device', pk=consoleserverport.device.pk)

    else:
        form = ConfirmationForm()

    return render(request, 'dcim/consoleserverport_disconnect.html', {
        'consoleserverport': consoleserverport,
        'form': form,
        'return_url': reverse('dcim:device', kwargs={'pk': consoleserverport.device.pk}),
    })


class ConsoleServerPortEditView(PermissionRequiredMixin, ComponentEditView):
    permission_required = 'dcim.change_consoleserverport'
    model = ConsoleServerPort
    parent_field = 'device'
    model_form = forms.ConsoleServerPortForm


class ConsoleServerPortDeleteView(PermissionRequiredMixin, ComponentDeleteView):
    permission_required = 'dcim.delete_consoleserverport'
    model = ConsoleServerPort
    parent_field = 'device'


class ConsoleServerPortBulkDisconnectView(PermissionRequiredMixin, BulkDisconnectView):
    permission_required = 'dcim.change_consoleserverport'
    model = ConsoleServerPort
    form = forms.ConsoleServerPortBulkDisconnectForm

    def disconnect_objects(self, cs_ports):
        return ConsolePort.objects.filter(cs_port__in=cs_ports).update(cs_port=None, connection_status=None)


class ConsoleServerPortBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_consoleserverport'
    cls = ConsoleServerPort
    parent_cls = Device
    table = tables.ConsoleServerPortTable


#
# Power ports
#

class PowerPortCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_powerport'
    parent_model = Device
    parent_field = 'device'
    model = PowerPort
    form = forms.PowerPortCreateForm
    model_form = forms.PowerPortForm
    template_name = 'dcim/device_component_add.html'


@permission_required('dcim.change_powerport')
def powerport_connect(request, pk):

    powerport = get_object_or_404(PowerPort, pk=pk)

    if request.method == 'POST':
        form = forms.PowerPortConnectionForm(request.POST, instance=powerport)
        if form.is_valid():
            powerport = form.save()
            msg = 'Connected <a href="{}">{}</a> {} to <a href="{}">{}</a> {}'.format(
                powerport.device.get_absolute_url(),
                escape(powerport.device),
                escape(powerport.name),
                powerport.power_outlet.device.get_absolute_url(),
                escape(powerport.power_outlet.device),
                escape(powerport.power_outlet.name),
            )
            messages.success(request, mark_safe(msg))
            UserAction.objects.log_edit(request.user, powerport, msg)
            return redirect('dcim:device', pk=powerport.device.pk)

    else:
        form = forms.PowerPortConnectionForm(instance=powerport, initial={
            'site': request.GET.get('site'),
            'rack': request.GET.get('rack'),
            'pdu': request.GET.get('pdu'),
            'connection_status': CONNECTION_STATUS_CONNECTED,
        })

    return render(request, 'dcim/powerport_connect.html', {
        'powerport': powerport,
        'form': form,
        'return_url': reverse('dcim:device', kwargs={'pk': powerport.device.pk}),
    })


@permission_required('dcim.change_powerport')
def powerport_disconnect(request, pk):

    powerport = get_object_or_404(PowerPort, pk=pk)

    if not powerport.power_outlet:
        messages.warning(
            request, "Cannot disconnect power port {}: It is not connected to an outlet.".format(powerport)
        )
        return redirect('dcim:device', pk=powerport.device.pk)

    if request.method == 'POST':
        form = ConfirmationForm(request.POST)
        if form.is_valid():
            power_outlet = powerport.power_outlet
            powerport.power_outlet = None
            powerport.connection_status = None
            powerport.save()
            msg = 'Disconnected <a href="{}">{}</a> {} from <a href="{}">{}</a> {}'.format(
                powerport.device.get_absolute_url(),
                escape(powerport.device),
                escape(powerport.name),
                power_outlet.device.get_absolute_url(),
                escape(power_outlet.device),
                escape(power_outlet.name),
            )
            messages.success(request, mark_safe(msg))
            UserAction.objects.log_edit(request.user, powerport, msg)
            return redirect('dcim:device', pk=powerport.device.pk)

    else:
        form = ConfirmationForm()

    return render(request, 'dcim/powerport_disconnect.html', {
        'powerport': powerport,
        'form': form,
        'return_url': reverse('dcim:device', kwargs={'pk': powerport.device.pk}),
    })


class PowerPortEditView(PermissionRequiredMixin, ComponentEditView):
    permission_required = 'dcim.change_powerport'
    model = PowerPort
    parent_field = 'device'
    model_form = forms.PowerPortForm


class PowerPortDeleteView(PermissionRequiredMixin, ComponentDeleteView):
    permission_required = 'dcim.delete_powerport'
    model = PowerPort
    parent_field = 'device'


class PowerPortBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_powerport'
    cls = PowerPort
    parent_cls = Device
    table = tables.PowerPortTable


class PowerConnectionsBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.change_powerport'
    model_form = forms.PowerConnectionCSVForm
    table = tables.PowerConnectionTable
    default_return_url = 'dcim:power_connections_list'


#
# Power outlets
#

class PowerOutletCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_poweroutlet'
    parent_model = Device
    parent_field = 'device'
    model = PowerOutlet
    form = forms.PowerOutletCreateForm
    model_form = forms.PowerOutletForm
    template_name = 'dcim/device_component_add.html'


@permission_required('dcim.change_poweroutlet')
def poweroutlet_connect(request, pk):

    poweroutlet = get_object_or_404(PowerOutlet, pk=pk)

    if request.method == 'POST':
        form = forms.PowerOutletConnectionForm(request.POST)
        if form.is_valid():
            powerport = form.cleaned_data['port']
            powerport.power_outlet = poweroutlet
            powerport.connection_status = form.cleaned_data['connection_status']
            powerport.save()
            msg = 'Connected <a href="{}">{}</a> {} to <a href="{}">{}</a> {}'.format(
                powerport.device.get_absolute_url(),
                escape(powerport.device),
                escape(powerport.name),
                poweroutlet.device.get_absolute_url(),
                escape(poweroutlet.device),
                escape(poweroutlet.name),
            )
            messages.success(request, mark_safe(msg))
            UserAction.objects.log_edit(request.user, powerport, msg)
            return redirect('dcim:device', pk=poweroutlet.device.pk)

    else:
        form = forms.PowerOutletConnectionForm(initial={
            'site': request.GET.get('site'),
            'rack': request.GET.get('rack'),
            'device': request.GET.get('device'),
            'connection_status': CONNECTION_STATUS_CONNECTED,
        })

    return render(request, 'dcim/poweroutlet_connect.html', {
        'poweroutlet': poweroutlet,
        'form': form,
        'return_url': reverse('dcim:device', kwargs={'pk': poweroutlet.device.pk}),
    })


@permission_required('dcim.change_poweroutlet')
def poweroutlet_disconnect(request, pk):

    poweroutlet = get_object_or_404(PowerOutlet, pk=pk)

    if not hasattr(poweroutlet, 'connected_port'):
        messages.warning(
            request, "Cannot disconnect power outlet {}: Nothing is connected to it.".format(poweroutlet)
        )
        return redirect('dcim:device', pk=poweroutlet.device.pk)

    if request.method == 'POST':
        form = ConfirmationForm(request.POST)
        if form.is_valid():
            powerport = poweroutlet.connected_port
            powerport.power_outlet = None
            powerport.connection_status = None
            powerport.save()
            msg = 'Disconnected <a href="{}">{}</a> {} from <a href="{}">{}</a> {}'.format(
                powerport.device.get_absolute_url(),
                escape(powerport.device),
                escape(powerport.name),
                poweroutlet.device.get_absolute_url(),
                escape(poweroutlet.device),
                escape(poweroutlet.name),
            )
            messages.success(request, mark_safe(msg))
            UserAction.objects.log_edit(request.user, powerport, msg)
            return redirect('dcim:device', pk=poweroutlet.device.pk)

    else:
        form = ConfirmationForm()

    return render(request, 'dcim/poweroutlet_disconnect.html', {
        'poweroutlet': poweroutlet,
        'form': form,
        'return_url': reverse('dcim:device', kwargs={'pk': poweroutlet.device.pk}),
    })


class PowerOutletEditView(PermissionRequiredMixin, ComponentEditView):
    permission_required = 'dcim.change_poweroutlet'
    model = PowerOutlet
    parent_field = 'device'
    model_form = forms.PowerOutletForm


class PowerOutletDeleteView(PermissionRequiredMixin, ComponentDeleteView):
    permission_required = 'dcim.delete_poweroutlet'
    model = PowerOutlet
    parent_field = 'device'


class PowerOutletBulkDisconnectView(PermissionRequiredMixin, BulkDisconnectView):
    permission_required = 'dcim.change_poweroutlet'
    model = PowerOutlet
    form = forms.PowerOutletBulkDisconnectForm

    def disconnect_objects(self, power_outlets):
        return PowerPort.objects.filter(power_outlet__in=power_outlets).update(
            power_outlet=None, connection_status=None
        )


class PowerOutletBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_poweroutlet'
    cls = PowerOutlet
    parent_cls = Device
    table = tables.PowerOutletTable


#
# Interfaces
#

class InterfaceCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_interface'
    parent_model = Device
    parent_field = 'device'
    model = Interface
    form = forms.InterfaceCreateForm
    model_form = forms.InterfaceForm
    template_name = 'dcim/device_component_add.html'


class InterfaceEditView(PermissionRequiredMixin, ComponentEditView):
    permission_required = 'dcim.change_interface'
    model = Interface
    parent_field = 'device'
    model_form = forms.InterfaceForm


class InterfaceDeleteView(PermissionRequiredMixin, ComponentDeleteView):
    permission_required = 'dcim.delete_interface'
    model = Interface
    parent_field = 'device'


class InterfaceBulkDisconnectView(PermissionRequiredMixin, BulkDisconnectView):
    permission_required = 'dcim.change_interface'
    model = Interface
    form = forms.InterfaceBulkDisconnectForm

    def disconnect_objects(self, interfaces):
        count, _ = InterfaceConnection.objects.filter(
            Q(interface_a__in=interfaces) | Q(interface_b__in=interfaces)
        ).delete()
        return count


class InterfaceBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_interface'
    cls = Interface
    parent_cls = Device
    table = tables.InterfaceTable
    form = forms.InterfaceBulkEditForm


class InterfaceBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_interface'
    cls = Interface
    parent_cls = Device
    table = tables.InterfaceTable


#
# Device bays
#

class DeviceBayCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_devicebay'
    parent_model = Device
    parent_field = 'device'
    model = DeviceBay
    form = forms.DeviceBayCreateForm
    model_form = forms.DeviceBayForm
    template_name = 'dcim/device_component_add.html'


class DeviceBayEditView(PermissionRequiredMixin, ComponentEditView):
    permission_required = 'dcim.change_devicebay'
    model = DeviceBay
    parent_field = 'device'
    model_form = forms.DeviceBayForm


class DeviceBayDeleteView(PermissionRequiredMixin, ComponentDeleteView):
    permission_required = 'dcim.delete_devicebay'
    model = DeviceBay
    parent_field = 'device'


@permission_required('dcim.change_devicebay')
def devicebay_populate(request, pk):

    device_bay = get_object_or_404(DeviceBay, pk=pk)

    if request.method == 'POST':
        form = forms.PopulateDeviceBayForm(device_bay, request.POST)
        if form.is_valid():

            device_bay.installed_device = form.cleaned_data['installed_device']
            device_bay.save()

            if not form.errors:
                messages.success(request, "Added {} to {}.".format(device_bay.installed_device, device_bay))
                return redirect('dcim:device', pk=device_bay.device.pk)

    else:
        form = forms.PopulateDeviceBayForm(device_bay)

    return render(request, 'dcim/devicebay_populate.html', {
        'device_bay': device_bay,
        'form': form,
        'return_url': reverse('dcim:device', kwargs={'pk': device_bay.device.pk}),
    })


@permission_required('dcim.change_devicebay')
def devicebay_depopulate(request, pk):

    device_bay = get_object_or_404(DeviceBay, pk=pk)

    if request.method == 'POST':
        form = ConfirmationForm(request.POST)
        if form.is_valid():
            removed_device = device_bay.installed_device
            device_bay.installed_device = None
            device_bay.save()
            messages.success(request, "{} has been removed from {}.".format(removed_device, device_bay))
            return redirect('dcim:device', pk=device_bay.device.pk)

    else:
        form = ConfirmationForm()

    return render(request, 'dcim/devicebay_depopulate.html', {
        'device_bay': device_bay,
        'form': form,
        'return_url': reverse('dcim:device', kwargs={'pk': device_bay.device.pk}),
    })


class DeviceBayBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_devicebay'
    cls = DeviceBay
    parent_cls = Device
    table = tables.DeviceBayTable


#
# Bulk Device component creation
#

class DeviceBulkAddConsolePortView(PermissionRequiredMixin, BulkComponentCreateView):
    permission_required = 'dcim.add_consoleport'
    parent_model = Device
    parent_field = 'device'
    form = forms.DeviceBulkAddComponentForm
    model = ConsolePort
    model_form = forms.ConsolePortForm
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


class DeviceBulkAddConsoleServerPortView(PermissionRequiredMixin, BulkComponentCreateView):
    permission_required = 'dcim.add_consoleserverport'
    parent_model = Device
    parent_field = 'device'
    form = forms.DeviceBulkAddComponentForm
    model = ConsoleServerPort
    model_form = forms.ConsoleServerPortForm
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


class DeviceBulkAddPowerPortView(PermissionRequiredMixin, BulkComponentCreateView):
    permission_required = 'dcim.add_powerport'
    parent_model = Device
    parent_field = 'device'
    form = forms.DeviceBulkAddComponentForm
    model = PowerPort
    model_form = forms.PowerPortForm
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


class DeviceBulkAddPowerOutletView(PermissionRequiredMixin, BulkComponentCreateView):
    permission_required = 'dcim.add_poweroutlet'
    parent_model = Device
    parent_field = 'device'
    form = forms.DeviceBulkAddComponentForm
    model = PowerOutlet
    model_form = forms.PowerOutletForm
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


class DeviceBulkAddInterfaceView(PermissionRequiredMixin, BulkComponentCreateView):
    permission_required = 'dcim.add_interface'
    parent_model = Device
    parent_field = 'device'
    form = forms.DeviceBulkAddInterfaceForm
    model = Interface
    model_form = forms.InterfaceForm
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


class DeviceBulkAddDeviceBayView(PermissionRequiredMixin, BulkComponentCreateView):
    permission_required = 'dcim.add_devicebay'
    parent_model = Device
    parent_field = 'device'
    form = forms.DeviceBulkAddComponentForm
    model = DeviceBay
    model_form = forms.DeviceBayForm
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


#
# Interface connections
#

@permission_required('dcim.add_interfaceconnection')
def interfaceconnection_add(request, pk):

    device = get_object_or_404(Device, pk=pk)

    if request.method == 'POST':
        form = forms.InterfaceConnectionForm(device, request.POST)
        if form.is_valid():

            interfaceconnection = form.save()
            msg = 'Connected <a href="{}">{}</a> {} to <a href="{}">{}</a> {}'.format(
                interfaceconnection.interface_a.device.get_absolute_url(),
                escape(interfaceconnection.interface_a.device),
                escape(interfaceconnection.interface_a.name),
                interfaceconnection.interface_b.device.get_absolute_url(),
                escape(interfaceconnection.interface_b.device),
                escape(interfaceconnection.interface_b.name),
            )
            messages.success(request, mark_safe(msg))
            UserAction.objects.log_edit(request.user, interfaceconnection, msg)

            if '_addanother' in request.POST:
                base_url = reverse('dcim:interfaceconnection_add', kwargs={'pk': device.pk})
                device_b = interfaceconnection.interface_b.device
                params = urlencode({
                    'rack_b': device_b.rack.pk if device_b.rack else '',
                    'device_b': device_b.pk,
                })
                return HttpResponseRedirect('{}?{}'.format(base_url, params))
            else:
                return redirect('dcim:device', pk=device.pk)

    else:
        form = forms.InterfaceConnectionForm(device, initial={
            'interface_a': request.GET.get('interface_a'),
            'site_b': request.GET.get('site_b'),
            'rack_b': request.GET.get('rack_b'),
            'device_b': request.GET.get('device_b'),
            'interface_b': request.GET.get('interface_b'),
        })

    return render(request, 'dcim/interfaceconnection_edit.html', {
        'device': device,
        'form': form,
        'return_url': reverse('dcim:device', kwargs={'pk': device.pk}),
    })


@permission_required('dcim.delete_interfaceconnection')
def interfaceconnection_delete(request, pk):

    interfaceconnection = get_object_or_404(InterfaceConnection, pk=pk)
    device_id = request.GET.get('device', None)

    if request.method == 'POST':
        form = forms.InterfaceConnectionDeletionForm(request.POST)
        if form.is_valid():
            interfaceconnection.delete()
            msg = 'Disconnected <a href="{}">{}</a> {} from <a href="{}">{}</a> {}'.format(
                interfaceconnection.interface_a.device.get_absolute_url(),
                escape(interfaceconnection.interface_a.device),
                escape(interfaceconnection.interface_a.name),
                interfaceconnection.interface_b.device.get_absolute_url(),
                escape(interfaceconnection.interface_b.device),
                escape(interfaceconnection.interface_b.name),
            )
            messages.success(request, mark_safe(msg))
            UserAction.objects.log_edit(request.user, interfaceconnection, msg)
            if form.cleaned_data['device']:
                return redirect('dcim:device', pk=form.cleaned_data['device'].pk)
            else:
                return redirect('dcim:device_list')

    else:
        form = forms.InterfaceConnectionDeletionForm(initial={
            'device': device_id,
        })

    # Determine where to direct user upon cancellation
    if device_id:
        return_url = reverse('dcim:device', kwargs={'pk': device_id})
    else:
        return_url = reverse('dcim:device_list')

    return render(request, 'dcim/interfaceconnection_delete.html', {
        'interfaceconnection': interfaceconnection,
        'device_id': device_id,
        'form': form,
        'return_url': return_url,
    })


class InterfaceConnectionsBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.change_interface'
    model_form = forms.InterfaceConnectionCSVForm
    table = tables.InterfaceConnectionTable
    default_return_url = 'dcim:interface_connections_list'


#
# Connections
#

class ConsoleConnectionsListView(ObjectListView):
    queryset = ConsolePort.objects.select_related('device', 'cs_port__device').filter(cs_port__isnull=False)\
        .order_by('cs_port__device__name', 'cs_port__name')
    filter = filters.ConsoleConnectionFilter
    filter_form = forms.ConsoleConnectionFilterForm
    table = tables.ConsoleConnectionTable
    template_name = 'dcim/console_connections_list.html'


class PowerConnectionsListView(ObjectListView):
    queryset = PowerPort.objects.select_related('device', 'power_outlet__device').filter(power_outlet__isnull=False)\
        .order_by('power_outlet__device__name', 'power_outlet__name')
    filter = filters.PowerConnectionFilter
    filter_form = forms.PowerConnectionFilterForm
    table = tables.PowerConnectionTable
    template_name = 'dcim/power_connections_list.html'


class InterfaceConnectionsListView(ObjectListView):
    queryset = InterfaceConnection.objects.select_related('interface_a__device', 'interface_b__device')\
        .order_by('interface_a__device__name', 'interface_a__name')
    filter = filters.InterfaceConnectionFilter
    filter_form = forms.InterfaceConnectionFilterForm
    table = tables.InterfaceConnectionTable
    template_name = 'dcim/interface_connections_list.html'


#
# Inventory items
#

class InventoryItemEditView(PermissionRequiredMixin, ComponentEditView):
    permission_required = 'dcim.change_inventoryitem'
    model = InventoryItem
    parent_field = 'device'
    model_form = forms.InventoryItemForm

    def alter_obj(self, obj, request, url_args, url_kwargs):
        if 'device' in url_kwargs:
            obj.device = get_object_or_404(Device, pk=url_kwargs['device'])
        return obj


class InventoryItemDeleteView(PermissionRequiredMixin, ComponentDeleteView):
    permission_required = 'dcim.delete_inventoryitem'
    model = InventoryItem
    parent_field = 'device'
