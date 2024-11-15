from functools import cached_property

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from dcim.choices import *
from dcim.constants import *
from dcim.fields import MACAddressField, WWNField
from netbox.choices import ColorChoices
from netbox.models import OrganizationalModel, NetBoxModel
from utilities.fields import ColorField, NaturalOrderingField
from utilities.mptt import TreeManager
from utilities.ordering import naturalize_interface
from utilities.query_functions import CollateAsChar
from utilities.tracking import TrackingModelMixin
from wireless.choices import *
from wireless.utils import get_channel_attr

__all__ = (
    'BaseInterface',
    'CabledObjectModel',
    'ConsolePort',
    'ConsoleServerPort',
    'DeviceBay',
    'FrontPort',
    'Interface',
    'InventoryItem',
    'InventoryItemRole',
    'ModuleBay',
    'PathEndpoint',
    'PowerOutlet',
    'PowerPort',
    'RearPort',
)


class ComponentModel(NetBoxModel):
    """
    An abstract model inherited by any model which has a parent Device.
    """
    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.CASCADE,
        related_name='%(class)ss'
    )
    name = models.CharField(
        verbose_name=_('name'),
        max_length=64,
        db_collation="natural_sort"
    )
    label = models.CharField(
        verbose_name=_('label'),
        max_length=64,
        blank=True,
        help_text=_('Physical label')
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )

    class Meta:
        abstract = True
        ordering = ('device', 'name')
        constraints = (
            models.UniqueConstraint(
                fields=('device', 'name'),
                name='%(app_label)s_%(class)s_unique_device_name'
            ),
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Cache the original Device ID for reference under clean()
        self._original_device = self.__dict__.get('device_id')

    def __str__(self):
        if self.label:
            return f"{self.name} ({self.label})"
        return self.name

    def to_objectchange(self, action):
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.device
        return objectchange

    def clean(self):
        super().clean()

        # Check list of Modules that allow device field to be changed
        if (type(self) not in [InventoryItem]) and (self.pk is not None) and (self._original_device != self.device_id):
            raise ValidationError({
                "device": _("Components cannot be moved to a different device.")
            })

    @property
    def parent_object(self):
        return self.device


class ModularComponentModel(ComponentModel):
    module = models.ForeignKey(
        to='dcim.Module',
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        blank=True,
        null=True
    )
    inventory_items = GenericRelation(
        to='dcim.InventoryItem',
        content_type_field='component_type',
        object_id_field='component_id'
    )

    class Meta(ComponentModel.Meta):
        abstract = True


class CabledObjectModel(models.Model):
    """
    An abstract model inherited by all models to which a Cable can terminate. Provides the `cable` and `cable_end`
    fields for caching cable associations, as well as `mark_connected` to designate "fake" connections.
    """
    cable = models.ForeignKey(
        to='dcim.Cable',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True
    )
    cable_end = models.CharField(
        verbose_name=_('cable end'),
        max_length=1,
        choices=CableEndChoices,
        blank=True,
        null=True
    )
    mark_connected = models.BooleanField(
        verbose_name=_('mark connected'),
        default=False,
        help_text=_('Treat as if a cable is connected')
    )

    cable_terminations = GenericRelation(
        to='dcim.CableTermination',
        content_type_field='termination_type',
        object_id_field='termination_id',
        related_query_name='%(class)s',
    )

    class Meta:
        abstract = True

    def clean(self):
        super().clean()

        if self.cable and not self.cable_end:
            raise ValidationError({
                "cable_end": _("Must specify cable end (A or B) when attaching a cable.")
            })
        if self.cable_end and not self.cable:
            raise ValidationError({
                "cable_end": _("Cable end must not be set without a cable.")
            })
        if self.mark_connected and self.cable:
            raise ValidationError({
                "mark_connected": _("Cannot mark as connected with a cable attached.")
            })

    @property
    def link(self):
        """
        Generic wrapper for a Cable, WirelessLink, or some other relation to a connected termination.
        """
        return self.cable

    @cached_property
    def link_peers(self):
        if self.cable:
            peers = self.cable.terminations.exclude(cable_end=self.cable_end).prefetch_related('termination')
            return [peer.termination for peer in peers]
        return []

    @property
    def _occupied(self):
        return bool(self.mark_connected or self.cable_id)

    @property
    def parent_object(self):
        raise NotImplementedError(
            _("{class_name} models must declare a parent_object property").format(class_name=self.__class__.__name__)
        )

    @property
    def opposite_cable_end(self):
        if not self.cable_end:
            return None
        return CableEndChoices.SIDE_A if self.cable_end == CableEndChoices.SIDE_B else CableEndChoices.SIDE_B


class PathEndpoint(models.Model):
    """
    An abstract model inherited by any CabledObjectModel subclass which represents the end of a CablePath; specifically,
    these include ConsolePort, ConsoleServerPort, PowerPort, PowerOutlet, Interface, and PowerFeed.

    `_path` references the CablePath originating from this instance, if any. It is set or cleared by the receivers in
    dcim.signals in response to changes in the cable path, and complements the `origin` GenericForeignKey field on the
    CablePath model. `_path` should not be accessed directly; rather, use the `path` property.

    `connected_endpoints()` is a convenience method for returning the destination of the associated CablePath, if any.
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
        origin = self
        path = []

        # Construct the complete path (including e.g. bridged interfaces)
        while origin is not None:

            if origin._path is None:
                break

            path.extend(origin._path.path_objects)

            # If the path ends at a non-connected pass-through port, pad out the link and far-end terminations
            if len(path) % 3 == 1:
                path.extend(([], []))
            # If the path ends at a site or provider network, inject a null "link" to render an attachment
            elif len(path) % 3 == 2:
                path.insert(-1, [])

            # Check for a bridged relationship to continue the trace
            destinations = origin._path.destinations
            if len(destinations) == 1:
                origin = getattr(destinations[0], 'bridge', None)
            else:
                origin = None

        # Return the path as a list of three-tuples (A termination(s), cable(s), B termination(s))
        return list(zip(*[iter(path)] * 3))

    @property
    def path(self):
        return self._path

    @cached_property
    def connected_endpoints(self):
        """
        Caching accessor for the attached CablePath's destination (if any)
        """
        return self._path.destinations if self._path else []


#
# Console components
#

class ConsolePort(ModularComponentModel, CabledObjectModel, PathEndpoint, TrackingModelMixin):
    """
    A physical console port within a Device. ConsolePorts connect to ConsoleServerPorts.
    """
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50,
        choices=ConsolePortTypeChoices,
        blank=True,
        null=True,
        help_text=_('Physical port type')
    )
    speed = models.PositiveIntegerField(
        verbose_name=_('speed'),
        choices=ConsolePortSpeedChoices,
        blank=True,
        null=True,
        help_text=_('Port speed in bits per second')
    )

    clone_fields = ('device', 'module', 'type', 'speed')

    class Meta(ModularComponentModel.Meta):
        verbose_name = _('console port')
        verbose_name_plural = _('console ports')


class ConsoleServerPort(ModularComponentModel, CabledObjectModel, PathEndpoint, TrackingModelMixin):
    """
    A physical port within a Device (typically a designated console server) which provides access to ConsolePorts.
    """
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50,
        choices=ConsolePortTypeChoices,
        blank=True,
        null=True,
        help_text=_('Physical port type')
    )
    speed = models.PositiveIntegerField(
        verbose_name=_('speed'),
        choices=ConsolePortSpeedChoices,
        blank=True,
        null=True,
        help_text=_('Port speed in bits per second')
    )

    clone_fields = ('device', 'module', 'type', 'speed')

    class Meta(ModularComponentModel.Meta):
        verbose_name = _('console server port')
        verbose_name_plural = _('console server ports')


#
# Power components
#

class PowerPort(ModularComponentModel, CabledObjectModel, PathEndpoint, TrackingModelMixin):
    """
    A physical power supply (intake) port within a Device. PowerPorts connect to PowerOutlets.
    """
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50,
        choices=PowerPortTypeChoices,
        blank=True,
        null=True,
        help_text=_('Physical port type')
    )
    maximum_draw = models.PositiveIntegerField(
        verbose_name=_('maximum draw'),
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text=_("Maximum power draw (watts)")
    )
    allocated_draw = models.PositiveIntegerField(
        verbose_name=_('allocated draw'),
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text=_('Allocated power draw (watts)')
    )

    clone_fields = ('device', 'module', 'maximum_draw', 'allocated_draw')

    class Meta(ModularComponentModel.Meta):
        verbose_name = _('power port')
        verbose_name_plural = _('power ports')

    def clean(self):
        super().clean()

        if self.maximum_draw is not None and self.allocated_draw is not None:
            if self.allocated_draw > self.maximum_draw:
                raise ValidationError({
                    'allocated_draw': _(
                        "Allocated draw cannot exceed the maximum draw ({maximum_draw}W)."
                    ).format(maximum_draw=self.maximum_draw)
                })

    def get_downstream_powerports(self, leg=None):
        """
        Return a queryset of all PowerPorts connected via cable to a child PowerOutlet. For example, in the topology
        below, PP1.get_downstream_powerports() would return PP2-4.

               ---- PO1 <---> PP2
             /
        PP1 ------- PO2 <---> PP3
             \
               ---- PO3 <---> PP4

        """
        poweroutlets = self.poweroutlets.filter(cable__isnull=False)
        if leg:
            poweroutlets = poweroutlets.filter(feed_leg=leg)
        if not poweroutlets:
            return PowerPort.objects.none()

        q = Q()
        for poweroutlet in poweroutlets:
            q |= Q(
                cable=poweroutlet.cable,
                cable_end=poweroutlet.opposite_cable_end
            )

        return PowerPort.objects.filter(q)

    def get_power_draw(self):
        """
        Return the allocated and maximum power draw (in VA) and child PowerOutlet count for this PowerPort.
        """
        from dcim.models import PowerFeed

        # Calculate aggregate draw of all child power outlets if no numbers have been defined manually
        if self.allocated_draw is None and self.maximum_draw is None:
            utilization = self.get_downstream_powerports().aggregate(
                maximum_draw_total=Sum('maximum_draw'),
                allocated_draw_total=Sum('allocated_draw'),
            )
            ret = {
                'allocated': utilization['allocated_draw_total'] or 0,
                'maximum': utilization['maximum_draw_total'] or 0,
                'outlet_count': self.poweroutlets.count(),
                'legs': [],
            }

            # Calculate per-leg aggregates for three-phase power feeds
            if len(self.link_peers) == 1 and isinstance(self.link_peers[0], PowerFeed) and \
                    self.link_peers[0].phase == PowerFeedPhaseChoices.PHASE_3PHASE:
                for leg, leg_name in PowerOutletFeedLegChoices:
                    utilization = self.get_downstream_powerports(leg=leg).aggregate(
                        maximum_draw_total=Sum('maximum_draw'),
                        allocated_draw_total=Sum('allocated_draw'),
                    )
                    ret['legs'].append({
                        'name': leg_name,
                        'allocated': utilization['allocated_draw_total'] or 0,
                        'maximum': utilization['maximum_draw_total'] or 0,
                        'outlet_count': self.poweroutlets.filter(feed_leg=leg).count(),
                    })

            return ret

        # Default to administratively defined values
        return {
            'allocated': self.allocated_draw or 0,
            'maximum': self.maximum_draw or 0,
            'outlet_count': self.poweroutlets.count(),
            'legs': [],
        }


class PowerOutlet(ModularComponentModel, CabledObjectModel, PathEndpoint, TrackingModelMixin):
    """
    A physical power outlet (output) within a Device which provides power to a PowerPort.
    """
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50,
        choices=PowerOutletTypeChoices,
        blank=True,
        null=True,
        help_text=_('Physical port type')
    )
    power_port = models.ForeignKey(
        to='dcim.PowerPort',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='poweroutlets'
    )
    feed_leg = models.CharField(
        verbose_name=_('feed leg'),
        max_length=50,
        choices=PowerOutletFeedLegChoices,
        blank=True,
        null=True,
        help_text=_('Phase (for three-phase feeds)')
    )
    color = ColorField(
        verbose_name=_('color'),
        blank=True
    )

    clone_fields = ('device', 'module', 'type', 'power_port', 'feed_leg')

    class Meta(ModularComponentModel.Meta):
        verbose_name = _('power outlet')
        verbose_name_plural = _('power outlets')

    def clean(self):
        super().clean()

        # Validate power port assignment
        if self.power_port and self.power_port.device != self.device:
            raise ValidationError(
                _("Parent power port ({power_port}) must belong to the same device").format(power_port=self.power_port)
            )


#
# Interfaces
#

class BaseInterface(models.Model):
    """
    Abstract base class for fields shared by dcim.Interface and virtualization.VMInterface.
    """
    enabled = models.BooleanField(
        verbose_name=_('enabled'),
        default=True
    )
    mac_address = MACAddressField(
        null=True,
        blank=True,
        verbose_name=_('MAC address')
    )
    mtu = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(INTERFACE_MTU_MIN),
            MaxValueValidator(INTERFACE_MTU_MAX)
        ],
        verbose_name=_('MTU')
    )
    mode = models.CharField(
        verbose_name=_('mode'),
        max_length=50,
        choices=InterfaceModeChoices,
        blank=True,
        null=True,
        help_text=_('IEEE 802.1Q tagging strategy')
    )
    parent = models.ForeignKey(
        to='self',
        on_delete=models.RESTRICT,
        related_name='child_interfaces',
        null=True,
        blank=True,
        verbose_name=_('parent interface')
    )
    bridge = models.ForeignKey(
        to='self',
        on_delete=models.SET_NULL,
        related_name='bridge_interfaces',
        null=True,
        blank=True,
        verbose_name=_('bridge interface')
    )
    untagged_vlan = models.ForeignKey(
        to='ipam.VLAN',
        on_delete=models.SET_NULL,
        related_name='%(class)ss_as_untagged',
        null=True,
        blank=True,
        verbose_name=_('untagged VLAN')
    )
    tagged_vlans = models.ManyToManyField(
        to='ipam.VLAN',
        related_name='%(class)ss_as_tagged',
        blank=True,
        verbose_name=_('tagged VLANs')
    )
    qinq_svlan = models.ForeignKey(
        to='ipam.VLAN',
        on_delete=models.SET_NULL,
        related_name='%(class)ss_svlan',
        null=True,
        blank=True,
        verbose_name=_('Q-in-Q SVLAN')
    )
    vlan_translation_policy = models.ForeignKey(
        to='ipam.VLANTranslationPolicy',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_('VLAN Translation Policy')
    )

    class Meta:
        abstract = True

    def clean(self):
        super().clean()

        # SVLAN can be defined only for Q-in-Q interfaces
        if self.qinq_svlan and self.mode != InterfaceModeChoices.MODE_Q_IN_Q:
            raise ValidationError({
                'qinq_svlan': _("Only Q-in-Q interfaces may specify a service VLAN.")
            })

    def save(self, *args, **kwargs):

        # Remove untagged VLAN assignment for non-802.1Q interfaces
        if not self.mode:
            self.untagged_vlan = None

        # Only "tagged" interfaces may have tagged VLANs assigned. ("tagged all" implies all VLANs are assigned.)
        if not self._state.adding and self.mode != InterfaceModeChoices.MODE_TAGGED:
            self.tagged_vlans.clear()

        return super().save(*args, **kwargs)

    @property
    def tunnel_termination(self):
        return self.tunnel_terminations.first()

    @property
    def count_ipaddresses(self):
        return self.ip_addresses.count()

    @property
    def count_fhrp_groups(self):
        return self.fhrp_group_assignments.count()


class Interface(ModularComponentModel, BaseInterface, CabledObjectModel, PathEndpoint, TrackingModelMixin):
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
    vdcs = models.ManyToManyField(
        to='dcim.VirtualDeviceContext',
        related_name='interfaces'
    )
    lag = models.ForeignKey(
        to='self',
        on_delete=models.SET_NULL,
        related_name='member_interfaces',
        null=True,
        blank=True,
        verbose_name=_('parent LAG')
    )
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50,
        choices=InterfaceTypeChoices
    )
    mgmt_only = models.BooleanField(
        default=False,
        verbose_name=_('management only'),
        help_text=_('This interface is used only for out-of-band management')
    )
    speed = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_('speed (Kbps)')
    )
    duplex = models.CharField(
        verbose_name=_('duplex'),
        max_length=50,
        blank=True,
        null=True,
        choices=InterfaceDuplexChoices
    )
    wwn = WWNField(
        null=True,
        blank=True,
        verbose_name=_('WWN'),
        help_text=_('64-bit World Wide Name')
    )
    rf_role = models.CharField(
        max_length=30,
        choices=WirelessRoleChoices,
        blank=True,
        null=True,
        verbose_name=_('wireless role')
    )
    rf_channel = models.CharField(
        max_length=50,
        choices=WirelessChannelChoices,
        blank=True,
        null=True,
        verbose_name=_('wireless channel')
    )
    rf_channel_frequency = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('channel frequency (MHz)'),
        help_text=_("Populated by selected channel (if set)")
    )
    rf_channel_width = models.DecimalField(
        max_digits=7,
        decimal_places=3,
        blank=True,
        null=True,
        verbose_name=('channel width (MHz)'),
        help_text=_("Populated by selected channel (if set)")
    )
    tx_power = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=(MaxValueValidator(127),),
        verbose_name=_('transmit power (dBm)')
    )
    poe_mode = models.CharField(
        max_length=50,
        choices=InterfacePoEModeChoices,
        blank=True,
        null=True,
        verbose_name=_('PoE mode')
    )
    poe_type = models.CharField(
        max_length=50,
        choices=InterfacePoETypeChoices,
        blank=True,
        null=True,
        verbose_name=_('PoE type')
    )
    wireless_link = models.ForeignKey(
        to='wireless.WirelessLink',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True
    )
    wireless_lans = models.ManyToManyField(
        to='wireless.WirelessLAN',
        related_name='interfaces',
        blank=True,
        verbose_name=_('wireless LANs')
    )
    vrf = models.ForeignKey(
        to='ipam.VRF',
        on_delete=models.SET_NULL,
        related_name='interfaces',
        null=True,
        blank=True,
        verbose_name=_('VRF')
    )
    ip_addresses = GenericRelation(
        to='ipam.IPAddress',
        content_type_field='assigned_object_type',
        object_id_field='assigned_object_id',
        related_query_name='interface'
    )
    fhrp_group_assignments = GenericRelation(
        to='ipam.FHRPGroupAssignment',
        content_type_field='interface_type',
        object_id_field='interface_id',
        related_query_name='+'
    )
    tunnel_terminations = GenericRelation(
        to='vpn.TunnelTermination',
        content_type_field='termination_type',
        object_id_field='termination_id',
        related_query_name='interface'
    )
    l2vpn_terminations = GenericRelation(
        to='vpn.L2VPNTermination',
        content_type_field='assigned_object_type',
        object_id_field='assigned_object_id',
        related_query_name='interface',
    )

    clone_fields = (
        'device', 'module', 'parent', 'bridge', 'lag', 'type', 'mgmt_only', 'mtu', 'mode', 'speed', 'duplex', 'rf_role',
        'rf_channel', 'rf_channel_frequency', 'rf_channel_width', 'tx_power', 'poe_mode', 'poe_type', 'vrf',
    )

    class Meta(ModularComponentModel.Meta):
        ordering = ('device', CollateAsChar('_name'))
        verbose_name = _('interface')
        verbose_name_plural = _('interfaces')

    def clean(self):
        super().clean()

        # Virtual Interfaces cannot have a Cable attached
        if self.is_virtual and self.cable:
            raise ValidationError({
                'type': _("{display_type} interfaces cannot have a cable attached.").format(
                    display_type=self.get_type_display()
                )
            })

        # Virtual Interfaces cannot be marked as connected
        if self.is_virtual and self.mark_connected:
            raise ValidationError({
                'mark_connected': _("{display_type} interfaces cannot be marked as connected.".format(
                    display_type=self.get_type_display())
                )
            })

        # Parent validation

        # An interface cannot be its own parent
        if self.pk and self.parent_id == self.pk:
            raise ValidationError({'parent': _("An interface cannot be its own parent.")})

        # A physical interface cannot have a parent interface
        if self.type != InterfaceTypeChoices.TYPE_VIRTUAL and self.parent is not None:
            raise ValidationError({'parent': _("Only virtual interfaces may be assigned to a parent interface.")})

        # An interface's parent must belong to the same device or virtual chassis
        if self.parent and self.parent.device != self.device:
            if self.device.virtual_chassis is None:
                raise ValidationError({
                    'parent': _(
                        "The selected parent interface ({interface}) belongs to a different device ({device})"
                    ).format(interface=self.parent, device=self.parent.device)
                })
            elif self.parent.device.virtual_chassis != self.parent.virtual_chassis:
                raise ValidationError({
                    'parent': _(
                        "The selected parent interface ({interface}) belongs to {device}, which is not part of "
                        "virtual chassis {virtual_chassis}."
                    ).format(
                        interface=self.parent,
                        device=self.parent_device,
                        virtual_chassis=self.device.virtual_chassis
                    )
                })

        # Bridge validation

        # An interface cannot be bridged to itself
        if self.pk and self.bridge_id == self.pk:
            raise ValidationError({'bridge': _("An interface cannot be bridged to itself.")})

        # A bridged interface belong to the same device or virtual chassis
        if self.bridge and self.bridge.device != self.device:
            if self.device.virtual_chassis is None:
                raise ValidationError({
                    'bridge': _(
                        "The selected bridge interface ({bridge}) belongs to a different device ({device})."
                    ).format(bridge=self.bridge, device=self.bridge.device)
                })
            elif self.bridge.device.virtual_chassis != self.device.virtual_chassis:
                raise ValidationError({
                    'bridge': _(
                        "The selected bridge interface ({interface}) belongs to {device}, which is not part of virtual "
                        "chassis {virtual_chassis}."
                    ).format(
                        interface=self.bridge, device=self.bridge.device, virtual_chassis=self.device.virtual_chassis
                    )
                })

        # LAG validation

        # A virtual interface cannot have a parent LAG
        if self.type == InterfaceTypeChoices.TYPE_VIRTUAL and self.lag is not None:
            raise ValidationError({'lag': _("Virtual interfaces cannot have a parent LAG interface.")})

        # A LAG interface cannot be its own parent
        if self.pk and self.lag_id == self.pk:
            raise ValidationError({'lag': _("A LAG interface cannot be its own parent.")})

        # An interface's LAG must belong to the same device or virtual chassis
        if self.lag and self.lag.device != self.device:
            if self.device.virtual_chassis is None:
                raise ValidationError({
                    'lag': _(
                        "The selected LAG interface ({lag}) belongs to a different device ({device})."
                    ).format(lag=self.lag, device=self.lag.device)
                })
            elif self.lag.device.virtual_chassis != self.device.virtual_chassis:
                raise ValidationError({
                    'lag': _(
                        "The selected LAG interface ({lag}) belongs to {device}, which is not part of virtual chassis "
                        "{virtual_chassis}.".format(
                            lag=self.lag, device=self.lag.device, virtual_chassis=self.device.virtual_chassis)
                    )
                })

        # PoE validation

        # Only physical interfaces may have a PoE mode/type assigned
        if self.poe_mode and self.is_virtual:
            raise ValidationError({
                'poe_mode': _("Virtual interfaces cannot have a PoE mode.")
            })
        if self.poe_type and self.is_virtual:
            raise ValidationError({
                'poe_type': _("Virtual interfaces cannot have a PoE type.")
            })

        # An interface with a PoE type set must also specify a mode
        if self.poe_type and not self.poe_mode:
            raise ValidationError({
                'poe_type': _("Must specify PoE mode when designating a PoE type.")
            })

        # Wireless validation

        # RF role & channel may only be set for wireless interfaces
        if self.rf_role and not self.is_wireless:
            raise ValidationError({'rf_role': _("Wireless role may be set only on wireless interfaces.")})
        if self.rf_channel and not self.is_wireless:
            raise ValidationError({'rf_channel': _("Channel may be set only on wireless interfaces.")})

        # Validate channel frequency against interface type and selected channel (if any)
        if self.rf_channel_frequency:
            if not self.is_wireless:
                raise ValidationError({
                    'rf_channel_frequency': _("Channel frequency may be set only on wireless interfaces."),
                })
            if self.rf_channel and self.rf_channel_frequency != get_channel_attr(self.rf_channel, 'frequency'):
                raise ValidationError({
                    'rf_channel_frequency': _("Cannot specify custom frequency with channel selected."),
                })

        # Validate channel width against interface type and selected channel (if any)
        if self.rf_channel_width:
            if not self.is_wireless:
                raise ValidationError({'rf_channel_width': _("Channel width may be set only on wireless interfaces.")})
            if self.rf_channel and self.rf_channel_width != get_channel_attr(self.rf_channel, 'width'):
                raise ValidationError({'rf_channel_width': _("Cannot specify custom width with channel selected.")})

        # VLAN validation

        # Validate untagged VLAN
        if self.untagged_vlan and self.untagged_vlan.site not in [self.device.site, None]:
            raise ValidationError({
                'untagged_vlan': _(
                    "The untagged VLAN ({untagged_vlan}) must belong to the same site as the interface's parent "
                    "device, or it must be global."
                ).format(untagged_vlan=self.untagged_vlan)
            })

    def save(self, *args, **kwargs):

        # Set absolute channel attributes from selected options
        if self.rf_channel and not self.rf_channel_frequency:
            self.rf_channel_frequency = get_channel_attr(self.rf_channel, 'frequency')
        if self.rf_channel and not self.rf_channel_width:
            self.rf_channel_width = get_channel_attr(self.rf_channel, 'width')

        super().save(*args, **kwargs)

    @property
    def _occupied(self):
        return super()._occupied or bool(self.wireless_link_id)

    @property
    def is_wired(self):
        return not self.is_virtual and not self.is_wireless

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
    def is_bridge(self):
        return self.type == InterfaceTypeChoices.TYPE_BRIDGE

    @property
    def link(self):
        return self.cable or self.wireless_link

    @cached_property
    def link_peers(self):
        if self.cable:
            return super().link_peers
        if self.wireless_link:
            # Return the opposite side of the attached wireless link
            if self.wireless_link.interface_a == self:
                return [self.wireless_link.interface_b]
            else:
                return [self.wireless_link.interface_a]
        return []

    @property
    def l2vpn_termination(self):
        return self.l2vpn_terminations.first()


#
# Pass-through ports
#

class FrontPort(ModularComponentModel, CabledObjectModel, TrackingModelMixin):
    """
    A pass-through port on the front of a Device.
    """
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50,
        choices=PortTypeChoices
    )
    color = ColorField(
        verbose_name=_('color'),
        blank=True
    )
    rear_port = models.ForeignKey(
        to='dcim.RearPort',
        on_delete=models.CASCADE,
        related_name='frontports'
    )
    rear_port_position = models.PositiveSmallIntegerField(
        verbose_name=_('rear port position'),
        default=1,
        validators=[
            MinValueValidator(REARPORT_POSITIONS_MIN),
            MaxValueValidator(REARPORT_POSITIONS_MAX)
        ],
        help_text=_('Mapped position on corresponding rear port')
    )

    clone_fields = ('device', 'type', 'color')

    class Meta(ModularComponentModel.Meta):
        constraints = (
            models.UniqueConstraint(
                fields=('device', 'name'),
                name='%(app_label)s_%(class)s_unique_device_name'
            ),
            models.UniqueConstraint(
                fields=('rear_port', 'rear_port_position'),
                name='%(app_label)s_%(class)s_unique_rear_port_position'
            ),
        )
        verbose_name = _('front port')
        verbose_name_plural = _('front ports')

    def clean(self):
        super().clean()

        if hasattr(self, 'rear_port'):

            # Validate rear port assignment
            if self.rear_port.device != self.device:
                raise ValidationError({
                    "rear_port": _(
                        "Rear port ({rear_port}) must belong to the same device"
                    ).format(rear_port=self.rear_port)
                })

            # Validate rear port position assignment
            if self.rear_port_position > self.rear_port.positions:
                raise ValidationError({
                    "rear_port_position": _(
                        "Invalid rear port position ({rear_port_position}): Rear port {name} has only {positions} "
                        "positions."
                    ).format(
                        rear_port_position=self.rear_port_position,
                        name=self.rear_port.name,
                        positions=self.rear_port.positions
                    )
                })


class RearPort(ModularComponentModel, CabledObjectModel, TrackingModelMixin):
    """
    A pass-through port on the rear of a Device.
    """
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50,
        choices=PortTypeChoices
    )
    color = ColorField(
        verbose_name=_('color'),
        blank=True
    )
    positions = models.PositiveSmallIntegerField(
        verbose_name=_('positions'),
        default=1,
        validators=[
            MinValueValidator(REARPORT_POSITIONS_MIN),
            MaxValueValidator(REARPORT_POSITIONS_MAX)
        ],
        help_text=_('Number of front ports which may be mapped')
    )
    clone_fields = ('device', 'type', 'color', 'positions')

    class Meta(ModularComponentModel.Meta):
        verbose_name = _('rear port')
        verbose_name_plural = _('rear ports')

    def clean(self):
        super().clean()

        # Check that positions count is greater than or equal to the number of associated FrontPorts
        if not self._state.adding:
            frontport_count = self.frontports.count()
            if self.positions < frontport_count:
                raise ValidationError({
                    "positions": _(
                        "The number of positions cannot be less than the number of mapped front ports "
                        "({frontport_count})"
                    ).format(frontport_count=frontport_count)
                })


#
# Bays
#

class ModuleBay(ModularComponentModel, TrackingModelMixin, MPTTModel):
    """
    An empty space within a Device which can house a child device
    """
    parent = TreeForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True,
        editable=False,
        db_index=True
    )
    position = models.CharField(
        verbose_name=_('position'),
        max_length=30,
        blank=True,
        help_text=_('Identifier to reference when renaming installed components')
    )

    objects = TreeManager()

    clone_fields = ('device',)

    class Meta(ModularComponentModel.Meta):
        constraints = (
            models.UniqueConstraint(
                fields=('device', 'module', 'name'),
                name='%(app_label)s_%(class)s_unique_device_module_name'
            ),
        )
        verbose_name = _('module bay')
        verbose_name_plural = _('module bays')

    class MPTTMeta:
        order_insertion_by = ('module',)

    def clean(self):
        super().clean()

        # Check for recursion
        if module := self.module:
            module_bays = [self.pk]
            modules = []
            while module:
                if module.pk in modules or module.module_bay.pk in module_bays:
                    raise ValidationError(_("A module bay cannot belong to a module installed within it."))
                modules.append(module.pk)
                module_bays.append(module.module_bay.pk)
                module = module.module_bay.module if module.module_bay else None

    def save(self, *args, **kwargs):
        if self.module:
            self.parent = self.module.module_bay
        super().save(*args, **kwargs)


class DeviceBay(ComponentModel, TrackingModelMixin):
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

    clone_fields = ('device',)

    class Meta(ComponentModel.Meta):
        verbose_name = _('device bay')
        verbose_name_plural = _('device bays')

    def clean(self):
        super().clean()

        # Validate that the parent Device can have DeviceBays
        if hasattr(self, 'device') and not self.device.device_type.is_parent_device:
            raise ValidationError(_("This type of device ({device_type}) does not support device bays.").format(
                device_type=self.device.device_type
            ))

        # Cannot install a device into itself, obviously
        if self.installed_device and getattr(self, 'device', None) == self.installed_device:
            raise ValidationError(_("Cannot install a device into itself."))

        # Check that the installed device is not already installed elsewhere
        if self.installed_device:
            current_bay = DeviceBay.objects.filter(installed_device=self.installed_device).first()
            if current_bay and current_bay != self:
                raise ValidationError({
                    'installed_device': _(
                        "Cannot install the specified device; device is already installed in {bay}."
                    ).format(bay=current_bay)
                })


#
# Inventory items
#


class InventoryItemRole(OrganizationalModel):
    """
    Inventory items may optionally be assigned a functional role.
    """
    color = ColorField(
        verbose_name=_('color'),
        default=ColorChoices.COLOR_GREY
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('inventory item role')
        verbose_name_plural = _('inventory item roles')


class InventoryItem(MPTTModel, ComponentModel, TrackingModelMixin):
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
    component_type = models.ForeignKey(
        to='contenttypes.ContentType',
        limit_choices_to=MODULAR_COMPONENT_MODELS,
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True
    )
    component_id = models.PositiveBigIntegerField(
        blank=True,
        null=True
    )
    component = GenericForeignKey(
        ct_field='component_type',
        fk_field='component_id'
    )
    status = models.CharField(
        verbose_name=_('status'),
        max_length=50,
        choices=InventoryItemStatusChoices,
        default=InventoryItemStatusChoices.STATUS_ACTIVE
    )
    role = models.ForeignKey(
        to='dcim.InventoryItemRole',
        on_delete=models.PROTECT,
        related_name='inventory_items',
        blank=True,
        null=True
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
        verbose_name=_('part ID'),
        blank=True,
        help_text=_('Manufacturer-assigned part identifier')
    )
    serial = models.CharField(
        max_length=50,
        verbose_name=_('serial number'),
        blank=True
    )
    asset_tag = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_('asset tag'),
        help_text=_('A unique tag used to identify this item')
    )
    discovered = models.BooleanField(
        verbose_name=_('discovered'),
        default=False,
        help_text=_('This item was automatically discovered')
    )

    objects = TreeManager()

    clone_fields = ('device', 'parent', 'role', 'manufacturer', 'status', 'part_id')

    class Meta:
        ordering = ('device__id', 'parent__id', 'name')
        indexes = (
            models.Index(fields=('component_type', 'component_id')),
        )
        constraints = (
            models.UniqueConstraint(
                fields=('device', 'parent', 'name'),
                name='%(app_label)s_%(class)s_unique_device_parent_name'
            ),
        )
        verbose_name = _('inventory item')
        verbose_name_plural = _('inventory items')

    def clean(self):
        super().clean()

        # An InventoryItem cannot be its own parent
        if self.pk and self.parent_id == self.pk:
            raise ValidationError({
                "parent": _("Cannot assign self as parent.")
            })

        # Validation for moving InventoryItems
        if not self._state.adding:
            # Cannot move an InventoryItem to another device if it has a parent
            if self.parent and self.parent.device != self.device:
                raise ValidationError({
                    "parent": _("Parent inventory item does not belong to the same device.")
                })

            # Prevent moving InventoryItems with children
            first_child = self.get_children().first()
            if first_child and first_child.device != self.device:
                raise ValidationError(_("Cannot move an inventory item with dependent children"))

            # When moving an InventoryItem to another device, remove any associated component
            if self.component and self.component.device != self.device:
                self.component = None
        else:
            if self.component and self.component.device != self.device:
                raise ValidationError({
                    "device": _("Cannot assign inventory item to component on another device")
                })

    def get_status_color(self):
        return InventoryItemStatusChoices.colors.get(self.status)
