from __future__ import unicode_literals

from collections import OrderedDict
from itertools import count, groupby

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Count, Q, ObjectDoesNotExist
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from mptt.models import MPTTModel, TreeForeignKey

from circuits.models import Circuit
from extras.models import CustomFieldModel, CustomFieldValue, ImageAttachment
from extras.rpc import RPC_CLIENTS
from tenancy.models import Tenant
from utilities.fields import ColorField, NullableCharField
from utilities.managers import NaturalOrderByManager
from utilities.models import CreatedUpdatedModel
from utilities.utils import csv_format
from .constants import *
from .fields import ASNField, MACAddressField
from .querysets import InterfaceQuerySet


#
# Regions
#

@python_2_unicode_compatible
class Region(MPTTModel):
    """
    Sites can be grouped within geographic Regions.
    """
    parent = TreeForeignKey(
        'self', null=True, blank=True, related_name='children', db_index=True, on_delete=models.CASCADE
    )
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    csv_headers = [
        'name', 'slug', 'parent',
    ]

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "{}?region={}".format(reverse('dcim:site_list'), self.slug)

    def to_csv(self):
        return csv_format([
            self.name,
            self.slug,
            self.parent.name if self.parent else None,
        ])


#
# Sites
#

class SiteManager(NaturalOrderByManager):

    def get_queryset(self):
        return self.natural_order_by('name')


@python_2_unicode_compatible
class Site(CreatedUpdatedModel, CustomFieldModel):
    """
    A Site represents a geographic location within a network; typically a building or campus. The optional facility
    field can be used to include an external designation, such as a data center name (e.g. Equinix SV6).
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    region = models.ForeignKey('Region', related_name='sites', blank=True, null=True, on_delete=models.SET_NULL)
    tenant = models.ForeignKey(Tenant, related_name='sites', blank=True, null=True, on_delete=models.PROTECT)
    facility = models.CharField(max_length=50, blank=True)
    asn = ASNField(blank=True, null=True, verbose_name='ASN')
    physical_address = models.CharField(max_length=200, blank=True)
    shipping_address = models.CharField(max_length=200, blank=True)
    contact_name = models.CharField(max_length=50, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True, verbose_name="Contact E-mail")
    comments = models.TextField(blank=True)
    custom_field_values = GenericRelation(CustomFieldValue, content_type_field='obj_type', object_id_field='obj_id')
    images = GenericRelation(ImageAttachment)

    objects = SiteManager()

    csv_headers = [
        'name', 'slug', 'region', 'tenant', 'facility', 'asn', 'contact_name', 'contact_phone', 'contact_email',
    ]

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dcim:site', args=[self.slug])

    def to_csv(self):
        return csv_format([
            self.name,
            self.slug,
            self.region.name if self.region else None,
            self.tenant.name if self.tenant else None,
            self.facility,
            self.asn,
            self.contact_name,
            self.contact_phone,
            self.contact_email,
        ])

    @property
    def count_prefixes(self):
        return self.prefixes.count()

    @property
    def count_vlans(self):
        return self.vlans.count()

    @property
    def count_racks(self):
        return Rack.objects.filter(site=self).count()

    @property
    def count_devices(self):
        return Device.objects.filter(site=self).count()

    @property
    def count_circuits(self):
        return Circuit.objects.filter(terminations__site=self).count()

    @property
    def count_vms(self):
        from virtualization.models import VirtualMachine
        return VirtualMachine.objects.filter(cluster__site=self).count()


#
# Racks
#

@python_2_unicode_compatible
class RackGroup(models.Model):
    """
    Racks can be grouped as subsets within a Site. The scope of a group will depend on how Sites are defined. For
    example, if a Site spans a corporate campus, a RackGroup might be defined to represent each building within that
    campus. If a Site instead represents a single building, a RackGroup might represent a single room or floor.
    """
    name = models.CharField(max_length=50)
    slug = models.SlugField()
    site = models.ForeignKey('Site', related_name='rack_groups', on_delete=models.CASCADE)

    csv_headers = [
        'site', 'name', 'slug',
    ]

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
        return csv_format([
            self.site,
            self.name,
            self.slug,
        ])


@python_2_unicode_compatible
class RackRole(models.Model):
    """
    Racks can be organized by functional role, similar to Devices.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    color = ColorField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "{}?role={}".format(reverse('dcim:rack_list'), self.slug)


class RackManager(NaturalOrderByManager):

    def get_queryset(self):
        return self.natural_order_by('site__name', 'name')


@python_2_unicode_compatible
class Rack(CreatedUpdatedModel, CustomFieldModel):
    """
    Devices are housed within Racks. Each rack has a defined height measured in rack units, and a front and rear face.
    Each Rack is assigned to a Site and (optionally) a RackGroup.
    """
    name = models.CharField(max_length=50)
    facility_id = NullableCharField(max_length=50, blank=True, null=True, verbose_name='Facility ID')
    site = models.ForeignKey('Site', related_name='racks', on_delete=models.PROTECT)
    group = models.ForeignKey('RackGroup', related_name='racks', blank=True, null=True, on_delete=models.SET_NULL)
    tenant = models.ForeignKey(Tenant, blank=True, null=True, related_name='racks', on_delete=models.PROTECT)
    role = models.ForeignKey('RackRole', related_name='racks', blank=True, null=True, on_delete=models.PROTECT)
    serial = models.CharField(max_length=50, blank=True, verbose_name='Serial number')
    type = models.PositiveSmallIntegerField(choices=RACK_TYPE_CHOICES, blank=True, null=True, verbose_name='Type')
    width = models.PositiveSmallIntegerField(choices=RACK_WIDTH_CHOICES, default=RACK_WIDTH_19IN, verbose_name='Width',
                                             help_text='Rail-to-rail width')
    u_height = models.PositiveSmallIntegerField(default=42, verbose_name='Height (U)',
                                                validators=[MinValueValidator(1), MaxValueValidator(100)])
    desc_units = models.BooleanField(default=False, verbose_name='Descending units',
                                     help_text='Units are numbered top-to-bottom')
    comments = models.TextField(blank=True)
    custom_field_values = GenericRelation(CustomFieldValue, content_type_field='obj_type', object_id_field='obj_id')
    images = GenericRelation(ImageAttachment)

    objects = RackManager()

    csv_headers = [
        'site', 'group_name', 'name', 'facility_id', 'tenant', 'role', 'type', 'serial', 'width', 'u_height',
        'desc_units',
    ]

    class Meta:
        ordering = ['site', 'name']
        unique_together = [
            ['site', 'name'],
            ['site', 'facility_id'],
        ]

    def __str__(self):
        return self.display_name or super(Rack, self).__str__()

    def get_absolute_url(self):
        return reverse('dcim:rack', args=[self.pk])

    def clean(self):

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

        super(Rack, self).save(*args, **kwargs)

        # Update racked devices if the assigned Site has been changed.
        if _site_id is not None and self.site_id != _site_id:
            Device.objects.filter(rack=self).update(site_id=self.site.pk)

    def to_csv(self):
        return csv_format([
            self.site.name,
            self.group.name if self.group else None,
            self.name,
            self.facility_id,
            self.tenant.name if self.tenant else None,
            self.role.name if self.role else None,
            self.get_type_display() if self.type else None,
            self.serial,
            self.width,
            self.u_height,
            self.desc_units,
        ])

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
            for device in Device.objects.select_related('device_type__manufacturer', 'device_role')\
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
        devices = self.devices.select_related('device_type').filter(position__gte=1).exclude(pk__in=exclude)

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


@python_2_unicode_compatible
class RackReservation(models.Model):
    """
    One or more reserved units within a Rack.
    """
    rack = models.ForeignKey('Rack', related_name='reservations', on_delete=models.CASCADE)
    units = ArrayField(models.PositiveSmallIntegerField())
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    description = models.CharField(max_length=100)

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

@python_2_unicode_compatible
class Manufacturer(models.Model):
    """
    A Manufacturer represents a company which produces hardware devices; for example, Juniper or Dell.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    csv_headers = [
        'name', 'slug',
    ]

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "{}?manufacturer={}".format(reverse('dcim:devicetype_list'), self.slug)

    def to_csv(self):
        return csv_format([
            self.name,
            self.slug,
        ])


@python_2_unicode_compatible
class DeviceType(models.Model, CustomFieldModel):
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
    manufacturer = models.ForeignKey('Manufacturer', related_name='device_types', on_delete=models.PROTECT)
    model = models.CharField(max_length=50)
    slug = models.SlugField()
    part_number = models.CharField(max_length=50, blank=True, help_text="Discrete part number (optional)")
    u_height = models.PositiveSmallIntegerField(verbose_name='Height (U)', default=1)
    is_full_depth = models.BooleanField(default=True, verbose_name="Is full depth",
                                        help_text="Device consumes both front and rear rack faces")
    interface_ordering = models.PositiveSmallIntegerField(choices=IFACE_ORDERING_CHOICES,
                                                          default=IFACE_ORDERING_POSITION)
    is_console_server = models.BooleanField(default=False, verbose_name='Is a console server',
                                            help_text="This type of device has console server ports")
    is_pdu = models.BooleanField(default=False, verbose_name='Is a PDU',
                                 help_text="This type of device has power outlets")
    is_network_device = models.BooleanField(default=True, verbose_name='Is a network device',
                                            help_text="This type of device has network interfaces")
    subdevice_role = models.NullBooleanField(default=None, verbose_name='Parent/child status',
                                             choices=SUBDEVICE_ROLE_CHOICES,
                                             help_text="Parent devices house child devices in device bays. Select "
                                                       "\"None\" if this device type is neither a parent nor a child.")
    comments = models.TextField(blank=True)
    custom_field_values = GenericRelation(CustomFieldValue, content_type_field='obj_type', object_id_field='obj_id')

    csv_headers = [
        'manufacturer', 'model', 'slug', 'part_number', 'u_height', 'is_full_depth', 'is_console_server',
        'is_pdu', 'is_network_device', 'subdevice_role', 'interface_ordering',
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
        super(DeviceType, self).__init__(*args, **kwargs)

        # Save a copy of u_height for validation in clean()
        self._original_u_height = self.u_height

    def get_absolute_url(self):
        return reverse('dcim:devicetype', args=[self.pk])

    def to_csv(self):
        return csv_format([
            self.manufacturer.name,
            self.model,
            self.slug,
            self.part_number,
            self.u_height,
            self.is_full_depth,
            self.is_console_server,
            self.is_pdu,
            self.is_network_device,
            self.get_subdevice_role_display() if self.subdevice_role else None,
            self.get_interface_ordering_display(),
        ])

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

        if not self.is_console_server and self.cs_port_templates.count():
            raise ValidationError({
                'is_console_server': "Must delete all console server port templates associated with this device before "
                                     "declassifying it as a console server."
            })

        if not self.is_pdu and self.power_outlet_templates.count():
            raise ValidationError({
                'is_pdu': "Must delete all power outlet templates associated with this device before declassifying it "
                          "as a PDU."
            })

        if not self.is_network_device and self.interface_templates.filter(mgmt_only=False).count():
            raise ValidationError({
                'is_network_device': "Must delete all non-management-only interface templates associated with this "
                                     "device before declassifying it as a network device."
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
    def full_name(self):
        return '{} {}'.format(self.manufacturer.name, self.model)

    @property
    def is_parent_device(self):
        return bool(self.subdevice_role)

    @property
    def is_child_device(self):
        return bool(self.subdevice_role is False)


@python_2_unicode_compatible
class ConsolePortTemplate(models.Model):
    """
    A template for a ConsolePort to be created for a new Device.
    """
    device_type = models.ForeignKey('DeviceType', related_name='console_port_templates', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class ConsoleServerPortTemplate(models.Model):
    """
    A template for a ConsoleServerPort to be created for a new Device.
    """
    device_type = models.ForeignKey('DeviceType', related_name='cs_port_templates', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class PowerPortTemplate(models.Model):
    """
    A template for a PowerPort to be created for a new Device.
    """
    device_type = models.ForeignKey('DeviceType', related_name='power_port_templates', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class PowerOutletTemplate(models.Model):
    """
    A template for a PowerOutlet to be created for a new Device.
    """
    device_type = models.ForeignKey('DeviceType', related_name='power_outlet_templates', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class InterfaceTemplate(models.Model):
    """
    A template for a physical data interface on a new Device.
    """
    device_type = models.ForeignKey('DeviceType', related_name='interface_templates', on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    form_factor = models.PositiveSmallIntegerField(choices=IFACE_FF_CHOICES, default=IFACE_FF_10GE_SFP_PLUS)
    mgmt_only = models.BooleanField(default=False, verbose_name='Management only')

    objects = InterfaceQuerySet.as_manager()

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class DeviceBayTemplate(models.Model):
    """
    A template for a DeviceBay to be created for a new parent Device.
    """
    device_type = models.ForeignKey('DeviceType', related_name='device_bay_templates', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['device_type', 'name']
        unique_together = ['device_type', 'name']

    def __str__(self):
        return self.name


#
# Devices
#

@python_2_unicode_compatible
class DeviceRole(models.Model):
    """
    Devices are organized by functional role; for example, "Core Switch" or "File Server". Each DeviceRole is assigned a
    color to be used when displaying rack elevations. The vm_role field determines whether the role is applicable to
    virtual machines as well.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    color = ColorField()
    vm_role = models.BooleanField(
        default=True,
        verbose_name="VM Role",
        help_text="Virtual machines may be assigned to this role"
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "{}?role={}".format(reverse('dcim:device_list'), self.slug)


@python_2_unicode_compatible
class Platform(models.Model):
    """
    Platform refers to the software or firmware running on a Device; for example, "Cisco IOS-XR" or "Juniper Junos".
    NetBox uses Platforms to determine how to interact with devices when pulling inventory data or other information by
    specifying an remote procedure call (RPC) client.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    napalm_driver = models.CharField(max_length=50, blank=True, verbose_name='NAPALM driver',
                                     help_text="The name of the NAPALM driver to use when interacting with devices.")
    rpc_client = models.CharField(max_length=30, choices=RPC_CLIENT_CHOICES, blank=True,
                                  verbose_name='Legacy RPC client')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "{}?platform={}".format(reverse('dcim:device_list'), self.slug)


class DeviceManager(NaturalOrderByManager):

    def get_queryset(self):
        return self.natural_order_by('name')


@python_2_unicode_compatible
class Device(CreatedUpdatedModel, CustomFieldModel):
    """
    A Device represents a piece of physical hardware mounted within a Rack. Each Device is assigned a DeviceType,
    DeviceRole, and (optionally) a Platform. Device names are not required, however if one is set it must be unique.

    Each Device must be assigned to a site, and optionally to a rack within that site. Associating a device with a
    particular rack face or unit is optional (for example, vertically mounted PDUs do not consume rack units).

    When a new Device is created, console/power/interface/device bay components are created along with it as dictated
    by the component templates assigned to its DeviceType. Components can also be added, modified, or deleted after the
    creation of a Device.
    """
    device_type = models.ForeignKey('DeviceType', related_name='instances', on_delete=models.PROTECT)
    device_role = models.ForeignKey('DeviceRole', related_name='devices', on_delete=models.PROTECT)
    tenant = models.ForeignKey(Tenant, blank=True, null=True, related_name='devices', on_delete=models.PROTECT)
    platform = models.ForeignKey('Platform', related_name='devices', blank=True, null=True, on_delete=models.SET_NULL)
    name = NullableCharField(max_length=64, blank=True, null=True, unique=True)
    serial = models.CharField(max_length=50, blank=True, verbose_name='Serial number')
    asset_tag = NullableCharField(
        max_length=50, blank=True, null=True, unique=True, verbose_name='Asset tag',
        help_text='A unique tag used to identify this device'
    )
    site = models.ForeignKey('Site', related_name='devices', on_delete=models.PROTECT)
    rack = models.ForeignKey('Rack', related_name='devices', blank=True, null=True, on_delete=models.PROTECT)
    position = models.PositiveSmallIntegerField(
        blank=True, null=True, validators=[MinValueValidator(1)], verbose_name='Position (U)',
        help_text='The lowest-numbered unit occupied by the device'
    )
    face = models.PositiveSmallIntegerField(blank=True, null=True, choices=RACK_FACE_CHOICES, verbose_name='Rack face')
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=STATUS_ACTIVE, verbose_name='Status')
    primary_ip4 = models.OneToOneField(
        'ipam.IPAddress', related_name='primary_ip4_for', on_delete=models.SET_NULL, blank=True, null=True,
        verbose_name='Primary IPv4'
    )
    primary_ip6 = models.OneToOneField(
        'ipam.IPAddress', related_name='primary_ip6_for', on_delete=models.SET_NULL, blank=True, null=True,
        verbose_name='Primary IPv6'
    )
    cluster = models.ForeignKey(
        to='virtualization.Cluster',
        on_delete=models.SET_NULL,
        related_name='devices',
        blank=True,
        null=True
    )
    comments = models.TextField(blank=True)
    custom_field_values = GenericRelation(CustomFieldValue, content_type_field='obj_type', object_id_field='obj_id')
    images = GenericRelation(ImageAttachment)

    objects = DeviceManager()

    csv_headers = [
        'name', 'device_role', 'tenant', 'manufacturer', 'model_name', 'platform', 'serial', 'asset_tag', 'status',
        'site', 'rack_group', 'rack_name', 'position', 'face',
    ]

    class Meta:
        ordering = ['name']
        unique_together = ['rack', 'position', 'face']
        permissions = (
            ('napalm_read', 'Read-only access to devices via NAPALM'),
            ('napalm_write', 'Read/write access to devices via NAPALM'),
        )

    def __str__(self):
        return self.display_name or super(Device, self).__str__()

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

        # Validate primary IPv4 address
        if self.primary_ip4 and (
            self.primary_ip4.interface is None or
            self.primary_ip4.interface.device != self
        ) and (
            self.primary_ip4.nat_inside.interface is None or
            self.primary_ip4.nat_inside.interface.device != self
        ):
            raise ValidationError({
                'primary_ip4': "The specified IP address ({}) is not assigned to this device.".format(self.primary_ip4),
            })

        # Validate primary IPv6 address
        if self.primary_ip6 and (
            self.primary_ip6.interface is None or
            self.primary_ip6.interface.device != self
        ) and (
            self.primary_ip6.nat_inside.interface is None or
            self.primary_ip6.nat_inside.interface.device != self
        ):
            raise ValidationError({
                'primary_ip6': "The specified IP address ({}) is not assigned to this device.".format(self.primary_ip6),
            })

        # A Device can only be assigned to a Cluster in the same Site (or no Site)
        if self.cluster and self.cluster.site is not None and self.cluster.site != self.site:
            raise ValidationError({
                'cluster': "The assigned cluster belongs to a different site ({})".format(self.cluster.site)
            })

    def save(self, *args, **kwargs):

        is_new = not bool(self.pk)

        super(Device, self).save(*args, **kwargs)

        # If this is a new Device, instantiate all of the related components per the DeviceType definition
        if is_new:
            ConsolePort.objects.bulk_create(
                [ConsolePort(device=self, name=template.name) for template in
                 self.device_type.console_port_templates.all()]
            )
            ConsoleServerPort.objects.bulk_create(
                [ConsoleServerPort(device=self, name=template.name) for template in
                 self.device_type.cs_port_templates.all()]
            )
            PowerPort.objects.bulk_create(
                [PowerPort(device=self, name=template.name) for template in
                 self.device_type.power_port_templates.all()]
            )
            PowerOutlet.objects.bulk_create(
                [PowerOutlet(device=self, name=template.name) for template in
                 self.device_type.power_outlet_templates.all()]
            )
            Interface.objects.bulk_create(
                [Interface(device=self, name=template.name, form_factor=template.form_factor,
                           mgmt_only=template.mgmt_only) for template in self.device_type.interface_templates.all()]
            )
            DeviceBay.objects.bulk_create(
                [DeviceBay(device=self, name=template.name) for template in
                 self.device_type.device_bay_templates.all()]
            )

        # Update Site and Rack assignment for any child Devices
        Device.objects.filter(parent_bay__device=self).update(site=self.site, rack=self.rack)

    def to_csv(self):
        return csv_format([
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
        ])

    @property
    def display_name(self):
        if self.name:
            return self.name
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

    def get_children(self):
        """
        Return the set of child Devices installed in DeviceBays within this Device.
        """
        return Device.objects.filter(parent_bay__device=self.pk)

    def get_status_class(self):
        return DEVICE_STATUS_CLASSES[self.status]

    def get_rpc_client(self):
        """
        Return the appropriate RPC (e.g. NETCONF, ssh, etc.) client for this device's platform, if one is defined.
        """
        if not self.platform:
            return None
        return RPC_CLIENTS.get(self.platform.rpc_client)


#
# Console ports
#

@python_2_unicode_compatible
class ConsolePort(models.Model):
    """
    A physical console port within a Device. ConsolePorts connect to ConsoleServerPorts.
    """
    device = models.ForeignKey('Device', related_name='console_ports', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    cs_port = models.OneToOneField('ConsoleServerPort', related_name='connected_console', on_delete=models.SET_NULL,
                                   verbose_name='Console server port', blank=True, null=True)
    connection_status = models.NullBooleanField(choices=CONNECTION_STATUS_CHOICES, default=CONNECTION_STATUS_CONNECTED)

    csv_headers = ['console_server', 'cs_port', 'device', 'console_port', 'connection_status']

    class Meta:
        ordering = ['device', 'name']
        unique_together = ['device', 'name']

    def __str__(self):
        return self.name

    # Used for connections export
    def to_csv(self):
        return csv_format([
            self.cs_port.device.identifier if self.cs_port else None,
            self.cs_port.name if self.cs_port else None,
            self.device.identifier,
            self.name,
            self.get_connection_status_display(),
        ])


#
# Console server ports
#

class ConsoleServerPortManager(models.Manager):

    def get_queryset(self):
        # Pad any trailing digits to effect natural sorting
        return super(ConsoleServerPortManager, self).get_queryset().extra(select={
            'name_padded': "CONCAT(REGEXP_REPLACE(dcim_consoleserverport.name, '\d+$', ''), "
                           "LPAD(SUBSTRING(dcim_consoleserverport.name FROM '\d+$'), 8, '0'))",
        }).order_by('device', 'name_padded')


@python_2_unicode_compatible
class ConsoleServerPort(models.Model):
    """
    A physical port within a Device (typically a designated console server) which provides access to ConsolePorts.
    """
    device = models.ForeignKey('Device', related_name='cs_ports', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    objects = ConsoleServerPortManager()

    class Meta:
        unique_together = ['device', 'name']

    def __str__(self):
        return self.name

    def clean(self):

        # Check that the parent device's DeviceType is a console server
        if self.device is None:
            raise ValidationError("Console server ports must be assigned to devices.")
        device_type = self.device.device_type
        if not device_type.is_console_server:
            raise ValidationError("The {} {} device type not support assignment of console server ports.".format(
                device_type.manufacturer, device_type
            ))


#
# Power ports
#

@python_2_unicode_compatible
class PowerPort(models.Model):
    """
    A physical power supply (intake) port within a Device. PowerPorts connect to PowerOutlets.
    """
    device = models.ForeignKey('Device', related_name='power_ports', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    power_outlet = models.OneToOneField('PowerOutlet', related_name='connected_port', on_delete=models.SET_NULL,
                                        blank=True, null=True)
    connection_status = models.NullBooleanField(choices=CONNECTION_STATUS_CHOICES, default=CONNECTION_STATUS_CONNECTED)

    csv_headers = ['pdu', 'power_outlet', 'device', 'power_port', 'connection_status']

    class Meta:
        ordering = ['device', 'name']
        unique_together = ['device', 'name']

    def __str__(self):
        return self.name

    # Used for connections export
    def to_csv(self):
        return csv_format([
            self.power_outlet.device.identifier if self.power_outlet else None,
            self.power_outlet.name if self.power_outlet else None,
            self.device.identifier,
            self.name,
            self.get_connection_status_display(),
        ])


#
# Power outlets
#

class PowerOutletManager(models.Manager):

    def get_queryset(self):
        # Pad any trailing digits to effect natural sorting
        return super(PowerOutletManager, self).get_queryset().extra(select={
            'name_padded': "CONCAT(REGEXP_REPLACE(dcim_poweroutlet.name, '\d+$', ''), "
                           "LPAD(SUBSTRING(dcim_poweroutlet.name FROM '\d+$'), 8, '0'))",
        }).order_by('device', 'name_padded')


@python_2_unicode_compatible
class PowerOutlet(models.Model):
    """
    A physical power outlet (output) within a Device which provides power to a PowerPort.
    """
    device = models.ForeignKey('Device', related_name='power_outlets', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    objects = PowerOutletManager()

    class Meta:
        unique_together = ['device', 'name']

    def __str__(self):
        return self.name

    def clean(self):

        # Check that the parent device's DeviceType is a PDU
        if self.device is None:
            raise ValidationError("Power outlets must be assigned to devices.")
        device_type = self.device.device_type
        if not device_type.is_pdu:
            raise ValidationError("The {} {} device type not support assignment of power outlets.".format(
                device_type.manufacturer, device_type
            ))


#
# Interfaces
#

@python_2_unicode_compatible
class Interface(models.Model):
    """
    A network interface within a Device or VirtualMachine. A physical Interface can connect to exactly one other
    Interface via the creation of an InterfaceConnection.
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
    lag = models.ForeignKey(
        to='self',
        on_delete=models.SET_NULL,
        related_name='member_interfaces',
        null=True,
        blank=True,
        verbose_name='Parent LAG'
    )
    name = models.CharField(max_length=64)
    form_factor = models.PositiveSmallIntegerField(choices=IFACE_FF_CHOICES, default=IFACE_FF_10GE_SFP_PLUS)
    enabled = models.BooleanField(default=True)
    mac_address = MACAddressField(null=True, blank=True, verbose_name='MAC Address')
    mtu = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='MTU')
    mgmt_only = models.BooleanField(
        default=False,
        verbose_name='OOB Management',
        help_text="This interface is used only for out-of-band management"
    )
    description = models.CharField(max_length=100, blank=True)

    objects = InterfaceQuerySet.as_manager()

    class Meta:
        ordering = ['device', 'name']
        unique_together = ['device', 'name']

    def __str__(self):
        return self.name

    def clean(self):

        # Check that the parent device's DeviceType is a network device
        if self.device is not None:
            device_type = self.device.device_type
            if not device_type.is_network_device:
                raise ValidationError("The {} {} device type not support assignment of network interfaces.".format(
                    device_type.manufacturer, device_type
                ))

        # An Interface must belong to a Device *or* to a VirtualMachine
        if self.device and self.virtual_machine:
            raise ValidationError("An interface cannot belong to both a device and a virtual machine.")
        if not self.device and not self.virtual_machine:
            raise ValidationError("An interface must belong to either a device or a virtual machine.")

        # VM interfaces must be virtual
        if self.virtual_machine and self.form_factor is not IFACE_FF_VIRTUAL:
            raise ValidationError({
                'form_factor': "Virtual machines can only have virtual interfaces."
            })

        # Virtual interfaces cannot be connected
        if self.form_factor in NONCONNECTABLE_IFACE_TYPES and self.is_connected:
            raise ValidationError({
                'form_factor': "Virtual and wireless interfaces cannot be connected to another interface or circuit. "
                               "Disconnect the interface or choose a suitable form factor."
            })

        # An interface's LAG must belong to the same device
        if self.lag and self.lag.device != self.device:
            raise ValidationError({
                'lag': "The selected LAG interface ({}) belongs to a different device ({}).".format(
                    self.lag.name, self.lag.device.name
                )
            })

        # A virtual interface cannot have a parent LAG
        if self.form_factor in NONCONNECTABLE_IFACE_TYPES and self.lag is not None:
            raise ValidationError({
                'lag': "{} interfaces cannot have a parent LAG interface.".format(self.get_form_factor_display())
            })

        # Only a LAG can have LAG members
        if self.form_factor != IFACE_FF_LAG and self.member_interfaces.exists():
            raise ValidationError({
                'form_factor': "Cannot change interface form factor; it has LAG members ({}).".format(
                    ", ".join([iface.name for iface in self.member_interfaces.all()])
                )
            })

    @property
    def parent(self):
        return self.device or self.virtual_machine

    @property
    def is_virtual(self):
        return self.form_factor in VIRTUAL_IFACE_TYPES

    @property
    def is_wireless(self):
        return self.form_factor in WIRELESS_IFACE_TYPES

    @property
    def is_lag(self):
        return self.form_factor == IFACE_FF_LAG

    @property
    def is_connected(self):
        try:
            return bool(self.circuit_termination)
        except ObjectDoesNotExist:
            pass
        return bool(self.connection)

    @property
    def connection(self):
        try:
            return self.connected_as_a
        except ObjectDoesNotExist:
            pass
        try:
            return self.connected_as_b
        except ObjectDoesNotExist:
            pass
        return None

    @property
    def connected_interface(self):
        try:
            if self.connected_as_a:
                return self.connected_as_a.interface_b
        except ObjectDoesNotExist:
            pass
        try:
            if self.connected_as_b:
                return self.connected_as_b.interface_a
        except ObjectDoesNotExist:
            pass
        return None


class InterfaceConnection(models.Model):
    """
    An InterfaceConnection represents a symmetrical, one-to-one connection between two Interfaces. There is no
    significant difference between the interface_a and interface_b fields.
    """
    interface_a = models.OneToOneField('Interface', related_name='connected_as_a', on_delete=models.CASCADE)
    interface_b = models.OneToOneField('Interface', related_name='connected_as_b', on_delete=models.CASCADE)
    connection_status = models.BooleanField(choices=CONNECTION_STATUS_CHOICES, default=CONNECTION_STATUS_CONNECTED,
                                            verbose_name='Status')

    csv_headers = ['device_a', 'interface_a', 'device_b', 'interface_b', 'connection_status']

    def clean(self):
        try:
            if self.interface_a == self.interface_b:
                raise ValidationError({
                    'interface_b': "Cannot connect an interface to itself."
                })
        except ObjectDoesNotExist:
            pass

    # Used for connections export
    def to_csv(self):
        return csv_format([
            self.interface_a.device.identifier,
            self.interface_a.name,
            self.interface_b.device.identifier,
            self.interface_b.name,
            self.get_connection_status_display(),
        ])


#
# Device bays
#

@python_2_unicode_compatible
class DeviceBay(models.Model):
    """
    An empty space within a Device which can house a child device
    """
    device = models.ForeignKey('Device', related_name='device_bays', on_delete=models.CASCADE)
    name = models.CharField(max_length=50, verbose_name='Name')
    installed_device = models.OneToOneField('Device', related_name='parent_bay', on_delete=models.SET_NULL, blank=True,
                                            null=True)

    class Meta:
        ordering = ['device', 'name']
        unique_together = ['device', 'name']

    def __str__(self):
        return '{} - {}'.format(self.device.name, self.name)

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

@python_2_unicode_compatible
class InventoryItem(models.Model):
    """
    An InventoryItem represents a serialized piece of hardware within a Device, such as a line card or power supply.
    InventoryItems are used only for inventory purposes.
    """
    device = models.ForeignKey('Device', related_name='inventory_items', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', related_name='child_items', blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, verbose_name='Name')
    manufacturer = models.ForeignKey(
        'Manufacturer', models.PROTECT, related_name='inventory_items', blank=True, null=True
    )
    part_id = models.CharField(max_length=50, verbose_name='Part ID', blank=True)
    serial = models.CharField(max_length=50, verbose_name='Serial number', blank=True)
    asset_tag = NullableCharField(
        max_length=50, blank=True, null=True, unique=True, verbose_name='Asset tag',
        help_text='A unique tag used to identify this item'
    )
    discovered = models.BooleanField(default=False, verbose_name='Discovered')
    description = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['device__id', 'parent__id', 'name']
        unique_together = ['device', 'parent', 'name']

    def __str__(self):
        return self.name
