from collections import OrderedDict

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Count, Sum
from django.urls import reverse

from dcim.choices import *
from dcim.constants import *
from dcim.elevations import RackElevationSVG
from extras.utils import extras_features
from netbox.models import OrganizationalModel, PrimaryModel
from utilities.choices import ColorChoices
from utilities.fields import ColorField, NaturalOrderingField
from utilities.querysets import RestrictedQuerySet
from utilities.utils import array_to_string
from .device_components import PowerOutlet, PowerPort
from .devices import Device
from .power import PowerFeed

__all__ = (
    'Rack',
    'RackReservation',
    'RackRole',
)


#
# Racks
#

@extras_features('custom_fields', 'custom_links', 'export_templates', 'webhooks')
class RackRole(OrganizationalModel):
    """
    Racks can be organized by functional role, similar to Devices.
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True
    )
    color = ColorField(
        default=ColorChoices.COLOR_GREY
    )
    description = models.CharField(
        max_length=200,
        blank=True,
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dcim:rackrole', args=[self.pk])


@extras_features('custom_fields', 'custom_links', 'export_templates', 'tags', 'webhooks')
class Rack(PrimaryModel):
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
        help_text='Locally-assigned identifier'
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
        help_text='Functional role'
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
        help_text='A unique tag used to identify this rack'
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
        help_text='Rail-to-rail width'
    )
    u_height = models.PositiveSmallIntegerField(
        default=RACK_U_HEIGHT_DEFAULT,
        verbose_name='Height (U)',
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text='Height in rack units'
    )
    desc_units = models.BooleanField(
        default=False,
        verbose_name='Descending units',
        help_text='Units are numbered top-to-bottom'
    )
    outer_width = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text='Outer dimension of rack (width)'
    )
    outer_depth = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text='Outer dimension of rack (depth)'
    )
    outer_unit = models.CharField(
        max_length=50,
        choices=RackDimensionUnitChoices,
        blank=True,
    )
    comments = models.TextField(
        blank=True
    )
    images = GenericRelation(
        to='extras.ImageAttachment'
    )

    objects = RestrictedQuerySet.as_manager()

    clone_fields = [
        'site', 'location', 'tenant', 'status', 'role', 'type', 'width', 'u_height', 'desc_units', 'outer_width',
        'outer_depth', 'outer_unit',
    ]

    class Meta:
        ordering = ('site', 'location', '_name', 'pk')  # (site, location, name) may be non-unique
        unique_together = (
            # Name and facility_id must be unique *only* within a Location
            ('location', 'name'),
            ('location', 'facility_id'),
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
        elif self.outer_width is None and self.outer_depth is None:
            self.outer_unit = ''

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

    @property
    def units(self):
        if self.desc_units:
            return range(1, self.u_height + 1)
        else:
            return reversed(range(1, self.u_height + 1))

    def get_status_class(self):
        return RackStatusChoices.CSS_CLASSES.get(self.status)

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

        elevation = OrderedDict()
        for u in self.units:
            elevation[u] = {
                'id': u,
                'name': f'U{u}',
                'face': face,
                'device': None,
                'occupied': False
            }

        # Add devices to rack units list
        if self.pk:

            # Retrieve all devices installed within the rack
            queryset = Device.objects.prefetch_related(
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

            for device in queryset:
                if expand_devices:
                    for u in range(device.position, device.position + device.device_type.u_height):
                        if user is None or device.pk in permitted_device_ids:
                            elevation[u]['device'] = device
                        elevation[u]['occupied'] = True
                else:
                    if user is None or device.pk in permitted_device_ids:
                        elevation[device.position]['device'] = device
                    elevation[device.position]['occupied'] = True
                    elevation[device.position]['height'] = device.device_type.u_height
                    for u in range(device.position + 1, device.position + device.device_type.u_height):
                        elevation.pop(u, None)

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
        units = list(range(1, self.u_height + 1))

        # Remove units consumed by installed devices
        for d in devices:
            if rack_face is None or d.face == rack_face or d.device_type.is_full_depth:
                for u in range(d.position, d.position + d.device_type.u_height):
                    try:
                        units.remove(u)
                    except ValueError:
                        # Found overlapping devices in the rack!
                        pass

        # Remove units without enough space above them to accommodate a device of the specified height
        available_units = []
        for u in units:
            if set(range(u, u + u_height)).issubset(units):
                available_units.append(u)

        return list(reversed(available_units))

    def get_reserved_units(self):
        """
        Return a dictionary mapping all reserved units within the rack to their reservation.
        """
        reserved_units = {}
        for r in self.reservations.all():
            for u in r.units:
                reserved_units[u] = r
        return reserved_units

    def get_elevation_svg(
            self,
            face=DeviceFaceChoices.FACE_FRONT,
            user=None,
            unit_width=settings.RACK_ELEVATION_DEFAULT_UNIT_WIDTH,
            unit_height=settings.RACK_ELEVATION_DEFAULT_UNIT_HEIGHT,
            legend_width=RACK_ELEVATION_LEGEND_WIDTH_DEFAULT,
            include_images=True,
            base_url=None
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
        :param include_images: Embed front/rear device images where available
        :param base_url: Base URL for links and images. If none, URLs will be relative.
        """
        elevation = RackElevationSVG(self, user=user, include_images=include_images, base_url=base_url)

        return elevation.render(face, unit_width, unit_height, legend_width)

    def get_0u_devices(self):
        return self.devices.filter(position=0)

    def get_utilization(self):
        """
        Determine the utilization rate of the rack and return it as a percentage. Occupied and reserved units both count
        as utilized.
        """
        # Determine unoccupied units
        available_units = self.get_available_units()

        # Remove reserved units
        for u in self.get_reserved_units():
            if u in available_units:
                available_units.remove(u)

        occupied_unit_count = self.u_height - len(available_units)
        percentage = int(float(occupied_unit_count) / self.u_height * 100)

        return percentage

    def get_power_utilization(self):
        """
        Determine the utilization rate of power in the rack and return it as a percentage.
        """
        powerfeeds = PowerFeed.objects.filter(rack=self)
        available_power_total = sum(pf.available_power for pf in powerfeeds)
        if not available_power_total:
            return 0

        pf_powerports = PowerPort.objects.filter(
            _cable_peer_type=ContentType.objects.get_for_model(PowerFeed),
            _cable_peer_id__in=powerfeeds.values_list('id', flat=True)
        )
        poweroutlets = PowerOutlet.objects.filter(power_port_id__in=pf_powerports)
        allocated_draw_total = PowerPort.objects.filter(
            _cable_peer_type=ContentType.objects.get_for_model(PowerOutlet),
            _cable_peer_id__in=poweroutlets.values_list('id', flat=True)
        ).aggregate(Sum('allocated_draw'))['allocated_draw__sum'] or 0

        return int(allocated_draw_total / available_power_total * 100)


@extras_features('custom_fields', 'custom_links', 'export_templates', 'tags', 'webhooks')
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

    objects = RestrictedQuerySet.as_manager()

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
