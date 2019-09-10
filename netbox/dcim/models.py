from collections import OrderedDict
from itertools import count, groupby

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Case, Count, Q, Sum, When, F, Subquery, OuterRef
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager
from timezone_field import TimeZoneField

from extras.models import ConfigContextModel, CustomFieldModel, ObjectChange, TaggedItem
from utilities.fields import ColorField
from utilities.managers import NaturalOrderingManager
from utilities.models import ChangeLoggedModel
from utilities.utils import serialize_object, to_meters
from .constants import *
from .exceptions import LoopDetected
from .fields import ASNField, MACAddressField
from .managers import InterfaceManager


class ComponentTemplateModel(models.Model):

    class Meta:
        abstract = True

    def instantiate(self, device):
        """
        Instantiate a new component on the specified Device.
        """
        raise NotImplementedError()

    def to_objectchange(self, action):
        return ObjectChange(
            changed_object=self,
            object_repr=str(self),
            action=action,
            related_object=self.device_type,
            object_data=serialize_object(self)
        )


class ComponentModel(models.Model):
    description = models.CharField(
        max_length=100,
        blank=True
    )

    class Meta:
        abstract = True

    def to_objectchange(self, action):
        # Annotate the parent Device/VM
        try:
            parent = getattr(self, 'device', None) or getattr(self, 'virtual_machine', None)
        except ObjectDoesNotExist:
            # The parent device/VM has already been deleted
            parent = None

        return ObjectChange(
            changed_object=self,
            object_repr=str(self),
            action=action,
            related_object=parent,
            object_data=serialize_object(self)
        )

    @property
    def parent(self):
        return getattr(self, 'device', None)


class CableTermination(models.Model):
    cable = models.ForeignKey(
        to='dcim.Cable',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True
    )

    # Generic relations to Cable. These ensure that an attached Cable is deleted if the terminated object is deleted.
    _cabled_as_a = GenericRelation(
        to='dcim.Cable',
        content_type_field='termination_a_type',
        object_id_field='termination_a_id'
    )
    _cabled_as_b = GenericRelation(
        to='dcim.Cable',
        content_type_field='termination_b_type',
        object_id_field='termination_b_id'
    )

    class Meta:
        abstract = True

    def trace(self, position=1, follow_circuits=False, cable_history=None):
        """
        Return a list representing a complete cable path, with each individual segment represented as a three-tuple:
            [
                (termination A, cable, termination B),
                (termination C, cable, termination D),
                (termination E, cable, termination F)
            ]
        """
        def get_peer_port(termination, position=1, follow_circuits=False):
            from circuits.models import CircuitTermination

            # Map a front port to its corresponding rear port
            if isinstance(termination, FrontPort):
                return termination.rear_port, termination.rear_port_position

            # Map a rear port/position to its corresponding front port
            elif isinstance(termination, RearPort):
                if position not in range(1, termination.positions + 1):
                    raise Exception("Invalid position for {} ({} positions): {})".format(
                        termination, termination.positions, position
                    ))
                try:
                    peer_port = FrontPort.objects.get(
                        rear_port=termination,
                        rear_port_position=position,
                    )
                    return peer_port, 1
                except ObjectDoesNotExist:
                    return None, None

            # Follow a circuit to its other termination
            elif isinstance(termination, CircuitTermination) and follow_circuits:
                peer_termination = termination.get_peer_termination()
                if peer_termination is None:
                    return None, None
                return peer_termination, position

            # Termination is not a pass-through port
            else:
                return None, None

        if not self.cable:
            return [(self, None, None)]

        # Record cable history to detect loops
        if cable_history is None:
            cable_history = []
        elif self.cable in cable_history:
            raise LoopDetected()
        cable_history.append(self.cable)

        far_end = self.cable.termination_b if self.cable.termination_a == self else self.cable.termination_a
        path = [(self, self.cable, far_end)]

        peer_port, position = get_peer_port(far_end, position, follow_circuits)
        if peer_port is None:
            return path

        try:
            next_segment = peer_port.trace(position, follow_circuits, cable_history)
        except LoopDetected:
            return path

        if next_segment is None:
            return path + [(peer_port, None, None)]

        return path + next_segment

    def get_cable_peer(self):
        if self.cable is None:
            return None
        if self._cabled_as_a.exists():
            return self.cable.termination_b
        if self._cabled_as_b.exists():
            return self.cable.termination_a


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
    status = models.PositiveSmallIntegerField(
        choices=SITE_STATUS_CHOICES,
        default=SITE_STATUS_ACTIVE
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
        return STATUS_CLASSES[self.status]


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

    csv_headers = ['name', 'slug', 'color']

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
        )


class Rack(ChangeLoggedModel, CustomFieldModel):
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
    status = models.PositiveSmallIntegerField(
        choices=RACK_STATUS_CHOICES,
        default=RACK_STATUS_ACTIVE
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
    type = models.PositiveSmallIntegerField(
        choices=RACK_TYPE_CHOICES,
        blank=True,
        null=True,
        verbose_name='Type'
    )
    width = models.PositiveSmallIntegerField(
        choices=RACK_WIDTH_CHOICES,
        default=RACK_WIDTH_19IN,
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
    outer_unit = models.PositiveSmallIntegerField(
        choices=RACK_DIMENSION_UNIT_CHOICES,
        blank=True,
        null=True
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

    class Meta:
        ordering = ['site', 'group', 'name']
        unique_together = [
            ['group', 'name'],
            ['group', 'facility_id'],
        ]

    def __str__(self):
        return self.display_name or super().__str__()

    def get_absolute_url(self):
        return reverse('dcim:rack', args=[self.pk])

    def clean(self):

        # Validate outer dimensions and unit
        if (self.outer_width is not None or self.outer_depth is not None) and self.outer_unit is None:
            raise ValidationError("Must specify a unit when setting an outer width/depth")
        elif self.outer_width is None and self.outer_depth is None:
            self.outer_unit = None

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
        return STATUS_CLASSES[self.status]

    def get_rack_units(self, face=RACK_FACE_FRONT, exclude=None, remove_redundant=False):
        """
        Return a list of rack units as dictionaries. Example: {'device': None, 'face': 0, 'id': 48, 'name': 'U48'}
        Each key 'device' is either a Device or None. By default, multi-U devices are repeated for each U they occupy.

        :param face: Rack face (front or rear)
        :param exclude: PK of a Device to exclude (optional); helpful when relocating a Device within a Rack
        :param remove_redundant: If True, rack units occupied by a device already listed will be omitted
        """

        elevation = OrderedDict()
        for u in self.units:
            elevation[u] = {'id': u, 'name': 'U{}'.format(u), 'face': face, 'device': None}

        # Add devices to rack units list
        if self.pk:
            for device in Device.objects.prefetch_related('device_type__manufacturer', 'device_role')\
                    .annotate(devicebay_count=Count('device_bays'))\
                    .exclude(pk=exclude)\
                    .filter(rack=self, position__gt=0)\
                    .filter(Q(face=face) | Q(device_type__is_full_depth=True)):
                if remove_redundant:
                    elevation[device.position]['device'] = device
                    for u in range(device.position + 1, device.position + device.device_type.u_height):
                        elevation.pop(u, None)
                else:
                    for u in range(device.position, device.position + device.device_type.u_height):
                        elevation[u]['device'] = device

        return [u for u in elevation.values()]

    def get_front_elevation(self):
        return self.get_rack_units(face=RACK_FACE_FRONT, remove_redundant=True)

    def get_rear_elevation(self):
        return self.get_rack_units(face=RACK_FACE_REAR, remove_redundant=True)

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
        Determine the utilization rate of the rack and return it as a percentage.
        """
        u_available = len(self.get_available_units())
        return int(float(self.u_height - u_available) / self.u_height * 100)

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
    subdevice_role = models.NullBooleanField(
        default=None,
        verbose_name='Parent/child status',
        choices=SUBDEVICE_ROLE_CHOICES,
        help_text='Parent devices house child devices in device bays. Select '
                  '"None" if this device type is neither a parent nor a child.'
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

    def to_csv(self):
        return (
            self.manufacturer.name,
            self.model,
            self.slug,
            self.part_number,
            self.u_height,
            self.is_full_depth,
            self.get_subdevice_role_display() if self.subdevice_role else None,
            self.comments,
        )

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

        if self.subdevice_role != SUBDEVICE_ROLE_PARENT and self.device_bay_templates.count():
            raise ValidationError({
                'subdevice_role': "Must delete all device bay templates associated with this device before "
                                  "declassifying it as a parent device."
            })

        if self.u_height and self.subdevice_role == SUBDEVICE_ROLE_CHILD:
            raise ValidationError({
                'u_height': "Child device types must be 0U."
            })

    @property
    def display_name(self):
        return '{} {}'.format(self.manufacturer.name, self.model)

    @property
    def is_parent_device(self):
        return bool(self.subdevice_role)

    @property
    def is_child_device(self):
        return bool(self.subdevice_role is False)


class ConsolePortTemplate(ComponentTemplateModel):
    """
    A template for a ConsolePort to be created for a new Device.
    """
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.CASCADE,
        related_name='consoleport_templates'
    )
    name = models.CharField(
        max_length=50
    )

    objects = NaturalOrderingManager()

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name

    def instantiate(self, device):
        return ConsolePort(
            device=device,
            name=self.name
        )


class ConsoleServerPortTemplate(ComponentTemplateModel):
    """
    A template for a ConsoleServerPort to be created for a new Device.
    """
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.CASCADE,
        related_name='consoleserverport_templates'
    )
    name = models.CharField(
        max_length=50
    )

    objects = NaturalOrderingManager()

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name

    def instantiate(self, device):
        return ConsoleServerPort(
            device=device,
            name=self.name
        )


class PowerPortTemplate(ComponentTemplateModel):
    """
    A template for a PowerPort to be created for a new Device.
    """
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.CASCADE,
        related_name='powerport_templates'
    )
    name = models.CharField(
        max_length=50
    )
    maximum_draw = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Maximum current draw (watts)"
    )
    allocated_draw = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Allocated current draw (watts)"
    )

    objects = NaturalOrderingManager()

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name

    def instantiate(self, device):
        return PowerPort(
            device=device,
            name=self.name,
            maximum_draw=self.maximum_draw,
            allocated_draw=self.allocated_draw
        )


class PowerOutletTemplate(ComponentTemplateModel):
    """
    A template for a PowerOutlet to be created for a new Device.
    """
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.CASCADE,
        related_name='poweroutlet_templates'
    )
    name = models.CharField(
        max_length=50
    )
    power_port = models.ForeignKey(
        to='dcim.PowerPortTemplate',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='poweroutlet_templates'
    )
    feed_leg = models.PositiveSmallIntegerField(
        choices=POWERFEED_LEG_CHOICES,
        blank=True,
        null=True,
        help_text="Phase (for three-phase feeds)"
    )

    objects = NaturalOrderingManager()

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name

    def clean(self):

        # Validate power port assignment
        if self.power_port and self.power_port.device_type != self.device_type:
            raise ValidationError(
                "Parent power port ({}) must belong to the same device type".format(self.power_port)
            )

    def instantiate(self, device):
        if self.power_port:
            power_port = PowerPort.objects.get(device=device, name=self.power_port.name)
        else:
            power_port = None
        return PowerOutlet(
            device=device,
            name=self.name,
            power_port=power_port,
            feed_leg=self.feed_leg
        )


class InterfaceTemplate(ComponentTemplateModel):
    """
    A template for a physical data interface on a new Device.
    """
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.CASCADE,
        related_name='interface_templates'
    )
    name = models.CharField(
        max_length=64
    )
    type = models.PositiveSmallIntegerField(
        choices=IFACE_TYPE_CHOICES,
        default=IFACE_TYPE_10GE_SFP_PLUS
    )
    mgmt_only = models.BooleanField(
        default=False,
        verbose_name='Management only'
    )

    objects = InterfaceManager()

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name

    # TODO: Remove in v2.7
    @property
    def form_factor(self):
        """
        Backward-compatibility for form_factor
        """
        return self.type

    # TODO: Remove in v2.7
    @form_factor.setter
    def form_factor(self, value):
        """
        Backward-compatibility for form_factor
        """
        self.type = value

    def instantiate(self, device):
        return Interface(
            device=device,
            name=self.name,
            type=self.type,
            mgmt_only=self.mgmt_only
        )


class FrontPortTemplate(ComponentTemplateModel):
    """
    Template for a pass-through port on the front of a new Device.
    """
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.CASCADE,
        related_name='frontport_templates'
    )
    name = models.CharField(
        max_length=64
    )
    type = models.PositiveSmallIntegerField(
        choices=PORT_TYPE_CHOICES
    )
    rear_port = models.ForeignKey(
        to='dcim.RearPortTemplate',
        on_delete=models.CASCADE,
        related_name='frontport_templates'
    )
    rear_port_position = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(64)]
    )

    objects = NaturalOrderingManager()

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = [
            ['device_type', 'name'],
            ['rear_port', 'rear_port_position'],
        ]

    def __str__(self):
        return self.name

    def clean(self):

        # Validate rear port assignment
        if self.rear_port.device_type != self.device_type:
            raise ValidationError(
                "Rear port ({}) must belong to the same device type".format(self.rear_port)
            )

        # Validate rear port position assignment
        if self.rear_port_position > self.rear_port.positions:
            raise ValidationError(
                "Invalid rear port position ({}); rear port {} has only {} positions".format(
                    self.rear_port_position, self.rear_port.name, self.rear_port.positions
                )
            )

    def instantiate(self, device):
        if self.rear_port:
            rear_port = RearPort.objects.get(device=device, name=self.rear_port.name)
        else:
            rear_port = None
        return FrontPort(
            device=device,
            name=self.name,
            type=self.type,
            rear_port=rear_port,
            rear_port_position=self.rear_port_position
        )


class RearPortTemplate(ComponentTemplateModel):
    """
    Template for a pass-through port on the rear of a new Device.
    """
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.CASCADE,
        related_name='rearport_templates'
    )
    name = models.CharField(
        max_length=64
    )
    type = models.PositiveSmallIntegerField(
        choices=PORT_TYPE_CHOICES
    )
    positions = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(64)]
    )

    objects = NaturalOrderingManager()

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name

    def instantiate(self, device):
        return RearPort(
            device=device,
            name=self.name,
            type=self.type,
            positions=self.positions
        )


class DeviceBayTemplate(ComponentTemplateModel):
    """
    A template for a DeviceBay to be created for a new parent Device.
    """
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.CASCADE,
        related_name='device_bay_templates'
    )
    name = models.CharField(
        max_length=50
    )

    objects = NaturalOrderingManager()

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name

    def instantiate(self, device):
        return DeviceBay(
            device=device,
            name=self.name
        )


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

    csv_headers = ['name', 'slug', 'color', 'vm_role']

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
        null=True,
        unique=True
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
    face = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        choices=RACK_FACE_CHOICES,
        verbose_name='Rack face'
    )
    status = models.PositiveSmallIntegerField(
        choices=DEVICE_STATUS_CHOICES,
        default=DEVICE_STATUS_ACTIVE,
        verbose_name='Status'
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

    class Meta:
        ordering = ['name']
        unique_together = [
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

    def clean(self):

        # Validate site/rack combination
        if self.rack and self.site != self.rack.site:
            raise ValidationError({
                'rack': "Rack {} does not belong to site {}.".format(self.rack, self.site),
            })

        if self.rack is None:
            if self.face is not None:
                raise ValidationError({
                    'face': "Cannot select a rack face without assigning a rack.",
                })
            if self.position:
                raise ValidationError({
                    'face': "Cannot select a rack position without assigning a rack.",
                })

        # Validate position/face combination
        if self.position and self.face is None:
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
        return STATUS_CLASSES[self.status]


#
# Console ports
#

class ConsolePort(CableTermination, ComponentModel):
    """
    A physical console port within a Device. ConsolePorts connect to ConsoleServerPorts.
    """
    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.CASCADE,
        related_name='consoleports'
    )
    name = models.CharField(
        max_length=50
    )
    connected_endpoint = models.OneToOneField(
        to='dcim.ConsoleServerPort',
        on_delete=models.SET_NULL,
        related_name='connected_endpoint',
        blank=True,
        null=True
    )
    connection_status = models.NullBooleanField(
        choices=CONNECTION_STATUS_CHOICES,
        blank=True
    )

    objects = NaturalOrderingManager()
    tags = TaggableManager(through=TaggedItem)

    csv_headers = ['device', 'name', 'description']

    class Meta:
        ordering = ['device', 'name']
        unique_together = ['device', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return self.device.get_absolute_url()

    def to_csv(self):
        return (
            self.device.identifier,
            self.name,
            self.description,
        )


#
# Console server ports
#

class ConsoleServerPort(CableTermination, ComponentModel):
    """
    A physical port within a Device (typically a designated console server) which provides access to ConsolePorts.
    """
    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.CASCADE,
        related_name='consoleserverports'
    )
    name = models.CharField(
        max_length=50
    )
    connection_status = models.NullBooleanField(
        choices=CONNECTION_STATUS_CHOICES,
        blank=True
    )

    objects = NaturalOrderingManager()
    tags = TaggableManager(through=TaggedItem)

    csv_headers = ['device', 'name', 'description']

    class Meta:
        unique_together = ['device', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return self.device.get_absolute_url()

    def to_csv(self):
        return (
            self.device.identifier,
            self.name,
            self.description,
        )


#
# Power ports
#

class PowerPort(CableTermination, ComponentModel):
    """
    A physical power supply (intake) port within a Device. PowerPorts connect to PowerOutlets.
    """
    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.CASCADE,
        related_name='powerports'
    )
    name = models.CharField(
        max_length=50
    )
    maximum_draw = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Maximum current draw (watts)"
    )
    allocated_draw = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Allocated current draw (watts)"
    )
    _connected_poweroutlet = models.OneToOneField(
        to='dcim.PowerOutlet',
        on_delete=models.SET_NULL,
        related_name='connected_endpoint',
        blank=True,
        null=True
    )
    _connected_powerfeed = models.OneToOneField(
        to='dcim.PowerFeed',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True
    )
    connection_status = models.NullBooleanField(
        choices=CONNECTION_STATUS_CHOICES,
        blank=True
    )

    objects = NaturalOrderingManager()
    tags = TaggableManager(through=TaggedItem)

    csv_headers = ['device', 'name', 'maximum_draw', 'allocated_draw', 'description']

    class Meta:
        ordering = ['device', 'name']
        unique_together = ['device', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return self.device.get_absolute_url()

    def to_csv(self):
        return (
            self.device.identifier,
            self.name,
            self.maximum_draw,
            self.allocated_draw,
            self.description,
        )

    @property
    def connected_endpoint(self):
        if self._connected_poweroutlet:
            return self._connected_poweroutlet
        return self._connected_powerfeed

    @connected_endpoint.setter
    def connected_endpoint(self, value):
        if value is None:
            self._connected_poweroutlet = None
            self._connected_powerfeed = None
        elif isinstance(value, PowerOutlet):
            self._connected_poweroutlet = value
            self._connected_powerfeed = None
        elif isinstance(value, PowerFeed):
            self._connected_poweroutlet = None
            self._connected_powerfeed = value
        else:
            raise ValueError(
                "Connected endpoint must be a PowerOutlet or PowerFeed, not {}.".format(type(value))
            )

    def get_power_draw(self):
        """
        Return the allocated and maximum power draw (in VA) and child PowerOutlet count for this PowerPort.
        """
        # Calculate aggregate draw of all child power outlets if no numbers have been defined manually
        if self.allocated_draw is None and self.maximum_draw is None:
            outlet_ids = PowerOutlet.objects.filter(power_port=self).values_list('pk', flat=True)
            utilization = PowerPort.objects.filter(_connected_poweroutlet_id__in=outlet_ids).aggregate(
                maximum_draw_total=Sum('maximum_draw'),
                allocated_draw_total=Sum('allocated_draw'),
            )
            ret = {
                'allocated': utilization['allocated_draw_total'] or 0,
                'maximum': utilization['maximum_draw_total'] or 0,
                'outlet_count': len(outlet_ids),
                'legs': [],
            }

            # Calculate per-leg aggregates for three-phase feeds
            if self._connected_powerfeed and self._connected_powerfeed.phase == POWERFEED_PHASE_3PHASE:
                for leg, leg_name in POWERFEED_LEG_CHOICES:
                    outlet_ids = PowerOutlet.objects.filter(power_port=self, feed_leg=leg).values_list('pk', flat=True)
                    utilization = PowerPort.objects.filter(_connected_poweroutlet_id__in=outlet_ids).aggregate(
                        maximum_draw_total=Sum('maximum_draw'),
                        allocated_draw_total=Sum('allocated_draw'),
                    )
                    ret['legs'].append({
                        'name': leg_name,
                        'allocated': utilization['allocated_draw_total'] or 0,
                        'maximum': utilization['maximum_draw_total'] or 0,
                        'outlet_count': len(outlet_ids),
                    })

            return ret

        # Default to administratively defined values
        return {
            'allocated': self.allocated_draw or 0,
            'maximum': self.maximum_draw or 0,
            'outlet_count': PowerOutlet.objects.filter(power_port=self).count(),
            'legs': [],
        }


#
# Power outlets
#

class PowerOutlet(CableTermination, ComponentModel):
    """
    A physical power outlet (output) within a Device which provides power to a PowerPort.
    """
    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.CASCADE,
        related_name='poweroutlets'
    )
    name = models.CharField(
        max_length=50
    )
    power_port = models.ForeignKey(
        to='dcim.PowerPort',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='poweroutlets'
    )
    feed_leg = models.PositiveSmallIntegerField(
        choices=POWERFEED_LEG_CHOICES,
        blank=True,
        null=True,
        help_text="Phase (for three-phase feeds)"
    )
    connection_status = models.NullBooleanField(
        choices=CONNECTION_STATUS_CHOICES,
        blank=True
    )

    objects = NaturalOrderingManager()
    tags = TaggableManager(through=TaggedItem)

    csv_headers = ['device', 'name', 'power_port', 'feed_leg', 'description']

    class Meta:
        unique_together = ['device', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return self.device.get_absolute_url()

    def to_csv(self):
        return (
            self.device.identifier,
            self.name,
            self.power_port.name if self.power_port else None,
            self.get_feed_leg_display(),
            self.description,
        )

    def clean(self):

        # Validate power port assignment
        if self.power_port and self.power_port.device != self.device:
            raise ValidationError(
                "Parent power port ({}) must belong to the same device".format(self.power_port)
            )


#
# Interfaces
#

class Interface(CableTermination, ComponentModel):
    """
    A network interface within a Device or VirtualMachine. A physical Interface can connect to exactly one other
    Interface.
    """
    device = models.ForeignKey(
        to='Device',
        on_delete=models.CASCADE,
        related_name='interfaces',
        null=True,
        blank=True
    )
    virtual_machine = models.ForeignKey(
        to='virtualization.VirtualMachine',
        on_delete=models.CASCADE,
        related_name='interfaces',
        null=True,
        blank=True
    )
    name = models.CharField(
        max_length=64
    )
    _connected_interface = models.OneToOneField(
        to='self',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True
    )
    _connected_circuittermination = models.OneToOneField(
        to='circuits.CircuitTermination',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True
    )
    connection_status = models.NullBooleanField(
        choices=CONNECTION_STATUS_CHOICES,
        blank=True
    )
    lag = models.ForeignKey(
        to='self',
        on_delete=models.SET_NULL,
        related_name='member_interfaces',
        null=True,
        blank=True,
        verbose_name='Parent LAG'
    )
    type = models.PositiveSmallIntegerField(
        choices=IFACE_TYPE_CHOICES,
        default=IFACE_TYPE_10GE_SFP_PLUS
    )
    enabled = models.BooleanField(
        default=True
    )
    mac_address = MACAddressField(
        null=True,
        blank=True,
        verbose_name='MAC Address'
    )
    mtu = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(65536)],
        verbose_name='MTU'
    )
    mgmt_only = models.BooleanField(
        default=False,
        verbose_name='OOB Management',
        help_text='This interface is used only for out-of-band management'
    )
    mode = models.PositiveSmallIntegerField(
        choices=IFACE_MODE_CHOICES,
        blank=True,
        null=True
    )
    untagged_vlan = models.ForeignKey(
        to='ipam.VLAN',
        on_delete=models.SET_NULL,
        related_name='interfaces_as_untagged',
        null=True,
        blank=True,
        verbose_name='Untagged VLAN'
    )
    tagged_vlans = models.ManyToManyField(
        to='ipam.VLAN',
        related_name='interfaces_as_tagged',
        blank=True,
        verbose_name='Tagged VLANs'
    )

    objects = InterfaceManager()
    tags = TaggableManager(through=TaggedItem)

    csv_headers = [
        'device', 'virtual_machine', 'name', 'lag', 'type', 'enabled', 'mac_address', 'mtu', 'mgmt_only',
        'description', 'mode',
    ]

    class Meta:
        ordering = ['device', 'name']
        unique_together = ['device', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dcim:interface', kwargs={'pk': self.pk})

    def to_csv(self):
        return (
            self.device.identifier if self.device else None,
            self.virtual_machine.name if self.virtual_machine else None,
            self.name,
            self.lag.name if self.lag else None,
            self.get_type_display(),
            self.enabled,
            self.mac_address,
            self.mtu,
            self.mgmt_only,
            self.description,
            self.get_mode_display(),
        )

    def clean(self):

        # An Interface must belong to a Device *or* to a VirtualMachine
        if self.device and self.virtual_machine:
            raise ValidationError("An interface cannot belong to both a device and a virtual machine.")
        if not self.device and not self.virtual_machine:
            raise ValidationError("An interface must belong to either a device or a virtual machine.")

        # VM interfaces must be virtual
        if self.virtual_machine and self.type is not IFACE_TYPE_VIRTUAL:
            raise ValidationError({
                'type': "Virtual machines can only have virtual interfaces."
            })

        # Virtual interfaces cannot be connected
        if self.type in NONCONNECTABLE_IFACE_TYPES and (
                self.cable or getattr(self, 'circuit_termination', False)
        ):
            raise ValidationError({
                'type': "Virtual and wireless interfaces cannot be connected to another interface or circuit. "
                        "Disconnect the interface or choose a suitable type."
            })

        # An interface's LAG must belong to the same device (or VC master)
        if self.lag and self.lag.device not in [self.device, self.device.get_vc_master()]:
            raise ValidationError({
                'lag': "The selected LAG interface ({}) belongs to a different device ({}).".format(
                    self.lag.name, self.lag.device.name
                )
            })

        # A virtual interface cannot have a parent LAG
        if self.type in NONCONNECTABLE_IFACE_TYPES and self.lag is not None:
            raise ValidationError({
                'lag': "{} interfaces cannot have a parent LAG interface.".format(self.get_type_display())
            })

        # Only a LAG can have LAG members
        if self.type != IFACE_TYPE_LAG and self.member_interfaces.exists():
            raise ValidationError({
                'type': "Cannot change interface type; it has LAG members ({}).".format(
                    ", ".join([iface.name for iface in self.member_interfaces.all()])
                )
            })

        # Validate untagged VLAN
        if self.untagged_vlan and self.untagged_vlan.site not in [self.parent.site, None]:
            raise ValidationError({
                'untagged_vlan': "The untagged VLAN ({}) must belong to the same site as the interface's parent "
                                 "device/VM, or it must be global".format(self.untagged_vlan)
            })

    def save(self, *args, **kwargs):

        # Remove untagged VLAN assignment for non-802.1Q interfaces
        if self.mode is None:
            self.untagged_vlan = None

        # Only "tagged" interfaces may have tagged VLANs assigned. ("tagged all" implies all VLANs are assigned.)
        if self.pk and self.mode is not IFACE_MODE_TAGGED:
            self.tagged_vlans.clear()

        return super().save(*args, **kwargs)

    def to_objectchange(self, action):
        # Annotate the parent Device/VM
        try:
            parent_obj = self.device or self.virtual_machine
        except ObjectDoesNotExist:
            parent_obj = None

        return ObjectChange(
            changed_object=self,
            object_repr=str(self),
            action=action,
            related_object=parent_obj,
            object_data=serialize_object(self)
        )

    # TODO: Remove in v2.7
    @property
    def form_factor(self):
        """
        Backward-compatibility for form_factor
        """
        return self.type

    # TODO: Remove in v2.7
    @form_factor.setter
    def form_factor(self, value):
        """
        Backward-compatibility for form_factor
        """
        self.type = value

    @property
    def connected_endpoint(self):
        if self._connected_interface:
            return self._connected_interface
        return self._connected_circuittermination

    @connected_endpoint.setter
    def connected_endpoint(self, value):
        from circuits.models import CircuitTermination

        if value is None:
            self._connected_interface = None
            self._connected_circuittermination = None
        elif isinstance(value, Interface):
            self._connected_interface = value
            self._connected_circuittermination = None
        elif isinstance(value, CircuitTermination):
            self._connected_interface = None
            self._connected_circuittermination = value
        else:
            raise ValueError(
                "Connected endpoint must be an Interface or CircuitTermination, not {}.".format(type(value))
            )

    @property
    def parent(self):
        return self.device or self.virtual_machine

    @property
    def is_connectable(self):
        return self.type not in NONCONNECTABLE_IFACE_TYPES

    @property
    def is_virtual(self):
        return self.type in VIRTUAL_IFACE_TYPES

    @property
    def is_wireless(self):
        return self.type in WIRELESS_IFACE_TYPES

    @property
    def is_lag(self):
        return self.type == IFACE_TYPE_LAG

    @property
    def count_ipaddresses(self):
        return self.ip_addresses.count()


#
# Pass-through ports
#

class FrontPort(CableTermination, ComponentModel):
    """
    A pass-through port on the front of a Device.
    """
    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.CASCADE,
        related_name='frontports'
    )
    name = models.CharField(
        max_length=64
    )
    type = models.PositiveSmallIntegerField(
        choices=PORT_TYPE_CHOICES
    )
    rear_port = models.ForeignKey(
        to='dcim.RearPort',
        on_delete=models.CASCADE,
        related_name='frontports'
    )
    rear_port_position = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(64)]
    )

    objects = NaturalOrderingManager()
    tags = TaggableManager(through=TaggedItem)

    csv_headers = ['device', 'name', 'type', 'rear_port', 'rear_port_position', 'description']

    class Meta:
        ordering = ['device', 'name']
        unique_together = [
            ['device', 'name'],
            ['rear_port', 'rear_port_position'],
        ]

    def __str__(self):
        return self.name

    def to_csv(self):
        return (
            self.device.identifier,
            self.name,
            self.get_type_display(),
            self.rear_port.name,
            self.rear_port_position,
            self.description,
        )

    def clean(self):

        # Validate rear port assignment
        if self.rear_port.device != self.device:
            raise ValidationError(
                "Rear port ({}) must belong to the same device".format(self.rear_port)
            )

        # Validate rear port position assignment
        if self.rear_port_position > self.rear_port.positions:
            raise ValidationError(
                "Invalid rear port position ({}); rear port {} has only {} positions".format(
                    self.rear_port_position, self.rear_port.name, self.rear_port.positions
                )
            )


class RearPort(CableTermination, ComponentModel):
    """
    A pass-through port on the rear of a Device.
    """
    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.CASCADE,
        related_name='rearports'
    )
    name = models.CharField(
        max_length=64
    )
    type = models.PositiveSmallIntegerField(
        choices=PORT_TYPE_CHOICES
    )
    positions = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(64)]
    )

    objects = NaturalOrderingManager()
    tags = TaggableManager(through=TaggedItem)

    csv_headers = ['device', 'name', 'type', 'positions', 'description']

    class Meta:
        ordering = ['device', 'name']
        unique_together = ['device', 'name']

    def __str__(self):
        return self.name

    def to_csv(self):
        return (
            self.device.identifier,
            self.name,
            self.get_type_display(),
            self.positions,
            self.description,
        )


#
# Device bays
#

class DeviceBay(ComponentModel):
    """
    An empty space within a Device which can house a child device
    """
    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.CASCADE,
        related_name='device_bays'
    )
    name = models.CharField(
        max_length=50,
        verbose_name='Name'
    )
    installed_device = models.OneToOneField(
        to='dcim.Device',
        on_delete=models.SET_NULL,
        related_name='parent_bay',
        blank=True,
        null=True
    )

    objects = NaturalOrderingManager()
    tags = TaggableManager(through=TaggedItem)

    csv_headers = ['device', 'name', 'installed_device', 'description']

    class Meta:
        ordering = ['device', 'name']
        unique_together = ['device', 'name']

    def __str__(self):
        return '{} - {}'.format(self.device.name, self.name)

    def get_absolute_url(self):
        return self.device.get_absolute_url()

    def to_csv(self):
        return (
            self.device.identifier,
            self.name,
            self.installed_device.identifier if self.installed_device else None,
            self.description,
        )

    def clean(self):

        # Validate that the parent Device can have DeviceBays
        if not self.device.device_type.is_parent_device:
            raise ValidationError("This type of device ({}) does not support device bays.".format(
                self.device.device_type
            ))

        # Cannot install a device into itself, obviously
        if self.device == self.installed_device:
            raise ValidationError("Cannot install a device into itself.")


#
# Inventory items
#

class InventoryItem(ComponentModel):
    """
    An InventoryItem represents a serialized piece of hardware within a Device, such as a line card or power supply.
    InventoryItems are used only for inventory purposes.
    """
    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.CASCADE,
        related_name='inventory_items'
    )
    parent = models.ForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='child_items',
        blank=True,
        null=True
    )
    name = models.CharField(
        max_length=50,
        verbose_name='Name'
    )
    manufacturer = models.ForeignKey(
        to='dcim.Manufacturer',
        on_delete=models.PROTECT,
        related_name='inventory_items',
        blank=True,
        null=True
    )
    part_id = models.CharField(
        max_length=50,
        verbose_name='Part ID',
        blank=True
    )
    serial = models.CharField(
        max_length=50,
        verbose_name='Serial number',
        blank=True
    )
    asset_tag = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Asset tag',
        help_text='A unique tag used to identify this item'
    )
    discovered = models.BooleanField(
        default=False,
        verbose_name='Discovered'
    )

    tags = TaggableManager(through=TaggedItem)

    csv_headers = [
        'device', 'name', 'manufacturer', 'part_id', 'serial', 'asset_tag', 'discovered', 'description',
    ]

    class Meta:
        ordering = ['device__id', 'parent__id', 'name']
        unique_together = ['device', 'parent', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return self.device.get_absolute_url()

    def to_csv(self):
        return (
            self.device.name or '{{{}}}'.format(self.device.pk),
            self.name,
            self.manufacturer.name if self.manufacturer else None,
            self.part_id,
            self.serial,
            self.asset_tag,
            self.discovered,
            self.description,
        )


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

    def to_csv(self):
        return (
            self.master,
            self.domain,
        )


#
# Cables
#

class Cable(ChangeLoggedModel):
    """
    A physical connection between two endpoints.
    """
    termination_a_type = models.ForeignKey(
        to=ContentType,
        limit_choices_to={'model__in': CABLE_TERMINATION_TYPES},
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
        limit_choices_to={'model__in': CABLE_TERMINATION_TYPES},
        on_delete=models.PROTECT,
        related_name='+'
    )
    termination_b_id = models.PositiveIntegerField()
    termination_b = GenericForeignKey(
        ct_field='termination_b_type',
        fk_field='termination_b_id'
    )
    type = models.PositiveSmallIntegerField(
        choices=CABLE_TYPE_CHOICES,
        blank=True,
        null=True
    )
    status = models.BooleanField(
        choices=CONNECTION_STATUS_CHOICES,
        default=CONNECTION_STATUS_CONNECTED
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
    length_unit = models.PositiveSmallIntegerField(
        choices=CABLE_LENGTH_UNIT_CHOICES,
        blank=True,
        null=True
    )
    # Stores the normalized length (in meters) for database ordering
    _abs_length = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        blank=True,
        null=True
    )

    csv_headers = [
        'termination_a_type', 'termination_a_id', 'termination_b_type', 'termination_b_id', 'type', 'status', 'label',
        'color', 'length', 'length_unit',
    ]

    class Meta:
        ordering = ['pk']
        unique_together = (
            ('termination_a_type', 'termination_a_id'),
            ('termination_b_type', 'termination_b_id'),
        )

    def __str__(self):
        if self.label:
            return self.label

        # Save a copy of the PK on the instance since it's nullified if .delete() is called
        if not hasattr(self, 'id_string'):
            self.id_string = '#{}'.format(self.pk)

        return self.id_string

    def get_absolute_url(self):
        return reverse('dcim:cable', args=[self.pk])

    def clean(self):

        # Validate that termination A exists
        try:
            self.termination_a_type.model_class().objects.get(pk=self.termination_a_id)
        except ObjectDoesNotExist:
            raise ValidationError({
                'termination_a': 'Invalid ID for type {}'.format(self.termination_a_type)
            })

        # Validate that termination B exists
        try:
            self.termination_b_type.model_class().objects.get(pk=self.termination_b_id)
        except ObjectDoesNotExist:
            raise ValidationError({
                'termination_b': 'Invalid ID for type {}'.format(self.termination_b_type)
            })

        type_a = self.termination_a_type.model
        type_b = self.termination_b_type.model

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

        # Virtual interfaces cannot be connected
        endpoint_a, endpoint_b, _ = self.get_path_endpoints()
        if (
            (
                isinstance(endpoint_a, Interface) and
                endpoint_a.type == IFACE_TYPE_VIRTUAL
            ) or
            (
                isinstance(endpoint_b, Interface) and
                endpoint_b.type == IFACE_TYPE_VIRTUAL
            )
        ):
            raise ValidationError("Cannot connect to a virtual interface")

        # Validate length and length_unit
        if self.length is not None and self.length_unit is None:
            raise ValidationError("Must specify a unit when setting a cable length")
        elif self.length is None:
            self.length_unit = None

    def save(self, *args, **kwargs):

        # Store the given length (if any) in meters for use in database ordering
        if self.length and self.length_unit:
            self._abs_length = to_meters(self.length, self.length_unit)

        super().save(*args, **kwargs)

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
        return 'success' if self.status else 'info'

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
        if self.status == CONNECTION_STATUS_PLANNED:
            path_status = CONNECTION_STATUS_PLANNED
        else:
            path_status = CONNECTION_STATUS_CONNECTED
            for segment in a_path[1:] + b_path[1:]:
                if segment[1] is None or segment[1].status == CONNECTION_STATUS_PLANNED:
                    path_status = CONNECTION_STATUS_PLANNED
                    break

        a_endpoint = a_path[-1][2]
        b_endpoint = b_path[-1][2]

        return a_endpoint, b_endpoint, path_status


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
    status = models.PositiveSmallIntegerField(
        choices=POWERFEED_STATUS_CHOICES,
        default=POWERFEED_STATUS_ACTIVE
    )
    type = models.PositiveSmallIntegerField(
        choices=POWERFEED_TYPE_CHOICES,
        default=POWERFEED_TYPE_PRIMARY
    )
    supply = models.PositiveSmallIntegerField(
        choices=POWERFEED_SUPPLY_CHOICES,
        default=POWERFEED_SUPPLY_AC
    )
    phase = models.PositiveSmallIntegerField(
        choices=POWERFEED_PHASE_CHOICES,
        default=POWERFEED_PHASE_SINGLE
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
    available_power = models.PositiveSmallIntegerField(
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

    class Meta:
        ordering = ['power_panel', 'name']
        unique_together = ['power_panel', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dcim:powerfeed', args=[self.pk])

    def to_csv(self):
        return (
            self.power_panel.name,
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
        if self.phase == POWERFEED_PHASE_3PHASE:
            self.available_power = round(kva * 1.732)
        else:
            self.available_power = round(kva)

        super().save(*args, **kwargs)

    def get_type_class(self):
        return STATUS_CLASSES[self.type]

    def get_status_class(self):
        return STATUS_CLASSES[self.status]
