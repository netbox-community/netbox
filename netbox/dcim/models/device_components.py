from cacheops import cached_as
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from taggit.managers import TaggableManager

from dcim.choices import *
from dcim.constants import *
from dcim.exceptions import LoopDetected
from dcim.fields import MACAddressField
from extras.models import ObjectChange, TaggedItem
from utilities.fields import NaturalOrderingField
from utilities.ordering import naturalize_interface
from utilities.utils import serialize_object
from virtualization.choices import VMInterfaceTypeChoices


__all__ = (
    'CableTermination',
    'ConsolePort',
    'ConsoleServerPort',
    'DeviceBay',
    'FrontPort',
    'Interface',
    'InventoryItem',
    'PowerOutlet',
    'PowerPort',
    'RearPort',
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

    is_path_endpoint = True

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
    _name = NaturalOrderingField(
        target_field='name',
        max_length=100,
        blank=True
    )
    type = models.CharField(
        max_length=50,
        choices=ConsolePortTypeChoices,
        blank=True
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
    tags = TaggableManager(through=TaggedItem)

    csv_headers = ['device', 'name', 'type', 'description']

    class Meta:
        ordering = ('device', '_name')
        unique_together = ('device', 'name')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return self.device.get_absolute_url()

    def to_csv(self):
        return (
            self.device.identifier,
            self.name,
            self.type,
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
    _name = NaturalOrderingField(
        target_field='name',
        max_length=100,
        blank=True
    )
    type = models.CharField(
        max_length=50,
        choices=ConsolePortTypeChoices,
        blank=True
    )
    connection_status = models.NullBooleanField(
        choices=CONNECTION_STATUS_CHOICES,
        blank=True
    )
    tags = TaggableManager(through=TaggedItem)

    csv_headers = ['device', 'name', 'type', 'description']

    class Meta:
        ordering = ('device', '_name')
        unique_together = ('device', 'name')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return self.device.get_absolute_url()

    def to_csv(self):
        return (
            self.device.identifier,
            self.name,
            self.type,
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
    _name = NaturalOrderingField(
        target_field='name',
        max_length=100,
        blank=True
    )
    type = models.CharField(
        max_length=50,
        choices=PowerPortTypeChoices,
        blank=True
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
    tags = TaggableManager(through=TaggedItem)

    csv_headers = ['device', 'name', 'type', 'maximum_draw', 'allocated_draw', 'description']

    class Meta:
        ordering = ('device', '_name')
        unique_together = ('device', 'name')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return self.device.get_absolute_url()

    def to_csv(self):
        return (
            self.device.identifier,
            self.name,
            self.get_type_display(),
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
        # TODO: Fix circular import
        from . import PowerFeed

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

    def get_power_draw(self, leg_stats=True):
        """
        Return the allocated and maximum power draw (in VA) and child PowerOutlet count for this PowerPort.
        If `leg_stats` is True, the `legs` key in the returned dict is populated with a list of per-leg statistics.
        """
        def get_power_stats(leg=None):
            """
            Return tuple of (outlet_count, allocated_draw_total, maximum_draw_total).
            """
            # Local outlets associated with this power port
            if leg:
                outlets = PowerOutlet.objects.filter(power_port=self, feed_leg=leg)
            else:
                outlets = PowerOutlet.objects.filter(power_port=self)

            # The outlets are used as extra to invalidate the cache when an outlet's leg is changed
            @cached_as(self, extra=outlets)
            def _stats():
                # Power ports drawing power from the local outlets
                return PowerPort.objects.filter(
                    pk__in=outlets.values_list('downstream_powerports', flat=True),
                ).aggregate(
                    Sum('allocated_draw'),
                    Sum('maximum_draw'),
                )

            stats = _stats()

            return outlets.count(), stats.get('allocated_draw__sum') or 0, stats.get('maximum_draw__sum') or 0

        # Calculate aggregate draw of all child power outlets if no numbers have been defined manually
        if self.allocated_draw is None and self.maximum_draw is None:
            # Global results
            outlet_count, allocated_draw_total, maximum_draw_total = get_power_stats()
            ret = {
                'allocated': allocated_draw_total,
                'maximum': maximum_draw_total,
                'outlet_count': outlet_count,
                'legs': [],
            }

            # Calculate per-leg aggregates for three-phase feeds
            if leg_stats and getattr(self._connected_powerfeed, 'phase', None) == PowerFeedPhaseChoices.PHASE_3PHASE:
                for leg, leg_name in PowerOutletFeedLegChoices:
                    outlet_count, allocated_draw_total, maximum_draw_total = get_power_stats(leg)
                    ret['legs'].append({
                        'name': leg_name,
                        'allocated': allocated_draw_total,
                        'maximum': maximum_draw_total,
                        'outlet_count': outlet_count,
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
    _name = NaturalOrderingField(
        target_field='name',
        max_length=100,
        blank=True
    )
    type = models.CharField(
        max_length=50,
        choices=PowerOutletTypeChoices,
        blank=True
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
    connection_status = models.NullBooleanField(
        choices=CONNECTION_STATUS_CHOICES,
        blank=True
    )
    downstream_powerports = models.ManyToManyField(
        to='dcim.PowerPort',
        related_name='upstream_poweroutlets',
        blank=True
    )
    tags = TaggableManager(through=TaggedItem)

    csv_headers = ['device', 'name', 'type', 'power_port', 'feed_leg', 'description']

    class Meta:
        ordering = ('device', '_name')
        unique_together = ('device', 'name')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return self.device.get_absolute_url()

    def to_csv(self):
        return (
            self.device.identifier,
            self.name,
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

    def save(self, *args, **kwargs):
        # Remove possibly-stale references to the old downstream power ports in upsteam power ports
        if self.pk:
            for poweroutlet in self.calculate_upstream_poweroutlets():
                poweroutlet.downstream_powerports.remove(*self.downstream_powerports.all())
            # TODO: breaking a loop will erroneously clear the downstream power ports on downstream power outlets

        # Make any toplogy changes
        super().save(*args, **kwargs)

        # Calculate the new downstream ports
        downstream_powerports = self.calculate_downstream_powerports()

        # Set to local downstream_powerports field, removing any existing values
        self.downstream_powerports.set(downstream_powerports)

        # Add to upstream power outlets' downstream_powerports field, keeping any existing values
        for poweroutlet in self.calculate_upstream_poweroutlets():
            poweroutlet.downstream_powerports.add(*downstream_powerports)

    def calculate_downstream_powerports(self):
        """
        Return a queryset of the power ports drawing power from this outlet.
        """
        downstream_powerports = PowerPort.objects.none()

        if hasattr(self, 'connected_endpoint'):
            next_powerports = PowerPort.objects.filter(pk=self.connected_endpoint.pk)

            while next_powerports.exists():
                downstream_powerports |= next_powerports

                # Prevent loops by excluding those already matched
                next_powerports = PowerPort.objects.exclude(
                    pk__in=downstream_powerports
                ).filter(
                    _connected_poweroutlet__power_port__in=downstream_powerports
                )

        return downstream_powerports

    def calculate_upstream_poweroutlets(self):
        """
        Return a queryset of the power outlets supplying power to this outlet.
        """
        upstream_poweroutlets = PowerOutlet.objects.none()

        if self.power_port and self.power_port._connected_poweroutlet:
            next_poweroutlets = PowerOutlet.objects.filter(pk=self.power_port._connected_poweroutlet.pk)

            while next_poweroutlets.exists():
                upstream_poweroutlets |= next_poweroutlets

                # Prevent loops by excluding those already matched
                next_poweroutlets = PowerOutlet.objects.exclude(
                    pk__in=upstream_poweroutlets
                ).filter(
                    connected_endpoint__poweroutlets__in=upstream_poweroutlets
                )

        return upstream_poweroutlets


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
    _name = NaturalOrderingField(
        target_field='name',
        naturalize_function=naturalize_interface,
        max_length=100,
        blank=True
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
    type = models.CharField(
        max_length=50,
        choices=InterfaceTypeChoices
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
    mode = models.CharField(
        max_length=50,
        choices=InterfaceModeChoices,
        blank=True,
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
    tags = TaggableManager(through=TaggedItem)

    csv_headers = [
        'device', 'virtual_machine', 'name', 'lag', 'type', 'enabled', 'mac_address', 'mtu', 'mgmt_only',
        'description', 'mode',
    ]

    class Meta:
        # TODO: ordering and unique_together should include virtual_machine
        ordering = ('device', '_name')
        unique_together = ('device', 'name')

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
        if self.virtual_machine and self.type not in VMInterfaceTypeChoices.values():
            raise ValidationError({
                'type': "Invalid interface type for a virtual machine: {}".format(self.type)
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
        if self.type != InterfaceTypeChoices.TYPE_LAG and self.member_interfaces.exists():
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
        if self.pk and self.mode != InterfaceModeChoices.MODE_TAGGED:
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
        return self.type == InterfaceTypeChoices.TYPE_LAG

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
    _name = NaturalOrderingField(
        target_field='name',
        max_length=100,
        blank=True
    )
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
        validators=[MinValueValidator(1), MaxValueValidator(64)]
    )
    tags = TaggableManager(through=TaggedItem)

    csv_headers = ['device', 'name', 'type', 'rear_port', 'rear_port_position', 'description']
    is_path_endpoint = False

    class Meta:
        ordering = ('device', '_name')
        unique_together = (
            ('device', 'name'),
            ('rear_port', 'rear_port_position'),
        )

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
    _name = NaturalOrderingField(
        target_field='name',
        max_length=100,
        blank=True
    )
    type = models.CharField(
        max_length=50,
        choices=PortTypeChoices
    )
    positions = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(64)]
    )
    tags = TaggableManager(through=TaggedItem)

    csv_headers = ['device', 'name', 'type', 'positions', 'description']
    is_path_endpoint = False

    class Meta:
        ordering = ('device', '_name')
        unique_together = ('device', 'name')

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
    _name = NaturalOrderingField(
        target_field='name',
        max_length=100,
        blank=True
    )
    installed_device = models.OneToOneField(
        to='dcim.Device',
        on_delete=models.SET_NULL,
        related_name='parent_bay',
        blank=True,
        null=True
    )
    tags = TaggableManager(through=TaggedItem)

    csv_headers = ['device', 'name', 'installed_device', 'description']

    class Meta:
        ordering = ('device', '_name')
        unique_together = ('device', 'name')

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
    _name = NaturalOrderingField(
        target_field='name',
        max_length=100,
        blank=True
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
        ordering = ('device__id', 'parent__id', '_name')
        unique_together = ('device', 'parent', 'name')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dcim:device_inventory', kwargs={'pk': self.device.pk})

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
