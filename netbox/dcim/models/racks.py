import decimal
from functools import cached_property

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Count
from django.urls import reverse
from django.utils.translation import gettext as _

from dcim.choices import *
from dcim.constants import *
from dcim.svg import RackElevationSVG
from netbox.models import OrganizationalModel, PrimaryModel
from utilities.choices import ColorChoices
from utilities.fields import ColorField, NaturalOrderingField
from utilities.utils import array_to_string, drange, to_grams
from .device_components import PowerPort
from .devices import Device, Module
from .mixins import WeightMixin
from .power import PowerFeed

__all__ = (
    'Rack',
    'RackReservation',
    'RackRole',
)


#
# Racks
#

class RackRole(OrganizationalModel):
    """
    Racks can be organized by functional role, similar to Devices.
    """
    color = ColorField(
        default=ColorChoices.COLOR_GREY
    )

    def get_absolute_url(self):
        return reverse('dcim:rackrole', args=[self.pk])


class Rack(PrimaryModel, WeightMixin):
    """
    Devices are housed within Racks. Each rack has a defined height measured in rack units, and a front and rear face.
    Each Rack is assigned to a Site and (optionally) a Location.
    """
    name = models.CharField(
        max_length=100
    )
    _name = NaturalOrderingField(
        target_field='name',
        max_length=100,
        blank=True
    )
    facility_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Facility ID',
        help_text=_('Locally-assigned identifier')
    )
    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.PROTECT,
        related_name='racks'
    )
    location = models.ForeignKey(
        to='dcim.Location',
        on_delete=models.SET_NULL,
        related_name='racks',
        blank=True,
        null=True
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='racks',
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=50,
        choices=RackStatusChoices,
        default=RackStatusChoices.STATUS_ACTIVE
    )
    role = models.ForeignKey(
        to='dcim.RackRole',
        on_delete=models.PROTECT,
        related_name='racks',
        blank=True,
        null=True,
        help_text=_('Functional role')
    )
    serial = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Serial number'
    )
    asset_tag = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        verbose_name='Asset tag',
        help_text=_('A unique tag used to identify this rack')
    )
    type = models.CharField(
        choices=RackTypeChoices,
        max_length=50,
        blank=True,
        verbose_name='Type'
    )
    width = models.PositiveSmallIntegerField(
        choices=RackWidthChoices,
        default=RackWidthChoices.WIDTH_19IN,
        verbose_name='Width',
        help_text=_('Rail-to-rail width')
    )
    u_height = models.PositiveSmallIntegerField(
        default=RACK_U_HEIGHT_DEFAULT,
        verbose_name='Height (U)',
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text=_('Height in rack units')
    )
    desc_units = models.BooleanField(
        default=False,
        verbose_name='Descending units',
        help_text=_('Units are numbered top-to-bottom')
    )
    outer_width = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text=_('Outer dimension of rack (width)')
    )
    outer_depth = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text=_('Outer dimension of rack (depth)')
    )
    outer_unit = models.CharField(
        max_length=50,
        choices=RackDimensionUnitChoices,
        blank=True,
    )
    max_weight = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_('Maximum load capacity for the rack')
    )
    # Stores the normalized max weight (in grams) for database ordering
    _abs_max_weight = models.PositiveBigIntegerField(
        blank=True,
        null=True
    )
    mounting_depth = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text=(
            _('Maximum depth of a mounted device, in millimeters. For four-post racks, this is the '
              'distance between the front and rear rails.')
        )
    )

    # Generic relations
    vlan_groups = GenericRelation(
        to='ipam.VLANGroup',
        content_type_field='scope_type',
        object_id_field='scope_id',
        related_query_name='rack'
    )
    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )
    images = GenericRelation(
        to='extras.ImageAttachment'
    )

    clone_fields = (
        'site', 'location', 'tenant', 'status', 'role', 'type', 'width', 'u_height', 'desc_units', 'outer_width',
        'outer_depth', 'outer_unit', 'mounting_depth', 'weight', 'max_weight', 'weight_unit',
    )
    prerequisite_models = (
        'dcim.Site',
    )

    class Meta:
        ordering = ('site', 'location', '_name', 'pk')  # (site, location, name) may be non-unique
        constraints = (
            # Name and facility_id must be unique *only* within a Location
            models.UniqueConstraint(
                fields=('location', 'name'),
                name='%(app_label)s_%(class)s_unique_location_name'
            ),
            models.UniqueConstraint(
                fields=('location', 'facility_id'),
                name='%(app_label)s_%(class)s_unique_location_facility_id'
            ),
        )

    def __str__(self):
        if self.facility_id:
            return f'{self.name} ({self.facility_id})'
        return self.name

    def get_absolute_url(self):
        return reverse('dcim:rack', args=[self.pk])

    def clean(self):
        super().clean()

        # Validate location/site assignment
        if self.site and self.location and self.location.site != self.site:
            raise ValidationError(f"Assigned location must belong to parent site ({self.site}).")

        # Validate outer dimensions and unit
        if (self.outer_width is not None or self.outer_depth is not None) and not self.outer_unit:
            raise ValidationError("Must specify a unit when setting an outer width/depth")

        # Validate max_weight and weight_unit
        if self.max_weight and not self.weight_unit:
            raise ValidationError("Must specify a unit when setting a maximum weight")

        if self.pk:
            # Validate that Rack is tall enough to house the installed Devices
            top_device = Device.objects.filter(
                rack=self
            ).exclude(
                position__isnull=True
            ).order_by('-position').first()
            if top_device:
                min_height = top_device.position + top_device.device_type.u_height - 1
                if self.u_height < min_height:
                    raise ValidationError({
                        'u_height': "Rack must be at least {}U tall to house currently installed devices.".format(
                            min_height
                        )
                    })
            # Validate that Rack was assigned a Location of its same site, if applicable
            if self.location:
                if self.location.site != self.site:
                    raise ValidationError({
                        'location': f"Location must be from the same site, {self.site}."
                    })

    def save(self, *args, **kwargs):

        # Store the given max weight (if any) in grams for use in database ordering
        if self.max_weight and self.weight_unit:
            self._abs_max_weight = to_grams(self.max_weight, self.weight_unit)
        else:
            self._abs_max_weight = None

        # Clear unit if outer width & depth are not set
        if self.outer_width is None and self.outer_depth is None:
            self.outer_unit = ''

        super().save(*args, **kwargs)

    @property
    def units(self):
        """
        Return a list of unit numbers, top to bottom.
        """
        if self.desc_units:
            return drange(decimal.Decimal(1.0), self.u_height + 1, 0.5)
        return drange(self.u_height + decimal.Decimal(0.5), 0.5, -0.5)

    def get_status_color(self):
        return RackStatusChoices.colors.get(self.status)

    def get_rack_units(self, user=None, face=DeviceFaceChoices.FACE_FRONT, exclude=None, expand_devices=True):
        """
        Return a list of rack units as dictionaries. Example: {'device': None, 'face': 0, 'id': 48, 'name': 'U48'}
        Each key 'device' is either a Device or None. By default, multi-U devices are repeated for each U they occupy.

        :param face: Rack face (front or rear)
        :param user: User instance to be used for evaluating device view permissions. If None, all devices
            will be included.
        :param exclude: PK of a Device to exclude (optional); helpful when relocating a Device within a Rack
        :param expand_devices: When True, all units that a device occupies will be listed with each containing a
            reference to the device. When False, only the bottom most unit for a device is included and that unit
            contains a height attribute for the device
        """
        elevation = {}
        for u in self.units:
            u_name = f'U{u}'.split('.')[0] if not u % 1 else f'U{u}'
            elevation[u] = {
                'id': u,
                'name': u_name,
                'face': face,
                'device': None,
                'occupied': False
            }

        # Add devices to rack units list
        if self.pk:

            # Retrieve all devices installed within the rack
            devices = Device.objects.prefetch_related(
                'device_type',
                'device_type__manufacturer',
                'device_role'
            ).annotate(
                devicebay_count=Count('devicebays')
            ).exclude(
                pk=exclude
            ).filter(
                rack=self,
                position__gt=0,
                device_type__u_height__gt=0
            ).filter(
                Q(face=face) | Q(device_type__is_full_depth=True)
            )

            # Determine which devices the user has permission to view
            permitted_device_ids = []
            if user is not None:
                permitted_device_ids = self.devices.restrict(user, 'view').values_list('pk', flat=True)

            for device in devices:
                if expand_devices:
                    for u in drange(device.position, device.position + device.device_type.u_height, 0.5):
                        if user is None or device.pk in permitted_device_ids:
                            elevation[u]['device'] = device
                        elevation[u]['occupied'] = True
                else:
                    if user is None or device.pk in permitted_device_ids:
                        elevation[device.position]['device'] = device
                    elevation[device.position]['occupied'] = True
                    elevation[device.position]['height'] = device.device_type.u_height

        return [u for u in elevation.values()]

    def get_available_units(self, u_height=1, rack_face=None, exclude=None):
        """
        Return a list of units within the rack available to accommodate a device of a given U height (default 1).
        Optionally exclude one or more devices when calculating empty units (needed when moving a device from one
        position to another within a rack).

        :param u_height: Minimum number of contiguous free units required
        :param rack_face: The face of the rack (front or rear) required; 'None' if device is full depth
        :param exclude: List of devices IDs to exclude (useful when moving a device within a rack)
        """
        # Gather all devices which consume U space within the rack
        devices = self.devices.prefetch_related('device_type').filter(position__gte=1)
        if exclude is not None:
            devices = devices.exclude(pk__in=exclude)

        # Initialize the rack unit skeleton
        units = list(self.units)

        # Remove units consumed by installed devices
        for d in devices:
            if rack_face is None or d.face == rack_face or d.device_type.is_full_depth:
                for u in drange(d.position, d.position + d.device_type.u_height, 0.5):
                    try:
                        units.remove(u)
                    except ValueError:
                        # Found overlapping devices in the rack!
                        pass

        # Remove units without enough space above them to accommodate a device of the specified height
        available_units = []
        for u in units:
            if set(drange(u, u + decimal.Decimal(u_height), 0.5)).issubset(units):
                available_units.append(u)

        return list(reversed(available_units))

    def get_reserved_units(self):
        """
        Return a dictionary mapping all reserved units within the rack to their reservation.
        """
        reserved_units = {}
        for reservation in self.reservations.all():
            for u in reservation.units:
                reserved_units[u] = reservation
        return reserved_units

    def get_elevation_svg(
            self,
            face=DeviceFaceChoices.FACE_FRONT,
            user=None,
            unit_width=None,
            unit_height=None,
            legend_width=RACK_ELEVATION_DEFAULT_LEGEND_WIDTH,
            margin_width=RACK_ELEVATION_DEFAULT_MARGIN_WIDTH,
            include_images=True,
            base_url=None,
            highlight_params=None
    ):
        """
        Return an SVG of the rack elevation

        :param face: Enum of [front, rear] representing the desired side of the rack elevation to render
        :param user: User instance to be used for evaluating device view permissions. If None, all devices
            will be included.
        :param unit_width: Width in pixels for the rendered drawing
        :param unit_height: Height of each rack unit for the rendered drawing. Note this is not the total
            height of the elevation
        :param legend_width: Width of the unit legend, in pixels
        :param margin_width: Width of the rigth-hand margin, in pixels
        :param include_images: Embed front/rear device images where available
        :param base_url: Base URL for links and images. If none, URLs will be relative.
        """
        elevation = RackElevationSVG(
            self,
            unit_width=unit_width,
            unit_height=unit_height,
            legend_width=legend_width,
            margin_width=margin_width,
            user=user,
            include_images=include_images,
            base_url=base_url,
            highlight_params=highlight_params
        )

        return elevation.render(face)

    def get_0u_devices(self):
        return self.devices.filter(position=0)

    def get_utilization(self):
        """
        Determine the utilization rate of the rack and return it as a percentage. Occupied and reserved units both count
        as utilized.
        """
        # Determine unoccupied units
        total_units = len(list(self.units))
        available_units = self.get_available_units(u_height=0.5)

        # Remove reserved units
        for ru in self.get_reserved_units():
            for u in drange(ru, ru + 1, 0.5):
                if u in available_units:
                    available_units.remove(u)

        occupied_unit_count = total_units - len(available_units)
        percentage = float(occupied_unit_count) / total_units * 100

        return percentage

    def get_power_utilization(self):
        """
        Determine the utilization rate of power in the rack and return it as a percentage.
        """
        powerfeeds = PowerFeed.objects.filter(rack=self)
        available_power_total = sum(pf.available_power for pf in powerfeeds)
        if not available_power_total:
            return 0

        powerports = []
        for powerfeed in powerfeeds:
            powerports.extend([
                peer for peer in powerfeed.link_peers if isinstance(peer, PowerPort)
            ])

        allocated_draw = sum([
            powerport.get_power_draw()['allocated'] for powerport in powerports
        ])

        return int(allocated_draw / available_power_total * 100)

    @cached_property
    def total_weight(self):
        total_weight = sum(
            device.device_type._abs_weight
            for device in self.devices.exclude(device_type___abs_weight__isnull=True).prefetch_related('device_type')
        )
        total_weight += sum(
            module.module_type._abs_weight
            for module in Module.objects.filter(device__rack=self)
            .exclude(module_type___abs_weight__isnull=True)
            .prefetch_related('module_type')
        )
        if self._abs_weight:
            total_weight += self._abs_weight
        return round(total_weight / 1000, 2)


class RackReservation(PrimaryModel):
    """
    One or more reserved units within a Rack.
    """
    rack = models.ForeignKey(
        to='dcim.Rack',
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    units = ArrayField(
        base_field=models.PositiveSmallIntegerField()
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='rackreservations',
        blank=True,
        null=True
    )
    user = models.ForeignKey(
        to=User,
        on_delete=models.PROTECT
    )
    description = models.CharField(
        max_length=200
    )

    clone_fields = ('rack', 'user', 'tenant')
    prerequisite_models = (
        'dcim.Rack',
    )

    class Meta:
        ordering = ['created', 'pk']

    def __str__(self):
        return "Reservation for rack {}".format(self.rack)

    def get_absolute_url(self):
        return reverse('dcim:rackreservation', args=[self.pk])

    def clean(self):
        super().clean()

        if hasattr(self, 'rack') and self.units:

            # Validate that all specified units exist in the Rack.
            invalid_units = [u for u in self.units if u not in self.rack.units]
            if invalid_units:
                raise ValidationError({
                    'units': "Invalid unit(s) for {}U rack: {}".format(
                        self.rack.u_height,
                        ', '.join([str(u) for u in invalid_units]),
                    ),
                })

            # Check that none of the units has already been reserved for this Rack.
            reserved_units = []
            for resv in self.rack.reservations.exclude(pk=self.pk):
                reserved_units += resv.units
            conflicting_units = [u for u in self.units if u in reserved_units]
            if conflicting_units:
                raise ValidationError({
                    'units': 'The following units have already been reserved: {}'.format(
                        ', '.join([str(u) for u in conflicting_units]),
                    )
                })

    @property
    def unit_list(self):
        return array_to_string(self.units)
