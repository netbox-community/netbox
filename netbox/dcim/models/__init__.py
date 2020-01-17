from collections import OrderedDict
from itertools import count, groupby

import svgwrite
import yaml
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Count, F, ProtectedError, Sum
from django.urls import reverse
from django.utils.http import urlencode
from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager
from timezone_field import TimeZoneField

from dcim.choices import *
from dcim.constants import *
from dcim.fields import ASNField
from extras.models import ConfigContextModel, CustomFieldModel, TaggedItem
from utilities.fields import ColorField
from utilities.managers import NaturalOrderingManager
from utilities.models import ChangeLoggedModel
from utilities.utils import foreground_color, to_meters
from .device_component_templates import (
    ConsolePortTemplate, ConsoleServerPortTemplate, DeviceBayTemplate, FrontPortTemplate, InterfaceTemplate,
    PowerOutletTemplate, PowerPortTemplate, RearPortTemplate,
)
from .device_components import (
    CableTermination, ConsolePort, ConsoleServerPort, DeviceBay, FrontPort, Interface, InventoryItem, PowerOutlet,
    PowerPort, RearPort,
)

__all__ = (
    'Cable',
    'CableTermination',
    'ConsolePort',
    'ConsolePortTemplate',
    'ConsoleServerPort',
    'ConsoleServerPortTemplate',
    'Device',
    'DeviceBay',
    'DeviceBayTemplate',
    'DeviceRole',
    'DeviceType',
    'FrontPort',
    'FrontPortTemplate',
    'Interface',
    'InterfaceTemplate',
    'InventoryItem',
    'Manufacturer',
    'Platform',
    'PowerFeed',
    'PowerOutlet',
    'PowerOutletTemplate',
    'PowerPanel',
    'PowerPort',
    'PowerPortTemplate',
    'Rack',
    'RackGroup',
    'RackReservation',
    'RackRole',
    'RearPort',
    'RearPortTemplate',
    'Region',
    'Site',
    'VirtualChassis',
)


#
# Regions
#

class Region(MPTTModel, ChangeLoggedModel):
    """
    Sites can be grouped within geographic Regions.
    """
    parent = TreeForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True,
        db_index=True
    )
    name = models.CharField(
        max_length=50,
        unique=True
    )
    slug = models.SlugField(
        unique=True
    )

    csv_headers = ['name', 'slug', 'parent']

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "{}?region={}".format(reverse('dcim:site_list'), self.slug)

    def to_csv(self):
        return (
            self.name,
            self.slug,
            self.parent.name if self.parent else None,
        )

    def get_site_count(self):
        return Site.objects.filter(
            Q(region=self) |
            Q(region__in=self.get_descendants())
        ).count()


#
# Sites
#

class Site(ChangeLoggedModel, CustomFieldModel):
    """
    A Site represents a geographic location within a network; typically a building or campus. The optional facility
    field can be used to include an external designation, such as a data center name (e.g. Equinix SV6).
    """
    name = models.CharField(
        max_length=50,
        unique=True
    )
    slug = models.SlugField(
        unique=True
    )
    status = models.CharField(
        max_length=50,
        choices=SiteStatusChoices,
        default=SiteStatusChoices.STATUS_ACTIVE
    )
    region = models.ForeignKey(
        to='dcim.Region',
        on_delete=models.SET_NULL,
        related_name='sites',
        blank=True,
        null=True
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='sites',
        blank=True,
        null=True
    )
    facility = models.CharField(
        max_length=50,
        blank=True
    )
    asn = ASNField(
        blank=True,
        null=True,
        verbose_name='ASN'
    )
    time_zone = TimeZoneField(
        blank=True
    )
    description = models.CharField(
        max_length=100,
        blank=True
    )
    physical_address = models.CharField(
        max_length=200,
        blank=True
    )
    shipping_address = models.CharField(
        max_length=200,
        blank=True
    )
    latitude = models.DecimalField(
        max_digits=8,
        decimal_places=6,
        blank=True,
        null=True
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )
    contact_name = models.CharField(
        max_length=50,
        blank=True
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True
    )
    contact_email = models.EmailField(
        blank=True,
        verbose_name='Contact E-mail'
    )
    comments = models.TextField(
        blank=True
    )
    custom_field_values = GenericRelation(
        to='extras.CustomFieldValue',
        content_type_field='obj_type',
        object_id_field='obj_id'
    )
    images = GenericRelation(
        to='extras.ImageAttachment'
    )

    objects = NaturalOrderingManager()
    tags = TaggableManager(through=TaggedItem)

    csv_headers = [
        'name', 'slug', 'status', 'region', 'tenant', 'facility', 'asn', 'time_zone', 'description', 'physical_address',
        'shipping_address', 'latitude', 'longitude', 'contact_name', 'contact_phone', 'contact_email', 'comments',
    ]
    clone_fields = [
        'status', 'region', 'tenant', 'facility', 'asn', 'time_zone', 'description', 'physical_address',
        'shipping_address', 'latitude', 'longitude', 'contact_name', 'contact_phone', 'contact_email',
    ]

    STATUS_CLASS_MAP = {
        SiteStatusChoices.STATUS_ACTIVE: 'success',
        SiteStatusChoices.STATUS_PLANNED: 'info',
        SiteStatusChoices.STATUS_RETIRED: 'danger',
    }

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dcim:site', args=[self.slug])

    def to_csv(self):
        return (
            self.name,
            self.slug,
            self.get_status_display(),
            self.region.name if self.region else None,
            self.tenant.name if self.tenant else None,
            self.facility,
            self.asn,
            self.time_zone,
            self.description,
            self.physical_address,
            self.shipping_address,
            self.latitude,
            self.longitude,
            self.contact_name,
            self.contact_phone,
            self.contact_email,
            self.comments,
        )

    def get_status_class(self):
        return self.STATUS_CLASS_MAP.get(self.status)


#
# Racks
#

class RackGroup(ChangeLoggedModel):
    """
    Racks can be grouped as subsets within a Site. The scope of a group will depend on how Sites are defined. For
    example, if a Site spans a corporate campus, a RackGroup might be defined to represent each building within that
    campus. If a Site instead represents a single building, a RackGroup might represent a single room or floor.
    """
    name = models.CharField(
        max_length=50
    )
    slug = models.SlugField()
    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.CASCADE,
        related_name='rack_groups'
    )

    csv_headers = ['site', 'name', 'slug']

    class Meta:
        ordering = ['site', 'name']
        unique_together = [
            ['site', 'name'],
            ['site', 'slug'],
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "{}?group_id={}".format(reverse('dcim:rack_list'), self.pk)

    def to_csv(self):
        return (
            self.site,
            self.name,
            self.slug,
        )


class RackRole(ChangeLoggedModel):
    """
    Racks can be organized by functional role, similar to Devices.
    """
    name = models.CharField(
        max_length=50,
        unique=True
    )
    slug = models.SlugField(
        unique=True
    )
    color = ColorField()
    description = models.CharField(
        max_length=100,
        blank=True,
    )

    csv_headers = ['name', 'slug', 'color', 'description']

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "{}?role={}".format(reverse('dcim:rack_list'), self.slug)

    def to_csv(self):
        return (
            self.name,
            self.slug,
            self.color,
            self.description,
        )


class RackElevationHelperMixin:
    """
    Utility class that renders rack elevations. Contains helper methods for rendering elevations as a list of
    rack units represented as dictionaries, or an SVG of the elevation.
    """

    @staticmethod
    def _add_gradient(drawing, id_, color):
        gradient = drawing.linearGradient(
            start=('0', '0%'),
            end=('0', '5%'),
            spreadMethod='repeat',
            id_=id_,
            gradientTransform='rotate(45, 0, 0)',
            gradientUnits='userSpaceOnUse'
        )
        gradient.add_stop_color(offset='0%', color='#f7f7f7')
        gradient.add_stop_color(offset='50%', color='#f7f7f7')
        gradient.add_stop_color(offset='50%', color=color)
        gradient.add_stop_color(offset='100%', color=color)
        drawing.defs.add(gradient)

    @staticmethod
    def _setup_drawing(width, height):
        drawing = svgwrite.Drawing(size=(width, height))

        # add the stylesheet
        with open('{}/css/rack_elevation.css'.format(settings.STATICFILES_DIRS[0])) as css_file:
            drawing.defs.add(drawing.style(css_file.read()))

        # add gradients
        RackElevationHelperMixin._add_gradient(drawing, 'reserved', '#c7c7ff')
        RackElevationHelperMixin._add_gradient(drawing, 'occupied', '#f0f0f0')
        RackElevationHelperMixin._add_gradient(drawing, 'blocked', '#ffc7c7')

        return drawing

    @staticmethod
    def _draw_device_front(drawing, device, start, end, text):
        color = device.device_role.color
        link = drawing.add(
            drawing.a(
                href=reverse('dcim:device', kwargs={'pk': device.pk}),
                target='_top',
                fill='black'
            )
        )
        link.add(drawing.rect(start, end, fill='#{}'.format(color)))
        hex_color = '#{}'.format(foreground_color(color))
        link.add(drawing.text(device.name, insert=text, fill=hex_color))

    @staticmethod
    def _draw_device_rear(drawing, device, start, end, text):
        drawing.add(drawing.rect(start, end, class_="blocked"))
        drawing.add(drawing.text(device.name, insert=text))

    @staticmethod
    def _draw_empty(drawing, rack, start, end, text, id_, face_id, class_):
        link = drawing.add(
            drawing.a(
                href='{}?{}'.format(
                    reverse('dcim:device_add'),
                    urlencode({'rack': rack.pk, 'site': rack.site.pk, 'face': face_id, 'position': id_})
                ),
                target='_top'
            )
        )
        link.add(drawing.rect(start, end, class_=class_))
        link.add(drawing.text("add device", insert=text, class_='add-device'))

    def _draw_elevations(self, elevation, reserved_units, face, unit_width, unit_height):

        drawing = self._setup_drawing(unit_width, unit_height * self.u_height)

        unit_cursor = 0
        for unit in elevation:

            # Loop through all units in the elevation
            device = unit['device']
            height = unit.get('height', 1)

            # Setup drawing coordinates
            start_y = unit_cursor * unit_height
            end_y = unit_height * height
            start_cordinates = (0, start_y)
            end_cordinates = (unit_width, end_y)
            text_cordinates = (unit_width / 2, start_y + end_y / 2)

            # Draw the device
            if device and device.face == face:
                self._draw_device_front(drawing, device, start_cordinates, end_cordinates, text_cordinates)
            elif device and device.device_type.is_full_depth:
                self._draw_device_rear(drawing, device, start_cordinates, end_cordinates, text_cordinates)
            else:
                # Draw shallow devices, reservations, or empty units
                class_ = 'slot'
                if device:
                    class_ += ' occupied'
                if unit["id"] in reserved_units:
                    class_ += ' reserved'
                self._draw_empty(
                    drawing, self, start_cordinates, end_cordinates, text_cordinates, unit["id"], face, class_
                )

            unit_cursor += height

        # Wrap the drawing with a border
        drawing.add(drawing.rect((0, 0), (unit_width, self.u_height * unit_height), class_='rack'))

        return drawing

    def get_elevation_svg(self, face=DeviceFaceChoices.FACE_FRONT, unit_width=230, unit_height=20):
        """
        Return an SVG of the rack elevation

        :param face: Enum of [front, rear] representing the desired side of the rack elevation to render
        :param width: Width in pixles for the rendered drawing
        :param unit_height: Height of each rack unit for the rendered drawing. Note this is not the total
            height of the elevation
        """
        elevation = self.get_rack_units(face=face, expand_devices=False)
        reserved_units = self.get_reserved_units().keys()

        return self._draw_elevations(elevation, reserved_units, face, unit_width, unit_height)


class Rack(ChangeLoggedModel, CustomFieldModel, RackElevationHelperMixin):
    """
    Devices are housed within Racks. Each rack has a defined height measured in rack units, and a front and rear face.
    Each Rack is assigned to a Site and (optionally) a RackGroup.
    """
    name = models.CharField(
        max_length=50
    )
    facility_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Facility ID'
    )
    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.PROTECT,
        related_name='racks'
    )
    group = models.ForeignKey(
        to='dcim.RackGroup',
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
        null=True
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
        default=42,
        verbose_name='Height (U)',
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    desc_units = models.BooleanField(
        default=False,
        verbose_name='Descending units',
        help_text='Units are numbered top-to-bottom'
    )
    outer_width = models.PositiveSmallIntegerField(
        blank=True,
        null=True
    )
    outer_depth = models.PositiveSmallIntegerField(
        blank=True,
        null=True
    )
    outer_unit = models.CharField(
        max_length=50,
        choices=RackDimensionUnitChoices,
        blank=True,
    )
    comments = models.TextField(
        blank=True
    )
    custom_field_values = GenericRelation(
        to='extras.CustomFieldValue',
        content_type_field='obj_type',
        object_id_field='obj_id'
    )
    images = GenericRelation(
        to='extras.ImageAttachment'
    )

    objects = NaturalOrderingManager()
    tags = TaggableManager(through=TaggedItem)

    csv_headers = [
        'site', 'group_name', 'name', 'facility_id', 'tenant', 'status', 'role', 'type', 'serial', 'asset_tag', 'width',
        'u_height', 'desc_units', 'outer_width', 'outer_depth', 'outer_unit', 'comments',
    ]
    clone_fields = [
        'site', 'group', 'tenant', 'status', 'role', 'type', 'width', 'u_height', 'desc_units', 'outer_width',
        'outer_depth', 'outer_unit',
    ]

    STATUS_CLASS_MAP = {
        RackStatusChoices.STATUS_RESERVED: 'warning',
        RackStatusChoices.STATUS_AVAILABLE: 'success',
        RackStatusChoices.STATUS_PLANNED: 'info',
        RackStatusChoices.STATUS_ACTIVE: 'primary',
        RackStatusChoices.STATUS_DEPRECATED: 'danger',
    }

    class Meta:
        ordering = ('site', 'group', 'name', 'pk')  # (site, group, name) may be non-unique
        unique_together = [
            # Name and facility_id must be unique *only* within a RackGroup
            ['group', 'name'],
            ['group', 'facility_id'],
        ]

    def __str__(self):
        return self.display_name or super().__str__()

    def get_absolute_url(self):
        return reverse('dcim:rack', args=[self.pk])

    def clean(self):

        # Validate outer dimensions and unit
        if (self.outer_width is not None or self.outer_depth is not None) and not self.outer_unit:
            raise ValidationError("Must specify a unit when setting an outer width/depth")
        elif self.outer_width is None and self.outer_depth is None:
            self.outer_unit = ''

        if self.pk:
            # Validate that Rack is tall enough to house the installed Devices
            top_device = Device.objects.filter(rack=self).exclude(position__isnull=True).order_by('-position').first()
            if top_device:
                min_height = top_device.position + top_device.device_type.u_height - 1
                if self.u_height < min_height:
                    raise ValidationError({
                        'u_height': "Rack must be at least {}U tall to house currently installed devices.".format(
                            min_height
                        )
                    })
            # Validate that Rack was assigned a group of its same site, if applicable
            if self.group:
                if self.group.site != self.site:
                    raise ValidationError({
                        'group': "Rack group must be from the same site, {}.".format(self.site)
                    })

    def save(self, *args, **kwargs):

        # Record the original site assignment for this rack.
        _site_id = None
        if self.pk:
            _site_id = Rack.objects.get(pk=self.pk).site_id

        super().save(*args, **kwargs)

        # Update racked devices if the assigned Site has been changed.
        if _site_id is not None and self.site_id != _site_id:
            devices = Device.objects.filter(rack=self)
            for device in devices:
                device.site = self.site
                device.save()

    def to_csv(self):
        return (
            self.site.name,
            self.group.name if self.group else None,
            self.name,
            self.facility_id,
            self.tenant.name if self.tenant else None,
            self.get_status_display(),
            self.role.name if self.role else None,
            self.get_type_display() if self.type else None,
            self.serial,
            self.asset_tag,
            self.width,
            self.u_height,
            self.desc_units,
            self.outer_width,
            self.outer_depth,
            self.outer_unit,
            self.comments,
        )

    @property
    def units(self):
        if self.desc_units:
            return range(1, self.u_height + 1)
        else:
            return reversed(range(1, self.u_height + 1))

    @property
    def display_name(self):
        if self.facility_id:
            return "{} ({})".format(self.name, self.facility_id)
        elif self.name:
            return self.name
        return ""

    def get_status_class(self):
        return self.STATUS_CLASS_MAP.get(self.status)

    def get_rack_units(self, face=DeviceFaceChoices.FACE_FRONT, exclude=None, expand_devices=True):
        """
        Return a list of rack units as dictionaries. Example: {'device': None, 'face': 0, 'id': 48, 'name': 'U48'}
        Each key 'device' is either a Device or None. By default, multi-U devices are repeated for each U they occupy.

        :param face: Rack face (front or rear)
        :param exclude: PK of a Device to exclude (optional); helpful when relocating a Device within a Rack
        :param expand_devices: When True, all units that a device occupies will be listed with each containing a
            reference to the device. When False, only the bottom most unit for a device is included and that unit
            contains a height attribute for the device
        """

        elevation = OrderedDict()
        for u in self.units:
            elevation[u] = {'id': u, 'name': 'U{}'.format(u), 'face': face, 'device': None}

        # Add devices to rack units list
        if self.pk:
            queryset = Device.objects.prefetch_related(
                'device_type',
                'device_type__manufacturer',
                'device_role'
            ).annotate(
                devicebay_count=Count('device_bays')
            ).exclude(
                pk=exclude
            ).filter(
                rack=self,
                position__gt=0
            ).filter(
                Q(face=face) | Q(device_type__is_full_depth=True)
            )
            for device in queryset:
                if expand_devices:
                    for u in range(device.position, device.position + device.device_type.u_height):
                        elevation[u]['device'] = device
                else:
                    elevation[device.position]['device'] = device
                    elevation[device.position]['height'] = device.device_type.u_height
                    for u in range(device.position + 1, device.position + device.device_type.u_height):
                        elevation.pop(u, None)

        return [u for u in elevation.values()]

    def get_available_units(self, u_height=1, rack_face=None, exclude=list()):
        """
        Return a list of units within the rack available to accommodate a device of a given U height (default 1).
        Optionally exclude one or more devices when calculating empty units (needed when moving a device from one
        position to another within a rack).

        :param u_height: Minimum number of contiguous free units required
        :param rack_face: The face of the rack (front or rear) required; 'None' if device is full depth
        :param exclude: List of devices IDs to exclude (useful when moving a device within a rack)
        """

        # Gather all devices which consume U space within the rack
        devices = self.devices.prefetch_related('device_type').filter(position__gte=1).exclude(pk__in=exclude)

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
        power_stats = PowerFeed.objects.filter(
            rack=self
        ).annotate(
            allocated_draw_total=Sum('connected_endpoint__poweroutlets__connected_endpoint__allocated_draw'),
        ).values(
            'allocated_draw_total',
            'available_power'
        )

        if power_stats:
            allocated_draw_total = sum(x['allocated_draw_total'] for x in power_stats)
            available_power_total = sum(x['available_power'] for x in power_stats)
            return int(allocated_draw_total / available_power_total * 100) or 0
        return 0


class RackReservation(ChangeLoggedModel):
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
        max_length=100
    )

    class Meta:
        ordering = ['created']

    def __str__(self):
        return "Reservation for rack {}".format(self.rack)

    def clean(self):

        if self.units:

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
        """
        Express the assigned units as a string of summarized ranges. For example:
            [0, 1, 2, 10, 14, 15, 16] => "0-2, 10, 14-16"
        """
        group = (list(x) for _, x in groupby(sorted(self.units), lambda x, c=count(): next(c) - x))
        return ', '.join('-'.join(map(str, (g[0], g[-1])[:len(g)])) for g in group)


#
# Device Types
#

class Manufacturer(ChangeLoggedModel):
    """
    A Manufacturer represents a company which produces hardware devices; for example, Juniper or Dell.
    """
    name = models.CharField(
        max_length=50,
        unique=True
    )
    slug = models.SlugField(
        unique=True
    )

    csv_headers = ['name', 'slug']

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "{}?manufacturer={}".format(reverse('dcim:devicetype_list'), self.slug)

    def to_csv(self):
        return (
            self.name,
            self.slug,
        )


class DeviceType(ChangeLoggedModel, CustomFieldModel):
    """
    A DeviceType represents a particular make (Manufacturer) and model of device. It specifies rack height and depth, as
    well as high-level functional role(s).

    Each DeviceType can have an arbitrary number of component templates assigned to it, which define console, power, and
    interface objects. For example, a Juniper EX4300-48T DeviceType would have:

      * 1 ConsolePortTemplate
      * 2 PowerPortTemplates
      * 48 InterfaceTemplates

    When a new Device of this type is created, the appropriate console, power, and interface objects (as defined by the
    DeviceType) are automatically created as well.
    """
    manufacturer = models.ForeignKey(
        to='dcim.Manufacturer',
        on_delete=models.PROTECT,
        related_name='device_types'
    )
    model = models.CharField(
        max_length=50
    )
    slug = models.SlugField()
    part_number = models.CharField(
        max_length=50,
        blank=True,
        help_text='Discrete part number (optional)'
    )
    u_height = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Height (U)'
    )
    is_full_depth = models.BooleanField(
        default=True,
        verbose_name='Is full depth',
        help_text='Device consumes both front and rear rack faces'
    )
    subdevice_role = models.CharField(
        max_length=50,
        choices=SubdeviceRoleChoices,
        blank=True,
        verbose_name='Parent/child status',
        help_text='Parent devices house child devices in device bays. Leave blank '
                  'if this device type is neither a parent nor a child.'
    )
    comments = models.TextField(
        blank=True
    )
    custom_field_values = GenericRelation(
        to='extras.CustomFieldValue',
        content_type_field='obj_type',
        object_id_field='obj_id'
    )

    tags = TaggableManager(through=TaggedItem)

    csv_headers = [
        'manufacturer', 'model', 'slug', 'part_number', 'u_height', 'is_full_depth', 'subdevice_role', 'comments',
    ]
    clone_fields = [
        'manufacturer', 'u_height', 'is_full_depth', 'subdevice_role',
    ]

    class Meta:
        ordering = ['manufacturer', 'model']
        unique_together = [
            ['manufacturer', 'model'],
            ['manufacturer', 'slug'],
        ]

    def __str__(self):
        return self.model

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Save a copy of u_height for validation in clean()
        self._original_u_height = self.u_height

    def get_absolute_url(self):
        return reverse('dcim:devicetype', args=[self.pk])

    def to_yaml(self):
        data = OrderedDict((
            ('manufacturer', self.manufacturer.name),
            ('model', self.model),
            ('slug', self.slug),
            ('part_number', self.part_number),
            ('u_height', self.u_height),
            ('is_full_depth', self.is_full_depth),
            ('subdevice_role', self.subdevice_role),
            ('comments', self.comments),
        ))

        # Component templates
        if self.consoleport_templates.exists():
            data['console-ports'] = [
                {
                    'name': c.name,
                    'type': c.type,
                }
                for c in self.consoleport_templates.all()
            ]
        if self.consoleserverport_templates.exists():
            data['console-server-ports'] = [
                {
                    'name': c.name,
                    'type': c.type,
                }
                for c in self.consoleserverport_templates.all()
            ]
        if self.powerport_templates.exists():
            data['power-ports'] = [
                {
                    'name': c.name,
                    'type': c.type,
                    'maximum_draw': c.maximum_draw,
                    'allocated_draw': c.allocated_draw,
                }
                for c in self.powerport_templates.all()
            ]
        if self.poweroutlet_templates.exists():
            data['power-outlets'] = [
                {
                    'name': c.name,
                    'type': c.type,
                    'power_port': c.power_port.name if c.power_port else None,
                    'feed_leg': c.feed_leg,
                }
                for c in self.poweroutlet_templates.all()
            ]
        if self.interface_templates.exists():
            data['interfaces'] = [
                {
                    'name': c.name,
                    'type': c.type,
                    'mgmt_only': c.mgmt_only,
                }
                for c in self.interface_templates.all()
            ]
        if self.frontport_templates.exists():
            data['front-ports'] = [
                {
                    'name': c.name,
                    'type': c.type,
                    'rear_port': c.rear_port.name,
                    'rear_port_position': c.rear_port_position,
                }
                for c in self.frontport_templates.all()
            ]
        if self.rearport_templates.exists():
            data['rear-ports'] = [
                {
                    'name': c.name,
                    'type': c.type,
                    'positions': c.positions,
                }
                for c in self.rearport_templates.all()
            ]
        if self.device_bay_templates.exists():
            data['device-bays'] = [
                {
                    'name': c.name,
                }
                for c in self.device_bay_templates.all()
            ]

        return yaml.dump(dict(data), sort_keys=False)

    def clean(self):

        # If editing an existing DeviceType to have a larger u_height, first validate that *all* instances of it have
        # room to expand within their racks. This validation will impose a very high performance penalty when there are
        # many instances to check, but increasing the u_height of a DeviceType should be a very rare occurrence.
        if self.pk is not None and self.u_height > self._original_u_height:
            for d in Device.objects.filter(device_type=self, position__isnull=False):
                face_required = None if self.is_full_depth else d.face
                u_available = d.rack.get_available_units(u_height=self.u_height, rack_face=face_required,
                                                         exclude=[d.pk])
                if d.position not in u_available:
                    raise ValidationError({
                        'u_height': "Device {} in rack {} does not have sufficient space to accommodate a height of "
                                    "{}U".format(d, d.rack, self.u_height)
                    })

        if (
                self.subdevice_role != SubdeviceRoleChoices.ROLE_PARENT
        ) and self.device_bay_templates.count():
            raise ValidationError({
                'subdevice_role': "Must delete all device bay templates associated with this device before "
                                  "declassifying it as a parent device."
            })

        if self.u_height and self.subdevice_role == SubdeviceRoleChoices.ROLE_CHILD:
            raise ValidationError({
                'u_height': "Child device types must be 0U."
            })

    @property
    def display_name(self):
        return '{} {}'.format(self.manufacturer.name, self.model)

    @property
    def is_parent_device(self):
        return self.subdevice_role == SubdeviceRoleChoices.ROLE_PARENT

    @property
    def is_child_device(self):
        return self.subdevice_role == SubdeviceRoleChoices.ROLE_CHILD


#
# Devices
#

class DeviceRole(ChangeLoggedModel):
    """
    Devices are organized by functional role; for example, "Core Switch" or "File Server". Each DeviceRole is assigned a
    color to be used when displaying rack elevations. The vm_role field determines whether the role is applicable to
    virtual machines as well.
    """
    name = models.CharField(
        max_length=50,
        unique=True
    )
    slug = models.SlugField(
        unique=True
    )
    color = ColorField()
    vm_role = models.BooleanField(
        default=True,
        verbose_name='VM Role',
        help_text='Virtual machines may be assigned to this role'
    )
    description = models.CharField(
        max_length=100,
        blank=True,
    )

    csv_headers = ['name', 'slug', 'color', 'vm_role', 'description']

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def to_csv(self):
        return (
            self.name,
            self.slug,
            self.color,
            self.vm_role,
            self.description,
        )


class Platform(ChangeLoggedModel):
    """
    Platform refers to the software or firmware running on a Device. For example, "Cisco IOS-XR" or "Juniper Junos".
    NetBox uses Platforms to determine how to interact with devices when pulling inventory data or other information by
    specifying a NAPALM driver.
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        unique=True,
        max_length=100
    )
    manufacturer = models.ForeignKey(
        to='dcim.Manufacturer',
        on_delete=models.PROTECT,
        related_name='platforms',
        blank=True,
        null=True,
        help_text='Optionally limit this platform to devices of a certain manufacturer'
    )
    napalm_driver = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='NAPALM driver',
        help_text='The name of the NAPALM driver to use when interacting with devices'
    )
    napalm_args = JSONField(
        blank=True,
        null=True,
        verbose_name='NAPALM arguments',
        help_text='Additional arguments to pass when initiating the NAPALM driver (JSON format)'
    )

    csv_headers = ['name', 'slug', 'manufacturer', 'napalm_driver', 'napalm_args']

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "{}?platform={}".format(reverse('dcim:device_list'), self.slug)

    def to_csv(self):
        return (
            self.name,
            self.slug,
            self.manufacturer.name if self.manufacturer else None,
            self.napalm_driver,
            self.napalm_args,
        )


class Device(ChangeLoggedModel, ConfigContextModel, CustomFieldModel):
    """
    A Device represents a piece of physical hardware mounted within a Rack. Each Device is assigned a DeviceType,
    DeviceRole, and (optionally) a Platform. Device names are not required, however if one is set it must be unique.

    Each Device must be assigned to a site, and optionally to a rack within that site. Associating a device with a
    particular rack face or unit is optional (for example, vertically mounted PDUs do not consume rack units).

    When a new Device is created, console/power/interface/device bay components are created along with it as dictated
    by the component templates assigned to its DeviceType. Components can also be added, modified, or deleted after the
    creation of a Device.
    """
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.PROTECT,
        related_name='instances'
    )
    device_role = models.ForeignKey(
        to='dcim.DeviceRole',
        on_delete=models.PROTECT,
        related_name='devices'
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='devices',
        blank=True,
        null=True
    )
    platform = models.ForeignKey(
        to='dcim.Platform',
        on_delete=models.SET_NULL,
        related_name='devices',
        blank=True,
        null=True
    )
    name = models.CharField(
        max_length=64,
        blank=True,
        null=True
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
        help_text='A unique tag used to identify this device'
    )
    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.PROTECT,
        related_name='devices'
    )
    rack = models.ForeignKey(
        to='dcim.Rack',
        on_delete=models.PROTECT,
        related_name='devices',
        blank=True,
        null=True
    )
    position = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        verbose_name='Position (U)',
        help_text='The lowest-numbered unit occupied by the device'
    )
    face = models.CharField(
        max_length=50,
        blank=True,
        choices=DeviceFaceChoices,
        verbose_name='Rack face'
    )
    status = models.CharField(
        max_length=50,
        choices=DeviceStatusChoices,
        default=DeviceStatusChoices.STATUS_ACTIVE
    )
    primary_ip4 = models.OneToOneField(
        to='ipam.IPAddress',
        on_delete=models.SET_NULL,
        related_name='primary_ip4_for',
        blank=True,
        null=True,
        verbose_name='Primary IPv4'
    )
    primary_ip6 = models.OneToOneField(
        to='ipam.IPAddress',
        on_delete=models.SET_NULL,
        related_name='primary_ip6_for',
        blank=True,
        null=True,
        verbose_name='Primary IPv6'
    )
    cluster = models.ForeignKey(
        to='virtualization.Cluster',
        on_delete=models.SET_NULL,
        related_name='devices',
        blank=True,
        null=True
    )
    virtual_chassis = models.ForeignKey(
        to='VirtualChassis',
        on_delete=models.SET_NULL,
        related_name='members',
        blank=True,
        null=True
    )
    vc_position = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MaxValueValidator(255)]
    )
    vc_priority = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MaxValueValidator(255)]
    )
    comments = models.TextField(
        blank=True
    )
    custom_field_values = GenericRelation(
        to='extras.CustomFieldValue',
        content_type_field='obj_type',
        object_id_field='obj_id'
    )
    images = GenericRelation(
        to='extras.ImageAttachment'
    )

    objects = NaturalOrderingManager()
    tags = TaggableManager(through=TaggedItem)

    csv_headers = [
        'name', 'device_role', 'tenant', 'manufacturer', 'model_name', 'platform', 'serial', 'asset_tag', 'status',
        'site', 'rack_group', 'rack_name', 'position', 'face', 'comments',
    ]
    clone_fields = [
        'device_type', 'device_role', 'tenant', 'platform', 'site', 'rack', 'status', 'cluster',
    ]

    STATUS_CLASS_MAP = {
        DeviceStatusChoices.STATUS_OFFLINE: 'warning',
        DeviceStatusChoices.STATUS_ACTIVE: 'success',
        DeviceStatusChoices.STATUS_PLANNED: 'info',
        DeviceStatusChoices.STATUS_STAGED: 'primary',
        DeviceStatusChoices.STATUS_FAILED: 'danger',
        DeviceStatusChoices.STATUS_INVENTORY: 'default',
        DeviceStatusChoices.STATUS_DECOMMISSIONING: 'warning',
    }

    class Meta:
        ordering = ('name', 'pk')  # Name may be NULL
        unique_together = [
            ['site', 'tenant', 'name'],  # See validate_unique below
            ['rack', 'position', 'face'],
            ['virtual_chassis', 'vc_position'],
        ]
        permissions = (
            ('napalm_read', 'Read-only access to devices via NAPALM'),
            ('napalm_write', 'Read/write access to devices via NAPALM'),
        )

    def __str__(self):
        return self.display_name or super().__str__()

    def get_absolute_url(self):
        return reverse('dcim:device', args=[self.pk])

    def validate_unique(self, exclude=None):

        # Check for a duplicate name on a device assigned to the same Site and no Tenant. This is necessary
        # because Django does not consider two NULL fields to be equal, and thus will not trigger a violation
        # of the uniqueness constraint without manual intervention.
        if self.tenant is None and Device.objects.exclude(pk=self.pk).filter(name=self.name, tenant__isnull=True):
            raise ValidationError({
                'name': 'A device with this name already exists.'
            })

        super().validate_unique(exclude)

    def clean(self):

        super().clean()

        # Validate site/rack combination
        if self.rack and self.site != self.rack.site:
            raise ValidationError({
                'rack': "Rack {} does not belong to site {}.".format(self.rack, self.site),
            })

        if self.rack is None:
            if self.face:
                raise ValidationError({
                    'face': "Cannot select a rack face without assigning a rack.",
                })
            if self.position:
                raise ValidationError({
                    'face': "Cannot select a rack position without assigning a rack.",
                })

        # Validate position/face combination
        if self.position and not self.face:
            raise ValidationError({
                'face': "Must specify rack face when defining rack position.",
            })

        # Prevent 0U devices from being assigned to a specific position
        if self.position and self.device_type.u_height == 0:
            raise ValidationError({
                'position': "A U0 device type ({}) cannot be assigned to a rack position.".format(self.device_type)
            })

        if self.rack:

            try:
                # Child devices cannot be assigned to a rack face/unit
                if self.device_type.is_child_device and self.face is not None:
                    raise ValidationError({
                        'face': "Child device types cannot be assigned to a rack face. This is an attribute of the "
                                "parent device."
                    })
                if self.device_type.is_child_device and self.position:
                    raise ValidationError({
                        'position': "Child device types cannot be assigned to a rack position. This is an attribute of "
                                    "the parent device."
                    })

                # Validate rack space
                rack_face = self.face if not self.device_type.is_full_depth else None
                exclude_list = [self.pk] if self.pk else []
                try:
                    available_units = self.rack.get_available_units(
                        u_height=self.device_type.u_height, rack_face=rack_face, exclude=exclude_list
                    )
                    if self.position and self.position not in available_units:
                        raise ValidationError({
                            'position': "U{} is already occupied or does not have sufficient space to accommodate a(n) "
                                        "{} ({}U).".format(self.position, self.device_type, self.device_type.u_height)
                        })
                except Rack.DoesNotExist:
                    pass

            except DeviceType.DoesNotExist:
                pass

        # Validate primary IP addresses
        vc_interfaces = self.vc_interfaces.all()
        if self.primary_ip4:
            if self.primary_ip4.interface in vc_interfaces:
                pass
            elif self.primary_ip4.nat_inside is not None and self.primary_ip4.nat_inside.interface in vc_interfaces:
                pass
            else:
                raise ValidationError({
                    'primary_ip4': "The specified IP address ({}) is not assigned to this device.".format(
                        self.primary_ip4),
                })
        if self.primary_ip6:
            if self.primary_ip6.interface in vc_interfaces:
                pass
            elif self.primary_ip6.nat_inside is not None and self.primary_ip6.nat_inside.interface in vc_interfaces:
                pass
            else:
                raise ValidationError({
                    'primary_ip6': "The specified IP address ({}) is not assigned to this device.".format(
                        self.primary_ip6),
                })

        # Validate manufacturer/platform
        if hasattr(self, 'device_type') and self.platform:
            if self.platform.manufacturer and self.platform.manufacturer != self.device_type.manufacturer:
                raise ValidationError({
                    'platform': "The assigned platform is limited to {} device types, but this device's type belongs "
                                "to {}.".format(self.platform.manufacturer, self.device_type.manufacturer)
                })

        # A Device can only be assigned to a Cluster in the same Site (or no Site)
        if self.cluster and self.cluster.site is not None and self.cluster.site != self.site:
            raise ValidationError({
                'cluster': "The assigned cluster belongs to a different site ({})".format(self.cluster.site)
            })

        # Validate virtual chassis assignment
        if self.virtual_chassis and self.vc_position is None:
            raise ValidationError({
                'vc_position': "A device assigned to a virtual chassis must have its position defined."
            })

    def save(self, *args, **kwargs):

        is_new = not bool(self.pk)

        super().save(*args, **kwargs)

        # If this is a new Device, instantiate all of the related components per the DeviceType definition
        if is_new:
            ConsolePort.objects.bulk_create(
                [x.instantiate(self) for x in self.device_type.consoleport_templates.all()]
            )
            ConsoleServerPort.objects.bulk_create(
                [x.instantiate(self) for x in self.device_type.consoleserverport_templates.all()]
            )
            PowerPort.objects.bulk_create(
                [x.instantiate(self) for x in self.device_type.powerport_templates.all()]
            )
            PowerOutlet.objects.bulk_create(
                [x.instantiate(self) for x in self.device_type.poweroutlet_templates.all()]
            )
            Interface.objects.bulk_create(
                [x.instantiate(self) for x in self.device_type.interface_templates.all()]
            )
            RearPort.objects.bulk_create(
                [x.instantiate(self) for x in self.device_type.rearport_templates.all()]
            )
            FrontPort.objects.bulk_create(
                [x.instantiate(self) for x in self.device_type.frontport_templates.all()]
            )
            DeviceBay.objects.bulk_create(
                [x.instantiate(self) for x in self.device_type.device_bay_templates.all()]
            )

        # Update Site and Rack assignment for any child Devices
        devices = Device.objects.filter(parent_bay__device=self)
        for device in devices:
            device.site = self.site
            device.rack = self.rack
            device.save()

    def to_csv(self):
        return (
            self.name or '',
            self.device_role.name,
            self.tenant.name if self.tenant else None,
            self.device_type.manufacturer.name,
            self.device_type.model,
            self.platform.name if self.platform else None,
            self.serial,
            self.asset_tag,
            self.get_status_display(),
            self.site.name,
            self.rack.group.name if self.rack and self.rack.group else None,
            self.rack.name if self.rack else None,
            self.position,
            self.get_face_display(),
            self.comments,
        )

    @property
    def display_name(self):
        if self.name:
            return self.name
        elif self.virtual_chassis and self.virtual_chassis.master.name:
            return "{}:{}".format(self.virtual_chassis.master, self.vc_position)
        elif hasattr(self, 'device_type'):
            return "{}".format(self.device_type)
        return ""

    @property
    def identifier(self):
        """
        Return the device name if set; otherwise return the Device's primary key as {pk}
        """
        if self.name is not None:
            return self.name
        return '{{{}}}'.format(self.pk)

    @property
    def primary_ip(self):
        if settings.PREFER_IPV4 and self.primary_ip4:
            return self.primary_ip4
        elif self.primary_ip6:
            return self.primary_ip6
        elif self.primary_ip4:
            return self.primary_ip4
        else:
            return None

    def get_vc_master(self):
        """
        If this Device is a VirtualChassis member, return the VC master. Otherwise, return None.
        """
        return self.virtual_chassis.master if self.virtual_chassis else None

    @property
    def vc_interfaces(self):
        """
        Return a QuerySet matching all Interfaces assigned to this Device or, if this Device is a VC master, to another
        Device belonging to the same VirtualChassis.
        """
        filter = Q(device=self)
        if self.virtual_chassis and self.virtual_chassis.master == self:
            filter |= Q(device__virtual_chassis=self.virtual_chassis, mgmt_only=False)
        return Interface.objects.filter(filter)

    def get_cables(self, pk_list=False):
        """
        Return a QuerySet or PK list matching all Cables connected to a component of this Device.
        """
        cable_pks = []
        for component_model in [
            ConsolePort, ConsoleServerPort, PowerPort, PowerOutlet, Interface, FrontPort, RearPort
        ]:
            cable_pks += component_model.objects.filter(
                device=self, cable__isnull=False
            ).values_list('cable', flat=True)
        if pk_list:
            return cable_pks
        return Cable.objects.filter(pk__in=cable_pks)

    def get_children(self):
        """
        Return the set of child Devices installed in DeviceBays within this Device.
        """
        return Device.objects.filter(parent_bay__device=self.pk)

    def get_status_class(self):
        return self.STATUS_CLASS_MAP.get(self.status)


#
# Virtual chassis
#

class VirtualChassis(ChangeLoggedModel):
    """
    A collection of Devices which operate with a shared control plane (e.g. a switch stack).
    """
    master = models.OneToOneField(
        to='Device',
        on_delete=models.PROTECT,
        related_name='vc_master_for'
    )
    domain = models.CharField(
        max_length=30,
        blank=True
    )

    tags = TaggableManager(through=TaggedItem)

    csv_headers = ['master', 'domain']

    class Meta:
        ordering = ['master']
        verbose_name_plural = 'virtual chassis'

    def __str__(self):
        return str(self.master) if hasattr(self, 'master') else 'New Virtual Chassis'

    def get_absolute_url(self):
        return self.master.get_absolute_url()

    def clean(self):

        # Verify that the selected master device has been assigned to this VirtualChassis. (Skip when creating a new
        # VirtualChassis.)
        if self.pk and self.master not in self.members.all():
            raise ValidationError({
                'master': "The selected master is not assigned to this virtual chassis."
            })

    def delete(self, *args, **kwargs):

        # Check for LAG interfaces split across member chassis
        interfaces = Interface.objects.filter(
            device__in=self.members.all(),
            lag__isnull=False
        ).exclude(
            lag__device=F('device')
        )
        if interfaces:
            raise ProtectedError(
                "Unable to delete virtual chassis {}. There are member interfaces which form a cross-chassis "
                "LAG".format(self),
                interfaces
            )

        return super().delete(*args, **kwargs)

    def to_csv(self):
        return (
            self.master,
            self.domain,
        )


#
# Power
#

class PowerPanel(ChangeLoggedModel):
    """
    A distribution point for electrical power; e.g. a data center RPP.
    """
    site = models.ForeignKey(
        to='Site',
        on_delete=models.PROTECT
    )
    rack_group = models.ForeignKey(
        to='RackGroup',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    name = models.CharField(
        max_length=50
    )

    csv_headers = ['site', 'rack_group_name', 'name']

    class Meta:
        ordering = ['site', 'name']
        unique_together = ['site', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dcim:powerpanel', args=[self.pk])

    def to_csv(self):
        return (
            self.site.name,
            self.rack_group.name if self.rack_group else None,
            self.name,
        )

    def clean(self):

        # RackGroup must belong to assigned Site
        if self.rack_group and self.rack_group.site != self.site:
            raise ValidationError("Rack group {} ({}) is in a different site than {}".format(
                self.rack_group, self.rack_group.site, self.site
            ))


class PowerFeed(ChangeLoggedModel, CableTermination, CustomFieldModel):
    """
    An electrical circuit delivered from a PowerPanel.
    """
    power_panel = models.ForeignKey(
        to='PowerPanel',
        on_delete=models.PROTECT,
        related_name='powerfeeds'
    )
    rack = models.ForeignKey(
        to='Rack',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    connected_endpoint = models.OneToOneField(
        to='dcim.PowerPort',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True
    )
    connection_status = models.NullBooleanField(
        choices=CONNECTION_STATUS_CHOICES,
        blank=True
    )
    name = models.CharField(
        max_length=50
    )
    status = models.CharField(
        max_length=50,
        choices=PowerFeedStatusChoices,
        default=PowerFeedStatusChoices.STATUS_ACTIVE
    )
    type = models.CharField(
        max_length=50,
        choices=PowerFeedTypeChoices,
        default=PowerFeedTypeChoices.TYPE_PRIMARY
    )
    supply = models.CharField(
        max_length=50,
        choices=PowerFeedSupplyChoices,
        default=PowerFeedSupplyChoices.SUPPLY_AC
    )
    phase = models.CharField(
        max_length=50,
        choices=PowerFeedPhaseChoices,
        default=PowerFeedPhaseChoices.PHASE_SINGLE
    )
    voltage = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        default=120
    )
    amperage = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        default=20
    )
    max_utilization = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        default=80,
        help_text="Maximum permissible draw (percentage)"
    )
    available_power = models.PositiveIntegerField(
        default=0,
        editable=False
    )
    comments = models.TextField(
        blank=True
    )
    custom_field_values = GenericRelation(
        to='extras.CustomFieldValue',
        content_type_field='obj_type',
        object_id_field='obj_id'
    )

    tags = TaggableManager(through=TaggedItem)

    csv_headers = [
        'site', 'panel_name', 'rack_group', 'rack_name', 'name', 'status', 'type', 'supply', 'phase', 'voltage',
        'amperage', 'max_utilization', 'comments',
    ]
    clone_fields = [
        'power_panel', 'rack', 'status', 'type', 'supply', 'phase', 'voltage', 'amperage', 'max_utilization',
        'available_power',
    ]

    STATUS_CLASS_MAP = {
        PowerFeedStatusChoices.STATUS_OFFLINE: 'warning',
        PowerFeedStatusChoices.STATUS_ACTIVE: 'success',
        PowerFeedStatusChoices.STATUS_PLANNED: 'info',
        PowerFeedStatusChoices.STATUS_FAILED: 'danger',
    }

    TYPE_CLASS_MAP = {
        PowerFeedTypeChoices.TYPE_PRIMARY: 'success',
        PowerFeedTypeChoices.TYPE_REDUNDANT: 'info',
    }

    class Meta:
        ordering = ['power_panel', 'name']
        unique_together = ['power_panel', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dcim:powerfeed', args=[self.pk])

    def to_csv(self):
        return (
            self.power_panel.site.name,
            self.power_panel.name,
            self.rack.group.name if self.rack and self.rack.group else None,
            self.rack.name if self.rack else None,
            self.name,
            self.get_status_display(),
            self.get_type_display(),
            self.get_supply_display(),
            self.get_phase_display(),
            self.voltage,
            self.amperage,
            self.max_utilization,
            self.comments,
        )

    def clean(self):

        # Rack must belong to same Site as PowerPanel
        if self.rack and self.rack.site != self.power_panel.site:
            raise ValidationError("Rack {} ({}) and power panel {} ({}) are in different sites".format(
                self.rack, self.rack.site, self.power_panel, self.power_panel.site
            ))

    def save(self, *args, **kwargs):

        # Cache the available_power property on the instance
        kva = self.voltage * self.amperage * (self.max_utilization / 100)
        if self.phase == PowerFeedPhaseChoices.PHASE_3PHASE:
            self.available_power = round(kva * 1.732)
        else:
            self.available_power = round(kva)

        super().save(*args, **kwargs)

    def get_type_class(self):
        return self.TYPE_CLASS_MAP.get(self.type)

    def get_status_class(self):
        return self.STATUS_CLASS_MAP.get(self.status)


#
# Cables
#

class Cable(ChangeLoggedModel):
    """
    A physical connection between two endpoints.
    """
    termination_a_type = models.ForeignKey(
        to=ContentType,
        limit_choices_to=CABLE_TERMINATION_MODELS,
        on_delete=models.PROTECT,
        related_name='+'
    )
    termination_a_id = models.PositiveIntegerField()
    termination_a = GenericForeignKey(
        ct_field='termination_a_type',
        fk_field='termination_a_id'
    )
    termination_b_type = models.ForeignKey(
        to=ContentType,
        limit_choices_to=CABLE_TERMINATION_MODELS,
        on_delete=models.PROTECT,
        related_name='+'
    )
    termination_b_id = models.PositiveIntegerField()
    termination_b = GenericForeignKey(
        ct_field='termination_b_type',
        fk_field='termination_b_id'
    )
    type = models.CharField(
        max_length=50,
        choices=CableTypeChoices,
        blank=True
    )
    status = models.CharField(
        max_length=50,
        choices=CableStatusChoices,
        default=CableStatusChoices.STATUS_CONNECTED
    )
    label = models.CharField(
        max_length=100,
        blank=True
    )
    color = ColorField(
        blank=True
    )
    length = models.PositiveSmallIntegerField(
        blank=True,
        null=True
    )
    length_unit = models.CharField(
        max_length=50,
        choices=CableLengthUnitChoices,
        blank=True,
    )
    # Stores the normalized length (in meters) for database ordering
    _abs_length = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        blank=True,
        null=True
    )
    # Cache the associated device (where applicable) for the A and B terminations. This enables filtering of Cables by
    # their associated Devices.
    _termination_a_device = models.ForeignKey(
        to=Device,
        on_delete=models.CASCADE,
        related_name='+',
        blank=True,
        null=True
    )
    _termination_b_device = models.ForeignKey(
        to=Device,
        on_delete=models.CASCADE,
        related_name='+',
        blank=True,
        null=True
    )

    csv_headers = [
        'termination_a_type', 'termination_a_id', 'termination_b_type', 'termination_b_id', 'type', 'status', 'label',
        'color', 'length', 'length_unit',
    ]

    STATUS_CLASS_MAP = {
        CableStatusChoices.STATUS_CONNECTED: 'success',
        CableStatusChoices.STATUS_PLANNED: 'info',
    }

    class Meta:
        ordering = ['pk']
        unique_together = (
            ('termination_a_type', 'termination_a_id'),
            ('termination_b_type', 'termination_b_id'),
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # A copy of the PK to be used by __str__ in case the object is deleted
        self._pk = self.pk

    def __str__(self):
        return self.label or '#{}'.format(self._pk)

    def get_absolute_url(self):
        return reverse('dcim:cable', args=[self.pk])

    def clean(self):

        # Validate that termination A exists
        if not hasattr(self, 'termination_a_type'):
            raise ValidationError('Termination A type has not been specified')
        try:
            self.termination_a_type.model_class().objects.get(pk=self.termination_a_id)
        except ObjectDoesNotExist:
            raise ValidationError({
                'termination_a': 'Invalid ID for type {}'.format(self.termination_a_type)
            })

        # Validate that termination B exists
        if not hasattr(self, 'termination_b_type'):
            raise ValidationError('Termination B type has not been specified')
        try:
            self.termination_b_type.model_class().objects.get(pk=self.termination_b_id)
        except ObjectDoesNotExist:
            raise ValidationError({
                'termination_b': 'Invalid ID for type {}'.format(self.termination_b_type)
            })

        type_a = self.termination_a_type.model
        type_b = self.termination_b_type.model

        # Validate interface types
        if type_a == 'interface' and self.termination_a.type in NONCONNECTABLE_IFACE_TYPES:
            raise ValidationError({
                'termination_a_id': 'Cables cannot be terminated to {} interfaces'.format(
                    self.termination_a.get_type_display()
                )
            })
        if type_b == 'interface' and self.termination_b.type in NONCONNECTABLE_IFACE_TYPES:
            raise ValidationError({
                'termination_b_id': 'Cables cannot be terminated to {} interfaces'.format(
                    self.termination_b.get_type_display()
                )
            })

        # Check that termination types are compatible
        if type_b not in COMPATIBLE_TERMINATION_TYPES.get(type_a):
            raise ValidationError("Incompatible termination types: {} and {}".format(
                self.termination_a_type, self.termination_b_type
            ))

        # A component with multiple positions must be connected to a component with an equal number of positions
        term_a_positions = getattr(self.termination_a, 'positions', 1)
        term_b_positions = getattr(self.termination_b, 'positions', 1)
        if term_a_positions != term_b_positions:
            raise ValidationError(
                "{} has {} positions and {} has {}. Both terminations must have the same number of positions.".format(
                    self.termination_a, term_a_positions, self.termination_b, term_b_positions
                )
            )

        # A termination point cannot be connected to itself
        if self.termination_a == self.termination_b:
            raise ValidationError("Cannot connect {} to itself".format(self.termination_a_type))

        # A front port cannot be connected to its corresponding rear port
        if (
            type_a in ['frontport', 'rearport'] and
            type_b in ['frontport', 'rearport'] and
            (
                getattr(self.termination_a, 'rear_port', None) == self.termination_b or
                getattr(self.termination_b, 'rear_port', None) == self.termination_a
            )
        ):
            raise ValidationError("A front port cannot be connected to it corresponding rear port")

        # Check for an existing Cable connected to either termination object
        if self.termination_a.cable not in (None, self):
            raise ValidationError("{} already has a cable attached (#{})".format(
                self.termination_a, self.termination_a.cable_id
            ))
        if self.termination_b.cable not in (None, self):
            raise ValidationError("{} already has a cable attached (#{})".format(
                self.termination_b, self.termination_b.cable_id
            ))

        # Validate length and length_unit
        if self.length is not None and not self.length_unit:
            raise ValidationError("Must specify a unit when setting a cable length")
        elif self.length is None:
            self.length_unit = ''

    def save(self, *args, **kwargs):

        # Store the given length (if any) in meters for use in database ordering
        if self.length and self.length_unit:
            self._abs_length = to_meters(self.length, self.length_unit)
        else:
            self._abs_length = None

        # Store the parent Device for the A and B terminations (if applicable) to enable filtering
        if hasattr(self.termination_a, 'device'):
            self._termination_a_device = self.termination_a.device
        if hasattr(self.termination_b, 'device'):
            self._termination_b_device = self.termination_b.device

        super().save(*args, **kwargs)

        # Update the private pk used in __str__ in case this is a new object (i.e. just got its pk)
        self._pk = self.pk

    def to_csv(self):
        return (
            '{}.{}'.format(self.termination_a_type.app_label, self.termination_a_type.model),
            self.termination_a_id,
            '{}.{}'.format(self.termination_b_type.app_label, self.termination_b_type.model),
            self.termination_b_id,
            self.get_type_display(),
            self.get_status_display(),
            self.label,
            self.color,
            self.length,
            self.length_unit,
        )

    def get_status_class(self):
        return self.STATUS_CLASS_MAP.get(self.status)

    def get_compatible_types(self):
        """
        Return all termination types compatible with termination A.
        """
        if self.termination_a is None:
            return
        return COMPATIBLE_TERMINATION_TYPES[self.termination_a._meta.model_name]

    def get_path_endpoints(self):
        """
        Traverse both ends of a cable path and return its connected endpoints. Note that one or both endpoints may be
        None.
        """
        a_path = self.termination_b.trace()
        b_path = self.termination_a.trace()

        # Determine overall path status (connected or planned)
        if self.status == CableStatusChoices.STATUS_PLANNED:
            path_status = CONNECTION_STATUS_PLANNED
        else:
            path_status = CONNECTION_STATUS_CONNECTED
            for segment in a_path[1:] + b_path[1:]:
                if segment[1] is None or segment[1].status == CableStatusChoices.STATUS_PLANNED:
                    path_status = CONNECTION_STATUS_PLANNED
                    break

        a_endpoint = a_path[-1][2]
        b_endpoint = b_path[-1][2]

        return a_endpoint, b_endpoint, path_status
