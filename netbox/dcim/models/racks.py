import decimal
from functools import cached_property

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Count
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from dcim.choices import *
from dcim.constants import *
from dcim.svg import RackElevationSVG
from netbox.choices import ColorChoices
from netbox.models import OrganizationalModel, PrimaryModel
from netbox.models.features import ContactsMixin, ImageAttachmentsMixin
from utilities.conversion import to_grams
from utilities.data import array_to_string, drange
from utilities.fields import ColorField, NaturalOrderingField
from .device_components import PowerPort
from .devices import Device, Module
from .mixins import WeightMixin
from .power import PowerFeed

__all__ = (
    'Rack',
    'RackReservation',
    'RackRole',
    'RackType',
)


#
# Rack Types
#

class RackBase(WeightMixin, PrimaryModel):
    """
    Base class for RackType & Rack. Holds
    """
    form_factor = models.CharField(
        choices=RackFormFactorChoices,
        max_length=50,
        blank=True,
        verbose_name=_('form factor')
    )
    width = models.PositiveSmallIntegerField(
        choices=RackWidthChoices,
        default=RackWidthChoices.WIDTH_19IN,
        verbose_name=_('width'),
        help_text=_('Rail-to-rail width')
    )

    # Numbering
    u_height = models.PositiveSmallIntegerField(
        default=RACK_U_HEIGHT_DEFAULT,
        verbose_name=_('height (U)'),
        validators=[MinValueValidator(1), MaxValueValidator(RACK_U_HEIGHT_MAX)],
        help_text=_('Height in rack units')
    )
    starting_unit = models.PositiveSmallIntegerField(
        default=RACK_STARTING_UNIT_DEFAULT,
        verbose_name=_('starting unit'),
        validators=[MinValueValidator(1)],
        help_text=_('Starting unit for rack')
    )
    desc_units = models.BooleanField(
        default=False,
        verbose_name=_('descending units'),
        help_text=_('Units are numbered top-to-bottom')
    )

    # Dimensions
    outer_width = models.PositiveSmallIntegerField(
        verbose_name=_('outer width'),
        blank=True,
        null=True,
        help_text=_('Outer dimension of rack (width)')
    )
    outer_depth = models.PositiveSmallIntegerField(
        verbose_name=_('outer depth'),
        blank=True,
        null=True,
        help_text=_('Outer dimension of rack (depth)')
    )
    outer_unit = models.CharField(
        verbose_name=_('outer unit'),
        max_length=50,
        choices=RackDimensionUnitChoices,
        blank=True
    )
    mounting_depth = models.PositiveSmallIntegerField(
        verbose_name=_('mounting depth'),
        blank=True,
        null=True,
        help_text=(_(
            'Maximum depth of a mounted device, in millimeters. For four-post racks, this is the distance between the '
            'front and rear rails.'
        ))
    )

    # Weight
    # WeightMixin provides weight, weight_unit, and _abs_weight
    max_weight = models.PositiveIntegerField(
        verbose_name=_('max weight'),
        blank=True,
        null=True,
        help_text=_('Maximum load capacity for the rack')
    )
    # Stores the normalized max weight (in grams) for database ordering
    _abs_max_weight = models.PositiveBigIntegerField(
        blank=True,
        null=True
    )

    class Meta:
        abstract = True


class RackType(RackBase):
    """
    Devices are housed within Racks. Each rack has a defined height measured in rack units, and a front and rear face.
    Each Rack is assigned to a Site and (optionally) a Location.
    """
    manufacturer = models.ForeignKey(
        to='dcim.Manufacturer',
        on_delete=models.PROTECT,
        related_name='rack_types'
    )
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100
    )
    _name = NaturalOrderingField(
        target_field='name',
        max_length=100,
        blank=True
    )
    slug = models.SlugField(
        verbose_name=_('slug'),
        max_length=100,
        unique=True
    )

    clone_fields = (
        'manufacturer', 'form_factor', 'width', 'u_height', 'desc_units', 'outer_width', 'outer_depth', 'outer_unit',
        'mounting_depth', 'weight', 'max_weight', 'weight_unit',
    )
    prerequisite_models = (
        'dcim.Manufacturer',
    )

    class Meta:
        ordering = ('_name', 'pk')  # (site, location, name) may be non-unique
        verbose_name = _('rack type')
        verbose_name_plural = _('rack types')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dcim:racktype', args=[self.pk])

    def clean(self):
        super().clean()

        # Validate outer dimensions and unit
        if (self.outer_width is not None or self.outer_depth is not None) and not self.outer_unit:
            raise ValidationError(_("Must specify a unit when setting an outer width/depth"))

        # Validate max_weight and weight_unit
        if self.max_weight and not self.weight_unit:
            raise ValidationError(_("Must specify a unit when setting a maximum weight"))

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

        # Update all Racks associated with this RackType
        for rack in self.racks.all():
            rack.snapshot()
            rack.copy_racktype_attrs()
            rack.save()

    @property
    def units(self):
        """
        Return a list of unit numbers, top to bottom.
        """
        if self.desc_units:
            return drange(decimal.Decimal(self.starting_unit), self.u_height + self.starting_unit, 0.5)
        return drange(self.u_height + decimal.Decimal(0.5) + self.starting_unit - 1, 0.5 + self.starting_unit - 1, -0.5)


#
# Racks
#

class RackRole(OrganizationalModel):
    """
    Racks can be organized by functional role, similar to Devices.
    """
    color = ColorField(
        verbose_name=_('color'),
        default=ColorChoices.COLOR_GREY
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('rack role')
        verbose_name_plural = _('rack roles')

    def get_absolute_url(self):
        return reverse('dcim:rackrole', args=[self.pk])


class Rack(ContactsMixin, ImageAttachmentsMixin, RackBase):
    """
    Devices are housed within Racks. Each rack has a defined height measured in rack units, and a front and rear face.
    Each Rack is assigned to a Site and (optionally) a Location.
    """
    # Fields which cannot be set locally if a RackType is assigned
    RACKTYPE_FIELDS = [
        'form_factor', 'width', 'u_height', 'starting_unit', 'desc_units', 'outer_width', 'outer_depth', 'outer_unit',
        'mounting_depth', 'weight', 'weight_unit', 'max_weight'
    ]

    rack_type = models.ForeignKey(
        to='dcim.RackType',
        on_delete=models.PROTECT,
        related_name='racks',
        blank=True,
        null=True,
    )
    name = models.CharField(
        verbose_name=_('name'),
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
        verbose_name=_('facility ID'),
        help_text=_("Locally-assigned identifier")
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
        verbose_name=_('status'),
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
        verbose_name=_('serial number')
    )
    asset_tag = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_('asset tag'),
        help_text=_('A unique tag used to identify this rack')
    )

    # Generic relations
    vlan_groups = GenericRelation(
        to='ipam.VLANGroup',
        content_type_field='scope_type',
        object_id_field='scope_id',
        related_query_name='rack'
    )

    clone_fields = (
        'site', 'location', 'tenant', 'status', 'role', 'form_factor', 'width', 'u_height', 'desc_units', 'outer_width',
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
        verbose_name = _('rack')
        verbose_name_plural = _('racks')

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
            raise ValidationError(_("Assigned location must belong to parent site ({site}).").format(site=self.site))

        # Validate outer dimensions and unit
        if (self.outer_width is not None or self.outer_depth is not None) and not self.outer_unit:
            raise ValidationError(_("Must specify a unit when setting an outer width/depth"))

        # Validate max_weight and weight_unit
        if self.max_weight and not self.weight_unit:
            raise ValidationError(_("Must specify a unit when setting a maximum weight"))

        if self.pk:
            mounted_devices = Device.objects.filter(rack=self).exclude(position__isnull=True).order_by('position')

            # Validate that Rack is tall enough to house the highest mounted Device
            if top_device := mounted_devices.last():
                min_height = top_device.position + top_device.device_type.u_height - self.starting_unit
                if self.u_height < min_height:
                    raise ValidationError({
                        'u_height': _("Rack must be at least {min_height}U tall to house currently installed devices.").format(min_height=min_height)
                    })

            # Validate that the Rack's starting unit is less than or equal to the position of the lowest mounted Device
            if last_device := mounted_devices.first():
                if self.starting_unit > last_device.position:
                    raise ValidationError({
                        'starting_unit': _("Rack unit numbering must begin at {position} or less to house "
                                           "currently installed devices.").format(position=last_device.position)
                    })

            # Validate that Rack was assigned a Location of its same site, if applicable
            if self.location:
                if self.location.site != self.site:
                    raise ValidationError({
                        'location': _("Location must be from the same site, {site}.").format(site=self.site)
                    })

    def save(self, *args, **kwargs):
        self.copy_racktype_attrs()

        # Store the given max weight (if any) in grams for use in database ordering
        if self.max_weight and self.weight_unit:
            self._abs_max_weight = to_grams(self.max_weight, self.weight_unit)
        else:
            self._abs_max_weight = None

        # Clear unit if outer width & depth are not set
        if self.outer_width is None and self.outer_depth is None:
            self.outer_unit = ''

        super().save(*args, **kwargs)

    def copy_racktype_attrs(self):
        """
        Copy physical attributes from the assigned RackType (if any).
        """
        if self.rack_type:
            for field_name in self.RACKTYPE_FIELDS:
                setattr(self, field_name, getattr(self.rack_type, field_name))

    @property
    def units(self):
        """
        Return a list of unit numbers, top to bottom.
        """
        if self.desc_units:
            return drange(decimal.Decimal(self.starting_unit), self.u_height + self.starting_unit, 0.5)
        return drange(self.u_height + decimal.Decimal(0.5) + self.starting_unit - 1, 0.5 + self.starting_unit - 1, -0.5)

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
                'role'
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

    def get_available_units(self, u_height=1, rack_face=None, exclude=None, ignore_excluded_devices=False):
        """
        Return a list of units within the rack available to accommodate a device of a given U height (default 1).
        Optionally exclude one or more devices when calculating empty units (needed when moving a device from one
        position to another within a rack).

        :param u_height: Minimum number of contiguous free units required
        :param rack_face: The face of the rack (front or rear) required; 'None' if device is full depth
        :param exclude: List of devices IDs to exclude (useful when moving a device within a rack)
        :param ignore_excluded_devices: Ignore devices that are marked to exclude from utilization calculations
        """
        # Gather all devices which consume U space within the rack
        devices = self.devices.prefetch_related('device_type').filter(position__gte=1)
        if ignore_excluded_devices:
            devices = devices.exclude(device_type__exclude_from_utilization=True)

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
        available_units = self.get_available_units(u_height=0.5, ignore_excluded_devices=True)

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

        return round(allocated_draw / available_power_total * 100, 1)

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
        verbose_name=_('units'),
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
        to=settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200
    )

    clone_fields = ('rack', 'user', 'tenant')
    prerequisite_models = (
        'dcim.Rack',
    )

    class Meta:
        ordering = ['created', 'pk']
        verbose_name = _('rack reservation')
        verbose_name_plural = _('rack reservations')

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
                    'units': _("Invalid unit(s) for {height}U rack: {unit_list}").format(
                        height=self.rack.u_height,
                        unit_list=', '.join([str(u) for u in invalid_units])
                    ),
                })

            # Check that none of the units has already been reserved for this Rack.
            reserved_units = []
            for resv in self.rack.reservations.exclude(pk=self.pk):
                reserved_units += resv.units
            conflicting_units = [u for u in self.units if u in reserved_units]
            if conflicting_units:
                raise ValidationError({
                    'units': _('The following units have already been reserved: {unit_list}').format(
                        unit_list=', '.join([str(u) for u in conflicting_units])
                    )
                })

    @property
    def unit_list(self):
        return array_to_string(self.units)
