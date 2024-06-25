import traceback

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db.models import Prefetch
from django.forms import ModelMultipleChoiceField, MultipleHiddenInput, modelformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.views.generic import View
from jinja2.exceptions import TemplateError

from circuits.models import Circuit, CircuitTermination
from extras.views import ObjectConfigContextView
from ipam.models import ASN, IPAddress, VLANGroup
from ipam.tables import InterfaceVLANTable
from netbox.constants import DEFAULT_ACTION_PERMISSIONS
from netbox.views import generic
from tenancy.views import ObjectContactsView
from utilities.forms import ConfirmationForm
from utilities.paginator import EnhancedPaginator, get_paginate_count
from utilities.permissions import get_permission_for_model
from utilities.query import count_related
from utilities.query_functions import CollateAsChar
from utilities.views import (
    GetRelatedModelsMixin, GetReturnURLMixin, ObjectPermissionRequiredMixin, ViewTab, register_model_view
)
from virtualization.filtersets import VirtualMachineFilterSet
from virtualization.models import VirtualMachine
from virtualization.tables import VirtualMachineTable
from . import filtersets, forms, tables
from .choices import DeviceFaceChoices
from .models import *

CABLE_TERMINATION_TYPES = {
    'dcim.consoleport': ConsolePort,
    'dcim.consoleserverport': ConsoleServerPort,
    'dcim.powerport': PowerPort,
    'dcim.poweroutlet': PowerOutlet,
    'dcim.interface': Interface,
    'dcim.frontport': FrontPort,
    'dcim.rearport': RearPort,
    'dcim.powerfeed': PowerFeed,
    'circuits.circuittermination': CircuitTermination,
}


class DeviceComponentsView(generic.ObjectChildrenView):
    actions = {
        **DEFAULT_ACTION_PERMISSIONS,
        'bulk_rename': {'change'},
        'bulk_disconnect': {'change'},
    }
    queryset = Device.objects.all()

    def get_children(self, request, parent):
        return self.child_model.objects.restrict(request.user, 'view').filter(device=parent)


class DeviceTypeComponentsView(generic.ObjectChildrenView):
    actions = {
        **DEFAULT_ACTION_PERMISSIONS,
        'bulk_rename': {'change'},
    }
    queryset = DeviceType.objects.all()
    template_name = 'dcim/devicetype/component_templates.html'
    viewname = None  # Used for return_url resolution

    def get_children(self, request, parent):
        return self.child_model.objects.restrict(request.user, 'view').filter(device_type=parent)

    def get_extra_context(self, request, instance):
        return {
            'return_url': reverse(self.viewname, kwargs={'pk': instance.pk}),
        }


class ModuleTypeComponentsView(DeviceComponentsView):
    queryset = ModuleType.objects.all()
    template_name = 'dcim/moduletype/component_templates.html'
    viewname = None  # Used for return_url resolution

    def get_children(self, request, parent):
        return self.child_model.objects.restrict(request.user, 'view').filter(module_type=parent)

    def get_extra_context(self, request, instance):
        return {
            'return_url': reverse(self.viewname, kwargs={'pk': instance.pk}),
        }


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
                    cable_ids = set()
                    for obj in self.queryset.filter(pk__in=form.cleaned_data['pk']):
                        if obj.cable:
                            cable_ids.add(obj.cable.pk)
                            count += 1
                    for cable in Cable.objects.filter(pk__in=cable_ids):
                        cable.delete()

                messages.success(request, _("Disconnected {count} {type}").format(
                    count=count,
                    type=self.queryset.model._meta.verbose_name_plural
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
            related_paths = CablePath.objects.filter(_nodes__contains=instance)
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
        api_viewname = f"{path.origin_type.app_label}-api:{path.origin_type.model}-trace"
        svg_url = f"{reverse(api_viewname, kwargs={'pk': path.origins[0].pk})}?render=svg"

        return {
            'path': path,
            'related_paths': related_paths,
            'total_length': total_length,
            'is_definitive': is_definitive,
            'svg_url': svg_url,
        }


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


@register_model_view(Region)
class RegionView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = Region.objects.all()

    def get_extra_context(self, request, instance):
        regions = instance.get_descendants(include_self=True)

        return {
            'related_models': self.get_related_models(
                request,
                regions,
                extra=(
                    (Location.objects.restrict(request.user, 'view').filter(site__region__in=regions), 'region_id'),
                    (Rack.objects.restrict(request.user, 'view').filter(site__region__in=regions), 'region_id'),
                ),
            ),
        }


@register_model_view(Region, 'edit')
class RegionEditView(generic.ObjectEditView):
    queryset = Region.objects.all()
    form = forms.RegionForm


@register_model_view(Region, 'delete')
class RegionDeleteView(generic.ObjectDeleteView):
    queryset = Region.objects.all()


class RegionBulkImportView(generic.BulkImportView):
    queryset = Region.objects.all()
    model_form = forms.RegionImportForm


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


@register_model_view(Region, 'contacts')
class RegionContactsView(ObjectContactsView):
    queryset = Region.objects.all()


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


@register_model_view(SiteGroup)
class SiteGroupView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = SiteGroup.objects.all()

    def get_extra_context(self, request, instance):
        groups = instance.get_descendants(include_self=True)

        return {
            'related_models': self.get_related_models(
                request,
                groups,
                extra=(
                    (Location.objects.restrict(request.user, 'view').filter(site__group__in=groups), 'site_group_id'),
                    (Rack.objects.restrict(request.user, 'view').filter(site__group__in=groups), 'site_group_id'),
                ),
            ),
        }


@register_model_view(SiteGroup, 'edit')
class SiteGroupEditView(generic.ObjectEditView):
    queryset = SiteGroup.objects.all()
    form = forms.SiteGroupForm


@register_model_view(SiteGroup, 'delete')
class SiteGroupDeleteView(generic.ObjectDeleteView):
    queryset = SiteGroup.objects.all()


class SiteGroupBulkImportView(generic.BulkImportView):
    queryset = SiteGroup.objects.all()
    model_form = forms.SiteGroupImportForm


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


@register_model_view(SiteGroup, 'contacts')
class SiteGroupContactsView(ObjectContactsView):
    queryset = SiteGroup.objects.all()


#
# Sites
#

class SiteListView(generic.ObjectListView):
    queryset = Site.objects.all()
    filterset = filtersets.SiteFilterSet
    filterset_form = forms.SiteFilterForm
    table = tables.SiteTable


@register_model_view(Site)
class SiteView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = Site.objects.prefetch_related('tenant__group')

    def get_extra_context(self, request, instance):
        return {
            'related_models': self.get_related_models(
                request,
                instance,
                [CableTermination, CircuitTermination],
                (
                    (VLANGroup.objects.restrict(request.user, 'view').filter(
                        scope_type=ContentType.objects.get_for_model(Site),
                        scope_id=instance.pk
                    ), 'site'),
                    (ASN.objects.restrict(request.user, 'view').filter(sites=instance), 'site_id'),
                    (Circuit.objects.restrict(request.user, 'view').filter(terminations__site=instance).distinct(),
                     'site_id'),
                ),
            ),
        }


@register_model_view(Site, 'edit')
class SiteEditView(generic.ObjectEditView):
    queryset = Site.objects.all()
    form = forms.SiteForm


@register_model_view(Site, 'delete')
class SiteDeleteView(generic.ObjectDeleteView):
    queryset = Site.objects.all()


class SiteBulkImportView(generic.BulkImportView):
    queryset = Site.objects.all()
    model_form = forms.SiteImportForm


class SiteBulkEditView(generic.BulkEditView):
    queryset = Site.objects.all()
    filterset = filtersets.SiteFilterSet
    table = tables.SiteTable
    form = forms.SiteBulkEditForm


class SiteBulkDeleteView(generic.BulkDeleteView):
    queryset = Site.objects.all()
    filterset = filtersets.SiteFilterSet
    table = tables.SiteTable


@register_model_view(Site, 'contacts')
class SiteContactsView(ObjectContactsView):
    queryset = Site.objects.all()


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


@register_model_view(Location)
class LocationView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = Location.objects.all()

    def get_extra_context(self, request, instance):
        locations = instance.get_descendants(include_self=True)
        return {
            'related_models': self.get_related_models(request, locations, [CableTermination]),
        }


@register_model_view(Location, 'edit')
class LocationEditView(generic.ObjectEditView):
    queryset = Location.objects.all()
    form = forms.LocationForm


@register_model_view(Location, 'delete')
class LocationDeleteView(generic.ObjectDeleteView):
    queryset = Location.objects.all()


class LocationBulkImportView(generic.BulkImportView):
    queryset = Location.objects.all()
    model_form = forms.LocationImportForm


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


@register_model_view(Location, 'contacts')
class LocationContactsView(ObjectContactsView):
    queryset = Location.objects.all()


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


@register_model_view(RackRole)
class RackRoleView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = RackRole.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'related_models': self.get_related_models(request, instance),
        }


@register_model_view(RackRole, 'edit')
class RackRoleEditView(generic.ObjectEditView):
    queryset = RackRole.objects.all()
    form = forms.RackRoleForm


@register_model_view(RackRole, 'delete')
class RackRoleDeleteView(generic.ObjectDeleteView):
    queryset = RackRole.objects.all()


class RackRoleBulkImportView(generic.BulkImportView):
    queryset = RackRole.objects.all()
    model_form = forms.RackRoleImportForm


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
    filterset = filtersets.RackRoleFilterSet
    table = tables.RackRoleTable


#
# Racks
#

class RackListView(generic.ObjectListView):
    queryset = Rack.objects.annotate(
        device_count=count_related(Device, 'rack')
    )
    filterset = filtersets.RackFilterSet
    filterset_form = forms.RackFilterForm
    table = tables.RackTable
    template_name = 'dcim/rack_list.html'


class RackElevationListView(generic.ObjectListView):
    """
    Display a set of rack elevations side-by-side.
    """
    queryset = Rack.objects.prefetch_related('role')

    def get(self, request):

        racks = filtersets.RackFilterSet(request.GET, self.queryset).qs
        total_count = racks.count()

        # Ordering
        ORDERING_CHOICES = {
            'name': 'Name (A-Z)',
            '-name': 'Name (Z-A)',
            'facility_id': 'Facility ID (A-Z)',
            '-facility_id': 'Facility ID (Z-A)',
        }
        sort = request.GET.get('sort', 'name')
        if sort not in ORDERING_CHOICES:
            sort = 'name'
        sort_field = sort.replace("name", "_name")  # Use natural ordering
        racks = racks.order_by(sort_field)

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
            'sort': sort,
            'sort_display_name': ORDERING_CHOICES[sort],
            'sort_choices': ORDERING_CHOICES,
            'rack_face': rack_face,
            'filter_form': forms.RackElevationFilterForm(request.GET),
            'model': self.queryset.model,
        })


@register_model_view(Rack)
class RackView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = Rack.objects.prefetch_related('site__region', 'tenant__group', 'location', 'role')

    def get_extra_context(self, request, instance):
        peer_racks = Rack.objects.restrict(request.user, 'view').filter(site=instance.site)

        if instance.location:
            peer_racks = peer_racks.filter(location=instance.location)
        else:
            peer_racks = peer_racks.filter(location__isnull=True)
        next_rack = peer_racks.filter(_name__gt=instance._name).first()
        prev_rack = peer_racks.filter(_name__lt=instance._name).reverse().first()

        # Determine any additional parameters to pass when embedding the rack elevations
        svg_extra = '&'.join([
            f'highlight=id:{pk}' for pk in request.GET.getlist('device')
        ])

        return {
            'related_models': self.get_related_models(request, instance, [CableTermination]),
            'next_rack': next_rack,
            'prev_rack': prev_rack,
            'svg_extra': svg_extra,
            'peer_racks': peer_racks,
        }


@register_model_view(Rack, 'reservations')
class RackRackReservationsView(generic.ObjectChildrenView):
    queryset = Rack.objects.all()
    child_model = RackReservation
    table = tables.RackReservationTable
    filterset = filtersets.RackReservationFilterSet
    template_name = 'dcim/rack/reservations.html'
    tab = ViewTab(
        label=_('Reservations'),
        badge=lambda obj: obj.reservations.count(),
        permission='dcim.view_rackreservation',
        weight=510
    )

    def get_children(self, request, parent):
        return parent.reservations.restrict(request.user, 'view')


@register_model_view(Rack, 'nonracked_devices', 'nonracked-devices')
class RackNonRackedView(generic.ObjectChildrenView):
    queryset = Rack.objects.all()
    child_model = Device
    table = tables.DeviceTable
    filterset = filtersets.DeviceFilterSet
    template_name = 'dcim/rack/non_racked_devices.html'
    tab = ViewTab(
        label=_('Non-Racked Devices'),
        badge=lambda obj: obj.devices.filter(rack=obj, position__isnull=True, parent_bay__isnull=True).count(),
        weight=500,
        permission='dcim.view_device',
    )

    def get_children(self, request, parent):
        return parent.devices.restrict(request.user, 'view').filter(
            rack=parent, position__isnull=True, parent_bay__isnull=True
        )


@register_model_view(Rack, 'edit')
class RackEditView(generic.ObjectEditView):
    queryset = Rack.objects.all()
    form = forms.RackForm


@register_model_view(Rack, 'delete')
class RackDeleteView(generic.ObjectDeleteView):
    queryset = Rack.objects.all()


class RackBulkImportView(generic.BulkImportView):
    queryset = Rack.objects.all()
    model_form = forms.RackImportForm


class RackBulkEditView(generic.BulkEditView):
    queryset = Rack.objects.all()
    filterset = filtersets.RackFilterSet
    table = tables.RackTable
    form = forms.RackBulkEditForm


class RackBulkDeleteView(generic.BulkDeleteView):
    queryset = Rack.objects.all()
    filterset = filtersets.RackFilterSet
    table = tables.RackTable


@register_model_view(Rack, 'contacts')
class RackContactsView(ObjectContactsView):
    queryset = Rack.objects.all()


#
# Rack reservations
#

class RackReservationListView(generic.ObjectListView):
    queryset = RackReservation.objects.all()
    filterset = filtersets.RackReservationFilterSet
    filterset_form = forms.RackReservationFilterForm
    table = tables.RackReservationTable


@register_model_view(RackReservation)
class RackReservationView(generic.ObjectView):
    queryset = RackReservation.objects.all()


@register_model_view(RackReservation, 'edit')
class RackReservationEditView(generic.ObjectEditView):
    queryset = RackReservation.objects.all()
    form = forms.RackReservationForm

    def alter_object(self, obj, request, args, kwargs):
        if not obj.pk:
            if 'rack' in request.GET:
                obj.rack = get_object_or_404(Rack, pk=request.GET.get('rack'))
            obj.user = request.user
        return obj


@register_model_view(RackReservation, 'delete')
class RackReservationDeleteView(generic.ObjectDeleteView):
    queryset = RackReservation.objects.all()


class RackReservationImportView(generic.BulkImportView):
    queryset = RackReservation.objects.all()
    model_form = forms.RackReservationImportForm

    def save_object(self, object_form, request):
        """
        Assign the currently authenticated user to the RackReservation.
        """
        instance = object_form.save(commit=False)
        instance.user = request.user
        instance.save()

        return instance


class RackReservationBulkEditView(generic.BulkEditView):
    queryset = RackReservation.objects.all()
    filterset = filtersets.RackReservationFilterSet
    table = tables.RackReservationTable
    form = forms.RackReservationBulkEditForm


class RackReservationBulkDeleteView(generic.BulkDeleteView):
    queryset = RackReservation.objects.all()
    filterset = filtersets.RackReservationFilterSet
    table = tables.RackReservationTable


#
# Manufacturers
#

class ManufacturerListView(generic.ObjectListView):
    queryset = Manufacturer.objects.annotate(
        devicetype_count=count_related(DeviceType, 'manufacturer'),
        moduletype_count=count_related(ModuleType, 'manufacturer'),
        inventoryitem_count=count_related(InventoryItem, 'manufacturer'),
        platform_count=count_related(Platform, 'manufacturer')
    )
    filterset = filtersets.ManufacturerFilterSet
    filterset_form = forms.ManufacturerFilterForm
    table = tables.ManufacturerTable


@register_model_view(Manufacturer)
class ManufacturerView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = Manufacturer.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'related_models': self.get_related_models(request, instance, [InventoryItemTemplate]),
        }


@register_model_view(Manufacturer, 'edit')
class ManufacturerEditView(generic.ObjectEditView):
    queryset = Manufacturer.objects.all()
    form = forms.ManufacturerForm


@register_model_view(Manufacturer, 'delete')
class ManufacturerDeleteView(generic.ObjectDeleteView):
    queryset = Manufacturer.objects.all()


class ManufacturerBulkImportView(generic.BulkImportView):
    queryset = Manufacturer.objects.all()
    model_form = forms.ManufacturerImportForm


class ManufacturerBulkEditView(generic.BulkEditView):
    queryset = Manufacturer.objects.annotate(
        devicetype_count=count_related(DeviceType, 'manufacturer'),
        moduletype_count=count_related(ModuleType, 'manufacturer'),
        inventoryitem_count=count_related(InventoryItem, 'manufacturer'),
        platform_count=count_related(Platform, 'manufacturer')
    )
    filterset = filtersets.ManufacturerFilterSet
    table = tables.ManufacturerTable
    form = forms.ManufacturerBulkEditForm


class ManufacturerBulkDeleteView(generic.BulkDeleteView):
    queryset = Manufacturer.objects.annotate(
        devicetype_count=count_related(DeviceType, 'manufacturer'),
        moduletype_count=count_related(ModuleType, 'manufacturer'),
        inventoryitem_count=count_related(InventoryItem, 'manufacturer'),
        platform_count=count_related(Platform, 'manufacturer')
    )
    filterset = filtersets.ManufacturerFilterSet
    table = tables.ManufacturerTable


@register_model_view(Manufacturer, 'contacts')
class ManufacturerContactsView(ObjectContactsView):
    queryset = Manufacturer.objects.all()


#
# Device types
#

class DeviceTypeListView(generic.ObjectListView):
    queryset = DeviceType.objects.annotate(
        instance_count=count_related(Device, 'device_type')
    )
    filterset = filtersets.DeviceTypeFilterSet
    filterset_form = forms.DeviceTypeFilterForm
    table = tables.DeviceTypeTable


@register_model_view(DeviceType)
class DeviceTypeView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = DeviceType.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'related_models': self.get_related_models(request, instance, omit=[
                ConsolePortTemplate, ConsoleServerPortTemplate, DeviceBayTemplate, FrontPortTemplate,
                InventoryItemTemplate, InterfaceTemplate, ModuleBayTemplate, PowerOutletTemplate, PowerPortTemplate,
                RearPortTemplate,
            ]),
        }


@register_model_view(DeviceType, 'edit')
class DeviceTypeEditView(generic.ObjectEditView):
    queryset = DeviceType.objects.all()
    form = forms.DeviceTypeForm


@register_model_view(DeviceType, 'delete')
class DeviceTypeDeleteView(generic.ObjectDeleteView):
    queryset = DeviceType.objects.all()


@register_model_view(DeviceType, 'consoleports', path='console-ports')
class DeviceTypeConsolePortsView(DeviceTypeComponentsView):
    child_model = ConsolePortTemplate
    table = tables.ConsolePortTemplateTable
    filterset = filtersets.ConsolePortTemplateFilterSet
    viewname = 'dcim:devicetype_consoleports'
    tab = ViewTab(
        label=_('Console Ports'),
        badge=lambda obj: obj.console_port_template_count,
        permission='dcim.view_consoleporttemplate',
        weight=550,
        hide_if_empty=True
    )


@register_model_view(DeviceType, 'consoleserverports', path='console-server-ports')
class DeviceTypeConsoleServerPortsView(DeviceTypeComponentsView):
    child_model = ConsoleServerPortTemplate
    table = tables.ConsoleServerPortTemplateTable
    filterset = filtersets.ConsoleServerPortTemplateFilterSet
    viewname = 'dcim:devicetype_consoleserverports'
    tab = ViewTab(
        label=_('Console Server Ports'),
        badge=lambda obj: obj.console_server_port_template_count,
        permission='dcim.view_consoleserverporttemplate',
        weight=560,
        hide_if_empty=True
    )


@register_model_view(DeviceType, 'powerports', path='power-ports')
class DeviceTypePowerPortsView(DeviceTypeComponentsView):
    child_model = PowerPortTemplate
    table = tables.PowerPortTemplateTable
    filterset = filtersets.PowerPortTemplateFilterSet
    viewname = 'dcim:devicetype_powerports'
    tab = ViewTab(
        label=_('Power Ports'),
        badge=lambda obj: obj.power_port_template_count,
        permission='dcim.view_powerporttemplate',
        weight=570,
        hide_if_empty=True
    )


@register_model_view(DeviceType, 'poweroutlets', path='power-outlets')
class DeviceTypePowerOutletsView(DeviceTypeComponentsView):
    child_model = PowerOutletTemplate
    table = tables.PowerOutletTemplateTable
    filterset = filtersets.PowerOutletTemplateFilterSet
    viewname = 'dcim:devicetype_poweroutlets'
    tab = ViewTab(
        label=_('Power Outlets'),
        badge=lambda obj: obj.power_outlet_template_count,
        permission='dcim.view_poweroutlettemplate',
        weight=580,
        hide_if_empty=True
    )


@register_model_view(DeviceType, 'interfaces')
class DeviceTypeInterfacesView(DeviceTypeComponentsView):
    child_model = InterfaceTemplate
    table = tables.InterfaceTemplateTable
    filterset = filtersets.InterfaceTemplateFilterSet
    viewname = 'dcim:devicetype_interfaces'
    tab = ViewTab(
        label=_('Interfaces'),
        badge=lambda obj: obj.interface_template_count,
        permission='dcim.view_interfacetemplate',
        weight=520,
        hide_if_empty=True
    )


@register_model_view(DeviceType, 'frontports', path='front-ports')
class DeviceTypeFrontPortsView(DeviceTypeComponentsView):
    child_model = FrontPortTemplate
    table = tables.FrontPortTemplateTable
    filterset = filtersets.FrontPortTemplateFilterSet
    viewname = 'dcim:devicetype_frontports'
    tab = ViewTab(
        label=_('Front Ports'),
        badge=lambda obj: obj.front_port_template_count,
        permission='dcim.view_frontporttemplate',
        weight=530,
        hide_if_empty=True
    )


@register_model_view(DeviceType, 'rearports', path='rear-ports')
class DeviceTypeRearPortsView(DeviceTypeComponentsView):
    child_model = RearPortTemplate
    table = tables.RearPortTemplateTable
    filterset = filtersets.RearPortTemplateFilterSet
    viewname = 'dcim:devicetype_rearports'
    tab = ViewTab(
        label=_('Rear Ports'),
        badge=lambda obj: obj.rear_port_template_count,
        permission='dcim.view_rearporttemplate',
        weight=540,
        hide_if_empty=True
    )


@register_model_view(DeviceType, 'modulebays', path='module-bays')
class DeviceTypeModuleBaysView(DeviceTypeComponentsView):
    child_model = ModuleBayTemplate
    table = tables.ModuleBayTemplateTable
    filterset = filtersets.ModuleBayTemplateFilterSet
    viewname = 'dcim:devicetype_modulebays'
    tab = ViewTab(
        label=_('Module Bays'),
        badge=lambda obj: obj.module_bay_template_count,
        permission='dcim.view_modulebaytemplate',
        weight=510,
        hide_if_empty=True
    )


@register_model_view(DeviceType, 'devicebays', path='device-bays')
class DeviceTypeDeviceBaysView(DeviceTypeComponentsView):
    child_model = DeviceBayTemplate
    table = tables.DeviceBayTemplateTable
    filterset = filtersets.DeviceBayTemplateFilterSet
    viewname = 'dcim:devicetype_devicebays'
    tab = ViewTab(
        label=_('Device Bays'),
        badge=lambda obj: obj.device_bay_template_count,
        permission='dcim.view_devicebaytemplate',
        weight=500,
        hide_if_empty=True
    )


@register_model_view(DeviceType, 'inventoryitems', path='inventory-items')
class DeviceTypeInventoryItemsView(DeviceTypeComponentsView):
    child_model = InventoryItemTemplate
    table = tables.InventoryItemTemplateTable
    filterset = filtersets.InventoryItemTemplateFilterSet
    viewname = 'dcim:devicetype_inventoryitems'
    tab = ViewTab(
        label=_('Inventory Items'),
        badge=lambda obj: obj.inventory_item_template_count,
        permission='dcim.view_inventoryitemtemplate',
        weight=590,
        hide_if_empty=True
    )


class DeviceTypeImportView(generic.BulkImportView):
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
        'dcim.add_inventoryitemtemplate',
    ]
    queryset = DeviceType.objects.all()
    model_form = forms.DeviceTypeImportForm
    related_object_forms = {
        'console-ports': forms.ConsolePortTemplateImportForm,
        'console-server-ports': forms.ConsoleServerPortTemplateImportForm,
        'power-ports': forms.PowerPortTemplateImportForm,
        'power-outlets': forms.PowerOutletTemplateImportForm,
        'interfaces': forms.InterfaceTemplateImportForm,
        'rear-ports': forms.RearPortTemplateImportForm,
        'front-ports': forms.FrontPortTemplateImportForm,
        'module-bays': forms.ModuleBayTemplateImportForm,
        'device-bays': forms.DeviceBayTemplateImportForm,
        'inventory-items': forms.InventoryItemTemplateImportForm,
    }

    def prep_related_object_data(self, parent, data):
        data.update({'device_type': parent})
        return data


class DeviceTypeBulkEditView(generic.BulkEditView):
    queryset = DeviceType.objects.annotate(
        instance_count=count_related(Device, 'device_type')
    )
    filterset = filtersets.DeviceTypeFilterSet
    table = tables.DeviceTypeTable
    form = forms.DeviceTypeBulkEditForm


class DeviceTypeBulkDeleteView(generic.BulkDeleteView):
    queryset = DeviceType.objects.annotate(
        instance_count=count_related(Device, 'device_type')
    )
    filterset = filtersets.DeviceTypeFilterSet
    table = tables.DeviceTypeTable


#
# Module types
#

class ModuleTypeListView(generic.ObjectListView):
    queryset = ModuleType.objects.annotate(
        instance_count=count_related(Module, 'module_type')
    )
    filterset = filtersets.ModuleTypeFilterSet
    filterset_form = forms.ModuleTypeFilterForm
    table = tables.ModuleTypeTable


@register_model_view(ModuleType)
class ModuleTypeView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = ModuleType.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'related_models': self.get_related_models(request, instance, omit=[
                ConsolePortTemplate, ConsoleServerPortTemplate, DeviceBayTemplate, FrontPortTemplate,
                InventoryItemTemplate, InterfaceTemplate, ModuleBayTemplate, PowerOutletTemplate, PowerPortTemplate,
                RearPortTemplate,
            ]),
        }


@register_model_view(ModuleType, 'edit')
class ModuleTypeEditView(generic.ObjectEditView):
    queryset = ModuleType.objects.all()
    form = forms.ModuleTypeForm


@register_model_view(ModuleType, 'delete')
class ModuleTypeDeleteView(generic.ObjectDeleteView):
    queryset = ModuleType.objects.all()


@register_model_view(ModuleType, 'consoleports', path='console-ports')
class ModuleTypeConsolePortsView(ModuleTypeComponentsView):
    child_model = ConsolePortTemplate
    table = tables.ConsolePortTemplateTable
    filterset = filtersets.ConsolePortTemplateFilterSet
    viewname = 'dcim:moduletype_consoleports'
    tab = ViewTab(
        label=_('Console Ports'),
        badge=lambda obj: obj.consoleporttemplates.count(),
        permission='dcim.view_consoleporttemplate',
        weight=530,
        hide_if_empty=True
    )


@register_model_view(ModuleType, 'consoleserverports', path='console-server-ports')
class ModuleTypeConsoleServerPortsView(ModuleTypeComponentsView):
    child_model = ConsoleServerPortTemplate
    table = tables.ConsoleServerPortTemplateTable
    filterset = filtersets.ConsoleServerPortTemplateFilterSet
    viewname = 'dcim:moduletype_consoleserverports'
    tab = ViewTab(
        label=_('Console Server Ports'),
        badge=lambda obj: obj.consoleserverporttemplates.count(),
        permission='dcim.view_consoleserverporttemplate',
        weight=540,
        hide_if_empty=True
    )


@register_model_view(ModuleType, 'powerports', path='power-ports')
class ModuleTypePowerPortsView(ModuleTypeComponentsView):
    child_model = PowerPortTemplate
    table = tables.PowerPortTemplateTable
    filterset = filtersets.PowerPortTemplateFilterSet
    viewname = 'dcim:moduletype_powerports'
    tab = ViewTab(
        label=_('Power Ports'),
        badge=lambda obj: obj.powerporttemplates.count(),
        permission='dcim.view_powerporttemplate',
        weight=550,
        hide_if_empty=True
    )


@register_model_view(ModuleType, 'poweroutlets', path='power-outlets')
class ModuleTypePowerOutletsView(ModuleTypeComponentsView):
    child_model = PowerOutletTemplate
    table = tables.PowerOutletTemplateTable
    filterset = filtersets.PowerOutletTemplateFilterSet
    viewname = 'dcim:moduletype_poweroutlets'
    tab = ViewTab(
        label=_('Power Outlets'),
        badge=lambda obj: obj.poweroutlettemplates.count(),
        permission='dcim.view_poweroutlettemplate',
        weight=560,
        hide_if_empty=True
    )


@register_model_view(ModuleType, 'interfaces')
class ModuleTypeInterfacesView(ModuleTypeComponentsView):
    child_model = InterfaceTemplate
    table = tables.InterfaceTemplateTable
    filterset = filtersets.InterfaceTemplateFilterSet
    viewname = 'dcim:moduletype_interfaces'
    tab = ViewTab(
        label=_('Interfaces'),
        badge=lambda obj: obj.interfacetemplates.count(),
        permission='dcim.view_interfacetemplate',
        weight=500,
        hide_if_empty=True
    )


@register_model_view(ModuleType, 'frontports', path='front-ports')
class ModuleTypeFrontPortsView(ModuleTypeComponentsView):
    child_model = FrontPortTemplate
    table = tables.FrontPortTemplateTable
    filterset = filtersets.FrontPortTemplateFilterSet
    viewname = 'dcim:moduletype_frontports'
    tab = ViewTab(
        label=_('Front Ports'),
        badge=lambda obj: obj.frontporttemplates.count(),
        permission='dcim.view_frontporttemplate',
        weight=510,
        hide_if_empty=True
    )


@register_model_view(ModuleType, 'rearports', path='rear-ports')
class ModuleTypeRearPortsView(ModuleTypeComponentsView):
    child_model = RearPortTemplate
    table = tables.RearPortTemplateTable
    filterset = filtersets.RearPortTemplateFilterSet
    viewname = 'dcim:moduletype_rearports'
    tab = ViewTab(
        label=_('Rear Ports'),
        badge=lambda obj: obj.rearporttemplates.count(),
        permission='dcim.view_rearporttemplate',
        weight=520,
        hide_if_empty=True
    )


class ModuleTypeImportView(generic.BulkImportView):
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
    related_object_forms = {
        'console-ports': forms.ConsolePortTemplateImportForm,
        'console-server-ports': forms.ConsoleServerPortTemplateImportForm,
        'power-ports': forms.PowerPortTemplateImportForm,
        'power-outlets': forms.PowerOutletTemplateImportForm,
        'interfaces': forms.InterfaceTemplateImportForm,
        'rear-ports': forms.RearPortTemplateImportForm,
        'front-ports': forms.FrontPortTemplateImportForm,
    }

    def prep_related_object_data(self, parent, data):
        data.update({'module_type': parent})
        return data


class ModuleTypeBulkEditView(generic.BulkEditView):
    queryset = ModuleType.objects.annotate(
        instance_count=count_related(Module, 'module_type')
    )
    filterset = filtersets.ModuleTypeFilterSet
    table = tables.ModuleTypeTable
    form = forms.ModuleTypeBulkEditForm


class ModuleTypeBulkDeleteView(generic.BulkDeleteView):
    queryset = ModuleType.objects.annotate(
        instance_count=count_related(Module, 'module_type')
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


@register_model_view(ConsolePortTemplate, 'edit')
class ConsolePortTemplateEditView(generic.ObjectEditView):
    queryset = ConsolePortTemplate.objects.all()
    form = forms.ConsolePortTemplateForm


@register_model_view(ConsolePortTemplate, 'delete')
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


@register_model_view(ConsoleServerPortTemplate, 'edit')
class ConsoleServerPortTemplateEditView(generic.ObjectEditView):
    queryset = ConsoleServerPortTemplate.objects.all()
    form = forms.ConsoleServerPortTemplateForm


@register_model_view(ConsoleServerPortTemplate, 'delete')
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


@register_model_view(PowerPortTemplate, 'edit')
class PowerPortTemplateEditView(generic.ObjectEditView):
    queryset = PowerPortTemplate.objects.all()
    form = forms.PowerPortTemplateForm


@register_model_view(PowerPortTemplate, 'delete')
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


@register_model_view(PowerOutletTemplate, 'edit')
class PowerOutletTemplateEditView(generic.ObjectEditView):
    queryset = PowerOutletTemplate.objects.all()
    form = forms.PowerOutletTemplateForm


@register_model_view(PowerOutletTemplate, 'delete')
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


@register_model_view(InterfaceTemplate, 'edit')
class InterfaceTemplateEditView(generic.ObjectEditView):
    queryset = InterfaceTemplate.objects.all()
    form = forms.InterfaceTemplateForm


@register_model_view(InterfaceTemplate, 'delete')
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


@register_model_view(FrontPortTemplate, 'edit')
class FrontPortTemplateEditView(generic.ObjectEditView):
    queryset = FrontPortTemplate.objects.all()
    form = forms.FrontPortTemplateForm


@register_model_view(FrontPortTemplate, 'delete')
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


@register_model_view(RearPortTemplate, 'edit')
class RearPortTemplateEditView(generic.ObjectEditView):
    queryset = RearPortTemplate.objects.all()
    form = forms.RearPortTemplateForm


@register_model_view(RearPortTemplate, 'delete')
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


@register_model_view(ModuleBayTemplate, 'edit')
class ModuleBayTemplateEditView(generic.ObjectEditView):
    queryset = ModuleBayTemplate.objects.all()
    form = forms.ModuleBayTemplateForm


@register_model_view(ModuleBayTemplate, 'delete')
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


@register_model_view(DeviceBayTemplate, 'edit')
class DeviceBayTemplateEditView(generic.ObjectEditView):
    queryset = DeviceBayTemplate.objects.all()
    form = forms.DeviceBayTemplateForm


@register_model_view(DeviceBayTemplate, 'delete')
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
# Inventory item templates
#

class InventoryItemTemplateCreateView(generic.ComponentCreateView):
    queryset = InventoryItemTemplate.objects.all()
    form = forms.InventoryItemTemplateCreateForm
    model_form = forms.InventoryItemTemplateForm

    def alter_object(self, instance, request):
        # Set component (if any)
        component_type = request.GET.get('component_type')
        component_id = request.GET.get('component_id')

        if component_type and component_id:
            content_type = get_object_or_404(ContentType, pk=component_type)
            instance.component = get_object_or_404(content_type.model_class(), pk=component_id)

        return instance


@register_model_view(InventoryItemTemplate, 'edit')
class InventoryItemTemplateEditView(generic.ObjectEditView):
    queryset = InventoryItemTemplate.objects.all()
    form = forms.InventoryItemTemplateForm


@register_model_view(InventoryItemTemplate, 'delete')
class InventoryItemTemplateDeleteView(generic.ObjectDeleteView):
    queryset = InventoryItemTemplate.objects.all()


class InventoryItemTemplateBulkEditView(generic.BulkEditView):
    queryset = InventoryItemTemplate.objects.all()
    table = tables.InventoryItemTemplateTable
    form = forms.InventoryItemTemplateBulkEditForm


class InventoryItemTemplateBulkRenameView(generic.BulkRenameView):
    queryset = InventoryItemTemplate.objects.all()


class InventoryItemTemplateBulkDeleteView(generic.BulkDeleteView):
    queryset = InventoryItemTemplate.objects.all()
    table = tables.InventoryItemTemplateTable


#
# Device roles
#

class DeviceRoleListView(generic.ObjectListView):
    queryset = DeviceRole.objects.annotate(
        device_count=count_related(Device, 'role'),
        vm_count=count_related(VirtualMachine, 'role')
    )
    filterset = filtersets.DeviceRoleFilterSet
    filterset_form = forms.DeviceRoleFilterForm
    table = tables.DeviceRoleTable


@register_model_view(DeviceRole)
class DeviceRoleView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = DeviceRole.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'related_models': self.get_related_models(request, instance),
        }


@register_model_view(DeviceRole, 'edit')
class DeviceRoleEditView(generic.ObjectEditView):
    queryset = DeviceRole.objects.all()
    form = forms.DeviceRoleForm


@register_model_view(DeviceRole, 'delete')
class DeviceRoleDeleteView(generic.ObjectDeleteView):
    queryset = DeviceRole.objects.all()


class DeviceRoleBulkImportView(generic.BulkImportView):
    queryset = DeviceRole.objects.all()
    model_form = forms.DeviceRoleImportForm


class DeviceRoleBulkEditView(generic.BulkEditView):
    queryset = DeviceRole.objects.annotate(
        device_count=count_related(Device, 'role'),
        vm_count=count_related(VirtualMachine, 'role')
    )
    filterset = filtersets.DeviceRoleFilterSet
    table = tables.DeviceRoleTable
    form = forms.DeviceRoleBulkEditForm


class DeviceRoleBulkDeleteView(generic.BulkDeleteView):
    queryset = DeviceRole.objects.annotate(
        device_count=count_related(Device, 'role'),
        vm_count=count_related(VirtualMachine, 'role')
    )
    filterset = filtersets.DeviceRoleFilterSet
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


@register_model_view(Platform)
class PlatformView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = Platform.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'related_models': self.get_related_models(request, instance),
        }


@register_model_view(Platform, 'edit')
class PlatformEditView(generic.ObjectEditView):
    queryset = Platform.objects.all()
    form = forms.PlatformForm


@register_model_view(Platform, 'delete')
class PlatformDeleteView(generic.ObjectDeleteView):
    queryset = Platform.objects.all()


class PlatformBulkImportView(generic.BulkImportView):
    queryset = Platform.objects.all()
    model_form = forms.PlatformImportForm


class PlatformBulkEditView(generic.BulkEditView):
    queryset = Platform.objects.all()
    filterset = filtersets.PlatformFilterSet
    table = tables.PlatformTable
    form = forms.PlatformBulkEditForm


class PlatformBulkDeleteView(generic.BulkDeleteView):
    queryset = Platform.objects.all()
    filterset = filtersets.PlatformFilterSet
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


@register_model_view(Device)
class DeviceView(generic.ObjectView):
    queryset = Device.objects.all()

    def get_extra_context(self, request, instance):
        # VirtualChassis members
        if instance.virtual_chassis is not None:
            vc_members = Device.objects.restrict(request.user, 'view').filter(
                virtual_chassis=instance.virtual_chassis
            ).order_by('vc_position')
        else:
            vc_members = []

        return {
            'vc_members': vc_members,
            'svg_extra': f'highlight=id:{instance.pk}'
        }


@register_model_view(Device, 'edit')
class DeviceEditView(generic.ObjectEditView):
    queryset = Device.objects.all()
    form = forms.DeviceForm
    template_name = 'dcim/device_edit.html'


@register_model_view(Device, 'delete')
class DeviceDeleteView(generic.ObjectDeleteView):
    queryset = Device.objects.all()


@register_model_view(Device, 'consoleports', path='console-ports')
class DeviceConsolePortsView(DeviceComponentsView):
    child_model = ConsolePort
    table = tables.DeviceConsolePortTable
    filterset = filtersets.ConsolePortFilterSet
    template_name = 'dcim/device/consoleports.html',
    tab = ViewTab(
        label=_('Console Ports'),
        badge=lambda obj: obj.console_port_count,
        permission='dcim.view_consoleport',
        weight=550,
        hide_if_empty=True
    )


@register_model_view(Device, 'consoleserverports', path='console-server-ports')
class DeviceConsoleServerPortsView(DeviceComponentsView):
    child_model = ConsoleServerPort
    table = tables.DeviceConsoleServerPortTable
    filterset = filtersets.ConsoleServerPortFilterSet
    template_name = 'dcim/device/consoleserverports.html'
    tab = ViewTab(
        label=_('Console Server Ports'),
        badge=lambda obj: obj.console_server_port_count,
        permission='dcim.view_consoleserverport',
        weight=560,
        hide_if_empty=True
    )


@register_model_view(Device, 'powerports', path='power-ports')
class DevicePowerPortsView(DeviceComponentsView):
    child_model = PowerPort
    table = tables.DevicePowerPortTable
    filterset = filtersets.PowerPortFilterSet
    template_name = 'dcim/device/powerports.html'
    tab = ViewTab(
        label=_('Power Ports'),
        badge=lambda obj: obj.power_port_count,
        permission='dcim.view_powerport',
        weight=570,
        hide_if_empty=True
    )


@register_model_view(Device, 'poweroutlets', path='power-outlets')
class DevicePowerOutletsView(DeviceComponentsView):
    child_model = PowerOutlet
    table = tables.DevicePowerOutletTable
    filterset = filtersets.PowerOutletFilterSet
    template_name = 'dcim/device/poweroutlets.html'
    tab = ViewTab(
        label=_('Power Outlets'),
        badge=lambda obj: obj.power_outlet_count,
        permission='dcim.view_poweroutlet',
        weight=580,
        hide_if_empty=True
    )


@register_model_view(Device, 'interfaces')
class DeviceInterfacesView(DeviceComponentsView):
    child_model = Interface
    table = tables.DeviceInterfaceTable
    filterset = filtersets.InterfaceFilterSet
    template_name = 'dcim/device/interfaces.html'
    tab = ViewTab(
        label=_('Interfaces'),
        badge=lambda obj: obj.vc_interfaces().count(),
        permission='dcim.view_interface',
        weight=520,
        hide_if_empty=True
    )

    def get_children(self, request, parent):
        return parent.vc_interfaces().restrict(request.user, 'view').prefetch_related(
            Prefetch('ip_addresses', queryset=IPAddress.objects.restrict(request.user)),
            Prefetch('member_interfaces', queryset=Interface.objects.restrict(request.user))
        )


@register_model_view(Device, 'frontports', path='front-ports')
class DeviceFrontPortsView(DeviceComponentsView):
    child_model = FrontPort
    table = tables.DeviceFrontPortTable
    filterset = filtersets.FrontPortFilterSet
    template_name = 'dcim/device/frontports.html'
    tab = ViewTab(
        label=_('Front Ports'),
        badge=lambda obj: obj.front_port_count,
        permission='dcim.view_frontport',
        weight=530,
        hide_if_empty=True
    )


@register_model_view(Device, 'rearports', path='rear-ports')
class DeviceRearPortsView(DeviceComponentsView):
    child_model = RearPort
    table = tables.DeviceRearPortTable
    filterset = filtersets.RearPortFilterSet
    template_name = 'dcim/device/rearports.html'
    tab = ViewTab(
        label=_('Rear Ports'),
        badge=lambda obj: obj.rear_port_count,
        permission='dcim.view_rearport',
        weight=540,
        hide_if_empty=True
    )


@register_model_view(Device, 'modulebays', path='module-bays')
class DeviceModuleBaysView(DeviceComponentsView):
    child_model = ModuleBay
    table = tables.DeviceModuleBayTable
    filterset = filtersets.ModuleBayFilterSet
    template_name = 'dcim/device/modulebays.html'
    actions = {
        **DEFAULT_ACTION_PERMISSIONS,
        'bulk_rename': {'change'},
    }
    tab = ViewTab(
        label=_('Module Bays'),
        badge=lambda obj: obj.module_bay_count,
        permission='dcim.view_modulebay',
        weight=510,
        hide_if_empty=True
    )


@register_model_view(Device, 'devicebays', path='device-bays')
class DeviceDeviceBaysView(DeviceComponentsView):
    child_model = DeviceBay
    table = tables.DeviceDeviceBayTable
    filterset = filtersets.DeviceBayFilterSet
    template_name = 'dcim/device/devicebays.html'
    actions = {
        **DEFAULT_ACTION_PERMISSIONS,
        'bulk_rename': {'change'},
    }
    tab = ViewTab(
        label=_('Device Bays'),
        badge=lambda obj: obj.device_bay_count,
        permission='dcim.view_devicebay',
        weight=500,
        hide_if_empty=True
    )


@register_model_view(Device, 'inventory')
class DeviceInventoryView(DeviceComponentsView):
    child_model = InventoryItem
    table = tables.DeviceInventoryItemTable
    filterset = filtersets.InventoryItemFilterSet
    template_name = 'dcim/device/inventory.html'
    actions = {
        **DEFAULT_ACTION_PERMISSIONS,
        'bulk_rename': {'change'},
    }
    tab = ViewTab(
        label=_('Inventory Items'),
        badge=lambda obj: obj.inventory_item_count,
        permission='dcim.view_inventoryitem',
        weight=590,
        hide_if_empty=True
    )


@register_model_view(Device, 'configcontext', path='config-context')
class DeviceConfigContextView(ObjectConfigContextView):
    queryset = Device.objects.annotate_config_context_data()
    base_template = 'dcim/device/base.html'
    tab = ViewTab(
        label=_('Config Context'),
        weight=2000
    )


@register_model_view(Device, 'render-config')
class DeviceRenderConfigView(generic.ObjectView):
    queryset = Device.objects.all()
    template_name = 'dcim/device/render_config.html'
    tab = ViewTab(
        label=_('Render Config'),
        weight=2100
    )

    def get(self, request, **kwargs):
        instance = self.get_object(**kwargs)
        context = self.get_extra_context(request, instance)

        # If a direct export has been requested, return the rendered template content as a
        # downloadable file.
        if request.GET.get('export'):
            response = HttpResponse(context['rendered_config'], content_type='text')
            filename = f"{instance.name or 'config'}.txt"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        return render(request, self.get_template_name(), {
            'object': instance,
            'tab': self.tab,
            **context,
        })

    def get_extra_context(self, request, instance):
        # Compile context data
        context_data = instance.get_config_context()
        context_data.update({'device': instance})

        # Render the config template
        rendered_config = None
        if config_template := instance.get_config_template():
            try:
                rendered_config = config_template.render(context=context_data)
            except TemplateError as e:
                messages.error(request, f"An error occurred while rendering the template: {e}")
                rendered_config = traceback.format_exc()

        return {
            'config_template': config_template,
            'context_data': context_data,
            'rendered_config': rendered_config,
        }


@register_model_view(Device, 'virtual-machines')
class DeviceVirtualMachinesView(generic.ObjectChildrenView):
    queryset = Device.objects.all()
    child_model = VirtualMachine
    table = VirtualMachineTable
    filterset = VirtualMachineFilterSet
    tab = ViewTab(
        label=_('Virtual Machines'),
        badge=lambda obj: VirtualMachine.objects.filter(cluster=obj.cluster, device=obj).count(),
        weight=2200,
        hide_if_empty=True,
        permission='virtualization.view_virtualmachine'
    )

    def get_children(self, request, parent):
        return self.child_model.objects.restrict(request.user, 'view').filter(cluster=parent.cluster, device=parent)


class DeviceBulkImportView(generic.BulkImportView):
    queryset = Device.objects.all()
    model_form = forms.DeviceImportForm

    def save_object(self, object_form, request):
        obj = object_form.save()

        # For child devices, save the reverse relation to the parent device bay
        if getattr(obj, 'parent_bay', None):
            device_bay = obj.parent_bay
            device_bay.installed_device = obj
            device_bay.save()

        return obj


class DeviceBulkEditView(generic.BulkEditView):
    queryset = Device.objects.prefetch_related('device_type__manufacturer')
    filterset = filtersets.DeviceFilterSet
    table = tables.DeviceTable
    form = forms.DeviceBulkEditForm


class DeviceBulkDeleteView(generic.BulkDeleteView):
    queryset = Device.objects.prefetch_related('device_type__manufacturer')
    filterset = filtersets.DeviceFilterSet
    table = tables.DeviceTable


class DeviceBulkRenameView(generic.BulkRenameView):
    queryset = Device.objects.all()
    filterset = filtersets.DeviceFilterSet
    table = tables.DeviceTable


@register_model_view(Device, 'contacts')
class DeviceContactsView(ObjectContactsView):
    queryset = Device.objects.all()


#
# Modules
#

class ModuleListView(generic.ObjectListView):
    queryset = Module.objects.prefetch_related('module_type__manufacturer')
    filterset = filtersets.ModuleFilterSet
    filterset_form = forms.ModuleFilterForm
    table = tables.ModuleTable


@register_model_view(Module)
class ModuleView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = Module.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'related_models': self.get_related_models(request, instance),
        }


@register_model_view(Module, 'edit')
class ModuleEditView(generic.ObjectEditView):
    queryset = Module.objects.all()
    form = forms.ModuleForm


@register_model_view(Module, 'delete')
class ModuleDeleteView(generic.ObjectDeleteView):
    queryset = Module.objects.all()


class ModuleBulkImportView(generic.BulkImportView):
    queryset = Module.objects.all()
    model_form = forms.ModuleImportForm


class ModuleBulkEditView(generic.BulkEditView):
    queryset = Module.objects.prefetch_related('module_type__manufacturer')
    filterset = filtersets.ModuleFilterSet
    table = tables.ModuleTable
    form = forms.ModuleBulkEditForm


class ModuleBulkDeleteView(generic.BulkDeleteView):
    queryset = Module.objects.prefetch_related('module_type__manufacturer')
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
    template_name = 'dcim/component_list.html'
    actions = {
        **DEFAULT_ACTION_PERMISSIONS,
        'bulk_rename': {'change'},
    }


@register_model_view(ConsolePort)
class ConsolePortView(generic.ObjectView):
    queryset = ConsolePort.objects.all()


class ConsolePortCreateView(generic.ComponentCreateView):
    queryset = ConsolePort.objects.all()
    form = forms.ConsolePortCreateForm
    model_form = forms.ConsolePortForm


@register_model_view(ConsolePort, 'edit')
class ConsolePortEditView(generic.ObjectEditView):
    queryset = ConsolePort.objects.all()
    form = forms.ConsolePortForm


@register_model_view(ConsolePort, 'delete')
class ConsolePortDeleteView(generic.ObjectDeleteView):
    queryset = ConsolePort.objects.all()


class ConsolePortBulkImportView(generic.BulkImportView):
    queryset = ConsolePort.objects.all()
    model_form = forms.ConsolePortImportForm


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


# Trace view
register_model_view(ConsolePort, 'trace', kwargs={'model': ConsolePort})(PathTraceView)


#
# Console server ports
#

class ConsoleServerPortListView(generic.ObjectListView):
    queryset = ConsoleServerPort.objects.all()
    filterset = filtersets.ConsoleServerPortFilterSet
    filterset_form = forms.ConsoleServerPortFilterForm
    table = tables.ConsoleServerPortTable
    template_name = 'dcim/component_list.html'
    actions = {
        **DEFAULT_ACTION_PERMISSIONS,
        'bulk_rename': {'change'},
    }


@register_model_view(ConsoleServerPort)
class ConsoleServerPortView(generic.ObjectView):
    queryset = ConsoleServerPort.objects.all()


class ConsoleServerPortCreateView(generic.ComponentCreateView):
    queryset = ConsoleServerPort.objects.all()
    form = forms.ConsoleServerPortCreateForm
    model_form = forms.ConsoleServerPortForm


@register_model_view(ConsoleServerPort, 'edit')
class ConsoleServerPortEditView(generic.ObjectEditView):
    queryset = ConsoleServerPort.objects.all()
    form = forms.ConsoleServerPortForm


@register_model_view(ConsoleServerPort, 'delete')
class ConsoleServerPortDeleteView(generic.ObjectDeleteView):
    queryset = ConsoleServerPort.objects.all()


class ConsoleServerPortBulkImportView(generic.BulkImportView):
    queryset = ConsoleServerPort.objects.all()
    model_form = forms.ConsoleServerPortImportForm


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


# Trace view
register_model_view(ConsoleServerPort, 'trace', kwargs={'model': ConsoleServerPort})(PathTraceView)


#
# Power ports
#

class PowerPortListView(generic.ObjectListView):
    queryset = PowerPort.objects.all()
    filterset = filtersets.PowerPortFilterSet
    filterset_form = forms.PowerPortFilterForm
    table = tables.PowerPortTable
    template_name = 'dcim/component_list.html'
    actions = {
        **DEFAULT_ACTION_PERMISSIONS,
        'bulk_rename': {'change'},
    }


@register_model_view(PowerPort)
class PowerPortView(generic.ObjectView):
    queryset = PowerPort.objects.all()


class PowerPortCreateView(generic.ComponentCreateView):
    queryset = PowerPort.objects.all()
    form = forms.PowerPortCreateForm
    model_form = forms.PowerPortForm


@register_model_view(PowerPort, 'edit')
class PowerPortEditView(generic.ObjectEditView):
    queryset = PowerPort.objects.all()
    form = forms.PowerPortForm


@register_model_view(PowerPort, 'delete')
class PowerPortDeleteView(generic.ObjectDeleteView):
    queryset = PowerPort.objects.all()


class PowerPortBulkImportView(generic.BulkImportView):
    queryset = PowerPort.objects.all()
    model_form = forms.PowerPortImportForm


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


# Trace view
register_model_view(PowerPort, 'trace', kwargs={'model': PowerPort})(PathTraceView)


#
# Power outlets
#

class PowerOutletListView(generic.ObjectListView):
    queryset = PowerOutlet.objects.all()
    filterset = filtersets.PowerOutletFilterSet
    filterset_form = forms.PowerOutletFilterForm
    table = tables.PowerOutletTable
    template_name = 'dcim/component_list.html'
    actions = {
        **DEFAULT_ACTION_PERMISSIONS,
        'bulk_rename': {'change'},
    }


@register_model_view(PowerOutlet)
class PowerOutletView(generic.ObjectView):
    queryset = PowerOutlet.objects.all()


class PowerOutletCreateView(generic.ComponentCreateView):
    queryset = PowerOutlet.objects.all()
    form = forms.PowerOutletCreateForm
    model_form = forms.PowerOutletForm


@register_model_view(PowerOutlet, 'edit')
class PowerOutletEditView(generic.ObjectEditView):
    queryset = PowerOutlet.objects.all()
    form = forms.PowerOutletForm


@register_model_view(PowerOutlet, 'delete')
class PowerOutletDeleteView(generic.ObjectDeleteView):
    queryset = PowerOutlet.objects.all()


class PowerOutletBulkImportView(generic.BulkImportView):
    queryset = PowerOutlet.objects.all()
    model_form = forms.PowerOutletImportForm


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


# Trace view
register_model_view(PowerOutlet, 'trace', kwargs={'model': PowerOutlet})(PathTraceView)


#
# Interfaces
#

class InterfaceListView(generic.ObjectListView):
    queryset = Interface.objects.all()
    filterset = filtersets.InterfaceFilterSet
    filterset_form = forms.InterfaceFilterForm
    table = tables.InterfaceTable
    template_name = 'dcim/component_list.html'
    actions = {
        **DEFAULT_ACTION_PERMISSIONS,
        'bulk_rename': {'change'},
    }


@register_model_view(Interface)
class InterfaceView(generic.ObjectView):
    queryset = Interface.objects.all()

    def get_extra_context(self, request, instance):
        # Get assigned VDCs
        vdc_table = tables.VirtualDeviceContextTable(
            data=instance.vdcs.restrict(request.user, 'view').prefetch_related('device'),
            exclude=(
                'tenant', 'tenant_group', 'primary_ip', 'primary_ip4', 'primary_ip6', 'oob_ip', 'comments', 'tags',
                'created', 'last_updated', 'actions',
            ),
            orderable=False
        )

        # Get bridge interfaces
        bridge_interfaces = Interface.objects.restrict(request.user, 'view').filter(bridge=instance)
        bridge_interfaces_tables = tables.InterfaceTable(
            bridge_interfaces,
            exclude=('device', 'parent'),
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
            'vdc_table': vdc_table,
            'bridge_interfaces_table': bridge_interfaces_tables,
            'child_interfaces_table': child_interfaces_tables,
            'vlan_table': vlan_table,
        }


class InterfaceCreateView(generic.ComponentCreateView):
    queryset = Interface.objects.all()
    form = forms.InterfaceCreateForm
    model_form = forms.InterfaceForm


@register_model_view(Interface, 'edit')
class InterfaceEditView(generic.ObjectEditView):
    queryset = Interface.objects.all()
    form = forms.InterfaceForm


@register_model_view(Interface, 'delete')
class InterfaceDeleteView(generic.ObjectDeleteView):
    queryset = Interface.objects.all()


class InterfaceBulkImportView(generic.BulkImportView):
    queryset = Interface.objects.all()
    model_form = forms.InterfaceImportForm


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
    # Ensure child interfaces are deleted prior to their parents
    queryset = Interface.objects.order_by('device', 'parent', CollateAsChar('_name'))
    filterset = filtersets.InterfaceFilterSet
    table = tables.InterfaceTable


# Trace view
register_model_view(Interface, 'trace', kwargs={'model': Interface})(PathTraceView)


#
# Front ports
#

class FrontPortListView(generic.ObjectListView):
    queryset = FrontPort.objects.all()
    filterset = filtersets.FrontPortFilterSet
    filterset_form = forms.FrontPortFilterForm
    table = tables.FrontPortTable
    template_name = 'dcim/component_list.html'
    actions = {
        **DEFAULT_ACTION_PERMISSIONS,
        'bulk_rename': {'change'},
    }


@register_model_view(FrontPort)
class FrontPortView(generic.ObjectView):
    queryset = FrontPort.objects.all()


class FrontPortCreateView(generic.ComponentCreateView):
    queryset = FrontPort.objects.all()
    form = forms.FrontPortCreateForm
    model_form = forms.FrontPortForm


@register_model_view(FrontPort, 'edit')
class FrontPortEditView(generic.ObjectEditView):
    queryset = FrontPort.objects.all()
    form = forms.FrontPortForm


@register_model_view(FrontPort, 'delete')
class FrontPortDeleteView(generic.ObjectDeleteView):
    queryset = FrontPort.objects.all()


class FrontPortBulkImportView(generic.BulkImportView):
    queryset = FrontPort.objects.all()
    model_form = forms.FrontPortImportForm


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


# Trace view
register_model_view(FrontPort, 'trace', kwargs={'model': FrontPort})(PathTraceView)


#
# Rear ports
#

class RearPortListView(generic.ObjectListView):
    queryset = RearPort.objects.all()
    filterset = filtersets.RearPortFilterSet
    filterset_form = forms.RearPortFilterForm
    table = tables.RearPortTable
    template_name = 'dcim/component_list.html'
    actions = {
        **DEFAULT_ACTION_PERMISSIONS,
        'bulk_rename': {'change'},
    }


@register_model_view(RearPort)
class RearPortView(generic.ObjectView):
    queryset = RearPort.objects.all()


class RearPortCreateView(generic.ComponentCreateView):
    queryset = RearPort.objects.all()
    form = forms.RearPortCreateForm
    model_form = forms.RearPortForm


@register_model_view(RearPort, 'edit')
class RearPortEditView(generic.ObjectEditView):
    queryset = RearPort.objects.all()
    form = forms.RearPortForm


@register_model_view(RearPort, 'delete')
class RearPortDeleteView(generic.ObjectDeleteView):
    queryset = RearPort.objects.all()


class RearPortBulkImportView(generic.BulkImportView):
    queryset = RearPort.objects.all()
    model_form = forms.RearPortImportForm


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


# Trace view
register_model_view(RearPort, 'trace', kwargs={'model': RearPort})(PathTraceView)


#
# Module bays
#

class ModuleBayListView(generic.ObjectListView):
    queryset = ModuleBay.objects.select_related('installed_module__module_type')
    filterset = filtersets.ModuleBayFilterSet
    filterset_form = forms.ModuleBayFilterForm
    table = tables.ModuleBayTable
    template_name = 'dcim/component_list.html'
    actions = {
        **DEFAULT_ACTION_PERMISSIONS,
        'bulk_rename': {'change'},
    }


@register_model_view(ModuleBay)
class ModuleBayView(generic.ObjectView):
    queryset = ModuleBay.objects.all()


class ModuleBayCreateView(generic.ComponentCreateView):
    queryset = ModuleBay.objects.all()
    form = forms.ModuleBayCreateForm
    model_form = forms.ModuleBayForm


@register_model_view(ModuleBay, 'edit')
class ModuleBayEditView(generic.ObjectEditView):
    queryset = ModuleBay.objects.all()
    form = forms.ModuleBayForm


@register_model_view(ModuleBay, 'delete')
class ModuleBayDeleteView(generic.ObjectDeleteView):
    queryset = ModuleBay.objects.all()


class ModuleBayBulkImportView(generic.BulkImportView):
    queryset = ModuleBay.objects.all()
    model_form = forms.ModuleBayImportForm


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
    template_name = 'dcim/component_list.html'
    actions = {
        **DEFAULT_ACTION_PERMISSIONS,
        'bulk_rename': {'change'},
    }


@register_model_view(DeviceBay)
class DeviceBayView(generic.ObjectView):
    queryset = DeviceBay.objects.all()


class DeviceBayCreateView(generic.ComponentCreateView):
    queryset = DeviceBay.objects.all()
    form = forms.DeviceBayCreateForm
    model_form = forms.DeviceBayForm


@register_model_view(DeviceBay, 'edit')
class DeviceBayEditView(generic.ObjectEditView):
    queryset = DeviceBay.objects.all()
    form = forms.DeviceBayForm


@register_model_view(DeviceBay, 'delete')
class DeviceBayDeleteView(generic.ObjectDeleteView):
    queryset = DeviceBay.objects.all()


@register_model_view(DeviceBay, 'populate')
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
            device_bay.snapshot()
            device_bay.installed_device = form.cleaned_data['installed_device']
            device_bay.save()
            messages.success(request, "Added {} to {}.".format(device_bay.installed_device, device_bay))
            return_url = self.get_return_url(request)

            return redirect(return_url)

        return render(request, 'dcim/devicebay_populate.html', {
            'device_bay': device_bay,
            'form': form,
            'return_url': self.get_return_url(request, device_bay),
        })


@register_model_view(DeviceBay, 'depopulate')
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
            device_bay.snapshot()
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
    model_form = forms.DeviceBayImportForm


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
    template_name = 'dcim/component_list.html'
    actions = {
        **DEFAULT_ACTION_PERMISSIONS,
        'bulk_rename': {'change'},
    }


@register_model_view(InventoryItem)
class InventoryItemView(generic.ObjectView):
    queryset = InventoryItem.objects.all()


@register_model_view(InventoryItem, 'edit')
class InventoryItemEditView(generic.ObjectEditView):
    queryset = InventoryItem.objects.all()
    form = forms.InventoryItemForm


class InventoryItemCreateView(generic.ComponentCreateView):
    queryset = InventoryItem.objects.all()
    form = forms.InventoryItemCreateForm
    model_form = forms.InventoryItemForm


@register_model_view(InventoryItem, 'delete')
class InventoryItemDeleteView(generic.ObjectDeleteView):
    queryset = InventoryItem.objects.all()


class InventoryItemBulkImportView(generic.BulkImportView):
    queryset = InventoryItem.objects.all()
    model_form = forms.InventoryItemImportForm


class InventoryItemBulkEditView(generic.BulkEditView):
    queryset = InventoryItem.objects.all()
    filterset = filtersets.InventoryItemFilterSet
    table = tables.InventoryItemTable
    form = forms.InventoryItemBulkEditForm


class InventoryItemBulkRenameView(generic.BulkRenameView):
    queryset = InventoryItem.objects.all()


class InventoryItemBulkDeleteView(generic.BulkDeleteView):
    queryset = InventoryItem.objects.all()
    filterset = filtersets.InventoryItemFilterSet
    table = tables.InventoryItemTable


@register_model_view(InventoryItem, 'children')
class InventoryItemChildrenView(generic.ObjectChildrenView):
    queryset = InventoryItem.objects.all()
    child_model = InventoryItem
    table = tables.InventoryItemTable
    filterset = filtersets.InventoryItemFilterSet
    tab = ViewTab(
        label=_('Children'),
        badge=lambda obj: obj.child_items.count(),
        permission='dcim.view_inventoryitem',
        hide_if_empty=True,
        weight=5000
    )

    def get_children(self, request, parent):
        return parent.child_items.restrict(request.user, 'view')


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


@register_model_view(InventoryItemRole)
class InventoryItemRoleView(generic.ObjectView):
    queryset = InventoryItemRole.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'inventoryitem_count': InventoryItem.objects.filter(role=instance).count(),
        }


@register_model_view(InventoryItemRole, 'edit')
class InventoryItemRoleEditView(generic.ObjectEditView):
    queryset = InventoryItemRole.objects.all()
    form = forms.InventoryItemRoleForm


@register_model_view(InventoryItemRole, 'delete')
class InventoryItemRoleDeleteView(generic.ObjectDeleteView):
    queryset = InventoryItemRole.objects.all()


class InventoryItemRoleBulkImportView(generic.BulkImportView):
    queryset = InventoryItemRole.objects.all()
    model_form = forms.InventoryItemRoleImportForm


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
    filterset = filtersets.InventoryItemRoleFilterSet
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
    queryset = Cable.objects.prefetch_related(
        'terminations__termination', 'terminations___device', 'terminations___rack', 'terminations___location',
        'terminations___site',
    )
    filterset = filtersets.CableFilterSet
    filterset_form = forms.CableFilterForm
    table = tables.CableTable


@register_model_view(Cable)
class CableView(generic.ObjectView):
    queryset = Cable.objects.all()


@register_model_view(Cable, 'edit')
class CableEditView(generic.ObjectEditView):
    queryset = Cable.objects.all()
    template_name = 'dcim/cable_edit.html'
    htmx_template_name = 'dcim/htmx/cable_edit.html'

    def alter_object(self, obj, request, url_args, url_kwargs):
        """
        Hack into alter_object() to set the form class when editing an existing Cable, since ObjectEditView
        doesn't currently provide a hook for dynamic class resolution.
        """
        a_terminations_type = CABLE_TERMINATION_TYPES.get(
            request.GET.get('a_terminations_type') or request.POST.get('a_terminations_type')
        )
        b_terminations_type = CABLE_TERMINATION_TYPES.get(
            request.GET.get('b_terminations_type') or request.POST.get('b_terminations_type')
        )

        if obj.pk:
            if not a_terminations_type and (termination_a := obj.terminations.filter(cable_end='A').first()):
                a_terminations_type = termination_a.termination._meta.model
            if not b_terminations_type and (termination_b := obj.terminations.filter(cable_end='B').first()):
                b_terminations_type = termination_b.termination._meta.model

        self.form = forms.get_cable_form(a_terminations_type, b_terminations_type)

        return super().alter_object(obj, request, url_args, url_kwargs)

    def get_extra_addanother_params(self, request):

        params = {
            'a_terminations_type': request.GET.get('a_terminations_type'),
            'b_terminations_type': request.GET.get('b_terminations_type')
        }

        for key in request.POST:
            if 'device' in key or 'power_panel' in key or 'circuit' in key:
                params.update({key: request.POST.get(key)})

        return params


@register_model_view(Cable, 'delete')
class CableDeleteView(generic.ObjectDeleteView):
    queryset = Cable.objects.all()


class CableBulkImportView(generic.BulkImportView):
    queryset = Cable.objects.all()
    model_form = forms.CableImportForm


class CableBulkEditView(generic.BulkEditView):
    queryset = Cable.objects.prefetch_related(
        'terminations__termination', 'terminations___device', 'terminations___rack', 'terminations___location',
        'terminations___site',
    )
    filterset = filtersets.CableFilterSet
    table = tables.CableTable
    form = forms.CableBulkEditForm


class CableBulkDeleteView(generic.BulkDeleteView):
    queryset = Cable.objects.prefetch_related(
        'terminations__termination', 'terminations___device', 'terminations___rack', 'terminations___location',
        'terminations___site',
    )
    filterset = filtersets.CableFilterSet
    table = tables.CableTable


#
# Connections
#

class ConsoleConnectionsListView(generic.ObjectListView):
    queryset = ConsolePort.objects.filter(_path__is_complete=True)
    filterset = filtersets.ConsoleConnectionFilterSet
    filterset_form = forms.ConsoleConnectionFilterForm
    table = tables.ConsoleConnectionTable
    template_name = 'dcim/connections_list.html'
    actions = {
        'export': {'view'},
    }

    def get_extra_context(self, request):
        return {
            'title': 'Console Connections'
        }


class PowerConnectionsListView(generic.ObjectListView):
    queryset = PowerPort.objects.filter(_path__is_complete=True)
    filterset = filtersets.PowerConnectionFilterSet
    filterset_form = forms.PowerConnectionFilterForm
    table = tables.PowerConnectionTable
    template_name = 'dcim/connections_list.html'
    actions = {
        'export': {'view'},
    }

    def get_extra_context(self, request):
        return {
            'title': 'Power Connections'
        }


class InterfaceConnectionsListView(generic.ObjectListView):
    queryset = Interface.objects.filter(_path__is_complete=True)
    filterset = filtersets.InterfaceConnectionFilterSet
    filterset_form = forms.InterfaceConnectionFilterForm
    table = tables.InterfaceConnectionTable
    template_name = 'dcim/connections_list.html'
    actions = {
        'export': {'view'},
    }

    def get_extra_context(self, request):
        return {
            'title': 'Interface Connections'
        }


#
# Virtual chassis
#

class VirtualChassisListView(generic.ObjectListView):
    queryset = VirtualChassis.objects.all()
    table = tables.VirtualChassisTable
    filterset = filtersets.VirtualChassisFilterSet
    filterset_form = forms.VirtualChassisFilterForm


@register_model_view(VirtualChassis)
class VirtualChassisView(generic.ObjectView):
    queryset = VirtualChassis.objects.all()

    def get_extra_context(self, request, instance):
        members = Device.objects.restrict(request.user).filter(virtual_chassis=instance)

        return {
            'members': members,
        }


class VirtualChassisCreateView(generic.ObjectEditView):
    queryset = VirtualChassis.objects.all()
    form = forms.VirtualChassisCreateForm
    template_name = 'dcim/virtualchassis_add.html'


@register_model_view(VirtualChassis, 'edit')
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
            'object': virtual_chassis,
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


@register_model_view(VirtualChassis, 'delete')
class VirtualChassisDeleteView(generic.ObjectDeleteView):
    queryset = VirtualChassis.objects.all()


@register_model_view(VirtualChassis, 'add_member', path='add-member')
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
                messages.success(request, mark_safe(
                    f'Added member <a href="{device.get_absolute_url()}">{escape(device)}</a>'
                ))

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
            messages.error(request, f'Unable to remove master device {device} from the virtual chassis.')
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
    model_form = forms.VirtualChassisImportForm


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
    queryset = PowerPanel.objects.annotate(
        powerfeed_count=count_related(PowerFeed, 'power_panel')
    )
    filterset = filtersets.PowerPanelFilterSet
    filterset_form = forms.PowerPanelFilterForm
    table = tables.PowerPanelTable


@register_model_view(PowerPanel)
class PowerPanelView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = PowerPanel.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'related_models': self.get_related_models(request, instance),
        }


@register_model_view(PowerPanel, 'edit')
class PowerPanelEditView(generic.ObjectEditView):
    queryset = PowerPanel.objects.all()
    form = forms.PowerPanelForm


@register_model_view(PowerPanel, 'delete')
class PowerPanelDeleteView(generic.ObjectDeleteView):
    queryset = PowerPanel.objects.all()


class PowerPanelBulkImportView(generic.BulkImportView):
    queryset = PowerPanel.objects.all()
    model_form = forms.PowerPanelImportForm


class PowerPanelBulkEditView(generic.BulkEditView):
    queryset = PowerPanel.objects.all()
    filterset = filtersets.PowerPanelFilterSet
    table = tables.PowerPanelTable
    form = forms.PowerPanelBulkEditForm


class PowerPanelBulkDeleteView(generic.BulkDeleteView):
    queryset = PowerPanel.objects.annotate(
        powerfeed_count=count_related(PowerFeed, 'power_panel')
    )
    filterset = filtersets.PowerPanelFilterSet
    table = tables.PowerPanelTable


@register_model_view(PowerPanel, 'contacts')
class PowerPanelContactsView(ObjectContactsView):
    queryset = PowerPanel.objects.all()


#
# Power feeds
#

class PowerFeedListView(generic.ObjectListView):
    queryset = PowerFeed.objects.all()
    filterset = filtersets.PowerFeedFilterSet
    filterset_form = forms.PowerFeedFilterForm
    table = tables.PowerFeedTable


@register_model_view(PowerFeed)
class PowerFeedView(generic.ObjectView):
    queryset = PowerFeed.objects.all()


@register_model_view(PowerFeed, 'edit')
class PowerFeedEditView(generic.ObjectEditView):
    queryset = PowerFeed.objects.all()
    form = forms.PowerFeedForm


@register_model_view(PowerFeed, 'delete')
class PowerFeedDeleteView(generic.ObjectDeleteView):
    queryset = PowerFeed.objects.all()


class PowerFeedBulkImportView(generic.BulkImportView):
    queryset = PowerFeed.objects.all()
    model_form = forms.PowerFeedImportForm


class PowerFeedBulkEditView(generic.BulkEditView):
    queryset = PowerFeed.objects.all()
    filterset = filtersets.PowerFeedFilterSet
    table = tables.PowerFeedTable
    form = forms.PowerFeedBulkEditForm


class PowerFeedBulkDisconnectView(BulkDisconnectView):
    queryset = PowerFeed.objects.all()


class PowerFeedBulkDeleteView(generic.BulkDeleteView):
    queryset = PowerFeed.objects.all()
    filterset = filtersets.PowerFeedFilterSet
    table = tables.PowerFeedTable


# Trace view
register_model_view(PowerFeed, 'trace', kwargs={'model': PowerFeed})(PathTraceView)


# VDC
class VirtualDeviceContextListView(generic.ObjectListView):
    queryset = VirtualDeviceContext.objects.annotate(
        interface_count=count_related(Interface, 'vdcs'),
    )
    filterset = filtersets.VirtualDeviceContextFilterSet
    filterset_form = forms.VirtualDeviceContextFilterForm
    table = tables.VirtualDeviceContextTable


@register_model_view(VirtualDeviceContext)
class VirtualDeviceContextView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = VirtualDeviceContext.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'related_models': self.get_related_models(
                request,
                instance,
                extra=(
                    (Interface.objects.restrict(request.user, 'view').filter(vdcs__in=[instance]), 'vdc_id'),
                ),
            ),
        }


@register_model_view(VirtualDeviceContext, 'edit')
class VirtualDeviceContextEditView(generic.ObjectEditView):
    queryset = VirtualDeviceContext.objects.all()
    form = forms.VirtualDeviceContextForm


@register_model_view(VirtualDeviceContext, 'delete')
class VirtualDeviceContextDeleteView(generic.ObjectDeleteView):
    queryset = VirtualDeviceContext.objects.all()


class VirtualDeviceContextBulkImportView(generic.BulkImportView):
    queryset = VirtualDeviceContext.objects.all()
    model_form = forms.VirtualDeviceContextImportForm


class VirtualDeviceContextBulkEditView(generic.BulkEditView):
    queryset = VirtualDeviceContext.objects.all()
    filterset = filtersets.VirtualDeviceContextFilterSet
    table = tables.VirtualDeviceContextTable
    form = forms.VirtualDeviceContextBulkEditForm


class VirtualDeviceContextBulkDeleteView(generic.BulkDeleteView):
    queryset = VirtualDeviceContext.objects.all()
    filterset = filtersets.VirtualDeviceContextFilterSet
    table = tables.VirtualDeviceContextTable
