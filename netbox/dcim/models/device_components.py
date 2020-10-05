from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager

from dcim.choices import *
from dcim.constants import *
from dcim.fields import MACAddressField
from dcim.utils import path_node_to_object
from extras.models import ObjectChange, TaggedItem
from extras.utils import extras_features
from utilities.fields import NaturalOrderingField
from utilities.mptt import TreeManager
from utilities.ordering import naturalize_interface
from utilities.querysets import RestrictedQuerySet
from utilities.query_functions import CollateAsChar
from utilities.utils import serialize_object


__all__ = (
    'BaseInterface',
    'CableTermination',
    'ConsolePort',
    'ConsoleServerPort',
    'DeviceBay',
    'FrontPort',
    'Interface',
    'InventoryItem',
    'PathEndpoint',
    'PowerOutlet',
    'PowerPort',
    'RearPort',
)


class ComponentModel(models.Model):
    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.CASCADE,
        related_name='%(class)ss'
    )
    name = models.CharField(
        max_length=64
    )
    _name = NaturalOrderingField(
        target_field='name',
        max_length=100,
        blank=True
    )
    label = models.CharField(
        max_length=64,
        blank=True,
        help_text="Physical label"
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        abstract = True

    def __str__(self):
        if self.label:
            return f"{self.name} ({self.label})"
        return self.name

    def to_objectchange(self, action):
        # Annotate the parent Device
        try:
            device = self.device
        except ObjectDoesNotExist:
            # The parent Device has already been deleted
            device = None
        return ObjectChange(
            changed_object=self,
            object_repr=str(self),
            action=action,
            related_object=device,
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

    def get_cable_peer(self):
        if self.cable is None:
            return None
        if self._cabled_as_a.exists():
            return self.cable.termination_b
        if self._cabled_as_b.exists():
            return self.cable.termination_a


class PathEndpoint(models.Model):
    """
    Any object which may serve as the originating endpoint of a CablePath.
    """
    _path = models.ForeignKey(
        to='dcim.CablePath',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        abstract = True

    def trace(self):
        if self._path is None:
            return []

        # Construct the complete path
        path = [self, *[path_node_to_object(obj) for obj in self._path.path], self._path.destination]
        assert not len(path) % 3,\
            f"Invalid path length for CablePath #{self.pk}: {len(self._path.path)} elements in path"

        # Return the path as a list of three-tuples (A termination, cable, B termination)
        return list(zip(*[iter(path)] * 3))

    @property
    def connected_endpoint(self):
        """
        Caching accessor for the attached CablePath's destination (if any)
        """
        if not hasattr(self, '_connected_endpoint'):
            self._connected_endpoint = self._path.destination if self._path else None
        return self._connected_endpoint


#
# Console ports
#

@extras_features('export_templates', 'webhooks')
class ConsolePort(CableTermination, PathEndpoint, ComponentModel):
    """
    A physical console port within a Device. ConsolePorts connect to ConsoleServerPorts.
    """
    type = models.CharField(
        max_length=50,
        choices=ConsolePortTypeChoices,
        blank=True,
        help_text='Physical port type'
    )
    tags = TaggableManager(through=TaggedItem)

    csv_headers = ['device', 'name', 'label', 'type', 'description']

    class Meta:
        ordering = ('device', '_name')
        unique_together = ('device', 'name')

    def get_absolute_url(self):
        return reverse('dcim:consoleport', kwargs={'pk': self.pk})

    def to_csv(self):
        return (
            self.device.identifier,
            self.name,
            self.label,
            self.type,
            self.description,
        )


#
# Console server ports
#

@extras_features('webhooks')
class ConsoleServerPort(CableTermination, PathEndpoint, ComponentModel):
    """
    A physical port within a Device (typically a designated console server) which provides access to ConsolePorts.
    """
    type = models.CharField(
        max_length=50,
        choices=ConsolePortTypeChoices,
        blank=True,
        help_text='Physical port type'
    )
    tags = TaggableManager(through=TaggedItem)

    csv_headers = ['device', 'name', 'label', 'type', 'description']

    class Meta:
        ordering = ('device', '_name')
        unique_together = ('device', 'name')

    def get_absolute_url(self):
        return reverse('dcim:consoleserverport', kwargs={'pk': self.pk})

    def to_csv(self):
        return (
            self.device.identifier,
            self.name,
            self.label,
            self.type,
            self.description,
        )


#
# Power ports
#

@extras_features('export_templates', 'webhooks')
class PowerPort(CableTermination, PathEndpoint, ComponentModel):
    """
    A physical power supply (intake) port within a Device. PowerPorts connect to PowerOutlets.
    """
    type = models.CharField(
        max_length=50,
        choices=PowerPortTypeChoices,
        blank=True,
        help_text='Physical port type'
    )
    maximum_draw = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Maximum power draw (watts)"
    )
    allocated_draw = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Allocated power draw (watts)"
    )
    tags = TaggableManager(through=TaggedItem)

    csv_headers = ['device', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'description']

    class Meta:
        ordering = ('device', '_name')
        unique_together = ('device', 'name')

    def get_absolute_url(self):
        return reverse('dcim:powerport', kwargs={'pk': self.pk})

    def to_csv(self):
        return (
            self.device.identifier,
            self.name,
            self.label,
            self.get_type_display(),
            self.maximum_draw,
            self.allocated_draw,
            self.description,
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
            if self._connected_powerfeed and self._connected_powerfeed.phase == PowerFeedPhaseChoices.PHASE_3PHASE:
                for leg, leg_name in PowerOutletFeedLegChoices:
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

@extras_features('webhooks')
class PowerOutlet(CableTermination, PathEndpoint, ComponentModel):
    """
    A physical power outlet (output) within a Device which provides power to a PowerPort.
    """
    type = models.CharField(
        max_length=50,
        choices=PowerOutletTypeChoices,
        blank=True,
        help_text='Physical port type'
    )
    power_port = models.ForeignKey(
        to='dcim.PowerPort',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='poweroutlets'
    )
    feed_leg = models.CharField(
        max_length=50,
        choices=PowerOutletFeedLegChoices,
        blank=True,
        help_text="Phase (for three-phase feeds)"
    )
    tags = TaggableManager(through=TaggedItem)

    csv_headers = ['device', 'name', 'label', 'type', 'power_port', 'feed_leg', 'description']

    class Meta:
        ordering = ('device', '_name')
        unique_together = ('device', 'name')

    def get_absolute_url(self):
        return reverse('dcim:poweroutlet', kwargs={'pk': self.pk})

    def to_csv(self):
        return (
            self.device.identifier,
            self.name,
            self.label,
            self.get_type_display(),
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

class BaseInterface(models.Model):
    """
    Abstract base class for fields shared by dcim.Interface and virtualization.VMInterface.
    """
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
    mode = models.CharField(
        max_length=50,
        choices=InterfaceModeChoices,
        blank=True
    )

    class Meta:
        abstract = True


@extras_features('export_templates', 'webhooks')
class Interface(CableTermination, PathEndpoint, ComponentModel, BaseInterface):
    """
    A network interface within a Device. A physical Interface can connect to exactly one other Interface.
    """
    # Override ComponentModel._name to specify naturalize_interface function
    _name = NaturalOrderingField(
        target_field='name',
        naturalize_function=naturalize_interface,
        max_length=100,
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
    type = models.CharField(
        max_length=50,
        choices=InterfaceTypeChoices
    )
    mgmt_only = models.BooleanField(
        default=False,
        verbose_name='OOB Management',
        help_text='This interface is used only for out-of-band management'
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
    ip_addresses = GenericRelation(
        to='ipam.IPAddress',
        content_type_field='assigned_object_type',
        object_id_field='assigned_object_id',
        related_query_name='interface'
    )
    tags = TaggableManager(through=TaggedItem)

    csv_headers = [
        'device', 'name', 'label', 'lag', 'type', 'enabled', 'mac_address', 'mtu', 'mgmt_only', 'description', 'mode',
    ]

    class Meta:
        ordering = ('device', CollateAsChar('_name'))
        unique_together = ('device', 'name')

    def get_absolute_url(self):
        return reverse('dcim:interface', kwargs={'pk': self.pk})

    def to_csv(self):
        return (
            self.device.identifier if self.device else None,
            self.name,
            self.label,
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

        # Virtual interfaces cannot be connected
        if self.type in NONCONNECTABLE_IFACE_TYPES and (
                self.cable or getattr(self, 'circuit_termination', False)
        ):
            raise ValidationError({
                'type': "Virtual and wireless interfaces cannot be connected to another interface or circuit. "
                        "Disconnect the interface or choose a suitable type."
            })

        # An interface's LAG must belong to the same device or virtual chassis
        if self.lag and self.lag.device != self.device:
            if self.device.virtual_chassis is None:
                raise ValidationError({
                    'lag': f"The selected LAG interface ({self.lag}) belongs to a different device ({self.lag.device})."
                })
            elif self.lag.device.virtual_chassis != self.device.virtual_chassis:
                raise ValidationError({
                    'lag': f"The selected LAG interface ({self.lag}) belongs to {self.lag.device}, which is not part "
                           f"of virtual chassis {self.device.virtual_chassis}."
                })

        # A virtual interface cannot have a parent LAG
        if self.type == InterfaceTypeChoices.TYPE_VIRTUAL and self.lag is not None:
            raise ValidationError({'lag': "Virtual interfaces cannot have a parent LAG interface."})

        # A LAG interface cannot be its own parent
        if self.pk and self.lag_id == self.pk:
            raise ValidationError({'lag': "A LAG interface cannot be its own parent."})

        # Validate untagged VLAN
        if self.untagged_vlan and self.untagged_vlan.site not in [self.parent.site, None]:
            raise ValidationError({
                'untagged_vlan': "The untagged VLAN ({}) must belong to the same site as the interface's parent "
                                 "device, or it must be global".format(self.untagged_vlan)
            })

    def save(self, *args, **kwargs):

        # Remove untagged VLAN assignment for non-802.1Q interfaces
        if self.mode is None:
            self.untagged_vlan = None

        # Only "tagged" interfaces may have tagged VLANs assigned. ("tagged all" implies all VLANs are assigned.)
        if self.pk and self.mode != InterfaceModeChoices.MODE_TAGGED:
            self.tagged_vlans.clear()

        return super().save(*args, **kwargs)

    @property
    def parent(self):
        return self.device

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
        return self.type == InterfaceTypeChoices.TYPE_LAG

    @property
    def count_ipaddresses(self):
        return self.ip_addresses.count()


#
# Pass-through ports
#

@extras_features('webhooks')
class FrontPort(CableTermination, ComponentModel):
    """
    A pass-through port on the front of a Device.
    """
    type = models.CharField(
        max_length=50,
        choices=PortTypeChoices
    )
    rear_port = models.ForeignKey(
        to='dcim.RearPort',
        on_delete=models.CASCADE,
        related_name='frontports'
    )
    rear_port_position = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(REARPORT_POSITIONS_MIN),
            MaxValueValidator(REARPORT_POSITIONS_MAX)
        ]
    )
    tags = TaggableManager(through=TaggedItem)

    csv_headers = ['device', 'name', 'label', 'type', 'rear_port', 'rear_port_position', 'description']

    class Meta:
        ordering = ('device', '_name')
        unique_together = (
            ('device', 'name'),
            ('rear_port', 'rear_port_position'),
        )

    def get_absolute_url(self):
        return reverse('dcim:frontport', kwargs={'pk': self.pk})

    def to_csv(self):
        return (
            self.device.identifier,
            self.name,
            self.label,
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


@extras_features('webhooks')
class RearPort(CableTermination, ComponentModel):
    """
    A pass-through port on the rear of a Device.
    """
    type = models.CharField(
        max_length=50,
        choices=PortTypeChoices
    )
    positions = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(REARPORT_POSITIONS_MIN),
            MaxValueValidator(REARPORT_POSITIONS_MAX)
        ]
    )
    tags = TaggableManager(through=TaggedItem)

    csv_headers = ['device', 'name', 'label', 'type', 'positions', 'description']

    class Meta:
        ordering = ('device', '_name')
        unique_together = ('device', 'name')

    def get_absolute_url(self):
        return reverse('dcim:rearport', kwargs={'pk': self.pk})

    def to_csv(self):
        return (
            self.device.identifier,
            self.name,
            self.label,
            self.get_type_display(),
            self.positions,
            self.description,
        )


#
# Device bays
#

@extras_features('webhooks')
class DeviceBay(ComponentModel):
    """
    An empty space within a Device which can house a child device
    """
    installed_device = models.OneToOneField(
        to='dcim.Device',
        on_delete=models.SET_NULL,
        related_name='parent_bay',
        blank=True,
        null=True
    )
    tags = TaggableManager(through=TaggedItem)

    csv_headers = ['device', 'name', 'label', 'installed_device', 'description']

    class Meta:
        ordering = ('device', '_name')
        unique_together = ('device', 'name')

    def get_absolute_url(self):
        return reverse('dcim:devicebay', kwargs={'pk': self.pk})

    def to_csv(self):
        return (
            self.device.identifier,
            self.name,
            self.label,
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

        # Check that the installed device is not already installed elsewhere
        if self.installed_device:
            current_bay = DeviceBay.objects.filter(installed_device=self.installed_device).first()
            if current_bay and current_bay != self:
                raise ValidationError({
                    'installed_device': "Cannot install the specified device; device is already installed in {}".format(
                        current_bay
                    )
                })


#
# Inventory items
#

@extras_features('export_templates', 'webhooks')
class InventoryItem(MPTTModel, ComponentModel):
    """
    An InventoryItem represents a serialized piece of hardware within a Device, such as a line card or power supply.
    InventoryItems are used only for inventory purposes.
    """
    parent = TreeForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='child_items',
        blank=True,
        null=True,
        db_index=True
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
        blank=True,
        help_text='Manufacturer-assigned part identifier'
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
        help_text='This item was automatically discovered'
    )

    tags = TaggableManager(through=TaggedItem)

    objects = TreeManager()

    csv_headers = [
        'device', 'name', 'label', 'manufacturer', 'part_id', 'serial', 'asset_tag', 'discovered', 'description',
    ]

    class Meta:
        ordering = ('device__id', 'parent__id', '_name')
        unique_together = ('device', 'parent', 'name')

    def get_absolute_url(self):
        return reverse('dcim:inventoryitem', kwargs={'pk': self.pk})

    def to_csv(self):
        return (
            self.device.name or '{{{}}}'.format(self.device.pk),
            self.name,
            self.label,
            self.manufacturer.name if self.manufacturer else None,
            self.part_id,
            self.serial,
            self.asset_tag,
            self.discovered,
            self.description,
        )
