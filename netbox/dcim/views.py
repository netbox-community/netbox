from collections import OrderedDict
import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db.models import Count, F
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import escape
from django.utils.http import is_safe_url
from django.utils.safestring import mark_safe
from django.views.generic import View

from circuits.models import Circuit
from extras.models import Graph
from extras.views import ObjectConfigContextView
from ipam.models import Prefix, VLAN
from ipam.tables import InterfaceIPAddressTable, InterfaceVLANTable
from utilities.forms import ConfirmationForm
from utilities.paginator import EnhancedPaginator
from utilities.utils import csv_format
from utilities.views import (
    BulkComponentCreateView, BulkDeleteView, BulkEditView, BulkImportView, ComponentCreateView, GetReturnURLMixin,
    ObjectImportView, ObjectDeleteView, ObjectEditView, ObjectListView, ObjectPermissionRequiredMixin,
)
from virtualization.models import VirtualMachine
from . import filters, forms, tables
from .choices import DeviceFaceChoices
from .constants import NONCONNECTABLE_IFACE_TYPES
from .models import (
    Cable, ConsolePort, ConsolePortTemplate, ConsoleServerPort, ConsoleServerPortTemplate, Device, DeviceBay,
    DeviceBayTemplate, DeviceRole, DeviceType, FrontPort, FrontPortTemplate, Interface, InterfaceTemplate,
    InventoryItem, Manufacturer, Platform, PowerFeed, PowerOutlet, PowerOutletTemplate, PowerPanel, PowerPort,
    PowerPortTemplate, Rack, RackGroup, RackReservation, RackRole, RearPort, RearPortTemplate, Region, Site,
    VirtualChassis,
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
                    find = form.cleaned_data['find']
                    replace = form.cleaned_data['replace']
                    if form.cleaned_data['use_regex']:
                        try:
                            obj.new_name = re.sub(find, replace, obj.name)
                        # Catch regex group reference errors
                        except re.error:
                            obj.new_name = obj.name
                    else:
                        obj.new_name = obj.name.replace(find, replace)

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


class BulkDisconnectView(GetReturnURLMixin, View):
    """
    An extendable view for disconnection console/power/interface components in bulk.
    """
    model = None
    form = None
    template_name = 'dcim/bulk_disconnect.html'

    def post(self, request):

        selected_objects = []
        return_url = self.get_return_url(request)

        if '_confirm' in request.POST:
            form = self.form(request.POST)

            if form.is_valid():

                with transaction.atomic():

                    count = 0
                    for obj in self.model.objects.filter(pk__in=form.cleaned_data['pk']):
                        if obj.cable is None:
                            continue
                        obj.cable.delete()
                        count += 1

                messages.success(request, "Disconnected {} {}".format(
                    count, self.model._meta.verbose_name_plural
                ))

                return redirect(return_url)

        else:
            form = self.form(initial={'pk': request.POST.getlist('pk')})
            selected_objects = self.model.objects.filter(pk__in=form.initial['pk'])

        return render(request, self.template_name, {
            'form': form,
            'obj_type_plural': self.model._meta.verbose_name_plural,
            'selected_objects': selected_objects,
            'return_url': return_url,
        })


#
# Regions
#

class RegionListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_region'
    queryset = Region.objects.add_related_count(
        Region.objects.all(),
        Site,
        'region',
        'site_count',
        cumulative=True
    )
    filterset = filters.RegionFilterSet
    filterset_form = forms.RegionFilterForm
    table = tables.RegionTable


class RegionCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_region'
    queryset = Region.objects.all()
    model_form = forms.RegionForm
    default_return_url = 'dcim:region_list'


class RegionEditView(RegionCreateView):
    permission_required = 'dcim.change_region'


class RegionBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_region'
    queryset = Region.objects.all()
    model_form = forms.RegionCSVForm
    table = tables.RegionTable
    default_return_url = 'dcim:region_list'


class RegionBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_region'
    queryset = Region.objects.all()
    filterset = filters.RegionFilterSet
    table = tables.RegionTable
    default_return_url = 'dcim:region_list'


#
# Sites
#

class SiteListView(ObjectPermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_site'
    queryset = Site.objects.prefetch_related('region', 'tenant')
    filterset = filters.SiteFilterSet
    filterset_form = forms.SiteFilterForm
    table = tables.SiteTable


class SiteView(ObjectPermissionRequiredMixin, View):
    permission_required = 'dcim.view_site'
    queryset = Site.objects.prefetch_related('region', 'tenant__group')

    def get(self, request, slug):

        site = get_object_or_404(self.queryset, slug=slug)
        stats = {
            'rack_count': Rack.objects.filter(site=site).count(),
            'device_count': Device.objects.filter(site=site).count(),
            'prefix_count': Prefix.objects.filter(site=site).count(),
            'vlan_count': VLAN.objects.filter(site=site).count(),
            'circuit_count': Circuit.objects.filter(terminations__site=site).count(),
            'vm_count': VirtualMachine.objects.filter(cluster__site=site).count(),
        }
        rack_groups = RackGroup.objects.filter(site=site).annotate(rack_count=Count('racks'))
        show_graphs = Graph.objects.filter(type__model='site').exists()

        return render(request, 'dcim/site.html', {
            'site': site,
            'stats': stats,
            'rack_groups': rack_groups,
            'show_graphs': show_graphs,
        })


class SiteCreateView(ObjectPermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_site'
    queryset = Site.objects.all()
    model_form = forms.SiteForm
    template_name = 'dcim/site_edit.html'
    default_return_url = 'dcim:site_list'


class SiteEditView(SiteCreateView):
    permission_required = 'dcim.change_site'


class SiteDeleteView(ObjectPermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_site'
    queryset = Site.objects.all()
    default_return_url = 'dcim:site_list'


class SiteBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_site'
    queryset = Site.objects.all()
    model_form = forms.SiteCSVForm
    table = tables.SiteTable
    default_return_url = 'dcim:site_list'


class SiteBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_site'
    queryset = Site.objects.prefetch_related('region', 'tenant')
    filterset = filters.SiteFilterSet
    table = tables.SiteTable
    form = forms.SiteBulkEditForm
    default_return_url = 'dcim:site_list'


class SiteBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_site'
    queryset = Site.objects.prefetch_related('region', 'tenant')
    filterset = filters.SiteFilterSet
    table = tables.SiteTable
    default_return_url = 'dcim:site_list'


#
# Rack groups
#

class RackGroupListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_rackgroup'
    queryset = RackGroup.objects.add_related_count(
        RackGroup.objects.all(),
        Rack,
        'group',
        'rack_count',
        cumulative=True
    ).prefetch_related('site')
    filterset = filters.RackGroupFilterSet
    filterset_form = forms.RackGroupFilterForm
    table = tables.RackGroupTable


class RackGroupCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_rackgroup'
    queryset = RackGroup.objects.all()
    model_form = forms.RackGroupForm
    default_return_url = 'dcim:rackgroup_list'


class RackGroupEditView(RackGroupCreateView):
    permission_required = 'dcim.change_rackgroup'


class RackGroupBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_rackgroup'
    queryset = RackGroup.objects.all()
    model_form = forms.RackGroupCSVForm
    table = tables.RackGroupTable
    default_return_url = 'dcim:rackgroup_list'


class RackGroupBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_rackgroup'
    queryset = RackGroup.objects.prefetch_related('site').annotate(rack_count=Count('racks'))
    filterset = filters.RackGroupFilterSet
    table = tables.RackGroupTable
    default_return_url = 'dcim:rackgroup_list'


#
# Rack roles
#

class RackRoleListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_rackrole'
    queryset = RackRole.objects.annotate(rack_count=Count('racks'))
    table = tables.RackRoleTable


class RackRoleCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_rackrole'
    queryset = RackRole.objects.all()
    model_form = forms.RackRoleForm
    default_return_url = 'dcim:rackrole_list'


class RackRoleEditView(RackRoleCreateView):
    permission_required = 'dcim.change_rackrole'


class RackRoleBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_rackrole'
    queryset = RackRole.objects.all()
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

class RackListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_rack'
    queryset = Rack.objects.prefetch_related(
        'site', 'group', 'tenant', 'role', 'devices__device_type'
    ).annotate(
        device_count=Count('devices')
    )
    filterset = filters.RackFilterSet
    filterset_form = forms.RackFilterForm
    table = tables.RackDetailTable


class RackElevationListView(PermissionRequiredMixin, View):
    """
    Display a set of rack elevations side-by-side.
    """
    permission_required = 'dcim.view_rack'

    def get(self, request):

        racks = Rack.objects.prefetch_related('role')
        racks = filters.RackFilterSet(request.GET, racks).qs
        total_count = racks.count()

        # Pagination
        per_page = request.GET.get('per_page', settings.PAGINATE_COUNT)
        page_number = request.GET.get('page', 1)
        paginator = EnhancedPaginator(racks, per_page)
        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)

        # Determine rack face
        rack_face = request.GET.get('face', DeviceFaceChoices.FACE_FRONT)
        if rack_face not in DeviceFaceChoices.values():
            rack_face = DeviceFaceChoices.FACE_FRONT

        return render(request, 'dcim/rack_elevation_list.html', {
            'paginator': paginator,
            'page': page,
            'total_count': total_count,
            'rack_face': rack_face,
            'filter_form': forms.RackElevationFilterForm(request.GET),
        })


class RackView(PermissionRequiredMixin, View):
    permission_required = 'dcim.view_rack'

    def get(self, request, pk):

        rack = get_object_or_404(Rack.objects.prefetch_related('site__region', 'tenant__group', 'group', 'role'), pk=pk)

        nonracked_devices = Device.objects.filter(
            rack=rack,
            position__isnull=True,
            parent_bay__isnull=True
        ).prefetch_related('device_type__manufacturer')
        if rack.group:
            peer_racks = Rack.objects.filter(site=rack.site, group=rack.group)
        else:
            peer_racks = Rack.objects.filter(site=rack.site, group__isnull=True)
        next_rack = peer_racks.filter(name__gt=rack.name).order_by('name').first()
        prev_rack = peer_racks.filter(name__lt=rack.name).order_by('-name').first()

        reservations = RackReservation.objects.filter(rack=rack)
        power_feeds = PowerFeed.objects.filter(rack=rack).prefetch_related('power_panel')

        return render(request, 'dcim/rack.html', {
            'rack': rack,
            'reservations': reservations,
            'power_feeds': power_feeds,
            'nonracked_devices': nonracked_devices,
            'next_rack': next_rack,
            'prev_rack': prev_rack,
        })


class RackCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_rack'
    queryset = Rack.objects.all()
    model_form = forms.RackForm
    template_name = 'dcim/rack_edit.html'
    default_return_url = 'dcim:rack_list'


class RackEditView(RackCreateView):
    permission_required = 'dcim.change_rack'


class RackDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_rack'
    queryset = Rack.objects.all()
    default_return_url = 'dcim:rack_list'


class RackBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_rack'
    queryset = Rack.objects.all()
    model_form = forms.RackCSVForm
    table = tables.RackTable
    default_return_url = 'dcim:rack_list'


class RackBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_rack'
    queryset = Rack.objects.prefetch_related('site', 'group', 'tenant', 'role')
    filterset = filters.RackFilterSet
    table = tables.RackTable
    form = forms.RackBulkEditForm
    default_return_url = 'dcim:rack_list'


class RackBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_rack'
    queryset = Rack.objects.prefetch_related('site', 'group', 'tenant', 'role')
    filterset = filters.RackFilterSet
    table = tables.RackTable
    default_return_url = 'dcim:rack_list'


#
# Rack reservations
#

class RackReservationListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_rackreservation'
    queryset = RackReservation.objects.prefetch_related('rack__site')
    filterset = filters.RackReservationFilterSet
    filterset_form = forms.RackReservationFilterForm
    table = tables.RackReservationTable
    action_buttons = ('export',)


class RackReservationView(PermissionRequiredMixin, View):
    permission_required = 'dcim.view_rackreservation'

    def get(self, request, pk):

        rackreservation = get_object_or_404(RackReservation.objects.prefetch_related('rack'), pk=pk)

        return render(request, 'dcim/rackreservation.html', {
            'rackreservation': rackreservation,
        })


class RackReservationCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_rackreservation'
    queryset = RackReservation.objects.all()
    model_form = forms.RackReservationForm
    template_name = 'dcim/rackreservation_edit.html'
    default_return_url = 'dcim:rackreservation_list'

    def alter_obj(self, obj, request, args, kwargs):
        if not obj.pk:
            if 'rack' in request.GET:
                obj.rack = get_object_or_404(Rack, pk=request.GET.get('rack'))
            obj.user = request.user
        return obj


class RackReservationEditView(RackReservationCreateView):
    permission_required = 'dcim.change_rackreservation'


class RackReservationDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_rackreservation'
    queryset = RackReservation.objects.all()
    default_return_url = 'dcim:rackreservation_list'


class RackReservationImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_rackreservation'
    queryset = RackReservation.objects.all()
    model_form = forms.RackReservationCSVForm
    table = tables.RackReservationTable
    default_return_url = 'dcim:rackreservation_list'

    def _save_obj(self, obj_form, request):
        """
        Assign the currently authenticated user to the RackReservation.
        """
        instance = obj_form.save(commit=False)
        instance.user = request.user
        instance.save()

        return instance


class RackReservationBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_rackreservation'
    queryset = RackReservation.objects.prefetch_related('rack', 'user')
    filterset = filters.RackReservationFilterSet
    table = tables.RackReservationTable
    form = forms.RackReservationBulkEditForm
    default_return_url = 'dcim:rackreservation_list'


class RackReservationBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_rackreservation'
    queryset = RackReservation.objects.prefetch_related('rack', 'user')
    filterset = filters.RackReservationFilterSet
    table = tables.RackReservationTable
    default_return_url = 'dcim:rackreservation_list'


#
# Manufacturers
#

class ManufacturerListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_manufacturer'
    queryset = Manufacturer.objects.annotate(
        devicetype_count=Count('device_types', distinct=True),
        inventoryitem_count=Count('inventory_items', distinct=True),
        platform_count=Count('platforms', distinct=True),
    )
    table = tables.ManufacturerTable


class ManufacturerCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_manufacturer'
    queryset = Manufacturer.objects.all()
    model_form = forms.ManufacturerForm
    default_return_url = 'dcim:manufacturer_list'


class ManufacturerEditView(ManufacturerCreateView):
    permission_required = 'dcim.change_manufacturer'


class ManufacturerBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_manufacturer'
    queryset = Manufacturer.objects.all()
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

class DeviceTypeListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_devicetype'
    queryset = DeviceType.objects.prefetch_related('manufacturer').annotate(instance_count=Count('instances'))
    filterset = filters.DeviceTypeFilterSet
    filterset_form = forms.DeviceTypeFilterForm
    table = tables.DeviceTypeTable


class DeviceTypeView(PermissionRequiredMixin, View):
    permission_required = 'dcim.view_devicetype'

    def get(self, request, pk):

        devicetype = get_object_or_404(DeviceType, pk=pk)

        # Component tables
        consoleport_table = tables.ConsolePortTemplateTable(
            ConsolePortTemplate.objects.filter(device_type=devicetype),
            orderable=False
        )
        consoleserverport_table = tables.ConsoleServerPortTemplateTable(
            ConsoleServerPortTemplate.objects.filter(device_type=devicetype),
            orderable=False
        )
        powerport_table = tables.PowerPortTemplateTable(
            PowerPortTemplate.objects.filter(device_type=devicetype),
            orderable=False
        )
        poweroutlet_table = tables.PowerOutletTemplateTable(
            PowerOutletTemplate.objects.filter(device_type=devicetype),
            orderable=False
        )
        interface_table = tables.InterfaceTemplateTable(
            list(InterfaceTemplate.objects.filter(device_type=devicetype)),
            orderable=False
        )
        front_port_table = tables.FrontPortTemplateTable(
            FrontPortTemplate.objects.filter(device_type=devicetype),
            orderable=False
        )
        rear_port_table = tables.RearPortTemplateTable(
            RearPortTemplate.objects.filter(device_type=devicetype),
            orderable=False
        )
        devicebay_table = tables.DeviceBayTemplateTable(
            DeviceBayTemplate.objects.filter(device_type=devicetype),
            orderable=False
        )
        if request.user.has_perm('dcim.change_devicetype'):
            consoleport_table.columns.show('pk')
            consoleserverport_table.columns.show('pk')
            powerport_table.columns.show('pk')
            poweroutlet_table.columns.show('pk')
            interface_table.columns.show('pk')
            front_port_table.columns.show('pk')
            rear_port_table.columns.show('pk')
            devicebay_table.columns.show('pk')

        return render(request, 'dcim/devicetype.html', {
            'devicetype': devicetype,
            'consoleport_table': consoleport_table,
            'consoleserverport_table': consoleserverport_table,
            'powerport_table': powerport_table,
            'poweroutlet_table': poweroutlet_table,
            'interface_table': interface_table,
            'front_port_table': front_port_table,
            'rear_port_table': rear_port_table,
            'devicebay_table': devicebay_table,
        })


class DeviceTypeCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_devicetype'
    queryset = DeviceType.objects.all()
    model_form = forms.DeviceTypeForm
    template_name = 'dcim/devicetype_edit.html'
    default_return_url = 'dcim:devicetype_list'


class DeviceTypeEditView(DeviceTypeCreateView):
    permission_required = 'dcim.change_devicetype'


class DeviceTypeDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_devicetype'
    queryset = DeviceType.objects.all()
    default_return_url = 'dcim:devicetype_list'


class DeviceTypeImportView(PermissionRequiredMixin, ObjectImportView):
    permission_required = [
        'dcim.add_devicetype',
        'dcim.add_consoleporttemplate',
        'dcim.add_consoleserverporttemplate',
        'dcim.add_powerporttemplate',
        'dcim.add_poweroutlettemplate',
        'dcim.add_interfacetemplate',
        'dcim.add_frontporttemplate',
        'dcim.add_rearporttemplate',
        'dcim.add_devicebaytemplate',
    ]
    model = DeviceType
    model_form = forms.DeviceTypeImportForm
    related_object_forms = OrderedDict((
        ('console-ports', forms.ConsolePortTemplateImportForm),
        ('console-server-ports', forms.ConsoleServerPortTemplateImportForm),
        ('power-ports', forms.PowerPortTemplateImportForm),
        ('power-outlets', forms.PowerOutletTemplateImportForm),
        ('interfaces', forms.InterfaceTemplateImportForm),
        ('rear-ports', forms.RearPortTemplateImportForm),
        ('front-ports', forms.FrontPortTemplateImportForm),
        ('device-bays', forms.DeviceBayTemplateImportForm),
    ))
    default_return_url = 'dcim:devicetype_import'


class DeviceTypeBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_devicetype'
    queryset = DeviceType.objects.prefetch_related('manufacturer').annotate(instance_count=Count('instances'))
    filterset = filters.DeviceTypeFilterSet
    table = tables.DeviceTypeTable
    form = forms.DeviceTypeBulkEditForm
    default_return_url = 'dcim:devicetype_list'


class DeviceTypeBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_devicetype'
    queryset = DeviceType.objects.prefetch_related('manufacturer').annotate(instance_count=Count('instances'))
    filterset = filters.DeviceTypeFilterSet
    table = tables.DeviceTypeTable
    default_return_url = 'dcim:devicetype_list'


#
# Console port templates
#

class ConsolePortTemplateCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_consoleporttemplate'
    model = ConsolePortTemplate
    form = forms.ConsolePortTemplateCreateForm
    model_form = forms.ConsolePortTemplateForm
    template_name = 'dcim/device_component_add.html'


class ConsolePortTemplateEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_consoleporttemplate'
    queryset = ConsolePortTemplate.objects.all()
    model_form = forms.ConsolePortTemplateForm


class ConsolePortTemplateDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_consoleporttemplate'
    queryset = ConsolePortTemplate.objects.all()


class ConsolePortTemplateBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_consoleporttemplate'
    queryset = ConsolePortTemplate.objects.all()
    table = tables.ConsolePortTemplateTable
    form = forms.ConsolePortTemplateBulkEditForm


class ConsolePortTemplateBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_consoleporttemplate'
    queryset = ConsolePortTemplate.objects.all()
    table = tables.ConsolePortTemplateTable


#
# Console server port templates
#

class ConsoleServerPortTemplateCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_consoleserverporttemplate'
    model = ConsoleServerPortTemplate
    form = forms.ConsoleServerPortTemplateCreateForm
    model_form = forms.ConsoleServerPortTemplateForm
    template_name = 'dcim/device_component_add.html'


class ConsoleServerPortTemplateEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_consoleserverporttemplate'
    queryset = ConsoleServerPortTemplate.objects.all()
    model_form = forms.ConsoleServerPortTemplateForm


class ConsoleServerPortTemplateDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_consoleserverporttemplate'
    queryset = ConsoleServerPortTemplate.objects.all()


class ConsoleServerPortTemplateBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_consoleserverporttemplate'
    queryset = ConsoleServerPortTemplate.objects.all()
    table = tables.ConsoleServerPortTemplateTable
    form = forms.ConsoleServerPortTemplateBulkEditForm


class ConsoleServerPortTemplateBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_consoleserverporttemplate'
    queryset = ConsoleServerPortTemplate.objects.all()
    table = tables.ConsoleServerPortTemplateTable


#
# Power port templates
#

class PowerPortTemplateCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_powerporttemplate'
    model = PowerPortTemplate
    form = forms.PowerPortTemplateCreateForm
    model_form = forms.PowerPortTemplateForm
    template_name = 'dcim/device_component_add.html'


class PowerPortTemplateEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_powerporttemplate'
    queryset = PowerPortTemplate.objects.all()
    model_form = forms.PowerPortTemplateForm


class PowerPortTemplateDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_powerporttemplate'
    queryset = PowerPortTemplate.objects.all()


class PowerPortTemplateBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_powerporttemplate'
    queryset = PowerPortTemplate.objects.all()
    table = tables.PowerPortTemplateTable
    form = forms.PowerPortTemplateBulkEditForm


class PowerPortTemplateBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_powerporttemplate'
    queryset = PowerPortTemplate.objects.all()
    table = tables.PowerPortTemplateTable


#
# Power outlet templates
#

class PowerOutletTemplateCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_poweroutlettemplate'
    model = PowerOutletTemplate
    form = forms.PowerOutletTemplateCreateForm
    model_form = forms.PowerOutletTemplateForm
    template_name = 'dcim/device_component_add.html'


class PowerOutletTemplateEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_poweroutlettemplate'
    queryset = PowerOutletTemplate.objects.all()
    model_form = forms.PowerOutletTemplateForm


class PowerOutletTemplateDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_poweroutlettemplate'
    queryset = PowerOutletTemplate.objects.all()


class PowerOutletTemplateBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_poweroutlettemplate'
    queryset = PowerOutletTemplate.objects.all()
    table = tables.PowerOutletTemplateTable
    form = forms.PowerOutletTemplateBulkEditForm


class PowerOutletTemplateBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_poweroutlettemplate'
    queryset = PowerOutletTemplate.objects.all()
    table = tables.PowerOutletTemplateTable


#
# Interface templates
#

class InterfaceTemplateCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_interfacetemplate'
    model = InterfaceTemplate
    form = forms.InterfaceTemplateCreateForm
    model_form = forms.InterfaceTemplateForm
    template_name = 'dcim/device_component_add.html'


class InterfaceTemplateEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_interfacetemplate'
    queryset = InterfaceTemplate.objects.all()
    model_form = forms.InterfaceTemplateForm


class InterfaceTemplateDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_interfacetemplate'
    queryset = InterfaceTemplate.objects.all()


class InterfaceTemplateBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_interfacetemplate'
    queryset = InterfaceTemplate.objects.all()
    table = tables.InterfaceTemplateTable
    form = forms.InterfaceTemplateBulkEditForm


class InterfaceTemplateBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_interfacetemplate'
    queryset = InterfaceTemplate.objects.all()
    table = tables.InterfaceTemplateTable


#
# Front port templates
#

class FrontPortTemplateCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_frontporttemplate'
    model = FrontPortTemplate
    form = forms.FrontPortTemplateCreateForm
    model_form = forms.FrontPortTemplateForm
    template_name = 'dcim/device_component_add.html'


class FrontPortTemplateEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_frontporttemplate'
    queryset = FrontPortTemplate.objects.all()
    model_form = forms.FrontPortTemplateForm


class FrontPortTemplateDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_frontporttemplate'
    queryset = FrontPortTemplate.objects.all()


class FrontPortTemplateBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_frontporttemplate'
    queryset = FrontPortTemplate.objects.all()
    table = tables.FrontPortTemplateTable
    form = forms.FrontPortTemplateBulkEditForm


class FrontPortTemplateBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_frontporttemplate'
    queryset = FrontPortTemplate.objects.all()
    table = tables.FrontPortTemplateTable


#
# Rear port templates
#

class RearPortTemplateCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_rearporttemplate'
    model = RearPortTemplate
    form = forms.RearPortTemplateCreateForm
    model_form = forms.RearPortTemplateForm
    template_name = 'dcim/device_component_add.html'


class RearPortTemplateEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_rearporttemplate'
    queryset = RearPortTemplate.objects.all()
    model_form = forms.RearPortTemplateForm


class RearPortTemplateDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_rearporttemplate'
    queryset = RearPortTemplate.objects.all()


class RearPortTemplateBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_rearporttemplate'
    queryset = RearPortTemplate.objects.all()
    table = tables.RearPortTemplateTable
    form = forms.RearPortTemplateBulkEditForm


class RearPortTemplateBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_rearporttemplate'
    queryset = RearPortTemplate.objects.all()
    table = tables.RearPortTemplateTable


#
# Device bay templates
#

class DeviceBayTemplateCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_devicebaytemplate'
    model = DeviceBayTemplate
    form = forms.DeviceBayTemplateCreateForm
    model_form = forms.DeviceBayTemplateForm
    template_name = 'dcim/device_component_add.html'


class DeviceBayTemplateEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_devicebaytemplate'
    queryset = DeviceBayTemplate.objects.all()
    model_form = forms.DeviceBayTemplateForm


class DeviceBayTemplateDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_devicebaytemplate'
    queryset = DeviceBayTemplate.objects.all()


# class DeviceBayTemplateBulkEditView(PermissionRequiredMixin, BulkEditView):
#     permission_required = 'dcim.change_devicebaytemplate'
#     queryset = DeviceBayTemplate.objects.all()
#     table = tables.DeviceBayTemplateTable
#     form = forms.DeviceBayTemplateBulkEditForm


class DeviceBayTemplateBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_devicebaytemplate'
    queryset = DeviceBayTemplate.objects.all()
    table = tables.DeviceBayTemplateTable


#
# Device roles
#

class DeviceRoleListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_devicerole'
    queryset = DeviceRole.objects.all()
    table = tables.DeviceRoleTable


class DeviceRoleCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_devicerole'
    queryset = DeviceRole.objects.all()
    model_form = forms.DeviceRoleForm
    default_return_url = 'dcim:devicerole_list'


class DeviceRoleEditView(DeviceRoleCreateView):
    permission_required = 'dcim.change_devicerole'


class DeviceRoleBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_devicerole'
    queryset = DeviceRole.objects.all()
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

class PlatformListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_platform'
    queryset = Platform.objects.all()
    table = tables.PlatformTable


class PlatformCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_platform'
    queryset = Platform.objects.all()
    model_form = forms.PlatformForm
    default_return_url = 'dcim:platform_list'


class PlatformEditView(PlatformCreateView):
    permission_required = 'dcim.change_platform'


class PlatformBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_platform'
    queryset = Platform.objects.all()
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

class DeviceListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_device'
    queryset = Device.objects.prefetch_related(
        'device_type__manufacturer', 'device_role', 'tenant', 'site', 'rack', 'primary_ip4', 'primary_ip6'
    )
    filterset = filters.DeviceFilterSet
    filterset_form = forms.DeviceFilterForm
    table = tables.DeviceTable
    template_name = 'dcim/device_list.html'


class DeviceView(PermissionRequiredMixin, View):
    permission_required = 'dcim.view_device'

    def get(self, request, pk):

        device = get_object_or_404(Device.objects.prefetch_related(
            'site__region', 'rack__group', 'tenant__group', 'device_role', 'platform'
        ), pk=pk)

        # VirtualChassis members
        if device.virtual_chassis is not None:
            vc_members = Device.objects.filter(
                virtual_chassis=device.virtual_chassis
            ).order_by('vc_position')
        else:
            vc_members = []

        # Console ports
        console_ports = device.consoleports.prefetch_related('connected_endpoint__device', 'cable')

        # Console server ports
        consoleserverports = device.consoleserverports.prefetch_related('connected_endpoint__device', 'cable')

        # Power ports
        power_ports = device.powerports.prefetch_related('_connected_poweroutlet__device', 'cable')

        # Power outlets
        poweroutlets = device.poweroutlets.prefetch_related('connected_endpoint__device', 'cable', 'power_port')

        # Interfaces
        interfaces = device.vc_interfaces.prefetch_related(
            'lag', '_connected_interface__device', '_connected_circuittermination__circuit', 'cable',
            'cable__termination_a', 'cable__termination_b', 'ip_addresses', 'tags'
        )

        # Front ports
        front_ports = device.frontports.prefetch_related('rear_port', 'cable')

        # Rear ports
        rear_ports = device.rearports.prefetch_related('cable')

        # Device bays
        device_bays = device.device_bays.prefetch_related('installed_device__device_type__manufacturer')

        # Services
        services = device.services.all()

        # Secrets
        secrets = device.secrets.all()

        # Find up to ten devices in the same site with the same functional role for quick reference.
        related_devices = Device.objects.filter(
            site=device.site, device_role=device.device_role
        ).exclude(
            pk=device.pk
        ).prefetch_related(
            'rack', 'device_type__manufacturer'
        )[:10]

        return render(request, 'dcim/device.html', {
            'device': device,
            'console_ports': console_ports,
            'consoleserverports': consoleserverports,
            'power_ports': power_ports,
            'poweroutlets': poweroutlets,
            'interfaces': interfaces,
            'device_bays': device_bays,
            'front_ports': front_ports,
            'rear_ports': rear_ports,
            'services': services,
            'secrets': secrets,
            'vc_members': vc_members,
            'related_devices': related_devices,
            'show_graphs': Graph.objects.filter(type__model='device').exists(),
            'show_interface_graphs': Graph.objects.filter(type__model='interface').exists(),
        })


class DeviceInventoryView(PermissionRequiredMixin, View):
    permission_required = 'dcim.view_device'

    def get(self, request, pk):

        device = get_object_or_404(Device, pk=pk)
        inventory_items = InventoryItem.objects.filter(
            device=device, parent=None
        ).prefetch_related(
            'manufacturer', 'child_items'
        )

        return render(request, 'dcim/device_inventory.html', {
            'device': device,
            'inventory_items': inventory_items,
            'active_tab': 'inventory',
        })


class DeviceStatusView(PermissionRequiredMixin, View):
    permission_required = ('dcim.view_device', 'dcim.napalm_read')

    def get(self, request, pk):

        device = get_object_or_404(Device, pk=pk)

        return render(request, 'dcim/device_status.html', {
            'device': device,
            'active_tab': 'status',
        })


class DeviceLLDPNeighborsView(PermissionRequiredMixin, View):
    permission_required = ('dcim.view_device', 'dcim.napalm_read')

    def get(self, request, pk):

        device = get_object_or_404(Device, pk=pk)
        interfaces = device.vc_interfaces.exclude(type__in=NONCONNECTABLE_IFACE_TYPES).prefetch_related(
            '_connected_interface__device'
        )

        return render(request, 'dcim/device_lldp_neighbors.html', {
            'device': device,
            'interfaces': interfaces,
            'active_tab': 'lldp-neighbors',
        })


class DeviceConfigView(PermissionRequiredMixin, View):
    permission_required = ('dcim.view_device', 'dcim.napalm_read')

    def get(self, request, pk):

        device = get_object_or_404(Device, pk=pk)

        return render(request, 'dcim/device_config.html', {
            'device': device,
            'active_tab': 'config',
        })


class DeviceConfigContextView(PermissionRequiredMixin, ObjectConfigContextView):
    permission_required = 'dcim.view_device'
    object_class = Device
    base_template = 'dcim/device.html'


class DeviceCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_device'
    queryset = Device.objects.all()
    model_form = forms.DeviceForm
    template_name = 'dcim/device_edit.html'
    default_return_url = 'dcim:device_list'


class DeviceEditView(DeviceCreateView):
    permission_required = 'dcim.change_device'


class DeviceDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_device'
    queryset = Device.objects.all()
    default_return_url = 'dcim:device_list'


class DeviceBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_device'
    queryset = Device.objects.all()
    model_form = forms.DeviceCSVForm
    table = tables.DeviceImportTable
    template_name = 'dcim/device_import.html'
    default_return_url = 'dcim:device_list'


class ChildDeviceBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_device'
    queryset = Device.objects.all()
    model_form = forms.ChildDeviceCSVForm
    table = tables.DeviceImportTable
    template_name = 'dcim/device_import_child.html'
    default_return_url = 'dcim:device_list'

    def _save_obj(self, obj_form, request):

        obj = obj_form.save()

        # Save the reverse relation to the parent device bay
        device_bay = obj.parent_bay
        device_bay.installed_device = obj
        device_bay.save()

        return obj


class DeviceBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_device'
    queryset = Device.objects.prefetch_related('tenant', 'site', 'rack', 'device_role', 'device_type__manufacturer')
    filterset = filters.DeviceFilterSet
    table = tables.DeviceTable
    form = forms.DeviceBulkEditForm
    default_return_url = 'dcim:device_list'


class DeviceBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_device'
    queryset = Device.objects.prefetch_related('tenant', 'site', 'rack', 'device_role', 'device_type__manufacturer')
    filterset = filters.DeviceFilterSet
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


#
# Console ports
#

class ConsolePortListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_consoleport'
    queryset = ConsolePort.objects.prefetch_related('device', 'device__tenant', 'device__site', 'cable')
    filterset = filters.ConsolePortFilterSet
    filterset_form = forms.ConsolePortFilterForm
    table = tables.ConsolePortDetailTable
    action_buttons = ('import', 'export')


class ConsolePortCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_consoleport'
    model = ConsolePort
    form = forms.ConsolePortCreateForm
    model_form = forms.ConsolePortForm
    template_name = 'dcim/device_component_add.html'


class ConsolePortEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_consoleport'
    queryset = ConsolePort.objects.all()
    model_form = forms.ConsolePortForm


class ConsolePortDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_consoleport'
    queryset = ConsolePort.objects.all()


class ConsolePortBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_consoleport'
    queryset = ConsolePort.objects.all()
    model_form = forms.ConsolePortCSVForm
    table = tables.ConsolePortImportTable
    default_return_url = 'dcim:consoleport_list'


class ConsolePortBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_consoleport'
    queryset = ConsolePort.objects.all()
    filterset = filters.ConsolePortFilterSet
    table = tables.ConsolePortTable
    form = forms.ConsolePortBulkEditForm


class ConsolePortBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_consoleport'
    queryset = ConsolePort.objects.all()
    filterset = filters.ConsolePortFilterSet
    table = tables.ConsolePortTable
    default_return_url = 'dcim:consoleport_list'


#
# Console server ports
#

class ConsoleServerPortListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_consoleserverport'
    queryset = ConsoleServerPort.objects.prefetch_related('device', 'device__tenant', 'device__site', 'cable')
    filterset = filters.ConsoleServerPortFilterSet
    filterset_form = forms.ConsoleServerPortFilterForm
    table = tables.ConsoleServerPortDetailTable
    action_buttons = ('import', 'export')


class ConsoleServerPortCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_consoleserverport'
    model = ConsoleServerPort
    form = forms.ConsoleServerPortCreateForm
    model_form = forms.ConsoleServerPortForm
    template_name = 'dcim/device_component_add.html'


class ConsoleServerPortEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_consoleserverport'
    queryset = ConsoleServerPort.objects.all()
    model_form = forms.ConsoleServerPortForm


class ConsoleServerPortDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_consoleserverport'
    queryset = ConsoleServerPort.objects.all()


class ConsoleServerPortBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_consoleserverport'
    queryset = ConsoleServerPort.objects.all()
    model_form = forms.ConsoleServerPortCSVForm
    table = tables.ConsoleServerPortImportTable
    default_return_url = 'dcim:consoleserverport_list'


class ConsoleServerPortBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_consoleserverport'
    queryset = ConsoleServerPort.objects.all()
    filterset = filters.ConsoleServerPortFilterSet
    table = tables.ConsoleServerPortTable
    form = forms.ConsoleServerPortBulkEditForm


class ConsoleServerPortBulkRenameView(PermissionRequiredMixin, BulkRenameView):
    permission_required = 'dcim.change_consoleserverport'
    queryset = ConsoleServerPort.objects.all()
    form = forms.ConsoleServerPortBulkRenameForm


class ConsoleServerPortBulkDisconnectView(PermissionRequiredMixin, BulkDisconnectView):
    permission_required = 'dcim.change_consoleserverport'
    model = ConsoleServerPort
    form = forms.ConsoleServerPortBulkDisconnectForm


class ConsoleServerPortBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_consoleserverport'
    queryset = ConsoleServerPort.objects.all()
    filterset = filters.ConsoleServerPortFilterSet
    table = tables.ConsoleServerPortTable
    default_return_url = 'dcim:consoleserverport_list'


#
# Power ports
#

class PowerPortListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_powerport'
    queryset = PowerPort.objects.prefetch_related('device', 'device__tenant', 'device__site', 'cable')
    filterset = filters.PowerPortFilterSet
    filterset_form = forms.PowerPortFilterForm
    table = tables.PowerPortDetailTable
    action_buttons = ('import', 'export')


class PowerPortCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_powerport'
    model = PowerPort
    form = forms.PowerPortCreateForm
    model_form = forms.PowerPortForm
    template_name = 'dcim/device_component_add.html'


class PowerPortEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_powerport'
    queryset = PowerPort.objects.all()
    model_form = forms.PowerPortForm


class PowerPortDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_powerport'
    queryset = PowerPort.objects.all()


class PowerPortBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_powerport'
    queryset = PowerPort.objects.all()
    model_form = forms.PowerPortCSVForm
    table = tables.PowerPortImportTable
    default_return_url = 'dcim:powerport_list'


class PowerPortBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_powerport'
    queryset = PowerPort.objects.all()
    filterset = filters.PowerPortFilterSet
    table = tables.PowerPortTable
    form = forms.PowerPortBulkEditForm


class PowerPortBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_powerport'
    queryset = PowerPort.objects.all()
    filterset = filters.PowerPortFilterSet
    table = tables.PowerPortTable
    default_return_url = 'dcim:powerport_list'


#
# Power outlets
#

class PowerOutletListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_poweroutlet'
    queryset = PowerOutlet.objects.prefetch_related('device', 'device__tenant', 'device__site', 'cable')
    filterset = filters.PowerOutletFilterSet
    filterset_form = forms.PowerOutletFilterForm
    table = tables.PowerOutletDetailTable
    action_buttons = ('import', 'export')


class PowerOutletCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_poweroutlet'
    model = PowerOutlet
    form = forms.PowerOutletCreateForm
    model_form = forms.PowerOutletForm
    template_name = 'dcim/device_component_add.html'


class PowerOutletEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_poweroutlet'
    queryset = PowerOutlet.objects.all()
    model_form = forms.PowerOutletForm


class PowerOutletDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_poweroutlet'
    queryset = PowerOutlet.objects.all()


class PowerOutletBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_poweroutlet'
    queryset = PowerOutlet.objects.all()
    model_form = forms.PowerOutletCSVForm
    table = tables.PowerOutletImportTable
    default_return_url = 'dcim:poweroutlet_list'


class PowerOutletBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_poweroutlet'
    queryset = PowerOutlet.objects.all()
    filterset = filters.PowerOutletFilterSet
    table = tables.PowerOutletTable
    form = forms.PowerOutletBulkEditForm


class PowerOutletBulkRenameView(PermissionRequiredMixin, BulkRenameView):
    permission_required = 'dcim.change_poweroutlet'
    queryset = PowerOutlet.objects.all()
    form = forms.PowerOutletBulkRenameForm


class PowerOutletBulkDisconnectView(PermissionRequiredMixin, BulkDisconnectView):
    permission_required = 'dcim.change_poweroutlet'
    model = PowerOutlet
    form = forms.PowerOutletBulkDisconnectForm


class PowerOutletBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_poweroutlet'
    queryset = PowerOutlet.objects.all()
    filterset = filters.PowerOutletFilterSet
    table = tables.PowerOutletTable
    default_return_url = 'dcim:poweroutlet_list'


#
# Interfaces
#

class InterfaceListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_interface'
    queryset = Interface.objects.prefetch_related('device', 'device__tenant', 'device__site', 'cable')
    filterset = filters.InterfaceFilterSet
    filterset_form = forms.InterfaceFilterForm
    table = tables.InterfaceDetailTable
    action_buttons = ('import', 'export')


class InterfaceView(PermissionRequiredMixin, View):
    permission_required = 'dcim.view_interface'

    def get(self, request, pk):

        interface = get_object_or_404(Interface, pk=pk)

        # Get assigned IP addresses
        ipaddress_table = InterfaceIPAddressTable(
            data=interface.ip_addresses.prefetch_related('vrf', 'tenant'),
            orderable=False
        )

        # Get assigned VLANs and annotate whether each is tagged or untagged
        vlans = []
        if interface.untagged_vlan is not None:
            vlans.append(interface.untagged_vlan)
            vlans[0].tagged = False
        for vlan in interface.tagged_vlans.prefetch_related('site', 'group', 'tenant', 'role'):
            vlan.tagged = True
            vlans.append(vlan)
        vlan_table = InterfaceVLANTable(
            interface=interface,
            data=vlans,
            orderable=False
        )

        return render(request, 'dcim/interface.html', {
            'interface': interface,
            'connected_interface': interface._connected_interface,
            'connected_circuittermination': interface._connected_circuittermination,
            'ipaddress_table': ipaddress_table,
            'vlan_table': vlan_table,
        })


class InterfaceCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_interface'
    model = Interface
    form = forms.InterfaceCreateForm
    model_form = forms.InterfaceForm
    template_name = 'dcim/device_component_add.html'


class InterfaceEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_interface'
    queryset = Interface.objects.all()
    model_form = forms.InterfaceForm
    template_name = 'dcim/interface_edit.html'


class InterfaceDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_interface'
    queryset = Interface.objects.all()


class InterfaceBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_interface'
    queryset = Interface.objects.all()
    model_form = forms.InterfaceCSVForm
    table = tables.InterfaceImportTable
    default_return_url = 'dcim:interface_list'


class InterfaceBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_interface'
    queryset = Interface.objects.all()
    filterset = filters.InterfaceFilterSet
    table = tables.InterfaceTable
    form = forms.InterfaceBulkEditForm


class InterfaceBulkRenameView(PermissionRequiredMixin, BulkRenameView):
    permission_required = 'dcim.change_interface'
    queryset = Interface.objects.all()
    form = forms.InterfaceBulkRenameForm


class InterfaceBulkDisconnectView(PermissionRequiredMixin, BulkDisconnectView):
    permission_required = 'dcim.change_interface'
    model = Interface
    form = forms.InterfaceBulkDisconnectForm


class InterfaceBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_interface'
    queryset = Interface.objects.all()
    filterset = filters.InterfaceFilterSet
    table = tables.InterfaceTable
    default_return_url = 'dcim:interface_list'


#
# Front ports
#

class FrontPortListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_frontport'
    queryset = FrontPort.objects.prefetch_related('device', 'device__tenant', 'device__site', 'cable')
    filterset = filters.FrontPortFilterSet
    filterset_form = forms.FrontPortFilterForm
    table = tables.FrontPortDetailTable
    action_buttons = ('import', 'export')


class FrontPortCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_frontport'
    model = FrontPort
    form = forms.FrontPortCreateForm
    model_form = forms.FrontPortForm
    template_name = 'dcim/device_component_add.html'


class FrontPortEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_frontport'
    queryset = FrontPort.objects.all()
    model_form = forms.FrontPortForm


class FrontPortDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_frontport'
    queryset = FrontPort.objects.all()


class FrontPortBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_frontport'
    queryset = FrontPort.objects.all()
    model_form = forms.FrontPortCSVForm
    table = tables.FrontPortImportTable
    default_return_url = 'dcim:frontport_list'


class FrontPortBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_frontport'
    queryset = FrontPort.objects.all()
    filterset = filters.FrontPortFilterSet
    table = tables.FrontPortTable
    form = forms.FrontPortBulkEditForm


class FrontPortBulkRenameView(PermissionRequiredMixin, BulkRenameView):
    permission_required = 'dcim.change_frontport'
    queryset = FrontPort.objects.all()
    form = forms.FrontPortBulkRenameForm


class FrontPortBulkDisconnectView(PermissionRequiredMixin, BulkDisconnectView):
    permission_required = 'dcim.change_frontport'
    model = FrontPort
    form = forms.FrontPortBulkDisconnectForm


class FrontPortBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_frontport'
    queryset = FrontPort.objects.all()
    filterset = filters.FrontPortFilterSet
    table = tables.FrontPortTable
    default_return_url = 'dcim:frontport_list'


#
# Rear ports
#

class RearPortListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_rearport'
    queryset = RearPort.objects.prefetch_related('device', 'device__tenant', 'device__site', 'cable')
    filterset = filters.RearPortFilterSet
    filterset_form = forms.RearPortFilterForm
    table = tables.RearPortDetailTable
    action_buttons = ('import', 'export')


class RearPortCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_rearport'
    model = RearPort
    form = forms.RearPortCreateForm
    model_form = forms.RearPortForm
    template_name = 'dcim/device_component_add.html'


class RearPortEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_rearport'
    queryset = RearPort.objects.all()
    model_form = forms.RearPortForm


class RearPortDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_rearport'
    queryset = RearPort.objects.all()


class RearPortBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_rearport'
    queryset = RearPort.objects.all()
    model_form = forms.RearPortCSVForm
    table = tables.RearPortImportTable
    default_return_url = 'dcim:rearport_list'


class RearPortBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_rearport'
    queryset = RearPort.objects.all()
    filterset = filters.RearPortFilterSet
    table = tables.RearPortTable
    form = forms.RearPortBulkEditForm


class RearPortBulkRenameView(PermissionRequiredMixin, BulkRenameView):
    permission_required = 'dcim.change_rearport'
    queryset = RearPort.objects.all()
    form = forms.RearPortBulkRenameForm


class RearPortBulkDisconnectView(PermissionRequiredMixin, BulkDisconnectView):
    permission_required = 'dcim.change_rearport'
    model = RearPort
    form = forms.RearPortBulkDisconnectForm


class RearPortBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_rearport'
    queryset = RearPort.objects.all()
    filterset = filters.RearPortFilterSet
    table = tables.RearPortTable
    default_return_url = 'dcim:rearport_list'


#
# Device bays
#

class DeviceBayListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_devicebay'
    queryset = DeviceBay.objects.prefetch_related(
        'device', 'device__site', 'installed_device', 'installed_device__site'
    )
    filterset = filters.DeviceBayFilterSet
    filterset_form = forms.DeviceBayFilterForm
    table = tables.DeviceBayDetailTable
    action_buttons = ('import', 'export')


class DeviceBayCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_devicebay'
    model = DeviceBay
    form = forms.DeviceBayCreateForm
    model_form = forms.DeviceBayForm
    template_name = 'dcim/device_component_add.html'


class DeviceBayEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_devicebay'
    queryset = DeviceBay.objects.all()
    model_form = forms.DeviceBayForm


class DeviceBayDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_devicebay'
    queryset = DeviceBay.objects.all()


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


class DeviceBayBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_devicebay'
    queryset = DeviceBay.objects.all()
    model_form = forms.DeviceBayCSVForm
    table = tables.DeviceBayImportTable
    default_return_url = 'dcim:devicebay_list'


class DeviceBayBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_devicebay'
    queryset = DeviceBay.objects.all()
    filterset = filters.DeviceBayFilterSet
    table = tables.DeviceBayTable
    form = forms.DeviceBayBulkEditForm


class DeviceBayBulkRenameView(PermissionRequiredMixin, BulkRenameView):
    permission_required = 'dcim.change_devicebay'
    queryset = DeviceBay.objects.all()
    form = forms.DeviceBayBulkRenameForm


class DeviceBayBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_devicebay'
    queryset = DeviceBay.objects.all()
    filterset = filters.DeviceBayFilterSet
    table = tables.DeviceBayTable
    default_return_url = 'dcim:devicebay_list'


#
# Bulk Device component creation
#

class DeviceBulkAddConsolePortView(PermissionRequiredMixin, BulkComponentCreateView):
    permission_required = 'dcim.add_consoleport'
    parent_model = Device
    parent_field = 'device'
    form = forms.ConsolePortBulkCreateForm
    model = ConsolePort
    model_form = forms.ConsolePortForm
    filterset = filters.DeviceFilterSet
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


class DeviceBulkAddConsoleServerPortView(PermissionRequiredMixin, BulkComponentCreateView):
    permission_required = 'dcim.add_consoleserverport'
    parent_model = Device
    parent_field = 'device'
    form = forms.ConsoleServerPortBulkCreateForm
    model = ConsoleServerPort
    model_form = forms.ConsoleServerPortForm
    filterset = filters.DeviceFilterSet
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


class DeviceBulkAddPowerPortView(PermissionRequiredMixin, BulkComponentCreateView):
    permission_required = 'dcim.add_powerport'
    parent_model = Device
    parent_field = 'device'
    form = forms.PowerPortBulkCreateForm
    model = PowerPort
    model_form = forms.PowerPortForm
    filterset = filters.DeviceFilterSet
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


class DeviceBulkAddPowerOutletView(PermissionRequiredMixin, BulkComponentCreateView):
    permission_required = 'dcim.add_poweroutlet'
    parent_model = Device
    parent_field = 'device'
    form = forms.PowerOutletBulkCreateForm
    model = PowerOutlet
    model_form = forms.PowerOutletForm
    filterset = filters.DeviceFilterSet
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


class DeviceBulkAddInterfaceView(PermissionRequiredMixin, BulkComponentCreateView):
    permission_required = 'dcim.add_interface'
    parent_model = Device
    parent_field = 'device'
    form = forms.InterfaceBulkCreateForm
    model = Interface
    model_form = forms.InterfaceForm
    filterset = filters.DeviceFilterSet
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


# class DeviceBulkAddFrontPortView(PermissionRequiredMixin, BulkComponentCreateView):
#     permission_required = 'dcim.add_frontport'
#     parent_model = Device
#     parent_field = 'device'
#     form = forms.FrontPortBulkCreateForm
#     model = FrontPort
#     model_form = forms.FrontPortForm
#     filterset = filters.DeviceFilterSet
#     table = tables.DeviceTable
#     default_return_url = 'dcim:device_list'


class DeviceBulkAddRearPortView(PermissionRequiredMixin, BulkComponentCreateView):
    permission_required = 'dcim.add_rearport'
    parent_model = Device
    parent_field = 'device'
    form = forms.RearPortBulkCreateForm
    model = RearPort
    model_form = forms.RearPortForm
    filterset = filters.DeviceFilterSet
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


class DeviceBulkAddDeviceBayView(PermissionRequiredMixin, BulkComponentCreateView):
    permission_required = 'dcim.add_devicebay'
    parent_model = Device
    parent_field = 'device'
    form = forms.DeviceBayBulkCreateForm
    model = DeviceBay
    model_form = forms.DeviceBayForm
    filterset = filters.DeviceFilterSet
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


#
# Cables
#

class CableListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_cable'
    queryset = Cable.objects.prefetch_related(
        'termination_a', 'termination_b'
    )
    filterset = filters.CableFilterSet
    filterset_form = forms.CableFilterForm
    table = tables.CableTable
    action_buttons = ('import', 'export')


class CableView(PermissionRequiredMixin, View):
    permission_required = 'dcim.view_cable'

    def get(self, request, pk):

        cable = get_object_or_404(Cable, pk=pk)

        return render(request, 'dcim/cable.html', {
            'cable': cable,
        })


class CableTraceView(PermissionRequiredMixin, View):
    """
    Trace a cable path beginning from the given termination.
    """
    permission_required = 'dcim.view_cable'

    def get(self, request, model, pk):

        obj = get_object_or_404(model, pk=pk)
        path, split_ends = obj.trace()
        total_length = sum(
            [entry[1]._abs_length for entry in path if entry[1] and entry[1]._abs_length]
        )

        return render(request, 'dcim/cable_trace.html', {
            'obj': obj,
            'trace': path,
            'split_ends': split_ends,
            'total_length': total_length,
        })


class CableCreateView(PermissionRequiredMixin, GetReturnURLMixin, View):
    permission_required = 'dcim.add_cable'
    template_name = 'dcim/cable_connect.html'

    def dispatch(self, request, *args, **kwargs):

        termination_a_type = kwargs.get('termination_a_type')
        termination_a_id = kwargs.get('termination_a_id')

        termination_b_type_name = kwargs.get('termination_b_type')
        self.termination_b_type = ContentType.objects.get(model=termination_b_type_name.replace('-', ''))

        self.obj = Cable(
            termination_a=termination_a_type.objects.get(pk=termination_a_id),
            termination_b_type=self.termination_b_type
        )
        self.form_class = {
            'console-port': forms.ConnectCableToConsolePortForm,
            'console-server-port': forms.ConnectCableToConsoleServerPortForm,
            'power-port': forms.ConnectCableToPowerPortForm,
            'power-outlet': forms.ConnectCableToPowerOutletForm,
            'interface': forms.ConnectCableToInterfaceForm,
            'front-port': forms.ConnectCableToFrontPortForm,
            'rear-port': forms.ConnectCableToRearPortForm,
            'power-feed': forms.ConnectCableToPowerFeedForm,
            'circuit-termination': forms.ConnectCableToCircuitTerminationForm,
        }[termination_b_type_name]

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        # Parse initial data manually to avoid setting field values as lists
        initial_data = {k: request.GET[k] for k in request.GET}

        # Set initial site and rack based on side A termination (if not already set)
        if 'termination_b_site' not in initial_data:
            initial_data['termination_b_site'] = getattr(self.obj.termination_a.parent, 'site', None)
        if 'termination_b_rack' not in initial_data:
            initial_data['termination_b_rack'] = getattr(self.obj.termination_a.parent, 'rack', None)

        form = self.form_class(instance=self.obj, initial=initial_data)

        return render(request, self.template_name, {
            'obj': self.obj,
            'obj_type': Cable._meta.verbose_name,
            'termination_b_type': self.termination_b_type.name,
            'form': form,
            'return_url': self.get_return_url(request, self.obj),
        })

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST, request.FILES, instance=self.obj)

        if form.is_valid():
            obj = form.save()

            msg = 'Created cable <a href="{}">{}</a>'.format(
                obj.get_absolute_url(),
                escape(obj)
            )
            messages.success(request, mark_safe(msg))

            if '_addanother' in request.POST:
                return redirect(request.get_full_path())

            return_url = form.cleaned_data.get('return_url')
            if return_url is not None and is_safe_url(url=return_url, allowed_hosts=request.get_host()):
                return redirect(return_url)
            else:
                return redirect(self.get_return_url(request, obj))

        return render(request, self.template_name, {
            'obj': self.obj,
            'obj_type': Cable._meta.verbose_name,
            'termination_b_type': self.termination_b_type.name,
            'form': form,
            'return_url': self.get_return_url(request, self.obj),
        })


class CableEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_cable'
    queryset = Cable.objects.all()
    model_form = forms.CableForm
    template_name = 'dcim/cable_edit.html'
    default_return_url = 'dcim:cable_list'


class CableDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_cable'
    queryset = Cable.objects.all()
    default_return_url = 'dcim:cable_list'


class CableBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_cable'
    queryset = Cable.objects.all()
    model_form = forms.CableCSVForm
    table = tables.CableTable
    default_return_url = 'dcim:cable_list'


class CableBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_cable'
    queryset = Cable.objects.prefetch_related('termination_a', 'termination_b')
    filterset = filters.CableFilterSet
    table = tables.CableTable
    form = forms.CableBulkEditForm
    default_return_url = 'dcim:cable_list'


class CableBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_cable'
    queryset = Cable.objects.prefetch_related('termination_a', 'termination_b')
    filterset = filters.CableFilterSet
    table = tables.CableTable
    default_return_url = 'dcim:cable_list'


#
# Connections
#

class ConsoleConnectionsListView(PermissionRequiredMixin, ObjectListView):
    permission_required = ('dcim.view_consoleport', 'dcim.view_consoleserverport')
    queryset = ConsolePort.objects.prefetch_related(
        'device', 'connected_endpoint__device'
    ).filter(
        connected_endpoint__isnull=False
    ).order_by(
        'cable', 'connected_endpoint__device__name', 'connected_endpoint__name'
    )
    filterset = filters.ConsoleConnectionFilterSet
    filterset_form = forms.ConsoleConnectionFilterForm
    table = tables.ConsoleConnectionTable
    template_name = 'dcim/console_connections_list.html'

    def queryset_to_csv(self):
        csv_data = [
            # Headers
            ','.join(['console_server', 'port', 'device', 'console_port', 'connection_status'])
        ]
        for obj in self.queryset:
            csv = csv_format([
                obj.connected_endpoint.device.identifier if obj.connected_endpoint else None,
                obj.connected_endpoint.name if obj.connected_endpoint else None,
                obj.device.identifier,
                obj.name,
                obj.get_connection_status_display(),
            ])
            csv_data.append(csv)

        return '\n'.join(csv_data)


class PowerConnectionsListView(PermissionRequiredMixin, ObjectListView):
    permission_required = ('dcim.view_powerport', 'dcim.view_poweroutlet')
    queryset = PowerPort.objects.prefetch_related(
        'device', '_connected_poweroutlet__device'
    ).filter(
        _connected_poweroutlet__isnull=False
    ).order_by(
        'cable', '_connected_poweroutlet__device__name', '_connected_poweroutlet__name'
    )
    filterset = filters.PowerConnectionFilterSet
    filterset_form = forms.PowerConnectionFilterForm
    table = tables.PowerConnectionTable
    template_name = 'dcim/power_connections_list.html'

    def queryset_to_csv(self):
        csv_data = [
            # Headers
            ','.join(['pdu', 'outlet', 'device', 'power_port', 'connection_status'])
        ]
        for obj in self.queryset:
            csv = csv_format([
                obj.connected_endpoint.device.identifier if obj.connected_endpoint else None,
                obj.connected_endpoint.name if obj.connected_endpoint else None,
                obj.device.identifier,
                obj.name,
                obj.get_connection_status_display(),
            ])
            csv_data.append(csv)

        return '\n'.join(csv_data)


class InterfaceConnectionsListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_interface'
    queryset = Interface.objects.prefetch_related(
        'device', 'cable', '_connected_interface__device'
    ).filter(
        # Avoid duplicate connections by only selecting the lower PK in a connected pair
        _connected_interface__isnull=False,
        pk__lt=F('_connected_interface')
    ).order_by(
        'device'
    )
    filterset = filters.InterfaceConnectionFilterSet
    filterset_form = forms.InterfaceConnectionFilterForm
    table = tables.InterfaceConnectionTable
    template_name = 'dcim/interface_connections_list.html'

    def queryset_to_csv(self):
        csv_data = [
            # Headers
            ','.join([
                'device_a', 'interface_a', 'device_b', 'interface_b', 'connection_status'
            ])
        ]
        for obj in self.queryset:
            csv = csv_format([
                obj.connected_endpoint.device.identifier if obj.connected_endpoint else None,
                obj.connected_endpoint.name if obj.connected_endpoint else None,
                obj.device.identifier,
                obj.name,
                obj.get_connection_status_display(),
            ])
            csv_data.append(csv)

        return '\n'.join(csv_data)


#
# Inventory items
#

class InventoryItemListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_inventoryitem'
    queryset = InventoryItem.objects.prefetch_related('device', 'manufacturer')
    filterset = filters.InventoryItemFilterSet
    filterset_form = forms.InventoryItemFilterForm
    table = tables.InventoryItemTable
    action_buttons = ('import', 'export')


class InventoryItemEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_inventoryitem'
    queryset = InventoryItem.objects.all()
    model_form = forms.InventoryItemForm


class InventoryItemCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_inventoryitem'
    model = InventoryItem
    form = forms.InventoryItemCreateForm
    model_form = forms.InventoryItemForm
    template_name = 'dcim/device_component_add.html'


class InventoryItemDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_inventoryitem'
    queryset = InventoryItem.objects.all()


class InventoryItemBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_inventoryitem'
    queryset = InventoryItem.objects.all()
    model_form = forms.InventoryItemCSVForm
    table = tables.InventoryItemTable
    default_return_url = 'dcim:inventoryitem_list'


class InventoryItemBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_inventoryitem'
    queryset = InventoryItem.objects.prefetch_related('device', 'manufacturer')
    filterset = filters.InventoryItemFilterSet
    table = tables.InventoryItemTable
    form = forms.InventoryItemBulkEditForm
    default_return_url = 'dcim:inventoryitem_list'


class InventoryItemBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_inventoryitem'
    queryset = InventoryItem.objects.prefetch_related('device', 'manufacturer')
    table = tables.InventoryItemTable
    template_name = 'dcim/inventoryitem_bulk_delete.html'
    default_return_url = 'dcim:inventoryitem_list'


#
# Virtual chassis
#

class VirtualChassisListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_virtualchassis'
    queryset = VirtualChassis.objects.prefetch_related('master').annotate(member_count=Count('members'))
    table = tables.VirtualChassisTable
    filterset = filters.VirtualChassisFilterSet
    filterset_form = forms.VirtualChassisFilterForm
    action_buttons = ('export',)


class VirtualChassisView(PermissionRequiredMixin, View):
    permission_required = 'dcim.view_virtualchassis'

    def get(self, request, pk):
        virtualchassis = get_object_or_404(VirtualChassis.objects.prefetch_related('members'), pk=pk)

        return render(request, 'dcim/virtualchassis.html', {
            'virtualchassis': virtualchassis,
        })


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
        ).prefetch_related('rack').order_by('vc_position')

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
        members_queryset = virtual_chassis.members.prefetch_related('rack').order_by('vc_position')

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
        members_queryset = virtual_chassis.members.prefetch_related('rack').order_by('vc_position')

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
                devices = Device.objects.filter(pk__in=[m.pk for m in members])
                for device in devices:
                    device.vc_position = None
                    device.save()
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
    queryset = VirtualChassis.objects.all()
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

            devices = Device.objects.filter(pk=device.pk)
            for device in devices:
                device.virtual_chassis = None
                device.vc_position = None
                device.vc_priority = None
                device.save()

            msg = 'Removed {} from virtual chassis {}'.format(device, device.virtual_chassis)
            messages.success(request, msg)

            return redirect(self.get_return_url(request, device))

        return render(request, 'dcim/virtualchassis_remove_member.html', {
            'device': device,
            'form': form,
            'return_url': self.get_return_url(request, device),
        })


class VirtualChassisBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_virtualchassis'
    queryset = VirtualChassis.objects.all()
    filterset = filters.VirtualChassisFilterSet
    table = tables.VirtualChassisTable
    form = forms.VirtualChassisBulkEditForm
    default_return_url = 'dcim:virtualchassis_list'


class VirtualChassisBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_virtualchassis'
    queryset = VirtualChassis.objects.all()
    filterset = filters.VirtualChassisFilterSet
    table = tables.VirtualChassisTable
    default_return_url = 'dcim:virtualchassis_list'


#
# Power panels
#

class PowerPanelListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_powerpanel'
    queryset = PowerPanel.objects.prefetch_related(
        'site', 'rack_group'
    ).annotate(
        powerfeed_count=Count('powerfeeds')
    )
    filterset = filters.PowerPanelFilterSet
    filterset_form = forms.PowerPanelFilterForm
    table = tables.PowerPanelTable


class PowerPanelView(PermissionRequiredMixin, View):
    permission_required = 'dcim.view_powerpanel'

    def get(self, request, pk):

        powerpanel = get_object_or_404(PowerPanel.objects.prefetch_related('site', 'rack_group'), pk=pk)
        powerfeed_table = tables.PowerFeedTable(
            data=PowerFeed.objects.filter(power_panel=powerpanel).prefetch_related('rack'),
            orderable=False
        )
        powerfeed_table.exclude = ['power_panel']

        return render(request, 'dcim/powerpanel.html', {
            'powerpanel': powerpanel,
            'powerfeed_table': powerfeed_table,
        })


class PowerPanelCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_powerpanel'
    queryset = PowerPanel.objects.all()
    model_form = forms.PowerPanelForm
    default_return_url = 'dcim:powerpanel_list'


class PowerPanelEditView(PowerPanelCreateView):
    permission_required = 'dcim.change_powerpanel'


class PowerPanelDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_powerpanel'
    queryset = PowerPanel.objects.all()
    default_return_url = 'dcim:powerpanel_list'


class PowerPanelBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_powerpanel'
    queryset = PowerPanel.objects.all()
    model_form = forms.PowerPanelCSVForm
    table = tables.PowerPanelTable
    default_return_url = 'dcim:powerpanel_list'


class PowerPanelBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_powerpanel'
    queryset = PowerPanel.objects.prefetch_related('site', 'rack_group')
    filterset = filters.PowerPanelFilterSet
    table = tables.PowerPanelTable
    form = forms.PowerPanelBulkEditForm
    default_return_url = 'dcim:powerpanel_list'


class PowerPanelBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_powerpanel'
    queryset = PowerPanel.objects.prefetch_related(
        'site', 'rack_group'
    ).annotate(
        rack_count=Count('powerfeeds')
    )
    filterset = filters.PowerPanelFilterSet
    table = tables.PowerPanelTable
    default_return_url = 'dcim:powerpanel_list'


#
# Power feeds
#

class PowerFeedListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_powerfeed'
    queryset = PowerFeed.objects.prefetch_related(
        'power_panel', 'rack'
    )
    filterset = filters.PowerFeedFilterSet
    filterset_form = forms.PowerFeedFilterForm
    table = tables.PowerFeedTable


class PowerFeedView(PermissionRequiredMixin, View):
    permission_required = 'dcim.view_powerfeed'

    def get(self, request, pk):

        powerfeed = get_object_or_404(PowerFeed.objects.prefetch_related('power_panel', 'rack'), pk=pk)

        return render(request, 'dcim/powerfeed.html', {
            'powerfeed': powerfeed,
        })


class PowerFeedCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_powerfeed'
    queryset = PowerFeed.objects.all()
    model_form = forms.PowerFeedForm
    template_name = 'dcim/powerfeed_edit.html'
    default_return_url = 'dcim:powerfeed_list'


class PowerFeedEditView(PowerFeedCreateView):
    permission_required = 'dcim.change_powerfeed'


class PowerFeedDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_powerfeed'
    queryset = PowerFeed.objects.all()
    default_return_url = 'dcim:powerfeed_list'


class PowerFeedBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'dcim.add_powerfeed'
    queryset = PowerFeed.objects.all()
    model_form = forms.PowerFeedCSVForm
    table = tables.PowerFeedTable
    default_return_url = 'dcim:powerfeed_list'


class PowerFeedBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_powerfeed'
    queryset = PowerFeed.objects.prefetch_related('power_panel', 'rack')
    filterset = filters.PowerFeedFilterSet
    table = tables.PowerFeedTable
    form = forms.PowerFeedBulkEditForm
    default_return_url = 'dcim:powerfeed_list'


class PowerFeedBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_powerfeed'
    queryset = PowerFeed.objects.prefetch_related('power_panel', 'rack')
    filterset = filters.PowerFeedFilterSet
    table = tables.PowerFeedTable
    default_return_url = 'dcim:powerfeed_list'
