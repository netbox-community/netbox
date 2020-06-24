from collections import OrderedDict

from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db.models import Count, F
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.views.generic import View

from circuits.models import Circuit
from extras.models import Graph
from extras.views import ObjectConfigContextView
from ipam.models import Prefix, Service, VLAN
from ipam.tables import InterfaceIPAddressTable, InterfaceVLANTable
from secrets.models import Secret
from utilities.forms import ConfirmationForm
from utilities.paginator import EnhancedPaginator
from utilities.permissions import get_permission_for_model
from utilities.utils import csv_format
from utilities.views import (
    BulkComponentCreateView, BulkDeleteView, BulkEditView, BulkImportView, BulkRenameView, ComponentCreateView,
    GetReturnURLMixin, ObjectView, ObjectImportView, ObjectDeleteView, ObjectEditView, ObjectListView,
    ObjectPermissionRequiredMixin,
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


class BulkDisconnectView(GetReturnURLMixin, ObjectPermissionRequiredMixin, View):
    """
    An extendable view for disconnection console/power/interface components in bulk.
    """
    queryset = None
    form = None
    template_name = 'dcim/bulk_disconnect.html'

    def get_required_permission(self):
        return get_permission_for_model(self.queryset.model, 'change')

    def post(self, request):

        selected_objects = []
        return_url = self.get_return_url(request)

        if '_confirm' in request.POST:
            form = self.form(request.POST)

            if form.is_valid():

                with transaction.atomic():

                    count = 0
                    for obj in self.queryset.filter(pk__in=form.cleaned_data['pk']):
                        if obj.cable is None:
                            continue
                        obj.cable.delete()
                        count += 1

                messages.success(request, "Disconnected {} {}".format(
                    count, self.queryset.model._meta.verbose_name_plural
                ))

                return redirect(return_url)

        else:
            form = self.form(initial={'pk': request.POST.getlist('pk')})
            selected_objects = self.queryset.filter(pk__in=form.initial['pk'])

        return render(request, self.template_name, {
            'form': form,
            'obj_type_plural': self.queryset.model._meta.verbose_name_plural,
            'selected_objects': selected_objects,
            'return_url': return_url,
        })


#
# Regions
#

class RegionListView(ObjectListView):
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


class RegionEditView(ObjectEditView):
    queryset = Region.objects.all()
    model_form = forms.RegionForm
    default_return_url = 'dcim:region_list'


class RegionBulkImportView(BulkImportView):
    queryset = Region.objects.all()
    model_form = forms.RegionCSVForm
    table = tables.RegionTable
    default_return_url = 'dcim:region_list'


class RegionBulkDeleteView(BulkDeleteView):
    queryset = Region.objects.all()
    filterset = filters.RegionFilterSet
    table = tables.RegionTable
    default_return_url = 'dcim:region_list'


#
# Sites
#

class SiteListView(ObjectListView):
    queryset = Site.objects.prefetch_related('region', 'tenant')
    filterset = filters.SiteFilterSet
    filterset_form = forms.SiteFilterForm
    table = tables.SiteTable


class SiteView(ObjectView):
    queryset = Site.objects.prefetch_related('region', 'tenant__group')

    def get(self, request, slug):

        site = get_object_or_404(self.queryset, slug=slug)
        stats = {
            'rack_count': Rack.objects.restrict(request.user, 'view').filter(site=site).count(),
            'device_count': Device.objects.restrict(request.user, 'view').filter(site=site).count(),
            'prefix_count': Prefix.objects.restrict(request.user, 'view').filter(site=site).count(),
            'vlan_count': VLAN.objects.restrict(request.user, 'view').filter(site=site).count(),
            'circuit_count': Circuit.objects.restrict(request.user, 'view').filter(terminations__site=site).count(),
            'vm_count': VirtualMachine.objects.restrict(request.user, 'view').filter(cluster__site=site).count(),
        }
        rack_groups = RackGroup.objects.restrict(request.user, 'view').filter(site=site).annotate(
            rack_count=Count('racks')
        )
        show_graphs = Graph.objects.filter(type__model='site').exists()

        return render(request, 'dcim/site.html', {
            'site': site,
            'stats': stats,
            'rack_groups': rack_groups,
            'show_graphs': show_graphs,
        })


class SiteEditView(ObjectEditView):
    queryset = Site.objects.all()
    model_form = forms.SiteForm
    template_name = 'dcim/site_edit.html'
    default_return_url = 'dcim:site_list'


class SiteDeleteView(ObjectDeleteView):
    queryset = Site.objects.all()
    default_return_url = 'dcim:site_list'


class SiteBulkImportView(BulkImportView):
    queryset = Site.objects.all()
    model_form = forms.SiteCSVForm
    table = tables.SiteTable
    default_return_url = 'dcim:site_list'


class SiteBulkEditView(BulkEditView):
    queryset = Site.objects.prefetch_related('region', 'tenant')
    filterset = filters.SiteFilterSet
    table = tables.SiteTable
    form = forms.SiteBulkEditForm
    default_return_url = 'dcim:site_list'


class SiteBulkDeleteView(BulkDeleteView):
    queryset = Site.objects.prefetch_related('region', 'tenant')
    filterset = filters.SiteFilterSet
    table = tables.SiteTable
    default_return_url = 'dcim:site_list'


#
# Rack groups
#

class RackGroupListView(ObjectListView):
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


class RackGroupEditView(ObjectEditView):
    queryset = RackGroup.objects.all()
    model_form = forms.RackGroupForm
    default_return_url = 'dcim:rackgroup_list'


class RackGroupBulkImportView(BulkImportView):
    queryset = RackGroup.objects.all()
    model_form = forms.RackGroupCSVForm
    table = tables.RackGroupTable
    default_return_url = 'dcim:rackgroup_list'


class RackGroupBulkDeleteView(BulkDeleteView):
    queryset = RackGroup.objects.prefetch_related('site').annotate(rack_count=Count('racks'))
    filterset = filters.RackGroupFilterSet
    table = tables.RackGroupTable
    default_return_url = 'dcim:rackgroup_list'


#
# Rack roles
#

class RackRoleListView(ObjectListView):
    queryset = RackRole.objects.annotate(rack_count=Count('racks'))
    table = tables.RackRoleTable


class RackRoleEditView(ObjectEditView):
    queryset = RackRole.objects.all()
    model_form = forms.RackRoleForm
    default_return_url = 'dcim:rackrole_list'


class RackRoleBulkImportView(BulkImportView):
    queryset = RackRole.objects.all()
    model_form = forms.RackRoleCSVForm
    table = tables.RackRoleTable
    default_return_url = 'dcim:rackrole_list'


class RackRoleBulkDeleteView(BulkDeleteView):
    queryset = RackRole.objects.annotate(rack_count=Count('racks'))
    table = tables.RackRoleTable
    default_return_url = 'dcim:rackrole_list'


#
# Racks
#

class RackListView(ObjectListView):
    queryset = Rack.objects.prefetch_related(
        'site', 'group', 'tenant', 'role', 'devices__device_type'
    ).annotate(
        device_count=Count('devices')
    )
    filterset = filters.RackFilterSet
    filterset_form = forms.RackFilterForm
    table = tables.RackDetailTable


class RackElevationListView(ObjectListView):
    """
    Display a set of rack elevations side-by-side.
    """
    queryset = Rack.objects.prefetch_related('role')

    def get(self, request):

        racks = filters.RackFilterSet(request.GET, self.queryset).qs
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


class RackView(ObjectView):
    queryset = Rack.objects.prefetch_related('site__region', 'tenant__group', 'group', 'role')

    def get(self, request, pk):
        rack = get_object_or_404(self.queryset, pk=pk)

        nonracked_devices = Device.objects.restrict(request.user, 'view').filter(
            rack=rack,
            position__isnull=True,
            parent_bay__isnull=True
        ).prefetch_related('device_type__manufacturer')

        peer_racks = Rack.objects.restrict(request.user, 'view').filter(site=rack.site)
        if rack.group:
            peer_racks = peer_racks.filter(group=rack.group)
        else:
            peer_racks = peer_racks.filter(group__isnull=True)
        next_rack = peer_racks.filter(name__gt=rack.name).order_by('name').first()
        prev_rack = peer_racks.filter(name__lt=rack.name).order_by('-name').first()

        reservations = RackReservation.objects.restrict(request.user, 'view').filter(rack=rack)
        power_feeds = PowerFeed.objects.restrict(request.user, 'view').filter(rack=rack).prefetch_related('power_panel')

        return render(request, 'dcim/rack.html', {
            'rack': rack,
            'device_count': Device.objects.restrict(request.user, 'view').filter(rack=rack).count(),
            'reservations': reservations,
            'power_feeds': power_feeds,
            'nonracked_devices': nonracked_devices,
            'next_rack': next_rack,
            'prev_rack': prev_rack,
        })


class RackEditView(ObjectEditView):
    queryset = Rack.objects.all()
    model_form = forms.RackForm
    template_name = 'dcim/rack_edit.html'
    default_return_url = 'dcim:rack_list'


class RackDeleteView(ObjectDeleteView):
    queryset = Rack.objects.all()
    default_return_url = 'dcim:rack_list'


class RackBulkImportView(BulkImportView):
    queryset = Rack.objects.all()
    model_form = forms.RackCSVForm
    table = tables.RackTable
    default_return_url = 'dcim:rack_list'


class RackBulkEditView(BulkEditView):
    queryset = Rack.objects.prefetch_related('site', 'group', 'tenant', 'role')
    filterset = filters.RackFilterSet
    table = tables.RackTable
    form = forms.RackBulkEditForm
    default_return_url = 'dcim:rack_list'


class RackBulkDeleteView(BulkDeleteView):
    queryset = Rack.objects.prefetch_related('site', 'group', 'tenant', 'role')
    filterset = filters.RackFilterSet
    table = tables.RackTable
    default_return_url = 'dcim:rack_list'


#
# Rack reservations
#

class RackReservationListView(ObjectListView):
    queryset = RackReservation.objects.prefetch_related('rack__site')
    filterset = filters.RackReservationFilterSet
    filterset_form = forms.RackReservationFilterForm
    table = tables.RackReservationTable
    action_buttons = ('export',)


class RackReservationView(ObjectView):
    queryset = RackReservation.objects.prefetch_related('rack')

    def get(self, request, pk):

        rackreservation = get_object_or_404(self.queryset, pk=pk)

        return render(request, 'dcim/rackreservation.html', {
            'rackreservation': rackreservation,
        })


class RackReservationEditView(ObjectEditView):
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


class RackReservationDeleteView(ObjectDeleteView):
    queryset = RackReservation.objects.all()
    default_return_url = 'dcim:rackreservation_list'


class RackReservationImportView(BulkImportView):
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


class RackReservationBulkEditView(BulkEditView):
    queryset = RackReservation.objects.prefetch_related('rack', 'user')
    filterset = filters.RackReservationFilterSet
    table = tables.RackReservationTable
    form = forms.RackReservationBulkEditForm
    default_return_url = 'dcim:rackreservation_list'


class RackReservationBulkDeleteView(BulkDeleteView):
    queryset = RackReservation.objects.prefetch_related('rack', 'user')
    filterset = filters.RackReservationFilterSet
    table = tables.RackReservationTable
    default_return_url = 'dcim:rackreservation_list'


#
# Manufacturers
#

class ManufacturerListView(ObjectListView):
    queryset = Manufacturer.objects.annotate(
        devicetype_count=Count('device_types', distinct=True),
        inventoryitem_count=Count('inventory_items', distinct=True),
        platform_count=Count('platforms', distinct=True),
    )
    table = tables.ManufacturerTable


class ManufacturerEditView(ObjectEditView):
    queryset = Manufacturer.objects.all()
    model_form = forms.ManufacturerForm
    default_return_url = 'dcim:manufacturer_list'


class ManufacturerBulkImportView(BulkImportView):
    queryset = Manufacturer.objects.all()
    model_form = forms.ManufacturerCSVForm
    table = tables.ManufacturerTable
    default_return_url = 'dcim:manufacturer_list'


class ManufacturerBulkDeleteView(BulkDeleteView):
    queryset = Manufacturer.objects.annotate(devicetype_count=Count('device_types'))
    table = tables.ManufacturerTable
    default_return_url = 'dcim:manufacturer_list'


#
# Device types
#

class DeviceTypeListView(ObjectListView):
    queryset = DeviceType.objects.prefetch_related('manufacturer').annotate(instance_count=Count('instances'))
    filterset = filters.DeviceTypeFilterSet
    filterset_form = forms.DeviceTypeFilterForm
    table = tables.DeviceTypeTable


class DeviceTypeView(ObjectView):
    queryset = DeviceType.objects.prefetch_related('manufacturer')

    def get(self, request, pk):

        devicetype = get_object_or_404(self.queryset, pk=pk)

        # Component tables
        consoleport_table = tables.ConsolePortTemplateTable(
            ConsolePortTemplate.objects.restrict(request.user, 'view').filter(device_type=devicetype),
            orderable=False
        )
        consoleserverport_table = tables.ConsoleServerPortTemplateTable(
            ConsoleServerPortTemplate.objects.restrict(request.user, 'view').filter(device_type=devicetype),
            orderable=False
        )
        powerport_table = tables.PowerPortTemplateTable(
            PowerPortTemplate.objects.restrict(request.user, 'view').filter(device_type=devicetype),
            orderable=False
        )
        poweroutlet_table = tables.PowerOutletTemplateTable(
            PowerOutletTemplate.objects.restrict(request.user, 'view').filter(device_type=devicetype),
            orderable=False
        )
        interface_table = tables.InterfaceTemplateTable(
            list(InterfaceTemplate.objects.restrict(request.user, 'view').filter(device_type=devicetype)),
            orderable=False
        )
        front_port_table = tables.FrontPortTemplateTable(
            FrontPortTemplate.objects.restrict(request.user, 'view').filter(device_type=devicetype),
            orderable=False
        )
        rear_port_table = tables.RearPortTemplateTable(
            RearPortTemplate.objects.restrict(request.user, 'view').filter(device_type=devicetype),
            orderable=False
        )
        devicebay_table = tables.DeviceBayTemplateTable(
            DeviceBayTemplate.objects.restrict(request.user, 'view').filter(device_type=devicetype),
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


class DeviceTypeEditView(ObjectEditView):
    queryset = DeviceType.objects.all()
    model_form = forms.DeviceTypeForm
    template_name = 'dcim/devicetype_edit.html'
    default_return_url = 'dcim:devicetype_list'


class DeviceTypeDeleteView(ObjectDeleteView):
    queryset = DeviceType.objects.all()
    default_return_url = 'dcim:devicetype_list'


class DeviceTypeImportView(ObjectImportView):
    additional_permissions = [
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
    queryset = DeviceType.objects.all()
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


class DeviceTypeBulkEditView(BulkEditView):
    queryset = DeviceType.objects.prefetch_related('manufacturer').annotate(instance_count=Count('instances'))
    filterset = filters.DeviceTypeFilterSet
    table = tables.DeviceTypeTable
    form = forms.DeviceTypeBulkEditForm
    default_return_url = 'dcim:devicetype_list'


class DeviceTypeBulkDeleteView(BulkDeleteView):
    queryset = DeviceType.objects.prefetch_related('manufacturer').annotate(instance_count=Count('instances'))
    filterset = filters.DeviceTypeFilterSet
    table = tables.DeviceTypeTable
    default_return_url = 'dcim:devicetype_list'


#
# Console port templates
#

class ConsolePortTemplateCreateView(ComponentCreateView):
    queryset = ConsolePortTemplate.objects.all()
    form = forms.ConsolePortTemplateCreateForm
    model_form = forms.ConsolePortTemplateForm
    template_name = 'dcim/device_component_add.html'


class ConsolePortTemplateEditView(ObjectEditView):
    queryset = ConsolePortTemplate.objects.all()
    model_form = forms.ConsolePortTemplateForm


class ConsolePortTemplateDeleteView(ObjectDeleteView):
    queryset = ConsolePortTemplate.objects.all()


class ConsolePortTemplateBulkEditView(BulkEditView):
    queryset = ConsolePortTemplate.objects.all()
    table = tables.ConsolePortTemplateTable
    form = forms.ConsolePortTemplateBulkEditForm


class ConsolePortTemplateBulkDeleteView(BulkDeleteView):
    queryset = ConsolePortTemplate.objects.all()
    table = tables.ConsolePortTemplateTable


#
# Console server port templates
#

class ConsoleServerPortTemplateCreateView(ComponentCreateView):
    queryset = ConsoleServerPortTemplate.objects.all()
    form = forms.ConsoleServerPortTemplateCreateForm
    model_form = forms.ConsoleServerPortTemplateForm
    template_name = 'dcim/device_component_add.html'


class ConsoleServerPortTemplateEditView(ObjectEditView):
    queryset = ConsoleServerPortTemplate.objects.all()
    model_form = forms.ConsoleServerPortTemplateForm


class ConsoleServerPortTemplateDeleteView(ObjectDeleteView):
    queryset = ConsoleServerPortTemplate.objects.all()


class ConsoleServerPortTemplateBulkEditView(BulkEditView):
    queryset = ConsoleServerPortTemplate.objects.all()
    table = tables.ConsoleServerPortTemplateTable
    form = forms.ConsoleServerPortTemplateBulkEditForm


class ConsoleServerPortTemplateBulkDeleteView(BulkDeleteView):
    queryset = ConsoleServerPortTemplate.objects.all()
    table = tables.ConsoleServerPortTemplateTable


#
# Power port templates
#

class PowerPortTemplateCreateView(ComponentCreateView):
    queryset = PowerPortTemplate.objects.all()
    form = forms.PowerPortTemplateCreateForm
    model_form = forms.PowerPortTemplateForm
    template_name = 'dcim/device_component_add.html'


class PowerPortTemplateEditView(ObjectEditView):
    queryset = PowerPortTemplate.objects.all()
    model_form = forms.PowerPortTemplateForm


class PowerPortTemplateDeleteView(ObjectDeleteView):
    queryset = PowerPortTemplate.objects.all()


class PowerPortTemplateBulkEditView(BulkEditView):
    queryset = PowerPortTemplate.objects.all()
    table = tables.PowerPortTemplateTable
    form = forms.PowerPortTemplateBulkEditForm


class PowerPortTemplateBulkDeleteView(BulkDeleteView):
    queryset = PowerPortTemplate.objects.all()
    table = tables.PowerPortTemplateTable


#
# Power outlet templates
#

class PowerOutletTemplateCreateView(ComponentCreateView):
    queryset = PowerOutletTemplate.objects.all()
    form = forms.PowerOutletTemplateCreateForm
    model_form = forms.PowerOutletTemplateForm
    template_name = 'dcim/device_component_add.html'


class PowerOutletTemplateEditView(ObjectEditView):
    queryset = PowerOutletTemplate.objects.all()
    model_form = forms.PowerOutletTemplateForm


class PowerOutletTemplateDeleteView(ObjectDeleteView):
    queryset = PowerOutletTemplate.objects.all()


class PowerOutletTemplateBulkEditView(BulkEditView):
    queryset = PowerOutletTemplate.objects.all()
    table = tables.PowerOutletTemplateTable
    form = forms.PowerOutletTemplateBulkEditForm


class PowerOutletTemplateBulkDeleteView(BulkDeleteView):
    queryset = PowerOutletTemplate.objects.all()
    table = tables.PowerOutletTemplateTable


#
# Interface templates
#

class InterfaceTemplateCreateView(ComponentCreateView):
    queryset = InterfaceTemplate.objects.all()
    form = forms.InterfaceTemplateCreateForm
    model_form = forms.InterfaceTemplateForm
    template_name = 'dcim/device_component_add.html'


class InterfaceTemplateEditView(ObjectEditView):
    queryset = InterfaceTemplate.objects.all()
    model_form = forms.InterfaceTemplateForm


class InterfaceTemplateDeleteView(ObjectDeleteView):
    queryset = InterfaceTemplate.objects.all()


class InterfaceTemplateBulkEditView(BulkEditView):
    queryset = InterfaceTemplate.objects.all()
    table = tables.InterfaceTemplateTable
    form = forms.InterfaceTemplateBulkEditForm


class InterfaceTemplateBulkDeleteView(BulkDeleteView):
    queryset = InterfaceTemplate.objects.all()
    table = tables.InterfaceTemplateTable


#
# Front port templates
#

class FrontPortTemplateCreateView(ComponentCreateView):
    queryset = FrontPortTemplate.objects.all()
    form = forms.FrontPortTemplateCreateForm
    model_form = forms.FrontPortTemplateForm
    template_name = 'dcim/device_component_add.html'


class FrontPortTemplateEditView(ObjectEditView):
    queryset = FrontPortTemplate.objects.all()
    model_form = forms.FrontPortTemplateForm


class FrontPortTemplateDeleteView(ObjectDeleteView):
    queryset = FrontPortTemplate.objects.all()


class FrontPortTemplateBulkEditView(BulkEditView):
    queryset = FrontPortTemplate.objects.all()
    table = tables.FrontPortTemplateTable
    form = forms.FrontPortTemplateBulkEditForm


class FrontPortTemplateBulkDeleteView(BulkDeleteView):
    queryset = FrontPortTemplate.objects.all()
    table = tables.FrontPortTemplateTable


#
# Rear port templates
#

class RearPortTemplateCreateView(ComponentCreateView):
    queryset = RearPortTemplate.objects.all()
    form = forms.RearPortTemplateCreateForm
    model_form = forms.RearPortTemplateForm
    template_name = 'dcim/device_component_add.html'


class RearPortTemplateEditView(ObjectEditView):
    queryset = RearPortTemplate.objects.all()
    model_form = forms.RearPortTemplateForm


class RearPortTemplateDeleteView(ObjectDeleteView):
    queryset = RearPortTemplate.objects.all()


class RearPortTemplateBulkEditView(BulkEditView):
    queryset = RearPortTemplate.objects.all()
    table = tables.RearPortTemplateTable
    form = forms.RearPortTemplateBulkEditForm


class RearPortTemplateBulkDeleteView(BulkDeleteView):
    queryset = RearPortTemplate.objects.all()
    table = tables.RearPortTemplateTable


#
# Device bay templates
#

class DeviceBayTemplateCreateView(ComponentCreateView):
    queryset = DeviceBayTemplate.objects.all()
    form = forms.DeviceBayTemplateCreateForm
    model_form = forms.DeviceBayTemplateForm
    template_name = 'dcim/device_component_add.html'


class DeviceBayTemplateEditView(ObjectEditView):
    queryset = DeviceBayTemplate.objects.all()
    model_form = forms.DeviceBayTemplateForm


class DeviceBayTemplateDeleteView(ObjectDeleteView):
    queryset = DeviceBayTemplate.objects.all()


# class DeviceBayTemplateBulkEditView(BulkEditView):
#     queryset = DeviceBayTemplate.objects.all()
#     table = tables.DeviceBayTemplateTable
#     form = forms.DeviceBayTemplateBulkEditForm


class DeviceBayTemplateBulkDeleteView(BulkDeleteView):
    queryset = DeviceBayTemplate.objects.all()
    table = tables.DeviceBayTemplateTable


#
# Device roles
#

class DeviceRoleListView(ObjectListView):
    queryset = DeviceRole.objects.all()
    table = tables.DeviceRoleTable


class DeviceRoleEditView(ObjectEditView):
    queryset = DeviceRole.objects.all()
    model_form = forms.DeviceRoleForm
    default_return_url = 'dcim:devicerole_list'


class DeviceRoleBulkImportView(BulkImportView):
    queryset = DeviceRole.objects.all()
    model_form = forms.DeviceRoleCSVForm
    table = tables.DeviceRoleTable
    default_return_url = 'dcim:devicerole_list'


class DeviceRoleBulkDeleteView(BulkDeleteView):
    queryset = DeviceRole.objects.all()
    table = tables.DeviceRoleTable
    default_return_url = 'dcim:devicerole_list'


#
# Platforms
#

class PlatformListView(ObjectListView):
    queryset = Platform.objects.all()
    table = tables.PlatformTable


class PlatformEditView(ObjectEditView):
    queryset = Platform.objects.all()
    model_form = forms.PlatformForm
    default_return_url = 'dcim:platform_list'


class PlatformBulkImportView(BulkImportView):
    queryset = Platform.objects.all()
    model_form = forms.PlatformCSVForm
    table = tables.PlatformTable
    default_return_url = 'dcim:platform_list'


class PlatformBulkDeleteView(BulkDeleteView):
    queryset = Platform.objects.all()
    table = tables.PlatformTable
    default_return_url = 'dcim:platform_list'


#
# Devices
#

class DeviceListView(ObjectListView):
    queryset = Device.objects.prefetch_related(
        'device_type__manufacturer', 'device_role', 'tenant', 'site', 'rack', 'primary_ip4', 'primary_ip6'
    )
    filterset = filters.DeviceFilterSet
    filterset_form = forms.DeviceFilterForm
    table = tables.DeviceTable
    template_name = 'dcim/device_list.html'


class DeviceView(ObjectView):
    queryset = Device.objects.prefetch_related(
        'site__region', 'rack__group', 'tenant__group', 'device_role', 'platform', 'primary_ip4', 'primary_ip6'
    )

    def get(self, request, pk):

        device = get_object_or_404(self.queryset, pk=pk)

        # VirtualChassis members
        if device.virtual_chassis is not None:
            vc_members = Device.objects.restrict(request.user, 'view').filter(
                virtual_chassis=device.virtual_chassis
            ).order_by('vc_position')
        else:
            vc_members = []

        # Console ports
        console_ports = ConsolePort.objects.restrict(request.user, 'view').filter(device=device).prefetch_related(
            'connected_endpoint__device', 'cable',
        )

        # Console server ports
        consoleserverports = ConsoleServerPort.objects.restrict(request.user, 'view').filter(
            device=device
        ).prefetch_related(
            'connected_endpoint__device', 'cable',
        )

        # Power ports
        power_ports = PowerPort.objects.restrict(request.user, 'view').filter(device=device).prefetch_related(
            '_connected_poweroutlet__device', 'cable',
        )

        # Power outlets
        poweroutlets = PowerOutlet.objects.restrict(request.user, 'view').filter(device=device).prefetch_related(
            'connected_endpoint__device', 'cable', 'power_port',
        )

        # Interfaces
        interfaces = device.vc_interfaces.restrict(request.user, 'view').filter(device=device).prefetch_related(
            'lag', '_connected_interface__device', '_connected_circuittermination__circuit', 'cable',
            'cable__termination_a', 'cable__termination_b', 'ip_addresses', 'tags'
        )

        # Front ports
        front_ports = FrontPort.objects.restrict(request.user, 'view').filter(device=device).prefetch_related(
            'rear_port', 'cable',
        )

        # Rear ports
        rear_ports = RearPort.objects.restrict(request.user, 'view').filter(device=device).prefetch_related('cable')

        # Device bays
        device_bays = DeviceBay.objects.restrict(request.user, 'view').filter(device=device).prefetch_related(
            'installed_device__device_type__manufacturer',
        )

        # Services
        services = Service.objects.restrict(request.user, 'view').filter(device=device)

        # Secrets
        secrets = Secret.objects.restrict(request.user, 'view').filter(device=device)

        # Find up to ten devices in the same site with the same functional role for quick reference.
        related_devices = Device.objects.restrict(request.user, 'view').filter(
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


class DeviceInventoryView(ObjectView):
    queryset = Device.objects.all()

    def get(self, request, pk):

        device = get_object_or_404(self.queryset, pk=pk)
        inventory_items = InventoryItem.objects.restrict(request.user, 'view').filter(
            device=device, parent=None
        ).prefetch_related(
            'manufacturer', 'child_items'
        )

        return render(request, 'dcim/device_inventory.html', {
            'device': device,
            'inventory_items': inventory_items,
            'active_tab': 'inventory',
        })


class DeviceStatusView(ObjectView):
    additional_permissions = ['dcim.napalm_read_device']
    queryset = Device.objects.all()

    def get(self, request, pk):

        device = get_object_or_404(self.queryset, pk=pk)

        return render(request, 'dcim/device_status.html', {
            'device': device,
            'active_tab': 'status',
        })


class DeviceLLDPNeighborsView(ObjectView):
    additional_permissions = ['dcim.napalm_read_device']
    queryset = Device.objects.all()

    def get(self, request, pk):

        device = get_object_or_404(self.queryset, pk=pk)
        interfaces = device.vc_interfaces.restrict(request.user, 'view').exclude(
            type__in=NONCONNECTABLE_IFACE_TYPES
        ).prefetch_related(
            '_connected_interface__device'
        )

        return render(request, 'dcim/device_lldp_neighbors.html', {
            'device': device,
            'interfaces': interfaces,
            'active_tab': 'lldp-neighbors',
        })


class DeviceConfigView(ObjectView):
    additional_permissions = ['dcim.napalm_read_device']
    queryset = Device.objects.all()

    def get(self, request, pk):

        device = get_object_or_404(self.queryset, pk=pk)

        return render(request, 'dcim/device_config.html', {
            'device': device,
            'active_tab': 'config',
        })


class DeviceConfigContextView(ObjectConfigContextView):
    queryset = Device.objects.all()
    base_template = 'dcim/device.html'


class DeviceEditView(ObjectEditView):
    queryset = Device.objects.all()
    model_form = forms.DeviceForm
    template_name = 'dcim/device_edit.html'
    default_return_url = 'dcim:device_list'


class DeviceDeleteView(ObjectDeleteView):
    queryset = Device.objects.all()
    default_return_url = 'dcim:device_list'


class DeviceBulkImportView(BulkImportView):
    queryset = Device.objects.all()
    model_form = forms.DeviceCSVForm
    table = tables.DeviceImportTable
    template_name = 'dcim/device_import.html'
    default_return_url = 'dcim:device_list'


class ChildDeviceBulkImportView(BulkImportView):
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


class DeviceBulkEditView(BulkEditView):
    queryset = Device.objects.prefetch_related('tenant', 'site', 'rack', 'device_role', 'device_type__manufacturer')
    filterset = filters.DeviceFilterSet
    table = tables.DeviceTable
    form = forms.DeviceBulkEditForm
    default_return_url = 'dcim:device_list'


class DeviceBulkDeleteView(BulkDeleteView):
    queryset = Device.objects.prefetch_related('tenant', 'site', 'rack', 'device_role', 'device_type__manufacturer')
    filterset = filters.DeviceFilterSet
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


#
# Console ports
#

class ConsolePortListView(ObjectListView):
    queryset = ConsolePort.objects.prefetch_related('device', 'device__tenant', 'device__site', 'cable')
    filterset = filters.ConsolePortFilterSet
    filterset_form = forms.ConsolePortFilterForm
    table = tables.ConsolePortDetailTable
    action_buttons = ('import', 'export')


class ConsolePortCreateView(ComponentCreateView):
    queryset = ConsolePort.objects.all()
    form = forms.ConsolePortCreateForm
    model_form = forms.ConsolePortForm
    template_name = 'dcim/device_component_add.html'


class ConsolePortEditView(ObjectEditView):
    queryset = ConsolePort.objects.all()
    model_form = forms.ConsolePortForm


class ConsolePortDeleteView(ObjectDeleteView):
    queryset = ConsolePort.objects.all()


class ConsolePortBulkImportView(BulkImportView):
    queryset = ConsolePort.objects.all()
    model_form = forms.ConsolePortCSVForm
    table = tables.ConsolePortImportTable
    default_return_url = 'dcim:consoleport_list'


class ConsolePortBulkEditView(BulkEditView):
    queryset = ConsolePort.objects.all()
    filterset = filters.ConsolePortFilterSet
    table = tables.ConsolePortTable
    form = forms.ConsolePortBulkEditForm


class ConsolePortBulkDeleteView(BulkDeleteView):
    queryset = ConsolePort.objects.all()
    filterset = filters.ConsolePortFilterSet
    table = tables.ConsolePortTable
    default_return_url = 'dcim:consoleport_list'


#
# Console server ports
#

class ConsoleServerPortListView(ObjectListView):
    queryset = ConsoleServerPort.objects.prefetch_related('device', 'device__tenant', 'device__site', 'cable')
    filterset = filters.ConsoleServerPortFilterSet
    filterset_form = forms.ConsoleServerPortFilterForm
    table = tables.ConsoleServerPortDetailTable
    action_buttons = ('import', 'export')


class ConsoleServerPortCreateView(ComponentCreateView):
    queryset = ConsoleServerPort.objects.all()
    form = forms.ConsoleServerPortCreateForm
    model_form = forms.ConsoleServerPortForm
    template_name = 'dcim/device_component_add.html'


class ConsoleServerPortEditView(ObjectEditView):
    queryset = ConsoleServerPort.objects.all()
    model_form = forms.ConsoleServerPortForm


class ConsoleServerPortDeleteView(ObjectDeleteView):
    queryset = ConsoleServerPort.objects.all()


class ConsoleServerPortBulkImportView(BulkImportView):
    queryset = ConsoleServerPort.objects.all()
    model_form = forms.ConsoleServerPortCSVForm
    table = tables.ConsoleServerPortImportTable
    default_return_url = 'dcim:consoleserverport_list'


class ConsoleServerPortBulkEditView(BulkEditView):
    queryset = ConsoleServerPort.objects.all()
    filterset = filters.ConsoleServerPortFilterSet
    table = tables.ConsoleServerPortTable
    form = forms.ConsoleServerPortBulkEditForm


class ConsoleServerPortBulkRenameView(BulkRenameView):
    queryset = ConsoleServerPort.objects.all()
    form = forms.ConsoleServerPortBulkRenameForm


class ConsoleServerPortBulkDisconnectView(BulkDisconnectView):
    queryset = ConsoleServerPort.objects.all()
    form = forms.ConsoleServerPortBulkDisconnectForm


class ConsoleServerPortBulkDeleteView(BulkDeleteView):
    queryset = ConsoleServerPort.objects.all()
    filterset = filters.ConsoleServerPortFilterSet
    table = tables.ConsoleServerPortTable
    default_return_url = 'dcim:consoleserverport_list'


#
# Power ports
#

class PowerPortListView(ObjectListView):
    queryset = PowerPort.objects.prefetch_related('device', 'device__tenant', 'device__site', 'cable')
    filterset = filters.PowerPortFilterSet
    filterset_form = forms.PowerPortFilterForm
    table = tables.PowerPortDetailTable
    action_buttons = ('import', 'export')


class PowerPortCreateView(ComponentCreateView):
    queryset = PowerPort.objects.all()
    form = forms.PowerPortCreateForm
    model_form = forms.PowerPortForm
    template_name = 'dcim/device_component_add.html'


class PowerPortEditView(ObjectEditView):
    queryset = PowerPort.objects.all()
    model_form = forms.PowerPortForm


class PowerPortDeleteView(ObjectDeleteView):
    queryset = PowerPort.objects.all()


class PowerPortBulkImportView(BulkImportView):
    queryset = PowerPort.objects.all()
    model_form = forms.PowerPortCSVForm
    table = tables.PowerPortImportTable
    default_return_url = 'dcim:powerport_list'


class PowerPortBulkEditView(BulkEditView):
    queryset = PowerPort.objects.all()
    filterset = filters.PowerPortFilterSet
    table = tables.PowerPortTable
    form = forms.PowerPortBulkEditForm


class PowerPortBulkDeleteView(BulkDeleteView):
    queryset = PowerPort.objects.all()
    filterset = filters.PowerPortFilterSet
    table = tables.PowerPortTable
    default_return_url = 'dcim:powerport_list'


#
# Power outlets
#

class PowerOutletListView(ObjectListView):
    queryset = PowerOutlet.objects.prefetch_related('device', 'device__tenant', 'device__site', 'cable')
    filterset = filters.PowerOutletFilterSet
    filterset_form = forms.PowerOutletFilterForm
    table = tables.PowerOutletDetailTable
    action_buttons = ('import', 'export')


class PowerOutletCreateView(ComponentCreateView):
    queryset = PowerOutlet.objects.all()
    form = forms.PowerOutletCreateForm
    model_form = forms.PowerOutletForm
    template_name = 'dcim/device_component_add.html'


class PowerOutletEditView(ObjectEditView):
    queryset = PowerOutlet.objects.all()
    model_form = forms.PowerOutletForm


class PowerOutletDeleteView(ObjectDeleteView):
    queryset = PowerOutlet.objects.all()


class PowerOutletBulkImportView(BulkImportView):
    queryset = PowerOutlet.objects.all()
    model_form = forms.PowerOutletCSVForm
    table = tables.PowerOutletImportTable
    default_return_url = 'dcim:poweroutlet_list'


class PowerOutletBulkEditView(BulkEditView):
    queryset = PowerOutlet.objects.all()
    filterset = filters.PowerOutletFilterSet
    table = tables.PowerOutletTable
    form = forms.PowerOutletBulkEditForm


class PowerOutletBulkRenameView(BulkRenameView):
    queryset = PowerOutlet.objects.all()
    form = forms.PowerOutletBulkRenameForm


class PowerOutletBulkDisconnectView(BulkDisconnectView):
    queryset = PowerOutlet.objects.all()
    form = forms.PowerOutletBulkDisconnectForm


class PowerOutletBulkDeleteView(BulkDeleteView):
    queryset = PowerOutlet.objects.all()
    filterset = filters.PowerOutletFilterSet
    table = tables.PowerOutletTable
    default_return_url = 'dcim:poweroutlet_list'


#
# Interfaces
#

class InterfaceListView(ObjectListView):
    queryset = Interface.objects.prefetch_related('device', 'device__tenant', 'device__site', 'cable')
    filterset = filters.InterfaceFilterSet
    filterset_form = forms.InterfaceFilterForm
    table = tables.InterfaceDetailTable
    action_buttons = ('import', 'export')


class InterfaceView(ObjectView):
    queryset = Interface.objects.all()

    def get(self, request, pk):

        interface = get_object_or_404(self.queryset, pk=pk)

        # Get assigned IP addresses
        ipaddress_table = InterfaceIPAddressTable(
            data=interface.ip_addresses.restrict(request.user, 'view').prefetch_related('vrf', 'tenant'),
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


class InterfaceCreateView(ComponentCreateView):
    queryset = Interface.objects.all()
    form = forms.InterfaceCreateForm
    model_form = forms.InterfaceForm
    template_name = 'dcim/device_component_add.html'


class InterfaceEditView(ObjectEditView):
    queryset = Interface.objects.all()
    model_form = forms.InterfaceForm
    template_name = 'dcim/interface_edit.html'


class InterfaceDeleteView(ObjectDeleteView):
    queryset = Interface.objects.all()


class InterfaceBulkImportView(BulkImportView):
    queryset = Interface.objects.all()
    model_form = forms.InterfaceCSVForm
    table = tables.InterfaceImportTable
    default_return_url = 'dcim:interface_list'


class InterfaceBulkEditView(BulkEditView):
    queryset = Interface.objects.all()
    filterset = filters.InterfaceFilterSet
    table = tables.InterfaceTable
    form = forms.InterfaceBulkEditForm


class InterfaceBulkRenameView(BulkRenameView):
    queryset = Interface.objects.all()
    form = forms.InterfaceBulkRenameForm


class InterfaceBulkDisconnectView(BulkDisconnectView):
    queryset = Interface.objects.all()
    form = forms.InterfaceBulkDisconnectForm


class InterfaceBulkDeleteView(BulkDeleteView):
    queryset = Interface.objects.all()
    filterset = filters.InterfaceFilterSet
    table = tables.InterfaceTable
    default_return_url = 'dcim:interface_list'


#
# Front ports
#

class FrontPortListView(ObjectListView):
    queryset = FrontPort.objects.prefetch_related('device', 'device__tenant', 'device__site', 'cable')
    filterset = filters.FrontPortFilterSet
    filterset_form = forms.FrontPortFilterForm
    table = tables.FrontPortDetailTable
    action_buttons = ('import', 'export')


class FrontPortCreateView(ComponentCreateView):
    queryset = FrontPort.objects.all()
    form = forms.FrontPortCreateForm
    model_form = forms.FrontPortForm
    template_name = 'dcim/device_component_add.html'


class FrontPortEditView(ObjectEditView):
    queryset = FrontPort.objects.all()
    model_form = forms.FrontPortForm


class FrontPortDeleteView(ObjectDeleteView):
    queryset = FrontPort.objects.all()


class FrontPortBulkImportView(BulkImportView):
    queryset = FrontPort.objects.all()
    model_form = forms.FrontPortCSVForm
    table = tables.FrontPortImportTable
    default_return_url = 'dcim:frontport_list'


class FrontPortBulkEditView(BulkEditView):
    queryset = FrontPort.objects.all()
    filterset = filters.FrontPortFilterSet
    table = tables.FrontPortTable
    form = forms.FrontPortBulkEditForm


class FrontPortBulkRenameView(BulkRenameView):
    queryset = FrontPort.objects.all()
    form = forms.FrontPortBulkRenameForm


class FrontPortBulkDisconnectView(BulkDisconnectView):
    queryset = FrontPort.objects.all()
    form = forms.FrontPortBulkDisconnectForm


class FrontPortBulkDeleteView(BulkDeleteView):
    queryset = FrontPort.objects.all()
    filterset = filters.FrontPortFilterSet
    table = tables.FrontPortTable
    default_return_url = 'dcim:frontport_list'


#
# Rear ports
#

class RearPortListView(ObjectListView):
    queryset = RearPort.objects.prefetch_related('device', 'device__tenant', 'device__site', 'cable')
    filterset = filters.RearPortFilterSet
    filterset_form = forms.RearPortFilterForm
    table = tables.RearPortDetailTable
    action_buttons = ('import', 'export')


class RearPortCreateView(ComponentCreateView):
    queryset = RearPort.objects.all()
    form = forms.RearPortCreateForm
    model_form = forms.RearPortForm
    template_name = 'dcim/device_component_add.html'


class RearPortEditView(ObjectEditView):
    queryset = RearPort.objects.all()
    model_form = forms.RearPortForm


class RearPortDeleteView(ObjectDeleteView):
    queryset = RearPort.objects.all()


class RearPortBulkImportView(BulkImportView):
    queryset = RearPort.objects.all()
    model_form = forms.RearPortCSVForm
    table = tables.RearPortImportTable
    default_return_url = 'dcim:rearport_list'


class RearPortBulkEditView(BulkEditView):
    queryset = RearPort.objects.all()
    filterset = filters.RearPortFilterSet
    table = tables.RearPortTable
    form = forms.RearPortBulkEditForm


class RearPortBulkRenameView(BulkRenameView):
    queryset = RearPort.objects.all()
    form = forms.RearPortBulkRenameForm


class RearPortBulkDisconnectView(BulkDisconnectView):
    queryset = RearPort.objects.all()
    form = forms.RearPortBulkDisconnectForm


class RearPortBulkDeleteView(BulkDeleteView):
    queryset = RearPort.objects.all()
    filterset = filters.RearPortFilterSet
    table = tables.RearPortTable
    default_return_url = 'dcim:rearport_list'


#
# Device bays
#

class DeviceBayListView(ObjectListView):
    queryset = DeviceBay.objects.prefetch_related(
        'device', 'device__site', 'installed_device', 'installed_device__site'
    )
    filterset = filters.DeviceBayFilterSet
    filterset_form = forms.DeviceBayFilterForm
    table = tables.DeviceBayDetailTable
    action_buttons = ('import', 'export')


class DeviceBayCreateView(ComponentCreateView):
    queryset = DeviceBay.objects.all()
    form = forms.DeviceBayCreateForm
    model_form = forms.DeviceBayForm
    template_name = 'dcim/device_component_add.html'


class DeviceBayEditView(ObjectEditView):
    queryset = DeviceBay.objects.all()
    model_form = forms.DeviceBayForm


class DeviceBayDeleteView(ObjectDeleteView):
    queryset = DeviceBay.objects.all()


class DeviceBayPopulateView(ObjectEditView):
    queryset = DeviceBay.objects.all()

    def get(self, request, pk):
        device_bay = get_object_or_404(self.queryset, pk=pk)
        form = forms.PopulateDeviceBayForm(device_bay)

        return render(request, 'dcim/devicebay_populate.html', {
            'device_bay': device_bay,
            'form': form,
            'return_url': reverse('dcim:device', kwargs={'pk': device_bay.device.pk}),
        })

    def post(self, request, pk):
        device_bay = get_object_or_404(self.queryset, pk=pk)
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


class DeviceBayDepopulateView(ObjectEditView):
    queryset = DeviceBay.objects.all()

    def get(self, request, pk):

        device_bay = get_object_or_404(self.queryset, pk=pk)
        form = ConfirmationForm()

        return render(request, 'dcim/devicebay_depopulate.html', {
            'device_bay': device_bay,
            'form': form,
            'return_url': reverse('dcim:device', kwargs={'pk': device_bay.device.pk}),
        })

    def post(self, request, pk):

        device_bay = get_object_or_404(self.queryset, pk=pk)
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


class DeviceBayBulkImportView(BulkImportView):
    queryset = DeviceBay.objects.all()
    model_form = forms.DeviceBayCSVForm
    table = tables.DeviceBayImportTable
    default_return_url = 'dcim:devicebay_list'


class DeviceBayBulkEditView(BulkEditView):
    queryset = DeviceBay.objects.all()
    filterset = filters.DeviceBayFilterSet
    table = tables.DeviceBayTable
    form = forms.DeviceBayBulkEditForm


class DeviceBayBulkRenameView(BulkRenameView):
    queryset = DeviceBay.objects.all()
    form = forms.DeviceBayBulkRenameForm


class DeviceBayBulkDeleteView(BulkDeleteView):
    queryset = DeviceBay.objects.all()
    filterset = filters.DeviceBayFilterSet
    table = tables.DeviceBayTable
    default_return_url = 'dcim:devicebay_list'


#
# Bulk Device component creation
#

class DeviceBulkAddConsolePortView(BulkComponentCreateView):
    parent_model = Device
    parent_field = 'device'
    form = forms.ConsolePortBulkCreateForm
    queryset = ConsolePort.objects.all()
    model_form = forms.ConsolePortForm
    filterset = filters.DeviceFilterSet
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


class DeviceBulkAddConsoleServerPortView(BulkComponentCreateView):
    parent_model = Device
    parent_field = 'device'
    form = forms.ConsoleServerPortBulkCreateForm
    queryset = ConsoleServerPort.objects.all()
    model_form = forms.ConsoleServerPortForm
    filterset = filters.DeviceFilterSet
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


class DeviceBulkAddPowerPortView(BulkComponentCreateView):
    parent_model = Device
    parent_field = 'device'
    form = forms.PowerPortBulkCreateForm
    queryset = PowerPort.objects.all()
    model_form = forms.PowerPortForm
    filterset = filters.DeviceFilterSet
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


class DeviceBulkAddPowerOutletView(BulkComponentCreateView):
    parent_model = Device
    parent_field = 'device'
    form = forms.PowerOutletBulkCreateForm
    queryset = PowerOutlet.objects.all()
    model_form = forms.PowerOutletForm
    filterset = filters.DeviceFilterSet
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


class DeviceBulkAddInterfaceView(BulkComponentCreateView):
    parent_model = Device
    parent_field = 'device'
    form = forms.InterfaceBulkCreateForm
    queryset = Interface.objects.all()
    model_form = forms.InterfaceForm
    filterset = filters.DeviceFilterSet
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


# class DeviceBulkAddFrontPortView(BulkComponentCreateView):
#     parent_model = Device
#     parent_field = 'device'
#     form = forms.FrontPortBulkCreateForm
#     queryset = FrontPort.objects.all()
#     model_form = forms.FrontPortForm
#     filterset = filters.DeviceFilterSet
#     table = tables.DeviceTable
#     default_return_url = 'dcim:device_list'


class DeviceBulkAddRearPortView(BulkComponentCreateView):
    parent_model = Device
    parent_field = 'device'
    form = forms.RearPortBulkCreateForm
    queryset = RearPort.objects.all()
    model_form = forms.RearPortForm
    filterset = filters.DeviceFilterSet
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


class DeviceBulkAddDeviceBayView(BulkComponentCreateView):
    parent_model = Device
    parent_field = 'device'
    form = forms.DeviceBayBulkCreateForm
    queryset = DeviceBay.objects.all()
    model_form = forms.DeviceBayForm
    filterset = filters.DeviceFilterSet
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


#
# Cables
#

class CableListView(ObjectListView):
    queryset = Cable.objects.prefetch_related(
        'termination_a', 'termination_b'
    )
    filterset = filters.CableFilterSet
    filterset_form = forms.CableFilterForm
    table = tables.CableTable
    action_buttons = ('import', 'export')


class CableView(ObjectView):
    queryset = Cable.objects.all()

    def get(self, request, pk):

        cable = get_object_or_404(self.queryset, pk=pk)

        return render(request, 'dcim/cable.html', {
            'cable': cable,
        })


class CableTraceView(ObjectView):
    """
    Trace a cable path beginning from the given termination.
    """
    additional_permissions = ['dcim.view_cable']

    def dispatch(self, request, *args, **kwargs):
        model = kwargs.pop('model')
        self.queryset = model.objects.all()

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):

        obj = get_object_or_404(self.queryset, pk=pk)
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


class CableCreateView(ObjectEditView):
    queryset = Cable.objects.all()
    template_name = 'dcim/cable_connect.html'
    default_return_url = 'dcim:cable_list'

    def dispatch(self, request, *args, **kwargs):

        # Set the model_form class based on the type of component being connected
        self.model_form = {
            'console-port': forms.ConnectCableToConsolePortForm,
            'console-server-port': forms.ConnectCableToConsoleServerPortForm,
            'power-port': forms.ConnectCableToPowerPortForm,
            'power-outlet': forms.ConnectCableToPowerOutletForm,
            'interface': forms.ConnectCableToInterfaceForm,
            'front-port': forms.ConnectCableToFrontPortForm,
            'rear-port': forms.ConnectCableToRearPortForm,
            'power-feed': forms.ConnectCableToPowerFeedForm,
            'circuit-termination': forms.ConnectCableToCircuitTerminationForm,
        }[kwargs.get('termination_b_type')]

        return super().dispatch(request, *args, **kwargs)

    def alter_obj(self, obj, request, url_args, url_kwargs):
        termination_a_type = url_kwargs.get('termination_a_type')
        termination_a_id = url_kwargs.get('termination_a_id')
        termination_b_type_name = url_kwargs.get('termination_b_type')
        self.termination_b_type = ContentType.objects.get(model=termination_b_type_name.replace('-', ''))

        # Initialize Cable termination attributes
        obj.termination_a = termination_a_type.objects.get(pk=termination_a_id)
        obj.termination_b_type = self.termination_b_type

        return obj

    def get(self, request, *args, **kwargs):
        obj = self.alter_obj(self.get_object(kwargs), request, args, kwargs)

        # Parse initial data manually to avoid setting field values as lists
        initial_data = {k: request.GET[k] for k in request.GET}

        # Set initial site and rack based on side A termination (if not already set)
        if 'termination_b_site' not in initial_data:
            initial_data['termination_b_site'] = getattr(obj.termination_a.parent, 'site', None)
        if 'termination_b_rack' not in initial_data:
            initial_data['termination_b_rack'] = getattr(obj.termination_a.parent, 'rack', None)

        form = self.model_form(instance=obj, initial=initial_data)

        return render(request, self.template_name, {
            'obj': obj,
            'obj_type': Cable._meta.verbose_name,
            'termination_b_type': self.termination_b_type.name,
            'form': form,
            'return_url': self.get_return_url(request, obj),
        })


class CableEditView(ObjectEditView):
    queryset = Cable.objects.all()
    model_form = forms.CableForm
    template_name = 'dcim/cable_edit.html'
    default_return_url = 'dcim:cable_list'


class CableDeleteView(ObjectDeleteView):
    queryset = Cable.objects.all()
    default_return_url = 'dcim:cable_list'


class CableBulkImportView(BulkImportView):
    queryset = Cable.objects.all()
    model_form = forms.CableCSVForm
    table = tables.CableTable
    default_return_url = 'dcim:cable_list'


class CableBulkEditView(BulkEditView):
    queryset = Cable.objects.prefetch_related('termination_a', 'termination_b')
    filterset = filters.CableFilterSet
    table = tables.CableTable
    form = forms.CableBulkEditForm
    default_return_url = 'dcim:cable_list'


class CableBulkDeleteView(BulkDeleteView):
    queryset = Cable.objects.prefetch_related('termination_a', 'termination_b')
    filterset = filters.CableFilterSet
    table = tables.CableTable
    default_return_url = 'dcim:cable_list'


#
# Connections
#

class ConsoleConnectionsListView(ObjectListView):
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


class PowerConnectionsListView(ObjectListView):
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


class InterfaceConnectionsListView(ObjectListView):
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

class InventoryItemListView(ObjectListView):
    queryset = InventoryItem.objects.prefetch_related('device', 'manufacturer')
    filterset = filters.InventoryItemFilterSet
    filterset_form = forms.InventoryItemFilterForm
    table = tables.InventoryItemTable
    action_buttons = ('import', 'export')


class InventoryItemEditView(ObjectEditView):
    queryset = InventoryItem.objects.all()
    model_form = forms.InventoryItemForm


class InventoryItemCreateView(ComponentCreateView):
    queryset = InventoryItem.objects.all()
    form = forms.InventoryItemCreateForm
    model_form = forms.InventoryItemForm
    template_name = 'dcim/device_component_add.html'


class InventoryItemDeleteView(ObjectDeleteView):
    queryset = InventoryItem.objects.all()


class InventoryItemBulkImportView(BulkImportView):
    queryset = InventoryItem.objects.all()
    model_form = forms.InventoryItemCSVForm
    table = tables.InventoryItemTable
    default_return_url = 'dcim:inventoryitem_list'


class InventoryItemBulkEditView(BulkEditView):
    queryset = InventoryItem.objects.prefetch_related('device', 'manufacturer')
    filterset = filters.InventoryItemFilterSet
    table = tables.InventoryItemTable
    form = forms.InventoryItemBulkEditForm
    default_return_url = 'dcim:inventoryitem_list'


class InventoryItemBulkDeleteView(BulkDeleteView):
    queryset = InventoryItem.objects.prefetch_related('device', 'manufacturer')
    table = tables.InventoryItemTable
    template_name = 'dcim/inventoryitem_bulk_delete.html'
    default_return_url = 'dcim:inventoryitem_list'


#
# Virtual chassis
#

class VirtualChassisListView(ObjectListView):
    queryset = VirtualChassis.objects.prefetch_related('master').annotate(member_count=Count('members'))
    table = tables.VirtualChassisTable
    filterset = filters.VirtualChassisFilterSet
    filterset_form = forms.VirtualChassisFilterForm
    action_buttons = ('export',)


class VirtualChassisView(ObjectView):
    queryset = VirtualChassis.objects.prefetch_related('members')

    def get(self, request, pk):
        virtualchassis = get_object_or_404(self.queryset, pk=pk)

        return render(request, 'dcim/virtualchassis.html', {
            'virtualchassis': virtualchassis,
        })


class VirtualChassisCreateView(ObjectPermissionRequiredMixin, View):
    queryset = VirtualChassis.objects.all()

    def get_required_permission(self):
        return 'dcim.add_virtualchassis'

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


class VirtualChassisEditView(ObjectPermissionRequiredMixin, GetReturnURLMixin, View):
    queryset = VirtualChassis.objects.all()

    def get_required_permission(self):
        return 'dcim.change_virtualchassis'

    def get(self, request, pk):

        virtual_chassis = get_object_or_404(self.queryset, pk=pk)
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

        virtual_chassis = get_object_or_404(self.queryset, pk=pk)
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


class VirtualChassisDeleteView(ObjectDeleteView):
    queryset = VirtualChassis.objects.all()
    default_return_url = 'dcim:device_list'


class VirtualChassisAddMemberView(ObjectPermissionRequiredMixin, GetReturnURLMixin, View):
    queryset = VirtualChassis.objects.all()

    def get_required_permission(self):
        return 'dcim.change_virtualchassis'

    def get(self, request, pk):

        virtual_chassis = get_object_or_404(self.queryset, pk=pk)

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

        virtual_chassis = get_object_or_404(self.queryset, pk=pk)

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


class VirtualChassisRemoveMemberView(ObjectPermissionRequiredMixin, GetReturnURLMixin, View):
    queryset = Device.objects.all()

    def get_required_permission(self):
        return 'dcim.change_device'

    def get(self, request, pk):

        device = get_object_or_404(self.queryset, pk=pk, virtual_chassis__isnull=False)
        form = ConfirmationForm(initial=request.GET)

        return render(request, 'dcim/virtualchassis_remove_member.html', {
            'device': device,
            'form': form,
            'return_url': self.get_return_url(request, device),
        })

    def post(self, request, pk):

        device = get_object_or_404(self.queryset, pk=pk, virtual_chassis__isnull=False)
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


class VirtualChassisBulkEditView(BulkEditView):
    queryset = VirtualChassis.objects.all()
    filterset = filters.VirtualChassisFilterSet
    table = tables.VirtualChassisTable
    form = forms.VirtualChassisBulkEditForm
    default_return_url = 'dcim:virtualchassis_list'


class VirtualChassisBulkDeleteView(BulkDeleteView):
    queryset = VirtualChassis.objects.all()
    filterset = filters.VirtualChassisFilterSet
    table = tables.VirtualChassisTable
    default_return_url = 'dcim:virtualchassis_list'


#
# Power panels
#

class PowerPanelListView(ObjectListView):
    queryset = PowerPanel.objects.prefetch_related(
        'site', 'rack_group'
    ).annotate(
        powerfeed_count=Count('powerfeeds')
    )
    filterset = filters.PowerPanelFilterSet
    filterset_form = forms.PowerPanelFilterForm
    table = tables.PowerPanelTable


class PowerPanelView(ObjectView):
    queryset = PowerPanel.objects.prefetch_related('site', 'rack_group')

    def get(self, request, pk):

        powerpanel = get_object_or_404(self.queryset, pk=pk)
        powerfeed_table = tables.PowerFeedTable(
            data=PowerFeed.objects.filter(power_panel=powerpanel).prefetch_related('rack'),
            orderable=False
        )
        powerfeed_table.exclude = ['power_panel']

        return render(request, 'dcim/powerpanel.html', {
            'powerpanel': powerpanel,
            'powerfeed_table': powerfeed_table,
        })


class PowerPanelEditView(ObjectEditView):
    queryset = PowerPanel.objects.all()
    model_form = forms.PowerPanelForm
    default_return_url = 'dcim:powerpanel_list'


class PowerPanelDeleteView(ObjectDeleteView):
    queryset = PowerPanel.objects.all()
    default_return_url = 'dcim:powerpanel_list'


class PowerPanelBulkImportView(BulkImportView):
    queryset = PowerPanel.objects.all()
    model_form = forms.PowerPanelCSVForm
    table = tables.PowerPanelTable
    default_return_url = 'dcim:powerpanel_list'


class PowerPanelBulkEditView(BulkEditView):
    queryset = PowerPanel.objects.prefetch_related('site', 'rack_group')
    filterset = filters.PowerPanelFilterSet
    table = tables.PowerPanelTable
    form = forms.PowerPanelBulkEditForm
    default_return_url = 'dcim:powerpanel_list'


class PowerPanelBulkDeleteView(BulkDeleteView):
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

class PowerFeedListView(ObjectListView):
    queryset = PowerFeed.objects.prefetch_related(
        'power_panel', 'rack'
    )
    filterset = filters.PowerFeedFilterSet
    filterset_form = forms.PowerFeedFilterForm
    table = tables.PowerFeedTable


class PowerFeedView(ObjectView):
    queryset = PowerFeed.objects.prefetch_related('power_panel', 'rack')

    def get(self, request, pk):

        powerfeed = get_object_or_404(self.queryset, pk=pk)

        return render(request, 'dcim/powerfeed.html', {
            'powerfeed': powerfeed,
        })


class PowerFeedEditView(ObjectEditView):
    queryset = PowerFeed.objects.all()
    model_form = forms.PowerFeedForm
    template_name = 'dcim/powerfeed_edit.html'
    default_return_url = 'dcim:powerfeed_list'


class PowerFeedDeleteView(ObjectDeleteView):
    queryset = PowerFeed.objects.all()
    default_return_url = 'dcim:powerfeed_list'


class PowerFeedBulkImportView(BulkImportView):
    queryset = PowerFeed.objects.all()
    model_form = forms.PowerFeedCSVForm
    table = tables.PowerFeedTable
    default_return_url = 'dcim:powerfeed_list'


class PowerFeedBulkEditView(BulkEditView):
    queryset = PowerFeed.objects.prefetch_related('power_panel', 'rack')
    filterset = filters.PowerFeedFilterSet
    table = tables.PowerFeedTable
    form = forms.PowerFeedBulkEditForm
    default_return_url = 'dcim:powerfeed_list'


class PowerFeedBulkDeleteView(BulkDeleteView):
    queryset = PowerFeed.objects.prefetch_related('power_panel', 'rack')
    filterset = filters.PowerFeedFilterSet
    table = tables.PowerFeedTable
    default_return_url = 'dcim:powerfeed_list'
