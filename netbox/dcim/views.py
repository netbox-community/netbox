from collections import OrderedDict

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db.models import Prefetch
from django.forms import ModelMultipleChoiceField, MultipleHiddenInput, modelformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.views.generic import View

from circuits.models import Circuit
from extras.views import ObjectConfigContextView
from ipam.models import ASN, IPAddress, Prefix, Service, VLAN
from ipam.tables import AssignedIPAddressesTable, InterfaceVLANTable
from netbox.views import generic
from utilities.forms import ConfirmationForm
from utilities.paginator import EnhancedPaginator, get_paginate_count
from utilities.permissions import get_permission_for_model
from utilities.tables import paginate_table
from utilities.utils import count_related
from utilities.views import GetReturnURLMixin, ObjectPermissionRequiredMixin
from virtualization.models import VirtualMachine
from . import filtersets, forms, tables
from .choices import DeviceFaceChoices
from .constants import NONCONNECTABLE_IFACE_TYPES
from .models import *


class DeviceComponentsView(generic.ObjectChildrenView):
    queryset = Device.objects.all()

    def get_children(self, request, parent):
        return self.child_model.objects.restrict(request.user, 'view').filter(device=parent)

    def get_extra_context(self, request, instance):
        return {
            'active_tab': f"{self.child_model._meta.verbose_name_plural.replace(' ', '-')}",
        }


class DeviceTypeComponentsView(DeviceComponentsView):
    queryset = DeviceType.objects.all()
    template_name = 'dcim/devicetype/component_templates.html'
    viewname = None  # Used for return_url resolution

    def get_children(self, request, parent):
        return self.child_model.objects.restrict(request.user, 'view').filter(device_type=parent)

    def get_extra_context(self, request, instance):
        if self.viewname:
            return_url = reverse(self.viewname, kwargs={'pk': instance.pk})
        else:
            return_url = instance.get_absolute_url()
        return {
            'active_tab': f"{self.child_model._meta.verbose_name_plural.replace(' ', '-')}",
            'return_url': return_url,
        }


class ModuleTypeComponentsView(DeviceComponentsView):
    queryset = ModuleType.objects.all()
    template_name = 'dcim/moduletype/component_templates.html'

    def get_children(self, request, parent):
        return self.child_model.objects.restrict(request.user, 'view').filter(module_type=parent)


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

class RegionListView(generic.ObjectListView):
    queryset = Region.objects.add_related_count(
        Region.objects.all(),
        Site,
        'region',
        'site_count',
        cumulative=True
    )
    filterset = filtersets.RegionFilterSet
    filterset_form = forms.RegionFilterForm
    table = tables.RegionTable


class RegionView(generic.ObjectView):
    queryset = Region.objects.all()

    def get_extra_context(self, request, instance):
        child_regions = Region.objects.add_related_count(
            Region.objects.all(),
            Site,
            'region',
            'site_count',
            cumulative=True
        ).restrict(request.user, 'view').filter(
            parent__in=instance.get_descendants(include_self=True)
        )
        child_regions_table = tables.RegionTable(child_regions)
        child_regions_table.columns.hide('actions')

        sites = Site.objects.restrict(request.user, 'view').filter(
            region=instance
        )
        sites_table = tables.SiteTable(sites, exclude=('region',))
        paginate_table(sites_table, request)

        return {
            'child_regions_table': child_regions_table,
            'sites_table': sites_table,
        }


class RegionEditView(generic.ObjectEditView):
    queryset = Region.objects.all()
    model_form = forms.RegionForm


class RegionDeleteView(generic.ObjectDeleteView):
    queryset = Region.objects.all()


class RegionBulkImportView(generic.BulkImportView):
    queryset = Region.objects.all()
    model_form = forms.RegionCSVForm
    table = tables.RegionTable


class RegionBulkEditView(generic.BulkEditView):
    queryset = Region.objects.add_related_count(
        Region.objects.all(),
        Site,
        'region',
        'site_count',
        cumulative=True
    )
    filterset = filtersets.RegionFilterSet
    table = tables.RegionTable
    form = forms.RegionBulkEditForm


class RegionBulkDeleteView(generic.BulkDeleteView):
    queryset = Region.objects.add_related_count(
        Region.objects.all(),
        Site,
        'region',
        'site_count',
        cumulative=True
    )
    filterset = filtersets.RegionFilterSet
    table = tables.RegionTable


#
# Site groups
#

class SiteGroupListView(generic.ObjectListView):
    queryset = SiteGroup.objects.add_related_count(
        SiteGroup.objects.all(),
        Site,
        'group',
        'site_count',
        cumulative=True
    )
    filterset = filtersets.SiteGroupFilterSet
    filterset_form = forms.SiteGroupFilterForm
    table = tables.SiteGroupTable


class SiteGroupView(generic.ObjectView):
    queryset = SiteGroup.objects.all()

    def get_extra_context(self, request, instance):
        child_groups = SiteGroup.objects.add_related_count(
            SiteGroup.objects.all(),
            Site,
            'group',
            'site_count',
            cumulative=True
        ).restrict(request.user, 'view').filter(
            parent__in=instance.get_descendants(include_self=True)
        )
        child_groups_table = tables.SiteGroupTable(child_groups)
        child_groups_table.columns.hide('actions')

        sites = Site.objects.restrict(request.user, 'view').filter(
            group=instance
        )
        sites_table = tables.SiteTable(sites, exclude=('group',))
        paginate_table(sites_table, request)

        return {
            'child_groups_table': child_groups_table,
            'sites_table': sites_table,
        }


class SiteGroupEditView(generic.ObjectEditView):
    queryset = SiteGroup.objects.all()
    model_form = forms.SiteGroupForm


class SiteGroupDeleteView(generic.ObjectDeleteView):
    queryset = SiteGroup.objects.all()


class SiteGroupBulkImportView(generic.BulkImportView):
    queryset = SiteGroup.objects.all()
    model_form = forms.SiteGroupCSVForm
    table = tables.SiteGroupTable


class SiteGroupBulkEditView(generic.BulkEditView):
    queryset = SiteGroup.objects.add_related_count(
        SiteGroup.objects.all(),
        Site,
        'group',
        'site_count',
        cumulative=True
    )
    filterset = filtersets.SiteGroupFilterSet
    table = tables.SiteGroupTable
    form = forms.SiteGroupBulkEditForm


class SiteGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = SiteGroup.objects.add_related_count(
        SiteGroup.objects.all(),
        Site,
        'group',
        'site_count',
        cumulative=True
    )
    filterset = filtersets.SiteGroupFilterSet
    table = tables.SiteGroupTable


#
# Sites
#

class SiteListView(generic.ObjectListView):
    queryset = Site.objects.all()
    filterset = filtersets.SiteFilterSet
    filterset_form = forms.SiteFilterForm
    table = tables.SiteTable


class SiteView(generic.ObjectView):
    queryset = Site.objects.prefetch_related('region', 'tenant__group')

    def get_extra_context(self, request, instance):
        stats = {
            'location_count': Location.objects.restrict(request.user, 'view').filter(site=instance).count(),
            'rack_count': Rack.objects.restrict(request.user, 'view').filter(site=instance).count(),
            'device_count': Device.objects.restrict(request.user, 'view').filter(site=instance).count(),
            'prefix_count': Prefix.objects.restrict(request.user, 'view').filter(site=instance).count(),
            'vlan_count': VLAN.objects.restrict(request.user, 'view').filter(site=instance).count(),
            'circuit_count': Circuit.objects.restrict(request.user, 'view').filter(terminations__site=instance).count(),
            'vm_count': VirtualMachine.objects.restrict(request.user, 'view').filter(cluster__site=instance).count(),
        }
        locations = Location.objects.add_related_count(
            Location.objects.all(),
            Rack,
            'location',
            'rack_count',
            cumulative=True
        )
        locations = Location.objects.add_related_count(
            locations,
            Device,
            'location',
            'device_count',
            cumulative=True
        ).restrict(request.user, 'view').filter(site=instance)

        asns = ASN.objects.restrict(request.user, 'view').filter(sites=instance)
        asn_count = asns.count()

        stats.update({'asn_count': asn_count})

        return {
            'stats': stats,
            'locations': locations,
            'asns': asns,
        }


class SiteEditView(generic.ObjectEditView):
    queryset = Site.objects.all()
    model_form = forms.SiteForm


class SiteDeleteView(generic.ObjectDeleteView):
    queryset = Site.objects.all()


class SiteBulkImportView(generic.BulkImportView):
    queryset = Site.objects.all()
    model_form = forms.SiteCSVForm
    table = tables.SiteTable


class SiteBulkEditView(generic.BulkEditView):
    queryset = Site.objects.prefetch_related('region', 'tenant')
    filterset = filtersets.SiteFilterSet
    table = tables.SiteTable
    form = forms.SiteBulkEditForm


class SiteBulkDeleteView(generic.BulkDeleteView):
    queryset = Site.objects.prefetch_related('region', 'tenant')
    filterset = filtersets.SiteFilterSet
    table = tables.SiteTable


#
# Locations
#

class LocationListView(generic.ObjectListView):
    queryset = Location.objects.add_related_count(
        Location.objects.add_related_count(
            Location.objects.all(),
            Device,
            'location',
            'device_count',
            cumulative=True
        ),
        Rack,
        'location',
        'rack_count',
        cumulative=True
    )
    filterset = filtersets.LocationFilterSet
    filterset_form = forms.LocationFilterForm
    table = tables.LocationTable


class LocationView(generic.ObjectView):
    queryset = Location.objects.all()

    def get_extra_context(self, request, instance):
        location_ids = instance.get_descendants(include_self=True).values_list('pk', flat=True)
        rack_count = Rack.objects.filter(location__in=location_ids).count()
        device_count = Device.objects.filter(location__in=location_ids).count()

        child_locations = Location.objects.add_related_count(
            Location.objects.add_related_count(
                Location.objects.all(),
                Device,
                'location',
                'device_count',
                cumulative=True
            ),
            Rack,
            'location',
            'rack_count',
            cumulative=True
        ).filter(pk__in=location_ids).exclude(pk=instance.pk)
        child_locations_table = tables.LocationTable(child_locations)
        paginate_table(child_locations_table, request)

        return {
            'rack_count': rack_count,
            'device_count': device_count,
            'child_locations_table': child_locations_table,
        }


class LocationEditView(generic.ObjectEditView):
    queryset = Location.objects.all()
    model_form = forms.LocationForm


class LocationDeleteView(generic.ObjectDeleteView):
    queryset = Location.objects.all()


class LocationBulkImportView(generic.BulkImportView):
    queryset = Location.objects.all()
    model_form = forms.LocationCSVForm
    table = tables.LocationTable


class LocationBulkEditView(generic.BulkEditView):
    queryset = Location.objects.add_related_count(
        Location.objects.all(),
        Rack,
        'location',
        'rack_count',
        cumulative=True
    ).prefetch_related('site')
    filterset = filtersets.LocationFilterSet
    table = tables.LocationTable
    form = forms.LocationBulkEditForm


class LocationBulkDeleteView(generic.BulkDeleteView):
    queryset = Location.objects.add_related_count(
        Location.objects.all(),
        Rack,
        'location',
        'rack_count',
        cumulative=True
    ).prefetch_related('site')
    filterset = filtersets.LocationFilterSet
    table = tables.LocationTable


#
# Rack roles
#

class RackRoleListView(generic.ObjectListView):
    queryset = RackRole.objects.annotate(
        rack_count=count_related(Rack, 'role')
    )
    filterset = filtersets.RackRoleFilterSet
    filterset_form = forms.RackRoleFilterForm
    table = tables.RackRoleTable


class RackRoleView(generic.ObjectView):
    queryset = RackRole.objects.all()

    def get_extra_context(self, request, instance):
        racks = Rack.objects.restrict(request.user, 'view').filter(
            role=instance
        )

        racks_table = tables.RackTable(racks, exclude=('role', 'get_utilization', 'get_power_utilization'))
        paginate_table(racks_table, request)

        return {
            'racks_table': racks_table,
        }


class RackRoleEditView(generic.ObjectEditView):
    queryset = RackRole.objects.all()
    model_form = forms.RackRoleForm


class RackRoleDeleteView(generic.ObjectDeleteView):
    queryset = RackRole.objects.all()


class RackRoleBulkImportView(generic.BulkImportView):
    queryset = RackRole.objects.all()
    model_form = forms.RackRoleCSVForm
    table = tables.RackRoleTable


class RackRoleBulkEditView(generic.BulkEditView):
    queryset = RackRole.objects.annotate(
        rack_count=count_related(Rack, 'role')
    )
    filterset = filtersets.RackRoleFilterSet
    table = tables.RackRoleTable
    form = forms.RackRoleBulkEditForm


class RackRoleBulkDeleteView(generic.BulkDeleteView):
    queryset = RackRole.objects.annotate(
        rack_count=count_related(Rack, 'role')
    )
    table = tables.RackRoleTable


#
# Racks
#

class RackListView(generic.ObjectListView):
    queryset = Rack.objects.prefetch_related(
        'site', 'location', 'tenant', 'role', 'devices__device_type'
    ).annotate(
        device_count=count_related(Device, 'rack')
    )
    filterset = filtersets.RackFilterSet
    filterset_form = forms.RackFilterForm
    table = tables.RackTable


class RackElevationListView(generic.ObjectListView):
    """
    Display a set of rack elevations side-by-side.
    """
    queryset = Rack.objects.prefetch_related('role')

    def get(self, request):

        racks = filtersets.RackFilterSet(request.GET, self.queryset).qs
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


class RackView(generic.ObjectView):
    queryset = Rack.objects.prefetch_related('site__region', 'tenant__group', 'location', 'role')

    def get_extra_context(self, request, instance):
        # Get 0U devices located within the rack
        nonracked_devices = Device.objects.filter(
            rack=instance,
            position__isnull=True,
            parent_bay__isnull=True
        ).prefetch_related('device_type__manufacturer')

        peer_racks = Rack.objects.restrict(request.user, 'view').filter(site=instance.site)

        if instance.location:
            peer_racks = peer_racks.filter(location=instance.location)
        else:
            peer_racks = peer_racks.filter(location__isnull=True)
        next_rack = peer_racks.filter(name__gt=instance.name).order_by('name').first()
        prev_rack = peer_racks.filter(name__lt=instance.name).order_by('-name').first()

        reservations = RackReservation.objects.restrict(request.user, 'view').filter(rack=instance)
        power_feeds = PowerFeed.objects.restrict(request.user, 'view').filter(rack=instance).prefetch_related(
            'power_panel'
        )

        device_count = Device.objects.restrict(request.user, 'view').filter(rack=instance).count()

        return {
            'device_count': device_count,
            'reservations': reservations,
            'power_feeds': power_feeds,
            'nonracked_devices': nonracked_devices,
            'next_rack': next_rack,
            'prev_rack': prev_rack,
        }


class RackEditView(generic.ObjectEditView):
    queryset = Rack.objects.all()
    model_form = forms.RackForm
    template_name = 'dcim/rack_edit.html'


class RackDeleteView(generic.ObjectDeleteView):
    queryset = Rack.objects.all()


class RackBulkImportView(generic.BulkImportView):
    queryset = Rack.objects.all()
    model_form = forms.RackCSVForm
    table = tables.RackTable


class RackBulkEditView(generic.BulkEditView):
    queryset = Rack.objects.prefetch_related('site', 'location', 'tenant', 'role')
    filterset = filtersets.RackFilterSet
    table = tables.RackTable
    form = forms.RackBulkEditForm


class RackBulkDeleteView(generic.BulkDeleteView):
    queryset = Rack.objects.prefetch_related('site', 'location', 'tenant', 'role')
    filterset = filtersets.RackFilterSet
    table = tables.RackTable


#
# Rack reservations
#

class RackReservationListView(generic.ObjectListView):
    queryset = RackReservation.objects.all()
    filterset = filtersets.RackReservationFilterSet
    filterset_form = forms.RackReservationFilterForm
    table = tables.RackReservationTable


class RackReservationView(generic.ObjectView):
    queryset = RackReservation.objects.prefetch_related('rack')


class RackReservationEditView(generic.ObjectEditView):
    queryset = RackReservation.objects.all()
    model_form = forms.RackReservationForm

    def alter_object(self, obj, request, args, kwargs):
        if not obj.pk:
            if 'rack' in request.GET:
                obj.rack = get_object_or_404(Rack, pk=request.GET.get('rack'))
            obj.user = request.user
        return obj


class RackReservationDeleteView(generic.ObjectDeleteView):
    queryset = RackReservation.objects.all()


class RackReservationImportView(generic.BulkImportView):
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


class RackReservationBulkEditView(generic.BulkEditView):
    queryset = RackReservation.objects.prefetch_related('rack', 'user')
    filterset = filtersets.RackReservationFilterSet
    table = tables.RackReservationTable
    form = forms.RackReservationBulkEditForm


class RackReservationBulkDeleteView(generic.BulkDeleteView):
    queryset = RackReservation.objects.prefetch_related('rack', 'user')
    filterset = filtersets.RackReservationFilterSet
    table = tables.RackReservationTable


#
# Manufacturers
#

class ManufacturerListView(generic.ObjectListView):
    queryset = Manufacturer.objects.annotate(
        devicetype_count=count_related(DeviceType, 'manufacturer'),
        inventoryitem_count=count_related(InventoryItem, 'manufacturer'),
        platform_count=count_related(Platform, 'manufacturer')
    )
    filterset = filtersets.ManufacturerFilterSet
    filterset_form = forms.ManufacturerFilterForm
    table = tables.ManufacturerTable


class ManufacturerView(generic.ObjectView):
    queryset = Manufacturer.objects.all()

    def get_extra_context(self, request, instance):
        devicetypes = DeviceType.objects.restrict(request.user, 'view').filter(
            manufacturer=instance
        ).annotate(
            instance_count=count_related(Device, 'device_type')
        )
        inventory_items = InventoryItem.objects.restrict(request.user, 'view').filter(
            manufacturer=instance
        )

        devicetypes_table = tables.DeviceTypeTable(devicetypes, exclude=('manufacturer',))
        paginate_table(devicetypes_table, request)

        return {
            'devicetypes_table': devicetypes_table,
            'inventory_item_count': inventory_items.count(),
        }


class ManufacturerEditView(generic.ObjectEditView):
    queryset = Manufacturer.objects.all()
    model_form = forms.ManufacturerForm


class ManufacturerDeleteView(generic.ObjectDeleteView):
    queryset = Manufacturer.objects.all()


class ManufacturerBulkImportView(generic.BulkImportView):
    queryset = Manufacturer.objects.all()
    model_form = forms.ManufacturerCSVForm
    table = tables.ManufacturerTable


class ManufacturerBulkEditView(generic.BulkEditView):
    queryset = Manufacturer.objects.annotate(
        devicetype_count=count_related(DeviceType, 'manufacturer')
    )
    filterset = filtersets.ManufacturerFilterSet
    table = tables.ManufacturerTable
    form = forms.ManufacturerBulkEditForm


class ManufacturerBulkDeleteView(generic.BulkDeleteView):
    queryset = Manufacturer.objects.annotate(
        devicetype_count=count_related(DeviceType, 'manufacturer')
    )
    table = tables.ManufacturerTable


#
# Device types
#

class DeviceTypeListView(generic.ObjectListView):
    queryset = DeviceType.objects.prefetch_related('manufacturer').annotate(
        instance_count=count_related(Device, 'device_type')
    )
    filterset = filtersets.DeviceTypeFilterSet
    filterset_form = forms.DeviceTypeFilterForm
    table = tables.DeviceTypeTable


class DeviceTypeView(generic.ObjectView):
    queryset = DeviceType.objects.prefetch_related('manufacturer')

    def get_extra_context(self, request, instance):
        instance_count = Device.objects.restrict(request.user).filter(device_type=instance).count()

        return {
            'instance_count': instance_count,
            'active_tab': 'devicetype',
        }


class DeviceTypeConsolePortsView(DeviceTypeComponentsView):
    child_model = ConsolePortTemplate
    table = tables.ConsolePortTemplateTable
    filterset = filtersets.ConsolePortTemplateFilterSet
    viewname = 'dcim:devicetype_consoleports'


class DeviceTypeConsoleServerPortsView(DeviceTypeComponentsView):
    child_model = ConsoleServerPortTemplate
    table = tables.ConsoleServerPortTemplateTable
    filterset = filtersets.ConsoleServerPortTemplateFilterSet
    viewname = 'dcim:devicetype_consoleserverports'


class DeviceTypePowerPortsView(DeviceTypeComponentsView):
    child_model = PowerPortTemplate
    table = tables.PowerPortTemplateTable
    filterset = filtersets.PowerPortTemplateFilterSet
    viewname = 'dcim:devicetype_powerports'


class DeviceTypePowerOutletsView(DeviceTypeComponentsView):
    child_model = PowerOutletTemplate
    table = tables.PowerOutletTemplateTable
    filterset = filtersets.PowerOutletTemplateFilterSet
    viewname = 'dcim:devicetype_poweroutlets'


class DeviceTypeInterfacesView(DeviceTypeComponentsView):
    child_model = InterfaceTemplate
    table = tables.InterfaceTemplateTable
    filterset = filtersets.InterfaceTemplateFilterSet
    viewname = 'dcim:devicetype_interfaces'


class DeviceTypeFrontPortsView(DeviceTypeComponentsView):
    child_model = FrontPortTemplate
    table = tables.FrontPortTemplateTable
    filterset = filtersets.FrontPortTemplateFilterSet
    viewname = 'dcim:devicetype_frontports'


class DeviceTypeRearPortsView(DeviceTypeComponentsView):
    child_model = RearPortTemplate
    table = tables.RearPortTemplateTable
    filterset = filtersets.RearPortTemplateFilterSet
    viewname = 'dcim:devicetype_rearports'


class DeviceTypeModuleBaysView(DeviceTypeComponentsView):
    child_model = ModuleBayTemplate
    table = tables.ModuleBayTemplateTable
    filterset = filtersets.ModuleBayTemplateFilterSet


class DeviceTypeDeviceBaysView(DeviceTypeComponentsView):
    child_model = DeviceBayTemplate
    table = tables.DeviceBayTemplateTable
    filterset = filtersets.DeviceBayTemplateFilterSet
    viewname = 'dcim:devicetype_devicebays'


class DeviceTypeEditView(generic.ObjectEditView):
    queryset = DeviceType.objects.all()
    model_form = forms.DeviceTypeForm


class DeviceTypeDeleteView(generic.ObjectDeleteView):
    queryset = DeviceType.objects.all()


class DeviceTypeImportView(generic.ObjectImportView):
    additional_permissions = [
        'dcim.add_devicetype',
        'dcim.add_consoleporttemplate',
        'dcim.add_consoleserverporttemplate',
        'dcim.add_powerporttemplate',
        'dcim.add_poweroutlettemplate',
        'dcim.add_interfacetemplate',
        'dcim.add_frontporttemplate',
        'dcim.add_rearporttemplate',
        'dcim.add_modulebaytemplate',
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
        ('module-bays', forms.ModuleBayTemplateImportForm),
        ('device-bays', forms.DeviceBayTemplateImportForm),
    ))

    def prep_related_object_data(self, parent, data):
        data.update({'device_type': parent})
        return data


class DeviceTypeBulkEditView(generic.BulkEditView):
    queryset = DeviceType.objects.prefetch_related('manufacturer').annotate(
        instance_count=count_related(Device, 'device_type')
    )
    filterset = filtersets.DeviceTypeFilterSet
    table = tables.DeviceTypeTable
    form = forms.DeviceTypeBulkEditForm


class DeviceTypeBulkDeleteView(generic.BulkDeleteView):
    queryset = DeviceType.objects.prefetch_related('manufacturer').annotate(
        instance_count=count_related(Device, 'device_type')
    )
    filterset = filtersets.DeviceTypeFilterSet
    table = tables.DeviceTypeTable


#
# Module types
#

class ModuleTypeListView(generic.ObjectListView):
    queryset = ModuleType.objects.prefetch_related('manufacturer').annotate(
        # instance_count=count_related(Module, 'module_type')
    )
    filterset = filtersets.ModuleTypeFilterSet
    filterset_form = forms.ModuleTypeFilterForm
    table = tables.ModuleTypeTable


class ModuleTypeView(generic.ObjectView):
    queryset = ModuleType.objects.prefetch_related('manufacturer')

    def get_extra_context(self, request, instance):
        # instance_count = Module.objects.restrict(request.user).filter(device_type=instance).count()

        return {
            # 'instance_count': instance_count,
            'active_tab': 'moduletype',
        }


class ModuleTypeConsolePortsView(ModuleTypeComponentsView):
    child_model = ConsolePortTemplate
    table = tables.ConsolePortTemplateTable
    filterset = filtersets.ConsolePortTemplateFilterSet


class ModuleTypeConsoleServerPortsView(ModuleTypeComponentsView):
    child_model = ConsoleServerPortTemplate
    table = tables.ConsoleServerPortTemplateTable
    filterset = filtersets.ConsoleServerPortTemplateFilterSet


class ModuleTypePowerPortsView(ModuleTypeComponentsView):
    child_model = PowerPortTemplate
    table = tables.PowerPortTemplateTable
    filterset = filtersets.PowerPortTemplateFilterSet


class ModuleTypePowerOutletsView(ModuleTypeComponentsView):
    child_model = PowerOutletTemplate
    table = tables.PowerOutletTemplateTable
    filterset = filtersets.PowerOutletTemplateFilterSet


class ModuleTypeInterfacesView(ModuleTypeComponentsView):
    child_model = InterfaceTemplate
    table = tables.InterfaceTemplateTable
    filterset = filtersets.InterfaceTemplateFilterSet


class ModuleTypeFrontPortsView(ModuleTypeComponentsView):
    child_model = FrontPortTemplate
    table = tables.FrontPortTemplateTable
    filterset = filtersets.FrontPortTemplateFilterSet


class ModuleTypeRearPortsView(ModuleTypeComponentsView):
    child_model = RearPortTemplate
    table = tables.RearPortTemplateTable
    filterset = filtersets.RearPortTemplateFilterSet


class ModuleTypeEditView(generic.ObjectEditView):
    queryset = ModuleType.objects.all()
    model_form = forms.ModuleTypeForm


class ModuleTypeDeleteView(generic.ObjectDeleteView):
    queryset = ModuleType.objects.all()


class ModuleTypeImportView(generic.ObjectImportView):
    additional_permissions = [
        'dcim.add_moduletype',
        'dcim.add_consoleporttemplate',
        'dcim.add_consoleserverporttemplate',
        'dcim.add_powerporttemplate',
        'dcim.add_poweroutlettemplate',
        'dcim.add_interfacetemplate',
        'dcim.add_frontporttemplate',
        'dcim.add_rearporttemplate',
    ]
    queryset = ModuleType.objects.all()
    model_form = forms.ModuleTypeImportForm
    related_object_forms = OrderedDict((
        ('console-ports', forms.ConsolePortTemplateImportForm),
        ('console-server-ports', forms.ConsoleServerPortTemplateImportForm),
        ('power-ports', forms.PowerPortTemplateImportForm),
        ('power-outlets', forms.PowerOutletTemplateImportForm),
        ('interfaces', forms.InterfaceTemplateImportForm),
        ('rear-ports', forms.RearPortTemplateImportForm),
        ('front-ports', forms.FrontPortTemplateImportForm),
    ))

    def prep_related_object_data(self, parent, data):
        data.update({'module_type': parent})
        return data


class ModuleTypeBulkEditView(generic.BulkEditView):
    queryset = ModuleType.objects.prefetch_related('manufacturer').annotate(
        # instance_count=count_related(Module, 'module_type')
    )
    filterset = filtersets.ModuleTypeFilterSet
    table = tables.ModuleTypeTable
    form = forms.ModuleTypeBulkEditForm


class ModuleTypeBulkDeleteView(generic.BulkDeleteView):
    queryset = ModuleType.objects.prefetch_related('manufacturer').annotate(
        # instance_count=count_related(Module, 'module_type')
    )
    filterset = filtersets.ModuleTypeFilterSet
    table = tables.ModuleTypeTable


#
# Console port templates
#

class ConsolePortTemplateCreateView(generic.ComponentCreateView):
    queryset = ConsolePortTemplate.objects.all()
    form = forms.ConsolePortTemplateCreateForm
    model_form = forms.ConsolePortTemplateForm


class ConsolePortTemplateEditView(generic.ObjectEditView):
    queryset = ConsolePortTemplate.objects.all()
    model_form = forms.ConsolePortTemplateForm


class ConsolePortTemplateDeleteView(generic.ObjectDeleteView):
    queryset = ConsolePortTemplate.objects.all()


class ConsolePortTemplateBulkEditView(generic.BulkEditView):
    queryset = ConsolePortTemplate.objects.all()
    table = tables.ConsolePortTemplateTable
    form = forms.ConsolePortTemplateBulkEditForm


class ConsolePortTemplateBulkRenameView(generic.BulkRenameView):
    queryset = ConsolePortTemplate.objects.all()


class ConsolePortTemplateBulkDeleteView(generic.BulkDeleteView):
    queryset = ConsolePortTemplate.objects.all()
    table = tables.ConsolePortTemplateTable


#
# Console server port templates
#

class ConsoleServerPortTemplateCreateView(generic.ComponentCreateView):
    queryset = ConsoleServerPortTemplate.objects.all()
    form = forms.ConsoleServerPortTemplateCreateForm
    model_form = forms.ConsoleServerPortTemplateForm


class ConsoleServerPortTemplateEditView(generic.ObjectEditView):
    queryset = ConsoleServerPortTemplate.objects.all()
    model_form = forms.ConsoleServerPortTemplateForm


class ConsoleServerPortTemplateDeleteView(generic.ObjectDeleteView):
    queryset = ConsoleServerPortTemplate.objects.all()


class ConsoleServerPortTemplateBulkEditView(generic.BulkEditView):
    queryset = ConsoleServerPortTemplate.objects.all()
    table = tables.ConsoleServerPortTemplateTable
    form = forms.ConsoleServerPortTemplateBulkEditForm


class ConsoleServerPortTemplateBulkRenameView(generic.BulkRenameView):
    queryset = ConsoleServerPortTemplate.objects.all()


class ConsoleServerPortTemplateBulkDeleteView(generic.BulkDeleteView):
    queryset = ConsoleServerPortTemplate.objects.all()
    table = tables.ConsoleServerPortTemplateTable


#
# Power port templates
#

class PowerPortTemplateCreateView(generic.ComponentCreateView):
    queryset = PowerPortTemplate.objects.all()
    form = forms.PowerPortTemplateCreateForm
    model_form = forms.PowerPortTemplateForm


class PowerPortTemplateEditView(generic.ObjectEditView):
    queryset = PowerPortTemplate.objects.all()
    model_form = forms.PowerPortTemplateForm


class PowerPortTemplateDeleteView(generic.ObjectDeleteView):
    queryset = PowerPortTemplate.objects.all()


class PowerPortTemplateBulkEditView(generic.BulkEditView):
    queryset = PowerPortTemplate.objects.all()
    table = tables.PowerPortTemplateTable
    form = forms.PowerPortTemplateBulkEditForm


class PowerPortTemplateBulkRenameView(generic.BulkRenameView):
    queryset = PowerPortTemplate.objects.all()


class PowerPortTemplateBulkDeleteView(generic.BulkDeleteView):
    queryset = PowerPortTemplate.objects.all()
    table = tables.PowerPortTemplateTable


#
# Power outlet templates
#

class PowerOutletTemplateCreateView(generic.ComponentCreateView):
    queryset = PowerOutletTemplate.objects.all()
    form = forms.PowerOutletTemplateCreateForm
    model_form = forms.PowerOutletTemplateForm


class PowerOutletTemplateEditView(generic.ObjectEditView):
    queryset = PowerOutletTemplate.objects.all()
    model_form = forms.PowerOutletTemplateForm


class PowerOutletTemplateDeleteView(generic.ObjectDeleteView):
    queryset = PowerOutletTemplate.objects.all()


class PowerOutletTemplateBulkEditView(generic.BulkEditView):
    queryset = PowerOutletTemplate.objects.all()
    table = tables.PowerOutletTemplateTable
    form = forms.PowerOutletTemplateBulkEditForm


class PowerOutletTemplateBulkRenameView(generic.BulkRenameView):
    queryset = PowerOutletTemplate.objects.all()


class PowerOutletTemplateBulkDeleteView(generic.BulkDeleteView):
    queryset = PowerOutletTemplate.objects.all()
    table = tables.PowerOutletTemplateTable


#
# Interface templates
#

class InterfaceTemplateCreateView(generic.ComponentCreateView):
    queryset = InterfaceTemplate.objects.all()
    form = forms.InterfaceTemplateCreateForm
    model_form = forms.InterfaceTemplateForm


class InterfaceTemplateEditView(generic.ObjectEditView):
    queryset = InterfaceTemplate.objects.all()
    model_form = forms.InterfaceTemplateForm


class InterfaceTemplateDeleteView(generic.ObjectDeleteView):
    queryset = InterfaceTemplate.objects.all()


class InterfaceTemplateBulkEditView(generic.BulkEditView):
    queryset = InterfaceTemplate.objects.all()
    table = tables.InterfaceTemplateTable
    form = forms.InterfaceTemplateBulkEditForm


class InterfaceTemplateBulkRenameView(generic.BulkRenameView):
    queryset = InterfaceTemplate.objects.all()


class InterfaceTemplateBulkDeleteView(generic.BulkDeleteView):
    queryset = InterfaceTemplate.objects.all()
    table = tables.InterfaceTemplateTable


#
# Front port templates
#

class FrontPortTemplateCreateView(generic.ComponentCreateView):
    queryset = FrontPortTemplate.objects.all()
    form = forms.FrontPortTemplateCreateForm
    model_form = forms.FrontPortTemplateForm


class FrontPortTemplateEditView(generic.ObjectEditView):
    queryset = FrontPortTemplate.objects.all()
    model_form = forms.FrontPortTemplateForm


class FrontPortTemplateDeleteView(generic.ObjectDeleteView):
    queryset = FrontPortTemplate.objects.all()


class FrontPortTemplateBulkEditView(generic.BulkEditView):
    queryset = FrontPortTemplate.objects.all()
    table = tables.FrontPortTemplateTable
    form = forms.FrontPortTemplateBulkEditForm


class FrontPortTemplateBulkRenameView(generic.BulkRenameView):
    queryset = FrontPortTemplate.objects.all()


class FrontPortTemplateBulkDeleteView(generic.BulkDeleteView):
    queryset = FrontPortTemplate.objects.all()
    table = tables.FrontPortTemplateTable


#
# Rear port templates
#

class RearPortTemplateCreateView(generic.ComponentCreateView):
    queryset = RearPortTemplate.objects.all()
    form = forms.RearPortTemplateCreateForm
    model_form = forms.RearPortTemplateForm


class RearPortTemplateEditView(generic.ObjectEditView):
    queryset = RearPortTemplate.objects.all()
    model_form = forms.RearPortTemplateForm


class RearPortTemplateDeleteView(generic.ObjectDeleteView):
    queryset = RearPortTemplate.objects.all()


class RearPortTemplateBulkEditView(generic.BulkEditView):
    queryset = RearPortTemplate.objects.all()
    table = tables.RearPortTemplateTable
    form = forms.RearPortTemplateBulkEditForm


class RearPortTemplateBulkRenameView(generic.BulkRenameView):
    queryset = RearPortTemplate.objects.all()


class RearPortTemplateBulkDeleteView(generic.BulkDeleteView):
    queryset = RearPortTemplate.objects.all()
    table = tables.RearPortTemplateTable


#
# Module bay templates
#

class ModuleBayTemplateCreateView(generic.ComponentCreateView):
    queryset = ModuleBayTemplate.objects.all()
    form = forms.ModuleBayTemplateCreateForm
    model_form = forms.ModuleBayTemplateForm


class ModuleBayTemplateEditView(generic.ObjectEditView):
    queryset = ModuleBayTemplate.objects.all()
    model_form = forms.ModuleBayTemplateForm


class ModuleBayTemplateDeleteView(generic.ObjectDeleteView):
    queryset = ModuleBayTemplate.objects.all()


class ModuleBayTemplateBulkEditView(generic.BulkEditView):
    queryset = ModuleBayTemplate.objects.all()
    table = tables.ModuleBayTemplateTable
    form = forms.ModuleBayTemplateBulkEditForm


class ModuleBayTemplateBulkRenameView(generic.BulkRenameView):
    queryset = ModuleBayTemplate.objects.all()


class ModuleBayTemplateBulkDeleteView(generic.BulkDeleteView):
    queryset = ModuleBayTemplate.objects.all()
    table = tables.ModuleBayTemplateTable


#
# Device bay templates
#

class DeviceBayTemplateCreateView(generic.ComponentCreateView):
    queryset = DeviceBayTemplate.objects.all()
    form = forms.DeviceBayTemplateCreateForm
    model_form = forms.DeviceBayTemplateForm


class DeviceBayTemplateEditView(generic.ObjectEditView):
    queryset = DeviceBayTemplate.objects.all()
    model_form = forms.DeviceBayTemplateForm


class DeviceBayTemplateDeleteView(generic.ObjectDeleteView):
    queryset = DeviceBayTemplate.objects.all()


class DeviceBayTemplateBulkEditView(generic.BulkEditView):
    queryset = DeviceBayTemplate.objects.all()
    table = tables.DeviceBayTemplateTable
    form = forms.DeviceBayTemplateBulkEditForm


class DeviceBayTemplateBulkRenameView(generic.BulkRenameView):
    queryset = DeviceBayTemplate.objects.all()


class DeviceBayTemplateBulkDeleteView(generic.BulkDeleteView):
    queryset = DeviceBayTemplate.objects.all()
    table = tables.DeviceBayTemplateTable


#
# Device roles
#

class DeviceRoleListView(generic.ObjectListView):
    queryset = DeviceRole.objects.annotate(
        device_count=count_related(Device, 'device_role'),
        vm_count=count_related(VirtualMachine, 'role')
    )
    filterset = filtersets.DeviceRoleFilterSet
    filterset_form = forms.DeviceRoleFilterForm
    table = tables.DeviceRoleTable


class DeviceRoleView(generic.ObjectView):
    queryset = DeviceRole.objects.all()

    def get_extra_context(self, request, instance):
        devices = Device.objects.restrict(request.user, 'view').filter(
            device_role=instance
        )
        devices_table = tables.DeviceTable(devices, exclude=('device_role',))
        paginate_table(devices_table, request)

        return {
            'devices_table': devices_table,
            'device_count': Device.objects.filter(device_role=instance).count(),
            'virtualmachine_count': VirtualMachine.objects.filter(role=instance).count(),
        }


class DeviceRoleEditView(generic.ObjectEditView):
    queryset = DeviceRole.objects.all()
    model_form = forms.DeviceRoleForm


class DeviceRoleDeleteView(generic.ObjectDeleteView):
    queryset = DeviceRole.objects.all()


class DeviceRoleBulkImportView(generic.BulkImportView):
    queryset = DeviceRole.objects.all()
    model_form = forms.DeviceRoleCSVForm
    table = tables.DeviceRoleTable


class DeviceRoleBulkEditView(generic.BulkEditView):
    queryset = DeviceRole.objects.annotate(
        device_count=count_related(Device, 'device_role'),
        vm_count=count_related(VirtualMachine, 'role')
    )
    filterset = filtersets.DeviceRoleFilterSet
    table = tables.DeviceRoleTable
    form = forms.DeviceRoleBulkEditForm


class DeviceRoleBulkDeleteView(generic.BulkDeleteView):
    queryset = DeviceRole.objects.annotate(
        device_count=count_related(Device, 'device_role'),
        vm_count=count_related(VirtualMachine, 'role')
    )
    table = tables.DeviceRoleTable


#
# Platforms
#

class PlatformListView(generic.ObjectListView):
    queryset = Platform.objects.annotate(
        device_count=count_related(Device, 'platform'),
        vm_count=count_related(VirtualMachine, 'platform')
    )
    table = tables.PlatformTable
    filterset = filtersets.PlatformFilterSet
    filterset_form = forms.PlatformFilterForm


class PlatformView(generic.ObjectView):
    queryset = Platform.objects.all()

    def get_extra_context(self, request, instance):
        devices = Device.objects.restrict(request.user, 'view').filter(
            platform=instance
        )
        devices_table = tables.DeviceTable(devices, exclude=('platform',))
        paginate_table(devices_table, request)

        return {
            'devices_table': devices_table,
            'virtualmachine_count': VirtualMachine.objects.filter(platform=instance).count()
        }


class PlatformEditView(generic.ObjectEditView):
    queryset = Platform.objects.all()
    model_form = forms.PlatformForm


class PlatformDeleteView(generic.ObjectDeleteView):
    queryset = Platform.objects.all()


class PlatformBulkImportView(generic.BulkImportView):
    queryset = Platform.objects.all()
    model_form = forms.PlatformCSVForm
    table = tables.PlatformTable


class PlatformBulkEditView(generic.BulkEditView):
    queryset = Platform.objects.all()
    filterset = filtersets.PlatformFilterSet
    table = tables.PlatformTable
    form = forms.PlatformBulkEditForm


class PlatformBulkDeleteView(generic.BulkDeleteView):
    queryset = Platform.objects.all()
    table = tables.PlatformTable


#
# Devices
#

class DeviceListView(generic.ObjectListView):
    queryset = Device.objects.all()
    filterset = filtersets.DeviceFilterSet
    filterset_form = forms.DeviceFilterForm
    table = tables.DeviceTable
    template_name = 'dcim/device_list.html'


class DeviceView(generic.ObjectView):
    queryset = Device.objects.prefetch_related(
        'site__region', 'location', 'rack', 'tenant__group', 'device_role', 'platform', 'primary_ip4', 'primary_ip6'
    )

    def get_extra_context(self, request, instance):
        # VirtualChassis members
        if instance.virtual_chassis is not None:
            vc_members = Device.objects.restrict(request.user, 'view').filter(
                virtual_chassis=instance.virtual_chassis
            ).order_by('vc_position')
        else:
            vc_members = []

        # Services
        services = Service.objects.restrict(request.user, 'view').filter(device=instance)

        return {
            'services': services,
            'vc_members': vc_members,
            'active_tab': 'device',
        }


class DeviceConsolePortsView(DeviceComponentsView):
    child_model = ConsolePort
    table = tables.DeviceConsolePortTable
    filterset = filtersets.ConsolePortFilterSet
    template_name = 'dcim/device/consoleports.html'


class DeviceConsoleServerPortsView(DeviceComponentsView):
    child_model = ConsoleServerPort
    table = tables.DeviceConsoleServerPortTable
    filterset = filtersets.ConsoleServerPortFilterSet
    template_name = 'dcim/device/consoleserverports.html'


class DevicePowerPortsView(DeviceComponentsView):
    child_model = PowerPort
    table = tables.DevicePowerPortTable
    filterset = filtersets.PowerPortFilterSet
    template_name = 'dcim/device/powerports.html'


class DevicePowerOutletsView(DeviceComponentsView):
    child_model = PowerOutlet
    table = tables.DevicePowerOutletTable
    filterset = filtersets.PowerOutletFilterSet
    template_name = 'dcim/device/poweroutlets.html'


class DeviceInterfacesView(DeviceComponentsView):
    child_model = Interface
    table = tables.DeviceInterfaceTable
    filterset = filtersets.InterfaceFilterSet
    template_name = 'dcim/device/interfaces.html'

    def get_children(self, request, parent):
        return parent.vc_interfaces().restrict(request.user, 'view').prefetch_related(
            Prefetch('ip_addresses', queryset=IPAddress.objects.restrict(request.user)),
            Prefetch('member_interfaces', queryset=Interface.objects.restrict(request.user))
        )


class DeviceFrontPortsView(DeviceComponentsView):
    child_model = FrontPort
    table = tables.DeviceFrontPortTable
    filterset = filtersets.FrontPortFilterSet
    template_name = 'dcim/device/frontports.html'


class DeviceRearPortsView(DeviceComponentsView):
    child_model = RearPort
    table = tables.DeviceRearPortTable
    filterset = filtersets.RearPortFilterSet
    template_name = 'dcim/device/rearports.html'


class DeviceModuleBaysView(DeviceComponentsView):
    child_model = ModuleBay
    table = tables.DeviceModuleBayTable
    filterset = filtersets.ModuleBayFilterSet
    template_name = 'dcim/device/modulebays.html'


class DeviceDeviceBaysView(DeviceComponentsView):
    child_model = DeviceBay
    table = tables.DeviceDeviceBayTable
    filterset = filtersets.DeviceBayFilterSet
    template_name = 'dcim/device/devicebays.html'


class DeviceInventoryView(DeviceComponentsView):
    child_model = InventoryItem
    table = tables.DeviceInventoryItemTable
    filterset = filtersets.InventoryItemFilterSet
    template_name = 'dcim/device/inventory.html'


class DeviceStatusView(generic.ObjectView):
    additional_permissions = ['dcim.napalm_read_device']
    queryset = Device.objects.all()
    template_name = 'dcim/device/status.html'

    def get_extra_context(self, request, instance):
        return {
            'active_tab': 'status',
        }


class DeviceLLDPNeighborsView(generic.ObjectView):
    additional_permissions = ['dcim.napalm_read_device']
    queryset = Device.objects.all()
    template_name = 'dcim/device/lldp_neighbors.html'

    def get_extra_context(self, request, instance):
        interfaces = instance.vc_interfaces().restrict(request.user, 'view').prefetch_related(
            '_path__destination'
        ).exclude(
            type__in=NONCONNECTABLE_IFACE_TYPES
        )

        return {
            'interfaces': interfaces,
            'active_tab': 'lldp-neighbors',
        }


class DeviceConfigView(generic.ObjectView):
    additional_permissions = ['dcim.napalm_read_device']
    queryset = Device.objects.all()
    template_name = 'dcim/device/config.html'

    def get_extra_context(self, request, instance):
        return {
            'active_tab': 'config',
        }


class DeviceConfigContextView(ObjectConfigContextView):
    queryset = Device.objects.annotate_config_context_data()
    base_template = 'dcim/device/base.html'


class DeviceEditView(generic.ObjectEditView):
    queryset = Device.objects.all()
    model_form = forms.DeviceForm
    template_name = 'dcim/device_edit.html'


class DeviceDeleteView(generic.ObjectDeleteView):
    queryset = Device.objects.all()


class DeviceBulkImportView(generic.BulkImportView):
    queryset = Device.objects.all()
    model_form = forms.DeviceCSVForm
    table = tables.DeviceImportTable
    template_name = 'dcim/device_import.html'


class ChildDeviceBulkImportView(generic.BulkImportView):
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


class DeviceBulkEditView(generic.BulkEditView):
    queryset = Device.objects.prefetch_related('tenant', 'site', 'rack', 'device_role', 'device_type__manufacturer')
    filterset = filtersets.DeviceFilterSet
    table = tables.DeviceTable
    form = forms.DeviceBulkEditForm


class DeviceBulkDeleteView(generic.BulkDeleteView):
    queryset = Device.objects.prefetch_related('tenant', 'site', 'rack', 'device_role', 'device_type__manufacturer')
    filterset = filtersets.DeviceFilterSet
    table = tables.DeviceTable


#
# Devices
#

class ModuleListView(generic.ObjectListView):
    queryset = Module.objects.prefetch_related('device', 'module_type__manufacturer')
    filterset = filtersets.ModuleFilterSet
    filterset_form = forms.ModuleFilterForm
    table = tables.ModuleTable


class ModuleView(generic.ObjectView):
    queryset = Module.objects.all()


class ModuleEditView(generic.ObjectEditView):
    queryset = Module.objects.all()
    model_form = forms.ModuleForm


class ModuleDeleteView(generic.ObjectDeleteView):
    queryset = Module.objects.all()


class ModuleBulkImportView(generic.BulkImportView):
    queryset = Module.objects.all()
    model_form = forms.ModuleCSVForm
    table = tables.ModuleTable


class ModuleBulkEditView(generic.BulkEditView):
    queryset = Module.objects.prefetch_related('device', 'module_type__manufacturer')
    filterset = filtersets.ModuleFilterSet
    table = tables.ModuleTable
    form = forms.ModuleBulkEditForm


class ModuleBulkDeleteView(generic.BulkDeleteView):
    queryset = Module.objects.prefetch_related('device', 'module_type__manufacturer')
    filterset = filtersets.ModuleFilterSet
    table = tables.ModuleTable


#
# Console ports
#

class ConsolePortListView(generic.ObjectListView):
    queryset = ConsolePort.objects.all()
    filterset = filtersets.ConsolePortFilterSet
    filterset_form = forms.ConsolePortFilterForm
    table = tables.ConsolePortTable
    action_buttons = ('import', 'export')


class ConsolePortView(generic.ObjectView):
    queryset = ConsolePort.objects.all()


class ConsolePortCreateView(generic.ComponentCreateView):
    queryset = ConsolePort.objects.all()
    form = forms.ConsolePortCreateForm
    model_form = forms.ConsolePortForm


class ConsolePortEditView(generic.ObjectEditView):
    queryset = ConsolePort.objects.all()
    model_form = forms.ConsolePortForm
    template_name = 'dcim/device_component_edit.html'


class ConsolePortDeleteView(generic.ObjectDeleteView):
    queryset = ConsolePort.objects.all()


class ConsolePortBulkImportView(generic.BulkImportView):
    queryset = ConsolePort.objects.all()
    model_form = forms.ConsolePortCSVForm
    table = tables.ConsolePortTable


class ConsolePortBulkEditView(generic.BulkEditView):
    queryset = ConsolePort.objects.all()
    filterset = filtersets.ConsolePortFilterSet
    table = tables.ConsolePortTable
    form = forms.ConsolePortBulkEditForm


class ConsolePortBulkRenameView(generic.BulkRenameView):
    queryset = ConsolePort.objects.all()


class ConsolePortBulkDisconnectView(BulkDisconnectView):
    queryset = ConsolePort.objects.all()


class ConsolePortBulkDeleteView(generic.BulkDeleteView):
    queryset = ConsolePort.objects.all()
    filterset = filtersets.ConsolePortFilterSet
    table = tables.ConsolePortTable


#
# Console server ports
#

class ConsoleServerPortListView(generic.ObjectListView):
    queryset = ConsoleServerPort.objects.all()
    filterset = filtersets.ConsoleServerPortFilterSet
    filterset_form = forms.ConsoleServerPortFilterForm
    table = tables.ConsoleServerPortTable
    action_buttons = ('import', 'export')


class ConsoleServerPortView(generic.ObjectView):
    queryset = ConsoleServerPort.objects.all()


class ConsoleServerPortCreateView(generic.ComponentCreateView):
    queryset = ConsoleServerPort.objects.all()
    form = forms.ConsoleServerPortCreateForm
    model_form = forms.ConsoleServerPortForm


class ConsoleServerPortEditView(generic.ObjectEditView):
    queryset = ConsoleServerPort.objects.all()
    model_form = forms.ConsoleServerPortForm
    template_name = 'dcim/device_component_edit.html'


class ConsoleServerPortDeleteView(generic.ObjectDeleteView):
    queryset = ConsoleServerPort.objects.all()


class ConsoleServerPortBulkImportView(generic.BulkImportView):
    queryset = ConsoleServerPort.objects.all()
    model_form = forms.ConsoleServerPortCSVForm
    table = tables.ConsoleServerPortTable


class ConsoleServerPortBulkEditView(generic.BulkEditView):
    queryset = ConsoleServerPort.objects.all()
    filterset = filtersets.ConsoleServerPortFilterSet
    table = tables.ConsoleServerPortTable
    form = forms.ConsoleServerPortBulkEditForm


class ConsoleServerPortBulkRenameView(generic.BulkRenameView):
    queryset = ConsoleServerPort.objects.all()


class ConsoleServerPortBulkDisconnectView(BulkDisconnectView):
    queryset = ConsoleServerPort.objects.all()


class ConsoleServerPortBulkDeleteView(generic.BulkDeleteView):
    queryset = ConsoleServerPort.objects.all()
    filterset = filtersets.ConsoleServerPortFilterSet
    table = tables.ConsoleServerPortTable


#
# Power ports
#

class PowerPortListView(generic.ObjectListView):
    queryset = PowerPort.objects.all()
    filterset = filtersets.PowerPortFilterSet
    filterset_form = forms.PowerPortFilterForm
    table = tables.PowerPortTable
    action_buttons = ('import', 'export')


class PowerPortView(generic.ObjectView):
    queryset = PowerPort.objects.all()


class PowerPortCreateView(generic.ComponentCreateView):
    queryset = PowerPort.objects.all()
    form = forms.PowerPortCreateForm
    model_form = forms.PowerPortForm


class PowerPortEditView(generic.ObjectEditView):
    queryset = PowerPort.objects.all()
    model_form = forms.PowerPortForm
    template_name = 'dcim/device_component_edit.html'


class PowerPortDeleteView(generic.ObjectDeleteView):
    queryset = PowerPort.objects.all()


class PowerPortBulkImportView(generic.BulkImportView):
    queryset = PowerPort.objects.all()
    model_form = forms.PowerPortCSVForm
    table = tables.PowerPortTable


class PowerPortBulkEditView(generic.BulkEditView):
    queryset = PowerPort.objects.all()
    filterset = filtersets.PowerPortFilterSet
    table = tables.PowerPortTable
    form = forms.PowerPortBulkEditForm


class PowerPortBulkRenameView(generic.BulkRenameView):
    queryset = PowerPort.objects.all()


class PowerPortBulkDisconnectView(BulkDisconnectView):
    queryset = PowerPort.objects.all()


class PowerPortBulkDeleteView(generic.BulkDeleteView):
    queryset = PowerPort.objects.all()
    filterset = filtersets.PowerPortFilterSet
    table = tables.PowerPortTable


#
# Power outlets
#

class PowerOutletListView(generic.ObjectListView):
    queryset = PowerOutlet.objects.all()
    filterset = filtersets.PowerOutletFilterSet
    filterset_form = forms.PowerOutletFilterForm
    table = tables.PowerOutletTable
    action_buttons = ('import', 'export')


class PowerOutletView(generic.ObjectView):
    queryset = PowerOutlet.objects.all()


class PowerOutletCreateView(generic.ComponentCreateView):
    queryset = PowerOutlet.objects.all()
    form = forms.PowerOutletCreateForm
    model_form = forms.PowerOutletForm


class PowerOutletEditView(generic.ObjectEditView):
    queryset = PowerOutlet.objects.all()
    model_form = forms.PowerOutletForm
    template_name = 'dcim/device_component_edit.html'


class PowerOutletDeleteView(generic.ObjectDeleteView):
    queryset = PowerOutlet.objects.all()


class PowerOutletBulkImportView(generic.BulkImportView):
    queryset = PowerOutlet.objects.all()
    model_form = forms.PowerOutletCSVForm
    table = tables.PowerOutletTable


class PowerOutletBulkEditView(generic.BulkEditView):
    queryset = PowerOutlet.objects.all()
    filterset = filtersets.PowerOutletFilterSet
    table = tables.PowerOutletTable
    form = forms.PowerOutletBulkEditForm


class PowerOutletBulkRenameView(generic.BulkRenameView):
    queryset = PowerOutlet.objects.all()


class PowerOutletBulkDisconnectView(BulkDisconnectView):
    queryset = PowerOutlet.objects.all()


class PowerOutletBulkDeleteView(generic.BulkDeleteView):
    queryset = PowerOutlet.objects.all()
    filterset = filtersets.PowerOutletFilterSet
    table = tables.PowerOutletTable


#
# Interfaces
#

class InterfaceListView(generic.ObjectListView):
    queryset = Interface.objects.all()
    filterset = filtersets.InterfaceFilterSet
    filterset_form = forms.InterfaceFilterForm
    table = tables.InterfaceTable
    action_buttons = ('import', 'export')


class InterfaceView(generic.ObjectView):
    queryset = Interface.objects.all()

    def get_extra_context(self, request, instance):
        # Get assigned IP addresses
        ipaddress_table = AssignedIPAddressesTable(
            data=instance.ip_addresses.restrict(request.user, 'view').prefetch_related('vrf', 'tenant'),
            orderable=False
        )

        # Get child interfaces
        child_interfaces = Interface.objects.restrict(request.user, 'view').filter(parent=instance)
        child_interfaces_tables = tables.InterfaceTable(
            child_interfaces,
            exclude=('device', 'parent'),
            orderable=False
        )

        # Get assigned VLANs and annotate whether each is tagged or untagged
        vlans = []
        if instance.untagged_vlan is not None:
            vlans.append(instance.untagged_vlan)
            vlans[0].tagged = False
        for vlan in instance.tagged_vlans.restrict(request.user).prefetch_related('site', 'group', 'tenant', 'role'):
            vlan.tagged = True
            vlans.append(vlan)
        vlan_table = InterfaceVLANTable(
            interface=instance,
            data=vlans,
            orderable=False
        )

        return {
            'ipaddress_table': ipaddress_table,
            'child_interfaces_table': child_interfaces_tables,
            'vlan_table': vlan_table,
        }


class InterfaceCreateView(generic.ComponentCreateView):
    queryset = Interface.objects.all()
    form = forms.InterfaceCreateForm
    model_form = forms.InterfaceForm
    template_name = 'dcim/interface_create.html'

    def post(self, request):
        """
        Override inherited post() method to handle request to assign newly created
        interface objects (first object) to an IP Address object.
        """
        form = self.form(request.POST, initial=request.GET)
        new_objs = self.validate_form(request, form)

        if form.is_valid() and not form.errors:
            if '_addanother' in request.POST:
                return redirect(request.get_full_path())
            elif new_objs is not None and '_assignip' in request.POST and len(new_objs) >= 1 and \
                    request.user.has_perm('ipam.add_ipaddress'):
                first_obj = new_objs[0].pk
                return redirect(
                    f'/ipam/ip-addresses/add/?interface={first_obj}&return_url={self.get_return_url(request)}'
                )
            else:
                return redirect(self.get_return_url(request))

        return render(request, self.template_name, {
            'obj_type': self.queryset.model._meta.verbose_name,
            'form': form,
            'return_url': self.get_return_url(request),
        })


class InterfaceEditView(generic.ObjectEditView):
    queryset = Interface.objects.all()
    model_form = forms.InterfaceForm
    template_name = 'dcim/interface_edit.html'


class InterfaceDeleteView(generic.ObjectDeleteView):
    queryset = Interface.objects.all()


class InterfaceBulkImportView(generic.BulkImportView):
    queryset = Interface.objects.all()
    model_form = forms.InterfaceCSVForm
    table = tables.InterfaceTable


class InterfaceBulkEditView(generic.BulkEditView):
    queryset = Interface.objects.all()
    filterset = filtersets.InterfaceFilterSet
    table = tables.InterfaceTable
    form = forms.InterfaceBulkEditForm


class InterfaceBulkRenameView(generic.BulkRenameView):
    queryset = Interface.objects.all()


class InterfaceBulkDisconnectView(BulkDisconnectView):
    queryset = Interface.objects.all()


class InterfaceBulkDeleteView(generic.BulkDeleteView):
    queryset = Interface.objects.all()
    filterset = filtersets.InterfaceFilterSet
    table = tables.InterfaceTable


#
# Front ports
#

class FrontPortListView(generic.ObjectListView):
    queryset = FrontPort.objects.all()
    filterset = filtersets.FrontPortFilterSet
    filterset_form = forms.FrontPortFilterForm
    table = tables.FrontPortTable
    action_buttons = ('import', 'export')


class FrontPortView(generic.ObjectView):
    queryset = FrontPort.objects.all()


class FrontPortCreateView(generic.ComponentCreateView):
    queryset = FrontPort.objects.all()
    form = forms.FrontPortCreateForm
    model_form = forms.FrontPortForm


class FrontPortEditView(generic.ObjectEditView):
    queryset = FrontPort.objects.all()
    model_form = forms.FrontPortForm
    template_name = 'dcim/device_component_edit.html'


class FrontPortDeleteView(generic.ObjectDeleteView):
    queryset = FrontPort.objects.all()


class FrontPortBulkImportView(generic.BulkImportView):
    queryset = FrontPort.objects.all()
    model_form = forms.FrontPortCSVForm
    table = tables.FrontPortTable


class FrontPortBulkEditView(generic.BulkEditView):
    queryset = FrontPort.objects.all()
    filterset = filtersets.FrontPortFilterSet
    table = tables.FrontPortTable
    form = forms.FrontPortBulkEditForm


class FrontPortBulkRenameView(generic.BulkRenameView):
    queryset = FrontPort.objects.all()


class FrontPortBulkDisconnectView(BulkDisconnectView):
    queryset = FrontPort.objects.all()


class FrontPortBulkDeleteView(generic.BulkDeleteView):
    queryset = FrontPort.objects.all()
    filterset = filtersets.FrontPortFilterSet
    table = tables.FrontPortTable


#
# Rear ports
#

class RearPortListView(generic.ObjectListView):
    queryset = RearPort.objects.all()
    filterset = filtersets.RearPortFilterSet
    filterset_form = forms.RearPortFilterForm
    table = tables.RearPortTable
    action_buttons = ('import', 'export')


class RearPortView(generic.ObjectView):
    queryset = RearPort.objects.all()


class RearPortCreateView(generic.ComponentCreateView):
    queryset = RearPort.objects.all()
    form = forms.RearPortCreateForm
    model_form = forms.RearPortForm


class RearPortEditView(generic.ObjectEditView):
    queryset = RearPort.objects.all()
    model_form = forms.RearPortForm
    template_name = 'dcim/device_component_edit.html'


class RearPortDeleteView(generic.ObjectDeleteView):
    queryset = RearPort.objects.all()


class RearPortBulkImportView(generic.BulkImportView):
    queryset = RearPort.objects.all()
    model_form = forms.RearPortCSVForm
    table = tables.RearPortTable


class RearPortBulkEditView(generic.BulkEditView):
    queryset = RearPort.objects.all()
    filterset = filtersets.RearPortFilterSet
    table = tables.RearPortTable
    form = forms.RearPortBulkEditForm


class RearPortBulkRenameView(generic.BulkRenameView):
    queryset = RearPort.objects.all()


class RearPortBulkDisconnectView(BulkDisconnectView):
    queryset = RearPort.objects.all()


class RearPortBulkDeleteView(generic.BulkDeleteView):
    queryset = RearPort.objects.all()
    filterset = filtersets.RearPortFilterSet
    table = tables.RearPortTable


#
# Module bays
#

class ModuleBayListView(generic.ObjectListView):
    queryset = ModuleBay.objects.select_related('installed_module__module_type')
    filterset = filtersets.ModuleBayFilterSet
    filterset_form = forms.ModuleBayFilterForm
    table = tables.ModuleBayTable
    action_buttons = ('import', 'export')


class ModuleBayView(generic.ObjectView):
    queryset = ModuleBay.objects.all()


class ModuleBayCreateView(generic.ComponentCreateView):
    queryset = ModuleBay.objects.all()
    form = forms.ModuleBayCreateForm
    model_form = forms.ModuleBayForm


class ModuleBayEditView(generic.ObjectEditView):
    queryset = ModuleBay.objects.all()
    model_form = forms.ModuleBayForm
    template_name = 'dcim/device_component_edit.html'


class ModuleBayDeleteView(generic.ObjectDeleteView):
    queryset = ModuleBay.objects.all()


class ModuleBayBulkImportView(generic.BulkImportView):
    queryset = ModuleBay.objects.all()
    model_form = forms.ModuleBayCSVForm
    table = tables.ModuleBayTable


class ModuleBayBulkEditView(generic.BulkEditView):
    queryset = ModuleBay.objects.all()
    filterset = filtersets.ModuleBayFilterSet
    table = tables.ModuleBayTable
    form = forms.ModuleBayBulkEditForm


class ModuleBayBulkRenameView(generic.BulkRenameView):
    queryset = ModuleBay.objects.all()


class ModuleBayBulkDeleteView(generic.BulkDeleteView):
    queryset = ModuleBay.objects.all()
    filterset = filtersets.ModuleBayFilterSet
    table = tables.ModuleBayTable


#
# Device bays
#

class DeviceBayListView(generic.ObjectListView):
    queryset = DeviceBay.objects.all()
    filterset = filtersets.DeviceBayFilterSet
    filterset_form = forms.DeviceBayFilterForm
    table = tables.DeviceBayTable
    action_buttons = ('import', 'export')


class DeviceBayView(generic.ObjectView):
    queryset = DeviceBay.objects.all()


class DeviceBayCreateView(generic.ComponentCreateView):
    queryset = DeviceBay.objects.all()
    form = forms.DeviceBayCreateForm
    model_form = forms.DeviceBayForm


class DeviceBayEditView(generic.ObjectEditView):
    queryset = DeviceBay.objects.all()
    model_form = forms.DeviceBayForm
    template_name = 'dcim/device_component_edit.html'


class DeviceBayDeleteView(generic.ObjectDeleteView):
    queryset = DeviceBay.objects.all()


class DeviceBayPopulateView(generic.ObjectEditView):
    queryset = DeviceBay.objects.all()

    def get(self, request, pk):
        device_bay = get_object_or_404(self.queryset, pk=pk)
        form = forms.PopulateDeviceBayForm(device_bay)

        return render(request, 'dcim/devicebay_populate.html', {
            'device_bay': device_bay,
            'form': form,
            'return_url': self.get_return_url(request, device_bay),
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
            'return_url': self.get_return_url(request, device_bay),
        })


class DeviceBayDepopulateView(generic.ObjectEditView):
    queryset = DeviceBay.objects.all()

    def get(self, request, pk):
        device_bay = get_object_or_404(self.queryset, pk=pk)
        form = ConfirmationForm()

        return render(request, 'dcim/devicebay_depopulate.html', {
            'device_bay': device_bay,
            'form': form,
            'return_url': self.get_return_url(request, device_bay),
        })

    def post(self, request, pk):
        device_bay = get_object_or_404(self.queryset, pk=pk)
        form = ConfirmationForm(request.POST)

        if form.is_valid():

            removed_device = device_bay.installed_device
            device_bay.installed_device = None
            device_bay.save()
            messages.success(request, f"{removed_device} has been removed from {device_bay}.")
            return_url = self.get_return_url(request, device_bay.device)

            return redirect(return_url)

        return render(request, 'dcim/devicebay_depopulate.html', {
            'device_bay': device_bay,
            'form': form,
            'return_url': self.get_return_url(request, device_bay),
        })


class DeviceBayBulkImportView(generic.BulkImportView):
    queryset = DeviceBay.objects.all()
    model_form = forms.DeviceBayCSVForm
    table = tables.DeviceBayTable


class DeviceBayBulkEditView(generic.BulkEditView):
    queryset = DeviceBay.objects.all()
    filterset = filtersets.DeviceBayFilterSet
    table = tables.DeviceBayTable
    form = forms.DeviceBayBulkEditForm


class DeviceBayBulkRenameView(generic.BulkRenameView):
    queryset = DeviceBay.objects.all()


class DeviceBayBulkDeleteView(generic.BulkDeleteView):
    queryset = DeviceBay.objects.all()
    filterset = filtersets.DeviceBayFilterSet
    table = tables.DeviceBayTable


#
# Inventory items
#

class InventoryItemListView(generic.ObjectListView):
    queryset = InventoryItem.objects.all()
    filterset = filtersets.InventoryItemFilterSet
    filterset_form = forms.InventoryItemFilterForm
    table = tables.InventoryItemTable
    action_buttons = ('import', 'export')


class InventoryItemView(generic.ObjectView):
    queryset = InventoryItem.objects.all()


class InventoryItemEditView(generic.ObjectEditView):
    queryset = InventoryItem.objects.all()
    model_form = forms.InventoryItemForm


class InventoryItemCreateView(generic.ComponentCreateView):
    queryset = InventoryItem.objects.all()
    form = forms.InventoryItemCreateForm
    model_form = forms.InventoryItemForm


class InventoryItemDeleteView(generic.ObjectDeleteView):
    queryset = InventoryItem.objects.all()


class InventoryItemBulkImportView(generic.BulkImportView):
    queryset = InventoryItem.objects.all()
    model_form = forms.InventoryItemCSVForm
    table = tables.InventoryItemTable


class InventoryItemBulkEditView(generic.BulkEditView):
    queryset = InventoryItem.objects.prefetch_related('device', 'manufacturer')
    filterset = filtersets.InventoryItemFilterSet
    table = tables.InventoryItemTable
    form = forms.InventoryItemBulkEditForm


class InventoryItemBulkRenameView(generic.BulkRenameView):
    queryset = InventoryItem.objects.all()


class InventoryItemBulkDeleteView(generic.BulkDeleteView):
    queryset = InventoryItem.objects.prefetch_related('device', 'manufacturer')
    table = tables.InventoryItemTable
    template_name = 'dcim/inventoryitem_bulk_delete.html'


#
# Inventory item roles
#

class InventoryItemRoleListView(generic.ObjectListView):
    queryset = InventoryItemRole.objects.annotate(
        inventoryitem_count=count_related(InventoryItem, 'role'),
    )
    filterset = filtersets.InventoryItemRoleFilterSet
    filterset_form = forms.InventoryItemRoleFilterForm
    table = tables.InventoryItemRoleTable


class InventoryItemRoleView(generic.ObjectView):
    queryset = InventoryItemRole.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'inventoryitem_count': InventoryItem.objects.filter(role=instance).count(),
        }


class InventoryItemRoleEditView(generic.ObjectEditView):
    queryset = InventoryItemRole.objects.all()
    model_form = forms.InventoryItemRoleForm


class InventoryItemRoleDeleteView(generic.ObjectDeleteView):
    queryset = InventoryItemRole.objects.all()


class InventoryItemRoleBulkImportView(generic.BulkImportView):
    queryset = InventoryItemRole.objects.all()
    model_form = forms.InventoryItemRoleCSVForm
    table = tables.InventoryItemRoleTable


class InventoryItemRoleBulkEditView(generic.BulkEditView):
    queryset = InventoryItemRole.objects.annotate(
        inventoryitem_count=count_related(InventoryItem, 'role'),
    )
    filterset = filtersets.InventoryItemRoleFilterSet
    table = tables.InventoryItemRoleTable
    form = forms.InventoryItemRoleBulkEditForm


class InventoryItemRoleBulkDeleteView(generic.BulkDeleteView):
    queryset = InventoryItemRole.objects.annotate(
        inventoryitem_count=count_related(InventoryItem, 'role'),
    )
    table = tables.InventoryItemRoleTable


#
# Bulk Device component creation
#

class DeviceBulkAddConsolePortView(generic.BulkComponentCreateView):
    parent_model = Device
    parent_field = 'device'
    form = forms.ConsolePortBulkCreateForm
    queryset = ConsolePort.objects.all()
    model_form = forms.ConsolePortForm
    filterset = filtersets.DeviceFilterSet
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


class DeviceBulkAddConsoleServerPortView(generic.BulkComponentCreateView):
    parent_model = Device
    parent_field = 'device'
    form = forms.ConsoleServerPortBulkCreateForm
    queryset = ConsoleServerPort.objects.all()
    model_form = forms.ConsoleServerPortForm
    filterset = filtersets.DeviceFilterSet
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


class DeviceBulkAddPowerPortView(generic.BulkComponentCreateView):
    parent_model = Device
    parent_field = 'device'
    form = forms.PowerPortBulkCreateForm
    queryset = PowerPort.objects.all()
    model_form = forms.PowerPortForm
    filterset = filtersets.DeviceFilterSet
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


class DeviceBulkAddPowerOutletView(generic.BulkComponentCreateView):
    parent_model = Device
    parent_field = 'device'
    form = forms.PowerOutletBulkCreateForm
    queryset = PowerOutlet.objects.all()
    model_form = forms.PowerOutletForm
    filterset = filtersets.DeviceFilterSet
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


class DeviceBulkAddInterfaceView(generic.BulkComponentCreateView):
    parent_model = Device
    parent_field = 'device'
    form = forms.InterfaceBulkCreateForm
    queryset = Interface.objects.all()
    model_form = forms.InterfaceForm
    filterset = filtersets.DeviceFilterSet
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


# class DeviceBulkAddFrontPortView(generic.BulkComponentCreateView):
#     parent_model = Device
#     parent_field = 'device'
#     form = forms.FrontPortBulkCreateForm
#     queryset = FrontPort.objects.all()
#     model_form = forms.FrontPortForm
#     filterset = filtersets.DeviceFilterSet
#     table = tables.DeviceTable
#     default_return_url = 'dcim:device_list'


class DeviceBulkAddRearPortView(generic.BulkComponentCreateView):
    parent_model = Device
    parent_field = 'device'
    form = forms.RearPortBulkCreateForm
    queryset = RearPort.objects.all()
    model_form = forms.RearPortForm
    filterset = filtersets.DeviceFilterSet
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


class DeviceBulkAddModuleBayView(generic.BulkComponentCreateView):
    parent_model = Device
    parent_field = 'device'
    form = forms.ModuleBayBulkCreateForm
    queryset = ModuleBay.objects.all()
    model_form = forms.ModuleBayForm
    filterset = filtersets.DeviceFilterSet
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


class DeviceBulkAddDeviceBayView(generic.BulkComponentCreateView):
    parent_model = Device
    parent_field = 'device'
    form = forms.DeviceBayBulkCreateForm
    queryset = DeviceBay.objects.all()
    model_form = forms.DeviceBayForm
    filterset = filtersets.DeviceFilterSet
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


class DeviceBulkAddInventoryItemView(generic.BulkComponentCreateView):
    parent_model = Device
    parent_field = 'device'
    form = forms.InventoryItemBulkCreateForm
    queryset = InventoryItem.objects.all()
    model_form = forms.InventoryItemForm
    filterset = filtersets.DeviceFilterSet
    table = tables.DeviceTable
    default_return_url = 'dcim:device_list'


#
# Cables
#

class CableListView(generic.ObjectListView):
    queryset = Cable.objects.all()
    filterset = filtersets.CableFilterSet
    filterset_form = forms.CableFilterForm
    table = tables.CableTable
    action_buttons = ('import', 'export')


class CableView(generic.ObjectView):
    queryset = Cable.objects.all()


class PathTraceView(generic.ObjectView):
    """
    Trace a cable path beginning from the given path endpoint (origin).
    """
    additional_permissions = ['dcim.view_cable']
    template_name = 'dcim/cable_trace.html'

    def dispatch(self, request, *args, **kwargs):
        model = kwargs.pop('model')
        self.queryset = model.objects.all()

        return super().dispatch(request, *args, **kwargs)

    def get_extra_context(self, request, instance):
        related_paths = []

        # If tracing a PathEndpoint, locate the CablePath (if one exists) by its origin
        if isinstance(instance, PathEndpoint):
            path = instance._path

        # Otherwise, find all CablePaths which traverse the specified object
        else:
            related_paths = CablePath.objects.filter(path__contains=instance).prefetch_related('origin')
            # Check for specification of a particular path (when tracing pass-through ports)
            try:
                path_id = int(request.GET.get('cablepath_id'))
            except TypeError:
                path_id = None
            if path_id in list(related_paths.values_list('pk', flat=True)):
                path = CablePath.objects.get(pk=path_id)
            else:
                path = related_paths.first()

        # No paths found
        if path is None:
            return {
                'path': None
            }

        # Get the total length of the cable and whether the length is definitive (fully defined)
        total_length, is_definitive = path.get_total_length() if path else (None, False)

        # Determine the path to the SVG trace image
        api_viewname = f"{path.origin._meta.app_label}-api:{path.origin._meta.model_name}-trace"
        svg_url = f"{reverse(api_viewname, kwargs={'pk': path.origin.pk})}?render=svg"

        return {
            'path': path,
            'related_paths': related_paths,
            'total_length': total_length,
            'is_definitive': is_definitive,
            'svg_url': svg_url,
        }


class CableCreateView(generic.ObjectEditView):
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

    def alter_object(self, obj, request, url_args, url_kwargs):
        termination_a_type = url_kwargs.get('termination_a_type')
        termination_a_id = url_kwargs.get('termination_a_id')
        termination_b_type_name = url_kwargs.get('termination_b_type')
        self.termination_b_type = ContentType.objects.get(model=termination_b_type_name.replace('-', ''))

        # Initialize Cable termination attributes
        obj.termination_a = termination_a_type.objects.get(pk=termination_a_id)
        obj.termination_b_type = self.termination_b_type

        return obj

    def get(self, request, *args, **kwargs):
        obj = self.get_object(**kwargs)
        obj = self.alter_object(obj, request, args, kwargs)

        # Parse initial data manually to avoid setting field values as lists
        initial_data = {k: request.GET[k] for k in request.GET}

        # Set initial site and rack based on side A termination (if not already set)
        termination_a_site = getattr(obj.termination_a.parent_object, 'site', None)
        if termination_a_site and 'termination_b_region' not in initial_data:
            initial_data['termination_b_region'] = termination_a_site.region
        if termination_a_site and 'termination_b_site_group' not in initial_data:
            initial_data['termination_b_site_group'] = termination_a_site.group
        if 'termination_b_site' not in initial_data:
            initial_data['termination_b_site'] = termination_a_site
        if 'termination_b_rack' not in initial_data:
            initial_data['termination_b_rack'] = getattr(obj.termination_a.parent_object, 'rack', None)

        form = self.model_form(instance=obj, initial=initial_data)

        return render(request, self.template_name, {
            'obj': obj,
            'obj_type': Cable._meta.verbose_name,
            'termination_b_type': self.termination_b_type.name,
            'form': form,
            'return_url': self.get_return_url(request, obj),
        })


class CableEditView(generic.ObjectEditView):
    queryset = Cable.objects.all()
    model_form = forms.CableForm
    template_name = 'dcim/cable_edit.html'


class CableDeleteView(generic.ObjectDeleteView):
    queryset = Cable.objects.all()


class CableBulkImportView(generic.BulkImportView):
    queryset = Cable.objects.all()
    model_form = forms.CableCSVForm
    table = tables.CableTable


class CableBulkEditView(generic.BulkEditView):
    queryset = Cable.objects.prefetch_related('termination_a', 'termination_b')
    filterset = filtersets.CableFilterSet
    table = tables.CableTable
    form = forms.CableBulkEditForm


class CableBulkDeleteView(generic.BulkDeleteView):
    queryset = Cable.objects.prefetch_related('termination_a', 'termination_b')
    filterset = filtersets.CableFilterSet
    table = tables.CableTable


#
# Connections
#

class ConsoleConnectionsListView(generic.ObjectListView):
    queryset = ConsolePort.objects.filter(_path__isnull=False).order_by('device')
    filterset = filtersets.ConsoleConnectionFilterSet
    filterset_form = forms.ConsoleConnectionFilterForm
    table = tables.ConsoleConnectionTable
    template_name = 'dcim/connections_list.html'
    action_buttons = ('export',)

    def get_extra_context(self, request):
        return {
            'title': 'Console Connections'
        }


class PowerConnectionsListView(generic.ObjectListView):
    queryset = PowerPort.objects.filter(_path__isnull=False).order_by('device')
    filterset = filtersets.PowerConnectionFilterSet
    filterset_form = forms.PowerConnectionFilterForm
    table = tables.PowerConnectionTable
    template_name = 'dcim/connections_list.html'
    action_buttons = ('export',)

    def get_extra_context(self, request):
        return {
            'title': 'Power Connections'
        }


class InterfaceConnectionsListView(generic.ObjectListView):
    queryset = Interface.objects.filter(_path__isnull=False).order_by('device')
    filterset = filtersets.InterfaceConnectionFilterSet
    filterset_form = forms.InterfaceConnectionFilterForm
    table = tables.InterfaceConnectionTable
    template_name = 'dcim/connections_list.html'
    action_buttons = ('export',)

    def get_extra_context(self, request):
        return {
            'title': 'Interface Connections'
        }


#
# Virtual chassis
#

class VirtualChassisListView(generic.ObjectListView):
    queryset = VirtualChassis.objects.prefetch_related('master').annotate(
        member_count=count_related(Device, 'virtual_chassis')
    )
    table = tables.VirtualChassisTable
    filterset = filtersets.VirtualChassisFilterSet
    filterset_form = forms.VirtualChassisFilterForm


class VirtualChassisView(generic.ObjectView):
    queryset = VirtualChassis.objects.all()

    def get_extra_context(self, request, instance):
        members = Device.objects.restrict(request.user).filter(virtual_chassis=instance)

        return {
            'members': members,
        }


class VirtualChassisCreateView(generic.ObjectEditView):
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


class VirtualChassisDeleteView(generic.ObjectDeleteView):
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


class VirtualChassisBulkImportView(generic.BulkImportView):
    queryset = VirtualChassis.objects.all()
    model_form = forms.VirtualChassisCSVForm
    table = tables.VirtualChassisTable


class VirtualChassisBulkEditView(generic.BulkEditView):
    queryset = VirtualChassis.objects.all()
    filterset = filtersets.VirtualChassisFilterSet
    table = tables.VirtualChassisTable
    form = forms.VirtualChassisBulkEditForm


class VirtualChassisBulkDeleteView(generic.BulkDeleteView):
    queryset = VirtualChassis.objects.all()
    filterset = filtersets.VirtualChassisFilterSet
    table = tables.VirtualChassisTable


#
# Power panels
#

class PowerPanelListView(generic.ObjectListView):
    queryset = PowerPanel.objects.prefetch_related(
        'site', 'location'
    ).annotate(
        powerfeed_count=count_related(PowerFeed, 'power_panel')
    )
    filterset = filtersets.PowerPanelFilterSet
    filterset_form = forms.PowerPanelFilterForm
    table = tables.PowerPanelTable


class PowerPanelView(generic.ObjectView):
    queryset = PowerPanel.objects.prefetch_related('site', 'location')

    def get_extra_context(self, request, instance):
        power_feeds = PowerFeed.objects.restrict(request.user).filter(power_panel=instance).prefetch_related('rack')
        powerfeed_table = tables.PowerFeedTable(
            data=power_feeds,
            orderable=False
        )
        if request.user.has_perm('dcim.delete_cable'):
            powerfeed_table.columns.show('pk')
        powerfeed_table.exclude = ['power_panel']

        return {
            'powerfeed_table': powerfeed_table,
        }


class PowerPanelEditView(generic.ObjectEditView):
    queryset = PowerPanel.objects.all()
    model_form = forms.PowerPanelForm


class PowerPanelDeleteView(generic.ObjectDeleteView):
    queryset = PowerPanel.objects.all()


class PowerPanelBulkImportView(generic.BulkImportView):
    queryset = PowerPanel.objects.all()
    model_form = forms.PowerPanelCSVForm
    table = tables.PowerPanelTable


class PowerPanelBulkEditView(generic.BulkEditView):
    queryset = PowerPanel.objects.prefetch_related('site', 'location')
    filterset = filtersets.PowerPanelFilterSet
    table = tables.PowerPanelTable
    form = forms.PowerPanelBulkEditForm


class PowerPanelBulkDeleteView(generic.BulkDeleteView):
    queryset = PowerPanel.objects.prefetch_related(
        'site', 'location'
    ).annotate(
        powerfeed_count=count_related(PowerFeed, 'power_panel')
    )
    filterset = filtersets.PowerPanelFilterSet
    table = tables.PowerPanelTable


#
# Power feeds
#

class PowerFeedListView(generic.ObjectListView):
    queryset = PowerFeed.objects.all()
    filterset = filtersets.PowerFeedFilterSet
    filterset_form = forms.PowerFeedFilterForm
    table = tables.PowerFeedTable


class PowerFeedView(generic.ObjectView):
    queryset = PowerFeed.objects.prefetch_related('power_panel', 'rack')


class PowerFeedEditView(generic.ObjectEditView):
    queryset = PowerFeed.objects.all()
    model_form = forms.PowerFeedForm


class PowerFeedDeleteView(generic.ObjectDeleteView):
    queryset = PowerFeed.objects.all()


class PowerFeedBulkImportView(generic.BulkImportView):
    queryset = PowerFeed.objects.all()
    model_form = forms.PowerFeedCSVForm
    table = tables.PowerFeedTable


class PowerFeedBulkEditView(generic.BulkEditView):
    queryset = PowerFeed.objects.prefetch_related('power_panel', 'rack')
    filterset = filtersets.PowerFeedFilterSet
    table = tables.PowerFeedTable
    form = forms.PowerFeedBulkEditForm


class PowerFeedBulkDisconnectView(BulkDisconnectView):
    queryset = PowerFeed.objects.all()


class PowerFeedBulkDeleteView(generic.BulkDeleteView):
    queryset = PowerFeed.objects.prefetch_related('power_panel', 'rack')
    filterset = filtersets.PowerFeedFilterSet
    table = tables.PowerFeedTable
