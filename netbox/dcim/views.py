from __future__ import unicode_literals

from operator import attrgetter

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db.models import Count, Q
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import escape
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from django.views.generic import View
from natsort import natsorted

from circuits.models import Circuit
from extras.models import Graph, TopologyMap, GRAPH_TYPE_INTERFACE, GRAPH_TYPE_SITE
from extras.views import ObjectConfigContextView
from ipam.models import Prefix, Service, VLAN
from ipam.tables import InterfaceIPAddressTable, InterfaceVLANTable
from utilities.forms import ConfirmationForm
from utilities.paginator import EnhancedPaginator
from utilities.views import (
    BulkComponentCreateView, BulkDeleteView, BulkEditView, BulkImportView, ComponentCreateView, GetReturnURLMixin,
    ObjectDeleteView, ObjectEditView, ObjectListView,
)
from virtualization.models import VirtualMachine
from . import filters, forms, tables
from .constants import CONNECTION_STATUS_CONNECTED
from .models import (
    ConsolePort, ConsolePortTemplate, ConsoleServerPort, ConsoleServerPortTemplate, Device, DeviceBay,
    DeviceBayTemplate, DeviceRole, DeviceType, Interface, InterfaceConnection, InterfaceTemplate, Manufacturer,
    InventoryItem, Platform, PowerOutlet, PowerOutletTemplate, PowerPort, PowerPortTemplate, Rack, RackGroup,
    RackReservation, RackRole, Region, Site, VirtualChassis,
)


class BulkRenameView(GetReturnURLMixin, View):
    """
    An extendable view for renaming device components in bulk.
    """
    queryset = None
    form = None
    template_name = 'dcim/bulk_rename.html'

    def post(self, request):

        model = self.queryset.model

        if '_preview' in request.POST or '_apply' in request.POST:
            form = self.form(request.POST, initial={'pk': request.POST.getlist('pk')})
            selected_objects = self.queryset.filter(pk__in=form.initial['pk'])

            if form.is_valid():
                for obj in selected_objects:
                    obj.new_name = obj.name.replace(form.cleaned_data['find'], form.cleaned_data['replace'])

                if '_apply' in request.POST:
                    for obj in selected_objects:
                        obj.name = obj.new_name
                        obj.save()
                    messages.success(request, "Renamed {} {}".format(
                        len(selected_objects),
                        model._meta.verbose_name_plural
                    ))
                    return redirect(self.get_return_url(request))

        else:
            form = self.form(initial={'pk': request.POST.getlist('pk')})
            selected_objects = self.queryset.filter(pk__in=form.initial['pk'])

        return render(request, self.template_name, {
            'form': form,
            'obj_type_plural': model._meta.verbose_name_plural,
            'selected_objects': selected_objects,
            'return_url': self.get_return_url(request),
        })


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
    filter = filters.RegionFilter
    filter_form = forms.RegionFilterForm
    table = tables.RegionTable
    template_name = 'dcim/region_list.html'


class RegionCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_region'
    model = Region
    model_form = forms.RegionForm
    default_return_url = 'dcim:region_list'


class RegionEditView(RegionCreateView):
    permission_required = 'dcim.change_region'


class RegionBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_region'
    model_form = forms.RegionCSVForm
    table = tables.RegionTable
    default_return_url = 'dcim:region_list'


class RegionBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_region'
    queryset = Region.objects.annotate(site_count=Count('sites'))
    filter = filters.RegionFilter
    table = tables.RegionTable
    default_return_url = 'dcim:region_list'


#
# Sites
#

class SiteListView(ObjectListView):
    queryset = Site.objects.select_related('region', 'tenant')
    filter = filters.SiteFilter
    filter_form = forms.SiteFilterForm
    table = tables.SiteTable
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
    default_return_url = 'dcim:rackgroup_list'


class RackGroupEditView(RackGroupCreateView):
    permission_required = 'dcim.change_rackgroup'


class RackGroupBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_rackgroup'
    model_form = forms.RackGroupCSVForm
    table = tables.RackGroupTable
    default_return_url = 'dcim:rackgroup_list'


class RackGroupBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_rackgroup'
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
    default_return_url = 'dcim:rackrole_list'


class RackRoleEditView(RackRoleCreateView):
    permission_required = 'dcim.change_rackrole'


class RackRoleBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_rackrole'
    model_form = forms.RackRoleCSVForm
    table = tables.RackRoleTable
    default_return_url = 'dcim:rackrole_list'


class RackRoleBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_rackrole'
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
        device_count=Count('devices')
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

        nonracked_devices = Device.objects.filter(rack=rack, position__isnull=True, parent_bay__isnull=True) \
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
    queryset = Rack.objects.select_related('site', 'group', 'tenant', 'role')
    filter = filters.RackFilter
    table = tables.RackTable
    form = forms.RackBulkEditForm
    default_return_url = 'dcim:rack_list'


class RackBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_rack'
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
    queryset = RackReservation.objects.select_related('rack', 'user')
    filter = filters.RackReservationFilter
    table = tables.RackReservationTable
    form = forms.RackReservationBulkEditForm
    default_return_url = 'dcim:rackreservation_list'


class RackReservationBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_rackreservation'
    queryset = RackReservation.objects.select_related('rack', 'user')
    filter = filters.RackReservationFilter
    table = tables.RackReservationTable
    default_return_url = 'dcim:rackreservation_list'


#
# Manufacturers
#

class ManufacturerListView(ObjectListView):
    queryset = Manufacturer.objects.annotate(
        devicetype_count=Count('device_types', distinct=True),
        platform_count=Count('platforms', distinct=True),
    )
    table = tables.ManufacturerTable
    template_name = 'dcim/manufacturer_list.html'


class ManufacturerCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_manufacturer'
    model = Manufacturer
    model_form = forms.ManufacturerForm
    default_return_url = 'dcim:manufacturer_list'


class ManufacturerEditView(ManufacturerCreateView):
    permission_required = 'dcim.change_manufacturer'


class ManufacturerBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_manufacturer'
    model_form = forms.ManufacturerCSVForm
    table = tables.ManufacturerTable
    default_return_url = 'dcim:manufacturer_list'


class ManufacturerBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_manufacturer'
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
            orderable=False
        )
        consoleserverport_table = tables.ConsoleServerPortTemplateTable(
            natsorted(ConsoleServerPortTemplate.objects.filter(device_type=devicetype), key=attrgetter('name')),
            orderable=False
        )
        powerport_table = tables.PowerPortTemplateTable(
            natsorted(PowerPortTemplate.objects.filter(device_type=devicetype), key=attrgetter('name')),
            orderable=False
        )
        poweroutlet_table = tables.PowerOutletTemplateTable(
            natsorted(PowerOutletTemplate.objects.filter(device_type=devicetype), key=attrgetter('name')),
            orderable=False
        )
        interface_table = tables.InterfaceTemplateTable(
            list(InterfaceTemplate.objects.order_naturally(
                devicetype.interface_ordering
            ).filter(device_type=devicetype)),
            orderable=False
        )
        devicebay_table = tables.DeviceBayTemplateTable(
            natsorted(DeviceBayTemplate.objects.filter(device_type=devicetype), key=attrgetter('name')),
            orderable=False
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
    queryset = DeviceType.objects.select_related('manufacturer').annotate(instance_count=Count('instances'))
    filter = filters.DeviceTypeFilter
    table = tables.DeviceTypeTable
    form = forms.DeviceTypeBulkEditForm
    default_return_url = 'dcim:devicetype_list'


class DeviceTypeBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_devicetype'
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
    queryset = ConsolePortTemplate.objects.all()
    parent_model = DeviceType
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
    queryset = ConsoleServerPortTemplate.objects.all()
    parent_model = DeviceType
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
    queryset = PowerPortTemplate.objects.all()
    parent_model = DeviceType
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
    queryset = PowerOutletTemplate.objects.all()
    parent_model = DeviceType
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
    queryset = InterfaceTemplate.objects.all()
    parent_model = DeviceType
    table = tables.InterfaceTemplateTable
    form = forms.InterfaceTemplateBulkEditForm


class InterfaceTemplateBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_interfacetemplate'
    queryset = InterfaceTemplate.objects.all()
    parent_model = DeviceType
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
    queryset = DeviceBayTemplate.objects.all()
    parent_model = DeviceType
    table = tables.DeviceBayTemplateTable


#
# Device roles
#

class DeviceRoleListView(ObjectListView):
    queryset = DeviceRole.objects.all()
    table = tables.DeviceRoleTable
    template_name = 'dcim/devicerole_list.html'


class DeviceRoleCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_devicerole'
    model = DeviceRole
    model_form = forms.DeviceRoleForm
    default_return_url = 'dcim:devicerole_list'


class DeviceRoleEditView(DeviceRoleCreateView):
    permission_required = 'dcim.change_devicerole'


class DeviceRoleBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_devicerole'
    model_form = forms.DeviceRoleCSVForm
    table = tables.DeviceRoleTable
    default_return_url = 'dcim:devicerole_list'


class DeviceRoleBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_devicerole'
    queryset = DeviceRole.objects.all()
    table = tables.DeviceRoleTable
    default_return_url = 'dcim:devicerole_list'


#
# Platforms
#

class PlatformListView(ObjectListView):
    queryset = Platform.objects.all()
    table = tables.PlatformTable
    template_name = 'dcim/platform_list.html'


class PlatformCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_platform'
    model = Platform
    model_form = forms.PlatformForm
    default_return_url = 'dcim:platform_list'


class PlatformEditView(PlatformCreateView):
    permission_required = 'dcim.change_platform'


class PlatformBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_platform'
    model_form = forms.PlatformCSVForm
    table = tables.PlatformTable
    default_return_url = 'dcim:platform_list'


class PlatformBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_platform'
    queryset = Platform.objects.all()
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

        # VirtualChassis members
        if device.virtual_chassis is not None:
            vc_members = Device.objects.filter(virtual_chassis=device.virtual_chassis).order_by('vc_position')
        else:
            vc_members = []

        # Console ports
        console_ports = natsorted(
            ConsolePort.objects.filter(device=device).select_related('cs_port__device'), key=attrgetter('name')
        )

        # Console server ports
        cs_ports = ConsoleServerPort.objects.filter(device=device).select_related('connected_console')

        # Power ports
        power_ports = natsorted(
            PowerPort.objects.filter(device=device).select_related('power_outlet__device'), key=attrgetter('name')
        )

        # Power outlets
        power_outlets = PowerOutlet.objects.filter(device=device).select_related('connected_port')

        # Interfaces
        interfaces = device.vc_interfaces.order_naturally(
            device.device_type.interface_ordering
        ).select_related(
            'connected_as_a__interface_b__device', 'connected_as_b__interface_a__device',
            'circuit_termination__circuit'
        ).prefetch_related('ip_addresses')

        # Device bays
        device_bays = natsorted(
            DeviceBay.objects.filter(device=device).select_related('installed_device__device_type__manufacturer'),
            key=attrgetter('name')
        )

        # Services
        services = Service.objects.filter(device=device)

        # Secrets
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
            'vc_members': vc_members,
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
            'active_tab': 'inventory',
        })


class DeviceStatusView(PermissionRequiredMixin, View):
    permission_required = 'dcim.napalm_read'

    def get(self, request, pk):

        device = get_object_or_404(Device, pk=pk)

        return render(request, 'dcim/device_status.html', {
            'device': device,
            'active_tab': 'status',
        })


class DeviceLLDPNeighborsView(PermissionRequiredMixin, View):
    permission_required = 'dcim.napalm_read'

    def get(self, request, pk):

        device = get_object_or_404(Device, pk=pk)
        interfaces = device.vc_interfaces.order_naturally(
            device.device_type.interface_ordering
        ).connectable().select_related(
            'connected_as_a', 'connected_as_b'
        )

        return render(request, 'dcim/device_lldp_neighbors.html', {
            'device': device,
            'interfaces': interfaces,
            'active_tab': 'lldp-neighbors',
        })


class DeviceConfigView(PermissionRequiredMixin, View):
    permission_required = 'dcim.napalm_read'

    def get(self, request, pk):

        device = get_object_or_404(Device, pk=pk)

        return render(request, 'dcim/device_config.html', {
            'device': device,
            'active_tab': 'config',
        })


class DeviceConfigContextView(ObjectConfigContextView):
    object_class = Device
    base_template = 'dcim/device.html'


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
    queryset = Device.objects.select_related('tenant', 'site', 'rack', 'device_role', 'device_type__manufacturer')
    filter = filters.DeviceFilter
    table = tables.DeviceTable
    form = forms.DeviceBulkEditForm
    default_return_url = 'dcim:device_list'


class DeviceBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_device'
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


class ConsolePortConnectView(PermissionRequiredMixin, View):
    permission_required = 'dcim.change_consoleport'

    def get(self, request, pk):

        consoleport = get_object_or_404(ConsolePort, pk=pk)
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

    def post(self, request, pk):

        consoleport = get_object_or_404(ConsolePort, pk=pk)
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

            return redirect('dcim:device', pk=consoleport.device.pk)

        return render(request, 'dcim/consoleport_connect.html', {
            'consoleport': consoleport,
            'form': form,
            'return_url': reverse('dcim:device', kwargs={'pk': consoleport.device.pk}),
        })


class ConsolePortDisconnectView(PermissionRequiredMixin, View):
    permission_required = 'dcim.change_consoleport'

    def get(self, request, pk):

        consoleport = get_object_or_404(ConsolePort, pk=pk)
        form = ConfirmationForm()

        if not consoleport.cs_port:
            messages.warning(
                request, "Cannot disconnect console port {}: It is not connected to anything.".format(consoleport)
            )
            return redirect('dcim:device', pk=consoleport.device.pk)

        return render(request, 'dcim/consoleport_disconnect.html', {
            'consoleport': consoleport,
            'form': form,
            'return_url': reverse('dcim:device', kwargs={'pk': consoleport.device.pk}),
        })

    def post(self, request, pk):

        consoleport = get_object_or_404(ConsolePort, pk=pk)
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

            return redirect('dcim:device', pk=consoleport.device.pk)

        return render(request, 'dcim/consoleport_disconnect.html', {
            'consoleport': consoleport,
            'form': form,
            'return_url': reverse('dcim:device', kwargs={'pk': consoleport.device.pk}),
        })


class ConsolePortEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_consoleport'
    model = ConsolePort
    model_form = forms.ConsolePortForm


class ConsolePortDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_consoleport'
    model = ConsolePort


class ConsolePortBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_consoleport'
    queryset = ConsolePort.objects.all()
    parent_model = Device
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


class ConsoleServerPortConnectView(PermissionRequiredMixin, View):
    permission_required = 'dcim.change_consoleserverport'

    def get(self, request, pk):

        consoleserverport = get_object_or_404(ConsoleServerPort, pk=pk)
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

    def post(self, request, pk):

        consoleserverport = get_object_or_404(ConsoleServerPort, pk=pk)
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

            return redirect('dcim:device', pk=consoleserverport.device.pk)

        return render(request, 'dcim/consoleserverport_connect.html', {
            'consoleserverport': consoleserverport,
            'form': form,
            'return_url': reverse('dcim:device', kwargs={'pk': consoleserverport.device.pk}),
        })


class ConsoleServerPortDisconnectView(PermissionRequiredMixin, View):
    permission_required = 'dcim.change_consoleserverport'

    def get(self, request, pk):

        consoleserverport = get_object_or_404(ConsoleServerPort, pk=pk)
        form = ConfirmationForm()

        if not hasattr(consoleserverport, 'connected_console'):
            messages.warning(
                request,
                "Cannot disconnect console server port {}: Nothing is connected to it.".format(consoleserverport)
            )
            return redirect('dcim:device', pk=consoleserverport.device.pk)

        return render(request, 'dcim/consoleserverport_disconnect.html', {
            'consoleserverport': consoleserverport,
            'form': form,
            'return_url': reverse('dcim:device', kwargs={'pk': consoleserverport.device.pk}),
        })

    def post(self, request, pk):

        consoleserverport = get_object_or_404(ConsoleServerPort, pk=pk)
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

            return redirect('dcim:device', pk=consoleserverport.device.pk)

        return render(request, 'dcim/consoleserverport_disconnect.html', {
            'consoleserverport': consoleserverport,
            'form': form,
            'return_url': reverse('dcim:device', kwargs={'pk': consoleserverport.device.pk}),
        })


class ConsoleServerPortEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_consoleserverport'
    model = ConsoleServerPort
    model_form = forms.ConsoleServerPortForm


class ConsoleServerPortDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_consoleserverport'
    model = ConsoleServerPort


class ConsoleServerPortBulkRenameView(PermissionRequiredMixin, BulkRenameView):
    permission_required = 'dcim.change_consoleserverport'
    queryset = ConsoleServerPort.objects.all()
    form = forms.ConsoleServerPortBulkRenameForm


class ConsoleServerPortBulkDisconnectView(PermissionRequiredMixin, BulkDisconnectView):
    permission_required = 'dcim.change_consoleserverport'
    model = ConsoleServerPort
    form = forms.ConsoleServerPortBulkDisconnectForm

    def disconnect_objects(self, cs_ports):
        return ConsolePort.objects.filter(cs_port__in=cs_ports).update(cs_port=None, connection_status=None)


class ConsoleServerPortBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_consoleserverport'
    queryset = ConsoleServerPort.objects.all()
    parent_model = Device
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


class PowerPortConnectView(PermissionRequiredMixin, View):
    permission_required = 'dcim.change_powerport'

    def get(self, request, pk):

        powerport = get_object_or_404(PowerPort, pk=pk)
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

    def post(self, request, pk):

        powerport = get_object_or_404(PowerPort, pk=pk)
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

            return redirect('dcim:device', pk=powerport.device.pk)

        return render(request, 'dcim/powerport_connect.html', {
            'powerport': powerport,
            'form': form,
            'return_url': reverse('dcim:device', kwargs={'pk': powerport.device.pk}),
        })


class PowerPortDisconnectView(PermissionRequiredMixin, View):
    permission_required = 'dcim.change_powerport'

    def get(self, request, pk):

        powerport = get_object_or_404(PowerPort, pk=pk)
        form = ConfirmationForm()

        if not powerport.power_outlet:
            messages.warning(
                request, "Cannot disconnect power port {}: It is not connected to an outlet.".format(powerport)
            )
            return redirect('dcim:device', pk=powerport.device.pk)

        return render(request, 'dcim/powerport_disconnect.html', {
            'powerport': powerport,
            'form': form,
            'return_url': reverse('dcim:device', kwargs={'pk': powerport.device.pk}),
        })

    def post(self, request, pk):

        powerport = get_object_or_404(PowerPort, pk=pk)
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

            return redirect('dcim:device', pk=powerport.device.pk)

        return render(request, 'dcim/powerport_disconnect.html', {
            'powerport': powerport,
            'form': form,
            'return_url': reverse('dcim:device', kwargs={'pk': powerport.device.pk}),
        })


class PowerPortEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_powerport'
    model = PowerPort
    model_form = forms.PowerPortForm


class PowerPortDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_powerport'
    model = PowerPort


class PowerPortBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_powerport'
    queryset = PowerPort.objects.all()
    parent_model = Device
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


class PowerOutletConnectView(PermissionRequiredMixin, View):
    permission_required = 'dcim.change_poweroutlet'

    def get(self, request, pk):

        poweroutlet = get_object_or_404(PowerOutlet, pk=pk)
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

    def post(self, request, pk):

        poweroutlet = get_object_or_404(PowerOutlet, pk=pk)
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

            return redirect('dcim:device', pk=poweroutlet.device.pk)

        return render(request, 'dcim/poweroutlet_connect.html', {
            'poweroutlet': poweroutlet,
            'form': form,
            'return_url': reverse('dcim:device', kwargs={'pk': poweroutlet.device.pk}),
        })


class PowerOutletDisconnectView(PermissionRequiredMixin, View):
    permission_required = 'dcim.change_poweroutlet'

    def get(self, request, pk):

        poweroutlet = get_object_or_404(PowerOutlet, pk=pk)
        form = ConfirmationForm()

        if not hasattr(poweroutlet, 'connected_port'):
            messages.warning(
                request, "Cannot disconnect power outlet {}: Nothing is connected to it.".format(poweroutlet)
            )
            return redirect('dcim:device', pk=poweroutlet.device.pk)

        return render(request, 'dcim/poweroutlet_disconnect.html', {
            'poweroutlet': poweroutlet,
            'form': form,
            'return_url': reverse('dcim:device', kwargs={'pk': poweroutlet.device.pk}),
        })

    def post(self, request, pk):

        poweroutlet = get_object_or_404(PowerOutlet, pk=pk)
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

            return redirect('dcim:device', pk=poweroutlet.device.pk)

        return render(request, 'dcim/poweroutlet_disconnect.html', {
            'poweroutlet': poweroutlet,
            'form': form,
            'return_url': reverse('dcim:device', kwargs={'pk': poweroutlet.device.pk}),
        })


class PowerOutletEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_poweroutlet'
    model = PowerOutlet
    model_form = forms.PowerOutletForm


class PowerOutletDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_poweroutlet'
    model = PowerOutlet


class PowerOutletBulkRenameView(PermissionRequiredMixin, BulkRenameView):
    permission_required = 'dcim.change_poweroutlet'
    queryset = PowerOutlet.objects.all()
    form = forms.PowerOutletBulkRenameForm


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
    queryset = PowerOutlet.objects.all()
    parent_model = Device
    table = tables.PowerOutletTable


#
# Interfaces
#

class InterfaceView(View):

    def get(self, request, pk):

        interface = get_object_or_404(Interface, pk=pk)

        # Get connected interface
        connected_interface = interface.connected_interface
        if connected_interface is None and hasattr(interface, 'circuit_termination'):
            peer_termination = interface.circuit_termination.get_peer_termination()
            if peer_termination is not None:
                connected_interface = peer_termination.interface

        # Get assigned IP addresses
        ipaddress_table = InterfaceIPAddressTable(
            data=interface.ip_addresses.select_related('vrf', 'tenant'),
            orderable=False
        )

        # Get assigned VLANs and annotate whether each is tagged or untagged
        vlans = []
        if interface.untagged_vlan is not None:
            vlans.append(interface.untagged_vlan)
            vlans[0].tagged = False
        for vlan in interface.tagged_vlans.select_related('site', 'group', 'tenant', 'role'):
            vlan.tagged = True
            vlans.append(vlan)
        vlan_table = InterfaceVLANTable(
            interface=interface,
            data=vlans,
            orderable=False
        )

        return render(request, 'dcim/interface.html', {
            'interface': interface,
            'connected_interface': connected_interface,
            'ipaddress_table': ipaddress_table,
            'vlan_table': vlan_table,
        })


class InterfaceCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_interface'
    parent_model = Device
    parent_field = 'device'
    model = Interface
    form = forms.InterfaceCreateForm
    model_form = forms.InterfaceForm
    template_name = 'dcim/device_component_add.html'


class InterfaceEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_interface'
    model = Interface
    model_form = forms.InterfaceForm
    template_name = 'dcim/interface_edit.html'


class InterfaceAssignVLANsView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_interface'
    model = Interface
    model_form = forms.InterfaceAssignVLANsForm


class InterfaceDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_interface'
    model = Interface


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
    queryset = Interface.objects.all()
    parent_model = Device
    table = tables.InterfaceTable
    form = forms.InterfaceBulkEditForm


class InterfaceBulkRenameView(PermissionRequiredMixin, BulkRenameView):
    permission_required = 'dcim.change_interface'
    queryset = Interface.objects.order_naturally()
    form = forms.InterfaceBulkRenameForm


class InterfaceBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_interface'
    queryset = Interface.objects.all()
    parent_model = Device
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


class DeviceBayEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_devicebay'
    model = DeviceBay
    model_form = forms.DeviceBayForm


class DeviceBayDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_devicebay'
    model = DeviceBay


class DeviceBayPopulateView(PermissionRequiredMixin, View):
    permission_required = 'dcim.change_devicebay'

    def get(self, request, pk):

        device_bay = get_object_or_404(DeviceBay, pk=pk)
        form = forms.PopulateDeviceBayForm(device_bay)

        return render(request, 'dcim/devicebay_populate.html', {
            'device_bay': device_bay,
            'form': form,
            'return_url': reverse('dcim:device', kwargs={'pk': device_bay.device.pk}),
        })

    def post(self, request, pk):

        device_bay = get_object_or_404(DeviceBay, pk=pk)
        form = forms.PopulateDeviceBayForm(device_bay, request.POST)

        if form.is_valid():

            device_bay.installed_device = form.cleaned_data['installed_device']
            device_bay.save()
            messages.success(request, "Added {} to {}.".format(device_bay.installed_device, device_bay))

            return redirect('dcim:device', pk=device_bay.device.pk)

        return render(request, 'dcim/devicebay_populate.html', {
            'device_bay': device_bay,
            'form': form,
            'return_url': reverse('dcim:device', kwargs={'pk': device_bay.device.pk}),
        })


class DeviceBayDepopulateView(PermissionRequiredMixin, View):
    permission_required = 'dcim.change_devicebay'

    def get(self, request, pk):

        device_bay = get_object_or_404(DeviceBay, pk=pk)
        form = ConfirmationForm()

        return render(request, 'dcim/devicebay_depopulate.html', {
            'device_bay': device_bay,
            'form': form,
            'return_url': reverse('dcim:device', kwargs={'pk': device_bay.device.pk}),
        })

    def post(self, request, pk):

        device_bay = get_object_or_404(DeviceBay, pk=pk)
        form = ConfirmationForm(request.POST)

        if form.is_valid():

            removed_device = device_bay.installed_device
            device_bay.installed_device = None
            device_bay.save()
            messages.success(request, "{} has been removed from {}.".format(removed_device, device_bay))

            return redirect('dcim:device', pk=device_bay.device.pk)

        return render(request, 'dcim/devicebay_depopulate.html', {
            'device_bay': device_bay,
            'form': form,
            'return_url': reverse('dcim:device', kwargs={'pk': device_bay.device.pk}),
        })


class DeviceBayBulkRenameView(PermissionRequiredMixin, BulkRenameView):
    permission_required = 'dcim.change_devicebay'
    queryset = DeviceBay.objects.all()
    form = forms.DeviceBayBulkRenameForm


class DeviceBayBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_devicebay'
    queryset = DeviceBay.objects.all()
    parent_model = Device
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

class InterfaceConnectionAddView(PermissionRequiredMixin, GetReturnURLMixin, View):
    permission_required = 'dcim.add_interfaceconnection'
    default_return_url = 'dcim:device_list'

    def get(self, request, pk):

        device = get_object_or_404(Device, pk=pk)
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
            'return_url': device.get_absolute_url(),
        })

    def post(self, request, pk):

        device = get_object_or_404(Device, pk=pk)
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

        return render(request, 'dcim/interfaceconnection_edit.html', {
            'device': device,
            'form': form,
            'return_url': device.get_absolute_url(),
        })


class InterfaceConnectionDeleteView(PermissionRequiredMixin, GetReturnURLMixin, View):
    permission_required = 'dcim.delete_interfaceconnection'
    default_return_url = 'dcim:device_list'

    def get(self, request, pk):

        interfaceconnection = get_object_or_404(InterfaceConnection, pk=pk)
        form = forms.ConfirmationForm()

        return render(request, 'dcim/interfaceconnection_delete.html', {
            'interfaceconnection': interfaceconnection,
            'form': form,
            'return_url': self.get_return_url(request, interfaceconnection),
        })

    def post(self, request, pk):

        interfaceconnection = get_object_or_404(InterfaceConnection, pk=pk)
        form = forms.ConfirmationForm(request.POST)

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

            return redirect(self.get_return_url(request, interfaceconnection))

        return render(request, 'dcim/interfaceconnection_delete.html', {
            'interfaceconnection': interfaceconnection,
            'form': form,
            'return_url': self.get_return_url(request, interfaceconnection),
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
    queryset = ConsolePort.objects.select_related('device', 'cs_port__device').filter(cs_port__isnull=False) \
        .order_by('cs_port__device__name', 'cs_port__name')
    filter = filters.ConsoleConnectionFilter
    filter_form = forms.ConsoleConnectionFilterForm
    table = tables.ConsoleConnectionTable
    template_name = 'dcim/console_connections_list.html'


class PowerConnectionsListView(ObjectListView):
    queryset = PowerPort.objects.select_related('device', 'power_outlet__device').filter(power_outlet__isnull=False) \
        .order_by('power_outlet__device__name', 'power_outlet__name')
    filter = filters.PowerConnectionFilter
    filter_form = forms.PowerConnectionFilterForm
    table = tables.PowerConnectionTable
    template_name = 'dcim/power_connections_list.html'


class InterfaceConnectionsListView(ObjectListView):
    queryset = InterfaceConnection.objects.select_related(
        'interface_a__device', 'interface_b__device'
    ).order_by(
        'interface_a__device__name', 'interface_a__name'
    )
    filter = filters.InterfaceConnectionFilter
    filter_form = forms.InterfaceConnectionFilterForm
    table = tables.InterfaceConnectionTable
    template_name = 'dcim/interface_connections_list.html'


#
# Inventory items
#

class InventoryItemListView(ObjectListView):
    queryset = InventoryItem.objects.select_related('device', 'manufacturer')
    filter = filters.InventoryItemFilter
    filter_form = forms.InventoryItemFilterForm
    table = tables.InventoryItemTable
    template_name = 'dcim/inventoryitem_list.html'


class InventoryItemEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_inventoryitem'
    model = InventoryItem
    model_form = forms.InventoryItemForm

    def alter_obj(self, obj, request, url_args, url_kwargs):
        if 'device' in url_kwargs:
            obj.device = get_object_or_404(Device, pk=url_kwargs['device'])
        return obj

    def get_return_url(self, request, obj):
        return reverse('dcim:device_inventory', kwargs={'pk': obj.device.pk})


class InventoryItemDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_inventoryitem'
    model = InventoryItem


class InventoryItemBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_inventoryitem'
    model_form = forms.InventoryItemCSVForm
    table = tables.InventoryItemTable
    default_return_url = 'dcim:inventoryitem_list'


class InventoryItemBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_inventoryitem'
    queryset = InventoryItem.objects.select_related('device', 'manufacturer')
    filter = filters.InventoryItemFilter
    table = tables.InventoryItemTable
    form = forms.InventoryItemBulkEditForm
    default_return_url = 'dcim:inventoryitem_list'


class InventoryItemBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_inventoryitem'
    queryset = InventoryItem.objects.select_related('device', 'manufacturer')
    table = tables.InventoryItemTable
    template_name = 'dcim/inventoryitem_bulk_delete.html'
    default_return_url = 'dcim:inventoryitem_list'


#
# Virtual chassis
#

class VirtualChassisListView(ObjectListView):
    queryset = VirtualChassis.objects.select_related('master').annotate(member_count=Count('members'))
    table = tables.VirtualChassisTable
    filter = filters.VirtualChassisFilter
    filter_form = forms.VirtualChassisFilterForm
    template_name = 'dcim/virtualchassis_list.html'


class VirtualChassisCreateView(PermissionRequiredMixin, View):
    permission_required = 'dcim.add_virtualchassis'

    def post(self, request):

        # Get the list of devices being added to a VirtualChassis
        pk_form = forms.DeviceSelectionForm(request.POST)
        pk_form.full_clean()
        if not pk_form.cleaned_data.get('pk'):
            messages.warning(request, "No devices were selected.")
            return redirect('dcim:device_list')
        device_queryset = Device.objects.filter(
            pk__in=pk_form.cleaned_data.get('pk')
        ).select_related('rack').order_by('vc_position')

        VCMemberFormSet = modelformset_factory(
            model=Device,
            formset=forms.BaseVCMemberFormSet,
            form=forms.DeviceVCMembershipForm,
            extra=0
        )

        if '_create' in request.POST:

            vc_form = forms.VirtualChassisForm(request.POST)
            vc_form.fields['master'].queryset = device_queryset
            formset = VCMemberFormSet(request.POST, queryset=device_queryset)

            if vc_form.is_valid() and formset.is_valid():

                with transaction.atomic():

                    # Assign each device to the VirtualChassis before saving
                    virtual_chassis = vc_form.save()
                    devices = formset.save(commit=False)
                    for device in devices:
                        device.virtual_chassis = virtual_chassis
                        device.save()

                return redirect(vc_form.cleaned_data['master'].get_absolute_url())

        else:

            vc_form = forms.VirtualChassisForm()
            vc_form.fields['master'].queryset = device_queryset
            formset = VCMemberFormSet(queryset=device_queryset)

        return render(request, 'dcim/virtualchassis_edit.html', {
            'pk_form': pk_form,
            'vc_form': vc_form,
            'formset': formset,
            'return_url': reverse('dcim:device_list'),
        })


class VirtualChassisEditView(PermissionRequiredMixin, GetReturnURLMixin, View):
    permission_required = 'dcim.change_virtualchassis'

    def get(self, request, pk):

        virtual_chassis = get_object_or_404(VirtualChassis, pk=pk)
        VCMemberFormSet = modelformset_factory(
            model=Device,
            form=forms.DeviceVCMembershipForm,
            formset=forms.BaseVCMemberFormSet,
            extra=0
        )
        members_queryset = virtual_chassis.members.select_related('rack').order_by('vc_position')

        vc_form = forms.VirtualChassisForm(instance=virtual_chassis)
        vc_form.fields['master'].queryset = members_queryset
        formset = VCMemberFormSet(queryset=members_queryset)

        return render(request, 'dcim/virtualchassis_edit.html', {
            'vc_form': vc_form,
            'formset': formset,
            'return_url': self.get_return_url(request, virtual_chassis),
        })

    def post(self, request, pk):

        virtual_chassis = get_object_or_404(VirtualChassis, pk=pk)
        VCMemberFormSet = modelformset_factory(
            model=Device,
            form=forms.DeviceVCMembershipForm,
            formset=forms.BaseVCMemberFormSet,
            extra=0
        )
        members_queryset = virtual_chassis.members.select_related('rack').order_by('vc_position')

        vc_form = forms.VirtualChassisForm(request.POST, instance=virtual_chassis)
        vc_form.fields['master'].queryset = members_queryset
        formset = VCMemberFormSet(request.POST, queryset=members_queryset)

        if vc_form.is_valid() and formset.is_valid():

            with transaction.atomic():

                # Save the VirtualChassis
                vc_form.save()

                # Nullify the vc_position of each member first to allow reordering without raising an IntegrityError on
                # duplicate positions. Then save each member instance.
                members = formset.save(commit=False)
                Device.objects.filter(pk__in=[m.pk for m in members]).update(vc_position=None)
                for member in members:
                    member.save()

            return redirect(vc_form.cleaned_data['master'].get_absolute_url())

        return render(request, 'dcim/virtualchassis_edit.html', {
            'vc_form': vc_form,
            'formset': formset,
            'return_url': self.get_return_url(request, virtual_chassis),
        })


class VirtualChassisDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_virtualchassis'
    model = VirtualChassis
    default_return_url = 'dcim:device_list'


class VirtualChassisAddMemberView(PermissionRequiredMixin, GetReturnURLMixin, View):
    permission_required = 'dcim.change_virtualchassis'

    def get(self, request, pk):

        virtual_chassis = get_object_or_404(VirtualChassis, pk=pk)

        initial_data = {k: request.GET[k] for k in request.GET}
        member_select_form = forms.VCMemberSelectForm(initial=initial_data)
        membership_form = forms.DeviceVCMembershipForm(initial=initial_data)

        return render(request, 'dcim/virtualchassis_add_member.html', {
            'virtual_chassis': virtual_chassis,
            'member_select_form': member_select_form,
            'membership_form': membership_form,
            'return_url': self.get_return_url(request, virtual_chassis),
        })

    def post(self, request, pk):

        virtual_chassis = get_object_or_404(VirtualChassis, pk=pk)

        member_select_form = forms.VCMemberSelectForm(request.POST)

        if member_select_form.is_valid():

            device = member_select_form.cleaned_data['device']
            device.virtual_chassis = virtual_chassis
            data = {k: request.POST[k] for k in ['vc_position', 'vc_priority']}
            membership_form = forms.DeviceVCMembershipForm(data=data, validate_vc_position=True, instance=device)

            if membership_form.is_valid():

                membership_form.save()
                msg = 'Added member <a href="{}">{}</a>'.format(device.get_absolute_url(), escape(device))
                messages.success(request, mark_safe(msg))

                if '_addanother' in request.POST:
                    return redirect(request.get_full_path())

                return redirect(self.get_return_url(request, device))

        else:

            membership_form = forms.DeviceVCMembershipForm(data=request.POST)

        return render(request, 'dcim/virtualchassis_add_member.html', {
            'virtual_chassis': virtual_chassis,
            'member_select_form': member_select_form,
            'membership_form': membership_form,
            'return_url': self.get_return_url(request, virtual_chassis),
        })


class VirtualChassisRemoveMemberView(PermissionRequiredMixin, GetReturnURLMixin, View):
    permission_required = 'dcim.change_virtualchassis'

    def get(self, request, pk):

        device = get_object_or_404(Device, pk=pk, virtual_chassis__isnull=False)
        form = ConfirmationForm(initial=request.GET)

        return render(request, 'dcim/virtualchassis_remove_member.html', {
            'device': device,
            'form': form,
            'return_url': self.get_return_url(request, device),
        })

    def post(self, request, pk):

        device = get_object_or_404(Device, pk=pk, virtual_chassis__isnull=False)
        form = ConfirmationForm(request.POST)

        # Protect master device from being removed
        virtual_chassis = VirtualChassis.objects.filter(master=device).first()
        if virtual_chassis is not None:
            msg = 'Unable to remove master device {} from the virtual chassis.'.format(escape(device))
            messages.error(request, mark_safe(msg))
            return redirect(device.get_absolute_url())

        if form.is_valid():

            Device.objects.filter(pk=device.pk).update(
                virtual_chassis=None,
                vc_position=None,
                vc_priority=None
            )

            msg = 'Removed {} from virtual chassis {}'.format(device, device.virtual_chassis)
            messages.success(request, msg)

            return redirect(self.get_return_url(request, device))

        return render(request, 'dcim/virtualchassis_remove_member.html', {
            'device': device,
            'form': form,
            'return_url': self.get_return_url(request, device),
        })
