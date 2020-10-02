from collections import OrderedDict

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db.models import Count, F, Prefetch
from django.forms import ModelMultipleChoiceField, MultipleHiddenInput, modelformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.views.generic import View

from circuits.models import Circuit
from extras.models import Graph
from extras.views import ObjectConfigContextView
from ipam.models import IPAddress, Prefix, Service, VLAN
from ipam.tables import InterfaceIPAddressTable, InterfaceVLANTable
from secrets.models import Secret
from utilities.forms import ConfirmationForm
from utilities.paginator import EnhancedPaginator, get_paginate_count
from utilities.permissions import get_permission_for_model
from utilities.utils import csv_format, get_subquery
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
    template_name = 'dcim/bulk_disconnect.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create a new Form class from ConfirmationForm
        class _Form(ConfirmationForm):
            pk = ModelMultipleChoiceField(
                queryset=self.queryset,
                widget=MultipleHiddenInput()
            )

        self.form = _Form

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


class RegionDeleteView(ObjectDeleteView):
    queryset = Region.objects.all()


class RegionBulkImportView(BulkImportView):
    queryset = Region.objects.all()
    model_form = forms.RegionCSVForm
    table = tables.RegionTable


class RegionBulkDeleteView(BulkDeleteView):
    queryset = Region.objects.add_related_count(
        Region.objects.all(),
        Site,
        'region',
        'site_count',
        cumulative=True
    )
    filterset = filters.RegionFilterSet
    table = tables.RegionTable


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
        rack_groups = RackGroup.objects.add_related_count(
            RackGroup.objects.all(),
            Rack,
            'group',
            'rack_count',
            cumulative=True
        ).restrict(request.user, 'view').filter(site=site)
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


class SiteDeleteView(ObjectDeleteView):
    queryset = Site.objects.all()


class SiteBulkImportView(BulkImportView):
    queryset = Site.objects.all()
    model_form = forms.SiteCSVForm
    table = tables.SiteTable


class SiteBulkEditView(BulkEditView):
    queryset = Site.objects.prefetch_related('region', 'tenant')
    filterset = filters.SiteFilterSet
    table = tables.SiteTable
    form = forms.SiteBulkEditForm


class SiteBulkDeleteView(BulkDeleteView):
    queryset = Site.objects.prefetch_related('region', 'tenant')
    filterset = filters.SiteFilterSet
    table = tables.SiteTable


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


class RackGroupDeleteView(ObjectDeleteView):
    queryset = RackGroup.objects.all()


class RackGroupBulkImportView(BulkImportView):
    queryset = RackGroup.objects.all()
    model_form = forms.RackGroupCSVForm
    table = tables.RackGroupTable


class RackGroupBulkDeleteView(BulkDeleteView):
    queryset = RackGroup.objects.add_related_count(
        RackGroup.objects.all(),
        Rack,
        'group',
        'rack_count',
        cumulative=True
    ).prefetch_related('site')
    filterset = filters.RackGroupFilterSet
    table = tables.RackGroupTable


#
# Rack roles
#

class RackRoleListView(ObjectListView):
    queryset = RackRole.objects.annotate(rack_count=Count('racks')).order_by(*RackRole._meta.ordering)
    table = tables.RackRoleTable


class RackRoleEditView(ObjectEditView):
    queryset = RackRole.objects.all()
    model_form = forms.RackRoleForm


class RackRoleDeleteView(ObjectDeleteView):
    queryset = RackRole.objects.all()


class RackRoleBulkImportView(BulkImportView):
    queryset = RackRole.objects.all()
    model_form = forms.RackRoleCSVForm
    table = tables.RackRoleTable


class RackRoleBulkDeleteView(BulkDeleteView):
    queryset = RackRole.objects.annotate(rack_count=Count('racks')).order_by(*RackRole._meta.ordering)
    table = tables.RackRoleTable


#
# Racks
#

class RackListView(ObjectListView):
    queryset = Rack.objects.prefetch_related(
        'site', 'group', 'tenant', 'role', 'devices__device_type'
    ).annotate(
        device_count=Count('devices')
    ).order_by(*Rack._meta.ordering)
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

        # Determine ordering
        reverse = bool(request.GET.get('reverse', False))
        if reverse:
            racks = racks.reverse()

        # Pagination
        per_page = get_paginate_count(request)
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
            'reverse': reverse,
            'rack_face': rack_face,
            'filter_form': forms.RackElevationFilterForm(request.GET),
        })


class RackView(ObjectView):
    queryset = Rack.objects.prefetch_related('site__region', 'tenant__group', 'group', 'role')

    def get(self, request, pk):
        rack = get_object_or_404(self.queryset, pk=pk)

        # Get 0U and child devices located within the rack
        nonracked_devices = Device.objects.filter(
            rack=rack,
            position__isnull=True
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


class RackDeleteView(ObjectDeleteView):
    queryset = Rack.objects.all()


class RackBulkImportView(BulkImportView):
    queryset = Rack.objects.all()
    model_form = forms.RackCSVForm
    table = tables.RackTable


class RackBulkEditView(BulkEditView):
    queryset = Rack.objects.prefetch_related('site', 'group', 'tenant', 'role')
    filterset = filters.RackFilterSet
    table = tables.RackTable
    form = forms.RackBulkEditForm


class RackBulkDeleteView(BulkDeleteView):
    queryset = Rack.objects.prefetch_related('site', 'group', 'tenant', 'role')
    filterset = filters.RackFilterSet
    table = tables.RackTable


#
# Rack reservations
#

class RackReservationListView(ObjectListView):
    queryset = RackReservation.objects.prefetch_related('rack__site')
    filterset = filters.RackReservationFilterSet
    filterset_form = forms.RackReservationFilterForm
    table = tables.RackReservationTable


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

    def alter_obj(self, obj, request, args, kwargs):
        if not obj.pk:
            if 'rack' in request.GET:
                obj.rack = get_object_or_404(Rack, pk=request.GET.get('rack'))
            obj.user = request.user
        return obj


class RackReservationDeleteView(ObjectDeleteView):
    queryset = RackReservation.objects.all()


class RackReservationImportView(BulkImportView):
    queryset = RackReservation.objects.all()
    model_form = forms.RackReservationCSVForm
    table = tables.RackReservationTable

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


class RackReservationBulkDeleteView(BulkDeleteView):
    queryset = RackReservation.objects.prefetch_related('rack', 'user')
    filterset = filters.RackReservationFilterSet
    table = tables.RackReservationTable


#
# Manufacturers
#

class ManufacturerListView(ObjectListView):
    queryset = Manufacturer.objects.annotate(
        devicetype_count=get_subquery(DeviceType, 'manufacturer'),
        inventoryitem_count=get_subquery(InventoryItem, 'manufacturer'),
        platform_count=get_subquery(Platform, 'manufacturer')
    )
    table = tables.ManufacturerTable


class ManufacturerEditView(ObjectEditView):
    queryset = Manufacturer.objects.all()
    model_form = forms.ManufacturerForm


class ManufacturerDeleteView(ObjectDeleteView):
    queryset = Manufacturer.objects.all()


class ManufacturerBulkImportView(BulkImportView):
    queryset = Manufacturer.objects.all()
    model_form = forms.ManufacturerCSVForm
    table = tables.ManufacturerTable


class ManufacturerBulkDeleteView(BulkDeleteView):
    queryset = Manufacturer.objects.annotate(
        devicetype_count=Count('device_types')
    ).order_by(*Manufacturer._meta.ordering)
    table = tables.ManufacturerTable


#
# Device types
#

class DeviceTypeListView(ObjectListView):
    queryset = DeviceType.objects.prefetch_related('manufacturer').annotate(
        instance_count=Count('instances')
    ).order_by(*DeviceType._meta.ordering)
    filterset = filters.DeviceTypeFilterSet
    filterset_form = forms.DeviceTypeFilterForm
    table = tables.DeviceTypeTable


class DeviceTypeView(ObjectView):
    queryset = DeviceType.objects.prefetch_related('manufacturer')

    def get(self, request, pk):

        devicetype = get_object_or_404(self.queryset, pk=pk)
        instance_count = Device.objects.restrict(request.user).filter(device_type=devicetype).count()

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
            'instance_count': instance_count,
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


class DeviceTypeDeleteView(ObjectDeleteView):
    queryset = DeviceType.objects.all()


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


class DeviceTypeBulkEditView(BulkEditView):
    queryset = DeviceType.objects.prefetch_related('manufacturer').annotate(
        instance_count=Count('instances')
    ).order_by(*DeviceType._meta.ordering)
    filterset = filters.DeviceTypeFilterSet
    table = tables.DeviceTypeTable
    form = forms.DeviceTypeBulkEditForm


class DeviceTypeBulkDeleteView(BulkDeleteView):
    queryset = DeviceType.objects.prefetch_related('manufacturer').annotate(
        instance_count=Count('instances')
    ).order_by(*DeviceType._meta.ordering)
    filterset = filters.DeviceTypeFilterSet
    table = tables.DeviceTypeTable


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


class ConsolePortTemplateBulkRenameView(BulkRenameView):
    queryset = ConsolePortTemplate.objects.all()


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


class ConsoleServerPortTemplateBulkRenameView(BulkRenameView):
    queryset = ConsoleServerPortTemplate.objects.all()


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


class PowerPortTemplateBulkRenameView(BulkRenameView):
    queryset = PowerPortTemplate.objects.all()


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


class PowerOutletTemplateBulkRenameView(BulkRenameView):
    queryset = PowerOutletTemplate.objects.all()


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


class InterfaceTemplateBulkRenameView(BulkRenameView):
    queryset = InterfaceTemplate.objects.all()


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


class FrontPortTemplateBulkRenameView(BulkRenameView):
    queryset = FrontPortTemplate.objects.all()


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


class RearPortTemplateBulkRenameView(BulkRenameView):
    queryset = RearPortTemplate.objects.all()


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


class DeviceBayTemplateBulkEditView(BulkEditView):
    queryset = DeviceBayTemplate.objects.all()
    table = tables.DeviceBayTemplateTable
    form = forms.DeviceBayTemplateBulkEditForm


class DeviceBayTemplateBulkRenameView(BulkRenameView):
    queryset = DeviceBayTemplate.objects.all()


class DeviceBayTemplateBulkDeleteView(BulkDeleteView):
    queryset = DeviceBayTemplate.objects.all()
    table = tables.DeviceBayTemplateTable


#
# Device roles
#

class DeviceRoleListView(ObjectListView):
    queryset = DeviceRole.objects.annotate(
        device_count=get_subquery(Device, 'device_role'),
        vm_count=get_subquery(VirtualMachine, 'role')
    )
    table = tables.DeviceRoleTable


class DeviceRoleEditView(ObjectEditView):
    queryset = DeviceRole.objects.all()
    model_form = forms.DeviceRoleForm


class DeviceRoleDeleteView(ObjectDeleteView):
    queryset = DeviceRole.objects.all()


class DeviceRoleBulkImportView(BulkImportView):
    queryset = DeviceRole.objects.all()
    model_form = forms.DeviceRoleCSVForm
    table = tables.DeviceRoleTable


class DeviceRoleBulkDeleteView(BulkDeleteView):
    queryset = DeviceRole.objects.all()
    table = tables.DeviceRoleTable


#
# Platforms
#

class PlatformListView(ObjectListView):
    queryset = Platform.objects.annotate(
        device_count=get_subquery(Device, 'platform'),
        vm_count=get_subquery(VirtualMachine, 'platform')
    )
    table = tables.PlatformTable


class PlatformEditView(ObjectEditView):
    queryset = Platform.objects.all()
    model_form = forms.PlatformForm


class PlatformDeleteView(ObjectDeleteView):
    queryset = Platform.objects.all()


class PlatformBulkImportView(BulkImportView):
    queryset = Platform.objects.all()
    model_form = forms.PlatformCSVForm
    table = tables.PlatformTable


class PlatformBulkDeleteView(BulkDeleteView):
    queryset = Platform.objects.all()
    table = tables.PlatformTable


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
        consoleports = ConsolePort.objects.restrict(request.user, 'view').filter(device=device).prefetch_related(
            'connected_endpoint__device', 'cable',
        )

        # Console server ports
        consoleserverports = ConsoleServerPort.objects.restrict(request.user, 'view').filter(
            device=device
        ).prefetch_related(
            'connected_endpoint__device', 'cable',
        )

        # Power ports
        powerports = PowerPort.objects.restrict(request.user, 'view').filter(device=device).prefetch_related(
            '_connected_poweroutlet__device', 'cable',
        )

        # Power outlets
        poweroutlets = PowerOutlet.objects.restrict(request.user, 'view').filter(device=device).prefetch_related(
            'connected_endpoint__device', 'cable', 'power_port',
        )

        # Interfaces
        interfaces = device.vc_interfaces.restrict(request.user, 'view').prefetch_related(
            Prefetch('ip_addresses', queryset=IPAddress.objects.restrict(request.user)),
            Prefetch('member_interfaces', queryset=Interface.objects.restrict(request.user)),
            'lag', '_connected_interface__device', '_connected_circuittermination__circuit', 'cable',
            'cable__termination_a', 'cable__termination_b', 'tags'
        )

        # Front ports
        frontports = FrontPort.objects.restrict(request.user, 'view').filter(device=device).prefetch_related(
            'rear_port', 'cable',
        )

        # Rear ports
        rearports = RearPort.objects.restrict(request.user, 'view').filter(device=device).prefetch_related('cable')

        # Device bays
        devicebays = DeviceBay.objects.restrict(request.user, 'view').filter(device=device).prefetch_related(
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
            'consoleports': consoleports,
            'consoleserverports': consoleserverports,
            'powerports': powerports,
            'poweroutlets': poweroutlets,
            'interfaces': interfaces,
            'devicebays': devicebays,
            'frontports': frontports,
            'rearports': rearports,
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


class DeviceDeleteView(ObjectDeleteView):
    queryset = Device.objects.all()


class DeviceBulkImportView(BulkImportView):
    queryset = Device.objects.all()
    model_form = forms.DeviceCSVForm
    table = tables.DeviceImportTable
    template_name = 'dcim/device_import.html'


class ChildDeviceBulkImportView(BulkImportView):
    queryset = Device.objects.all()
    model_form = forms.ChildDeviceCSVForm
    table = tables.DeviceImportTable
    template_name = 'dcim/device_import_child.html'

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


class DeviceBulkDeleteView(BulkDeleteView):
    queryset = Device.objects.prefetch_related('tenant', 'site', 'rack', 'device_role', 'device_type__manufacturer')
    filterset = filters.DeviceFilterSet
    table = tables.DeviceTable


#
# Console ports
#

class ConsolePortListView(ObjectListView):
    queryset = ConsolePort.objects.prefetch_related('device', 'cable')
    filterset = filters.ConsolePortFilterSet
    filterset_form = forms.ConsolePortFilterForm
    table = tables.ConsolePortTable
    action_buttons = ('import', 'export')


class ConsolePortView(ObjectView):
    queryset = ConsolePort.objects.all()


class ConsolePortCreateView(ComponentCreateView):
    queryset = ConsolePort.objects.all()
    form = forms.ConsolePortCreateForm
    model_form = forms.ConsolePortForm
    template_name = 'dcim/device_component_add.html'


class ConsolePortEditView(ObjectEditView):
    queryset = ConsolePort.objects.all()
    model_form = forms.ConsolePortForm
    template_name = 'dcim/device_component_edit.html'


class ConsolePortDeleteView(ObjectDeleteView):
    queryset = ConsolePort.objects.all()


class ConsolePortBulkImportView(BulkImportView):
    queryset = ConsolePort.objects.all()
    model_form = forms.ConsolePortCSVForm
    table = tables.ConsolePortTable


class ConsolePortBulkEditView(BulkEditView):
    queryset = ConsolePort.objects.all()
    filterset = filters.ConsolePortFilterSet
    table = tables.ConsolePortTable
    form = forms.ConsolePortBulkEditForm


class ConsolePortBulkRenameView(BulkRenameView):
    queryset = ConsolePort.objects.all()


class ConsolePortBulkDisconnectView(BulkDisconnectView):
    queryset = ConsolePort.objects.all()


class ConsolePortBulkDeleteView(BulkDeleteView):
    queryset = ConsolePort.objects.all()
    filterset = filters.ConsolePortFilterSet
    table = tables.ConsolePortTable


#
# Console server ports
#

class ConsoleServerPortListView(ObjectListView):
    queryset = ConsoleServerPort.objects.prefetch_related('device', 'cable')
    filterset = filters.ConsoleServerPortFilterSet
    filterset_form = forms.ConsoleServerPortFilterForm
    table = tables.ConsoleServerPortTable
    action_buttons = ('import', 'export')


class ConsoleServerPortView(ObjectView):
    queryset = ConsoleServerPort.objects.all()


class ConsoleServerPortCreateView(ComponentCreateView):
    queryset = ConsoleServerPort.objects.all()
    form = forms.ConsoleServerPortCreateForm
    model_form = forms.ConsoleServerPortForm
    template_name = 'dcim/device_component_add.html'


class ConsoleServerPortEditView(ObjectEditView):
    queryset = ConsoleServerPort.objects.all()
    model_form = forms.ConsoleServerPortForm
    template_name = 'dcim/device_component_edit.html'


class ConsoleServerPortDeleteView(ObjectDeleteView):
    queryset = ConsoleServerPort.objects.all()


class ConsoleServerPortBulkImportView(BulkImportView):
    queryset = ConsoleServerPort.objects.all()
    model_form = forms.ConsoleServerPortCSVForm
    table = tables.ConsoleServerPortTable


class ConsoleServerPortBulkEditView(BulkEditView):
    queryset = ConsoleServerPort.objects.all()
    filterset = filters.ConsoleServerPortFilterSet
    table = tables.ConsoleServerPortTable
    form = forms.ConsoleServerPortBulkEditForm


class ConsoleServerPortBulkRenameView(BulkRenameView):
    queryset = ConsoleServerPort.objects.all()


class ConsoleServerPortBulkDisconnectView(BulkDisconnectView):
    queryset = ConsoleServerPort.objects.all()


class ConsoleServerPortBulkDeleteView(BulkDeleteView):
    queryset = ConsoleServerPort.objects.all()
    filterset = filters.ConsoleServerPortFilterSet
    table = tables.ConsoleServerPortTable


#
# Power ports
#

class PowerPortListView(ObjectListView):
    queryset = PowerPort.objects.prefetch_related('device', 'cable')
    filterset = filters.PowerPortFilterSet
    filterset_form = forms.PowerPortFilterForm
    table = tables.PowerPortTable
    action_buttons = ('import', 'export')


class PowerPortView(ObjectView):
    queryset = PowerPort.objects.all()


class PowerPortCreateView(ComponentCreateView):
    queryset = PowerPort.objects.all()
    form = forms.PowerPortCreateForm
    model_form = forms.PowerPortForm
    template_name = 'dcim/device_component_add.html'


class PowerPortEditView(ObjectEditView):
    queryset = PowerPort.objects.all()
    model_form = forms.PowerPortForm
    template_name = 'dcim/device_component_edit.html'


class PowerPortDeleteView(ObjectDeleteView):
    queryset = PowerPort.objects.all()


class PowerPortBulkImportView(BulkImportView):
    queryset = PowerPort.objects.all()
    model_form = forms.PowerPortCSVForm
    table = tables.PowerPortTable


class PowerPortBulkEditView(BulkEditView):
    queryset = PowerPort.objects.all()
    filterset = filters.PowerPortFilterSet
    table = tables.PowerPortTable
    form = forms.PowerPortBulkEditForm


class PowerPortBulkRenameView(BulkRenameView):
    queryset = PowerPort.objects.all()


class PowerPortBulkDisconnectView(BulkDisconnectView):
    queryset = PowerPort.objects.all()


class PowerPortBulkDeleteView(BulkDeleteView):
    queryset = PowerPort.objects.all()
    filterset = filters.PowerPortFilterSet
    table = tables.PowerPortTable


#
# Power outlets
#

class PowerOutletListView(ObjectListView):
    queryset = PowerOutlet.objects.prefetch_related('device', 'cable')
    filterset = filters.PowerOutletFilterSet
    filterset_form = forms.PowerOutletFilterForm
    table = tables.PowerOutletTable
    action_buttons = ('import', 'export')


class PowerOutletView(ObjectView):
    queryset = PowerOutlet.objects.all()


class PowerOutletCreateView(ComponentCreateView):
    queryset = PowerOutlet.objects.all()
    form = forms.PowerOutletCreateForm
    model_form = forms.PowerOutletForm
    template_name = 'dcim/device_component_add.html'


class PowerOutletEditView(ObjectEditView):
    queryset = PowerOutlet.objects.all()
    model_form = forms.PowerOutletForm
    template_name = 'dcim/device_component_edit.html'


class PowerOutletDeleteView(ObjectDeleteView):
    queryset = PowerOutlet.objects.all()


class PowerOutletBulkImportView(BulkImportView):
    queryset = PowerOutlet.objects.all()
    model_form = forms.PowerOutletCSVForm
    table = tables.PowerOutletTable


class PowerOutletBulkEditView(BulkEditView):
    queryset = PowerOutlet.objects.all()
    filterset = filters.PowerOutletFilterSet
    table = tables.PowerOutletTable
    form = forms.PowerOutletBulkEditForm


class PowerOutletBulkRenameView(BulkRenameView):
    queryset = PowerOutlet.objects.all()


class PowerOutletBulkDisconnectView(BulkDisconnectView):
    queryset = PowerOutlet.objects.all()


class PowerOutletBulkDeleteView(BulkDeleteView):
    queryset = PowerOutlet.objects.all()
    filterset = filters.PowerOutletFilterSet
    table = tables.PowerOutletTable


#
# Interfaces
#

class InterfaceListView(ObjectListView):
    queryset = Interface.objects.prefetch_related('device', 'cable')
    filterset = filters.InterfaceFilterSet
    filterset_form = forms.InterfaceFilterForm
    table = tables.InterfaceTable
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
        for vlan in interface.tagged_vlans.restrict(request.user).prefetch_related('site', 'group', 'tenant', 'role'):
            vlan.tagged = True
            vlans.append(vlan)
        vlan_table = InterfaceVLANTable(
            interface=interface,
            data=vlans,
            orderable=False
        )

        return render(request, 'dcim/interface.html', {
            'instance': interface,
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
    table = tables.InterfaceTable


class InterfaceBulkEditView(BulkEditView):
    queryset = Interface.objects.all()
    filterset = filters.InterfaceFilterSet
    table = tables.InterfaceTable
    form = forms.InterfaceBulkEditForm


class InterfaceBulkRenameView(BulkRenameView):
    queryset = Interface.objects.all()


class InterfaceBulkDisconnectView(BulkDisconnectView):
    queryset = Interface.objects.all()


class InterfaceBulkDeleteView(BulkDeleteView):
    queryset = Interface.objects.all()
    filterset = filters.InterfaceFilterSet
    table = tables.InterfaceTable


#
# Front ports
#

class FrontPortListView(ObjectListView):
    queryset = FrontPort.objects.prefetch_related('device', 'cable')
    filterset = filters.FrontPortFilterSet
    filterset_form = forms.FrontPortFilterForm
    table = tables.FrontPortTable
    action_buttons = ('import', 'export')


class FrontPortView(ObjectView):
    queryset = FrontPort.objects.all()


class FrontPortCreateView(ComponentCreateView):
    queryset = FrontPort.objects.all()
    form = forms.FrontPortCreateForm
    model_form = forms.FrontPortForm
    template_name = 'dcim/device_component_add.html'


class FrontPortEditView(ObjectEditView):
    queryset = FrontPort.objects.all()
    model_form = forms.FrontPortForm
    template_name = 'dcim/device_component_edit.html'


class FrontPortDeleteView(ObjectDeleteView):
    queryset = FrontPort.objects.all()


class FrontPortBulkImportView(BulkImportView):
    queryset = FrontPort.objects.all()
    model_form = forms.FrontPortCSVForm
    table = tables.FrontPortTable


class FrontPortBulkEditView(BulkEditView):
    queryset = FrontPort.objects.all()
    filterset = filters.FrontPortFilterSet
    table = tables.FrontPortTable
    form = forms.FrontPortBulkEditForm


class FrontPortBulkRenameView(BulkRenameView):
    queryset = FrontPort.objects.all()


class FrontPortBulkDisconnectView(BulkDisconnectView):
    queryset = FrontPort.objects.all()


class FrontPortBulkDeleteView(BulkDeleteView):
    queryset = FrontPort.objects.all()
    filterset = filters.FrontPortFilterSet
    table = tables.FrontPortTable


#
# Rear ports
#

class RearPortListView(ObjectListView):
    queryset = RearPort.objects.prefetch_related('device', 'cable')
    filterset = filters.RearPortFilterSet
    filterset_form = forms.RearPortFilterForm
    table = tables.RearPortTable
    action_buttons = ('import', 'export')


class RearPortView(ObjectView):
    queryset = RearPort.objects.all()


class RearPortCreateView(ComponentCreateView):
    queryset = RearPort.objects.all()
    form = forms.RearPortCreateForm
    model_form = forms.RearPortForm
    template_name = 'dcim/device_component_add.html'


class RearPortEditView(ObjectEditView):
    queryset = RearPort.objects.all()
    model_form = forms.RearPortForm
    template_name = 'dcim/device_component_edit.html'


class RearPortDeleteView(ObjectDeleteView):
    queryset = RearPort.objects.all()


class RearPortBulkImportView(BulkImportView):
    queryset = RearPort.objects.all()
    model_form = forms.RearPortCSVForm
    table = tables.RearPortTable


class RearPortBulkEditView(BulkEditView):
    queryset = RearPort.objects.all()
    filterset = filters.RearPortFilterSet
    table = tables.RearPortTable
    form = forms.RearPortBulkEditForm


class RearPortBulkRenameView(BulkRenameView):
    queryset = RearPort.objects.all()


class RearPortBulkDisconnectView(BulkDisconnectView):
    queryset = RearPort.objects.all()


class RearPortBulkDeleteView(BulkDeleteView):
    queryset = RearPort.objects.all()
    filterset = filters.RearPortFilterSet
    table = tables.RearPortTable


#
# Device bays
#

class DeviceBayListView(ObjectListView):
    queryset = DeviceBay.objects.prefetch_related('device', 'installed_device')
    filterset = filters.DeviceBayFilterSet
    filterset_form = forms.DeviceBayFilterForm
    table = tables.DeviceBayTable
    action_buttons = ('import', 'export')


class DeviceBayView(ObjectView):
    queryset = DeviceBay.objects.all()


class DeviceBayCreateView(ComponentCreateView):
    queryset = DeviceBay.objects.all()
    form = forms.DeviceBayCreateForm
    model_form = forms.DeviceBayForm
    template_name = 'dcim/device_component_add.html'


class DeviceBayEditView(ObjectEditView):
    queryset = DeviceBay.objects.all()
    model_form = forms.DeviceBayForm
    template_name = 'dcim/device_component_edit.html'


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
    table = tables.DeviceBayTable


class DeviceBayBulkEditView(BulkEditView):
    queryset = DeviceBay.objects.all()
    filterset = filters.DeviceBayFilterSet
    table = tables.DeviceBayTable
    form = forms.DeviceBayBulkEditForm


class DeviceBayBulkRenameView(BulkRenameView):
    queryset = DeviceBay.objects.all()


class DeviceBayBulkDeleteView(BulkDeleteView):
    queryset = DeviceBay.objects.all()
    filterset = filters.DeviceBayFilterSet
    table = tables.DeviceBayTable


#
# Inventory items
#

class InventoryItemListView(ObjectListView):
    queryset = InventoryItem.objects.prefetch_related('device', 'manufacturer')
    filterset = filters.InventoryItemFilterSet
    filterset_form = forms.InventoryItemFilterForm
    table = tables.InventoryItemTable
    action_buttons = ('import', 'export')


class InventoryItemView(ObjectView):
    queryset = InventoryItem.objects.all()


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


class InventoryItemBulkEditView(BulkEditView):
    queryset = InventoryItem.objects.prefetch_related('device', 'manufacturer')
    filterset = filters.InventoryItemFilterSet
    table = tables.InventoryItemTable
    form = forms.InventoryItemBulkEditForm


class InventoryItemBulkRenameView(BulkRenameView):
    queryset = InventoryItem.objects.all()


class InventoryItemBulkDeleteView(BulkDeleteView):
    queryset = InventoryItem.objects.prefetch_related('device', 'manufacturer')
    table = tables.InventoryItemTable
    template_name = 'dcim/inventoryitem_bulk_delete.html'


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


class DeviceBulkAddInventoryItemView(BulkComponentCreateView):
    parent_model = Device
    parent_field = 'device'
    form = forms.InventoryItemBulkCreateForm
    queryset = InventoryItem.objects.all()
    model_form = forms.InventoryItemForm
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
        path, split_ends, position_stack = obj.trace()
        total_length = sum(
            [entry[1]._abs_length for entry in path if entry[1] and entry[1]._abs_length]
        )

        return render(request, 'dcim/cable_trace.html', {
            'obj': obj,
            'trace': path,
            'split_ends': split_ends,
            'position_stack': position_stack,
            'total_length': total_length,
        })


class CableCreateView(ObjectEditView):
    queryset = Cable.objects.all()
    template_name = 'dcim/cable_connect.html'

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


class CableDeleteView(ObjectDeleteView):
    queryset = Cable.objects.all()


class CableBulkImportView(BulkImportView):
    queryset = Cable.objects.all()
    model_form = forms.CableCSVForm
    table = tables.CableTable


class CableBulkEditView(BulkEditView):
    queryset = Cable.objects.prefetch_related('termination_a', 'termination_b')
    filterset = filters.CableFilterSet
    table = tables.CableTable
    form = forms.CableBulkEditForm


class CableBulkDeleteView(BulkDeleteView):
    queryset = Cable.objects.prefetch_related('termination_a', 'termination_b')
    filterset = filters.CableFilterSet
    table = tables.CableTable


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
# Virtual chassis
#

class VirtualChassisListView(ObjectListView):
    queryset = VirtualChassis.objects.prefetch_related('master').annotate(
        member_count=Count('members', distinct=True)
    ).order_by(*VirtualChassis._meta.ordering)
    table = tables.VirtualChassisTable
    filterset = filters.VirtualChassisFilterSet
    filterset_form = forms.VirtualChassisFilterForm


class VirtualChassisView(ObjectView):
    queryset = VirtualChassis.objects.all()

    def get(self, request, pk):
        virtualchassis = get_object_or_404(self.queryset, pk=pk)
        members = Device.objects.restrict(request.user).filter(virtual_chassis=virtualchassis)

        return render(request, 'dcim/virtualchassis.html', {
            'virtualchassis': virtualchassis,
            'members': members,
        })


class VirtualChassisCreateView(ObjectEditView):
    queryset = VirtualChassis.objects.all()
    model_form = forms.VirtualChassisCreateForm
    template_name = 'dcim/virtualchassis_add.html'


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

            return redirect(virtual_chassis.get_absolute_url())

        return render(request, 'dcim/virtualchassis_edit.html', {
            'vc_form': vc_form,
            'formset': formset,
            'return_url': self.get_return_url(request, virtual_chassis),
        })


class VirtualChassisDeleteView(ObjectDeleteView):
    queryset = VirtualChassis.objects.all()


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


class VirtualChassisBulkImportView(BulkImportView):
    queryset = VirtualChassis.objects.all()
    model_form = forms.VirtualChassisCSVForm
    table = tables.VirtualChassisTable


class VirtualChassisBulkEditView(BulkEditView):
    queryset = VirtualChassis.objects.all()
    filterset = filters.VirtualChassisFilterSet
    table = tables.VirtualChassisTable
    form = forms.VirtualChassisBulkEditForm


class VirtualChassisBulkDeleteView(BulkDeleteView):
    queryset = VirtualChassis.objects.all()
    filterset = filters.VirtualChassisFilterSet
    table = tables.VirtualChassisTable


#
# Power panels
#

class PowerPanelListView(ObjectListView):
    queryset = PowerPanel.objects.prefetch_related(
        'site', 'rack_group'
    ).annotate(
        powerfeed_count=Count('powerfeeds')
    ).order_by(*PowerPanel._meta.ordering)
    filterset = filters.PowerPanelFilterSet
    filterset_form = forms.PowerPanelFilterForm
    table = tables.PowerPanelTable


class PowerPanelView(ObjectView):
    queryset = PowerPanel.objects.prefetch_related('site', 'rack_group')

    def get(self, request, pk):

        powerpanel = get_object_or_404(self.queryset, pk=pk)
        power_feeds = PowerFeed.objects.restrict(request.user).filter(power_panel=powerpanel).prefetch_related('rack')
        powerfeed_table = tables.PowerFeedTable(
            data=power_feeds,
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


class PowerPanelDeleteView(ObjectDeleteView):
    queryset = PowerPanel.objects.all()


class PowerPanelBulkImportView(BulkImportView):
    queryset = PowerPanel.objects.all()
    model_form = forms.PowerPanelCSVForm
    table = tables.PowerPanelTable


class PowerPanelBulkEditView(BulkEditView):
    queryset = PowerPanel.objects.prefetch_related('site', 'rack_group')
    filterset = filters.PowerPanelFilterSet
    table = tables.PowerPanelTable
    form = forms.PowerPanelBulkEditForm


class PowerPanelBulkDeleteView(BulkDeleteView):
    queryset = PowerPanel.objects.prefetch_related(
        'site', 'rack_group'
    ).annotate(
        rack_count=Count('powerfeeds')
    ).order_by(*PowerPanel._meta.ordering)
    filterset = filters.PowerPanelFilterSet
    table = tables.PowerPanelTable


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


class PowerFeedDeleteView(ObjectDeleteView):
    queryset = PowerFeed.objects.all()


class PowerFeedBulkImportView(BulkImportView):
    queryset = PowerFeed.objects.all()
    model_form = forms.PowerFeedCSVForm
    table = tables.PowerFeedTable


class PowerFeedBulkEditView(BulkEditView):
    queryset = PowerFeed.objects.prefetch_related('power_panel', 'rack')
    filterset = filters.PowerFeedFilterSet
    table = tables.PowerFeedTable
    form = forms.PowerFeedBulkEditForm


class PowerFeedBulkDeleteView(BulkDeleteView):
    queryset = PowerFeed.objects.prefetch_related('power_panel', 'rack')
    filterset = filters.PowerFeedFilterSet
    table = tables.PowerFeedTable
